import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np

# Cấu hình giao diện web
st.set_page_config(page_title="Robot Săn Cá Mập HOSE", layout="wide")

st.title("🚀 Robot Phân Tích Siêu Cổ Phiếu HOSE")
st.markdown("Hệ thống quét dòng tiền Smart Money và đột biến khối lượng.")

# Khởi tạo Vnstock
s = Vnstock()

def quet_du_lieu():
    try:
        df_ls = s.market.listing()
        tickers = df_ls[df_ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
        
        all_data = []
        # Quét 50 mã đầu tiên để trang web chạy nhanh
        for ticker in tickers[:50]:
            try:
                df = s.stock_price.khop_lenh_history(symbol=ticker, period='1y')
                if df.empty: continue
                
                curr_price = df['close'].iloc[-1]
                if curr_price < 10000: continue
                
                vol_avg = df['volume'].tail(20).mean()
                v_ratio = df['volume'].iloc[-1] / (vol_avg + 1e-9)
                
                all_data.append({
                    'Mã': ticker, 
                    'Giá': curr_price, 
                    'Sức mạnh Vol': round(v_ratio, 2),
                    'Dự báo': "🔥 ĐỘT BIẾN" if v_ratio > 1.3 else "⏳ TÍCH LŨY"
                })
            except: continue
        return pd.DataFrame(all_data)
    except:
        return pd.DataFrame()

# Nút bấm trên web
if st.button('🔍 BẮT ĐẦU QUÉT TOÀN SÀN'):
    with st.spinner('Đang lùng sục dữ liệu...'):
        df_final = quet_du_lieu()
        if not df_final.empty:
            st.success('Đã tìm thấy mã tiềm năng!')
            st.dataframe(df_final.sort_values(by='Sức mạnh Vol', ascending=False), use_container_width=True)
        else:
            st.error('Server dữ liệu đang bảo trì. Thử lại sau ít phút!')

st.sidebar.info("Lưu ý: Robot hoạt động tốt nhất trong giờ giao dịch Thứ 2 - Thứ 6.")
