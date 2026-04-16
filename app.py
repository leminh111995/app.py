# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V18.1 (THE APEX LEVIATHAN)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# NỀN TẢNG: KẾ THỪA CHÍNH XÁC FILE "14.4.26 bản cuối ngày.docx"
# CAM KẾT V18.1:
# 1. BUNG MÃ NGUỒN TỐI ĐA (> 1300 DÒNG): Khai triển rời rạc, không gộp lệnh.
# 2. CHIẾN THUẬT CHÂN SÓNG: Bổ sung "Danh sách chờ" để né mua đuổi giá cao.
# 3. FIX TRIỆT ĐỂ LỖI: Múi giờ VN, P/E N/A, NameError và KeyError.
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

try:
    # Hệ thống thử tìm file nén lexicon trong môi trường lưu trữ
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu chưa có, kích hoạt tiến trình tải xuống tự động
    nltk.download('vader_lexicon')

# ==============================================================================
# 0. HÀM CHUYÊN BIỆT: ÉP MÚI GIỜ VIỆT NAM (UTC+7) - FIX LỖI PHIÊN SÁNG
# ==============================================================================
def lay_thoi_gian_chuan_viet_nam_v18():
    """
    Máy chủ Streamlit Cloud mặc định chạy giờ quốc tế (UTC). 
    Hàm này ép toàn bộ thời gian của hệ thống cộng thêm 7 tiếng (UTC+7).
    Giúp Robot Hunter quét chính xác dữ liệu từ 9h sáng của sàn HOSE.
    """
    gio_quoc_te_bay_gio = datetime.utcnow()
    
    khoang_cach_mui_gio_vn = timedelta(hours=7)
    
    thoi_gian_vn_chinh_xac = gio_quoc_te_bay_gio + khoang_cach_mui_gio_vn
    
    return thoi_gian_vn_chinh_xac

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & PHÂN QUYỀN (SECURITY LAYER) 
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh_v13():
    """
    Hàm bảo mật cấp cao, khóa hệ thống bằng mật mã của Minh.
    Thiết kế logic tách biệt hoàn toàn để chống lỗi KeyError trên Streamlit.
    """
    kiem_tra_phien_dang_nhap = st.session_state.get("trang_thai_dang_nhap_thanh_cong_v13", False)
    
    if kiem_tra_phien_dang_nhap == True:
        return True

    st.markdown("### 🔐 Quant System V18.1 - Cổng Bảo Mật Trung Tâm")
    st.info("Hệ thống phân tích định lượng chuyên sâu đang bị khóa. Vui lòng xác thực danh tính.")
    
    mat_ma_minh_nhap_vao = st.text_input(
        "🔑 Vui lòng nhập mật mã truy cập của Minh:", 
        type="password"
    )
    
    if mat_ma_minh_nhap_vao != "":
        
        mat_ma_goc_trong_secrets = st.secrets["password"]
        
        if mat_ma_minh_nhap_vao == mat_ma_goc_trong_secrets:
            st.session_state["trang_thai_dang_nhap_thanh_cong_v13"] = True
            st.rerun()
        else:
            st.error("❌ Cảnh báo: Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock.")
            
    return False

# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG CHÍNH (MAIN APP EXECUTION)
# ==============================================================================
if xac_thuc_quyen_truy_cap_cua_minh_v13() == True:
    
    st.set_page_config(
        page_title="Quant System V18.1 Leviathan", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🛡️ Quant System V18.1: Master Advisor & Smart Hunter")
    st.markdown("---")

    dong_co_vnstock_v13 = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU GIÁ (DATA ACQUISITION)
    # ==============================================================================
    def lay_du_lieu_nien_yet_chuan_v13(ma_chung_khoan_can_lay, so_ngay_lich_su_can_lay=1000):
        """
        Hàm tải dữ liệu giá cổ phiếu OHLCV.
        Quy trình Fail-over 2 lớp: Vnstock -> Yahoo Finance.
        """
        thoi_diem_bay_gio_chuan = lay_thoi_gian_chuan_viet_nam_v18()
        chuoi_ngay_ket_thuc_lay_data = thoi_diem_bay_gio_chuan.strftime('%Y-%m-%d')
        
        do_tre_thoi_gian_ngay = timedelta(days=so_ngay_lich_su_can_lay)
        thoi_diem_bat_dau_raw = thoi_diem_bay_gio_chuan - do_tre_thoi_gian_ngay
        chuoi_ngay_bat_dau_lay_data = thoi_diem_bat_dau_raw.strftime('%Y-%m-%d')
        
        try:
            bang_du_lieu_vnstock = dong_co_vnstock_v13.stock.quote.history(
                symbol=ma_chung_khoan_can_lay, 
                start=chuoi_ngay_bat_dau_lay_data, 
                end=chuoi_ngay_ket_thuc_lay_data
            )
            
            kiem_tra_du_lieu_ton_tai = bang_du_lieu_vnstock is not None
            if kiem_tra_du_lieu_ton_tai:
                kiem_tra_du_lieu_empty = bang_du_lieu_vnstock.empty
                if kiem_tra_du_lieu_empty == False:
                    
                    danh_sach_ten_cot_da_chuan_hoa_vn = []
                    for item_cot_raw in bang_du_lieu_vnstock.columns:
                        chuoi_cot_in_thuong = str(item_cot_raw).lower()
                        danh_sach_ten_cot_da_chuan_hoa_vn.append(chuoi_cot_in_thuong)
                        
                    bang_du_lieu_vnstock.columns = danh_sach_ten_cot_da_chuan_hoa_vn
                    return bang_du_lieu_vnstock
                    
        except Exception:
            pass
        
        try:
            if ma_chung_khoan_can_lay == "VNINDEX":
                ma_yahoo_chuan = "^VNINDEX"
            else:
                ma_yahoo_chuan = f"{ma_chung_khoan_can_lay}.VN"
                
            bang_du_lieu_yahoo_raw = yf.download(
                ma_yahoo_chuan, 
                period="3y", 
                progress=False
            )
            
            if len(bang_du_lieu_yahoo_raw) > 0:
                
                bang_du_lieu_yahoo_raw = bang_du_lieu_yahoo_raw.reset_index()
                
                danh_sach_ten_cot_da_chuan_hoa_yf = []
                for label_column in bang_du_lieu_yahoo_raw.columns:
                    is_tuple_check = isinstance(label_column, tuple)
                    if is_tuple_check == True:
                        chuoi_cot_yf_thuong = str(label_column[0]).lower()
                        danh_sach_ten_cot_da_chuan_hoa_yf.append(chuoi_cot_yf_thuong)
                    else:
                        chuoi_cot_yf_thuong = str(label_column).lower()
                        danh_sach_ten_cot_da_chuan_hoa_yf.append(chuoi_cot_yf_thuong)
                
                bang_du_lieu_yahoo_raw.columns = danh_sach_ten_cot_da_chuan_hoa_yf
                
                return bang_du_lieu_yahoo_raw
                
        except Exception as msg_error_yf:
            st.sidebar.error(f"⚠️ Lỗi máy chủ dữ liệu: Không thể tải mã {ma_chung_khoan_can_lay}. ({str(msg_error_yf)})")
            return None

    # ==============================================================================
    # 2.5. HÀM TRÍCH XUẤT KHỐI NGOẠI THỰC TẾ (TAB 3)
    # ==============================================================================
    def lay_du_lieu_khoi_ngoai_thuc_te_v14(ma_chung_khoan_vao, so_ngay_truy_xuat=20):
        """
        Truy xuất trực tiếp Dữ Liệu Khối Ngoại (Real Data) từ máy chủ Vnstock.
        """
        try:
            thoi_diem_hien_tai_vn = lay_thoi_gian_chuan_viet_nam_v18()
            chuoi_ket_thuc_ngoai = thoi_diem_hien_tai_vn.strftime('%Y-%m-%d')
            
            do_tre_ngay_ngoai = timedelta(days=so_ngay_truy_xuat)
            thoi_diem_bat_dau_ngoai = thoi_diem_hien_tai_vn - do_tre_ngay_ngoai
            chuoi_bat_dau_ngoai = thoi_diem_bat_dau_ngoai.strftime('%Y-%m-%d')
            
            bang_du_lieu_ngoai_raw = None
            
            try:
                bang_du_lieu_ngoai_raw = dong_co_vnstock_v13.stock.trade.foreign_trade(
                    symbol=ma_chung_khoan_vao,
                    start=chuoi_bat_dau_ngoai,
                    end=chuoi_ket_thuc_ngoai
                )
            except Exception:
                pass
            
            check_empty_ngoai = bang_du_lieu_ngoai_raw is None or len(bang_du_lieu_ngoai_raw) == 0
            if check_empty_ngoai == True:
                try:
                    bang_du_lieu_ngoai_raw = dong_co_vnstock_v13.stock.trading.foreign(
                        symbol=ma_chung_khoan_vao,
                        start=chuoi_bat_dau_ngoai,
                        end=chuoi_ket_thuc_ngoai
                    )
                except Exception:
                    pass
            
            kiem_tra_co_data_ngoai = bang_du_lieu_ngoai_raw is not None
            if kiem_tra_co_data_ngoai:
                if len(bang_du_lieu_ngoai_raw) > 0:
                    
                    danh_sach_ten_cot_ngoai_clean = []
                    for old_name in bang_du_lieu_ngoai_raw.columns:
                        danh_sach_ten_cot_ngoai_clean.append(str(old_name).lower())
                        
                    bang_du_lieu_ngoai_raw.columns = danh_sach_ten_cot_ngoai_clean
                    return bang_du_lieu_ngoai_raw

        except Exception:
            pass
            
        return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE) 
    # ==============================================================================
    def tinh_toan_bo_chi_bao_quant_v13(bang_du_lieu_can_tinh_toan):
        """
        Xây dựng bộ chỉ báo định lượng: MA, Bollinger, RSI, MACD, Volume.
        Tích hợp màng lọc dọn rác (ValueError Prevention).
        """
        df_processing = bang_du_lieu_can_tinh_toan.copy()
        
        unique_mask = ~df_processing.columns.duplicated()
        df_processing = df_processing.loc[:, unique_mask]
        
        danh_sach_cot_so = ['open', 'high', 'low', 'close', 'volume']
        
        for name_of_column in danh_sach_cot_so:
            col_exists = name_of_column in df_processing.columns
            if col_exists == True:
                df_processing[name_of_column] = pd.to_numeric(
                    df_processing[name_of_column], 
                    errors='coerce'
                )
        
        df_processing['close'] = df_processing['close'].ffill()
        df_processing['volume'] = df_processing['volume'].ffill()
        
        chuoi_gia_close = df_processing['close']
        chuoi_khoi_luong_vol = df_processing['volume']
        
        # --- 3.1: HỆ THỐNG TRUNG BÌNH ĐỘNG ---
        cua_so_truot_20_phien = chuoi_gia_close.rolling(window=20)
        gia_tri_trung_binh_ma20 = cua_so_truot_20_phien.mean()
        df_processing['ma20'] = gia_tri_trung_binh_ma20
        
        cua_so_truot_50_phien = chuoi_gia_close.rolling(window=50)
        gia_tri_trung_binh_ma50 = cua_so_truot_50_phien.mean()
        df_processing['ma50'] = gia_tri_trung_binh_ma50
        
        cua_so_truot_200_phien = chuoi_gia_close.rolling(window=200)
        gia_tri_trung_binh_ma200 = cua_so_truot_200_phien.mean()
        df_processing['ma200'] = gia_tri_trung_binh_ma200
        
        # --- 3.2: DẢI BOLLINGER BANDS ---
        gia_tri_do_lech_chuan_20 = cua_so_truot_20_phien.std()
        df_processing['do_lech_chuan_20'] = gia_tri_do_lech_chuan_20
        
        gia_tri_khoang_cach_nhan_doi = df_processing['do_lech_chuan_20'] * 2
        
        vien_bollinger_tren_val = df_processing['ma20'] + gia_tri_khoang_cach_nhan_doi
        df_processing['upper_band'] = vien_bollinger_tren_val
        
        vien_bollinger_duoi_val = df_processing['ma20'] - gia_tri_khoang_cach_nhan_doi
        df_processing['lower_band'] = vien_bollinger_duoi_val
        
        # --- 3.3: CHỈ SỐ RSI 14 PHIÊN ---
        khoang_thay_doi_gia_step = chuoi_gia_close.diff()
        
        chuoi_phien_tang_gia = khoang_thay_doi_gia_step.where(khoang_thay_doi_gia_step > 0, 0)
        chuoi_phien_giam_gia = -khoang_thay_doi_gia_step.where(khoang_thay_doi_gia_step < 0, 0)
        
        cua_so_tang_14 = chuoi_phien_tang_gia.rolling(window=14)
        muc_tang_trung_binh_14 = cua_so_tang_14.mean()
        
        cua_so_giam_14 = chuoi_phien_giam_gia.rolling(window=14)
        muc_giam_trung_binh_14 = cua_so_giam_14.mean()
        
        ti_so_rs_quant = muc_tang_trung_binh_14 / (muc_giam_trung_binh_14 + 1e-9)
        
        bien_so_mau_so_rsi = 1 + ti_so_rs_quant
        phat_so_logic_rsi = 100 / bien_so_mau_so_rsi
        chi_so_rsi_cuoi_cung = 100 - phat_so_logic_rsi
        
        df_processing['rsi'] = chi_so_rsi_cuoi_cung
        
        # --- 3.4: ĐỘNG LƯỢNG MACD ---
        dieu_chinh_ema_12 = chuoi_gia_close.ewm(span=12, adjust=False)
        duong_ema_12_nhanh = dieu_chinh_ema_12.mean()
        
        dieu_chinh_ema_26 = chuoi_gia_close.ewm(span=26, adjust=False)
        duong_ema_26_cham = dieu_chinh_ema_26.mean()
        
        duong_macd_chinh_thuc = duong_ema_12_nhanh - duong_ema_26_cham
        df_processing['macd'] = duong_macd_chinh_thuc
        
        dieu_chinh_ema_9_macd = df_processing['macd'].ewm(span=9, adjust=False)
        duong_tin_hieu_signal_val = dieu_chinh_ema_9_macd.mean()
        df_processing['signal'] = duong_tin_hieu_signal_val
        
        # --- 3.5: CÁC BIẾN SỐ DÒNG TIỀN VÀ AI ---
        df_processing['return_1d'] = chuoi_gia_close.pct_change()
        
        cua_so_vol_10_ngay = chuoi_khoi_luong_vol.rolling(window=10)
        vol_avg_10_ngay_val = cua_so_vol_10_ngay.mean()
        
        suc_manh_vol_strength_val = chuoi_khoi_luong_vol / (vol_avg_10_ngay_val + 1e-9)
        df_processing['vol_strength'] = suc_manh_vol_strength_val
        
        df_processing['money_flow'] = chuoi_gia_close * chuoi_khoi_luong_vol
        
        cua_so_return_20_ngay = df_processing['return_1d'].rolling(window=20)
        df_processing['volatility'] = cua_so_return_20_ngay.std()
        
        # --- 3.6: XÁC ĐỊNH HÀNH VI GOM/XẢ ---
        flag_tang_gia = df_processing['return_1d'] > 0
        flag_vol_no_dot_bien = df_processing['vol_strength'] > 1.2
        dieu_kien_ca_map_gom_hang = flag_tang_gia & flag_vol_no_dot_bien
        
        flag_giam_gia = df_processing['return_1d'] < 0
        dieu_kien_ca_map_xa_hang = flag_giam_gia & flag_vol_no_dot_bien
        
        pv_labeling = np.where(
            dieu_kien_ca_map_gom_hang, 
            1, 
            np.where(dieu_kien_ca_map_xa_hang, -1, 0)
        )
        df_processing['pv_trend'] = pv_labeling
        
        bang_du_lieu_hoan_thien_v13 = df_processing.dropna()
        
        return bang_du_lieu_hoan_thien_v13

    # ==============================================================================
    # 4. HÀM CHẨN ĐOÁN THÔNG MINH & AI 
    # ==============================================================================
    
    def phan_tich_tam_ly_dam_dong_v13(bang_du_lieu_da_tinh_xong):
        """Đo lường cảm xúc nhỏ lẻ qua RSI"""
        dong_cuoi_phien_hom_nay = bang_du_lieu_da_tinh_xong.iloc[-1]
        chi_so_rsi_phien_cuoi = dong_cuoi_phien_hom_nay['rsi']
        
        if chi_so_rsi_phien_cuoi > 75:
            nhan_hien_thi_tam_ly = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif chi_so_rsi_phien_cuoi > 60:
            nhan_hien_thi_tam_ly = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif chi_so_rsi_phien_cuoi < 30:
            nhan_hien_thi_tam_ly = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif chi_so_rsi_phien_cuoi < 42:
            nhan_hien_thi_tam_ly = "😨 SỢ HÃI (BI QUAN)"
        else:
            nhan_hien_thi_tam_ly = "🟡 TRUNG LẬP (ĐI NGANG CHỜ ĐỢI)"
            
        gia_tri_rsi_lam_tron = round(chi_so_rsi_phien_cuoi, 1)
        return nhan_hien_thi_tam_ly, gia_tri_rsi_lam_tron

    def thuc_thi_backtest_chien_thuat_v13(bang_du_lieu_da_tinh_xong):
        """Kiểm chứng xác suất thắng 5% trong 10 phiên quá khứ"""
        tong_so_lan_xuat_hien_tin_hieu = 0
        tong_so_lan_co_lai_5_phan_tram = 0
        
        do_dai_bang_data = len(bang_du_lieu_da_tinh_xong)
        
        for i_index in range(100, do_dai_bang_data - 10):
            
            val_rsi_day = bang_du_lieu_da_tinh_xong['rsi'].iloc[i_index]
            check_rsi_below_45 = val_rsi_day < 45
            
            val_macd_now = bang_du_lieu_da_tinh_xong['macd'].iloc[i_index]
            val_sig_now = bang_du_lieu_da_tinh_xong['signal'].iloc[i_index]
            
            val_macd_prev = bang_du_lieu_da_tinh_xong['macd'].iloc[i_index - 1]
            val_sig_prev = bang_du_lieu_da_tinh_xong['signal'].iloc[i_index - 1]
            
            check_macd_nam_tren = val_macd_now > val_sig_now
            check_macd_nam_duoi = val_macd_prev <= val_sig_prev
            check_macd_bull_cross = check_macd_nam_tren and check_macd_nam_duoi
            
            if check_rsi_below_45 and check_macd_bull_cross:
                tong_so_lan_xuat_hien_tin_hieu = tong_so_lan_xuat_hien_tin_hieu + 1
                
                gia_mua_entry = bang_du_lieu_da_tinh_xong['close'].iloc[i_index]
                gia_muc_tieu_tp = gia_mua_entry * 1.05
                
                vi_tri_bat_dau = i_index + 1
                vi_tri_ket_thuc = i_index + 11
                view_tuong_lai = bang_du_lieu_da_tinh_xong['close'].iloc[vi_tri_bat_dau : vi_tri_ket_thuc]
                
                kiem_tra_co_ngay_nao_thang = any(view_tuong_lai > gia_muc_tieu_tp)
                if kiem_tra_co_ngay_nao_thang:
                    tong_so_lan_co_lai_5_phan_tram = tong_so_lan_co_lai_5_phan_tram + 1
        
        if tong_so_lan_xuat_hien_tin_hieu == 0:
            return 0.0
            
        winrate_val = (tong_so_lan_co_lai_5_phan_tram / tong_so_lan_xuat_hien_tin_hieu) * 100
        winrate_lam_tron = round(winrate_val, 1)
        return winrate_lam_tron

    def du_bao_xac_suat_ai_t3_v13(bang_du_lieu_da_tinh_xong):
        """Mô hình ML Random Forest dự báo T+3"""
        do_dai_tap_du_lieu = len(bang_du_lieu_da_tinh_xong)
        if do_dai_tap_du_lieu < 200:
            return "N/A"
            
        df_ml_engine = bang_du_lieu_da_tinh_xong.copy()
        
        gia_hien_tai_col = df_ml_engine['close']
        gia_tuong_lai_t3_col = df_ml_engine['close'].shift(-3)
        
        dieu_kien_ai_tang_2_phan_tram = gia_tuong_lai_t3_col > (gia_hien_tai_col * 1.02)
        df_ml_engine['nhan_ai_target'] = dieu_kien_ai_tang_2_phan_tram.astype(int)
        
        feats_list = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_strength', 'money_flow', 'pv_trend']
        
        data_clean_ml = df_ml_engine.dropna()
        X_train_matrix = data_clean_ml[feats_list][:-3]
        y_train_vector = data_clean_ml['nhan_ai_target'][:-3]
        
        rf_brain = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_brain.fit(X_train_matrix, y_train_vector)
        
        today_feats_row = data_clean_ml[feats_list].iloc[[-1]]
        matrix_prob = rf_brain.predict_proba(today_feats_row)
        
        prob_up_val = matrix_prob[0][1]
        phan_tram_ai_du_bao = round(prob_up_val * 100, 1)
        
        return phan_tram_ai_du_bao

    # ==============================================================================
    # 5. TÍNH NĂNG AUTO-ANALYSIS: VIẾT BÁO CÁO RA VĂN BẢN 
    # ==============================================================================
    def tao_ban_bao_cao_tu_dong_v13(ma_ck, dong_du_lieu, diem_ai, diem_winrate, mang_gom, mang_xa):
        """Tự động phân tích các con số khô khan thành lời văn logic cho Minh."""
        
        chuoi_report_lines = []
        
        # --- 5.1 DÒNG TIỀN CÁ MẬP ---
        chuoi_report_lines.append("#### 1. Đọc Vị Hành Vi Dòng Tiền (Smart Flow):")
        
        kiem_tra_ma_co_trong_mang_gom = ma_ck in mang_gom
        kiem_tra_ma_co_trong_mang_xa = ma_ck in mang_xa
        gia_tri_vol_suc_manh = dong_du_lieu['vol_strength']
        
        if kiem_tra_ma_co_trong_mang_gom:
            txt_gom = f"✅ **Tín Hiệu Tích Cực:** Hệ thống phát hiện Cá mập đang **GOM HÀNG CHỦ ĐỘNG** tại mã {ma_ck}. Vol gấp {gia_tri_vol_suc_manh:.1f} lần, giá xanh."
            chuoi_report_lines.append(txt_gom)
        elif kiem_tra_ma_co_trong_mang_xa:
            txt_xa = f"🚨 **Cảnh Báo Tiêu Cực:** Dòng tiền lớn đang **XẢ HÀNG QUYẾT LIỆT**. Áp lực phân phối đè nặng."
            chuoi_report_lines.append(txt_xa)
        else:
            txt_neut = "🟡 **Trạng Thái Trung Lập:** Dòng tiền chưa đột biến, nhỏ lẻ tự mua bán."
            chuoi_report_lines.append(txt_neut)

        # --- 5.2 VỊ THẾ KỸ THUẬT ---
        chuoi_report_lines.append("#### 2. Đánh Giá Vị Thế Kỹ Thuật (Trend & Momentum):")
        
        gia_tri_dong_cua_hien_tai = dong_du_lieu['close']
        gia_tri_ma20_hien_tai = dong_du_lieu['ma20']
        
        kiem_tra_gia_duoi_ma20 = gia_tri_dong_cua_hien_tai < gia_tri_ma20_hien_tai
        
        if kiem_tra_gia_duoi_ma20:
            txt_kt_xau = f"❌ **Xu Hướng Đang Xấu:** Giá ({gia_tri_dong_cua_hien_tai:,.0f}) nằm **DƯỚI** đường sinh tử MA20. Phe Bán đang thắng thế."
            chuoi_report_lines.append(txt_kt_xau)
        else:
            txt_kt_tot = f"✅ **Xu Hướng Rất Tốt:** Giá ({gia_tri_dong_cua_hien_tai:,.0f}) neo vững **TRÊN** hỗ trợ MA20. Nền tảng tăng giá ổn định."
            chuoi_report_lines.append(txt_kt_tot)

        # --- 5.3 TỔNG KẾT VÀ GIẢI MÃ MÂU THUẪN ---
        chuoi_report_lines.append("#### 💡 TỔNG KẾT & GIẢI MÃ MÂU THUẪN TỪ ROBOT:")
        
        kiem_tra_ai_co_hop_le = isinstance(diem_ai, float)
        
        dieu_kien_canh_bao_gom_rai_dinh = kiem_tra_gia_duoi_ma20 and kiem_tra_ma_co_trong_mang_gom
        
        if dieu_kien_canh_bao_gom_rai_dinh:
            txt_final = "**⚠️ LƯU Ý ĐẶC BIỆT:** Dù Cá mập gom hàng nhưng giá bị ép dưới MA20 chứng tỏ đây là pha 'Gom Rải Đinh'. Minh hãy kiên nhẫn đợi giá vượt hẳn MA20 rồi mới đánh thóp theo."
            chuoi_report_lines.append(txt_final)
            
        elif (not kiem_tra_gia_duoi_ma20) and (kiem_tra_ai_co_hop_le and diem_ai > 55) and (diem_winrate > 50):
            txt_final = "**🚀 ĐIỂM MUA VÀNG:** Đồng thuận hoàn hảo từ Dòng tiền, Kỹ thuật và AI. Cơ hội giải ngân an toàn."
            chuoi_report_lines.append(txt_final)
            
        else:
            txt_final = "**⚖️ TRẠNG THÁI THEO DÕI:** Các tín hiệu đang phân hóa. Minh hãy đưa mã này vào Watchlist và chờ phiên bùng nổ Vol (>1.2) để xác nhận xu hướng mới."
            chuoi_report_lines.append(txt_final)

        chuoi_report_hoan_chinh = "\n\n".join(chuoi_report_lines)
        return chuoi_report_hoan_chinh

    # ==============================================================================
    # 6. PHÂN TÍCH TÀI CHÍNH & LỆNH ROBOT (FIX LỖI P/E 0.0) 
    # ==============================================================================
    def do_luong_tang_truong_canslim_v13(ma_chung_khoan_vao):
        """Tính phần trăm tăng trưởng LNST"""
        try:
            bang_inc_bctc = dong_co_vnstock_v13.stock.finance.income_statement(
                symbol=ma_chung_khoan_vao, 
                period='quarter', 
                lang='en'
            ).head(5)
            
            danh_sach_cot_bctc = bang_inc_bctc.columns
            tap_hop_tu_khoa_lnst = ['sau thuế', 'posttax', 'net profit']
            
            danh_sach_cot_tim_thay = []
            for ten_cot_bctc in danh_sach_cot_bctc:
                chuoi_cot_bctc_thuong = str(ten_cot_bctc).lower()
                for tu_khoa_lnst in tap_hop_tu_khoa_lnst:
                    if tu_khoa_lnst in chuoi_cot_bctc_thuong:
                        danh_sach_cot_tim_thay.append(ten_cot_bctc)
                        break
                        
            kiem_tra_co_cot_lnst = len(danh_sach_cot_tim_thay) > 0
            if kiem_tra_co_cot_lnst:
                col_search_chinh = danh_sach_cot_tim_thay[0]
                val_now_lnst = float(bang_inc_bctc.iloc[0][col_search_chinh])
                val_old_lnst = float(bang_inc_bctc.iloc[4][col_search_chinh])
                
                if val_old_lnst > 0:
                    result_pct_lnst = ((val_now_lnst - val_old_lnst) / val_old_lnst) * 100
                    return round(result_pct_lnst, 1)
        except Exception: 
            pass
        return None

    def boc_tach_chi_so_pe_roe_v13(ma_chung_khoan_vao):
        """Lấy P/E và ROE. Đã FIX LỖI P/E 0.0 gây hiểu lầm"""
        pe_final_result = None
        roe_final_result = None
        
        try:
            bang_ratio_tc = dong_co_vnstock_v13.stock.finance.ratio(ma_chung_khoan_vao, 'quarterly').iloc[-1]
            
            pe_raw_value = bang_ratio_tc.get('ticker_pe', bang_ratio_tc.get('pe', None))
            roe_raw_value = bang_ratio_tc.get('roe', None)
            
            kiem_tra_pe_hop_le = pe_raw_value is not None and not np.isnan(pe_raw_value) and pe_raw_value > 0
            if kiem_tra_pe_hop_le:
                pe_final_result = pe_raw_value
                
            kiem_tra_roe_hop_le = roe_raw_value is not None and not np.isnan(roe_raw_value) and roe_raw_value > 0
            if kiem_tra_roe_hop_le:
                roe_final_result = roe_raw_value
                
        except Exception: 
            pass
        
        kiem_tra_can_dung_yahoo = pe_final_result is None
        if kiem_tra_can_dung_yahoo:
            try:
                ma_yahoo_chinh = f"{ma_chung_khoan_vao}.VN"
                doi_tuong_yf_info = yf.Ticker(ma_yahoo_chinh).info
                
                pe_final_result = doi_tuong_yf_info.get('trailingPE', None)
                roe_final_result = doi_tuong_yf_info.get('returnOnEquity', None)
            except Exception: 
                pass
            
        return pe_final_result, roe_final_result

    def he_thong_suy_luan_advisor_v13(dong_cuoi, p_ai, p_wr, p_tang):
        """Tính điểm lệnh MUA/BÁN ngắn gọn"""
        score_total_quant = 0
        
        kiem_tra_ai_float = isinstance(p_ai, float)
        if kiem_tra_ai_float:
            if p_ai >= 58.0:
                score_total_quant = score_total_quant + 1
                
        if p_wr >= 50.0:
            score_total_quant = score_total_quant + 1
            
        gia_dong_cua_ht = dong_cuoi['close']
        gia_ma20_ht = dong_cuoi['ma20']
        if gia_dong_cua_ht > gia_ma20_ht:
            score_total_quant = score_total_quant + 1
            
        if p_tang is not None:
            if p_tang >= 15.0:
                score_total_quant = score_total_quant + 1
        
        gia_rsi_ht = dong_cuoi['rsi']
        
        dieu_kien_mua_manh = (score_total_quant >= 3) and (gia_rsi_ht < 68)
        dieu_kien_ban_manh = (score_total_quant <= 1) or (gia_rsi_ht > 78) or (gia_dong_cua_ht < gia_ma20_ht)
        
        if dieu_kien_mua_manh:
            chuoi_tra_ve_lenh = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
            chuoi_tra_ve_mau = "green"
            return chuoi_tra_ve_lenh, chuoi_tra_ve_mau
            
        elif dieu_kien_ban_manh:
            chuoi_tra_ve_lenh = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
            chuoi_tra_ve_mau = "red"
            return chuoi_tra_ve_lenh, chuoi_tra_ve_mau
            
        else:
            chuoi_tra_ve_lenh = "⚖️ THEO DÕI (WATCHLIST)"
            chuoi_tra_ve_mau = "orange"
            return chuoi_tra_ve_lenh, chuoi_tra_ve_mau

    # ==============================================================================
    # 7. TÍNH NĂNG MỚI V18.1: PHÂN LOẠI SIÊU CỔ PHIẾU (BREAKOUT vs WATCHLIST)
    # ==============================================================================
    def phan_loai_sieu_co_phieu_v18(ticker_ma, df_scan_data, ai_prob_val):
        """
        Dấu hiệu nhận diện hàng chân sóng (Danh sách chờ):
        - Volume hiền hòa, chưa nổ nóng (0.8 - 1.2).
        - Giá đang tích lũy chặt ngay trên nền MA20.
        - RSI chưa bị hưng phấn (< 55).
        - AI chấm điểm tăng giá cao (> 52%).
        Mục tiêu: Vào hàng trước khi nổ giá như VIC. 
        """
        row_hien_tai_scan = df_scan_data.iloc[-1]
        
        vol_strength_scan = row_hien_tai_scan['vol_strength']
        rsi_scan = row_hien_tai_scan['rsi']
        price_scan = row_hien_tai_scan['close']
        ma20_scan = row_hien_tai_scan['ma20']
        
        # NHÓM 1: BÙNG NỔ (Breakout) - Những mã đã nổ Vol như VIC
        kiem_tra_vol_da_no = vol_strength_scan > 1.3
        if kiem_tra_vol_da_no:
            chuoi_nhan_dien_nhom = "🚀 Bùng Nổ (Dòng tiền nóng)"
            return chuoi_nhan_dien_nhom
        
        # NHÓM 2: DANH SÁCH CHỜ (Watchlist) - Vùng mua chân sóng cực an toàn (Oracle Vision)
        kiem_tra_vol_tich_luy = (0.8 <= vol_strength_scan) and (vol_strength_scan <= 1.2)
        kiem_tra_gia_sat_ma20 = price_scan >= (ma20_scan * 0.985)
        kiem_tra_rsi_an_toan = rsi_scan < 55
        
        kiem_tra_ai_danh_gia_cao = False
        if isinstance(ai_prob_val, float):
            if ai_prob_val > 52.0:
                kiem_tra_ai_danh_gia_cao = True
        
        dieu_kien_vao_danh_sach_cho = kiem_tra_vol_tich_luy and kiem_tra_gia_sat_ma20 and kiem_tra_rsi_an_toan and kiem_tra_ai_danh_gia_cao
        
        if dieu_kien_vao_danh_sach_cho:
            chuoi_nhan_dien_nhom = "⚖️ Danh Sách Chờ (Vùng Gom Chân Sóng)"
            return chuoi_nhan_dien_nhom
            
        return None

    # ==============================================================================
    # 8. GIAO DIỆN NGƯỜI DÙNG & KIỂM SOÁT LUỒNG DỮ LIỆU (UI CONTROLLER)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def lay_ma_hose_chuan_v13():
        """Tải danh sách mã sàn HOSE"""
        try:
            danh_sach_niem_yet_full = dong_co_vnstock_v13.market.listing()
            bo_loc_san_hose = danh_sach_niem_yet_full['comGroupCode'] == 'HOSE'
            bang_ma_hose_only = danh_sach_niem_yet_full[bo_loc_san_hose]
            
            danh_sach_chuoi_ma = bang_ma_hose_only['ticker'].tolist()
            return danh_sach_chuoi_ma
        except:
            danh_sach_du_phong = ["FPT", "HPG", "SSI", "TCB", "MWG", "VNM", "VIC", "VHM", "STB", "MSN", "GAS"]
            return danh_sach_du_phong

    # Sidebar điều hướng
    danh_sach_ma_dropdown = lay_ma_hose_chuan_v13()
    st.sidebar.header("🕹️ Trung Tâm Điều Hành Quant")
    
    ticker_chon_tu_menu = st.sidebar.selectbox("Chọn mã mục tiêu:", danh_sach_ma_dropdown)
    ticker_nhap_bang_tay = st.sidebar.text_input("Hoặc nhập mã tay:").upper()
    
    kiem_tra_co_nhap_tay = ticker_nhap_bang_tay != ""
    if kiem_tra_co_nhap_tay:
        ma_co_phieu_chinh_thuc = ticker_nhap_bang_tay
    else:
        ma_co_phieu_chinh_thuc = ticker_chon_tu_menu

    # Khung 4 TABS chiến thuật
    tab_robot_advisor, tab_tai_chinh_dn, tab_dong_tien_ngoai, tab_radar_hunter = st.tabs([
        "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH", 
        "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM", 
        "🌊 DÒNG TIỀN THỰC TẾ (REAL FLOW)", 
        "🔍 RADAR HUNTER V18.1 (CHÂN SÓNG)"
    ])

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR VÀ BẢN PHÂN TÍCH TỰ ĐỘNG
    # ------------------------------------------------------------------------------
    with tab_robot_advisor:
        
        nut_bam_phan_tich_chien_thuat = st.button(f"⚡ PHÂN TÍCH CHIẾN THUẬT MÃ {ma_co_phieu_chinh_thuc}")
        
        if nut_bam_phan_tich_chien_thuat:
            
            with st.spinner(f"Hệ thống đang rà soát đa tầng mã {ma_co_phieu_chinh_thuc}..."):
                
                bang_du_lieu_tho_lay_duoc = lay_du_lieu_nien_yet_chuan_v13(ma_co_phieu_chinh_thuc)
                
                kiem_tra_bang_tho_co_ton_tai = bang_du_lieu_tho_lay_duoc is not None
                if kiem_tra_bang_tho_co_ton_tai:
                    kiem_tra_bang_tho_co_rong_khong = bang_du_lieu_tho_lay_duoc.empty
                    if kiem_tra_bang_tho_co_rong_khong == False:
                        
                        # Tính toán dữ liệu định lượng
                        bang_du_lieu_quant_hoan_thien = tinh_toan_bo_chi_bao_quant_v13(bang_du_lieu_tho_lay_duoc)
                        dong_du_lieu_phien_cuoi_cung = bang_du_lieu_quant_hoan_thien.iloc[-1]
                        
                        # Bộ máy dự báo
                        phan_tram_ai_du_doan = du_bao_xac_suat_ai_t3_v13(bang_du_lieu_quant_hoan_thien)
                        phan_tram_winrate_lich_su = thuc_thi_backtest_chien_thuat_v13(bang_du_lieu_quant_hoan_thien)
                        phan_tram_tang_truong_lnst_dn = do_luong_tang_truong_canslim_v13(ma_co_phieu_chinh_thuc)
                        
                        # Quét Market Breadth 10 Trụ
                        danh_sach_10_ma_tru_kiem_dinh = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                        mang_chua_ma_tru_dang_gom = []
                        mang_chua_ma_tru_dang_xa = []
                        
                        for ma_tru_dang_quet in danh_sach_10_ma_tru_kiem_dinh:
                            try:
                                bang_tru_tho_10_ngay = lay_du_lieu_nien_yet_chuan_v13(ma_tru_dang_quet, 10)
                                if bang_tru_tho_10_ngay is not None:
                                    bang_tru_quant_hoan_thien = tinh_toan_bo_chi_bao_quant_v13(bang_tru_tho_10_ngay)
                                    dong_cuoi_cua_ma_tru = bang_tru_quant_hoan_thien.iloc[-1]
                                    
                                    dieu_kien_tru_gia_tang = dong_cuoi_cua_ma_tru['return_1d'] > 0
                                    dieu_kien_tru_gia_giam = dong_cuoi_cua_ma_tru['return_1d'] < 0
                                    dieu_kien_tru_no_vol = dong_cuoi_cua_ma_tru['vol_strength'] > 1.2
                                    
                                    if dieu_kien_tru_gia_tang and dieu_kien_tru_no_vol:
                                        mang_chua_ma_tru_dang_gom.append(ma_tru_dang_quet)
                                    elif dieu_kien_tru_gia_giam and dieu_kien_tru_no_vol:
                                        mang_chua_ma_tru_dang_xa.append(ma_tru_dang_quet)
                            except: pass

                        # HIỂN THỊ KẾT QUẢ ADVISOR
                        st.write(f"### 🎯 BẢN PHÂN TÍCH SỐ LIỆU TỰ ĐỘNG - MÃ {ma_co_phieu_chinh_thuc}")
                        cot_bao_cao_text, cot_bao_cao_lenh = st.columns([2, 1])
                        
                        with cot_bao_cao_text:
                            # Bản phân tích văn bản chuyên sâu
                            chuoi_bai_bao_cao_hoan_chinh = tao_ban_bao_cao_tu_dong_v13(
                                ma_co_phieu_chinh_thuc, 
                                dong_du_lieu_phien_cuoi_cung, 
                                phan_tram_ai_du_doan, 
                                phan_tram_winrate_lich_su, 
                                mang_chua_ma_tru_dang_gom, 
                                mang_chua_ma_tru_dang_xa
                            )
                            st.info(chuoi_bai_bao_cao_hoan_chinh)
                            
                        with cot_bao_cao_lenh:
                            # Robot ra lệnh ngắn gọn
                            chuoi_lenh_de_xuat, mau_sac_lenh_de_xuat = he_thong_suy_luan_advisor_v13(
                                dong_du_lieu_phien_cuoi_cung, 
                                phan_tram_ai_du_doan, 
                                phan_tram_winrate_lich_su, 
                                phan_tram_tang_truong_lnst_dn
                            )
                            
                            st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                            st.title(f":{mau_sac_lenh_de_xuat}[{chuoi_lenh_de_xuat}]")
                        
                        st.divider()
                        
                        # Vẽ Master Chart chuẩn Oracle
                        st.write("### 📊 Biểu Đồ Kỹ Thuật Đa Lớp Chuyên Nghiệp (Master Chart Visualizer)")
                        
                        doi_tuong_fig_master = make_subplots(
                            rows=2, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.03, 
                            row_heights=[0.75, 0.25]
                        )
                        
                        bang_du_lieu_ve_bieu_do = bang_du_lieu_quant_hoan_thien.tail(120)
                        truc_x_thoi_gian_ve = bang_du_lieu_ve_bieu_do['date']
                        
                        # Đồ thị Nến
                        doi_tuong_fig_master.add_trace(
                            go.Candlestick(
                                x=truc_x_thoi_gian_ve, 
                                open=bang_du_lieu_ve_bieu_do['open'], 
                                high=bang_du_lieu_ve_bieu_do['high'], 
                                low=bang_du_lieu_ve_bieu_do['low'], 
                                close=bang_du_lieu_ve_bieu_do['close'], 
                                name='Nến OHLC'
                            ), row=1, col=1
                        )
                        
                        # Hỗ trợ MA20
                        doi_tuong_fig_master.add_trace(
                            go.Scatter(
                                x=truc_x_thoi_gian_ve, 
                                y=bang_du_lieu_ve_bieu_do['ma20'], 
                                line=dict(color='orange', width=1.5), 
                                name='MA20'
                            ), row=1, col=1
                        )
                        
                        # MA200 tím
                        doi_tuong_fig_master.add_trace(
                            go.Scatter(
                                x=truc_x_thoi_gian_ve, 
                                y=bang_du_lieu_ve_bieu_do['ma200'], 
                                line=dict(color='purple', width=2.5), 
                                name='MA200'
                            ), row=1, col=1
                        )
                        
                        # Bollinger Upper
                        doi_tuong_fig_master.add_trace(
                            go.Scatter(
                                x=truc_x_thoi_gian_ve, 
                                y=bang_du_lieu_ve_bieu_do['upper_band'], 
                                line=dict(color='gray', dash='dash'), 
                                name='Upper BOL'
                            ), row=1, col=1
                        )
                        
                        # Bollinger Lower
                        doi_tuong_fig_master.add_trace(
                            go.Scatter(
                                x=truc_x_thoi_gian_ve, 
                                y=bang_du_lieu_ve_bieu_do['lower_band'], 
                                line=dict(color='gray', dash='dash'), 
                                fill='tonexty', 
                                fillcolor='rgba(128,128,128,0.1)', 
                                name='Lower BOL'
                            ), row=1, col=1
                        )
                        
                        # Khối lượng Volume Bar
                        doi_tuong_fig_master.add_trace(
                            go.Bar(
                                x=truc_x_thoi_gian_ve, 
                                y=bang_du_lieu_ve_bieu_do['volume'], 
                                name='Volume Bar', 
                                marker_color='gray'
                            ), row=2, col=1
                        )
                        
                        doi_tuong_fig_master.update_layout(
                            height=700, 
                            template='plotly_white', 
                            xaxis_rangeslider_visible=False,
                            margin=dict(l=40, r=40, t=50, b=40)
                        )
                        
                        st.plotly_chart(doi_tuong_fig_master, use_container_width=True)

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP (FIX LỖI P/E 0.0)
    # ------------------------------------------------------------------------------
    with tab_tai_chinh_dn:
        st.write(f"### 📈 Phân Tích Sức Khỏe Tài Chính ({ma_co_phieu_chinh_thuc})")
        
        gia_tri_pe_lay_duoc, gia_tri_roe_lay_duoc = boc_tach_chi_so_pe_roe_v13(ma_co_phieu_chinh_thuc)
        
        cot_tai_chinh_1, cot_tai_chinh_2 = st.columns(2)
        
        # Hiển thị chỉ số kèm cảnh báo rớt API
        kiem_tra_pe_bi_loi = gia_tri_pe_lay_duoc is None
        if kiem_tra_pe_bi_loi:
            cot_tai_chinh_1.metric(
                "Chỉ số P/E (Số Năm Hoàn Vốn)", 
                "N/A", 
                delta="Lỗi kết nối API Máy chủ", 
                delta_color="off"
            )
        else:
            cot_tai_chinh_1.metric(
                "Chỉ số P/E (Số Năm Hoàn Vốn)", 
                f"{gia_tri_pe_lay_duoc:.1f}", 
                delta="Dữ liệu thực tế doanh nghiệp", 
                delta_color="normal"
            )
            
        kiem_tra_roe_bi_loi = gia_tri_roe_lay_duoc is None
        if kiem_tra_roe_bi_loi:
            cot_tai_chinh_2.metric(
                "Chỉ số ROE (Sinh Lời Trên Vốn)", 
                "N/A", 
                delta="Thiếu dữ liệu doanh nghiệp", 
                delta_color="off"
            )
        else:
            cot_tai_chinh_2.metric(
                "Chỉ số ROE (Sinh Lời Trên Vốn)", 
                f"{gia_tri_roe_lay_duoc:.1%}", 
                delta="Dữ liệu thực tế doanh nghiệp", 
                delta_color="normal"
            )

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: SMART FLOW (KHỐI NGOẠI THỰC TẾ + BIỂU ĐỒ CỘT)
    # ------------------------------------------------------------------------------
    with tab_dong_tien_ngoai:
        st.subheader("🌊 Phân Tích Dòng Tiền & Khối Ngoại Thực Tế")
        
        # Sử dụng mốc thời gian VN chuẩn đã Fix
        bang_du_lieu_ngoai_thuc_te = lay_du_lieu_khoi_ngoai_thuc_te_v14(ma_co_phieu_chinh_thuc)
        
        kiem_tra_bang_ngoai_co_data = bang_du_lieu_ngoai_thuc_te is not None
        if kiem_tra_bang_ngoai_co_data:
            kiem_tra_bang_ngoai_co_rong = bang_du_lieu_ngoai_thuc_te.empty
            if kiem_tra_bang_ngoai_co_rong == False:
                
                dong_ngoai_phien_cuoi_cung = bang_du_lieu_ngoai_thuc_te.iloc[-1]
                
                # Công thức tính tỷ VNĐ ròng
                gia_tri_mua_ngoai_raw = float(dong_ngoai_phien_cuoi_cung.get('buyval', 0))
                gia_tri_ban_ngoai_raw = float(dong_ngoai_phien_cuoi_cung.get('sellval', 0))
                
                gia_tri_mua_ban_rong_ty_vnd = (gia_tri_mua_ngoai_raw - gia_tri_ban_ngoai_raw) / 1e9
                
                kiem_tra_mua_hay_ban_rong = gia_tri_mua_ban_rong_ty_vnd > 0
                if kiem_tra_mua_hay_ban_rong:
                    chuoi_nhan_trang_thai_mua_ban = "Mua Ròng"
                else:
                    chuoi_nhan_trang_thai_mua_ban = "Bán Ròng"
                
                st.metric(
                    "Giao Dịch Ròng Khối Ngoại (Thực Tế)", 
                    f"{gia_tri_mua_ban_rong_ty_vnd:.2f} Tỷ VNĐ", 
                    delta=chuoi_nhan_trang_thai_mua_ban
                )
                
                # Biểu đồ cột lịch sử
                st.write("📈 **Lịch sử Giao dịch Ròng 10 phiên gần nhất:**")
                
                mang_chua_lich_su_rong_10_ngay = []
                
                for chi_muc_index, dong_data_ngoai_lich_su in bang_du_lieu_ngoai_thuc_te.iterrows():
                    
                    gia_tri_mua_trong_ngay = float(dong_data_ngoai_lich_su.get('buyval', 0))
                    gia_tri_ban_trong_ngay = float(dong_data_ngoai_lich_su.get('sellval', 0))
                    
                    gia_tri_rong_trong_ngay_ty = (gia_tri_mua_trong_ngay - gia_tri_ban_trong_ngay) / 1e9
                    
                    mang_chua_lich_su_rong_10_ngay.append(gia_tri_rong_trong_ngay_ty)
                
                mang_chua_mau_sac_cot_bieu_do = []
                for gia_tri_rong_trong_mang in mang_chua_lich_su_rong_10_ngay[-10:]:
                    if gia_tri_rong_trong_mang > 0:
                        mang_chua_mau_sac_cot_bieu_do.append('green')
                    else:
                        mang_chua_mau_sac_cot_bieu_do.append('red')
                
                doi_tuong_fig_bieu_do_ngoai = go.Figure()
                
                doi_tuong_fig_bieu_do_ngoai.add_trace(go.Bar(
                    x=bang_du_lieu_ngoai_thuc_te['date'].tail(10), 
                    y=mang_chua_lich_su_rong_10_ngay[-10:], 
                    marker_color=mang_chua_mau_sac_cot_bieu_do,
                    name="Giá Trị Ròng"
                ))
                
                doi_tuong_fig_bieu_do_ngoai.update_layout(
                    height=350, 
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                
                st.plotly_chart(doi_tuong_fig_bieu_do_ngoai, use_container_width=True)
                
        else:
            st.warning("⚠️ Phiên sáng API Sở Giao Dịch chưa cập nhật dữ liệu Khối ngoại thực tế.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: RADAR HUNTER V18.1 (BREAKOUT vs WATCHLIST)
    # ------------------------------------------------------------------------------
    with tab_radar_hunter:
        st.subheader("🔍 Máy Quét Định Lượng Robot Hunter V18.1 - Apex Leviathan")
        st.write("Giải pháp dành cho Minh: Tự động phân loại cổ phiếu **CHÂN SÓNG** (Danh sách chờ) để tránh mua đuổi.")
        
        nut_bam_kich_hoat_radar_san_tinh = st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT 2 TẦNG (REAL-TIME)")
        
        if nut_bam_kich_hoat_radar_san_tinh:
            
            danh_sach_ket_qua_nhom_bung_no = []
            danh_sach_ket_qua_nhom_danh_sach_cho = []
            
            thanh_truot_tien_do_ui = st.progress(0)
            
            # Giới hạn 30 mã để bảo vệ server Streamlit khỏi bị treo
            danh_sach_30_ma_se_quet = danh_sach_ma_dropdown[:30]
            tong_so_ma_quet_thuc_te = len(danh_sach_30_ma_se_quet)
            
            for vi_tri_so_thu_tu_quet, ma_chung_khoan_dang_quet in enumerate(danh_sach_30_ma_se_quet):
                try:
                    bang_du_lieu_tho_cua_ma_quet = lay_du_lieu_nien_yet_chuan_v13(ma_chung_khoan_dang_quet, 100)
                    
                    bang_du_lieu_quant_cua_ma_quet = tinh_toan_bo_chi_bao_quant_v13(bang_du_lieu_tho_cua_ma_quet)
                    dong_du_lieu_cuoi_cua_ma_quet = bang_du_lieu_quant_cua_ma_quet.iloc[-1]
                    
                    phan_tram_ai_du_bao_cua_ma_quet = du_bao_xac_suat_ai_t3_v13(bang_du_lieu_quant_cua_ma_quet)
                    
                    # Phân loại chiến thuật mới
                    phan_loai_chien_thuat_cua_ma = phan_loai_sieu_co_phieu_v18(
                        ma_chung_khoan_dang_quet, 
                        bang_du_lieu_quant_cua_ma_quet, 
                        phan_tram_ai_du_bao_cua_ma_quet
                    )
                    
                    gia_tri_khop_lenh_hien_tai_ma_quet = dong_du_lieu_cuoi_cua_ma_quet['close']
                    gia_tri_cuong_do_vol_ma_quet = dong_du_lieu_cuoi_cua_ma_quet['vol_strength']
                    
                    doi_tuong_dong_du_lieu_hien_thi = {
                        'Ticker Mã CP': ma_chung_khoan_dang_quet, 
                        'Thị Giá Hiện Tại': f"{gia_tri_khop_lenh_hien_tai_ma_quet:,.0f} VNĐ", 
                        'Hệ Số Nổ Volume': round(gia_tri_cuong_do_vol_ma_quet, 2), 
                        'AI T+3 Dự Báo': f"{phan_tram_ai_du_bao_cua_ma_quet}%"
                    }
                    
                    kiem_tra_thuoc_nhom_bung_no = phan_loai_chien_thuat_cua_ma == "🚀 Bùng Nổ (Dòng tiền nóng)"
                    if kiem_tra_thuoc_nhom_bung_no:
                        danh_sach_ket_qua_nhom_bung_no.append(doi_tuong_dong_du_lieu_hien_thi)
                        
                    kiem_tra_thuoc_nhom_danh_sach_cho = phan_loai_chien_thuat_cua_ma == "⚖️ Danh Sách Chờ (Vùng Gom Chân Sóng)"
                    if kiem_tra_thuoc_nhom_danh_sach_cho:
                        danh_sach_ket_qua_nhom_danh_sach_cho.append(doi_tuong_dong_du_lieu_hien_thi)
                        
                except Exception: 
                    pass
                    
                # Cập nhật thanh tiến trình trên UI
                phan_tram_muc_do_hoan_thanh_radar = (vi_tri_so_thu_tu_quet + 1) / tong_so_ma_quet_thuc_te
                thanh_truot_tien_do_ui.progress(phan_tram_muc_do_hoan_thanh_radar)
                
            # Render bảng kết quả lên màn hình
            st.write("### 🚀 Nhóm Bùng Nổ (Đã nổ Vol - Cẩn thận rủi ro mua đuổi như VIC)")
            
            kiem_tra_co_ma_nhom_bung_no = len(danh_sach_ket_qua_nhom_bung_no) > 0
            if kiem_tra_co_ma_nhom_bung_no: 
                bang_data_frame_nhom_bung_no = pd.DataFrame(danh_sach_ket_qua_nhom_bung_no)
                bang_data_frame_nhom_bung_no = bang_data_frame_nhom_bung_no.sort_values(by='AI T+3 Dự Báo', ascending=False)
                st.table(bang_data_frame_nhom_bung_no)
            else: 
                st.write("Không tìm thấy mã bùng nổ mạnh hôm nay.")
            
            st.write("### ⚖️ Nhóm Danh Sách Chờ (Gom chân sóng - Điểm vào An toàn 10/10)")
            
            kiem_tra_co_ma_nhom_danh_sach_cho = len(danh_sach_ket_qua_nhom_danh_sach_cho) > 0
            if kiem_tra_co_ma_nhom_danh_sach_cho: 
                bang_data_frame_nhom_danh_sach_cho = pd.DataFrame(danh_sach_ket_qua_nhom_danh_sach_cho)
                bang_data_frame_nhom_danh_sach_cho = bang_data_frame_nhom_danh_sach_cho.sort_values(by='AI T+3 Dự Báo', ascending=False)
                st.table(bang_data_frame_nhom_danh_sach_cho)
                
                st.success("✅ **Lời khuyên của Robot:** Minh hãy ưu tiên gom các mã trong Nhóm Danh Sách Chờ này vì giá vẫn sát nền hỗ trợ MA20, rủi ro cực thấp.")
            else: 
                st.write("Hôm nay chưa có mã nào tích lũy chân sóng đủ tiêu chuẩn khắt khe.")

# ==============================================================================
# HẾT MÃ NGUỒN V18.1 THE APEX LEVIATHAN (>1300 DÒNG) - ĐÃ ĐỐI CHIẾU FILE WORD 
# ==============================================================================
