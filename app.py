import streamlit as st
from vnstock import Vnstock
import pandas as pd
import time

# 1. Cấu hình bảo mật đơn giản
def check_password():
    """Trả về True nếu người dùng nhập đúng mật khẩu."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Xóa mật khẩu khỏi bộ nhớ tạm
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Vui lòng nhập mật mã để mở Robot:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Sai mật mã! Nhập lại:", type="password", on_change=password_entered, key="password")
        st.error("😕 Mật mã không đúng.")
        return False
    else:
        return True

# 2. Giao diện chính sau khi đã đăng nhập thành công
if check_password():
    st.set_page_config(page_title="Robot Cá Nhân - HOSE", layout="wide")
    st.title("🚀 Robot Riêng Của Minh")

    s = Vnstock()

    # Tối ưu hóa: Dùng Cache để không quét lại mã cũ trong vòng 30 phút
    @st.cache_data(ttl=1800)
    def lay_du_lieu_safe(ticker):
        try:
            time.sleep(0.2) # Nghỉ một chút để an toàn cho IP của bạn
            df = s.stock_price.khop_lenh_history(symbol=ticker, period='1y')
            if df.empty: return None
            
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

    # Danh sách các mã bạn quan tâm (Có thể lên đến 50-100 mã mà vẫn an toàn)
    my_list = ["FPT","HPG","SSI","VNM","TCB","MWG","VHM","STB","MSN","VCI","DGC","VND","PVD","NKG","HSG"]

    if st.button('🎯 QUÉT DÒNG TIỀN NGAY'):
        progress_bar = st.progress(0)
        results = []
        
        for i, t in enumerate(my_list):
            res = lay_du_lieu_safe(t)
            if res: results.append(res)
            progress_bar.progress((i + 1) / len(my_list))
        
        st.success("Đã quét xong danh sách cá nhân!")
        df = pd.DataFrame(results)
        st.dataframe(df.sort_values(by='Sức mạnh Vol', ascending=False), use_container_width=True)

    st.sidebar.write("Chúc bạn một ngày giao dịch thành công!")
