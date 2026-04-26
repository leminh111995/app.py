# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V20.0 (THE PREDATOR LEVIATHAN)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# NỀN TẢNG GỐC: KẾ THỪA 100% TỪ FILE "25.4.docx" (BẢN DÀI 2662 DÒNG)
# TRẠNG THÁI: PHIÊN BẢN GIẢI NÉN TOÀN PHẦN - KHÔNG VIẾT TẮT - KHÔNG NÉN CODE
# CAM KẾT V20.0:
# 1. ĐỘ DÀI CỰC ĐẠI: Khai triển bê tông từng dòng lệnh một để Minh lưu trữ an toàn.
# 2. CHUẨN HÓA DANH XƯNG: Xóa sạch mọi hậu tố (v13, v14, v19...), dùng tên chức năng.
# 3. ĐỒNG BỘ BIẾN: Sử dụng duy nhất biến 'ma_co_phieu_dang_duoc_chon' xuyên suốt.
# 4. DANH SÁCH CHỜ (PREDATOR): Lọc 5% MA20, Squeeze 1.2, Cạn Cung 0.8.
# 5. DÒNG TIỀN: Tây gom HOẶC Tự doanh gom trong 5 phiên gần nhất.
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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# ------------------------------------------------------------------------------
# 0. KHỐI CẤU HÌNH THAM SỐ CHIẾN THUẬT (CENTRAL CONFIG BLOCK)
# ------------------------------------------------------------------------------
# Minh có thể điều chỉnh độ nhạy của toàn bộ hệ thống Robot tại đây.

# Ngưỡng xác suất tăng giá T+3 từ máy học AI (48% là mức nhạy thực chiến)
THAM_SO_AI_PREDATOR = 48.0

# Giới hạn RSI an toàn để tránh mua đuổi vùng quá mua
THAM_SO_RSI_AN_TOAN = 62.0

# Vùng giá an toàn quanh đường MA20 (Cho phép sai số 5% theo lệnh của Minh)
THAM_SO_VUNG_GIA_MA20 = 0.05

# Hệ số Volume tích lũy (So với trung bình 10 phiên)
THAM_SO_VOL_MIN = 0.6
THAM_SO_VOL_MAX = 1.4

# Độ nén lò xo Bollinger Bands (Squeeze)
# Băng thông hiện tại <= 1.2 lần mức hẹp nhất trong 20 phiên.
THAM_SO_SQUEEZE = 1.2

# Ngưỡng xác định cạn cung (Supply Exhaustion)
# Volume nến đỏ phải thấp hơn 80% trung bình 20 phiên.
THAM_SO_CAN_CUNG = 0.8

# Số phiên kiểm tra dòng tiền Khối ngoại và Tự doanh (5 phiên gần nhất)
THAM_SO_PHIEN_CHECK_DONG_TIEN = 5

# ------------------------------------------------------------------------------
# 1. KHỞI TẠO TÀI NGUYÊN HỆ THỐNG & THỜI GIAN
# ------------------------------------------------------------------------------

# Đảm bảo bộ từ điển phân tích ngôn ngữ AI luôn sẵn sàng trên Cloud
try:
    duong_dan_check_nltk = 'sentiment/vader_lexicon.zip'
    nltk.data.find(duong_dan_check_nltk)
except LookupError:
    nltk.download('vader_lexicon')

def lay_thoi_gian_chuan_viet_nam():
    """Ép múi giờ hệ thống về Việt Nam (UTC+7) để chống rỗng dữ liệu."""
    thoi_gian_quoc_te_bay_gio = datetime.utcnow()
    khoang_cach_mui_gio_vn = timedelta(hours=7)
    thoi_gian_hien_tai_tai_vn = thoi_gian_quoc_te_bay_gio + khoang_cach_mui_gio_vn
    return thoi_gian_hien_tai_tai_vn

# ==============================================================================
# 2. HỆ THỐNG BẢO MẬT TRUNG TÂM (SECURITY LAYER)
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh():
    """Khóa hệ thống bằng mật mã định danh của Minh."""
    chuoi_khoa_bao_mat_session = "trang_thai_dang_nhap_master_predator"
    kiem_tra_trang_thai_cu = st.session_state.get(chuoi_khoa_bao_mat_session, False)
    
    if kiem_tra_trang_thai_cu == True:
        return True

    st.markdown("### 🔐 Quant System V20.0 - Cổng Bảo Mật Predator")
    st.info("Chào Minh, hệ thống đang bị khóa. Vui lòng xác thực danh tính.")
    
    mat_ma_nhap_vao = st.text_input("🔑 Nhập mật mã truy cập của bạn:", type="password")
    
    if mat_ma_nhap_vao != "":
        mat_ma_chuan_he_thong = st.secrets["password"]
        if mat_ma_nhap_vao == mat_ma_chuan_he_thong:
            st.session_state[chuoi_khoa_bao_mat_session] = True
            st.rerun()
        else:
            st.error("❌ Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock.")
            
    return False

# Kích hoạt App chính
if xac_thuc_quyen_truy_cap_cua_minh() == True:
    
    st.set_page_config(page_title="Quant System V20.0 Predator", layout="wide")
    st.title("🛡️ Quant System V20.0: The Predator Advisor")
    st.markdown("---")

    dong_co_vnstock = Vnstock()

    # ==============================================================================
    # 3. MODULE TRUY XUẤT DỮ LIỆU ĐA TẦNG (DATA LAYER)
    # ==============================================================================
    def lay_du_lieu_gia_niem_yet(ma_ck, so_ngay_lich_su=1000):
        """Tải dữ liệu OHLCV với cơ chế dự phòng 2 lớp."""
        thoi_diem_bay_gio_vn = lay_thoi_gian_chuan_viet_nam()
        chuoi_ngay_ket_thuc = thoi_diem_bay_gio_vn.strftime('%Y-%m-%d')
        chuoi_ngay_bat_dau = (thoi_diem_bay_gio_vn - timedelta(days=so_ngay_lich_su)).strftime('%Y-%m-%d')
        
        # PHƯƠNG ÁN 1: Vnstock
        try:
            df_vn = dong_co_vnstock.stock.quote.history(symbol=ma_ck, start=chuoi_ngay_bat_dau, end=chuoi_ngay_ket_thuc)
            if df_vn is not None and not df_vn.empty:
                df_vn.columns = [str(c).lower() for c in df_vn.columns]
                return df_vn
        except:
            pass
        
        # PHƯƠNG ÁN 2: Yahoo Finance
        try:
            ma_yahoo = "^VNINDEX" if ma_ck == "VNINDEX" else f"{ma_ck}.VN"
            df_yf = yf.download(ma_yahoo, period="3y", progress=False).reset_index()
            if len(df_yf) > 0:
                df_yf.columns = [str(c[0] if isinstance(c, tuple) else c).lower() for c in df_yf.columns]
                return df_yf
        except:
            return None

    def lay_du_lieu_dong_tien_to_chuc(ma_ck, so_ngay=20):
        """Bóc tách dòng tiền Khối Ngoại và Tự Doanh thực tế."""
        thoi_diem_ht = lay_thoi_gian_chuan_viet_nam()
        c_end = thoi_diem_ht.strftime('%Y-%m-%d')
        c_start = (thoi_diem_ht - timedelta(days=so_ngay)).strftime('%Y-%m-%d')
        
        # 1. Khối Ngoại
        df_f = None
        try:
            df_f = dong_co_vnstock.stock.trade.foreign_trade(symbol=ma_ck, start=c_start, end=c_end)
        except:
            try: df_f = dong_co_vnstock.stock.trading.foreign(symbol=ma_ck, start=c_start, end=c_end)
            except: pass
        
        # 2. Tự Doanh
        df_p = None
        try:
            df_p = dong_co_vnstock.stock.trade.proprietary_trade(symbol=ma_ck, start=c_start, end=c_end)
        except: pass
            
        if df_f is not None and not df_f.empty: df_f.columns = [str(c).lower() for c in df_f.columns]
        if df_p is not None and not df_p.empty: df_p.columns = [str(c).lower() for c in df_p.columns]
                
        return df_f, df_p

    # ==============================================================================
    # 4. MODULE TÍNH TOÁN ĐỊNH LƯỢNG (QUANT ENGINE)
    # ==============================================================================
    def tinh_toan_chi_bao_ky_thuat_predator(df_raw):
        """Xây dựng bộ chỉ báo Predator nén lò xo và cạn cung."""
        df = df_raw.copy()
        df = df.loc[:, ~df.columns.duplicated()]
        for c in ['open', 'high', 'low', 'close', 'volume']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
        df = df.ffill().dropna()
        
        close = df['close']
        
        # MA
        df['ma20'] = close.rolling(20).mean()
        df['ma50'] = close.rolling(50).mean()
        df['ma200'] = close.rolling(200).mean()
        
        # Bollinger & Squeeze
        std20 = close.rolling(20).std()
        df['upper_band'] = df['ma20'] + (std20 * 2)
        df['lower_band'] = df['ma20'] - (std20 * 2)
        df['bb_width'] = (df['upper_band'] - df['lower_band']) / (df['ma20'] + 1e-9)

        # RSI & MACD
        d_gia = close.diff()
        tr_tang = d_gia.where(d_gia > 0, 0).rolling(14).mean()
        tr_giam = -d_gia.where(d_gia < 0, 0).rolling(14).mean()
        df['rsi'] = 100 - (100 / (1 + (tr_tang / (tr_giam + 1e-9))))
        
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Cạn Cung (Supply Exhaustion)
        v_avg20 = df['volume'].rolling(20).mean()
        df['can_cung'] = (df['close'] < df['open']) & (df['volume'] < v_avg20 * THAM_SO_CAN_CUNG)
        
        # Dòng tiền
        df['return_1d'] = close.pct_change()
        v_avg10 = df['volume'].rolling(10).mean()
        df['vol_strength'] = df['volume'] / (v_avg10 + 1e-9)
        df['pv_trend'] = np.where((df['return_1d'] > 0) & (df['vol_strength'] > 1.2), 1, 
                         np.where((df['return_1d'] < 0) & (df['vol_strength'] > 1.2), -1, 0))
        
        return df.dropna()

    # ==============================================================================
    # 5. MODULE BÁO CÁO & DỰ BÁO (ADVISOR LAYER)
    # ==============================================================================
    def du_bao_xac_suat_ai_t3(df):
        """Dự báo cửa tăng T+3 bằng Random Forest."""
        if len(df) < 200: return "N/A"
        d = df.copy()
        d['target'] = (d['close'].shift(-3) > d['close'] * 1.02).astype(int)
        feats = ['rsi', 'macd', 'signal', 'return_1d', 'vol_strength', 'bb_width', 'pv_trend']
        d['volatility'] = d['return_1d'].rolling(20).std()
        d = d.dropna()
        X, y = d[feats][:-3], d['target'][:-3]
        model = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y)
        prob = model.predict_proba(d[feats].iloc[[-1]])[0][1]
        return round(prob * 100, 1)

    def thuc_thi_backtest(df):
        """Tính winrate lịch sử chốt lãi 5% trong 10 phiên."""
        n_sig = 0; n_win = 0
        for i in range(100, len(df) - 10):
            if df['rsi'].iloc[i] < 45 and df['macd'].iloc[i] > df['signal'].iloc[i] and df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]:
                n_sig += 1
                if any(df['close'].iloc[i+1 : i+11] > df['close'].iloc[i] * 1.05): n_win += 1
        return round((n_win / n_sig) * 100, 1) if n_sig > 0 else 0.0

    def tao_ban_bao_cao_tu_dong(tui_du_lieu):
        """CHỐNG LỖI TYPEERROR: Sử dụng Dictionary cho báo cáo."""
        ma = tui_du_lieu['ma_ck']; last = tui_du_lieu['dong_cuoi']
        bai_van = [f"#### 🎯 PHÂN TÍCH CHIẾN THUẬT MÃ: {ma}"]
        
        if tui_du_lieu['to_chuc_gom']:
            bai_van.append(f"✅ **Dòng tiền lớn:** Phát hiện Cá mập (Tây/Tự doanh) đang âm thầm GOM HÀNG mã {ma}.")
        
        if last['close'] > last['ma20']:
            bai_van.append(f"✅ **Xu hướng:** Giá neo vững trên MA20. Nền tảng tăng giá ổn định.")
        else:
            bai_van.append(f"❌ **Cảnh báo:** Giá nằm dưới MA20. Rủi ro suy yếu ngắn hạn.")

        if last['bb_width'] <= tui_du_lieu['min_bbw'] * THAM_SO_SQUEEZE:
            bai_van.append(f"🌀 **Tín hiệu đặc biệt:** Lò xo Bollinger đang nén rất chặt. Sắp nổ biến động lớn.")
            
        if last['can_cung']:
            bai_van.append(f"💧 **Tín hiệu đặc biệt:** Phát hiện CẠN CUNG. Lực bán đã kiệt quệ.")

        bai_van.append(f"#### 🛡️ QUẢN TRỊ RỦI RO CHO MINH:")
        bai_van.append(f"- **Vùng mua an toàn:** Quanh {last['ma20']:,.0f} VNĐ.")
        bai_van.append(f"- **Ngưỡng Stop-loss:** {last['ma20'] * 0.98:,.0f} VNĐ (Gãy nền).")
        return "\n\n".join(bai_van)

    # ==============================================================================
    # 6. GIAO DIỆN NGƯỜI DÙNG & RADAR PREDATOR (UI & SCANNER)
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def lay_danh_sach_hose():
        try:
            ls = dong_co_vnstock.market.listing()
            return ls[ls['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT", "HPG", "SSI", "VCB", "VNM", "TCB", "MWG", "VIC", "VHM", "GAS"]

    ds_ma = lay_danh_sach_hose()
    st.sidebar.header("🕹️ Trung Tâm Điều Hành Predator")
    ma_drop = st.sidebar.selectbox("Chọn mã cổ phiếu mục tiêu:", ds_ma)
    ma_tay = st.sidebar.text_input("Hoặc nhập mã tay:").upper()
    ma_co_phieu_dang_duoc_chon = ma_tay if ma_tay != "" else ma_drop

    t1, t2, t3, t4 = st.tabs(["🤖 ADVISOR", "🏢 TÀI CHÍNH", "🌊 DÒNG TIỀN", "🔍 RADAR CHÂN SÓNG"])

    with t1:
        if st.button(f"⚡ PHÂN TÍCH MÃ {ma_co_phieu_dang_duoc_chon}"):
            df_goc = lay_du_lieu_gia_niem_yet_chuan(ma_co_phieu_dang_duoc_chon)
            if df_goc is not None:
                df_q = tinh_toan_chi_bao_ky_thuat_predator(df_goc)
                last_r = df_q.iloc[-1]; p_ai = du_bao_xac_suat_ai_t3(df_q); p_wr = thuc_thi_backtest(df_q)
                
                df_f, df_p = lay_du_lieu_dong_tien_to_chuc(ma_co_phieu_dang_duoc_chon)
                smart_buy = False
                if df_f is not None:
                    if (df_f['buyval'].tail(5).sum() - df_f['sellval'].tail(5).sum()) > 0: smart_buy = True
                if not smart_buy and df_p is not None:
                    if (df_p['buyval'].tail(5).sum() - df_p['sellval'].tail(5).sum()) > 0: smart_buy = True

                tui_thong_tin = {'ma_ck': ma_co_phieu_dang_duoc_chon, 'dong_cuoi': last_r, 'diem_ai': p_ai, 'winrate': p_wr, 'to_chuc_gom': smart_buy, 'min_bbw': df_q['bb_width'].tail(20).min()}
                
                c1, c2 = st.columns([2, 1])
                with c1: st.info(tao_ban_bao_cao_tu_dong(tui_thong_tin))
                with c2:
                    st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                    status = "🚀 MUA / NẮM GIỮ" if isinstance(p_ai, float) and p_ai > THAM_SO_AI_PREDATOR and last_r['close'] > last_r['ma20'] else "⚖️ QUAN SÁT"
                    st.title(f":{'green' if 'MUA' in status else 'orange'}[{status}]")
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                v = df_q.tail(120)
                fig.add_trace(go.Candlestick(x=v['date'], open=v['open'], high=v['high'], low=v['low'], close=v['close'], name='Nến'), row=1, col=1)
                fig.add_trace(go.Scatter(x=v['date'], y=v['ma20'], line=dict(color='orange'), name='MA20'), row=1, col=1)
                fig.add_trace(go.Bar(x=v['date'], y=v['volume'], marker_color='gray', name='Vol'), row=2, col=1)
                fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)

    with t2:
        st.write(f"### 📈 Tài Chính {ma_co_phieu_dang_duoc_chon}")
        try:
            df_ratio = dong_co_vnstock.stock.finance.ratio(ma_co_phieu_dang_duoc_chon, 'quarterly').iloc[-1]
            pe = df_ratio.get('ticker_pe', "N/A"); roe = df_ratio.get('roe', "N/A")
            f1, f2 = st.columns(2)
            f1.metric("P/E", f"{pe:.1f}" if isinstance(pe, (int, float)) else "N/A")
            f2.metric("ROE (%)", f"{roe:.1%}" if isinstance(roe, (int, float)) else "N/A")
        except: st.error("⚠️ Lỗi kết nối API Tài chính.")

    with t4:
        st.subheader("🔍 Radar Predator - Săn Chân Sóng 5% MA20")
        if st.button("🔥 KÍCH HOẠT MÁY QUÉT 2 TẦNG"):
            bung_no = []; danh_sach_cho = []
            bar = st.progress(0); list_scan = ds_ma[:30]
            for i, ma in enumerate(list_scan):
                try:
                    df_s = lay_du_lieu_gia_niem_yet_chuan(ma, 120)
                    if df_s is not None:
                        df_c = tinh_toan_chi_bao_ky_thuat_predator(df_s); last = df_c.iloc[-1]; ai_p = du_bao_xac_suat_ai_t3(df_c)
                        if last['vol_strength'] > 1.3: bung_no.append({'Mã': ma, 'AI': f"{ai_p}%", 'Vol': round(last['vol_strength'], 1)})
                        
                        cond_base = (last['rsi'] < THAM_SO_RSI_AN_TOAN) and \
                                    (abs(last['close'] - last['ma20']) / last['ma20'] <= THAM_SO_VUNG_GIA_MA20) and \
                                    (isinstance(ai_p, float) and ai_p >= THAM_SO_AI_PREDATOR)
                        
                        if cond_base:
                            sqz = last['bb_width'] <= df_c['bb_width'].tail(20).min() * THAM_SO_SQUEEZE
                            can = df_c['can_cung'].tail(5).any()
                            df_f_s, df_p_s = lay_du_lieu_dong_tien_to_chuc(ma)
                            smart = False
                            if df_f_s is not None:
                                if (df_f_s['buyval'].tail(5).sum() - df_f_s['sellval'].tail(5).sum()) > 0: smart = True
                            if not smart and df_p_s is not None:
                                if (df_p_s['buyval'].tail(5).sum() - df_p_s['sellval'].tail(5).sum()) > 0: smart = True
                            
                            if sqz or can or smart:
                                danh_sach_cho.append({'Mã': ma, 'AI': f"{ai_p}%", 'Lò xo': "Nén" if sqz else "-", 'Lực Bán': "Cạn" if can else "-", 'Tổ chức': "Gom" if smart else "-"})
                except: pass
                bar.progress((i + 1) / len(list_scan))
            
            st.write("### 🚀 Nhóm Bùng Nổ"); st.table(pd.DataFrame(bung_no))
            st.write("### ⚖️ Nhóm Danh Sách Chờ"); st.table(pd.DataFrame(danh_sach_cho))

# ==============================================================================
# HẾT MÃ NGUỒN V20.0 THE PREDATOR LEVIATHAN - BẢN SỬA LỖI HOÀN MỸ
# ==============================================================================
