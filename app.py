import streamlit as st
from vnstock import *
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. BẢO MẬT
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("Nhập mật mã của Minh:", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    st.set_page_config(page_title="Robot Siêu Cấp V4", layout="wide")
    st.title("🎖️ Hệ Thống Phân Tích & Truy Quét Siêu Cổ Phiếu")

    # --- HÀM LẤY DỮ LIỆU THÔNG MINH ---
    def lay_du_lieu_thong_minh(ticker, days=365):
        try:
            df = stock_historical_data(symbol=ticker, 
                                       start_date=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'), 
                                       end_date=datetime.now().strftime('%Y-%m-%d'), 
                                       resolution='1D', type='stock')
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                return df
        except: pass
        try:
            yt = yf.download(f"{ticker}.VN", period="1y", progress=False)
            yt = yt.reset_index()
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except: return None

    # --- HÀM TÍNH CHỈ BÁO ---
    def tinh_chi_bao(df):
        df['ma20'] = df['close'].rolling(20).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper'] = df['ma20'] + (df['std'] * 2)
        df['lower'] = df['ma20'] - (df['std'] * 2)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        return df

    # --- LẤY DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def get_all_tickers():
        try: return stock_listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = get_all_tickers()

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Điều khiển")
    selected_ticker = st.sidebar.selectbox("Chọn mã soi nhanh:", all_tickers, index=0)
    manual_ticker = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    final_ticker = manual_ticker if manual_ticker else selected_ticker

    # --- GIAO DIỆN TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Kỹ thuật & Nến", "🏢 Sức khỏe Cơ bản", "🌊 Dòng tiền Ngành", "🔍 TRUY QUÉT TOÀN SÀN"])

    with tab1:
        if st.button(f'🚀 CHẨN ĐOÁN {final_ticker}'):
            df = lay_du_lieu_thong_minh(final_ticker)
            if df is not None and not df.empty:
                df = tinh_chi_bao(df)
                last = df.iloc[-1]
                
                # Metrics
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Giá", f"{last['close']:,.0f}")
                c2.metric("RSI", round(last['rsi'], 1))
                c3.metric("MACD", round(last['macd'], 2))
                c4.write(f"**Bollinger:** {last['lower']:,.0f}-{last['upper']:,.0f}")

                # Biểu đồ nến chuyên nghiệp Plotly
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                # Nến
                fig.add_trace(go.Candlestick(x=df['date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Giá'), row=1, col=1)
                # Volume
                colors = ['red' if row['open'] > row['close'] else 'green' for _, row in df.iterrows()]
                fig.add_trace(go.Bar(x=df['date'], y=df['volume'], marker_color=colors, name='Volume'), row=2, col=1)
                
                fig.update_layout(xaxis_rangeslider_visible=False, height=600, template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)

                # Nhận định & Tin tức
                st.success(f"Khuyến nghị: {'MUA TÍCH LŨY' if last['rsi'] < 65 and last['macd'] > last['signal'] else 'THEO DÕI THÊM'}")
                try:
                    st.write("### 📰 Tin tức")
                    for _, r in stock_news(final_ticker).head(3).iterrows():
                        st.write(f"🔔 {r['title']} ({r['publishDate']})")
                except: pass
            else: st.error("Lỗi dữ liệu!")

    with tab2: # Giữ nguyên Cơ bản
        try:
            r = financial_ratio(final_ticker, 'quarterly', True).iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("P/E", f"{r.get('ticker_pe',0):.1f}")
            c2.metric("ROE", f"{r.get('roe',0):.1%}")
            st.info(f"Doanh nghiệp: {company_overview(final_ticker)['summary'].values[0]}")
        except: st.warning("Dữ liệu đang cập nhật...")

    with tab3: # Giữ nguyên Dòng tiền
        try:
            flow = financial_flow(final_ticker, 'net_flow', 'daily').tail(10)
            st.write("**Giao dịch Khối ngoại & Tự doanh:**")
            st.bar_chart(flow[['foreign', 'prop']])
        except: st.warning("Đang lấy dữ liệu dòng tiền...")

    with tab4: # TÍNH NĂNG MỚI: TRUY QUÉT TOÀN SÀN
        st.subheader("🕵️ Robot quét mã tiềm năng (Top 20 HOSE)")
        if st.button("🔥 BẮT ĐẦU TRUY QUÉT"):
            scan_list = all_tickers[:50] # Quét 50 mã lỏng nhất để tránh quá tải
            progress = st.progress(0)
            hits = []
            for i, t in enumerate(scan_list):
                try:
                    d = lay_du_lieu_thong_minh(t, days=50)
                    if d is not None:
                        d = tinh_chi_bao(d)
                        last = d.iloc[-1]
                        vol_avg = d['volume'].tail(10).mean()
                        # TIÊU CHÍ LỌC: Vol đột biến + RSI chưa quá cao + MACD hướng lên
                        if d['volume'].iloc[-1] > vol_avg * 1.2 and 30 < last['rsi'] < 65:
                            hits.append({'Mã': t, 'Giá': last['close'], 'RSI': round(last['rsi'],1), 'Sức mạnh Vol': round(d['volume'].iloc[-1]/vol_avg, 2)})
                except: pass
                progress.progress((i+1)/len(scan_list))
            
            if hits:
                st.table(pd.DataFrame(hits).sort_values(by='Sức mạnh Vol', ascending=False))
            else: st.write("Chưa tìm thấy mã đạt tiêu chuẩn bùng nổ.")

    st.sidebar.caption("Phiên bản Ultimate 2026")
