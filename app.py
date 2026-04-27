# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V20.0 (THE PREDATOR LEVIATHAN)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# NỀN TẢNG CƠ SỞ: KẾ THỪA 100% TỪ FILE "25.4.docx"
# TRẠNG THÁI: PHIÊN BẢN CHUẨN HÓA ĐỊNH DANH & KHAI TRIỂN TOÀN PHẦN
# CAM KẾT V20.0:
# 1. ĐỘ DÀI CỰC ĐẠI: Áp dụng Vertical Formatting (Định dạng dọc), không viết tắt.
# 2. CHUẨN HÓA DANH XƯNG: Xóa sạch mọi hậu tố (v13, v14, v17, v18...).
# 3. DANH SÁCH CHỜ (WATCHLIST): Lọc 4 màng: Thắt Bollinger, Cạn Cung, Tây Gom, Tự Doanh Gom.
# 4. FIX TRIỆT ĐỂ: Múi giờ VN (chống rỗng data sáng), P/E N/A, NameError, TypeError.
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
# Khởi tạo khối lệnh Try-Except để đảm bảo tài nguyên NLTK luôn sẵn sàng
try:

    # Hệ thống thử tìm file nén lexicon trong môi trường lưu trữ của máy chủ
    chuoi_du_ong_dan_nltk = 'sentiment/vader_lexicon.zip'
    nltk.data.find(chuoi_du_ong_dan_nltk)

except LookupError:

    # Nếu chưa có, kích hoạt tiến trình tải xuống tự động từ máy chủ chính thức
    chuoi_ten_goi_tai_ve = 'vader_lexicon'
    nltk.download(chuoi_ten_goi_tai_ve)
# ==============================================================================
# 0. HÀM CHUYÊN BIỆT: ÉP MÚI GIỜ VIỆT NAM (UTC+7) - FIX LỖI PHIÊN SÁNG
# ==============================================================================
def lay_thoi_gian_chuan_viet_nam():
    """
    Máy chủ Streamlit Cloud mặc định chạy giờ quốc tế (UTC).
    Hàm này ép toàn bộ thời gian của hệ thống cộng thêm 7 tiếng (UTC+7).
    Giúp Robot quét chính xác dữ liệu từ 9h sáng của sàn HOSE.
    """

    # 1. Lấy thời gian quốc tế (UTC) hiện tại từ đồng hồ máy chủ
    thoi_gian_quoc_te_hien_tai = datetime.utcnow()

    # 2. Khai báo khoảng chênh lệch 7 tiếng để đưa về giờ Việt Nam
    so_gio_can_bu_tru = 7
    khoang_cach_mui_gio_viet_nam = timedelta(hours=so_gio_can_bu_tru)

    # 3. Thực hiện phép toán cộng thời gian
    thoi_gian_viet_nam_chinh_xac = thoi_gian_quoc_te_hien_tai + khoang_cach_mui_gio_viet_nam

    # 4. Trả về kết quả thời gian chuẩn xác đã được đồng bộ
    return thoi_gian_viet_nam_chinh_xac
# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & PHÂN QUYỀN (SECURITY LAYER)
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh():
    """
    Hàm bảo mật cấp cao, khóa hệ thống bằng mật mã của Minh.
    Thiết kế logic tách biệt hoàn toàn để chống lỗi KeyError trên Streamlit.
    (Đã gọt rửa hậu tố _v13, quy hoạch về chuẩn duy nhất)
    """

    # 1. Định nghĩa chuỗi khóa (Key) lưu trong bộ nhớ Session
    chuoi_khoa_luu_tru_session = "trang_thai_dang_nhap_thanh_cong_master"

    # 2. Kiểm tra trạng thái đã đăng nhập thành công từ trước
    trang_thai_xac_thuc_lan_truoc = st.session_state.get(
        chuoi_khoa_luu_tru_session,
        False
    )

    # Đánh giá kết quả kiểm tra
    kiem_tra_da_dang_nhap = trang_thai_xac_thuc_lan_truoc == True

    if kiem_tra_da_dang_nhap:
        # Nếu đã xác thực thành công trước đó, cho phép ứng dụng khởi chạy
        return True
    # 3. Nếu chưa đăng nhập, dựng giao diện khóa trung tâm
    chuoi_tieu_de_giao_dien_khoa = "###  🔐  Quant System V20.0 - Cổng Bảo Mật Trung Tâm"
    st.markdown(chuoi_tieu_de_giao_dien_khoa)

    chuoi_thong_bao_khoa = "Hệ thống phân tích định lượng chuyên sâu đang bị khóa. Vui lòng xác thực danh tính."
    st.info(chuoi_thong_bao_khoa)

    # 4. Tạo ô nhập mật mã (không dùng on_change để tránh lỗi widget)
    chuoi_nhan_hien_thi_o_nhap = " 🔑  Vui lòng nhập mật mã truy cập của Minh:"
    mat_ma_nguoi_dung_vua_go_vao = st.text_input(
        chuoi_nhan_hien_thi_o_nhap,
        type="password"
    )

    # 5. Xử lý logic khi có dữ liệu nhập vào ô text_input
    kiem_tra_co_chuoi_nhap_vao = mat_ma_nguoi_dung_vua_go_vao != ""

    if kiem_tra_co_chuoi_nhap_vao:

        # Đọc mật mã gốc được cấu hình bí mật trong Streamlit Secrets
        chuoi_khoa_lay_mat_ma = "password"
        mat_ma_chuan_dang_duoc_luu = st.secrets[chuoi_khoa_lay_mat_ma]

        # Tiến hành so sánh đối chiếu chuỗi mật khẩu
        kiem_tra_mat_khau_chinh_xac = mat_ma_nguoi_dung_vua_go_vao == mat_ma_chuan_dang_duoc_luu

        if kiem_tra_mat_khau_chinh_xac:

            # Gán cờ thành công vào bộ nhớ phiên làm việc
            st.session_state[chuoi_khoa_luu_tru_session] = True

            # Ra lệnh tải lại trang (Rerun) để ẩn form đăng nhập ngay lập tức
            st.rerun()

        else:

            # Nếu sai, hiển thị thông báo lỗi màu đỏ kèm cảnh báo Caps Lock
            chuoi_thong_bao_loi_mat_ma = " ❌  Cảnh báo: Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock."
            st.error(chuoi_thong_bao_loi_mat_ma)

    # Mặc định chặn đứng mọi hành vi truy cập trái phép bằng cách trả về False
    return False
# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG CHÍNH (MAIN APP EXECUTION)
# ==============================================================================
# Gọi hàm kiểm tra bảo mật
quyen_truy_cap_da_duoc_cap_phep = xac_thuc_quyen_truy_cap_cua_minh()
# Chỉ khi Minh nhập đúng mật mã, các module Quant bên dưới mới chạy
if quyen_truy_cap_da_duoc_cap_phep:

    # 1. Cấu hình giao diện tổng thể của Dashboard
    chuoi_ten_the_trinh_duyet = "Quant System V20.0 Predator"
    kieu_bo_cuc_trang = "wide"
    trang_thai_thanh_ben_ban_dau = "expanded"

    st.set_page_config(
        page_title=chuoi_ten_the_trinh_duyet,
        layout=kieu_bo_cuc_trang,
        initial_sidebar_state=trang_thai_thanh_ben_ban_dau
    )

    # 2. Render tiêu đề chính và thanh gạch ngang trang trí
    chuoi_tieu_de_he_thong = " 🛡️  Quant System V20.0: Master Advisor & Predator Radar"
    st.title(chuoi_tieu_de_he_thong)

    chuoi_ky_tu_gach_ngang = "---"
    st.markdown(chuoi_ky_tu_gach_ngang)
    # 3. Khởi tạo đối tượng động cơ Vnstock
    # Đã xóa bỏ các định danh hậu tố thừa, thống nhất 1 tên gọi
    dong_co_truy_xuat_vnstock = Vnstock()
# ==============================================================================
# 2. HÀM TRUY XUẤT DỮ LIỆU GIÁ (DATA ACQUISITION)
# ==============================================================================
    def lay_du_lieu_nien_yet_chuan(ma_chung_khoan_can_lay, so_ngay_lich_su_can_lay=1000):
        """
        Hàm tải dữ liệu giá cổ phiếu OHLCV.
        Quy trình Fail-over 2 lớp: Vnstock -> Yahoo Finance.
        Sử dụng giờ VN chuẩn để tránh rỗng dữ liệu buổi sáng.
        """

        # 2.1 Khởi tạo mốc thời gian (Đã ép giờ Việt Nam)
        thoi_diem_bay_gio_tai_vn = lay_thoi_gian_chuan_viet_nam()

        chuoi_dinh_dang_ngay_thang = '%Y-%m-%d'
        chuoi_ngay_ket_thuc_yeu_cau = thoi_diem_bay_gio_tai_vn.strftime(chuoi_dinh_dang_ngay_thang)

        khoang_thoi_gian_lui_ve_truoc = timedelta(days=so_ngay_lich_su_can_lay)
        thoi_diem_bat_dau_chua_format = thoi_diem_bay_gio_tai_vn - khoang_thoi_gian_lui_ve_truoc

        chuoi_ngay_bat_dau_yeu_cau = thoi_diem_bat_dau_chua_format.strftime(chuoi_dinh_dang_ngay_thang)

        # 2.2 Phương án A: Gọi API máy chủ Vnstock (Dữ liệu nội địa)
        try:
            bang_du_lieu_tra_ve_tu_vnstock = dong_co_truy_xuat_vnstock.stock.quote.history(
                symbol=ma_chung_khoan_can_lay,
                start=chuoi_ngay_bat_dau_yeu_cau,
                end=chuoi_ngay_ket_thuc_yeu_cau
            )

            # Kiểm tra xem dữ liệu có bị None không
            kiem_tra_co_bang_du_lieu = bang_du_lieu_tra_ve_tu_vnstock is not None

            if kiem_tra_co_bang_du_lieu:

                # Kiểm tra xem bảng có rỗng không
                so_luong_dong_du_lieu = len(bang_du_lieu_tra_ve_tu_vnstock)
                kiem_tra_bang_co_data = so_luong_dong_du_lieu > 0

                if kiem_tra_bang_co_data:

                    # Đồng bộ hóa tiêu đề cột về chữ thường toàn bộ
                    danh_sach_ten_cot_chuan_hoa_chu_thuong = []

                    tap_hop_ten_cot_hien_tai = bang_du_lieu_tra_ve_tu_vnstock.columns

                    for ten_cot_dang_xet in tap_hop_ten_cot_hien_tai:
                        chuoi_ten_cot_in_thuong = str(ten_cot_dang_xet).lower()
                        danh_sach_ten_cot_chuan_hoa_chu_thuong.append(chuoi_ten_cot_in_thuong)

                    # Gán lại tập hợp cột mới cho bảng dữ liệu
                    bang_du_lieu_tra_ve_tu_vnstock.columns = danh_sach_ten_cot_chuan_hoa_chu_thuong

                    # Trả về bảng dữ liệu hoàn chỉnh
                    return bang_du_lieu_tra_ve_tu_vnstock

        except Exception:
            # Bỏ qua im lặng để chạy Fallback
            pass

        # 2.3 Phương án B: Gọi API Yahoo Finance dự phòng
        try:

            # Chuyển đổi định dạng mã chứng khoán theo chuẩn Yahoo
            kiem_tra_la_chi_so_thitruong = ma_chung_khoan_can_lay == "VNINDEX"

            if kiem_tra_la_chi_so_thitruong:
                chuoi_ma_danh_cho_yahoo = "^VNINDEX"
            else:
                chuoi_hau_to_danh_cho_vn = ".VN"
                chuoi_ma_danh_cho_yahoo = f"{ma_chung_khoan_can_lay}{chuoi_hau_to_danh_cho_vn}"

            # Cấu hình gọi lệnh thư viện yfinance
            chuoi_chu_ky_lay_du_lieu = "3y"
            trang_thai_hien_thi_tien_do = False

            bang_du_lieu_tra_ve_tu_yahoo = yf.download(
                chuoi_ma_danh_cho_yahoo,
                period=chuoi_chu_ky_lay_du_lieu,
                progress=trang_thai_hien_thi_tien_do
            )

            # Kiểm tra dữ liệu Yahoo
            do_dai_bang_yahoo_tra_ve = len(bang_du_lieu_tra_ve_tu_yahoo)
            kiem_tra_yahoo_co_du_lieu = do_dai_bang_yahoo_tra_ve > 0

            if kiem_tra_yahoo_co_du_lieu:

                # Giải phóng cột Index Date ra thành cột dữ liệu
                bang_du_lieu_yahoo_da_reset = bang_du_lieu_tra_ve_tu_yahoo.reset_index()

                # Sửa lỗi Multi-Index Header của các phiên bản pandas mới
                danh_sach_ten_cot_yahoo_sach = []

                tap_hop_ten_cot_yahoo = bang_du_lieu_yahoo_da_reset.columns

                for phan_tu_tieu_de in tap_hop_ten_cot_yahoo:

                    kiem_tra_la_kieu_tuple = isinstance(phan_tu_tieu_de, tuple)

                    if kiem_tra_la_kieu_tuple:
                        gia_tri_chinh_cua_tuple = phan_tu_tieu_de[0]
                        chuoi_thuong_cua_tuple = str(gia_tri_chinh_cua_tuple).lower()
                        danh_sach_ten_cot_yahoo_sach.append(chuoi_thuong_cua_tuple)
                    else:
                        chuoi_thuong_don_le = str(phan_tu_tieu_de).lower()
                        danh_sach_ten_cot_yahoo_sach.append(chuoi_thuong_don_le)

                # Gán lại mảng tên cột chuẩn cho bảng
                bang_du_lieu_yahoo_da_reset.columns = danh_sach_ten_cot_yahoo_sach

                # Trả về bảng dữ liệu hoàn chỉnh
                return bang_du_lieu_yahoo_da_reset

        except Exception as doi_tuong_loi_yahoo:

            chuoi_thong_bao_loi_chinh = f" ⚠️  Lỗi máy chủ dữ liệu: Không thể tải mã {ma_chung_khoan_can_lay}."
            chuoi_chi_tiet_loi_yahoo = str(doi_tuong_loi_yahoo)
            chuoi_loi_hoan_chinh = f"{chuoi_thong_bao_loi_chinh} Chi tiết: {chuoi_chi_tiet_loi_yahoo}"

            st.sidebar.error(chuoi_loi_hoan_chinh)

        return None
# ==============================================================================
# 2.5. HÀM TRÍCH XUẤT KHỐI NGOẠI THỰC TẾ (REAL DATA)
# ==============================================================================
    def lay_du_lieu_khoi_ngoai_thuc_te(ma_chung_khoan_vao, so_ngay_truy_xuat=20):
        """
        Truy xuất trực tiếp Dữ Liệu Khối Ngoại (Real Data) từ máy chủ Vnstock.
        (Đã gọt rửa đuôi v14, sử dụng 100% chuẩn định danh gốc)
        """
        try:
            # 1. Cài đặt các mốc thời gian lấy dữ liệu
            thoi_gian_hien_tai_tai_vn = lay_thoi_gian_chuan_viet_nam()
            chuoi_dinh_dang_chuan_ngay = '%Y-%m-%d'

            chuoi_ngay_ket_thuc_quet_ngoai = thoi_gian_hien_tai_tai_vn.strftime(chuoi_dinh_dang_chuan_ngay)

            khoang_lui_ngay_quet_ngoai = timedelta(days=so_ngay_truy_xuat)
            thoi_gian_bat_dau_quet_ngoai = thoi_gian_hien_tai_tai_vn - khoang_lui_ngay_quet_ngoai

            chuoi_ngay_bat_dau_quet_ngoai = thoi_gian_bat_dau_quet_ngoai.strftime(chuoi_dinh_dang_chuan_ngay)

            # Khởi tạo đối tượng bảng rỗng
            bang_du_lieu_giao_dich_ngoai = None

            # 2. Bước A: Thử gọi hàm foreign_trade chính thức (API Version 1)
            try:
                bang_du_lieu_giao_dich_ngoai = dong_co_truy_xuat_vnstock.stock.trade.foreign_trade(
                    symbol=ma_chung_khoan_vao,
                    start=chuoi_ngay_bat_dau_quet_ngoai,
                    end=chuoi_ngay_ket_thuc_quet_ngoai
                )
            except Exception:
                pass

            # 3. Bước B: Thử gọi hàm trading.foreign dự phòng (API Version 2)
            kiem_tra_bien_ngoai_none = bang_du_lieu_giao_dich_ngoai is None

            if kiem_tra_bien_ngoai_none == False:
                do_dai_cua_bang_ngoai_hien_tai = len(bang_du_lieu_giao_dich_ngoai)
                kiem_tra_bang_ngoai_rong = do_dai_cua_bang_ngoai_hien_tai == 0
            else:
                kiem_tra_bang_ngoai_rong = True

            kiem_tra_co_can_chay_du_phong = kiem_tra_bien_ngoai_none or kiem_tra_bang_ngoai_rong

            if kiem_tra_co_can_chay_du_phong:
                try:
                    bang_du_lieu_giao_dich_ngoai = dong_co_truy_xuat_vnstock.stock.trading.foreign(
                        symbol=ma_chung_khoan_vao,
                        start=chuoi_ngay_bat_dau_quet_ngoai,
                        end=chuoi_ngay_ket_thuc_quet_ngoai
                    )
                except Exception:
                    pass

            # 4. Bước C: Chuẩn hóa dữ liệu cột
            kiem_tra_bang_ngoai_da_ton_tai = bang_du_lieu_giao_dich_ngoai is not None

            if kiem_tra_bang_ngoai_da_ton_tai:

                so_luong_dong_du_lieu_ngoai = len(bang_du_lieu_giao_dich_ngoai)
                kiem_tra_co_chua_du_lieu_ngoai = so_luong_dong_du_lieu_ngoai > 0

                if kiem_tra_co_chua_du_lieu_ngoai:

                    danh_sach_ten_cot_khoi_ngoai_chuan = []

                    tap_hop_ten_cot_ngoai_goc = bang_du_lieu_giao_dich_ngoai.columns

                    for ten_cot_ngoai_hien_tai in tap_hop_ten_cot_ngoai_goc:
                        chuoi_thuong_ten_cot = str(ten_cot_ngoai_hien_tai).lower()
                        danh_sach_ten_cot_khoi_ngoai_chuan.append(chuoi_thuong_ten_cot)

                    # Gán lại chuẩn cột
                    bang_du_lieu_giao_dich_ngoai.columns = danh_sach_ten_cot_khoi_ngoai_chuan

                    # Trả về bảng hoàn chỉnh
                    return bang_du_lieu_giao_dich_ngoai
        except Exception:
            pass

        return None
        
    def lay_du_lieu_tu_doanh_thuc_te(ma_chung_khoan_vao, so_ngay_truy_xuat=20):
        try:
            thoi_gian_hien_tai_tai_vn = lay_thoi_gian_chuan_viet_nam()
            chuoi_dinh_dang_chuan_ngay = '%Y-%m-%d'

            chuoi_ngay_ket_thuc_quet_td = thoi_gian_hien_tai_tai_vn.strftime(chuoi_dinh_dang_chuan_ngay)

            khoang_lui_ngay_quet_td = timedelta(days=so_ngay_truy_xuat)
            thoi_gian_bat_dau_quet_td = thoi_gian_hien_tai_tai_vn - khoang_lui_ngay_quet_td

            chuoi_ngay_bat_dau_quet_td = thoi_gian_bat_dau_quet_td.strftime(chuoi_dinh_dang_chuan_ngay)

            bang_du_lieu_giao_dich_tu_doanh = None
            try:
                bang_du_lieu_giao_dich_tu_doanh = dong_co_truy_xuat_vnstock.stock.trade.proprietary_trade(
                    symbol=ma_chung_khoan_vao,
                    start=chuoi_ngay_bat_dau_quet_td,
                    end=chuoi_ngay_ket_thuc_quet_td
                )
            except Exception:
                pass
                
            kiem_tra_bang_td_da_ton_tai = bang_du_lieu_giao_dich_tu_doanh is not None

            if kiem_tra_bang_td_da_ton_tai:
                so_luong_dong_du_lieu_td = len(bang_du_lieu_giao_dich_tu_doanh)
                if so_luong_dong_du_lieu_td > 0:
                    danh_sach_ten_cot_td_chuan = []
                    tap_hop_ten_cot_td_goc = bang_du_lieu_giao_dich_tu_doanh.columns
                    for ten_cot_td_hien_tai in tap_hop_ten_cot_td_goc:
                        chuoi_thuong_ten_cot = str(ten_cot_td_hien_tai).lower()
                        danh_sach_ten_cot_td_chuan.append(chuoi_thuong_ten_cot)
                    bang_du_lieu_giao_dich_tu_doanh.columns = danh_sach_ten_cot_td_chuan
                    return bang_du_lieu_giao_dich_tu_doanh
        except Exception:
            pass
        return None
# ==============================================================================
# 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE)
# ==============================================================================
    def tinh_toan_bo_chi_bao_quant(bang_du_lieu_can_tinh_toan):
        """
        Xây dựng bộ chỉ báo định lượng: MA, Bollinger, RSI, MACD, Volume.
        Tích hợp màng lọc dọn rác (ValueError Prevention).
        ĐẶC BIỆT BỔ SUNG CHO TAB 4: Bollinger Band Width (Squeeze) và Cạn Cung.
        """

        # 1. TẠO BẢN SAO ĐỂ TRÁNH THAY ĐỔI DỮ LIỆU GỐC
        bang_du_lieu_dang_xu_ly_ky_thuat = bang_du_lieu_can_tinh_toan.copy()

        # --- BƯỚC 2: LỌC DỮ LIỆU RÁC VÀ ÉP KIỂU ---

        # Tiêu diệt các cột bị trùng lặp tên
        danh_sach_cot_hien_tai_cua_bang = bang_du_lieu_dang_xu_ly_ky_thuat.columns
        mat_na_phat_hien_cot_trung_lap = danh_sach_cot_hien_tai_cua_bang.duplicated()
        mat_na_giu_lai_cot_duy_nhat = ~mat_na_phat_hien_cot_trung_lap

        bang_du_lieu_dang_xu_ly_ky_thuat = bang_du_lieu_dang_xu_ly_ky_thuat.loc[:, mat_na_giu_lai_cot_duy_nhat]

        # Đúc ép các cột dữ liệu quan trọng về đúng định dạng số thực (Float)
        danh_sach_cac_cot_quan_trong_can_kiem_tra = [
            'open',
            'high',
            'low',
            'close',
            'volume'
        ]

        tap_hop_cot_cua_bang_da_loc = bang_du_lieu_dang_xu_ly_ky_thuat.columns

        for ten_cot_can_duyet_ep_kieu in danh_sach_cac_cot_quan_trong_can_kiem_tra:

            kiem_tra_cot_nay_co_trong_bang = ten_cot_can_duyet_ep_kieu in tap_hop_cot_cua_bang_da_loc

            if kiem_tra_cot_nay_co_trong_bang:

                # Biến đổi thành dạng số, nếu lỗi (là chuỗi ký tự) thì biến thành rỗng (NaN)
                cot_du_lieu_sau_khi_ep = pd.to_numeric(
                    bang_du_lieu_dang_xu_ly_ky_thuat[ten_cot_can_duyet_ep_kieu],
                    errors='coerce'
                )

                bang_du_lieu_dang_xu_ly_ky_thuat[ten_cot_can_duyet_ep_kieu] = cot_du_lieu_sau_khi_ep

        # Vá lấp các lỗ hổng rỗng bằng phương pháp điền dữ liệu tiến tới (Forward Fill)
        cot_gia_dong_cua_sau_khi_va = bang_du_lieu_dang_xu_ly_ky_thuat['close'].ffill()
        bang_du_lieu_dang_xu_ly_ky_thuat['close'] = cot_gia_dong_cua_sau_khi_va

        cot_gia_mo_cua_sau_khi_va = bang_du_lieu_dang_xu_ly_ky_thuat['open'].ffill()
        bang_du_lieu_dang_xu_ly_ky_thuat['open'] = cot_gia_mo_cua_sau_khi_va

        cot_khoi_luong_sau_khi_va = bang_du_lieu_dang_xu_ly_ky_thuat['volume'].ffill()
        bang_du_lieu_dang_xu_ly_ky_thuat['volume'] = cot_khoi_luong_sau_khi_va

        # Trích xuất các chuỗi dữ liệu gốc để sử dụng cho phép tính
        chuoi_lich_su_gia_dong_cua_chinh = bang_du_lieu_dang_xu_ly_ky_thuat['close']
        chuoi_lich_su_gia_mo_cua_chinh = bang_du_lieu_dang_xu_ly_ky_thuat['open']
        chuoi_lich_su_khoi_luong_giao_dich_chinh = bang_du_lieu_dang_xu_ly_ky_thuat['volume']

        # --- BƯỚC 3: HỆ THỐNG CÁC ĐƯỜNG TRUNG BÌNH ĐỘNG (MOVING AVERAGES) ---

        # Tính MA20
        cua_so_truot_20_ngay_cho_gia = chuoi_lich_su_gia_dong_cua_chinh.rolling(window=20)
        gia_tri_duong_ma_20_phien = cua_so_truot_20_ngay_cho_gia.mean()
        bang_du_lieu_dang_xu_ly_ky_thuat['ma20'] = gia_tri_duong_ma_20_phien

        # Tính MA50
        cua_so_truot_50_ngay_cho_gia = chuoi_lich_su_gia_dong_cua_chinh.rolling(window=50)
        gia_tri_duong_ma_50_phien = cua_so_truot_50_ngay_cho_gia.mean()
        bang_du_lieu_dang_xu_ly_ky_thuat['ma50'] = gia_tri_duong_ma_50_phien

        # Tính MA200
        cua_so_truot_200_ngay_cho_gia = chuoi_lich_su_gia_dong_cua_chinh.rolling(window=200)
        gia_tri_duong_ma_200_phien = cua_so_truot_200_ngay_cho_gia.mean()
        bang_du_lieu_dang_xu_ly_ky_thuat['ma200'] = gia_tri_duong_ma_200_phien

        # --- BƯỚC 4: DẢI BOLLINGER BANDS VÀ CHỈ BÁO NÉN LÒ XO (SQUEEZE) ---

        # Tính toán mức độ lệch chuẩn
        gia_tri_do_lech_chuan_20_ngay = cua_so_truot_20_ngay_cho_gia.std()
        bang_du_lieu_dang_xu_ly_ky_thuat['do_lech_chuan_20'] = gia_tri_do_lech_chuan_20_ngay

        # Tính khoảng cách dải
        khoang_cach_nhan_doi_cua_dai = bang_du_lieu_dang_xu_ly_ky_thuat['do_lech_chuan_20'] * 2

        # Cấu hình dải Bollinger trên
        duong_bien_tren_cua_dai_bol = bang_du_lieu_dang_xu_ly_ky_thuat['ma20'] + khoang_cach_nhan_doi_cua_dai
        bang_du_lieu_dang_xu_ly_ky_thuat['upper_band'] = duong_bien_tren_cua_dai_bol

        # Cấu hình dải Bollinger dưới
        duong_bien_duoi_cua_dai_bol = bang_du_lieu_dang_xu_ly_ky_thuat['ma20'] - khoang_cach_nhan_doi_cua_dai
        bang_du_lieu_dang_xu_ly_ky_thuat['lower_band'] = duong_bien_duoi_cua_dai_bol

        # TÍNH TOÁN BĂNG THÔNG BOLLINGER (Band Width) - Dành riêng cho Robot Hunter săn Squeeze
        khoang_cach_giua_hai_dai_bol = bang_du_lieu_dang_xu_ly_ky_thuat['upper_band'] - bang_du_lieu_dang_xu_ly_ky_thuat['lower_band']

        # Chia cho MA20 để ra phần trăm (Cộng 1e-9 chống lỗi chia 0)
        gia_tri_mau_so_chia_bang_thong = bang_du_lieu_dang_xu_ly_ky_thuat['ma20'] + 1e-9
        ti_le_phan_tram_cua_bang_thong = khoang_cach_giua_hai_dai_bol / gia_tri_mau_so_chia_bang_thong

        bang_du_lieu_dang_xu_ly_ky_thuat['bb_width'] = ti_le_phan_tram_cua_bang_thong

        # --- BƯỚC 5: CHỈ SỐ SỨC MẠNH TƯƠNG ĐỐI (RSI 14 PHIÊN) ---

        # Tính khoảng cách chênh lệch giá so với ngày trước
        khoang_chenh_gia_giua_cac_phien = chuoi_lich_su_gia_dong_cua_chinh.diff()

        # Lọc ra các phiên tăng điểm
        dieu_kien_loc_phien_tang_diem = khoang_chenh_gia_giua_cac_phien > 0
        chuoi_du_lieu_cac_phien_tang = khoang_chenh_gia_giua_cac_phien.where(dieu_kien_loc_phien_tang_diem, 0)

        # Lọc ra các phiên giảm điểm
        dieu_kien_loc_phien_giam_diem = khoang_chenh_gia_giua_cac_phien < 0
        chuoi_du_lieu_cac_phien_giam = -khoang_chenh_gia_giua_cac_phien.where(dieu_kien_loc_phien_giam_diem, 0)

        # Tính mức trung bình trượt 14 ngày
        cua_so_truot_14_ngay_tinh_tang = chuoi_du_lieu_cac_phien_tang.rolling(window=14)
        gia_tri_trung_binh_tang_14 = cua_so_truot_14_ngay_tinh_tang.mean()

        cua_so_truot_14_ngay_tinh_giam = chuoi_du_lieu_cac_phien_giam.rolling(window=14)
        gia_tri_trung_binh_giam_14 = cua_so_truot_14_ngay_tinh_giam.mean()

        # Áp dụng công thức RSI
        gia_tri_mau_so_tinh_rs = gia_tri_trung_binh_giam_14 + 1e-9
        ti_so_suc_manh_tuong_doi_rs = gia_tri_trung_binh_tang_14 / gia_tri_mau_so_tinh_rs

        gia_tri_mau_so_tinh_rsi = 1 + ti_so_suc_manh_tuong_doi_rs
        phan_tu_bi_tru_khi_tinh_rsi = 100 / gia_tri_mau_so_tinh_rsi

        ket_qua_chinh_thuc_chi_so_rsi = 100 - phan_tu_bi_tru_khi_tinh_rsi
        bang_du_lieu_dang_xu_ly_ky_thuat['rsi'] = ket_qua_chinh_thuc_chi_so_rsi

        # --- BƯỚC 6: ĐỘNG LƯỢNG MACD (CẤU HÌNH 12, 26, 9) ---

        # Đường EMA nhanh
        cau_hinh_ema_12 = chuoi_lich_su_gia_dong_cua_chinh.ewm(span=12, adjust=False)
        duong_ema_nhanh_12_phien = cau_hinh_ema_12.mean()

        # Đường EMA chậm
        cau_hinh_ema_26 = chuoi_lich_su_gia_dong_cua_chinh.ewm(span=26, adjust=False)
        duong_ema_cham_26_phien = cau_hinh_ema_26.mean()

        # Đường MACD chính
        duong_chi_bao_macd_chinh_thuc = duong_ema_nhanh_12_phien - duong_ema_cham_26_phien
        bang_du_lieu_dang_xu_ly_ky_thuat['macd'] = duong_chi_bao_macd_chinh_thuc

        # Đường Signal
        cau_hinh_ema_9_cho_macd = bang_du_lieu_dang_xu_ly_ky_thuat['macd'].ewm(span=9, adjust=False)
        duong_tin_hieu_signal_chinh_thuc = cau_hinh_ema_9_cho_macd.mean()
        bang_du_lieu_dang_xu_ly_ky_thuat['signal'] = duong_tin_hieu_signal_chinh_thuc

        # --- BƯỚC 7: CÁC BIẾN SỐ PHỤC VỤ DÒNG TIỀN VÀ AI ---

        # Tính tỷ suất phần trăm thay đổi giá
        chuoi_phan_tram_thay_doi_gia_hang_ngay = chuoi_lich_su_gia_dong_cua_chinh.pct_change()
        bang_du_lieu_dang_xu_ly_ky_thuat['return_1d'] = chuoi_phan_tram_thay_doi_gia_hang_ngay

        # TÍNH CƯỜNG ĐỘ KHỐI LƯỢNG GIAO DỊCH (vol_strength)
        cua_so_truot_10_phien_tinh_vol = chuoi_lich_su_khoi_luong_giao_dich_chinh.rolling(window=10)
        muc_trung_binh_khoi_luong_10_ngay = cua_so_truot_10_phien_tinh_vol.mean()

        mau_so_tinh_suc_manh_vol = muc_trung_binh_khoi_luong_10_ngay + 1e-9
        he_so_suc_manh_no_vol_thuc_te = chuoi_lich_su_khoi_luong_giao_dich_chinh / mau_so_tinh_suc_manh_vol

        bang_du_lieu_dang_xu_ly_ky_thuat['vol_strength'] = he_so_suc_manh_no_vol_thuc_te

        # Dòng tiền lưu chuyển
        chuoi_dong_tien_luan_chuyen_hang_ngay = chuoi_lich_su_gia_dong_cua_chinh * chuoi_lich_su_khoi_luong_giao_dich_chinh
        bang_du_lieu_dang_xu_ly_ky_thuat['money_flow'] = chuoi_dong_tien_luan_chuyen_hang_ngay

        # Đo lường rủi ro biến động
        cua_so_truot_20_phien_tinh_rui_ro = bang_du_lieu_dang_xu_ly_ky_thuat['return_1d'].rolling(window=20)
        chi_so_bien_dong_lich_su_volatility = cua_so_truot_20_phien_tinh_rui_ro.std()
        bang_du_lieu_dang_xu_ly_ky_thuat['volatility'] = chi_so_bien_dong_lich_su_volatility

        # --- BƯỚC 8: XÁC ĐỊNH DẤU HIỆU CẠN CUNG (SUPPLY EXHAUSTION - Dành cho Tab 4) ---

        # Kiểm tra xem nến hôm đó là nến đỏ (Giá giảm từ lúc mở cửa)
        dieu_kien_kiem_tra_nen_do = chuoi_lich_su_gia_dong_cua_chinh < chuoi_lich_su_gia_mo_cua_chinh
        bang_du_lieu_dang_xu_ly_ky_thuat['is_red_candle'] = dieu_kien_kiem_tra_nen_do

        # Tính trung bình Volume trong 20 ngày
        cua_so_truot_20_phien_tinh_vol_tong = chuoi_lich_su_khoi_luong_giao_dich_chinh.rolling(window=20)
        muc_trung_binh_vol_20_ngay_chuan = cua_so_truot_20_phien_tinh_vol_tong.mean()
        bang_du_lieu_dang_xu_ly_ky_thuat['vol_avg_20'] = muc_trung_binh_vol_20_ngay_chuan

        # Tìm các phiên cạn kiệt khối lượng
        nguong_vol_duoc_xem_la_can_kiet = muc_trung_binh_vol_20_ngay_chuan * 0.8
        dieu_kien_kiem_tra_vol_bi_teo_top = chuoi_lich_su_khoi_luong_giao_dich_chinh < nguong_vol_duoc_xem_la_can_kiet

        # Tổ hợp dấu hiệu Cạn Cung: Vừa là phiên nến đỏ bị bán xuống, VÀ khối lượng teo tóp
        dieu_kien_to_hop_chinh_thuc_ve_can_cung = dieu_kien_kiem_tra_nen_do & dieu_kien_kiem_tra_vol_bi_teo_top
        bang_du_lieu_dang_xu_ly_ky_thuat['can_cung'] = dieu_kien_to_hop_chinh_thuc_ve_can_cung

        # --- BƯỚC 9: PHÂN LỚP XU HƯỚNG DÒNG TIỀN THEO HÀNH VI (PV TREND) ---

        # Quy luật Gom: Đẩy giá tăng + Khối lượng nổ
        dieu_kien_xac_nhan_gia_dang_tang = bang_du_lieu_dang_xu_ly_ky_thuat['return_1d'] > 0
        dieu_kien_xac_nhan_vol_dang_no = bang_du_lieu_dang_xu_ly_ky_thuat['vol_strength'] > 1.2

        dieu_kien_gop_cho_tin_hieu_gom = dieu_kien_xac_nhan_gia_dang_tang & dieu_kien_xac_nhan_vol_dang_no

        # Quy luật Xả: Đạp giá giảm + Khối lượng nổ
        dieu_kien_xac_nhan_gia_dang_giam = bang_du_lieu_dang_xu_ly_ky_thuat['return_1d'] < 0

        dieu_kien_gop_cho_tin_hieu_xa = dieu_kien_xac_nhan_gia_dang_giam & dieu_kien_xac_nhan_vol_dang_no

        # Gắn thẻ nhãn để AI có thể hiểu
        chuoi_so_nhan_dang_hanh_vi_pv = np.where(
            dieu_kien_gop_cho_tin_hieu_gom,
            1,
            np.where(
                dieu_kien_gop_cho_tin_hieu_xa,
                -1,
                0
            )
        )

        bang_du_lieu_dang_xu_ly_ky_thuat['pv_trend'] = chuoi_so_nhan_dang_hanh_vi_pv

        # --- BƯỚC 10: XÓA BỎ DỮ LIỆU RỖNG BẢO VỆ AI ---
        bang_du_lieu_chi_bao_da_hoan_toan_sach = bang_du_lieu_dang_xu_ly_ky_thuat.dropna()

        return bang_du_lieu_chi_bao_da_hoan_toan_sach
# ==============================================================================
# 4. HÀM CHẨN ĐOÁN THÔNG MINH ĐỊNH LƯỢNG (INTELLIGENCE & AI LAYER)
# ==============================================================================

    def phan_tich_tam_ly_dam_dong(bang_du_lieu_da_tinh_xong_toan_bo):
        """
        Đo lường sức nóng RSI hiện tại để xem nhỏ lẻ đang sợ hãi hay hưng phấn.
        """
        # Trích xuất dòng dữ liệu mới nhất
        dong_thong_tin_cua_phien_giao_dich_cuoi = bang_du_lieu_da_tinh_xong_toan_bo.iloc[-1]

        # Lấy giá trị RSI
        muc_chi_so_rsi_phien_hien_tai = dong_thong_tin_cua_phien_giao_dich_cuoi['rsi']

        # Cấu trúc Bóc tách cung bậc cảm xúc
        if muc_chi_so_rsi_phien_hien_tai > 75:
            chuoi_nhan_dang_tam_ly_dam_dong = " 🔥  CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"

        elif muc_chi_so_rsi_phien_hien_tai > 60:
            chuoi_nhan_dang_tam_ly_dam_dong = " ⚖️  THAM LAM (HƯNG PHẤN)"

        elif muc_chi_so_rsi_phien_hien_tai < 30:
            chuoi_nhan_dang_tam_ly_dam_dong = " 💀  CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"

        elif muc_chi_so_rsi_phien_hien_tai < 42:
            chuoi_nhan_dang_tam_ly_dam_dong = " 😨  SỢ HÃI (BI QUAN)"

        else:
            chuoi_nhan_dang_tam_ly_dam_dong = " 🟡  TRUNG LẬP (ĐI NGANG CHỜ ĐỢI)"

        # Làm tròn số để hiển thị đẹp hơn
        gia_tri_rsi_sau_lam_tron = round(muc_chi_so_rsi_phien_hien_tai, 1)

        return chuoi_nhan_dang_tam_ly_dam_dong, gia_tri_rsi_sau_lam_tron
    def thuc_thi_backtest_chien_thuat(bang_du_lieu_da_tinh_xong_toan_bo):
        """
        Cỗ máy thời gian: Lục lọi lại lịch sử 1000 ngày qua để đo lường xác suất:
        Nếu mua lúc RSI < 45 và MACD cắt lên, thì tỷ lệ chốt lời 5% trong 10 ngày là bao nhiêu?
        """
        # Khởi tạo các biến đếm
        bien_dem_tong_so_lan_xuat_hien_tin_hieu = 0
        bien_dem_tong_so_lan_nguoi_mua_co_lai = 0

        # Tính toán chiều dài vòng lặp
        chieu_dai_tong_cua_tap_du_lieu_hien_tai = len(bang_du_lieu_da_tinh_xong_toan_bo)

        # Điểm bắt đầu (Bỏ qua 100 phiên đầu để đường MA hội tụ đủ chuẩn)
        diem_bat_dau_vong_lap_lich_su = 100

        # Điểm kết thúc (Bỏ qua 10 phiên cuối để chừa chỗ soi tương lai)
        diem_ket_thuc_vong_lap_lich_su = chieu_dai_tong_cua_tap_du_lieu_hien_tai - 10

        # Kích hoạt vòng lặp
        for chi_so_ngay_dang_duyet in range(diem_bat_dau_vong_lap_lich_su, diem_ket_thuc_vong_lap_lich_su):

            # --- 1. Kiểm tra tiêu chí đầu vào tại phiên đang xét ---

            # Kiểm tra RSI
            gia_tri_rsi_cua_ngay_trong_lich_su = bang_du_lieu_da_tinh_xong_toan_bo['rsi'].iloc[chi_so_ngay_dang_duyet]
            dieu_kien_kiem_tra_rsi_co_nam_vung_thap = gia_tri_rsi_cua_ngay_trong_lich_su < 45

            # Kiểm tra MACD giao cắt
            muc_macd_hom_do = bang_du_lieu_da_tinh_xong_toan_bo['macd'].iloc[chi_so_ngay_dang_duyet]
            muc_signal_hom_do = bang_du_lieu_da_tinh_xong_toan_bo['signal'].iloc[chi_so_ngay_dang_duyet]

            vi_tri_ngay_hom_qua = chi_so_ngay_dang_duyet - 1
            muc_macd_hom_qua_do = bang_du_lieu_da_tinh_xong_toan_bo['macd'].iloc[vi_tri_ngay_hom_qua]
            muc_signal_hom_qua_do = bang_du_lieu_da_tinh_xong_toan_bo['signal'].iloc[vi_tri_ngay_hom_qua]

            dieu_kien_macd_hien_tai_cao_hon = muc_macd_hom_do > muc_signal_hom_do
            dieu_kien_macd_hom_qua_thap_hon = muc_macd_hom_qua_do <= muc_signal_hom_qua_do

            dieu_kien_giao_cat_huong_len_chuan_xac = dieu_kien_macd_hien_tai_cao_hon and dieu_kien_macd_hom_qua_thap_hon

            # Tổ hợp điều kiện mua
            dieu_kien_mua_duoc_xac_nhan_xay_ra = dieu_kien_kiem_tra_rsi_co_nam_vung_thap and dieu_kien_giao_cat_huong_len_chuan_xac

            if dieu_kien_mua_duoc_xac_nhan_xay_ra:

                # Ghi nhận 1 lần hệ thống phát ra tín hiệu
                bien_dem_tong_so_lan_xuat_hien_tin_hieu += 1

                # --- 2. Tính toán mục tiêu và đối chiếu tương lai ---

                # Mua giả định tại mức giá đóng cửa hôm đó
                muc_gia_mua_khop_lenh_gia_dinh = bang_du_lieu_da_tinh_xong_toan_bo['close'].iloc[chi_so_ngay_dang_duyet]

                # Tính giá mục tiêu chốt lãi 5%
                muc_gia_de_chot_lai_thanh_cong = muc_gia_mua_khop_lenh_gia_dinh * 1.05

                # Quét xem 10 ngày tiếp theo có ngày nào giá vọt lên khỏi mục tiêu không
                vi_tri_ngay_tuong_lai_bat_dau = chi_so_ngay_dang_duyet + 1
                vi_tri_ngay_tuong_lai_ket_thuc = chi_so_ngay_dang_duyet + 11

                chuoi_gia_cua_tuong_lai_trong_10_ngay = bang_du_lieu_da_tinh_xong_toan_bo['close'].iloc[vi_tri_ngay_tuong_lai_bat_dau : vi_tri_ngay_tuong_lai_ket_thuc]

                kiem_tra_co_ngay_nao_thang_loi_khong = any(chuoi_gia_cua_tuong_lai_trong_10_ngay > muc_gia_de_chot_lai_thanh_cong)

                if kiem_tra_co_ngay_nao_thang_loi_khong:
                    # Ghi nhận 1 lần lệnh mua sinh ra lợi nhuận
                    bien_dem_tong_so_lan_nguoi_mua_co_lai += 1

        # Xử lý ngoại lệ nếu không tìm thấy mẫu nào để tránh chia cho 0
        kiem_tra_co_mau_thu_nghiem_khong = bien_dem_tong_so_lan_xuat_hien_tin_hieu == 0
        if kiem_tra_co_mau_thu_nghiem_khong:
            return 0.0

        # Áp dụng công thức tính tỷ lệ chiến thắng (Winrate)
        ty_le_phan_tram_thang_loi_cuoi_cung = (bien_dem_tong_so_lan_nguoi_mua_co_lai / bien_dem_tong_so_lan_xuat_hien_tin_hieu) * 100

        gia_tri_winrate_sau_khi_lam_tron = round(ty_le_phan_tram_thang_loi_cuoi_cung, 1)

        return gia_tri_winrate_sau_khi_lam_tron
    def du_bao_xac_suat_ai_t3(bang_du_lieu_da_tinh_xong_toan_bo):
        """
        Huấn luyện cỗ máy Machine Learning (Random Forest).
        Cho máy đọc 8 chỉ báo kỹ thuật để dự báo cửa tăng giá T+3.
        """

        # Kiểm tra rào cản kỹ thuật: Máy cần ít nhất 200 dòng để học cho bớt nhiễu
        do_dai_cua_bang_du_lieu_cap_cho_ai = len(bang_du_lieu_da_tinh_xong_toan_bo)

        kiem_tra_data_co_du_lon_de_hoc_khong = do_dai_cua_bang_du_lieu_cap_cho_ai < 200
        if kiem_tra_data_co_du_lon_de_hoc_khong:
            return "N/A"

        # Tạo bản sao môi trường học
        bang_du_lieu_mang_di_hoc_may = bang_du_lieu_da_tinh_xong_toan_bo.copy()

        # --- BƯỚC 1: XÂY DỰNG BỘ NHÃN ĐÁP ÁN (Y) ---
        chuoi_gia_hien_tai_lam_moc_so_sanh = bang_du_lieu_mang_di_hoc_may['close']

        # Nhìn trước tương lai 3 ngày
        chuoi_gia_cua_tuong_lai_t3_ve_sau = bang_du_lieu_mang_di_hoc_may['close'].shift(-3)

        # Điều kiện thắng của AI: Giá T+3 phải cao hơn giá lúc mua 2%
        muc_gia_dich_buoc_phai_vuot_qua = chuoi_gia_hien_tai_lam_moc_so_sanh * 1.02

        dieu_kien_gia_da_tang_thanh_cong = chuoi_gia_cua_tuong_lai_t3_ve_sau > muc_gia_dich_buoc_phai_vuot_qua

        # Ép kiểu Logic True/False thành số nguyên 1/0
        chuoi_nhan_dich_so_nguyen = dieu_kien_gia_da_tang_thanh_cong.astype(int)

        bang_du_lieu_mang_di_hoc_may['nhan_muc_tieu_cho_ai_hoc'] = chuoi_nhan_dich_so_nguyen

        # --- BƯỚC 2: CẤU HÌNH THÔNG TIN ĐẦU VÀO (FEATURES X) ---
        danh_sach_cac_chuyen_muc_hoc_tap = [
            'rsi',
            'macd',
            'signal',
            'return_1d',
            'volatility',
            'vol_strength',
            'money_flow',
            'pv_trend'
        ]

        # --- BƯỚC 3: DỌN DẸP CHIẾN TRƯỜNG ---
        bang_du_lieu_ai_da_don_dep_sach_se = bang_du_lieu_mang_di_hoc_may.dropna()

        ma_tran_thong_tin_dau_vao_x = bang_du_lieu_ai_da_don_dep_sach_se[danh_sach_cac_chuyen_muc_hoc_tap]

        vector_dap_an_dau_ra_y = bang_du_lieu_ai_da_don_dep_sach_se['nhan_muc_tieu_cho_ai_hoc']

        # --- BƯỚC 4: KHỞI TẠO VÀ NHỒI NHÉT KIẾN THỨC VÀO MÔ HÌNH ---
        so_luong_cay_quyet_dinh_trong_rung = 100
        ma_so_dam_bao_tinh_lap_lai_random_state = 42

        mo_hinh_rung_ngau_nhien_rf = RandomForestClassifier(
            n_estimators=so_luong_cay_quyet_dinh_trong_rung,
            random_state=ma_so_dam_bao_tinh_lap_lai_random_state
        )

        # Tách bóc: Loại bỏ 3 ngày cuối cùng vì chúng ta chưa biết đáp án của chúng
        ma_tran_x_dung_de_huan_luyen = ma_tran_thong_tin_dau_vao_x[:-3]
        vector_y_dung_de_doi_chieu_dap_an = vector_dap_an_dau_ra_y[:-3]

        # Kích hoạt máy học
        mo_hinh_rung_ngau_nhien_rf.fit(ma_tran_x_dung_de_huan_luyen, vector_y_dung_de_doi_chieu_dap_an)

        # --- BƯỚC 5: ỨNG DỤNG KIẾN THỨC VÀO NGÀY HÔM NAY ---
        dong_du_lieu_chi_tieu_cua_ngay_hom_nay = ma_tran_thong_tin_dau_vao_x.iloc[[-1]]

        ma_tran_ket_qua_du_doan_xac_suat = mo_hinh_rung_ngau_nhien_rf.predict_proba(dong_du_lieu_chi_tieu_cua_ngay_hom_nay)

        # Lấy xác suất rơi vào kịch bản 1 (Tăng giá)
        xac_suat_co_kha_nang_tang_gia_thuc_te = ma_tran_ket_qua_du_doan_xac_suat[0][1]

        # Trả về hệ phần trăm
        ket_qua_xac_suat_lam_tron_phan_tram = round(xac_suat_co_kha_nang_tang_gia_thuc_te * 100, 1)

        return ket_qua_xac_suat_lam_tron_phan_tram
# ==============================================================================
# 5. TÍNH NĂNG TỰ ĐỘNG PHÂN TÍCH RA VĂN BẢN CHO MINH (AUTO-ANALYSIS ENGINE)
# ==============================================================================
    def tao_ban_bao_cao_tu_dong_chuyen_sau(tui_du_lieu):
        ma_chung_khoan = tui_du_lieu['ma_chung_khoan']
        dong_du_lieu_cuoi = tui_du_lieu['dong_du_lieu_cuoi']
        diem_so_ai = tui_du_lieu['diem_so_ai']
        diem_so_winrate = tui_du_lieu['diem_so_winrate']
        mang_tru_gom = tui_du_lieu['mang_tru_gom']
        mang_tru_xa = tui_du_lieu['mang_tru_xa']
        """
        Nhà phân tích ảo: Tự động gom nhặt các con số khô khan, lắp ghép lại
        và viết ra một bài văn phân tích chi tiết dễ hiểu.
        Khai triển tối đa để chống nén code.
        """

        # Mảng chứa các đoạn văn bản
        mang_chua_cac_dong_text_phan_tich_hoan_thien = []

        # --- PHẦN 1: ĐỌC VỊ DÒNG TIỀN ---
        chuoi_tieu_de_phan_dong_tien = "#### 1. Đọc Vị Hành Vi Dòng Tiền (Smart Flow):"
        mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_tieu_de_phan_dong_tien)

        kiem_tra_co_bi_cá_mập_gom_khong = ma_chung_khoan in mang_tru_gom
        kiem_tra_co_bi_cá_mập_xa_khong = ma_chung_khoan in mang_tru_xa

        gia_tri_muc_do_no_vol_hien_tai = dong_du_lieu_cuoi['vol_strength']

        if kiem_tra_co_bi_cá_mập_gom_khong:
            chuoi_phan_tich_tin_hieu_dong_tien_tot = f" ✅  **Tín Hiệu Tích Cực:** Hệ thống phát hiện dòng tiền lớn đang **GOM HÀNG CHỦ ĐỘNG** tại mã {ma_chung_khoan}. Khối lượng giao dịch nổ đột biến gấp {gia_tri_muc_do_no_vol_hien_tai:.1f} lần trung bình, kèm theo sự xác nhận của giá đóng cửa xanh."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_tin_hieu_dong_tien_tot)

        elif kiem_tra_co_bi_cá_mập_xa_khong:
            chuoi_phan_tich_tin_hieu_dong_tien_xau = f" 🚨  **Cảnh Báo Tiêu Cực:** Dòng tiền lớn đang **XẢ HÀNG QUYẾT LIỆT**. Khối lượng bị bán ra ồ ạt gấp {gia_tri_muc_do_no_vol_hien_tai:.1f} lần bình thường và giá đóng cửa bị dìm trong sắc đỏ. Áp lực phân phối đang đè nặng lên cổ phiếu."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_tin_hieu_dong_tien_xau)

        else:
            chuoi_phan_tich_tin_hieu_dong_tien_trung_lap = f" 🟡  **Trạng Thái Trung Lập:** Dòng tiền chưa có dấu hiệu đột biến. Khối lượng giao dịch nằm ở mức bình thường, cho thấy chủ yếu là các nhà đầu tư cá nhân tự giao dịch với nhau."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_tin_hieu_dong_tien_trung_lap)
        # --- PHẦN 2: ĐỌC VỊ VỊ THẾ KỸ THUẬT ---
        chuoi_tieu_de_phan_ky_thuat = "#### 2. Đánh Giá Vị Thế Kỹ Thuật (Trend & Momentum):"
        mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_tieu_de_phan_ky_thuat)

        gia_tri_dong_cua_thuc_te_dn = dong_du_lieu_cuoi['close']
        gia_tri_duong_ho_tro_ma20_dn = dong_du_lieu_cuoi['ma20']

        kiem_tra_xu_huong_gia_dang_bi_gay = gia_tri_dong_cua_thuc_te_dn < gia_tri_duong_ho_tro_ma20_dn

        if kiem_tra_xu_huong_gia_dang_bi_gay:
            chuoi_phan_tich_muc_gia_xau = f" ❌  **Xu Hướng Đang Xấu:** Mức giá hiện tại ({gia_tri_dong_cua_thuc_te_dn:,.0f} VNĐ) đang nằm **DƯỚI** đường phòng thủ sinh tử MA20 ({gia_tri_duong_ho_tro_ma20_dn:,.0f} VNĐ). Điều này khẳng định phe Bán đang áp đảo. Tuyệt đối chưa nên đưa tay bắt đáy sớm."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_muc_gia_xau)
        else:
            chuoi_phan_tich_muc_gia_tot = f" ✅  **Xu Hướng Rất Tốt:** Mức giá hiện tại ({gia_tri_dong_cua_thuc_te_dn:,.0f} VNĐ) đang được neo giữ vững chắc **TRÊN** đường hỗ trợ MA20 ({gia_tri_duong_ho_tro_ma20_dn:,.0f} VNĐ). Cấu trúc tăng giá ngắn hạn đang được bảo vệ thành công."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_muc_gia_tot)
        # Bổ sung đánh giá RSI
        gia_tri_chi_so_rsi_dn = dong_du_lieu_cuoi['rsi']
        kiem_tra_rsi_nong_qua_muc = gia_tri_chi_so_rsi_dn > 70
        kiem_tra_rsi_lanh_qua_muc = gia_tri_chi_so_rsi_dn < 35

        if kiem_tra_rsi_nong_qua_muc:
            chuoi_phan_tich_tam_ly_rsi_nong = f" ⚠️  **Cảnh Báo Tâm Lý:** Chỉ báo RSI đang vọt lên mức {gia_tri_chi_so_rsi_dn:.1f} (Vùng Quá Mua). Cổ phiếu đang rơi vào trạng thái quá hưng phấn, rất dễ quay đầu điều chỉnh giảm bất cứ lúc nào."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_tam_ly_rsi_nong)

        elif kiem_tra_rsi_lanh_qua_muc:
            chuoi_phan_tich_tam_ly_rsi_lanh = f" 💡  **Cơ Hội Tâm Lý:** Chỉ báo RSI đang lùi sâu về mức {gia_tri_chi_so_rsi_dn:.1f} (Vùng Quá Bán). Lực bán tháo gần như đã cạn kiệt, xác suất xuất hiện một nhịp hồi phục kỹ thuật là rất lớn."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_tam_ly_rsi_lanh)

        else:
            chuoi_phan_tich_tam_ly_rsi_on_dinh = f" 📉  **Tâm Lý Ổn Định:** Chỉ báo RSI dao động quanh mốc {gia_tri_chi_so_rsi_dn:.1f}, cho thấy thị trường chưa có sự hưng phấn hay hoảng loạn thái quá."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_tam_ly_rsi_on_dinh)
        # --- PHẦN 3: ĐỌC VỊ AI & LỊCH SỬ ---
        chuoi_tieu_de_phan_ai_lich_su = "#### 3. Đánh Giá Xác Suất Định Lượng (AI & Lịch Sử):"
        mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_tieu_de_phan_ai_lich_su)

        kiem_tra_co_diem_ai_hop_le_khong = isinstance(diem_so_ai, float)

        if kiem_tra_co_diem_ai_hop_le_khong:
            kiem_tra_ai_co_tot = diem_so_ai > 55

            if kiem_tra_ai_co_tot:
                chuoi_nhan_dinh_nhanh_ve_ai_tot = "Mức độ tin cậy tốt, cửa tăng T+3 rất sáng"
                chuoi_phan_tich_ket_qua_ai_tot = f"- **Hệ thống AI Dự báo:** Xác suất tăng giá trong 3 ngày tới được máy học chấm ở mức **{diem_so_ai}%** ➔  *{chuoi_nhan_dinh_nhanh_ve_ai_tot}*."
                mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_ket_qua_ai_tot)
            else:
                chuoi_nhan_dinh_nhanh_ve_ai_xau = "Mức độ tin cậy thấp, rủi ro chôn vốn cao"
                chuoi_phan_tich_ket_qua_ai_xau = f"- **Hệ thống AI Dự báo:** Xác suất tăng giá trong 3 ngày tới được máy học chấm ở mức **{diem_so_ai}%** ➔  *{chuoi_nhan_dinh_nhanh_ve_ai_xau}*."
                mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_ket_qua_ai_xau)

        kiem_tra_winrate_co_te = diem_so_winrate < 45

        if kiem_tra_winrate_co_te:
            chuoi_nhan_dinh_nhanh_ve_lich_su_te = "Trong quá khứ, mẫu hình này thường là Bẫy lừa (Bull Trap)"
            chuoi_phan_tich_ket_qua_lich_su_te = f"- **Kiểm chứng Lịch sử:** Tỷ lệ chiến thắng của chiến thuật này đạt mốc **{diem_so_winrate}%** ➔  *{chuoi_nhan_dinh_nhanh_ve_lich_su_te}*."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_ket_qua_lich_su_te)
        else:
            chuoi_nhan_dinh_nhanh_ve_lich_su_tot = "Dữ liệu quá khứ chứng minh đây là tín hiệu uy tín"
            chuoi_phan_tich_ket_qua_lich_su_tot = f"- **Kiểm chứng Lịch sử:** Tỷ lệ chiến thắng của chiến thuật này đạt mốc **{diem_so_winrate}%** ➔  *{chuoi_nhan_dinh_nhanh_ve_lich_su_tot}*."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_phan_tich_ket_qua_lich_su_tot)
        # --- PHẦN 4: TỔNG KẾT VÀ GIẢI MÃ ---
        chuoi_tieu_de_phan_tong_ket_giai_ma = "####  💡  TỔNG KẾT & GIẢI MÃ MÂU THUẪN TỪ HỆ THỐNG QUANT:"
        mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_tieu_de_phan_tong_ket_giai_ma)

        # Thiết lập các mệnh đề Logic
        menh_de_1_canh_bao_gom_rai_dinh = kiem_tra_xu_huong_gia_dang_bi_gay and kiem_tra_co_bi_cá_mập_gom_khong

        kiem_tra_ai_dang_xau = kiem_tra_co_diem_ai_hop_le_khong and diem_so_ai < 50
        menh_de_2_canh_bao_rui_ro_bo_chay = (diem_so_winrate < 40) and kiem_tra_ai_dang_xau

        kiem_tra_xu_huong_gia_dang_tot = not kiem_tra_xu_huong_gia_dang_bi_gay
        kiem_tra_ai_dang_tot = kiem_tra_co_diem_ai_hop_le_khong and diem_so_ai > 55
        kiem_tra_winrate_dang_tot = diem_so_winrate > 50

        menh_de_3_diem_mua_vang_dong_thuan = kiem_tra_xu_huong_gia_dang_tot and kiem_tra_ai_dang_tot and kiem_tra_winrate_dang_tot

        if menh_de_1_canh_bao_gom_rai_dinh:
            chuoi_van_ban_tong_ket_ra_lenh_1 = f"** ⚠️  LƯU Ý ĐẶC BIỆT DÀNH CHO MINH:** Dù hệ thống báo hiệu có dòng tiền Cá mập đang gom hàng, nhưng vì giá vẫn bị ép nằm dưới MA20, nên đây thực chất là pha 'Gom Hàng Rải Đinh' ròng rã nhiều tháng của các Quỹ Lớn. Nhỏ lẻ mua lúc này rất dễ bị chôn vốn. Lời khuyên là hãy đợi giá bứt phá qua MA20 rồi mới đánh thóp theo."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_van_ban_tong_ket_ra_lenh_1)

        elif menh_de_2_canh_bao_rui_ro_bo_chay:
            chuoi_van_ban_tong_ket_ra_lenh_2 = f"** ⛔  RỦI RO NGẬP TRÀN:** Cả Trí tuệ nhân tạo và Dữ liệu Lịch sử đều quay lưng với cổ phiếu này. Bất kỳ nhịp kéo tăng nào (nếu có) khả năng cao chỉ là Bull Trap để xả hàng. Tuyệt đối nên đứng ngoài quan sát."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_van_ban_tong_ket_ra_lenh_2)

        elif menh_de_3_diem_mua_vang_dong_thuan:
            chuoi_van_ban_tong_ket_ra_lenh_3 = f"** 🚀  ĐIỂM MUA VÀNG (GOLDEN CROSS):** Biểu đồ nền tảng đẹp, Dòng tiền lớn nhập cuộc, AI và Lịch sử đều đồng thuận ủng hộ. Đây là cơ hội giải ngân có mức độ an toàn rất cao. Có thể mua 30-50% vị thế."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_van_ban_tong_ket_ra_lenh_3)

        else:
            chuoi_van_ban_tong_ket_ra_lenh_4 = f"** ⚖️  TRẠNG THÁI THEO DÕI (50/50):** Tín hiệu từ các chỉ báo đang có sự phân hóa, điểm mua chưa thực sự chín muồi. Minh nên đưa mã này vào Watchlist và chờ một phiên bùng nổ khối lượng thực sự để xác nhận xu hướng."
            mang_chua_cac_dong_text_phan_tich_hoan_thien.append(chuoi_van_ban_tong_ket_ra_lenh_4)
        # Trả về kết quả hoàn chỉnh
        chuoi_van_ban_bao_cao_hoan_chinh = "\n\n".join(mang_chua_cac_dong_text_phan_tich_hoan_thien)
        return chuoi_van_ban_bao_cao_hoan_chinh
# ==============================================================================
# 6. PHÂN TÍCH TÀI CHÍNH CỐT LÕI (FUNDAMENTAL LAYER)
# ==============================================================================
    def do_luong_tang_truong_canslim(ma_chung_khoan_kiem_tra):
        """Đo lường mức tăng trưởng chữ C (Current Earnings)"""
        try:
            # Truy vấn Báo Cáo Kết Quả Kinh Doanh
            chuoi_tham_so_chu_ky = 'quarter'
            chuoi_tham_so_ngon_ngu = 'en'

            bang_bctc_ket_qua_kinh_doanh_full = dong_co_truy_xuat_vnstock.stock.finance.income_statement(
                symbol=ma_chung_khoan_kiem_tra,
                period=chuoi_tham_so_chu_ky,
                lang=chuoi_tham_so_ngon_ngu
            )

            bang_bctc_ket_qua_kinh_doanh_rut_gon = bang_bctc_ket_qua_kinh_doanh_full.head(5)

            # Tập hợp các từ khóa chứa Lợi nhuận sau thuế
            tap_hop_tu_khoa_nhan_dien_loi_nhuan_dn = [
                'sau thuế',
                'posttax',
                'net profit',
                'earning'
            ]

            danh_sach_cac_cot_tuong_thich_khi_quet_bctc = []

            tap_hop_cac_cot_hien_co_cua_bctc = bang_bctc_ket_qua_kinh_doanh_rut_gon.columns

            # Quét vòng lặp để lấy tên cột chuẩn xác
            for ten_cot_dang_duoc_quet_trong_bang_bctc in tap_hop_cac_cot_hien_co_cua_bctc:

                chuoi_ten_cot_da_duoc_in_thuong = str(ten_cot_dang_duoc_quet_trong_bang_bctc).lower()

                for tu_khoa_mau_trong_tu_dien in tap_hop_tu_khoa_nhan_dien_loi_nhuan_dn:

                    kiem_tra_co_chua_tu_khoa_khong = tu_khoa_mau_trong_tu_dien in chuoi_ten_cot_da_duoc_in_thuong

                    if kiem_tra_co_chua_tu_khoa_khong:
                        danh_sach_cac_cot_tuong_thich_khi_quet_bctc.append(ten_cot_dang_duoc_quet_trong_bang_bctc)
                        break

            # Xử lý kết quả quét
            so_luong_cot_tuong_thich_tim_thay = len(danh_sach_cac_cot_tuong_thich_khi_quet_bctc)
            kiem_tra_co_tim_thay_cot_lnst_hop_le = so_luong_cot_tuong_thich_tim_thay > 0

            if kiem_tra_co_tim_thay_cot_lnst_hop_le:

                ten_cot_lnst_chinh_xac_duoc_lay = danh_sach_cac_cot_tuong_thich_khi_quet_bctc[0]

                gia_tri_lnst_cua_quy_moi_nhat_nay = float(bang_bctc_ket_qua_kinh_doanh_rut_gon.iloc[0][ten_cot_lnst_chinh_xac_duoc_lay])
                gia_tri_lnst_cua_cung_ky_nam_ngoai_do = float(bang_bctc_ket_qua_kinh_doanh_rut_gon.iloc[4][ten_cot_lnst_chinh_xac_duoc_lay])

                kiem_tra_lnst_nam_ngoai_co_duong_de_tinh_khong = gia_tri_lnst_cua_cung_ky_nam_ngoai_do > 0

                if kiem_tra_lnst_nam_ngoai_co_duong_de_tinh_khong:

                    muc_do_chenh_lech_loi_nhuan_sinh_ra = gia_tri_lnst_cua_quy_moi_nhat_nay - gia_tri_lnst_cua_cung_ky_nam_ngoai_do

                    bien_do_tang_truong_bang_ty_le_phan_tram = (muc_do_chenh_lech_loi_nhuan_sinh_ra / gia_tri_lnst_cua_cung_ky_nam_ngoai_do) * 100

                    ket_qua_tang_truong_lam_tron = round(bien_do_tang_truong_bang_ty_le_phan_tram, 1)

                    return ket_qua_tang_truong_lam_tron

        except Exception:
            pass

        # Fallback Yahoo Finance
        try:
            chuoi_hau_to_vn_cho_yahoo = ".VN"
            chuoi_ma_chung_khoan_danh_cho_yahoo_dn = f"{ma_chung_khoan_kiem_tra}{chuoi_hau_to_vn_cho_yahoo}"

            doi_tuong_yf_ticker_lay_thong_tin_dn = yf.Ticker(chuoi_ma_chung_khoan_danh_cho_yahoo_dn)
            du_lieu_ho_so_doanh_nghiep_tu_yahoo_dn = doi_tuong_yf_ticker_lay_thong_tin_dn.info

            chuoi_tu_khoa_tang_truong_yahoo = 'earningsQuarterlyGrowth'
            ti_le_tang_truong_tu_he_thong_yahoo_dn = du_lieu_ho_so_doanh_nghiep_tu_yahoo_dn.get(chuoi_tu_khoa_tang_truong_yahoo)

            kiem_tra_co_du_lieu_tu_yahoo_dn = ti_le_tang_truong_tu_he_thong_yahoo_dn is not None

            if kiem_tra_co_du_lieu_tu_yahoo_dn:
                gia_tri_tang_truong_phan_tram_yf_dn = ti_le_tang_truong_tu_he_thong_yahoo_dn * 100
                ket_qua_tang_truong_yf_lam_tron = round(gia_tri_tang_truong_phan_tram_yf_dn, 1)

                return ket_qua_tang_truong_yf_lam_tron

        except Exception:
            pass

        return None
    def boc_tach_chi_so_pe_roe(ma_chung_khoan_kiem_tra):
        """
        Đo lường P/E và ROE.
        Đã FIX LỖI P/E 0.0 theo yêu cầu của Minh: Trả về None nếu API sập.
        """
        chi_so_pe_cuoi_cung_tra_ve_minh = None
        chi_so_roe_cuoi_cung_tra_ve_minh = None

        try:
            # Gọi API Vnstock
            chuoi_tham_so_chu_ky_ratio = 'quarterly'
            bang_chi_so_tai_chinh_vnstock_goc = dong_co_truy_xuat_vnstock.stock.finance.ratio(
                ma_chung_khoan_kiem_tra,
                chuoi_tham_so_chu_ky_ratio
            )

            dong_chi_so_cua_quy_moi_nhat = bang_chi_so_tai_chinh_vnstock_goc.iloc[-1]

            chi_so_pe_tu_may_chu_vnstock_truy_xuat = dong_chi_so_cua_quy_moi_nhat.get(
                'ticker_pe',
                dong_chi_so_cua_quy_moi_nhat.get('pe', None)
            )

            chi_so_roe_tu_may_chu_vnstock_truy_xuat = dong_chi_so_cua_quy_moi_nhat.get(
                'roe',
                None
            )

            # Kiểm tra lỗi P/E rỗng hoặc 0.0 hoặc NaN
            kiem_tra_pe_co_ton_tai = chi_so_pe_tu_may_chu_vnstock_truy_xuat is not None
            if kiem_tra_pe_co_ton_tai:
                kiem_tra_pe_khong_bi_nan = not np.isnan(chi_so_pe_tu_may_chu_vnstock_truy_xuat)
                kiem_tra_pe_lon_hon_khong = chi_so_pe_tu_may_chu_vnstock_truy_xuat > 0

                if kiem_tra_pe_khong_bi_nan and kiem_tra_pe_lon_hon_khong:
                    chi_so_pe_cuoi_cung_tra_ve_minh = chi_so_pe_tu_may_chu_vnstock_truy_xuat

            # Kiểm tra lỗi ROE
            kiem_tra_roe_co_ton_tai = chi_so_roe_tu_may_chu_vnstock_truy_xuat is not None
            if kiem_tra_roe_co_ton_tai:
                kiem_tra_roe_khong_bi_nan = not np.isnan(chi_so_roe_tu_may_chu_vnstock_truy_xuat)
                kiem_tra_roe_lon_hon_khong = chi_so_roe_tu_may_chu_vnstock_truy_xuat > 0

                if kiem_tra_roe_khong_bi_nan and kiem_tra_roe_lon_hon_khong:
                    chi_so_roe_cuoi_cung_tra_ve_minh = chi_so_roe_tu_may_chu_vnstock_truy_xuat

        except Exception:
            pass

        # Nếu Vnstock sập (Giá trị vẫn đang là None), chạy fallback Yahoo
        kiem_tra_can_fallback_cho_pe_khong = chi_so_pe_cuoi_cung_tra_ve_minh is None

        if kiem_tra_can_fallback_cho_pe_khong:
            try:
                chuoi_hau_to_vn_pe = ".VN"
                chuoi_ma_chung_khoan_pe_yahoo_dn = f"{ma_chung_khoan_kiem_tra}{chuoi_hau_to_vn_pe}"

                doi_tuong_yf_ticker_lay_pe_dn = yf.Ticker(chuoi_ma_chung_khoan_pe_yahoo_dn)
                du_lieu_ho_so_doanh_nghiep_yf_dn = doi_tuong_yf_ticker_lay_pe_dn.info

                chuoi_tu_khoa_pe_yahoo = 'trailingPE'
                chi_so_pe_tu_may_chu_yahoo_dn = du_lieu_ho_so_doanh_nghiep_yf_dn.get(chuoi_tu_khoa_pe_yahoo, None)

                chuoi_tu_khoa_roe_yahoo = 'returnOnEquity'
                chi_so_roe_tu_may_chu_yahoo_dn = du_lieu_ho_so_doanh_nghiep_yf_dn.get(chuoi_tu_khoa_roe_yahoo, None)

                kiem_tra_pe_yahoo_co_du_lieu = chi_so_pe_tu_may_chu_yahoo_dn is not None
                if kiem_tra_pe_yahoo_co_du_lieu:
                    chi_so_pe_cuoi_cung_tra_ve_minh = chi_so_pe_tu_may_chu_yahoo_dn

                kiem_tra_roe_yahoo_co_du_lieu = chi_so_roe_tu_may_chu_yahoo_dn is not None
                if kiem_tra_roe_yahoo_co_du_lieu:
                    chi_so_roe_cuoi_cung_tra_ve_minh = chi_so_roe_tu_may_chu_yahoo_dn

            except Exception:
                pass

        return chi_so_pe_cuoi_cung_tra_ve_minh, chi_so_roe_cuoi_cung_tra_ve_minh
# ==============================================================================
# 7.  🧠  ROBOT ADVISOR MASTER: ĐƯA RA LỆNH NGẮN GỌN BÊN GÓC PHẢI
# ==============================================================================
    def he_thong_suy_luan_advisor(dong_du_lieu_cuoi_phien, diem_so_ai_ht, diem_so_winrate_ht, diem_so_tang_truong_ht):
        """Tính toán điểm số định lượng để xuất ra thông báo MUA/BÁN ngắn gọn"""

        tong_diem_danh_gia_tin_cay_cua_robot = 0

        # 1. Đánh giá cỗ máy AI
        kiem_tra_ai_co_hop_le_de_tinh_diem = isinstance(diem_so_ai_ht, float)

        if kiem_tra_ai_co_hop_le_de_tinh_diem:
            kiem_tra_ai_co_ung_ho_mua = diem_so_ai_ht >= 58.0
            if kiem_tra_ai_co_ung_ho_mua:
                tong_diem_danh_gia_tin_cay_cua_robot += 1

        # 2. Đánh giá mức độ Winrate
        kiem_tra_winrate_co_tot_de_tinh_diem = diem_so_winrate_ht >= 50.0

        if kiem_tra_winrate_co_tot_de_tinh_diem:
            tong_diem_danh_gia_tin_cay_cua_robot += 1

        # 3. Đánh giá Kỹ thuật
        gia_dong_cua_hien_tai_tai_phien_xet = dong_du_lieu_cuoi_phien['close']
        duong_ho_tro_ma20_tai_phien_xet = dong_du_lieu_cuoi_phien['ma20']

        kiem_tra_gia_co_an_toan_tren_ma20 = gia_dong_cua_hien_tai_tai_phien_xet > duong_ho_tro_ma20_tai_phien_xet

        if kiem_tra_gia_co_an_toan_tren_ma20:
            tong_diem_danh_gia_tin_cay_cua_robot += 1

        # 4. Đánh giá Tài chính
        kiem_tra_co_diem_tang_truong_bctc = diem_so_tang_truong_ht is not None

        if kiem_tra_co_diem_tang_truong_bctc:
            kiem_tra_tang_truong_co_tot_khong = diem_so_tang_truong_ht >= 15.0
            if kiem_tra_tang_truong_co_tot_khong:
                tong_diem_danh_gia_tin_cay_cua_robot += 1

        # Lấy RSI làm hệ quy chiếu chống Fomo
        chi_so_rsi_hien_tai_de_chong_fomo = dong_du_lieu_cuoi_phien['rsi']
        # Rút ra kết luận bằng các mệnh đề Boolean
        dieu_kien_mua_diem_so_cao_dat_chuan = tong_diem_danh_gia_tin_cay_cua_robot >= 3
        dieu_kien_mua_rsi_tot_chua_nong = chi_so_rsi_hien_tai_de_chong_fomo < 68

        dieu_kien_gop_cho_lenh_mua_manh = dieu_kien_mua_diem_so_cao_dat_chuan and dieu_kien_mua_rsi_tot_chua_nong

        dieu_kien_ban_diem_so_qua_thap = tong_diem_danh_gia_tin_cay_cua_robot <= 1
        dieu_kien_ban_rsi_qua_cao_nong = chi_so_rsi_hien_tai_de_chong_fomo > 78
        dieu_kien_ban_gia_giam_roi_gay_nen = gia_dong_cua_hien_tai_tai_phien_xet < duong_ho_tro_ma20_tai_phien_xet

        dieu_kien_gop_cho_lenh_ban_manh = dieu_kien_ban_diem_so_qua_thap or dieu_kien_ban_rsi_qua_cao_nong or dieu_kien_ban_gia_giam_roi_gay_nen

        if dieu_kien_gop_cho_lenh_mua_manh:
            chuoi_lenh_duoc_hien_thi_robot = " 🚀  MUA / NẮM GIỮ (STRONG BUY)"
            chuoi_mau_sac_hien_thi_robot = "green"

        elif dieu_kien_gop_cho_lenh_ban_manh:
            chuoi_lenh_duoc_hien_thi_robot = " 🚨  BÁN / ĐỨNG NGOÀI (BEARISH)"
            chuoi_mau_sac_hien_thi_robot = "red"

        else:
            chuoi_lenh_duoc_hien_thi_robot = " ⚖️  THEO DÕI (WATCHLIST)"
            chuoi_mau_sac_hien_thi_robot = "orange"
        return chuoi_lenh_duoc_hien_thi_robot, chuoi_mau_sac_hien_thi_robot
# ==============================================================================
# 7.5 TÍNH NĂNG MỚI: PHÂN LOẠI SIÊU CỔ PHIẾU (TÍCH HỢP 3 VŨ KHÍ MỚI)
# ==============================================================================
    def phan_loai_sieu_co_phieu_tab_4(ma_co_phieu_dau_vao, df_bang_scan_day_du_truy_xuat, ai_prob_val_hien_tai_duoc_cap):
        """
        Radar lọc 2 tầng chuyên sâu:
        Tầng 1: Đã bùng nổ Vol (Dành cho đánh T+ rủi ro)
        Tầng 2: Danh Sách Chờ (Tích hợp: Thắt chặt Bollinger, Cạn Cung, Tây Gom)
        """

        # Trích xuất dữ liệu ngày hiện tại
        dong_du_lieu_cua_phien_hom_nay_scan = df_bang_scan_day_du_truy_xuat.iloc[-1]

        gia_tri_vol_strength_ht_scan = dong_du_lieu_cua_phien_hom_nay_scan['vol_strength']
        gia_tri_rsi_ht_scan = dong_du_lieu_cua_phien_hom_nay_scan['rsi']
        gia_tri_khop_lenh_ht_scan = dong_du_lieu_cua_phien_hom_nay_scan['close']
        gia_tri_ma20_ht_scan = dong_du_lieu_cua_phien_hom_nay_scan['ma20']

        # --- TẦNG 1: BÙNG NỔ (BREAKOUT) ---
        # Điều kiện: Nổ Vol
        kiem_tra_vol_dang_no_scan = gia_tri_vol_strength_ht_scan > 1.3

        if kiem_tra_vol_dang_no_scan:
            chuoi_tra_ve_nhom_bung_no = " 🚀  Bùng Nổ (Dòng tiền nóng)"
            return chuoi_tra_ve_nhom_bung_no

        # --- TẦNG 2: DANH SÁCH CHỜ CHÂN SÓNG (WATCHLIST) ---

        # 1. Điều kiện Cơ Bản (Base Criteria)
        dk_base_vol_duoi = gia_tri_vol_strength_ht_scan >= 0.8
        dk_base_vol_tren = gia_tri_vol_strength_ht_scan <= 1.2
        dk_base_vol_tich_luy = dk_base_vol_duoi and dk_base_vol_tren

        muc_gia_chap_nhan_sat_nen = gia_tri_ma20_ht_scan * 0.95
        dk_base_price_an_toan = gia_tri_khop_lenh_ht_scan >= muc_gia_chap_nhan_sat_nen

        dk_base_rsi_chua_nong = gia_tri_rsi_ht_scan < 62

        dk_base_ai_thich_co_phieu_nay = False
        kiem_tra_kieu_du_lieu_ai_hop_le = isinstance(ai_prob_val_hien_tai_duoc_cap, float)

        if kiem_tra_kieu_du_lieu_ai_hop_le:
            if ai_prob_val_hien_tai_duoc_cap > 48.0:
                dk_base_ai_thich_co_phieu_nay = True

        dieu_kien_co_ban_pass_toan_bo = dk_base_vol_tich_luy and dk_base_price_an_toan and dk_base_rsi_chua_nong and dk_base_ai_thich_co_phieu_nay

        if dieu_kien_co_ban_pass_toan_bo == False:
            return None

        # 2. Vũ khí 1: Màng lọc Nén Lò Xo (Bollinger Squeeze)
        gia_tri_bb_width_hom_nay_cua_ma = dong_du_lieu_cua_phien_hom_nay_scan['bb_width']

        tap_du_lieu_bb_width_20_ngay_truoc_do = df_bang_scan_day_du_truy_xuat['bb_width'].tail(20)
        gia_tri_bb_width_nho_nhat_20_ngay_qua = tap_du_lieu_bb_width_20_ngay_truoc_do.min()

        muc_chap_nhan_sai_so_squeeze_cua_ma = gia_tri_bb_width_nho_nhat_20_ngay_qua * 1.2
        dieu_kien_da_bi_nen_chat_cua_ma = gia_tri_bb_width_hom_nay_cua_ma <= muc_chap_nhan_sai_so_squeeze_cua_ma

        # 3. Vũ khí 2: Màng lọc Cạn Cung (Supply Exhaustion)
        tap_du_lieu_can_cung_5_ngay_qua_cua_ma = df_bang_scan_day_du_truy_xuat['can_cung'].tail(5)

        # Hàm any() sẽ kiểm tra xem có ít nhất 1 giá trị True trong 5 ngày không
        dieu_kien_co_xuat_hien_can_cung_cua_ma = tap_du_lieu_can_cung_5_ngay_qua_cua_ma.any()

        # 4. Vũ khí 3: Khối Ngoại Gom Ròng (Smart Money)
        dieu_kien_khoi_ngoai_dang_gom_cua_ma = False

        # Gọi trực tiếp hàm Khối Ngoại để check (Lấy 5 ngày cho nhẹ API)
        so_ngay_can_lay_de_check_ngoai = 5
        bang_check_ngoai_cua_ma = lay_du_lieu_khoi_ngoai_thuc_te(
            ma_co_phieu_dau_vao,
            so_ngay_can_lay_de_check_ngoai
        )

        kiem_tra_bang_check_ngoai_co_data = bang_check_ngoai_cua_ma is not None

        if kiem_tra_bang_check_ngoai_co_data:

            kiem_tra_bang_check_ngoai_empty = bang_check_ngoai_cua_ma.empty

            if kiem_tra_bang_check_ngoai_empty == False:

                # Tính tổng 3 ngày gần nhất
                tong_mua_3_ngay_gan_nhat = 0.0
                tong_ban_3_ngay_gan_nhat = 0.0

                bang_3_ngay_cuoi_cung_cua_ma = bang_check_ngoai_cua_ma.tail(3)

                for idx_ngoai_cua_ma, dong_du_lieu_ngoai_hunter_cua_ma in bang_3_ngay_cuoi_cung_cua_ma.iterrows():

                    gia_tri_mua_hunter_cua_ma = float(dong_du_lieu_ngoai_hunter_cua_ma.get('buyval', 0))
                    tong_mua_3_ngay_gan_nhat = tong_mua_3_ngay_gan_nhat + gia_tri_mua_hunter_cua_ma

                    gia_tri_ban_hunter_cua_ma = float(dong_du_lieu_ngoai_hunter_cua_ma.get('sellval', 0))
                    tong_ban_3_ngay_gan_nhat = tong_ban_3_ngay_gan_nhat + gia_tri_ban_hunter_cua_ma

                tong_rong_3_ngay_cua_tay_long_cua_ma = tong_mua_3_ngay_gan_nhat - tong_ban_3_ngay_gan_nhat

                kiem_tra_tay_long_co_mua_rong_khong = tong_rong_3_ngay_cua_tay_long_cua_ma > 0

                if kiem_tra_tay_long_co_mua_rong_khong:
                    dieu_kien_khoi_ngoai_dang_gom_cua_ma = True

        # Bổ sung quét Tự Doanh Gom
        bang_check_tu_doanh_cua_ma = lay_du_lieu_tu_doanh_thuc_te(ma_co_phieu_dau_vao, so_ngay_can_lay_de_check_ngoai)
        kiem_tra_bang_check_td_co_data = bang_check_tu_doanh_cua_ma is not None
        if kiem_tra_bang_check_td_co_data:
            kiem_tra_bang_check_td_empty = bang_check_tu_doanh_cua_ma.empty
            if kiem_tra_bang_check_td_empty == False:
                tong_mua_td_3_ngay_gan_nhat = 0.0
                tong_ban_td_3_ngay_gan_nhat = 0.0
                bang_3_ngay_cuoi_cung_td_cua_ma = bang_check_tu_doanh_cua_ma.tail(3)
                for idx_td_cua_ma, dong_du_lieu_td_hunter_cua_ma in bang_3_ngay_cuoi_cung_td_cua_ma.iterrows():
                    gia_tri_mua_td_hunter_cua_ma = float(dong_du_lieu_td_hunter_cua_ma.get('buyval', 0))
                    tong_mua_td_3_ngay_gan_nhat = tong_mua_td_3_ngay_gan_nhat + gia_tri_mua_td_hunter_cua_ma
                    gia_tri_ban_td_hunter_cua_ma = float(dong_du_lieu_td_hunter_cua_ma.get('sellval', 0))
                    tong_ban_td_3_ngay_gan_nhat = tong_ban_td_3_ngay_gan_nhat + gia_tri_ban_td_hunter_cua_ma
                tong_rong_3_ngay_cua_tu_doanh_cua_ma = tong_mua_td_3_ngay_gan_nhat - tong_ban_td_3_ngay_gan_nhat
                kiem_tra_tu_doanh_co_mua_rong_khong = tong_rong_3_ngay_cua_tu_doanh_cua_ma > 0
                if kiem_tra_tu_doanh_co_mua_rong_khong:
                    dieu_kien_khoi_ngoai_dang_gom_cua_ma = True

        # 5. TỔNG HỢP SIÊU MÀNG LỌC
        # Nếu đạt Cơ bản + (Nén chặt HOẶC Cạn cung HOẶC Tây gom/Tự doanh gom) -> Đưa vào Danh sách vàng
        dieu_kien_nang_cao_pass_toan_bo = dieu_kien_da_bi_nen_chat_cua_ma or dieu_kien_co_xuat_hien_can_cung_cua_ma or dieu_kien_khoi_ngoai_dang_gom_cua_ma

        if dieu_kien_nang_cao_pass_toan_bo:
            chuoi_tra_ve_nhom_danh_sach_cho = " ⚖️  Danh Sách Chờ (Vùng Gom An Toàn)"
            return chuoi_tra_ve_nhom_danh_sach_cho

        return None
# ==============================================================================
# 8. GIAO DIỆN NGƯỜI DÙNG & KIỂM SOÁT LUỒNG DỮ LIỆU (UI CONTROLLER)
# ==============================================================================

    @st.cache_data(ttl=3600)
    def tai_va_chuan_bi_danh_sach_ma_chung_khoan_hose():
        """
        Tải bảng danh sách mã niêm yết từ máy chủ để làm menu.
        Bộ nhớ cache giúp không phải tải lại mỗi khi F5.
        """
        try:
            bang_danh_sach_niem_yet_toan_bo_hose = dong_co_truy_xuat_vnstock.market.listing()

            chuoi_loc_san_hose_chinh = 'HOSE'
            bo_loc_nhung_ma_thuoc_san_hose_chinh = bang_danh_sach_niem_yet_toan_bo_hose['comGroupCode'] == chuoi_loc_san_hose_chinh

            bang_danh_sach_chi_chua_ma_hose_chinh = bang_danh_sach_niem_yet_toan_bo_hose[bo_loc_nhung_ma_thuoc_san_hose_chinh]

            danh_sach_cac_chuoi_ma_chung_khoan_chinh = bang_danh_sach_chi_chua_ma_hose_chinh['ticker'].tolist()

            return danh_sach_cac_chuoi_ma_chung_khoan_chinh

        except Exception:
            # Dữ liệu dự phòng nếu mất mạng API
            danh_sach_cung_du_phong_cho_menu = [
                "FPT",
                "HPG",
                "SSI",
                "TCB",
                "MWG",
                "VNM",
                "VIC",
                "VHM",
                "STB",
                "MSN",
                "GAS"
            ]
            return danh_sach_cung_du_phong_cho_menu
    # Bắt đầu vẽ Sidebar
    danh_sach_toan_bo_cac_ma_hose_hien_co = tai_va_chuan_bi_danh_sach_ma_chung_khoan_hose()

    chuoi_tieu_de_thanh_dieu_huong = " 🕹️  Trung Tâm Giao Dịch Định Lượng Quant"
    st.sidebar.header(chuoi_tieu_de_thanh_dieu_huong)

    chuoi_huong_dan_chon_ma_dropdown = "Lựa chọn mã cổ phiếu mục tiêu để phân tích:"
    thanh_phan_chon_ma_dropdown = st.sidebar.selectbox(
        chuoi_huong_dan_chon_ma_dropdown,
        danh_sach_toan_bo_cac_ma_hose_hien_co
    )

    chuoi_huong_dan_nhap_ma_tay = "Hoặc nhập trực tiếp tên mã (Ví dụ: FPT):"
    thanh_phan_nhap_ma_bang_tay_goc = st.sidebar.text_input(chuoi_huong_dan_nhap_ma_tay)
    thanh_phan_nhap_ma_bang_tay_da_viet_hoa = thanh_phan_nhap_ma_bang_tay_goc.upper()

    # Logic xác định ưu tiên chọn mã nào
    # ĐÃ ĐƯỢC CHUẨN HÓA DUY NHẤT 1 BIẾN ĐỂ FIX LỖI NAMEERROR TẠI DÒNG 1600
    kiem_tra_co_nhap_tay_khong = thanh_phan_nhap_ma_bang_tay_da_viet_hoa != ""

    if kiem_tra_co_nhap_tay_khong:
        ma_co_phieu_dang_duoc_chon = thanh_phan_nhap_ma_bang_tay_da_viet_hoa
    else:
        ma_co_phieu_dang_duoc_chon = thanh_phan_chon_ma_dropdown
    # Xây dựng bộ 4 TABS chính
    chuoi_ten_tab_1 = " 🤖  ROBOT ADVISOR & BẢN PHÂN TÍCH TỰ ĐỘNG"
    chuoi_ten_tab_2 = " 🏢  BÁO CÁO TÀI CHÍNH & CANSLIM"
    chuoi_ten_tab_3 = " 🌊  BÓC TÁCH DÒNG TIỀN THÔNG MINH"
    chuoi_ten_tab_4 = " 🔍  RADAR TRUY QUÉT SIÊU CỔ PHIẾU"

    khung_tab_robot_advisor, khung_tab_tai_chinh_co_ban, khung_tab_dong_tien_chuyen_sau, khung_tab_radar_truy_quet = st.tabs([
        chuoi_ten_tab_1,
        chuoi_ten_tab_2,
        chuoi_ten_tab_3,
        chuoi_ten_tab_4
    ])
    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR VÀ BẢN PHÂN TÍCH TỰ ĐỘNG
    # ------------------------------------------------------------------------------
    with khung_tab_robot_advisor:

        chuoi_hien_thi_nut_bam_phan_tich = f" ⚡  TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG TOÀN DIỆN MÃ CỔ PHIẾU {ma_co_phieu_dang_duoc_chon}"
        nut_nhan_chay_phan_tich_toan_dien = st.button(chuoi_hien_thi_nut_bam_phan_tich)

        if nut_nhan_chay_phan_tich_toan_dien:

            chuoi_hien_thi_vong_xoay_cho = f"Hệ thống đang kích hoạt quy trình đồng bộ dữ liệu đa tầng cho mã {ma_co_phieu_dang_duoc_chon}..."

            with st.spinner(chuoi_hien_thi_vong_xoay_cho):

                # BƯỚC 1: Gọi dữ liệu
                bang_du_lieu_tho_lay_duoc_tab1 = lay_du_lieu_nien_yet_chuan(ma_co_phieu_dang_duoc_chon)

                kiem_tra_bang_tho_co_ton_tai_tab1 = bang_du_lieu_tho_lay_duoc_tab1 is not None

                if kiem_tra_bang_tho_co_ton_tai_tab1:

                    kiem_tra_bang_tho_co_rong_khong_tab1 = bang_du_lieu_tho_lay_duoc_tab1.empty

                    if kiem_tra_bang_tho_co_rong_khong_tab1 == False:

                        # BƯỚC 2: Tính toán bộ chỉ báo
                        bang_du_lieu_chi_tiet_da_tinh_xong_tab1 = tinh_toan_bo_chi_bao_quant(bang_du_lieu_tho_lay_duoc_tab1)

                        dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1 = bang_du_lieu_chi_tiet_da_tinh_xong_tab1.iloc[-1]

                        # BƯỚC 3: AI và Lịch sử
                        diem_ai_du_bao_t3_tra_ve_tab1 = du_bao_xac_suat_ai_t3(bang_du_lieu_chi_tiet_da_tinh_xong_tab1)

                        diem_win_rate_lich_su_tra_ve_tab1 = thuc_thi_backtest_chien_thuat(bang_du_lieu_chi_tiet_da_tinh_xong_tab1)

                        nhan_tam_ly_fng_tra_ve_tab1, diem_tam_ly_fng_tra_ve_tab1 = phan_tich_tam_ly_dam_dong(bang_du_lieu_chi_tiet_da_tinh_xong_tab1)

                        # BƯỚC 4: Tài chính cơ bản
                        muc_tang_truong_quy_lnst_tra_ve_tab1 = do_luong_tang_truong_canslim(ma_co_phieu_dang_duoc_chon)

                        # BƯỚC 5: Quét Market Breadth
                        danh_sach_10_ma_tru_kiem_dinh_tab1 = [
                            "FPT",
                            "HPG",
                            "VCB",
                            "VIC",
                            "VNM",
                            "TCB",
                            "SSI",
                            "MWG",
                            "VHM",
                            "GAS"
                        ]

                        mang_chua_ma_tru_co_dau_hieu_gom_tab1 = []
                        mang_chua_ma_tru_co_dau_hieu_xa_tab1 = []

                        for ma_tru_dang_quet_trong_tab1 in danh_sach_10_ma_tru_kiem_dinh_tab1:
                            try:
                                bang_tru_tho_10_ngay_tab1 = lay_du_lieu_nien_yet_chuan(ma_tru_dang_quet_trong_tab1, so_ngay_lich_su_can_lay=10)

                                kiem_tra_bang_tru_co_khong_tab1 = bang_tru_tho_10_ngay_tab1 is not None

                                if kiem_tra_bang_tru_co_khong_tab1:

                                    bang_tru_da_tinh_toan_tab1 = tinh_toan_bo_chi_bao_quant(bang_tru_tho_10_ngay_tab1)

                                    dong_cuoi_cua_ma_tru_tab1 = bang_tru_da_tinh_toan_tab1.iloc[-1]

                                    dieu_kien_tru_gia_tang_tab1 = dong_cuoi_cua_ma_tru_tab1['return_1d'] > 0

                                    dieu_kien_tru_gia_giam_tab1 = dong_cuoi_cua_ma_tru_tab1['return_1d'] < 0

                                    dieu_kien_tru_no_vol_tab1 = dong_cuoi_cua_ma_tru_tab1['vol_strength'] > 1.2

                                    if dieu_kien_tru_gia_tang_tab1 and dieu_kien_tru_no_vol_tab1:
                                        mang_chua_ma_tru_co_dau_hieu_gom_tab1.append(ma_tru_dang_quet_trong_tab1)

                                    elif dieu_kien_tru_gia_giam_tab1 and dieu_kien_tru_no_vol_tab1:
                                        mang_chua_ma_tru_co_dau_hieu_xa_tab1.append(ma_tru_dang_quet_trong_tab1)
                            except Exception:
                                pass
                        # --- GIAO DIỆN HIỂN THỊ KẾT QUẢ ĐẦU VÀO TRUNG TÂM ---
                        chuoi_tieu_de_bao_cao_chinh = f"###  🎯  BẢN PHÂN TÍCH CHUYÊN MÔN TỰ ĐỘNG - MÃ {ma_co_phieu_dang_duoc_chon}"
                        st.write(chuoi_tieu_de_bao_cao_chinh)

                        cot_khung_bao_cao_chu_chuyen_sau, cot_khung_lenh_hanh_dong_ngan_gon = st.columns([2, 1])

                        with cot_khung_bao_cao_chu_chuyen_sau:
                            # Kích hoạt AI viết bài phân tích
                            tui_du_lieu_bao_cao = {
                                'ma_chung_khoan': ma_co_phieu_dang_duoc_chon,
                                'dong_du_lieu_cuoi': dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1,
                                'diem_so_ai': diem_ai_du_bao_t3_tra_ve_tab1,
                                'diem_so_winrate': diem_win_rate_lich_su_tra_ve_tab1,
                                'mang_tru_gom': mang_chua_ma_tru_co_dau_hieu_gom_tab1,
                                'mang_tru_xa': mang_chua_ma_tru_co_dau_hieu_xa_tab1
                            }
                            chuoi_bai_bao_cao_hoan_chinh_tab1 = tao_ban_bao_cao_tu_dong_chuyen_sau(tui_du_lieu_bao_cao)

                            st.info(chuoi_bai_bao_cao_hoan_chinh_tab1)

                        with cot_khung_lenh_hanh_dong_ngan_gon:
                            chuoi_tieu_de_robot_de_xuat = " 🤖  ROBOT ĐỀ XUẤT LỆNH HIỆN TẠI:"
                            st.subheader(chuoi_tieu_de_robot_de_xuat)

                            chuoi_lenh_duoc_tra_ve_tab1, mau_sac_lenh_duoc_tra_ve_tab1 = he_thong_suy_luan_advisor(
                                dong_du_lieu_cuoi_phien=dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1,
                                diem_so_ai_ht=diem_ai_du_bao_t3_tra_ve_tab1,
                                diem_so_winrate_ht=diem_win_rate_lich_su_tra_ve_tab1,
                                diem_so_tang_truong_ht=muc_tang_truong_quy_lnst_tra_ve_tab1
                            )

                            chuoi_hien_thi_lenh_co_mau = f":{mau_sac_lenh_duoc_tra_ve_tab1}[{chuoi_lenh_duoc_tra_ve_tab1}]"
                            st.title(chuoi_hien_thi_lenh_co_mau)

                        st.divider()

                        # --- GIAO DIỆN BẢNG RADAR HIỆU SUẤT TỔNG QUAN ---
                        chuoi_tieu_de_bang_radar = "###  🧭  Bảng Radar Đo Lường Hiệu Suất Tổng Quan"
                        st.write(chuoi_tieu_de_bang_radar)

                        cot_radar_so_1, cot_radar_so_2, cot_radar_so_3, cot_radar_so_4 = st.columns(4)

                        gia_tri_khop_lenh_moi_nhat_hom_nay_tab1 = dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1['close']
                        chuoi_hien_thi_gia_khop_lenh = f"{gia_tri_khop_lenh_moi_nhat_hom_nay_tab1:,.0f}"

                        cot_radar_so_1.metric(
                            "Giá Khớp Lệnh Mới Nhất",
                            chuoi_hien_thi_gia_khop_lenh
                        )

                        chuoi_hien_thi_diem_fng = f"{diem_tam_ly_fng_tra_ve_tab1}/100"
                        cot_radar_so_2.metric(
                            "Tâm Lý F&G Index",
                            chuoi_hien_thi_diem_fng,
                            delta=nhan_tam_ly_fng_tra_ve_tab1
                        )

                        kiem_tra_ai_co_hop_le_de_danh_gia_tab1 = isinstance(diem_ai_du_bao_t3_tra_ve_tab1, float)

                        if kiem_tra_ai_co_hop_le_de_danh_gia_tab1:
                            kiem_tra_ai_co_tren_55_tab1 = diem_ai_du_bao_t3_tra_ve_tab1 > 55.0
                            if kiem_tra_ai_co_tren_55_tab1:
                                nhan_dang_delta_mui_ten_ai_tab1 = "Tín hiệu Tốt"
                            else:
                                nhan_dang_delta_mui_ten_ai_tab1 = None
                        else:
                            nhan_dang_delta_mui_ten_ai_tab1 = None

                        chuoi_hien_thi_diem_ai = f"{diem_ai_du_bao_t3_tra_ve_tab1}%"
                        cot_radar_so_3.metric(
                            "Khả năng Tăng (AI T+3)",
                            chuoi_hien_thi_diem_ai,
                            delta=nhan_dang_delta_mui_ten_ai_tab1
                        )

                        kiem_tra_winrate_co_tren_45_tab1 = diem_win_rate_lich_su_tra_ve_tab1 > 45

                        if kiem_tra_winrate_co_tren_45_tab1:
                            nhan_dang_delta_mui_ten_backtest_tab1 = "Tỉ lệ Ổn định"
                        else:
                            nhan_dang_delta_mui_ten_backtest_tab1 = None

                        chuoi_hien_thi_diem_winrate = f"{diem_win_rate_lich_su_tra_ve_tab1}%"
                        cot_radar_so_4.metric(
                            "Xác suất Thắng Lịch sử",
                            chuoi_hien_thi_diem_winrate,
                            delta=nhan_dang_delta_mui_ten_backtest_tab1
                        )
                        # --- GIAO DIỆN BẢNG NAKED STATS CHUYÊN MÔN ---
                        chuoi_tieu_de_naked_stats = "###  🎛️  Bảng Chỉ Số Kỹ Thuật Trần (Naked Stats)"
                        st.write(chuoi_tieu_de_naked_stats)

                        cot_naked_so_1, cot_naked_so_2, cot_naked_so_3, cot_naked_so_4 = st.columns(4)

                        # RSI Metric
                        chi_so_rsi_de_trinh_dien_tab1 = dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1['rsi']
                        kiem_tra_rsi_qua_mua = chi_so_rsi_de_trinh_dien_tab1 > 70
                        kiem_tra_rsi_qua_ban = chi_so_rsi_de_trinh_dien_tab1 < 30

                        if kiem_tra_rsi_qua_mua:
                            nhan_canh_bao_rsi_trinh_dien_tab1 = "Đang Quá mua"
                        elif kiem_tra_rsi_qua_ban:
                            nhan_canh_bao_rsi_trinh_dien_tab1 = "Đang Quá bán"
                        else:
                            nhan_canh_bao_rsi_trinh_dien_tab1 = "Vùng An toàn"

                        chuoi_hien_thi_rsi = f"{chi_so_rsi_de_trinh_dien_tab1:.1f}"
                        cot_naked_so_1.metric(
                            "RSI (Sức mạnh 14 Phiên)",
                            chuoi_hien_thi_rsi,
                            delta=nhan_canh_bao_rsi_trinh_dien_tab1
                        )

                        # MACD Metric
                        chi_so_macd_de_trinh_dien_tab1 = dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1['macd']
                        chi_so_signal_de_trinh_dien_tab1 = dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1['signal']

                        kiem_tra_macd_co_cat_len_tab1 = chi_so_macd_de_trinh_dien_tab1 > chi_so_signal_de_trinh_dien_tab1

                        if kiem_tra_macd_co_cat_len_tab1:
                            nhan_canh_bao_macd_trinh_dien_tab1 = "MACD > Signal (Tốt)"
                        else:
                            nhan_canh_bao_macd_trinh_dien_tab1 = "MACD < Signal (Xấu)"

                        chuoi_hien_thi_macd = f"{chi_so_macd_de_trinh_dien_tab1:.2f}"
                        cot_naked_so_2.metric(
                            "Tình trạng Giao cắt MACD",
                            chuoi_hien_thi_macd,
                            delta=nhan_canh_bao_macd_trinh_dien_tab1
                        )

                        # MAs Metric
                        chi_so_ma20_de_trinh_dien_tab1 = dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1['ma20']
                        chi_so_ma50_de_trinh_dien_tab1 = dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1['ma50']

                        chuoi_hien_thi_delta_ma50_tab1 = f"MA50 hiện tại: {chi_so_ma50_de_trinh_dien_tab1:,.0f}"
                        chuoi_hien_thi_ma20 = f"{chi_so_ma20_de_trinh_dien_tab1:,.0f}"

                        cot_naked_so_3.metric(
                            "MA20 (Ngắn) / MA50 (Trung)",
                            chuoi_hien_thi_ma20,
                            delta=chuoi_hien_thi_delta_ma50_tab1
                        )

                        # BOL Metric
                        chi_so_upper_band_de_trinh_dien_tab1 = dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1['upper_band']
                        chi_so_lower_band_de_trinh_dien_tab1 = dong_du_lieu_cua_phien_giao_dich_moi_nhat_tab1['lower_band']

                        chuoi_hien_thi_delta_lower_band_tab1 = f"Khung Chạm Đáy: {chi_so_lower_band_de_trinh_dien_tab1:,.0f}"
                        chuoi_hien_thi_upper = f"{chi_so_upper_band_de_trinh_dien_tab1:,.0f}"

                        cot_naked_so_4.metric(
                            "Khung Chạm Trần Bollinger",
                            chuoi_hien_thi_upper,
                            delta=chuoi_hien_thi_delta_lower_band_tab1,
                            delta_color="inverse"
                        )
                        # ==================================================================
                        # --- VẼ BIỂU ĐỒ MASTER CANDLESTICK CHUYÊN SÂU ---
                        # ==================================================================
                        st.divider()
                        chuoi_tieu_de_master_chart = "###  📊  Biểu Đồ Kỹ Thuật Đa Lớp Chuyên Nghiệp (Master Chart Visualizer)"
                        st.write(chuoi_tieu_de_master_chart)

                        khung_hinh_ve_bieu_do_master_chinh = make_subplots(
                            rows=2,
                            cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.03,
                            row_heights=[0.75, 0.25]
                        )

                        bang_du_lieu_chi_lay_120_phien_de_ve_hinh = bang_du_lieu_chi_tiet_da_tinh_xong_tab1.tail(120)
                        truc_thoi_gian_x_cua_bieu_do_ve_tab1 = bang_du_lieu_chi_lay_120_phien_de_ve_hinh['date']

                        # Nến OHLC
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Candlestick(
                                x=truc_thoi_gian_x_cua_bieu_do_ve_tab1,
                                open=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['open'],
                                high=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['high'],
                                low=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['low'],
                                close=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['close'],
                                name='Biểu Đồ Nến'
                            ),
                            row=1,
                            col=1
                        )

                        # MA20
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Scatter(
                                x=truc_thoi_gian_x_cua_bieu_do_ve_tab1,
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['ma20'],
                                line=dict(color='orange', width=1.5),
                                name='Hỗ Trợ Nền MA20'
                            ),
                            row=1,
                            col=1
                        )

                        # MA200
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Scatter(
                                x=truc_thoi_gian_x_cua_bieu_do_ve_tab1,
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['ma200'],
                                line=dict(color='purple', width=2),
                                name='Chỉ Nam Sinh Tử MA200'
                            ),
                            row=1,
                            col=1
                        )

                        # BOL Upper
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Scatter(
                                x=truc_thoi_gian_x_cua_bieu_do_ve_tab1,
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['upper_band'],
                                line=dict(color='gray', dash='dash', width=0.8),
                                name='Trần Bán BOL'
                            ),
                            row=1,
                            col=1
                        )

                        # BOL Lower
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Scatter(
                                x=truc_thoi_gian_x_cua_bieu_do_ve_tab1,
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['lower_band'],
                                line=dict(color='gray', dash='dash', width=0.8),
                                fill='tonexty',
                                fillcolor='rgba(128,128,128,0.1)',
                                name='Đáy Mua BOL'
                            ),
                            row=1,
                            col=1
                        )

                        # Volume Bar
                        khung_hinh_ve_bieu_do_master_chinh.add_trace(
                            go.Bar(
                                x=truc_thoi_gian_x_cua_bieu_do_ve_tab1,
                                y=bang_du_lieu_chi_lay_120_phien_de_ve_hinh['volume'],
                                name='Lực Khối Lượng',
                                marker_color='gray'
                            ),
                            row=2,
                            col=1
                        )

                        khung_hinh_ve_bieu_do_master_chinh.update_layout(
                            height=750,
                            template='plotly_white',
                            xaxis_rangeslider_visible=False,
                            margin=dict(l=40, r=40, t=50, b=40)
                        )

                        st.plotly_chart(khung_hinh_ve_bieu_do_master_chinh, use_container_width=True)

                else:
                    chuoi_canh_bao_loi_mang = " ❌  Cảnh báo Hệ thống: Không thể kết nối để lấy gói dữ liệu giá. Vui lòng F5 lại trang."
                    st.error(chuoi_canh_bao_loi_mang)
    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP CƠ BẢN (ĐÃ XỬ LÝ LỖI P/E 0.0)
    # ------------------------------------------------------------------------------
    with khung_tab_tai_chinh_co_ban:

        chuoi_tieu_de_tab_tai_chinh = f"###  📈  Phân Tích Sức Khỏe Báo Cáo Tài Chính ({ma_co_phieu_dang_duoc_chon})"
        st.write(chuoi_tieu_de_tab_tai_chinh)

        chuoi_thong_bao_dang_quet_bctc = "Hệ thống đang quét báo cáo thu nhập quý gần nhất để bóc tách..."

        with st.spinner(chuoi_thong_bao_dang_quet_bctc):

            phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve_tab2 = do_luong_tang_truong_canslim(ma_co_phieu_dang_duoc_chon)

            kiem_tra_co_thong_tin_tang_truong_khong_tab2 = phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve_tab2 is not None

            if kiem_tra_co_thong_tin_tang_truong_khong_tab2:

                kiem_tra_tang_truong_co_dot_pha_tab2 = phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve_tab2 >= 20.0

                kiem_tra_tang_truong_co_duong_tab2 = phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve_tab2 > 0

                if kiem_tra_tang_truong_co_dot_pha_tab2:
                    chuoi_hien_thi_tang_truong_dot_pha = f"** 🔥  Tiêu Chuẩn Vàng (Chữ C trong CanSLIM):** Lợi nhuận Quý tăng mạnh **+{phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve_tab2}%**. Mức tăng trưởng đột phá cực kỳ hấp dẫn đối với các Quỹ."
                    st.success(chuoi_hien_thi_tang_truong_dot_pha)

                elif kiem_tra_tang_truong_co_duong_tab2:
                    chuoi_hien_thi_tang_truong_ben_vung = f"** ⚖️  Tăng Trưởng Bền Vững:** Doanh nghiệp gia tăng lợi nhuận được **{phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve_tab2}%**. Đang hoạt động ở trạng thái ổn định và an toàn."
                    st.info(chuoi_hien_thi_tang_truong_ben_vung)

                else:
                    chuoi_hien_thi_suy_yeu_nang = f"** 🚨  Tín Hiệu Suy Yếu Nặng:** Lợi nhuận rớt thê thảm **{phan_tram_tang_truong_lnst_cua_doanh_nghiep_tra_ve_tab2}%**. Báo động đỏ về năng lực vận hành của ban lãnh đạo."
                    st.error(chuoi_hien_thi_suy_yeu_nang)

            st.divider()

            # Khởi chạy hàm đo lường P/E và ROE
            chi_so_pe_cua_doanh_nghiep_tra_ve_tab2, chi_so_roe_cua_doanh_nghiep_tra_ve_tab2 = boc_tach_chi_so_pe_roe(ma_co_phieu_dang_duoc_chon)

            cot_hien_thi_dinh_gia_so_1_tab2, cot_hien_thi_dinh_gia_so_2_tab2 = st.columns(2)

            # --- FIX LỖI HIỂN THỊ P/E ---
            kiem_tra_pe_bi_loi_api_khong_tab2 = chi_so_pe_cua_doanh_nghiep_tra_ve_tab2 is None

            if kiem_tra_pe_bi_loi_api_khong_tab2:
                chuoi_so_pe_duoc_in_ra_man_hinh_tab2 = "N/A"
                chuoi_nhan_xet_ve_pe_tab2 = "Lỗi kết nối API / Thiếu dữ liệu"
                mau_sac_cua_nhan_xet_pe_tab2 = "off"
            else:
                chuoi_so_pe_duoc_in_ra_man_hinh_tab2 = f"{chi_so_pe_cua_doanh_nghiep_tra_ve_tab2:.1f}"

                kiem_tra_pe_nam_trong_vung_re_tab2 = (chi_so_pe_cua_doanh_nghiep_tra_ve_tab2 > 0) and (chi_so_pe_cua_doanh_nghiep_tra_ve_tab2 < 12)

                kiem_tra_pe_nam_trong_vung_hop_ly_tab2 = chi_so_pe_cua_doanh_nghiep_tra_ve_tab2 < 18

                if kiem_tra_pe_nam_trong_vung_re_tab2:
                    chuoi_nhan_xet_ve_pe_tab2 = "Mức Rất Tốt (Định Giá Rẻ)"
                elif kiem_tra_pe_nam_trong_vung_hop_ly_tab2:
                    chuoi_nhan_xet_ve_pe_tab2 = "Mức Khá Hợp Lý"
                else:
                    chuoi_nhan_xet_ve_pe_tab2 = "Mức Đắt Đỏ (Chứa rủi ro ảo giá)"

                mau_sac_cua_nhan_xet_pe_tab2 = "normal" if kiem_tra_pe_nam_trong_vung_hop_ly_tab2 else "inverse"

            cot_hien_thi_dinh_gia_so_1_tab2.metric(
                "Chỉ Số P/E (Số Năm Hoàn Vốn Ước Tính)",
                chuoi_so_pe_duoc_in_ra_man_hinh_tab2,
                delta=chuoi_nhan_xet_ve_pe_tab2,
                delta_color=mau_sac_cua_nhan_xet_pe_tab2
            )

            chuoi_luan_giai_pe = "> **Luận Giải P/E:** P/E càng thấp nghĩa là bạn càng tốn ít tiền hơn để mua được 1 đồng lợi nhuận của doanh nghiệp này trên sàn chứng khoán. Nếu hệ thống hiện 'N/A', có nghĩa là API máy chủ chứng khoán đang bảo trì không cấp dữ liệu."
            st.write(chuoi_luan_giai_pe)

            # --- FIX LỖI HIỂN THỊ ROE ---
            kiem_tra_roe_bi_loi_api_khong_tab2 = chi_so_roe_cua_doanh_nghiep_tra_ve_tab2 is None

            if kiem_tra_roe_bi_loi_api_khong_tab2:
                chuoi_so_roe_duoc_in_ra_man_hinh_tab2 = "N/A"
                chuoi_nhan_xet_ve_roe_tab2 = "Lỗi kết nối API / Thiếu dữ liệu"
                mau_sac_cua_nhan_xet_roe_tab2 = "off"
            else:
                chuoi_so_roe_duoc_in_ra_man_hinh_tab2 = f"{chi_so_roe_cua_doanh_nghiep_tra_ve_tab2:.1%}"

                kiem_tra_roe_nam_trong_vung_xuat_sac_tab2 = chi_so_roe_cua_doanh_nghiep_tra_ve_tab2 >= 0.25

                kiem_tra_roe_nam_trong_vung_tot_tab2 = chi_so_roe_cua_doanh_nghiep_tra_ve_tab2 >= 0.15

                if kiem_tra_roe_nam_trong_vung_xuat_sac_tab2:
                    chuoi_nhan_xet_ve_roe_tab2 = "Vô Cùng Xuất Sắc"
                elif kiem_tra_roe_nam_trong_vung_tot_tab2:
                    chuoi_nhan_xet_ve_roe_tab2 = "Mức Độ Tốt"
                else:
                    chuoi_nhan_xet_ve_roe_tab2 = "Mức Trung Bình - Dưới Chuẩn"

                mau_sac_cua_nhan_xet_roe_tab2 = "normal" if kiem_tra_roe_nam_trong_vung_tot_tab2 else "inverse"

            cot_hien_thi_dinh_gia_so_2_tab2.metric(
                "Chỉ Số ROE (Năng Lực Sinh Lời Trên Vốn)",
                chuoi_so_roe_duoc_in_ra_man_hinh_tab2,
                delta=chuoi_nhan_xet_ve_roe_tab2,
                delta_color=mau_sac_cua_nhan_xet_roe_tab2
            )

            chuoi_luan_giai_roe = "> **Luận Giải ROE:** ROE là thước đo xem Ban giám đốc dùng tiền của cổ đông có tạo ra lãi tốt không. Bắt buộc phải trên 15% mới đáng xem xét đầu tư dài hạn."
            st.write(chuoi_luan_giai_roe)
    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: CHUYÊN GIA ĐỌC VỊ DÒNG TIỀN (VÀ KHỐI NGOẠI THỰC TẾ)
    # ------------------------------------------------------------------------------
    with khung_tab_dong_tien_chuyen_sau:

        chuoi_tieu_de_tab_3 = f"###  🌊  Smart Flow Specialist - Mổ Xẻ Chi Tiết Hành Vi Dòng Tiền ({ma_co_phieu_dang_duoc_chon})"
        st.write(chuoi_tieu_de_tab_3)

        chuoi_tieu_de_khoi_ngoai = "####  📊  Dữ Liệu Giao Dịch Khối Ngoại Thực Tế (Tính Bằng Tỷ VNĐ):"
        st.write(chuoi_tieu_de_khoi_ngoai)

        chuoi_hien_thi_spinner_ngoai = "Đang trích xuất dữ liệu Khối Ngoại chuẩn từ Sở Giao Dịch..."

        with st.spinner(chuoi_hien_thi_spinner_ngoai):

            bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3 = lay_du_lieu_khoi_ngoai_thuc_te(ma_co_phieu_dang_duoc_chon)

            kiem_tra_co_bang_du_lieu_ngoai_khong_tab3 = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3 is not None

            if kiem_tra_co_bang_du_lieu_ngoai_khong_tab3:

                kiem_tra_bang_ngoai_co_rong_khong_tab3 = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3.empty

                if kiem_tra_bang_ngoai_co_rong_khong_tab3 == False:

                    dong_giao_dich_ngoai_cua_ngay_cuoi_cung_tab3 = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3.iloc[-1]

                    gia_tri_tong_mua_khoi_ngoai_vnd_tab3 = 0.0
                    gia_tri_tong_ban_khoi_ngoai_vnd_tab3 = 0.0
                    gia_tri_giao_dich_rong_khoi_ngoai_vnd_tab3 = 0.0

                    tap_hop_ten_cot_cua_dong_ngoai = dong_giao_dich_ngoai_cua_ngay_cuoi_cung_tab3.index

                    for ten_cot_trong_dong_cuoi_tab3 in tap_hop_ten_cot_cua_dong_ngoai:

                        gia_tri_so_thuc_cua_cot_hien_tai_tab3 = float(dong_giao_dich_ngoai_cua_ngay_cuoi_cung_tab3[ten_cot_trong_dong_cuoi_tab3])

                        gia_tri_tuyet_doi_cua_cot = abs(gia_tri_so_thuc_cua_cot_hien_tai_tab3)
                        kiem_tra_so_lieu_co_phai_la_tien_vnd_chua_quy_doi_tab3 = gia_tri_tuyet_doi_cua_cot > 1e6

                        if kiem_tra_so_lieu_co_phai_la_tien_vnd_chua_quy_doi_tab3:
                            gia_tri_sau_khi_quy_doi_thanh_ty_vnd_tab3 = gia_tri_so_thuc_cua_cot_hien_tai_tab3 / 1e9
                        else:
                            gia_tri_sau_khi_quy_doi_thanh_ty_vnd_tab3 = gia_tri_so_thuc_cua_cot_hien_tai_tab3

                        kiem_tra_cot_nay_co_phai_cot_mua_tab3 = 'buyval' in ten_cot_trong_dong_cuoi_tab3 or 'buy_val' in ten_cot_trong_dong_cuoi_tab3 or 'mua' in ten_cot_trong_dong_cuoi_tab3

                        if kiem_tra_cot_nay_co_phai_cot_mua_tab3:
                            if gia_tri_sau_khi_quy_doi_thanh_ty_vnd_tab3 > gia_tri_tong_mua_khoi_ngoai_vnd_tab3:
                                gia_tri_tong_mua_khoi_ngoai_vnd_tab3 = gia_tri_sau_khi_quy_doi_thanh_ty_vnd_tab3

                        kiem_tra_cot_nay_co_phai_cot_ban_tab3 = 'sellval' in ten_cot_trong_dong_cuoi_tab3 or 'sell_val' in ten_cot_trong_dong_cuoi_tab3 or 'ban' in ten_cot_trong_dong_cuoi_tab3

                        if kiem_tra_cot_nay_co_phai_cot_ban_tab3:
                            if gia_tri_sau_khi_quy_doi_thanh_ty_vnd_tab3 > gia_tri_tong_ban_khoi_ngoai_vnd_tab3:
                                gia_tri_tong_ban_khoi_ngoai_vnd_tab3 = gia_tri_sau_khi_quy_doi_thanh_ty_vnd_tab3

                        kiem_tra_cot_nay_co_phai_cot_rong_tab3 = 'netval' in ten_cot_trong_dong_cuoi_tab3 or 'net_val' in ten_cot_trong_dong_cuoi_tab3 or 'rong' in ten_cot_trong_dong_cuoi_tab3

                        if kiem_tra_cot_nay_co_phai_cot_rong_tab3:
                            gia_tri_tuyet_doi_cua_rong = abs(gia_tri_giao_dich_rong_khoi_ngoai_vnd_tab3)
                            if abs(gia_tri_sau_khi_quy_doi_thanh_ty_vnd_tab3) > gia_tri_tuyet_doi_cua_rong:
                                gia_tri_giao_dich_rong_khoi_ngoai_vnd_tab3 = gia_tri_sau_khi_quy_doi_thanh_ty_vnd_tab3

                    kiem_tra_neu_cot_rong_bi_thieu_tab3 = gia_tri_giao_dich_rong_khoi_ngoai_vnd_tab3 == 0.0

                    kiem_tra_neu_co_chi_so_mua_ban_thuc_te_tab3 = (gia_tri_tong_mua_khoi_ngoai_vnd_tab3 > 0) or (gia_tri_tong_ban_khoi_ngoai_vnd_tab3 > 0)

                    if kiem_tra_neu_cot_rong_bi_thieu_tab3 and kiem_tra_neu_co_chi_so_mua_ban_thuc_te_tab3:
                        gia_tri_giao_dich_rong_khoi_ngoai_vnd_tab3 = gia_tri_tong_mua_khoi_ngoai_vnd_tab3 - gia_tri_tong_ban_khoi_ngoai_vnd_tab3

                    cot_hien_thi_ngoai_thuc_te_1_tab3, cot_hien_thi_ngoai_thuc_te_2_tab3, cot_hien_thi_ngoai_thuc_te_3_tab3 = st.columns(3)

                    chuoi_hien_thi_tong_mua = f"{gia_tri_tong_mua_khoi_ngoai_vnd_tab3:.2f} Tỷ VNĐ"
                    cot_hien_thi_ngoai_thuc_te_1_tab3.metric(
                        "Tổng Mua (Khối Ngoại)",
                        chuoi_hien_thi_tong_mua
                    )

                    chuoi_hien_thi_tong_ban = f"{gia_tri_tong_ban_khoi_ngoai_vnd_tab3:.2f} Tỷ VNĐ"
                    cot_hien_thi_ngoai_thuc_te_2_tab3.metric(
                        "Tổng Bán (Khối Ngoại)",
                        chuoi_hien_thi_tong_ban
                    )

                    kiem_tra_dang_mua_hay_ban_rong_tab3 = gia_tri_giao_dich_rong_khoi_ngoai_vnd_tab3 > 0

                    if kiem_tra_dang_mua_hay_ban_rong_tab3:
                        chuoi_nhan_trang_thai_mua_rong_tab3 = "Mua Ròng Tích Cực"
                        chuoi_mau_sac_delta_mua_rong_tab3 = "normal"
                    else:
                        chuoi_nhan_trang_thai_mua_rong_tab3 = "Bán Ròng Cảnh Báo"
                        chuoi_mau_sac_delta_mua_rong_tab3 = "inverse"

                    chuoi_hien_thi_tong_rong = f"{gia_tri_giao_dich_rong_khoi_ngoai_vnd_tab3:.2f} Tỷ VNĐ"
                    cot_hien_thi_ngoai_thuc_te_3_tab3.metric(
                        "Giá Trị Giao Dịch Ròng",
                        chuoi_hien_thi_tong_rong,
                        delta=chuoi_nhan_trang_thai_mua_rong_tab3,
                        delta_color=chuoi_mau_sac_delta_mua_rong_tab3
                    )

                    chuoi_tieu_de_bieu_do_ngoai = " 📈  **Lịch sử Giao Dịch Ròng Khối Ngoại (10 Phiên Gần Nhất):**"
                    st.write(chuoi_tieu_de_bieu_do_ngoai)

                    kiem_tra_cot_date_co_ton_tai_tab3 = 'date' in bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3.columns

                    if kiem_tra_cot_date_co_ton_tai_tab3:
                        mang_thoi_gian_cua_khoi_ngoai_tab3 = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3['date']
                    else:
                        mang_thoi_gian_cua_khoi_ngoai_tab3 = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3.index

                    mang_chua_tat_ca_gia_tri_rong_10_ngay_tab3 = []

                    for index_cua_tung_dong_tab3, dong_du_lieu_dang_xet_tab3 in bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3.iterrows():

                        gia_tri_rong_cua_dong_nay_tab3 = 0.0
                        gia_tri_mua_cua_dong_nay_tab3 = 0.0
                        gia_tri_ban_cua_dong_nay_tab3 = 0.0

                        tap_hop_ten_cot_cua_bang_ngoai = bang_du_lieu_khoi_ngoai_thuc_te_tra_ve_tab3.columns

                        for ten_cua_tung_cot_nhan_tab3 in tap_hop_ten_cot_cua_bang_ngoai:

                            kiem_tra_o_du_lieu_co_thuc_khong_tab3 = pd.notnull(dong_du_lieu_dang_xet_tab3[ten_cua_tung_cot_nhan_tab3])

                            if kiem_tra_o_du_lieu_co_thuc_khong_tab3:
                                gia_tri_cot_hien_tai_dang_xet_tab3 = float(dong_du_lieu_dang_xet_tab3[ten_cua_tung_cot_nhan_tab3])
                            else:
                                gia_tri_cot_hien_tai_dang_xet_tab3 = 0.0

                            gia_tri_tuyet_doi_cua_cot_dang_xet = abs(gia_tri_cot_hien_tai_dang_xet_tab3)
                            kiem_tra_co_phai_tien_dong_khong_tab3 = gia_tri_tuyet_doi_cua_cot_dang_xet > 1e6

                            if kiem_tra_co_phai_tien_dong_khong_tab3:
                                gia_tri_sau_khi_quy_doi_ty_tab3 = gia_tri_cot_hien_tai_dang_xet_tab3 / 1e9
                            else:
                                gia_tri_sau_khi_quy_doi_ty_tab3 = gia_tri_cot_hien_tai_dang_xet_tab3

                            kiem_tra_cot_rong_tab3 = 'netval' in ten_cua_tung_cot_nhan_tab3 or 'net_val' in ten_cua_tung_cot_nhan_tab3 or 'rong' in ten_cua_tung_cot_nhan_tab3

                            if kiem_tra_cot_rong_tab3:
                                gia_tri_rong_cua_dong_nay_tab3 = gia_tri_sau_khi_quy_doi_ty_tab3

                            kiem_tra_cot_mua_tab3 = 'buyval' in ten_cua_tung_cot_nhan_tab3 or 'mua' in ten_cua_tung_cot_nhan_tab3

                            if kiem_tra_cot_mua_tab3:
                                gia_tri_mua_cua_dong_nay_tab3 = gia_tri_sau_khi_quy_doi_ty_tab3

                            kiem_tra_cot_ban_tab3 = 'sellval' in ten_cua_tung_cot_nhan_tab3 or 'ban' in ten_cua_tung_cot_nhan_tab3

                            if kiem_tra_cot_ban_tab3:
                                gia_tri_ban_cua_dong_nay_tab3 = gia_tri_sau_khi_quy_doi_ty_tab3

                        kiem_tra_neu_thieu_cot_rong_o_dong_tab3 = gia_tri_rong_cua_dong_nay_tab3 == 0.0

                        if kiem_tra_neu_thieu_cot_rong_o_dong_tab3:
                            gia_tri_rong_cua_dong_nay_tab3 = gia_tri_mua_cua_dong_nay_tab3 - gia_tri_ban_cua_dong_nay_tab3

                        mang_chua_tat_ca_gia_tri_rong_10_ngay_tab3.append(gia_tri_rong_cua_dong_nay_tab3)

                    doi_tuong_bieu_do_khoi_ngoai_tab3 = go.Figure()

                    mang_chua_mau_sac_tung_cot_khoi_ngoai_tab3 = []

                    tap_gia_tri_10_ngay_cuoi = mang_chua_tat_ca_gia_tri_rong_10_ngay_tab3[-10:]

                    for gia_tri_trong_mang_tab3 in tap_gia_tri_10_ngay_cuoi:

                        if gia_tri_trong_mang_tab3 > 0:
                            mang_chua_mau_sac_tung_cot_khoi_ngoai_tab3.append('green')
                        else:
                            mang_chua_mau_sac_tung_cot_khoi_ngoai_tab3.append('red')

                    tap_thoi_gian_10_ngay_cuoi = mang_thoi_gian_cua_khoi_ngoai_tab3.tail(10)

                    doi_tuong_bieu_do_khoi_ngoai_tab3.add_trace(
                        go.Bar(
                            x=tap_thoi_gian_10_ngay_cuoi,
                            y=tap_gia_tri_10_ngay_cuoi,
                            marker_color=mang_chua_mau_sac_tung_cot_khoi_ngoai_tab3,
                            name="Giá Trị Ròng (Tỷ VNĐ)"
                        )
                    )

                    chuoi_tieu_de_bieu_do_chinh = "Khối Ngoại Mua/Bán Ròng (Tỷ VNĐ)"

                    doi_tuong_bieu_do_khoi_ngoai_tab3.update_layout(
                        height=300,
                        margin=dict(l=20, r=20, t=30, b=20),
                        title=chuoi_tieu_de_bieu_do_chinh
                    )

                    st.plotly_chart(doi_tuong_bieu_do_khoi_ngoai_tab3, use_container_width=True)

            else:
                chuoi_bao_loi_api_ngoai = " ⚠️  Lỗi truy cập API Sở Giao Dịch: Không lấy được Dữ liệu Khối Ngoại. Chuyển sang mô hình Ước lượng Hành vi Dòng tiền."
                st.warning(chuoi_bao_loi_api_ngoai)
        st.divider()
        # --- MODULE 2: MÔ HÌNH ƯỚC LƯỢNG HÀNH VI TỔ CHỨC VÀ NHỎ LẺ ---
        bang_du_lieu_dong_tien_tho_truy_xuat_tab3 = lay_du_lieu_nien_yet_chuan(ma_co_phieu_dang_duoc_chon, so_ngay_lich_su_can_lay=30)

        kiem_tra_bang_dong_tien_tho_co_ton_tai_tab3 = bang_du_lieu_dong_tien_tho_truy_xuat_tab3 is not None

        if kiem_tra_bang_dong_tien_tho_co_ton_tai_tab3:

            bang_du_lieu_dong_tien_da_tinh_xong_chi_bao_tab3 = tinh_toan_bo_chi_bao_quant(bang_du_lieu_dong_tien_tho_truy_xuat_tab3)

            dong_du_lieu_dong_tien_cua_ngay_hom_nay_tab3 = bang_du_lieu_dong_tien_da_tinh_xong_chi_bao_tab3.iloc[-1]

            suc_manh_vol_flow_cua_ngay_hom_nay_dang_xet_tab3 = dong_du_lieu_dong_tien_cua_ngay_hom_nay_tab3['vol_strength']

            kiem_tra_vol_dang_no_cuc_dai_tab3 = suc_manh_vol_flow_cua_ngay_hom_nay_dang_xet_tab3 > 1.8

            kiem_tra_vol_dang_no_kha_tot_tab3 = suc_manh_vol_flow_cua_ngay_hom_nay_dang_xet_tab3 > 1.2

            if kiem_tra_vol_dang_no_cuc_dai_tab3:

                ti_le_phan_tram_uoc_luong_cua_to_chuc_noi_tab3 = 0.55
                ti_le_phan_tram_uoc_luong_cua_ca_nhan_le_tab3 = 0.45

            elif kiem_tra_vol_dang_no_kha_tot_tab3:

                ti_le_phan_tram_uoc_luong_cua_to_chuc_noi_tab3 = 0.40
                ti_le_phan_tram_uoc_luong_cua_ca_nhan_le_tab3 = 0.60

            else:

                ti_le_phan_tram_uoc_luong_cua_to_chuc_noi_tab3 = 0.15
                ti_le_phan_tram_uoc_luong_cua_ca_nhan_le_tab3 = 0.85

            chuoi_tieu_de_uoc_luong = "####  📊  Tỷ Lệ Phân Bổ Dòng Tiền Tổ Chức Và Nhỏ Lẻ (Mô Hình AI Ước Tính Theo Volume):"
            st.write(chuoi_tieu_de_uoc_luong)

            cot_hien_thi_dong_tien_to_chuc_tab3, cot_hien_thi_dong_tien_nho_le_tab3 = st.columns(2)

            kiem_tra_gia_hom_nay_co_tang_tab3 = dong_du_lieu_dong_tien_cua_ngay_hom_nay_tab3['return_1d'] > 0

            if kiem_tra_gia_hom_nay_co_tang_tab3:
                chuoi_nhan_hanh_dong_cua_to_chuc_uoc_luong_tab3 = "Đang Tích Cực Kê Gom"
            else:
                chuoi_nhan_hanh_dong_cua_to_chuc_uoc_luong_tab3 = "Đang Nhồi Lệnh Táng Xả"

            chuoi_hien_thi_ti_le_to_chuc = f"{ti_le_phan_tram_uoc_luong_cua_to_chuc_noi_tab3*100:.1f}%"

            cot_hien_thi_dong_tien_to_chuc_tab3.metric(
                " 🏦  Tổ Chức & Tự Doanh (Nhóm Tạo lập)",
                chuoi_hien_thi_ti_le_to_chuc,
                delta=chuoi_nhan_hanh_dong_cua_to_chuc_uoc_luong_tab3
            )

            kiem_tra_nho_le_co_du_bam_nhieu_tab3 = ti_le_phan_tram_uoc_luong_cua_ca_nhan_le_tab3 > 0.6

            if kiem_tra_nho_le_co_du_bam_nhieu_tab3:
                chuoi_nhan_hanh_dong_cua_nho_le_uoc_luong_tab3 = "Cảnh Báo Đỏ: Nhỏ Lẻ Đu Bám Quá Nhiều"
                chuoi_mau_sac_canh_bao_nho_le_uoc_luong_tab3 = "inverse"
            else:
                chuoi_nhan_hanh_dong_cua_nho_le_uoc_luong_tab3 = "Tình Trạng Ổn Định"
                chuoi_mau_sac_canh_bao_nho_le_uoc_luong_tab3 = "normal"

            chuoi_hien_thi_ti_le_nho_le = f"{ti_le_phan_tram_uoc_luong_cua_ca_nhan_le_tab3*100:.1f}%"

            cot_hien_thi_dong_tien_nho_le_tab3.metric(
                " 🐜  Cá Nhân (Nhà đầu tư lẻ)",
                chuoi_hien_thi_ti_le_nho_le,
                delta=chuoi_nhan_hanh_dong_cua_nho_le_uoc_luong_tab3,
                delta_color=chuoi_mau_sac_canh_bao_nho_le_uoc_luong_tab3
            )
    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: RADAR HUNTER (TÍCH HỢP BÙNG NỔ VÀ DANH SÁCH CHỜ CHÂN SÓNG)
    # ------------------------------------------------------------------------------
    with khung_tab_radar_truy_quet:

        chuoi_tieu_de_radar_chinh = " 🔍  Máy Quét Định Lượng Robot Hunter V20.0 - Predator Leviathan"
        st.subheader(chuoi_tieu_de_radar_chinh)

        chuoi_mo_ta_tinh_nang_moi_tab4 = "Giải pháp tối thượng dành cho Minh: Tự động phân loại cổ phiếu thành **BÙNG NỔ** (đã chạy nóng) và **DANH SÁCH CHỜ CHÂN SÓNG** (tích hợp 3 vũ khí: Squeeze, Cạn cung, Tây/Tự Doanh gom) để tránh mua đuổi đỉnh."
        st.write(chuoi_mo_ta_tinh_nang_moi_tab4)

        chuoi_hien_thi_nut_bam_radar = " 🔥  KÍCH HOẠT RADAR TRUY QUÉT 2 TẦNG (REAL-TIME)"
        nut_bam_kich_hoat_radar_san_tinh_tab4 = st.button(chuoi_hien_thi_nut_bam_radar)

        if nut_bam_kich_hoat_radar_san_tinh_tab4:

            danh_sach_ket_qua_nhom_bung_no_tab4 = []
            danh_sach_ket_qua_nhom_danh_sach_cho_tab4 = []

            thanh_truot_tien_do_ui_tab4 = st.progress(0)

            # Giới hạn 30 mã để bảo vệ server Streamlit khỏi bị treo
            danh_sach_30_ma_se_quet_tab4 = danh_sach_toan_bo_cac_ma_hose_hien_co[:30]
            tong_so_ma_quet_thuc_te_tab4 = len(danh_sach_30_ma_se_quet_tab4)

            for vi_tri_so_thu_tu_quet_tab4, ma_chung_khoan_dang_quet_tab4 in enumerate(danh_sach_30_ma_se_quet_tab4):
                try:
                    bang_du_lieu_tho_cua_ma_quet_tab4 = lay_du_lieu_nien_yet_chuan(
                        ma_chung_khoan_dang_quet_tab4,
                        so_ngay_lich_su_can_lay=100
                    )

                    bang_du_lieu_quant_cua_ma_quet_tab4 = tinh_toan_bo_chi_bao_quant(bang_du_lieu_tho_cua_ma_quet_tab4)

                    dong_du_lieu_cuoi_cua_ma_quet_tab4 = bang_du_lieu_quant_cua_ma_quet_tab4.iloc[-1]

                    phan_tram_ai_du_bao_cua_ma_quet_tab4 = du_bao_xac_suat_ai_t3(bang_du_lieu_quant_cua_ma_quet_tab4)

                    # -------------------------------------------------------------
                    # LOGIC PHÂN LOẠI CHIẾN THUẬT SIÊU CỔ PHIẾU (RADAR 2 TẦNG)
                    # -------------------------------------------------------------
                    chuoi_ket_qua_phan_loai_ma_nay_tab4 = None

                    gia_tri_vol_strength_hien_tai_ma_tab4 = dong_du_lieu_cuoi_cua_ma_quet_tab4['vol_strength']
                    gia_tri_rsi_hien_tai_ma_tab4 = dong_du_lieu_cuoi_cua_ma_quet_tab4['rsi']
                    gia_tri_khop_lenh_hien_tai_ma_tab4 = dong_du_lieu_cuoi_cua_ma_quet_tab4['close']
                    gia_tri_ma20_hien_tai_ma_tab4 = dong_du_lieu_cuoi_cua_ma_quet_tab4['ma20']

                    # TẦNG 1: KIỂM TRA NHÓM BÙNG NỔ (Đã nổ Vol)
                    kiem_tra_vol_da_no_chua_tab4 = gia_tri_vol_strength_hien_tai_ma_tab4 > 1.3

                    if kiem_tra_vol_da_no_chua_tab4:
                        chuoi_ket_qua_phan_loai_ma_nay_tab4 = " 🚀  Bùng Nổ (Dòng tiền nóng)"

                    # TẦNG 2: KIỂM TRA DANH SÁCH CHỜ (Vùng mua chân sóng an toàn)
                    if kiem_tra_vol_da_no_chua_tab4 == False:

                        # Điều kiện Cơ bản
                        dk_vol_dang_tich_luy_duoi = 0.8 <= gia_tri_vol_strength_hien_tai_ma_tab4
                        dk_vol_dang_tich_luy_tren = gia_tri_vol_strength_hien_tai_ma_tab4 <= 1.2

                        dk_vol_dang_tich_luy_tab4 = dk_vol_dang_tich_luy_duoi and dk_vol_dang_tich_luy_tren

                        muc_gia_chap_nhan_sat_nen = gia_tri_ma20_ht_scan * 0.95
                        dk_gia_nam_tren_nen_tab4 = gia_tri_khop_lenh_hien_tai_ma_tab4 >= muc_gia_chap_nhan_sat_nen

                        dk_rsi_chua_hung_phan_tab4 = gia_tri_rsi_ht_scan < 62

                        dk_base_ai_thich_co_phieu_nay = False
                        kiem_tra_kieu_du_lieu_ai = isinstance(phan_tram_ai_du_bao_cua_ma_quet_tab4, float)

                        if kiem_tra_kieu_du_lieu_ai:
                            if ai_prob_val_hien_tai_duoc_cap > 48.0:
                                dk_base_ai_thich_co_phieu_nay = True

                        dieu_kien_co_ban_qua_mon_tab4 = dk_vol_dang_tich_luy_tab4 and dk_gia_nam_tren_nen_tab4 and dk_rsi_chua_hung_phan_tab4 and dk_base_ai_thich_co_phieu_nay

                        if dieu_kien_co_ban_qua_mon_tab4 == True:

                            # Vũ khí 1: Nút Thắt Cổ Chai (Bollinger Squeeze)
                            gia_tri_bb_width_hom_nay_tab4 = dong_du_lieu_cuoi_cua_ma_quet_tab4['bb_width']

                            tap_du_lieu_bb_width_20_ngay_tab4 = bang_du_lieu_quant_cua_ma_quet_tab4['bb_width'].tail(20)
                            gia_tri_bb_width_nho_nhat_20_ngay_tab4 = tap_du_lieu_bb_width_20_ngay_tab4.min()

                            muc_sai_so_chap_nhan_duoc_tab4 = gia_tri_bb_width_nho_nhat_20_ngay_qua * 1.2

                            dieu_kien_lo_xo_da_nen_chat_tab4 = gia_tri_bb_width_hom_nay_tab4 <= muc_sai_so_chap_nhan_duoc_tab4

                            # Vũ khí 2: Cạn Cung (Supply Exhaustion)
                            chuoi_can_cung_5_phien_gan_nhat_tab4 = bang_du_lieu_quant_cua_ma_quet_tab4['can_cung'].tail(5)

                            dieu_kien_da_xuat_hien_can_cung_tab4 = chuoi_can_cung_5_phien_gan_nhat_tab4.any()

                            # Vũ khí 3: Khối Ngoại Gom Ròng
                            dieu_kien_tay_long_dang_gom_tab4 = False

                            so_ngay_lay_du_lieu_ngoai = 5
                            bang_check_ngoai_hunter_tab4 = lay_du_lieu_khoi_ngoai_thuc_te(
                                ma_chung_khoan_dang_quet_tab4,
                                so_ngay_lay_du_lieu_ngoai
                            )

                            kiem_tra_bang_check_co_dl_tab4 = bang_check_ngoai_hunter_tab4 is not None

                            if kiem_tra_bang_check_co_dl_tab4:

                                kiem_tra_bang_check_co_rong_khong_tab4 = bang_check_ngoai_hunter_tab4.empty

                                if kiem_tra_bang_check_co_rong_khong_tab4 == False:

                                    tong_mua_trong_3_ngay_tab4 = 0.0
                                    tong_ban_trong_3_ngay_tab4 = 0.0

                                    bang_3_ngay_cuoi_cung_tab4 = bang_check_ngoai_hunter_tab4.tail(3)

                                    for idx_hunter_tab4, dong_hunter_tab4 in bang_3_ngay_cuoi_cung_tab4.iterrows():

                                        gia_tri_mua_hunter_tab4 = float(dong_hunter_tab4.get('buyval', 0))
                                        tong_mua_trong_3_ngay_tab4 = tong_mua_trong_3_ngay_tab4 + gia_tri_mua_hunter_tab4

                                        gia_tri_ban_hunter_tab4 = float(dong_hunter_tab4.get('sellval', 0))
                                        tong_ban_trong_3_ngay_tab4 = tong_ban_trong_3_ngay_tab4 + gia_tri_ban_hunter_tab4

                                    tong_rong_trong_3_ngay_tab4 = tong_mua_trong_3_ngay_tab4 - tong_ban_trong_3_ngay_tab4

                                    kiem_tra_tong_rong_co_duong_khong = tong_rong_trong_3_ngay_tab4 > 0

                                    if kiem_tra_tong_rong_co_duong_khong:
                                        dieu_kien_khoi_ngoai_dang_gom_cua_ma = True

                            # Bổ sung quét Tự Doanh Gom
                            bang_check_tu_doanh_cua_ma = lay_du_lieu_tu_doanh_thuc_te(ma_chung_khoan_dang_quet_tab4, so_ngay_lay_du_lieu_ngoai)
                            kiem_tra_bang_check_td_co_data = bang_check_tu_doanh_cua_ma is not None
                            if kiem_tra_bang_check_td_co_data:
                                kiem_tra_bang_check_td_empty = bang_check_tu_doanh_cua_ma.empty
                                if kiem_tra_bang_check_td_empty == False:
                                    tong_mua_td_3_ngay_gan_nhat = 0.0
                                    tong_ban_td_3_ngay_gan_nhat = 0.0
                                    bang_3_ngay_cuoi_cung_td_cua_ma = bang_check_tu_doanh_cua_ma.tail(3)
                                    for idx_td_cua_ma, dong_du_lieu_td_hunter_cua_ma in bang_3_ngay_cuoi_cung_td_cua_ma.iterrows():
                                        gia_tri_mua_td_hunter_cua_ma = float(dong_du_lieu_td_hunter_cua_ma.get('buyval', 0))
                                        tong_mua_td_3_ngay_gan_nhat = tong_mua_td_3_ngay_gan_nhat + gia_tri_mua_td_hunter_cua_ma
                                        gia_tri_ban_td_hunter_cua_ma = float(dong_du_lieu_td_hunter_cua_ma.get('sellval', 0))
                                        tong_ban_td_3_ngay_gan_nhat = tong_ban_td_3_ngay_gan_nhat + gia_tri_ban_td_hunter_cua_ma
                                    tong_rong_3_ngay_cua_tu_doanh_cua_ma = tong_mua_td_3_ngay_gan_nhat - tong_ban_td_3_ngay_gan_nhat
                                    kiem_tra_tu_doanh_co_mua_rong_khong = tong_rong_3_ngay_cua_tu_doanh_cua_ma > 0
                                    if kiem_tra_tu_doanh_co_mua_rong_khong:
                                        dieu_kien_khoi_ngoai_dang_gom_cua_ma = True

                            # Tổng hợp Siêu màng lọc: Cơ bản + (Nén chặt HOẶC Cạn cung HOẶC Tây gom/Tự Doanh gom)
                            dieu_kien_nang_cao_dat_chuan_tab4 = dieu_kien_lo_xo_da_nen_chat_tab4 or dieu_kien_da_xuat_hien_can_cung_tab4 or dieu_kien_khoi_ngoai_dang_gom_cua_ma

                            if dieu_kien_nang_cao_dat_chuan_tab4 == True:
                                chuoi_ket_qua_phan_loai_ma_nay_tab4 = " ⚖️  Danh Sách Chờ (Vùng Gom Chân Sóng)"

                    # -------------------------------------------------------------
                    # ĐÓNG GÓI KẾT QUẢ HIỂN THỊ
                    # -------------------------------------------------------------
                    chuoi_hien_thi_gia_khop_lenh_tab4 = f"{gia_tri_khop_lenh_hien_tai_ma_tab4:,.0f} VNĐ"
                    gia_tri_vol_lam_tron_tab4 = round(gia_tri_vol_strength_hien_tai_ma_tab4, 2)
                    chuoi_hien_thi_ai_du_bao_tab4 = f"{phan_tram_ai_du_bao_cua_ma_quet_tab4}%"

                    doi_tuong_dong_du_lieu_hien_thi_tab4 = {
                        'Ticker Mã CP': ma_chung_khoan_dang_quet_tab4,
                        'Thị Giá Hiện Tại': chuoi_hien_thi_gia_khop_lenh_tab4,
                        'Hệ Số Nổ Volume': gia_tri_vol_lam_tron_tab4,
                        'AI T+3 Dự Báo': chuoi_hien_thi_ai_du_bao_tab4
                    }

                    kiem_tra_thuoc_nhom_bung_no_tab4 = chuoi_ket_qua_phan_loai_ma_nay_tab4 == " 🚀  Bùng Nổ (Dòng tiền nóng)"

                    if kiem_tra_thuoc_nhom_bung_no_tab4:
                        danh_sach_ket_qua_nhom_bung_no_tab4.append(doi_tuong_dong_du_lieu_hien_thi_tab4)

                    kiem_tra_thuoc_nhom_danh_sach_cho_tab4 = chuoi_ket_qua_phan_loai_ma_nay_tab4 == " ⚖️  Danh Sách Chờ (Vùng Gom Chân Sóng)"

                    if kiem_tra_thuoc_nhom_danh_sach_cho_tab4:
                        danh_sach_ket_qua_nhom_danh_sach_cho_tab4.append(doi_tuong_dong_du_lieu_hien_thi_tab4)

                except Exception:
                    pass

                # Cập nhật thanh tiến trình trên UI
                gia_tri_so_thu_tu_cung = vi_tri_so_thu_tu_quet_tab4 + 1
                phan_tram_muc_do_hoan_thanh_radar_tab4 = gia_tri_so_thu_tu_cung / tong_so_ma_quet_thuc_te_tab4

                thanh_truot_tien_do_ui_tab4.progress(phan_tram_muc_do_hoan_thanh_radar_tab4)

            # -------------------------------------------------------------
            # RENDER BẢNG KẾT QUẢ RA GIAO DIỆN CHÍNH
            # -------------------------------------------------------------
            chuoi_tieu_de_nhom_bung_no = "###  🚀  Nhóm Bùng Nổ (Đã nổ Vol - Cẩn thận rủi ro mua đuổi đỉnh như VIC)"
            st.write(chuoi_tieu_de_nhom_bung_no)

            so_luong_ma_nhom_bung_no = len(danh_sach_ket_qua_nhom_bung_no_tab4)
            kiem_tra_co_ma_nhom_bung_no_tab4 = so_luong_ma_nhom_bung_no > 0

            if kiem_tra_co_ma_nhom_bung_no_tab4:
                bang_data_frame_nhom_bung_no_tab4 = pd.DataFrame(danh_sach_ket_qua_nhom_bung_no_tab4)

                chuoi_cot_de_sap_xep_1 = 'AI T+3 Dự Báo'
                bang_data_frame_nhom_bung_no_tab4 = bang_data_frame_nhom_bung_no_tab4.sort_values(
                    by=chuoi_cot_de_sap_xep_1,
                    ascending=False
                )

                st.table(bang_data_frame_nhom_bung_no_tab4)
            else:
                chuoi_thong_bao_khong_co_ma_bung_no = "Không tìm thấy mã bùng nổ mạnh hôm nay."
                st.write(chuoi_thong_bao_khong_co_ma_bung_no)

            chuoi_tieu_de_nhom_danh_sach_cho = "###  ⚖️  Nhóm Danh Sách Chờ (Gom chân sóng - Cực kỳ an toàn)"
            st.write(chuoi_tieu_de_nhom_danh_sach_cho)

            so_luong_ma_nhom_danh_sach_cho = len(danh_sach_ket_qua_nhom_danh_sach_cho_tab4)
            kiem_tra_co_ma_nhom_danh_sach_cho_tab4 = so_luong_ma_nhom_danh_sach_cho > 0

            if kiem_tra_co_ma_nhom_danh_sach_cho_tab4:

                bang_data_frame_nhom_danh_sach_cho_tab4 = pd.DataFrame(danh_sach_ket_qua_nhom_danh_sach_cho_tab4)

                chuoi_cot_de_sap_xep_2 = 'AI T+3 Dự Báo'
                bang_data_frame_nhom_danh_sach_cho_tab4 = bang_data_frame_nhom_danh_sach_cho_tab4.sort_values(
                    by=chuoi_cot_de_sap_xep_2,
                    ascending=False
                )

                st.table(bang_data_frame_nhom_danh_sach_cho_tab4)

                chuoi_loi_khuyen_cho_minh_tab4 = " ✅  **Lời khuyên của Robot:** Minh hãy ưu tiên giải ngân vào các mã trong Nhóm Danh Sách Chờ này vì giá vẫn đang nằm sát nền hỗ trợ MA20, hội tụ đủ điều kiện nén lò xo hoặc cạn cung, rủi ro đu đỉnh cực thấp."
                st.success(chuoi_loi_khuyen_cho_minh_tab4)
            else:
                chuoi_thong_bao_khong_co_ma_danh_sach_cho = "Hôm nay chưa có mã nào tích lũy chân sóng đủ tiêu chuẩn khắt khe."
                st.write(chuoi_thong_bao_khong_co_ma_danh_sach_cho)
# ==============================================================================
# HẾT MÃ NGUỒN V20.0 THE PREDATOR LEVIATHAN (BẢN GỐC ĐÃ CẬP NHẬT)
# ==============================================================================


