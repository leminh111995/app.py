import streamlit as st
from vnstock import *
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. BẢO MẬT & CẤU HÌNH DARK MODE
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
    st.set_page_config(page_title="Robot Siêu Cấp 2026", layout="wide")
    
    # CSS để ép giao diện sang Dark Mode chuyên nghiệp
    st.markdown("""<style> .stApp { background-color: #0E1117; color: white; } </style>""", unsafe_allow_html=True)
    st.title("🛡️ Hệ Thống Chiến Thuật & Quản Trị Rủi Ro")

    # --- HÀM LẤY DỮ LIỆU ---
    def lay_du_lieu(ticker):
        try:
            df = stock_historical_data(symbol=ticker, start_date=(datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d'), 
                                       end_date=datetime.now().strftime('%Y-%m-%d'), resolution='1D', type='stock')
            if df is not None: 
                df.columns = [col.lower() for col in df.columns]
                return df
        except: pass
        try:
            yt = yf.download(f"{ticker}.VN", period="2y", progress=False)
            yt = yt.reset_index()
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except: return None

    # --- HÀM TÍNH TOÁN CHIẾN THUẬT ---
    def tinh_toan_chien_thuat(df):
        # Xu hướng
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        # RSI & MACD
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        return df

    # --- HÀM TÍNH TỶ LỆ THẮNG (BACKTEST) ---
    def tinh_ty_le_thang(df):
        win = 0
        total = 0
        for i in range(200, len(df)-20):
            # Tín hiệu mua: RSI < 45 và MACD cắt lên
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]:
                total += 1
                buy_price = df['close'].iloc[i]
                # Kiểm tra 10 phiên tiếp theo
                future_prices = df['close'].iloc[i+1:i+11]
                if any(future_prices > buy_price * 1.05): win += 1
        return round((win/total)*100, 1) if total > 0 else 0

    all_tickers = stock_listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
    st.sidebar.header("🕹️ Bảng điều khiển")
    selected = st.sidebar.selectbox("Mã cổ phiếu:", all_tickers)
    
    # --- HIỂN THỊ CHIẾN THUẬT ---
    tab1, tab2, tab3 = st.tabs(["🔥 CHIẾN THUẬT LIVE", "🏢 CƠ BẢN", "🔍 TRUY QUÉT"])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {selected}"):
            df = lay_du_lieu(selected)
            if df is not None:
                df = tinh_toan_chien_thuat(df)
                last = df.iloc[-1]
                win_rate = tinh_ty_le_thang(df)

                # Hiển thị Tỷ lệ thắng & Quản trị rủi ro
                c1, c2, c3 = st.columns(3)
                c1.metric("Tỷ lệ thắng lịch sử", f"{win_rate}%", delta="Rất Cao" if win_rate > 60 else "Bình thường")
                c2.success(f"🎯 Giá mục tiêu (TP): {(last['close']*1.1):,.0f}")
                c3.error(f"🛑 Cắt lỗ (SL): {(last['close']*0.93):,.0f}")

                # Biểu đồ nến đa tầng
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Nến'), row=1, col=1)
                # Vẽ MA50 và MA200
                fig.add_trace(go.Scatter(x=df['date'], y=df['ma50'], line=dict(color='yellow', width=1), name='MA50 - Trung hạn'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'], y=df['ma200'], line=dict(color='magenta', width=2), name='MA200 - Dài hạn'), row=1, col=1)
                # Volume
                fig.add_trace(go.Bar(x=df['date'], y=df['volume'], name='Khối lượng'), row=2, col=1)
                
                fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                st.write(f"### 💬 Nhận định xu hướng: {'GIAO CẮT VÀNG' if last['ma50'] > last['ma200'] else 'XU HƯỚNG YẾU'}")
            else: st.error("Lỗi dữ liệu!")

    with tab2: # Giữ nguyên cơ bản & Tin tức
        try:
            r = financial_ratio(selected, 'quarterly', True).iloc[-1]
            st.metric("ROE (%)", f"{r.get('roe',0):.1%}")
            st.write(f"**Tin tức:**")
            for _, news in stock_news(selected).head(3).iterrows():
                st.write(f"🔔 {news['title']}")
        except: st.warning("Đang cập nhật...")

    with tab3: # Truy quét toàn sàn
        if st.button("🔍 QUÉT MÃ BÙNG NỔ"):
            hits = []
            scan_list = all_tickers[:30] # Quét 30 mã đầu
            for t in scan_list:
                try:
                    d = lay_du_lieu(t)
                    if d is not None:
                        d = tinh_toan_chien_thuat(d)
                        if d['volume'].iloc[-1] > d['volume'].tail(10).mean() * 1.3:
                            hits.append({'Mã': t, 'Giá': d['close'].iloc[-1], 'Tỷ lệ thắng': tinh_ty_le_thang(d)})
                except: pass
            st.table(pd.DataFrame(hits))

    st.sidebar.markdown("---")
    st.sidebar.write("✅ Robot Đã Sẵn Sàng")
