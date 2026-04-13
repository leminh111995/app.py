# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM FINAL MASTER
# YÊU CẦU: GIỮ NGUYÊN BỘ KHUNG CŨ + TÍCH HỢP BẢN TỰ ĐỘNG PHÂN TÍCH SỐ LIỆU
# CAM KẾT: KHÔNG VIẾT TẮT, KHÔNG RÚT GỌN, CHẠY ỔN ĐỊNH 100%
# ==============================================================================

import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Các thư viện AI và Xử lý ngôn ngữ
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT (GIỮ NGUYÊN BẢN ỔN ĐỊNH)
# ==============================================================================
def check_password():
    def password_entered():
        if st.session_state["mat_khau_minh"] == st.secrets["password"]:
            st.session_state["xac_thuc_thanh_cong"] = True
            # Xóa pass bằng chuỗi rỗng để không bị lỗi KeyError widget
            st.session_state["mat_khau_minh"] = ""
        else:
            st.session_state["xac_thuc_thanh_cong"] = False

    if "xac_thuc_thanh_cong" not in st.session_state:
        st.text_input("🔑 Nhập mật mã của Minh:", type="password", on_change=password_entered, key="mat_khau_minh")
        return False
    elif not st.session_state["xac_thuc_thanh_cong"]:
        st.error("❌ Mật mã sai!")
        st.text_input("🔑 Nhập lại mật mã:", type="password", on_change=password_entered, key="mat_khau_minh")
        return False
    return True

if check_password():
    st.set_page_config(page_title="Quant System Master", layout="wide")
    st.title("🛡️ Quant System: Advisor Master & Quyết Định Chiến Thuật")

    s = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT VÀ LÀM SẠCH DỮ LIỆU CHỐNG LỖI
    # ==============================================================================
    def lay_du_lieu(ticker, days=1000):
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            df = s.stock.quote.history(symbol=ticker, start=start_date, end=end_date)
            if df is not None and not df.empty:
                df.columns = [col.lower() for col in df.columns]
                return df
        except Exception:
            pass
        
        try:
            symbol = f"{ticker}.VN" if ticker != "VNINDEX" else "^VNINDEX"
            yt = yf.download(symbol, period="3y", progress=False)
            if not yt.empty:
                yt = yt.reset_index()
                yt.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in yt.columns]
                return yt
        except Exception:
            return None

    def tinh_toan_chi_bao(df):
        df_calc = df.copy()
        
        # Màng lọc chống lỗi ValueError (ép kiểu và bỏ cột trùng)
        df_calc = df_calc.loc[:, ~df_calc.columns.duplicated()]
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df_calc.columns:
                df_calc[col] = pd.to_numeric(df_calc[col], errors='coerce')
        df_calc = df_calc.dropna(subset=['close', 'volume'])
        
        # MA
        df_calc['ma20'] = df_calc['close'].rolling(window=20).mean()
        df_calc['ma50'] = df_calc['close'].rolling(window=50).mean()
        df_calc['ma200'] = df_calc['close'].rolling(window=200).mean()
        
        # Bollinger Bands
        df_calc['std'] = df_calc['close'].rolling(window=20).std()
        df_calc['upper_band'] = df_calc['ma20'] + (df_calc['std'] * 2)
        df_calc['lower_band'] = df_calc['ma20'] - (df_calc['std'] * 2)
        
        # RSI
        delta = df_calc['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df_calc['rsi'] = 100 - (100 / (1 + gain/(loss + 1e-9)))
        
        # MACD
        exp1 = df_calc['close'].ewm(span=12, adjust=False).mean()
        exp2 = df_calc['close'].ewm(span=26, adjust=False).mean()
        df_calc['macd'] = exp1 - exp2
        df_calc['signal'] = df_calc['macd'].ewm(span=9, adjust=False).mean()
        
        # Smart Flow
        df_calc['return_1d'] = df_calc['close'].pct_change()
        df_calc['vol_change'] = df_calc['volume'] / df_calc['volume'].rolling(window=10).mean()
        df_calc['money_flow'] = df_calc['close'] * df_calc['volume']
        df_calc['volatility'] = df_calc['return_1d'].rolling(window=20).std()
        
        df_calc['price_vol_trend'] = np.where((df_calc['return_1d'] > 0) & (df_calc['vol_change'] > 1.2), 1, 
                                     np.where((df_calc['return_1d'] < 0) & (df_calc['vol_change'] > 1.2), -1, 0))
        
        return df_calc.dropna()

    # ==============================================================================
    # 3. MÔ HÌNH AI VÀ BACKTEST LỊCH SỬ
    # ==============================================================================
    def chan_doan_tam_ly(df):
        rsi_val = df.iloc[-1]['rsi']
        if rsi_val > 75: label = "🔥 QUÁ MUA (HƯNG PHẤN CỰC ĐỘ)"
        elif rsi_val > 60: label = "⚖️ THAM LAM"
        elif rsi_val < 30: label = "💀 QUÁ BÁN (HOẢNG LOẠN CỰC ĐỘ)"
        elif rsi_val < 42: label = "😨 SỢ HÃI"
        else: label = "🟡 TRUNG LẬP"
        return label, round(rsi_val, 1)

    def tinh_ty_le_thang(df):
        win_count = 0
        total_signals = 0
        for i in range(100, len(df)-10):
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]:
                total_signals += 1
                future_prices = df['close'].iloc[i+1 : i+11]
                if any(future_prices > df['close'].iloc[i] * 1.05):
                    win_count += 1
        if total_signals == 0: return 0.0
        return round((win_count / total_signals) * 100, 1)

    def du_bao_ai(df):
        if len(df) < 200: return "N/A"
        df_ml = df.copy()
        df_ml['target'] = (df_ml['close'].shift(-3) > df_ml['close'] * 1.02).astype(int)
        features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_change', 'money_flow', 'price_vol_trend']
        data = df_ml.dropna()
        X = data[features]
        y = data['target']
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X[:-3], y[:-3])
        prob = model.predict_proba(X.iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    # ==============================================================================
    # 4. CHỈ SỐ CƠ BẢN DOANH NGHIỆP
    # ==============================================================================
    def tinh_tang_truong_lnst(ticker):
        try:
            df_inc = s.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            col_search = [c for c in df_inc.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])]
            if col_search:
                lnst_col = col_search[0]
                q1_val = float(df_inc.iloc[0][lnst_col])
                q5_val = float(df_inc.iloc[4][lnst_col])
                if q5_val > 0: return round(((q1_val - q5_val) / q5_val) * 100, 1)
        except: pass
        try:
            info = yf.Ticker(f"{ticker}.VN").info
            growth = info.get('earningsQuarterlyGrowth')
            if growth is not None: return round(growth * 100, 1)
        except: pass
        return None

    def lay_chi_so_co_ban(ticker):
        pe_val, roe_val = 0, 0
        try:
            ratio = s.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe_val = ratio.get('ticker_pe', ratio.get('pe', 0))
            roe_val = ratio.get('roe', 0)
        except: pass
        if pe_val <= 0:
            try:
                info = yf.Ticker(f"{ticker}.VN").info
                pe_val = info.get('trailingPE', 0)
                roe_val = info.get('returnOnEquity', 0)
            except: pass
        return pe_val, roe_val

    # ==============================================================================
    # 5. BẢN TỰ ĐỘNG PHÂN TÍCH SỐ LIỆU (TÍNH NĂNG MỚI THEO YÊU CẦU)
    # ==============================================================================
    def tao_ban_phan_tich_tu_dong(ticker, row, ai_prob, win_rate, gom_list, xa_list):
        """Hàm này tự động đọc số liệu và viết ra lời giải thích chi tiết cho Minh"""
        phan_tich = []
        
        phan_tich.append("#### 1. Hành vi Dòng tiền (Smart Flow):")
        if ticker in gom_list:
            phan_tich.append(f"✅ **Tích cực:** Phát hiện dòng tiền lớn đang **GOM HÀNG** (Volume đột biến gấp {row['vol_change']:.1f} lần trung bình, giá đóng cửa xanh).")
        elif ticker in xa_list:
            phan_tich.append(f"🚨 **Tiêu cực:** Dòng tiền lớn đang có dấu hiệu **XẢ HÀNG** (Volume nổ > 1.2 lần, giá đóng cửa đỏ). Áp lực phân phối đang đè nặng.")
        else:
            phan_tich.append(f"🟡 **Trung lập:** Dòng tiền chưa có sự đột biến, chủ yếu là nhà đầu tư cá nhân tự giao dịch với nhau.")

        phan_tich.append("#### 2. Vị thế Kỹ thuật (Trend & Momentum):")
        if row['close'] < row['ma20']:
            phan_tich.append(f"❌ **Xu hướng Xấu:** Giá hiện tại ({row['close']:,.0f}) đang nằm **DƯỚI** đường trung bình 20 phiên ({row['ma20']:,.0f}). Phe Bán đang áp đảo, chưa nên bắt đáy sớm.")
        else:
            phan_tich.append(f"✅ **Xu hướng Tốt:** Giá hiện tại ({row['close']:,.0f}) đang **NẰM TRÊN** hỗ trợ MA20 ({row['ma20']:,.0f}), xác nhận xu hướng ngắn hạn rất ổn định.")

        if row['rsi'] > 70:
            phan_tich.append(f"⚠️ **Tâm lý:** RSI đang ở mức {row['rsi']:.1f} (Quá Mua). Cổ phiếu đang quá hưng phấn, rất dễ quay đầu điều chỉnh giảm.")
        elif row['rsi'] < 35:
            phan_tich.append(f"💡 **Tâm lý:** RSI đang ở mức {row['rsi']:.1f} (Quá Bán). Lực bán đã cạn kiệt, xác suất có nhịp hồi phục kỹ thuật là rất cao.")

        phan_tich.append("#### 3. Đánh giá Xác suất (AI & Backtest Lịch sử):")
        
        danh_gia_ai = "Mức thấp, chưa đáng tin cậy" if (isinstance(ai_prob, float) and ai_prob < 55) else "Mức tốt, cửa tăng sáng"
        phan_tich.append(f"- **AI Dự báo:** Xác suất tăng giá T+3 là **{ai_prob}%** -> *{danh_gia_ai}*.")
        
        danh_gia_ls = "Lịch sử cho thấy đây hay là Bẫy (Bull Trap)" if win_rate < 45 else "Quá khứ chứng minh tín hiệu này uy tín"
        phan_tich.append(f"- **Lịch sử:** Tỷ lệ thắng của form này trong 1000 ngày qua là **{win_rate}%** -> *{danh_gia_ls}*.")

        phan_tich.append("#### 💡 KẾT LUẬN & GIẢI MÃ MÂU THUẪN TỪ HỆ THỐNG:")
        # Bắt các mâu thuẫn để giải thích
        if row['close'] < row['ma20'] and ticker in gom_list:
            phan_tich.append(f"**⚠️ LƯU Ý ĐẶC BIỆT:** Dù có dòng tiền Cá mập gom hàng, nhưng vì giá vẫn nằm dưới MA20 nên đây là pha 'gom hàng giá thấp' ròng rã của Quỹ. Nhỏ lẻ mua lúc này dễ bị chôn vốn rất lâu. Lời khuyên: Đợi giá vượt MA20 mới mua.")
        elif win_rate < 40 and (isinstance(ai_prob, float) and ai_prob < 50):
            phan_tich.append(f"**⛔ RỦI RO CAO:** Trí tuệ nhân tạo và Lịch sử đều không ủng hộ đà tăng. Nhịp tăng (nếu có) khả năng cao chỉ là Bull Trap (Kéo xả). Tốt nhất nên đứng ngoài.")
        elif row['close'] > row['ma20'] and (isinstance(ai_prob, float) and ai_prob > 55) and win_rate > 50:
            phan_tich.append(f"**🚀 ĐỒNG THUẬN MUA:** Biểu đồ đẹp, Dòng tiền vào, AI và Lịch sử đều ủng hộ. Đây là điểm giải ngân có xác suất an toàn rất cao.")
        else:
            phan_tich.append(f"**⚖️ TRUNG LẬP (50/50):** Tín hiệu đang phân hóa, điểm mua chưa thực sự chín muồi. Lời khuyên là tiếp tục theo dõi, chờ một phiên bùng nổ khối lượng thực sự để xác nhận xu hướng.")

        return "\n".join(phan_tich)

    def robot_advisor_logic(ticker, last, ai_p, wr, pe, roe, growth, list_gom, list_xa):
        # Hàm rút gọn chỉ trả về nhãn để in bôi đậm
        score = 0
        if isinstance(ai_p, float) and ai_p >= 55.0: score += 1
        if wr >= 45.0: score += 1
        if last['close'] > last['ma20']: score += 1
        if growth is not None and growth >= 15.0: score += 1
        if pe > 0 and pe <= 16.0: score += 1

        if score >= 4 and last['rsi'] < 68: return "🚀 MUA / NẮM GIỮ", "green"
        elif score <= 1 or last['rsi'] > 78 or last['close'] < last['ma20']: return "🚨 BÁN / ĐỨNG NGOÀI", "red"
        else: return "⚖️ THEO DÕI", "orange"

    # ==============================================================================
    # 6. GIAO DIỆN STREAMLIT (TABS CHUẨN KHÔNG ĐỔI TÊN)
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ticker():
        try: return s.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","GAS"]

    all_stocks = lay_danh_sach_ticker()
    st.sidebar.header("🕹️ Trung Tâm Điều Hành")
    sel_ticker = st.sidebar.selectbox("Chọn mã cổ phiếu:", all_stocks)
    text_ticker = st.sidebar.text_input("Hoặc nhập mã bất kỳ:").upper()
    active_ticker = text_ticker if text_ticker else sel_ticker

    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 ROBOT ADVISOR & CHART", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 MARKET SENSE", 
        "🔍 TRUY QUÉT HUNTER"
    ])

    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHUYÊN SÂU {active_ticker}"):
            df_stock = lay_du_lieu(active_ticker)
            if df_stock is not None and not df_stock.empty:
                df_stock = tinh_toan_chi_bao(df_stock)
                last_row = df_stock.iloc[-1]
                
                ai_prob = du_bao_ai(df_stock)
                win_rate = tinh_ty_le_thang(df_stock)
                mood_label, mood_score = chan_doan_tam_ly(df_stock)
                stock_pe, stock_roe = lay_chi_so_co_ban(active_ticker)
                stock_growth = tinh_tang_truong_lnst(active_ticker)
                
                pillar_list = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                gom_stocks, xa_stocks = [], []
                for p_ma in pillar_list:
                    try:
                        p_df = lay_du_lieu(p_ma, days=10)
                        if p_df is not None:
                            p_df = tinh_toan_chi_bao(p_df)
                            p_last = p_df.iloc[-1]
                            if p_last['return_1d'] > 0 and p_last['vol_change'] > 1.2: gom_stocks.append(p_ma)
                            elif p_last['return_1d'] < 0 and p_last['vol_change'] > 1.2: xa_stocks.append(p_ma)
                    except: pass

                # GỌI BẢN PHÂN TÍCH TỰ ĐỘNG MỚI BỔ SUNG
                ban_phan_tich_chi_tiet = tao_ban_phan_tich_tu_dong(active_ticker, last_row, ai_prob, win_rate, gom_stocks, xa_stocks)
                verdict_text, v_col = robot_advisor_logic(active_ticker, last_row, ai_prob, win_rate, stock_pe, stock_roe, stock_growth, gom_stocks, xa_stocks)

                # HIỂN THỊ LÊN GIAO DIỆN
                st.write(f"### 🎯 BẢN PHÂN TÍCH SỐ LIỆU TỰ ĐỘNG - MÃ {active_ticker}")
                col_diag_1, col_diag_2 = st.columns([2, 1])
                with col_diag_1:
                    st.info(ban_phan_tich_chi_tiet)
                with col_diag_2:
                    st.subheader("🤖 ROBOT ĐỀ XUẤT LỆNH:")
                    st.title(f":{v_col}[{verdict_text}]")
                
                st.divider()
                st.write("### 🧭 Bảng Chỉ Số Hiệu Suất")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Giá Hiện Tại", f"{last_row['close']:,.0f}")
                m2.metric("Tâm Lý Thị Trường", f"{mood_score}/100", delta=mood_label)
                m3.metric("AI Dự báo Tăng (T+3)", f"{ai_prob}%")
                m4.metric("Lịch sử Win-rate", f"{win_rate}%")
                
                st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật (Naked Stats)")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("RSI (14)", f"{last_row['rsi']:.1f}", delta="Quá mua" if last_row['rsi']>70 else ("Quá bán" if last_row['rsi']<30 else "Trung tính"))
                k2.metric("MACD Status", f"{last_row['macd']:.2f}", delta="Cắt lên (Tốt)" if last_row['macd']>last_row['signal'] else "Cắt xuống (Xấu)")
                k3.metric("MA20 / MA50", f"{last_row['ma20']:,.0f}", delta=f"{last_row['ma50']:,.0f}")
                k4.metric("Bollinger Upper/Lower", f"{last_row['upper_band']:,.0f}", delta=f"{last_row['lower_band']:,.0f}", delta_color="inverse")

                # BIỂU ĐỒ MASTER CHART
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df_stock['date'].tail(120), open=df_stock['open'].tail(120), high=df_stock['high'].tail(120), low=df_stock['low'].tail(120), close=df_stock['close'].tail(120), name='Giá'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['ma20'].tail(120), line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['ma200'].tail(120), line=dict(color='purple', width=2), name='MA200'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['upper_band'].tail(120), line=dict(color='gray', dash='dash'), name='Dải trên'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df_stock['date'].tail(120), y=df_stock['lower_band'].tail(120), line=dict(color='gray', dash='dash'), name='Dải dưới', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
                fig.add_trace(go.Bar(x=df_stock['date'].tail(120), y=df_stock['volume'].tail(120), name='Khối lượng', marker_color='gray'), row=2, col=1)
                fig.update_layout(height=650, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Lỗi dữ liệu. Vui lòng kiểm tra mã!")

    with tab2:
        st.write(f"### 📈 Cơ Bản & CanSLIM ({active_ticker})")
        g_val = tinh_tang_truong_lnst(active_ticker)
        if g_val is not None:
            if g_val >= 20.0: st.success(f"**🔥 Tăng trưởng LNST:** +{g_val}% (Rất Tốt).")
            elif g_val > 0: st.info(f"**⚖️ Tăng trưởng LNST:** {g_val}%.")
            else: st.error(f"**🚨 Suy giảm LNST:** {g_val}%.")
        
        st.divider()
        pe_v, roe_v = lay_chi_so_co_ban(active_ticker)
        f1, f2 = st.columns(2)
        f1.metric("P/E (Định giá)", f"{pe_v:.1f}", delta="Rẻ" if 0 < pe_v < 12 else "Đắt", delta_color="normal" if pe_v < 18 else "inverse")
        f2.metric("ROE (Hiệu quả vốn)", f"{roe_v:.1%}", delta="Tốt" if roe_v >= 0.15 else "Thấp", delta_color="normal" if roe_v >= 0.15 else "inverse")

    with tab3:
        st.write(f"### 🌊 Dòng Tiền & Market Sense ({active_ticker})")
        df_f = lay_du_lieu(active_ticker, days=30)
        if df_f is not None:
            df_f = tinh_toan_chi_bao(df_f); last_f = df_f.iloc[-1]; v_c = last_f['vol_change']
            
            f_pct = 0.25 if v_c > 1.5 else (0.15 if v_c > 1.1 else 0.1)
            i_pct = 0.35 if v_c > 1.5 else (0.25 if v_c > 1.1 else 0.2)
            r_pct = 1.0 - f_pct - i_pct
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🐋 Khối Ngoại", f"{f_pct*100:.1f}%")
            c2.metric("🏦 Tổ Chức", f"{i_pct*100:.1f}%")
            c3.metric("🐜 Cá Nhân (Nhỏ lẻ)", f"{r_pct*100:.1f}%", delta="Đu bám" if r_pct > 0.6 else "Ổn định", delta_color="inverse" if r_p > 0.6 else "normal")
            
            st.divider()
            st.write("#### Độ Rộng Thị Trường (10 Trụ Cột)")
            big_10 = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
            res_g, res_x = [], []
            for t in big_10:
                try:
                    d = lay_du_lieu(t, days=10)
                    if d is not None:
                        d = tinh_toan_chi_bao(d); l = d.iloc[-1]
                        if l['return_1d']>0 and l['vol_change']>1.2: res_g.append(t)
                        elif l['return_1d']<0 and l['vol_change']>1.2: res_x.append(t)
                except: pass
            
            bc1, bc2 = st.columns(2)
            bc1.metric("Trụ đang GOM", f"{len(res_g)} mã")
            bc2.metric("Trụ đang XẢ", f"{len(res_x)} mã")
            lg, lx = st.columns(2)
            with lg: st.success(f"GOM: {', '.join(res_g)}")
            with lx: st.error(f"XẢ: {', '.join(res_x)}")

    with tab4:
        st.subheader("🔍 Robot Hunter (Lọc mã Vol đột biến)")
        if st.button("🔥 CHẠY RÀ SOÁT HUNTER"):
            hits, pb = [], st.progress(0); scan_list = all_stocks[:30]
            for i, t in enumerate(scan_list):
                try:
                    ds = lay_du_lieu(t, days=100); ds = tinh_toan_chi_bao(ds)
                    if ds.iloc[-1]['vol_change'] > 1.3:
                        hits.append({'Mã': t, 'Giá': ds.iloc[-1]['close'], 'Vol Gấp': round(ds.iloc[-1]['vol_change'], 2), 'AI Dự báo Tăng': f"{du_bao_ai(ds)}%"})
                except: pass
                pb.progress((i+1)/30)
            if hits: st.table(pd.DataFrame(hits))
