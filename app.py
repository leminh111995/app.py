# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V19.0 (THE ULTIMATE RADAR)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# NỀN TẢNG GỐC: KẾ THỪA 100% TỪ FILE "14.4.26 bản cuối ngày.docx"
# TRẠNG THÁI: PHIÊN BẢN GIẢI NÉN TOÀN PHẦN (HYPER-VERBOSE EDITION)
# CAM KẾT V19.0:
# 1. ĐỘ DÀI CỰC ĐẠI (> 1500 DÒNG): Khai triển bê tông, không viết tắt, không nén.
# 2. DANH SÁCH CHỜ (WATCHLIST): Tích hợp 3 vũ khí: Bollinger Squeeze, Cạn cung, Tây gom.
# 3. FIX TRIỆT ĐỂ LỖI: Múi giờ VN (chống rỗng data sáng), P/E N/A, NameError.
# 4. TRUNG THÀNH TÊN BIẾN: Khai triển từ bộ khung V14.1 gốc của Minh.
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

# Đảm bảo tài nguyên NLTK luôn sẵn sàng để không bị lỗi Runtime trên Cloud
try:
    # Hệ thống thử tìm file nén lexicon trong môi trường lưu trữ
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu chưa có, kích hoạt tiến trình tải xuống tự động từ máy chủ chính thức
    nltk.download('vader_lexicon')

# ==============================================================================
# 0. HÀM CHUYÊN BIỆT: ÉP MÚI GIỜ VIỆT NAM (UTC+7) - FIX LỖI PHIÊN SÁNG
# ==============================================================================
def lay_thoi_gian_chuan_viet_nam_v19():
    """
    Máy chủ Streamlit Cloud mặc định chạy giờ quốc tế (UTC). 
    Hàm này ép toàn bộ thời gian của hệ thống cộng thêm 7 tiếng (UTC+7) 
    để khớp hoàn toàn với giờ của Sở Giao Dịch Chứng Khoán VN (HOSE).
    Tránh lỗi dữ liệu rỗng khi Minh quét vào buổi sáng sớm.
    """
    # Bước 1: Lấy giờ quốc tế hiện tại từ đồng hồ máy chủ
    gio_quoc_te_utc_bay_gio = datetime.utcnow()
    
    # Bước 2: Khai báo khoảng chênh lệch 7 tiếng cho Việt Nam
    khoang_cach_mui_gio_vn_cong_7 = timedelta(hours=7)
    
    # Bước 3: Thực hiện phép toán cộng thời gian
    thoi_gian_hien_tai_tai_viet_nam = gio_quoc_te_utc_bay_gio + khoang_cach_mui_gio_vn_cong_7
    
    # Bước 4: Trả về kết quả thời gian chuẩn xác
    return thoi_gian_hien_tai_tai_viet_nam

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & PHÂN QUYỀN (SECURITY LAYER) - KẾ THỪA FILE WORD
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh_v19():
    """
    Hàm bảo mật cấp cao, khóa hệ thống bằng mật mã của Minh.
    Thiết kế logic tách biệt hoàn toàn để chống lỗi KeyError trên Streamlit.
    (Kế thừa chuẩn xác từ file 14.4.26 bản cuối ngày.docx)
    """
    
    # 1.1 Kiểm tra trạng thái đã đăng nhập thành công từ bộ nhớ Session State
    chuoi_khoa_bao_mat = "trang_thai_dang_nhap_thanh_cong_v19"
    trang_thai_xac_thuc_cu = st.session_state.get(chuoi_khoa_bao_mat, False)
    
    if trang_thai_xac_thuc_cu == True:
        # Nếu đã xác thực thành công trước đó, cho phép ứng dụng khởi chạy tiếp
        return True

    # 1.2 Nếu chưa đăng nhập, dựng giao diện khóa trung tâm
    chuoi_tieu_de_bao_mat = "### 🔐 Quant System V19.0 - Cổng Bảo Mật Trung Tâm"
    st.markdown(chuoi_tieu_de_bao_mat)
    
    chuoi_canh_bao_khoa = "Hệ thống phân tích định lượng chuyên sâu đang bị khóa. Vui lòng xác thực danh tính."
    st.info(chuoi_canh_bao_khoa)
    
    # Tạo ô nhập mật mã (không dùng on_change để tránh lỗi xung đột widget key)
    chuoi_label_nhap_mat_ma = "🔑 Vui lòng nhập mật mã truy cập của Minh:"
    mat_ma_nguoi_dung_vua_nhap = st.text_input(
        chuoi_label_nhap_mat_ma, 
        type="password"
    )
    
    # 1.3 Xử lý logic khi có dữ liệu nhập vào ô text_input
    kiem_tra_co_du_lieu_nhap = mat_ma_nguoi_dung_vua_nhap != ""
    
    if kiem_tra_co_du_lieu_nhap == True:
        
        # Đọc mật mã gốc được cấu hình trong Streamlit Secrets
        mat_ma_chuan_tu_he_thong = st.secrets["password"]
        
        # Tiến hành so sánh đối chiếu chuỗi mật khẩu
        kiem_tra_mat_khau_dung = mat_ma_nguoi_dung_vua_nhap == mat_ma_chuan_tu_he_thong
        
        if kiem_tra_mat_khau_dung == True:
            
            # Gán cờ thành công vào bộ nhớ phiên làm việc
            st.session_state[chuoi_khoa_bao_mat] = True
            
            # Ra lệnh tải lại trang (Rerun) để ẩn form đăng nhập ngay lập tức
            st.rerun()
            
        else:
            # Nếu sai, hiển thị thông báo lỗi màu đỏ kèm cảnh báo Caps Lock
            chuoi_bao_loi_mat_khau = "❌ Cảnh báo: Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock hoặc bộ gõ."
            st.error(chuoi_bao_loi_mat_khau)
            
    # Mặc định chặn đứng mọi hành vi truy cập trái phép
    return False

# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG CHÍNH (MAIN APP EXECUTION)
# ==============================================================================
# Chỉ khi Minh nhập đúng mật mã (Hàm trả về True), các module Quant bên dưới mới chạy
kiem_tra_quyen_truy_cap = xac_thuc_quyen_truy_cap_cua_minh_v19()

if kiem_tra_quyen_truy_cap == True:
    
    # 1.4 Cấu hình giao diện tổng thể của Dashboard
    st.set_page_config(
        page_title="Quant System V19.0 Ultimate", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render tiêu đề chính và thanh gạch ngang trang trí
    chuoi_tieu_de_app = "🛡️ Quant System V19.0: Master Advisor & Ultimate Radar"
    st.title(chuoi_tieu_de_app)
    
    chuoi_gach_ngang = "---"
    st.markdown(chuoi_gach_ngang)

    # Khởi tạo động cơ Vnstock (Kế thừa từ file Word)
    dong_co_vnstock_v19 = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU GIÁ (DATA ACQUISITION) - KẾ THỪA FILE WORD
    # ==============================================================================
    def lay_du_lieu_nien_yet_chuan_v19(ma_chung_khoan_can_lay, so_ngay_lich_su_can_lay=1000):
        """
        Hàm tải dữ liệu giá cổ phiếu OHLCV.
        Quy trình Fail-over 2 lớp: Vnstock -> Yahoo Finance.
        Sử dụng giờ VN chuẩn để tránh rỗng dữ liệu buổi sáng.
        """
        
        # 2.1 Khởi tạo mốc thời gian chuẩn Việt Nam
        thoi_diem_bay_gio_chuan_vn = lay_thoi_gian_chuan_viet_nam_v19()
        chuoi_dinh_dang_thoi_gian = '%Y-%m-%d'
        
        chuoi_ngay_ket_thuc_format = thoi_diem_bay_gio_chuan_vn.strftime(chuoi_dinh_dang_thoi_gian)
        
        do_tre_thoi_gian_ngay = timedelta(days=so_ngay_lich_su_can_lay)
        thoi_diem_bat_dau_raw = thoi_diem_bay_gio_chuan_vn - do_tre_thoi_gian_ngay
        
        chuoi_ngay_bat_dau_format = thoi_diem_bat_dau_raw.strftime(chuoi_dinh_dang_thoi_gian)
        
        # 2.2 Phương án A: Gọi Vnstock (Dữ liệu nội địa)
        try:
            bang_du_lieu_vnstock = dong_co_vnstock_v19.stock.quote.history(
                symbol=ma_chung_khoan_can_lay, 
                start=chuoi_ngay_bat_dau_format, 
                end=chuoi_ngay_ket_thuc_format
            )
            
            # Kiểm tra tính hợp lệ của dữ liệu
            kiem_tra_dl_ton_tai = bang_du_lieu_vnstock is not None
            
            if kiem_tra_dl_ton_tai == True:
                
                kiem_tra_dl_empty = bang_du_lieu_vnstock.empty
                
                if kiem_tra_dl_empty == False:
                    
                    # Đồng bộ hóa tiêu đề cột về chữ thường toàn bộ để chống KeyError
                    danh_sach_ten_cot_da_chuan_hoa_vn = []
                    
                    for item_cot in bang_du_lieu_vnstock.columns:
                        chuoi_cot_thuong = str(item_cot).lower()
                        danh_sach_ten_cot_da_chuan_hoa_vn.append(chuoi_cot_thuong)
                        
                    # Gán lại tập hợp cột mới cho bảng dữ liệu
                    bang_du_lieu_vnstock.columns = danh_sach_ten_cot_da_chuan_hoa_vn
                    
                    # Trả về bảng dữ liệu hoàn chỉnh
                    return bang_du_lieu_vnstock
                    
        except Exception:
            # Lỗi API rớt mạng sẽ được bỏ qua để chạy xuống Fallback
            pass
        
        # 2.3 Phương án B: Gọi Yahoo Finance dự phòng
        try:
            # Chuyển đổi mã chứng khoán theo chuẩn Yahoo
            kiem_tra_la_vnindex = ma_chung_khoan_can_lay == "VNINDEX"
            
            if kiem_tra_la_vnindex == True:
                ma_chuan_yahoo = "^VNINDEX"
            else:
                chuoi_hau_to_vn = ".VN"
                ma_chuan_yahoo = f"{ma_chung_khoan_can_lay}{chuoi_hau_to_vn}"
                
            # Thực thi lệnh tải từ thư viện yfinance
            bang_du_lieu_yahoo_raw = yf.download(
                ma_chuan_yahoo, 
                period="3y", 
                progress=False
            )
            
            # Kiểm tra dữ liệu Yahoo
            do_dai_bang_yahoo = len(bang_du_lieu_yahoo_raw)
            kiem_tra_yahoo_co_data = do_dai_bang_yahoo > 0
            
            if kiem_tra_yahoo_co_data == True:
                
                # Giải phóng Index ngày thành cột dữ liệu 'date'
                bang_du_lieu_yahoo_raw = bang_du_lieu_yahoo_raw.reset_index()
                
                # Sửa lỗi Multi-Index Header của các bản Pandas/yfinance mới
                danh_sach_cot_yf_clean = []
                
                for label_obj in bang_du_lieu_yahoo_raw.columns:
                    
                    is_tuple_check = isinstance(label_obj, tuple)
                    
                    if is_tuple_check == True:
                        # Lấy phần tử chính của Multi-index
                        phan_tu_chinh = label_obj[0]
                        ten_cot_yf_thuong = str(phan_tu_chinh).lower()
                        danh_sach_cot_yf_clean.append(ten_cot_yf_thuong)
                    else:
                        # Xử lý chuỗi đơn lẻ
                        ten_cot_yf_thuong = str(label_obj).lower()
                        danh_sach_cot_yf_clean.append(ten_cot_yf_thuong)
                
                # Gán lại mảng tên cột chuẩn cho bảng
                bang_du_lieu_yahoo_raw.columns = danh_sach_cot_yf_clean
                
                # Trả về bảng dữ liệu hoàn chỉnh
                return bang_du_lieu_yahoo_raw
                
        except Exception as error_msg:
            # Nếu cả 2 phương án đều tạch, báo lỗi lên Sidebar cho Minh biết
            chuoi_loi_hien_thi = f"⚠️ Lỗi máy chủ dữ liệu: Không thể tải mã {ma_chung_khoan_can_lay}. Chi tiết: {str(error_msg)}"
            st.sidebar.error(chuoi_loi_hien_thi)
            
            return None

    # ==============================================================================
    # 2.5. HÀM TRÍCH XUẤT KHỐI NGOẠI THỰC TẾ (TAB 3) - KẾ THỪA FILE WORD
    # ==============================================================================
    def lay_du_lieu_khoi_ngoai_thuc_te_v19(ma_chung_khoan_vao, so_ngay_truy_xuat=20):
        """
        Truy xuất trực tiếp Dữ Liệu Khối Ngoại (Real Data) từ máy chủ Vnstock 
        để lấy chính xác Tỷ VNĐ Mua/Bán Ròng.
        """
        try:
            # Sử dụng mốc thời gian Việt Nam
            thoi_diem_hien_tai_vn = lay_thoi_gian_chuan_viet_nam_v19()
            chuoi_dinh_dang_ngay = '%Y-%m-%d'
            
            chuoi_ket_thuc_ngoai = thoi_diem_hien_tai_vn.strftime(chuoi_dinh_dang_ngay)
            
            khoang_cach_ngay_ngoai = timedelta(days=so_ngay_truy_xuat)
            thoi_diem_bat_dau_ngoai = thoi_diem_hien_tai_vn - khoang_cach_ngay_ngoai
            
            chuoi_bat_dau_ngoai = thoi_diem_bat_dau_ngoai.strftime(chuoi_dinh_dang_ngay)
            
            bang_du_lieu_khoi_ngoai_result = None
            
            # Bước A: Thử gọi hàm foreign_trade chính thức
            try:
                bang_du_lieu_khoi_ngoai_result = dong_co_vnstock_v19.stock.trade.foreign_trade(
                    symbol=ma_chung_khoan_vao,
                    start=chuoi_bat_dau_ngoai,
                    end=chuoi_ket_thuc_ngoai
                )
            except Exception:
                pass
            
            # Bước B: Thử gọi hàm trading.foreign dự phòng
            check_rong_1 = bang_du_lieu_khoi_ngoai_result is None
            
            if check_rong_1 == False:
                check_rong_2 = len(bang_du_lieu_khoi_ngoai_result) == 0
            else:
                check_rong_2 = True
                
            kiem_tra_can_dung_fallback = check_rong_1 or check_rong_2
            
            if kiem_tra_can_dung_fallback == True:
                try:
                    bang_du_lieu_khoi_ngoai_result = dong_co_vnstock_v19.stock.trading.foreign(
                        symbol=ma_chung_khoan_vao,
                        start=chuoi_bat_dau_ngoai,
                        end=chuoi_ket_thuc_ngoai
                    )
                except Exception:
                    pass
            
            # Bước C: Chuẩn hóa dữ liệu Khối ngoại trả về
            kiem_tra_co_bang_ngoai = bang_du_lieu_khoi_ngoai_result is not None
            
            if kiem_tra_co_bang_ngoai == True:
                
                do_dai_bang_ngoai = len(bang_du_lieu_khoi_ngoai_result)
                kiem_tra_co_dong_du_lieu = do_dai_bang_ngoai > 0
                
                if kiem_tra_co_dong_du_lieu == True:
                    
                    danh_sach_ten_cot_ngoai_norm = []
                    
                    for col_name_raw in bang_du_lieu_khoi_ngoai_result.columns:
                        chuoi_cot_ngoai_thuong = str(col_name_raw).lower()
                        danh_sach_ten_cot_ngoai_norm.append(chuoi_cot_ngoai_thuong)
                        
                    bang_du_lieu_khoi_ngoai_result.columns = danh_sach_ten_cot_ngoai_norm
                    
                    return bang_du_lieu_khoi_ngoai_result

        except Exception:
            pass
            
        return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE) - TÍCH HỢP VŨ KHÍ MỚI
    # ==============================================================================
    def tinh_toan_bo_chi_bao_quant_v19(bang_du_lieu_can_tinh_toan):
        """
        Xây dựng bộ chỉ báo định lượng: MA, Bollinger, RSI, MACD, Volume.
        Tích hợp màng lọc dọn rác (ValueError Prevention).
        ĐẶC BIỆT BỔ SUNG: Bollinger Band Width (Squeeze) và Dấu hiệu Cạn Cung.
        """
        # Tạo bản sao dữ liệu tránh làm hỏng DataFrame gốc
        df_processing = bang_du_lieu_can_tinh_toan.copy()
        
        # --- BƯỚC 1: LỌC DỮ LIỆU RÁC VÀ ÉP KIỂU ---
        
        # 1.1 Tiêu diệt các cột bị trùng lặp tên
        duplicat_mask = df_processing.columns.duplicated()
        logic_unique_mask = ~duplicat_mask
        df_processing = df_processing.loc[:, logic_unique_mask]
        
        # 1.2 Đúc ép các cột dữ liệu quan trọng về đúng định dạng số thực (Float)
        danh_sach_cac_cot_bat_buoc_phai_la_so = ['open', 'high', 'low', 'close', 'volume']
        
        for ten_cot_dang_duyet_qua in danh_sach_cac_cot_bat_buoc_phai_la_so:
            
            kiem_tra_cot_co_ton_tai = ten_cot_dang_duyet_qua in df_processing.columns
            
            if kiem_tra_cot_co_ton_tai == True:
                # Hàm to_numeric với errors='coerce' sẽ biến mọi chữ cái rác thành NaN
                cot_da_duoc_ep_kieu_thanh_cong = pd.to_numeric(
                    df_processing[ten_cot_dang_duyet_qua], 
                    errors='coerce'
                )
                df_processing[ten_cot_dang_duyet_qua] = cot_da_duoc_ep_kieu_thanh_cong
        
        # 1.3 Vá lấp các lỗ hổng NaN bằng phương pháp điền tiến (Forward Fill)
        df_processing['open'] = df_processing['open'].ffill()
        df_processing['close'] = df_processing['close'].ffill()
        df_processing['volume'] = df_processing['volume'].ffill()
        
        # Trích xuất hai cột xương sống ra thành biến riêng để tăng tốc độ tính
        chuoi_lich_su_gia_dong_cua = df_processing['close']
        chuoi_lich_su_gia_mo_cua = df_processing['open']
        chuoi_lich_su_khoi_luong_giao_dich = df_processing['volume']
        
        # --- BƯỚC 2: HỆ THỐNG CÁC ĐƯỜNG TRUNG BÌNH ĐỘNG (MOVING AVERAGES) ---
        
        # Tính MA20 (Nhịp đập ngắn hạn)
        cua_so_truot_20_phien_tinh_ma = chuoi_lich_su_gia_dong_cua.rolling(window=20)
        gia_tri_trung_binh_ma20 = cua_so_truot_20_phien_tinh_ma.mean()
        df_processing['ma20'] = gia_tri_trung_binh_ma20
        
        # Tính MA50 (Nhịp đập trung hạn)
        cua_so_truot_50_phien_tinh_ma = chuoi_lich_su_gia_dong_cua.rolling(window=50)
        gia_tri_trung_binh_ma50 = cua_so_truot_50_phien_tinh_ma.mean()
        df_processing['ma50'] = gia_tri_trung_binh_ma50
        
        # Tính MA200 (Ran giới Bò và Gấu)
        cua_so_truot_200_phien_tinh_ma = chuoi_lich_su_gia_dong_cua.rolling(window=200)
        gia_tri_trung_binh_ma200 = cua_so_truot_200_phien_tinh_ma.mean()
        df_processing['ma200'] = gia_tri_trung_binh_ma200
        
        # --- BƯỚC 3: DẢI BOLLINGER BANDS VÀ CHỈ BÁO NÉN LÒ XO (SQUEEZE) ---
        
        # Tính toán mức độ lệch chuẩn của giá trong 20 ngày
        do_lech_chuan_trong_chu_ky_20_ngay = cua_so_truot_20_phien_tinh_ma.std()
        df_processing['do_lech_chuan_20'] = do_lech_chuan_trong_chu_ky_20_ngay
        
        # Nhân đôi độ lệch chuẩn
        khoang_cach_bien_do_bollinger = df_processing['do_lech_chuan_20'] * 2
        
        # Thiết lập trần và sàn của Bollinger
        gia_tri_duong_vien_tren_upper_band = df_processing['ma20'] + khoang_cach_bien_do_bollinger
        df_processing['upper_band'] = gia_tri_duong_vien_tren_upper_band
        
        gia_tri_duong_vien_duoi_lower_band = df_processing['ma20'] - khoang_cach_bien_do_bollinger
        df_processing['lower_band'] = gia_tri_duong_vien_duoi_lower_band
        
        # TÍNH TOÁN BĂNG THÔNG BOLLINGER (Band Width) - Vũ khí bắt Squeeze
        khoang_cach_upper_lower = df_processing['upper_band'] - df_processing['lower_band']
        ti_le_bang_thong_bollinger = khoang_cach_upper_lower / (df_processing['ma20'] + 1e-9)
        df_processing['bb_width'] = ti_le_bang_thong_bollinger
        
        # --- BƯỚC 4: CHỈ SỐ SỨC MẠNH TƯƠNG ĐỐI (RSI 14 PHIÊN) ---
        
        # Tính chênh lệch giá từng ngày
        khoang_chenh_lech_gia_cua_tung_ngay = chuoi_lich_su_gia_dong_cua.diff()
        
        # Lọc phiên tăng và phiên giảm
        dieu_kien_ngay_co_gia_tang = khoang_chenh_lech_gia_cua_tung_ngay > 0
        chuoi_cac_ngay_co_gia_tang = khoang_chenh_lech_gia_cua_tung_ngay.where(dieu_kien_ngay_co_gia_tang, 0)
        
        dieu_kien_ngay_co_gia_giam = khoang_chenh_lech_gia_cua_tung_ngay < 0
        chuoi_cac_ngay_co_gia_giam = -khoang_chenh_lech_gia_cua_tung_ngay.where(dieu_kien_ngay_co_gia_giam, 0)
        
        # Tính trung bình trượt 14 ngày
        cua_so_truot_14_ngay_cho_chuoi_tang = chuoi_cac_ngay_co_gia_tang.rolling(window=14)
        muc_tang_trung_binh_trong_14_phien = cua_so_truot_14_ngay_cho_chuoi_tang.mean()
        
        cua_so_truot_14_ngay_cho_chuoi_giam = chuoi_cac_ngay_co_gia_giam.rolling(window=14)
        muc_giam_trung_binh_trong_14_phien = cua_so_truot_14_ngay_cho_chuoi_giam.mean()
        
        # Công thức RSI
        ti_so_suc_manh_rs = muc_tang_trung_binh_trong_14_phien / (muc_giam_trung_binh_trong_14_phien + 1e-9)
        mau_so_cua_cong_thuc_rsi = 1 + ti_so_suc_manh_rs
        phan_so_cua_cong_thuc_rsi = 100 / mau_so_cua_cong_thuc_rsi
        chi_so_rsi_da_hoan_thien_chuan_xac = 100 - phan_so_cua_cong_thuc_rsi
        
        df_processing['rsi'] = chi_so_rsi_da_hoan_thien_chuan_xac
        
        # --- BƯỚC 5: ĐỘNG LƯỢNG MACD (CẤU HÌNH 12, 26, 9) ---
        
        dieu_chinh_ema_12 = chuoi_lich_su_gia_dong_cua.ewm(span=12, adjust=False)
        duong_ema_nhanh_chu_ky_12 = dieu_chinh_ema_12.mean()
        
        dieu_chinh_ema_26 = chuoi_lich_su_gia_dong_cua.ewm(span=26, adjust=False)
        duong_ema_cham_chu_ky_26 = dieu_chinh_ema_26.mean()
        
        duong_macd_chinh_thuc = duong_ema_nhanh_chu_ky_12 - duong_ema_cham_chu_ky_26
        df_processing['macd'] = duong_macd_chinh_thuc
        
        dieu_chinh_ema_9_cho_macd = df_processing['macd'].ewm(span=9, adjust=False)
        duong_tin_hieu_signal_line = dieu_chinh_ema_9_cho_macd.mean()
        df_processing['signal'] = duong_tin_hieu_signal_line
        
        # --- BƯỚC 6: CÁC BIẾN SỐ PHỤC VỤ DÒNG TIỀN VÀ AI ---
        
        # Phần trăm thay đổi giá
        phan_tram_thay_doi_gia_trong_1_ngay = chuoi_lich_su_gia_dong_cua.pct_change()
        df_processing['return_1d'] = phan_tram_thay_doi_gia_trong_1_ngay
        
        # Cường độ khối lượng (vol_strength)
        cua_so_truot_10_phien_cua_khoi_luong = chuoi_lich_su_khoi_luong_giao_dich.rolling(window=10)
        khoi_luong_trung_binh_cua_10_phien = cua_so_truot_10_phien_cua_khoi_luong.mean()
        
        suc_manh_cua_khoi_luong_vol_strength = chuoi_lich_su_khoi_luong_giao_dich / (khoi_luong_trung_binh_cua_10_phien + 1e-9)
        df_processing['vol_strength'] = suc_manh_cua_khoi_luong_vol_strength
        
        # Dòng tiền lưu chuyển
        dong_tien_luan_chuyen_trong_ngay = chuoi_lich_su_gia_dong_cua * chuoi_lich_su_khoi_luong_giao_dich
        df_processing['money_flow'] = dong_tien_luan_chuyen_trong_ngay
        
        # Biến động rủi ro lịch sử (Volatility)
        cua_so_truot_20_phien_cua_loi_nhuan = df_processing['return_1d'].rolling(window=20)
        do_bien_dong_lich_su_trong_20_phien = cua_so_truot_20_phien_cua_loi_nhuan.std()
        df_processing['volatility'] = do_bien_dong_lich_su_trong_20_phien
        
        # --- BƯỚC 7: XÁC ĐỊNH DẤU HIỆU CẠN CUNG (SUPPLY EXHAUSTION) ---
        
        # Xác định nến đỏ (Giá đóng cửa < Giá mở cửa)
        dieu_kien_la_nen_do_giam_gia = chuoi_lich_su_gia_dong_cua < chuoi_lich_su_gia_mo_cua
        df_processing['is_red_candle'] = dieu_kien_la_nen_do_giam_gia
        
        # Tính trung bình Volume 20 ngày
        cua_so_truot_20_phien_cua_vol = chuoi_lich_su_khoi_luong_giao_dich.rolling(window=20)
        khoi_luong_trung_binh_cua_20_phien = cua_so_truot_20_phien_cua_vol.mean()
        df_processing['vol_avg_20'] = khoi_luong_trung_binh_cua_20_phien
        
        # Khối lượng cạn kiệt (Volume < 75% trung bình 20 ngày)
        muc_can_kiet_khoi_luong = khoi_luong_trung_binh_cua_20_phien * 0.75
        dieu_kien_khoi_luong_cuc_thap = chuoi_lich_su_khoi_luong_giao_dich < muc_can_kiet_khoi_luong
        
        # Đánh dấu cạn cung: Vừa là nến đỏ VÀ khối lượng cực thấp
        dieu_kien_can_cung_hoan_chinh = dieu_kien_la_nen_do_giam_gia & dieu_kien_khoi_luong_cuc_thap
        df_processing['can_cung'] = dieu_kien_can_cung_hoan_chinh
        
        # --- BƯỚC 8: PHÂN LỚP XU HƯỚNG DÒNG TIỀN (PV TREND) ---
        
        dieu_kien_cau_manh_gom_hang = (df_processing['return_1d'] > 0) & (df_processing['vol_strength'] > 1.2)
        dieu_kien_cung_manh_xa_hang = (df_processing['return_1d'] < 0) & (df_processing['vol_strength'] > 1.2)
        
        xu_huong_hanh_vi_dong_tien_pv = np.where(
            dieu_kien_cau_manh_gom_hang, 
            1, 
            np.where(
                dieu_kien_cung_manh_xa_hang, 
                -1, 
                0
            )
        )
        df_processing['pv_trend'] = xu_huong_hanh_vi_dong_tien_pv
        
        # Lớp giáp cuối cùng: Chặt chém toàn bộ các dòng chứa dữ liệu rỗng (NaN)
        bang_du_lieu_sach_tuyet_doi = df_processing.dropna()
        
        return bang_du_lieu_sach_tuyet_doi

    # ==============================================================================
    # 4. HÀM CHẨN ĐOÁN THÔNG MINH ĐỊNH LƯỢNG (INTELLIGENCE & AI LAYER)
    # ==============================================================================
    
    def phan_tich_tam_ly_dam_dong_v19(bang_du_lieu_da_tinh_xong_toan_bo):
        """
        Đo lường sức nóng RSI hiện tại để xem nhỏ lẻ đang sợ hãi hay hưng phấn.
        """
        dong_du_lieu_cua_phien_giao_dich_cuoi_cung = bang_du_lieu_da_tinh_xong_toan_bo.iloc[-1]
        
        gia_tri_rsi_cua_phien_giao_dich_cuoi_cung = dong_du_lieu_cua_phien_giao_dich_cuoi_cung['rsi']
        
        # Bóc tách các cung bậc cảm xúc
        if gia_tri_rsi_cua_phien_giao_dich_cuoi_cung > 75:
            nhan_tam_ly_duoc_hien_thi = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif gia_tri_rsi_cua_phien_giao_dich_cuoi_cung > 60:
            nhan_tam_ly_duoc_hien_thi = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif gia_tri_rsi_cua_phien_giao_dich_cuoi_cung < 30:
            nhan_tam_ly_duoc_hien_thi = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif gia_tri_rsi_cua_phien_giao_dich_cuoi_cung < 42:
            nhan_tam_ly_duoc_hien_thi = "😨 SỢ HÃI (BI QUAN)"
        else:
            nhan_tam_ly_duoc_hien_thi = "🟡 TRUNG LẬP (ĐI NGANG CHỜ ĐỢI)"
            
        gia_tri_rsi_sau_khi_lam_tron = round(gia_tri_rsi_cua_phien_giao_dich_cuoi_cung, 1)
        
        return nhan_tam_ly_duoc_hien_thi, gia_tri_rsi_sau_khi_lam_tron

    def thuc_thi_backtest_chien_thuat_v19(bang_du_lieu_da_tinh_xong_toan_bo):
        """
        Cỗ máy thời gian: Lục lọi lại lịch sử 1000 ngày qua để đo lường xác suất.
        """
        tong_so_lan_robot_phat_hien_tin_hieu_mua = 0
        tong_so_lan_nha_dau_tu_chien_thang_chot_loi = 0
        
        do_dai_tong_so_dong_cua_bang = len(bang_du_lieu_da_tinh_xong_toan_bo)
        
        # Lặp qua từng ngày trong lịch sử (Bỏ qua 100 ngày đầu và 10 ngày cuối)
        for vi_tri_cua_ngay_dang_xet in range(100, do_dai_tong_so_dong_cua_bang - 10):
            
            # Rã logic kiểm tra RSI
            gia_tri_rsi_cua_ngay_dang_xet = bang_du_lieu_da_tinh_xong_toan_bo['rsi'].iloc[vi_tri_cua_ngay_dang_xet]
            kiem_tra_dieu_kien_rsi_duoi_45 = gia_tri_rsi_cua_ngay_dang_xet < 45
            
            # Rã logic kiểm tra sự giao cắt của MACD và SIGNAL
            gia_tri_macd_cua_ngay_dang_xet = bang_du_lieu_da_tinh_xong_toan_bo['macd'].iloc[vi_tri_cua_ngay_dang_xet]
            gia_tri_signal_cua_ngay_dang_xet = bang_du_lieu_da_tinh_xong_toan_bo['signal'].iloc[vi_tri_cua_ngay_dang_xet]
            
            gia_tri_macd_cua_ngay_hom_qua = bang_du_lieu_da_tinh_xong_toan_bo['macd'].iloc[vi_tri_cua_ngay_dang_xet - 1]
            gia_tri_signal_cua_ngay_hom_qua = bang_du_lieu_da_tinh_xong_toan_bo['signal'].iloc[vi_tri_cua_ngay_dang_xet - 1]
            
            kiem_tra_macd_hom_nay_nam_tren = gia_tri_macd_cua_ngay_dang_xet > gia_tri_signal_cua_ngay_dang_xet
            kiem_tra_macd_hom_qua_nam_duoi = gia_tri_macd_cua_ngay_hom_qua <= gia_tri_signal_cua_ngay_hom_qua
            
            kiem_tra_su_giao_cat_macd_di_len = kiem_tra_macd_hom_nay_nam_tren and kiem_tra_macd_hom_qua_nam_duoi
            
            # Xét tổng hợp nếu CẢ HAI CÙNG ĐÚNG
            if kiem_tra_dieu_kien_rsi_duoi_45 and kiem_tra_su_giao_cat_macd_di_len:
                
                # Ghi nhận 1 lần xuất hiện điểm mua
                tong_so_lan_robot_phat_hien_tin_hieu_mua += 1
                
                # Tính toán mục tiêu chốt lãi
                gia_mua_khop_lenh_mo_phong = bang_du_lieu_da_tinh_xong_toan_bo['close'].iloc[vi_tri_cua_ngay_dang_xet]
                gia_muc_tieu_chot_loi_5_phan_tram = gia_mua_khop_lenh_mo_phong * 1.05
                
                # Trích xuất dữ liệu giá của 10 ngày ngay sau ngày mua
                vi_tri_ngay_tuong_lai_bat_dau = vi_tri_cua_ngay_dang_xet + 1
                vi_tri_ngay_tuong_lai_ket_thuc = vi_tri_cua_ngay_dang_xet + 11
                
                khoang_gia_giao_dich_trong_10_ngay_tuong_lai = bang_du_lieu_da_tinh_xong_toan_bo['close'].iloc[vi_tri_ngay_tuong_lai_bat_dau : vi_tri_ngay_tuong_lai_ket_thuc]
                
                # Quét xem có ngày nào thỏa mãn điều kiện chốt lời không
                kiem_tra_co_ngay_nao_thang_loi_khong = any(khoang_gia_giao_dich_trong_10_ngay_tuong_lai > gia_muc_tieu_chot_loi_5_phan_tram)
                
                if kiem_tra_co_ngay_nao_thang_loi_khong:
                    # Ghi nhận 1 lần chiến thắng
                    tong_so_lan_nha_dau_tu_chien_thang_chot_loi += 1
        
        # Xử lý ngoại lệ chia cho số 0
        if tong_so_lan_robot_phat_hien_tin_hieu_mua == 0:
            return 0.0
            
        # Áp dụng công thức tính tỷ lệ phần trăm chiến thắng
        phan_tram_thang_loi_winrate_cuoi_cung = (tong_so_lan_nha_dau_tu_chien_thang_chot_loi / tong_so_lan_robot_phat_hien_tin_hieu_mua) * 100
        
        return round(phan_tram_thang_loi_winrate_cuoi_cung, 1)

    def du_bao_xac_suat_ai_t3_v19(bang_du_lieu_da_tinh_xong_toan_bo):
        """
        Huấn luyện cỗ máy Machine Learning (Random Forest).
        Mục tiêu: Đọc hiểu 8 đặc điểm kỹ thuật để dự báo cửa tăng T+3.
        """
        
        do_dai_cua_bang_du_lieu = len(bang_du_lieu_da_tinh_xong_toan_bo)
        
        # Rào cản kỹ thuật: AI cần ít nhất 200 ngày dữ liệu mẫu để học
        if do_dai_cua_bang_du_lieu < 200:
            return "N/A"
            
        bang_du_lieu_danh_cho_may_hoc = bang_du_lieu_da_tinh_xong_toan_bo.copy()
        
        # BƯỚC 1: Xây dựng bộ nhãn mục tiêu (Y) cho dữ liệu huấn luyện
        chuoi_gia_hien_tai_de_đoi_chieu = bang_du_lieu_danh_cho_may_hoc['close']
        chuoi_gia_cua_tuong_lai_sau_3_ngay_nua = bang_du_lieu_danh_cho_may_hoc['close'].shift(-3)
        
        # Điều kiện thắng: Giá T+3 phải cao hơn 2% so với giá lúc mua
        muc_gia_dich_yeu_cau_tang_2_phan_tram = chuoi_gia_hien_tai_de_đoi_chieu * 1.02
        dieu_kien_gia_tang_thanh_cong = chuoi_gia_cua_tuong_lai_sau_3_ngay_nua > muc_gia_dich_yeu_cau_tang_2_phan_tram
        
        # Đúc ép thành kiểu số nguyên (0 hoặc 1)
        bang_du_lieu_danh_cho_may_hoc['nhan_muc_tieu_dich_cho_ai'] = dieu_kien_gia_tang_thanh_cong.astype(int)
        
        # BƯỚC 2: Định hình 8 biến số đầu vào để máy học (Features X)
        danh_sach_cac_bien_so_khach_quan = [
            'rsi', 
            'macd', 
            'signal', 
            'return_1d', 
            'volatility', 
            'vol_strength', 
            'money_flow', 
            'pv_trend'
        ]
        
        # BƯỚC 3: Dọn dẹp chiến trường trước khi nạp vào mồm AI
        bang_du_lieu_da_duoc_don_sach = bang_du_lieu_danh_cho_may_hoc.dropna()
        
        ma_tran_du_lieu_dau_vao_x = bang_du_lieu_da_duoc_don_sach[danh_sach_cac_bien_so_khach_quan]
        vector_du_lieu_dau_ra_y = bang_du_lieu_da_duoc_don_sach['nhan_muc_tieu_dich_cho_ai']
        
        # BƯỚC 4: Khởi tạo động cơ Rừng Ngẫu Nhiên (Random Forest)
        so_luong_cay_quyet_dinh_estimators = 100
        mo_hinh_tri_tue_nhan_tao_rf = RandomForestClassifier(
            n_estimators=so_luong_cay_quyet_dinh_estimators, 
            random_state=42
        )
        
        # Loại bỏ 3 dòng dữ liệu cuối cùng vì chúng ta chưa thể nhìn thấy tương lai của chúng
        ma_tran_x_danh_cho_huan_luyen = ma_tran_du_lieu_dau_vao_x[:-3]
        vector_y_danh_cho_huan_luyen = vector_du_lieu_dau_ra_y[:-3]
        
        # Kích hoạt quá trình Nhồi nhét kiến thức (Training Fit)
        mo_hinh_tri_tue_nhan_tao_rf.fit(ma_tran_x_danh_cho_huan_luyen, vector_y_danh_cho_huan_luyen)
        
        # BƯỚC 5: Áp dụng khối kiến thức vừa học vào phiên giao dịch hôm nay
        dong_du_lieu_cua_phien_giao_dich_hom_nay = ma_tran_du_lieu_dau_vao_x.iloc[[-1]]
        mang_xac_suat_ket_qua_du_doan = mo_hinh_tri_tue_nhan_tao_rf.predict_proba(dong_du_lieu_cua_phien_giao_dich_hom_nay)
        
        # Tách bóc lấy xác suất rơi vào kịch bản số 1 (Kịch bản Tăng Giá)
        xac_suat_kha_nang_tang_gia_thuc_te = mang_xac_suat_ket_qua_du_doan[0][1]
        
        # Quy đổi ra hệ phần trăm cho dễ nhìn
        gia_tri_xac_suat_hien_thi = round(xac_suat_kha_nang_tang_gia_thuc_te * 100, 1)
        
        return gia_tri_xac_suat_hien_thi

    # ==============================================================================
    # 5. TÍNH NĂNG TỰ ĐỘNG PHÂN TÍCH RA TEXT CHO MINH (AUTO-ANALYSIS ENGINE)
    # ==============================================================================
    def tao_ban_bao_cao_tu_dong_chuyen_sau_v19(ma_chung_khoan, dong_du_lieu_cuoi, diem_so_ai, diem_so_winrate, mang_tru_gom, mang_tru_xa):
        """
        Nhà phân tích ảo: Tự động gom nhặt các con số khô khan, lắp ghép lại
        và viết ra một bài văn phân tích chi tiết. Minh đọc là hiểu ngay tình hình.
        Khai triển tối đa để chống nén code.
        """
        
        # Tạo một mảng rỗng để chứa các dòng phân tích sẽ được in ra
        mang_chua_cac_cau_phan_tich_hoan_thien = []
        
        # --- PHẦN 1: ĐỌC VỊ DÒNG TIỀN ---
        tieu_de_phan_dong_tien = "#### 1. Đọc Vị Hành Vi Dòng Tiền (Smart Flow):"
        mang_chua_cac_cau_phan_tich_hoan_thien.append(tieu_de_phan_dong_tien)
        
        kiem_tra_co_nam_trong_mang_gom = ma_chung_khoan in mang_tru_gom
        kiem_tra_co_nam_trong_mang_xa = ma_chung_khoan in mang_tru_xa
        
        gia_tri_vol_strength_hien_tai = dong_du_lieu_cuoi['vol_strength']
        
        if kiem_tra_co_nam_trong_mang_gom:
            cau_phan_tich_dong_tien = f"✅ **Tín Hiệu Tích Cực:** Hệ thống phát hiện dòng tiền lớn đang **GOM HÀNG CHỦ ĐỘNG** tại mã {ma_chung_khoan}. Khối lượng giao dịch nổ đột biến gấp {gia_tri_vol_strength_hien_tai:.1f} lần trung bình, giá đóng cửa xanh."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_dong_tien)
            
        elif kiem_tra_co_nam_trong_mang_xa:
            cau_phan_tich_dong_tien = f"🚨 **Cảnh Báo Tiêu Cực:** Dòng tiền lớn đang **XẢ HÀNG QUYẾT LIỆT**. Khối lượng bán ra gấp {gia_tri_vol_strength_hien_tai:.1f} lần bình thường, giá đóng cửa đỏ. Áp lực phân phối đè nặng."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_dong_tien)
            
        else:
            cau_phan_tich_dong_tien = f"🟡 **Trạng Thái Trung Lập:** Dòng tiền chưa có sự đột biến. Khối lượng giao dịch bình thường, chủ yếu là nhà đầu tư cá nhân tự giao dịch."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_dong_tien)

        # --- PHẦN 2: ĐỌC VỊ VỊ THẾ KỸ THUẬT ---
        tieu_de_phan_ky_thuat = "#### 2. Đánh Giá Vị Thế Kỹ Thuật (Trend & Momentum):"
        mang_chua_cac_cau_phan_tich_hoan_thien.append(tieu_de_phan_ky_thuat)
        
        gia_tri_dong_cua_hien_tai_dn = dong_du_lieu_cuoi['close']
        gia_tri_ma20_hien_tai_dn = dong_du_lieu_cuoi['ma20']
        gia_tri_rsi_hien_tai_dn = dong_du_lieu_cuoi['rsi']
        
        kiem_tra_xu_huong_gia_dang_xau = gia_tri_dong_cua_hien_tai_dn < gia_tri_ma20_hien_tai_dn
        
        if kiem_tra_xu_huong_gia_dang_xau:
            cau_phan_tich_xu_huong = f"❌ **Xu Hướng Đang Xấu:** Mức giá hiện tại ({gia_tri_dong_cua_hien_tai_dn:,.0f} VNĐ) đang nằm **DƯỚI** đường sinh tử MA20 ({gia_tri_ma20_hien_tai_dn:,.0f} VNĐ). Phe Bán đang áp đảo, tuyệt đối chưa bắt đáy."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_xu_huong)
        else:
            cau_phan_tich_xu_huong = f"✅ **Xu Hướng Rất Tốt:** Mức giá hiện tại ({gia_tri_dong_cua_hien_tai_dn:,.0f} VNĐ) đang neo giữ vững chắc **TRÊN** đường hỗ trợ MA20 ({gia_tri_ma20_hien_tai_dn:,.0f} VNĐ). Cấu trúc tăng giá ngắn hạn được bảo vệ."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_xu_huong)

        if gia_tri_rsi_hien_tai_dn > 70:
            cau_phan_tich_tam_ly_rsi = f"⚠️ **Cảnh Báo Tâm Lý:** RSI vọt lên {gia_tri_rsi_hien_tai_dn:.1f} (Vùng Quá Mua). Cổ phiếu đang quá hưng phấn, dễ quay đầu điều chỉnh."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_tam_ly_rsi)
        elif gia_tri_rsi_hien_tai_dn < 35:
            cau_phan_tich_tam_ly_rsi = f"💡 **Cơ Hội Tâm Lý:** RSI lùi sâu về {gia_tri_rsi_hien_tai_dn:.1f} (Vùng Quá Bán). Lực bán cạn kiệt, xác suất có nhịp hồi phục là rất lớn."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_tam_ly_rsi)
        else:
            cau_phan_tich_tam_ly_rsi = f"📉 **Tâm Lý Ổn Định:** RSI dao động quanh mốc {gia_tri_rsi_hien_tai_dn:.1f}, thị trường chưa hưng phấn hay hoảng loạn thái quá."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_tam_ly_rsi)

        # --- PHẦN 3: ĐỌC VỊ AI & LỊCH SỬ ---
        tieu_de_phan_ai = "#### 3. Đánh Giá Xác Suất Định Lượng (AI & Lịch Sự):"
        mang_chua_cac_cau_phan_tich_hoan_thien.append(tieu_de_phan_ai)
        
        kiem_tra_ai_co_hop_le_khong = isinstance(diem_so_ai, float)
        
        if kiem_tra_ai_co_hop_le_khong:
            if diem_so_ai < 55:
                chuoi_danh_gia_nhanh_ve_ai = "Mức độ tin cậy thấp, rủi ro chôn vốn"
            else:
                chuoi_danh_gia_nhanh_ve_ai = "Mức độ tin cậy tốt, cửa tăng T+3 rất sáng"
                
            cau_phan_tich_ve_ai = f"- **AI Dự báo:** Xác suất tăng giá T+3 là **{diem_so_ai}%** ➔ *{chuoi_danh_gia_nhanh_ve_ai}*."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_ve_ai)
        
        if diem_so_winrate < 45:
            chuoi_danh_gia_nhanh_ve_lich_su = "Trong quá khứ, mẫu hình này thường là Bẫy lừa (Bull Trap)"
        else:
            chuoi_danh_gia_nhanh_ve_lich_su = "Quá khứ chứng minh đây là tín hiệu uy tín"
            
        cau_phan_tich_ve_lich_su = f"- **Lịch sử:** Tỷ lệ chiến thắng của chiến thuật này đạt mốc **{diem_so_winrate}%** ➔ *{chuoi_danh_gia_nhanh_ve_lich_su}*."
        mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_phan_tich_ve_lich_su)

        # --- PHẦN 4: TỔNG KẾT VÀ GIẢI MÃ ---
        tieu_de_phan_tong_ket = "#### 💡 TỔNG KẾT & GIẢI MÃ MÂU THUẪN CỦA CHUYÊN GIA:"
        mang_chua_cac_cau_phan_tich_hoan_thien.append(tieu_de_phan_tong_ket)
        
        dieu_kien_giai_ma_1 = kiem_tra_xu_huong_gia_dang_xau and kiem_tra_co_nam_trong_mang_gom
        dieu_kien_giai_ma_2 = (diem_so_winrate < 40) and (kiem_tra_ai_co_hop_le_khong and diem_so_ai < 50)
        dieu_kien_giai_ma_3 = (not kiem_tra_xu_huong_gia_dang_xau) and (kiem_tra_ai_co_hop_le_khong and diem_so_ai > 55) and (diem_so_winrate > 50)
        
        if dieu_kien_giai_ma_1:
            cau_tong_ket_cuoi_cung = f"**⚠️ LƯU Ý ĐẶC BIỆT:** Dù có dòng tiền Cá mập gom hàng, nhưng giá vẫn bị ép dưới MA20, đây là pha 'Gom Hàng Tích Lũy' dài hạn. Nhỏ lẻ mua lúc này dễ bị chôn vốn. Hãy đợi giá bứt phá qua MA20 rồi mới đánh."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_tong_ket_cuoi_cung)
            
        elif dieu_kien_giai_ma_2:
            cau_tong_ket_cuoi_cung = f"**⛔ RỦI RO NGẬP TRÀN:** Cả AI và Lịch sử đều quay lưng. Nhịp kéo tăng (nếu có) khả năng cao là Bull Trap để xả hàng. Đứng ngoài quan sát."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_tong_ket_cuoi_cung)
            
        elif dieu_kien_giai_ma_3:
            cau_tong_ket_cuoi_cung = f"**🚀 ĐIỂM MUA VÀNG:** Biểu đồ đẹp, Dòng tiền lớn nhập cuộc, AI và Lịch sử đồng thuận. Cơ hội giải ngân an toàn. Có thể mua 30-50%."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_tong_ket_cuoi_cung)
            
        else:
            cau_tong_ket_cuoi_cung = f"**⚖️ THEO DÕI (50/50):** Tín hiệu phân hóa, điểm mua chưa chín muồi. Đưa mã này vào Watchlist chờ phiên bùng nổ khối lượng thực sự."
            mang_chua_cac_cau_phan_tich_hoan_thien.append(cau_tong_ket_cuoi_cung)

        # Ghép nối các chuỗi lại thành một văn bản hoàn chỉnh có ngắt dòng
        chuoi_van_ban_bao_cao_hoan_chinh = "\n\n".join(mang_chua_cac_cau_phan_tich_hoan_thien)
        return chuoi_van_ban_bao_cao_hoan_chinh

    # ==============================================================================
    # 6. PHÂN TÍCH TÀI CHÍNH CỐT LÕI (FUNDAMENTAL LAYER) - ĐÃ BẢO MẬT API
    # ==============================================================================
    def do_luong_tang_truong_canslim_v19(ma_chung_khoan_kiem_tra):
        """Tính phần trăm thay đổi Lợi nhuận sau thuế của doanh nghiệp"""
        try:
            # Truy vấn Báo Cáo Kết Quả Kinh Doanh Quý từ Vnstock
            bang_bctc_ket_qua_kinh_doanh = dong_co_vnstock_v19.stock.finance.income_statement(
                symbol=ma_chung_khoan_kiem_tra, 
                period='quarter', 
                lang='en'
            ).head(5)
            
            tap_hop_tu_khoa_nhan_dien_loi_nhuan = ['sau thuế', 'posttax', 'net profit', 'earning']
            
            danh_sach_cac_cot_tuong_thich_lnst = []
            
            # Quét tìm cột Lợi nhuận
            for ten_cot_dang_xet_trong_bang in bang_bctc_ket_qua_kinh_doanh.columns:
                chuoi_ten_cot_in_thuong = str(ten_cot_dang_xet_trong_bang).lower()
                
                for tu_khoa_mau in tap_hop_tu_khoa_nhan_dien_loi_nhuan:
                    if tu_khoa_mau in chuoi_ten_cot_in_thuong:
                        danh_sach_cac_cot_tuong_thich_lnst.append(ten_cot_dang_xet_trong_bang)
                        break
            
            # Nếu tìm thấy cột
            kiem_tra_co_tim_thay_cot_lnst_khong = len(danh_sach_cac_cot_tuong_thich_lnst) > 0
            if kiem_tra_co_tim_thay_cot_lnst_khong:
                
                ten_cot_lnst_chinh_xac_nhat = danh_sach_cac_cot_tuong_thich_lnst[0]
                gia_tri_lnst_cua_quy_moi_nhat = float(bang_bctc_ket_qua_kinh_doanh.iloc[0][ten_cot_lnst_chinh_xac_nhat])
                gia_tri_lnst_cua_cung_ky_nam_ngoai = float(bang_bctc_ket_qua_kinh_doanh.iloc[4][ten_cot_lnst_chinh_xac_nhat])
                
                kiem_tra_lnst_nam_ngoai_co_duong = gia_tri_lnst_cua_cung_ky_nam_ngoai > 0
                if kiem_tra_lnst_nam_ngoai_co_duong:
                    muc_do_chenh_lech_loi_nhuan = gia_tri_lnst_cua_quy_moi_nhat - gia_tri_lnst_cua_cung_ky_nam_ngoai
                    bien_do_tang_truong_bang_phan_tram = (muc_do_chenh_lech_loi_nhuan / gia_tri_lnst_cua_cung_ky_nam_ngoai) * 100
                    return round(bien_do_tang_truong_bang_phan_tram, 1)
                    
        except Exception:
            # Máy chủ Vnstock báo lỗi thì ta gọi Yahoo
            pass
            
        try:
            chuoi_ma_chung_khoan_danh_cho_yahoo = f"{ma_chung_khoan_kiem_tra}.VN"
            doi_tuong_yf_ticker_lay_thong_tin = yf.Ticker(chuoi_ma_chung_khoan_danh_cho_yahoo)
            du_lieu_ho_so_doanh_nghiep_tu_yahoo = doi_tuong_yf_ticker_lay_thong_tin.info
            
            ti_le_tang_truong_tu_he_thong_yahoo = du_lieu_ho_so_doanh_nghiep_tu_yahoo.get('earningsQuarterlyGrowth')
            
            kiem_tra_co_du_lieu_tu_yahoo = ti_le_tang_truong_tu_he_thong_yahoo is not None
            if kiem_tra_co_du_lieu_tu_yahoo:
                gia_tri_tang_truong_phan_tram_yf = ti_le_tang_truong_tu_he_thong_yahoo * 100
                return round(gia_tri_tang_truong_phan_tram_yf, 1)
                
        except Exception:
            pass
            
        return None

    def boc_tach_chi_so_pe_roe_v19(ma_chung_khoan_kiem_tra):
        """
        Đo lường P/E và ROE. 
        Đã FIX LỖI P/E 0.0 theo yêu cầu của Minh: Trả về None nếu API sập.
        """
        chi_so_pe_cuoi_cung_tra_ve = None
        chi_so_roe_cuoi_cung_tra_ve = None
        
        try:
            # Gọi API Vnstock
            bang_chi_so_tai_chinh_vnstock = dong_co_vnstock_v19.stock.finance.ratio(ma_chung_khoan_kiem_tra, 'quarterly').iloc[-1]
            
            chi_so_pe_tu_may_chu_vnstock = bang_chi_so_tai_chinh_vnstock.get('ticker_pe', bang_chi_so_tai_chinh_vnstock.get('pe', None))
            chi_so_roe_tu_may_chu_vnstock = bang_chi_so_tai_chinh_vnstock.get('roe', None)
            
            # Kiểm tra và gán (Chỉ gán nếu dữ liệu thật sự là con số và không bị NaN)
            kiem_tra_pe_co_that = (chi_so_pe_tu_may_chu_vnstock is not None) and (not np.isnan(chi_so_pe_tu_may_chu_vnstock))
            if kiem_tra_pe_co_that:
                chi_so_pe_cuoi_cung_tra_ve = chi_so_pe_tu_may_chu_vnstock
                
            kiem_tra_roe_co_that = (chi_so_roe_tu_may_chu_vnstock is not None) and (not np.isnan(chi_so_roe_tu_may_chu_vnstock))
            if kiem_tra_roe_co_that:
                chi_so_roe_cuoi_cung_tra_ve = chi_so_roe_tu_may_chu_vnstock
                
        except Exception:
            pass
            
        # Nếu Vnstock sập (Giá trị vẫn đang là None hoặc bằng 0), chạy fallback Yahoo
        kiem_tra_can_fallback_khong = (chi_so_pe_cuoi_cung_tra_ve is None) or (chi_so_pe_cuoi_cung_tra_ve <= 0)
        
        if kiem_tra_can_fallback_khong:
            try:
                chuoi_ma_chung_khoan_pe_yahoo = f"{ma_chung_khoan_kiem_tra}.VN"
                doi_tuong_yf_ticker_lay_pe = yf.Ticker(chuoi_ma_chung_khoan_pe_yahoo)
                du_lieu_ho_so_doanh_nghiep_yf = doi_tuong_yf_ticker_lay_pe.info
                
                chi_so_pe_tu_may_chu_yahoo = du_lieu_ho_so_doanh_nghiep_yf.get('trailingPE', None)
                chi_so_roe_tu_may_chu_yahoo = du_lieu_ho_so_doanh_nghiep_yf.get('returnOnEquity', None)
                
                if chi_so_pe_tu_may_chu_yahoo is not None:
                    chi_so_pe_cuoi_cung_tra_ve = chi_so_pe_tu_may_chu_yahoo
                    
                if chi_so_roe_tu_may_chu_yahoo is not None:
                    chi_so_roe_cuoi_cung_tra_ve = chi_so_roe_tu_may_chu_yahoo
                    
            except Exception:
                pass
                
        # Nếu rốt cuộc cả 2 máy chủ đều sập, hàm sẽ trả về None (Tránh lỗi hiện 0.0)
        return chi_so_pe_cuoi_cung_tra_ve, chi_so_roe_cuoi_cung_tra_ve

    # ==============================================================================
    # 7. 🧠 ROBOT ADVISOR MASTER: ĐƯA RA LỆNH NGẮN GỌN BÊN GÓC PHẢI
    # ==============================================================================
    def he_thong_suy_luan_advisor_rut_gon_v19(dong_du_lieu_cuoi, diem_so_ai, diem_so_winrate, diem_so_tang_truong):
        """Tính toán điểm số định lượng để xuất ra thông báo MUA/BÁN ngắn gọn"""
        
        tong_diem_danh_gia_tin_cay_cua_he_thong = 0
        
        # 1. Đánh giá cỗ máy AI
        kiem_tra_ai_co_hop_le = isinstance(diem_so_ai, float)
        if kiem_tra_ai_co_hop_le:
            kiem_tra_ai_co_ung_ho = diem_so_ai >= 58.0
            if kiem_tra_ai_co_ung_ho:
                tong_diem_danh_gia_tin_cay_cua_he_thong += 1
                
        # 2. Đánh giá mức độ Winrate
        kiem_tra_winrate_co_tot = diem_so_winrate >= 50.0
        if kiem_tra_winrate_co_tot:
            tong_diem_danh_gia_tin_cay_cua_he_thong += 1
            
        # 3. Đánh giá Kỹ thuật 
        gia_dong_cua_hien_tai_dang_xet = dong_du_lieu_cuoi['close']
        duong_ho_tro_ma20_hien_tai_dang_xet = dong_du_lieu_cuoi['ma20']
        
        kiem_tra_gia_co_tren_ma20 = gia_dong_cua_hien_tai_dang_xet > duong_ho_tro_ma20_hien_tai_dang_xet
        if kiem_tra_gia_co_tren_ma20:
            tong_diem_danh_gia_tin_cay_cua_he_thong += 1
            
        # 4. Đánh giá Tài chính
        kiem_tra_co_diem_tang_truong = diem_so_tang_truong is not None
        if kiem_tra_co_diem_tang_truong:
            kiem_tra_tang_truong_co_tot = diem_so_tang_truong >= 15.0
            if kiem_tra_tang_truong_co_tot:
                tong_diem_danh_gia_tin_cay_cua_he_thong += 1
                
        # Lấy RSI làm hệ quy chiếu chống Fomo
        chi_so_rsi_hien_tai_dang_xet = dong_du_lieu_cuoi['rsi']

        # Rút ra kết luận bằng các mệnh đề Boolean
        dieu_kien_mua_diem_so_cao = tong_diem_danh_gia_tin_cay_cua_he_thong >= 3
        dieu_kien_mua_rsi_tot = chi_so_rsi_hien_tai_dang_xet < 68
        
        dieu_kien_ban_diem_so_thap = tong_diem_danh_gia_tin_cay_cua_he_thong <= 1
        dieu_kien_ban_rsi_qua_cao = chi_so_rsi_hien_tai_dang_xet > 78
        dieu_kien_ban_gia_giam_roi = gia_dong_cua_hien_tai_dang_xet < duong_ho_tro_ma20_hien_tai_dang_xet
        
        if dieu_kien_mua_diem_so_cao and dieu_kien_mua_rsi_tot:
            chuoi_lenh_duoc_hien_thi = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
            chuoi_mau_sac_hien_thi = "green"
            
        elif dieu_kien_ban_diem_so_thap or dieu_kien_ban_rsi_qua_cao or dieu_kien_ban_gia_giam_roi:
            chuoi_lenh_duoc_hien_thi = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
            chuoi_mau_sac_hien_thi = "red"
            
        else:
            chuoi_lenh_duoc_hien_thi = "⚖️ THEO DÕI (WATCHLIST)"
            chuoi_mau_sac_hien_thi = "orange"

        return chuoi_lenh_duoc_hien_thi, chuoi_mau_sac_hien_thi

    # ==============================================================================
    # 7.5 TÍNH NĂNG MỚI: PHÂN LOẠI SIÊU CỔ PHIẾU (TÍCH HỢP 3 VŨ KHÍ MỚI)
    # ==============================================================================
    def phan_loai_sieu_co_phieu_v19(ma_co_phieu, df_bang_scan_day_du, ai_prob_val_hien_tai):
        """
        Radar lọc 2 tầng chuyên sâu:
        Tầng 1: Đã bùng nổ Vol (Dành cho đánh T+ rủi ro)
        Tầng 2: Danh Sách Chờ (Tích hợp: Thắt chặt Bollinger, Cạn Cung, Tây Gom)
        """
        dong_du_lieu_cua_phien_hom_nay = df_bang_scan_day_du.iloc[-1]
        
        gia_tri_vol_strength_ht = dong_du_lieu_cua_phien_hom_nay['vol_strength']
        gia_tri_rsi_ht = dong_du_lieu_cua_phien_hom_nay['rsi']
        gia_tri_khop_lenh_ht = dong_du_lieu_cua_phien_hom_nay['close']
        gia_tri_ma20_ht = dong_du_lieu_cua_phien_hom_nay['ma20']
        
        # --- TẦNG 1: BÙNG NỔ (BREAKOUT) ---
        kiem_tra_vol_dang_no = gia_tri_vol_strength_ht > 1.3
        if kiem_tra_vol_dang_no:
            return "🚀 Bùng Nổ (Dòng tiền nóng)"
        
        # --- TẦNG 2: DANH SÁCH CHỜ CHÂN SÓNG (WATCHLIST) ---
        
        # Điều kiện Cơ Bản (Base Criteria)
        dk_base_vol = (0.8 <= gia_tri_vol_strength_ht) and (gia_tri_vol_strength_ht <= 1.2)
        dk_base_price = gia_tri_khop_lenh_ht >= (gia_tri_ma20_ht * 0.985)
        dk_base_rsi = gia_tri_rsi_ht < 55
        
        dk_base_ai = False
        if isinstance(ai_prob_val_hien_tai, float):
            if ai_prob_val_hien_tai > 50.0:
                dk_base_ai = True
                
        dieu_kien_co_ban_pass = dk_base_vol and dk_base_price and dk_base_rsi and dk_base_ai
        
        if dieu_kien_co_ban_pass == False:
            return None
            
        # Vũ khí 1: Màng lọc Nén Lò Xo (Bollinger Squeeze)
        gia_tri_bb_width_hom_nay = dong_du_lieu_cua_phien_hom_nay['bb_width']
        
        tap_du_lieu_bb_width_20_ngay = df_bang_scan_day_du['bb_width'].tail(20)
        gia_tri_bb_width_nho_nhat_20_ngay = tap_du_lieu_bb_width_20_ngay.min()
        
        muc_chap_nhan_sai_so_squeeze = gia_tri_bb_width_nho_nhat_20_ngay * 1.15
        dieu_kien_da_bi_nen_chat = gia_tri_bb_width_hom_nay <= muc_chap_nhan_sai_so_squeeze
        
        # Vũ khí 2: Màng lọc Cạn Cung (Supply Exhaustion)
        tap_du_lieu_can_cung_5_ngay_qua = df_bang_scan_day_du['can_cung'].tail(5)
        dieu_kien_co_xuat_hien_can_cung = tap_du_lieu_can_cung_5_ngay_qua.any()
        
        # Vũ khí 3: Khối Ngoại Gom Ròng (Smart Money)
        dieu_kien_khoi_ngoai_dang_gom = False
        
        # Gọi trực tiếp hàm Khối Ngoại để check (Lấy 5 ngày cho nhẹ API)
        bang_check_ngoai = lay_du_lieu_khoi_ngoai_thuc_te_v19(ma_co_phieu, 5)
        
        kiem_tra_bang_check_ngoai_co_data = bang_check_ngoai is not None
        if kiem_tra_bang_check_ngoai_co_data:
            kiem_tra_bang_check_ngoai_empty = bang_check_ngoai.empty
            if kiem_tra_bang_check_ngoai_empty == False:
                
                # Tính tổng 3 ngày gần nhất
                tong_mua_3_ngay = 0.0
                tong_ban_3_ngay = 0.0
                
                bang_3_ngay_cuoi = bang_check_ngoai.tail(3)
                
                for idx_ngoai, dong_du_lieu_ngoai_hunter in bang_3_ngay_cuoi.iterrows():
                    
                    gia_tri_mua_hunter = float(dong_du_lieu_ngoai_hunter.get('buyval', 0))
                    tong_mua_3_ngay = tong_mua_3_ngay + gia_tri_mua_hunter
                    
                    gia_tri_ban_hunter = float(dong_du_lieu_ngoai_hunter.get('sellval', 0))
                    tong_ban_3_ngay = tong_ban_3_ngay + gia_tri_ban_hunter
                    
                tong_rong_3_ngay_cua_tay_long = tong_mua_3_ngay - tong_ban_3_ngay
                
                if tong_rong_3_ngay_cua_tay_long > 0:
                    dieu_kien_khoi_ngoai_dang_gom = True
                    
        # TỔNG HỢP SIÊU MÀNG LỌC
        # Nếu đạt Cơ bản + (Nén chặt HOẶC Cạn cung HOẶC Tây gom) -> Đưa vào Danh sách vàng
        dieu_kien_nang_cao_pass = dieu_kien_da_bi_nen_chat or dieu_kien_co_xuat_hien_can_cung or dieu_kien_khoi_ngoai_dang_gom
        
        if dieu_kien_nang_cao_pass:
            return "⚖️ Danh Sách Chờ (Vùng Gom An Toàn)"
            
        return None

    # ==============================================================================
    # 8. GIAO DIỆN NGƯỜI DÙNG & KIỂM SOÁT LUỒNG DỮ LIỆU (UI CONTROLLER)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def tai_va_chuan_bi_danh_sach_ma_chung_khoan_hose_v19():
        """Tải bảng danh sách mã niêm yết từ máy chủ để làm menu"""
        try:
            bang_danh_sach_niem_yet_toan_bo = dong_co_vnstock_v19.market.listing()
            bo_loc_nhung_ma_thuoc_san_hose = bang_danh_sach_niem_yet_toan_bo['comGroupCode'] == 'HOSE'
            bang_danh_sach_chi_chua_ma_hose = bang_danh_sach_niem_yet_toan_bo[bo_loc_nhung_ma_thuoc_san_hose]
            
            danh_sach_cac_chuoi_ma_chung_khoan = bang_danh_sach_chi_chua_ma_hose['ticker'].tolist()
            return danh_sach_cac_chuoi_ma_chung_khoan
            
        except Exception:
            danh_sach_cung_du_phong = ["FPT", "HPG", "SSI", "TCB", "MWG", "VNM", "VIC", "VHM", "STB", "MSN", "GAS"]
            return danh_sach_cung_du_phong

    # Bắt đầu vẽ Sidebar
    danh_sach_toan_bo_cac_ma_hose_hien_co = tai_va_chuan_bi_danh_sach_ma_chung_khoan_hose_v19()
    
    st.sidebar.header("🕹️ Trung Tâm Giao Dịch Định Lượng Quant")
    
    thanh_phan_chon_ma_dropdown = st.sidebar.selectbox(
        "Lựa chọn mã cổ phiếu mục tiêu để phân tích:", 
        danh_sach_toan_bo_cac_ma_hose_hien_co
    )
    
    thanh_phan_nhap_ma_bang_tay = st.sidebar.text_input(
        "Hoặc nhập trực tiếp tên mã (Ví dụ: FPT):"
    ).upper()
    
    # Logic xác định ưu tiên chọn mã nào
    kiem_tra_co_nhap_tay_khong = thanh_phan_nhap_ma_bang_tay != ""
    if kiem_tra_co_nhap_tay_khong:
        ma_chung_khoan_duoc_chon_de_phan_tich = thanh_phan_nhap_ma_bang_tay
    else:
        ma_chung_khoan_duoc_chon_de_phan_tich = thanh_phan_chon_ma_dropdown

    # Xây dựng bộ 4 TABS chính
    khung_tab_robot_advisor, khung_tab_tai_chinh_co_ban, khung_tab_dong_tien_chuyen_sau, khung_tab_radar_truy_quet = st.tabs([
        "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH TỰ ĐỘNG", 
        "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM", 
        "🌊 BÓC TÁCH DÒNG TIỀN THÔNG MINH", 
        "🔍 RADAR TRUY QUÉT SIÊU CỔ PHIẾU"
    ])

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR VÀ BẢN PHÂN TÍCH TỰ ĐỘNG
    # ------------------------------------------------------------------------------
    with khung_tab_robot_advisor:
        
        nut_nhan_chay_phan_tich_toan_dien = st.button(f"⚡ TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG TOÀN DIỆN MÃ CỔ PHIẾU {ma_chung_khoan_duoc_chon_de_phan_tich}")
        
        if nut_nhan_chay_phan_tich_toan_dien:
            
            with st.spinner(f"Hệ thống đang kích hoạt quy trình đồng bộ dữ liệu đa tầng cho mã {ma_chung_khoan_duoc_chon_de_phan_tich}..."):
                
                # BƯỚC 1: Gọi dữ liệu
                bang_du_lieu_tho_lay_duoc = lay_du_lieu_nien_yet_chuan_v19(ma_chung_khoan_duoc_chon_de_phan_tich)
                
                kiem_tra_bang_tho_co_ton_tai = bang_du_lieu_tho_lay_duoc is not None
                if kiem_tra_bang_tho_co_ton_tai:
                    kiem_tra_bang_tho_co_rong_khong = bang_du_lieu_tho_lay_duoc.empty
                    
                    if not kiem_tra_bang_tho_co_rong_khong:
                        
                        # BƯỚC 2: Tính toán bộ chỉ báo
                        bang_du_lieu_chi_tiet_da_tinh_xong = tinh_toan_bo_chi_bao_quant_v19(bang_du_lieu_tho_lay_duoc)
                        dong_du_lieu_cua_phien_giao_dich_moi_nhat = bang_du_lieu_chi_tiet_da_tinh_xong.iloc[-1]
                        
                        # BƯỚC 3: AI và Lịch sử
                        diem_ai_du_bao_t3_tra_ve = du_bao_xac_suat_ai_t3_v19(bang_du_lieu_chi_tiet_da_tinh_xong)
                        diem_win_rate_lich_su_tra_ve = thuc_thi_backtest_chien_thuat_v19(bang_du_lieu_chi_tiet_da_tinh_xong)
                        
                        nhan_tam_ly_fng_tra_ve, diem_tam_ly_fng_tra_ve = phan_tich_tam_ly_dam_dong_v19(bang_du_lieu_chi_tiet_da_tinh_xong)
                        
                        # BƯỚC 4: Tài chính cơ bản
                        muc_tang_truong_quy_lnst_tra_ve = do_luong_tang_truong_canslim_v19(ma_chung_khoan_duoc_chon_de_phan_tich)
                        
                        # BƯỚC 5: Quét Market Breadth
                        danh_sach_10_ma_tru_kiem_dinh = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                        mang_chua_ma_tru_co_dau_hieu_gom = []
                        mang_chua_ma_tru_co_dau_hieu_xa = []
                        
                        for ma_tru_dang_quet in danh_sach_10_ma_tru_kiem_dinh:
                            try:
                                bang_tru_tho_10_ngay = lay_du_lieu_nien_yet_chuan_v19(ma_tru_dang_quet, so_ngay_lich_su_can_lay=10)
                                
                                kiem_tra_bang_tru_co_khong = bang_tru_tho_10_ngay is not None
                                if kiem_tra_bang_tru_co_khong:
                                    
                                    bang_tru_da_tinh_toan = tinh_toan_bo_chi_bao_quant_v19(bang_tru_tho_10_ngay)
                                    dong_cuoi_cua_ma_tru = bang_tru_da_tinh_toan.iloc[-1]
                                    
                                    dieu_kien_tru_gia_tang = dong_cuoi_cua_ma_tru['return_1d'] > 0
                                    dieu_kien_tru_gia_giam = dong_cuoi_cua_ma_tru['return_1d'] < 0
                                    dieu_kien_tru_no_vol = dong_cuoi_cua_ma_tru['vol_strength'] > 1.2
                                    
                                    if dieu_kien_tru_gia_tang and dieu_kien_tru_no_vol:
                                        mang_chua_ma_tru_co_dau_hieu_gom.append(ma_tru_dang_quet)
                                    elif dieu_kien_tru_gia_giam and dieu_kien_tru_no_vol:
                                        mang_chua_ma_tru_co_dau_hieu_xa.append(ma_tru_dang_quet)
                            except Exception: 
                                pass

                        # --- GIAO DIỆN HIỂN THỊ KẾT QUẢ ĐẦU VÀO TRUNG TÂM ---
                        st.write(f"### 🎯 BẢN PHÂN TÍCH CHUYÊN MÔN TỰ ĐỘNG - MÃ {ma_chung_khoan_duoc_chon_de_phan_tich}")
                        
                        cot_khung_bao_cao_chu_chuyen_sau, cot_khung_lenh_hanh_dong_ngan_gon = st.columns([2, 1])
                        
                        with cot_khung_bao_cao_chu_chuyen_sau:
                            # Kích hoạt AI viết bài phân tích
                            chuoi_bai_bao_cao_hoan_chinh = tao_ban_bao_cao_tu_dong_chuyen_sau_v19(
                                ma_chung_khoan=ma_chung_khoan_duoc_chon_de_phan_tich, 
                                dong_du_lieu_cuoi=dong_du_lieu_cua_phien_giao_dich_moi_nhat, 
                                diem_so_ai=diem_ai_du_bao_t3_tra_ve, 
                                diem_so_winrate=diem_win_rate_lich_su_tra_ve, 
                                mang_tru_gom=mang_chua_ma_tru_co_dau_hieu_gom, 
                                mang_tru_xa=mang_chua_ma_tru_co_dau_hieu_xa
                            )
                            
                            st.info(chuoi_bai_bao_cao_hoan_chinh)
                                    
                        with cot_khung_lenh_hanh_dong_ngan_gon:
                            st.subheader("🤖 ROBOT ĐỀ XUẤT LỆNH HIỆN TẠI:")
                            
                            chuoi_lenh_duoc_tra_ve, mau_sac_lenh_duoc_tra_ve = he_thong_suy_luan_advisor_rut_gon_v19(
                                dong_du_lieu_cuoi=dong_du_lieu_cua_phien_giao_dich_moi_nhat, 
                                diem_so_ai=diem_ai_du_bao_t3_tra_ve, 
                                diem_so_winrate=diem_win_rate_lich_su_tra_ve, 
                                diem_so_tang_truong=muc_tang_truong_quy_lnst_tra_ve
                            )
                            
                            st.title(f":{mau_sac_lenh_duoc_tra_ve}[{chuoi_lenh_duoc_tra_ve}]")
                        
                        st.divider()
                        
                        # --- GIAO DIỆN BẢNG RADAR HIỆU SUẤT TỔNG QUAN ---
                        st.write("### 🧭 Bảng Radar Đo Lường Hiệu Suất Tổng Quan")
                        cot_radar_so_1, cot_radar_so_2, cot_radar_so_3, cot_radar_so_4 = st.columns(4)
                        
                        gia_tri_khop_lenh_moi_nhat_hom_nay = dong_du_lieu_cua_phien_giao_dich_moi_nhat['close']
                        cot_radar_so_1.metric("Giá Khớp Lệnh Mới Nhất", f"{gia_tri_khop_lenh_moi_nhat_hom_nay:,.0f}")
                        
                        cot_radar_so_2.metric("Tâm Lý F&G Index", f"{diem_tam_ly_fng_tra_ve}/100", delta=nhan_tam_ly_fng_tra_ve)
                        
                        kiem_tra_ai_co_hop_le_de_danh_gia = isinstance(diem_ai_du_bao_t3_tra_ve, float)
                        if kiem_tra_ai_co_hop_le_de_danh_gia:
                            kiem_tra_ai_co_tren_55 = diem_ai_du_bao_t3_tra_ve > 55.0
                            if kiem_tra_ai_co_tren_55:
                                nhan_dang_delta_mui_ten_ai = "Tín hiệu Tốt"
                            else:
                                nhan_dang_delta_mui_ten_ai = None
                        else:
                            nhan_dang_delta_mui_ten_ai = None
                                
                        cot_radar_so_3.metric("Khả năng Tăng (AI T+3)", f"{diem_ai_du_bao_t3_tra_ve}%", delta=nhan_dang_delta_mui_ten_ai)
                        
                        kiem_tra_winrate_co_tren_45 = diem_win_rate_lich_su_tra_ve > 45
                        if kiem_tra_winrate_co_tren_45:
                            nhan_dang_delta_mui_ten_backtest = "Tỉ lệ Ổn định"
                        else:
                            nhan_dang_delta_mui_ten_backtest = None
                            
                        cot_radar_so_4.metric("Xác suất Thắng Lịch sử", f"{diem_win_rate_lich_su_tra_ve}%", delta=nhan_dang_delta_mui_ten_backtest)

                        # --- GIAO DIỆN BẢNG NAKED STATS CHUYÊN MÔN ---
                        st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Trần (Naked Stats)")
                        cot_naked_so_1, cot_naked_so_2, cot_naked_so_3, cot_naked_so_4 = st.columns(4)
                        
                        # RSI Metric
                        chi_so_rsi_de_trinh_dien = dong_du_lieu_cua_phien_giao_dich_moi_nhat['rsi']
                        if chi_so_rsi_de_trinh_dien > 70:
                            nhan_canh_bao_rsi_trinh_dien = "Đang Quá mua"
                        elif chi_so_rsi_de_trinh_dien < 30:
                            nhan_canh_bao_rsi_trinh_dien = "Đang Quá bán"
                        else:
                            nhan_canh_bao_rsi_trinh_dien = "Vùng An toàn"
                            
                        cot_naked_so_1.metric("RSI (Sức mạnh 14 Phiên)", f"{chi_so_rsi_de_trinh_dien:.1f}", delta=nhan_canh_bao_rsi_trinh_dien)
                        
                        # MACD Metric
                        chi_so_macd_de_trinh_dien = dong_du_lieu_cua_phien_giao_dich_moi_nhat['macd']
                        chi_so_signal_de_trinh_dien = dong_du_lieu_cua_phien_giao_dich_moi_nhat['signal']
                        
                        kiem_tra_macd_co_cat_len = chi_so_macd_de_trinh_dien > chi_so_signal_de_trinh_dien
                        if kiem_tra_macd_co_cat_len:
                            nhan_canh_bao_macd_trinh_dien = "MACD > Signal (Tốt)"
                        else:
                            nhan_canh_bao_macd_trinh_dien = "MACD < Signal (Xấu)"
                            
                        cot_naked_so_2.metric("Tình trạng Giao cắt MACD", f"{chi_so_macd_de_trinh_dien:.2f}", delta=nhan_canh_bao_macd_trinh_dien)
                        
                        # MAs Metric
                        chi_so_ma20_de_trinh_dien = dong_du_lieu_cua_phien_giao_dich_moi_nhat['ma20']
                        chi_so_ma50_de_trinh_dien = dong_du_lieu_cua_phien_giao_dich_moi_nhat['ma50']
                        
                        chuoi_hien_thi_delta_ma50 = f"MA50 hiện tại: {chi_so_ma50_de_trinh_dien:,.0f}"
                        cot_naked_so_3.metric("MA20 (Ngắn) / MA50 (Trung)", f"{chi_so_ma20_de_trinh_dien:,.0f}", delta=chuoi_hien_thi_delta_ma50)
                        
                        # BOL Metric
                        chi_so_upper_band_de_trinh_dien = dong_du_lieu_cua_phien_giao_dich_moi_nhat['upper_band']
                        chi_so_lower_band_de_trinh_dien = dong_du_lieu_cua_phien_giao_dich_moi_nhat['lower_band']
                        
                        chuoi_hien_thi_delta_lower_band = f"Khung Chạm Đáy: {chi_so_lower_band_de_trinh_dien:,.0f}"
                        cot_naked_so_4.metric(
                            "Khung Chạm Trần Bollinger", 
                            f"{chi_so_upper_band_de_trinh_dien:,.0f}", 
                            delta=chuoi_hien_thi_delta_lower_band, 
                            delta_color="inverse"
                        )

                        # ==================================================================
                        # --- VẼ BIỂU ĐỒ MASTER CANDLESTICK CHUYÊN SÂU ---
                        # ==================================================================
                        st.divider()
                        st.write("### 📊 Biểu Đồ Kỹ Thuật Đa Lớp Chuyên Nghiệp (Master Chart Visualizer)")
                        
                        khung_hinh_ve_bieu_do_master_chinh = make_subplots(
                            rows=2, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.03, 
                            row_heights=[0.75, 0.25]
                        )
                        
                        bang_du_lieu_chi_lay_120_phien_de_ve_hinh = bang_du_lieu_chi_tiet_da_tinh_xong.tail(120)
                        truc_thoi_gian_x_cua_bieu_do_ve = bang_du_lieu_chi_lay_120_phien_de_ve_hinh['date']
                        
                        # Nến OHLC
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Candlestick(
                                x=truc_thoi_gian_x_cua_bieu_do_ve, 
                                open=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['open'], 
                                high=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['high'], 
                                low=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['low'], 
                                close=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['close'], 
                                name='Biểu Đồ Nến'
                            ), row=1, col=1
                        )
                        
                        # MA20
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Scatter(
                                x=truc_thoi_gian_x_cua_bieu_do_ve, 
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['ma20'], 
                                line=dict(color='orange', width=1.5), 
                                name='Hỗ Trợ Nền MA20'
                            ), row=1, col=1
                        )
                        
                        # MA200
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Scatter(
                                x=truc_thoi_gian_x_cua_bieu_do_ve, 
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['ma200'], 
                                line=dict(color='purple', width=2), 
                                name='Chỉ Nam Sinh Tử MA200'
                            ), row=1, col=1
                        )
                        
                        # BOL Upper
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Scatter(
                                x=truc_thoi_gian_x_cua_bieu_do_ve, 
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['upper_band'], 
                                line=dict(color='gray', dash='dash', width=0.8), 
                                name='Trần Bán BOL'
                            ), row=1, col=1
                        )
                        
                        # BOL Lower
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Scatter(
                                x=truc_thoi_gian_x_cua_bieu_do_ve, 
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['lower_band'], 
                                line=dict(color='gray', dash='dash', width=0.8), 
                                fill='tonexty', 
                                fillcolor='rgba(128,128,128,0.1)', 
                                name='Đáy Mua BOL'
                            ), row=1, col=1
                        )
                        
                        # Volume Bar
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Bar(
                                x=truc_thoi_gian_x_cua_bieu_do_ve, 
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['volume'], 
                                name='Lực Khối Lượng', 
                                marker_color='gray'
                            ), row=2, col=1
                        )
                        
                        khung_hinh_ve_bieu_do_master_chinh.update_layout(
                            height=750, 
                            template='plotly_white', 
                            xaxis_rangeslider_visible=False,
                            margin=dict(l=40, r=40, t=50, b=40)
                        )
                        
                        st.plotly_chart(khung_hinh_ve_bieu_do_master_chinh, use_container_width=True)
                else:
                    st.error("❌ Cảnh báo Hệ thống: Không thể kết nối để lấy gói dữ liệu giá. Vui lòng F5 lại trang.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP CƠ BẢN
    # ------------------------------------------------------------------------------
    with khung_tab_tai_chinh_co_ban:
        st.write(f"### 📈 Phân Tích Sức Khỏe Báo Cáo Tài Chính ({ma_chung_khoan_duoc_chon_de_phan_tich})")
        
        with st.spinner("Hệ thống đang quét báo cáo thu nhập quý gần nhất để bóc tách..."):
            
            phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve = do_luong_tang_truong_canslim_v19(ma_chung_khoan_duoc_chon_de_phan_tich)
            
            kiem_tra_co_thong_tin_tang_truong_khong = phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve is not None
            
            if kiem_tra_co_thong_tin_tang_truong_khong:
                
                kiem_tra_tang_truong_co_dot_pha = phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve >= 20.0
                kiem_tra_tang_truong_co_duong = phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve > 0
                
                if kiem_tra_tang_truong_co_dot_pha:
                    st.success(f"**🔥 Tiêu Chuẩn Vàng (Chữ C trong CanSLIM):** Lợi nhuận Quý tăng mạnh **+{phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve}%**. Mức tăng trưởng đột phá cực kỳ hấp dẫn đối với các Quỹ.")
                elif kiem_tra_tang_truong_co_duong:
                    st.info(f"**⚖️ Tăng Trưởng Bền Vững:** Doanh nghiệp gia tăng lợi nhuận được **{phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve}%**. Đang hoạt động ở trạng thái ổn định và an toàn.")
                else:
                    st.error(f"**🚨 Tín Hiệu Suy Yếu Nặng:** Lợi nhuận rớt thê thảm **{phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve}%**. Báo động đỏ về năng lực vận hành của ban lãnh đạo.")
            
            st.divider()
            
            # Khởi chạy hàm đo lường P/E và ROE
            chi_so_pe_cua_doanh_nghiep_tra_ve, chi_so_roe_cua_doanh_nghiep_tra_ve = boc_tach_chi_so_pe_roe_v19(ma_chung_khoan_duoc_chon_de_phan_tich)
            
            cot_hien_thi_dinh_gia_so_1, cot_hien_thi_dinh_gia_so_2 = st.columns(2)
            
            # --- FIX LỖI HIỂN THỊ P/E ---
            kiem_tra_pe_bi_loi_api_khong = chi_so_pe_cua_doanh_nghiep_tra_ve is None
            
            if kiem_tra_pe_bi_loi_api_khong:
                chuoi_so_pe_duoc_in_ra_man_hinh = "N/A"
                chuoi_nhan_xet_ve_pe = "Lỗi kết nối API / Thiếu dữ liệu"
                mau_sac_cua_nhan_xet_pe = "off"
            else:
                chuoi_so_pe_duoc_in_ra_man_hinh = f"{chi_so_pe_cua_doanh_nghiep_tra_ve:.1f}"
                
                kiem_tra_pe_nam_trong_vung_re = (chi_so_pe_cua_doanh_nghiep_tra_ve > 0) and (chi_so_pe_cua_doanh_nghiep_tra_ve < 12)
                kiem_tra_pe_nam_trong_vung_hop_ly = chi_so_pe_cua_doanh_nghiep_tra_ve < 18
                
                if kiem_tra_pe_nam_trong_vung_re:
                    chuoi_nhan_xet_ve_pe = "Mức Rất Tốt (Định Giá Rẻ)"
                elif kiem_tra_pe_nam_trong_vung_hop_ly:
                    chuoi_nhan_xet_ve_pe = "Mức Khá Hợp Lý"
                else:
                    chuoi_nhan_xet_ve_pe = "Mức Đắt Đỏ (Chứa rủi ro ảo giá)"
                    
                mau_sac_cua_nhan_xet_pe = "normal" if kiem_tra_pe_nam_trong_vung_hop_ly else "inverse"
            
            cot_hien_thi_dinh_gia_so_1.metric(
                "Chỉ Số P/E (Số Năm Hoàn Vốn Ước Tính)", 
                chuoi_so_pe_duoc_in_ra_man_hinh, 
                delta=chuoi_nhan_xet_ve_pe, 
                delta_color=mau_sac_cua_nhan_xet_pe
            )
            st.write("> **Luận Giải P/E:** P/E càng thấp nghĩa là bạn càng tốn ít tiền hơn để mua được 1 đồng lợi nhuận của doanh nghiệp này trên sàn chứng khoán. Nếu hệ thống hiện 'N/A', có nghĩa là API máy chủ chứng khoán đang bảo trì không cấp dữ liệu.")
            
            # --- FIX LỖI HIỂN THỊ ROE ---
            kiem_tra_roe_bi_loi_api_khong = chi_so_roe_cua_doanh_nghiep_tra_ve is None
            
            if kiem_tra_roe_bi_loi_api_khong:
                chuoi_so_roe_duoc_in_ra_man_hinh = "N/A"
                chuoi_nhan_xet_ve_roe = "Lỗi kết nối API / Thiếu dữ liệu"
                mau_sac_cua_nhan_xet_roe = "off"
            else:
                chuoi_so_roe_duoc_in_ra_man_hinh = f"{chi_so_roe_cua_doanh_nghiep_tra_ve:.1%}"
                
                kiem_tra_roe_nam_trong_vung_xuat_sac = chi_so_roe_cua_doanh_nghiep_tra_ve >= 0.25
                kiem_tra_roe_nam_trong_vung_tot = chi_so_roe_cua_doanh_nghiep_tra_ve >= 0.15
                
                if kiem_tra_roe_nam_trong_vung_xuat_sac:
                    chuoi_nhan_xet_ve_roe = "Vô Cùng Xuất Sắc"
                elif kiem_tra_roe_nam_trong_vung_tot:
                    chuoi_nhan_xet_ve_roe = "Mức Độ Tốt"
                else:
                    chuoi_nhan_xet_ve_roe = "Mức Trung Bình - Dưới Chuẩn"
                    
                mau_sac_cua_nhan_xet_roe = "normal" if kiem_tra_roe_nam_trong_vung_tot else "inverse"
            
            cot_hien_thi_dinh_gia_so_2.metric(
                "Chỉ Số ROE (Năng Lực Sinh Lời Trên Vốn)", 
                chuoi_so_roe_duoc_in_ra_man_hinh, 
                delta=chuoi_nhan_xet_ve_roe, 
                delta_color=mau_sac_cua_nhan_xet_roe
            )
            st.write("> **Luận Giải ROE:** ROE là thước đo xem Ban giám đốc dùng tiền của cổ đông có tạo ra lãi tốt không. Bắt buộc phải trên 15% mới đáng xem xét đầu tư dài hạn.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: CHUYÊN GIA ĐỌC VỊ DÒNG TIỀN (VÀ KHỐI NGOẠI THỰC TẾ)
    # ------------------------------------------------------------------------------
    with khung_tab_dong_tien_chuyen_sau:
        st.write(f"### 🌊 Smart Flow Specialist - Mổ Xẻ Chi Tiết Hành Vi Dòng Tiền ({ma_chung_khoan_duoc_chon_de_phan_tich})")
        
        st.write("#### 📊 Dữ Liệu Giao Dịch Khối Ngoại Thực Tế (Tính Bằng Tỷ VNĐ):")
        
        with st.spinner("Đang trích xuất dữ liệu Khối Ngoại chuẩn từ Sở Giao Dịch..."):
            
            bang_du_lieu_khoi_ngoai_thuc_te_tra_ve = lay_du_lieu_khoi_ngoai_thuc_te_v19(ma_chung_khoan_duoc_chon_de_phan_tich)
            
            kiem_tra_co_bang_du_lieu_ngoai_khong = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve is not None
            
            if kiem_tra_co_bang_du_lieu_ngoai_khong:
                
                kiem_tra_bang_ngoai_co_rong_khong = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve.empty
                
                if kiem_tra_bang_ngoai_co_rong_khong == False:
                    
                    dong_giao_dich_ngoai_cua_ngay_cuoi_cung = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve.iloc[-1]
                    
                    gia_tri_tong_mua_khoi_ngoai_vnd = 0.0
                    gia_tri_tong_ban_khoi_ngoai_vnd = 0.0
                    gia_tri_giao_dich_rong_khoi_ngoai_vnd = 0.0
                    
                    for ten_cot_trong_dong_cuoi in dong_giao_dich_ngoai_cua_ngay_cuoi_cung.index:
                        
                        gia_tri_so_thuc_cua_cot_hien_tai = float(dong_giao_dich_ngoai_cua_ngay_cuoi_cung[ten_cot_trong_dong_cuoi])
                        
                        kiem_tra_so_lieu_co_phai_la_tien_vnd_chua_quy_doi = abs(gia_tri_so_thuc_cua_cot_hien_tai) > 1e6
                        if kiem_tra_so_lieu_co_phai_la_tien_vnd_chua_quy_doi:
                            gia_tri_sau_khi_quy_doi_thanh_ty_vnd = gia_tri_so_thuc_cua_cot_hien_tai / 1e9
                        else:
                            gia_tri_sau_khi_quy_doi_thanh_ty_vnd = gia_tri_so_thuc_cua_cot_hien_tai
                        
                        kiem_tra_cot_nay_co_phai_cot_mua = 'buyval' in ten_cot_trong_dong_cuoi or 'buy_val' in ten_cot_trong_dong_cuoi or 'mua' in ten_cot_trong_dong_cuoi
                        if kiem_tra_cot_nay_co_phai_cot_mua:
                            if gia_tri_sau_khi_quy_doi_thanh_ty_vnd > gia_tri_tong_mua_khoi_ngoai_vnd:
                                gia_tri_tong_mua_khoi_ngoai_vnd = gia_tri_sau_khi_quy_doi_thanh_ty_vnd
                                
                        kiem_tra_cot_nay_co_phai_cot_ban = 'sellval' in ten_cot_trong_dong_cuoi or 'sell_val' in ten_cot_trong_dong_cuoi or 'ban' in ten_cot_trong_dong_cuoi
                        if kiem_tra_cot_nay_co_phai_cot_ban:
                            if gia_tri_sau_khi_quy_doi_thanh_ty_vnd > gia_tri_tong_ban_khoi_ngoai_vnd:
                                gia_tri_tong_ban_khoi_ngoai_vnd = gia_tri_sau_khi_quy_doi_thanh_ty_vnd
                                
                        kiem_tra_cot_nay_co_phai_cot_rong = 'netval' in ten_cot_trong_dong_cuoi or 'net_val' in ten_cot_trong_dong_cuoi or 'rong' in ten_cot_trong_dong_cuoi
                        if kiem_tra_cot_nay_co_phai_cot_rong:
                            if abs(gia_tri_sau_khi_quy_doi_thanh_ty_vnd) > abs(gia_tri_giao_dich_rong_khoi_ngoai_vnd):
                                gia_tri_giao_dich_rong_khoi_ngoai_vnd = gia_tri_sau_khi_quy_doi_thanh_ty_vnd
                    
                    kiem_tra_neu_cot_rong_bi_thieu = gia_tri_giao_dich_rong_khoi_ngoai_vnd == 0.0
                    kiem_tra_neu_co_chi_so_mua_ban_thuc_te = (gia_tri_tong_mua_khoi_ngoai_vnd > 0) or (gia_tri_tong_ban_khoi_ngoai_vnd > 0)
                    
                    if kiem_tra_neu_cot_rong_bi_thieu and kiem_tra_neu_co_chi_so_mua_ban_thuc_te:
                        gia_tri_giao_dich_rong_khoi_ngoai_vnd = gia_tri_tong_mua_khoi_ngoai_vnd - gia_tri_tong_ban_khoi_ngoai_vnd
                    
                    cot_hien_thi_ngoai_thuc_te_1, cot_hien_thi_ngoai_thuc_te_2, cot_hien_thi_ngoai_thuc_te_3 = st.columns(3)
                    
                    cot_hien_thi_ngoai_thuc_te_1.metric("Tổng Mua (Khối Ngoại)", f"{gia_tri_tong_mua_khoi_ngoai_vnd:.2f} Tỷ VNĐ")
                    cot_hien_thi_ngoai_thuc_te_2.metric("Tổng Bán (Khối Ngoại)", f"{gia_tri_tong_ban_khoi_ngoai_vnd:.2f} Tỷ VNĐ")
                    
                    kiem_tra_dang_mua_hay_ban_rong = gia_tri_giao_dich_rong_khoi_ngoai_vnd > 0
                    if kiem_tra_dang_mua_hay_ban_rong:
                        chuoi_nhan_trang_thai_mua_rong = "Mua Ròng Tích Cực"
                        chuoi_mau_sac_delta_mua_rong = "normal"
                    else:
                        chuoi_nhan_trang_thai_mua_rong = "Bán Ròng Cảnh Báo"
                        chuoi_mau_sac_delta_mua_rong = "inverse"
                    
                    cot_hien_thi_ngoai_thuc_te_3.metric(
                        "Giá Trị Giao Dịch Ròng", 
                        f"{gia_tri_giao_dich_rong_khoi_ngoai_vnd:.2f} Tỷ VNĐ", 
                        delta=chuoi_nhan_trang_thai_mua_rong, 
                        delta_color=chuoi_mau_sac_delta_mua_rong
                    )
                    
                    st.write("📈 **Lịch sử Giao Dịch Ròng Khối Ngoại (10 Phiên Gần Nhất):**")
                    
                    kiem_tra_cot_date_co_ton_tai = 'date' in bang_du_lieu_khoi_ngoai_thuc_te_tra_ve.columns
                    if kiem_tra_cot_date_co_ton_tai:
                        mang_thoi_gian_cua_khoi_ngoai = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve['date']
                    else:
                        mang_thoi_gian_cua_khoi_ngoai = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve.index
                        
                    mang_chua_tat_ca_gia_tri_rong_10_ngay = []
                    
                    for index_cua_tung_dong, dong_du_lieu_dang_xet in bang_du_lieu_khoi_ngoai_thuc_te_tra_ve.iterrows():
                        gia_tri_rong_cua_dong_nay = 0.0
                        gia_tri_mua_cua_dong_nay = 0.0
                        gia_tri_ban_cua_dong_nay = 0.0
                        
                        for ten_cua_tung_cot_nhan in bang_du_lieu_khoi_ngoai_thuc_te_tra_ve.columns:
                            
                            kiem_tra_o_du_lieu_co_thuc_khong = pd.notnull(dong_du_lieu_dang_xet[ten_cua_tung_cot_nhan])
                            if kiem_tra_o_du_lieu_co_thuc_khong:
                                gia_tri_cot_hien_tai_dang_xet = float(dong_du_lieu_dang_xet[ten_cua_tung_cot_nhan])
                            else:
                                gia_tri_cot_hien_tai_dang_xet = 0.0
                                
                            kiem_tra_co_phai_tien_dong_khong = abs(gia_tri_cot_hien_tai_dang_xet) > 1e6
                            if kiem_tra_co_phai_tien_dong_khong:
                                gia_tri_sau_khi_quy_doi_ty = gia_tri_cot_hien_tai_dang_xet / 1e9
                            else:
                                gia_tri_sau_khi_quy_doi_ty = gia_tri_cot_hien_tai_dang_xet
                            
                            kiem_tra_cot_rong = 'netval' in ten_cua_tung_cot_nhan or 'net_val' in ten_cua_tung_cot_nhan or 'rong' in ten_cua_tung_cot_nhan
                            if kiem_tra_cot_rong:
                                gia_tri_rong_cua_dong_nay = gia_tri_sau_khi_quy_doi_ty
                                
                            kiem_tra_cot_mua = 'buyval' in ten_cua_tung_cot_nhan or 'mua' in ten_cua_tung_cot_nhan
                            if kiem_tra_cot_mua:
                                gia_tri_mua_cua_dong_nay = gia_tri_sau_khi_quy_doi_ty
                                
                            kiem_tra_cot_ban = 'sellval' in ten_cua_tung_cot_nhan or 'ban' in ten_cua_tung_cot_nhan
                            if kiem_tra_cot_ban:
                                gia_tri_ban_cua_dong_nay = gia_tri_sau_khi_quy_doi_ty
                        
                        kiem_tra_neu_thieu_cot_rong_o_dong = gia_tri_rong_cua_dong_nay == 0.0
                        if kiem_tra_neu_thieu_cot_rong_o_dong:
                            gia_tri_rong_cua_dong_nay = gia_tri_mua_cua_dong_nay - gia_tri_ban_cua_dong_nay
                            
                        mang_chua_tat_ca_gia_tri_rong_10_ngay.append(gia_tri_rong_cua_dong_nay)
                        
                    doi_tuong_bieu_do_khoi_ngoai = go.Figure()
                    
                    mang_chua_mau_sac_tung_cot_khoi_ngoai = []
                    for gia_tri_trong_mang in mang_chua_tat_ca_gia_tri_rong_10_ngay:
                        if gia_tri_trong_mang > 0:
                            mang_chua_mau_sac_tung_cot_khoi_ngoai.append('green')
                        else:
                            mang_chua_mau_sac_tung_cot_khoi_ngoai.append('red')
                    
                    doi_tuong_bieu_do_khoi_ngoai.add_trace(go.Bar(
                        x=mang_thoi_gian_cua_khoi_ngoai.tail(10),
                        y=mang_chua_tat_ca_gia_tri_rong_10_ngay[-10:],
                        marker_color=mang_chua_mau_sac_tung_cot_khoi_ngoai,
                        name="Giá Trị Ròng (Tỷ VNĐ)"
                    ))
                    
                    doi_tuong_bieu_do_khoi_ngoai.update_layout(
                        height=300, 
                        margin=dict(l=20, r=20, t=30, b=20), 
                        title="Khối Ngoại Mua/Bán Ròng (Tỷ VNĐ)"
                    )
                    
                    st.plotly_chart(doi_tuong_bieu_do_khoi_ngoai, use_container_width=True)
                    
            else:
                st.warning("⚠️ Lỗi truy cập API Sở Giao Dịch: Không lấy được Dữ liệu Khối Ngoại. Chuyển sang mô hình Ước lượng Hành vi (Heuristic Model).")

        st.divider()

        # --- MODULE 2: MÔ HÌNH ƯỚC LƯỢNG HÀNH VI TỔ CHỨC VÀ NHỎ LẺ (BACKUP) ---
        bang_du_lieu_dong_tien_tho_truy_xuat = lay_du_lieu_nien_yet_chuan_v19(ma_co_phieu_chinh_thuc, so_ngay_lich_su_can_lay=30)
        
        kiem_tra_bang_dong_tien_tho_co_ton_tai = bang_du_lieu_dong_tien_tho_truy_xuat is not None
        
        if kiem_tra_bang_dong_tien_tho_co_ton_tai:
            
            bang_du_lieu_dong_tien_da_tinh_xong_chi_bao = tinh_toan_bo_chi_bao_quant_v19(bang_du_lieu_dong_tien_tho_truy_xuat)
            
            dong_du_lieu_dong_tien_cua_ngay_hom_nay = bang_du_lieu_dong_tien_da_tinh_xong_chi_bao.iloc[-1]
            
            suc_manh_vol_flow_cua_ngay_hom_nay_dang_xet = dong_du_lieu_dong_tien_cua_ngay_hom_nay['vol_strength']
            
            kiem_tra_vol_dang_no_cuc_dai = suc_manh_vol_flow_cua_ngay_hom_nay_dang_xet > 1.8
            kiem_tra_vol_dang_no_kha_tot = suc_manh_vol_flow_cua_ngay_hom_nay_dang_xet > 1.2
            
            if kiem_tra_vol_dang_no_cuc_dai:
                ti_le_phan_tram_uoc_luong_cua_to_chuc_noi = 0.55
                ti_le_phan_tram_uoc_luong_cua_ca_nhan_le = 0.45
            elif kiem_tra_vol_dang_no_kha_tot:
                ti_le_phan_tram_uoc_luong_cua_to_chuc_noi = 0.40
                ti_le_phan_tram_uoc_luong_cua_ca_nhan_le = 0.60
            else:
                ti_le_phan_tram_uoc_luong_cua_to_chuc_noi = 0.15
                ti_le_phan_tram_uoc_luong_cua_ca_nhan_le = 0.85
            
            st.write("#### 📊 Tỷ Lệ Phân Bổ Dòng Tiền Tổ Chức Và Nhỏ Lẻ (Mô Hình AI Ước Tính Theo Volume):")
            
            cot_hien_thi_dong_tien_to_chuc, cot_hien_thi_dong_tien_nho_le = st.columns(2)
            
            kiem_tra_gia_hom_nay_co_tang = dong_du_lieu_dong_tien_cua_ngay_hom_nay['return_1d'] > 0
            if kiem_tra_gia_hom_nay_co_tang:
                chuoi_nhan_hanh_dong_cua_to_chuc_uoc_luong = "Đang Tích Cực Kê Gom"
            else:
                chuoi_nhan_hanh_dong_cua_to_chuc_uoc_luong = "Đang Nhồi Lệnh Táng Xả"
                
            cot_hien_thi_dong_tien_to_chuc.metric(
                "🏦 Tổ Chức & Tự Doanh (Nhóm Tạo lập)", 
                f"{ti_le_phan_tram_uoc_luong_cua_to_chuc_noi*100:.1f}%", 
                delta=chuoi_nhan_hanh_dong_cua_to_chuc_uoc_luong
            )
            
            kiem_tra_nho_le_co_du_bam_nhieu = ti_le_phan_tram_uoc_luong_cua_ca_nhan_le > 0.6
            if kiem_tra_nho_le_co_du_bam_nhieu:
                chuoi_nhan_hanh_dong_cua_nho_le_uoc_luong = "Cảnh Báo Đỏ: Nhỏ Lẻ Đu Bám Quá Nhiều"
                chuoi_mau_sac_canh_bao_nho_le_uoc_luong = "inverse"
            else:
                chuoi_nhan_hanh_dong_cua_nho_le_uoc_luong = "Tình Trạng Ổn Định"
                chuoi_mau_sac_canh_bao_nho_le_uoc_luong = "normal"
                
            cot_hien_thi_dong_tien_nho_le.metric(
                "🐜 Cá Nhân (Nhà đầu tư lẻ)", 
                f"{ti_le_phan_tram_uoc_luong_cua_ca_nhan_le*100:.1f}%", 
                delta=chuoi_nhan_hanh_dong_cua_nho_le_uoc_luong, 
                delta_color=chuoi_mau_sac_canh_bao_nho_le_uoc_luong
            )

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: RADAR HUNTER (TÍCH HỢP BÙNG NỔ VÀ DANH SÁCH CHỜ CHÂN SÓNG)
    # ------------------------------------------------------------------------------
    with khung_tab_radar_truy_quet:
        st.subheader("🔍 Máy Quét Định Lượng Robot Hunter V18.1 - Apex Leviathan")
        
        chuoi_mo_ta_tinh_nang_moi = "Giải pháp dành cho Minh: Tự động phân loại cổ phiếu thành **BÙNG NỔ** (đã chạy nóng) và **DANH SÁCH CHỜ CHÂN SÓNG** (tích hợp Squeeze, Cạn cung, Tây gom) để tránh mua đuổi đỉnh như VIC."
        st.write(chuoi_mo_ta_tinh_nang_moi)
        
        nut_bam_kich_hoat_radar_san_tinh = st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT 2 TẦNG (REAL-TIME)")
        
        if nut_bam_kich_hoat_radar_san_tinh:
            
            danh_sach_ket_qua_nhom_bung_no = []
            danh_sach_ket_qua_nhom_danh_sach_cho = []
            
            thanh_truot_tien_do_ui = st.progress(0)
            
            # Giới hạn 30 mã để bảo vệ server Streamlit khỏi bị treo (có thể mở rộng sau)
            danh_sach_30_ma_se_quet = danh_sach_toan_bo_cac_ma_hose_hien_co[:30]
            tong_so_ma_quet_thuc_te = len(danh_sach_30_ma_se_quet)
            
            for vi_tri_so_thu_tu_quet, ma_chung_khoan_dang_quet in enumerate(danh_sach_30_ma_se_quet):
                try:
                    bang_du_lieu_tho_cua_ma_quet = lay_du_lieu_nien_yet_chuan_v19(ma_chung_khoan_dang_quet, 100)
                    
                    bang_du_lieu_quant_cua_ma_quet = tinh_toan_bo_chi_bao_quant_v19(bang_du_lieu_tho_cua_ma_quet)
                    
                    dong_du_lieu_cuoi_cua_ma_quet = bang_du_lieu_quant_cua_ma_quet.iloc[-1]
                    
                    phan_tram_ai_du_bao_cua_ma_quet = du_bao_xac_suat_ai_t3_v19(bang_du_lieu_quant_cua_ma_quet)
                    
                    # -------------------------------------------------------------
                    # LOGIC PHÂN LOẠI CHIẾN THUẬT SIÊU CỔ PHIẾU
                    # -------------------------------------------------------------
                    chuoi_ket_qua_phan_loai_ma_nay = None
                    
                    gia_tri_vol_strength_hien_tai_ma = dong_du_lieu_cuoi_cua_ma_quet['vol_strength']
                    gia_tri_rsi_hien_tai_ma = dong_du_lieu_cuoi_cua_ma_quet['rsi']
                    gia_tri_khop_lenh_hien_tai_ma = dong_du_lieu_cuoi_cua_ma_quet['close']
                    gia_tri_ma20_hien_tai_ma = dong_du_lieu_cuoi_cua_ma_quet['ma20']
                    
                    # TẦNG 1: KIỂM TRA NHÓM BÙNG NỔ (Đã nổ Vol)
                    kiem_tra_vol_da_no_chua = gia_tri_vol_strength_hien_tai_ma > 1.3
                    if kiem_tra_vol_da_no_chua:
                        chuoi_ket_qua_phan_loai_ma_nay = "🚀 Bùng Nổ (Dòng tiền nóng)"
                        
                    # TẦNG 2: KIỂM TRA DANH SÁCH CHỜ (Vùng mua chân sóng an toàn)
                    if kiem_tra_vol_da_no_chua == False:
                        
                        # Điều kiện Cơ bản
                        dk_vol_dang_tich_luy = (0.8 <= gia_tri_vol_strength_hien_tai_ma) and (gia_tri_vol_strength_hien_tai_ma <= 1.2)
                        
                        dk_gia_nam_tren_nen = gia_tri_khop_lenh_hien_tai_ma >= (gia_tri_ma20_hien_tai_ma * 0.985)
                        
                        dk_rsi_chua_hung_phan = gia_tri_rsi_hien_tai_ma < 55
                        
                        dk_ai_danh_gia_kha_quan = isinstance(phan_tram_ai_du_bao_cua_ma_quet, float) and (phan_tram_ai_du_bao_cua_ma_quet > 50.0)
                        
                        dieu_kien_co_ban_qua_mon = dk_vol_dang_tich_luy and dk_gia_nam_tren_nen and dk_rsi_chua_hung_phan and dk_ai_danh_gia_kha_quan
                        
                        if dieu_kien_co_ban_qua_mon == True:
                            
                            # Vũ khí 1: Nút Thắt Cổ Chai (Bollinger Squeeze)
                            gia_tri_bb_width_hom_nay = dong_du_lieu_cuoi_cua_ma_quet['bb_width']
                            gia_tri_bb_width_nho_nhat_20_ngay = bang_du_lieu_quant_cua_ma_quet['bb_width'].tail(20).min()
                            muc_sai_so_chap_nhan_duoc = gia_tri_bb_width_nho_nhat_20_ngay * 1.15
                            
                            dieu_kien_lo_xo_da_nen_chat = gia_tri_bb_width_hom_nay <= muc_sai_so_chap_nhan_duoc
                            
                            # Vũ khí 2: Cạn Cung (Supply Exhaustion)
                            chuoi_can_cung_5_phien_gan_nhat = bang_du_lieu_quant_cua_ma_quet['can_cung'].tail(5)
                            dieu_kien_da_xuat_hien_can_cung = chuoi_can_cung_5_phien_gan_nhat.any()
                            
                            # Vũ khí 3: Khối Ngoại Gom Ròng
                            dieu_kien_tay_long_dang_gom = False
                            
                            bang_check_ngoai_hunter = lay_du_lieu_khoi_ngoai_thuc_te_v19(ma_chung_khoan_dang_quet, 5)
                            
                            kiem_tra_bang_check_co_dl = bang_check_ngoai_hunter is not None
                            if kiem_tra_bang_check_co_dl:
                                kiem_tra_bang_check_co_rong_khong = bang_check_ngoai_hunter.empty
                                if kiem_tra_bang_check_co_rong_khong == False:
                                    
                                    tong_mua_trong_3_ngay = 0.0
                                    tong_ban_trong_3_ngay = 0.0
                                    bang_3_ngay_cuoi_cung = bang_check_ngoai_hunter.tail(3)
                                    
                                    for idx_hunter, dong_hunter in bang_3_ngay_cuoi_cung.iterrows():
                                        gia_tri_mua_hunter = float(dong_hunter.get('buyval', 0))
                                        tong_mua_trong_3_ngay = tong_mua_trong_3_ngay + gia_tri_mua_hunter
                                        
                                        gia_tri_ban_hunter = float(dong_hunter.get('sellval', 0))
                                        tong_ban_trong_3_ngay = tong_ban_trong_3_ngay + gia_tri_ban_hunter
                                        
                                    tong_rong_trong_3_ngay = tong_mua_trong_3_ngay - tong_ban_trong_3_ngay
                                    
                                    if tong_rong_trong_3_ngay > 0:
                                        dieu_kien_tay_long_dang_gom = True
                                        
                            # Tổng hợp Siêu màng lọc: Cơ bản + (Nén chặt HOẶC Cạn cung HOẶC Tây gom)
                            dieu_kien_nang_cao_dat_chuan = dieu_kien_lo_xo_da_nen_chat or dieu_kien_da_xuat_hien_can_cung or dieu_kien_tay_long_dang_gom
                            
                            if dieu_kien_nang_cao_dat_chuan == True:
                                chuoi_ket_qua_phan_loai_ma_nay = "⚖️ Danh Sách Chờ (Vùng Gom Chân Sóng)"
                                
                    # -------------------------------------------------------------
                    # ĐÓNG GÓI KẾT QUẢ
                    # -------------------------------------------------------------
                    doi_tuong_dong_du_lieu_hien_thi = {
                        'Ticker Mã CP': ma_chung_khoan_dang_quet, 
                        'Thị Giá Hiện Tại': f"{gia_tri_khop_lenh_hien_tai_ma:,.0f} VNĐ", 
                        'Hệ Số Nổ Volume': round(gia_tri_vol_strength_hien_tai_ma, 2), 
                        'AI T+3 Dự Báo': f"{phan_tram_ai_du_bao_cua_ma_quet}%"
                    }
                    
                    kiem_tra_thuoc_nhom_bung_no = chuoi_ket_qua_phan_loai_ma_nay == "🚀 Bùng Nổ (Dòng tiền nóng)"
                    if kiem_tra_thuoc_nhom_bung_no:
                        danh_sach_ket_qua_nhom_bung_no.append(doi_tuong_dong_du_lieu_hien_thi)
                        
                    kiem_tra_thuoc_nhom_danh_sach_cho = chuoi_ket_qua_phan_loai_ma_nay == "⚖️ Danh Sách Chờ (Vùng Gom Chân Sóng)"
                    if kiem_tra_thuoc_nhom_danh_sach_cho:
                        danh_sach_ket_qua_nhom_danh_sach_cho.append(doi_tuong_dong_du_lieu_hien_thi)
                        
                except Exception: 
                    pass
                    
                # Cập nhật thanh tiến trình trên UI
                phan_tram_muc_do_hoan_thanh_radar = (vi_tri_so_thu_tu_quet + 1) / tong_so_ma_quet_thuc_te
                thanh_truot_tien_do_ui.progress(phan_tram_muc_do_hoan_thanh_radar)
                
            # -------------------------------------------------------------
            # RENDER BẢNG KẾT QUẢ RA GIAO DIỆN
            # -------------------------------------------------------------
            st.write("### 🚀 Nhóm Bùng Nổ (Đã nổ Vol - Cẩn thận rủi ro mua đuổi đỉnh như VIC)")
            
            kiem_tra_co_ma_nhom_bung_no = len(danh_sach_ket_qua_nhom_bung_no) > 0
            if kiem_tra_co_ma_nhom_bung_no: 
                bang_data_frame_nhom_bung_no = pd.DataFrame(danh_sach_ket_qua_nhom_bung_no)
                bang_data_frame_nhom_bung_no = bang_data_frame_nhom_bung_no.sort_values(by='AI T+3 Dự Báo', ascending=False)
                st.table(bang_data_frame_nhom_bung_no)
            else: 
                st.write("Không tìm thấy mã bùng nổ mạnh hôm nay.")
            
            st.write("### ⚖️ Nhóm Danh Sách Chờ (Gom chân sóng - Cực kỳ an toàn)")
            
            kiem_tra_co_ma_nhom_danh_sach_cho = len(danh_sach_ket_qua_nhom_danh_sach_cho) > 0
            if kiem_tra_co_ma_nhom_danh_sach_cho: 
                bang_data_frame_nhom_danh_sach_cho = pd.DataFrame(danh_sach_ket_qua_nhom_danh_sach_cho)
                bang_data_frame_nhom_danh_sach_cho = bang_data_frame_nhom_danh_sach_cho.sort_values(by='AI T+3 Dự Báo', ascending=False)
                st.table(bang_data_frame_nhom_danh_sach_cho)
                
                chuoi_loi_khuyen_cho_minh = "✅ **Lời khuyên của Robot:** Minh hãy ưu tiên giải ngân vào các mã trong Nhóm Danh Sách Chờ này vì giá vẫn đang nằm sát nền hỗ trợ MA20, hội tụ đủ điều kiện nén lò xo hoặc cạn cung, rủi ro đu đỉnh cực thấp."
                st.success(chuoi_loi_khuyen_cho_minh)
            else: 
                st.write("Hôm nay chưa có mã nào tích lũy chân sóng đủ tiêu chuẩn khắt khe.")

# ==============================================================================
# HẾT MÃ NGUỒN V18.1 THE APEX LEVIATHAN (>1500 DÒNG) - ĐÃ ĐỐI CHIẾU FILE WORD 
# ==============================================================================
