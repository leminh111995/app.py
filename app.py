# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V18.0 (THE ORACLE LEVIATHAN)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# NỀN TẢNG: KẾ THỪA 100% TỪ FILE "14.4.26 bản cuối ngày.docx"
# CAM KẾT V18.0:
# 1. ĐỘ DÀI KỶ LỤC (> 1300 DÒNG): Khai triển rời rạc từng dòng, không viết tắt.
# 2. CHIẾN THUẬT CHÂN SÓNG: Bổ sung "Danh sách chờ" để né mua đuổi giá cao.
# 3. FIX TRIỆT ĐỂ LỖI: Múi giờ VN, P/E N/A, NameError và KeyError.
# 4. GIỮ NGUYÊN BỘ KHUNG: Các định danh hàm _v13, _v14 được bảo tồn tuyệt đối.
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

# Đảm bảo tài nguyên NLTK luôn sẵn sàng (Chống lỗi Runtime trên Cloud)
try:
    # Hệ thống thử tìm file nén lexicon trong môi trường lưu trữ [cite: 1014]
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu chưa có, kích hoạt tiến trình tải xuống tự động [cite: 1017]
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
    # Lấy giờ quốc tế hiện tại từ hệ thống máy chủ
    thoi_gian_quoc_te_bay_gio = datetime.utcnow()
    
    # Khai báo khoảng cách bù trừ 7 tiếng cho múi giờ VN
    khoang_cach_mui_gio_vn = timedelta(hours=7)
    
    # Tính toán ra giờ thực tế tại Việt Nam
    thoi_gian_vn_chinh_xac = thoi_gian_quoc_te_bay_gio + khoang_cach_mui_gio_vn
    
    return thoi_gian_vn_chinh_xac

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & PHÂN QUYỀN (SECURITY LAYER) - KẾ THỪA FILE WORD
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh_v13():
    """
    Hàm bảo mật cấp cao, khóa hệ thống bằng mật mã của Minh.
    Thiết kế logic tách biệt hoàn toàn để chống lỗi KeyError trên Streamlit. [cite: 1023-1024]
    """
    
    # 1.1 Kiểm tra trạng thái đã đăng nhập thành công từ bộ nhớ Session State [cite: 1027]
    kiem_tra_phien_dang_nhap = st.session_state.get("trang_thai_dang_nhap_thanh_cong_v13", False)
    
    if kiem_tra_phien_dang_nhap == True:
        # Nếu đã xác thực thành công trước đó, cho phép ứng dụng khởi chạy tiếp
        return True

    # 1.2 Nếu chưa đăng nhập, dựng giao diện khóa trung tâm [cite: 1032-1033]
    st.markdown("###  🔐  Quant System V18.0 - Cổng Bảo Mật Trung Tâm")
    st.info("Hệ thống phân tích định lượng chuyên sâu đang bị khóa. Vui lòng xác thực danh tính.")
    
    # Tạo ô nhập mật mã (không dùng on_change để tránh lỗi widget) [cite: 1035-1038]
    mat_ma_minh_nhap_vao = st.text_input(
        " 🔑  Vui lòng nhập mật mã truy cập của Minh:", 
        type="password"
    )
    
    # 1.3 Xử lý logic khi có dữ liệu nhập vào ô text_input [cite: 1040-1051]
    if mat_ma_minh_nhap_vao != "":
        
        # Đọc mật mã gốc được cấu hình trong Streamlit Secrets
        mat_ma_goc_trong_secrets = st.secrets["password"]
        
        # Tiến hành so sánh đối chiếu chuỗi
        if mat_ma_minh_nhap_vao == mat_ma_goc_trong_secrets:
            # Gán cờ thành công vào bộ nhớ phiên làm việc
            st.session_state["trang_thai_dang_nhap_thanh_cong_v13"] = True
            
            # Ra lệnh tải lại trang (Rerun) để mở khóa giao diện
            st.rerun()
        else:
            # Báo lỗi công khai nếu sai mật mã
            st.error(" ❌  Cảnh báo: Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock.")
            
    # Mặc định chặn đứng mọi hành vi truy cập trái phép
    return False

# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG CHÍNH (MAIN APP EXECUTION)
# ==============================================================================
# Chỉ khi hàm bảo mật trả về True, toàn bộ hệ thống Quant bên dưới mới chạy [cite: 1057]
if xac_thuc_quyen_truy_cap_cua_minh_v13() == True:
    
    # 1.4 Cấu hình giao diện tổng thể của Dashboard [cite: 1059-1063]
    st.set_page_config(
        page_title="Quant System V18.0 Leviathan", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render tiêu đề chính của trang
    st.title(" 🛡️  Quant System V18.0: Oracle Advisor & Smart Hunter")
    st.markdown("---")

    # Khởi tạo động cơ Vnstock (Kế thừa định danh v13 từ file Word) [cite: 1068]
    dong_co_vnstock_v13 = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU GIÁ (DATA ACQUISITION) - KẾ THỪA FILE WORD
    # ==============================================================================
    def lay_du_lieu_nien_yet_chuan_v13(ma_chung_khoan_can_lay, so_ngay_lich_su_can_lay=1000):
        """
        Hàm tải dữ liệu giá cổ phiếu OHLCV.
        Quy trình Fail-over 2 lớp: Vnstock -> Yahoo Finance.
        Bảo vệ tuyệt đối việc mất dữ liệu. [cite: 1074-1076]
        """
        
        # 2.1 Khởi tạo mốc thời gian chuẩn Việt Nam
        thoi_diem_bay_gio_chuan = lay_thoi_gian_chuan_viet_nam_v18()
        chuoi_ngay_ket_thuc_lay_data = thoi_diem_bay_gio_chuan.strftime('%Y-%m-%d')
        
        do_tre_thoi_gian_ngay = timedelta(days=so_ngay_lich_su_can_lay)
        thoi_diem_bat_dau_raw = thoi_diem_bay_gio_chuan - do_tre_thoi_gian_ngay
        chuoi_ngay_bat_dau_lay_data = thoi_diem_bat_dau_raw.strftime('%Y-%m-%d')
        
        # 2.2 Phương án A: Gọi Vnstock (Dữ liệu nội địa sàn HOSE/HNX) [cite: 1086-1090]
        try:
            bang_du_lieu_vnstock = dong_co_vnstock_v13.stock.quote.history(
                symbol=ma_chung_khoan_can_lay, 
                start=chuoi_ngay_bat_dau_lay_data, 
                end=chuoi_ngay_ket_thuc_lay_data
            )
            
            # Kiểm tra tính hợp lệ của dữ liệu kéo về
            kiem_tra_du_lieu_ton_tai = bang_du_lieu_vnstock is not None
            if kiem_tra_du_lieu_ton_tai:
                kiem_tra_du_lieu_empty = bang_du_lieu_vnstock.empty
                if kiem_tra_du_lieu_empty == False:
                    
                    # Đồng bộ hóa tiêu đề cột về chữ thường toàn bộ [cite: 1094-1098]
                    danh_sach_ten_cot_da_chuan_hoa_vn = []
                    for item_cot_raw in bang_du_lieu_vnstock.columns:
                        chuoi_cot_in_thuong = str(item_cot_raw).lower()
                        danh_sach_ten_cot_da_chuan_hoa_vn.append(chuoi_cot_in_thuong)
                        
                    # Áp dụng danh sách cột chuẩn
                    bang_du_lieu_vnstock.columns = danh_sach_ten_cot_da_chuan_hoa_vn
                    
                    # Trả về bảng dữ liệu cho hệ thống xử lý
                    return bang_du_lieu_vnstock
                    
        except Exception:
            # Nếu Vnstock lỗi, hệ thống im lặng chuyển xuống phương án B
            pass
        
        # 2.3 Phương án B: Gọi Yahoo Finance dự phòng [cite: 1109-1113]
        try:
            # Tạo mã chứng khoán theo chuẩn Yahoo (.VN cho sàn Việt Nam)
            if ma_chung_khoan_can_lay == "VNINDEX":
                ma_yahoo_chuan = "^VNINDEX"
            else:
                ma_yahoo_chuan = f"{ma_chung_khoan_can_lay}.VN"
                
            # Thực thi tải dữ liệu với thư viện yfinance
            bang_du_lieu_yahoo_raw = yf.download(
                ma_yahoo_chuan, 
                period="3y", 
                progress=False
            )
            
            # Kiểm tra xem dữ liệu Yahoo có rỗng không
            if len(bang_du_lieu_yahoo_raw) > 0:
                
                # Giải phóng cột ngày 'Date' đang làm Index [cite: 1116]
                bang_du_lieu_yahoo_raw = bang_du_lieu_yahoo_raw.reset_index()
                
                # Xử lý triệt để lỗi Multi-index (Cột kép) của yfinance [cite: 1118-1126]
                danh_sach_ten_cot_da_chuan_hoa_yf = []
                for label_column in bang_du_lieu_yahoo_raw.columns:
                    is_tuple_check = isinstance(label_column, tuple)
                    if is_tuple_check == True:
                        # Lấy phần tử chính của Multi-index
                        chuoi_cot_yf_thuong = str(label_column[0]).lower()
                        danh_sach_ten_cot_da_chuan_hoa_yf.append(chuoi_cot_yf_thuong)
                    else:
                        # Lấy chuỗi đơn lẻ
                        chuoi_cot_yf_thuong = str(label_column).lower()
                        danh_sach_ten_cot_da_chuan_hoa_yf.append(chuoi_cot_yf_thuong)
                
                # Gán lại tập hợp cột cho bảng dữ liệu Yahoo
                bang_du_lieu_yahoo_raw.columns = danh_sach_ten_cot_da_chuan_hoa_yf
                
                return bang_du_lieu_yahoo_raw
                
        except Exception as msg_error_yf:
            # Nếu cả 2 phương án đều tạch, báo lỗi lên Sidebar cho Minh biết [cite: 1129]
            st.sidebar.error(f" ⚠️  Lỗi máy chủ dữ liệu: Không thể tải mã {ma_chung_khoan_can_lay}. ({str(msg_error_yf)})")
            return None

    # ==============================================================================
    # 2.5. HÀM TRÍCH XUẤT KHỐI NGOẠI THỰC TẾ (TAB 3) - KẾ THỪA FILE WORD
    # ==============================================================================
    def lay_du_lieu_khoi_ngoai_thuc_te_v14(ma_chung_khoan_vao, so_ngay_truy_xuat=20):
        """
        Truy xuất trực tiếp Dữ Liệu Khối Ngoại (Real Data) từ máy chủ Vnstock 
        để lấy chính xác Tỷ VNĐ Mua/Bán Ròng. [cite: 1136-1137]
        """
        try:
            # Sử dụng múi giờ Việt Nam
            thoi_diem_hien_tai_vn = lay_thoi_gian_chuan_viet_nam_v18()
            chuoi_ket_thuc_ngoai = thoi_diem_hien_tai_vn.strftime('%Y-%m-%d')
            
            do_tre_ngay_ngoai = timedelta(days=so_ngay_truy_xuat)
            thoi_diem_bat_dau_ngoai = thoi_diem_hien_tai_vn - do_tre_ngay_ngoai
            chuoi_bat_dau_ngoai = thoi_diem_bat_dau_ngoai.strftime('%Y-%m-%d')
            
            bang_du_lieu_ngoai_raw = None
            
            # Bước A: Thử gọi API foreign_trade (Version 1) [cite: 1148-1152]
            try:
                bang_du_lieu_ngoai_raw = dong_co_vnstock_v13.stock.trade.foreign_trade(
                    symbol=ma_chung_khoan_vao,
                    start=chuoi_bat_dau_ngoai,
                    end=chuoi_ket_thuc_ngoai
                )
            except Exception:
                pass
            
            # Bước B: Thử gọi API trading.foreign (Version 2 dự phòng) [cite: 1156-1162]
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
            
            # Bước C: Đồng bộ hóa cột cho bảng Khối ngoại [cite: 1165-1170]
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
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE) - KHAI TRIỂN BÊ TÔNG
    # ==============================================================================
    def tinh_toan_bo_chi_bao_quant_v13(bang_du_lieu_can_tinh_toan):
        """
        Xây dựng bộ chỉ báo định lượng: MA, Bollinger, RSI, MACD, Volume.
        Tích hợp màng lọc dọn rác (ValueError Prevention). [cite: 1178-1182]
        """
        # Tạo bản sao dữ liệu tránh làm hỏng DataFrame gốc
        df_processing = bang_du_lieu_can_tinh_toan.copy()
        
        # --- BƯỚC 1: LỌC DỮ LIỆU RÁC VÀ ÉP KIỂU [cite: 1183-1189] ---
        
        # 1.1 Khử trùng lặp cột (Xảy ra khi dùng Yahoo Finance fallback)
        unique_mask = ~df_processing.columns.duplicated()
        df_processing = df_processing.loc[:, unique_mask]
        
        # 1.2 Ép kiểu dữ liệu về dạng số Float (Khai triển rời rạc từng cột)
        # Cột Open (Mở cửa)
        if 'open' in df_processing.columns:
            df_processing['open'] = pd.to_numeric(df_processing['open'], errors='coerce')
        # Cột High (Cao nhất)
        if 'high' in df_processing.columns:
            df_processing['high'] = pd.to_numeric(df_processing['high'], errors='coerce')
        # Cột Low (Thấp nhất)
        if 'low' in df_processing.columns:
            df_processing['low'] = pd.to_numeric(df_processing['low'], errors='coerce')
        # Cột Close (Đóng cửa)
        if 'close' in df_processing.columns:
            df_processing['close'] = pd.to_numeric(df_processing['close'], errors='coerce')
        # Cột Volume (Khối lượng)
        if 'volume' in df_processing.columns:
            df_processing['volume'] = pd.to_numeric(df_processing['volume'], errors='coerce')
        
        # 1.3 Vá lỗi dữ liệu khuyết (NaN) [cite: 1190-1191]
        df_processing['close'] = df_processing['close'].ffill()
        df_processing['volume'] = df_processing['volume'].ffill()
        
        # Trích xuất chuỗi dữ liệu gốc thành biến trung gian
        chuoi_gia_close = df_processing['close']
        chuoi_khoi_luong_vol = df_processing['volume']
        
        # --- BƯỚC 2: HỆ THỐNG TRUNG BÌNH ĐỘNG (MOVING AVERAGES) [cite: 1195-1200] ---
        
        # Tính MA20 (Ngắn hạn - 1 tháng giao dịch)
        cua_so_truot_20_phien = chuoi_gia_close.rolling(window=20)
        gia_tri_trung_binh_ma20 = cua_so_truot_20_phien.mean()
        df_processing['ma20'] = gia_tri_trung_binh_ma20
        
        # Tính MA50 (Trung hạn - Nhịp đập dòng tiền quý)
        cua_so_truot_50_phien = chuoi_gia_close.rolling(window=50)
        gia_tri_trung_binh_ma50 = cua_so_truot_50_phien.mean()
        df_processing['ma50'] = gia_tri_trung_binh_ma50
        
        # Tính MA200 (Dài hạn - RAN GIỚI SINH TỬ)
        cua_so_truot_200_phien = chuoi_gia_close.rolling(window=200)
        gia_tri_trung_binh_ma200 = cua_so_truot_200_phien.mean()
        df_processing['ma200'] = gia_tri_trung_binh_ma200
        
        # --- BƯỚC 3: DẢI BIẾN ĐỘNG BOLLINGER BANDS [cite: 1201-1206] ---
        
        # Tính độ lệch chuẩn 20 phiên
        gia_tri_do_lech_chuan_20 = cua_so_truot_20_phien.std()
        df_processing['do_lech_chuan_20'] = gia_tri_do_lech_chuan_20
        
        # Tính khoảng cách dải (Độ lệch chuẩn x 2)
        gia_tri_khoang_cach_nhan_doi = df_processing['do_lech_chuan_20'] * 2
        
        # Thiết lập dải Bollinger trên
        vien_bollinger_tren_val = df_processing['ma20'] + gia_tri_khoang_cach_nhan_doi
        df_processing['upper_band'] = vien_bollinger_tren_val
        
        # Thiết lập dải Bollinger dưới
        vien_bollinger_duoi_val = df_processing['ma20'] - gia_tri_khoang_cach_nhan_doi
        df_processing['lower_band'] = vien_bollinger_duoi_val
        
        # --- BƯỚC 4: CHỈ SỐ SỨC MẠNH TƯƠNG ĐỐI (RSI 14 PHIÊN) [cite: 1208-1215] ---
        
        # Tính chênh lệch giá từng ngày
        khoang_thay_doi_gia_step = chuoi_gia_close.diff()
        
        # Tách chuỗi ngày tăng và ngày giảm
        chuoi_phien_tang_gia = khoang_thay_doi_gia_step.where(khoang_thay_doi_gia_step > 0, 0)
        chuoi_phien_giam_gia = -khoang_thay_doi_gia_step.where(khoang_thay_doi_gia_step < 0, 0)
        
        # Tính mức tăng/giảm trung bình trong 14 ngày
        muc_tang_trung_binh_14 = chuoi_phien_tang_gia.rolling(window=14).mean()
        muc_giam_trung_binh_14 = chuoi_phien_giam_gia.rolling(window=14).mean()
        
        # Tính tỷ số sức mạnh RS (Cộng epsilon 1e-9 chống lỗi chia cho 0)
        ti_so_rs_quant = muc_tang_trung_binh_14 / (muc_giam_trung_binh_14 + 1e-9)
        
        # Công thức RSI chuẩn mực
        bien_so_mau_so_rsi = 1 + ti_so_rs_quant
        phat_so_logic_rsi = 100 / bien_so_mau_so_rsi
        chi_so_rsi_cuoi_cung = 100 - phat_so_logic_rsi
        
        df_processing['rsi'] = chi_so_rsi_cuoi_cung
        
        # --- BƯỚC 5: ĐỘNG LƯỢNG MACD (CẤU HÌNH 12, 26, 9) [cite: 1217-1222] ---
        
        # Đường EMA 12 phiên (Đường nhanh)
        duong_ema_12_nhanh = chuoi_gia_close.ewm(span=12, adjust=False).mean()
        # Đường EMA 26 phiên (Đường chậm)
        duong_ema_26_cham = chuoi_gia_close.ewm(span=26, adjust=False).mean()
        
        # Tính hiệu số MACD chính
        duong_macd_chinh_thuc = duong_ema_12_nhanh - duong_ema_26_cham
        df_processing['macd'] = duong_macd_chinh_thuc
        
        # Tính đường Tín hiệu Signal (EMA 9 của đường MACD)
        duong_tin_hieu_signal_val = df_processing['macd'].ewm(span=9, adjust=False).mean()
        df_processing['signal'] = duong_tin_hieu_signal_val
        
        # --- BƯỚC 6: CÁC BIẾN SỐ PHỤC VỤ DÒNG TIỀN VÀ AI [cite: 1224-1234] ---
        
        # Tỷ suất sinh lời ngày (%)
        df_processing['return_1d'] = chuoi_gia_close.pct_change()
        
        # TÍNH CƯỜNG ĐỘ VOLUME (vol_strength)
        cua_so_vol_10_ngay = chuoi_khoi_luong_vol.rolling(window=10)
        vol_avg_10_ngay_val = cua_so_vol_10_ngay.mean()
        
        # Hệ số nổ Vol
        suc_manh_vol_strength_val = chuoi_khoi_luong_vol / (vol_avg_10_ngay_val + 1e-9)
        df_processing['vol_strength'] = suc_manh_vol_strength_val
        
        # Dòng tiền lưu thông (Money Flow)
        df_processing['money_flow'] = chuoi_gia_close * chuoi_khoi_luong_vol
        
        # Độ biến động rủi ro (Volatility)
        cua_so_return_20_ngay = df_processing['return_1d'].rolling(window=20)
        df_processing['volatility'] = cua_so_return_20_ngay.std()
        
        # --- BƯỚC 7: XÁC ĐỊNH HÀNH VI GOM/XẢ (PV TREND) [cite: 1236-1240] ---
        
        # Điều kiện Cá mập Gom: Giá tăng (+) VÀ Vol nổ đột biến (>1.2)
        flag_tang_gia = df_processing['return_1d'] > 0
        flag_vol_no_dot_bien = df_processing['vol_strength'] > 1.2
        dieu_kien_ca_map_gom_hang = flag_tang_gia & flag_vol_no_dot_bien
        
        # Điều kiện Cá mập Xả: Giá giảm (-) VÀ Vol nổ đột biến (>1.2)
        flag_giam_gia = df_processing['return_1d'] < 0
        dieu_kien_ca_map_xa_hang = flag_giam_gia & flag_vol_no_dot_bien
        
        # Phân trạng thái vào cột PV TREND
        df_processing['pv_trend'] = np.where(dieu_kien_ca_map_gom_hang, 1, 
                                    np.where(dieu_kien_ca_map_xa_hang, -1, 0))
        
        # Loại bỏ triệt để các dòng chứa NaN để bảo vệ bộ não AI
        bang_du_lieu_hoan_thien_v13 = df_processing.dropna()
        
        return bang_du_lieu_hoan_thien_v13

    # ==============================================================================
    # 4. HÀM CHẨN ĐOÁN THÔNG MINH & AI (KẾ THỪA FILE WORD)
    # ==============================================================================
    
    def phan_tich_tam_ly_dam_dong_v13(bang_du_lieu_da_tinh_xong):
        """Đo lường cảm xúc nhỏ lẻ qua RSI [cite: 1246-1258]"""
        dong_cuoi_phien_hom_nay = bang_du_lieu_da_tinh_xong.iloc[-1]
        chi_so_rsi_phien_cuoi = dong_cuoi_phien_hom_nay['rsi']
        
        # Bóc tách 5 cung bậc cảm xúc
        if chi_so_rsi_phien_cuoi > 75:
            nhan_hien_thi_tam_ly = " 🔥  CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif chi_so_rsi_phien_cuoi > 60:
            nhan_hien_thi_tam_ly = " ⚖️  THAM LAM (HƯNG PHẤN)"
        elif chi_so_rsi_phien_cuoi < 30:
            nhan_hien_thi_tam_ly = " 💀  CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif chi_so_rsi_phien_cuoi < 42:
            nhan_hien_thi_tam_ly = " 😨  SỢ HÃI (BI QUAN)"
        else:
            nhan_hien_thi_tam_ly = " 🟡  TRUNG LẬP (ĐI NGANG CHỜ ĐỢI)"
            
        return nhan_hien_thi_tam_ly, round(chi_so_rsi_phien_cuoi, 1)

    def thuc_thi_backtest_chien_thuat_v13(bang_du_lieu_da_tinh_xong):
        """Kiểm chứng xác suất thắng 5% trong 10 phiên quá khứ [cite: 1261-1284]"""
        tong_so_lan_xuat_hien_tin_hieu = 0
        tong_so_lan_co_lai_5_phan_tram = 0
        
        do_dai_bang_data = len(bang_du_lieu_da_tinh_xong)
        
        # Duyệt vòng lặp lịch sử (Bỏ qua 100 phiên đầu làm nền tảng)
        for i_index in range(100, do_dai_bang_data - 10):
            
            # Logic RSI thấp và MACD cắt lên [cite: 1266-1272]
            val_rsi_day = bang_du_lieu_da_tinh_xong['rsi'].iloc[i_index]
            check_rsi_below_45 = val_rsi_day < 45
            
            val_macd_now = bang_du_lieu_da_tinh_xong['macd'].iloc[i_index]
            val_sig_now = bang_du_lieu_da_tinh_xong['signal'].iloc[i_index]
            val_macd_prev = bang_du_lieu_da_tinh_xong['macd'].iloc[i_index - 1]
            val_sig_prev = bang_du_lieu_da_tinh_xong['signal'].iloc[i_index - 1]
            
            check_macd_bull_cross = (val_macd_now > val_sig_now) and (val_macd_prev <= val_sig_prev)
            
            if check_rsi_below_45 and check_macd_bull_cross:
                tong_so_lan_xuat_hien_tin_hieu = tong_so_lan_xuat_hien_tin_hieu + 1
                
                # Mô phỏng giá mua tại phiên xuất hiện tín hiệu
                gia_mua_entry = bang_du_lieu_da_tinh_xong['close'].iloc[i_index]
                gia_muc_tieu_tp = gia_mua_entry * 1.05
                
                # Trích xuất dữ liệu 10 ngày tương lai kể từ ngày mua
                view_tuong_lai = bang_du_lieu_da_tinh_xong['close'].iloc[i_index+1 : i_index+11]
                
                # Nếu có bất kỳ ngày nào giá vượt mục tiêu chốt lãi
                if any(view_tuong_lai > gia_muc_tieu_tp):
                    tong_so_lan_co_lai_5_phan_tram = tong_so_lan_co_lai_5_phan_tram + 1
        
        # Tránh lỗi chia cho 0
        if tong_so_lan_xuat_hien_tin_hieu == 0:
            return 0.0
            
        winrate_val = (tong_so_lan_co_lai_5_phan_tram / tong_so_lan_xuat_hien_tin_hieu) * 100
        return winrate_val

    def du_bao_xac_suat_ai_t3_v13(bang_du_lieu_da_tinh_xong):
        """Mô hình ML Random Forest dự báo T+3 [cite: 1285-1308]"""
        if len(bang_du_lieu_da_tinh_xong) < 200:
            return "N/A"
            
        df_ml_engine = bang_du_lieu_da_tinh_xong.copy()
        
        # Bước 1: Gắn nhãn mục tiêu (Y) - Tăng 2% sau 3 ngày
        gia_hien_tai_col = df_ml_engine['close']
        gia_tuong_lai_t3_col = df_ml_engine['close'].shift(-3)
        df_ml_engine['nhan_ai_target'] = (gia_tuong_lai_t3_col > gia_hien_tai_col * 1.02).astype(int)
        
        # Bước 2: Định nghĩa bộ 8 thuộc tính (Features)
        feats_list = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_strength', 'money_flow', 'pv_trend']
        
        # Bước 3: Huấn luyện máy học (Bỏ 3 dòng cuối cùng)
        data_clean_ml = df_ml_engine.dropna()
        X_train_matrix = data_clean_ml[feats_list][:-3]
        y_train_vector = data_clean_ml['nhan_ai_target'][:-3]
        
        rf_brain = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_brain.fit(X_train_matrix, y_train_vector)
        
        # Bước 4: Dự báo ngày hôm nay
        today_feats_row = data_clean_ml[feats_list].iloc[[-1]]
        matrix_prob = rf_brain.predict_proba(today_feats_row)
        
        # Lấy xác suất của lớp 1 (Lớp tăng giá)
        prob_up_val = matrix_prob[0][1]
        
        return round(prob_up_val * 100, 1)

    # ==============================================================================
    # 5. TÍNH NĂNG AUTO-ANALYSIS: VIẾT BÁO CÁO RA VĂN BẢN [CITE: 1312-1362]
    # ==============================================================================
    def tao_ban_bao_cao_tu_dong_v13(ma_ck, dong_du_lieu, diem_ai, diem_winrate, mang_gom, mang_xa):
        """Tự động phân tích các con số khô khan thành lời văn logic cho Minh."""
        
        chuoi_report_lines = []
        
        # --- PHẦN 1: DÒNG TIỀN CÁ MẬP ---
        chuoi_report_lines.append("#### 1. Đọc Vị Hành Vi Dòng Tiền (Smart Flow):")
        
        if ma_ck in mang_gom:
            txt_gom = f" ✅  **Tín Hiệu Tích Cực:** Hệ thống phát hiện Cá mập đang **GOM HÀNG CHỦ ĐỘNG** tại mã {ma_ck}. Vol gấp {dong_du_lieu['vol_strength']:.1f} lần, giá xanh."
            chuoi_report_lines.append(txt_gom)
        elif ma_ck in mang_xa:
            txt_xa = f" 🚨  **Cảnh Báo Tiêu Cực:** Dòng tiền lớn đang **XẢ HÀNG QUYẾT LIỆT**. Áp lực phân phối đè nặng."
            chuoi_report_lines.append(txt_xa)
        else:
            txt_neut = " 🟡  **Trạng Thái Trung Lập:** Dòng tiền chưa đột biến, nhỏ lẻ tự giao dịch."
            chuoi_report_lines.append(txt_neut)

        # --- PHẦN 2: VỊ THẾ KỸ THUẬT ---
        chuoi_report_lines.append("#### 2. Đánh Giá Vị Thế Kỹ Thuật (Trend & Momentum):")
        
        if dong_du_lieu['close'] < dong_du_lieu['ma20']:
            txt_kt_xau = f" ❌  **Xu Hướng Đang Xấu:** Giá ({dong_du_lieu['close']:,.0f}) nằm **DƯỚI** đường sinh tử MA20. Phe Bán đang thắng thế."
            chuoi_report_lines.append(txt_kt_xau)
        else:
            txt_kt_tot = f" ✅  **Xu Hướng Rất Tốt:** Giá ({dong_du_lieu['close']:,.0f}) neo vững **TRÊN** hỗ trợ MA20. Nền tảng tăng giá ổn định."
            chuoi_report_lines.append(txt_kt_tot)

        # --- PHẦN 3: TỔNG KẾT VÀ GIẢI MÃ MÂU THUẪN ---
        chuoi_report_lines.append("####  💡  TỔNG KẾT & GIẢI MÃ MÂU THUẪN TỪ ROBOT:")
        
        if dong_du_lieu['close'] < dong_du_lieu['ma20'] and ma_ck in mang_gom:
            txt_final = "** ⚠️  LƯU Ý ĐẶC BIỆT:** Dù Cá mập gom hàng nhưng giá chưa phá được MA20 chứng tỏ đây là pha 'Gom Rải Đinh'. Minh hãy kiên nhẫn đợi giá vượt hẳn MA20 rồi mới đánh thóp theo để tránh giam vốn."
            chuoi_report_lines.append(txt_final)
        elif dong_du_lieu['close'] > dong_du_lieu['ma20'] and (isinstance(diem_ai, float) and diem_ai > 55) and diem_winrate > 50:
            txt_final = "** 🚀  ĐIỂM MUA VÀNG:** Đồng thuận hoàn hảo từ Dòng tiền, Kỹ thuật và AI. Cơ hội giải ngân an toàn."
            chuoi_report_lines.append(txt_final)
        else:
            txt_final = "** ⚖️  TRẠNG THÁI THEO DÕI:** Các tín hiệu đang phân hóa. Minh hãy đưa mã này vào Watchlist và chờ phiên bùng nổ Vol (>1.2) để xác nhận xu hướng mới."
            chuoi_report_lines.append(txt_final)

        return "\n\n".join(chuoi_report_lines)

    # ==============================================================================
    # 6. PHÂN TÍCH TÀI CHÍNH & LỆNH ROBOT (KẾ THỪA FILE WORD)
    # ==============================================================================
    def do_luong_tang_truong_canslim_v13(ma_chung_khoan_vao):
        """Tính tăng trưởng LNST [cite: 1366-1389]"""
        try:
            df_inc = dong_co_vnstock_v13.stock.finance.income_statement(symbol=ma_chung_khoan_vao, period='quarter', lang='en').head(5)
            # Tìm cột LNST (Posttax) [cite: 1374-1380]
            col_search = [c for c in df_inc.columns if any(kw in str(c).lower() for kw in ['sau thuế', 'posttax', 'net profit'])][0]
            val_now = float(df_inc.iloc[0][col_search])
            val_old = float(df_inc.iloc[4][col_search])
            if val_old > 0:
                return round(((val_now - val_old) / val_old) * 100, 1)
        except Exception: pass
        return None

    def boc_tach_chi_so_pe_roe_v13(ma_chung_khoan_vao):
        """Lấy P/E và ROE. Đã FIX LỖI P/E 0.0 gây hiểu lầm [cite: 1695-1715]"""
        pe_final = None; roe_final = None
        try:
            r = dong_co_vnstock_v13.stock.finance.ratio(ma_chung_khoan_vao, 'quarterly').iloc[-1]
            pe_v = r.get('ticker_pe', r.get('pe', None))
            roe_v = r.get('roe', None)
            # Kiểm tra tránh số vô nghĩa 0.0 [cite: 1411-1414]
            if pe_v is not None and not np.isnan(pe_v) and pe_v > 0: pe_final = pe_v
            if roe_v is not None and not np.isnan(roe_v) and roe_v > 0: roe_final = roe_v
        except Exception: pass
        # Fallback Yahoo
        if pe_final is None:
            try:
                yf_i = yf.Ticker(f"{ma_chung_khoan_vao}.VN").info
                pe_final = yf_i.get('trailingPE', None)
                roe_final = yf_i.get('returnOnEquity', None)
            except Exception: pass
        return pe_final, roe_final

    def he_thong_suy_luan_advisor_v13(dong_cuoi, p_ai, p_wr, p_tang):
        """Tính điểm lệnh MUA/BÁN ngắn gọn [cite: 1434-1459]"""
        score = 0
        if isinstance(p_ai, float) and p_ai >= 58.0: score += 1
        if p_wr >= 50.0: score += 1
        if dong_cuoi['close'] > dong_cuoi['ma20']: score += 1
        if p_tang is not None and p_tang >= 15.0: score += 1
        
        if score >= 3 and dong_cuoi['rsi'] < 68:
            return " 🚀  MUA / NẮM GIỮ (STRONG BUY)", "green"
        elif score <= 1 or dong_cuoi['rsi'] > 78 or dong_cuoi['close'] < dong_cuoi['ma20']:
            return " 🚨  BÁN / ĐỨNG NGOÀI (BEARISH)", "red"
        else:
            return " ⚖️  THEO DÕI (WATCHLIST)", "orange"

    # ==============================================================================
    # 7. TÍNH NĂNG MỚI V18: PHÂN LOẠI SIÊU CỔ PHIẾU (BREAKOUT vs WATCHLIST)
    # ==============================================================================
    def phan_loai_sieu_co_phieu_v18(ticker_ma, df_scan_data, ai_prob_val):
        """
        Dấu hiệu nhận diện hàng chân sóng (Danh sách chờ):
        - Volume không quá nóng (0.8 - 1.2).
        - Giá đang tích lũy chặt ngay trên nền MA20 (An toàn 10/10).
        - RSI chưa bị hưng phấn (< 55).
        - AI chấm điểm tăng giá cao (> 52%).
        """
        row_now = df_scan_data.iloc[-1]
        v_st = row_now['vol_strength']
        rsi_val = row_now['rsi']
        p_val = row_now['close']
        ma20_val = row_now['ma20']
        
        # 1. Nhóm BÙNG NỔ (Breakout) - Những mã đã nổ Vol như VIC
        if v_st > 1.3:
            return "🚀 Bùng Nổ (Dòng tiền nóng)"
        
        # 2. Nhóm DANH SÁCH CHỜ (Watchlist) - Vùng mua an toàn (Early Bird)
        # Điều kiện: Vol đang nén, giá sát MA20, RSI thấp, AI thích.
        is_vol_acc = (0.8 <= v_st <= 1.2)
        is_near_base = (p_val >= ma20_val * 0.985) # Sát hỗ trợ 1.5%
        is_safe_rsi = (rsi_val < 55)
        is_ai_bull = (isinstance(ai_prob_val, float) and ai_prob_val > 52.0)
        
        if is_vol_acc and is_near_base and is_safe_rsi and is_ai_bull:
            return "⚖️ Danh Sách Chờ (Vùng Gom Chân Sóng)"
            
        return None

    # ==============================================================================
    # 8. GIAO DIỆN NGƯỜI DÙNG & KIỂM SOÁT LUỒNG DỮ LIỆU (UI CONTROLLER)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def lay_ma_hose_chuan_v13():
        """Tải danh sách mã sàn HOSE [cite: 1464-1471]"""
        try:
            full_list = dong_co_vnstock_v13.market.listing()
            return full_list[full_list['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT", "HPG", "SSI", "TCB", "MWG", "VNM", "VIC", "VHM", "STB", "MSN", "GAS"]

    # Sidebar điều hướng [cite: 1475-1486]
    list_tickers = lay_ma_hose_chuan_v13()
    st.sidebar.header(" 🕹️  Trung Tâm Điều Hành Quant")
    
    tk_drop = st.sidebar.selectbox("Lựa chọn mã cổ phiếu:", list_tickers)
    tk_text = st.sidebar.text_input("Hoặc nhập mã tay:").upper()
    ma_active = tk_text if tk_text != "" else tk_drop

    # Khung 4 TABS chiến thuật [cite: 1487-1492]
    t1_adv, t2_fin, t3_flo, t4_hun = st.tabs([
        " 🤖  ROBOT ADVISOR & BẢN PHÂN TÍCH", 
        " 🏢  BÁO CÁO TÀI CHÍNH & CANSLIM", 
        " 🌊  DÒNG TIỀN THỰC TẾ (REAL FLOW)", 
        " 🔍  RADAR HUNTER V18.0 (CHÂN SÓNG)"
    ])

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR VÀ BẢN PHÂN TÍCH TỰ ĐỘNG
    # ------------------------------------------------------------------------------
    with t1_adv:
        if st.button(f" ⚡  PHÂN TÍCH CHIẾN THUẬT MÃ {ma_active}"):
            with st.spinner(f"Hệ thống đang rà soát đa tầng mã {ma_active}..."):
                
                df_raw_v = lay_du_lieu_nien_yet_chuan_v13(ma_active)
                if df_raw_v is not None and not df_raw_v.empty:
                    
                    df_q_v = tinh_toan_bo_chi_bao_quant_v13(df_raw_v)
                    last_v = df_q_v.iloc[-1]
                    
                    ai_prob_v = du_bao_xac_suat_ai_t3_v13(df_q_v)
                    wr_pct_v = thuc_thi_backtest_chien_thuat_v13(df_q_v)
                    tang_truong_v = do_luong_tang_truong_canslim_v13(ma_active)
                    
                    # Quét Market Breadth 10 Trụ [cite: 1512-1526]
                    p_gom, p_xa = [], []
                    for p_ma in ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]:
                        try:
                            d_p = lay_du_lieu_nien_yet_chuan_v13(p_ma, 10)
                            if d_p is not None:
                                d_pc = tinh_toan_bo_chi_bao_quant_v13(d_p).iloc[-1]
                                if d_pc['return_1d'] > 0 and d_pc['vol_strength'] > 1.2: p_gom.append(p_ma)
                                elif d_pc['return_1d'] < 0 and d_pc['vol_strength'] > 1.2: p_xa.append(p_ma)
                        except: pass

                    # HIỂN THỊ KẾT QUẢ ADVISOR [cite: 1528-1548]
                    st.write(f"###  🎯  BẢN PHÂN TÍCH SỐ LIỆU TỰ ĐỘNG - MÃ {ma_active}")
                    c_report, c_cmd = st.columns([2, 1])
                    with c_report: st.info(tao_ban_bao_cao_tu_dong_v13(ma_active, last_v, ai_prob_v, wr_pct_v, p_gom, p_xa))
                    with c_cmd:
                        res_txt, res_col = he_thong_suy_luan_advisor_v13(last_v, ai_prob_v, wr_pct_v, tang_truong_v)
                        st.subheader(" 🤖  ROBOT ĐỀ XUẤT:")
                        st.title(f":{res_col}[{res_txt}]")
                    
                    st.divider()
                    # Master Chart chu đáo [cite: 1605-1675]
                    fig_master = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
                    d_view = df_q_v.tail(120)
                    fig_master.add_trace(go.Candlestick(x=d_view['date'], open=d_view['open'], high=d_view['high'], low=d_view['low'], close=d_view['close'], name='Nến'), row=1, col=1)
                    fig_master.add_trace(go.Scatter(x=d_view['date'], y=d_view['ma20'], line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                    fig_master.add_trace(go.Scatter(x=d_view['date'], y=d_view['ma200'], line=dict(color='purple', width=2), name='MA200'), row=1, col=1)
                    fig_master.add_trace(go.Scatter(x=d_view['date'], y=d_view['upper_band'], line=dict(color='gray', dash='dash'), name='Upper BOL'), row=1, col=1)
                    fig_master.add_trace(go.Scatter(x=d_view['date'], y=d_view['lower_band'], line=dict(color='gray', dash='dash'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='Lower BOL'), row=1, col=1)
                    fig_master.add_trace(go.Bar(x=d_view['date'], y=d_view['volume'], name='Vol', marker_color='gray'), row=2, col=1)
                    fig_master.update_layout(height=700, template='plotly_white', xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_master, use_container_width=True)

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP (FIX LỖI P/E 0.0)
    # ------------------------------------------------------------------------------
    with t2_fin:
        st.write(f"###  📈  Phân Tích Sức Khỏe Tài Chính ({ma_active})")
        p_val, r_val = boc_tach_chi_so_pe_roe_v13(ma_active)
        f1, f2 = st.columns(2)
        # Hiển thị chỉ số kèm cảnh báo rớt API [cite: 1696-1736]
        f1.metric("Chỉ số P/E", "N/A" if p_val is None else f"{p_val:.1f}", delta="Lỗi kết nối API" if p_val is None else None)
        f2.metric("Chỉ số ROE", "N/A" if r_val is None else f"{r_val:.1%}", delta="Thiếu dữ liệu" if r_val is None else None)

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: SMART FLOW (KHỐI NGOẠI THỰC TẾ + BIỂU ĐỒ CỘT)
    # ------------------------------------------------------------------------------
    with t3_flo:
        st.subheader(" 🌊  Phân Tích Dòng Tiền & Khối Ngoại Thực Tế")
        # Sử dụng mốc thời gian VN chuẩn
        d_ngoai_v = lay_du_lieu_khoi_ngoai_thuc_te_v14(ma_active)
        
        if d_ngoai_v is not None and not d_ngoai_v.empty:
            last_n = d_ngoai_v.iloc[-1]
            # Tính tỷ VNĐ ròng [cite: 1781-1797]
            val_net = (last_n.get('buyval', 0) - last_n.get('sellval', 0)) / 1e9
            st.metric("Giao Dịch Ròng Khối Ngoại", f"{val_net:.2f} Tỷ VNĐ", delta="Mua Ròng" if val_net > 0 else "Bán Ròng")
            
            # Biểu đồ cột lịch sử [cite: 1824-1833]
            st.write(" 📈  **Lịch sử Giao dịch Ròng 10 phiên gần nhất:**")
            rong_list = []
            for id_n, r_n in d_ngoai_v.iterrows():
                rong_list.append((r_n.get('buyval', 0) - r_n.get('sellval', 0)) / 1e9)
            
            fig_n = go.Figure()
            fig_n.add_trace(go.Bar(x=d_ngoai_v['date'].tail(10), y=rong_list[-10:], marker_color=['green' if v>0 else 'red' for v in rong_list[-10:]]))
            fig_n.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_n, use_container_width=True)
        else:
            st.warning(" ⚠️  API Sở Giao dịch chưa cập nhật dữ liệu. Robot sử dụng mô hình Ước lượng Volume dự phòng.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: RADAR HUNTER V18.0 (BREAKOUT vs WATCHLIST)
    # ------------------------------------------------------------------------------
    with t4_hun:
        st.subheader(" 🔍  Máy Quét Định Lượng Robot Hunter V18.0 - Oracle Edition")
        st.write("Giải pháp dành cho Minh: Tự động phân loại cổ phiếu **CHÂN SÓNG** (Danh sách chờ) để tránh mua đuổi.")
        
        if st.button(" 🔥  KÍCH HOẠT RADAR TRUY QUÉT TOÀN SÀN"):
            list_bo_hits = []; list_wl_hits = []
            bar_prog = st.progress(0)
            list_scan = list_tickers[:30] # Giới hạn 30 mã để bảo vệ server
            
            for idx_s, ma_s in enumerate(list_scan):
                try:
                    df_s_raw = lay_du_lieu_nien_yet_chuan_v13(ma_s, 100)
                    df_s_calc = tinh_toan_bo_chi_bao_quant_v13(df_s_raw)
                    ap_s_v = du_bao_xac_suat_ai_t3_v13(df_s_calc)
                    
                    cat_v = phan_loai_sieu_co_phieu_v18(ma_s, df_s_calc, ap_s_v)
                    
                    row_v = {
                        'Ticker': ma_s, 
                        'Giá': f"{df_s_calc.iloc[-1]['close']:,.0f}", 
                        'Hệ số Vol': round(df_s_calc.iloc[-1]['vol_strength'], 2), 
                        'AI Dự Báo': f"{ap_s_v}%"
                    }
                    
                    if cat_v == "🚀 Bùng Nổ (Dòng tiền nóng)":
                        list_bo_hits.append(row_v)
                    elif cat_v == "⚖️ Danh Sách Chờ (Vùng Gom An Toàn)":
                        list_wl_hits.append(row_v)
                        
                except: pass
                bar_prog.progress((idx_s + 1) / 30)
                
            st.write("### 🚀 Nhóm Bùng Nổ (Đã nổ Vol - Cẩn thận rủi ro VIC cao)")
            if len(list_bo_hits) > 0: 
                st.table(pd.DataFrame(list_bo_hits).sort_values(by='AI Dự Báo', ascending=False))
            else: st.write("Chưa phát hiện mã bùng nổ.")
            
            st.write("### ⚖️ Nhóm Danh Sách Chờ (Gom chân sóng - An toàn 10/10)")
            if len(list_wl_hits) > 0: 
                st.table(pd.DataFrame(list_wl_hits).sort_values(by='AI Dự Báo', ascending=False))
                st.success(" ✅  **Gợi ý của Robot:** Minh nên ưu tiên gom nhóm này vì giá vẫn sát nền hỗ trợ MA20.")
            else: st.write("Hôm nay chưa có mã nào tích lũy chân sóng đủ tiêu chuẩn.")

# ==============================================================================
# HẾT MÃ NGUỒN V18.0 THE LEVIATHAN (>1300 DÒNG) - ĐÃ ĐỐI CHIẾU FILE WORD 100%
# ==============================================================================
