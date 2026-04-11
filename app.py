import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Thư viện AI và NLP
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==========================================
# 1. BẢO MẬT & SETUP
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("🔑 Nhập mật mã của Minh:", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    st.set_page_config(page_title="Quant System V6.7 - Full Option", layout="wide")
    st.title("🛡️ Quant System V6.7: Radar + AI + CanSLIM + Smart Flow")

    s = Vnstock()

    # --- HÀM LẤY DỮ LIỆU KỸ THUẬT ---
    def lay_du_lieu(ticker, days=1000):
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            df = s.stock.quote.history(symbol=ticker, start=start_date, end=end_date)
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                return df
        except: pass
        try:
            yt = yf.download(f"{ticker}.VN", period="3y", progress=False)
            yt = yt.reset_index()
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except: return None

    # --- TÍNH TOÁN CHỈ BÁO & FEATURE CHO AI ---
    def tinh_toan_chi_bao(df):
        df = df.copy()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper_band'] = df['ma20'] + (df['std'] * 2)
        df['lower_band'] = df['ma20'] - (df['std'] * 2)
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        df['return_1d'] = df['close'].pct_change()
        df['vol_change'] = df['volume'] / df['volume'].rolling(10).mean()
        df['money_flow'] = df['close'] * df['volume']
        df['volatility'] = df['return_1d'].rolling(20).std()
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1), -1, 0))
        return df.dropna()

    # --- MÔ HÌNH DỰ BÁO AI ---
    def du_bao_ai(df):
        if len(df) < 200: return "N/A"
        df_copy = df.copy()
        df_copy['target'] = (df_copy['close'].shift(-3) > df_copy['close'] * 1.02).astype(int)
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data = df_copy.dropna()
        X = data[features]; y = data['target']
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X[:-3], y[:-3])
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    # --- HÀM TÍNH TĂNG TRƯỞNG CANSLIM ---
    def tinh_tang_truong_lnst(ticker):
        try:
            df_inc = s.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en')
            df_inc = df_inc.head(5) 
            target_cols = [c for c in df_inc.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit', 'lãi ròng'])]
            if target_cols:
                col_name = target_cols[0]
                lnst_q1 = float(df_inc.iloc[0][col_name])
                lnst_q5 = float(df_inc.iloc[4][col_name])
                if lnst_q5 > 0: return round(((lnst_q1 - lnst_q5) / lnst_q5) * 100, 1)
        except: pass
        try:
            info = yf.Ticker(f"{ticker}.VN").info
            growth = info.get('earningsQuarterlyGrowth')
            if growth is not None: return round(growth * 100, 1)
        except: pass
        return None

    # --- HÀM LẤY CHỈ SỐ CƠ BẢN ---
    def lay_chi_so_co_ban(ticker):
        pe, roe = 0, 0
        try:
            ratio = s.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe = ratio.get('ticker_pe', ratio.get('pe', 0)); roe = ratio.get('roe', 0)
            if pe > 0: return pe, roe
        except: pass
        try:
            info = yf.Ticker(f"{ticker}.VN").info
            pe = info.get('trailingPE', 0); roe = info.get('returnOnEquity', 0)
        except: pass
        return pe, roe

    # --- DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma():
        try: return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = lay_danh_sach_ma()
    st.sidebar.header("🕹️ Điều khiển")
    selected = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_tickers)
    manual = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    final_ticker = manual if manual else selected

    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 KỸ THUẬT & RADAR", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 DÒNG TIỀN (SMART FLOW)", 
        "🔍 TRUY QUÉT TOÀN SÀN"
    ])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {final_ticker}"):
            df = lay_du_lieu(final_ticker)
            if df is not None and not df.empty:
                df = tinh_toan_chi_bao(df); last = df.iloc[-1]; ai_p = du_bao_ai(df)
                
                st.write("### 🎯 Mục tiêu & Rủi ro")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                m2.metric("Dự báo AI (Volume-based)", f"{ai_p}%")
                m3.success(f"Chốt lời: {last['close']*1.1:,.0f}"); m4.error(f"Cắt lỗ: {last['close']*0.93:,.0f}")
                
                st.divider(); st.write("### 📡 Radar Phát Hiện Đỉnh/Đáy Ngắn Hạn")
                close_p = last['close']; ma20 = last['ma20']; upper = last['upper_band']; lower = last['lower_band']; rsi = last['rsi']
                if rsi > 65 and close_p >= upper * 0.98:
                    st.error(f"**🚨 CẢNH BÁO TẠO ĐỈNH:** RSI = {rsi:.1f}. Mức giảm dự kiến về MA20: -{((close_p - ma20) / close_p) * 100:.1f}%")
                elif rsi < 35 and close_p <= lower * 1.02:
                    st.success(f"**🌟 TÍN HIỆU TẠO ĐÁY:** RSI = {rsi:.1f}. Mức tăng dự kiến lên MA20: +{((ma20 - close_p) / close_p) * 100:.1f}%")
                else: st.info(f"**⚖️ CÂN BẰNG:** Cổ phiếu đang tích lũy.")

                # --- PHỤC HỒI CẨM NANG GIẢI THÍCH SỐ LIỆU ---
                vol_avg = df['volume'].tail(10).mean()
                vol_ratio = last['volume'] / vol_avg if vol_avg > 0 else 0
                with st.expander("📖 CẨM NANG ĐỌC TÍN HIỆU & NÉ FALSE BREAKOUT (Bấm để xem)"):
                    st.markdown(f"""
                    **1. Khối lượng (Volume):** Khối lượng mã {final_ticker} đang bằng **{vol_ratio:.1f} lần** trung bình. Nếu Giá tăng + Vol > 1.2 ➔ Cá mập gom hàng. Nếu Giá giảm + Vol > 1.2 ➔ Cá mập xả hàng.
                    
                    **2. Chỉ báo MACD:** MACD đang {'nằm TRÊN (Tốt)' if last['macd'] > last['signal'] else 'nằm DƯỚI (Xấu)'} đường Tín hiệu.
                    
                    **3. CÁCH NÉ TÍN HIỆU GIẢ (BẪY GIÁ):**
                    * **Né Đỉnh Giả:** Giá vượt đỉnh nhưng Vol thấp hơn trung bình ➔ Tuyệt đối không mua đuổi, dễ dính Bull Trap.
                    * **Né Đáy Giả:** Giá chạm dải dưới nhưng Vol đỏ vẫn cực lớn ➔ Đừng bắt đáy, áp lực bán tháo vẫn còn. Chỉ mua khi Vol cạn kiệt và xuất hiện nến xanh rút chân.
                    
                    **4. Nguyên tắc Thiên nga đen:** Khi thị trường có tin bắt bớ/chiến tranh, hãy bỏ qua kỹ thuật và tuân thủ tuyệt đối mức cắt lỗ **{last['close']*0.93:,.0f}**.
                    """)

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df['date'].tail(150), open=df['open'].tail(150), high=df['high'].tail(150), low=df['low'].tail(150), close=df['close'].tail(150), name='Nến'), row=1, col=1)
                fig.add_trace(go.Bar(x=df['date'].tail(150), y=df['volume'].tail(150), marker_color='gray', name='Vol'), row=2, col=1)
                fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False); st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.write(f"### 📈 CanSLIM & Chẩn Đoán Tài Chính ({final_ticker})")
        growth = tinh_tang_truong_lnst(final_ticker)
        if growth is not None:
            if growth > 20: st.success(f"**🔥 TUYỆT VỜI:** LNST tăng **+{growth}%** (Đạt chuẩn CanSLIM).")
            elif growth > 0: st.info(f"**⚖️ TRUNG BÌNH:** LNST tăng trưởng **+{growth}%**.")
            else: st.error(f"**🚨 RỦI RO:** LNST đi lùi **{growth}%**.")
        
        st.divider(); pe, roe = lay_chi_so_co_ban(final_ticker); c1, c2 = st.columns(2)
        pe_status = "Tốt (Rẻ)" if 0 < pe < 12 else ("Hợp lý" if 12 <= pe < 20 else "Đắt")
        c1.metric("P/E (Định giá)", f"{pe:.1f}", delta=pe_status, delta_color="normal" if pe < 20 else "inverse")
        roe_status = "Xuất sắc" if roe >= 0.2 else ("Tốt" if 0.15 <= roe < 0.2 else "Trung bình")
        c2.metric("ROE (Hiệu quả)", f"{roe:.1%}", delta=roe_status, delta_color="normal" if roe >= 0.15 else "inverse")

    with tab3:
        st.write(f"### 🌊 Dòng Tiền Smart Flow Mã {final_ticker}")
        df_flow = lay_du_lieu(final_ticker, days=30)
        if df_flow is not None:
            df_flow = tinh_toan_chi_bao(df_flow); last_f = df_flow.iloc[-1]; v_c = last_f['vol_change']
            big_m = 0.6 if v_c > 1.5 else (0.4 if v_c > 1.1 else 0.2)
            med_m = 0.3 if v_c > 1.5 else (0.4 if v_c > 1.1 else 0.3)
            sma_m = 0.1 if v_c > 1.5 else (0.2 if v_c > 1.1 else 0.5)
            
            s_txt = "Gom" if last_f['return_1d'] > 0 else "Xả"; s_col = "normal" if last_f['return_1d'] > 0 else "inverse"
            c1, c2, c3 = st.columns(3)
            c1.metric("🐋 Tiền Lớn", f"{big_m*100:.0f}%", delta=s_txt, delta_color=s_col)
            c2.metric("🏦 Tiền Vừa", f"{med_m*100:.0f}%"); c3.metric("🐜 Tiền Nhỏ", f"{sma_m*100:.0f}%")
            
            history = df_flow.tail(20).copy()
            fig_f = go.Figure()
            fig_f.add_trace(go.Bar(x=history['date'], y=history['money_flow'], marker_color=['#2ca02c' if r > 0 else '#d62728' for r in history['return_1d']]))
            fig_f.update_layout(height=400, template='plotly_white'); st.plotly_chart(fig_f, use_container_width=True)

    with tab4:
        st.subheader("🔍 Robot Truy Quét")
        if st.button("🔥 CHẠY RÀ SOÁT"):
            hits = []; bar = st.progress(0); tickers = all_tickers[:30]
            for i, t in enumerate(tickers):
                try:
                    d = lay_du_lieu(t, days=100); d = tinh_toan_chi_bao(d)
                    if d.iloc[-1]['vol_change'] > 1.3:
                        hits.append({'Mã': t, 'Giá': d.iloc[-1]['close'], 'AI Dự báo': f"{du_bao_ai(d)}%"})
                except: pass
                bar.progress((i+1)/len(tickers))
            if hits: st.table(pd.DataFrame(hits))
