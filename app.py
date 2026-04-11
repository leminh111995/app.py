import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
import time

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
    st.set_page_config(page_title="Hệ Thống Phân Tích 24/7", layout="wide")
    st.title("🛡️ Hệ Thống Chẩn Đoán Siêu Cổ Phiếu")
    
    s = Vnstock()

    # --- HÀM TÍNH TOÁN KỸ THUẬT CHUYÊN SÂU ---
    def tinh_toan_ky_thuat(df):
        # Bollinger Bands
        df['MA20'] = df['close'].rolling(20).mean()
        df['STD'] = df['close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + gain/loss))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df.iloc[-1]

    @st.cache_data(ttl=3600)
    def get_all_tickers():
        try:
            df_ls = s.market.listing()
            return df_ls[df_ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = get_all_tickers()

    # --- GIAO DIỆN CHÍNH ---
    st.sidebar.header("🎯 Danh mục theo dõi")
    selected_ticker = st.sidebar.selectbox("Chọn mã để soi chi tiết:", all_tickers, index=0)
    
    st.subheader(f"🔍 Phân tích chuyên sâu mã: {selected_ticker}")
    
    if st.button('🚀 CHẨN ĐOÁN NGAY'):
        with st.spinner(f'Đang rà soát dữ liệu {selected_ticker}...'):
            try:
                # Lấy dữ liệu 1 năm để tính chỉ báo
                df = s.stock_price.khop_lenh_history(symbol=selected_ticker, period='1y')
                
                if not df.empty:
                    last_row = tinh_toan_ky_thuat(df)
                    
                    # Layout hiển thị 3 cột
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Giá Hiện Tại", f"{last_row['close']:,}")
                        rsi_val = round(last_row['RSI'], 1)
                        st.write(f"**RSI (14):** {rsi_val}")
                        if rsi_val > 70: st.error("⚠️ Quá mua (Rủi ro)")
                        elif rsi_val < 30: st.success("✅ Quá bán (Cơ hội)")
                        else: st.info("Neutral (Trung tính)")

                    with col2:
                        st.write("**Bollinger Bands**")
                        st.write(f"Upper: {last_row['Upper']:,.0f}")
                        st.write(f"Lower: {last_row['Lower']:,.0f}")
                        if last_row['close'] >= last_row['Upper']: st.warning("Giá chạm dải trên")
                        elif last_row['close'] <= last_row['Lower']: st.success("Giá chạm dải dưới")

                    with col3:
                        st.write("**MACD Trend**")
                        macd_status = "TĂNG" if last_row['MACD'] > last_row['Signal'] else "GIẢM"
                        st.write(f"Trạng thái: **{macd_status}**")
                        st.write(f"MACD: {round(last_row['MACD'], 2)}")

                    st.divider()
                    
                    # NHẬN ĐỊNH TỰ ĐỘNG
                    st.write("### 🧠 Nhận định từ Robot:")
                    score = 0
                    if last_row['RSI'] < 60: score += 1
                    if last_row['MACD'] > last_row['Signal']: score += 1
                    if last_row['close'] < last_row['Upper']: score += 1
                    
                    if score == 3:
                        st.balloons()
                        st.success("🎯 KHUYẾN NGHỊ: **MUA TÍCH LŨY**. Các chỉ số đồng thuận cho xu hướng tăng.")
                    elif score == 2:
                        st.info("🎯 KHUYẾN NGHỊ: **THEO DÕI CHẶT**. Cổ phiếu đang ổn định, đợi dòng tiền nổ (Vol X).")
                    else:
                        st.warning("🎯 KHUYẾN NGHỊ: **TẠM ĐỨNG NGOÀI**. Xung lực yếu hoặc giá đã quá cao.")
                else:
                    st.error("Không lấy được dữ liệu. Có thể server API đang bảo trì.")
            except Exception as e:
                st.error(f"Lỗi phân tích: {e}")

    st.sidebar.markdown("---")
    st.sidebar.caption("Lưu ý: Phân tích dựa trên dữ liệu chốt phiên gần nhất nếu ngoài giờ giao dịch.")
