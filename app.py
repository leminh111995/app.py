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
    st.set_page_config(page_title="Quant System V7.5 - Psychology", layout="wide")
    st.title("🛡️ Quant System V7.5: Tâm Lý Đám Đông & Chu Kỳ Cảm Xúc")

    s = Vnstock()

    # --- HÀM LẤY DỮ LIỆU ---
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

    # --- TÍNH TOÁN CHỈ BÁO ---
    def tinh_toan_chi_bao(df):
        df = df.copy()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
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

    # --- CHẨN ĐOÁN TÂM LÝ ĐÁM ĐÔNG (MỚI) ---
    def chan_doan_tam_ly(df):
        last = df.iloc[-1]
        rsi = last['rsi']
        vol_c = last['vol_change']
        ret = last['return_1d']
        
        # Fear & Greed Index (0-100)
        fg_index = rsi
        if fg_index > 75: label = "🔥 CỰC KỲ THAM LAM (Euphoria)"; color = "red"
        elif fg_index > 60: label = "⚖️ THAM LAM (Optimism)"; color = "orange"
        elif fg_index > 40: label = "🟡 TRUNG LẬP (Skepticism)"; color = "yellow"
        elif fg_index > 25: label = "😨 SỢ HÃI (Anxiety)"; color = "blue"
        else: label = "💀 CỰC KỲ SỢ HÃI (Panic)"; color = "cyan"
        
        # Xác định vị trí trong chu kỳ cảm xúc
        if rsi > 70 and vol_c > 1.2 and ret > 0: cycle = "Hưng phấn tột độ - Dễ sập"
        elif rsi < 30 and vol_c > 1.2 and ret < 0: cycle = "Tuyệt vọng - Vùng đáy tiềm năng"
        elif rsi > 50 and ret > 0: cycle = "Niềm tin đang trở lại"
        elif rsi < 50 and ret < 0: cycle = "Nghi ngờ & Lo âu"
        else: cycle = "Chán nản (Sideway)"
        
        return label, color, cycle, round(fg_index, 0)

    # --- TÍNH TỶ LỆ THẮNG LỊCH SỬ ---
    def tinh_ty_le_thang(df):
        win = 0; total = 0
        for i in range(100, len(df)-10):
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i]:
                total += 1
                if any(df['close'].iloc[i+1:i+11] > df['close'].iloc[i] * 1.05): win += 1
        return round((win/total)*100, 1) if total > 0 else 0

    # --- MÔ HÌNH DỰ BÁO AI ---
    def du_bao_ai(df):
        if len(df) < 200: return "N/A"
        df_copy = df.copy(); df_copy['target'] = (df_copy['close'].shift(-3) > df_copy['close'] * 1.02).astype(int)
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data = df_copy.dropna(); X = data[features]; y = data['target']
        model = RandomForestClassifier(n_estimators=100, random_state=42); model.fit(X[:-3], y[:-3])
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

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

    tab1, tab2, tab3, tab4 = st.tabs(["🤖 KỸ THUẬT & TÂM LÝ", "🏢 CƠ BẢN & CANSLIM", "🌊 SMART FLOW", "🔍 TRUY QUÉT"])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {final_ticker}"):
            df = lay_du_lieu(final_ticker)
            if df is not None and not df.empty:
                df = tinh_toan_chi_bao(df); last = df.iloc[-1]; ai_p = du_bao_ai(df); wr = tinh_ty_le_thang(df)
                fg_label, fg_color, cycle, fg_score = chan_doan_tam_ly(df)
                
                # --- PHẦN TÂM LÝ MỚI ---
                st.write("### 🧠 Trạng Thái Tâm Lý Đám Đông")
                c1, c2, c3 = st.columns(3)
                c1.metric("Fear & Greed Index", f"{fg_score}/100", delta=fg_label, delta_color="inverse" if fg_score > 60 else "normal")
                c2.metric("Chu Kỳ Cảm Xúc", cycle)
                c3.metric("Xác Suất Ăn 5% (Lịch sử)", f"{wr}%")
                
                st.divider()
                st.write("### 🎯 Dự Báo & Radar")
                m1, m2, m3 = st.columns(3)
                m1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                m2.metric("AI Dự Báo Tăng (T+3)", f"{ai_p}%")
                m3.success(f"Mục tiêu Chốt lời: {last['close']*1.1:,.0f}")
                
                with st.expander("📖 CẨM NANG ĐỌC VỊ TÂM LÝ (Bấm xem)"):
                    st.markdown("""
                    * **Tham lam (RSI > 70):** Đám đông đang say máu. Đây là lúc Cá mập âm thầm xả hàng. **Nên bán bớt.**
                    * **Sợ hãi (RSI < 30):** Đám đông đang hoảng loạn. Đây là lúc 'máu chảy trên đường phố', cơ hội mua hàng giá rẻ. **Nên quan sát để mua.**
                    * **Nghi ngờ:** Giá tăng nhưng Vol thấp. Thị trường đang dò đáy.
                    """)

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df['date'].tail(150), open=df['open'].tail(150), high=df['high'].tail(150), low=df['low'].tail(150), close=df['close'].tail(150), name='Nến'), row=1, col=1)
                fig.add_trace(go.Bar(x=df['date'].tail(150), y=df['volume'].tail(150), marker_color='gray', name='Vol'), row=2, col=1)
                fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False); st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.write(f"### 📈 Chẩn Đoán Tài Chính ({final_ticker})")
        # Giữ nguyên phần P/E, ROE và giải thích từ V7.0
        # ... (Phần code cũ của tab 2)

    with tab3:
        st.write(f"### 🌊 Smart Flow - Dòng Tiền Cá Mập")
        # Giữ nguyên phần Tiền Lớn/Vừa/Nhỏ từ V7.0
        # ... (Phần code cũ của tab 3)

    with tab4:
        # Giữ nguyên phần Truy quét từ V7.0
