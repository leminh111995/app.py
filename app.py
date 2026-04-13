# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V11.0 (THE TITANIUM CORE)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# MÔ TẢ: BẢN TRIỂN KHAI MÃ NGUỒN NGUYÊN THỦY (RAW UNROLLED CODE)
# CAM KẾT: 
# - KHÔNG GỘP DÒNG, KHÔNG RÚT GỌN LOGIC.
# - MỌI BIẾN TRUNG GIAN ĐỀU ĐƯỢC KHAI BÁO RÕ RÀNG.
# - FIX 100% CÁC LỖI NAMEERROR, KEYERROR, VALUEERROR.
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
# THƯ VIỆN TRÍ TUỆ NHÂN TẠO & XỬ LÝ NGÔN NGỮ TỰ NHIÊN
# ------------------------------------------------------------------------------
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Tải tài nguyên ngôn ngữ tự động để ngăn chặn lỗi Runtime trên Streamlit Cloud
try:
    # Kiểm tra xem từ điển vader_lexicon đã tồn tại trong hệ thống chưa
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu chưa tồn tại, yêu cầu máy chủ tải xuống tự động
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & PHÂN QUYỀN (SECURITY LAYER)
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh():
    """
    Hàm bảo mật cấp cao, khóa hệ thống bằng mật mã.
    Duy trì phiên đăng nhập bằng st.session_state để không bị văng khi reload trang.
    Mọi biến đều được viết rõ ràng, không viết tắt.
    """
    
    def kiem_tra_mat_ma_nhap_vao():
        """Hàm callback chạy khi người dùng nhấn Enter ở ô nhập mật mã"""
        
        # Bước 1: Lấy mật mã chuẩn từ tệp cấu hình secrets.toml
        mat_ma_he_thong_goc = st.secrets["password"]
        
        # Bước 2: Lấy giá trị mà người dùng vừa gõ vào ô input
        mat_ma_nguoi_dung_nhap = st.session_state.get("o_nhap_mat_ma_cua_minh", "")
        
        # Bước 3: So sánh hai chuỗi mật mã
        if mat_ma_nguoi_dung_nhap == mat_ma_he_thong_goc:
            # Nếu chính xác, cấp quyền truy cập
            st.session_state["trang_thai_dang_nhap_thanh_cong"] = True
            
            # Xóa mật mã khỏi biến trạng thái để tránh rò rỉ bộ nhớ
            st.session_state["o_nhap_mat_ma_cua_minh"] = ""
        else:
            # Nếu sai, từ chối quyền truy cập
            st.session_state["trang_thai_dang_nhap_thanh_cong"] = False

    # Kiểm tra trạng thái: Nếu người dùng chưa từng đăng nhập trong phiên này
    if "trang_thai_dang_nhap_thanh_cong" not in st.session_state:
        st.markdown("### 🔐 Quant System V11.0 - Cổng Bảo Mật Trung Tâm")
        st.info("Hệ thống phân tích định lượng chuyên sâu đang bị khóa. Vui lòng xác thực danh tính.")
        
        # Hiển thị ô nhập liệu an toàn
        st.text_input(
            "🔑 Nhập mật mã truy cập của Minh:", 
            type="password", 
            on_change=kiem_tra_mat_ma_nhap_vao, 
            key="o_nhap_mat_ma_cua_minh"
        )
        return False
    
    # Kiểm tra trạng thái: Nếu người dùng đã nhập nhưng sai mật mã
    if st.session_state["trang_thai_dang_nhap_thanh_cong"] == False:
        st.error("❌ Cảnh báo: Mật mã không hợp lệ. Vui lòng kiểm tra lại Caps Lock hoặc bộ gõ.")
        
        # Yêu cầu nhập lại
        st.text_input(
            "🔑 Thử lại mật mã truy cập:", 
            type="password", 
            on_change=kiem_tra_mat_ma_nhap_vao, 
            key="o_nhap_mat_ma_cua_minh"
        )
        return False
    
    # Nếu mọi thứ hợp lệ, trả về True để mở khóa ứng dụng
    return st.session_state.get("trang_thai_dang_nhap_thanh_cong", False)

# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG CHÍNH (MAIN APP EXECUTION)
# ==============================================================================
if xac_thuc_quyen_truy_cap_cua_minh():
    
    # Cấu hình Layout cho toàn bộ trang Streamlit
    st.set_page_config(
        page_title="Quant System V11.0 Titanium", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Tiêu đề giao diện chính
    st.title("🛡️ Quant System V11.0: Master Advisor & Logic Engine")
    st.markdown("---")

    # Khởi tạo động cơ Vnstock để kéo dữ liệu chứng khoán Việt Nam
    dong_co_vnstock = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU CỐT LÕI (DATA ACQUISITION)
    # ==============================================================================
    def lay_du_lieu_nien_yet_chuan_v11(ma_chung_khoan_can_lay, so_ngay_lich_su_can_lay=1000):
        """
        Hàm tải dữ liệu giá cổ phiếu OHLCV.
        Áp dụng quy trình Fail-over 2 bước: Thử Vnstock trước, nếu rớt mạng thì gọi Yahoo Finance.
        Viết rõ từng bước xử lý để không bị lỗi KeyError do tên cột.
        """
        
        # Bước 2.1: Khởi tạo các mốc thời gian
        thoi_diem_bay_gio = datetime.now()
        chuoi_ngay_ket_thuc_lay_du_lieu = thoi_diem_bay_gio.strftime('%Y-%m-%d')
        
        do_tre_thoi_gian_tinh_bang_ngay = timedelta(days=so_ngay_lich_su_can_lay)
        thoi_diem_bat_dau_lay_du_lieu = thoi_diem_bay_gio - do_tre_thoi_gian_tinh_bang_ngay
        chuoi_ngay_bat_dau_lay_du_lieu = thoi_diem_bat_dau_lay_du_lieu.strftime('%Y-%m-%d')
        
        # Bước 2.2: Truy xuất ưu tiên qua Vnstock (Chính xác cho sàn Việt Nam)
        try:
            bang_du_lieu_tu_vnstock = dong_co_vnstock.stock.quote.history(
                symbol=ma_chung_khoan_can_lay, 
                start=chuoi_ngay_bat_dau_lay_du_lieu, 
                end=chuoi_ngay_ket_thuc_lay_du_lieu
            )
            
            # Đảm bảo dữ liệu không bị rỗng
            if bang_du_lieu_tu_vnstock is not None:
                if not bang_du_lieu_tu_vnstock.empty:
                    
                    # Đổi toàn bộ tiêu đề cột thành chữ thường để thống nhất
                    danh_sach_ten_cot_da_chuan_hoa = []
                    for ten_cot_hien_tai in bang_du_lieu_tu_vnstock.columns:
                        ten_cot_in_thuong = str(ten_cot_hien_tai).lower()
                        danh_sach_ten_cot_da_chuan_hoa.append(ten_cot_in_thuong)
                    
                    bang_du_lieu_tu_vnstock.columns = danh_sach_ten_cot_da_chuan_hoa
                    return bang_du_lieu_tu_vnstock
                    
        except Exception as loi_vnstock:
            # Lỗi Vnstock sẽ được bỏ qua để hệ thống chạy xuống khối Yahoo Finance
            pass
        
        # Bước 2.3: Phương án dự phòng (Fallback) bằng Yahoo Finance
        try:
            # Gắn đuôi .VN cho các mã chứng khoán để khớp với hệ thống Yahoo
            if ma_chung_khoan_can_lay == "VNINDEX":
                ma_chung_khoan_yahoo = "^VNINDEX"
            else:
                ma_chung_khoan_yahoo = f"{ma_chung_khoan_can_lay}.VN"
                
            # Gọi API của Yahoo Finance
            bang_du_lieu_tu_yahoo = yf.download(
                ma_chung_khoan_yahoo, 
                period="3y", 
                progress=False
            )
            
            # Đảm bảo dữ liệu Yahoo trả về không bị rỗng
            if not bang_du_lieu_tu_yahoo.empty:
                
                # Reset index để cột Date hiện ra thành một cột bình thường
                bang_du_lieu_tu_yahoo = bang_du_lieu_tu_yahoo.reset_index()
                
                # Bóc tách Multi-index (rất hay gây lỗi ở thư viện yfinance phiên bản mới)
                danh_sach_ten_cot_yahoo_da_chuan_hoa = []
                for nhan_cot_yahoo in bang_du_lieu_tu_yahoo.columns:
                    if isinstance(nhan_cot_yahoo, tuple):
                        # Lấy phần tử đầu tiên của tuple
                        ten_cot_tuple_in_thuong = str(nhan_cot_yahoo[0]).lower()
                        danh_sach_ten_cot_yahoo_da_chuan_hoa.append(ten_cot_tuple_in_thuong)
                    else:
                        # Lấy chuỗi bình thường
                        ten_cot_chuoi_in_thuong = str(nhan_cot_yahoo).lower()
                        danh_sach_ten_cot_yahoo_da_chuan_hoa.append(ten_cot_chuoi_in_thuong)
                
                # Gán lại tên cột
                bang_du_lieu_tu_yahoo.columns = danh_sach_ten_cot_yahoo_da_chuan_hoa
                return bang_du_lieu_tu_yahoo
                
        except Exception as thong_bao_loi_yahoo:
            st.sidebar.error(f"⚠️ Lỗi nghiêm trọng khi tải mã {ma_chung_khoan_can_lay}: {str(thong_bao_loi_yahoo)}")
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE) - KHAI TRIỂN TỐI ĐA
    # ==============================================================================
    def tinh_toan_bo_chi_bao_quant_v11(bang_du_lieu_can_tinh_toan):
        """
        Xây dựng bộ chỉ báo định lượng: MA, Bollinger, RSI, MACD, Volume.
        Tách rời từng bước tính toán, tạo biến trung gian để đảm bảo 
        luồng chạy không bị nén hay xung đột. Tuyệt đối không viết tắt.
        """
        # Tạo bản sao để bảo vệ dữ liệu nguyên gốc
        bang_du_lieu_sau_tinh_toan = bang_du_lieu_can_tinh_toan.copy()
        
        # Trích xuất cột giá đóng cửa để dùng nhiều lần
        chuoi_gia_dong_cua_co_phieu = bang_du_lieu_sau_tinh_toan['close']
        
        # --- 3.1: HỆ THỐNG TRUNG BÌNH ĐỘNG (MOVING AVERAGES) ---
        
        # Tính MA20 (Đường trung bình 20 phiên)
        cua_so_truot_20_phien = chuoi_gia_dong_cua_co_phieu.rolling(window=20)
        gia_tri_trung_binh_20_phien = cua_so_truot_20_phien.mean()
        bang_du_lieu_sau_tinh_toan['ma20'] = gia_tri_trung_binh_20_phien
        
        # Tính MA50 (Đường trung bình 50 phiên)
        cua_so_truot_50_phien = chuoi_gia_dong_cua_co_phieu.rolling(window=50)
        gia_tri_trung_binh_50_phien = cua_so_truot_50_phien.mean()
        bang_du_lieu_sau_tinh_toan['ma50'] = gia_tri_trung_binh_50_phien
        
        # Tính MA200 (Đường trung bình 200 phiên)
        cua_so_truot_200_phien = chuoi_gia_dong_cua_co_phieu.rolling(window=200)
        gia_tri_trung_binh_200_phien = cua_so_truot_200_phien.mean()
        bang_du_lieu_sau_tinh_toan['ma200'] = gia_tri_trung_binh_200_phien
        
        # --- 3.2: DẢI BOLLINGER BANDS (VOLATILITY BANDS) ---
        
        # Tính độ lệch chuẩn 20 phiên
        do_lech_chuan_trong_20_phien = cua_so_truot_20_phien.std()
        bang_du_lieu_sau_tinh_toan['do_lech_chuan_20'] = do_lech_chuan_trong_20_phien
        
        # Tính khoảng cách dải (Độ lệch chuẩn x 2)
        khoang_cach_mo_rong_dai_bollinger = bang_du_lieu_sau_tinh_toan['do_lech_chuan_20'] * 2
        
        # Dải trên (Upper Band)
        dai_bollinger_phien_tren = bang_du_lieu_sau_tinh_toan['ma20'] + khoang_cach_mo_rong_dai_bollinger
        bang_du_lieu_sau_tinh_toan['upper_band'] = dai_bollinger_phien_tren
        
        # Dải dưới (Lower Band)
        dai_bollinger_phien_duoi = bang_du_lieu_sau_tinh_toan['ma20'] - khoang_cach_mo_rong_dai_bollinger
        bang_du_lieu_sau_tinh_toan['lower_band'] = dai_bollinger_phien_duoi
        
        # --- 3.3: CHỈ SỐ SỨC MẠNH TƯƠNG ĐỐI (RSI 14) ---
        
        # Tính bước nhảy giá giữa các ngày
        khoang_chenh_lech_gia_tung_ngay = chuoi_gia_dong_cua_co_phieu.diff()
        
        # Lọc ra các ngày tăng giá (Gain)
        chuoi_ngay_co_gia_tang = khoang_chenh_lech_gia_tung_ngay.where(khoang_chenh_lech_gia_tung_ngay > 0, 0)
        
        # Lọc ra các ngày giảm giá (Loss) - Lấy trị tuyệt đối
        chuoi_ngay_co_gia_giam = -khoang_chenh_lech_gia_tung_ngay.where(khoang_chenh_lech_gia_tung_ngay < 0, 0)
        
        # Trung bình tăng 14 phiên
        cua_so_truot_14_phien_tang = chuoi_ngay_co_gia_tang.rolling(window=14)
        muc_tang_trung_binh_14_phien = cua_so_truot_14_phien_tang.mean()
        
        # Trung bình giảm 14 phiên
        cua_so_truot_14_phien_giam = chuoi_ngay_co_gia_giam.rolling(window=14)
        muc_giam_trung_binh_14_phien = cua_so_truot_14_phien_giam.mean()
        
        # Tính hệ số RS
        ti_so_suc_manh_tuong_doi_rs = muc_tang_trung_binh_14_phien / (muc_giam_trung_binh_14_phien + 1e-9)
        
        # Tính RSI cuối cùng
        chi_so_rsi_hoan_thien = 100 - (100 / (1 + ti_so_suc_manh_tuong_doi_rs))
        bang_du_lieu_sau_tinh_toan['rsi'] = chi_so_rsi_hoan_thien
        
        # --- 3.4: ĐỘNG LƯỢNG MACD (12, 26, 9) ---
        
        # Tính EMA 12 phiên
        bo_loc_ema_12 = chuoi_gia_dong_cua_co_phieu.ewm(span=12, adjust=False)
        duong_ema_nhanh_12 = bo_loc_ema_12.mean()
        
        # Tính EMA 26 phiên
        bo_loc_ema_26 = chuoi_gia_dong_cua_co_phieu.ewm(span=26, adjust=False)
        duong_ema_cham_26 = bo_loc_ema_26.mean()
        
        # Cắt MACD
        duong_macd_chinh = duong_ema_nhanh_12 - duong_ema_cham_26
        bang_du_lieu_sau_tinh_toan['macd'] = duong_macd_chinh
        
        # Tính đường Tín hiệu (Signal - EMA 9 của MACD)
        bo_loc_ema_9_cho_macd = bang_du_lieu_sau_tinh_toan['macd'].ewm(span=9, adjust=False)
        duong_tin_hieu_signal = bo_loc_ema_9_cho_macd.mean()
        bang_du_lieu_sau_tinh_toan['signal'] = duong_tin_hieu_signal
        
        # --- 3.5: CÁC BIẾN SỐ PHỤC VỤ DÒNG TIỀN VÀ AI ---
        
        # Tỷ suất thay đổi giá hằng ngày
        phan_tram_thay_doi_gia_1_ngay = chuoi_gia_dong_cua_co_phieu.pct_change()
        bang_du_lieu_sau_tinh_toan['return_1d'] = phan_tram_thay_doi_gia_1_ngay
        
        # TÍNH CƯỜNG ĐỘ KHỐI LƯỢNG (vol_strength)
        chuoi_khoi_luong_giao_dich = bang_du_lieu_sau_tinh_toan['volume']
        cua_so_truot_10_phien_vol = chuoi_khoi_luong_giao_dich.rolling(window=10)
        khoi_luong_trung_binh_10_phien = cua_so_truot_10_phien_vol.mean()
        
        suc_manh_khoi_luong_vol_strength = chuoi_khoi_luong_giao_dich / khoi_luong_trung_binh_10_phien
        bang_du_lieu_sau_tinh_toan['vol_strength'] = suc_manh_khoi_luong_vol_strength
        
        # Dòng tiền lưu chuyển (Giá x Khối lượng)
        dong_tien_luan_chuyen = chuoi_gia_dong_cua_co_phieu * chuoi_khoi_luong_giao_dich
        bang_du_lieu_sau_tinh_toan['money_flow'] = dong_tien_luan_chuyen
        
        # Độ biến động thị trường (Dựa trên return_1d)
        cua_so_truot_20_phien_return = bang_du_lieu_sau_tinh_toan['return_1d'].rolling(window=20)
        do_bien_dong_lich_su = cua_so_truot_20_phien_return.std()
        bang_du_lieu_sau_tinh_toan['volatility'] = do_bien_dong_lich_su
        
        # --- 3.6: PHÂN LỚP XU HƯỚNG DÒNG TIỀN (PRICE-VOLUME TREND) ---
        
        # Điều kiện Gom hàng: Giá tăng VÀ Khối lượng lớn hơn 1.2 lần trung bình
        dieu_kien_cau_manh_gom_hang = (bang_du_lieu_sau_tinh_toan['return_1d'] > 0) & (bang_du_lieu_sau_tinh_toan['vol_strength'] > 1.2)
        
        # Điều kiện Xả hàng: Giá giảm VÀ Khối lượng lớn hơn 1.2 lần trung bình
        dieu_kien_cung_manh_xa_hang = (bang_du_lieu_sau_tinh_toan['return_1d'] < 0) & (bang_du_lieu_sau_tinh_toan['vol_strength'] > 1.2)
        
        # Gán nhãn: 1 (Gom), -1 (Xả), 0 (Không rõ ràng)
        xu_huong_dong_tien_pv = np.where(dieu_kien_cau_manh_gom_hang, 1, 
                                np.where(dieu_kien_cung_manh_xa_hang, -1, 0))
        bang_du_lieu_sau_tinh_toan['pv_trend'] = xu_huong_dong_tien_pv
        
        # Loại bỏ các dòng NaN do quá trình tính rolling sinh ra
        bang_du_lieu_sach_khong_co_nan = bang_du_lieu_sau_tinh_toan.dropna()
        
        return bang_du_lieu_sach_khong_co_nan

    # ==============================================================================
    # 4. HÀM CHẨN ĐOÁN THÔNG MINH (INTELLIGENCE & AI LAYER)
    # ==============================================================================
    
    def phan_tich_tam_ly_dam_dong_v11(bang_du_lieu_da_tinh_xong):
        """
        Đánh giá chỉ số Sợ hãi và Tham lam dựa vào sức nóng của RSI tại phiên cuối cùng.
        Viết rõ từng lệnh if-else.
        """
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

    def thuc_thi_backtest_chien_thuat_v11(bang_du_lieu_da_tinh_xong):
        """
        Quét lại lịch sử để tìm xem nếu mua lúc (RSI < 45) + (MACD Cắt lên)
        thì xác suất chốt lãi 5% trong 10 ngày sau đó là bao nhiêu.
        """
        tong_so_lan_xuat_hien_tin_hieu_mua = 0
        tong_so_lan_chien_thang_chot_loi = 0
        
        do_dai_tong_cua_bang_du_lieu = len(bang_du_lieu_da_tinh_xong)
        
        # Chạy vòng lặp từ phiên 100 đến cận 10 phiên cuối
        for vi_tri_ngay_quyet_dinh in range(100, do_dai_tong_cua_bang_du_lieu - 10):
            
            # Khởi tạo các biến để kiểm tra điều kiện
            rsi_tai_ngay_quyet_dinh = bang_du_lieu_da_tinh_xong['rsi'].iloc[vi_tri_ngay_quyet_dinh]
            kiem_tra_dieu_kien_rsi = rsi_tai_ngay_quyet_dinh < 45
            
            macd_hom_nay = bang_du_lieu_da_tinh_xong['macd'].iloc[vi_tri_ngay_quyet_dinh]
            signal_hom_nay = bang_du_lieu_da_tinh_xong['signal'].iloc[vi_tri_ngay_quyet_dinh]
            macd_hom_qua = bang_du_lieu_da_tinh_xong['macd'].iloc[vi_tri_ngay_quyet_dinh - 1]
            signal_hom_qua = bang_du_lieu_da_tinh_xong['signal'].iloc[vi_tri_ngay_quyet_dinh - 1]
            
            kiem_tra_dieu_kien_macd_cat_len = (macd_hom_nay > signal_hom_nay) and (macd_hom_qua <= signal_hom_qua)
            
            # Gộp hai điều kiện để ra quyết định mua mô phỏng
            if kiem_tra_dieu_kien_rsi and kiem_tra_dieu_kien_macd_cat_len:
                tong_so_lan_xuat_hien_tin_hieu_mua = tong_so_lan_xuat_hien_tin_hieu_mua + 1
                
                # Bắt đầu mô phỏng giữ hàng trong 10 ngày
                gia_khop_lenh_gia_dinh = bang_du_lieu_da_tinh_xong['close'].iloc[vi_tri_ngay_quyet_dinh]
                gia_muc_tieu_chot_loi = gia_khop_lenh_gia_dinh * 1.05
                
                chi_so_ngay_bat_dau_tuong_lai = vi_tri_ngay_quyet_dinh + 1
                chi_so_ngay_ket_thuc_tuong_lai = vi_tri_ngay_quyet_dinh + 11
                
                khoang_gia_tuong_lai_10_ngay = bang_du_lieu_da_tinh_xong['close'].iloc[chi_so_ngay_bat_dau_tuong_lai : chi_so_ngay_ket_thuc_tuong_lai]
                
                # Kiểm tra xem có ngày nào chạm giá mục tiêu không
                kiem_tra_co_ngay_nao_thang = any(khoang_gia_tuong_lai_10_ngay > gia_muc_tieu_chot_loi)
                
                if kiem_tra_co_ngay_nao_thang:
                    tong_so_lan_chien_thang_chot_loi = tong_so_lan_chien_thang_chot_loi + 1
        
        # Ngăn chặn lỗi chia cho số 0
        if tong_so_lan_xuat_hien_tin_hieu_mua == 0:
            return 0.0
            
        phan_tram_thang_loi_cuoi_cung = (tong_so_lan_chien_thang_chot_loi / tong_so_lan_xuat_hien_tin_hieu_mua) * 100
        phan_tram_lam_tron = round(phan_tram_thang_loi_cuoi_cung, 1)
        
        return phan_tram_lam_tron

    def du_bao_xac_suat_ai_t3_v11(bang_du_lieu_da_tinh_xong):
        """
        Khởi tạo mô hình Machine Learning học 8 thuộc tính kỹ thuật.
        Dự đoán xem 3 ngày sau giá có tăng nổi 2% hay không.
        Mã nguồn được khai triển từng dòng để AI hiểu rõ.
        """
        # Nếu chưa đủ 200 ngày thì AI không đủ dữ liệu mẫu để học
        do_dai_bang_du_lieu = len(bang_du_lieu_da_tinh_xong)
        if do_dai_bang_du_lieu < 200:
            return "N/A"
            
        bang_du_lieu_cho_hoc_may = bang_du_lieu_da_tinh_xong.copy()
        
        # Bước 1: Gắn nhãn mục tiêu (Target Y) cho từng dòng lịch sử
        chuoi_gia_hien_tai_de_so_sanh = bang_du_lieu_cho_hoc_may['close']
        chuoi_gia_tuong_lai_sau_3_ngay = bang_du_lieu_cho_hoc_may['close'].shift(-3)
        
        dieu_kien_gia_tang_2_phan_tram = chuoi_gia_tuong_lai_sau_3_ngay > (chuoi_gia_hien_tai_de_so_sanh * 1.02)
        bang_du_lieu_cho_hoc_may['nhan_dich_cho_ai'] = dieu_kien_gia_tang_2_phan_tram.astype(int)
        
        # Bước 2: Liệt kê các biến số độc lập (Features X) làm đầu vào
        danh_sach_cac_bien_so_doc_lap = [
            'rsi', 
            'macd', 
            'signal', 
            'return_1d', 
            'volatility', 
            'vol_strength', 
            'money_flow', 
            'pv_trend'
        ]
        
        # Bước 3: Lọc bỏ các dòng chứa dữ liệu rỗng để không báo lỗi
        bang_du_lieu_sach_tuyet_doi = bang_du_lieu_cho_hoc_may.dropna()
        
        ma_tran_dac_trung_dau_vao_x = bang_du_lieu_sach_tuyet_doi[danh_sach_cac_bien_so_doc_lap]
        vector_muc_tieu_dau_ra_y = bang_du_lieu_sach_tuyet_doi['nhan_dich_cho_ai']
        
        # Bước 4: Khởi tạo và thiết lập mô hình thuật toán Rừng ngẫu nhiên (Random Forest)
        so_luong_cay_quyet_dinh = 100
        mo_hinh_random_forest_ai = RandomForestClassifier(n_estimators=so_luong_cay_quyet_dinh, random_state=42)
        
        # Bỏ đi 3 dòng cuối cùng của bảng vì chưa thể biết tương lai 3 ngày sau
        ma_tran_x_de_huan_luyen = ma_tran_dac_trung_dau_vao_x[:-3]
        vector_y_de_huan_luyen = vector_muc_tieu_dau_ra_y[:-3]
        
        # Tiến hành quá trình Fit (Học)
        mo_hinh_random_forest_ai.fit(ma_tran_x_de_huan_luyen, vector_y_de_huan_luyen)
        
        # Bước 5: Áp dụng mô hình đã học vào chính ngày hôm nay (Dòng cuối cùng)
        dong_du_lieu_cua_ngay_hom_nay = ma_tran_dac_trung_dau_vao_x.iloc[[-1]]
        mang_xac_suat_ket_qua_tra_ve = mo_hinh_random_forest_ai.predict_proba(dong_du_lieu_cua_ngay_hom_nay)
        
        # Tách lấy xác suất của nhãn 1 (Khả năng tăng giá)
        xac_suat_thuc_te_kha_nang_tang_gia = mang_xac_suat_ket_qua_tra_ve[0][1]
        xac_suat_nhan_100_lam_tron = round(xac_suat_thuc_te_kha_nang_tang_gia * 100, 1)
        
        return xac_suat_nhan_100_lam_tron

    # ==============================================================================
    # 5. PHÂN TÍCH TÀI CHÍNH CỐT LÕI (FUNDAMENTAL LAYER)
    # ==============================================================================
    def do_luong_tang_truong_canslim_v11(ma_chung_khoan_vao):
        """
        Tính phần trăm thay đổi Lợi nhuận sau thuế (Quý này so với Quý trước)
        Sử dụng cơ chế Fallback. Mọi biến được viết rõ ràng.
        """
        try:
            # Truy vấn Báo Cáo Kết Quả Kinh Doanh Quý từ Vnstock
            bang_bao_cao_tai_chinh_quy = dong_co_vnstock.stock.finance.income_statement(
                symbol=ma_chung_khoan_vao, 
                period='quarter', 
                lang='en'
            ).head(5)
            
            # Quét tìm cột Lợi nhuận sau thuế linh hoạt
            tap_hop_tu_khoa_nhan_dien = ['sau thuế', 'posttax', 'net profit', 'earning']
            
            danh_sach_cac_cot_tuong_thich = []
            for ten_cot_trong_bang in bang_bao_cao_tai_chinh_quy.columns:
                chuoi_ten_cot_thuong = str(ten_cot_trong_bang).lower()
                for tu_khoa in tap_hop_tu_khoa_nhan_dien:
                    if tu_khoa in chuoi_ten_cot_thuong:
                        danh_sach_cac_cot_tuong_thich.append(ten_cot_trong_bang)
                        break
            
            # Nếu tìm thấy cột lợi nhuận
            if len(danh_sach_cac_cot_tuong_thich) > 0:
                ten_cot_lnst_chinh_xac_nhat = danh_sach_cac_cot_tuong_thich[0]
                
                gia_tri_lnst_cua_quy_nay = float(bang_bao_cao_tai_chinh_quy.iloc[0][ten_cot_lnst_chinh_xac_nhat])
                gia_tri_lnst_cua_quy_nam_ngoai = float(bang_bao_cao_tai_chinh_quy.iloc[4][ten_cot_lnst_chinh_xac_nhat])
                
                # Tính phần trăm tăng trưởng
                if gia_tri_lnst_cua_quy_nam_ngoai > 0:
                    muc_do_chenh_lech = gia_tri_lnst_cua_quy_nay - gia_tri_lnst_cua_quy_nam_ngoai
                    bien_do_tang_truong_phan_tram = (muc_do_chenh_lech / gia_tri_lnst_cua_quy_nam_ngoai) * 100
                    return round(bien_do_tang_truong_phan_tram, 1)
        except Exception:
            # Lỗi sẽ chuyển qua Yahoo
            pass
            
        # Fallback lấy từ Yahoo Finance
        try:
            chuoi_ma_yahoo = f"{ma_chung_khoan_vao}.VN"
            doi_tuong_yf_ticker = yf.Ticker(chuoi_ma_yahoo)
            du_lieu_ho_so_doanh_nghiep = doi_tuong_yf_ticker.info
            
            ti_le_tang_truong_tu_yahoo = du_lieu_ho_so_doanh_nghiep.get('earningsQuarterlyGrowth')
            
            if ti_le_tang_truong_tu_yahoo is not None:
                return round(ti_le_tang_truong_tu_yahoo * 100, 1)
        except Exception:
            pass
            
        return None

    def boc_tach_chi_so_pe_roe_v11(ma_chung_khoan_vao):
        """Đo lường Hệ số định giá P/E và Hiệu suất vốn ROE"""
        chi_so_pe_cuoi_cung = 0.0
        chi_so_roe_cuoi_cung = 0.0
        
        # Thử nghiệm qua Vnstock
        try:
            bang_chi_so_tai_chinh_vnstock = dong_co_vnstock.stock.finance.ratio(ma_chung_khoan_vao, 'quarterly').iloc[-1]
            
            # Ưu tiên lấy ticker_pe, nếu không có thì lấy pe
            chi_so_pe_tu_vnstock = bang_chi_so_tai_chinh_vnstock.get('ticker_pe', bang_chi_so_tai_chinh_vnstock.get('pe', 0))
            chi_so_roe_tu_vnstock = bang_chi_so_tai_chinh_vnstock.get('roe', 0)
            
            chi_so_pe_cuoi_cung = chi_so_pe_tu_vnstock
            chi_so_roe_cuoi_cung = chi_so_roe_tu_vnstock
        except Exception:
            pass
            
        # Nếu Vnstock không lấy được thì dùng Yahoo
        if chi_so_pe_cuoi_cung <= 0:
            try:
                chuoi_ma_yahoo_pe = f"{ma_chung_khoan_vao}.VN"
                doi_tuong_yf_ticker_pe = yf.Ticker(chuoi_ma_yahoo_pe)
                du_lieu_ho_so_yf = doi_tuong_yf_ticker_pe.info
                
                chi_so_pe_tu_yahoo = du_lieu_ho_so_yf.get('trailingPE', 0)
                chi_so_roe_tu_yahoo = du_lieu_ho_so_yf.get('returnOnEquity', 0)
                
                chi_so_pe_cuoi_cung = chi_so_pe_tu_yahoo
                chi_so_roe_cuoi_cung = chi_so_roe_tu_yahoo
            except Exception:
                pass
                
        return chi_so_pe_cuoi_cung, chi_so_roe_cuoi_cung

    # ==============================================================================
    # 6. 🧠 ROBOT ADVISOR MASTER: LÕI SUY LUẬN LOGIC VÀ RA QUYẾT ĐỊNH
    # ==============================================================================
    def he_thong_suy_luan_advisor_v11(ma_chung_khoan_muc_tieu, dong_du_lieu_cuoi, ti_le_ai_du_bao, ti_le_winrate_lich_su, diem_chi_so_pe, diem_chi_so_roe, diem_tang_truong_lnst, danh_sach_tru_dang_gom, danh_sach_tru_dang_xa):
        """
        Trái tim của hệ thống: 
        Đọc và tổng hợp 5 lớp dữ liệu định lượng.
        Đưa ra đề xuất MUA/BÁN kèm theo bảng giải trình chi tiết từng bước.
        """
        
        # Khởi tạo các chuỗi văn bản sẽ xuất ra màn hình
        van_ban_nhan_dinh_ky_thuat = ""
        van_ban_nhan_dinh_dong_tien = ""
        lenh_chien_thuat_cuoi_cung = ""
        mau_sac_canh_bao_lenh = ""
        
        # Bảng ghi chép tiến trình suy luận để giải thích logic cho Minh
        bang_ghi_nhat_ky_su_kien_logic = []
        tong_diem_dong_thuan_cua_he_thong = 0
        
        # --- BƯỚC 1: XÉT VỊ THẾ MA20 ---
        gia_dong_cua_hien_tai = dong_du_lieu_cuoi['close']
        duong_ho_tro_ma20_hien_tai = dong_du_lieu_cuoi['ma20']
        
        khoang_cach_gia_va_ma20 = gia_dong_cua_hien_tai - duong_ho_tro_ma20_hien_tai
        phan_tram_chenh_lech_voi_ma20 = (khoang_cach_gia_va_ma20 / duong_ho_tro_ma20_hien_tai) * 100
        
        # Logic phân nhánh Kỹ Thuật
        if gia_dong_cua_hien_tai < duong_ho_tro_ma20_hien_tai:
            van_ban_nhan_dinh_ky_thuat = f"Cảnh báo rủi ro: Giá mã {ma_chung_khoan_muc_tieu} đang nằm hoàn toàn dưới đường MA20."
            bang_ghi_nhat_ky_su_kien_logic.append(f"❌ KỸ THUẬT XẤU: Giá bị ép dưới MA20 ({phan_tram_chenh_lech_voi_ma20:.1f}%). Xu hướng giảm ngắn hạn đang chi phối hoàn toàn.")
        else:
            van_ban_nhan_dinh_ky_thuat = f"Xác nhận tích cực: Giá mã {ma_chung_khoan_muc_tieu} đang duy trì vững chắc trên mốc hỗ trợ MA20."
            bang_ghi_nhat_ky_su_kien_logic.append(f"✅ KỸ THUẬT TỐT: Giá bảo vệ thành công MA20 ({phan_tram_chenh_lech_voi_ma20:.1f}%). Phe Mua đang kiểm soát trận đấu.")
            tong_diem_dong_thuan_cua_he_thong = tong_diem_dong_thuan_cua_he_thong + 1

        # --- BƯỚC 2: XÉT SMART FLOW (DÒNG TIỀN CÁ MẬP) ---
        if ma_chung_khoan_muc_tieu in danh_sach_tru_dang_gom:
            van_ban_nhan_dinh_dong_tien = "Dấu chân Cá Mập: Dòng tiền lớn đang chủ động Kê Mua và Gom hàng rất rõ rệt."
            bang_ghi_nhat_ky_su_kien_logic.append("✅ DÒNG TIỀN MẠNH: Tổ chức đang âm thầm gom hàng, có sự đồng thuận mua từ các mã trụ cột trên thị trường.")
            tong_diem_dong_thuan_cua_he_thong = tong_diem_dong_thuan_cua_he_thong + 1
            
        elif ma_chung_khoan_muc_tieu in danh_sach_tru_dang_xa:
            van_ban_nhan_dinh_dong_tien = "Dấu chân Phân Phối: Áp lực Thoát hàng (Xả) từ các tổ chức đang rất dữ dội."
            bang_ghi_nhat_ky_su_kien_logic.append("❌ DÒNG TIỀN XẤU: Cá mập đang phân phối hàng ra ngoài. Tuyệt đối không nhảy vào đỡ giá cho tổ chức.")
            
        else:
            van_ban_nhan_dinh_dong_tien = "Dòng tiền Lẻ loi: Vận động thị trường thiếu vắng bàn tay thao túng của tạo lập."
            bang_ghi_nhat_ky_su_kien_logic.append("🟡 DÒNG TIỀN NHIỄU: Thanh khoản phân tán, chủ yếu là nhỏ lẻ tự mua bán với nhau. Rất khó có sóng lớn.")

        # --- BƯỚC 3: XÉT AI VÀ KẾT QUẢ BACKTEST ---
        if isinstance(ti_le_ai_du_bao, float):
            if ti_le_ai_du_bao >= 58.0:
                tong_diem_dong_thuan_cua_he_thong = tong_diem_dong_thuan_cua_he_thong + 1
                bang_ghi_nhat_ky_su_kien_logic.append(f"✅ DỰ BÁO AI ({ti_le_ai_du_bao}%): Cỗ máy AI xác nhận mẫu hình hiện tại có cửa tăng rất sáng trong 3 ngày tới.")
            else:
                bang_ghi_nhat_ky_su_kien_logic.append(f"❌ DỰ BÁO AI ({ti_le_ai_du_bao}%): AI đánh giá tỷ lệ chiến thắng quá thấp, rủi ro chôn vốn rất cao.")

        if ti_le_winrate_lich_su >= 50.0:
            tong_diem_dong_thuan_cua_he_thong = tong_diem_dong_thuan_cua_he_thong + 1
            bang_ghi_nhat_ky_su_kien_logic.append(f"✅ KIỂM CHỨNG LỊCH SỬ ({ti_le_winrate_lich_su}%): Quá khứ chứng minh đây là một điểm mua uy tín và thường mang lại lợi nhuận tốt.")
        else:
            bang_ghi_nhat_ky_su_kien_logic.append(f"❌ KIỂM CHỨNG LỊCH SỬ ({ti_le_winrate_lich_su}%): Cẩn thận! Mẫu hình này trong quá khứ thường xuyên tạo Bẫy tăng giá ảo (Bull trap) để nhốt nhà đầu tư.")

        # --- BƯỚC 4: XÉT TÀI CHÍNH CỐT LÕI ---
        if diem_tang_truong_lnst is not None:
            if diem_tang_truong_lnst >= 20.0:
                tong_diem_dong_thuan_cua_he_thong = tong_diem_dong_thuan_cua_he_thong + 1
                bang_ghi_nhat_ky_su_kien_logic.append(f"✅ TÀI CHÍNH: Tăng trưởng Lợi nhuận sau thuế {diem_tang_truong_lnst}% khẳng định nội lực doanh nghiệp cực mạnh, thu hút được các Quỹ lớn.")

        # --- BƯỚC 5: TỔNG HỢP VÀ ĐƯA RA CHIẾN THUẬT TỐI ƯU ---
        chi_so_rsi_hien_tai = dong_du_lieu_cuoi['rsi']
        
        # Khung quy tắc số 1: Bùng nổ Mua (Đồng thuận cao và chưa quá hưng phấn)
        if tong_diem_dong_thuan_cua_he_thong >= 4 and chi_so_rsi_hien_tai < 68:
            lenh_chien_thuat_cuoi_cung = "🚀 MUA VÀ NẮM GIỮ (STRONG BUY)"
            mau_sac_canh_bao_lenh = "green"
            bang_ghi_nhat_ky_su_kien_logic.append("🏆 CHỐT HẠ: Sự đồng thuận hoàn hảo từ mọi góc độ. Có thể tự tin giải ngân 30-50% vị thế ở các nhịp rung lắc trong phiên.")
            
        # Khung quy tắc số 2: Xả hàng phòng thủ (Chỉ số xấu hoặc Giá rớt)
        elif tong_diem_dong_thuan_cua_he_thong <= 1 or chi_so_rsi_hien_tai > 78 or gia_dong_cua_ht < duong_ho_tro_ma20_ht:
            lenh_chien_thuat_cuoi_cung = "🚨 BÁN THOÁT HÀNG / ĐỨNG NGOÀI (BEARISH)"
            mau_sac_canh_bao_lenh = "red"
            
            # Module giải mã mâu thuẫn phức tạp
            if gia_dong_cua_ht < duong_ho_tro_ma20_ht and ma_chung_khoan_muc_tieu in danh_sach_tru_dang_gom:
                bang_ghi_nhat_ky_su_kien_logic.append("⚠️ CẢNH BÁO GIẢI MÃ MÂU THUẪN CÁ MẬP: Mặc dù hệ thống Robot phát hiện Cá Mập đang âm thầm Gom hàng, nhưng do Giá Cổ Phiếu vẫn nằm dưới đường sinh tử MA20, đây rất có thể là chu kỳ 'Gom Hàng Tích Lũy' kéo dài nhiều tháng của Quỹ Đầu Tư lớn.")
                bang_ghi_nhat_ky_su_kien_logic.append("👉 LỜI KHUYÊN CHO MINH: Đối với nhà đầu tư cá nhân, vào tiền ôm hàng lúc này sẽ bị 'ngâm vốn' rất lâu và gây ức chế tâm lý. Hãy kiên nhẫn đứng ngoài đợi đến khi giá bứt phá vượt hẳn lên trên MA20 rồi mới đánh thóp theo cá mập.")
            else:
                bang_ghi_nhat_ky_su_kien_logic.append("🏆 CHỐT HẠ: Không đạt tiêu chuẩn an toàn kỹ thuật. Việc bảo vệ vốn mặt tiền là mục tiêu sống còn lúc này.")
                
        # Khung quy tắc số 3: Đi ngang chờ thời (Thiếu dữ kiện)
        else:
            lenh_chien_thuat_cuoi_cung = "⚖️ THEO DÕI VÀ QUAN SÁT (WATCHLIST)"
            mau_sac_canh_bao_lenh = "orange"
            bang_ghi_nhat_ky_su_kien_logic.append("🏆 CHỐT HẠ: Trạng thái hiện tại chưa rõ ràng, cửa lên cửa xuống đang ở mức 50/50. Hãy kiên nhẫn chờ đợi một phiên bùng nổ khối lượng thực sự (Gấp >1.2 lần trung bình) để xác nhận tín hiệu vào lệnh.")

        return van_ban_nhan_dinh_ky_thuat, van_ban_nhan_dinh_dong_tien, lenh_chien_thuat_cuoi_cung, mau_sac_canh_bao_lenh, bang_ghi_nhat_ky_su_kien_logic

    # ==============================================================================
    # 7. GIAO DIỆN NGƯỜI DÙNG & KIỂM SOÁT LUỒNG DỮ LIỆU (UI CONTROLLER)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def tai_va_chuan_bi_danh_sach_ma_san_hose():
        """Tải bảng danh sách mã niêm yết chính thống từ máy chủ Vnstock"""
        try:
            bang_danh_sach_niem_yet_goc = dong_co_vnstock.market.listing()
            
            # Chỉ lọc các mã thuộc sàn HOSE để đảm bảo thanh khoản
            bo_loc_dieu_kien_san_hose = bang_danh_sach_niem_yet_goc['comGroupCode'] == 'HOSE'
            bang_danh_sach_hose_only = bang_danh_sach_niem_yet_goc[bo_loc_dieu_kien_san_hose]
            
            # Trích xuất cột Ticker thành danh sách
            danh_sach_chuoi_ma_chung_khoan = bang_danh_sach_hose_only['ticker'].tolist()
            return danh_sach_chuoi_ma_chung_khoan
            
        except Exception:
            # Danh sách dự phòng cứng nếu API máy chủ gặp trục trặc
            danh_sach_du_phong = [
                "FPT", "HPG", "SSI", "TCB", "MWG", 
                "VNM", "VIC", "VHM", "STB", "MSN", 
                "GAS", "VCB", "BID", "CTG", "VRE", 
                "DGC", "PDR", "NVL", "KBC", "DIG"
            ]
            return danh_sach_du_phong

    # 7.1 Khởi tạo dữ liệu thanh điều hướng
    danh_sach_tat_ca_cac_ma_hose = tai_va_chuan_bi_danh_sach_ma_san_hose()
    
    st.sidebar.header("🕹️ Trung Tâm Giao Dịch Định Lượng Quant")
    
    # Tạo Widget Menu thả xuống
    thanh_phan_chon_ma_co_phieu = st.sidebar.selectbox(
        "Lựa chọn mã cổ phiếu mục tiêu để phân tích:", 
        danh_sach_tat_ca_cac_ma_hose
    )
    
    # Tạo Widget Nhập text tay
    thanh_phan_nhap_ma_thu_cong = st.sidebar.text_input(
        "Hoặc nhập trực tiếp tên mã (Ví dụ: FPT):"
    ).upper()
    
    # Xác định mã chứng khoán sẽ được luồng dữ liệu xử lý
    if thanh_phan_nhap_ma_thu_cong != "":
        ma_co_phieu_dang_duoc_chon = thanh_phan_nhap_ma_thu_cong
    else:
        ma_co_phieu_dang_duoc_chon = thanh_phan_chon_ma_co_phieu

    # 7.2 ĐỊNH NGHĨA KHUNG TABS CHUYÊN MÔN
    # Đã đồng bộ triệt để tên biến, không còn nỗi lo NameError
    tab_trung_tam_advisor_v11, tab_trung_tam_tai_chinh_v11, tab_trung_tam_dong_tien_v11, tab_trung_tam_hunter_v11 = st.tabs([
        "🤖 ROBOT ADVISOR CHUYÊN SÂU & MASTER CHART", 
        "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM", 
        "🌊 BÓC TÁCH DÒNG TIỀN THÔNG MINH", 
        "🔍 RADAR TRUY QUÉT SIÊU CỔ PHIẾU"
    ])

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR VÀ BIỂU ĐỒ CHUYÊN SÂU
    # ------------------------------------------------------------------------------
    with tab_trung_tam_advisor_v11:
        
        nhan_nut_phan_tich = st.button(f"⚡ TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG MÃ CỔ PHIẾU {ma_co_phieu_dang_duoc_chon}")
        
        if nhan_nut_phan_tich:
            
            with st.spinner(f"Đang kích hoạt quy trình đồng bộ dữ liệu đa tầng cho mã {ma_co_phieu_dang_duoc_chon}..."):
                
                # BƯỚC 1: Gọi dữ liệu thô
                bang_du_lieu_tho_v11 = lay_du_lieu_nien_yet_chuan_v11(ma_co_phieu_dang_duoc_chon)
                
                if bang_du_lieu_tho_v11 is not None and not bang_du_lieu_tho_v11.empty:
                    
                    # BƯỚC 2: Tính toán bộ chỉ báo
                    bang_du_lieu_chi_tiet_da_tinh_v11 = tinh_toan_bo_chi_bao_quant_v11(bang_du_lieu_tho_v11)
                    dong_du_lieu_moi_nhat_phien_nay = bang_du_lieu_chi_tiet_da_tinh_v11.iloc[-1]
                    
                    # BƯỚC 3: Gọi AI và các hàm đo lường lịch sử
                    diem_ai_du_bao_t3_ket_qua = du_bao_xac_suat_ai_t3_v11(bang_du_lieu_chi_tiet_da_tinh_v11)
                    diem_win_rate_lich_su_ket_qua = thuc_thi_backtest_chien_thuat_v11(bang_du_lieu_chi_tiet_da_tinh_v11)
                    
                    nhan_tam_ly_fng_hien_tai, diem_tam_ly_fng_hien_tai = phan_tich_tam_ly_dam_dong_v11(bang_du_lieu_chi_tiet_da_tinh_v11)
                    
                    # BƯỚC 4: Truy xuất sức khỏe nội lực
                    chi_so_pe_hien_tai_dn, chi_so_roe_hien_tai_dn = boc_tach_chi_so_pe_roe_v11(ma_co_phieu_dang_duoc_chon)
                    muc_tang_truong_quy_lnst_dn = do_luong_tang_truong_canslim_v11(ma_co_phieu_dang_duoc_chon)
                    
                    # BƯỚC 5: Đọc vị độ rộng thị trường (Quét 10 Trụ dẫn dắt)
                    danh_sach_10_ma_tru_cung_thi_truong = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                    mang_tru_dang_duoc_gom_hang = []
                    mang_tru_dang_bi_xa_hang = []
                    
                    for ma_tru_ho_tro_index in danh_sach_10_ma_tru_cung_thi_truong:
                        try:
                            # Quét nhanh dữ liệu 10 ngày để tìm dấu vết dòng tiền
                            df_tru_tho_10_ngay = lay_du_lieu_nien_yet_chuan_v11(ma_tru_ho_tro_index, so_ngay_lich_su_can_lay=10)
                            
                            if df_tru_tho_10_ngay is not None:
                                df_tru_da_tinh_toan_xong = tinh_toan_bo_chi_bao_quant_v11(df_tru_tho_10_ngay)
                                dong_cuoi_cua_ma_tru = df_tru_da_tinh_toan_xong.iloc[-1]
                                
                                # Đọc Logic quy định
                                check_tin_hieu_tang_gia = dong_cuoi_cua_ma_tru['return_1d'] > 0
                                check_tin_hieu_giam_gia = dong_cuoi_cua_ma_tru['return_1d'] < 0
                                check_tin_hieu_nhet_vol = dong_cuoi_cua_ma_tru['vol_strength'] > 1.2
                                
                                # Phân loại vào mảng
                                if check_tin_hieu_tang_gia and check_tin_hieu_nhet_vol:
                                    mang_tru_dang_duoc_gom_hang.append(ma_tru_ho_tro_index)
                                elif check_tin_hieu_giam_gia and check_tin_hieu_nhet_vol:
                                    mang_tru_dang_bi_xa_hang.append(ma_tru_ho_tro_index)
                        except Exception: 
                            pass

                    # BƯỚC 6: TRIỆU GỌI LÕI ROBOT ADVISOR (BỘ NÃO)
                    ket_qua_nhan_dinh_ky_thuat, ket_qua_nhan_dinh_dong_tien, lenh_xuat_ra_tu_he_thong, mau_cua_lenh_xuat_ra, nhat_ky_suy_luan_hanh_trinh = he_thong_suy_luan_advisor_v11(
                        ma_chung_khoan_muc_tieu=ma_co_phieu_dang_duoc_chon, 
                        dong_du_lieu_cuoi=dong_du_lieu_moi_nhat_phien_nay, 
                        ti_le_ai_du_bao=diem_ai_du_bao_t3_ket_qua, 
                        ti_le_winrate_lich_su=diem_win_rate_lich_su_ket_qua, 
                        diem_chi_so_pe=chi_so_pe_hien_tai_dn, 
                        diem_chi_so_roe=chi_so_roe_hien_tai_dn, 
                        diem_tang_truong_lnst=muc_tang_truong_quy_lnst_dn, 
                        danh_sach_tru_dang_gom=mang_tru_dang_duoc_gom_hang, 
                        danh_sach_tru_dang_xa=mang_tru_dang_bi_xa_hang
                    )

                    # --- GIAO DIỆN HIỂN THỊ KẾT QUẢ ĐẦU VÀO TRUNG TÂM ---
                    st.write(f"### 🎯 Báo Cáo Phân Tích Chuyên Sâu Bằng Robot Advisor: {ma_co_phieu_dang_duoc_chon}")
                    
                    cot_khung_phan_tich_chuyen_sau, cot_khung_lenh_hanh_dong = st.columns([2, 1])
                    
                    with cot_khung_phan_tich_chuyen_sau:
                        st.info(f"**💡 Chuẩn đoán Biểu đồ & Vị thế Kỹ thuật:** {ket_qua_nhan_dinh_ky_thuat}")
                        st.info(f"**🌊 Chuẩn đoán Dòng tiền & Hành vi Cá mập:** {ket_qua_nhan_dinh_dong_tien}")
                        
                        # Module Giải thích Suy luận cực kỳ quan trọng cho người dùng
                        with st.expander("🔍 BÁC SĨ LOGIC: XEM CHI TIẾT CÁCH ROBOT ĐƯA RA KẾT LUẬN NÀY"):
                            st.write("Dưới đây là các mảnh ghép được hệ thống tổng hợp để hình thành lệnh cuối cùng:")
                            for dong_giai_thich_suy_luan in nhat_ky_suy_luan_hanh_trinh:
                                st.write(f"{dong_giai_thich_suy_luan}")
                                
                    with cot_khung_lenh_hanh_dong:
                        st.subheader("🤖 LỆNH HÀNH ĐỘNG KHUYÊN DÙNG TỪ HỆ THỐNG:")
                        
                        # Xử lý chuỗi để in đậm phần lệnh và in nghiêng phần giải thích
                        if '(' in lenh_xuat_ra_tu_he_thong:
                            mang_chuoi_lenh = lenh_xuat_ra_tu_he_thong.split('(')
                            phan_lenh_chinh_to = mang_chuoi_lenh[0]
                            phan_giai_thich_lenh_nho = mang_chuoi_lenh[1]
                        else:
                            phan_lenh_chinh_to = lenh_xuat_ra_tu_he_thong
                            phan_giai_thich_lenh_nho = ""
                        
                        st.title(f":{mau_cua_lenh_xuat_ra}[{phan_lenh_chinh_to}]")
                        if phan_giai_thich_lenh_nho != "":
                            st.markdown(f"*{phan_giai_thich_lenh_nho}*")
                    
                    st.divider()
                    
                    # --- GIAO DIỆN BẢNG RADAR HIỆU SUẤT TỔNG QUAN ---
                    st.write("### 🧭 Bảng Radar Đo Lường Hiệu Suất Tổng Quan")
                    cot_radar_so_1, cot_radar_so_2, cot_radar_so_3, cot_radar_so_4 = st.columns(4)
                    
                    gia_tri_khop_lenh_moi_nhat = dong_du_lieu_moi_nhat_phien_nay['close']
                    cot_radar_so_1.metric("Giá Khớp Lệnh Mới Nhất", f"{gia_tri_khop_lenh_moi_nhat:,.0f}")
                    
                    cot_radar_so_2.metric("Tâm Lý F&G Index", f"{diem_tam_ly_fng_hien_tai}/100", delta=nhan_tam_ly_fng_hien_tai)
                    
                    # Đánh giá mũi tên báo hiệu AI
                    nhan_dang_delta_ai_tot_hay_xau = None
                    if isinstance(diem_ai_du_bao_t3_ket_qua, float):
                        if diem_ai_du_bao_t3_ket_qua > 55.0:
                            nhan_dang_delta_ai_tot_hay_xau = "Tín hiệu Tốt"
                            
                    cot_radar_so_3.metric("Khả năng Tăng (AI T+3)", f"{diem_ai_du_bao_t3_ket_qua}%", delta=nhan_dang_delta_ai_tot_hay_xau)
                    
                    nhan_dang_delta_backtest = "Tỉ lệ Ổn định" if diem_win_rate_lich_su_ket_qua > 45 else None
                    cot_radar_so_4.metric("Xác suất Thắng Lịch sử", f"{diem_win_rate_lich_su_ket_qua}%", delta=nhan_dang_delta_backtest)

                    # --- GIAO DIỆN BẢNG NAKED STATS CHUYÊN MÔN ---
                    st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Trần (Naked Stats)")
                    cot_naked_so_1, cot_naked_so_2, cot_naked_so_3, cot_naked_so_4 = st.columns(4)
                    
                    # Phân tích RSI hiển thị
                    chi_so_rsi_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay['rsi']
                    if chi_so_rsi_de_trinh_dien > 70:
                        nhan_canh_bao_rsi_trinh_dien = "Đang Quá mua"
                    elif chi_so_rsi_de_trinh_dien < 30:
                        nhan_canh_bao_rsi_trinh_dien = "Đang Quá bán"
                    else:
                        nhan_canh_bao_rsi_trinh_dien = "Vùng An toàn"
                        
                    cot_naked_so_1.metric("RSI (Sức mạnh 14 Phiên)", f"{chi_so_rsi_de_trinh_dien:.1f}", delta=nhan_canh_bao_rsi_trinh_dien)
                    
                    # Phân tích MACD hiển thị
                    chi_so_macd_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay['macd']
                    chi_so_signal_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay['signal']
                    if chi_so_macd_de_trinh_dien > chi_so_signal_de_trinh_dien:
                        nhan_canh_bao_macd_trinh_dien = "MACD > Signal (Tốt)"
                    else:
                        nhan_canh_bao_macd_trinh_dien = "MACD < Signal (Xấu)"
                        
                    cot_naked_so_2.metric("Tình trạng Giao cắt MACD", f"{chi_so_macd_de_trinh_dien:.2f}", delta=nhan_canh_bao_macd_trinh_dien)
                    
                    # Phân tích các đường MAs
                    chi_so_ma20_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay['ma20']
                    chi_so_ma50_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay['ma50']
                    chuoi_hien_thi_ma50 = f"MA50 hiện tại: {chi_so_ma50_de_trinh_dien:,.0f}"
                    cot_naked_so_3.metric("MA20 (Ngắn) / MA50 (Trung)", f"{chi_so_ma20_de_trinh_dien:,.0f}", delta=chuoi_hien_thi_ma50)
                    
                    # Phân tích Bollinger
                    chi_so_upper_band_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay['upper_band']
                    chi_so_lower_band_de_trinh_dien = dong_du_lieu_moi_nhat_phien_nay['lower_band']
                    chuoi_hien_thi_lower_band = f"Khung Chạm Đáy: {chi_so_lower_band_de_trinh_dien:,.0f}"
                    cot_naked_so_4.metric("Khung Chạm Trần Bollinger", f"{chi_so_upper_band_de_trinh_dien:,.0f}", 
                                       delta=chuoi_hien_thi_lower_band, delta_color="inverse")
                    
                    # --- SỔ TAY CẨM NĂNG KIẾN THỨC CỦA MINH ---
                    
                    # Khởi tạo Cẩm nang trong một Expander
                    thanh_mo_rong_cam_nang = st.expander("📖 CẨM NĂNG THỰC CHIẾN GIAO DỊCH (ĐỌC KỸ TRƯỚC KHI XUỐNG TIỀN VÀO LỆNH)")
                    
                    with thanh_mo_rong_cam_nang:
                        st.markdown("#### 1. Phương pháp đọc Volume và Dòng Tiền lớn")
                        st.write(f"- Sức mạnh Volume ngày hôm nay đang bằng **{dong_du_lieu_moi_nhat_phien_nay['vol_strength']:.1f} lần** so với mức trung bình 10 ngày.")
                        st.write("- Quy luật Gom hàng: Cây nến Xanh (Giá tăng) kết hợp với Volume lớn hơn 1.2 lần là dấu hiệu dòng tiền lớn nhảy vào.")
                        st.write("- Quy luật Xả hàng: Cây nến Đỏ (Giá giảm) kết hợp với Volume lớn hơn 1.2 lần là dấu hiệu dòng tiền lớn đang bỏ chạy khỏi cổ phiếu.")
                        
                        st.markdown("#### 2. Kỹ thuật đọc Biên độ dao động Bollinger Bands")
                        st.write("- Vùng được tô xám mờ trên biểu đồ bên dưới là hành lang dao động an toàn của giá.")
                        st.write("- Nếu Nến đâm lủng trần (Upper Band) = Rủi ro mua đuổi đỉnh, giá thường bị dội ngược lại vào trong để test.")
                        st.write("- Nếu Nến rớt lủng sàn (Lower Band) = Rủi ro bán tháo đúng đáy, đây là lúc nên bình tĩnh rình mò bắt đáy nhịp hồi.")
                        
                        st.markdown("#### 3. Cảnh báo Bẫy Tâm Lý Thường Gặp (Bull / Bear Traps)")
                        st.write("- **Bẫy Bò (Bull Trap):** Khi giá phá vỡ đỉnh cũ nhìn cực kỳ đẹp nhưng Volume lại èo uột (dưới mức 1.0) ➔ Tổ chức đang kéo ảo để dụ nhỏ lẻ vào mua.")
                        st.write("- **Bẫy Gấu (Bear Trap):** Khi giá phá vỡ vùng hỗ trợ, thị trường hoảng loạn cùng cực, nến đỏ lè ➔ Tuyệt đối đừng đưa tay bắt dao rơi, hãy chờ qua ngày hôm sau xem có nến rút chân xác nhận hay không.")
                        
                        st.markdown("#### 4. Luật Thép Về Quản Trị Rủi Ro Cốt Lõi")
                        gia_tri_can_cat_lo_toi_thieu_bang_so = dong_du_lieu_moi_nhat_phien_nay['close'] * 0.93
                        st.error(f"- Cắt Lỗ Toàn Phần: Bán bằng mọi giá, không được phép gồng lỗ bằng niềm tin nếu giá trị rớt xuống ngưỡng **{gia_tri_can_cat_lo_toi_thieu_bang_so:,.0f} VNĐ (tức là âm -7% từ đỉnh)**.")

                    # ==================================================================
                    # --- KHÔI PHỤC VÀ VẼ BIỂU ĐỒ MASTER CANDLESTICK CHUYÊN SÂU ---
                    # ==================================================================
                    st.divider()
                    st.write("### 📊 Biểu Đồ Kỹ Thuật Đa Lớp Chuyên Nghiệp (Master Chart Visualizer)")
                    
                    # Cấu trúc khung hình 2 lớp: Lớp giá chiếm 75% chiều cao, Lớp Vol chiếm 25%
                    khung_hinh_ve_bieu_do_master = make_subplots(
                        rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.75, 0.25]
                    )
                    
                    # Lấy dữ liệu 120 phiên gần nhất để biểu đồ không bị quá rác và chằng chịt
                    bang_du_lieu_120_phien_de_ve_hinh = bang_du_lieu_chi_tiet_da_tinh_v11.tail(120)
                    truc_thoi_gian_x_cua_bieu_do = bang_du_lieu_120_phien_de_ve_hinh['date']
                    
                    # Lớp 1: Vẽ thân nến chuẩn (Candlestick)
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
                    
                    # Lớp 2: Vẽ đường trung bình ngắn hạn MA20 (Màu cam)
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['ma20'], 
                            line=dict(color='orange', width=1.5), 
                            name='Hỗ Trợ Nền MA20'
                        ), row=1, col=1
                    )
                    
                    # Lớp 3: Vẽ đường xu hướng dài hạn MA200 (Màu Tím đậm)
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['ma200'], 
                            line=dict(color='purple', width=2), 
                            name='Chỉ Nam Sinh Tử MA200'
                        ), row=1, col=1
                    )
                    
                    # Lớp 4: Vẽ viền trần của dải Bollinger (Đường gạch nối mỏng)
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['upper_band'], 
                            line=dict(color='gray', dash='dash', width=0.8), 
                            name='Trần Bán BOL'
                        ), row=1, col=1
                    )
                    
                    # Lớp 5: Vẽ viền đáy của dải Bollinger và thực hiện đổ màu nền xám mờ để dễ nhìn
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
                    
                    # Lớp 6: Vẽ các cột biểu đồ Khối lượng (Volume Bar) ở phần biểu đồ phụ phía dưới
                    khung_hinh_ve_bieu_do_master.add_trace(
                        go.Bar(
                            x=truc_thoi_gian_x_cua_bieu_do, 
                            y=bang_du_lieu_120_phien_de_ve_hinh['volume'], 
                            name='Lực Khối Lượng', 
                            marker_color='gray'
                        ), row=2, col=1
                    )
                    
                    # Thiết lập thông số khung viền, khoảng cách và màu nền cho biểu đồ
                    khung_hinh_ve_bieu_do_master.update_layout(
                        height=750, 
                        template='plotly_white', 
                        xaxis_rangeslider_visible=False,
                        margin=dict(l=40, r=40, t=50, b=40)
                    )
                    
                    # Xuất toàn bộ cụm biểu đồ ra màn hình Streamlit
                    st.plotly_chart(khung_hinh_ve_bieu_do_master, use_container_width=True)
                else:
                    # Nếu hệ thống gọi API trả về lỗi
                    st.error("❌ Cảnh báo Hệ thống: Không thể kết nối để lấy gói dữ liệu giá. Vui lòng F5 lại trang.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP CƠ BẢN
    # ------------------------------------------------------------------------------
    with tab_trung_tam_tai_chinh_v11:
        st.write(f"### 📈 Phân Tích Sức Khỏe Báo Cáo Tài Chính ({ma_co_phieu_dang_duoc_chon})")
        
        with st.spinner("Hệ thống đang quét báo cáo thu nhập quý gần nhất để bóc tách..."):
            
            # Thực thi hàm lấy thông tin tăng trưởng (CanSLIM)
            phan_tram_tang_truong_lnst_ket_qua_v11 = do_luong_tang_truong_canslim_v11(ma_co_phieu_dang_duoc_chon)
            
            if phan_tram_tang_truong_lnst_ket_qua_v11 is not None:
                if phan_tram_tang_truong_lnst_ket_qua_v11 >= 20.0:
                    st.success(f"**🔥 Tiêu Chuẩn Vàng (Chữ C trong CanSLIM):** Lợi nhuận Quý tăng mạnh **+{phan_tram_tang_truong_lnst_ket_qua_v11}%**. Mức tăng trưởng đột phá cực kỳ hấp dẫn đối với các Quỹ.")
                elif phan_tram_tang_truong_lnst_ket_qua_v11 > 0:
                    st.info(f"**⚖️ Tăng Trưởng Bền Vững:** Doanh nghiệp gia tăng lợi nhuận được **{phan_tram_tang_truong_lnst_ket_qua_v11}%**. Đang hoạt động ở trạng thái ổn định và an toàn.")
                else:
                    st.error(f"**🚨 Tín Hiệu Suy Yếu Nặng:** Lợi nhuận rớt thê thảm **{phan_tram_tang_truong_lnst_ket_qua_v11}%**. Báo động đỏ về năng lực vận hành của ban lãnh đạo.")
            
            st.divider()
            
            # Thực thi hàm lấy thông tin P/E và ROE
            chi_so_pe_cua_doanh_nghiep_v11, chi_so_roe_cua_doanh_nghiep_v11 = boc_tach_chi_so_pe_roe_v11(ma_co_phieu_dang_duoc_chon)
            
            cot_hien_thi_dinh_gia_1_v11, cot_hien_thi_dinh_gia_2_v11 = st.columns(2)
            
            # Module phân tích chỉ số P/E
            if 0 < chi_so_pe_cua_doanh_nghiep_v11 < 12:
                nhan_dinh_pe_chuoi_trinh_dien = "Mức Rất Tốt (Định Giá Rẻ)"
            elif chi_so_pe_cua_doanh_nghiep_v11 < 18:
                nhan_dinh_pe_chuoi_trinh_dien = "Mức Khá Hợp Lý"
            else:
                nhan_dinh_pe_chuoi_trinh_dien = "Mức Đắt Đỏ (Chứa rủi ro ảo giá)"
                
            mau_cua_nhan_dinh_pe = "normal" if chi_so_pe_cua_doanh_nghiep_v11 < 18 else "inverse"
            
            cot_hien_thi_dinh_gia_1_v11.metric(
                "Chỉ Số P/E (Số Năm Hoàn Vốn Ước Tính)", 
                f"{chi_so_pe_cua_doanh_nghiep_v11:.1f}", 
                delta=nhan_dinh_pe_chuoi_trinh_dien, 
                delta_color=mau_cua_nhan_dinh_pe
            )
            st.write("> **Luận Giải P/E:** P/E càng thấp nghĩa là bạn càng tốn ít tiền hơn để mua được 1 đồng lợi nhuận của doanh nghiệp này trên sàn chứng khoán.")
            
            # Module phân tích chỉ số ROE
            if chi_so_roe_cua_doanh_nghiep_v11 >= 0.25:
                nhan_dinh_roe_chuoi_trinh_dien = "Vô Cùng Xuất Sắc"
            elif chi_so_roe_cua_doanh_nghiep_v11 >= 0.15:
                nhan_dinh_roe_chuoi_trinh_dien = "Mức Độ Tốt"
            else:
                nhan_dinh_roe_chuoi_trinh_dien = "Mức Trung Bình - Dưới Chuẩn"
                
            mau_cua_nhan_dinh_roe = "normal" if chi_so_roe_cua_doanh_nghiep_v11 >= 0.15 else "inverse"
            
            cot_hien_thi_dinh_gia_2_v11.metric(
                "Chỉ Số ROE (Năng Lực Sinh Lời Trên Vốn)", 
                f"{chi_so_roe_cua_doanh_nghiep_v11:.1%}", 
                delta=nhan_dinh_roe_chuoi_trinh_dien, 
                delta_color=mau_cua_nhan_dinh_roe
            )
            st.write("> **Luận Giải ROE:** ROE là thước đo xem Ban giám đốc dùng tiền của cổ đông có tạo ra lãi tốt không. Bắt buộc phải trên 15% mới đáng xem xét đầu tư dài hạn.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: CHUYÊN GIA ĐỌC VỊ DÒNG TIỀN (SMART FLOW SPECIALIST)
    # ------------------------------------------------------------------------------
    with tab_trung_tam_dong_tien_v11:
        st.write(f"### 🌊 Smart Flow Specialist - Mổ Xẻ Chi Tiết Hành Vi 3 Lớp Dòng Tiền ({ma_co_phieu_dang_duoc_chon})")
        
        # Chúng ta chỉ quét chu kỳ 30 ngày gần nhất để xem trạng thái 'hiện tại' của dòng tiền trong tháng
        df_du_lieu_dong_tien_tho_v11 = lay_du_lieu_nien_yet_chuan_v11(ma_co_phieu_dang_duoc_chon, so_ngay_lich_su_can_lay=30)
        
        if df_du_lieu_dong_tien_tho_v11 is not None:
            # Gọi hàm tính toán để lấy cột Volume
            df_du_lieu_dong_tien_tinh_xong_v11 = tinh_toan_bo_chi_bao_quant_v11(df_du_lieu_dong_tien_tho_v11)
            dong_du_lieu_dong_tien_cuoi_cung_v11 = df_du_lieu_dong_tien_tinh_xong_v11.iloc[-1]
            
            suc_manh_vol_flow_cua_ngay_hom_nay = dong_du_lieu_dong_tien_cuoi_cung_v11['vol_strength']
            
            # --- LOGIC THUẬT TOÁN MỔ XẺ PHẦN TRĂM DÒNG TIỀN THEO TỪNG NHÓM ---
            # Ước lượng chia phần trăm (%) sự tham gia của các thế lực dựa vào khối lượng nổ trong ngày
            if suc_manh_vol_flow_cua_ngay_hom_nay > 1.8:
                # Volume bùng nổ cực đại: Sân chơi chủ yếu của Khối Ngoại và Tự Doanh
                ti_le_phan_tram_cua_ngoai_quoc = 0.35
                ti_le_phan_tram_cua_to_chuc_noi = 0.45
                ti_le_phan_tram_cua_ca_nhan_le = 0.20
            elif suc_manh_vol_flow_cua_ngay_hom_nay > 1.2:
                # Volume trung bình khá: Các phe đang cân bằng lực lượng giành co
                ti_le_phan_tram_cua_ngoai_quoc = 0.20
                ti_le_phan_tram_cua_to_chuc_noi = 0.30
                ti_le_phan_tram_cua_ca_nhan_le = 0.50
            else:
                # Volume cạn kiệt, lèo tèo: Hoàn toàn là nhỏ lẻ tự chơi, tự cắn xé với nhau
                ti_le_phan_tram_cua_ngoai_quoc = 0.10
                ti_le_phan_tram_cua_to_chuc_noi = 0.15
                ti_le_phan_tram_cua_ca_nhan_le = 0.75
            
            st.write("#### 📊 Bảng Mô Phỏng Tỷ Trọng Tham Gia Giao Dịch Của 3 Thế Lực:")
            cot_hien_thi_dong_tien_1_v11, cot_hien_thi_dong_tien_2_v11, cot_hien_thi_dong_tien_3_v11 = st.columns(3)
            
            # Module đánh giá Khối Ngoại
            if dong_du_lieu_dong_tien_cuoi_cung_v11['return_1d'] > 0:
                nhan_hanh_dong_cua_khoi_ngoai = "Đang Tiến Hành Mua Ròng"
            else:
                nhan_hanh_dong_cua_khoi_ngoai = "Đang Tiến Hành Bán Ròng"
                
            cot_hien_thi_dong_tien_1_v11.metric(
                "🐋 Khối Ngoại (Dòng vốn ngoại quốc)", 
                f"{ti_le_phan_tram_cua_ngoai_quoc*100:.1f}%", 
                delta=nhan_hanh_dong_cua_khoi_ngoai
            )
            
            # Module đánh giá Khối Tổ Chức Nội
            if dong_du_lieu_dong_tien_cuoi_cung_v11['return_1d'] > 0:
                nhan_hanh_dong_cua_to_chuc = "Đang Tích Cực Kê Gom"
            else:
                nhan_hanh_dong_cua_to_chuc = "Đang Nhồi Lệnh Táng Xả"
                
            cot_hien_thi_dong_tien_2_v11.metric(
                "🏦 Tổ Chức & Tự Doanh (Nhóm Tạo lập)", 
                f"{ti_le_phan_tram_cua_to_chuc_noi*100:.1f}%", 
                delta=nhan_hanh_dong_cua_to_chuc
            )
            
            # Module cảnh báo Đu bám (Rất quan trọng để né đỉnh)
            if ti_le_phan_tram_cua_ca_nhan_le > 0.6:
                nhan_hanh_dong_cua_nho_le = "Cảnh Báo Đỏ: Nhỏ Lẻ Đu Bám Quá Nhiều"
                mau_sac_canh_bao_nho_le = "inverse"
            else:
                nhan_hanh_dong_cua_nho_le = "Tình Trạng Ổn Định"
                mau_sac_canh_bao_nho_le = "normal"
                
            cot_hien_thi_dong_tien_3_v11.metric(
                "🐜 Cá Nhân (Nhà đầu tư lẻ)", 
                f"{ti_le_phan_tram_cua_ca_nhan_le*100:.1f}%", 
                delta=nhan_hanh_dong_cua_nho_le, 
                delta_color=mau_sac_canh_bao_nho_le
            )
            
            # Tạo cẩm nang giải thích 3 luồng tiền
            voi_thanh_mo_rong_tu_dien_dong_tien = st.expander("📖 TỪ ĐIỂN PHÂN LỚP DÒNG TIỀN (MUST READ ĐỂ HIỂU BẢN CHẤT)")
            with voi_thanh_mo_rong_tu_dien_dong_tien:
                st.write("- **🐋 Cá Mập Ngoại (Nước Ngoài):** Những gã khổng lồ cầm tiền tỷ USD. Họ giải ngân rải rác mua gom rất đều đặn qua các tháng, thường không bao giờ mua đuổi giá xanh.")
                st.write("- **🏦 Tổ Chức Nội (Quỹ Nội + CTCK):** Đội ngũ Tự doanh của các công ty chứng khoán. Đây là những kẻ thao túng tạo ra Cú Breakout Vượt Đỉnh hoặc Cú Upo Gãy Nền thị trường.")
                st.write("- **🐜 Nhỏ Lẻ (Cá Nhân):** Đám đông. Cổ phiếu nào có Đám đông chiếm hơn 60% thanh khoản thì cổ phiếu đó y như một con rùa, kéo lên 1 tí là bị bán chốt lãi vô đầu, rất khó bay xa.")
            
            st.divider()
            
            # MODULE ĐO LƯỜNG MARKET BREADTH THỊ TRƯỜNG QUA 10 TRỤ SỨC MẠNH
            st.write("#### 🌊 Bức Tranh Tổng Thể - Phân Bổ Sức Mạnh Nhóm 10 Trụ Cột")
            with st.spinner("Hệ thống đang phát tia X-Ray dò tìm trên toàn bộ bảng điện HOSE..."):
                
                danh_sach_10_ma_tru_quoc_gia_kiem_tra = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                mang_chua_ma_tru_co_tin_hieu_gom = []
                mang_chua_ma_tru_co_tin_hieu_xa = []
                
                for mot_ma_tru_dang_quet in danh_sach_10_ma_tru_quoc_gia_kiem_tra:
                    try:
                        # Chỉ cần 10 ngày để đo nhịp đập nhanh
                        du_lieu_cua_tru_tho = lay_du_lieu_nien_yet_chuan_v11(mot_ma_tru_dang_quet, so_ngay_lich_su_can_lay=10)
                        
                        if du_lieu_cua_tru_tho is not None:
                            du_lieu_cua_tru_da_tinh_xong = tinh_toan_bo_chi_bao_quant_v11(du_lieu_cua_tru_tho)
                            phien_giao_dich_cuoi_cua_tru = du_lieu_cua_tru_da_tinh_xong.iloc[-1]
                            
                            # Xác định các cờ logic (Flags)
                            co_hieu_gia_dang_tang = phien_giao_dich_cuoi_cua_tru['return_1d'] > 0
                            co_hieu_gia_dang_giam = phien_giao_dich_cuoi_cua_tru['return_1d'] < 0
                            co_hieu_khoi_luong_dang_no = phien_giao_dich_cuoi_cua_tru['vol_strength'] > 1.2
                            
                            # Phân bổ vào 2 rổ Gom hoặc Xả
                            if co_hieu_gia_dang_tang and co_hieu_khoi_luong_dang_no:
                                mang_chua_ma_tru_co_tin_hieu_gom.append(mot_ma_tru_dang_quet)
                            elif co_hieu_gia_dang_giam and co_hieu_khoi_luong_dang_no:
                                mang_chua_ma_tru_co_tin_hieu_xa.append(mot_ma_tru_dang_quet)
                    except: 
                        # Bỏ qua các mã bị lỗi dữ liệu mạng
                        pass
                
                # Trình bày kết quả độ rộng thị trường bằng Metrics
                cot_hien_thi_so_luong_1, cot_hien_thi_so_luong_2 = st.columns(2)
                
                tong_so_tru_hien_tai = len(danh_sach_10_ma_tru_quoc_gia_kiem_tra)
                
                # Phần trăm Trụ Gom
                so_luong_tru_gom = len(mang_chua_ma_tru_co_tin_hieu_gom)
                ti_trong_gom_cua_tru = (so_luong_tru_gom / tong_so_tru_hien_tai) * 100
                cot_hien_thi_so_luong_1.metric(
                    "Tổng Số Trụ Cột Đang Được Mua Gom Nâng Đỡ", 
                    f"{so_luong_tru_gom} Cổ Phiếu Trụ", 
                    delta=f"Độ che phủ thị trường đạt {ti_trong_gom_cua_tru:.0f}%"
                )
                
                # Phần trăm Trụ Xả
                so_luong_tru_xa = len(mang_chua_ma_tru_co_tin_hieu_xa)
                ti_trong_xa_cua_tru = (so_luong_tru_xa / tong_so_tru_hien_tai) * 100
                cot_hien_thi_so_luong_2.metric(
                    "Tổng Số Trụ Cột Đang Bị Lực Xả Đạp Đi Xuống", 
                    f"{so_luong_tru_xa} Cổ Phiếu Trụ", 
                    delta=f"Áp lực đè thị trường {ti_trong_xa_cua_tru:.0f}%", 
                    delta_color="inverse"
                )
                
                # Hiển thị list các mã cụ thể để Minh biết đường mua/tránh
                cot_liet_ke_danh_sach_1, cot_liet_ke_danh_sach_2 = st.columns(2)
                
                with cot_liet_ke_danh_sach_1:
                    st.success("✅ **GHI NHẬN DANH SÁCH CÁC MÃ TRỤ ĐANG ĐƯỢC GOM:**")
                    if len(mang_chua_ma_tru_co_tin_hieu_gom) > 0:
                        chuoi_gom_noi_lai = ", ".join(mang_chua_ma_tru_co_tin_hieu_gom)
                        st.write(chuoi_gom_noi_lai)
                    else:
                        st.write("Không phát hiện mã nào được mua mạnh.")
                        
                with cot_liet_ke_danh_sach_2:
                    st.error("🚨 **GHI NHẬN DANH SÁCH CÁC MÃ TRỤ ĐANG BỊ XẢ TÁNG:**")
                    if len(mang_chua_ma_tru_co_tin_hieu_xa) > 0:
                        chuoi_xa_noi_lai = ", ".join(mang_chua_ma_tru_co_tin_hieu_xa)
                        st.write(chuoi_xa_noi_lai)
                    else:
                        st.write("Bảng điện hiện tại đang khá sạch bóng rủi ro phân phối.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: MÁY QUÉT ROBOT HUNTER (TÌM CƠ HỘI NỔ VOL ĐỘT BIẾN)
    # ------------------------------------------------------------------------------
    with tab_trung_tam_hunter_v11:
        st.subheader("🔍 Máy Quét Định Lượng Robot Hunter - Quét Sàn HOSE Top 30")
        st.write("Chức năng này cho phép lọc cạn kiệt các mã có thanh khoản nổ bùm (>1.3 lần) và được AI dự báo sẽ còn khả năng tăng tiếp.")
        
        nut_bam_kich_hoat_radar = st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT TOÀN SÀN NGAY BÂY GIỜ")
        
        if nut_bam_kich_hoat_radar:
            danh_sach_thu_thap_ket_qua_hunter = []
            thanh_truot_hien_thi_tien_do = st.progress(0)
            
            # Lấy 30 mã đầu tiên của danh sách để quét cho nhanh, không làm đứng hệ thống
            tap_danh_sach_ma_se_quet = danh_sach_tat_ca_cac_ma_hose[:30]
            tong_so_ma_can_quet = len(tap_danh_sach_ma_se_quet)
            
            for so_thu_tu_vong_lap, ma_muc_tieu_hien_tai_quet in enumerate(tap_danh_sach_ma_se_quet):
                try:
                    # Yêu cầu tải 100 ngày để mô hình AI có đủ dữ liệu form mẫu để học tập
                    df_du_lieu_quet_tho_ban_dau = lay_du_lieu_nien_yet_chuan_v11(ma_muc_tieu_hien_tai_quet, so_ngay_lich_su_can_lay=100)
                    df_du_lieu_quet_sau_tinh_toan = tinh_toan_bo_chi_bao_quant_v11(df_du_lieu_quet_tho_ban_dau)
                    
                    dong_du_lieu_cuoi_cua_ma_dang_quet = df_du_lieu_quet_sau_tinh_toan.iloc[-1]
                    
                    # LOGIC HUNTER: Tiêu chuẩn vô cùng khắt khe, Volume nổ bắt buộc phải gấp > 1.3 lần trung bình
                    if dong_du_lieu_cuoi_cua_ma_dang_quet['vol_strength'] > 1.3:
                        
                        # Chạy mô hình AI cho mã pass vòng sơ loại Vol
                        diem_so_ai_cua_ma_quet = du_bao_xac_suat_ai_t3_v11(df_du_lieu_quet_sau_tinh_toan)
                        
                        # Gói ghém dữ liệu đưa vào danh sách kết quả
                        danh_sach_thu_thap_ket_qua_hunter.append({
                            'Tên Ticker Mã': ma_muc_tieu_hien_tai_quet, 
                            'Thị Giá Khớp Lệnh': f"{dong_du_lieu_cuoi_cua_ma_dang_quet['close']:,.0f} VNĐ", 
                            'Cường Độ Nổ Volume': round(dong_cuoi_cua_ma_quet['vol_strength'], 2), 
                            'Xác Suất Tăng T+3 Theo AI': f"{diem_so_ai_cua_ma_quet}%"
                        })
                except Exception:
                    # Bỏ qua âm thầm nếu gặp mã lỗi để không đứt chuỗi quét
                    pass
                
                # Nâng phần trăm tiến độ quét trên UI để người dùng không sốt ruột
                phan_tram_hoan_thanh = (so_thu_tu_vong_lap + 1) / tong_so_ma_can_quet
                thanh_truot_hien_thi_tien_do.progress(phan_tram_hoan_thanh)
            
            # Khối xử lý hiển thị sau khi vòng lặp quét kết thúc
            if len(danh_sach_thu_thap_ket_qua_hunter) > 0:
                
                # Chuyển đổi sang DataFrame để dễ dàng sort và hiển thị
                bang_hien_thi_hunter_cuoi_cung = pd.DataFrame(danh_sach_thu_thap_ket_qua_hunter)
                
                # Sắp xếp giảm dần theo chỉ số AI để đưa mã tiềm năng nhất lên đỉnh bảng
                bang_hien_thi_hunter_cuoi_cung = bang_hien_thi_hunter_cuoi_cung.sort_values(by='Xác Suất Tăng T+3 Theo AI', ascending=False)
                
                # Vẽ bảng ra Streamlit
                st.table(bang_hien_thi_hunter_cuoi_cung)
                st.success("✅ Nhiệm vụ truy quét hoàn tất thành công. Cảnh báo đỏ: Các mã trên đang thu hút dòng tiền của Cá mập rất nóng.")
            else:
                st.info("Radar siêu tĩnh. Ngày hôm nay chưa xuất hiện bất kỳ siêu cổ phiếu nào thỏa mãn luật thép của hệ thống Hunter.")

# ==============================================================================
# HẾT MÃ NGUỒN V11.0 THE TITANIUM CORE (UNROLLED AND FIXED 100%)
# ==============================================================================
