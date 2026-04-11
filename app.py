import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# 1. Bảo mật
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

    # Khởi tạo đối tượng chính
    s = Vnstock()

    # --- HÀM TÍNH TOÁN KỸ THUẬT ---
    def tinh_toan_ky_thuat(df):
        df['MA20'] = df['close'].rolling(20).mean()
        df['STD'] = df['close'].rolling(20).std()
        df['Upper'] = df['MA20'] + (df['STD'] * 2)
        df['Lower'] = df['MA20'] - (df['STD'] * 2)
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        return df.iloc[-1]

    # --- HÀM LẤY DỮ LIỆU "THÁM TỬ" (Sửa lỗi Not Defined) ---
    def lay_du_lieu_tu_moi_nguon(ticker):
        # Thử cách 1: Phiên bản mới nhất
        try:
            return s.stock.quote.history(symbol=ticker, start='2025-01-01', end=datetime.now().strftime('%Y-%m-%d'))
        except: pass
        
        # Thử cách 2: Phiên bản trung gian
        try:
            return s.stock_price.khop_lenh_history(symbol=ticker, period='1y')
        except: pass
        
        # Thử cách 3: Dùng yfinance làm cứu cánh cuối cùng (Chỉ cần mã thêm .VN)
        import yfinance as yf
        try:
            yt = yf.download(f"{ticker}.VN", period="1y", progress=False)
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except: return None

    # --- LẤY DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def get_all_tickers():
        try:
            return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = get_all_tickers()
    st.sidebar.header("🎯 Danh mục theo dõi")
    selected_ticker = st.sidebar.selectbox("Chọn mã để soi chi tiết:", all_tickers)
    
    if st.button(f'🚀 CHẨN ĐOÁN MÃ {selected_ticker}'):
        with st.spinner(f'Đang phân tích {selected_ticker}...'):
            df = lay_du_lieu_tu_moi_nguon(selected_ticker)
            
            if df is not None and not df.empty:
                last_row = tinh_toan_ky_thuat(df)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Giá Hiện Tại", f"{last_row['close']:,.0f}")
                    st.write(f"**RSI (14):** {round(last_row['RSI'], 1)}")
                with c2:
                    st.write("**Bollinger Bands**")
                    st.write(f"Upper: {last_row['Upper']:,.0f} | Lower: {last_row['Lower']:,.0f}")
                with c3:
                    macd_trend = "TĂNG" if last_row['MACD'] > last_row['Signal'] else "GIẢM"
                    st.write(f"**MACD:** {macd_trend}")
                
                st.divider()
                st.write("### 🧠 Nhận định từ Robot:")
                score = 0
                if 30 < last_row['RSI'] < 65: score += 1
                if last_row['MACD'] > last_row['Signal']: score += 1
                if last_row['close'] < last_row['Upper']: score += 1
                
                if score == 3:
                    st.balloons()
                    st.success(f"🌟 **MUA TÍCH LŨY**: {selected_ticker} hội tụ đủ điều kiện bùng nổ.")
                elif score == 2:
                    st.info(f"⚖️ **THEO DÕI**: {selected_ticker} đang ổn định, đợi tín hiệu dòng tiền.")
                else:
                    st.warning(f"⚠️ **TẠM ĐỨNG NGOÀI**: Xung lực yếu hoặc giá quá cao.")
            else:
                st.error("Không thể kết nối server dữ liệu. Hãy thử lại sau ít phút.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Hệ thống tự thích nghi phiên bản 2026.")
