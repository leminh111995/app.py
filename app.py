import streamlit as st
from vnstock import *
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import yfinance as yf

# ==========================================
# 1. HỆ THỐNG BẢO MẬT
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("Vui lòng nhập mật mã của Minh:", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    st.set_page_config(page_title="Robot Phân Tích 24/7", layout="wide")
    st.title("🛡️ Hệ Thống Chẩn Đoán Siêu Cổ Phiếu")

    s = Vnstock()

    # --- HÀM TÍNH TOÁN KỸ THUẬT ---
    def tinh_toan_ky_thuat(df):
        # Tính BB
        df['MA20'] = df['close'].rolling(20).mean()
        df['STD'] = df['close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
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
        return df

    # --- HÀM LẤY DỮ LIỆU ĐA NGUỒN ---
    def lay_du_lieu_thong_minh(ticker):
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        # Cách 1: Vnstock
        try:
            df = stock_historical_data(symbol=ticker, start_date=start_date, end_date=end_date, resolution='1D', type='stock')
            if df is not None and not df.empty: 
                df.columns = [col.lower() for col in df.columns]
                return df
        except: pass
        # Cách 2: Yfinance dự phòng
        try:
            yt = yf.download(f"{ticker}.VN", period="1y", progress=False)
            yt = yt.reset_index()
            # Xử lý tên cột yfinance cho đồng nhất
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except: return None

    @st.cache_data(ttl=3600)
    def get_all_tickers():
        try:
            return stock_listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = get_all_tickers()
    st.sidebar.header("🎯 Danh mục theo dõi")
    selected_ticker = st.sidebar.selectbox("Chọn mã muốn soi:", all_tickers, index=0)

    if st.button(f'🚀 BẮT ĐẦU CHẨN ĐOÁN MÃ {selected_ticker}'):
        with st.spinner(f'Đang quét dữ liệu {selected_ticker}...'):
            raw_data = lay_du_lieu_thong_minh(selected_ticker)
            
            if raw_data is not None and not raw_data.empty:
                df = tinh_toan_ky_thuat(raw_data)
                last_row = df.iloc[-1]
                
                # Hiển thị số liệu
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Giá Hiện Tại", f"{last_row['close']:,.0f}")
                    st.write(f"**RSI (14):** {round(last_row['RSI'], 1)}")
                with c2:
                    st.write("**Bollinger Bands**")
                    st.write(f"Upper: {last_row['Upper']:,.0f} | Lower: {last_row['Lower']:,.0f}")
                with c3:
                    st.write(f"**MACD:** {'TĂNG' if last_row['MACD'] > last_row['Signal'] else 'GIẢM'}")
                
                st.divider()

                # Nhận định
                score = 0
                if 30 < last_row['RSI'] < 68: score += 1
                if last_row['MACD'] > last_row['Signal']: score += 1
                if last_row['close'] < last_row['Upper']: score += 1
                
                if score == 3:
                    st.balloons()
                    st.success(f"🌟 **MUA TÍCH LŨY**: {selected_ticker} đang có tín hiệu rất tốt.")
                elif score == 2:
                    st.info(f"⚖️ **THEO DÕI**: {selected_ticker} đang ổn định.")
                else:
                    st.warning(f"⚠️ **TẠM ĐỨNG NGOÀI**: Xung lực đang yếu.")

                # --- PHẦN VẼ BIỂU ĐỒ MỚI (CHỐNG LỖI) ---
                st.write(f"### 📈 Biểu đồ biến động giá {selected_ticker}")
                try:
                    # Lấy 60 phiên gần nhất, chỉ lấy cột giá đóng cửa
                    chart_data = df.tail(60)[['close']].copy()
                    # Vẽ biểu đồ dạng vùng (Area chart) nhìn sẽ đẹp và chuyên nghiệp hơn
                    st.area_chart(chart_data)
                except:
                    st.write("Đang nạp dữ liệu biểu đồ, bạn hãy đợi vài giây...")
                # ---------------------------------------
                
            else:
                st.error("Không lấy được dữ liệu. Hãy thử lại sau!")

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Hệ thống vận hành 24/7")
