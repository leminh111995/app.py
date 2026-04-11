import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. BẢO MẬT & DARK MODE
# ==========================================
def check_password():
    def password_entered():
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

if check_password():
    st.set_page_config(page_title="Robot Siêu Cấp 2026", layout="wide")
    st.markdown(
        """<style> .stApp { background-color: #0E1117; color: white; } </style>""", 
        unsafe_allow_html=True
    )
    st.title("🛡️ Hệ Thống Chiến Thuật & Quản Trị Rủi Ro")

    s = Vnstock()

    # --- HÀM LẤY DỮ LIỆU ---
    def lay_du_lieu(ticker):
        try:
            df = s.stock.quote.history(
                symbol=ticker, 
                start='2024-01-01', 
                end=datetime.now().strftime('%Y-%m-%d')
            )
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                return df
        except: 
            pass
            
        try:
            yt = yf.download(f"{ticker}.VN", period="2y", progress=False)
            yt = yt.reset_index()
            yt.columns = [
                col[0].lower() if isinstance(col, tuple) else col.lower() 
                for col in yt.columns
            ]
            return yt
        except: 
            return None

    # --- TÍNH TOÁN CHỈ BÁO ---
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
        return df

    # --- TÍNH TỶ LỆ THẮNG ---
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

    # --- LẤY DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma():
        try:
            return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = lay_danh_sach_ma()
    st.sidebar.header("🕹️ Điều khiển")
    selected = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_tickers)
    manual = st.sidebar.text_input("Nhập mã thủ công:").upper()
    final_ticker = manual if manual else selected

    tab1, tab2, tab3 = st.tabs(["📊 CHIẾN THUẬT LIVE", "🏢 CƠ BẢN", "🔍 TRUY QUÉT"])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH {final_ticker}"):
            df = lay_du_lieu(final_ticker)
