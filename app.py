import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Thư viện AI và Xử lý ngôn ngữ
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo các tài nguyên ngôn ngữ được tải đầy đủ để tránh lỗi runtime
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT TRUY CẬP (GATEKEEPER)
# ==============================================================================
def check_password():
    """Hàm xác thực mật mã dành riêng cho Minh"""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔑 Nhập mật mã của Minh:", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    # Cấu hình giao diện chuẩn Quant System
    st.set_page_config(page_title="Quant System V9.0 Final Master", layout="wide")
    st.title("🛡️ Quant System V9.0: Advisor Master & Quyết Định Chiến Thuật")

    s = Vnstock()

    # ==============================================================================
    # 2. HÀM XỬ LÝ DỮ LIỆU (DATA LAYER)
    # ==============================================================================
    def lay_du_lieu(ticker, days=1000):
        """Lấy dữ liệu giá lịch sử, ưu tiên Vnstock, dự phòng Yahoo Finance"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            df = s.stock.quote.history(symbol=ticker, start=start_date, end=end_date)
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                return df
        except Exception:
            pass
        
        try:
            # Dự phòng cho mã SSI, Ngân hàng hoặc khi Vnstock bị giới hạn truy cập
            symbol = f"{ticker}.VN" if ticker != "VNINDEX" else "^VNINDEX"
            yt = yf.download(symbol, period="3y", progress=False)
            yt = yt.reset_index()
            # Xử lý Multi-index của Yahoo Finance nếu có
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except Exception:
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (LOGIC LAYER)
    # ==============================================================================
    def tinh_toan_chi_bao(df):
        """Tính toán các chỉ số: MA, Bollinger, RSI, MACD, Money Flow"""
        df = df.copy()
        
        # Các đường trung bình động (Moving Averages)
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma50'] = df['close'].rolling(window=50).mean()
        df['ma200'] = df['close'].rolling(window=200).mean()
        
        # Dải Bollinger Bands (BOL) - Vùng biên biến động
        df['std'] = df['close'].rolling(window=20).std()
        df['upper_band'] = df['ma20'] + (df['std'] * 2)
        df['lower_band'] = df['ma20'] - (df['std'] * 2)
        
        # Chỉ số sức mạnh tương đối (RSI 14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        # Chỉ báo MACD (12, 26, 9)
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Các chỉ số phục vụ mô hình AI và Smart Flow
        df['return_1d'] = df['close'].pct_change()
        df['vol_change'] = df['volume'] / df['volume'].rolling(window=10).mean()
        df['money_flow'] = df['close'] * df['volume']
        df['volatility'] = df['return_1d'].rolling(window=20).std()
        
        # Logic xác định Gom/Xả dựa trên Volume và Giá
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1.2), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1.2), -1, 0))
        
        return df.dropna()

    # ==============================================================================
    # 4. CHẨN ĐOÁN TÂM LÝ & BACKTEST LỊCH SỬ
    # ==============================================================================
    def chan_doan_tam_ly(df):
        """Phân tích tâm lý dựa trên RSI (Chỉ số Fear & Greed Index)"""
        last_rsi = df.iloc[-1]['rsi']
        if last_rsi > 75:
            label = "🔥 CỰC KỲ THAM LAM (QUÁ MUA)"
        elif last_rsi > 60:
            label = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif last_rsi < 30:
            label = "💀 CỰC KỲ SỢ HÃI (QUÁ BÁN)"
        elif last_rsi < 42:
            label = "😨 SỢ HÃI (BI QUAN)"
        else:
            label = "🟡 TRUNG LẬP"
        return label, round(last_rsi, 1)

    def tinh_ty_le_thang(df):
        """Kiểm tra xác suất thắng lịch sử cho tín hiệu RSI/MACD"""
        win_count = 0
        total_signals = 0
        # Duyệt qua dữ liệu lịch sử
        for i in range(100, len(df)-10):
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]:
                total_signals += 1
                # Kiểm tra lợi nhuận sau 10 phiên
                future_prices = df['close'].iloc[i+1 : i+11]
                if any(future_prices > df['close'].iloc[i] * 1.05):
                    win_count += 1
        
        if total_signals == 0:
            return 0.0
        return round((win_count / total_signals) * 100, 1)

    # ==============================================================================
    # 5. MÔ HÌNH DỰ BÁO AI (PREDICTIVE ENGINE)
    # ==============================================================================
    def du_bao_ai(df):
        """Dự báo xác suất tăng giá T+3 bằng thuật toán Random Forest"""
        if len(df) < 200:
            return "N/A"
        
        df_copy = df.copy()
        # Mục tiêu: Giá tăng > 2% sau 3 phiên giao dịch
        df_copy['target'] = (df_copy['close'].shift(-3) > df_copy['close'] * 1.02).astype(int)
        
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data = df_copy.dropna()
        
        X = data[features]
        y = data['target']
        
        # Huấn luyện mô hình
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X[:-3], y[:-3])
        
        # Dự báo cho phiên gần nhất
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    # ==============================================================================
    # 6. PHÂN TÍCH TÀI CHÍNH & CANSLIM (FUNDAMENTAL ENGINE)
    # ==============================================================================
    def tinh_tang_truong_lnst(ticker):
        """Tính toán tăng trưởng LNST quý gần nhất so với cùng kỳ năm trước"""
        try:
            df_inc = s.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            # Tự động tìm cột lợi nhuận sau thuế
            col_search = [c for c in df_inc.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])]
            if col_search:
                lnst_col = col_search[0]
                q1_val = float(df_inc.iloc[0][lnst_col])
                q5_val = float(df_inc.iloc[4][lnst_col])
                if q5_val > 0:
                    return round(((q1_val - q5_val) / q5_val) * 100, 1)
        except Exception:
            pass
        
        try:
            # Fallback sang Yahoo Finance cho các mã SSI/Ngân hàng
            info = yf.Ticker(f"{ticker}.VN").info
            growth = info.get('earningsQuarterlyGrowth')
            if growth is not None:
                return round(growth * 100, 1)
        except Exception:
            pass
        return None

    def lay_chi_so_co_ban(ticker):
        """Lấy các chỉ số định giá P/E và hiệu quả ROE"""
        pe_v, roe_v = 0, 0
        try:
            ratio = s.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe_v = ratio.get('ticker_pe', ratio.get('pe', 0))
            roe_v = ratio.get('roe', 0)
        except Exception:
            pass
            
        if pe_v <= 0:
            try:
                info = yf.Ticker(f"{ticker}.VN").info
                pe_v = info.get('trailingPE', 0)
                roe_v = info.get('returnOnEquity', 0)
            except Exception:
                pass
        return pe_v, roe_v

    # ==============================================================================
    # 7. 🧠 HỆ THỐNG ROBOT ADVISOR: CHẨN ĐOÁN CHI TIẾT & ĐỀ XUẤT (V9.0 MASTER)
    # ==============================================================================
    def robot_advisor_diagnostics(ticker, last, ai_p, wr, pe, roe, growth, list_gom, list_xa):
        """Hệ thống ra quyết định dựa trên sự đồng thuận đa tầng"""
        diag_tech = ""
        diag_flow = ""
        action_verdict = ""
        action_color = ""
        logic_score = 0
        
        # --- LỚP 1: PHÂN TÍCH KỸ THUẬT ---
        if last['rsi'] > 72:
            diag_tech = f"Giá của {ticker} đang nằm trong vùng Quá mua (RSI: {last['rsi']:.1f}). Áp lực chốt lời đang tăng dần, rủi ro điều chỉnh về MA20 là rất lớn. KHÔNG NÊN MUA ĐUỔI."
        elif last['rsi'] < 35:
            diag_tech = f"Giá của {ticker} đang bị chiết khấu quá mức (RSI: {last['rsi']:.1f}). Đây là vùng Quá bán, thường xuất hiện nhịp hồi kỹ thuật mạnh. CƠ HỘI BẮT ĐÁY."
        else:
            diag_tech = f"Giá đang vận động tích lũy ổn định trên đường MA20 ({last['ma20']:,.0f}). Xu hướng ngắn hạn vẫn đang được duy trì tốt."
            
        # --- LỚP 2: PHÂN TÍCH DÒNG TIỀN (SMART FLOW) ---
        if ticker in list_gom:
            diag_flow = f"Tín hiệu cực kỳ tích cực: Dòng tiền lớn (Cá mập) đang Gom hàng chủ động tại mã {ticker} đồng thuận với nhóm trụ cột thị trường."
        elif ticker in list_xa:
            diag_flow = f"Cảnh báo: Dòng tiền thông minh đang rút ra (Xả hàng) khỏi {ticker}. Áp lực phân phối từ các tổ chức đang chiếm ưu thế."
        else:
            diag_flow = "Dòng tiền chủ yếu đến từ các nhà đầu tư cá nhân nhỏ lẻ, chưa thấy sự nhập cuộc rõ ràng của các 'tay chơi lớn'."

        # --- LỚP 3: THUẬT TOÁN ĐIỂM SỐ ĐỒNG THUẬN ---
        if isinstance(ai_p, float) and ai_p >= 55.0: logic_score += 1
        if wr >= 45.0: logic_score += 1
        if last['close'] > last['ma20']: logic_score += 1
        if growth is not None and growth >= 15.0: logic_score += 1
        if pe > 0 and pe <= 16.0: logic_score += 1

        # --- LỚP 4: KẾT LUẬN & ĐỀ XUẤT ---
        if logic_score >= 4 and last['rsi'] < 68:
            action_verdict = "🚀 MUA / NẮM GIỮ: Các chỉ số Kỹ thuật, Dòng tiền và Cơ bản đều đồng thuận. Đây là điểm vào lệnh an toàn."
            action_color = "green"
        elif logic_score <= 1 or last['rsi'] > 78:
            action_verdict = "🚨 BÁN / ĐỨNG NGOÀI: Các chỉ số đang ở vùng rủi ro cực đại hoặc nội lực doanh nghiệp suy giảm. Bảo vệ vốn là trên hết."
            action_color = "red"
        else:
            action_verdict = "⚖️ THEO DÕI: Tín hiệu chưa thực sự bứt phá. Hãy kiên nhẫn chờ một phiên nổ Volume (>1.2) để xác nhận xu hướng."
            action_color = "orange"

        return diag_tech, diag_flow, action_verdict, action_color

    # ==============================================================================
    # 8. GIAO DIỆN NGƯỜI DÙNG & ĐIỀU KHIỂN CHIẾN THUẬT
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def lay_danh_sach_all():
        try:
            return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except Exception:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_hose_stocks = lay_danh_sach_all()
    st.sidebar.header("🕹️ Trung Tâm Điều Khiển")
    sel_stock = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_hose_stocks)
    inp_stock = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    active_mã = inp_stock if inp_stock else sel_stock

    # Phân bổ các Tab chức năng (SỬA LỖI NAMEERROR)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 ROBOT ADVISOR & CHART", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 MARKET SENSE (COMMAND)", 
        "🔍 TRUY QUÉT HUNTER"
    ])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {active_mã}"):
            df_main = lay_du_lieu(active_mã)
            if df_main is not None and not df_main.empty:
                df_main = tinh_toan_chi_bao(df_main)
                row_last = df_main.iloc[-1]
                
                # Thực hiện các quy trình phân tích
                ai_pct = du_bao_ai(df_main)
                wr_pct = tinh_ty_le_thang(df_main)
                m_label, m_score = chan_doan_tam_ly(df_main)
                s_pe, s_roe = lay_chi_so_co_ban(active_mã)
                s_growth = tinh_tang_truong_lnst(active_mã)
                
                # Quét nhanh nhóm trụ dẫn dắt
                pillars = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                gom_mã, xa_mã = [], []
                for p in pillars:
                    try:
                        p_data = lay_du_lieu(p, days=10)
                        if p_data is not None:
                            p_data = tinh_toan_chi_bao(p_data)
                            p_last = p_data.iloc[-1]
                            if p_last['return_1d'] > 0 and p_last['vol_change'] > 1.2: gom_mã.append(p)
                            elif p_last['return_1d'] < 0 and p_last['vol_change'] > 1.2: xa_mã.append(p)
                    except Exception: pass

                # GỌI HỆ THỐNG ADVISOR PHÂN TÍCH
                t_diag, f_diag, verdict_str, v_hue = robot_advisor_diagnostics(active_mã, row_last, ai_pct, wr_pct, s_pe, s_roe, s_growth, gom_mã, xa_mã)

                st.write(f"### 🎯 Chẩn Đoán Robot Advisor cho {active_mã}")
                diag_col1, diag_col2 = st.columns([2, 1])
                with diag_col1:
                    st.info(f"**💡 Góc nhìn kỹ thuật:** {t_diag}")
                    st.info(f"**🌊 Góc nhìn dòng tiền:** {f_diag}")
                    st.markdown(f"**Robot ghi chú:** AI dự báo xác suất tăng là **{ai_pct}%**. Win-rate lịch sử của mã là **{wr_pct}%**.")
                with diag_col2:
                    st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                    st.title(f":{v_hue}[{verdict_str.split(':')[0]}]")
                    st.write(f"*{verdict_str.split(':')[1]}*")
                
                st.divider()
                st.write("### 🧭 Bảng Chỉ Số Kỹ Thuật (Naked Stats)")
                met1, met2, met3, met4 = st.columns(4)
                met1.metric("Giá Hiện Tại", f"{row_last['close']:,.0f}")
                met2.metric("Tâm Lý Thị Trường", f"{m_score}/100", delta=m_label)
                met3.metric("RSI (14)", f"{row_last['rsi']:.1f}", delta="Quá mua" if row_last['rsi']>70 else ("Quá bán" if row_last['rsi']<30 else None))
                met4.metric("MACD Status", f"{row_last['macd']:.2f}", delta="Cắt lên (Tốt)" if row_last['macd']>row_last['signal'] else "Cắt xuống (Xấu)")
                
                with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (QUY TẮC VÀNG)"):
                    st.markdown(f"""
                    **1. Khối lượng (Volume):** Vol phiên hiện tại đạt **{row_last['vol_change']:.1f} lần** trung bình 10 phiên.
                    - Giá tăng + Vol cao (>1.2) ➔ Cá mập đang Gom hàng.
                    - Giá giảm + Vol cao (>1.2) ➔ Cá mập đang Xả (Tháo hàng).
                    
                    **2. Bollinger Bands (BOL):** Vùng xám mờ trên biểu đồ là dải vận động an toàn. 
                    - Vượt dải trên ➔ Hưng phấn quá đà, có xu hướng chỉnh vào trong. 
                    - Thủng dải dưới ➔ Hoảng loạn cực độ, có xu hướng hồi kỹ thuật.
                    
                    **3. CÁCH NÉ BẪY GIÁ (BULL TRAP / BEAR TRAP):**
                    - **Né Đỉnh Giả:** Giá vượt đỉnh nhưng Vol thấp hơn trung bình ➔ Bẫy dụ mua để xả.
                    - **Né Đáy Giả:** Giá chạm dải dưới nhưng Vol xả vẫn cực lớn ➔ Đừng bắt đáy vội, hãy chờ nến rút chân kèm Vol thấp.
                    
                    **4. Cắt lỗ kỷ luật:** Tuyệt đối thoát hàng nếu giá chạm mốc **{row_last['close']*0.93:,.0f} (-7%)**.
                    """)

                # BIỂU ĐỒ NẾN PHỨC HỢP MASTER CHART
                fig_final = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig_final.add_trace(go.Candlestick(x=df_main['date'].tail(120), open=df_main['open'].tail(120), high=df_main['high'].tail(120), low=df_main['low'].tail(120), close=df_main['close'].tail(120), name='Giá'), row=1, col=1)
                fig_final.add_trace(go.Scatter(x=df_main['date'].tail(120), y=df_main['ma20'].tail(120), line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                fig_final.add_trace(go.Scatter(x=df_main['date'].tail(120), y=df_main['ma200'].tail(120), line=dict(color='purple', width=2), name='MA200 (Dài hạn)'), row=1, col=1)
                # Bollinger Bands với hiệu ứng Fill màu xám
                fig_final.add_trace(go.Scatter(x=df_main['date'].tail(120), y=df_main['upper_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải trên'), row=1, col=1)
                fig_final.add_trace(go.Scatter(x=df_main['date'].tail(120), y=df_main['lower_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải dưới', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
                # Volume Chart
                fig_final.add_trace(go.Bar(x=df_main['date'].tail(120), y=df_main['volume'].tail(120), name='Khối lượng', marker_color='gray'), row=2, col=1)
                
                fig_final.update_layout(height=650, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig_final, use_container_width=True)
            else:
                st.error("Lỗi: Không thể tải dữ liệu. Vui lòng kiểm tra mã hoặc kết nối!")

    with tab2:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá Doanh Nghiệp ({active_mã})")
        with st.spinner("Đang phân tích báo cáo tài chính..."):
            g_pct = tinh_tang_truong_lnst(active_mã)
            if g_pct is not None:
                if g_pct >= 20.0:
                    st.success(f"**🔥 CanSLIM:** LNST tăng trưởng đột phá **+{g_pct}%** (Đạt chuẩn doanh nghiệp tăng trưởng).")
                elif g_pct > 0:
                    st.info(f"**⚖️ Tăng trưởng:** LNST cải thiện **{g_pct}%** (Mức tăng ổn định).")
                else:
                    st.error(f"**🚨 Cảnh báo:** LNST sụt giảm mạnh **{g_pct}%** (Sức khỏe tài chính suy yếu).")
            
            st.divider()
            pe_cur, roe_cur = lay_chi_so_co_ban(active_mã)
            fc1, fc2 = st.columns(2)
            
            pe_tag = "Tốt (Rẻ)" if 0 < pe_cur < 12 else ("Hợp lý" if pe_cur < 18 else "Đắt (Rủi ro)")
            fc1.metric("P/E (Định giá)", f"{pe_cur:.1f}", delta=pe_tag, delta_color="normal" if pe_cur < 18 else "inverse")
            st.write("> Chỉ số P/E đo lường giá trị tương quan với lợi nhuận. P/E thấp chứng tỏ cổ phiếu đang rẻ.")
            
            roe_tag = "Xuất sắc" if roe_cur >= 0.25 else ("Tốt" if roe_cur >= 0.15 else "Trung bình")
            fc2.metric("ROE (Hiệu quả vốn)", f"{roe_cur:.1%}", delta=roe_tag, delta_color="normal" if roe_cur >= 0.15 else "inverse")
            st.write("> ROE đo lường khả năng sinh lời của đồng vốn cổ đông. Tiêu chuẩn vàng doanh nghiệp tốt là > 15%.")

    with tab3:
        st.write("### 🌊 Market Sense - Danh Sách Gom/Xả Trụ Cột")
        with st.spinner("Đang quét dấu chân Cá mập trên thị trường..."):
            hose_pillars = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
            gom_res, xa_res = [], []
            
            for m in hose_pillars:
                try:
                    d_p = lay_du_lieu(m, days=10)
                    if d_p is not None:
                        d_p = tinh_toan_chi_bao(d_p)
                        l_p = d_p.iloc[-1]
                        # Logic Gom/Xả: Giá xanh/đỏ + Vol nổ > 1.2
                        if l_p['return_1d'] > 0 and l_p['vol_change'] > 1.2:
                            gom_res.append(m)
                        elif l_p['return_1d'] < 0 and l_p['vol_change'] > 1.2:
                            xa_res.append(m)
                except Exception:
                    pass
            
            bc1, bc2 = st.columns(2)
            bc1.metric("Trụ đang GOM", f"{len(gom_res)} mã", delta=f"{(len(gom_res)/len(hose_pillars))*100:.0f}%", delta_color="normal")
            bc2.metric("Trụ đang XẢ", f"{len(xa_res)} mã", delta=f"{(len(xa_res)/len(hose_pillars))*100:.0f}%", delta_color="inverse")
            
            st.divider()
            cl_g, cl_x = st.columns(2)
            with cl_g:
                st.success("✅ **DANH SÁCH MÃ ĐANG ĐƯỢC GOM:**")
                if gom_res: st.write(", ".join(gom_res))
                else: st.write("Không tìm thấy mã trụ nào có tín hiệu gom đột biến.")
            with cl_x:
                st.error("🚨 **DANH SÁCH MÃ ĐANG BỊ XẢ:**")
                if xa_res: st.write(", ".join(xa_res))
                else: st.write("Không có áp lực bán tháo lớn ở nhóm trụ dẫn dắt.")
            
            if len(xa_res) > len(gom_res):
                st.warning("⚠️ Nhận định: Áp lực bán ở nhóm trụ lớn hơn lực gom. Thị trường rủi ro cao.")
            else:
                st.info("ℹ️ Nhận định: Lực gom ở nhóm trụ đang ổn định. Thị trường có bệ đỡ.")

    with tab4:
        st.subheader("🔍 Robot Hunter - Truy Quét Top 30 HOSE")
        if st.button("🔥 CHẠY RÀ SOÁT HUNTER"):
            results_h = []
            h_progress = st.progress(0)
            stocks_to_scan = all_hose_stocks[:30]
            
            for i, tick_s in enumerate(stocks_to_scan):
                try:
                    df_s = lay_du_lieu(tick_s, days=100)
                    df_s = tinh_toan_chi_bao(df_s)
                    # Tiêu chuẩn Hunter: Volume phải nổ cực mạnh (> 1.3)
                    if df_s.iloc[-1]['vol_change'] > 1.3:
                        results_h.append({
                            'Mã': tick_s, 
                            'Giá': df_s.iloc[-1]['close'], 
                            'Sức mạnh Vol': round(df_s.iloc[-1]['vol_change'], 2), 
                            'AI Dự báo Tăng': f"{du_bao_ai(df_s)}%"
                        })
                except Exception:
                    pass
                h_progress.progress((i+1)/len(target_stocks) if 'target_stocks' in locals() else (i+1)/30)
            
            if results_h:
                df_final_h = pd.DataFrame(results_h).sort_values(by='AI Dự báo Tăng', ascending=False)
                st.table(df_final_h)
                st.success("✅ Đã phát hiện các mã có tín hiệu bùng nổ dòng tiền và xác suất tăng cao.")
            else:
                st.write("Chưa có mã nào trong Top 30 đạt tiêu chuẩn Hunter hôm nay.")
