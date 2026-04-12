import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Thư viện AI và xử lý ngôn ngữ
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo các tài nguyên ngôn ngữ được tải đầy đủ
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & XÁC THỰC NGƯỜI DÙNG
# ==============================================================================
def check_password():
    """Hàm kiểm tra mật mã truy cập riêng cho Minh"""
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
    # Cấu hình giao diện chính
    st.set_page_config(page_title="Quant System V9.0 Advisor Master", layout="wide")
    st.title("🛡️ Quant System V9.0: Hệ Thống Advisor Master & Quyết Định Chiến Thuật")

    s = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU (VNSTOCK & YFINANCE FALLBACK)
    # ==============================================================================
    def lay_du_lieu(ticker, days=1000):
        """Lấy dữ liệu lịch sử giá từ Vnstock, tự động dự phòng sang Yahoo Finance"""
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
            # Fallback cho các mã ngân hàng, chứng khoán (SSI) hoặc khi API Vnstock nghẽn
            symbol = f"{ticker}.VN" if ticker != "VNINDEX" else "^VNINDEX"
            yt = yf.download(symbol, period="3y", progress=False)
            yt = yt.reset_index()
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except Exception:
            return None

    # ==============================================================================
    # 3. TÍNH TOÁN CÁC CHỈ BÁO KỸ THUẬT CHI TIẾT
    # ==============================================================================
    def tinh_toan_chi_bao(df):
        """Tính toán các chỉ báo: MA, Bollinger, RSI, MACD, Money Flow"""
        df = df.copy()
        
        # Đường trung bình động (MA) - Xương sống của xu hướng
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        
        # Bollinger Bands (BOL) - Vùng biên vận động của giá
        df['std'] = df['close'].rolling(20).std()
        df['upper_band'] = df['ma20'] + (df['std'] * 2)
        df['lower_band'] = df['ma20'] - (df['std'] * 2)
        
        # Chỉ báo sức mạnh tương đối (RSI 14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        # Chỉ báo MACD & Đường Signal
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Các chỉ số phục vụ AI và Smart Flow
        df['return_1d'] = df['close'].pct_change()
        df['vol_change'] = df['volume'] / df['volume'].rolling(10).mean()
        df['money_flow'] = df['close'] * df['volume']
        df['volatility'] = df['return_1d'].rolling(20).std()
        
        # Logic xác định Gom/Xả: Giá tăng/giảm đồng thuận với Volume nổ
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1.2), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1.2), -1, 0))
        
        return df.dropna()

    # ==============================================================================
    # 4. CHẨN ĐOÁN TÂM LÝ & BACKTEST LỊCH SỬ
    # ==============================================================================
    def chan_doan_tam_ly(df):
        """Phân tích tâm lý dựa trên Fear & Greed Index (RSI)"""
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
        """Hàm Backtest: Kiểm tra xác suất thắng của tín hiệu RSI/MACD trong 1000 phiên"""
        win_count = 0
        total_signals = 0
        for i in range(100, len(df)-10):
            # Tín hiệu Mua: RSI thấp (<45) và MACD cắt lên Signal
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]:
                total_signals += 1
                # Kiểm tra sau 10 phiên giá có tăng 5% không
                future_prices = df['close'].iloc[i+1 : i+11]
                if any(future_prices > df['close'].iloc[i] * 1.05):
                    win_count += 1
        
        if total_signals == 0:
            return 0.0
        return round((win_count / total_signals) * 100, 1)

    # ==============================================================================
    # 5. MÔ HÌNH DỰ BÁO TƯƠNG LAI AI (RANDOM FOREST)
    # ==============================================================================
    def du_bao_ai(df):
        """Mô hình dự báo xác suất tăng giá T+3"""
        if len(df) < 200:
            return "N/A"
        
        df_copy = df.copy()
        # Mục tiêu: Giá tăng > 2% sau 3 phiên
        df_copy['target'] = (df_copy['close'].shift(-3) > df_copy['close'] * 1.02).astype(int)
        
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data = df_copy.dropna()
        
        X = data[features]
        y = data['target']
        
        # Khởi tạo và huấn luyện mô hình
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        # Huấn luyện trên toàn bộ dữ liệu trừ 3 phiên cuối cùng
        model.fit(X[:-3], y[:-3])
        
        # Lấy xác suất dự báo cho phiên hiện tại
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    # ==============================================================================
    # 6. PHÂN TÍCH TÀI CHÍNH & CANSLIM (PHỤC HỒI ĐẦY ĐỦ)
    # ==============================================================================
    def tinh_tang_truong_lnst(ticker):
        """Tính tăng trưởng LNST quý gần nhất so với cùng kỳ"""
        try:
            df_inc = s.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            # Xác định cột lợi nhuận sau thuế
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
            # Fallback sang Yahoo Finance
            info = yf.Ticker(f"{ticker}.VN").info
            growth = info.get('earningsQuarterlyGrowth')
            if growth is not None:
                return round(growth * 100, 1)
        except Exception:
            pass
        return None

    def lay_chi_so_co_ban(ticker):
        """Lấy P/E và ROE từ dữ liệu tài chính"""
        pe_val, roe_val = 0, 0
        try:
            ratio = s.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe_val = ratio.get('ticker_pe', ratio.get('pe', 0))
            roe_val = ratio.get('roe', 0)
        except Exception:
            pass
            
        if pe_val <= 0:
            try:
                info = yf.Ticker(f"{ticker}.VN").info
                pe_val = info.get('trailingPE', 0)
                roe_val = info.get('returnOnEquity', 0)
            except Exception:
                pass
        return pe_val, roe_val

    # ==============================================================================
    # 7. 🧠 HỆ THỐNG ROBOT ADVISOR: CHẨN ĐOÁN & ĐỀ XUẤT (V9.0 MASTER)
    # ==============================================================================
    def robot_advisor_logic(ticker, last, ai_p, wr, pe, roe, growth, list_gom, list_xa):
        """Hệ thống ra quyết định dựa trên sự đồng thuận của đa chỉ báo"""
        diag_tech_text = ""
        diag_flow_text = ""
        action_verdict = ""
        action_color = ""
        logic_score = 0
        
        # Bước 1: Chẩn đoán Kỹ thuật
        if last['rsi'] > 72:
            diag_tech_text = "Thận trọng: RSI đang tiến sát vùng Quá mua. Áp lực chốt lời tiềm tàng rất lớn, không nên mở vị thế mới."
        elif last['rsi'] < 35:
            diag_tech_text = "Cơ hội: RSI đang ở vùng Quá bán cực độ. Lực bán đã cạn kiệt, cổ phiếu đang ở vùng định giá rẻ ngắn hạn."
        else:
            diag_tech_text = f"Giá đang vận động tích cực trên đường MA20 ({last['ma20']:,.0f}). Xu hướng ngắn hạn được ủng hộ."
            
        # Bước 2: Chẩn đoán Dòng tiền (Smart Flow)
        if ticker in list_gom:
            diag_flow_text = "Tích cực: Dòng tiền Cá mập đang Gom hàng chủ động cùng nhóm trụ cột HOSE. Đây là bệ đỡ vững chắc."
        elif ticker in list_xa:
            diag_flow_text = "Cảnh báo: Dòng tiền lớn đang có dấu hiệu rút lui (Xả hàng). Áp lực bán từ tổ chức đang tăng dần."
        else:
            diag_flow_text = "Dòng tiền chủ yếu đến từ nhỏ lẻ, chưa thấy sự nhập cuộc rõ ràng của các quỹ và tay chơi lớn."

        # Bước 3: Tính điểm đồng thuận (Decision Score)
        if isinstance(ai_p, float) and ai_p >= 55.0: logic_score += 1
        if wr >= 45.0: logic_score += 1
        if last['close'] > last['ma20']: logic_score += 1
        if growth is not None and growth >= 15.0: logic_score += 1
        if pe > 0 and pe <= 16.0: logic_score += 1

        # Bước 4: Đưa ra Đề xuất cuối cùng
        if logic_score >= 4 and last['rsi'] < 68:
            action_verdict = "🚀 MUA / NẮM GIỮ: Tín hiệu đồng thuận cao từ Kỹ thuật, AI và Cơ bản. Ưu tiên giải ngân."
            action_color = "green"
        elif logic_score <= 1 or last['rsi'] > 78:
            action_verdict = "🚨 BÁN / ĐỨNG NGOÀI: Các chỉ số đang ở vùng rủi ro hoặc dòng tiền lớn đã thoát. Bảo vệ vốn là trên hết."
            action_color = "red"
        else:
            action_verdict = "⚖️ THEO DÕI: Tín hiệu chưa đủ mạnh để ra quyết định. Hãy kiên nhẫn chờ phiên nổ Volume xác nhận."
            action_color = "orange"

        return diag_tech_text, diag_flow_text, action_verdict, action_color

    # ==============================================================================
    # 8. GIAO DIỆN STREAMLIT & ĐIỀU KHIỂN
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ticker():
        try:
            return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except Exception:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_stocks = lay_danh_sach_ticker()
    st.sidebar.header("🕹️ Trung Tâm Điều Hành")
    sel_ticker = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_stocks)
    text_ticker = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    active_ticker = text_ticker if text_ticker else sel_ticker

    # Phân chia các Tab chức năng
    t1, t2, t3, t4 = st.tabs([
        "🤖 ROBOT ADVISOR & CHART", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 MARKET SENSE (COMMAND)", 
        "🔍 TRUY QUÉT HUNTER"
    ])

    with t1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {active_ticker}"):
            df_stock = lay_du_lieu(active_ticker)
            if df_stock is not None and not df_stock.empty:
                df_stock = tinh_toan_chi_bao(df_stock)
                last_row = df_stock.iloc[-1]
                
                # Thực hiện các phân tích
                ai_prob = du_bao_ai(df_stock)
                win_rate = tinh_ty_le_thang(df_stock)
                mood_label, mood_score = chan_doan_tam_ly(df_stock)
                stock_pe, stock_roe = lay_chi_so_co_ban(active_ticker)
                stock_growth = tinh_tang_truong_lnst(active_ticker)
                
                # Quét nhanh nhóm trụ cột để phục vụ Advisor
                pillar_list = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                gom_stocks, xa_stocks = [], []
                for p_mã in pillar_list:
                    try:
                        p_df = lay_du_lieu(p_mã, days=10)
                        if p_df is not None:
                            p_df = tinh_toan_chi_bao(p_df)
                            p_last = p_df.iloc[-1]
                            if p_last['return_1d'] > 0 and p_last['vol_change'] > 1.2: gom_stocks.append(p_mã)
                            elif p_last['return_1d'] < 0 and p_last['vol_change'] > 1.2: xa_stocks.append(p_mã)
                    except Exception: pass

                # GỌI ROBOT ADVISOR PHÂN TÍCH
                t_diag, f_diag, verdict_text, v_col = robot_advisor_logic(active_ticker, last_row, ai_prob, win_rate, stock_pe, stock_roe, stock_growth, gom_stocks, xa_stocks)

                st.write(f"### 🎯 Chẩn Đoán Robot Advisor cho {active_ticker}")
                col_diag_1, col_diag_2 = st.columns([2, 1])
                with col_diag_1:
                    st.info(f"**💡 Góc nhìn kỹ thuật:** {t_diag}")
                    st.info(f"**🌊 Góc nhìn dòng tiền:** {f_diag}")
                    st.markdown(f"**Robot ghi chú:** AI dự báo xác suất tăng là **{ai_prob}%**. Win-rate lịch sử đạt **{win_rate}%**.")
                with col_diag_2:
                    st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                    st.title(f":{v_col}[{verdict_text.split(':')[0]}]")
                    st.write(f"*{verdict_text.split(':')[1]}*")
                
                st.divider()
                st.write("### 🧭 Bảng Chỉ Số Kỹ Thuật (Naked Stats)")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Giá Hiện Tại", f"{last_row['close']:,.0f}")
                m2.metric("Tâm Lý Thị Trường", f"{mood_score}/100", delta=mood_label)
                m3.metric("RSI (14)", f"{last_row['rsi']:.1f}", delta="Quá mua" if last_row['rsi']>70 else ("Quá bán" if last_row['rsi']<30 else None))
                m4.metric("MACD Status", f"{last_row['macd']:.2f}", delta="Cắt lên (Tốt)" if last_row['macd']>last_row['signal'] else "Cắt xuống (Xấu)")
                
                with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (QUY TẮC VÀNG)"):
                    st.markdown(f"""
                    **1. Khối lượng (Volume):** Vol phiên hiện tại đạt **{last_row['vol_change']:.1f} lần** trung bình 10 phiên.
                    - Giá tăng + Vol cao (>1.2) ➔ Cá mập đang Gom.
                    - Giá giảm + Vol cao (>1.2) ➔ Cá mập đang Xả (Tháo hàng).
                    
                    **2. Bollinger Bands (BOL):** Vùng xám mờ trên biểu đồ là dải vận động chuẩn. 
                    - Vượt dải trên ➔ Hưng phấn quá đà. 
                    - Thủng dải dưới ➔ Hoảng loạn cực độ.
                    
                    **3. CÁCH NÉ BẪY GIÁ (BULL TRAP / BEAR TRAP):**
                    - **Né Đỉnh Giả:** Giá vượt đỉnh nhưng Vol thấp hơn trung bình ➔ Bẫy lừa người mua đuổi.
                    - **Né Đáy Giả:** Giá chạm dải dưới nhưng Vol xả vẫn cực lớn ➔ Đừng bắt đáy vội, hãy chờ nến rút chân.
                    
                    **4. Cắt lỗ kỷ luật:** Tuyệt đối thoát hàng nếu giá chạm mốc **{last_row['close']*0.93:,.0f} (-7%)**.
                    """)

                # BIỂU ĐỒ NẾN PHỨC HỢP
                fig_master = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig_master.add_trace(go.Candlestick(x=df_stock['date'].tail(120), open=df_stock['open'].tail(120), high=df_stock['high'].tail(120), low=df_stock['low'].tail(120), close=df_stock['close'].tail(120), name='Giá'), row=1, col=1)
                fig_master.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['ma20'].tail(120), line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                fig_master.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['ma200'].tail(120), line=dict(color='purple', width=2), name='MA200 (Dài hạn)'), row=1, col=1)
                # Bollinger Bands với Fill màu
                fig_master.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['upper_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải trên'), row=1, col=1)
                fig_master.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['lower_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải dưới', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
                # Volume
                fig_master.add_trace(go.Bar(x=df_stock['date'].tail(120), y=df_stock['volume'].tail(120), name='Khối lượng', marker_color='gray'), row=2, col=1)
                
                fig_master.update_layout(height=650, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig_master, use_container_width=True)
            else:
                st.error("Lỗi: Không thể truy xuất dữ liệu từ các nguồn dự phòng!")

    with tab2:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá ({active_ticker})")
        with st.spinner("Đang tính toán nội lực doanh nghiệp..."):
            g_val = tinh_tang_truong_lnst(active_ticker)
            if g_val is not None:
                if g_val >= 20.0:
                    st.success(f"**🔥 CanSLIM:** LNST tăng trưởng đột phá **+{g_val}%** (Rất Tốt).")
                elif g_val > 0:
                    st.info(f"**⚖️ Tăng trưởng:** LNST cải thiện ở mức **{g_val}%**.")
                else:
                    st.error(f"**🚨 Cảnh báo:** LNST suy giảm mạnh **{g_val}%** (Kinh doanh đi lùi).")
            
            st.divider()
            pe_v, roe_v = lay_chi_so_co_ban(active_ticker)
            col_f1, col_f2 = st.columns(2)
            
            pe_st = "Tốt (Định giá Rẻ)" if 0 < pe_v < 12 else ("Hợp lý" if pe_v < 18 else "Đắt (Rủi ro mua hớ)")
            col_f1.metric("P/E (Định giá)", f"{pe_v:.1f}", delta=pe_st, delta_color="normal" if pe_v < 18 else "inverse")
            st.write("> P/E thấp chứng tỏ giá cổ phiếu đang hấp dẫn so với lợi nhuận mang lại.")
            
            roe_st = "Xuất sắc" if roe_v >= 0.25 else ("Tốt" if roe_v >= 0.15 else "Trung bình/Thấp")
            col_f2.metric("ROE (Hiệu quả vốn)", f"{roe_v:.1%}", delta=roe_st, delta_color="normal" if roe_v >= 0.15 else "inverse")
            st.write("> ROE đo lường khả năng sinh lời trên mỗi đồng vốn của cổ đông. Tiêu chuẩn vàng là > 15%.")

    with tab3:
        st.write("### 🌊 Market Sense - Độ Rộng & Danh Sách Gom/Xả Trụ Cột")
        with st.spinner("Đang quét dấu chân Cá mập trên 10 mã dẫn dắt thị trường..."):
            big_10 = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
            gom_list, xa_list = [], []
            
            for mã in big_10:
                try:
                    df_p = lay_du_lieu(mã, days=10)
                    if df_p is not None:
                        df_p = tinh_toan_chi_bao(df_p)
                        l_p = df_p.iloc[-1]
                        # Điều kiện Gom/Xả: Giá đồng thuận + Volume nổ (> 1.2)
                        if l_p['return_1d'] > 0 and l_p['vol_change'] > 1.2:
                            gom_list.append(mã)
                        elif l_p['return_1d'] < 0 and l_p['vol_change'] > 1.2:
                            xa_list.append(mã)
                except Exception:
                    pass
            
            b_c1, b_c2 = st.columns(2)
            b_c1.metric("Trụ đang GOM (Mua ròng mạnh)", f"{len(gom_list)} mã", delta=f"{(len(gom_list)/len(big_10))*100:.0f}%", delta_color="normal")
            b_c2.metric("Trụ đang XẢ (Bán tháo mạnh)", f"{len(xa_list)} mã", delta=f"{(len(xa_list)/len(big_10))*100:.0f}%", delta_color="inverse")
            
            st.divider()
            col_list_g, col_list_x = st.columns(2)
            with col_list_g:
                st.success("✅ **DANH SÁCH MÃ TRỤ ĐANG ĐƯỢC GOM:**")
                if gom_list: st.write(", ".join(gom_list))
                else: st.write("Hiện chưa có mã trụ nào có tín hiệu gom đột biến.")
            with col_list_x:
                st.error("🚨 **DANH SÁCH MÃ TRỤ ĐANG BỊ XẢ:**")
                if xa_list: st.write(", ".join(xa_list))
                else: st.write("Hiện chưa có áp lực bán tháo lớn ở nhóm trụ cột.")
            
            if len(xa_list) > len(gom_list):
                st.warning("⚠️ Nhận định: Áp lực bán ở nhóm trụ đang áp đảo. Thị trường chung đang gặp rủi ro 'gãy'.")
            else:
                st.info("ℹ️ Nhận định: Lực mua ở nhóm trụ đang ổn định. Thị trường có bệ đỡ dòng tiền lớn.")

    with tab4:
        st.subheader("🔍 Robot Hunter - Truy Quét Siêu Cổ Phiếu (HOSE 30)")
        if st.button("🔥 BẮT ĐẦU TRUY QUÉT DÒNG TIỀN"):
            hunter_results = []
            scan_progress = st.progress(0)
            target_stocks = all_stocks[:30]
            
            for i, ticker_s in enumerate(target_stocks):
                try:
                    df_s = lay_du_lieu(ticker_s, days=100)
                    df_s = tinh_toan_chi_bao(df_s)
                    # Tiêu chuẩn Hunter: Volume phải nổ cực mạnh (> 1.3)
                    if df_s.iloc[-1]['vol_change'] > 1.3:
                        hunter_results.append({
                            'Mã': ticker_s, 
                            'Giá': df_s.iloc[-1]['close'], 
                            'Sức mạnh Vol': round(df_s.iloc[-1]['vol_change'], 2), 
                            'AI Dự báo Tăng': f"{du_bao_ai(df_s)}%"
                        })
                except Exception:
                    pass
                scan_progress.progress((i+1)/len(target_stocks))
            
            if hunter_results:
                final_df = pd.DataFrame(hunter_results).sort_values(by='AI Dự báo Tăng', ascending=False)
                st.table(final_df)
                st.success("✅ Đã tìm ra các mã tiềm năng nhất dựa trên sự bùng nổ của dòng tiền thông minh.")
            else:
                st.write("Hiện chưa tìm thấy siêu cổ phiếu nào đạt tiêu chuẩn Hunter của hệ thống.")
