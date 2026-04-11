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
    st.set_page_config(page_title="Quant System V5 - Full", layout="wide")
    st.title("🛡️ Hệ Thống Chiến Thuật AI & Truy Quét Toàn Diện")

    s = Vnstock()

    # --- 1. HÀM LẤY DỮ LIỆU ---
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

    # --- 2. TÍNH TOÁN CHỈ BÁO KỸ THUẬT (CÔNG THỨC CHUẨN) ---
    def tinh_toan_chi_bao(df):
        df = df.copy()
        
        # 1. Đường Trung Bình (SMA)
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        
        # 2. Dải Bollinger Bands (Độ lệch chuẩn * 2)
        df['std'] = df['close'].rolling(20).std()
        df['upper_band'] = df['ma20'] + (df['std'] * 2)
        df['lower_band'] = df['ma20'] - (df['std'] * 2)
        
        # 3. Chỉ báo RSI (14 phiên chuẩn)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        # 4. Chỉ báo MACD (Sử dụng đường EMA)
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # 5. Dữ liệu mồi cho AI (Biến động & Khối lượng)
        df['return_1d'] = df['close'].pct_change()
        df['volatility'] = df['return_1d'].rolling(20).std()
        df['vol_change'] = df['volume'] / df['volume'].rolling(10).mean()
        
        return df.dropna()

    # --- 3. TÍNH TỶ LỆ THẮNG LỊCH SỬ (BACKTEST 10 PHIÊN) ---
    def tinh_ty_le_thang(df):
        win = 0
        total = 0
        
        for i in range(200, len(df)-10):
            cond1 = df['rsi'].iloc[i] < 45
            cond2 = df['macd'].iloc[i] > df['signal'].iloc[i]
            cond3 = df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
            
            if cond1 and cond2 and cond3:
                total += 1
                buy_p = df['close'].iloc[i]
                if any(df['close'].iloc[i+1:i+11] > buy_p * 1.05): 
                    win += 1
                    
        if total > 0:
            return round((win/total)*100, 1)
        else:
            return 0

    # --- 4. MÔ HÌNH DỰ BÁO AI ---
    def du_bao_ai(df):
        if len(df) < 200: return "N/A"
        df_copy = df.copy()
        df_copy['target'] = (df_copy['close'].shift(-3) > df_copy['close'] * 1.02).astype(int)
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change']
        data = df_copy.dropna()
        X = data[features]
        y = data['target']
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X[:-3], y[:-3])
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    # --- 5. PHÂN TÍCH TÂM LÝ TIN TỨC ---
    def phan_tich_tin_tuc(ticker):
        try:
            news = s.stock.news(ticker).head(5)
            analyzer = SentimentIntensityAnalyzer()
            scores = [analyzer.polarity_scores(t)['compound'] for t in news['title']]
            avg = np.mean(scores)
            if avg > 0.05: status = "🟢 Tích cực"
            elif avg < -0.05: status = "🔴 Tiêu cực"
            else: status = "🟡 Trung lập"
            return status, news
        except: return "⚪ Không xác định", pd.DataFrame()

    # --- 6. DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma():
        try: return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = lay_danh_sach_ma()
    st.sidebar.header("🕹️ Điều khiển")
    selected = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_tickers)
    manual = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    final_ticker = manual if manual else selected

    # ==========================================
    # GIAO DIỆN 4 TAB CHÍNH
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 KỸ THUẬT & AI", 
        "🏢 CƠ BẢN & TIN TỨC", 
        "🌊 DÒNG TIỀN", 
        "🔍 TRUY QUÉT TOÀN SÀN"
    ])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {final_ticker}"):
            df = lay_du_lieu(final_ticker)
            if df is not None and not df.empty:
                df = tinh_toan_chi_bao(df)
                last = df.iloc[-1]
                ai_p = du_bao_ai(df)
                
                st.write("### 🎯 Mục tiêu & Rủi ro")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                m2.metric("Dự báo AI (3 phiên)", f"{ai_p}%" if isinstance(ai_p, float) else "N/A")
                m3.success(f"Chốt lời: {last['close']*1.1:,.0f}")
                m4.error(f"Cắt lỗ: {last['close']*0.93:,.0f}")
                
                st.divider()
                st.write("### 🎛️ Chỉ số Kỹ thuật Chi tiết")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("RSI (14)", round(last['rsi'], 1), delta="Quá mua" if last['rsi']>70 else "Quá bán" if last['rsi']<30 else None, delta_color="inverse")
                k2.metric("MACD", round(last['macd'], 2), delta="Tăng" if last['macd']>last['signal'] else "Giảm")
                k3.write(f"**Bollinger Upper:** {last['upper_band']:,.0f}")
                k3.write(f"**Bollinger Lower:** {last['lower_band']:,.0f}")
                k4.write(f"**MA50:** {last['ma50']:,.0f}")
                k4.write(f"**MA200:** {last['ma200']:,.0f}")

                # --- BỔ SUNG CẨM NANG GIẢI THÍCH CHỈ BÁO VÀ RỦI RO (BẢN ĐỘNG 100%) ---
                vol_avg = df['volume'].tail(10).mean()
                vol_ratio = last['volume'] / vol_avg if vol_avg > 0 else 0
                macd_status = "TÍCH CỰC (Dòng tiền mua chủ động)" if last['macd'] > last['signal'] else "TIÊU CỰC (Dòng tiền rút ra)"
                bollinger_pos = "NỬA TRÊN (Xu hướng khỏe)" if last['close'] > last['ma20'] else "NỬA DƯỚI (Xu hướng yếu)"

                with st.expander("📖 CẨM NANG ĐỌC TÍN HIỆU & PHÒNG VỆ RỦI RO BẤT KHẢ KHÁNG (Bấm để mở)"):
                    st.markdown(f"""
                    **1. Khối lượng (Volume) & Dòng tiền:**
                    * **Bản chất:** "Giá là sự kỳ vọng, Khối lượng là sự thật". Giá tăng phải đi kèm khối lượng vượt trung bình thì mới bền vững.
                    * **Thực tế mã {final_ticker}:** Khối lượng phiên gần nhất là **{last['volume']:
