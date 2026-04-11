import streamlit as st
from vnstock import Vnstock
import pandas as pd
import time

# 1. Cấu hình bảo mật
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Vui lòng nhập mật mã của Minh:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Sai mật mã! Nhập lại:", type="password", on_change=password_entered, key="password")
        st.error("😕 Mật mã không đúng.")
        return False
    else:
        return True

if check_password():
    st.set_page_config(page_title="Robot Cá Nhân - HOSE", layout="wide")
    st.title("🚀 Robot Phân Tích Siêu Cổ Phiếu")

    s = Vnstock()

    # --- TỰ ĐỘNG LẤY DANH SÁCH MÃ TỪ SÀN ---
    @st.cache_data
    def get_all_tickers():
        try:
            df_ls = s.market.listing()
            # Chỉ lấy các mã trên sàn HOSE
            return df_ls[df_ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","VNM","TCB","MWG","VIC","VHM","STB","MSN"]

    all_tickers = get_all_tickers()

    # Tạo ô chọn mã đa năng trên giao diện
    st.sidebar.header("Cài đặt danh mục")
    selected_list = st.sidebar.multiselect(
        "Chọn các mã bạn muốn quét:",
        options=all_tickers,
        default=["FPT","HPG","SSI","TCB","MWG"] # Các mã mặc định hiện ra
    )
    # ---------------------------------------

    @st.cache_data(ttl=1800)
    def lay_du_lieu_safe(ticker):
        try:
            time.sleep(0.2) 
            df = s.stock_price.khop_lenh_history(symbol=ticker, period='1y')
            if df.empty or len(df) < 5: return None
            
            curr_price = df['close'].iloc[-1]
            vol_avg = df['volume'].tail(20).mean()
            v_ratio = df['volume'].iloc[-1] / (vol_avg + 1e-9)
            
            return {
                'Mã': ticker, 
                'Giá': curr_price, 
                'Sức mạnh Vol': round(v_ratio, 2),
                'Trạng thái': "🔥 ĐỘT BIẾN" if v_ratio > 1.3 else "⏳ TÍCH LŨY"
            }
        except:
            return None

    if st.button('🎯 QUÉT DÒNG TIỀN NGAY'):
        if not selected_list:
            st.warning("Bạn chưa chọn mã nào để quét cả!")
        else:
            progress_bar = st.progress(0)
            results = []
            
            for i, t in enumerate(selected_list):
                res = lay_du_lieu_safe(t)
                if res: results.append(res)
                progress_bar.progress((i + 1) / len(selected_list))
            
            if results:
                st.success(f"Đã quét xong {len(results)} mã bạn chọn!")
                df = pd.DataFrame(results)
                st.dataframe(df.sort_values(by='Sức mạnh Vol', ascending=False), use_container_width=True)
            else:
                st.warning("⚠️ Hiện tại server không trả về dữ liệu (Thị trường đang nghỉ).")

    st.sidebar.markdown("---")
    st.sidebar.write(f"Tổng số mã HOSE khả dụng: {len(all_tickers)}")
