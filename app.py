# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V20.0 (THE PREDATOR LEVIATHAN)
# ==============================================================================
# PHẦN 1/3: THƯ VIỆN, CẤU HÌNH CHIẾN THUẬT, BẢO MẬT VÀ DỮ LIỆU
# CAM KẾT: Không viết tắt, không nén code, sạch bóng hậu tố v13/v14.
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

# Ngưỡng xác suất dự báo tăng giá từ trí tuệ nhân tạo (AI)
THAM_SO_AI_PREDATOR = 48.0

# Giới hạn chỉ số sức mạnh tương đối (RSI) để đảm bảo an toàn
THAM_SO_RSI_AN_TOAN = 62.0

# Vùng giá an toàn cho phép dao động quanh đường MA20 (5%)
THAM_SO_VUNG_GIA_MA20 = 0.05

# Hệ số khối lượng (Volume) tích lũy
THAM_SO_VOL_MIN = 0.6
THAM_SO_VOL_MAX = 1.4

# Độ nén lò xo Bollinger Bands (Squeeze)
THAM_SO_SQUEEZE = 1.2

# Ngưỡng xác định cạn kiệt lực bán (Supply Exhaustion)
THAM_SO_CAN_CUNG = 0.8

# Phạm vi rà soát dòng tiền tổ chức (Số phiên giao dịch gần nhất)
THAM_SO_PHIEN_CHECK_DONG_TIEN = 5

# ------------------------------------------------------------------------------
# 1. KHỞI TẠO TÀI NGUYÊN HỆ THỐNG & ĐỒNG BỘ THỜI GIAN
# ------------------------------------------------------------------------------

# Đảm bảo các tài nguyên AI luôn sẵn sàng trên máy chủ Cloud
try:
    chuoi_kiem_tra_nltk = 'sentiment/vader_lexicon.zip'
    nltk.data.find(chuoi_kiem_tra_nltk)
except LookupError:
    ten_tai_nguyen_nltk = 'vader_lexicon'
    nltk.download(ten_tai_nguyen_nltk)

def lay_thoi_gian_chuan_viet_nam():
    """
    Ép múi giờ hệ thống về Việt Nam (UTC+7) để chống rỗng dữ liệu phiên sáng.
    """
    thoi_gian_quoc_te_raw = datetime.utcnow()
    khoang_cach_mui_gio_vn = timedelta(hours=7)
    thoi_gian_hien_tai_tai_vn = thoi_gian_quoc_te_raw + khoang_cach_mui_gio_vn
    return thoi_gian_hien_tai_tai_vn

# ==============================================================================
# 2. HỆ THỐNG BẢO MẬT TRUNG TÂM (SECURITY LAYER)
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh():
    """
    Cổng bảo mật cấp cao khóa hệ thống bằng mật mã định danh.
    Đã gọt rửa sạch hậu tố _v13 rườm rà.
    """
    chuoi_key_phien_dang_nhap = "trang_thai_xac_thuc_master_predator"
    kiem_tra_phien_dang_nhap = st.session_state.get(chuoi_key_phien_dang_nhap, False)
    
    if kiem_tra_phien_dang_nhap == True:
        return True

    st.markdown("### 🔐 Quant System V20.0 - Cổng Bảo Mật Predator")
    chuoi_info_bao_mat = "Chào Minh, hệ thống Predator Leviathan đang bị khóa. Vui lòng xác thực danh tính."
    st.info(chuoi_info_bao_mat)
    
    chuoi_label_mat_ma = "🔑 Nhập mật mã truy cập của bạn:"
    mat_ma_nguoi_dung_vua_nhap = st.text_input(chuoi_label_mat_ma, type="password")
    
    co_du_lieu_nhap_vao = mat_ma_nguoi_dung_vua_nhap != ""
    
    if co_du_lieu_nhap_vao == True:
        mat_ma_chuan_he_thong = st.secrets["password"]
        kiem_tra_khop_mat_ma = mat_ma_nguoi_dung_vua_nhap == mat_ma_chuan_he_thong
        
        if kiem_tra_khop_mat_ma == True:
            st.session_state[chuoi_key_phien_dang_nhap] = True
            st.rerun()
        else:
            chuoi_error_mat_ma = "❌ Mật mã không hợp lệ. Minh vui lòng kiểm tra lại phím Caps Lock."
            st.error(chuoi_error_mat_ma)
            
    return False

# Khởi tạo đối tượng động cơ Vnstock toàn cục
dong_co_vnstock = Vnstock()

# ==============================================================================
# 3. MODULE TRUY XUẤT DỮ LIỆU ĐA TẦNG (DATA ACQUISITION)
# ==============================================================================
def lay_du_lieu_gia_niem_yet_chuan(ma_chung_khoan, so_ngay_lich_su=1000):
    """
    Tải dữ liệu giá OHLCV với cơ chế dự phòng 2 lớp.
    Đã xóa sạch hậu tố _v13.
    """
    thoi_diem_bay_gio = lay_thoi_gian_chuan_viet_nam()
    chuoi_dinh_dang_date = '%Y-%m-%d'
    
    chuoi_ngay_ket_thuc_format = thoi_diem_bay_gio.strftime(chuoi_dinh_dang_date)
    khoang_lui_ngay = timedelta(days=so_ngay_lich_su)
    thoi_diem_bat_dau_raw = thoi_diem_bay_gio - khoang_lui_ngay
    chuoi_ngay_bat_dau_format = thoi_diem_bat_dau_raw.strftime(chuoi_dinh_dang_date)
    
    # LỚP DỮ LIỆU 1 (API VNSTOCK - DỮ LIỆU NỘI ĐỊA)
    try:
        bang_du_lieu_vnstock = dong_co_vnstock.stock.quote.history(
            symbol=ma_chung_khoan, 
            start=chuoi_ngay_bat_dau_format, 
            end=chuoi_ngay_ket_thuc_format
        )
        
        kiem_tra_bang_ton_tai = bang_du_lieu_vnstock is not None
        
        if kiem_tra_bang_ton_tai == True:
            so_luong_dong_du_lieu = len(bang_du_lieu_vnstock)
            kiem_tra_bang_co_chua_du_lieu = so_luong_dong_du_lieu > 0
            
            if kiem_tra_bang_co_chua_du_lieu == True:
                danh_sach_ten_cot_chuan_hoa = []
                for item_ten_cot in bang_du_lieu_vnstock.columns:
                    chuoi_cot_thuong = str(item_ten_cot).lower()
                    danh_sach_ten_cot_chuan_hoa.append(chuoi_cot_thuong)
                    
                bang_du_lieu_vnstock.columns = danh_sach_ten_cot_chuan_hoa
                return bang_du_lieu_vnstock
    except Exception:
        pass
    
    # LỚP DỮ LIỆU 2 (API YAHOO FINANCE - DỮ LIỆU QUỐC TẾ)
    try:
        kiem_tra_la_vnindex = ma_chung_khoan == "VNINDEX"
        
        if kiem_tra_la_vnindex == True:
            ma_chuan_yahoo = "^VNINDEX"
        else:
            ma_chuan_yahoo = f"{ma_chung_khoan}.VN"
            
        bang_du_lieu_yahoo_raw = yf.download(
            ma_chuan_yahoo, 
            period="3y", 
            progress=False
        )
        
        do_dai_bang_yahoo = len(bang_du_lieu_yahoo_raw)
        kiem_tra_yahoo_co_du_lieu = do_dai_bang_yahoo > 0
        
        if kiem_tra_yahoo_co_du_lieu == True:
            bang_du_lieu_yahoo_da_reset = bang_du_lieu_yahoo_raw.reset_index()
            danh_sach_ten_cot_sach = []
            
            for label_obj in bang_du_lieu_yahoo_da_reset.columns:
                kiem_tra_obj_la_tuple = isinstance(label_obj, tuple)
                if kiem_tra_obj_la_tuple == True:
                    gia_tri_phan_tu_dau = label_obj[0]
                    chuoi_ten_cot_yf = str(gia_tri_phan_tu_dau).lower()
                    danh_sach_ten_cot_sach.append(chuoi_ten_cot_yf)
                else:
                    chuoi_ten_cot_yf = str(label_obj).lower()
                    danh_sach_ten_cot_sach.append(chuoi_ten_cot_yf)
            
            bang_du_lieu_yahoo_da_reset.columns = danh_sach_ten_cot_sach
            return bang_du_lieu_yahoo_da_reset
            
    except Exception as doi_tuong_loi_data:
        chuoi_loi_log = f"⚠️ Cảnh báo: Không thể kết nối máy chủ dữ liệu cho mã {ma_chung_khoan}."
        st.sidebar.error(chuoi_loi_log)
        return None

def lay_du_lieu_dong_tien_to_chuc_chuyen_sau(ma_ck, so_ngay_truy_xuat=20):
    """
    Bóc tách dòng tiền Khối Ngoại và Tự Doanh thực tế.
    Đã xóa sạch hậu tố _v14.
    """
    try:
        thoi_diem_ht = lay_thoi_gian_chuan_viet_nam()
        chuoi_ngay_ht = thoi_diem_ht.strftime('%Y-%m-%d')
        khoang_lui_thoi_gian = timedelta(days=so_ngay_truy_xuat)
        thoi_diem_bat_dau_quet = thoi_diem_ht - khoang_lui_thoi_gian
        chuoi_ngay_bat_dau_quet = thoi_diem_bat_dau_quet.strftime('%Y-%m-%d')
        
        # TRUY XUẤT KHỐI NGOẠI
        df_foreign_kq = None
        try:
            df_foreign_kq = dong_co_vnstock.stock.trade.foreign_trade(
                symbol=ma_ck, start=chuoi_ngay_bat_dau_quet, end=chuoi_ngay_ht)
        except:
            try:
                df_foreign_kq = dong_co_vnstock.stock.trading.foreign(
                    symbol=ma_ck, start=chuoi_ngay_bat_dau_quet, end=chuoi_ngay_ht)
            except: pass
        
        # TRUY XUẤT TỰ DOANH
        df_proprietary_kq = None
        try:
            df_proprietary_kq = dong_co_vnstock.stock.trade.proprietary_trade(
                symbol=ma_ck, start=chuoi_ngay_bat_dau_quet, end=chuoi_ngay_ht)
        except:
            pass
        
        # CHUẨN HÓA CỘT DỮ LIỆU TRẢ VỀ
        if df_foreign_kq is not None and not df_foreign_kq.empty:
            df_foreign_kq.columns = [str(c).lower() for c in df_foreign_kq.columns]
        
        if df_proprietary_kq is not None and not df_proprietary_kq.empty:
            df_proprietary_kq.columns = [str(c).lower() for c in df_proprietary_kq.columns]
            
        return df_foreign_kq, df_proprietary_kq

    except Exception:
        pass
    return None, None

# ==============================================================================
# HẾT PHẦN 1. MINH HÃY DÁN VÀO FILE VÀ GÕ "PHẦN 2" NHÉ!
# ==============================================================================
# ==============================================================================
# PHẦN 2/3: BỘ NÃO LƯỢNG TỬ (QUANT ENGINE) VÀ TRÍ TUỆ NHÂN TẠO (AI)
# MINH HÃY DÁN NỐI TIẾP NGAY BÊN DƯỚI PHẦN 1
# ==============================================================================

# ==============================================================================
# 4. MODULE TÍNH TOÁN CHỈ BÁO ĐỊNH LƯỢNG (QUANT ENGINE)
# ==============================================================================
def tinh_toan_bo_chi_bao_ky_thuat_predator(bang_du_lieu_can_tinh_toan):
    """
    Xây dựng hệ thống chỉ báo Predator: MA, BOL, RSI, MACD, Volume.
    Khai triển dọc từng dòng lệnh, không viết tắt.
    """
    # Tạo bản sao dữ liệu để bảo vệ DataFrame gốc
    df = bang_du_lieu_can_tinh_toan.copy()

    # Bước 1: Dọn dẹp chiến trường dữ liệu rác
    mat_na_trung_lap_cot = df.columns.duplicated()
    df = df.loc[:, ~mat_na_trung_lap_cot]

    # Đúc ép các cột dữ liệu quan trọng về định dạng số thực (Float)
    danh_sach_cot_so = ['open', 'high', 'low', 'close', 'volume']

    for ten_cot_dang_duyet in danh_sach_cot_so:
        kiem_tra_cot_ton_tai = ten_cot_dang_duyet in df.columns
        if kiem_tra_cot_ton_tai == True:
            chuoi_so_da_ep_kieu = pd.to_numeric(df[ten_cot_dang_duyet], errors='coerce')
            df[ten_cot_dang_duyet] = chuoi_so_da_ep_kieu

    # Vá lấp các lỗ hổng rỗng (NaN) bằng phương pháp ffill
    df['close'] = df['close'].ffill()
    df['open'] = df['open'].ffill()
    df['volume'] = df['volume'].ffill()

    # Trích xuất chuỗi giá đóng cửa để tính toán
    chuoi_close = df['close']

    # Bước 2: HỆ THỐNG ĐƯỜNG TRUNG BÌNH ĐỘNG (MA)
    cua_so_ma20 = chuoi_close.rolling(window=20)
    df['ma20'] = cua_so_ma20.mean()

    cua_so_ma50 = chuoi_close.rolling(window=50)
    df['ma50'] = cua_so_ma50.mean()

    cua_so_ma200 = chuoi_close.rolling(window=200)
    df['ma200'] = cua_so_ma200.mean()

    # Bước 3: DẢI BOLLINGER BANDS VÀ SQUEEZE (NÉN LÒ XO)
    do_lech_chuan_20 = cua_so_ma20.std()

    khoang_mo_rong = do_lech_chuan_20 * 2
    df['upper_band'] = df['ma20'] + khoang_mo_rong
    df['lower_band'] = df['ma20'] - khoang_mo_rong

    # TÍNH TOÁN BĂNG THÔNG SQUEEZE
    khoang_cach_upper_lower = df['upper_band'] - df['lower_band']
    ti_le_bang_thong = khoang_cach_upper_lower / (df['ma20'] + 1e-9)
    df['bb_width'] = ti_le_bang_thong

    # Bước 4: CHỈ SỐ SỨC MẠNH TƯƠNG ĐỐI (RSI 14 PHIÊN)
    bien_dong_gia = chuoi_close.diff()

    chuoi_tang = bien_dong_gia.where(bien_dong_gia > 0, 0)
    chuoi_giam = -bien_dong_gia.where(bien_dong_gia < 0, 0)

    trung_binh_tang_14 = chuoi_tang.rolling(window=14).mean()
    trung_binh_giam_14 = chuoi_giam.rolling(window=14).mean()

    rs_logic = trung_binh_tang_14 / (trung_binh_giam_14 + 1e-9)
    phan_bu_rsi = 100 / (1 + rs_logic)
    df['rsi'] = 100 - phan_bu_rsi

    # Bước 5: ĐỘNG LƯỢNG MACD (CẤU HÌNH 12, 26, 9)
    ema12 = chuoi_close.ewm(span=12, adjust=False).mean()
    ema26 = chuoi_close.ewm(span=26, adjust=False).mean()

    df['macd'] = ema12 - ema26
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # Bước 6: XÁC ĐỊNH DẤU HIỆU CẠN CUNG (SUPPLY EXHAUSTION)
    kiem_tra_nen_do = df['close'] < df['open']
    df['is_red_candle'] = kiem_tra_nen_do

    chuoi_volume = df['volume']
    trung_binh_vol_20 = chuoi_volume.rolling(window=20).mean()

    # Cạn cung: Khối lượng < 80% trung bình
    nguong_can_cung_thuc_te = trung_binh_vol_20 * THAM_SO_CAN_CUNG
    kiem_tra_volume_nho_hon = df['volume'] < nguong_can_cung_thuc_te

    df['can_cung'] = (df['is_red_candle'] == True) & (kiem_tra_volume_nho_hon == True)

    # Bước 7: BIẾN SỐ PHỤC VỤ DÒNG TIỀN VÀ AI
    df['return_1d'] = chuoi_close.pct_change()

    trung_binh_vol_10 = chuoi_volume.rolling(window=10).mean()
    df['vol_strength'] = df['volume'] / (trung_binh_vol_10 + 1e-9)

    dk_cau_manh = (df['return_1d'] > 0) & (df['vol_strength'] > 1.2)
    dk_cung_manh = (df['return_1d'] < 0) & (df['vol_strength'] > 1.2)

    df['pv_trend'] = np.where(dk_cau_manh, 1, np.where(dk_cung_manh, -1, 0))

    bang_du_lieu_sach_tuyet_doi = df.dropna()

    return bang_du_lieu_sach_tuyet_doi

# ==============================================================================
# 5. MODULE DỰ BÁO VÀ KIỂM CHỨNG (PREDICTION LAYER)
# ==============================================================================

def phan_tich_tam_ly_dam_dong(df_quant):
    """Đo lường RSI để bóc tách cung bậc cảm xúc."""
    dong_cuoi = df_quant.iloc[-1]
    val_rsi = dong_cuoi['rsi']

    if val_rsi > 75:
        chuoi_nhan = " 🔥  CỰC KỲ THAM LAM (QUÁ MUA)"
    elif val_rsi > 60:
        chuoi_nhan = " ⚖️  THAM LAM (HƯNG PHẤN)"
    elif val_rsi < 30:
        chuoi_nhan = " 💀  CỰC KỲ SỢ HÃI (QUÁ BÁN)"
    elif val_rsi < 42:
        chuoi_nhan = " 😨  SỢ HÃI (BI QUAN)"
    else:
        chuoi_nhan = " 🟡  TRUNG LẬP (ĐI NGANG)"

    gia_tri_lam_tron = round(val_rsi, 1)
    return chuoi_nhan, gia_tri_lam_tron

def thuc_thi_backtest_chien_thuat(df_quant):
    """Kiểm chứng xác suất chốt lãi 5% trong lịch sử."""
    so_lan_co_tin_hieu = 0
    so_lan_thanh_cong = 0
    do_dai_du_lieu = len(df_quant)

    for i in range(100, do_dai_du_lieu - 10):
        gia_tri_rsi_qua_khu = df_quant['rsi'].iloc[i]
        gia_tri_macd_qua_khu = df_quant['macd'].iloc[i]
        gia_tri_signal_qua_khu = df_quant['signal'].iloc[i]

        gia_tri_macd_truoc_do = df_quant['macd'].iloc[i-1]
        gia_tri_signal_truoc_do = df_quant['signal'].iloc[i-1]

        dieu_kien_rsi_thap = gia_tri_rsi_qua_khu < 45
        dieu_kien_macd_cat_len = (gia_tri_macd_qua_khu > gia_tri_signal_qua_khu) and (gia_tri_macd_truoc_do <= gia_tri_signal_truoc_do)

        if dieu_kien_rsi_thap and dieu_kien_macd_cat_len:
            so_lan_co_tin_hieu = so_lan_co_tin_hieu + 1

            muc_gia_mua_vao = df_quant['close'].iloc[i]
            muc_gia_chot_lai = muc_gia_mua_vao * 1.05

            chuoi_gia_tuong_lai_10_ngay = df_quant['close'].iloc[i+1 : i+11]

            kiem_tra_cham_muc_tieu = any(chuoi_gia_tuong_lai_10_ngay > muc_gia_chot_lai)

            if kiem_tra_cham_muc_tieu == True:
                so_lan_thanh_cong = so_lan_thanh_cong + 1

    if so_lan_co_tin_hieu == 0:
        return 0.0

    ty_le_thang_thuc_te = (so_lan_thanh_cong / so_lan_co_tin_hieu) * 100
    ty_le_lam_tron = round(ty_le_thang_thuc_te, 1)

    return ty_le_lam_tron

def du_bao_xac_suat_ai_t3(df_quant):
    """Huấn luyện máy học Random Forest để dự báo cửa tăng."""
    do_dai_tap_du_lieu = len(df_quant)

    if do_dai_tap_du_lieu < 200:
        return "N/A"

    df_ml = df_quant.copy()

    gia_dong_cua_tuong_lai = df_ml['close'].shift(-3)
    gia_dong_cua_hien_tai = df_ml['close']

    muc_tieu_tang_gia = gia_dong_cua_hien_tai * 1.02
    dieu_kien_dat_muc_tieu = gia_dong_cua_tuong_lai > muc_tieu_tang_gia

    df_ml['muc_tieu_ai'] = dieu_kien_dat_muc_tieu.astype(int)

    danh_sach_bien_ai = [
        'rsi',
        'macd',
        'signal',
        'return_1d',
        'vol_strength',
        'bb_width',
        'pv_trend'
    ]

    df_ml_sach = df_ml.dropna()

    tap_huan_luyen_x = df_ml_sach[danh_sach_bien_ai][:-3]
    tap_huan_luyen_y = df_ml_sach['muc_tieu_ai'][:-3]

    mo_hinh_ai_random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
    mo_hinh_ai_random_forest.fit(tap_huan_luyen_x, tap_huan_luyen_y)

    du_lieu_phien_hien_tai = df_ml_sach[danh_sach_bien_ai].iloc[[-1]]
    ma_tran_xac_suat = mo_hinh_ai_random_forest.predict_proba(du_lieu_phien_hien_tai)

    xac_suat_cua_tang = ma_tran_xac_suat[0][1]
    xac_suat_lam_tron = round(xac_suat_cua_tang * 100, 1)

    return xac_suat_lam_tron

# ==============================================================================
# HẾT PHẦN 2. MINH HÃY DÁN NỐI TIẾP VÀ GÕ "PHẦN 3" ĐỂ NHẬN PHẦN CUỐI (GIAO DIỆN & RADAR) NHÉ!
# ==============================================================================
# ==============================================================================
# PHẦN 3/3: BÁO CÁO TÀI CHÍNH, GIAO DIỆN UI VÀ SIÊU RADAR PREDATOR 2 TẦNG
# MINH HÃY DÁN NỐI TIẾP NGAY BÊN DƯỚI PHẦN 2
# ==============================================================================

# ==============================================================================
# 6. MODULE PHÂN TÍCH TÀI CHÍNH VÀ BÁO CÁO (REPORTING LAYER)
# ==============================================================================

def do_luong_tang_truong_canslim(ma_chung_khoan):
    """
    Đo lường tăng trưởng lợi nhuận quý (Chữ C trong CANSLIM).
    Đã gọt rửa sạch hậu tố phiên bản cũ.
    """
    try:
        bang_bao_cao_kqkd = dong_co_vnstock.stock.finance.income_statement(
            symbol=ma_chung_khoan, 
            period='quarter', 
            lang='en'
        ).head(5)
        
        danh_sach_tu_khoa_lnst = ['sau thuế', 'posttax', 'net profit']
        danh_sach_cot_tim_thay = []
        
        for ten_cot_bao_cao in bang_bao_cao_kqkd.columns:
            chuoi_ten_cot_thuong = str(ten_cot_bao_cao).lower()
            
            for tu_khoa_kiem_tra in danh_sach_tu_khoa_lnst:
                kiem_tra_chua_tu_khoa = tu_khoa_kiem_tra in chuoi_ten_cot_thuong
                if kiem_tra_chua_tu_khoa == True:
                    danh_sach_cot_tim_thay.append(ten_cot_bao_cao)
                    break
        
        so_luong_cot_tim_thay = len(danh_sach_cot_tim_thay)
        
        if so_luong_cot_tim_thay > 0:
            ten_cot_loi_nhuan_chinh = danh_sach_cot_tim_thay[0]
            
            loi_nhuan_quy_gan_nhat = float(bang_bao_cao_kqkd.iloc[0][ten_cot_loi_nhuan_chinh])
            loi_nhuan_quy_cung_ky_nam_ngoai = float(bang_bao_cao_kqkd.iloc[4][ten_cot_loi_nhuan_chinh])
            
            kiem_tra_co_loi_nhuan_duong = loi_nhuan_quy_cung_ky_nam_ngoai > 0
            
            if kiem_tra_co_loi_nhuan_duong == True:
                muc_chenh_lech_loi_nhuan = loi_nhuan_quy_gan_nhat - loi_nhuan_quy_cung_ky_nam_ngoai
                ty_le_tang_truong_thuc_te = (muc_chenh_lech_loi_nhuan / loi_nhuan_quy_cung_ky_nam_ngoai) * 100
                ty_le_lam_tron = round(ty_le_tang_truong_thuc_te, 1)
                
                return ty_le_lam_tron
                
    except Exception:
        pass
    
    return None

def boc_tach_chi_so_pe_roe(ma_chung_khoan):
    """
    Lấy P/E và ROE - Đã FIX LỖI 0.0 gây hiểu lầm.
    Chỉ hiển thị khi dữ liệu là số thực dương hợp lý.
    """
    gia_tri_pe_cuoi_cung = None
    gia_tri_roe_cuoi_cung = None
    
    try:
        bang_chi_so_tai_chinh = dong_co_vnstock.stock.finance.ratio(ma_chung_khoan, 'quarterly')
        dong_du_lieu_chi_so_moi_nhat = bang_chi_so_tai_chinh.iloc[-1]
        
        pe_tu_vnstock = dong_du_lieu_chi_so_moi_nhat.get('ticker_pe', dong_du_lieu_chi_so_moi_nhat.get('pe', None))
        roe_tu_vnstock = dong_du_lieu_chi_so_moi_nhat.get('roe', None)
        
        kiem_tra_pe_hop_le = (pe_tu_vnstock is not None) and (not np.isnan(pe_tu_vnstock)) and (pe_tu_vnstock > 0)
        if kiem_tra_pe_hop_le == True:
            gia_tri_pe_cuoi_cung = pe_tu_vnstock
            
        kiem_tra_roe_hop_le = (roe_tu_vnstock is not None) and (not np.isnan(roe_tu_vnstock)) and (roe_tu_vnstock > 0)
        if kiem_tra_roe_hop_le == True:
            gia_tri_roe_cuoi_cung = roe_tu_vnstock
            
    except Exception:
        pass
        
    kiem_tra_thieu_pe = gia_tri_pe_cuoi_cung is None
    
    if kiem_tra_thieu_pe == True:
        try:
            chuoi_ma_yahoo_finance = f"{ma_chung_khoan}.VN"
            doi_tuong_info_yahoo = yf.Ticker(chuoi_ma_yahoo_finance).info
            
            gia_tri_pe_cuoi_cung = doi_tuong_info_yahoo.get('trailingPE', None)
            gia_tri_roe_cuoi_cung = doi_tuong_info_yahoo.get('returnOnEquity', None)
            
        except Exception:
            pass
            
    return gia_tri_pe_cuoi_cung, gia_tri_roe_cuoi_cung

def tao_ban_bao_cao_tu_dong(tui_du_lieu_dong_goi):
    """
    HÀM BÁO CÁO BẰNG DICTIONARY: Triệt tiêu hoàn toàn lỗi TypeError do lệch tham số.
    """
    ma_co_phieu_dang_xet = tui_du_lieu_dong_goi['ma_ck']
    dong_du_lieu_cuoi_cung = tui_du_lieu_dong_goi['dong_cuoi']
    
    danh_sach_doan_van_bao_cao = []
    
    chuoi_tieu_de_bao_cao = f"#### 🎯 PHÂN TÍCH CHIẾN THUẬT MÃ: {ma_co_phieu_dang_xet}"
    danh_sach_doan_van_bao_cao.append(chuoi_tieu_de_bao_cao)
    
    # 1. Đọc vị dòng tiền Cá mập (Tây hoặc Tự doanh)
    kiem_tra_to_chuc_co_gom = tui_du_lieu_dong_goi['to_chuc_gom']
    if kiem_tra_to_chuc_co_gom == True:
        chuoi_dong_tien_manh = f"✅ **Dòng tiền lớn:** Phát hiện Cá mập (Tây/Tự doanh) đang âm thầm GOM HÀNG mã {ma_co_phieu_dang_xet}."
        danh_sach_doan_van_bao_cao.append(chuoi_dong_tien_manh)
    else:
        chuoi_dong_tien_yeu = f"🟡 **Dòng tiền lớn:** Chưa thấy dấu hiệu gom hàng rõ nét từ tổ chức."
        danh_sach_doan_van_bao_cao.append(chuoi_dong_tien_yeu)

    # 2. Đọc vị vị thế nền giá kỹ thuật
    gia_dong_cua_hien_tai = dong_du_lieu_cuoi_cung['close']
    gia_tri_ma20_hien_tai = dong_du_lieu_cuoi_cung['ma20']
    
    kiem_tra_giu_duoc_nen = gia_dong_cua_hien_tai > gia_tri_ma20_hien_tai
    if kiem_tra_giu_duoc_nen == True:
        chuoi_xu_huong_tot = f"✅ **Xu hướng:** Giá ({gia_dong_cua_hien_tai:,.0f}) neo vững trên đường sinh tử MA20. Nền tảng rất ổn định."
        danh_sach_doan_van_bao_cao.append(chuoi_xu_huong_tot)
    else:
        chuoi_xu_huong_xau = f"❌ **Cảnh báo:** Giá rớt xuống dưới đường MA20. Xu hướng ngắn hạn bị đe dọa."
        danh_sach_doan_van_bao_cao.append(chuoi_xu_huong_xau)

    # 3. Đọc vị vũ khí Predator siêu hạng
    bang_thong_hien_tai = dong_du_lieu_cuoi_cung['bb_width']
    bang_thong_nho_nhat_20p = tui_du_lieu_dong_goi['min_bbw']
    nguong_bop_nghet_lo_xo = bang_thong_nho_nhat_20p * THAM_SO_SQUEEZE
    
    kiem_tra_lo_xo_nen_chat = bang_thong_hien_tai <= nguong_bop_nghet_lo_xo
    if kiem_tra_lo_xo_nen_chat == True:
        chuoi_lo_xo = f"🌀 **Tín hiệu nén:** Lò xo Bollinger đang siết rất chặt. Khả năng sắp nổ biến động cực lớn."
        danh_sach_doan_van_bao_cao.append(chuoi_lo_xo)
        
    kiem_tra_trang_thai_can_cung = dong_du_lieu_cuoi_cung['can_cung']
    if kiem_tra_trang_thai_can_cung == True:
        chuoi_can_cung = f"💧 **Tín hiệu cạn cung:** Phát hiện trạng thái CẠN CUNG. Lực bán đã kiệt quệ, giá rất dễ bật tăng."
        danh_sach_doan_van_bao_cao.append(chuoi_can_cung)

    # 4. Quản trị rủi ro và Stop-loss cho Minh
    muc_gia_dung_lo_stoploss = gia_tri_ma20_hien_tai * 0.98
    
    danh_sach_doan_van_bao_cao.append(f"#### 🛡️ QUẢN TRỊ RỦI RO DÀNH CHO MINH:")
    
    chuoi_khuyen_nghi_mua = f"- **Vùng giá mua an toàn:** Quanh nền MA20 ({gia_tri_ma20_hien_tai:,.0f} VNĐ)."
    danh_sach_doan_van_bao_cao.append(chuoi_khuyen_nghi_mua)
    
    chuoi_khuyen_nghi_ban = f"- **Ngưỡng Stop-loss:** {muc_gia_dung_lo_stoploss:,.0f} VNĐ (Cắt lổ nếu gãy nền quá 2%)."
    danh_sach_doan_van_bao_cao.append(chuoi_khuyen_nghi_ban)
    
    chuoi_van_ban_hoan_chinh = "\n\n".join(danh_sach_doan_van_bao_cao)
    return chuoi_van_ban_hoan_chinh

# ==============================================================================
# 7. GIAO DIỆN NGƯỜI DÙNG & MÁY QUÉT RADAR PREDATOR (UI & SCANNER)
# ==============================================================================

@st.cache_data(ttl=3600)
def lay_danh_sach_toan_bo_ma_hose():
    """Tải và lưu trữ bộ nhớ đệm danh sách mã HOSE."""
    try:
        bang_danh_sach_niem_yet = dong_co_vnstock.market.listing()
        chi_lay_san_hose = bang_danh_sach_niem_yet['comGroupCode'] == 'HOSE'
        danh_sach_ma_hose = bang_danh_sach_niem_yet[chi_lay_san_hose]['ticker'].tolist()
        return danh_sach_ma_hose
    except Exception:
        # Danh sách dự phòng nếu kết nối lỗi
        danh_sach_du_phong = ["FPT", "HPG", "SSI", "VCB", "VNM", "TCB", "MWG", "VIC", "VHM", "GAS", "HSG", "STB"]
        return danh_sach_du_phong

# 7.1 THIẾT LẬP THANH ĐIỀU HÀNH BÊN TRÁI (SIDEBAR)
danh_sach_ma_san_hose = lay_danh_sach_toan_bo_ma_hose()

st.sidebar.header("🕹️ Trung Tâm Điều Hành Predator V20.0")

chuoi_label_chon_ma = "1. Chọn mã cổ phiếu mục tiêu từ danh sách:"
ma_duoc_chon_tu_danh_sach = st.sidebar.selectbox(chuoi_label_chon_ma, danh_sach_ma_san_hose)

chuoi_label_nhap_tay = "2. Hoặc tự nhập mã tay (VD: HSG):"
ma_duoc_nhap_tay_vao = st.sidebar.text_input(chuoi_label_nhap_tay).upper()

# KHAI BÁO BIẾN TRỤC CHÍNH ĐỒNG BỘ 100% TOÀN HỆ THỐNG
kiem_tra_co_nhap_tay_khong = ma_duoc_nhap_tay_vao != ""
if kiem_tra_co_nhap_tay_khong == True:
    ma_co_phieu_dang_duoc_chon = ma_duoc_nhap_tay_vao
else:
    ma_co_phieu_dang_duoc_chon = ma_duoc_chon_tu_danh_sach

# 7.2 THIẾT LẬP HỆ THỐNG CÁC TAB CHỨC NĂNG
danh_sach_ten_tab = [
    "🤖 ROBOT ADVISOR MASTER", 
    "🏢 SỨC KHỎE TÀI CHÍNH", 
    "🌊 DÒNG TIỀN TỔ CHỨC", 
    "🔍 RADAR PREDATOR (SĂN CHÂN SÓNG)"
]
tab_advisor, tab_tai_chinh, tab_dong_tien, tab_radar = st.tabs(danh_sach_ten_tab)

# ------------------------------------------------------------------------------
# MÀN HÌNH TAB 1: ROBOT ADVISOR MASTER
# ------------------------------------------------------------------------------
with tab_advisor:
    chuoi_nut_bam_phan_tich = f"⚡ KÍCH HOẠT PHÂN TÍCH MÃ {ma_co_phieu_dang_duoc_chon}"
    
    if st.button(chuoi_nut_bam_phan_tich):
        chuoi_thong_bao_cho = f"Predator đang rà soát dữ liệu đa tầng mã {ma_co_phieu_dang_duoc_chon}..."
        
        with st.spinner(chuoi_thong_bao_cho):
            
            bang_du_lieu_gia_goc = lay_du_lieu_gia_niem_yet_chuan(ma_co_phieu_dang_duoc_chon)
            
            kiem_tra_du_lieu_gia_ton_tai = bang_du_lieu_gia_goc is not None
            
            if kiem_tra_du_lieu_gia_ton_tai == True:
                
                bang_du_lieu_da_tinh_toan = tinh_toan_bo_chi_bao_ky_thuat_predator(bang_du_lieu_gia_goc)
                dong_du_lieu_cuoi_cung = bang_du_lieu_da_tinh_toan.iloc[-1]
                
                diem_xac_suat_ai = du_bao_xac_suat_ai_t3(bang_du_lieu_da_tinh_toan)
                
                # Quét dòng tiền tổ chức 10 phiên gần nhất
                bang_khoi_ngoai, bang_tu_doanh = lay_du_lieu_dong_tien_to_chuc_chuyen_sau(ma_co_phieu_dang_duoc_chon, 10)
                trang_thai_ca_map_gom = False
                
                kiem_tra_khoi_ngoai_ton_tai = bang_khoi_ngoai is not None
                if kiem_tra_khoi_ngoai_ton_tai == True:
                    tong_mua_ngoai_5_phien = bang_khoi_ngoai['buyval'].tail(5).sum()
                    tong_ban_ngoai_5_phien = bang_khoi_ngoai['sellval'].tail(5).sum()
                    
                    if tong_mua_ngoai_5_phien > tong_ban_ngoai_5_phien:
                        trang_thai_ca_map_gom = True
                        
                kiem_tra_ca_map_chua_gom = trang_thai_ca_map_gom == False
                kiem_tra_tu_doanh_ton_tai = bang_tu_doanh is not None
                
                if kiem_tra_ca_map_chua_gom and kiem_tra_tu_doanh_ton_tai:
                    tong_mua_tu_doanh_5_phien = bang_tu_doanh['buyval'].tail(5).sum()
                    tong_ban_tu_doanh_5_phien = bang_tu_doanh['sellval'].tail(5).sum()
                    
                    if tong_mua_tu_doanh_5_phien > tong_ban_tu_doanh_5_phien:
                        trang_thai_ca_map_gom = True

                bang_thong_nho_nhat_20_phien = bang_du_lieu_da_tinh_toan['bb_width'].tail(20).min()

                # Đóng gói Dictionary để chống lỗi TypeError
                tui_thong_tin_truyen_vao = {
                    'ma_ck': ma_co_phieu_dang_duoc_chon, 
                    'dong_cuoi': dong_du_lieu_cuoi_cung, 
                    'diem_ai': diem_xac_suat_ai, 
                    'to_chuc_gom': trang_thai_ca_map_gom, 
                    'min_bbw': bang_thong_nho_nhat_20_phien
                }
                
                cot_bao_cao, cot_ra_lenh = st.columns([2, 1])
                
                with cot_bao_cao: 
                    chuoi_bao_cao_chi_tiet = tao_ban_bao_cao_tu_dong(tui_thong_tin_truyen_vao)
                    st.info(chuoi_bao_cao_chi_tiet)
                    
                with cot_ra_lenh:
                    st.subheader("🤖 ROBOT ĐỀ XUẤT LỆNH:")
                    
                    kiem_tra_ai_hop_le = isinstance(diem_xac_suat_ai, float)
                    
                    if kiem_tra_ai_hop_le == True:
                        kiem_tra_ai_dat_chuan = diem_xac_suat_ai > THAM_SO_AI_PREDATOR
                    else:
                        kiem_tra_ai_dat_chuan = False
                        
                    kiem_tra_gia_tren_ma20 = dong_du_lieu_cuoi_cung['close'] > dong_du_lieu_cuoi_cung['ma20']
                    
                    dieu_kien_mua_hop_le = kiem_tra_ai_dat_chuan and kiem_tra_gia_tren_ma20
                    
                    if dieu_kien_mua_hop_le == True:
                        chuoi_lenh_hanh_dong = "🚀 MUA / NẮM GIỮ"
                        mau_sac_lenh = "green"
                    else:
                        chuoi_lenh_hanh_dong = "⚖️ QUAN SÁT"
                        mau_sac_lenh = "orange"
                        
                    chuoi_hien_thi_lenh = f":{mau_sac_lenh}[{chuoi_lenh_hanh_dong}]"
                    st.title(chuoi_hien_thi_lenh)
                
                # Vẽ biểu đồ nến Master Chart
                st.divider()
                doi_tuong_bieu_do = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                bang_du_lieu_ve = bang_du_lieu_da_tinh_toan.tail(120)
                
                bieu_do_nen = go.Candlestick(
                    x=bang_du_lieu_ve['date'], open=bang_du_lieu_ve['open'], 
                    high=bang_du_lieu_ve['high'], low=bang_du_lieu_ve['low'], 
                    close=bang_du_lieu_ve['close'], name='Giá Cổ Phiếu'
                )
                doi_tuong_bieu_do.add_trace(bieu_do_nen, row=1, col=1)
                
                bieu_do_duong_ma20 = go.Scatter(
                    x=bang_du_lieu_ve['date'], y=bang_du_lieu_ve['ma20'], 
                    line=dict(color='orange'), name='Đường Sinh Tử MA20'
                )
                doi_tuong_bieu_do.add_trace(bieu_do_duong_ma20, row=1, col=1)
                
                bieu_do_cot_volume = go.Bar(
                    x=bang_du_lieu_ve['date'], y=bang_du_lieu_ve['volume'], 
                    marker_color='gray', name='Khối Lượng'
                )
                doi_tuong_bieu_do.add_trace(bieu_do_cot_volume, row=2, col=1)
                
                doi_tuong_bieu_do.update_layout(height=650, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(doi_tuong_bieu_do, use_container_width=True)
                
            else:
                chuoi_bao_loi_du_lieu = "❌ Lỗi: Không thể tải dữ liệu giá cổ phiếu."
                st.error(chuoi_bao_loi_du_lieu)

# ------------------------------------------------------------------------------
# MÀN HÌNH TAB 2 & 3: TÀI CHÍNH & DÒNG TIỀN
# ------------------------------------------------------------------------------
with tab_tai_chinh:
    chuoi_tieu_de_tai_chinh = f"### 📈 Phân Tích Tài Chính {ma_co_phieu_dang_duoc_chon}"
    st.write(chuoi_tieu_de_tai_chinh)
    
    chi_so_pe_thuc, chi_so_roe_thuc = boc_tach_chi_so_pe_roe(ma_co_phieu_dang_duoc_chon)
    cot_pe, cot_roe = st.columns(2)
    
    kiem_tra_co_pe_khong = chi_so_pe_thuc is not None
    if kiem_tra_co_pe_khong: chuoi_hien_thi_pe = f"{chi_so_pe_thuc:.1f}"
    else: chuoi_hien_thi_pe = "N/A"
        
    kiem_tra_co_roe_khong = chi_so_roe_thuc is not None
    if kiem_tra_co_roe_khong: chuoi_hien_thi_roe = f"{chi_so_roe_thuc:.1%}"
    else: chuoi_hien_thi_roe = "N/A"
        
    cot_pe.metric("Chỉ số P/E", chuoi_hien_thi_pe)
    cot_roe.metric("Chỉ số ROE (%)", chuoi_hien_thi_roe)

with tab_dong_tien:
    chuoi_tieu_de_dong_tien = f"### 🌊 Dòng Tiền Tổ Chức (10 Phiên) - {ma_co_phieu_dang_duoc_chon}"
    st.write(chuoi_tieu_de_dong_tien)
    
    bang_ngoai_tab3, bang_doanh_tab3 = lay_du_lieu_dong_tien_to_chuc_chuyen_sau(ma_co_phieu_dang_duoc_chon, 20)
    cot_ngoai_tab3, cot_doanh_tab3 = st.columns(2)
    
    kiem_tra_co_bang_ngoai = bang_ngoai_tab3 is not None and not bang_ngoai_tab3.empty
    if kiem_tra_co_bang_ngoai:
        gia_tri_rong_ngoai = (bang_ngoai_tab3['buyval'].iloc[-1] - bang_ngoai_tab3['sellval'].iloc[-1]) / 1e9
        chuoi_trang_thai_ngoai = "Mua Ròng" if gia_tri_rong_ngoai > 0 else "Bán Ròng"
        cot_ngoai_tab3.metric("Khối Ngoại (Hôm nay)", f"{gia_tri_rong_ngoai:.2f} Tỷ VNĐ", delta=chuoi_trang_thai_ngoai)
        
    kiem_tra_co_bang_doanh = bang_doanh_tab3 is not None and not bang_doanh_tab3.empty
    if kiem_tra_co_bang_doanh:
        gia_tri_rong_doanh = (bang_doanh_tab3['buyval'].iloc[-1] - bang_doanh_tab3['sellval'].iloc[-1]) / 1e9
        chuoi_trang_thai_doanh = "Mua Ròng" if gia_tri_rong_doanh > 0 else "Bán Ròng"
        cot_doanh_tab3.metric("Tự Doanh (Hôm nay)", f"{gia_tri_rong_doanh:.2f} Tỷ VNĐ", delta=chuoi_trang_thai_doanh)

# ------------------------------------------------------------------------------
# MÀN HÌNH TAB 4: SIÊU RADAR PREDATOR (MÁY QUÉT 2 TẦNG CHÂN SÓNG)
# ------------------------------------------------------------------------------
with tab_radar:
    chuoi_tieu_de_radar = "🔍 Siêu Radar Predator - Săn Cổ Phiếu Chân Sóng (5% MA20)"
    st.subheader(chuoi_tieu_de_radar)
    
    chuoi_nut_bam_radar = "🔥 KÍCH HOẠT MÁY QUÉT PREDATOR"
    if st.button(chuoi_nut_bam_radar):
        
        danh_sach_ket_qua_bung_no = []
        danh_sach_ket_qua_danh_sach_cho = []
        
        thanh_tien_do_quet = st.progress(0)
        danh_sach_ma_can_quet = danh_sach_ma_san_hose[:30] # Lấy 30 mã đầu tiên
        tong_so_ma_can_quet = len(danh_sach_ma_can_quet)
        
        for vi_tri_chi_muc, ma_co_phieu_dang_quet in enumerate(danh_sach_ma_can_quet):
            try:
                bang_gia_quet_duoc = lay_du_lieu_gia_niem_yet_chuan(ma_co_phieu_dang_quet, 120)
                
                kiem_tra_bang_gia_quet_ton_tai = bang_gia_quet_duoc is not None
                if kiem_tra_bang_gia_quet_ton_tai == True:
                    
                    bang_da_tinh_toan_quet = tinh_toan_bo_chi_bao_ky_thuat_predator(bang_gia_quet_duoc)
                    dong_cuoi_cung_quet = bang_da_tinh_toan_quet.iloc[-1]
                    
                    diem_ai_quet = du_bao_xac_suat_ai_t3(bang_da_tinh_toan_quet)
                    chuoi_hien_thi_ai = f"{diem_ai_quet}%"
                    
                    # LOGIC TẦNG 1: NHÓM BÙNG NỔ (RỦI RO MUA ĐUỔI)
                    kiem_tra_vol_bung_no = dong_cuoi_cung_quet['vol_strength'] > 1.3
                    if kiem_tra_vol_bung_no == True:
                        tu_dien_ket_qua_bung_no = {
                            'Mã CK': ma_co_phieu_dang_quet, 
                            'Dự Báo AI': chuoi_hien_thi_ai, 
                            'Sức Mạnh Vol': round(dong_cuoi_cung_quet['vol_strength'], 1)
                        }
                        danh_sach_ket_qua_bung_no.append(tu_dien_ket_qua_bung_no)
                    
                    # LOGIC TẦNG 2: NHÓM DANH SÁCH CHỜ PREDATOR (CHÂN SÓNG AN TOÀN)
                    
                    # Điều kiện 1: RSI An Toàn
                    kiem_tra_rsi_an_toan = dong_cuoi_cung_quet['rsi'] < THAM_SO_RSI_AN_TOAN
                    
                    # Điều kiện 2: Vùng giá an toàn 5% quanh MA20
                    gia_tri_ma20_quet = dong_cuoi_cung_quet['ma20']
                    gia_tri_close_quet = dong_cuoi_cung_quet['close']
                    khoang_cach_tuyet_doi = abs(gia_tri_close_quet - gia_tri_ma20_quet)
                    ty_le_khoang_cach = khoang_cach_tuyet_doi / gia_tri_ma20_quet
                    kiem_tra_vung_gia_an_toan = ty_le_khoang_cach <= THAM_SO_VUNG_GIA_MA20
                    
                    # Điều kiện 3: Volume tích lũy
                    kiem_tra_vol_lon_hon_min = dong_cuoi_cung_quet['vol_strength'] >= THAM_SO_VOL_MIN
                    kiem_tra_vol_nho_hon_max = dong_cuoi_cung_quet['vol_strength'] <= THAM_SO_VOL_MAX
                    kiem_tra_vol_tich_luy = kiem_tra_vol_lon_hon_min and kiem_tra_vol_nho_hon_max
                    
                    # Điều kiện 4: AI Ủng hộ
                    kiem_tra_ai_la_so = isinstance(diem_ai_quet, float)
                    kiem_tra_ai_ung_ho = False
                    if kiem_tra_ai_la_so == True:
                        if diem_ai_quet >= THAM_SO_AI_PREDATOR:
                            kiem_tra_ai_ung_ho = True
                    
                    # Gộp điều kiện nền tảng
                    dieu_kien_nen_tang_pass = kiem_tra_rsi_an_toan and kiem_tra_vung_gia_an_toan and kiem_tra_vol_tich_luy and kiem_tra_ai_ung_ho
                    
                    if dieu_kien_nen_tang_pass == True:
                        
                        # Quét màng lọc vũ khí siêu hạng
                        bang_thong_nho_nhat_quet = bang_da_tinh_toan_quet['bb_width'].tail(20).min()
                        nguong_bop_nghet_quet = bang_thong_nho_nhat_quet * THAM_SO_SQUEEZE
                        kiem_tra_squeeze = dong_cuoi_cung_quet['bb_width'] <= nguong_bop_nghet_quet
                        
                        kiem_tra_can_cung = bang_da_tinh_toan_quet['can_cung'].tail(5).any()
                        
                        bang_ngoai_quet, bang_doanh_quet = lay_du_lieu_dong_tien_to_chuc_chuyen_sau(ma_co_phieu_dang_quet, 10)
                        kiem_tra_dong_tien_to_chuc = False
                        
                        kiem_tra_ngoai_quet_ton_tai = bang_ngoai_quet is not None
                        if kiem_tra_ngoai_quet_ton_tai == True:
                            mua_ngoai_quet = bang_ngoai_quet['buyval'].tail(5).sum()
                            ban_ngoai_quet = bang_ngoai_quet['sellval'].tail(5).sum()
                            if mua_ngoai_quet > ban_ngoai_quet:
                                kiem_tra_dong_tien_to_chuc = True
                                
                        kiem_tra_doanh_quet_ton_tai = bang_doanh_quet is not None
                        kiem_tra_chua_thay_dong_tien = kiem_tra_dong_tien_to_chuc == False
                        
                        if kiem_tra_chua_thay_dong_tien and kiem_tra_doanh_quet_ton_tai:
                            mua_doanh_quet = bang_doanh_quet['buyval'].tail(5).sum()
                            ban_doanh_quet = bang_doanh_quet['sellval'].tail(5).sum()
                            if mua_doanh_quet > ban_doanh_quet:
                                kiem_tra_dong_tien_to_chuc = True
                        
                        # Chốt hạ: Đạt nền tảng + Ít nhất 1 vũ khí
                        dieu_kien_chot_ha = kiem_tra_squeeze or kiem_tra_can_cung or kiem_tra_dong_tien_to_chuc
                        
                        if dieu_kien_chot_ha == True:
                            
                            chuoi_lo_xo_hien_thi = "Nén chặt" if kiem_tra_squeeze else "Bình thường"
                            chuoi_can_cung_hien_thi = "Cạn kiệt" if kiem_tra_can_cung else "Đủ cung"
                            chuoi_to_chuc_hien_thi = "Đang Gom" if kiem_tra_dong_tien_to_chuc else "Đứng ngoài"
                            
                            tu_dien_ket_qua_cho = {
                                'Mã CK': ma_co_phieu_dang_quet, 
                                'AI Dự Báo': chuoi_hien_thi_ai, 
                                'Lò Xo': chuoi_lo_xo_hien_thi, 
                                'Lực Bán': chuoi_can_cung_hien_thi, 
                                'Tổ Chức': chuoi_to_chuc_hien_thi
                            }
                            danh_sach_ket_qua_danh_sach_cho.append(tu_dien_ket_qua_cho)
            except Exception:
                pass
            
            # Cập nhật thanh tiến trình
            ty_le_hoan_thanh = (vi_tri_chi_muc + 1) / tong_so_ma_can_quet
            thanh_tien_do_quet.progress(ty_le_hoan_thanh)
            
        # In kết quả ra màn hình
        st.write("### 🚀 Nhóm Bùng Nổ (Thanh khoản cao - Cẩn thận rủi ro mua đuổi)")
        so_luong_ma_bung_no = len(danh_sach_ket_qua_bung_no)
        kiem_tra_co_ma_bung_no = so_luong_ma_bung_no > 0
        if kiem_tra_co_ma_bung_no == True:
            bang_data_frame_bung_no = pd.DataFrame(danh_sach_ket_qua_bung_no)
            st.table(bang_data_frame_bung_no.sort_values(by='Dự Báo AI', ascending=False))
        else:
            st.write("Không phát hiện mã nào bùng nổ.")
            
        st.write("### ⚖️ Nhóm Danh Sách Chờ Predator (An toàn quanh MA20 - Ưu tiên giải ngân)")
        so_luong_ma_danh_sach_cho = len(danh_sach_ket_qua_danh_sach_cho)
        kiem_tra_co_ma_cho = so_luong_ma_danh_sach_cho > 0
        if kiem_tra_co_ma_cho == True:
            bang_data_frame_cho = pd.DataFrame(danh_sach_ket_qua_danh_sach_cho)
            st.table(bang_data_frame_cho.sort_values(by='AI Dự Báo', ascending=False))
            st.success("✅ **Lời khuyên của Robot:** Minh hãy ưu tiên các mã có cột Tổ chức 'Đang Gom' và Lò xo 'Nén chặt'.")
        else:
            st.info("Chưa có mã nào thỏa mãn bộ lọc 5% khắt khe của Predator.")

# ==============================================================================
# HẾT MÃ NGUỒN V20.0 - THE PREDATOR LEVIATHAN (HOÀN TẤT)
# ==============================================================================
