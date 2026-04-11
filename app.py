import streamlit as st
from vnstock import Vnstock
import pandas as pd
import time

# 1. Bảo mật
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("Nhập mật mã của Minh:", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    st.set_page_config(page_title="Robot Siêu Cổ Phiếu", layout="wide")
    st.title("🚀 Robot Phân Tích Siêu Cổ Phiếu")
    
    s = Vnstock()

    @st.cache_data(ttl=3600)
    def get_all_tickers():
        try:
            # Thử mọi cách để lấy danh sách HOSE
            df_ls = s.market.listing()
            return df_ls[df_ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            # Danh sách dự phòng mở rộng (Top các mã thanh khoản cao)
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","VCI","DGC","VND","PVD","NKG","HSG","HCM","VRE","VPB","MBB"]

    all_tickers = get_all_tickers()

    # --- SIDEBAR TỐI ƯU ---
    st.sidebar.header("🎯 Cài đặt danh mục")
    
    # Nút chọn nhanh
    if st.sidebar.button("Chọn nhanh Top 20 mã"):
        st.session_state["selected_list"] = ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","VCI","DGC","VND","PVD","NKG","HSG","HCM","VRE","VPB","MBB"]
    
    selected_list = st.sidebar.multiselect(
        "Danh sách quét:",
        options=all_tickers,
        default=all_tickers[:10], # Mặc định lấy 10 mã đầu tiên
        key="selected_list"
    )

    @st.cache_data(ttl=600)
    def lay_du_lieu_safe(ticker):
        try:
            time.sleep(0.2)
            df = s.stock_price.khop_lenh_history(symbol=ticker, period='1y')
            if df.empty: return None
            
            curr_price = df['close'].iloc[-1]
            vol_avg = df['volume'].tail(20).mean()
            v_ratio = df['volume'].iloc[-1] / (vol_avg + 1e-9)
            
            return {
                'Mã': ticker, 'Giá': curr_price, 
                'Sức mạnh Vol': round(v_ratio, 2),
                'Trạng thái': "🔥 ĐỘT BIẾN" if v_ratio > 1.3 else "⏳ TÍCH LŨY"
            }
        except: return None

    if st.button('🔍 QUÉT DÒNG TIỀN NGAY'):
        if not selected_list:
            st.warning("Hãy chọn ít nhất 1 mã!")
        else:
            progress_bar = st.progress(0)
            results = []
            for i, t in enumerate(selected_list):
                res = lay_du_lieu_safe(t)
                if res: results.append(res)
                progress_bar.progress((i + 1) / len(selected_list))
            
            if results:
                st.success(f"Quét xong {len(results)} mã!")
                df = pd.DataFrame(results).sort_values(by='Sức mạnh Vol', ascending=False)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("⚠️ Thị trường đang nghỉ, chưa có dữ liệu mới.")

    st.sidebar.markdown("---")
    st.sidebar.write(f"Sàn HOSE khả dụng: {len(all_tickers)} mã")
