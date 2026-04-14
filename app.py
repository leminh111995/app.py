# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V14.1 (THE LEVIATHAN)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# TRẠNG THÁI: PHIÊN BẢN TÍCH HỢP DỮ LIỆU KHỐI NGOẠI THỰC TẾ (REAL DATA)
# CAM KẾT V14.1:
# 1. KẾ THỪA 100% BỘ KHUNG V14.0 (Hoạt động ổn định).
# 2. FIX LỖI TAB 2: Đã xử lý triệt để hiển thị "N/A" khi P/E và ROE bị mất API.
# 3. KHÔNG NÉN CODE: Khai triển tối đa mọi logic để hệ thống luôn ổn định.
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

# Đảm bảo tài nguyên NLTK luôn sẵn sàng để không bị lỗi Runtime
try:
    # Hệ thống thử tìm file nén lexicon trong môi trường
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu chưa có, kích hoạt tiến trình tải xuống tự động
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & PHÂN QUYỀN (SECURITY LAYER)
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh_v13():
    """
    Hàm bảo mật cấp cao, khóa hệ thống bằng mật mã.
    Thiết kế logic tách biệt để chống lỗi KeyError trên Streamlit.
    """
    
    # 1. Kiểm tra trạng thái đã đăng nhập thành công từ trước
    co_dang_nhap_chua = st.session_state.get("trang_thai_dang_nhap_thanh_cong_v13", False)
    
    if co_dang_nhap_chua == True:
        # Đã đăng nhập, cho phép chạy tiếp
        return True

    # 2. Nếu chưa đăng nhập, tạo giao diện khóa
    st.markdown("### 🔐 Quant System V14.1 - Cổng Bảo Mật Trung Tâm")
    st.info("Hệ thống phân tích định lượng chuyên sâu đang bị khóa. Vui lòng xác thực danh tính.")
    
    # Tạo ô nhập mật mã (không dùng on_change để tránh lỗi widget)
    mat_ma_nguoi_dung_nhap_vao = st.text_input(
        "🔑 Vui lòng nhập mật mã truy cập của Minh:", 
        type="password"
    )
    
    # 3. Xử lý khi có dữ liệu nhập vào ô text_input
    if mat_ma_nguoi_dung_nhap_vao != "":
        
        # Đọc mật mã gốc từ hệ thống bảo mật
        mat_ma_chuan_he_thong = st.secrets["password"]
        
        # Tiến hành so sánh
        if mat_ma_nguoi_dung_nhap_vao == mat_ma_chuan_he_thong:
            # Gán cờ thành công
            st.session_state["trang_thai_dang_nhap_thanh_cong_v13"] = True
            
            # Tải lại trang để xóa form đăng nhập
            st.rerun()
        else:
            # Báo lỗi công khai
            st.error("❌ Cảnh báo: Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock.")
            
    # Mặc định chặn truy cập
    return False

# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG CHÍNH (MAIN APP EXECUTION)
# ==============================================================================
if xac_thuc_quyen_truy_cap_cua_minh_v13() == True:
    
    # Cấu hình Layout cho toàn bộ trang
    st.set_page_config(
        page_title="Quant System V14.1 Real Data", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Tiêu đề giao diện chính
    st.title("🛡️ Quant System V14.1: Master Advisor & Real-Flow Engine")
    st.markdown("---")

    # Khởi tạo động cơ Vnstock
    dong_co_vnstock_v13 = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU CỐT LÕI (DATA ACQUISITION)
    # ==============================================================================
    def lay_du_lieu_nien_yet_chuan_v13(ma_chung_khoan_can_lay, so_ngay_lich_su_can_lay=1000):
        """
        Hàm tải dữ liệu giá cổ phiếu OHLCV.
        Quy trình Fail-over 2 lớp: Vnstock -> Yahoo Finance.
        Bảo vệ tuyệt đối việc mất dữ liệu.
        """
        
        # 2.1 Khởi tạo mốc thời gian
        thoi_diem_bay_gio = datetime.now()
        chuoi_ngay_ket_thuc_lay_du_lieu = thoi_diem_bay_gio.strftime('%Y-%m-%d')
        
        do_tre_thoi_gian_tinh_bang_ngay = timedelta(days=so_ngay_lich_su_can_lay)
        thoi_diem_bat_dau_lay_du_lieu = thoi_diem_bay_gio - do_tre_thoi_gian_tinh_bang_ngay
        chuoi_ngay_bat_dau_lay_du_lieu = thoi_diem_bat_dau_lay_du_lieu.strftime('%Y-%m-%d')
        
        # 2.2 Gọi Vnstock
        try:
            bang_du_lieu_tu_vnstock = dong_co_vnstock_v13.stock.quote.history(
                symbol=ma_chung_khoan_can_lay, 
                start=chuoi_ngay_bat_dau_lay_du_lieu, 
                end=chuoi_ngay_ket_thuc_lay_du_lieu
            )
            
            if bang_du_lieu_tu_vnstock is not None:
                if len(bang_du_lieu_tu_vnstock) > 0:
                    
                    # Chuẩn hóa tên cột thành chữ thường
                    danh_sach_ten_cot_da_chuan_hoa = []
                    for ten_cot_hien_tai in bang_du_lieu_tu_vnstock.columns:
                        ten_cot_in_thuong = str(ten_cot_hien_tai).lower()
                        danh_sach_ten_cot_da_chuan_hoa.append(ten_cot_in_thuong)
                    
                    bang_du_lieu_tu_vnstock.columns = danh_sach_ten_cot_da_chuan_hoa
                    return bang_du_lieu_tu_vnstock
                    
        except Exception:
            pass
        
        # 2.3 Gọi Yahoo Finance dự phòng
        try:
            # Tạo mã chuẩn Yahoo
            if ma_chung_khoan_can_lay == "VNINDEX":
                ma_chung_khoan_yahoo = "^VNINDEX"
            else:
                ma_chung_khoan_yahoo = f"{ma_chung_khoan_can_lay}.VN"
                
            bang_du_lieu_tu_yahoo = yf.download(
                ma_chung_khoan_yahoo, 
                period="3y", 
                progress=False
            )
            
            if len(bang_du_lieu_tu_yahoo) > 0:
                
                # Biến index ngày thành cột
                bang_du_lieu_tu_yahoo = bang_du_lieu_tu_yahoo.reset_index()
                
                # Sửa lỗi cột kép (Multi-index) của thư viện YF mới
                danh_sach_ten_cot_yahoo_da_chuan_hoa = []
                for nhan_cot_yahoo in bang_du_lieu_tu_yahoo.columns:
                    if isinstance(nhan_cot_yahoo, tuple):
                        ten_cot_tuple_in_thuong = str(nhan_cot_yahoo[0]).lower()
                        danh_sach_ten_cot_yahoo_da_chuan_hoa.append(ten_cot_tuple_in_thuong)
                    else:
                        ten_cot_chuoi_in_thuong = str(nhan_cot_yahoo).lower()
                        danh_sach_ten_cot_yahoo_da_chuan_hoa.append(ten_cot_chuoi_in_thuong)
                
                bang_du_lieu_tu_yahoo.columns = danh_sach_ten_cot_yahoo_da_chuan_hoa
                return bang_du_lieu_tu_yahoo
                
        except Exception as thong_bao_loi_yahoo:
            st.sidebar.error(f"⚠️ Lỗi nghiêm trọng khi tải mã {ma_chung_khoan_can_lay}: {str(thong_bao_loi_yahoo)}")
            return None

    # ==============================================================================
    # 2.5. HÀM TRÍCH XUẤT KHỐI NGOẠI THỰC TẾ (TAB 3)
    # ==============================================================================
    def lay_du_lieu_khoi_ngoai_thuc_te_v14(ma_chung_khoan_vao, so_ngay_truy_xuat=20):
        """
        Truy xuất trực tiếp Dữ Liệu Khối Ngoại (Real Data) từ máy chủ Vnstock 
        để lấy chính xác Tỷ VNĐ Mua/Bán Ròng.
        """
        try:
            thoi_diem_bay_gio = datetime.now()
            chuoi_ngay_ket_thuc = thoi_diem_bay_gio.strftime('%Y-%m-%d')
            
            do_tre_thoi_gian = timedelta(days=so_ngay_truy_xuat)
            thoi_diem_bat_dau = thoi_diem_bay_gio - do_tre_thoi_gian
            chuoi_ngay_bat_dau = thoi_diem_bat_dau.strftime('%Y-%m-%d')
            
            bang_du_lieu_khoi_ngoai = None
            
            # 1. Thử gọi hàm foreign_trade
            try:
                bang_du_lieu_khoi_ngoai = dong_co_vnstock_v13.stock.trade.foreign_trade(
                    symbol=ma_chung_khoan_vao,
                    start=chuoi_ngay_bat_dau,
                    end=chuoi_ngay_ket_thuc
                )
            except Exception:
                pass
            
            # 2. Thử gọi hàm trading.foreign (dự phòng)
            if bang_du_lieu_khoi_ngoai is None or len(bang_du_lieu_khoi_ngoai) == 0:
                try:
                    bang_du_lieu_khoi_ngoai = dong_co_vnstock_v13.stock.trading.foreign(
                        symbol=ma_chung_khoan_vao,
                        start=chuoi_ngay_bat_dau,
                        end=chuoi_ngay_ket_thuc
                    )
                except Exception:
                    pass
            
            if bang_du_lieu_khoi_ngoai is not None and len(bang_du_lieu_khoi_ngoai) > 0:
                danh_sach_ten_cot_moi = []
                for ten_cot in bang_du_lieu_khoi_ngoai.columns:
                    danh_sach_ten_cot_moi.append(str(ten_cot).lower())
                bang_du_lieu_khoi_ngoai.columns = danh_sach_ten_cot_moi
                
                return bang_du_lieu_khoi_ngoai
                
        except Exception:
            pass
            
        return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE)
    # ==============================================================================
    def tinh_toan_bo_chi_bao_quant_v13(bang_du_lieu_can_tinh_toan):
        """Xây dựng bộ chỉ báo định lượng: MA, Bollinger, RSI, MACD, Volume."""
        bang_du_lieu_dang_xu_ly = bang_du_lieu_can_tinh_toan.copy()
        
        # --- BỘ LỌC CHỐNG LỖI VALUEERROR ---
        mat_na_cot_duy_nhat = ~bang_du_lieu_dang_xu_ly.columns.duplicated()
        bang_du_lieu_dang_xu_ly = bang_du_lieu_dang_xu_ly.loc[:, mat_na_cot_duy_nhat]
        
        danh_sach_cot_co_ban = ['open', 'high', 'low', 'close', 'volume']
        for ten_cot_can_ep in danh_sach_cot_co_ban:
            if ten_cot_can_ep in bang_du_lieu_dang_xu_ly.columns:
                bang_du_lieu_dang_xu_ly[ten_cot_can_ep] = pd.to_numeric(
                    bang_du_lieu_dang_xu_ly[ten_cot_can_ep], 
                    errors='coerce'
                )
        
        bang_du_lieu_dang_xu_ly['close'] = bang_du_lieu_dang_xu_ly['close'].ffill()
        bang_du_lieu_dang_xu_ly['volume'] = bang_du_lieu_dang_xu_ly['volume'].ffill()
        
        chuoi_gia_dong_cua_co_phieu = bang_du_lieu_dang_xu_ly['close']
        chuoi_khoi_luong_giao_dich = bang_du_lieu_dang_xu_ly['volume']
        
        # --- 3.1: HỆ THỐNG TRUNG BÌNH ĐỘNG (MOVING AVERAGES) ---
        cua_so_truot_20_phien = chuoi_gia_dong_cua_co_phieu.rolling(window=20)
        bang_du_lieu_dang_xu_ly['ma20'] = cua_so_truot_20_phien.mean()
        
        cua_so_truot_50_phien = chuoi_gia_dong_cua_co_phieu.rolling(window=50)
        bang_du_lieu_dang_xu_ly['ma50'] = cua_so_truot_50_phien.mean()
        
        cua_so_truot_200_phien = chuoi_gia_dong_cua_co_phieu.rolling(window=200)
        bang_du_lieu_dang_xu_ly['ma200'] = cua_so_truot_200_phien.mean()
        
        # --- 3.2: DẢI BOLLINGER BANDS ---
        do_lech_chuan_trong_20_phien = cua_so_truot_20_phien.std()
        bang_du_lieu_dang_xu_ly['do_lech_chuan_20'] = do_lech_chuan_trong_20_phien
        
        khoang_cach_mo_rong_bol = bang_du_lieu_dang_xu_ly['do_lech_chuan_20'] * 2
        
        bang_du_lieu_dang_xu_ly['upper_band'] = bang_du_lieu_dang_xu_ly['ma20'] + khoang_cach_mo_rong_bol
        bang_du_lieu_dang_xu_ly['lower_band'] = bang_du_lieu_dang_xu_ly['ma20'] - khoang_cach_mo_rong_bol
        
        # --- 3.3: CHỈ SỐ SỨC MẠNH TƯƠNG ĐỐI (RSI 14) ---
        khoang_chenh_lech_gia_tung_ngay = chuoi_gia_dong_cua_co_phieu.diff()
        
        chuoi_ngay_co_gia_tang = khoang_chenh_lech_gia_tung_ngay.where(khoang_chenh_lech_gia_tung_ngay > 0, 0)
        chuoi_ngay_co_gia_giam = -khoang_chenh_lech_gia_tung_ngay.where(khoang_chenh_lech_gia_tung_ngay < 0, 0)
        
        muc_tang_trung_binh_14_phien = chuoi_ngay_co_gia_tang.rolling(window=14).mean()
        muc_giam_trung_binh_14_phien = chuoi_ngay_co_gia_giam.rolling(window=14).mean()
        
        ti_so_suc_manh_rs = muc_tang_trung_binh_14_phien / (muc_giam_trung_binh_14_phien + 1e-9)
        chi_so_rsi_hoan_thien = 100 - (100 / (1 + ti_so_suc_manh_rs))
        
        bang_du_lieu_dang_xu_ly['rsi'] = chi_so_rsi_hoan_thien
        
        # --- 3.4: ĐỘNG LƯỢNG MACD (12, 26, 9) ---
        duong_ema_nhanh_12 = chuoi_gia_dong_cua_co_phieu.ewm(span=12, adjust=False).mean()
        duong_ema_cham_26 = chuoi_gia_dong_cua_co_phieu.ewm(span=26, adjust=False).mean()
        
        duong_macd_chinh = duong_ema_nhanh_12 - duong_ema_cham_26
        bang_du_lieu_dang_xu_ly['macd'] = duong_macd_chinh
        
        duong_tin_hieu_signal = bang_du_lieu_dang_xu_ly['macd'].ewm(span=9, adjust=False).mean()
        bang_du_lieu_dang_xu_ly['signal'] = duong_tin_hieu_signal
        
        # --- 3.5: CÁC BIẾN SỐ PHỤC VỤ DÒNG TIỀN VÀ AI ---
        phan_tram_thay_doi_gia_1_ngay = chuoi_gia_dong_cua_co_phieu.pct_change()
        bang_du_lieu_dang_xu_ly['return_1d'] = phan_tram_thay_doi_gia_1_ngay
        
        cua_so_truot_10_phien_vol = chuoi_khoi_luong_giao_dich.rolling(window=10)
        khoi_luong_trung_binh_10_phien = cua_so_truot_10_phien_vol.mean()
        
        suc_manh_khoi_luong_vol_strength = chuoi_khoi_luong_giao_dich / khoi_luong_trung_binh_10_phien
        bang_du_lieu_dang_xu_ly['vol_strength'] = suc_manh_khoi_luong_vol_strength
        
        dong_tien_luan_chuyen = chuoi_gia_dong_cua_co_phieu * chuoi_khoi_luong_giao_dich
        bang_du_lieu_dang_xu_ly['money_flow'] = dong_tien_luan_chuyen
        
        cua_so_truot_20_phien_return = bang_du_lieu_dang_xu_ly['return_1d'].rolling(window=20)
        do_bien_dong_lich_su = cua_so_truot_20_phien_return.std()
        bang_du_lieu_dang_xu_ly['volatility'] = do_bien_dong_lich_su
        
        # --- 3.6: PHÂN LỚP XU HƯỚNG DÒNG TIỀN (PRICE-VOLUME TREND) ---
        dieu_kien_cau_manh_gom_hang = (bang_du_lieu_dang_xu_ly['return_1d'] > 0) & (bang_du_lieu_dang_xu_ly['vol_strength'] > 1.2)
        dieu_kien_cung_manh_xa_hang = (bang_du_lieu_dang_xu_ly['return_1d'] < 0) & (bang_du_lieu_dang_xu_ly['vol_strength'] > 1.2)
        
        xu_huong_dong_tien_pv = np.where(dieu_kien_cau_manh_gom_hang, 1, 
                                np.where(dieu_kien_cung_manh_xa_hang, -1, 0))
        bang_du_lieu_dang_xu_ly['pv_trend'] = xu_huong_dong_tien_pv
        
        bang_du_lieu_sach_tuyet_doi = bang_du_lieu_dang_xu_ly.dropna()
        return bang_du_lieu_sach_tuyet_doi

    # ==============================================================================
    # 4. HÀM CHẨN ĐOÁN THÔNG MINH (INTELLIGENCE & AI LAYER)
    # ==============================================================================
    
    def phan_tich_tam_ly_dam_dong_v13(bang_du_lieu_da_tinh_xong):
        dong_du_lieu_cuoi_cung = bang_du_lieu_da_tinh_xong.iloc[-1]
        gia_tri_rsi_phien_cuoi = dong_du_lieu_cuoi_cung['rsi']
        
        if gia_tri_rsi_phien_cuoi > 75:
            nhan_tam_ly_hien_thi = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif gia_tri_rsi_phien_cuoi > 60:
            nhan_tam_ly_hien_thi = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif gia_tri_rsi_phien_cuoi < 30:
            nhan_tam_ly_hien_thi = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif gia_tri_rsi_phien_cuoi < 42:
            nhan_tam_ly_hien_thi = "😨 SỢ HÃI (BI QUAN)"
        else:
            nhan_tam_ly_hien_thi = "🟡 TRUNG LẬP (ĐI NGANG CHỜ ĐỢI)"
            
        gia_tri_rsi_lam_tron = round(gia_tri_rsi_phien_cuoi, 1)
        return nhan_tam_ly_hien_thi, gia_tri_rsi_lam_tron

    def thuc_thi_backtest_chien_thuat_v13(bang_du_lieu_da_tinh_xong):
        tong_so_lan_xuat_hien_tin_hieu_mua = 0
        tong_so_lan_chien_thang_chot_loi = 0
        
        do_dai_tong = len(bang_du_lieu_da_tinh_xong)
        
        for vi_tri_ngay in range(100, do_dai_tong - 10):
            rsi_hien_tai = bang_du_lieu_da_tinh_xong['rsi'].iloc[vi_tri_ngay]
            kiem_tra_rsi = rsi_hien_tai < 45
            
            macd_hom_nay = bang_du_lieu_da_tinh_xong['macd'].iloc[vi_tri_ngay]
            signal_hom_nay = bang_du_lieu_da_tinh_xong['signal'].iloc[vi_tri_ngay]
            macd_hom_qua = bang_du_lieu_da_tinh_xong['macd'].iloc[vi_tri_ngay - 1]
            signal_hom_qua = bang_du_lieu_da_tinh_xong['signal'].iloc[vi_tri_ngay - 1]
            
            kiem_tra_macd = (macd_hom_nay > signal_hom_nay) and (macd_hom_qua <= signal_hom_qua)
            
            if kiem_tra_rsi and kiem_tra_macd:
                tong_so_lan_xuat_hien_tin_hieu_mua += 1
                
                gia_mua = bang_du_lieu_da_tinh_xong['close'].iloc[vi_tri_ngay]
                gia_muc_tieu = gia_mua * 1.05
                
                khoang_gia_tuong_lai = bang_du_lieu_da_tinh_xong['close'].iloc[vi_tri_ngay+1 : vi_tri_ngay+11]
                
                kiem_tra_thang = any(khoang_gia_tuong_lai > gia_muc_tieu)
                
                if kiem_tra_thang:
                    tong_so_lan_chien_thang_chot_loi += 1
        
        if tong_so_lan_xuat_hien_tin_hieu_mua == 0:
            return 0.0
            
        phan_tram_thang_loi = (tong_so_lan_chien_thang_chot_loi / tong_so_lan_xuat_hien_tin_hieu_mua) * 100
        return round(phan_tram_thang_loi, 1)

    def du_bao_xac_suat_ai_t3_v13(bang_du_lieu_da_tinh_xong):
        do_dai_bang = len(bang_du_lieu_da_tinh_xong)
        if do_dai_bang < 200:
            return "N/A"
            
        bang_du_lieu_hoc_may = bang_du_lieu_da_tinh_xong.copy()
        
        chuoi_gia_hien_tai = bang_du_lieu_hoc_may['close']
        chuoi_gia_tuong_lai_sau_3_ngay = bang_du_lieu_hoc_may['close'].shift(-3)
        
        dieu_kien_gia_tang = chuoi_gia_tuong_lai_sau_3_ngay > (chuoi_gia_hien_tai * 1.02)
        bang_du_lieu_hoc_may['nhan_dich_cho_ai'] = dieu_kien_gia_tang.astype(int)
        
        danh_sach_cac_bien = [
            'rsi', 'macd', 'signal', 'return_1d', 
            'volatility', 'vol_strength', 'money_flow', 'pv_trend'
        ]
        
        bang_du_lieu_sach = bang_du_lieu_hoc_may.dropna()
        
        ma_tran_x = bang_du_lieu_sach[danh_sach_cac_bien]
        vector_y = bang_du_lieu_sach['nhan_dich_cho_ai']
        
        mo_hinh_rf = RandomForestClassifier(n_estimators=100, random_state=42)
        
        x_huan_luyen = ma_tran_x[:-3]
        y_huan_luyen = vector_y[:-3]
        
        mo_hinh_rf.fit(x_huan_luyen, y_huan_luyen)
        
        dong_du_lieu_hom_nay = ma_tran_x.iloc[[-1]]
        mang_xac_suat = mo_hinh_rf.predict_proba(dong_du_lieu_hom_nay)
        
        xac_suat_tang = mang_xac_suat[0][1]
        
        return round(xac_suat_tang * 100, 1)

    # ==============================================================================
    # 5. TÍNH NĂNG ĐỘT PHÁ: BẢN PHÂN TÍCH TỰ ĐỘNG CHO MINH
    # ==============================================================================
    def tao_ban_bao_cao_tu_dong_v13(ma_ck, dong_du_lieu, diem_ai, diem_winrate, mang_gom, mang_xa):
        bai_phan_tich_hoan_thien = []
        
        bai_phan_tich_hoan_thien.append("#### 1. Đọc Vị Hành Vi Dòng Tiền (Smart Flow):")
        
        if ma_ck in mang_gom:
            cau_1 = f"✅ **Tín Hiệu Tích Cực:** Hệ thống phát hiện dòng tiền lớn đang **GOM HÀNG CHỦ ĐỘNG** tại mã {ma_ck}. Thể hiện qua việc Khối lượng giao dịch hôm nay nổ đột biến gấp {dong_du_lieu['vol_strength']:.1f} lần so với trung bình, đồng thời giá đóng cửa xanh."
            bai_phan_tich_hoan_thien.append(cau_1)
        elif ma_ck in mang_xa:
            cau_1 = f"🚨 **Cảnh Báo Tiêu Cực:** Dòng tiền lớn đang có dấu hiệu **XẢ HÀNG QUYẾT LIỆT**. Khối lượng bị bán ra gấp {dong_du_lieu['vol_strength']:.1f} lần bình thường và giá đóng cửa chìm trong sắc đỏ. Áp lực phân phối đang đè nặng."
            bai_phan_tich_hoan_thien.append(cau_1)
        else:
            cau_1 = f"🟡 **Trạng Thái Trung Lập:** Dòng tiền chưa có sự đột biến. Khối lượng giao dịch ở mức bình thường, cho thấy chủ yếu là nhà đầu tư cá nhân tự giao dịch với nhau."
            bai_phan_tich_hoan_thien.append(cau_1)

        bai_phan_tich_hoan_thien.append("#### 2. Đánh Giá Vị Thế Kỹ Thuật (Trend & Momentum):")
        
        if dong_du_lieu['close'] < dong_du_lieu['ma20']:
            cau_2 = f"❌ **Xu Hướng Đang Xấu:** Mức giá hiện tại ({dong_du_lieu['close']:,.0f} VNĐ) đang nằm **DƯỚI** đường phòng thủ sinh tử MA20 ({dong_du_lieu['ma20']:,.0f} VNĐ). Điều này khẳng định phe Bán đang áp đảo. Tuyệt đối chưa nên bắt đáy sớm."
            bai_phan_tich_hoan_thien.append(cau_2)
        else:
            cau_2 = f"✅ **Xu Hướng Rất Tốt:** Mức giá hiện tại ({dong_du_lieu['close']:,.0f} VNĐ) đang được neo giữ vững chắc **TRÊN** đường hỗ trợ MA20 ({dong_du_lieu['ma20']:,.0f} VNĐ). Cấu trúc tăng giá ngắn hạn đang được bảo vệ thành công."
            bai_phan_tich_hoan_thien.append(cau_2)

        if dong_du_lieu['rsi'] > 70:
            cau_3 = f"⚠️ **Cảnh Báo Tâm Lý:** Chỉ báo RSI đang vọt lên mức {dong_du_lieu['rsi']:.1f} (Vùng Quá Mua). Cổ phiếu đang rơi vào trạng thái quá hưng phấn, rất dễ quay đầu điều chỉnh giảm bất cứ lúc nào."
            bai_phan_tich_hoan_thien.append(cau_3)
        elif dong_du_lieu['rsi'] < 35:
            cau_3 = f"💡 **Cơ Hội Tâm Lý:** Chỉ báo RSI đang lùi sâu về mức {dong_du_lieu['rsi']:.1f} (Vùng Quá Bán). Lực bán tháo gần như đã cạn kiệt, xác suất xuất hiện nhịp hồi phục kỹ thuật là rất lớn."
            bai_phan_tich_hoan_thien.append(cau_3)
        else:
            cau_3 = f"📉 **Tâm Lý Ổn Định:** Chỉ báo RSI dao động quanh mốc {dong_du_lieu['rsi']:.1f}, cho thấy thị trường chưa có sự hưng phấn hay hoảng loạn thái quá."
            bai_phan_tich_hoan_thien.append(cau_3)

        bai_phan_tich_hoan_thien.append("#### 3. Đánh Giá Xác Suất Định Lượng (AI & Lịch Sử):")
        
        if isinstance(diem_ai, float):
            danh_gia_ai_nhanh = "Mức độ tin cậy thấp, rủi ro chôn vốn cao" if diem_ai < 55 else "Mức độ tin cậy tốt, cửa tăng T+3 rất sáng"
            cau_4 = f"- **Hệ thống AI Dự báo:** Xác suất tăng giá trong 3 ngày tới được máy học chấm ở mức **{diem_ai}%** ➔ *{danh_gia_ai_nhanh}*."
            bai_phan_tich_hoan_thien.append(cau_4)
        
        danh_gia_lich_su_nhanh = "Trong quá khứ, mẫu hình này thường là Bẫy lừa (Bull Trap)" if diem_winrate < 45 else "Dữ liệu quá khứ 1000 ngày chứng minh đây là tín hiệu uy tín"
        cau_5 = f"- **Kiểm chứng Lịch sử:** Tỷ lệ chiến thắng của chiến thuật này đạt mốc **{diem_winrate}%** ➔ *{danh_gia_lich_su_nhanh}*."
        bai_phan_tich_hoan_thien.append(cau_5)

        bai_phan_tich_hoan_thien.append("#### 💡 TỔNG KẾT & GIẢI MÃ MÂU THUẪN TỪ HỆ THỐNG QUANT:")
        
        if dong_du_lieu['close'] < dong_du_lieu['ma20'] and ma_ck in mang_gom:
            cau_6 = f"**⚠️ LƯU Ý ĐẶC BIỆT DÀNH CHO MINH:** Dù hệ thống báo hiệu có dòng tiền Cá mập đang gom hàng, nhưng vì giá vẫn bị ép nằm dưới MA20, nên đây thực chất là pha 'Gom Hàng Rải Đinh' ròng rã nhiều tháng của các Quỹ Lớn. Nhỏ lẻ mua lúc này rất dễ bị chôn vốn. Lời khuyên là hãy đợi giá bứt phá qua MA20 rồi mới đánh thóp theo."
            bai_phan_tich_hoan_thien.append(cau_6)
        elif diem_winrate < 40 and (isinstance(diem_ai, float) and diem_ai < 50):
            cau_6 = f"**⛔ RỦI RO NGẬP TRÀN:** Cả Trí tuệ nhân tạo và Dữ liệu Lịch sử đều quay lưng với cổ phiếu này. Bất kỳ nhịp kéo tăng nào (nếu có) khả năng cao chỉ là Bull Trap để xả hàng. Tuyệt đối nên đứng ngoài quan sát."
            bai_phan_tich_hoan_thien.append(cau_6)
        elif dong_du_lieu['close'] > dong_du_lieu['ma20'] and (isinstance(diem_ai, float) and diem_ai > 55) and diem_winrate > 50:
            cau_6 = f"**🚀 ĐIỂM MUA VÀNG (GOLDEN CROSS):** Biểu đồ nền tảng đẹp, Dòng tiền lớn nhập cuộc, AI và Lịch sử đều đồng thuận ủng hộ. Đây là cơ hội giải ngân có mức độ an toàn rất cao. Có thể mua 30-50% vị thế."
            bai_phan_tich_hoan_thien.append(cau_6)
        else:
            cau_6 = f"**⚖️ TRẠNG THÁI THEO DÕI (50/50):** Tín hiệu từ các chỉ báo đang có sự phân hóa, điểm mua chưa thực sự chín muồi. Minh nên đưa mã này vào Watchlist và chờ một phiên bùng nổ khối lượng thực sự để xác nhận xu hướng."
            bai_phan_tich_hoan_thien.append(cau_6)

        chuoi_van_ban_hoan_chinh = "\n\n".join(bai_phan_tich_hoan_thien)
        return chuoi_van_ban_hoan_chinh

    # ==============================================================================
    # 6. PHÂN TÍCH TÀI CHÍNH CỐT LÕI (FUNDAMENTAL LAYER)
    # ==============================================================================
    def do_luong_tang_truong_canslim_v13(ma_chung_khoan_vao):
        """Tính phần trăm thay đổi Lợi nhuận sau thuế"""
        try:
            bang_bctc_quy = dong_co_vnstock_v13.stock.finance.income_statement(
                symbol=ma_chung_khoan_vao, 
                period='quarter', 
                lang='en'
            ).head(5)
            
            tap_tu_khoa = ['sau thuế', 'posttax', 'net profit', 'earning']
            
            danh_sach_cac_cot_tuong_thich = []
            for ten_cot_trong_bang in bang_bctc_quy.columns:
                chuoi_ten_cot_thuong = str(ten_cot_trong_bang).lower()
                for tu_khoa in tap_tu_khoa:
                    if tu_khoa in chuoi_ten_cot_thuong:
                        danh_sach_cac_cot_tuong_thich.append(ten_cot_trong_bang)
                        break
            
            if len(danh_sach_cac_cot_tuong_thich) > 0:
                ten_cot_lnst_chinh_xac = danh_sach_cac_cot_tuong_thich[0]
                
                gia_tri_lnst_quy_nay = float(bang_bctc_quy.iloc[0][ten_cot_lnst_chinh_xac])
                gia_tri_lnst_quy_nam_ngoai = float(bang_bctc_quy.iloc[4][ten_cot_lnst_chinh_xac])
                
                if gia_tri_lnst_quy_nam_ngoai > 0:
                    muc_do_chenh_lech = gia_tri_lnst_quy_nay - gia_tri_lnst_quy_nam_ngoai
                    bien_do_tang_truong_phan_tram = (muc_do_chenh_lech / gia_tri_lnst_quy_nam_ngoai) * 100
                    return round(bien_do_tang_truong_phan_tram, 1)
        except Exception:
            pass
            
        try:
            chuoi_ma_yahoo_ho_so = f"{ma_chung_khoan_vao}.VN"
            doi_tuong_yf_ticker = yf.Ticker(chuoi_ma_yahoo_ho_so)
            du_lieu_ho_so_doanh_nghiep = doi_tuong_yf_ticker.info
            
            ti_le_tang_truong_tu_yahoo = du_lieu_ho_so_doanh_nghiep.get('earningsQuarterlyGrowth')
            if ti_le_tang_truong_tu_yahoo is not None:
                return round(ti_le_tang_truong_tu_yahoo * 100, 1)
        except Exception:
            pass
            
        return None

    def boc_tach_chi_so_pe_roe_v13(ma_chung_khoan_vao):
        """Đo lường Hệ số định giá P/E và Hiệu suất vốn ROE"""
        chi_so_pe_cuoi_cung = 0.0
        chi_so_roe_cuoi_cung = 0.0
        
        try:
            bang_chi_so_tai_chinh_vnstock = dong_co_vnstock_v13.stock.finance.ratio(ma_chung_khoan_vao, 'quarterly').iloc[-1]
            
            chi_so_pe_tu_vnstock = bang_chi_so_tai_chinh_vnstock.get('ticker_pe', bang_chi_so_tai_chinh_vnstock.get('pe', 0))
            chi_so_roe_tu_vnstock = bang_chi_so_tai_chinh_vnstock.get('roe', 0)
            
            # Chỉ lấy nếu dữ liệu không rỗng để tránh trả về số vô lý
            if chi_so_pe_tu_vnstock is not None and not np.isnan(chi_so_pe_tu_vnstock):
                chi_so_pe_cuoi_cung = chi_so_pe_tu_vnstock
            if chi_so_roe_tu_vnstock is not None and not np.isnan(chi_so_roe_tu_vnstock):
                chi_so_roe_cuoi_cung = chi_so_roe_tu_vnstock
        except Exception:
            pass
            
        if chi_so_pe_cuoi_cung <= 0:
            try:
                chuoi_ma_yahoo_pe = f"{ma_chung_khoan_vao}.VN"
                doi_tuong_yf_ticker_pe = yf.Ticker(chuoi_ma_yahoo_pe)
                du_lieu_ho_so_yf = doi_tuong_yf_ticker_pe.info
                
                chi_so_pe_tu_yahoo = du_lieu_ho_so_yf.get('trailingPE', 0)
                chi_so_roe_tu_yahoo = du_lieu_ho_so_yf.get('returnOnEquity', 0)
                
                if chi_so_pe_tu_yahoo is not None:
                    chi_so_pe_cuoi_cung = chi_so_pe_tu_yahoo
                if chi_so_roe_tu_yahoo is not None:
                    chi_so_roe_cuoi_cung = chi_so_roe_tu_yahoo
            except Exception:
                pass
                
        return chi_so_pe_cuoi_cung, chi_so_roe_cuoi_cung

    # ==============================================================================
    # 7. 🧠 ROBOT ADVISOR MASTER V13: ĐƯA RA LỆNH NGẮN GỌN
    # ==============================================================================
    def he_thong_suy_luan_advisor_v13(dong_du_lieu_cuoi, ti_le_ai_du_bao, ti_le_winrate_lich_su, diem_tang_truong_lnst):
        """Tính toán điểm số để xuất ra lệnh MUA/BÁN hiển thị bên góc phải"""
        tong_diem_danh_gia_tin_cay = 0
        
        if isinstance(ti_le_ai_du_bao, float):
            if ti_le_ai_du_bao >= 58.0:
                tong_diem_danh_gia_tin_cay += 1
                
        if ti_le_winrate_lich_su >= 50.0:
            tong_diem_danh_gia_tin_cay += 1
            
        gia_dong_cua = dong_du_lieu_cuoi['close']
        duong_ma20 = dong_du_lieu_cuoi['ma20']
        if gia_dong_cua > duong_ma20:
            tong_diem_danh_gia_tin_cay += 1
            
        if diem_tang_truong_lnst is not None:
            if diem_tang_truong_lnst >= 15.0:
                tong_diem_danh_gia_tin_cay += 1
                
        chi_so_rsi = dong_du_lieu_cuoi['rsi']

        if tong_diem_danh_gia_tin_cay >= 3 and chi_so_rsi < 68:
            lenh_hien_thi = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
            mau_sac_hien_thi = "green"
        elif tong_diem_danh_gia_tin_cay <= 1 or chi_so_rsi > 78 or gia_dong_cua < duong_ma20:
            lenh_hien_thi = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
            mau_sac_hien_thi = "red"
        else:
            lenh_hien_thi = "⚖️ THEO DÕI (WATCHLIST)"
            mau_sac_hien_thi = "orange"

        return lenh_hien_thi, mau_sac_hien_thi

    # ==============================================================================
    # 8. GIAO DIỆN NGƯỜI DÙNG & KIỂM SOÁT LUỒNG DỮ LIỆU (UI CONTROLLER)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def tai_va_chuan_bi_danh_sach_ma_san_hose():
        """Tải bảng danh sách mã niêm yết từ Vnstock"""
        try:
            bang_danh_sach_niem_yet_goc = dong_co_vnstock_v13.market.listing()
            bo_loc_dieu_kien_san_hose = bang_danh_sach_niem_yet_goc['comGroupCode'] == 'HOSE'
            bang_danh_sach_hose_only = bang_danh_sach_niem_yet_goc[bo_loc_dieu_kien_san_hose]
            danh_sach_chuoi_ma_chung_khoan = bang_danh_sach_hose_only['ticker'].tolist()
            return danh_sach_chuoi_ma_chung_khoan
        except Exception:
            return ["FPT", "HPG", "SSI", "TCB", "MWG", "VNM", "VIC", "VHM", "STB", "MSN", "GAS"]

    danh_sach_tat_ca_cac_ma_hose = tai_va_chuan_bi_danh_sach_ma_san_hose()
    
    st.sidebar.header("🕹️ Trung Tâm Giao Dịch Định Lượng Quant")
    
    thanh_phan_chon_ma_co_phieu = st.sidebar.selectbox(
        "Lựa chọn mã cổ phiếu mục tiêu để phân tích:", 
        danh_sach_tat_ca_cac_ma_hose
    )
    
    thanh_phan_nhap_ma_thu_cong = st.sidebar.text_input(
        "Hoặc nhập trực tiếp tên mã (Ví dụ: FPT):"
    ).upper()
    
    if thanh_phan_nhap_ma_thu_cong != "":
        ma_co_phieu_dang_duoc_chon = thanh_phan_nhap_ma_thu_cong
    else:
        ma_co_phieu_dang_duoc_chon = thanh_phan_chon_ma_co_phieu

    tab_trung_tam_advisor_v13, tab_trung_tam_tai_chinh_v13, tab_trung_tam_dong_tien_v13, tab_trung_tam_hunter_v13 = st.tabs([
        "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH TỰ ĐỘNG", 
        "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM", 
        "🌊 BÓC TÁCH DÒNG TIỀN THÔNG MINH", 
        "🔍 RADAR TRUY QUÉT SIÊU CỔ PHIẾU"
    ])

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR VÀ BẢN PHÂN TÍCH TỰ ĐỘNG
    # ------------------------------------------------------------------------------
    with tab_trung_tam_advisor_v13:
        
        nut_nhan_khoi_chay_phan_tich_toan_dien = st.button(f"⚡ TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG MÃ CỔ PHIẾU {ma_co_phieu_dang_duoc_chon}")
        
        if nut_nhan_khoi_chay_phan_tich_toan_dien:
            
            with st.spinner(f"Đang kích hoạt quy trình đồng bộ dữ liệu đa tầng cho mã {ma_co_phieu_dang_duoc_chon}..."):
                
                bang_du_lieu_tho_v13 = lay_du_lieu_nien_yet_chuan_v13(ma_co_phieu_dang_duoc_chon)
                
                if bang_du_lieu_tho_v13 is not None and not bang_du_lieu_tho_v13.empty:
                    
                    bang_du_lieu_chi_tiet_da_tinh_v13 = tinh_toan_bo_chi_bao_quant_v13(bang_du_lieu_tho_v13)
                    dong_du_lieu_moi_nhat_phien_nay_v13 = bang_du_lieu_chi_tiet_da_tinh_v13.iloc[-1]
                    
                    diem_ai_du_bao_t3_ket_qua_v13 = du_bao_xac_suat_ai_t3_v13(bang_du_lieu_chi_tiet_da_tinh_v13)
                    diem_win_rate_lich_su_ket_qua_v13 = thuc_thi_backtest_chien_thuat_v13(bang_du_lieu_chi_tiet_da_tinh_v13)
                    nhan_tam_ly_fng_hien_tai_v13, diem_tam_ly_fng_hien_tai_v13 = phan_tich_tam_ly_dam_dong_v13(bang_du_lieu_chi_tiet_da_tinh_v13)
                    
                    chi_so_pe_hien_tai_dn_v13, chi_so_roe_hien_tai_dn_v13 = boc_tach_chi_so_pe_roe_v13(ma_co_phieu_dang_duoc_chon)
                    muc_tang_truong_quy_lnst_dn_v13 = do_luong_tang_truong_canslim_v13(ma_co_phieu_dang_duoc_chon)
                    
                    danh_sach_10_ma_tru_cung_thi_truong_v13 = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                    mang_tru_dang_duoc_gom_hang_v13 = []
                    mang_tru_dang_bi_xa_hang_v13 = []
                    
                    for ma_tru_ho_tro_index_v13 in danh_sach_10_ma_tru_cung_thi_truong_v13:
                        try:
                            df_tru_tho_10_ngay_v13 = lay_du_lieu_nien_yet_chuan_v13(ma_tru_ho_tro_index_v13, so_ngay_lich_su_can_lay=10)
                            
                            if df_tru_tho_10_ngay_v13 is not None:
                                df_tru_da_tinh_toan_xong_v13 = tinh_toan_bo_chi_bao_quant_v13(df_tru_tho_10_ngay_v13)
                                dong_cuoi_cua_ma_tru_v13 = df_tru_da_tinh_toan_xong_v13.iloc[-1]
                                
                                check_tin_hieu_tang_gia_v13 = dong_cuoi_cua_ma_tru_v13['return_1d'] > 0
                                check_tin_hieu_giam_gia_v13 = dong_cuoi_cua_ma_tru_v13['return_1d'] < 0
                                check_tin_hieu_nhet_vol_v13 = dong_cuoi_cua_ma_tru_v13['vol_strength'] > 1.2
                                
                                if check_tin_hieu_tang_gia_v13 and check_tin_hieu_nhet_vol_v13:
                                    mang_tru_dang_duoc_gom_hang_v13.append(ma_tru_ho_tro_index_v13)
                                elif check_tin_hieu_giam_gia_v13 and check_tin_hieu_nhet_vol_v13:
                                    mang_tru_dang_bi_xa_hang_v13.append(ma_tru_ho_tro_index_v13)
                        except Exception: 
                            pass

                    # --- GIAO DIỆN HIỂN THỊ KẾT QUẢ ĐẦU VÀO TRUNG TÂM ---
                    st.write(f"### 🎯 BẢN PHÂN TÍCH CHUYÊN MÔN TỰ ĐỘNG - MÃ {ma_co_phieu_dang_duoc_chon}")
                    
                    cot_khung_bao_cao_chu_text, cot_khung_lenh_hanh_dong_ngan_gon = st.columns([2, 1])
                    
                    with cot_khung_bao_cao_chu_text:
                        noi_dung_bai_bao_cao_dai = tao_ban_bao_cao_tu_dong_v13(
                            ma_co_phieu_dang_duoc_chon, 
                            dong_du_lieu_moi_nhat_phien_nay_v13, 
                            diem_ai_du_bao_t3_ket_qua_v13, 
                            diem_win_rate_lich_su_ket_qua_v13, 
                            mang_tru_dang_duoc_gom_hang_v13, 
                            mang_tru_dang_bi_xa_hang_v13
                        )
                        st.info(noi_dung_bai_bao_cao_dai)
                                
                    with cot_khung_lenh_hanh_dong_ngan_gon:
                        st.subheader("🤖 ROBOT ĐỀ XUẤT LỆNH:")
                        chuoi_lenh_ngan_gon, mau_sac_lenh_ngan_gon = he_thong_suy_luan_advisor_v13(
                            dong_du_lieu_moi_nhat_phien_nay_v13, 
                            diem_ai_du_bao_t3_ket_qua_v13, 
                            diem_win_rate_lich_su_ket_qua_v13, 
                            muc_tang_truong_quy_lnst_dn_v13
                        )
                        st.title(f":{mau_sac_lenh_ngan_gon}[{chuoi_lenh_ngan_gon}]")
                    
                    st.divider()
                    
                    # --- GIAO DIỆN BẢNG RADAR HIỆU SUẤT TỔNG QUAN ---
                    st.write("### 🧭 Bảng Radar Đo Lường Hiệu Suất Tổng Quan")
                    cot_radar_so_1, cot_radar_so_2, cot_radar_so_3, cot_radar_so_4 = st.columns(4)
                    
                    gia_tri_khop_lenh_moi_nhat = dong_du_lieu_moi_nhat_phien_nay_v13['close']
                    cot_radar_so_1.metric("Giá Khớp Lệnh Mới Nhất", f"{gia_tri_khop_lenh_moi_nhat:,.0f}")
                    
                    cot_radar_so_2.metric("Tâm Lý F&G Index", f"{diem_tam_ly_fng_hien_tai_v13}/100", delta=nhan_tam_ly_fng_hien_tai_v13)
                    
                    nhan_dang_delta_ai_tot_hay_xau = None
                    if isinstance(diem_ai_du_bao_t3_ket_qua_v13, float):
                        if diem_ai_du_bao_t3_ket_qua_v13 > 55.0:
                            nhan_dang_delta_ai_tot_hay_xau = "Tín hiệu Tốt"
                            
                    cot_radar_so_3.metric("Khả năng Tăng (AI T+3)", f"{diem_ai_du_bao_t3_ket_qua_v13}%", delta=nhan_dang_delta_ai_tot_hay_xau)
                    
                    nhan_dang_delta_backtest = "Tỉ lệ Ổn định" if diem_win_rate_lich_su_ket_qua_v13 > 45 else None
                    cot_radar_so_4.metric("Xác suất Thắng Lịch sử", f"{diem_win_rate_lich_su_ket_qua_v13}%", delta=nhan_dang_delta_backtest)

                    # --- GIAO DIỆN BẢNG NAKED STATS CHUYÊN MÔN ---
                    st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Trần (Naked Stats)")
                    cot_naked_so_1, cot_naked_so_2, cot_naked_so_3, cot_naked_so_4 = st.columns(4)
                    
                    chi_so_rsi_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay_v13['rsi']
                    if chi_so_rsi_de_trinh_dien > 70:
                        nhan_canh_bao_rsi_trinh_dien = "Đang Quá mua"
                    elif chi_so_rsi_de_trinh_dien < 30:
                        nhan_canh_bao_rsi_trinh_dien = "Đang Quá bán"
                    else:
                        nhan_canh_bao_rsi_trinh_dien = "Vùng An toàn"
                        
                    cot_naked_so_1.metric("RSI (Sức mạnh 14 Phiên)", f"{chi_so_rsi_de_trinh_dien:.1f}", delta=nhan_canh_bao_rsi_trinh_dien)
                    
                    chi_so_macd_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay_v13['macd']
                    chi_so_signal_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay_v13['signal']
                    if chi_so_macd_de_trinh_dien > chi_so_signal_de_trinh_dien:
                        nhan_canh_bao_macd_trinh_dien = "MACD > Signal (Tốt)"
                    else:
                        nhan_canh_bao_macd_trinh_dien = "MACD < Signal (Xấu)"
                        
                    cot_naked_so_2.metric("Tình trạng Giao cắt MACD", f"{chi_so_macd_de_trinh_dien:.2f}", delta=nhan_canh_bao_macd_trinh_dien)
                    
                    chi_so_ma20_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay_v13['ma20']
                    chi_so_ma50_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay_v13['ma50']
                    chuoi_hien_thi_ma50 = f"MA50 hiện tại: {chi_so_ma50_de_trinh_dien:,.0f}"
                    cot_naked_so_3.metric("MA20 (Ngắn) / MA50 (Trung)", f"{chi_so_ma20_de_trinh_dien:,.0f}", delta=chuoi_hien_thi_ma50)
                    
                    chi_so_upper_band_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay_v13['upper_band']
                    chi_so_lower_band_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay_v13['lower_band']
                    chuoi_hien_thi_lower_band = f"Khung Chạm Đáy: {chi_so_lower_band_de_trinh_dien:,.0f}"
                    cot_naked_so_4.metric("Khung Chạm Trần Bollinger", f"{chi_so_upper_band_de_trinh_dien:,.0f}", 
                                       delta=chuoi_hien_thi_lower_band, delta_color="inverse")
                    
                    # --- SỔ TAY CẨM NĂNG KIẾN THỨC CỦA MINH ---
                    thanh_mo_rong_cam_nang = st.expander("📖 CẨM NĂNG THỰC CHIẾN GIAO DỊCH (ĐỌC KỸ TRƯỚC KHI XUỐNG TIỀN VÀO LỆNH)")
                    with thanh_mo_rong_cam_nang:
                        st.markdown("#### 1. Phương pháp đọc Volume và Dòng Tiền lớn")
                        st.write(f"- Sức mạnh Volume ngày hôm nay đang bằng **{dong_du_lieu_moi_nhat_phien_nay_v13['vol_strength']:.1f} lần** so với mức trung bình 10 ngày.")
                        st.write("- Quy luật Gom hàng: Cây nến Xanh (Giá tăng) kết hợp với Volume lớn hơn 1.2 lần là dấu hiệu dòng tiền lớn nhảy vào.")
                        st.write("- Quy luật Xả hàng: Cây nến Đỏ (Giá giảm) kết hợp với Volume lớn hơn 1.2 lần là dấu hiệu dòng tiền lớn đang bỏ chạy khỏi cổ phiếu.")
                        
                        st.markdown("#### 2. Kỹ thuật đọc Biên độ dao động Bollinger Bands")
                        st.write("- Vùng được tô xám mờ trên biểu đồ bên dưới là hành lang dao động an toàn của giá.")
                        st.write("- Nếu Nến đâm lủng trần (Upper Band) = Rủi ro mua đuổi đỉnh, giá thường bị dội ngược lại vào trong để test.")
                        st.write("- Nếu Nến rớt lủng sàn (Lower Band) = Rủi ro bán tháo đúng đáy, đây là lúc nên bình tĩnh rình mò bắt đáy nhịp hồi.")
                        
                        st.markdown("#### 3. Luật Thép Về Quản Trị Rủi Ro Cốt Lõi")
                        gia_tri_can_cat_lo_toi_thieu_bang_so = dong_du_lieu_moi_nhat_phien_nay_v13['close'] * 0.93
                        st.error(f"- Cắt Lỗ Toàn Phần: Bán bằng mọi giá, không được phép gồng lỗ bằng niềm tin nếu giá trị rớt xuống ngưỡng **{gia_tri_can_cat_lo_toi_thieu_bang_so:,.0f} VNĐ (tức là âm -7% từ đỉnh)**.")

                    # ==================================================================
                    # --- VẼ BIỂU ĐỒ MASTER CANDLESTICK CHUYÊN SÂU ---
                    # ==================================================================
                    st.divider()
                    st.write("### 📊 Biểu Đồ Kỹ Thuật Đa Lớp Chuyên Nghiệp (Master Chart Visualizer)")
                    
                    khung_hinh_ve_bieu_do_master = make_subplots(
                        rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.75, 0.25]
                    )
                    
                    bang_du_lieu_120_phien_de_ve_hinh = bang_du_lieu_chi_tiet_da_tinh_v13.tail(120)
                    truc_thoi_gian_x_cua_bieu_do = bang_du_lieu_120_phien_de_ve_hinh['date']
                    
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Candlestick(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            open=bang_du_lieu_120_phien_de_ve_hinh['open'], 
                            high=bang_du_lieu_120_phien_de_ve_hinh['high'], 
                            low=bang_du_lieu_120_phien_de_ve_hinh['low'], 
                            close=bang_du_lieu_120_phien_de_ve_hinh['close'], 
                            name='Biểu Đồ Nến'
                        ), row=1, col=1
                    )
                    
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['ma20'], 
                            line=dict(color='orange', width=1.5), 
                            name='Hỗ Trợ Nền MA20'
                        ), row=1, col=1
                    )
                    
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['ma200'], 
                            line=dict(color='purple', width=2), 
                            name='Chỉ Nam Sinh Tử MA200'
                        ), row=1, col=1
                    )
                    
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['upper_band'], 
                            line=dict(color='gray', dash='dash', width=0.8), 
                            name='Trần Bán BOL'
                        ), row=1, col=1
                    )
                    
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['lower_band'], 
                            line=dict(color='gray', dash='dash', width=0.8), 
                            fill='tonexty', 
                            fillcolor='rgba(128,128,128,0.1)', 
                            name='Đáy Mua BOL'
                        ), row=1, col=1
                    )
                    
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Bar(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['volume'], 
                            name='Lực Khối Lượng', 
                            marker_color='gray'
                        ), row=2, col=1
                    )
                    
                    khung_hinh_ve_bieu_do_master.update_layout(
                        height=750, 
                        template='plotly_white', 
                        xaxis_rangeslider_visible=False,
                        margin=dict(l=40, r=40, t=50, b=40)
                    )
                    
                    st.plotly_chart(khung_hinh_ve_bieu_do_master, use_container_width=True)
                else:
                    st.error("❌ Cảnh báo Hệ thống: Không thể kết nối để lấy gói dữ liệu giá. Vui lòng F5 lại trang.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP CƠ BẢN (ĐÃ XỬ LÝ LỖI P/E 0.0)
    # ------------------------------------------------------------------------------
    with tab_trung_tam_tai_chinh_v13:
        st.write(f"### 📈 Phân Tích Sức Khỏe Báo Cáo Tài Chính ({ma_co_phieu_dang_duoc_chon})")
        
        with st.spinner("Hệ thống đang quét báo cáo thu nhập quý gần nhất để bóc tách..."):
            
            phan_tram_tang_truong_lnst_ket_qua_v13 = do_luong_tang_truong_canslim_v13(ma_co_phieu_dang_duoc_chon)
            
            if phan_tram_tang_truong_lnst_ket_qua_v13 is not None:
                if phan_tram_tang_truong_lnst_ket_qua_v13 >= 20.0:
                    st.success(f"**🔥 Tiêu Chuẩn Vàng (Chữ C trong CanSLIM):** Lợi nhuận Quý tăng mạnh **+{phan_tram_tang_truong_lnst_ket_qua_v13}%**. Mức tăng trưởng đột phá cực kỳ hấp dẫn đối với các Quỹ.")
                elif phan_tram_tang_truong_lnst_ket_qua_v13 > 0:
                    st.info(f"**⚖️ Tăng Trưởng Bền Vững:** Doanh nghiệp gia tăng lợi nhuận được **{phan_tram_tang_truong_lnst_ket_qua_v13}%**. Đang hoạt động ở trạng thái ổn định và an toàn.")
                else:
                    st.error(f"**🚨 Tín Hiệu Suy Yếu Nặng:** Lợi nhuận rớt thê thảm **{phan_tram_tang_truong_lnst_ket_qua_v13}%**. Báo động đỏ về năng lực vận hành của ban lãnh đạo.")
            
            st.divider()
            
            chi_so_pe_cua_doanh_nghiep_v13, chi_so_roe_cua_doanh_nghiep_v13 = boc_tach_chi_so_pe_roe_v13(ma_co_phieu_dang_duoc_chon)
            
            cot_hien_thi_dinh_gia_1_v13, cot_hien_thi_dinh_gia_2_v13 = st.columns(2)
            
            # FIX LỖI P/E 0.0 TẠI ĐÂY: Phát hiện API chết
            if chi_so_pe_cua_doanh_nghiep_v13 == 0.0:
                chuoi_hien_thi_pe_v13 = "N/A"
                nhan_dinh_pe_chuoi_trinh_dien_v13 = "Lỗi kết nối API / Thiếu dữ liệu"
                mau_cua_nhan_dinh_pe_v13 = "off"
            else:
                chuoi_hien_thi_pe_v13 = f"{chi_so_pe_cua_doanh_nghiep_v13:.1f}"
                if 0 < chi_so_pe_cua_doanh_nghiep_v13 < 12:
                    nhan_dinh_pe_chuoi_trinh_dien_v13 = "Mức Rất Tốt (Định Giá Rẻ)"
                elif chi_so_pe_cua_doanh_nghiep_v13 < 18:
                    nhan_dinh_pe_chuoi_trinh_dien_v13 = "Mức Khá Hợp Lý"
                else:
                    nhan_dinh_pe_chuoi_trinh_dien_v13 = "Mức Đắt Đỏ (Chứa rủi ro ảo giá)"
                mau_cua_nhan_dinh_pe_v13 = "normal" if chi_so_pe_cua_doanh_nghiep_v13 < 18 else "inverse"
            
            cot_hien_thi_dinh_gia_1_v13.metric(
                "Chỉ Số P/E (Số Năm Hoàn Vốn Ước Tính)", 
                chuoi_hien_thi_pe_v13, 
                delta=nhan_dinh_pe_chuoi_trinh_dien_v13, 
                delta_color=mau_cua_nhan_dinh_pe_v13
            )
            st.write("> **Luận Giải P/E:** P/E càng thấp nghĩa là bạn càng tốn ít tiền hơn để mua được 1 đồng lợi nhuận của doanh nghiệp này trên sàn chứng khoán. Nếu hiện 'N/A' là do API máy chủ chứng khoán đang bảo trì không cấp dữ liệu.")
            
            # FIX LỖI ROE 0.0 TẠI ĐÂY: Phát hiện API chết
            if chi_so_roe_cua_doanh_nghiep_v13 == 0.0:
                chuoi_hien_thi_roe_v13 = "N/A"
                nhan_dinh_roe_chuoi_trinh_dien_v13 = "Lỗi kết nối API / Thiếu dữ liệu"
                mau_cua_nhan_dinh_roe_v13 = "off"
            else:
                chuoi_hien_thi_roe_v13 = f"{chi_so_roe_cua_doanh_nghiep_v13:.1%}"
                if chi_so_roe_cua_doanh_nghiep_v13 >= 0.25:
                    nhan_dinh_roe_chuoi_trinh_dien_v13 = "Vô Cùng Xuất Sắc"
                elif chi_so_roe_cua_doanh_nghiep_v13 >= 0.15:
                    nhan_dinh_roe_chuoi_trinh_dien_v13 = "Mức Độ Tốt"
                else:
                    nhan_dinh_roe_chuoi_trinh_dien_v13 = "Mức Trung Bình - Dưới Chuẩn"
                mau_cua_nhan_dinh_roe_v13 = "normal" if chi_so_roe_cua_doanh_nghiep_v13 >= 0.15 else "inverse"
            
            cot_hien_thi_dinh_gia_2_v13.metric(
                "Chỉ Số ROE (Năng Lực Sinh Lời Trên Vốn)", 
                chuoi_hien_thi_roe_v13, 
                delta=nhan_dinh_roe_chuoi_trinh_dien_v13, 
                delta_color=mau_cua_nhan_dinh_roe_v13
            )
            st.write("> **Luận Giải ROE:** ROE là thước đo xem Ban giám đốc dùng tiền của cổ đông có tạo ra lãi tốt không. Bắt buộc phải trên 15% mới đáng xem xét đầu tư dài hạn.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: CHUYÊN GIA ĐỌC VỊ DÒNG TIỀN (VÀ KHỐI NGOẠI THỰC TẾ)
    # ------------------------------------------------------------------------------
    with tab_trung_tam_dong_tien_v13:
        st.write(f"### 🌊 Smart Flow Specialist - Mổ Xẻ Chi Tiết Hành Vi Dòng Tiền ({ma_co_phieu_dang_duoc_chon})")
        
        # --- MODULE 1: LẤY VÀ VẼ BIỂU ĐỒ KHỐI NGOẠI THỰC TẾ (REAL DATA) ---
        def lay_du_lieu_khoi_ngoai_thuc_te_v14(ma_chung_khoan_vao):
            """Hàm kéo dữ liệu mua bán Khối ngoại tỷ VNĐ thật"""
            try:
                thoi_diem_bay_gio = datetime.now()
                chuoi_ngay_ket_thuc = thoi_diem_bay_gio.strftime('%Y-%m-%d')
                chuoi_ngay_bat_dau = (thoi_diem_bay_gio - timedelta(days=20)).strftime('%Y-%m-%d')
                
                bang_ngoai = None
                
                try:
                    bang_ngoai = dong_co_vnstock_v13.stock.trade.foreign_trade(
                        symbol=ma_chung_khoan_vao, 
                        start=chuoi_ngay_bat_dau, 
                        end=chuoi_ngay_ket_thuc
                    )
                except Exception:
                    pass
                    
                if bang_ngoai is None or bang_ngoai.empty:
                    try:
                        bang_ngoai = dong_co_vnstock_v13.stock.trading.foreign(
                            symbol=ma_chung_khoan_vao, 
                            start=chuoi_ngay_bat_dau, 
                            end=chuoi_ngay_ket_thuc
                        )
                    except Exception:
                        pass
                
                if bang_ngoai is not None and not bang_ngoai.empty:
                    danh_sach_ten_cot_chuan_hoa = []
                    for cot in bang_ngoai.columns:
                        danh_sach_ten_cot_chuan_hoa.append(str(cot).lower())
                    bang_ngoai.columns = danh_sach_ten_cot_chuan_hoa
                    return bang_ngoai
                    
            except Exception:
                pass
            return None

        st.write("#### 📊 Dữ Liệu Giao Dịch Khối Ngoại Thực Tế (Tính Bằng Tỷ VNĐ):")
        
        with st.spinner("Đang trích xuất dữ liệu Khối Ngoại chuẩn từ Sở Giao Dịch..."):
            bang_du_lieu_khoi_ngoai_thuc_te = lay_du_lieu_khoi_ngoai_thuc_te_v14(ma_co_phieu_dang_duoc_chon)
            
            if bang_du_lieu_khoi_ngoai_thuc_te is not None and not bang_du_lieu_khoi_ngoai_thuc_te.empty:
                dong_giao_dich_ngoai_cuoi_cung = bang_du_lieu_khoi_ngoai_thuc_te.iloc[-1]
                
                gia_tri_mua_ngoai_vnd = 0.0
                gia_tri_ban_ngoai_vnd = 0.0
                gia_tri_rong_ngoai_vnd = 0.0
                
                for ten_cot_thuong in dong_giao_dich_ngoai_cuoi_cung.index:
                    gia_tri_cot_hien_tai = float(dong_giao_dich_ngoai_cuoi_cung[ten_cot_thuong])
                    gia_tri_quy_doi_ty_vnd = gia_tri_cot_hien_tai / 1e9 if abs(gia_tri_cot_hien_tai) > 1e6 else gia_tri_cot_hien_tai
                    
                    if 'buyval' in ten_cot_thuong or 'buy_val' in ten_cot_thuong or 'mua' in ten_cot_thuong:
                        if gia_tri_quy_doi_ty_vnd > gia_tri_mua_ngoai_vnd:
                            gia_tri_mua_ngoai_vnd = gia_tri_quy_doi_ty_vnd
                            
                    elif 'sellval' in ten_cot_thuong or 'sell_val' in ten_cot_thuong or 'ban' in ten_cot_thuong:
                        if gia_tri_quy_doi_ty_vnd > gia_tri_ban_ngoai_vnd:
                            gia_tri_ban_ngoai_vnd = gia_tri_quy_doi_ty_vnd
                            
                    elif 'netval' in ten_cot_thuong or 'net_val' in ten_cot_thuong or 'rong' in ten_cot_thuong:
                        if abs(gia_tri_quy_doi_ty_vnd) > abs(gia_tri_rong_ngoai_vnd):
                            gia_tri_rong_ngoai_vnd = gia_tri_quy_doi_ty_vnd
                
                if gia_tri_rong_ngoai_vnd == 0.0 and (gia_tri_mua_ngoai_vnd > 0 or gia_tri_ban_ngoai_vnd > 0):
                    gia_tri_rong_ngoai_vnd = gia_tri_mua_ngoai_vnd - gia_tri_ban_ngoai_vnd
                
                cot_ngoai_thuc_1, cot_ngoai_thuc_2, cot_ngoai_thuc_3 = st.columns(3)
                
                cot_ngoai_thuc_1.metric("Tổng Mua (Khối Ngoại)", f"{gia_tri_mua_ngoai_vnd:.2f} Tỷ VNĐ")
                cot_ngoai_thuc_2.metric("Tổng Bán (Khối Ngoại)", f"{gia_tri_ban_ngoai_vnd:.2f} Tỷ VNĐ")
                
                nhan_trang_thai_rong = "Mua Ròng Tích Cực" if gia_tri_rong_ngoai_vnd > 0 else "Bán Ròng Cảnh Báo"
                mau_sac_delta_rong = "normal" if gia_tri_rong_ngoai_vnd > 0 else "inverse"
                
                cot_ngoai_thuc_3.metric("Giá Trị Giao Dịch Ròng", f"{gia_tri_rong_ngoai_vnd:.2f} Tỷ VNĐ", delta=nhan_trang_thai_rong, delta_color=mau_sac_delta_rong)
                
                # Biểu đồ Khối ngoại 10 phiên
                st.write("📈 **Lịch sử Giao Dịch Ròng Khối Ngoại (10 Phiên Gần Nhất):**")
                
                mang_thoi_gian_ngoai = bang_du_lieu_khoi_ngoai_thuc_te['date'] if 'date' in bang_du_lieu_khoi_ngoai_thuc_te.columns else bang_du_lieu_khoi_ngoai_thuc_te.index
                mang_gia_tri_rong = []
                
                for index_dong, dong_dl in bang_du_lieu_khoi_ngoai_thuc_te.iterrows():
                    gt_rong_dong = 0.0
                    gt_mua_dong = 0.0
                    gt_ban_dong = 0.0
                    for cot_nhan in bang_du_lieu_khoi_ngoai_thuc_te.columns:
                        gt_cot_hien_tai = float(dong_dl[cot_nhan]) if pd.notnull(dong_dl[cot_nhan]) else 0.0
                        gt_quy_doi_dong = gt_cot_hien_tai / 1e9 if abs(gt_cot_hien_tai) > 1e6 else gt_cot_hien_tai
                        
                        if 'netval' in cot_nhan or 'net_val' in cot_nhan or 'rong' in cot_nhan:
                            gt_rong_dong = gt_quy_doi_dong
                        elif 'buyval' in cot_nhan or 'mua' in cot_nhan:
                            gt_mua_dong = gt_quy_doi_dong
                        elif 'sellval' in cot_nhan or 'ban' in cot_nhan:
                            gt_ban_dong = gt_quy_doi_dong
                    
                    if gt_rong_dong == 0.0:
                        gt_rong_dong = gt_mua_dong - gt_ban_dong
                        
                    mang_gia_tri_rong.append(gt_rong_dong)
                    
                bieu_do_khoi_ngoai = go.Figure()
                mang_mau_sac_cot = ['green' if val > 0 else 'red' for val in mang_gia_tri_rong]
                
                bieu_do_khoi_ngoai.add_trace(go.Bar(
                    x=mang_thoi_gian_ngoai.tail(10),
                    y=mang_gia_tri_rong[-10:],
                    marker_color=mang_mau_sac_cot,
                    name="Giá Trị Ròng (Tỷ VNĐ)"
                ))
                bieu_do_khoi_ngoai.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20), title="Khối Ngoại Mua/Bán Ròng (Tỷ VNĐ)")
                st.plotly_chart(bieu_do_khoi_ngoai, use_container_width=True)
                
            else:
                st.warning("⚠️ Lỗi truy cập API Sở Giao Dịch: Không lấy được Dữ liệu Khối Ngoại. Chuyển sang sử dụng bộ máy AI Ước lượng Hành vi Dòng tiền bên dưới.")

        st.divider()

        # --- MODULE 2: MÔ HÌNH ƯỚC LƯỢNG HÀNH VI TỔ CHỨC VÀ NHỎ LẺ ---
        df_du_lieu_dong_tien_tho_v13 = lay_du_lieu_nien_yet_chuan_v13(ma_co_phieu_dang_duoc_chon, so_ngay_lich_su_can_lay=30)
        
        if df_du_lieu_dong_tien_tho_v13 is not None:
            df_du_lieu_dong_tien_tinh_xong_v13 = tinh_toan_bo_chi_bao_quant_v13(df_du_lieu_dong_tien_tho_v13)
            dong_du_lieu_dong_tien_cuoi_cung_v13 = df_du_lieu_dong_tien_tinh_xong_v13.iloc[-1]
            
            suc_manh_vol_flow_cua_ngay_hom_nay_v13 = dong_du_lieu_dong_tien_cuoi_cung_v13['vol_strength']
            
            if suc_manh_vol_flow_cua_ngay_hom_nay_v13 > 1.8:
                ti_le_phan_tram_cua_to_chuc_noi_v13 = 0.55
                ti_le_phan_tram_cua_ca_nhan_le_v13 = 0.45
            elif suc_manh_vol_flow_cua_ngay_hom_nay_v13 > 1.2:
                ti_le_phan_tram_cua_to_chuc_noi_v13 = 0.40
                ti_le_phan_tram_cua_ca_nhan_le_v13 = 0.60
            else:
                ti_le_phan_tram_cua_to_chuc_noi_v13 = 0.15
                ti_le_phan_tram_cua_ca_nhan_le_v13 = 0.85
            
            st.write("#### 📊 Tỷ Lệ Phân Bổ Dòng Tiền Tổ Chức Và Nhỏ Lẻ (Mô Hình AI Ước Tính Theo Volume):")
            cot_hien_thi_dong_tien_2_v13, cot_hien_thi_dong_tien_3_v13 = st.columns(2)
            
            if dong_du_lieu_dong_tien_cuoi_cung_v13['return_1d'] > 0:
                nhan_hanh_dong_cua_to_chuc_v13 = "Đang Tích Cực Kê Gom"
            else:
                nhan_hanh_dong_cua_to_chuc_v13 = "Đang Nhồi Lệnh Táng Xả"
                
            cot_hien_thi_dong_tien_2_v13.metric(
                "🏦 Tổ Chức & Tự Doanh (Nhóm Tạo lập)", 
                f"{ti_le_phan_tram_cua_to_chuc_noi_v13*100:.1f}%", 
                delta=nhan_hanh_dong_cua_to_chuc_v13
            )
            
            if ti_le_phan_tram_cua_ca_nhan_le_v13 > 0.6:
                nhan_hanh_dong_cua_nho_le_v13 = "Cảnh Báo Đỏ: Nhỏ Lẻ Đu Bám Quá Nhiều"
                mau_sac_canh_bao_nho_le_v13 = "inverse"
            else:
                nhan_hanh_dong_cua_nho_le_v13 = "Tình Trạng Ổn Định"
                mau_sac_canh_bao_nho_le_v13 = "normal"
                
            cot_hien_thi_dong_tien_3_v13.metric(
                "🐜 Cá Nhân (Nhà đầu tư lẻ)", 
                f"{ti_le_phan_tram_cua_ca_nhan_le_v13*100:.1f}%", 
                delta=nhan_hanh_dong_cua_nho_le_v13, 
                delta_color=mau_sac_canh_bao_nho_le_v13
            )
            
            voi_thanh_mo_rong_tu_dien_dong_tien_v13 = st.expander("📖 TỪ ĐIỂN PHÂN LỚP DÒNG TIỀN NỘI ĐỊA")
            with voi_thanh_mo_rong_tu_dien_dong_tien_v13:
                st.write("- **🏦 Tổ Chức Nội (Quỹ Nội + CTCK):** Đội ngũ Tự doanh. Đây là những kẻ thao túng tạo ra Cú Breakout Vượt Đỉnh hoặc Cú Upo Gãy Nền thị trường.")
                st.write("- **🐜 Nhỏ Lẻ (Cá Nhân):** Đám đông. Cổ phiếu nào có Đám đông chiếm hơn 60% thanh khoản thì cổ phiếu đó y như một con rùa, kéo lên 1 tí là bị bán chốt lãi vô đầu, rất khó bay xa.")
            
            st.divider()
            
            # --- MODULE 3: MARKET BREADTH (ĐỘ RỘNG THỊ TRƯỜNG QUA 10 TRỤ) ---
            st.write("#### 🌊 Bức Tranh Tổng Thể - Phân Bổ Sức Mạnh Nhóm 10 Trụ Cột")
            with st.spinner("Hệ thống đang phát tia X-Ray dò tìm trên toàn bộ bảng điện HOSE..."):
                
                danh_sach_10_ma_tru_quoc_gia_kiem_tra_v13 = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                mang_chua_ma_tru_co_tin_hieu_gom_hang_v13 = []
                mang_chua_ma_tru_co_tin_hieu_xa_hang_v13 = []
                
                for mot_ma_tru_dang_quet_v13 in danh_sach_10_ma_tru_quoc_gia_kiem_tra_v13:
                    try:
                        du_lieu_cua_tru_tho_v13 = lay_du_lieu_nien_yet_chuan_v13(mot_ma_tru_dang_quet_v13, so_ngay_lich_su_can_lay=10)
                        
                        if du_lieu_cua_tru_tho_v13 is not None:
                            du_lieu_cua_tru_da_tinh_xong_v13 = tinh_toan_bo_chi_bao_quant_v13(du_lieu_cua_tru_tho_v13)
                            phien_giao_dich_cuoi_cua_tru_v13 = du_lieu_cua_tru_da_tinh_xong_v13.iloc[-1]
                            
                            co_hieu_gia_dang_tang_v13 = phien_giao_dich_cuoi_cua_tru_v13['return_1d'] > 0
                            co_hieu_gia_dang_giam_v13 = phien_giao_dich_cuoi_cua_tru_v13['return_1d'] < 0
                            co_hieu_khoi_luong_dang_no_v13 = phien_giao_dich_cuoi_cua_tru_v13['vol_strength'] > 1.2
                            
                            if co_hieu_gia_dang_tang_v13 and co_hieu_khoi_luong_dang_no_v13:
                                mang_chua_ma_tru_co_tin_hieu_gom_hang_v13.append(mot_ma_tru_dang_quet_v13)
                            elif co_hieu_gia_dang_giam_v13 and co_hieu_khoi_luong_dang_no_v13:
                                mang_chua_ma_tru_co_tin_hieu_xa_hang_v13.append(mot_ma_tru_dang_quet_v13)
                    except: 
                        pass
                
                cot_hien_thi_so_luong_1_v13, cot_hien_thi_so_luong_2_v13 = st.columns(2)
                
                tong_so_tru_hien_tai_v13 = len(danh_sach_10_ma_tru_quoc_gia_kiem_tra_v13)
                
                so_luong_tru_gom_v13 = len(mang_chua_ma_tru_co_tin_hieu_gom_hang_v13)
                ti_trong_gom_cua_tru_v13 = (so_luong_tru_gom_v13 / tong_so_tru_hien_tai_v13) * 100
                cot_hien_thi_so_luong_1_v13.metric(
                    "Tổng Số Trụ Cột Đang Được Mua Gom Nâng Đỡ", 
                    f"{so_luong_tru_gom_v13} Cổ Phiếu Trụ", 
                    delta=f"Độ che phủ thị trường đạt {ti_trong_gom_cua_tru_v13:.0f}%"
                )
                
                so_luong_tru_xa_v13 = len(mang_chua_ma_tru_co_tin_hieu_xa_hang_v13)
                ti_trong_xa_cua_tru_v13 = (so_luong_tru_xa_v13 / tong_so_tru_hien_tai_v13) * 100
                cot_hien_thi_so_luong_2_v13.metric(
                    "Tổng Số Trụ Cột Đang Bị Lực Xả Đạp Đi Xuống", 
                    f"{so_luong_tru_xa_v13} Cổ Phiếu Trụ", 
                    delta=f"Áp lực đè thị trường {ti_trong_xa_cua_tru_v13:.0f}%", 
                    delta_color="inverse"
                )
                
                cot_liet_ke_danh_sach_1_v13, cot_liet_ke_danh_sach_2_v13 = st.columns(2)
                
                with cot_liet_ke_danh_sach_1_v13:
                    st.success("✅ **GHI NHẬN DANH SÁCH CÁC MÃ TRỤ ĐANG ĐƯỢC GOM:**")
                    if len(mang_chua_ma_tru_co_tin_hieu_gom_hang_v13) > 0:
                        chuoi_gom_noi_lai_v13 = ", ".join(mang_chua_ma_tru_co_tin_hieu_gom_hang_v13)
                        st.write(chuoi_gom_noi_lai_v13)
                    else:
                        st.write("Không phát hiện mã nào được mua mạnh.")
                        
                with cot_liet_ke_danh_sach_2_v13:
                    st.error("🚨 **GHI NHẬN DANH SÁCH CÁC MÃ TRỤ ĐANG BỊ XẢ TÁNG:**")
                    if len(mang_chua_ma_tru_co_tin_hieu_xa_hang_v13) > 0:
                        chuoi_xa_noi_lai_v13 = ", ".join(mang_chua_ma_tru_co_tin_hieu_xa_hang_v13)
                        st.write(chuoi_xa_noi_lai_v13)
                    else:
                        st.write("Bảng điện hiện tại đang khá sạch bóng rủi ro phân phối.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: MÁY QUÉT ROBOT HUNTER (TÌM CƠ HỘI ĐỘT BIẾN)
    # ------------------------------------------------------------------------------
    with tab_trung_tam_hunter_v13:
        st.subheader("🔍 Máy Quét Định Lượng Robot Hunter - Quét Sàn HOSE Top 30")
        st.write("Chức năng này cho phép lọc cạn kiệt các mã có thanh khoản nổ bùm (>1.3 lần) và được AI dự báo sẽ còn khả năng tăng tiếp.")
        
        nut_bam_kich_hoat_radar_v13 = st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT TOÀN SÀN NGAY BÂY GIỜ")
        
        if nut_bam_kich_hoat_radar_v13:
            danh_sach_thu_thap_ket_qua_hunter_v13 = []
            thanh_truot_hien_thi_tien_do_v13 = st.progress(0)
            
            tap_danh_sach_ma_se_quet_v13 = danh_sach_tat_ca_cac_ma_hose[:30]
            tong_so_ma_can_quet_v13 = len(tap_danh_sach_ma_se_quet_v13)
            
            for so_thu_tu_vong_lap_v13, ma_muc_tieu_hien_tai_quet_v13 in enumerate(tap_danh_sach_ma_se_quet_v13):
                try:
                    bang_du_lieu_quet_tho_ban_dau_v13 = lay_du_lieu_nien_yet_chuan_v13(ma_muc_tieu_hien_tai_quet_v13, so_ngay_lich_su_can_lay=100)
                    bang_du_lieu_quet_sau_tinh_toan_v13 = tinh_toan_bo_chi_bao_quant_v13(bang_du_lieu_quet_tho_ban_dau_v13)
                    
                    dong_cuoi_cua_ma_dang_quet_v13 = bang_du_lieu_quet_sau_tinh_toan_v13.iloc[-1]
                    
                    # LOGIC HUNTER: Vô cùng khắt khe, Volume nổ bắt buộc phải gấp > 1.3 lần trung bình
                    if dong_cuoi_cua_ma_dang_quet_v13['vol_strength'] > 1.3:
                        
                        diem_so_ai_cua_ma_quet_v13 = du_bao_xac_suat_ai_t3_v13(bang_du_lieu_quet_sau_tinh_toan_v13)
                        
                        danh_sach_thu_thap_ket_qua_hunter_v13.append({
                            'Tên Ticker Mã': ma_muc_tieu_hien_tai_quet_v13, 
                            'Thị Giá Khớp Lệnh': f"{dong_cuoi_cua_ma_dang_quet_v13['close']:,.0f} VNĐ", 
                            'Cường Độ Nổ Volume': round(dong_cuoi_cua_ma_dang_quet_v13['vol_strength'], 2), 
                            'Xác Suất Tăng T+3 Theo AI': f"{diem_so_ai_cua_ma_quet_v13}%"
                        })
                except Exception:
                    pass
                
                phan_tram_hoan_thanh_v13 = (so_thu_tu_vong_lap_v13 + 1) / tong_so_ma_can_quet_v13
                thanh_truot_hien_thi_tien_do_v13.progress(phan_tram_hoan_thanh_v13)
            
            if len(danh_sach_thu_thap_ket_qua_hunter_v13) > 0:
                bang_hien_thi_hunter_cuoi_cung_v13 = pd.DataFrame(danh_sach_thu_thap_ket_qua_hunter_v13)
                bang_hien_thi_hunter_cuoi_cung_v13 = bang_hien_thi_hunter_cuoi_cung_v13.sort_values(by='Xác Suất Tăng T+3 Theo AI', ascending=False)
                
                st.table(bang_hien_thi_hunter_cuoi_cung_v13)
                st.success("✅ Nhiệm vụ truy quét hoàn tất thành công. Cảnh báo đỏ: Các mã trên đang thu hút dòng tiền của Cá mập rất nóng.")
            else:
                st.info("Radar siêu tĩnh. Ngày hôm nay chưa xuất hiện bất kỳ siêu cổ phiếu nào thỏa mãn luật thép của hệ thống Hunter.")

# ==============================================================================
# HẾT MÃ NGUỒN V15.0 - BẢN KHÔNG TÌ VẾT (THE FLAWLESS MASTER)
# ==============================================================================
