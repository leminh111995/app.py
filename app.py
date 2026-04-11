import streamlit as st
from vnstock import *
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import yfinance as yf

# 1. Bảo mật
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
        return df

    # --- HÀM LẤY DỮ LIỆU ĐA NGUỒN ---
    def lay_du_lieu_thong_minh(ticker):
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        try:
            df = stock_historical_data(symbol=ticker, start_date=start_date, end_date=end_date, resolution='1D', type='stock')
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

    # --- DANH SÁCH DỰ PHÒNG 50 MÃ TOP HOSE ---
    fallback_tickers = [
        "FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","DGC","VND","HCM","VCI","HSG",
        "MBB","VPB","ACB","VRE","POW","GAS","SAB","PLX","VJC","BID","CTG","HDB","TPB","GVR","SHB",
        "NKG","PVD","PVT","DIG","DXG","PDR","NLG","KDH","KBC","IDC","REE","SAM","GEX","VIX","ORS",
        "ANV","VHC","IDI","HHV","LCG"
    ]

    @st.cache_data(ttl=3600)
    def get_all_tickers():
        try:
            ls = stock_listing()
            hose_list = ls[ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
            return hose_list if len(hose_list) > 10 else fallback_tickers
        except:
            return fallback_tickers

    all_tickers = get_all_tickers()

    # --- SIDEBAR: CHỌN MÃ HOẶC NHẬP MÃ ---
    st.sidebar.header("🎯 Cài đặt danh mục")
    
    # 1. Chọn từ danh sách có sẵn
    selected_ticker = st.sidebar.selectbox("Chọn từ danh sách:", all_tickers, index=0)
    
    # 2. Hoặc nhập mã thủ công
    st.sidebar.write("--- HOẶC ---")
    manual_ticker = st.sidebar.text_input("Nhập mã thủ công (VD: VCB, AAA...):").upper()
    
    # Ưu tiên mã nhập thủ công nếu có
    final_ticker = manual_ticker if manual_ticker else selected_ticker

    # --- PHẦN HIỂN THỊ CHÍNH ---
    st.subheader(f"🔍 Đang chuẩn bị chẩn đoán mã: {final_ticker}")

    if st.button(f'🚀 BẤT ĐẦU PHÂN TÍCH {final_ticker}'):
        with st.spinner(f'Đang quét dữ liệu chuyên sâu...'):
            raw_data = lay_du_lieu_thong_minh(final_ticker)
            
            if raw_data is not None and not raw_data.empty:
                df = tinh_toan_ky_thuat(raw_data)
                last_row = df.iloc[-1]
                
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
                    st.success(f"🌟 **MUA TÍCH LŨY**: {final_ticker} đang hội tụ các chỉ số bùng nổ.")
                elif score == 2:
                    st.info(f"⚖️ **THEO DÕI**: {final_ticker} đang ở trạng thái tích lũy ổn định.")
                else:
                    st.warning(f"⚠️ **TẠM ĐỨNG NGOÀI**: Xung lực của {final_ticker} đang yếu.")

                st.write(f"### 📈 Biểu đồ biến động giá {final_ticker}")
                st.area_chart(df.tail(60)[['close']])
                
            else:
                st.error(f"Không tìm thấy dữ liệu cho mã '{final_ticker}'. Hãy kiểm tra lại mã có thuộc sàn HOSE không!")

    st.sidebar.markdown("---")
    st.sidebar.write(f"Số lượng mã đang quản lý: {len(all_tickers)}")
