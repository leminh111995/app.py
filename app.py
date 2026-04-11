import streamlit as st
from vnstock import *
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import yfinance as yf

# ==========================================
# 1. BẢO MẬT & CẤU HÌNH
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
    st.set_page_config(page_title="Hệ Thống Phân Tích Toàn Diện", layout="wide")
    st.title("🚀 Hệ Thống Phân Tích Kỹ Thuật & Dòng Tiền 24/7")

    # --- HÀM LẤY DỮ LIỆU ĐA NGUỒN ---
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

    # --- DANH SÁCH MÃ ---
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

    # --- HIỂN THỊ CHÍNH ---
    tab1, tab2, tab3 = st.tabs(["📊 Phân tích Kỹ thuật", "🏢 Sức mạnh Cơ bản", "🌊 Dòng tiền & Ngành"])

    with tab1: # PHÂN TÍCH KỸ THUẬT (Đã có sẵn)
        if st.button(f'🚀 CHẨN ĐOÁN KỸ THUẬT {final_ticker}'):
            df = lay_du_lieu_thong_minh(final_ticker)
            if df is not None and not df.empty:
                # Tính chỉ báo
                df['MA20'] = df['close'].rolling(20).mean()
                df['Upper'] = df['MA20'] + (df['close'].rolling(20).std() * 2)
                df['Lower'] = df['MA20'] - (df['close'].rolling(20).std() * 2)
                last_row = df.iloc[-1]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Giá Hiện Tại", f"{last_row['close']:,.0f}")
                c2.write(f"**Vùng Bollinger:** {last_row['Lower']:,.0f} - {last_row['Upper']:,.0f}")
                c3.write(f"**Trạng thái:** {'TỐT' if last_row['close'] > last_row['MA20'] else 'YẾU'}")
                
                st.area_chart(df.tail(60)[['close']])
                st.success(f"Dữ liệu kỹ thuật của {final_ticker} đã sẵn sàng.")
            else: st.error("Lỗi dữ liệu!")

    with tab2: # SỨC MẠNH CƠ BẢN (Nâng cấp mới)
        st.subheader(f"💎 Sức khỏe tài chính: {final_ticker}")
        try:
            ratio = financial_ratio(final_ticker, report_range='quarterly', is_not_all=True).iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("P/E", f"{ratio['ticker_pe']:.1f}")
            c2.metric("P/B", f"{ratio['ticker_pb']:.1f}")
            c3.metric("ROE", f"{ratio['roe']:.1%}")
            c4.metric("EPS Growth", f"{ratio['earning_per_share_growth']:.1%}")
            
            st.info("💡 Lời khuyên: P/E thấp và ROE > 15% là dấu hiệu của doanh nghiệp cực tốt.")
        except: st.warning("Dữ liệu cơ bản đang được cập nhật cho mã này.")

    with tab3: # DÒNG TIỀN & NGÀNH (Yêu cầu mới)
        st.subheader(f"🌊 Xu hướng dòng tiền & Nhóm ngành")
        try:
            # 1. Lấy dòng tiền Smart Money
            flow = financial_flow(final_ticker, report_type='net_flow', report_range='daily').tail(10)
            st.write("**Dòng tiền Tự doanh & Nước ngoài (10 phiên gần nhất):**")
            st.bar_chart(flow[['foreign', 'prop']])
            
            # 2. Xác định ngành
            ls = stock_listing()
            industry = ls[ls['ticker'] == final_ticker]['en_icb_name_lv4'].values[0]
            st.markdown(f"🚩 Cổ phiếu thuộc nhóm ngành: **{industry}**")
            
            # 3. Phân tích ngành (Quét Top mã cùng ngành)
            same_industry = ls[ls['en_icb_name_lv4'] == industry]['ticker'].head(5).tolist()
            st.write(f"**So sánh sức mạnh trong nhóm {industry}:**")
            
            industry_results = []
            for t in same_industry:
                try:
                    d = stock_historical_data(symbol=t, start_date=(datetime.now()-timedelta(days=10)).strftime('%Y-%m-%d'), end_date=datetime.now().strftime('%Y-%m-%d'), resolution='1D', type='stock')
                    vol_change = d['volume'].iloc[-1] / d['volume'].mean()
                    industry_results.append({'Mã': t, 'Biến động Vol': round(vol_change, 2)})
                except: pass
            
            st.table(pd.DataFrame(industry_results))
            st.caption("Ghi chú: 'Biến động Vol' > 1 nghĩa là dòng tiền đang vào ngành này mạnh hơn trung bình.")
        except: st.warning("Không thể truy xuất dữ liệu ngành lúc này.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Phiên bản Toàn Diện 24/7 - Made for Minh")
