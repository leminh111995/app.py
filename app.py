import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Thư viện AI và NLP
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==========================================
# 1. BẢO MẬT & SETUP
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("🔑 Nhập mật mã của Minh:", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    st.set_page_config(page_title="Quant System V6 - Trùm Cuối", layout="wide")
    st.title("🛡️ Hệ Thống Chiến Thuật V6: Radar + AI + CanSLIM")

    s = Vnstock()

    # --- HÀM LẤY DỮ LIỆU KỸ THUẬT ---
    def lay_du_lieu(ticker, days=1000):
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            df = s.stock.quote.history(symbol=ticker, start=start_date, end=end_date)
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                return df
        except: pass
        try:
            yt = yf.download(f"{ticker}.VN", period="3y", progress=False)
            yt = yt.reset_index()
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except: return None

    # --- TÍNH TOÁN CHỈ BÁO & FEATURE CHO AI ---
    def tinh_toan_chi_bao(df):
        df = df.copy()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper_band'] = df['ma20'] + (df['std'] * 2)
        df['lower_band'] = df['ma20'] - (df['std'] * 2)
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # FEATURE CHO AI
        df['return_1d'] = df['close'].pct_change()
        df['volatility'] = df['return_1d'].rolling(20).std()
        df['vol_change'] = df['volume'] / df['volume'].rolling(10).mean()
        df['money_flow'] = df['close'] * df['volume']
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1), -1, 0))
        
        return df.dropna()

    # --- MÔ HÌNH DỰ BÁO AI ---
    def du_bao_ai(df):
        if len(df) < 200: return "N/A"
        df_copy = df.copy()
        df_copy['target'] = (df_copy['close'].shift(-3) > df_copy['close'] * 1.02).astype(int)
        
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data = df_copy.dropna()
        X = data[features]
        y = data['target']
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X[:-3], y[:-3])
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    # --- HÀM TÍNH TĂNG TRƯỞNG CANSLIM ---
    def tinh_tang_truong_lnst(ticker):
        try:
            df_inc = s.stock.finance.income_statement(symbol=ticker, period='quarter', lang='vi')
            df_inc = df_inc.head(5) 
            col_name = [c for c in df_inc.columns if 'sau thuế' in c.lower() or 'posttax' in c.lower()][0]
            lnst_q1 = df_inc.iloc[0][col_name]
            lnst_q5 = df_inc.iloc[4][col_name]
            if lnst_q5 <= 0: return None
            growth = ((lnst_q1 - lnst_q5) / lnst_q5) * 100
            return round(growth, 1)
        except: return None

    # --- PHÂN TÍCH TÂM LÝ TIN TỨC ---
    def phan_tich_tin_tuc(ticker):
        try:
            news = s.stock.news(ticker).head(5)
            analyzer = SentimentIntensityAnalyzer()
            scores = [analyzer.polarity_scores(t)['compound'] for t in news['title']]
            avg = np.mean(scores)
            if avg > 0.05: status = "🟢 Tích cực"
            elif avg < -0.05: status = "🔴 Tiêu cực"
            else: status = "🟡 Trung lập"
            return status, news
        except: return "⚪ Không xác định", pd.DataFrame()

    # --- DANH SÁCH MÃ ---
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma():
        try: return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = lay_danh_sach_ma()
    st.sidebar.header("🕹️ Điều khiển")
    selected = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_tickers)
    manual = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    final_ticker = manual if manual else selected

    # 4 TAB HOÀN CHỈNH
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 KỸ THUẬT & RADAR", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 DÒNG TIỀN", 
        "🔍 TRUY QUÉT TOÀN SÀN"
    ])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {final_ticker}"):
            df = lay_du_lieu(final_ticker)
            if df is not None and not df.empty:
                df = tinh_toan_chi_bao(df)
                last = df.iloc[-1]
                ai_p = du_bao_ai(df)
                
                # --- METRICS CƠ BẢN ---
                st.write("### 🎯 Mục tiêu & Rủi ro")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                m2.metric("Dự báo AI (Đã tích hợp Vol)", f"{ai_p}%" if isinstance(ai_p, float) else "N/A")
                m3.success(f"Chốt lời: {last['close']*1.1:,.0f}")
                m4.error(f"Cắt lỗ: {last['close']*0.93:,.0f}")
                
                st.divider()

                # --- RADAR ĐỈNH / ĐÁY NGẮN HẠN (ĐÃ TÍCH HỢP LẠI) ---
                st.write("### 📡 Radar Phát Hiện Đỉnh/Đáy Ngắn Hạn")
                close_p = last['close']
                ma20 = last['ma20']
                upper = last['upper_band']
                lower = last['lower_band']
                rsi = last['rsi']
                vol_change = last['vol_change']
                
                if rsi > 65 and close_p >= upper * 0.98:
                    drop_to_ma20 = ((close_p - ma20) / close_p) * 100
                    drop_to_lower = ((close_p - lower) / close_p) * 100
                    st.error(f"**🚨 CẢNH BÁO TẠO ĐỈNH NGẮN HẠN:** Giá đang rướn quá mức dải trên Bollinger và bị kéo căng (RSI = {rsi:.1f}).")
                    st.write(f"- **Kịch bản điều chỉnh 1:** Rơi về hỗ trợ MA20 ({ma20:,.0f}đ) ➔ **Mức giảm dự kiến: -{drop_to_ma20:.1f}%**")
                    st.write(f"- **Kịch bản điều chỉnh 2:** Rơi thẳng về dải dưới ({lower:,.0f}đ) ➔ **Mức giảm tối đa: -{drop_to_lower:.1f}%**")
                    if vol_change > 1.5: st.warning("⚠️ LƯU Ý MỞ RỘNG ĐỈNH: Khối lượng xả đang rất lớn, đây là đỉnh thật, tuyệt đối không bắt dao rơi!")
                
                elif rsi < 35 and close_p <= lower * 1.02:
                    rise_to_ma20 = ((ma20 - close_p) / close_p) * 100
                    rise_to_upper = ((upper - close_p) / close_p) * 100
                    st.success(f"**🌟 TÍN HIỆU TẠO ĐÁY NGẮN HẠN:** Lực bán đã cạn kiệt, giá đâm thủng dải dưới và RSI rớt vùng quá bán ({rsi:.1f}).")
                    st.write(f"- **Kịch bản hồi phục 1:** Bật lên trạm giữa MA20 ({ma20:,.0f}đ) ➔ **Mức tăng dự kiến: +{rise_to_ma20:.1f}%**")
                    st.write(f"- **Kịch bản hồi phục 2:** Sóng hồi mạnh lên dải trên ({upper:,.0f}đ) ➔ **Mức tăng tối đa: +{rise_to_upper:.1f}%**")
                    if vol_change < 0.8: st.warning("⚠️ LƯU Ý ĐÁY GIẢ (BULL TRAP): Khối lượng bắt đáy quá thấp (< 0.8), có nguy cơ đây chỉ là hồi kỹ thuật rồi rơi tiếp. Cần chờ thêm 1 phiên xác nhận Vol!")
                
                else:
                    dist_upper = ((upper - close_p) / close_p) * 100
                    dist_lower = ((close_p - lower) / close_p) * 100
                    st.info(f"**⚖️ TRẠNG THÁI CÂN BẰNG:** Chưa có dấu hiệu Đỉnh hay Đáy cực đoan. Cổ phiếu đang tích lũy.")
                    st.write(f"- Dư địa tăng lên vùng đỉnh cũ (Upper Band): **+{dist_upper:.1f}%**")
                    st.write(f"- Khoảng lùi về vùng đáy cũ (Lower Band): **-{dist_lower:.1f}%**")

                st.divider()

                # --- CHỈ SỐ KỸ THUẬT & CẨM NANG (BỔ SUNG NÉ TÍN HIỆU GIẢ) ---
                st.write("### 🎛️ Chỉ số Kỹ thuật Chi tiết")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("RSI (14)", round(last['rsi'], 1), delta="Quá mua" if last['rsi']>70 else "Quá bán" if last['rsi']<30 else None, delta_color="inverse")
                k2.metric("MACD", round(last['macd'], 2), delta="Tăng" if last['macd']>last['signal'] else "Giảm")
                k3.write(f"**Bollinger Upper:** {last['upper_band']:,.0f}")
                k3.write(f"**Bollinger Lower:** {last['lower_band']:,.0f}")
                k4.write(f"**MA50:** {last['ma50']:,.0f}")
                k4.write(f"**MA200:** {last['ma200']:,.0f}")

                vol_avg = df['volume'].tail(10).mean()
                vol_ratio = last['volume'] / vol_avg if vol_avg > 0 else 0
                macd_status = "TÍCH CỰC (Dòng tiền mua chủ động)" if last['macd'] > last['signal'] else "TIÊU CỰC (Dòng tiền rút ra)"

                with st.expander("📖 CẨM NANG ĐỌC TÍN HIỆU & NÉ FALSE BREAKOUT (Bấm để mở)"):
                    st.markdown(f"""
**1. Khối lượng (Volume) & Dòng tiền:**
* **Thực tế mã {final_ticker}:** Khối lượng bằng **{vol_ratio:.1f} lần** trung bình 10 phiên. {'🔥 CÓ SỰ BÙNG NỔ DÒNG TIỀN' if vol_ratio > 1.2 else '❄️ KHỐI LƯỢNG BÌNH THƯỜNG'}.

**2. CÁCH NÉ TÍN HIỆU GIẢ (FALSE BREAKOUT / BULL TRAP):**
* **Né Đỉnh Giả (Breakout hụt):** Giá vượt đỉnh cũ nhưng Khối lượng < Trung bình 10 phiên (Tỷ lệ < 1.0). Đây là kéo xả, tuyệt đối không mua đuổi.
* **Né Đáy Giả (Bắt dao rơi):** Giá chạm đáy dưới Bollinger, RSI quá bán nhưng Khối lượng xả vẫn đỏ lòm và cao hơn trung bình (Tỷ lệ > 1.0). Đừng bắt đáy, dòng tiền to vẫn đang tháo chạy!
* **Quy tắc vàng:** Chỉ mua khi Radar báo Đáy + Nến hôm sau là nến XANH rút chân + Khối lượng Vol tăng dần.

**3. Chỉ báo MACD (Xu hướng cốt lõi):**
* **Thực tế mã {final_ticker}:** MACD ({last['macd']:.2f}) đang {'nằm TRÊN' if last['macd'] > last['signal'] else 'nằm DƯỚI'} đường Signal ➔ **{macd_status}**.

---
🚨 **NGUYÊN TẮC BẤT KHẢ KHÁNG (THIÊN NGA ĐEN):**
* Khi dính tin đồn bắt bớ, chiến tranh... phân tích kỹ thuật sẽ vô tác dụng. Tuân thủ Cắt Lỗ (SL) là **{last['close']*0.93:,.0f}**.
                    """)

                # Biểu đồ nến
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df['date'].tail(150), open=df['open'].tail(150), high=df['high'].tail(150), low=df['low'].tail(150), close=df['close'].tail(150), name='Nến'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'].tail(150), y=df['ma50'].tail(150), line=dict(color='orange', width=1.5), name='MA50'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'].tail(150), y=df['ma200'].tail(150), line=dict(color='purple', width=2), name='MA200'), row=1, col=1)
                fig.add_trace(go.Bar(x=df['date'].tail(150), y=df['volume'].tail(150), marker_color='gray', name='Vol'), row=2, col=1)
                fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            else: st.error("Lỗi lấy dữ liệu!")

    with tab2:
        # --- BỘ LỌC CANSLIM HIỂN THỊ TẠI ĐÂY ---
        st.write(f"### 📈 Chấm điểm Tăng trưởng CanSLIM ({final_ticker})")
        with st.spinner("Đang phân tích Báo cáo Tài chính..."):
            growth = tinh_tang_truong_lnst(final_ticker)
            if growth is not None:
                if growth > 20:
                    st.success(f"**🔥 TUYỆT VỜI:** Lợi nhuận sau thuế quý gần nhất tăng **+{growth}%** so với cùng kỳ. Đạt tiêu chuẩn chữ C trong CanSLIM!")
                elif growth > 0:
                    st.info(f"**⚖️ TRUNG BÌNH:** Lợi nhuận tăng nhẹ **+{growth}%** so với cùng kỳ. Doanh nghiệp làm ăn ổn định nhưng chưa có sự bùng nổ.")
                else:
                    st.error(f"**🚨 RỦI RO:** Lợi nhuận ĐI LÙI **{growth}%** so với cùng kỳ. Thận trọng nếu giá đang ở vùng đỉnh (phân phối).")
            else:
                st.warning("Không đủ dữ liệu Báo cáo Tài chính (hoặc doanh nghiệp mới lên sàn/lỗ năm trước).")
        
        st.divider()
        st.write("### 🏢 Sức khỏe Tài chính (Định giá)")
        try:
            ratio = s.stock.finance.ratio(final_ticker, 'quarterly').iloc[-1]
            c1, c2 = st.columns(2)
            c1.metric("P/E (Định giá)", f"{ratio.get('ticker_pe', 0):.1f}")
            c2.metric("ROE (Hiệu quả Vốn)", f"{ratio.get('roe', 0):.1%}")
        except: st.warning("Dữ liệu tài chính đang cập nhật.")

        st.divider()
        st.write("### 🧠 Tâm lý Tin tức Báo chí")
        status, news = phan_tich_tin_tuc(final_ticker)
        st.metric("Tâm lý chung:", status)
        if not news.empty:
            for _, r in news.iterrows(): st.write(f"- {r['title']}")

    with tab3:
        st.write("### 🌊 Dòng tiền Tự doanh & Khối ngoại")
        try:
            flow = s.stock.finance.flow(final_ticker, 'net_flow', 'daily').tail(10)
            st.bar_chart(flow[['foreign', 'prop']])
        except: st.warning("Dòng tiền đang cập nhật...")

    with tab4:
        st.subheader("🔍 Truy quét Toàn sàn & Lọc mã Tiềm năng")
        if st.button("🔥 CHẠY RÀ SOÁT CHUNG (TOP 30 HOSE)"):
            hits = []
            bar = st.progress(0)
            for i, t in enumerate(all_tickers[:30]):
                try:
                    d = lay_du_lieu(t, days=300)
                    if d is not None:
                        d = tinh_toan_chi_bao(d)
                        prob = du_bao_ai(d)
                        vol_avg = d['volume'].tail(10).mean()
                        if d['volume'].iloc[-1] > vol_avg * 1.3:
                            hits.append({
                                'Mã': t, 
                                'Giá': d['close'].iloc[-1], 
                                'Sức mạnh Vol': round(d['volume'].iloc[-1]/vol_avg, 2),
                                'AI Dự báo Tăng (%)': prob
                            })
                except: pass
                bar.progress((i+1)/30)
            if hits:
                res_df = pd.DataFrame(hits).sort_values(by='AI Dự báo Tăng (%)', ascending=False)
                st.table(res_df)
                st.success("✅ Đã tìm ra các mã có tín hiệu bùng nổ khối lượng và xác suất tăng cao.")
            else: st.write("Chưa tìm thấy mã bùng nổ.")
