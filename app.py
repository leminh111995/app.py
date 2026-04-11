import streamlit as st
from vnstock import *
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# 1. Bảo mật mật mã
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
    st.set_page_config(page_title="Robot Phân Tích 24/7", layout="wide")
    st.title("🛡️ Hệ Thống Chẩn Đoán Siêu Cổ Phiếu")

    # --- HÀM TÍNH TOÁN KỸ THUẬT ---
    def tinh_toan_ky_thuat(df):
        # Tính Bollinger Bands
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
        return df.iloc[-1]

    # --- LẤY DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def get_all_tickers():
        try:
            df_ls = stock_listing()
            return df_ls[df_ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","DGC","VND","HCM","VCI","HSG"]

    all_tickers = get_all_tickers()

    st.sidebar.header("🎯 Danh mục theo dõi")
    selected_ticker = st.sidebar.selectbox("Chọn mã để soi chi tiết:", all_tickers)
    
    if st.button(f'🚀 CHẨN ĐOÁN MÃ {selected_ticker}'):
        with st.spinner(f'Đang phân tích dữ liệu {selected_ticker}...'):
            try:
                # SỬA LỖI: Dùng hàm direct stock_historical_data
                # Lấy dữ liệu 1 năm tính từ hôm nay
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                
                df = stock_historical_data(symbol=selected_ticker, 
                                           start_date=start_date, 
                                           end_date=end_date, 
                                           resolution='1D', 
                                           type='stock')
                
                if df is not None and not df.empty:
                    last_row = tinh_toan_ky_thuat(df)
                    
                    # Hiển thị Metrics
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Giá Hiện Tại", f"{last_row['close']:,.0f}")
                        rsi_v = round(last_row['RSI'], 1)
                        st.write(f"**RSI (14):** {rsi_v}")
                    with c2:
                        st.write("**Bollinger Bands**")
                        st.write(f"Upper: {last_row['Upper']:,.0f}")
                        st.write(f"Lower: {last_row['Lower']:,.0f}")
                    with c3:
                        st.write("**Xu hướng MACD**")
                        macd_trend = "TĂNG" if last_row['MACD'] > last_row['Signal'] else "GIẢM"
                        st.write(f"Trạng thái: **{macd_trend}**")
                    
                    st.divider()
                    
                    # NHẬN ĐỊNH
                    st.write("### 🧠 Nhận định từ Robot:")
                    score = 0
                    if 30 < last_row['RSI'] < 65: score += 1
                    if last_row['MACD'] > last_row['Signal']: score += 1
                    if last_row['close'] < last_row['Upper']: score += 1
                    
                    if score == 3:
                        st.balloons()
                        st.success(f"🌟 **MUA TÍCH LŨY**: {selected_ticker} đang có sự đồng thuận kỹ thuật rất đẹp.")
                    elif score == 2:
                        st.info(f"⚖️ **THEO DÕI**: {selected_ticker} đang ổn định, cần thêm dòng tiền mạnh để bứt phá.")
                    else:
                        st.warning(f"⚠️ **TẠM ĐỨNG NGOÀI**: {selected_ticker} có dấu hiệu yếu hoặc giá đã quá cao.")
                else:
                    st.error("Server không trả về dữ liệu. Có thể do ngoài giờ hoặc mã bị tạm ngừng giao dịch.")
            except Exception as e:
                st.error(f"Lỗi hệ thống: {e}")

    st.sidebar.markdown("---")
    st.sidebar.caption("Dữ liệu tự động cập nhật theo phiên giao dịch gần nhất.")
