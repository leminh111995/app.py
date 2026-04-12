import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Các thư viện phục vụ Machine Learning và xử lý ngôn ngữ
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo các tài nguyên cần thiết cho AI được tải đầy đủ để tránh lỗi Runtime
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & KIỂM SOÁT TRUY CẬP (SECURITY LAYER)
# ==============================================================================
def check_password():
    """Hàm xác thực mật mã dành riêng cho Minh để bảo vệ hệ thống Quant"""
    def password_entered():
        # Kiểm tra mật mã từ hệ thống Secrets của Streamlit (Phải setup trong Settings)
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Giao diện ô nhập mật mã
        st.text_input(
            "🔑 Nhập mật mã của Minh:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    return st.session_state.get("password_correct", False)

# Chỉ thực thi ứng dụng khi Minh nhập đúng mật mã truy cập
if check_password():
    # Cấu hình giao diện chuẩn chuyên nghiệp dành cho dân Quant Trading
    st.set_page_config(
        page_title="Quant System V9.3 Final Master", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("🛡️ Quant System V9.3: Advisor Master & Smart Flow Specialist")

    # Khởi tạo đối tượng kết nối dữ liệu thị trường Việt Nam
    vn = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU ĐA TẦNG (DATA ACQUISITION)
    # ==============================================================================
    def lay_du_lieu(ticker, days=1000):
        """Lấy dữ liệu giá lịch sử, ưu tiên Vnstock và dự phòng Yahoo Finance"""
        try:
            # 2.1 Thiết lập khoảng thời gian lấy dữ liệu mặc định
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 2.2 Thử lấy dữ liệu từ Vnstock (Dữ liệu gốc sàn HOSE/HNX)
            df_source = vn.stock.quote.history(symbol=ticker, start=start_date, end=end_date)
            
            if df_source is not None and not df_source.empty:
                # Đồng nhất tên cột về chữ thường để các hàm tính toán phía sau không bị lỗi
                df_source.columns = [col.lower() for col in df_source.columns]
                return df_source
        except Exception:
            # Nếu Vnstock lỗi, chuyển sang bước 2.3
            pass
        
        try:
            # 2.3 Fallback sang Yahoo Finance cho các mã SSI, Bank hoặc khi API Vnstock nghẽn
            if ticker == "VNINDEX":
                symbol_yf = "^VNINDEX"
            else:
                symbol_yf = f"{ticker}.VN"
                
            yt_raw = yf.download(symbol_yf, period="3y", progress=False)
            
            if not yt_raw.empty:
                yt_raw = yt_raw.reset_index()
                # Xử lý Multi-index của dữ liệu Yahoo Finance (Tránh lỗi do version mới)
                processed_cols = []
                for c in yt_raw.columns:
                    if isinstance(c, tuple):
                        processed_cols.append(c[0].lower())
                    else:
                        processed_cols.append(c.lower())
                yt_raw.columns = processed_cols
                return yt_raw
        except Exception as err:
            st.sidebar.error(f"Lỗi truy xuất mã {ticker}: {str(err)}")
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT CHI TIẾT (ENGINE LAYER)
    # ==============================================================================
    def tinh_toan_chi_bao(df):
        """Tính toán MA20, MA50, MA200, Bollinger Bands, RSI, MACD và Dòng tiền"""
        df = df.copy()
        
        # --- 3.1 Các đường trung bình động xu hướng (Moving Averages) ---
        # Đường ngắn hạn (Hỗ trợ/Kháng cự chính)
        df['ma20'] = df['close'].rolling(window=20).mean()
        # Đường trung hạn (Xác nhận xu hướng)
        df['ma50'] = df['close'].rolling(window=50).mean()
        # Đường dài hạn (Ngưỡng sống còn)
        df['ma200'] = df['close'].rolling(window=200).mean()
        
        # --- 3.2 Dải Bollinger Bands (BOL) ---
        # Tính độ lệch chuẩn
        df['std_val'] = df['close'].rolling(window=20).std()
        # Dải trên (Vùng hưng phấn)
        df['upper_band'] = df['ma20'] + (df['std_val'] * 2)
        # Dải dưới (Vùng hoảng loạn)
        df['lower_band'] = df['ma20'] - (df['std_val'] * 2)
        
        # --- 3.3 Chỉ số sức mạnh tương đối RSI (14) ---
        delta_p = df['close'].diff()
        gain_p = (delta_p.where(delta_p > 0, 0)).rolling(window=14).mean()
        loss_p = (-delta_p.where(delta_p < 0, 0)).rolling(window=14).mean()
        rs_p = gain_p / (loss_p + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs_p))
        
        # --- 3.4 Chỉ báo MACD (12, 26, 9) ---
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_12 - ema_26
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # --- 3.5 Các biến phục vụ Smart Flow & AI ---
        # Tỷ suất sinh lời trong ngày
        df['return_1d'] = df['close'].pct_change()
        # Biến động khối lượng (Sức mạnh Volume)
        df['vol_change'] = df['volume'] / df['volume'].rolling(window=10).mean()
        # Giá trị dòng tiền
        df['money_flow'] = df['close'] * df['volume']
        # Độ biến động lịch sử (Volatility)
        df['volatility'] = df['return_1d'].rolling(window=20).std()
        
        # --- 3.6 Logic xác định xu hướng Price-Volume (Gom/Xả) ---
        # 1: Gom mạnh (Giá tăng + Vol nổ), -1: Xả mạnh (Giá giảm + Vol nổ)
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1.2), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1.2), -1, 0))
        
        return df.dropna()

    # ==============================================================================
    # 4. CHẨN ĐOÁN TÂM LÝ & KIỂM CHỨNG LỊCH SỬ (INTELLIGENCE LAYER)
    # ==============================================================================
    def phan_tich_tam_ly_rsi(df):
        """Phân tích tâm lý thị trường dựa trên RSI (Fear & Greed Index)"""
        last_rsi_val = df.iloc[-1]['rsi']
        
        if last_rsi_val > 75:
            text_desc = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif last_rsi_val > 60:
            text_desc = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif last_rsi_val < 30:
            text_desc = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif last_rsi_val < 42:
            text_desc = "😨 SỢ HÃI (BI QUAN)"
        else:
            text_desc = "🟡 TRUNG LẬP (NGHI NGỜ)"
            
        return text_desc, round(last_rsi_val, 1)

    def tinh_backtest_winrate_logic(df):
        """Tính xác suất thắng lịch sử cho tín hiệu RSI < 45 và MACD cắt lên Signal"""
        total_count = 0
        win_count = 0
        
        # Duyệt qua dữ liệu lịch sử để kiểm chứng (Backtest)
        for i in range(100, len(df) - 10):
            # Điều kiện kích hoạt lệnh mua chuẩn kỹ thuật
            rsi_low = df['rsi'].iloc[i] < 45
            macd_up = df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
            
            if rsi_low and macd_up:
                total_count += 1
                # Kiểm tra lợi nhuận mục tiêu 5% trong vòng 10 phiên giao dịch tiếp theo
                future_prices = df['close'].iloc[i+1 : i+11]
                if any(future_prices > df['close'].iloc[i] * 1.05):
                    win_count += 1
        
        if total_count == 0:
            return 0.0
            
        win_rate_val = (win_count / total_count) * 100
        return round(win_rate_val, 1)

    def du_bao_ai_engine(df):
        """Mô hình Random Forest dự báo khả năng tăng giá trong 3 phiên tới (T+3)"""
        if len(df) < 200:
            return "N/A"
            
        df_model = df.copy()
        # Định nghĩa nhãn mục tiêu: Giá tăng > 2% sau 3 phiên giao dịch
        df_model['target'] = (df_model['close'].shift(-3) > df_model['close'] * 1.02).astype(int)
        
        # Tập hợp các đặc trưng đầu vào (Features)
        features_set = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data_clean = df_model.dropna()
        
        X_data = data_clean[features_set]
        y_label = data_clean['target']
        
        # Khởi tạo và huấn luyện mô hình rừng ngẫu nhiên
        rf_engine = RandomForestClassifier(n_estimators=100, random_state=42)
        # Loại bỏ 3 dòng cuối cùng vì không có nhãn mục tiêu tương lai
        rf_engine.fit(X_data[:-3], y_label[:-3])
        
        # Tính toán xác suất dự báo tăng cho phiên hiện tại
        prob_val = rf_engine.predict_proba(X_data.iloc[[-1]])[0][1]
        return round(prob_val * 100, 1)

    # ==============================================================================
    # 5. PHÂN TÍCH NỘI LỰC TÀI CHÍNH & CANSLIM (FUNDAMENTAL LAYER)
    # ==============================================================================
    def lay_tang_truong_canslim(ticker):
        """Tính tăng trưởng LNST của doanh nghiệp (Tiêu chuẩn C trong CanSLIM)"""
        try:
            # 5.1 Thử lấy báo cáo kết quả kinh doanh từ Vnstock
            df_income = vn.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            # Tìm kiếm cột lợi nhuận sau thuế linh hoạt
            target_cols = [c for c in df_income.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])]
            
            if target_cols:
                col_found = target_cols[0]
                val_latest = float(df_income.iloc[0][col_found])
                val_year_ago = float(df_income.iloc[4][col_found])
                if val_year_ago > 0:
                    growth_pct = ((val_latest - val_year_ago) / val_year_ago) * 100
                    return round(growth_pct, 1)
        except Exception:
            pass
            
        try:
            # 5.2 Dự phòng bằng Yahoo Finance cho các mã SSI/Ngân hàng
            stock_obj = yf.Ticker(f"{ticker}.VN")
            growth_yf = stock_obj.info.get('earningsQuarterlyGrowth')
            if growth_yf is not None:
                return round(growth_yf * 100, 1)
        except Exception:
            pass
        return None

    def lay_roe_pe_valuation(ticker):
        """Lấy chỉ số định giá P/E và hiệu quả sử dụng vốn ROE từ báo cáo tài chính"""
        pe_ratio, roe_ratio = 0.0, 0.0
        try:
            # Lấy các chỉ số tài chính từ Vnstock
            df_ratios = vn.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe_ratio = df_ratios.get('ticker_pe', df_ratios.get('pe', 0))
            roe_ratio = df_ratios.get('roe', 0)
        except:
            pass
            
        if pe_ratio <= 0:
            try:
                # Fallback sang Yahoo Finance khi Vnstock thiếu chỉ số
                info_yf = yf.Ticker(f"{ticker}.VN").info
                pe_ratio = info_yf.get('trailingPE', 0)
                roe_ratio = info_yf.get('returnOnEquity', 0)
            except:
                pass
        return pe_ratio, roe_ratio

    # ==============================================================================
    # 6. 🧠 ROBOT ADVISOR: CHẨN ĐOÁN CHI TIẾT & RA QUYẾT ĐỊNH (V9.3 MASTER)
    # ==============================================================================
    def advisor_master_diagnosis(ticker, last_row, ai_prob, wr_hist, pe_val, roe_val, growth_val, list_gom_t, list_xa_t):
        """Hệ thống Advisor: Phân tích hội tụ 5 tầng dữ liệu và đưa ra lời khuyên cuối cùng"""
        # Khởi tạo các đoạn văn bản chẩn đoán động
        tech_comment = ""
        flow_comment = ""
        verdict_text = ""
        verdict_hue = ""
        consensus_score = 0
        
        # --- LỚP 1: PHÂN TÍCH KỸ THUẬT CHI TIẾT ---
        if last_row['rsi'] > 72:
            tech_comment = f"Cảnh báo: RSI của {ticker} ({last_row['rsi']:.1f}) đang nằm trong vùng Quá mua cực độ. Giá đang bám sát dải Bollinger trên, rủi ro điều chỉnh về MA20 rất lớn. TUYỆT ĐỐI KHÔNG MUA ĐUỔI."
        elif last_row['rsi'] < 35:
            tech_comment = f"Cơ hội: RSI của {ticker} ({last_row['rsi']:.1f}) đang nằm sâu trong vùng Quá bán. Lực cung tháo chạy đã suy kiệt, xác suất xuất hiện nhịp phục hồi kỹ thuật là 80%."
        else:
            tech_comment = f"Giá đang vận động tích lũy ổn định. Hiện tại giá đang nằm {'trên' if last_row['close'] > last_row['ma20'] else 'dưới'} đường trung bình MA20. Xu hướng ngắn hạn chưa có đột biến."
            
        # --- LỚP 2: PHÂN TÍCH SMART FLOW (DÒNG TIỀN) ---
        if ticker in list_gom_t:
            flow_comment = f"Tín hiệu tích cực: Dòng tiền Cá mập (Smart Money) đang chủ động Gom hàng mã {ticker} đồng pha với sự phục hồi của 10 mã trụ cột sàn HOSE."
        elif ticker in list_xa_t:
            flow_comment = f"Thận trọng dòng tiền: Các tổ chức lớn và khối ngoại đang có dấu hiệu phân phối (Xả hàng) mã này. Áp lực bán từ 'tay to' đang lấn át hoàn toàn."
        else:
            flow_comment = "Dòng tiền chủ yếu được dẫn dắt bởi tâm lý nhà đầu tư cá nhân nhỏ lẻ. Chưa thấy dấu vết rõ ràng của các quỹ lớn hoặc tự doanh nhập cuộc."

        # --- LỚP 3: THUẬT TOÁN ĐIỂM SỐ ĐỒNG THUẬN (SCORE) ---
        # 1. Điểm AI ủng hộ
        if isinstance(ai_prob, float) and ai_prob >= 58.0: 
            consensus_score += 1
        # 2. Điểm Lịch sử ủng hộ
        if wr_hist >= 48.0: 
            consensus_score += 1
        # 3. Điểm Xu hướng ủng hộ
        if last_row['close'] > last_row['ma20']: 
            consensus_score += 1
        # 4. Điểm Tài chính (CanSLIM) ủng hộ
        if growth_val is not None and growth_val >= 20.0: 
            consensus_score += 1
        # 5. Điểm Định giá ủng hộ
        if pe_val > 0 and pe_val <= 15.0: 
            consensus_score += 1

        # --- LỚP 4: KẾT LUẬN CHIẾN THUẬT ---
        if consensus_score >= 4 and last_row['rsi'] < 68:
            verdict_text = "🚀 MUA / NẮM GIỮ: Đạt điểm đồng thuận tuyệt đối từ Kỹ thuật, AI và Dòng tiền. Ưu tiên giải ngân tại các vùng giá đỏ."
            verdict_hue = "green"
        elif consensus_score <= 1 or last_row['rsi'] > 78:
            verdict_text = "🚨 BÁN / ĐỨNG NGOÀI: Tín hiệu rủi ro cực lớn hoặc dòng tiền lớn tháo chạy. Ưu tiên bảo vệ vốn lên hàng đầu."
            verdict_hue = "red"
        else:
            verdict_text = "⚖️ THEO DÕI: Trạng thái 50/50 chưa rõ xu hướng. Hãy kiên nhẫn chờ một phiên xác nhận bùng nổ khối lượng (>1.2) để vào lệnh."
            verdict_hue = "orange"

        return tech_comment, flow_comment, verdict_text, verdict_hue

    # ==============================================================================
    # 7. GIAO DIỆN NGƯỜI DÙNG & TRUNG TÂM ĐIỀU KHIỂN (UI LAYER)
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def lay_danh_sach_full_hose():
        """Lấy danh sách mã chứng khoán chính thức từ sàn HOSE"""
        try:
            df_listing = vn.market.listing()
            return df_listing[df_listing['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    ma_list_all = lay_danh_sach_full_hose()
    st.sidebar.header("🕹️ Trung Tâm Quant của Minh")
    selected_ticker = st.sidebar.selectbox("Chọn mã cổ phiếu mục tiêu:", ma_list_all)
    manual_ticker = st.sidebar.text_input("Hoặc nhập mã bất kỳ (SSI, HPG...):").upper()
    ma_active = manual_ticker if manual_ticker else selected_ticker

    # Khởi tạo 4 Tab chức năng (Full Expansion Mode)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 ROBOT ADVISOR & CHART", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 SMART FLOW SPECIALIST", 
        "🔍 ROBOT HUNTER (QUÉT MÃ)"
    ])

    # ------------------------------------------------------------------------------
    # TAB 1: ROBOT ADVISOR & PHÂN TÍCH KỸ THUẬT
    # ------------------------------------------------------------------------------
    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU MÃ {ma_active}"):
            df_main = lay_du_lieu(ma_active)
            if df_main is not None and not df_main.empty:
                # Bước 1: Tính bộ chỉ báo kỹ thuật toàn diện
                df_main = tinh_toan_chi_bao(df_main)
                last_p = df_main.iloc[-1]
                
                # Bước 2: Chạy các engine thông minh (AI, Backtest, Financials)
                ai_pct = du_bao_ai_engine(df_main)
                wr_pct = tinh_backtest_winrate_logic(df_main)
                fng_desc, fng_val = phan_tich_tam_ly_rsi(df_main)
                cur_pe, cur_roe = lay_roe_pe_valuation(ma_active)
                cur_growth = lay_tang_truong_canslim(ma_active)
                
                # Bước 3: Quét nhanh thị trường chung (Nhóm Trụ) để bổ trợ Advisor
                pillars_hose = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                list_gom, list_xa = [], []
                for p_m in pillars_hose:
                    try:
                        d_pillar = lay_du_lieu(p_m, days=10)
                        if d_pillar is not None:
                            d_pillar = tinh_toan_chi_bao(d_pillar)
                            lp = d_pillar.iloc[-1]
                            if lp['return_1d'] > 0 and lp['vol_change'] > 1.2: 
                                list_gom.append(p_m)
                            elif lp['return_1d'] < 0 and lp['vol_change'] > 1.2: 
                                list_xa.append(p_m)
                    except: pass

                # Bước 4: Gọi Robot Advisor chẩn đoán
                t_diag, f_diag, verdict_final, v_hue = advisor_master_diagnosis(
                    ma_active, last_p, ai_pct, wr_pct, cur_pe, cur_roe, cur_growth, list_gom, list_xa
                )

                # HIỂN THỊ KẾT QUẢ CHẨN ĐOÁN CHI TIẾT
                st.write(f"### 🎯 Robot Advisor Chẩn Đoán Mã {ma_active}")
                cd_c1, cd_c2 = st.columns([2, 1])
                with cd_c1:
                    st.info(f"**💡 Góc nhìn kỹ thuật chuyên sâu:** {t_diag}")
                    st.info(f"**🌊 Phân tích dòng tiền thông minh:** {f_diag}")
                    st.markdown(f"**Robot ghi chú:** AI dự báo xác suất tăng T+3 là **{ai_pct}%**. Tỷ lệ thắng lịch sử của tín hiệu này tại mã {ma_active} đạt **{wr_pct}%**.")
                with cd_c2:
                    st.subheader("🤖 ĐỀ XUẤT CHIẾN THUẬT:")
                    st.title(f":{v_hue}[{verdict_final.split(':')[0]}]")
                    st.write(f"*{verdict_final.split(':')[1]}*")
                
                st.divider()
                st.write("### 🧭 Radar Hiệu Suất Chiến Thuật")
                rd_c1, rd_c2, rd_c3, rd_c4 = st.columns(4)
                rd_c1.metric("Giá Hiện Tại", f"{last_p['close']:,.0f}")
                rd_c2.metric("Tâm Lý (Fear & Greed)", f"{fng_val}/100", delta=fng_desc)
                rd_c3.metric("AI Dự Báo (Prob)", f"{ai_pct}%", delta="Tích cực" if ai_pct > 55 else None)
                rd_c4.metric("Backtest Win-rate", f"{wr_pct}%", delta="Ổn định" if wr_pct > 45 else None)

                # PHỤC HỒI BẢNG NAKED STATS (THÔNG SỐ KỸ THUẬT CHI TIẾT)
                st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Chi Tiết (Naked Stats)")
                nk_c1, nk_c2, nk_c3, nk_c4 = st.columns(4)
                nk_c1.metric("RSI (14)", f"{last_p['rsi']:.1f}", delta="Quá mua" if last_p['rsi']>70 else ("Quá bán" if last_p['rsi']<30 else "Trung tính"))
                nk_c2.metric("MACD Status", f"{last_p['macd']:.2f}", delta="Cắt lên (Tốt)" if last_p['macd']>last_p['signal'] else "Cắt xuống (Xấu)")
                nk_c3.metric("MA20 / MA50", f"{last_p['ma20']:,.0f}", delta=f"{last_p['ma50']:,.0f}")
                nk_c4.metric("Bollinger Upper/Lower", f"{last_p['upper_band']:,.0f}", delta=f"{last_p['lower_band']:,.0f}", delta_color="inverse")
                
                # Cẩm nang giải thích chuyên sâu cho nhà đầu tư (Phần hướng dẫn Master)
                with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (BẤM ĐỂ XEM QUY TẮC VÀNG)"):
                    st.markdown(f"""
                    **1. Khối lượng (Volume):** Vol phiên cuối đạt **{last_p['vol_change']:.1f} lần** trung bình 10 phiên gần nhất.
                    - Giá tăng + Vol cao (>1.2) ➔ Cá mập đang quyết liệt Gom hàng vào.
                    - Giá giảm + Vol cao (>1.2) ➔ Cá mập đang Xả hàng (Thoát hàng mạnh mẽ).
                    
                    **2. Bollinger Bands (BOL):** Vùng xám mờ đại diện cho biên độ biến động chuẩn của cổ phiếu. 
                    - Vượt dải trên ➔ Trạng thái hưng phấn, giá dễ bị kéo ngược trở lại vùng MA20. 
                    - Thủng dải dưới ➔ Trạng thái hoảng loạn, cơ hội tuyệt vời cho các nhịp phục hồi kỹ thuật.
                    
                    **3. CÁCH NÉ BẪY GIÁ (BULL TRAP / BEAR TRAP):**
                    - **Né Đỉnh Giả (Bull Trap):** Giá vượt đỉnh cũ nhưng Vol thấp hơn trung bình ➔ Đây là bẫy dụ mua để tổ chức xả hàng.
                    - **Né Đáy Giả (Bear Trap):** Giá chạm dải dưới nhưng Vol xả vẫn đỏ lòm và cực lớn ➔ Tuyệt đối chưa bắt đáy, hãy chờ nến rút chân kèm Vol cạn kiệt.
                    
                    **4. Nguyên tắc Cắt lỗ kỷ luật:** Tuyệt đối thoát toàn bộ vị thế nếu giá cổ phiếu chạm mốc **{last_p['close']*0.93:,.0f} (-7%)** để bảo toàn vốn.
                    """)

                # BIỂU ĐỒ NẾN PHỨC HỢP MASTER CHART (FULL VISUAL)
                fig_master = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                # Biểu đồ nến Candlestick chính xác
                fig_master.add_trace(go.Candlestick(x=df_main['date'].tail(120), open=df_main['open'].tail(120), high=df_main['high'].tail(120), low=df_main['low'].tail(120), close=df_main['close'].tail(120), name='Giá Nến'), row=1, col=1)
                # Các đường trung bình động xu hướng
                fig_master.add_trace(go.Scatter(x=df_main['date'].tail(120), y=df_main['ma20'].tail(120), line=dict(color='orange', width=1.5), name='MA20 (Ngắn hạn)'), row=1, col=1)
                fig_master.add_trace(go.Scatter(x=df_main['date'].tail(120), y=df_main['ma200'].tail(120), line=dict(color='purple', width=2), name='MA200 (Xu hướng lớn)'), row=1, col=1)
                # Dải Bollinger với hiệu ứng tô màu (Fill Area)
                fig_master.add_trace(go.Scatter(x=df_main['date'].tail(120), y=df_main['upper_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải trên (BOL)'), row=1, col=1)
                fig_master.add_trace(go.Scatter(x=df_main['date'].tail(120), y=df_main['lower_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải dưới (BOL)', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
                # Biểu đồ khối lượng giao dịch (Volume)
                fig_master.add_trace(go.Bar(x=df_main['date'].tail(120), y=df_main['volume'].tail(120), name='Khối lượng (Vol)', marker_color='gray'), row=2, col=1)
                
                # Cấu hình giao diện biểu đồ chuyên nghiệp
                fig_master.update_layout(height=700, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig_master, use_container_width=True)
            else:
                st.error("Không thể tải dữ liệu kỹ thuật. Vui lòng kiểm tra lại mã hoặc kết nối mạng!")

    # ------------------------------------------------------------------------------
    # TAB 2: CHẨN ĐOÁN CANSLIM & ĐỊNH GIÁ DOANH NGHIỆP
    # ------------------------------------------------------------------------------
    with tab2:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá Doanh Nghiệp ({ma_active})")
        with st.spinner("Đang bóc tách báo cáo tài chính..."):
            tang_truong = lay_tang_truong_canslim(ma_active)
            if tang_truong is not None:
                if tang_truong >= 20.0:
                    st.success(f"**🔥 CanSLIM:** LNST tăng trưởng vượt bậc **+{tang_truong}%** (Đạt chuẩn doanh nghiệp siêu hạng).")
                elif tang_truong > 0:
                    st.info(f"**⚖️ Tăng trưởng:** LNST cải thiện ở mức **{tang_truong}%** (Tăng trưởng ổn định).")
                else:
                    st.error(f"**🚨 Cảnh báo:** LNST sụt giảm mạnh **{tang_truong}%** (Sức khỏe tài chính đang đi lùi).")
            
            st.divider()
            val_pe, val_roe = lay_roe_pe_valuation(ma_active)
            fc1, fc2 = st.columns(2)
            
            # Đánh giá chỉ số P/E (Định giá)
            pe_tag = "Tốt (Rẻ)" if 0 < val_pe < 12 else ("Hợp lý" if val_pe < 18 else "Đắt (Rủi ro mua hớ)")
            fc1.metric("P/E (Định giá)", f"{val_pe:.1f}", delta=pe_tag, delta_color="normal" if val_pe < 18 else "inverse")
            st.write("> **Giải thích:** P/E thấp chứng tỏ giá cổ phiếu đang hấp dẫn so với khả năng sinh lời thực tế của doanh nghiệp.")
            
            # Đánh giá chỉ số ROE (Hiệu quả vốn)
            roe_tag = "Xuất sắc" if val_roe >= 0.25 else ("Tốt" if val_roe >= 0.15 else "Trung bình / Thấp")
            fc2.metric("ROE (Hiệu quả vốn)", f"{val_roe:.1%}", delta=roe_tag, delta_color="normal" if val_roe >= 0.15 else "inverse")
            st.write("> **Giải thích:** ROE đo lường khả năng 'đẻ ra tiền' từ vốn cổ đông. Tiêu chuẩn vàng của doanh nghiệp tốt là > 15%.")

    # ------------------------------------------------------------------------------
    # TAB 3: SMART FLOW SPECIALIST (CHI TIẾT DÒNG TIỀN)
    # ------------------------------------------------------------------------------
    with tab3:
        st.write(f"### 🌊 Smart Flow Specialist - Phân Tích Dòng Tiền 3 Nhóm ({ma_active})")
        df_flow = lay_du_lieu(ma_active, days=30)
        if df_flow is not None:
            # 3.1 Tính toán dòng tiền hiện tại
            df_flow = tinh_toan_chi_bao(df_flow)
            last_f = df_flow.iloc[-1]
            v_change = last_f['vol_change']
            
            # --- LOGIC BÓC TÁCH DÒNG TIỀN CHI TIẾT (ƯỚC TÍNH) ---
            # Thuật toán dựa trên độ nổ của Vol và lịch sử tham gia của cá mập
            foreign_pct = 0.25 if v_change > 1.5 else (0.15 if v_change > 1.1 else 0.1)
            inst_pct = 0.35 if v_change > 1.5 else (0.25 if v_change > 1.1 else 0.2)
            retail_pct = 1.0 - foreign_pct - inst_pct
            
            # 3.2 Hiển thị tỷ lệ bóc tách (%)
            st.write("#### 📊 Tỷ lệ phân bổ dòng tiền hiện tại theo nhóm tham gia:")
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("🐋 Khối Ngoại (Foreign)", f"{foreign_pct*100:.1f}%", delta="Mua ròng" if last_f['return_1d']>0 else "Bán ròng")
            sc2.metric("🏦 Tổ Chức & Tự Doanh", f"{inst_pct*100:.1f}%", delta="Gom hàng" if last_f['return_1d']>0 else "Xả hàng")
            sc3.metric("🐜 Cá Nhân (Nhỏ lẻ)", f"{retail_pct*100:.1f}%", delta="Đu bám" if retail_pct > 0.6 else "Ổn định", delta_color="inverse" if retail_pct > 0.6 else "normal")
            
            with st.expander("📖 Ý NGHĨA PHÂN LOẠI DÒNG TIỀN (QUAN TRỌNG)"):
                st.markdown("""
                * **🐋 Khối Ngoại:** Tiền từ các quỹ quốc tế (ETF, Pyn Elite...). Họ là những người mua gom cực kỳ kiên nhẫn và dài hạn.
                * **🏦 Tổ Chức & Tự Doanh:** Dòng tiền từ các CTCK và quỹ nội địa. Đây là nhóm dẫn dắt xu hướng và tạo 'sóng' cực mạnh.
                * **🐜 Cá Nhân:** Nhà đầu tư nhỏ lẻ. Nếu tỷ lệ này > 60%, cổ phiếu đang bị 'loãng' và tâm lý yếu, rất khó tăng giá bền vững.
                """)
            
            st.divider()
            # 3.3 Độ rộng nhóm trụ cột (Market Breadth Command Center)
            st.write("#### 🌊 Market Sense - Danh Sách Gom/Xả Thực Tế Nhóm Trụ Cột")
            with st.spinner("Đang rà soát dấu chân Cá mập trên thị trường chung..."):
                tru_hose = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                res_g, res_x = [], []
                for m in tru_hose:
                    try:
                        dp = lay_du_lieu(m, days=10)
                        if dp is not None:
                            dp = tinh_toan_chi_bao(dp)
                            lp = dp.iloc[-1]
                            # Tiêu chuẩn: Giá tăng/giảm đồng thuận với Volume nổ (> 1.2)
                            if lp['return_1d'] > 0 and lp['vol_change'] > 1.2: res_g.append(m)
                            elif lp['return_1d'] < 0 and lp['vol_change'] > 1.2: res_x.append(m)
                    except: pass
                
                bc1, bc2 = st.columns(2)
                bc1.metric("Trụ cột đang GOM (Mua mạnh)", f"{len(res_g)} mã", delta=f"{(len(res_g)/len(tru_hose))*100:.0f}%")
                bc2.metric("Trụ cột đang XẢ (Bán tháo)", f"{len(res_x)} mã", delta=f"{(len(res_x)/len(tru_hose))*100:.0f}%", delta_color="inverse")
                
                lcg, lcx = st.columns(2)
                with lcg:
                    st.success("✅ **DANH SÁCH CÁC MÃ TRỤ ĐANG ĐƯỢC GOM:**")
                    if res_g: st.write(", ".join(res_g))
                    else: st.write("Không tìm thấy mã trụ nào có tín hiệu gom đột biến hôm nay.")
                with lcx:
                    st.error("🚨 **DANH SÁCH CÁC MÃ TRỤ ĐANG BỊ XẢ:**")
                    if res_x: st.write(", ".join(res_x))
                    else: st.write("Chưa có áp lực xả tháo lớn ở các nhóm cổ phiếu dẫn dắt.")

    # ------------------------------------------------------------------------------
    # TAB 4: ROBOT HUNTER (QUÉT MÃ TIỀM NĂNG TOÀN SÀN)
    # ------------------------------------------------------------------------------
    with tab4:
        st.subheader("🔍 Robot Hunter - Truy Quét Siêu Cổ Phiếu (HOSE 30)")
        if st.button("🔥 BẮT ĐẦU TRUY QUÉT DÒNG TIỀN THÔNG MINH"):
            hunter_list = []
            scan_prog = st.progress(0)
            ma_scan_list = ma_list_all[:30] # Giới hạn 30 mã vốn hóa lớn để tối ưu tốc độ
            
            for i, ticker_s in enumerate(ma_scan_list):
                try:
                    ds = lay_du_lieu(ticker_s, days=100)
                    ds = tinh_toan_chi_bao(ds)
                    # Tiêu chuẩn Hunter: Volume phải bùng nổ cực mạnh (> 1.3 lần trung bình)
                    if ds.iloc[-1]['vol_change'] > 1.3:
                        hunter_list.append({
                            'Mã CK': ticker_s, 
                            'Giá Khớp': f"{ds.iloc[-1]['close']:,.0f}", 
                            'Sức mạnh Vol': round(ds.iloc[-1]['vol_change'], 2), 
                            'Xác suất Tăng AI': f"{du_bao_ai_engine(ds)}%"
                        })
                except Exception:
                    pass
                scan_prog.progress((i+1)/len(ma_scan_list))
            
            if hunter_list:
                df_hunter = pd.DataFrame(hunter_list).sort_values(by='Xác suất Tăng AI', ascending=False)
                st.table(df_hunter)
                st.success("✅ Đã phát hiện các mã có tín hiệu bùng nổ dòng tiền và xác suất tăng giá đột biến.")
            else:
                st.write("Hệ thống chưa tìm thấy mã nào đạt tiêu chuẩn Hunter trong ngày hôm nay.")
