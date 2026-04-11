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
    st.set_page_config(page_title="Quant System V8.0 - Ultimate", layout="wide")
    st.title("🛡️ Quant System V8.0: Hệ Thống Chiến Thuật Toàn Diện")

    s = Vnstock()

    # --- HÀM LẤY DỮ LIỆU ---
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

    # --- TÍNH TOÁN CHỈ BÁO KỸ THUẬT & FEATURES AI ---
    def tinh_toan_chi_bao(df):
        df = df.copy()
        # Moving Averages
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        # Bollinger Bands
        df['std'] = df['close'].rolling(20).std()
        df['upper_band'] = df['ma20'] + (df['std'] * 2)
        df['lower_band'] = df['ma20'] - (df['std'] * 2)
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        # Features AI
        df['return_1d'] = df['close'].pct_change()
        df['vol_change'] = df['volume'] / df['volume'].rolling(10).mean()
        df['money_flow'] = df['close'] * df['volume']
        df['volatility'] = df['return_1d'].rolling(20).std()
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1.1), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1.1), -1, 0))
        return df.dropna()

    # --- CHẨN ĐOÁN TÂM LÝ ĐÁM ĐÔNG ---
    def chan_doan_tam_ly(df):
        last = df.iloc[-1]
        rsi = last['rsi']
        if rsi > 75: label = "🔥 CỰC KỲ THAM LAM (QUÁ MUA)"; color = "red"
        elif rsi > 60: label = "⚖️ THAM LAM (LẠC QUAN)"; color = "orange"
        elif rsi < 30: label = "💀 CỰC KỲ SỢ HÃI (QUÁ BÁN)"; color = "cyan"
        elif rsi < 40: label = "😨 SỢ HÃI (BI QUAN)"; color = "blue"
        else: label = "🟡 TRUNG LẬP"; color = "gray"
        return label, round(rsi, 0)

    # --- TÍNH TỶ LỆ THẮNG LỊCH SỬ (BACKTEST) ---
    def tinh_ty_le_thang(df):
        win = 0; total = 0
        for i in range(100, len(df)-10):
            # Chiến thuật: RSI < 45 + MACD cắt lên
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]:
                total += 1
                if any(df['close'].iloc[i+1:i+11] > df['close'].iloc[i] * 1.05): win += 1
        return round((win/total)*100, 1) if total > 0 else 0

    # --- MÔ HÌNH DỰ BÁO AI ---
    def du_bao_ai(df):
        if len(df) < 200: return "N/A"
        df_copy = df.copy()
        df_copy['target'] = (df_copy['close'].shift(-3) > df_copy['close'] * 1.02).astype(int)
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data = df_copy.dropna(); X = data[features]; y = data['target']
        model = RandomForestClassifier(n_estimators=100, random_state=42); model.fit(X[:-3], y[:-3])
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    # --- HÀM TÀI CHÍNH & CANSLIM (FIX SSI/BANK) ---
    def tinh_tang_truong_lnst(ticker):
        try:
            df_inc = s.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            target_cols = [c for c in df_inc.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])]
            if target_cols:
                lnst_q1 = float(df_inc.iloc[0][target_cols[0]]); lnst_q5 = float(df_inc.iloc[4][target_cols[0]])
                if lnst_q5 > 0: return round(((lnst_q1 - lnst_q5) / lnst_q5) * 100, 1)
        except: pass
        try:
            info = yf.Ticker(f"{ticker}.VN").info
            growth = info.get('earningsQuarterlyGrowth')
            if growth is not None: return round(growth * 100, 1)
        except: pass
        return None

    def lay_chi_so_co_ban(ticker):
        pe, roe = 0, 0
        try:
            ratio = s.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe = ratio.get('ticker_pe', ratio.get('pe', 0)); roe = ratio.get('roe', 0)
        except: pass
        if pe <= 0:
            try:
                info = yf.Ticker(f"{ticker}.VN").info
                pe = info.get('trailingPE', 0); roe = info.get('returnOnEquity', 0)
            except: pass
        return pe, roe

    # --- SETUP GIAO DIỆN ---
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma():
        try: return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = lay_danh_sach_ma()
    st.sidebar.header("🕹️ Điều khiển")
    selected = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_tickers)
    manual = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    final_ticker = manual if manual else selected

    tab1, tab2, tab3, tab4 = st.tabs(["🤖 KỸ THUẬT & TÂM LÝ", "🏢 CƠ BẢN & CANSLIM", "🌊 SMART FLOW", "🔍 TRUY QUÉT"])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {final_ticker}"):
            df = lay_du_lieu(final_ticker)
            if df is not None and not df.empty:
                df = tinh_toan_chi_bao(df); last = df.iloc[-1]
                ai_p = du_bao_ai(df); wr = tinh_ty_le_thang(df)
                fg_label, fg_score = chan_doan_tam_ly(df)
                
                st.write("### 🧭 Radar & Hiệu Suất")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                c2.metric("Tâm Lý (F&G)", f"{fg_score}/100", delta=fg_label)
                c3.metric("AI Dự Báo (T+3)", f"{ai_p}%")
                c4.metric("Backtest Win-rate", f"{wr}%")
                
                st.divider(); st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Chi Tiết")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("RSI (14)", f"{last['rsi']:.1f}", delta="Quá mua" if last['rsi']>70 else ("Quá bán" if last['rsi']<30 else "Trung tính"))
                k2.metric("MACD Status", f"{last['macd']:.2f}", delta="Cắt lên" if last['macd']>last['signal'] else "Cắt xuống")
                k3.metric("MA20", f"{last['ma20']:,.0f}", delta=f"{((last['close']-last['ma20'])/last['ma20'])*100:.1f}%")
                k4.metric("Dải Bollinger Trên", f"{last['upper_band']:,.0f}")

                with st.expander("📖 CẨM NANG GIẢI THÍCH CHI TIẾT (Bấm để xem)"):
                    st.markdown(f"""
                    **1. Khối lượng (Volume):** Vol đang bằng **{last['vol_change']:.1f} lần** trung bình 10 phiên. 
                    - Giá tăng + Vol cao (>1.2) ➔ Cá mập đang quyết liệt gom hàng.
                    - Giá giảm + Vol cao (>1.2) ➔ Cá mập đang xả hàng (Phân phối).

                    **2. Chỉ báo RSI & MACD:**
                    - RSI dưới 30 ➔ Vùng 'Sợ hãi cực độ', thường là cơ hội bắt đáy.
                    - MACD nằm trên đường Signal ➔ Xu hướng tăng đang được ủng hộ.

                    **3. CÁCH NÉ BẪY GIÁ (BULL TRAP / BEAR TRAP):**
                    - **Né Đỉnh Giả:** Giá bứt phá đỉnh cũ nhưng Vol không tăng (thấp hơn trung bình) ➔ Đây là bẫy dụ mua. Tuyệt đối không mua đuổi.
                    - **Né Đáy Giả:** Giá chạm dải dưới Bollinger nhưng Vol đỏ xả vẫn rất lớn ➔ Đừng bắt đáy vội, hãy chờ một nến xanh rút chân kèm Vol cạn kiệt.

                    **4. Nguyên tắc Thiên nga đen:** Luôn đặt mức cắt lỗi tại **{last['close']*0.93:,.0f} (-7%)** để bảo vệ vốn.
                    """)

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df['date'].tail(120), open=df['open'].tail(120), high=df['high'].tail(120), low=df['low'].tail(120), close=df['close'].tail(120), name='Giá'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'].tail(120), y=df['ma20'].tail(120), line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'].tail(120), y=df['ma50'].tail(120), line=dict(color='blue', width=1.5), name='MA50'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'].tail(120), y=df['upper_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải trên'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'].tail(120), y=df['lower_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải dưới', fill='tonexty'), row=1, col=1)
                fig.add_trace(go.Bar(x=df['date'].tail(120), y=df['volume'].tail(120), name='Khối lượng', marker_color='gray'), row=2, col=1)
                fig.update_layout(height=700, template='plotly_white', xaxis_rangeslider_visible=False, legend=dict(orientation="h", y=1.02, x=1))
                st.plotly_chart(fig, use_container_width=True)
            else: st.error("Lỗi lấy dữ liệu!")

    with tab2:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá ({final_ticker})")
        growth = tinh_tang_truong_lnst(final_ticker)
        if growth is not None:
            if growth > 20: st.success(f"**🔥 CanSLIM:** LNST quý gần nhất tăng **+{growth}%** (Đạt chuẩn - Tốt).")
            elif growth > 0: st.info(f"**⚖️ Tăng trưởng:** LNST tăng **+{growth}%** (Ổn định).")
            else: st.error(f"**🚨 Rủi ro:** LNST đi lùi **{growth}%** (Cảnh báo kinh doanh giảm sút).")
        else: st.warning("Dữ liệu tài chính đang được cập nhật.")
        
        st.divider(); pe, roe = lay_chi_so_co_ban(final_ticker); c1, c2 = st.columns(2)
        pe_status = "Tốt (Rẻ)" if 0 < pe < 12 else ("Hợp lý" if pe < 20 else "Đắt (Mua hớ)")
        c1.metric("P/E (Định giá)", f"{pe:.1f}", delta=pe_status, delta_color="normal" if pe < 20 else "inverse")
        st.caption("💡 **P/E:** Thấp là rẻ so với lợi nhuận mang lại. P/E > 20 là vùng rủi ro định giá quá cao.")
        
        roe_status = "Xuất sắc" if roe >= 0.2 else ("Tốt" if roe >= 0.15 else "Trung bình/Thấp")
        c2.metric("ROE (Hiệu quả)", f"{roe:.1%}", delta=roe_status, delta_color="normal" if roe >= 0.15 else "inverse")
        st.caption("💡 **ROE:** Đo khả năng đẻ ra tiền của vốn chủ. Tiêu chuẩn vàng doanh nghiệp tốt là > 15%.")

    with tab3:
        st.write(f"### 🌊 Smart Flow - Dòng Tiền Cá Mập")
        df_f = lay_du_lieu(final_ticker, days=30)
        if df_f is not None:
            df_f = tinh_toan_chi_bao(df_f); last_f = df_f.iloc[-1]; v_c = last_f['vol_change']
            big = 0.6 if v_c > 1.5 else (0.4 if v_c > 1.1 else 0.2); med = 0.3 if v_c > 1.5 else (0.4 if v_c > 1.1 else 0.3); sma = 1 - big - med
            status_txt = "Gom" if last_f['return_1d'] > 0 else "Xả"; status_col = "normal" if last_f['return_1d'] > 0 else "inverse"
            c1, c2, c3 = st.columns(3)
            c1.metric("🐋 Tiền Lớn (Cá mập)", f"{big*100:.0f}%", delta=status_txt, delta_color=status_col)
            c2.metric("🏦 Tiền Vừa (Tổ chức)", f"{med*100:.0f}%"); c3.metric("🐜 Tiền Nhỏ (Nhỏ lẻ)", f"{sma*100:.0f}%")
            
            with st.expander("📖 GIẢI NGHĨA DÒNG TIỀN SMART FLOW"):
                st.markdown("""
                * **🐋 Tiền Lớn (Cá mập):** Tiền của khối ngoại, tự doanh. Gom (Xanh) là động lực tăng giá mạnh. Xả (Đỏ) là rủi ro sập.
                * **🏦 Tiền Vừa (Tổ chức nội):** Tiền của quỹ nội, đội nhóm chuyên nghiệp. Nhóm duy trì xu hướng.
                * **🐜 Tiền Nhỏ (Nhỏ lẻ):** Nhà đầu tư cá nhân. Tỷ lệ này cao (>50%) chứng tỏ cổ phiếu đang bị 'loãng'.
                """)
            fig_f = go.Figure()
            fig_f.add_trace(go.Bar(x=df_f.tail(20)['date'], y=df_f.tail(20)['money_flow'], marker_color=['green' if r > 0 else 'red' for r in df_f.tail(20)['return_1d']]))
            fig_f.update_layout(height=400, template='plotly_white', title="Dòng tiền 20 phiên gần nhất"); st.plotly_chart(fig_f, use_container_width=True)

    with tab4:
        st.subheader("🔍 Robot Truy Quét Toàn Sàn")
        if st.button("🔥 CHẠY RÀ SOÁT CHUNG (TOP 30 HOSE)"):
            hits = []; bar = st.progress(0); tickers = all_tickers[:30]
            for i, t in enumerate(tickers):
                try:
                    d = lay_du_lieu(t, days=100); d = tinh_toan_chi_bao(d)
                    if d.iloc[-1]['vol_change'] > 1.3:
                        hits.append({'Mã': t, 'Giá': d.iloc[-1]['close'], 'Sức mạnh Vol': round(d.iloc[-1]['vol_change'], 2), 'AI Dự báo': f"{du_bao_ai(d)}%"})
                except: pass
                bar.progress((i+1)/len(tickers))
            if hits: st.table(pd.DataFrame(hits))
            else: st.write("Chưa thấy mã bùng nổ.")
