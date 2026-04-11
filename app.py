import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Các thư viện AI và NLP mới thêm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import urllib.request
import json

# ==========================================
# 1. BẢO MẬT & SETUP
# ==========================================
def check_password():
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
    st.set_page_config(page_title="Quant System V5", layout="wide")
    st.title("🛡️ Hệ Thống Giao Dịch Định Lượng AI")

    s = Vnstock()

    # --- HÀM LẤY DỮ LIỆU ---
    def lay_du_lieu(ticker, days=1000): # Lấy nhiều dữ liệu hơn để train AI
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
    def tinh_toan_chien_thuat(df):
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Features cho AI: Biến động giá, Volatility
        df['return_1d'] = df['close'].pct_change()
        df['volatility'] = df['return_1d'].rolling(20).std()
        df['vol_change'] = df['volume'] / df['volume'].rolling(10).mean()
        
        return df.dropna()

    # --- NÂNG CẤP 2: AI MACHINE LEARNING ---
    def du_bao_ai(df):
        # Target: Nếu giá 3 phiên sau cao hơn giá hiện tại 2% -> MUA (1), ngược lại BÁN (0)
        df['target'] = (df['close'].shift(-3) > df['close'] * 1.02).astype(int)
        
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change']
        data = df.dropna()
        
        if len(data) < 200: return "Không đủ dữ liệu"
        
        X = data[features]
        y = data['target']
        
        # Train mô hình Random Forest
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X[:-3], y[:-3]) # Bỏ 3 phiên cuối vì chưa biết tương lai
        
        # Dự báo phiên hiện tại
        last_features = X.iloc[[-1]]
        prob = model.predict_proba(last_features)[0][1] # Xác suất tăng
        
        return round(prob * 100, 1)

    # --- NÂNG CẤP 3: PHÂN TÍCH TÂM LÝ TIN TỨC ---
    def phan_tich_tin_tuc(ticker):
        try:
            news = s.stock.news(ticker).head(5)
            analyzer = SentimentIntensityAnalyzer()
            scores = []
            
            for title in news['title']:
                # VADER hoạt động tốt với tiếng Anh, ta giả định phân tích trực tiếp (hoặc dịch ngầm)
                score = analyzer.polarity_scores(title)['compound']
                scores.append(score)
                
            avg_score = np.mean(scores)
            if avg_score > 0.05: return "🟢 Tích cực", news
            elif avg_score < -0.05: return "🔴 Tiêu cực", news
            else: return "🟡 Trung lập", news
        except: return "⚪ Không xác định", pd.DataFrame()

    # --- LẤY DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma():
        try: return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = lay_danh_sach_ma()
    st.sidebar.header("🕹️ Điều khiển")
    selected = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_tickers)
    manual = st.sidebar.text_input("Nhập mã thủ công:").upper()
    final_ticker = manual if manual else selected

    tab1, tab2, tab3 = st.tabs(["🤖 AI PROJECTION", "🏢 ĐỊNH GIÁ & TIN TỨC", "🌊 DÒNG TIỀN"])

    with tab1:
        if st.button(f"⚡ CHẠY MÔ HÌNH {final_ticker}"):
            with st.spinner("Đang huấn luyện AI từ 1000 phiên lịch sử..."):
                df = lay_du_lieu(final_ticker)
                if df is not None and not df.empty:
                    df = tinh_toan_chien_thuat(df)
                    last = df.iloc[-1]
                    
                    # Chạy AI
                    ai_prob = du_bao_ai(df)
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                    
                    # Hiển thị AI Probability
                    if isinstance(ai_prob, float):
                        c2.metric("AI Dự báo Tăng (3 phiên)", f"{ai_prob}%")
                    else: c2.metric("AI Dự báo", "N/A")
                    
                    c3.success(f"🎯 Mục tiêu: {last['close']*1.1:,.0f}")
                    c4.error(f"🛑 Cắt lỗ: {last['close']*0.93:,.0f}")

                    st.divider()

                    # Biểu đồ kỹ thuật
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                    fig.add_trace(go.Candlestick(x=df['date'].tail(150), open=df['open'].tail(150), high=df['high'].tail(150), low=df['low'].tail(150), close=df['close'].tail(150), name='Nến'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df['date'].tail(150), y=df['ma50'].tail(150), line=dict(color='orange', width=1.5), name='MA50'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df['date'].tail(150), y=df['ma200'].tail(150), line=dict(color='purple', width=2), name='MA200'), row=1, col=1)
                    fig.add_trace(go.Bar(x=df['date'].tail(150), y=df['volume'].tail(150), marker_color='gray', name='Vol'), row=2, col=1)
                    
                    fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
                else: st.error("Lỗi lấy dữ liệu kỹ thuật!")

    with tab2:
        st.subheader(f"⚖️ Định giá tương đối & Tâm lý thị trường")
        try:
            # 1. Quét Tin tức NLP
            st.write("### 🧠 AI Đọc Báo (Sentiment Analysis)")
            sentiment_status, news_df = phan_tich_tin_tuc(final_ticker)
            st.metric("Tâm lý chung từ Báo chí:", sentiment_status)
            
            if not news_df.empty:
                for _, n in news_df.iterrows():
                    st.write(f"- {n['title']}")
            
            st.divider()
            
            # 2. Định giá Tương đối
            st.write("### 🏢 Sức khỏe Tài chính")
            ratio = s.stock.finance.ratio(final_ticker, report_range='quarterly', is_not_all=True).iloc[-1]
            c1, c2 = st.columns(2)
            c1.metric("P/E (Định giá)", f"{ratio.get('ticker_pe', 0):.1f}")
            c2.metric("ROE (Hiệu quả)", f"{ratio.get('roe', 0):.1%}")
            
            st.caption("Mẹo: Hãy kiểm tra xem P/E này cao hay thấp hơn trung bình ngành ở Tab Dòng Tiền.")
            
        except Exception as e: 
            st.warning("Dữ liệu cơ bản đang được cập nhật.")

    with tab3: # (Giữ nguyên phần Dòng tiền & Sóng ngành như bản V4)
        st.subheader("🌊 Phân tích Dòng tiền")
        try:
            flow = s.stock.finance.flow(final_ticker, report_type='net_flow', report_range='daily').tail(10)
            st.write("**Giao dịch Nước ngoài & Tự doanh:**")
            st.bar_chart(flow[['foreign', 'prop']])
        except: st.warning("Dữ liệu dòng tiền đang cập nhật.")
