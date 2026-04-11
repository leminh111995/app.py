import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. BẢO MẬT (GIAO DIỆN SÁNG MẶC ĐỊNH)
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: 
            st.session_state["password_correct"] = False
            
    if "password_correct" not in st.session_state:
        st.text_input(
            "🔑 Nhập mật mã của Minh:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    st.set_page_config(page_title="Robot Siêu Cấp 2026", layout="wide")
    st.title("🛡️ Hệ Thống Chiến Thuật & Quản Trị Rủi Ro")

    s = Vnstock()

    # --- HÀM LẤY DỮ LIỆU ---
    def lay_du_lieu(ticker):
        try:
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            df = s.stock.quote.history(
                symbol=ticker, 
                start=start_date, 
                end=end_date
            )
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                return df
        except: 
            pass
            
        try:
            yt = yf.download(f"{ticker}.VN", period="2y", progress=False)
            yt = yt.reset_index()
            yt.columns = [
                col[0].lower() if isinstance(col, tuple) else col.lower() 
                for col in yt.columns
            ]
            return yt
        except: 
            return None

    # --- TÍNH TOÁN CHỈ BÁO ---
    def tinh_toan_chien_thuat(df):
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        return df

    # --- TÍNH TỶ LỆ THẮNG ---
    def tinh_ty_le_thang(df):
        win = 0
        total = 0
        for i in range(200, len(df)-10):
            cond1 = df['rsi'].iloc[i] < 45
            cond2 = df['macd'].iloc[i] > df['signal'].iloc[i]
            cond3 = df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
            
            if cond1 and cond2 and cond3:
                total += 1
                buy_p = df['close'].iloc[i]
                if any(df['close'].iloc[i+1:i+11] > buy_p * 1.05): 
                    win += 1
                    
        if total > 0:
            return round((win/total)*100, 1)
        else:
            return 0

    # --- LẤY DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma():
        try:
            ls = s.market.listing()
            return ls[ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = lay_danh_sach_ma()
    st.sidebar.header("🕹️ Điều khiển")
    selected = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_tickers)
    manual = st.sidebar.text_input("Nhập mã thủ công:").upper()
    final_ticker = manual if manual else selected

    # 4 TAB CHỨC NĂNG
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 CHIẾN THUẬT LIVE", 
        "🏢 CƠ BẢN & TIN TỨC", 
        "🌊 DÒNG TIỀN & NGÀNH", 
        "🔍 TRUY QUÉT TOÀN SÀN"
    ])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH {final_ticker}"):
            df = lay_du_lieu(final_ticker)
            if df is not None and not df.empty:
                df = tinh_toan_chien_thuat(df)
                last = df.iloc[-1]
                wr = tinh_ty_le_thang(df)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                c2.metric("Tỷ lệ thắng", f"{wr}%")
                c3.success(f"🎯 Mục tiêu (TP): {last['close']*1.1:,.0f}")
                c4.error(f"🛑 Cắt lỗ (SL): {last['close']*0.93:,.0f}")

                fig = make_subplots(
                    rows=2, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.03, row_heights=[0.7, 0.3]
                )
                
                fig.add_trace(go.Candlestick(
                    x=df['date'], open=df['open'], high=df['high'], 
                    low=df['low'], close=df['close'], name='Nến'), row=1, col=1)
                
                # Đổi màu MA50 thành Cam đậm và MA200 thành Tím đậm để dễ nhìn trên nền trắng
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['ma50'], 
                    line=dict(color='#FF8C00', width=1.5), name='MA50'), row=1, col=1)
                
                fig.add_trace(go.Scatter(
                    x=df['date'], y=df['ma200'], 
                    line=dict(color='#800080', width=2), name='MA200'), row=1, col=1)
                
                fig.add_trace(go.Bar(
                    x=df['date'], y=df['volume'], 
                    marker_color='#555555', name='Vol'), row=2, col=1)
                
                # Đổi template biểu đồ sang nền trắng
                fig.update_layout(
                    height=600, template='plotly_white', xaxis_rangeslider_visible=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.write(f"### 💬 Nhận định xu hướng: {'🌟 GIAO CẮT VÀNG (UPTREND)' if last['ma50'] > last['ma200'] else '⏳ CHỜ ĐỢI TÍN HIỆU RÕ RÀNG'}")
            else: 
                st.error("Lỗi lấy dữ liệu kỹ thuật!")

    with tab2:
        st.subheader(f"🏢 Sức khỏe doanh nghiệp & Tin tức: {final_ticker}")
        try:
            ratio = s.stock.finance.ratio(final_ticker, report_range='quarterly').iloc[-1]
            c1, c2 = st.columns(2)
            c1.metric("ROE (Hiệu quả vốn)", f"{ratio.get('roe', 0):.1%}")
            c2.metric("P/E (Định giá)", f"{ratio.get('ticker_pe', 0):.1f}")
            st.divider()
            
            news = s.stock.news(final_ticker)
            for _, n in news.head(5).iterrows():
                st.write(f"🔔 **{n['title']}** (*{n['publishDate']}*)")
        except: 
            st.warning("Dữ liệu cơ bản đang được cập nhật (Server có thể đang bảo trì cuối tuần).")

    with tab3:
        st.subheader("🌊 Phân tích Dòng tiền & Khối lượng")
        try:
            flow = s.stock.finance.flow(final_ticker, report_type='net_flow', report_range='daily').tail(10)
            st.write("**Biến động dòng tiền Tự doanh & Nước ngoài (10 phiên):**")
            st.bar_chart(flow[['foreign', 'prop']])
            
            ls = s.market.listing()
            industry = ls[ls['ticker'] == final_ticker]['en_icb_name_lv4'].values[0]
            st.info(f"🚩 Nhóm ngành: **{industry}**")
            
            peers = ls[ls['en_icb_name_lv4'] == industry]['ticker'].head(8).tolist()
            st.write(f"**So sánh Sức mạnh Vol trong ngành {industry}:**")
            p_res = []
            for t in peers:
                try:
                    d = s.stock.quote.history(symbol=t, start=(datetime.now()-timedelta(days=15)).strftime('%Y-%m-%d'), end=datetime.now().strftime('%Y-%m-%d'))
                    p_res.append({'Mã': t, 'Sức mạnh Vol': round(d['volume'].iloc[-1]/d['volume'].mean(), 2)})
                except: 
                    pass
            if p_res:
                st.table(pd.DataFrame(p_res).sort_values(by='Sức mạnh Vol', ascending=False))
        except: 
            st.warning("Dữ liệu dòng tiền ngành chưa sẵn sàng ngoài giờ giao dịch.")

    with tab4:
        st.subheader("🕵️ Robot quét mã tiềm năng")
        if st.button("🔥 BẮT ĐẦU TRUY QUÉT (TOP 30)"):
            hits = []
            scan_list = all_tickers[:30]
            progress = st.progress(0)
            for i, t in enumerate(scan_list):
                try:
                    d = lay_du_lieu(t)
                    if d is not None:
                        d = tinh_toan_chien_thuat(d)
                        vol_avg = d['volume'].tail(10).mean()
                        if d['volume'].iloc[-1] > vol_avg * 1.3:
                            hits.append({
                                'Mã': t, 
                                'Giá': d['close'].iloc[-1], 
                                'Tỷ lệ thắng': f"{tinh_ty_le_thang(d)}%"
                            })
                except: 
                    pass
                progress.progress((i+1)/len(scan_list))
                
            if hits: 
                st.table(pd.DataFrame(hits))
            else: 
                st.write("Hiện chưa tìm thấy mã đạt chuẩn bùng nổ khối lượng.")
