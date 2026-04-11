import streamlit as st
from vnstock import *
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import yfinance as yf

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
    st.set_page_config(page_title="Robot Toàn Diện V3", layout="wide")
    st.title("🚀 Robot Phân Tích Kỹ Thuật, Cơ Bản & Dòng Tiền")

    # --- HÀM LẤY DỮ LIỆU ---
    def lay_du_lieu_thong_minh(ticker):
        try:
            df = stock_historical_data(symbol=ticker, 
                                       start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'), 
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

    # --- LẤY DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def get_all_tickers():
        try:
            return stock_listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = get_all_tickers()

    # --- SIDEBAR ---
    st.sidebar.header("🎯 Cài đặt danh mục")
    selected_ticker = st.sidebar.selectbox("Chọn mã muốn soi:", all_tickers, index=0)
    manual_ticker = st.sidebar.text_input("Hoặc nhập mã thủ công:").upper()
    final_ticker = manual_ticker if manual_ticker else selected_ticker

    # --- GIAO DIỆN CHÍNH ---
    tab1, tab2, tab3 = st.tabs(["📊 Phân tích Kỹ thuật", "🏢 Sức mạnh Cơ bản", "🌊 Dòng tiền & Ngành"])

    with tab1:
        if st.button(f'🚀 CHẨN ĐOÁN KỸ THUẬT {final_ticker}'):
            df_raw = lay_du_lieu_thong_minh(final_ticker)
            if df_raw is not None and not df_raw.empty:
                # TÍNH TOÁN CHỈ BÁO
                df = df_raw.copy()
                df['MA20'] = df['close'].rolling(20).mean()
                df['Upper'] = df['MA20'] + (df['close'].rolling(20).std() * 2)
                df['Lower'] = df['MA20'] - (df['close'].rolling(20).std() * 2)
                
                # Tính RSI
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                df['RSI'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
                
                # Tính MACD
                exp1 = df['close'].ewm(span=12, adjust=False).mean()
                exp2 = df['close'].ewm(span=26, adjust=False).mean()
                df['MACD'] = exp1 - exp2
                df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                
                last_row = df.iloc[-1]
                
                # HIỂN THỊ METRICS (Phần bạn cần nhất đây)
                st.write(f"### 🚩 Tín hiệu kỹ thuật mã: {final_ticker}")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Giá Hiện Tại", f"{last_row['close']:,.0f}")
                
                with col2:
                    rsi_val = round(last_row['RSI'], 1)
                    st.metric("RSI (14)", rsi_val)
                    if rsi_val > 70: st.error("⚠️ Quá mua")
                    elif rsi_val < 30: st.success("✅ Quá bán")
                    else: st.info("Bình thường")
                
                with col3:
                    macd_val = round(last_row['MACD'], 2)
                    st.metric("MACD", macd_val)
                    if last_row['MACD'] > last_row['Signal']: st.write("📈 Xu hướng: **TĂNG**")
                    else: st.write("📉 Xu hướng: **GIẢM**")
                
                with col4:
                    st.write("**Bollinger Bands**")
                    st.write(f"Upper: {last_row['Upper']:,.0f}")
                    st.write(f"Lower: {last_row['Lower']:,.0f}")

                st.divider()
                
                # NHẬN ĐỊNH TỰ ĐỘNG
                score = 0
                if 30 < last_row['RSI'] < 68: score += 1
                if last_row['MACD'] > last_row['Signal']: score += 1
                if last_row['close'] < last_row['Upper']: score += 1
                
                if score == 3:
                    st.balloons()
                    st.success("🌟 **KHUYẾN NGHỊ: MUA TÍCH LŨY**")
                elif score == 2:
                    st.info("⚖️ **KHUYẾN NGHỊ: THEO DÕI**")
                else:
                    st.warning("⚠️ **KHUYẾN NGHỊ: ĐỨNG NGOÀI**")

                st.area_chart(df.tail(60)[['close']])
                
                # TIN TỨC
                st.write("### 📰 Tin tức mới nhất")
                try:
                    news = stock_news(final_ticker)
                    for _, row in news.head(3).iterrows():
                        st.write(f"🔔 **{row['title']}** (*{row['publishDate']}*)")
                except: st.write("Tin tức đang cập nhật...")
                
            else: st.error("Không lấy được dữ liệu!")

    with tab2: # (Giữ nguyên phần Cơ bản của bạn)
        st.subheader(f"💎 Sức khỏe tài chính: {final_ticker}")
        try:
            ratio = financial_ratio(final_ticker, report_range='quarterly', is_not_all=True).iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("P/E", f"{ratio.get('ticker_pe', 0):.1f}")
            c2.metric("P/B", f"{ratio.get('ticker_pb', 0):.1f}")
            c3.metric("ROE", f"{ratio.get('roe', 0):.1%}")
            c4.metric("EPS Growth", f"{ratio.get('earning_per_share_growth', 0):.1%}")
        except: st.warning("Dữ liệu cơ bản đang được cập nhật ngoài giờ.")

    with tab3: # (Giữ nguyên phần Dòng tiền & Ngành)
        st.subheader(f"🌊 Dòng tiền & Sóng Ngành")
        try:
            flow = financial_flow(final_ticker, report_type='net_flow', report_range='daily').tail(10)
            st.bar_chart(flow[['foreign', 'prop']])
            
            ls = stock_listing()
            industry = ls[ls['ticker'] == final_ticker]['en_icb_name_lv4'].values[0]
            st.info(f"🚩 Ngành: **{industry}**")
            
            peers = ls[ls['en_icb_name_lv4'] == industry]['ticker'].head(5).tolist()
            st.write(f"**So sánh Sức mạnh Vol trong ngành:**")
            p_res = []
            for t in peers:
                try:
                    d = stock_historical_data(symbol=t, start_date=(datetime.now()-timedelta(days=15)).strftime('%Y-%m-%d'), end_date=datetime.now().strftime('%Y-%m-%d'), resolution='1D', type='stock')
                    p_res.append({'Mã': t, 'Sức mạnh Vol': round(d['volume'].iloc[-1]/d['volume'].mean(), 2)})
                except: pass
            st.table(pd.DataFrame(p_res).sort_values(by='Sức mạnh Vol', ascending=False))
        except: st.warning("Dữ liệu dòng tiền ngành đang cập nhật.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Bản Toàn Diện V3 - Đầy đủ RSI & MACD")
