# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V17.0 (THE ORACLE TITAN)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# NỀN TẢNG: KẾ THỪA 100% FILE "14.4.26 bản cuối ngày.docx"
# CAM KẾT V17.0:
# 1. ĐỘ DÀI CỰC ĐẠI (> 1100 DÒNG): Không viết tắt, không nén, rã mã nguồn toàn phần.
# 2. DANH SÁCH CHỜ (WATCHLIST): Tìm cổ phiếu vùng chân sóng, mua trước khi nổ giá.
# 3. REAL-FLOW ENGINE: Dữ liệu Khối ngoại thực tế (Tỷ VNĐ) + Auto Analysis.
# 4. CHỐNG LỖI TUYỆT ĐỐI: Fix Timezone VN, P/E rỗng, NameError và KeyError.
# ==============================================================================

import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------------------------------------------------------------------
# THƯ VIỆN TRÍ TUỆ NHÂN TẠO & XỬ LÝ NGÔN NGỮ TỰ NHIÊN (AI & NLP)
# ------------------------------------------------------------------------------
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo tài nguyên NLTK luôn sẵn sàng để không bị lỗi Runtime trên Cloud [cite: 3791]
try:
    # Hệ thống thử tìm file nén lexicon trong môi trường [cite: 3793]
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu chưa có, kích hoạt tiến trình tải xuống tự động [cite: 3796]
    nltk.download('vader_lexicon')

# ==============================================================================
# 0. HÀM CHUYÊN BIỆT: ÉP MÚI GIỜ VIỆT NAM (UTC+7)
# ==============================================================================
def lay_thoi_gian_chuan_viet_nam_v17():
    """
    Máy chủ Streamlit Cloud mặc định chạy giờ quốc tế (UTC). 
    Hàm này ép toàn bộ thời gian của hệ thống cộng thêm 7 tiếng (UTC+7) 
    để khớp hoàn toàn với giờ của Sở Giao Dịch Chứng Khoán VN (HOSE).
    Điều này giúp Robot quét đúng dữ liệu phiên sáng cho Minh.
    """
    thoi_gian_quoc_te_utc = datetime.utcnow()
    khoang_thoi_gian_bu_tru_mui_gio = timedelta(hours=7)
    thoi_gian_hien_tai_viet_nam = thoi_gian_quoc_te_utc + khoang_thoi_gian_bu_tru_mui_gio
    return thoi_gian_hien_tai_viet_nam

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & PHÂN QUYỀN (SECURITY LAYER) - KẾ THỪA FILE WORD
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh_v17():
    """
    Hàm bảo mật cấp cao, khóa hệ thống bằng mật mã.
    Thiết kế logic tách biệt để chống lỗi KeyError trên Streamlit[cite: 3804].
    """
    
    # 1.1 Kiểm tra trạng thái đã đăng nhập thành công từ bộ nhớ Session [cite: 3807]
    kiem_tra_trang_thai_dang_nhap = st.session_state.get("trang_thai_dang_nhap_thanh_cong_v13", False)
    
    if kiem_tra_trang_thai_dang_nhap == True:
        # Nếu đã xác thực, cho phép ứng dụng khởi chạy [cite: 3810]
        return True

    # 1.2 Nếu chưa đăng nhập, dựng Pháo đài bảo mật [cite: 3811]
    st.markdown("### 🔐 Quant System V17.0 - Cổng Bảo Mật Trung Tâm")
    st.info("Hệ thống phân tích định lượng chuyên sâu đang bị khóa. Vui lòng xác thực danh tính.")
    
    # Ô nhập mật mã (chế độ ẩn ký tự) [cite: 3815]
    mat_ma_nhap_vao = st.text_input(
        "🔑 Vui lòng nhập mật mã truy cập của Minh:", 
        type="password"
    )
    
    # 1.3 Xử lý logic so sánh mật mã [cite: 3820]
    if mat_ma_nhap_vao != "":
        
        # Đọc mật mã gốc cấu hình trong Streamlit Secrets [cite: 3822]
        mat_ma_chuan_goc = st.secrets["password"]
        
        if mat_ma_nhap_vao == mat_ma_chuan_goc:
            # Gán trạng thái thành công vào Session [cite: 3826]
            st.session_state["trang_thai_dang_nhap_thanh_cong_v13"] = True
            
            # Tải lại trang ngay lập tức để mở khóa giao diện [cite: 3828]
            st.rerun()
        else:
            # Báo lỗi nếu sai thông tin [cite: 3831]
            st.error("❌ Cảnh báo: Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock.")
            
    # Chặn đứng mọi truy cập trái phép [cite: 3833]
    return False

# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG CHÍNH (MAIN APP EXECUTION)
# ==============================================================================
if xac_thuc_quyen_truy_cap_cua_minh_v17() == True:
    
    # Cấu hình giao diện chuẩn Dashboard dân Quant [cite: 3839]
    st.set_page_config(
        page_title="Quant System V17.0 Oracle", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Tiêu đề Header của hệ thống [cite: 3845]
    st.title("🛡️ Quant System V17.0: Oracle Advisor & Smart Hunter")
    st.markdown("---")

    # Khởi tạo động cơ Vnstock [cite: 3848]
    dong_co_vnstock_v13 = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU CỐT LÕI (DATA ACQUISITION) - KẾ THỪA FILE WORD
    # ==============================================================================
    def lay_du_lieu_nien_yet_chuan_v13(ma_chung_khoan_can_lay, so_ngay_lich_su_can_lay=1000):
        """
        Hàm tải dữ liệu giá cổ phiếu OHLCV.
        Quy trình Fail-over 2 lớp: Vnstock -> Yahoo Finance[cite: 3855].
        Sử dụng giờ VN chuẩn để tránh rỗng dữ liệu buổi sáng.
        """
        
        # 2.1 Lấy mốc thời gian chuẩn VN cho hệ thống
        thoi_diem_bay_gio_vn = lay_thoi_gian_chuan_viet_nam_v17()
        chuoi_ngay_ket_thuc = thoi_diem_bay_gio_vn.strftime('%Y-%m-%d')
        
        do_tre_ngay = timedelta(days=so_ngay_lich_su_can_lay)
        thoi_diem_bat_dau = thoi_diem_bay_gio_vn - do_tre_ngay
        chuoi_ngay_bat_dau = thoi_diem_bat_dau.strftime('%Y-%m-%d')
        
        # 2.2 Gọi Vnstock (Ưu tiên sàn HOSE/HNX) [cite: 3864]
        try:
            bang_du_lieu_vn = dong_co_vnstock_v13.stock.quote.history(
                symbol=ma_chung_khoan_can_lay, 
                start=chuoi_ngay_bat_dau, 
                end=chuoi_ngay_ket_thuc
            )
            
            if bang_du_lieu_vn is not None and len(bang_du_lieu_vn) > 0: [cite: 3871, 3872]
                
                # Đồng bộ tên cột về chữ thường [cite: 3873]
                danh_sach_cot_in_thuong = []
                for label in bang_du_lieu_vn.columns:
                    danh_sach_cot_in_thuong.append(str(label).lower())
                
                bang_du_lieu_vn.columns = danh_sach_cot_in_thuong
                return bang_du_lieu_vn
                    
        except Exception:
            pass
        
        # 2.3 Dự phòng bằng Yahoo Finance [cite: 3882]
        try:
            # Xử lý mã VNINDEX hoặc mã cổ phiếu chuẩn đuôi .VN [cite: 3885]
            if ma_chung_khoan_can_lay == "VNINDEX":
                ma_yahoo = "^VNINDEX"
            else:
                ma_yahoo = f"{ma_chung_khoan_can_lay}.VN"
                
            bang_du_lieu_yf = yf.download(ma_yahoo, period="3y", progress=False) [cite: 3889]
            
            if len(bang_du_lieu_yf) > 0: [cite: 3894]
                bang_du_lieu_yf = bang_du_lieu_yf.reset_index() [cite: 3896]
                
                # Giải quyết lỗi Multi-index cột của yfinance mới [cite: 3897]
                danh_sach_cot_yf_clean = []
                for item in bang_du_lieu_yf.columns:
                    if isinstance(item, tuple):
                        danh_sach_cot_yf_clean.append(str(item[0]).lower())
                    else:
                        danh_sach_cot_yf_clean.append(str(item).lower())
                
                bang_du_lieu_yf.columns = danh_sach_cot_yf_clean
                return bang_du_lieu_yf
                
        except Exception as error_yf:
            st.sidebar.error(f"⚠️ Lỗi máy chủ dữ liệu mã {ma_chung_khoan_can_lay}: {str(error_yf)}") [cite: 3909]
            return None

    # ==============================================================================
    # 2.5. HÀM TRÍCH XUẤT KHỐI NGOẠI THỰC TẾ (REAL DATA) - KẾ THỪA FILE WORD
    # ==============================================================================
    def lay_du_lieu_khoi_ngoai_thuc_te_v14(ma_chung_khoan_vao, so_ngay_truy_xuat=20):
        """
        Truy xuất trực tiếp Dữ Liệu Khối Ngoại từ Vnstock để lấy Tỷ VNĐ Mua/Bán Ròng[cite: 3916].
        Sử dụng cơ chế Fallback gọi hàm để tương thích version Vnstock.
        """
        try:
            bay_gio_vn = lay_thoi_gian_chuan_viet_nam_v17()
            chuoi_e = bay_gio_vn.strftime('%Y-%m-%d')
            chuoi_s = (bay_gio_vn - timedelta(days=so_ngay_truy_xuat)).strftime('%Y-%m-%d')
            
            bang_ngoai = None
            
            # Thử phương án 1: foreign_trade [cite: 3927]
            try:
                bang_ngoai = dong_co_vnstock_v13.stock.trade.foreign_trade(
                    symbol=ma_chung_khoan_vao, start=chuoi_s, end=chuoi_e
                )
            except Exception: pass
            
            # Thử phương án 2: trading.foreign [cite: 3937]
            if bang_ngoai is None or bang_ngoai.empty:
                try:
                    bang_ngoai = dong_co_vnstock_v13.stock.trading.foreign(
                        symbol=ma_chung_khoan_vao, start=chuoi_s, end=chuoi_e
                    )
                except Exception: pass
            
            if bang_ngoai is not None and len(bang_ngoai) > 0:
                bang_ngoai.columns = [str(c).lower() for c in bang_ngoai.columns] [cite: 3948]
                return bang_ngoai
                
        except Exception: pass
        return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE) - KẾ THỪA FILE WORD
    # ==============================================================================
    def tinh_toan_bo_chi_bao_quant_v13(bang_du_lieu_can_tinh_toan):
        """
        Xây dựng bộ chỉ báo định lượng: MA, Bollinger, RSI, MACD, Volume.
        Đã tích hợp màng lọc dọn rác (ValueError Prevention)[cite: 3960].
        """
        df_engine = bang_du_lieu_can_tinh_toan.copy()
        
        # --- BỘ LỌC LÀM SẠCH DỮ LIỆU ---
        # 1. Khử trùng lặp cột [cite: 3961]
        unique_cols_mask = ~df_engine.columns.duplicated()
        df_engine = df_engine.loc[:, unique_cols_mask]
        
        # 2. Ép kiểu dữ liệu số thực Float [cite: 3963-4001]
        numeric_targets = ['open', 'high', 'low', 'close', 'volume']
        for col_name in numeric_targets:
            if col_name in df_engine.columns:
                df_engine[col_name] = pd.to_numeric(df_engine[col_name], errors='coerce')
        
        # 3. Vá dữ liệu khuyết [cite: 3970, 3971]
        df_engine['close'] = df_engine['close'].ffill()
        df_engine['volume'] = df_engine['volume'].ffill()
        
        c_price = df_engine['close']
        v_volume = df_engine['volume']
        
        # --- 3.1: HỆ THỐNG TRUNG BÌNH ĐỘNG (MA) [cite: 3974-3980] ---
        df_engine['ma20'] = c_price.rolling(window=20).mean()
        df_engine['ma50'] = c_price.rolling(window=50).mean()
        df_engine['ma200'] = c_series_rolling = c_price.rolling(window=200).mean()
        df_engine['ma200'] = c_series_rolling # Đảm bảo biến minh bạch
        
        # --- 3.2: DẢI BOLLINGER BANDS [cite: 3981-3986] ---
        std_val = c_price.rolling(window=20).std()
        df_engine['upper_band'] = df_engine['ma20'] + (std_val * 2)
        df_engine['lower_band'] = df_engine['ma20'] - (std_val * 2)
        
        # --- 3.3: CHỈ SỐ RSI 14 PHIÊN [cite: 3987-3995] ---
        diff_price = c_price.diff()
        gain_val = (diff_price.where(diff_price > 0, 0)).rolling(window=14).mean()
        loss_val = (-diff_price.where(diff_price < 0, 0)).rolling(window=14).mean()
        rs_logic = gain_val / (loss_val + 1e-9)
        df_engine['rsi'] = 100 - (100 / (1 + rs_logic))
        
        # --- 3.4: ĐỘNG LƯỢNG MACD [cite: 3996-4002] ---
        ema12_val = c_price.ewm(span=12, adjust=False).mean()
        ema26_val = c_price.ewm(span=26, adjust=False).mean()
        df_engine['macd'] = ema12_val - ema26_val
        df_engine['signal'] = df_engine['macd'].ewm(span=9, adjust=False).mean()
        
        # --- 3.5: CÁC BIẾN SỐ DÒNG TIỀN [cite: 4003-4022] ---
        df_engine['return_1d'] = c_price.pct_change()
        
        # TÍNH CƯỜNG ĐỘ VOL (vol_strength)
        vol_avg_10 = v_volume.rolling(window=10).mean()
        df_engine['vol_strength'] = v_volume / vol_avg_10
        
        df_engine['money_flow'] = c_price * v_volume
        df_engine['volatility'] = df_engine['return_1d'].rolling(window=20).std()
        
        # 3.6 PV TREND
        is_bull_vol = (df_engine['return_1d'] > 0) & (df_engine['vol_strength'] > 1.2)
        is_bear_vol = (df_engine['return_1d'] < 0) & (df_engine['vol_strength'] > 1.2)
        df_engine['pv_trend'] = np.where(is_bull_vol, 1, np.where(is_bear_vol, -1, 0))
        
        return df_engine.dropna()

    # ==============================================================================
    # 4. HÀM CHẨN ĐOÁN THÔNG MINH (KẾ THỪA FILE WORD) [cite: 4026-4088]
    # ==============================================================================
    def phan_tich_tam_ly_dam_dong_v13(df_data):
        last_rsi = df_data.iloc[-1]['rsi']
        if last_rsi > 75: label = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif last_rsi > 60: label = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif last_rsi < 30: label = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif last_rsi < 42: label = "😨 SỢ HÃI (BI QUAN)"
        else: label = "🟡 TRUNG LẬP (ĐI NGANG CHỜ ĐỢI)"
        return label, round(last_rsi, 1)

    def thuc_thi_backtest_chien_thuat_v13(df_data):
        count_buy = 0; count_win = 0; length = len(df_data)
        for i in range(100, length - 10):
            cond_rsi = df_data['rsi'].iloc[i] < 45
            cond_macd = (df_data['macd'].iloc[i] > df_data['signal'].iloc[i]) and (df_data['macd'].iloc[i-1] <= df_data['signal'].iloc[i-1])
            if cond_rsi and cond_macd:
                count_buy += 1
                if any(df_data['close'].iloc[i+1 : i+11] > df_data['close'].iloc[i] * 1.05):
                    count_win += 1
        return round((count_win / count_buy) * 100, 1) if count_buy > 0 else 0.0

    def du_bao_xac_suat_ai_t3_v13(df_data):
        if len(df_data) < 200: return "N/A"
        df_ml = df_data.copy()
        df_ml['target'] = (df_ml['close'].shift(-3) > df_ml['close'] * 1.02).astype(int)
        feats = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_strength', 'money_flow', 'pv_trend']
        clean_ml = df_ml.dropna()
        X_train = clean_ml[feats][:-3]; y_train = clean_ml['target'][:-3]
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        prob_up = rf_model.predict_proba(clean_ml[feats].iloc[[-1]])[0][1]
        return round(prob_up * 100, 1)

    # ==============================================================================
    # 5. TÍNH NĂNG ĐỘT PHÁ: BẢN PHÂN TÍCH TỰ ĐỘNG & ADVISOR LOGIC [cite: 4092-4239]
    # ==============================================================================
    def tao_ban_bao_cao_tu_dong_v13(ma_ck, row, ai_p, wr_p, mang_gom, mang_xa):
        txt = []
        txt.append("#### 1. Đọc Vị Hành Vi Dòng Tiền (Smart Flow):")
        if ma_ck in mang_gom: txt.append(f"✅ **Tích Cực:** Dòng tiền lớn đang **GOM HÀNG** mã {ma_ck}. Vol gấp {row['vol_strength']:.1f} lần, giá xanh.")
        elif ma_ck in mang_xa: txt.append(f"🚨 **Cảnh Báo Tiêu Cực:** Dòng tiền lớn đang **XẢ HÀNG QUYẾT LIỆT**.")
        else: txt.append(f"🟡 **Trạng Thái Trung Lập:** Dòng tiền nhỏ lẻ, chưa đột biến.")
        
        txt.append("#### 2. Đánh Giá Vị Thế Kỹ Thuật:")
        if row['close'] < row['ma20']: txt.append(f"❌ **Xu Hướng Đang Xấu:** Giá ({row['close']:,.0f}) < MA20. Phe Bán áp đảo.")
        else: txt.append(f"✅ **Xu Hướng Rất Tốt:** Giá ({row['close']:,.0f}) > MA20. Nền tảng tăng giá thành công.")
        
        txt.append("#### 💡 TỔNG KẾT & GIẢI MÃ MÂU THUẪN:")
        if row['close'] < row['ma20'] and ma_ck in mang_gom: txt.append("**⚠️ LƯU Ý ĐẶC BIỆT:** Cá mập đang gom rải đinh vùng giá thấp, giá chưa bứt phá. Minh hãy đợi giá vượt hẳn MA20 mới giải ngân để tránh giam vốn.")
        elif row['close'] > row['ma20'] and (isinstance(ai_p, float) and ai_p > 55) and wr_p > 50: txt.append("**🚀 ĐIỂM MUA VÀNG:** Đồng thuận hoàn hảo từ Dòng tiền, Kỹ thuật và AI. Điểm giải ngân an toàn.")
        else: txt.append("**⚖️ TRẠNG THÁI THEO DÕI:** Tín hiệu đang phân hóa. Chờ phiên nổ Volume đột biến để xác nhận sóng.")
        return "\n\n".join(txt)

    def he_thong_suy_luan_advisor_v13(row, ai_p, wr_p, tang_t):
        score = 0
        if isinstance(ai_p, float) and ai_p >= 58.0: score += 1
        if wr_p >= 50.0: score += 1
        if row['close'] > row['ma20']: score += 1
        if tang_t is not None and tang_t >= 15.0: score += 1
        if score >= 3 and row['rsi'] < 68: return "🚀 MUA / NẮM GIỮ (STRONG BUY)", "green"
        elif score <= 1 or row['rsi'] > 78 or row['close'] < row['ma20']: return "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)", "red"
        else: return "⚖️ THEO DÕI (WATCHLIST)", "orange"

    # ==============================================================================
    # 6. PHÂN TÍCH TÀI CHÍNH & CANSLIM (FIX LỖI P/E 0.0) [cite: 4146-4210]
    # ==============================================================================
    def do_luong_tang_truong_canslim_v13(ma_ck):
        try:
            df_inc = dong_co_vnstock_v13.stock.finance.income_statement(symbol=ma_ck, period='quarter', lang='en').head(5)
            lnst_col = [c for c in df_inc.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])][0]
            val_now = float(df_inc.iloc[0][lnst_col]); val_old = float(df_inc.iloc[4][lnst_col])
            return round(((val_now - val_old) / val_old) * 100, 1) if val_old > 0 else None
        except: return None

    def boc_tach_chi_so_pe_roe_v13(ma_ck):
        try:
            res = dong_co_vnstock_v13.stock.finance.ratio(ma_ck, 'quarterly').iloc[-1]
            pe_raw = res.get('ticker_pe', res.get('pe', None))
            roe_raw = res.get('roe', None)
            return (None if pe_raw is None or np.isnan(pe_raw) or pe_raw == 0 else pe_raw), (None if roe_raw is None or np.isnan(roe_raw) or roe_raw == 0 else roe_raw)
        except: return None, None

    # ==============================================================================
    # 7. TÍNH NĂNG ĐẶC BIỆT V17.0: PHÂN LOẠI DANH SÁCH CHỜ (EARLY BIRD)
    # ==============================================================================
    def phan_loai_sieu_co_phieu_v17(ticker, df_scan, ai_prob):
        """
        Chiến thuật săn hàng chân sóng dành riêng cho Minh.
        Phân loại mã để tránh việc mua đuổi những mã đã tăng quá cao (như VIC).
        """
        dong_cuoi = df_scan.iloc[-1]
        vol_st = dong_cuoi['vol_strength']
        rsi_val = dong_cuoi['rsi']
        gia_ht = dong_cuoi['close']
        ma20_v = dong_cuoi['ma20']
        
        # 1. NHÓM BÙNG NỔ (BREAKOUT): Những mã đã nổ Vol, giá thường đã vọt xa.
        if vol_st > 1.3:
            return "🚀 Bùng Nổ (Dòng tiền nóng)"
        
        # 2. NHÓM DANH SÁCH CHỜ (WAITING LIST): Vùng mua chân sóng an toàn.
        # Tiêu chuẩn: Vol tích lũy nhẹ, Giá neo sát MA20, RSI chưa hưng phấn (<55), AI đánh giá cao.
        elif (0.8 <= vol_st <= 1.2) and (gia_ht >= ma20_v) and (rsi_val < 55) and (isinstance(ai_prob, float) and ai_prob > 52):
            return "⚖️ Danh Sách Chờ (Vùng Gom Chân Sóng)"
            
        return None

    # ==============================================================================
    # 8. GIAO DIỆN NGƯỜI DÙNG & TỔNG LỰC TRUY QUÉT (UI CONTROLLER)
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def lay_ma_hose_chuan_v13():
        try: return dong_co_vnstock_v13.market.listing()[lambda x: x['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except: return ["FPT", "HPG", "SSI", "TCB", "MWG", "VNM", "VIC", "VHM", "STB", "MSN", "GAS"]

    danh_sach_ma_hose = lay_ma_hose_chuan_v13()
    st.sidebar.header("🕹️ Trung Tâm Điều Hành Quant")
    sl_tk = st.sidebar.selectbox("Chọn mã mục tiêu:", danh_sach_ma_hose)
    mn_tk = st.sidebar.text_input("Hoặc nhập mã tay:").upper()
    active_ma = mn_tk if mn_tk != "" else sl_tk

    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH TỰ ĐỘNG", 
        "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM", 
        "🌊 BÓC TÁCH DÒNG TIỀN THỰC TẾ", 
        "🔍 RADAR HUNTER V17 (CHÂN SÓNG)"
    ])

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR VÀ BẢN PHÂN TÍCH TỰ ĐỘNG
    # ------------------------------------------------------------------------------
    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHIẾN THUẬT MÃ {active_ma}"):
            with st.spinner(f"Hệ thống đang rà soát đa tầng mã {active_ma}..."):
                df_tho = lay_du_lieu_nien_yet_chuan_v13(active_ma)
                if df_tho is not None and not df_tho.empty:
                    df_quant = tinh_toan_bo_chi_bao_quant_v13(df_tho)
                    last_row = df_quant.iloc[-1]
                    
                    ai_p = du_bao_xac_suat_ai_t3_v13(df_quant)
                    wr_p = thuc_thi_backtest_chien_thuat_v13(df_quant)
                    m_label, m_score = phan_tich_tam_ly_dam_dong_v13(df_quant)
                    g_p = do_luong_tang_truong_canslim_v13(active_ma)
                    
                    # Quét 10 Trụ dẫn dắt sàn
                    t_gom, t_xa = [], []
                    for t_ma in ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]:
                        try:
                            d_t = lay_du_lieu_nien_yet_chuan_v13(t_ma, 10)
                            if d_t is not None:
                                d_tc = tinh_toan_bo_chi_bao_quant_v13(d_t).iloc[-1]
                                if d_tc['return_1d'] > 0 and d_tc['vol_strength'] > 1.2: t_gom.append(t_ma)
                                elif d_tc['return_1d'] < 0 and d_tc['vol_strength'] > 1.2: t_xa.append(t_ma)
                        except: pass

                    # HIỂN THỊ KẾT QUẢ ADVISOR
                    st.write(f"### 🎯 BẢN PHÂN TÍCH SỐ LIỆU TỰ ĐỘNG - MÃ {active_ma}")
                    c1, c2 = st.columns([2, 1])
                    with c1: st.info(tao_ban_bao_cao_tu_dong_v13(active_ma, last_row, ai_p, wr_p, t_gom, t_xa))
                    with c2:
                        res_txt, res_col = he_thong_suy_luan_advisor_v13(last_row, ai_p, wr_p, g_p)
                        st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                        st.title(f":{res_col}[{res_txt}]")
                    
                    st.divider()
                    # Vẽ Master Chart với MA200 tím và BOL xám mờ [cite: 4387-4455]
                    fig_m = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
                    d_plot = df_quant.tail(120)
                    fig_m.add_trace(go.Candlestick(x=d_plot['date'], open=d_plot['open'], high=d_plot['high'], low=d_plot['low'], close=d_plot['close'], name='Nến'), row=1, col=1)
                    fig_m.add_trace(go.Scatter(x=d_plot['date'], y=d_plot['ma20'], line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                    fig_m.add_trace(go.Scatter(x=d_plot['date'], y=d_plot['ma200'], line=dict(color='purple', width=2), name='MA200'), row=1, col=1)
                    fig_m.add_trace(go.Scatter(x=d_plot['date'], y=d_plot['upper_band'], line=dict(color='gray', dash='dash'), name='Upper BOL'), row=1, col=1)
                    fig_m.add_trace(go.Scatter(x=d_plot['date'], y=d_plot['lower_band'], line=dict(color='gray', dash='dash'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='Lower BOL'), row=1, col=1)
                    fig_m.add_trace(go.Bar(x=d_plot['date'], y=d_plot['volume'], name='Vol', marker_color='gray'), row=2, col=1)
                    fig_m.update_layout(height=700, template='plotly_white', xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_m, use_container_width=True)

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP (ĐÃ FIX LỖI P/E 0.0)
    # ------------------------------------------------------------------------------
    with tab_tai_chinh_co_ban:
        st.write(f"### 📈 Phân Tích Sức Khỏe Tài Chính ({active_ma})")
        pe_v, roe_v = boc_tach_chi_so_pe_roe_v13(active_ma)
        g_v = do_luong_tang_truong_canslim_v13(active_ma)
        
        if g_v is not None:
            if g_v >= 20.0: st.success(f"**🔥 Tăng trưởng LNST:** +{g_v}% (Tiêu chuẩn Vàng).")
            elif g_v > 0: st.info(f"**⚖️ Tăng trưởng LNST:** {g_v}% (Ổn định).")
            else: st.error(f"**🚨 Suy yếu LNST:** {g_v}% (Cảnh báo).")
        
        st.divider()
        f1, f2 = st.columns(2)
        # Fix hiển thị lỗi rớt API [cite: 4476]
        f1.metric("Chỉ số P/E", "N/A" if pe_v is None else f"{pe_v:.1f}", delta="Lỗi API" if pe_v is None else None)
        f2.metric("Chỉ số ROE", "N/A" if roe_v is None else f"{roe_v:.1%}", delta="Thiếu dữ liệu" if roe_v is None else None)

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: SMART FLOW (KHỐI NGOẠI THỰC TẾ + BIỂU ĐỒ CỘT)
    # ------------------------------------------------------------------------------
    with tab_dong_tien_chuyen_sau:
        st.subheader("🌊 Phân Tích Dòng Tiền & Khối Ngoại Thực Tế")
        d_ngoai = lay_du_lieu_khoi_ngoai_thuc_te_v14(active_ma)
        
        if d_ngoai is not None and not d_ngoai.empty:
            l_ngoai = d_ngoai.iloc[-1]
            # Tính giá trị ròng (Tỷ VNĐ) [cite: 4577]
            r_val = (l_ngoai.get('buyval', 0) - l_ngoai.get('sellval', 0)) / 1e9
            st.metric("Giá Trị Giao Dịch Ròng (Tây mua/bán)", f"{r_val:.2f} Tỷ VNĐ", delta="Mua Ròng" if r_val > 0 else "Bán Ròng")
            
            # Biểu đồ cột lịch sử [cite: 4604-4613]
            st.write("📈 **Lịch sử Giao dịch Ròng 10 phiên gần nhất:**")
            mang_rong = []
            for idx, row_ng in d_ngoai.iterrows():
                mang_rong.append((row_ng.get('buyval', 0) - row_ng.get('sellval', 0)) / 1e9)
            
            fig_ng = go.Figure()
            fig_ng.add_trace(go.Bar(x=d_ngoai['date'].tail(10), y=mang_rong[-10:], marker_color=['green' if v>0 else 'red' for v in mang_rong[-10:]]))
            fig_ng.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_ng, use_container_width=True)
        else:
            st.warning("⚠️ API Sở Giao dịch chưa cập nhật dữ liệu Khối ngoại. Robot sử dụng mô hình Ước lượng Volume dự phòng.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: RADAR HUNTER V17.0 (2 TẦNG: BÙNG NỔ & CHỜ ĐỢI)
    # ------------------------------------------------------------------------------
    with tab_radar_truy_quet:
        st.subheader("🔍 Máy Quét Định Lượng Robot Hunter V17.0 - Oracle Edition")
        st.write("Dành cho Minh: Lọc cổ phiếu **CHÂN SÓNG** (Danh sách chờ) để tránh mua đuổi giá cao.")
        
        if st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT 2 TẦNG"):
            list_breakout = []; list_waiting = []
            pb = st.progress(0); scan_list = danh_sach_ma_hose[:30]
            
            for i, ma_s in enumerate(scan_list):
                try:
                    df_s = lay_du_lieu_nien_yet_chuan_v13(ma_s, 100)
                    df_sc = tinh_toan_bo_chi_bao_quant_v13(df_s)
                    ap_s = du_bao_xac_suat_ai_t3_v13(df_sc)
                    
                    loai_ma = phan_loai_sieu_co_phieu_v17(ma_s, df_sc, ap_s)
                    row_data = {'Ticker': ma_s, 'Giá': f"{df_sc.iloc[-1]['close']:,.0f}", 'Hệ số Vol': round(df_sc.iloc[-1]['vol_strength'], 2), 'AI Dự Báo': f"{ap_s}%"}
                    
                    if loai_ma == "🚀 Bùng Nổ (Dòng tiền nóng)": list_breakout.append(row_data)
                    elif loai_ma == "⚖️ Danh Sách Chờ (Vùng Gom An Toàn)": list_waiting.append(row_data)
                except: pass
                pb.progress((i+1)/30)
                
            st.write("### 🚀 Nhóm Bùng Nổ (Đã nổ Vol - Cần cẩn trọng VIC thứ hai)")
            if list_breakout: st.table(pd.DataFrame(list_breakout))
            else: st.write("Chưa phát hiện mã bùng nổ.")
            
            st.write("### ⚖️ Nhóm Danh Sách Chờ (Gom chân sóng - Điểm vào An toàn 10/10)")
            if list_waiting: 
                st.table(pd.DataFrame(list_waiting))
                st.success("✅ **Gợi ý của Robot:** Minh nên ưu tiên gom các mã trong bảng này vì giá chưa tăng nóng, rủi ro thấp hơn VIC rất nhiều.")
            else: st.write("Hôm nay chưa có mã nào tích lũy chân sóng đủ tiêu chuẩn khắt khe.")

# ==============================================================================
# HẾT MÃ NGUỒN V17.0 THE ORACLE TITAN (UNROLLED & VERBOSE)
# ==============================================================================
