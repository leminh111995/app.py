import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Các thư viện phục vụ AI và xử lý ngôn ngữ tự nhiên
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo hệ thống đã tải các tài nguyên cần thiết cho NLP
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & XÁC THỰC TRUY CẬP (GATEKEEPER)
# ==============================================================================
def check_password():
    """Hàm xác thực mật mã dành riêng cho Minh để bảo vệ hệ thống"""
    def password_entered():
        # Kiểm tra mật mã từ Secrets của Streamlit
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "🔑 Nhập mật mã của Minh:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    return st.session_state.get("password_correct", False)

# Chỉ thực thi ứng dụng khi mật mã chính xác
if check_password():
    # Thiết lập cấu hình trang hiển thị
    st.set_page_config(
        page_title="Quant System V9.2 Absolute Master", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🛡️ Quant System V9.2: Absolute Master Advisor")

    # Khởi tạo đối tượng Vnstock
    vn = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU ĐA TẦNG (DATA LAYER)
    # ==============================================================================
    def lay_du_lieu(ticker, days=1000):
        """Lấy dữ liệu giá lịch sử từ Vnstock, tự động dự phòng sang Yahoo Finance"""
        # Phương án 1: Sử dụng Vnstock (Dữ liệu chuẩn sàn Việt Nam)
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            df_raw = vn.stock.quote.history(symbol=ticker, start=start_date, end=end_date)
            
            if df_raw is not None and not df_raw.empty:
                # Đồng nhất tên cột về chữ thường để dễ xử lý
                df_raw.columns = [col.lower() for col in df_raw.columns]
                return df_raw
        except Exception as e:
            # Ghi nhận lỗi thầm lặng để chuyển sang dự phòng
            pass
        
        # Phương án 2: Dự phòng Yahoo Finance (Khi Vnstock nghẽn hoặc lỗi mã SSI/Bank)
        try:
            # Thêm hậu tố .VN cho mã chứng khoán Việt Nam trừ chỉ số Index
            if ticker == "VNINDEX":
                symbol_yf = "^VNINDEX"
            else:
                symbol_yf = f"{ticker}.VN"
                
            yt_data = yf.download(symbol_yf, period="3y", progress=False)
            
            if not yt_data.empty:
                yt_data = yt_data.reset_index()
                # Xử lý Multi-index của Yahoo Finance (thường gặp ở phiên bản mới)
                new_cols = []
                for col in yt_data.columns:
                    if isinstance(col, tuple):
                        new_cols.append(col[0].lower())
                    else:
                        new_cols.append(col.lower())
                yt_data.columns = new_cols
                return yt_data
        except Exception as e:
            st.error(f"Lỗi truy xuất dữ liệu mã {ticker}: {str(e)}")
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE)
    # ==============================================================================
    def tinh_toan_chi_bao(df):
        """Tính toán toàn bộ các chỉ báo kỹ thuật cốt lõi: MA, BOL, RSI, MACD, FLOW"""
        df = df.copy()
        
        # --- Các đường trung bình động (Moving Averages) ---
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma50'] = df['close'].rolling(window=50).mean()
        df['ma200'] = df['close'].rolling(window=200).mean()
        
        # --- Dải Bollinger Bands (Vùng biên vận động) ---
        df['std_dev'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['ma20'] + (df['std_dev'] * 2)
        df['lower_band'] = df['ma20'] - (df['std_dev'] * 2)
        
        # --- Chỉ báo sức mạnh tương đối (RSI 14) ---
        delta_price = df['close'].diff()
        gain_val = (delta_price.where(delta_price > 0, 0)).rolling(window=14).mean()
        loss_val = (-delta_price.where(delta_price < 0, 0)).rolling(window=14).mean()
        rs_val = gain_val / (loss_val + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs_val))
        
        # --- Chỉ báo MACD (12, 26, 9) ---
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # --- Các biến số phục vụ Dòng tiền & AI ---
        df['return_1d'] = df['close'].pct_change()
        # So sánh khối lượng hiện tại với trung bình 10 phiên
        df['vol_change'] = df['volume'] / df['volume'].rolling(window=10).mean()
        df['money_flow'] = df['close'] * df['volume']
        df['volatility'] = df['return_1d'].rolling(window=20).std()
        
        # Xác định xu hướng Gom/Xả: (Giá tăng & Vol nổ) hoặc (Giá giảm & Vol nổ)
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1.2), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1.2), -1, 0))
        
        return df.dropna()

    # ==============================================================================
    # 4. HÀM TRÍ TUỆ NHÂN TẠO & KIỂM CHỨNG LỊCH SỬ (INTELLIGENCE)
    # ==============================================================================
    def chan_doan_tam_ly_fng(df):
        """Phân tích tâm lý thị trường dựa trên chỉ số Fear & Greed (RSI)"""
        current_rsi = df.iloc[-1]['rsi']
        
        if current_rsi > 75:
            text_label = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif current_rsi > 60:
            text_label = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif current_rsi < 30:
            text_label = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif current_rsi < 42:
            text_label = "😨 SỢ HÃI (BI QUAN)"
        else:
            text_label = "🟡 TRUNG LẬP"
            
        return text_label, round(current_rsi, 1)

    def tinh_backtest_winrate(df):
        """Kiểm tra xác suất thắng của tín hiệu RSI/MACD trong lịch sử 1000 phiên"""
        total_signals = 0
        successful_wins = 0
        
        for i in range(100, len(df) - 10):
            # Điều kiện mua: RSI thấp và MACD cắt lên Signal
            is_rsi_low = df['rsi'].iloc[i] < 45
            is_macd_cross_up = df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
            
            if is_rsi_low and is_macd_cross_up:
                total_signals += 1
                # Kiểm tra lợi nhuận mục tiêu 5% trong vòng 10 phiên kế tiếp
                future_window = df['close'].iloc[i+1 : i+11]
                if any(future_window > df['close'].iloc[i] * 1.05):
                    successful_wins += 1
        
        if total_signals == 0:
            return 0.0
            
        win_rate_pct = (successful_wins / total_signals) * 100
        return round(win_rate_pct, 1)

    def du_bao_ai_t3(df):
        """Sử dụng mô hình Machine Learning dự báo xác suất tăng giá sau 3 phiên"""
        if len(df) < 200:
            return "N/A"
            
        df_ml = df.copy()
        # Định nghĩa mục tiêu: Giá tăng > 2% sau 3 phiên giao dịch
        df_ml['target'] = (df_ml['close'].shift(-3) > df_ml['close'] * 1.02).astype(int)
        
        # Các đặc trưng đầu vào cho mô hình
        features_list = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data_clean = df_ml.dropna()
        
        X_train_data = data_clean[features_list]
        y_train_label = data_clean['target']
        
        # Huấn luyện mô hình Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train_data[:-3], y_train_label[:-3])
        
        # Lấy xác suất dự báo cho phiên cuối cùng
        last_prediction_prob = rf_model.predict_proba(X_train_data.iloc[[-1]])[0][1]
        return round(last_prediction_prob * 100, 1)

    # ==============================================================================
    # 5. PHÂN TÍCH NỘI LỰC TÀI CHÍNH (FUNDAMENTAL ENGINE)
    # ==============================================================================
    def lay_tang_truong_lnst(ticker):
        """Tính tăng trưởng Lợi nhuận sau thuế của doanh nghiệp"""
        try:
            df_income = vn.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            # Tìm kiếm cột LNST không phân biệt ngôn ngữ
            possible_cols = [c for c in df_income.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])]
            
            if possible_cols:
                col_name = possible_cols[0]
                val_q1 = float(df_income.iloc[0][col_name])
                val_q5 = float(df_income.iloc[4][col_name])
                if val_q5 > 0:
                    growth_val = ((val_q1 - val_q5) / val_q5) * 100
                    return round(growth_val, 1)
        except:
            pass
            
        try:
            # Fallback sang Yahoo Finance cho các mã đặc thù
            stock_info = yf.Ticker(f"{ticker}.VN").info
            growth_yf = stock_info.get('earningsQuarterlyGrowth')
            if growth_yf is not None:
                return round(growth_yf * 100, 1)
        except:
            pass
        return None

    def lay_dinh_gia_roe_pe(ticker):
        """Lấy chỉ số định giá P/E và hiệu quả sử dụng vốn ROE"""
        pe_ratio, roe_ratio = 0.0, 0.0
        try:
            df_ratio = vn.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe_ratio = df_ratio.get('ticker_pe', df_ratio.get('pe', 0))
            roe_ratio = df_ratio.get('roe', 0)
        except:
            pass
            
        if pe_ratio <= 0:
            try:
                info_yf = yf.Ticker(f"{ticker}.VN").info
                pe_ratio = info_yf.get('trailingPE', 0)
                roe_ratio = info_yf.get('returnOnEquity', 0)
            except:
                pass
        return pe_ratio, roe_ratio

    # ==============================================================================
    # 6. 🧠 HỆ THỐNG ADVISOR: CHẨN ĐOÁN CHI TIẾT & ĐỀ XUẤT (V9.2 ABSOLUTE)
    # ==============================================================================
    def absolute_advisor_system(ticker, last_p, ai_val, wr_val, pe_val, roe_val, growth_val, list_gom_trụ, list_xa_trụ):
        """Hệ thống ra quyết định chiến thuật dựa trên sự hội tụ đa tầng"""
        # Khởi tạo các biến nội dung
        technical_comment = ""
        money_flow_comment = ""
        final_verdict = ""
        status_color = ""
        consensus_score = 0
        
        # --- LỚP 1: PHÂN TÍCH KỸ THUẬT CHI TIẾT ---
        if last_p['rsi'] > 72:
            technical_comment = f"Cảnh báo rủi ro: RSI ({last_p['rsi']:.1f}) đang ở vùng cực kỳ hưng phấn. Lịch sử cho thấy giá thường có xu hướng điều chỉnh mạnh về đường MA20 ({last_p['ma20']:,.0f}) khi chạm ngưỡng này."
        elif last_p['rsi'] < 35:
            technical_comment = f"Tín hiệu bắt đáy: RSI ({last_p['rsi']:.1f}) đang nằm ở vùng quá bán. Lực bán tháo đã suy kiệt, đây là khu vực có xác suất phục hồi kỹ thuật rất cao."
        else:
            technical_comment = f"Giá đang tích lũy ổn định. Hiện tại giá đang cách MA20 khoảng {((last_p['close']-last_p['ma20'])/last_p['ma20'])*100:.1f}%. Xu hướng ngắn hạn vẫn được bảo toàn tốt."
            
        # --- LỚP 2: PHÂN TÍCH DÒNG TIỀN THÔNG MINH ---
        if ticker in list_gom_trụ:
            money_flow_comment = f"Dòng tiền Cá mập (Smart Money) đang đổ vào {ticker} một cách chủ động, đồng pha với xu hướng gom hàng chung của nhóm trụ cột thị trường."
        elif ticker in list_xa_trụ:
            money_flow_comment = f"Thận trọng dòng tiền: Các tổ chức lớn đang có dấu hiệu phân phối (xả hàng) tại mã này. Áp lực bán từ 'tay to' đang gây sức ép lên giá."
        else:
            money_flow_comment = "Dòng tiền chủ yếu vận động bởi các nhà đầu tư cá nhân lẻ. Chưa thấy sự can thiệp đáng kể từ các quỹ hoặc các tổ chức tài chính lớn."

        # --- LỚP 3: THUẬT TOÁN TÍNH ĐIỂM ĐỒNG THUẬN ---
        if isinstance(ai_val, float) and ai_val >= 55.0: consensus_score += 1
        if wr_val >= 48.0: consensus_score += 1
        if last_p['close'] > last_p['ma20']: consensus_score += 1
        if growth_val is not None and growth_val >= 20.0: consensus_score += 1
        if pe_val > 0 and pe_val <= 15.0: consensus_score += 1
        if roe_val >= 0.15: consensus_score += 1

        # --- LỚP 4: RA QUYẾT ĐỊNH CHIẾN THUẬT ---
        if consensus_score >= 4 and last_p['rsi'] < 68:
            final_verdict = "🚀 MUA / NẮM GIỮ: Đạt điểm đồng thuận tuyệt đối. Ưu tiên giải ngân tại các vùng hỗ trợ ngắn hạn."
            status_color = "green"
        elif consensus_score <= 1 or last_p['rsi'] > 78:
            final_verdict = "🚨 BÁN / ĐỨNG NGOÀI: Tín hiệu rủi ro cao hoặc nội lực doanh nghiệp suy giảm. Ưu tiên bảo toàn vốn."
            status_color = "red"
        else:
            final_verdict = "⚖️ THEO DÕI: Tín hiệu đang ở trạng thái 50/50. Cần chờ đợi một phiên xác nhận với Volume bùng nổ (>1.2)."
            status_color = "orange"

        return technical_comment, money_flow_comment, final_verdict, status_color

    # ==============================================================================
    # 7. GIAO DIỆN NGƯỜI DÙNG & TRUNG TÂM ĐIỀU KHIỂN
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def lay_tat_ca_ma_hose():
        try:
            df_listing = vn.market.listing()
            return df_listing[df_listing['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    danh_sach_ma = lay_tat_ca_ma_hose()
    st.sidebar.header("🕹️ Trung Tâm Điều Hành")
    select_ma = st.sidebar.selectbox("Chọn mã cổ phiếu:", danh_sach_ma)
    input_ma = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    ma_hien_tai = input_ma if input_ma else select_ma

    # Khởi tạo các Tab chức năng (Full Tabs)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 ROBOT ADVISOR & CHIẾN THUẬT", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 MARKET SENSE (COMMAND)", 
        "🔍 ROBOT HUNTER (TRUY QUÉT)"
    ])

    with tab1:
        # Nút thực thi phân tích chuyên sâu
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU MÃ {ma_hien_tai}"):
            df_stock = lay_du_lieu(ma_hien_tai)
            if df_stock is not None and not df_stock.empty:
                # Tính toán bộ chỉ báo
                df_stock = tinh_toan_chi_bao(df_stock)
                row_cuoi = df_stock.iloc[-1]
                
                # Chạy các engine thông minh
                ai_prob_pct = du_bao_ai_t3(df_stock)
                backtest_wr = tinh_backtest_winrate(df_stock)
                fng_text, fng_score = chan_doan_tam_ly_fng(df_stock)
                ma_pe, ma_roe = lay_dinh_gia_roe_pe(ma_hien_tai)
                ma_growth = lay_tang_truong_lnst(ma_hien_tai)
                
                # Quét nhanh thị trường chung để hỗ trợ Advisor
                nhom_tru = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                gom_list, xa_list = [], []
                for trụ in nhom_tru:
                    try:
                        d_trụ = lay_du_lieu(trụ, days=10)
                        if d_trụ is not None:
                            d_trụ = tinh_toan_chi_bao(d_trụ)
                            l_trụ = d_trụ.iloc[-1]
                            if l_trụ['return_1d'] > 0 and l_trụ['vol_change'] > 1.2: gom_list.append(trụ)
                            elif l_trụ['return_1d'] < 0 and l_trụ['vol_change'] > 1.2: xa_list.append(trụ)
                    except: pass

                # GỌI HỆ THỐNG ADVISOR ABSOLUTE
                t_diag, m_diag, verdict_final, v_color = absolute_advisor_system(
                    ma_hien_tai, row_cuoi, ai_prob_pct, backtest_wr, ma_pe, ma_roe, ma_growth, gom_list, xa_list
                )

                # HIỂN THỊ KẾT QUẢ CHẨN ĐOÁN
                st.write(f"### 🎯 Chẩn Đoán Robot Advisor cho {ma_hien_tai}")
                col_diag_a, col_diag_b = st.columns([2, 1])
                with col_diag_a:
                    st.info(f"**💡 Phân tích kỹ thuật chuyên sâu:** {t_diag}")
                    st.info(f"**🌊 Phân tích dòng tiền thông minh:** {m_diag}")
                    st.markdown(f"**Robot ghi chú:** AI dự báo xác suất tăng là **{ai_prob_pct}%**. Win-rate lịch sử của mã đạt **{backtest_wr}%**.")
                with col_diag_b:
                    st.subheader("🤖 ĐỀ XUẤT HÀNH ĐỘNG:")
                    st.title(f":{v_color}[{verdict_final.split(':')[0]}]")
                    st.write(f"*{verdict_final.split(':')[1]}*")
                
                st.divider()
                st.write("### 🧭 Bảng Chỉ Số Radar Hiệu Suất")
                col_rad_1, col_rad_2, col_rad_3, col_rad_4 = st.columns(4)
                col_rad_1.metric("Giá Hiện Tại", f"{row_cuoi['close']:,.0f}")
                col_rad_2.metric("Tâm Lý (Fear & Greed)", f"{fng_score}/100", delta=fng_text)
                col_rad_3.metric("AI Dự Báo (Xác suất)", f"{ai_prob_pct}%", delta="Tích cực" if ai_prob_pct > 55 else None)
                col_rad_4.metric("Backtest Win-rate", f"{backtest_wr}%", delta="Ổn định" if backtest_wr > 45 else None)

                # PHẦN HIỂN THỊ NAKED STATS (BẮT BUỘC)
                st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Chi Tiết (Naked Stats)")
                col_nk_1, col_nk_2, col_nk_3, col_nk_4 = st.columns(4)
                col_nk_1.metric("RSI (14)", f"{row_cuoi['rsi']:.1f}", delta="Quá mua" if row_cuoi['rsi']>70 else ("Quá bán" if row_cuoi['rsi']<30 else "Trung tính"))
                col_nk_2.metric("MACD Status", f"{row_cuoi['macd']:.2f}", delta="Cắt lên" if row_cuoi['macd']>row_cuoi['signal'] else "Cắt xuống")
                col_nk_3.metric("MA20 / MA50", f"{row_cuoi['ma20']:,.0f}", delta=f"{row_cuoi['ma50']:,.0f}")
                col_nk_4.metric("Bollinger Upper/Lower", f"{row_cuoi['upper_band']:,.0f}", delta=f"{row_cuoi['lower_band']:,.0f}", delta_color="inverse")
                
                # Cẩm nang thực chiến chi tiết
                with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (QUY TẮC VÀNG)"):
                    st.markdown(f"""
                    **1. Khối lượng (Volume):** Vol phiên hiện tại đạt **{row_cuoi['vol_change']:.1f} lần** trung bình 10 phiên.
                    - Giá tăng + Vol cao (>1.2) ➔ Cá mập đang Gom hàng mạnh mẽ.
                    - Giá giảm + Vol cao (>1.2) ➔ Cá mập đang Xả (Thoát hàng quyết liệt).
                    
                    **2. Bollinger Bands (BOL):** Vùng xám mờ trên biểu đồ đại diện cho dải biến động chuẩn. 
                    - Vượt dải trên ➔ Trạng thái hưng phấn, có xu hướng bị kéo ngược vào trong. 
                    - Thủng dải dưới ➔ Trạng thái hoảng loạn, cơ hội cho nhịp hồi kỹ thuật.
                    
                    **3. CÁCH NÉ BẪY GIÁ (BULL TRAP / BEAR TRAP):**
                    - **Né Đỉnh Giả:** Giá vượt đỉnh nhưng Vol thấp hơn trung bình ➔ Bẫy lừa mua để phân phối hàng.
                    - **Né Đáy Giả:** Giá chạm dải dưới nhưng Vol xả vẫn đỏ lòm và cực lớn ➔ Đừng bắt đáy, hãy chờ nến rút chân kèm Vol thấp.
                    
                    **4. Nguyên tắc Cắt lỗ kỷ luật:** Tuyệt đối thoát toàn bộ vị thế nếu giá chạm mốc **{row_cuoi['close']*0.93:,.0f} (-7%)**.
                    """)

                # BIỂU ĐỒ NẾN PHỨC HỢP (MASTER CHART)
                fig_master = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                # Biểu đồ nến
                fig_master.add_trace(go.Candlestick(x=df_stock['date'].tail(120), open=df_stock['open'].tail(120), high=df_stock['high'].tail(120), low=df_stock['low'].tail(120), close=df_stock['close'].tail(120), name='Giá'), row=1, col=1)
                # Các đường xu hướng
                fig_master.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['ma20'].tail(120), line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                fig_master.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['ma200'].tail(120), line=dict(color='purple', width=2), name='MA200 (Dài hạn)'), row=1, col=1)
                # Bollinger Bands với hiệu ứng tô màu xám mờ
                fig_master.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['upper_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải trên'), row=1, col=1)
                fig_master.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['lower_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải dưới', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
                # Biểu đồ khối lượng
                fig_master.add_trace(go.Bar(x=df_stock['date'].tail(120), y=df_stock['volume'].tail(120), name='Khối lượng', marker_color='gray'), row=2, col=1)
                
                fig_master.update_layout(height=650, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig_master, use_container_width=True)
            else:
                st.error("Không thể tải dữ liệu. Vui lòng kiểm tra mã chứng khoán!")

    with tab2:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá Doanh Nghiệp ({ma_hien_tai})")
        with st.spinner("Đang phân tích sức khỏe tài chính..."):
            tang_truong = lay_tang_truong_lnst(ma_hien_tai)
            if tang_truong is not None:
                if tang_truong >= 20.0:
                    st.success(f"**🔥 CanSLIM:** LNST tăng trưởng vượt bậc **+{tang_truong}%** (Đạt chuẩn doanh nghiệp siêu hạng).")
                elif tang_truong > 0:
                    st.info(f"**⚖️ Tăng trưởng:** LNST cải thiện ở mức **{tang_truong}%** (Tăng trưởng ổn định).")
                else:
                    st.error(f"**🚨 Cảnh báo:** LNST sụt giảm **{tang_truong}%** (Dấu hiệu doanh nghiệp đang đi lùi).")
            
            st.divider()
            val_pe, val_roe = lay_dinh_gia_roe_pe(ma_hien_tai)
            col_f_1, col_f_2 = st.columns(2)
            
            pe_tag = "Tốt (Định giá Rẻ)" if 0 < val_pe < 12 else ("Hợp lý" if val_pe < 18 else "Đắt (Rủi ro mua hớ)")
            col_f_1.metric("P/E (Định giá)", f"{val_pe:.1f}", delta=pe_tag, delta_color="normal" if val_pe < 18 else "inverse")
            st.write("> P/E thấp chứng tỏ giá cổ phiếu đang hấp dẫn so với khả năng sinh lời thực tế.")
            
            roe_tag = "Xuất sắc" if val_roe >= 0.25 else ("Tốt" if val_roe >= 0.15 else "Trung bình")
            col_f_2.metric("ROE (Hiệu quả vốn)", f"{val_roe:.1%}", delta=roe_tag, delta_color="normal" if val_roe >= 0.15 else "inverse")
            st.write("> ROE đo lường khả năng 'đẻ ra tiền' từ vốn của cổ đông. Tiêu chuẩn vàng là > 15%.")

    with tab3:
        st.write("### 🌊 Market Sense - Danh Sách Gom/Xả Trụ Cột")
        with st.spinner("Đang rà soát dấu chân Cá mập trên thị trường chung..."):
            tru_hose = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
            res_gom, res_xa = [], []
            
            for m in tru_hose:
                try:
                    df_p = lay_du_lieu(m, days=10)
                    if df_p is not None:
                        df_p = tinh_toan_chi_bao(df_p)
                        last_p = df_p.iloc[-1]
                        # Logic Gom/Xả: Giá đồng thuận với Volume đột biến (> 1.2)
                        if last_p['return_1d'] > 0 and last_p['vol_change'] > 1.2:
                            res_gom.append(m)
                        elif last_p['return_1d'] < 0 and last_p['vol_change'] > 1.2:
                            res_xa.append(m)
                except: pass
            
            b_col1, b_col2 = st.columns(2)
            b_col1.metric("Trụ đang GOM (Mua mạnh)", f"{len(res_gom)} mã", delta=f"{(len(res_gom)/len(tru_hose))*100:.0f}%", delta_color="normal")
            b_col2.metric("Trụ đang XẢ (Bán tháo)", f"{len(res_xa)} mã", delta=f"{(len(res_xa)/len(tru_hose))*100:.0f}%", delta_color="inverse")
            
            st.divider()
            list_col_g, list_col_x = st.columns(2)
            with list_col_g:
                st.success("✅ **DANH SÁCH MÃ ĐANG ĐƯỢC CÁ MẬP GOM:**")
                if res_gom: st.write(", ".join(res_gom))
                else: st.write("Không tìm thấy mã trụ nào có tín hiệu gom mạnh.")
            with list_col_x:
                st.error("🚨 **DANH SÁCH MÃ ĐANG BỊ CÁ MẬP XẢ:**")
                if res_xa: st.write(", ".join(res_xa))
                else: st.write("Chưa có áp lực bán tháo lớn ở nhóm cổ phiếu dẫn dắt.")
            
            if len(res_xa) > len(res_gom):
                st.warning("⚠️ Cảnh báo thị trường chung: Áp lực bán ở nhóm trụ lớn hơn lực mua. Rủi ro điều chỉnh cao.")
            else:
                st.info("ℹ️ Nhận định: Lực mua ở nhóm trụ đang ổn định. Thị trường có bệ đỡ từ dòng tiền lớn.")

    with tab4:
        st.subheader("🔍 Robot Hunter - Truy Quét Top 30 HOSE")
        if st.button("🔥 BẮT ĐẦU TRUY QUÉT DÒNG TIỀN"):
            h_list = []
            h_progress = st.progress(0)
            ma_scan = danh_sach_ma[:30]
            
            for idx, m_s in enumerate(ma_scan):
                try:
                    df_s = lay_du_lieu(m_s, days=100)
                    df_s = tinh_toan_chi_bao(df_s)
                    # Tiêu chuẩn Hunter: Volume phải nổ cực mạnh (> 1.3)
                    if df_s.iloc[-1]['vol_change'] > 1.3:
                        h_list.append({
                            'Mã': m_s, 
                            'Giá': df_s.iloc[-1]['close'], 
                            'Sức mạnh Vol': round(df_s.iloc[-1]['vol_change'], 2), 
                            'AI Dự báo Tăng': f"{du_bao_ai_t3(df_s)}%"
                        })
                except: pass
                h_progress.progress((idx+1)/len(ma_scan))
            
            if h_list:
                df_h = pd.DataFrame(h_list).sort_values(by='AI Dự báo Tăng', ascending=False)
                st.table(df_h)
                st.success("✅ Đã phát hiện các mã tiềm năng có tín hiệu bùng nổ dòng tiền và xác suất tăng cao.")
            else:
                st.write("Chưa tìm thấy mã nào đạt tiêu chuẩn Hunter trong ngày hôm nay.")
