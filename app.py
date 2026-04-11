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
    st.set_page_config(page_title="Quant System V7.5 Final", layout="wide")
    st.title("🛡️ Quant System V7.5: Hệ Thống Chiến Thuật Toàn Diện")

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

    # --- TÍNH TOÁN CHỈ BÁO ---
    def tinh_toan_chi_bao(df):
        df = df.copy()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
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
        df['return_1d'] = df['close'].pct_change()
        df['vol_change'] = df['volume'] / df['volume'].rolling(10).mean()
        df['money_flow'] = df['close'] * df['volume']
        df['volatility'] = df['return_1d'].rolling(20).std()
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1.1), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1.1), -1, 0))
        return df.dropna()

    # --- CHẨN ĐOÁN TÂM LÝ ---
    def chan_doan_tam_ly(df):
        last = df.iloc[-1]
        rsi = last['rsi']; vol_c = last['vol_change']; ret = last['return_1d']
        fg_index = rsi
        if fg_index > 75: label = "🔥 CỰC KỲ THAM LAM"; color = "red"
        elif fg_index > 60: label = "⚖️ THAM LAM"; color = "orange"
        elif fg_index > 40: label = "🟡 TRUNG LẬP"; color = "yellow"
        elif fg_index > 25: label = "😨 SỢ HÃI"; color = "blue"
        else: label = "💀 CỰC KỲ SỢ HÃI"; color = "cyan"
        
        if rsi > 70 and vol_c > 1.2 and ret > 0: cycle = "Hưng phấn tột độ - Dễ sập"
        elif rsi < 30 and vol_c > 1.2 and ret < 0: cycle = "Tuyệt vọng - Vùng đáy tiềm năng"
        elif rsi > 50 and ret > 0: cycle = "Niềm tin đang trở lại"
        else: cycle = "Nghi ngờ hoặc Chán nản"
        return label, color, cycle, round(fg_index, 0)

    # --- WIN-RATE BACKTEST ---
    def tinh_ty_le_thang(df):
        win = 0; total = 0
        for i in range(100, len(df)-10):
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i]:
                total += 1
                if any(df['close'].iloc[i+1:i+11] > df['close'].iloc[i] * 1.05): win += 1
        return round((win/total)*100, 1) if total > 0 else 0

    # --- DỰ BÁO AI ---
    def du_bao_ai(df):
        if len(df) < 200: return "N/A"
        df_copy = df.copy(); df_copy['target'] = (df_copy['close'].shift(-3) > df_copy['close'] * 1.02).astype(int)
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data = df_copy.dropna(); X = data[features]; y = data['target']
        model = RandomForestClassifier(n_estimators=100, random_state=42); model.fit(X[:-3], y[:-3])
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    # --- TÀI CHÍNH ---
    def tinh_tang_truong_lnst(ticker):
        try:
            df_inc = s.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            target_cols = [c for c in df_inc.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])]
            if target_cols:
                lnst_q1 = float(df_inc.iloc[0][target_cols[0]]); lnst_q5 = float(df_inc.iloc[4][target_cols[0]])
                if lnst_q5 > 0: return round(((lnst_q1 - lnst_q5) / lnst_q5) * 100, 1)
        except: pass
        try:
            growth = yf.Ticker(f"{ticker}.VN").info.get('earningsQuarterlyGrowth')
            if growth: return round(growth * 100, 1)
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
                df = tinh_toan_chi_bao(df); last = df.iloc[-1]; ai_p = du_bao_ai(df); wr = tinh_ty_le_thang(df)
                fg_label, fg_color, cycle, fg_score = chan_doan_tam_ly(df)
                
                st.write("### 🧠 Trạng Thái Tâm Lý & Hiệu Suất")
                c1, c2, c3 = st.columns(3)
                c1.metric("Fear & Greed Index", f"{fg_score}/100", delta=fg_label)
                c2.metric("Chu Kỳ Cảm Xúc", cycle)
                c3.metric("Win-rate Backtest", f"{wr}%")
                
                st.divider()
                st.write("### 🎯 Dự Báo & Radar")
                m1, m2, m3 = st.columns(3)
                m1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                m2.metric("AI Dự Báo Tăng", f"{ai_p}%")
                m3.success(f"Chốt lời mục tiêu: {last['close']*1.1:,.0f}")
                
                st.write("#### 📡 Radar Phát Hiện Đỉnh/Đáy")
                cp = last['close']; m20 = last['ma20']; up = last['upper_band']; lw = last['lower_band']; rsi = last['rsi']
                if rsi > 65 and cp >= up * 0.98: st.error(f"🚨 CẢNH BÁO ĐỈNH: RSI quá cao. Chỉnh về MA20: -{((cp-m20)/cp)*100:.1f}%")
                elif rsi < 35 and cp <= lw * 1.02: st.success(f"🌟 TÍN HIỆU ĐÁY: RSI quá thấp. Hồi về MA20: +{((m20-cp)/cp)*100:.1f}%")
                else: st.info("⚖️ CÂN BẰNG: Cổ phiếu đang trong vùng tích lũy.")

                with st.expander("📖 CẨM NĂNG GIẢI THÍCH (Bấm để xem)"):
                    st.markdown(f"**Vol:** {last['vol_change']:.1f}x trung bình. **MACD:** {'Tốt' if last['macd']>last['signal'] else 'Xấu'}. **Cắt lỗ:** {cp*0.93:,.0f}")

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df['date'].tail(150), open=df['open'].tail(150), high=df['high'].tail(150), low=df['low'].tail(150), close=df['close'].tail(150), name='Giá'), row=1, col=1)
                fig.add_trace(go.Bar(x=df['date'].tail(150), y=df['volume'].tail(150), name='Khối lượng'), row=2, col=1)
                fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False); st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.write(f"### 📈 Chẩn Đoán Tài Chính ({final_ticker})")
        growth = tinh_tang_truong_lnst(final_ticker)
        if growth is not None:
            if growth > 20: st.success(f"🔥 CanSLIM: LNST tăng **+{growth}%**")
            else: st.warning(f"⚖️ Tăng trưởng: LNST đạt **{growth}%**")
        
        pe, roe = lay_chi_so_co_ban(final_ticker); c1, c2 = st.columns(2)
        p_st = "Rẻ" if 0 < pe < 12 else ("Hợp lý" if pe < 20 else "Đắt")
        c1.metric("P/E (Định giá)", f"{pe:.1f}", delta=p_st, delta_color="normal" if pe < 20 else "inverse")
        st.caption("P/E thấp là rẻ so với lợi nhuận. P/E > 20 là vùng rủi ro.")
        
        r_st = "Xuất sắc" if roe >= 0.2 else ("Tốt" if roe >= 0.15 else "Trung bình")
        c2.metric("ROE (Hiệu quả)", f"{roe:.1%}", delta=r_st, delta_color="normal" if roe >= 0.15 else "inverse")
        st.caption("ROE > 15% là doanh nghiệp làm ăn cực tốt.")

    with tab3:
        st.write(f"### 🌊 Smart Flow - Dòng Tiền Riêng Mã {final_ticker}")
        df_f = lay_du_lieu(final_ticker, days=30)
        if df_f is not None:
            df_f = tinh_toan_chi_bao(df_f); last_f = df_f.iloc[-1]; v_c = last_f['vol_change']
            big = 0.6 if v_c > 1.5 else (0.4 if v_c > 1.1 else 0.2)
            med = 0.3 if v_c > 1.5 else (0.4 if v_c > 1.1 else 0.3); sma = 1 - big - med
            c1, c2, c3 = st.columns(3)
            c1.metric("🐋 Tiền Lớn", f"{big*100:.0f}%", delta="Gom" if last_f['return_1d']>0 else "Xả", delta_color="normal" if last_f['return_1d']>0 else "inverse")
            c2.metric("🏦 Tiền Vừa", f"{med*100:.0f}%"); c3.metric("🐜 Tiền Nhỏ", f"{sma*100:.0f}%")
            
            fig_f = go.Figure()
            fig_f.add_trace(go.Bar(x=df_f.tail(20)['date'], y=df_f.tail(20)['money_flow'], marker_color=['green' if r > 0 else 'red' for r in df_f.tail(20)['return_1d']]))
            fig_f.update_layout(height=400, template='plotly_white', title="Biến động dòng tiền 20 phiên"); st.plotly_chart(fig_f, use_container_width=True)

    with tab4:
        st.subheader("🔍 Robot Truy Quét Mã Tiềm Năng")
        if st.button("🔥 CHẠY RÀ SOÁT"):
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
