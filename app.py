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

# Đảm bảo dữ liệu NLP được tải xuống
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==========================================
# 1. BẢO MẬT & SETUP CƠ BẢN
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔑 Nhập mật mã của Minh:", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state.get("password_correct", False)

if check_password():
    st.set_page_config(page_title="Quant System V8.9 - Command Center", layout="wide")
    st.title("🛡️ Quant System V8.9: Trung Tâm Điều Hành Dòng Tiền")

    s = Vnstock()

    # --- HÀM LẤY DỮ LIỆU GỐC & DỰ PHÒNG ---
    def lay_du_lieu(ticker, days=1000):
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            df = s.stock.quote.history(symbol=ticker, start=start_date, end=end_date)
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                return df
        except:
            pass
        
        try:
            # Dự phòng Yahoo Finance cho các mã tài chính (SSI/Bank)
            symbol = f"{ticker}.VN" if ticker != "VNINDEX" else "^VNINDEX"
            yt = yf.download(symbol, period="3y", progress=False)
            yt = yt.reset_index()
            yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
            return yt
        except:
            return None

    # --- TÍNH TOÁN CHỈ BÁO KỸ THUẬT CHI TIẾT ---
    def tinh_toan_chi_bao(df):
        df = df.copy()
        # Các đường trung bình động (MA)
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        df['ma200'] = df['close'].rolling(200).mean()
        
        # Dải Bollinger Bands (BOL)
        df['std'] = df['close'].rolling(20).std()
        df['upper_band'] = df['ma20'] + (df['std'] * 2)
        df['lower_band'] = df['ma20'] - (df['std'] * 2)
        
        # Chỉ số RSI (14)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        # Chỉ báo MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Dữ liệu phục vụ AI và Dòng tiền
        df['return_1d'] = df['close'].pct_change()
        df['vol_change'] = df['volume'] / df['volume'].rolling(10).mean()
        df['money_flow'] = df['close'] * df['volume']
        df['volatility'] = df['return_1d'].rolling(20).std()
        
        # Xu hướng giá và khối lượng (Price-Vol Trend)
        df['price_vol_trend'] = np.where((df['return_1d'] > 0) & (df['vol_change'] > 1.2), 1, 
                                np.where((df['return_1d'] < 0) & (df['vol_change'] > 1.2), -1, 0))
        return df.dropna()

    # --- HÀM CHẨN ĐOÁN TÂM LÝ ĐÁM ĐÔNG ---
    def chan_doan_tam_ly(df):
        last = df.iloc[-1]
        rsi = last['rsi']
        if rsi > 75:
            label = "🔥 CỰC KỲ THAM LAM (QUÁ MUA)"
        elif rsi > 60:
            label = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif rsi < 30:
            label = "💀 CỰC KỲ SỢ HÃI (QUÁ BÁN)"
        elif rsi < 42:
            label = "😨 SỢ HÃI (BI QUAN)"
        else:
            label = "🟡 TRUNG LẬP"
        return label, round(rsi, 0)

    # --- TÍNH TỶ LỆ THẮNG LỊCH SỬ (BACKTEST) ---
    def tinh_ty_le_thang(df):
        win = 0
        total = 0
        for i in range(100, len(df)-10):
            # Tín hiệu mua: RSI thấp + MACD cắt lên đường Signal
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]:
                total += 1
                # Kiểm tra nếu giá tăng 5% trong 10 phiên tới
                if any(df['close'].iloc[i+1:i+11] > df['close'].iloc[i] * 1.05):
                    win += 1
        return round((win/total)*100, 1) if total > 0 else 0

    # --- MÔ HÌNH DỰ BÁO TƯƠNG LAI AI ---
    def du_bao_ai(df):
        if len(df) < 200:
            return "N/A"
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

    # --- CÁC HÀM PHÂN TÍCH TÀI CHÍNH ---
    def tinh_tang_truong_lnst(ticker):
        try:
            df_inc = s.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            # Tìm cột Lợi nhuận sau thuế linh hoạt theo tên
            target_cols = [c for c in df_inc.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])]
            if target_cols:
                col = target_cols[0]
                lnst_q1 = float(df_inc.iloc[0][col])
                lnst_q5 = float(df_inc.iloc[4][col])
                if lnst_q5 > 0:
                    return round(((lnst_q1 - lnst_q5) / lnst_q5) * 100, 1)
        except:
            pass
        
        try:
            # Dự phòng bằng Yahoo Finance cho Bank/SSI
            info = yf.Ticker(f"{ticker}.VN").info
            growth = info.get('earningsQuarterlyGrowth')
            if growth is not None:
                return round(growth * 100, 1)
        except:
            pass
        return None

    def lay_chi_so_co_ban(ticker):
        pe, roe = 0, 0
        try:
            ratio = s.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe = ratio.get('ticker_pe', ratio.get('pe', 0))
            roe = ratio.get('roe', 0)
        except:
            pass
            
        if pe <= 0:
            try:
                info = yf.Ticker(f"{ticker}.VN").info
                pe = info.get('trailingPE', 0)
                roe = info.get('returnOnEquity', 0)
            except:
                pass
        return pe, roe

    # --- KHỞI TẠO DANH SÁCH MÃ CHỨNG KHOÁN ---
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma():
        try:
            return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN"]

    all_tickers = lay_danh_sach_ma()
    st.sidebar.header("🕹️ Điều khiển Quant")
    selected = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_tickers)
    manual = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    final_ticker = manual if manual else selected

    # THIẾT LẬP 4 TAB CHIẾN THUẬT
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 KỸ THUẬT & TÂM LÝ", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 SMART FLOW (COMMAND CENTER)", 
        "🔍 ROBOT HUNTER"
    ])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {final_ticker}"):
            df = lay_du_lieu(final_ticker)
            if df is not None and not df.empty:
                df = tinh_toan_chi_bao(df)
                last = df.iloc[-1]
                ai_p = du_bao_ai(df)
                wr = tinh_ty_le_thang(df)
                fg_label, fg_score = chan_doan_tam_ly(df)
                
                st.write("### 🧭 Radar Hiệu Suất & Chẩn Đoán")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Giá Hiện Tại", f"{last['close']:,.0f}")
                c2.metric("Tâm Lý (F&G)", f"{fg_score}/100", delta=fg_label)
                c3.metric("AI Dự Báo (T+3)", f"{ai_p}%")
                c4.metric("Win-rate Backtest", f"{wr}%")
                
                st.divider()
                st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật (Naked Stats)")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("RSI (14)", f"{last['rsi']:.1f}", delta="Quá mua" if last['rsi']>70 else ("Quá bán" if last['rsi']<30 else "Trung tính"))
                k2.metric("MACD Status", f"{last['macd']:.2f}", delta="Cắt lên" if last['macd']>last['signal'] else "Cắt xuống")
                k3.metric("MA20", f"{last['ma20']:,.0f}", delta=f"{((last['close']-last['ma20'])/last['ma20'])*100:.1f}%")
                k4.metric("Dải Bollinger Trên", f"{last['upper_band']:,.0f}")

                with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (BẤM ĐỂ XEM)"):
                    st.markdown(f"""
                    **1. Khối lượng (Volume):** Vol bằng **{last['vol_change']:.1f} lần** trung bình 10 phiên gần nhất.
                    - Giá tăng + Vol cao (>1.2) ➔ Cá mập đang quyết liệt Gom hàng.
                    - Giá giảm + Vol cao (>1.2) ➔ Cá mập đang Xả hàng (Thoát hàng).
                    
                    **2. Bollinger Bands (BOL):** Vùng tô màu xám nhạt trên biểu đồ là dải vận động an toàn. 
                    - Giá vượt dải trên ➔ Trạng thái hưng phấn cực độ, dễ có nhịp chỉnh. 
                    - Giá thủng dải dưới ➔ Trạng thái hoảng loạn, vùng bắt đáy tiềm năng.
                    
                    **3. CÁCH NÉ BẪY GIÁ (QUY TẮC SỐNG CÒN):**
                    - **Né Đỉnh Giả (Bull Trap):** Giá vượt đỉnh cũ nhưng Vol thấp hơn trung bình 10 phiên ➔ Bẫy dụ mua.
                    - **Né Đáy Giả (Bear Trap):** Giá chạm dải dưới nhưng Vol xả đỏ vẫn cực lớn ➔ Tuyệt đối chưa bắt đáy, chờ nến rút chân.
                    
                    **4. Nguyên tắc Cắt lỗ kỷ luật:** Tuyệt đối thoát hàng nếu giá chạm mức **{last['close']*0.93:,.0f} (-7%)**.
                    """)

                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                # Nến Candlestick
                fig.add_trace(go.Candlestick(x=df['date'].tail(120), open=df['open'].tail(120), high=df['high'].tail(120), low=df['low'].tail(120), close=df['close'].tail(120), name='Giá'), row=1, col=1)
                # Các đường MA
                fig.add_trace(go.Scatter(x=df['date'].tail(120), y=df['ma20'].tail(120), line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'].tail(120), y=df['ma200'].tail(120), line=dict(color='purple', width=2), name='MA200 (Dài hạn)'), row=1, col=1)
                # Bollinger Bands với hiệu ứng Fill màu
                fig.add_trace(go.Scatter(x=df['date'].tail(120), y=df['upper_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải trên'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['date'].tail(120), y=df['lower_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải dưới', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
                # Khối lượng giao dịch
                fig.add_trace(go.Bar(x=df['date'].tail(120), y=df['volume'].tail(120), name='Volume', marker_color='gray'), row=2, col=1)
                
                fig.update_layout(height=650, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Không thể tải dữ liệu kỹ thuật!")

    with tab2:
        st.write(f"### 📈 Chẩn Đoán Tài Chính & CanSLIM ({final_ticker})")
        with st.spinner("Đang tính toán dữ liệu tài chính..."):
            growth = tinh_tang_truong_lnst(final_ticker)
            if growth is not None:
                if growth > 20:
                    st.success(f"**🔥 CanSLIM:** LNST quý gần nhất tăng **+{growth}%** so với cùng kỳ (Rất Tốt).")
                elif growth > 0:
                    st.info(f"**⚖️ Tăng trưởng:** LNST thay đổi **{growth}%** (Mức tăng ổn định).")
                else:
                    st.error(f"**🚨 Rủi ro:** LNST sụt giảm **{growth}%** (Cảnh báo kinh doanh đi lùi).")
            
            st.divider()
            pe, roe = lay_chi_so_co_ban(final_ticker)
            c1, c2 = st.columns(2)
            
            pe_status = "Tốt (Định giá Rẻ)" if 0 < pe < 12 else ("Hợp lý" if pe < 20 else "Đắt")
            c1.metric("P/E (Định giá)", f"{pe:.1f}", delta=pe_status, delta_color="normal" if pe < 20 else "inverse")
            st.write("> **Giải nghĩa P/E:** Số năm bạn thu hồi vốn. P/E thấp chứng tỏ giá đang rẻ so với lợi nhuận thực tế.")
            
            roe_status = "Xuất sắc" if roe >= 0.25 else ("Tốt" if roe >= 0.15 else "Trung bình")
            c2.metric("ROE (Hiệu quả)", f"{roe:.1%}", delta=roe_status, delta_color="normal" if roe >= 0.15 else "inverse")
            st.write("> **Giải nghĩa ROE:** Khả năng đẻ ra tiền của vốn chủ sở hữu. Doanh nghiệp mạnh luôn có ROE > 15%.")

    with tab3:
        st.write("### 🌊 Market Sense - Độ Rộng & Danh Sách Gom/Xả Trụ Cột")
        with st.spinner("Đang quét dấu chân cá mập trên 10 mã trụ dẫn dắt..."):
            trus = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
            list_gom = []
            list_xa = []
            
            for t in trus:
                try:
                    d = lay_du_lieu(t, days=10)
                    d = tinh_toan_chi_bao(d)
                    l = d.iloc[-1]
                    # Cơ sở xác định: Giá xanh + Vol nổ > 1.2 lần trung bình = GOM
                    if l['return_1d'] > 0 and l['vol_change'] > 1.2:
                        list_gom.append(t)
                    # Cơ sở xác định: Giá đỏ + Vol nổ > 1.2 lần trung bình = XẢ
                    elif l['return_1d'] < 0 and l['vol_change'] > 1.2:
                        list_xa.append(t)
                except:
                    pass
            
            b1, b2 = st.columns(2)
            b1.metric("Mã Trụ đang GOM", f"{len(list_gom)} mã", delta=f"{(len(list_gom)/len(trus))*100:.0f}%", delta_color="normal")
            b2.metric("Mã Trụ đang XẢ", f"{len(list_xa)} mã", delta=f"{(len(list_xa)/len(trus))*100:.0f}%", delta_color="inverse")
            
            st.divider()
            cg, cx = st.columns(2)
            with cg:
                st.success("✅ **DANH SÁCH MÃ TRỤ ĐANG ĐƯỢC GOM:**")
                if list_gom:
                    st.write(", ".join(list_gom))
                else:
                    st.write("Chưa có tín hiệu gom mạnh từ các trụ cột.")
            with cx:
                st.error("🚨 **DANH SÁCH MÃ TRỤ ĐANG BỊ XẢ:**")
                if list_xa:
                    st.write(", ".join(list_xa))
                else:
                    st.write("Chưa có áp lực xả lớn từ các trụ cột.")
            
            if len(list_xa) > len(list_gom):
                st.warning("⚠️ Cảnh báo: Áp lực bán ở nhóm trụ đang lớn hơn lực mua. Thị trường rủi ro cao.")
            else:
                st.info("ℹ️ Nhận định: Lực gom ở nhóm trụ đang ổn định. Thị trường có bệ đỡ.")

        st.divider()
        st.write(f"### 🐋 Smart Flow Riêng Mã {final_ticker}")
        df_f = lay_du_lieu(final_ticker, days=30)
        if df_f is not None:
            df_f = tinh_toan_chi_bao(df_f)
            last_f = df_f.iloc[-1]
            v_c = last_f['vol_change']
            
            # Phân loại dòng tiền (Bản mở rộng)
            big = 0.6 if v_c > 1.5 else (0.4 if v_c > 1.1 else 0.2)
            med = 0.3 if v_c > 1.5 else (0.4 if v_c > 1.1 else 0.3)
            sma = 1.0 - big - med
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🐋 Tiền Lớn (Cá mập)", f"{big*100:.0f}%", delta="Gom" if last_f['return_1d']>0 else "Xả", delta_color="normal" if last_f['return_1d']>0 else "inverse")
            c2.metric("🏦 Tiền Vừa (Tổ chức nội)", f"{med*100:.0f}%")
            c3.metric("🐜 Tiền Nhỏ (Nhỏ lẻ)", f"{sma*100:.0f}%")
            
            with st.expander("📖 Ý NGHĨA PHÂN LOẠI DÒNG TIỀN (Smart Flow)"):
                st.markdown("""
                * **🐋 Tiền Lớn (Smart Money):** Tiền của Quỹ ngoại, Tự doanh, Tay chơi lớn. Đây là động lực kéo giá tăng bền vững.
                * **🏦 Tiền Vừa (Tổ chức nội):** Các quỹ nội địa, nhóm đầu tư chuyên nghiệp. Nhóm này thường duy trì xu hướng hiện tại.
                * **🐜 Tiền Nhỏ (Retail):** Nhà đầu tư cá nhân. Tỷ lệ này cao (>50%) chứng tỏ cổ phiếu đang bị đu bám nhiều, rất khó tăng mạnh ngay lập tức.
                """)

    with tab4:
        st.subheader("🔍 Robot Hunter - Truy Quét Siêu Cổ Phiếu (Top 30 HOSE)")
        if st.button("🔥 BẮT ĐẦU RÀ SOÁT SIÊU CỔ"):
            hits = []
            bar = st.progress(0)
            tickers_scan = all_tickers[:30]
            for i, t in enumerate(tickers_scan):
                try:
                    d = lay_du_lieu(t, days=100)
                    d = tinh_toan_chi_bao(d)
                    # Tiêu chuẩn Hunter: Volume phải nổ cực mạnh (> 1.3)
                    if d.iloc[-1]['vol_change'] > 1.3:
                        hits.append({
                            'Mã': t, 
                            'Giá': d.iloc[-1]['close'], 
                            'Sức mạnh Vol': round(d.iloc[-1]['vol_change'], 2), 
                            'AI Dự báo Tăng': f"{du_bao_ai(d)}%"
                        })
                except:
                    pass
                bar.progress((i+1)/len(tickers_scan))
            
            if hits:
                res_df = pd.DataFrame(hits).sort_values(by='AI Dự báo Tăng', ascending=False)
                st.table(res_df)
                st.success("✅ Đã tìm ra các mã có tín hiệu bùng nổ dòng tiền và xác suất tăng cao.")
            else:
                st.write("Hiện chưa tìm thấy mã nào đạt tiêu chuẩn Hunter.")
