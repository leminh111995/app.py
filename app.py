# ==============================================================================
# QUANT SYSTEM V20.0 - THE PREDATOR LEVIATHAN (BẢN HỢP NHẤT DUY NHẤT 1 LẦN)
# ==============================================================================
import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
import nltk

# --- CẤU HÌNH THAM SỐ CHIẾN THUẬT PREDATOR ---
THAM_SO_AI_PREDATOR = 48.0
THAM_SO_RSI_AN_TOAN = 62.0
THAM_SO_VUNG_GIA_MA20 = 0.05
THAM_SO_VOL_MIN = 0.6
THAM_SO_VOL_MAX = 1.4
THAM_SO_SQUEEZE = 1.2
THAM_SO_CAN_CUNG = 0.8

try: nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError: nltk.download('vader_lexicon')

def lay_thoi_gian_vn():
    return datetime.utcnow() + timedelta(hours=7)

def xac_thuc_bao_mat():
    if st.session_state.get("auth_predator", False): return True
    st.markdown("### 🔐 Quant System V20.0 - Cổng Bảo Mật Predator")
    pw = st.text_input("🔑 Nhập mật mã truy cập:", type="password")
    if pw:
        if pw == st.secrets["password"]:
            st.session_state["auth_predator"] = True
            st.rerun()
        else: st.error("❌ Mật mã không hợp lệ.")
    return False

if xac_thuc_bao_mat():
    st.set_page_config(page_title="Quant System V20.0 Predator", layout="wide")
    st.title("🛡️ Quant System V20.0: The Predator Advisor")
    st.markdown("---")
    dong_co_vnstock = Vnstock()

    # ==============================================================================
    # 1. MODULE TRUY XUẤT DỮ LIỆU
    # ==============================================================================
    def lay_du_lieu_gia_niem_yet(ma_ck, days=1000):
        end_date = lay_thoi_gian_vn().strftime('%Y-%m-%d')
        start_date = (lay_thoi_gian_vn() - timedelta(days=days)).strftime('%Y-%m-%d')
        try:
            df = dong_co_vnstock.stock.quote.history(symbol=ma_ck, start=start_date, end=end_date)
            if df is not None and not df.empty:
                df.columns = [str(c).lower() for c in df.columns]
                return df
        except: pass
        try:
            yf_ma = "^VNINDEX" if ma_ck == "VNINDEX" else f"{ma_ck}.VN"
            df_yf = yf.download(yf_ma, period="3y", progress=False).reset_index()
            if not df_yf.empty:
                df_yf.columns = [str(c[0] if isinstance(c, tuple) else c).lower() for c in df_yf.columns]
                return df_yf
        except: return None

    def lay_du_lieu_dong_tien_to_chuc(ma_ck, days=20):
        end_date = lay_thoi_gian_vn().strftime('%Y-%m-%d')
        start_date = (lay_thoi_gian_vn() - timedelta(days=days)).strftime('%Y-%m-%d')
        df_f, df_p = None, None
        try: df_f = dong_co_vnstock.stock.trade.foreign_trade(symbol=ma_ck, start=start_date, end=end_date)
        except:
            try: df_f = dong_co_vnstock.stock.trading.foreign(symbol=ma_ck, start=start_date, end=end_date)
            except: pass
        try: df_p = dong_co_vnstock.stock.trade.proprietary_trade(symbol=ma_ck, start=start_date, end=end_date)
        except: pass
        if df_f is not None and not df_f.empty: df_f.columns = [str(c).lower() for c in df_f.columns]
        if df_p is not None and not df_p.empty: df_p.columns = [str(c).lower() for c in df_p.columns]
        return df_f, df_p

    # ==============================================================================
    # 2. MODULE CHỈ BÁO QUANT ENGINE
    # ==============================================================================
    def tinh_toan_chi_bao_predator(df_raw):
        df = df_raw.copy().loc[:, ~df_raw.columns.duplicated()]
        for c in ['open', 'high', 'low', 'close', 'volume']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.ffill().dropna()

        close = df['close']
        df['ma20'] = close.rolling(20).mean()
        df['ma50'] = close.rolling(50).mean()
        df['ma200'] = close.rolling(200).mean()
        
        std20 = close.rolling(20).std()
        df['upper_band'] = df['ma20'] + (std20 * 2)
        df['lower_band'] = df['ma20'] - (std20 * 2)
        df['bb_width'] = (df['upper_band'] - df['lower_band']) / (df['ma20'] + 1e-9)

        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

        df['macd'] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        vol20 = df['volume'].rolling(20).mean()
        df['can_cung'] = (df['close'] < df['open']) & (df['volume'] < vol20 * THAM_SO_CAN_CUNG)
        
        df['return_1d'] = close.pct_change()
        df['vol_strength'] = df['volume'] / (df['volume'].rolling(10).mean() + 1e-9)
        df['pv_trend'] = np.where((df['return_1d'] > 0) & (df['vol_strength'] > 1.2), 1, np.where((df['return_1d'] < 0) & (df['vol_strength'] > 1.2), -1, 0))
        return df.dropna()

    # ==============================================================================
    # 3. MODULE DỰ BÁO VÀ TÀI CHÍNH
    # ==============================================================================
    def du_bao_ai_t3(df):
        if len(df) < 200: return "N/A"
        d = df.copy()
        d['target'] = (d['close'].shift(-3) > d['close'] * 1.02).astype(int)
        feats = ['rsi', 'macd', 'signal', 'return_1d', 'vol_strength', 'bb_width', 'pv_trend']
        d = d.dropna()
        X, y = d[feats][:-3], d['target'][:-3]
        model = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y)
        return round(model.predict_proba(d[feats].iloc[[-1]])[0][1] * 100, 1)

    def thuc_thi_backtest(df):
        n_sig = 0; n_win = 0
        for i in range(100, len(df) - 10):
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]:
                n_sig += 1
                if any(df['close'].iloc[i+1:i+11] > df['close'].iloc[i] * 1.05): n_win += 1
        return round((n_win / n_sig) * 100, 1) if n_sig > 0 else 0.0

    def boc_tach_pe_roe(ma_ck):
        pe, roe = None, None
        try:
            r = dong_co_vnstock.stock.finance.ratio(ma_ck, 'quarterly').iloc[-1]
            pe_v = r.get('ticker_pe', r.get('pe', None))
            roe_v = r.get('roe', None)
            if pe_v and pe_v > 0: pe = pe_v
            if roe_v and roe_v > 0: roe = roe_v
        except: pass
        if pe is None:
            try:
                info = yf.Ticker(f"{ma_ck}.VN").info
                pe = info.get('trailingPE', None); roe = info.get('returnOnEquity', None)
            except: pass
        return pe, roe

    def tao_bao_cao_dictionary(tui):
        ma = tui['ma_ck']; last = tui['dong_cuoi']
        txt = [f"#### 🎯 PHÂN TÍCH CHIẾN THUẬT MÃ: {ma}"]
        if tui['to_chuc_gom']: txt.append(f"✅ **Dòng tiền lớn:** Phát hiện Tây/Tự doanh đang GOM HÀNG mã {ma}.")
        else: txt.append(f"🟡 **Dòng tiền lớn:** Chưa có dấu hiệu tổ chức gom rõ rệt.")
        
        if last['close'] > last['ma20']: txt.append(f"✅ **Xu hướng:** Giá ({last['close']:,.0f}) neo vững trên nền MA20.")
        else: txt.append(f"❌ **Cảnh báo:** Giá rớt dưới MA20. Xu hướng ngắn hạn nguy hiểm.")

        if last['bb_width'] <= tui['min_bbw'] * THAM_SO_SQUEEZE: txt.append(f"🌀 **Tín hiệu nén:** Lò xo Bollinger đang siết cực chặt.")
        if last['can_cung']: txt.append(f"💧 **Tín hiệu cạn cung:** Lực bán đã kiệt quệ, khối lượng cạn kiệt.")

        txt.append(f"#### 🛡️ QUẢN TRỊ RỦI RO CHO MINH:")
        txt.append(f"- **Vùng mua an toàn:** Quanh {last['ma20']:,.0f} VNĐ.")
        txt.append(f"- **Ngưỡng Stop-loss:** {last['ma20'] * 0.98:,.0f} VNĐ (Gãy nền).")
        return "\n\n".join(txt)

    # ==============================================================================
    # 4. GIAO DIỆN NGƯỜI DÙNG & RADAR PREDATOR
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def lay_danh_sach_hose():
        try:
            ls = dong_co_vnstock.market.listing()
            return ls[ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT", "HPG", "SSI", "VCB", "VNM", "TCB", "MWG", "VIC", "VHM", "GAS"]

    ds_ma = lay_danh_sach_hose()
    st.sidebar.header("🕹️ Điều Hành Predator")
    ma_drop = st.sidebar.selectbox("Chọn mã cổ phiếu:", ds_ma)
    ma_tay = st.sidebar.text_input("Hoặc nhập tay (VD: HSG):").upper()
    ma_co_phieu_dang_duoc_chon = ma_tay if ma_tay else ma_drop

    t1, t2, t3, t4 = st.tabs(["🤖 ADVISOR", "🏢 TÀI CHÍNH", "🌊 DÒNG TIỀN", "🔍 RADAR CHÂN SÓNG"])

    with t1:
        if st.button(f"⚡ PHÂN TÍCH MÃ {ma_co_phieu_dang_duoc_chon}"):
            with st.spinner("Đang rà soát đa tầng..."):
                df = lay_du_lieu_gia_niem_yet(ma_co_phieu_dang_duoc_chon)
                if df is not None:
                    df_q = tinh_toan_chi_bao_predator(df)
                    last = df_q.iloc[-1]; ai_p = du_bao_ai_t3(df_q); wr_p = thuc_thi_backtest(df_q)
                    
                    df_f, df_p = lay_du_lieu_dong_tien_to_chuc(ma_co_phieu_dang_duoc_chon, 10)
                    smart_buy = False
                    if df_f is not None and (df_f['buyval'].tail(5).sum() - df_f['sellval'].tail(5).sum()) > 0: smart_buy = True
                    if not smart_buy and df_p is not None and (df_p['buyval'].tail(5).sum() - df_p['sellval'].tail(5).sum()) > 0: smart_buy = True

                    tui_data = {'ma_ck': ma_co_phieu_dang_duoc_chon, 'dong_cuoi': last, 'diem_ai': ai_p, 'to_chuc_gom': smart_buy, 'min_bbw': df_q['bb_width'].tail(20).min()}
                    
                    c1, c2 = st.columns([2, 1])
                    with c1: st.info(tao_bao_cao_dictionary(tui_data))
                    with c2:
                        st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                        is_buy = isinstance(ai_p, float) and ai_p > THAM_SO_AI_PREDATOR and last['close'] > last['ma20']
                        st.title(f":{'green' if is_buy else 'orange'}[{'🚀 MUA / NẮM GIỮ' if is_buy else '⚖️ QUAN SÁT'}]")
                    
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                    v = df_q.tail(120)
                    fig.add_trace(go.Candlestick(x=v['date'], open=v['open'], high=v['high'], low=v['low'], close=v['close'], name='Nến'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=v['date'], y=v['ma20'], line=dict(color='orange'), name='MA20'), row=1, col=1)
                    fig.add_trace(go.Bar(x=v['date'], y=v['volume'], marker_color='gray', name='Vol'), row=2, col=1)
                    fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
                else: st.error("❌ Lỗi tải dữ liệu.")

    with t2:
        st.write(f"### 📈 Tài Chính {ma_co_phieu_dang_duoc_chon}")
        pe, roe = boc_tach_pe_roe(ma_co_phieu_dang_duoc_chon)
        c1, c2 = st.columns(2)
        c1.metric("P/E", f"{pe:.1f}" if pe else "N/A", delta="API Lỗi" if not pe else None, delta_color="off" if not pe else "normal")
        c2.metric("ROE (%)", f"{roe:.1%}" if roe else "N/A", delta="API Lỗi" if not roe else None, delta_color="off" if not roe else "normal")

    with t3:
        st.write(f"### 🌊 Dòng Tiền Tổ Chức (10 Phiên) - {ma_co_phieu_dang_duoc_chon}")
        df_f, df_p = lay_du_lieu_dong_tien_to_chuc(ma_co_phieu_dang_duoc_chon, 20)
        c1, c2 = st.columns(2)
        if df_f is not None and not df_f.empty:
            rong_f = (df_f['buyval'].iloc[-1] - df_f['sellval'].iloc[-1]) / 1e9
            c1.metric("Khối Ngoại (Hôm nay)", f"{rong_f:.2f} Tỷ", delta="Mua" if rong_f > 0 else "Bán", delta_color="normal" if rong_f > 0 else "inverse")
        if df_p is not None and not df_p.empty:
            rong_p = (df_p['buyval'].iloc[-1] - df_p['sellval'].iloc[-1]) / 1e9
            c2.metric("Tự Doanh (Hôm nay)", f"{rong_p:.2f} Tỷ", delta="Mua" if rong_p > 0 else "Bán", delta_color="normal" if rong_p > 0 else "inverse")

    with t4:
        st.subheader("🔍 Radar Predator - Săn Chân Sóng (5% MA20)")
        if st.button("🔥 KÍCH HOẠT QUÉT 2 TẦNG"):
            bung_no = []; danh_sach_cho = []
            bar = st.progress(0); lst = ds_ma[:30]
            for i, ma in enumerate(lst):
                try:
                    df = lay_du_lieu_gia_niem_yet(ma, 120)
                    if df is not None:
                        df_q = tinh_toan_chi_bao_predator(df); last = df_q.iloc[-1]; ai_p = du_bao_ai_t3(df_q)
                        
                        if last['vol_strength'] > 1.3:
                            bung_no.append({'Mã': ma, 'AI': f"{ai_p}%", 'Vol': round(last['vol_strength'], 1)})
                        
                        # Điều kiện cơ bản 5% MA20
                        base = (last['rsi'] < THAM_SO_RSI_AN_TOAN) and \
                               (abs(last['close'] - last['ma20']) / last['ma20'] <= THAM_SO_VUNG_GIA_MA20) and \
                               (THAM_SO_VOL_MIN <= last['vol_strength'] <= THAM_SO_VOL_MAX) and \
                               (isinstance(ai_p, float) and ai_p >= THAM_SO_AI_PREDATOR)
                        
                        if base:
                            sqz = last['bb_width'] <= df_q['bb_width'].tail(20).min() * THAM_SO_SQUEEZE
                            can = df_q['can_cung'].tail(5).any()
                            
                            df_f, df_p = lay_du_lieu_dong_tien_to_chuc(ma, 10)
                            smart = False
                            if df_f is not None and (df_f['buyval'].tail(5).sum() - df_f['sellval'].tail(5).sum()) > 0: smart = True
                            if not smart and df_p is not None and (df_p['buyval'].tail(5).sum() - df_p['sellval'].tail(5).sum()) > 0: smart = True
                            
                            if sqz or can or smart:
                                danh_sach_cho.append({'Mã': ma, 'AI': f"{ai_p}%", 'Lò xo': "Nén" if sqz else "-", 'Cung': "Cạn" if can else "-", 'Tổ chức': "Gom" if smart else "-"})
                except: pass
                bar.progress((i + 1) / len(lst))
            
            st.write("### 🚀 Nhóm Bùng Nổ"); st.table(pd.DataFrame(bung_no).sort_values(by='AI', ascending=False) if bung_no else "Không có.")
            st.write("### ⚖️ Nhóm Danh Sách Chờ (An Toàn)"); st.table(pd.DataFrame(danh_sach_cho).sort_values(by='AI', ascending=False) if danh_sach_cho else "Chưa có.")
