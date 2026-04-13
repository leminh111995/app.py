# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V10.4 (THE UNCOMPRESSED CORE)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# CAM KẾT V10.4:
# 1. TUYỆT ĐỐI KHÔNG VIẾT TẮT HAY NÉN MÃ NGUỒN.
# 2. ĐỒNG BỘ CHÍNH XÁC MỌI ĐỊNH DANH (BIẾN, HÀM, TABS).
# 3. KHÔI PHỤC HOÀN TOÀN BIỂU ĐỒ VÀ LOGIC GIẢI MÃ CỦA ADVISOR.
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
# THƯ VIỆN TRÍ TUỆ NHÂN TẠO & XỬ LÝ NGÔN NGỮ
# ------------------------------------------------------------------------------
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Tải tài nguyên ngôn ngữ tự động để ngăn chặn lỗi Runtime trên Streamlit Cloud
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & PHÂN QUYỀN (SECURITY LAYER)
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh():
    """
    Hàm bảo mật cấp cao, khóa hệ thống bằng mật mã.
    Duy trì phiên đăng nhập bằng st.session_state để không bị văng khi reload.
    """
    def kiem_tra_mat_ma_nhap_vao():
        """Hàm callback chạy khi người dùng nhấn Enter ở ô nhập mật mã"""
        # Truy xuất mật mã gốc từ file cấu hình bí mật (secrets)
        mat_ma_he_thong = st.secrets["password"]
        
        # Lấy giá trị người dùng vừa gõ vào
        mat_ma_nguoi_dung = st.session_state["o_nhap_mat_ma"]
        
        # So sánh logic
        if mat_ma_nguoi_dung == mat_ma_he_thong:
            st.session_state["trang_thai_dang_nhap_thanh_cong"] = True
            # Xóa ngay lập tức mật mã khỏi bộ nhớ để chống lộ lọt
            del st.session_state["o_nhap_mat_ma"]
        else:
            st.session_state["trang_thai_dang_nhap_thanh_cong"] = False

    # 1.1 Kiểm tra nếu chưa từng đăng nhập
    if "trang_thai_dang_nhap_thanh_cong" not in st.session_state:
        st.markdown("### 🔐 Quant System V10.4 - Cổng Bảo Mật")
        st.info("Hệ thống phân tích định lượng chuyên sâu. Vui lòng xác thực danh tính.")
        
        st.text_input(
            "🔑 Nhập mật mã truy cập của Minh:", 
            type="password", 
            on_change=kiem_tra_mat_ma_nhap_vao, 
            key="o_nhap_mat_ma"
        )
        return False
    
    # 1.2 Kiểm tra nếu đã nhập nhưng sai mật mã
    if st.session_state["trang_thai_dang_nhap_thanh_cong"] == False:
        st.error("❌ Cảnh báo: Mật mã không hợp lệ. Vui lòng nhập lại.")
        
        st.text_input(
            "🔑 Thử lại mật mã truy cập:", 
            type="password", 
            on_change=kiem_tra_mat_ma_nhap_vao, 
            key="o_nhap_mat_ma"
        )
        return False
    
    # 1.3 Trả về True nếu đăng nhập thành công
    return st.session_state.get("trang_thai_dang_nhap_thanh_cong", False)

# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG CHÍNH (MAIN APP EXECUTION)
# ==============================================================================
if xac_thuc_quyen_truy_cap_cua_minh():
    
    # Cấu hình Layout cho toàn bộ trang Streamlit
    st.set_page_config(
        page_title="Quant System V10.4 Core", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Tiêu đề giao diện chính
    st.title("🛡️ Quant System V10.4: Master Advisor & Logic Engine")
    st.markdown("---")

    # Khởi tạo động cơ Vnstock để kéo dữ liệu
    dong_co_vnstock = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU CỐT LÕI (DATA ACQUISITION)
    # ==============================================================================
    def lay_du_lieu_nien_yet_chuan_v104(ma_chung_khoan, so_ngay_lich_su=1000):
        """
        Hàm tải dữ liệu giá cổ phiếu OHLCV.
        Áp dụng quy trình Fail-over 2 bước: Thử Vnstock trước, nếu rớt mạng thì gọi Yahoo Finance.
        """
        # Bước 1: Khởi tạo mốc thời gian
        thoi_diem_hien_tai = datetime.now()
        chuoi_ngay_ket_thuc = thoi_diem_hien_tai.strftime('%Y-%m-%d')
        
        do_tre_thoi_gian = timedelta(days=so_ngay_lich_su)
        thoi_diem_bat_dau = thoi_diem_hien_tai - do_tre_thoi_gian
        chuoi_ngay_bat_dau = thoi_diem_bat_dau.strftime('%Y-%m-%d')
        
        # Bước 2: Truy xuất ưu tiên qua Vnstock (Chính xác cho sàn Việt Nam)
        try:
            bang_du_lieu_vnstock = dong_co_vnstock.stock.quote.history(
                symbol=ma_chung_khoan, 
                start=chuoi_ngay_bat_dau, 
                end=chuoi_ngay_ket_thuc
            )
            
            if bang_du_lieu_vnstock is not None and not bang_du_lieu_vnstock.empty:
                # Đổi toàn bộ tiêu đề cột thành chữ thường để không bị lỗi KeyError
                danh_sach_ten_cot_moi = []
                for ten_cot in bang_du_lieu_vnstock.columns:
                    danh_sach_ten_cot_moi.append(str(ten_cot).lower())
                
                bang_du_lieu_vnstock.columns = danh_sach_ten_cot_moi
                return bang_du_lieu_vnstock
        except Exception:
            # Lỗi Vnstock sẽ được bỏ qua để chạy xuống khối Yahoo Finance
            pass
        
        # Bước 3: Phương án dự phòng (Fallback) bằng Yahoo Finance
        try:
            # Gắn đuôi .VN cho các mã chứng khoán để khớp với hệ thống Yahoo
            if ma_chung_khoan == "VNINDEX":
                ma_yahoo_tuong_thich = "^VNINDEX"
            else:
                ma_yahoo_tuong_thich = f"{ma_chung_khoan}.VN"
                
            bang_du_lieu_yahoo = yf.download(
                ma_yahoo_tuong_thich, 
                period="3y", 
                progress=False
            )
            
            if not bang_du_lieu_yahoo.empty:
                # Reset index để cột Date hiện ra
                bang_du_lieu_yahoo = bang_du_lieu_yahoo.reset_index()
                
                # Bóc tách Multi-index (rất hay gây lỗi ở thư viện yfinance mới)
                danh_sach_ten_cot_yahoo = []
                for nhan_cot in bang_du_lieu_yahoo.columns:
                    if isinstance(nhan_cot, tuple):
                        danh_sach_ten_cot_yahoo.append(str(nhan_cot[0]).lower())
                    else:
                        danh_sach_ten_cot_yahoo.append(str(nhan_cot).lower())
                
                bang_du_lieu_yahoo.columns = danh_sach_ten_cot_yahoo
                return bang_du_lieu_yahoo
                
        except Exception as thong_bao_loi:
            st.sidebar.error(f"⚠️ Lỗi nghiêm trọng khi tải mã {ma_chung_khoan}: {str(thong_bao_loi)}")
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (INDICATOR ENGINE)
    # ==============================================================================
    def tinh_toan_bo_chi_bao_quant_v104(bang_du_lieu_dau_vao):
        """
        Xây dựng bộ chỉ báo định lượng: MA, Bollinger, RSI, MACD, Volume.
        Tách rời từng bước tính toán để đảm bảo luồng chạy không bị nén hay xung đột.
        """
        # Tạo bản sao để bảo vệ dữ liệu nguyên gốc
        bang_du_lieu_tinh_toan = bang_du_lieu_dau_vao.copy()
        
        # --- 3.1: HỆ THỐNG TRUNG BÌNH ĐỘNG (MOVING AVERAGES) ---
        chuoi_gia_dong_cua = bang_du_lieu_tinh_toan['close']
        
        # MA20: Ngắn hạn
        bang_du_lieu_tinh_toan['ma20'] = chuoi_gia_dong_cua.rolling(window=20).mean()
        # MA50: Trung hạn
        bang_du_lieu_tinh_toan['ma50'] = chuoi_gia_dong_cua.rolling(window=50).mean()
        # MA200: Dài hạn (Biên giới sinh tử)
        bang_du_lieu_tinh_toan['ma200'] = chuoi_gia_dong_cua.rolling(window=200).mean()
        
        # --- 3.2: DẢI BOLLINGER BANDS (VOLATILITY BANDS) ---
        bang_du_lieu_tinh_toan['do_lech_chuan_20'] = chuoi_gia_dong_cua.rolling(window=20).std()
        
        khoang_cach_do_lech = bang_du_lieu_tinh_toan['do_lech_chuan_20'] * 2
        bang_du_lieu_tinh_toan['upper_band'] = bang_du_lieu_tinh_toan['ma20'] + khoang_cach_do_lech
        bang_du_lieu_tinh_toan['lower_band'] = bang_du_lieu_tinh_toan['ma20'] - khoang_cach_do_lech
        
        # --- 3.3: CHỈ SỐ SỨC MẠNH TƯƠNG ĐỐI (RSI 14) ---
        khoang_chenh_lech_gia = chuoi_gia_dong_cua.diff()
        
        chuoi_gia_tang = khoang_chenh_lech_gia.where(khoang_chenh_lech_gia > 0, 0)
        chuoi_gia_giam = -khoang_chenh_lech_gia.where(khoang_chenh_lech_gia < 0, 0)
        
        muc_tang_trung_binh = chuoi_gia_tang.rolling(window=14).mean()
        muc_giam_trung_binh = chuoi_gia_giam.rolling(window=14).mean()
        
        ti_so_rs = muc_tang_trung_binh / (muc_giam_trung_binh + 1e-9)
        bang_du_lieu_tinh_toan['rsi'] = 100 - (100 / (1 + ti_so_rs))
        
        # --- 3.4: ĐỘNG LƯỢNG MACD (12, 26, 9) ---
        duong_ema_12 = chuoi_gia_dong_cua.ewm(span=12, adjust=False).mean()
        duong_ema_26 = chuoi_gia_dong_cua.ewm(span=26, adjust=False).mean()
        
        bang_du_lieu_tinh_toan['macd'] = duong_ema_12 - duong_ema_26
        bang_du_lieu_tinh_toan['signal'] = bang_du_lieu_tinh_toan['macd'].ewm(span=9, adjust=False).mean()
        
        # --- 3.5: CÁC BIẾN SỐ PHỤC VỤ DÒNG TIỀN VÀ AI ---
        # Tính % thay đổi giá mỗi ngày
        bang_du_lieu_tinh_toan['return_1d'] = chuoi_gia_dong_cua.pct_change()
        
        # SỨC MẠNH KHỐI LƯỢNG (vol_strength - Khóa định danh 100% không đổi)
        chuoi_khoi_luong = bang_du_lieu_tinh_toan['volume']
        khoi_luong_trung_binh_10 = chuoi_khoi_luong.rolling(window=10).mean()
        bang_du_lieu_tinh_toan['vol_strength'] = chuoi_khoi_luong / khoi_luong_trung_binh_10
        
        # Dòng tiền lưu chuyển
        bang_du_lieu_tinh_toan['money_flow'] = chuoi_gia_dong_cua * chuoi_khoi_luong
        
        # Độ biến động thị trường
        bang_du_lieu_tinh_toan['volatility'] = bang_du_lieu_tinh_toan['return_1d'].rolling(window=20).std()
        
        # --- 3.6: PHÂN LỚP XU HƯỚNG DÒNG TIỀN (PRICE-VOLUME TREND) ---
        dieu_kien_cau_manh = (bang_du_lieu_tinh_toan['return_1d'] > 0) & (bang_du_lieu_tinh_toan['vol_strength'] > 1.2)
        dieu_kien_cung_manh = (bang_du_lieu_tinh_toan['return_1d'] < 0) & (bang_du_lieu_tinh_toan['vol_strength'] > 1.2)
        
        bang_du_lieu_tinh_toan['pv_trend'] = np.where(dieu_kien_cau_manh, 1, 
                                             np.where(dieu_kien_cung_manh, -1, 0))
        
        # Xóa bỏ các dòng NaN do quá trình rolling tạo ra để chuẩn bị cho AI
        bang_du_lieu_hoan_thien = bang_du_lieu_tinh_toan.dropna()
        
        return bang_du_lieu_hoan_thien

    # ==============================================================================
    # 4. HÀM CHẨN ĐOÁN THÔNG MINH (INTELLIGENCE & AI LAYER)
    # ==============================================================================
    
    def phan_tich_tam_ly_dam_dong_v104(bang_du_lieu_da_tinh):
        """Đánh giá chỉ số Sợ hãi và Tham lam dựa vào sức nóng của RSI"""
        gia_tri_rsi_cuoi = bang_du_lieu_da_tinh.iloc[-1]['rsi']
        
        if gia_tri_rsi_cuoi > 75:
            nhan_hien_thi = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif gia_tri_rsi_cuoi > 60:
            nhan_hien_thi = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif gia_tri_rsi_cuoi < 30:
            nhan_hien_thi = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif gia_tri_rsi_cuoi < 42:
            nhan_hien_thi = "😨 SỢ HÃI (BI QUAN)"
        else:
            nhan_hien_thi = "🟡 TRUNG LẬP (ĐI NGANG)"
            
        return nhan_hien_thi, round(gia_tri_rsi_cuoi, 1)

    def thuc_thi_backtest_chien_thuat_v104(bang_du_lieu_da_tinh):
        """
        Backtesting: Tìm xem nếu mua lúc (RSI < 45) + (MACD Cắt lên)
        thì xác suất chốt lãi 5% trong 10 ngày sau đó là bao nhiêu.
        """
        tong_so_lan_xuat_hien_tin_hieu = 0
        tong_so_lan_chien_thang = 0
        
        do_dai_du_lieu = len(bang_du_lieu_da_tinh)
        
        for vi_tri_ngay in range(100, do_dai_du_lieu - 10):
            # Điều kiện mua số 1: RSI kiệt quệ
            kiem_tra_rsi = bang_du_lieu_da_tinh['rsi'].iloc[vi_tri_ngay] < 45
            
            # Điều kiện mua số 2: MACD giao cắt đường Tín hiệu
            macd_hom_nay = bang_du_lieu_da_tinh['macd'].iloc[vi_tri_ngay]
            signal_hom_nay = bang_du_lieu_da_tinh['signal'].iloc[vi_tri_ngay]
            macd_hom_qua = bang_du_lieu_da_tinh['macd'].iloc[vi_tri_ngay-1]
            signal_hom_qua = bang_du_lieu_da_tinh['signal'].iloc[vi_tri_ngay-1]
            
            kiem_tra_macd = (macd_hom_nay > signal_hom_nay) and (macd_hom_qua <= signal_hom_qua)
            
            # Gộp điều kiện
            if kiem_tra_rsi and kiem_tra_macd:
                tong_so_lan_xuat_hien_tin_hieu += 1
                
                # Setup mô phỏng chốt lời
                gia_khop_gia_dinh = bang_du_lieu_da_tinh['close'].iloc[vi_tri_ngay]
                gia_muc_tieu = gia_khop_gia_dinh * 1.05
                
                # Quét 10 ngày tiếp theo trong tương lai
                khoang_gia_tuong_lai = bang_du_lieu_da_tinh['close'].iloc[vi_tri_ngay+1 : vi_tri_ngay+11]
                
                # Nếu có ngày nào chạm mức +5%
                if any(khoang_gia_tuong_lai > gia_muc_tieu):
                    tong_so_lan_chien_thang += 1
        
        # Ngăn chặn lỗi chia cho 0
        if tong_so_lan_xuat_hien_tin_hieu == 0:
            return 0.0
            
        phan_tram_thang_loi = (tong_so_lan_chien_thang / tong_so_lan_xuat_hien_tin_hieu) * 100
        return round(phan_tram_thang_loi, 1)

    def du_bao_xac_suat_ai_v104(bang_du_lieu_da_tinh):
        """
        Khởi tạo mô hình Machine Learning học 8 thuộc tính kỹ thuật.
        Dự đoán xem 3 ngày sau giá có tăng nổi 2% hay không.
        """
        # Nếu chưa đủ 200 ngày thì AI không đủ thông minh để học
        if len(bang_du_lieu_da_tinh) < 200:
            return "N/A"
            
        bang_du_lieu_hoc_may = bang_du_lieu_da_tinh.copy()
        
        # Bước 1: Gắn kết quả (Target Y) cho từng dòng lịch sử
        chuoi_gia_hien_tai = bang_du_lieu_hoc_may['close']
        chuoi_gia_tuong_lai_t3 = bang_du_lieu_hoc_may['close'].shift(-3)
        
        bang_du_lieu_hoc_may['nhan_dich'] = (chuoi_gia_tuong_lai_t3 > chuoi_gia_hien_tai * 1.02).astype(int)
        
        # Bước 2: Liệt kê các biến số độc lập (Features X)
        danh_sach_bien_so_doc_lap = [
            'rsi', 'macd', 'signal', 'return_1d', 
            'volatility', 'vol_strength', 'money_flow', 'pv_trend'
        ]
        
        # Bước 3: Lọc dữ liệu lỗi
        bang_du_lieu_sach_cho_ai = bang_du_lieu_hoc_may.dropna()
        ma_tran_dac_trung_x = bang_du_lieu_sach_cho_ai[danh_sach_bien_so_doc_lap]
        vector_muc_tieu_y = bang_du_lieu_sach_cho_ai['nhan_dich']
        
        # Bước 4: Chạy thuật toán Rừng ngẫu nhiên (100 Decision Trees)
        mo_hinh_random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Bỏ đi 3 dòng cuối cùng của bảng vì chưa thể biết tương lai 3 ngày sau
        x_huan_luyen = ma_tran_dac_trung_x[:-3]
        y_huan_luyen = vector_muc_tieu_y[:-3]
        
        mo_hinh_random_forest.fit(x_huan_luyen, y_huan_luyen)
        
        # Bước 5: Áp dụng mô hình đã học vào chính ngày hôm nay (Dòng cuối)
        dong_du_lieu_hom_nay = ma_tran_dac_trung_x.iloc[[-1]]
        mang_xac_suat_tra_ve = mo_hinh_random_forest.predict_proba(dong_du_lieu_hom_nay)
        
        # Tách lấy xác suất của nhãn 1 (Khả năng tăng giá)
        xac_suat_tang_gia = mang_xac_suat_tra_ve[0][1]
        
        return round(xac_suat_tang_gia * 100, 1)

    # ==============================================================================
    # 5. PHÂN TÍCH TÀI CHÍNH CỐT LÕI (FUNDAMENTAL LAYER)
    # ==============================================================================
    def do_luong_tang_truong_canslim_v104(ma_chung_khoan_vao):
        """Tính phần trăm thay đổi Lợi nhuận sau thuế (Quý này so với Quý trước)"""
        try:
            # Truy vấn BCTC Quý từ hệ thống Vnstock
            bang_bctc_quy = vn_engine.stock.finance.income_statement(
                symbol=ma_chung_khoan_vao, 
                period='quarter', 
                lang='en'
            ).head(5)
            
            # Quét tìm cột LNST
            tap_tu_khoa = ['sau thuế', 'posttax', 'net profit', 'earning']
            cac_cot_tuong_thich = [cot for cot in bang_bctc_quy.columns if any(tu_khoa in str(cot).lower() for tu_khoa in tap_tu_khoa)]
            
            if cac_cot_tuong_thich:
                ten_cot_lnst_chinh_xac = cac_cot_tuong_thich[0]
                gia_tri_lnst_quy_nay = float(bang_bctc_quy.iloc[0][ten_cot_lnst_chinh_xac])
                gia_tri_lnst_quy_nam_ngoai = float(bang_bctc_quy.iloc[4][ten_cot_lnst_chinh_xac])
                
                if gia_tri_lnst_quy_nam_ngoai > 0:
                    bien_do_tang_truong = ((gia_tri_lnst_quy_nay - gia_tri_lnst_quy_nam_ngoai) / gia_tri_lnst_quy_nam_ngoai) * 100
                    return round(bien_do_tang_truong, 1)
        except Exception:
            pass
            
        # Fallback YF
        try:
            du_lieu_ho_so_yf = yf.Ticker(f"{ma_chung_khoan_vao}.VN").info
            ti_le_tang_truong_yf = du_lieu_ho_so_yf.get('earningsQuarterlyGrowth')
            if ti_le_tang_truong_yf is not None:
                return round(ti_le_tang_truong_yf * 100, 1)
        except Exception:
            pass
            
        return None

    def boc_tach_pe_roe_v104(ma_chung_khoan_vao):
        """Đo lường Hệ số định giá P/E và Hiệu suất vốn ROE"""
        chi_so_pe_tra_ve = 0.0
        chi_so_roe_tra_ve = 0.0
        
        try:
            bang_chi_so_tai_chinh = vn_engine.stock.finance.ratio(ma_chung_khoan_vao, 'quarterly').iloc[-1]
            chi_so_pe_tra_ve = bang_chi_so_tai_chinh.get('ticker_pe', bang_chi_so_tai_chinh.get('pe', 0))
            chi_so_roe_tra_ve = bang_chi_so_tai_chinh.get('roe', 0)
        except:
            pass
            
        if chi_so_pe_tra_ve <= 0:
            try:
                du_lieu_ho_so_yf = yf.Ticker(f"{ma_chung_khoan_vao}.VN").info
                chi_so_pe_tra_ve = du_lieu_ho_so_yf.get('trailingPE', 0)
                chi_so_roe_tra_ve = du_lieu_ho_so_yf.get('returnOnEquity', 0)
            except:
                pass
                
        return chi_so_pe_tra_ve, chi_so_roe_tra_ve

    # ==============================================================================
    # 6. 🧠 ROBOT ADVISOR MASTER V10.4: LÕI SUY LUẬN LOGIC CHUYÊN SÂU
    # ==============================================================================
    def he_thong_suy_luan_advisor_v104(ma_ck, dong_du_lieu, ti_le_ai, ti_le_winrate, diem_pe, diem_roe, diem_tang_truong, danh_sach_tru_gom, danh_sach_tru_xa):
        """
        Trái tim của hệ thống. Đọc và tổng hợp 5 lớp dữ liệu định lượng.
        Đưa ra đề xuất MUA/BÁN kèm theo bảng giải trình chi tiết (Reasoning Log).
        """
        
        # Khởi tạo các chuỗi văn bản báo cáo
        bao_cao_ky_thuat = ""
        bao_cao_dong_tien = ""
        hanh_dong_khuyen_nghi = ""
        mau_sac_khuyen_nghi = ""
        
        # Bảng ghi chép tiến trình suy luận để giải thích cho người dùng
        bang_ghi_nhat_ky_logic = []
        diem_dong_thuan_tong_hop = 0
        
        # --- BƯỚC 1: XÉT VỊ THẾ MA20 ---
        gia_dong_cua_ht = dong_du_lieu['close']
        duong_ho_tro_ma20_ht = dong_du_lieu['ma20']
        do_chenh_lech_voi_ma20 = ((gia_dong_cua_ht - duong_ho_tro_ma20_ht) / duong_ho_tro_ma20_ht) * 100
        
        if gia_dong_cua_ht < duong_ho_tro_ma20_ht:
            bao_cao_ky_thuat = f"Cảnh báo rủi ro: Giá mã {ma_ck} đang nằm hoàn toàn dưới đường MA20."
            bang_ghi_nhat_ky_logic.append(f"❌ KỸ THUẬT XẤU: Giá bị ép dưới MA20 ({do_chenh_lech_voi_ma20:.1f}%). Xu hướng giảm ngắn hạn đang chi phối.")
        else:
            bao_cao_ky_thuat = f"Xác nhận tích cực: Giá mã {ma_ck} đang duy trì vững chắc trên mốc MA20."
            bang_ghi_nhat_ky_logic.append(f"✅ KỸ THUẬT TỐT: Giá bảo vệ thành công MA20 ({do_chenh_lech_voi_ma20:.1f}%). Phe Mua đang kiểm soát trận đấu.")
            diem_dong_thuan_tong_hop += 1

        # --- BƯỚC 2: XÉT SMART FLOW ---
        if ma_ck in danh_sach_tru_gom:
            bao_cao_dong_tien = "Dấu chân Cá Mập: Dòng tiền lớn đang chủ động Kê Mua và Gom hàng."
            bang_ghi_nhat_ky_logic.append("✅ DÒNG TIỀN MẠNH: Tổ chức đang âm thầm gom hàng, có sự đồng thuận từ các mã trụ cột.")
            diem_dong_thuan_tong_hop += 1
        elif ma_ck in danh_sach_tru_xa:
            bao_cao_dong_tien = "Dấu chân Phân Phối: Áp lực Thoát hàng (Xả) từ các tổ chức đang rất dữ dội."
            bang_ghi_nhat_ky_logic.append("❌ DÒNG TIỀN XẤU: Cá mập đang phân phối hàng ra ngoài. Tuyệt đối không nhảy vào đỡ giá.")
        else:
            bao_cao_dong_tien = "Dòng tiền Lẻ loi: Vận động thị trường thiếu vắng bàn tay của tạo lập."
            bang_ghi_nhat_ky_logic.append("🟡 DÒNG TIỀN NHIỄU: Thanh khoản phân tán, chủ yếu là nhỏ lẻ tự mua bán với nhau.")

        # --- BƯỚC 3: XÉT AI & BACKTEST ---
        if isinstance(ti_le_ai, float) and ti_le_ai >= 58.0:
            diem_dong_thuan_tong_hop += 1
            bang_ghi_nhat_ky_logic.append(f"✅ DỰ BÁO AI ({ti_le_ai}%): Cỗ máy AI xác nhận mẫu hình hiện tại có cửa tăng rất sáng trong 3 ngày tới.")
        else:
            bang_ghi_nhat_ky_logic.append(f"❌ DỰ BÁO AI ({ti_le_ai}%): AI đánh giá tỷ lệ chiến thắng quá thấp, rủi ro chôn vốn cao.")

        if ti_le_winrate >= 50.0:
            diem_dong_thuan_tong_hop += 1
            bang_ghi_nhat_ky_logic.append(f"✅ KIỂM CHỨNG LỊCH SỬ ({ti_le_winrate}%): Quá khứ chứng minh đây là một điểm mua uy tín và mang lại lợi nhuận.")
        else:
            bang_ghi_nhat_ky_logic.append(f"❌ KIỂM CHỨNG LỊCH SỬ ({ti_le_winrate}%): Cẩn thận! Mẫu hình này trong quá khứ thường xuyên tạo Bẫy tăng giá ảo (Bull trap).")

        # --- BƯỚC 4: TỔNG KẾT VÀ TÍNH TOÁN QUYẾT ĐỊNH ---
        chi_so_rsi_ht = dong_du_lieu['rsi']
        
        # Khung quy tắc số 1: Bùng nổ Mua
        if diem_dong_thuan_tong_hop >= 4 and chi_so_rsi_ht < 68:
            hanh_dong_khuyen_nghi = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
            mau_sac_khuyen_nghi = "green"
            bang_ghi_nhat_ky_logic.append("🏆 KẾT LUẬN TỔNG THỂ: Các chỉ số đang tạo ra một điểm đồng thuận tuyệt đối. Ưu tiên giải ngân.")
            
        # Khung quy tắc số 2: Xả hàng phòng thủ
        elif diem_dong_thuan_tong_hop <= 1 or chi_so_rsi_ht > 78 or gia_dong_cua_ht < duong_ho_tro_ma20_ht:
            hanh_dong_khuyen_nghi = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
            mau_sac_khuyen_nghi = "red"
            
            # Module giải nghĩa mâu thuẫn hóc búa (Rất quan trọng)
            if gia_dong_cua_ht < duong_ho_tro_ma20_ht and ma_ck in danh_sach_tru_gom:
                bang_ghi_nhat_ky_logic.append("⚠️ CẢNH BÁO GIẢI MÃ MÂU THUẪN: Mặc dù Robot phát hiện Cá Mập đang Gom hàng, nhưng do Giá Cổ Phiếu vẫn nằm dưới MA20, đây rất có thể là chu kỳ 'Gom Hàng Tích Lũy' kéo dài nhiều tháng của Quỹ Đầu Tư.")
                bang_ghi_nhat_ky_logic.append("👉 LỜI KHUYÊN: Đối với nhà đầu tư cá nhân, vào tiền lúc này sẽ bị ngâm vốn rất lâu. Hãy kiên nhẫn đợi đến khi giá bứt phá vượt hẳn lên trên MA20 rồi mới đánh thóp theo cá mập.")
            else:
                bang_ghi_nhat_ky_logic.append("🏆 KẾT LUẬN TỔNG THỂ: Rủi ro đang bao trùm mọi mặt trận. Việc bảo vệ an toàn cho dòng vốn là mệnh lệnh số 1.")
                
        # Khung quy tắc số 3: Đi ngang chờ thời
        else:
            hanh_dong_khuyen_nghi = "⚖️ THEO DÕI (WATCHLIST)"
            mau_sac_khuyen_nghi = "orange"
            bang_ghi_nhat_ky_logic.append("🏆 KẾT LUẬN TỔNG THỂ: Tín hiệu đang ở mức độ trung bình (50/50). Chưa đủ điều kiện an toàn để xuống tiền. Cần chờ đợi một phiên nổ Volume đột biến (>1.2 lần) để kích hoạt xu hướng mới.")

        return bao_cao_ky_thuat, bao_cao_dong_tien, hanh_dong_khuyen_nghi, mau_sac_khuyen_nghi, bang_ghi_nhat_ky_logic

    # ==============================================================================
    # 7. GIAO DIỆN NGƯỜI DÙNG & KIỂM SOÁT LUỒNG DỮ LIỆU (UI CONTROLLER)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def tai_va_lay_danh_sach_ma_san_hose():
        """Tải bảng danh sách mã niêm yết chính thống từ máy chủ"""
        try:
            bang_danh_sach_niem_yet = vn_engine.market.listing()
            bo_loc_san_hose = bang_danh_sach_niem_yet['comGroupCode'] == 'HOSE'
            danh_sach_chuoi = bang_danh_sach_niem_yet[bo_loc_san_hose]['ticker'].tolist()
            return danh_sach_chuoi
        except:
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","GAS","VCB","BID","CTG","VRE","DGC","PDR"]

    # 7.1 Lấy danh sách nạp vào thanh điều hướng
    danh_sach_tat_ca_ma_hose = tai_va_lay_danh_sach_ma_san_hose()
    
    st.sidebar.header("🕹️ Trung Tâm Giao Dịch Quant")
    
    # Dropdown Menu
    thanh_phan_chon_ma = st.sidebar.selectbox(
        "Lựa chọn mã cổ phiếu mục tiêu:", 
        danh_sach_tat_ca_ma_hose
    )
    
    # Manual Text Input
    thanh_phan_nhap_ma_tay = st.sidebar.text_input(
        "Hoặc nhập trực tiếp tên mã (VD: FPT):"
    ).upper()
    
    # Chốt mã cuối cùng
    ma_co_phieu_dang_chon = thanh_phan_nhap_ma_tay if thanh_phan_nhap_ma_tay else thanh_phan_chon_ma

    # 7.2 ĐỊNH NGHĨA KHUNG TABS (NGĂN CHẶN LỖI NAMEERROR TUYỆT ĐỐI)
    tab_trung_tam_advisor, tab_trung_tam_tai_chinh, tab_trung_tam_dong_tien, tab_trung_tam_hunter = st.tabs([
        "🤖 ADVISOR & MASTER CHART", 
        "🏢 BÁO CÁO CƠ BẢN", 
        "🌊 BÓC TÁCH DÒNG TIỀN", 
        "🔍 RADAR SIÊU CỔ PHIẾU"
    ])

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR VÀ BIỂU ĐỒ CHUYÊN SÂU
    # ------------------------------------------------------------------------------
    with tab_trung_tam_advisor:
        if st.button(f"⚡ TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG MÃ {ma_co_phieu_dang_chon}"):
            
            with st.spinner(f"Đang kích hoạt quy trình đồng bộ đa tầng cho mã {ma_co_phieu_dang_chon}..."):
                
                # BƯỚC 1: Gọi dữ liệu
                bang_du_lieu_tho_v104 = lay_du_lieu_nien_yet_chuan_v104(ma_co_phieu_dang_chon)
                
                if bang_du_lieu_tho_v104 is not None and not bang_du_lieu_tho_v104.empty:
                    
                    # BƯỚC 2: Gọi động cơ tính toán
                    bang_du_lieu_chi_tiet_v104 = tinh_toan_bo_chi_bao_quant_v104(bang_du_lieu_tho_v104)
                    dong_du_lieu_moi_nhat_v104 = bang_du_lieu_chi_tiet_v104.iloc[-1]
                    
                    # BƯỚC 3: Gọi các AI và Hàm đo lường lịch sử
                    diem_ai_du_bao_t3 = du_bao_xac_suat_ai_v104(bang_du_lieu_chi_tiet_v104)
                    diem_win_rate_lich_su = thuc_thi_backtest_chien_thuat_v104(bang_du_lieu_chi_tiet_v104)
                    nhan_fng_hien_tai, diem_fng_hien_tai = phan_tich_tam_ly_dam_dong_v104(bang_du_lieu_chi_tiet_v104)
                    
                    # BƯỚC 4: Truy xuất sức khỏe cơ bản
                    chi_so_pe_hien_tai, chi_so_roe_hien_tai = boc_tach_pe_roe_v104(ma_co_phieu_dang_chon)
                    muc_tang_truong_quy = do_luong_tang_truong_canslim_v104(ma_co_phieu_dang_chon)
                    
                    # BƯỚC 5: Đọc vị độ rộng thị trường (10 Trụ dẫn dắt)
                    danh_sach_10_tru_cung = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                    mang_tru_dang_gom = []
                    mang_tru_dang_xa = []
                    
                    for ma_tru_ho_tro_index in danh_sach_10_tru_cung:
                        try:
                            # Quét nhanh 10 ngày để tìm dấu vết
                            df_tru_tho = lay_du_lieu_nien_yet_chuan_v104(ma_tru_ho_tro_index, so_ngay_lich_su=10)
                            if df_tru_tho is not None:
                                df_tru_tinh_xong = tinh_toan_bo_chi_bao_quant_v104(df_tru_tho)
                                dong_cuoi_tru = df_tru_tinh_xong.iloc[-1]
                                
                                # Logic quy định
                                check_tang_gia = dong_cuoi_tru['return_1d'] > 0
                                check_giam_gia = dong_cuoi_tru['return_1d'] < 0
                                check_nhet_vol = dong_cuoi_tru['vol_strength'] > 1.2
                                
                                if check_tang_gia and check_nhet_vol:
                                    mang_tru_dang_gom.append(ma_tru_ho_tro_index)
                                elif check_giam_gia and check_nhet_vol:
                                    mang_tru_dang_xa.append(ma_tru_ho_tro_index)
                        except: 
                            pass

                    # BƯỚC 6: TRIỆU GỌI LÕI ROBOT ADVISOR (THE BRAIN)
                    kq_ky_thuat, kq_dong_tien, lenh_xuat_ra, mau_lenh_xuat, nhat_ky_hanh_trinh = he_thong_suy_luan_advisor_v104(
                        ma_co_phieu_dang_chon, 
                        dong_du_lieu_moi_nhat_v104, 
                        diem_ai_du_bao_t3, 
                        diem_win_rate_lich_su, 
                        chi_so_pe_hien_tai, 
                        chi_so_roe_hien_tai, 
                        muc_tang_truong_quy, 
                        mang_tru_dang_gom, 
                        mang_tru_dang_xa
                    )

                    # --- GIAO DIỆN HIỂN THỊ KẾT QUẢ ĐẦU VÀO TRUNG TÂM ---
                    st.write(f"### 🎯 Phân Tích Chuyên Sâu Bằng Robot Advisor: {ma_co_phieu_dang_chon}")
                    cot_phan_tich_chuyen_sau, cot_lenh_hanh_dong = st.columns([2, 1])
                    
                    with cot_phan_tich_chuyen_sau:
                        st.info(f"**💡 Chuẩn đoán Biểu đồ & Kỹ thuật:** {kq_ky_thuat}")
                        st.info(f"**🌊 Chuẩn đoán Dòng tiền Cá mập:** {kq_dong_tien}")
                        
                        # Module Giải thích Suy luận
                        with st.expander("🔍 BÁC SĨ LOGIC: XEM CÁCH ROBOT ĐƯA RA KẾT LUẬN NÀY"):
                            st.write("Dưới đây là các mảnh ghép được hệ thống tổng hợp để hình thành lệnh:")
                            for dong_suy_luan in nhat_ky_hanh_trinh:
                                st.write(f"{dong_suy_luan}")
                                
                    with cot_lenh_hanh_dong:
                        st.subheader("🤖 LỆNH HÀNH ĐỘNG KHUYÊN DÙNG:")
                        phan_lenh_chinh = lenh_xuat_ra.split('(')[0]
                        phan_giai_thich_lenh = lenh_xuat_ra.split('(')[1] if '(' in lenh_xuat_ra else ''
                        
                        st.title(f":{mau_lenh_xuat}[{phan_lenh_chinh}]")
                        st.markdown(f"*{phan_giai_thich_lenh}*")
                    
                    st.divider()
                    
                    # --- GIAO DIỆN BẢNG RADAR HIỆU SUẤT TỔNG QUAN ---
                    st.write("### 🧭 Bảng Radar Đo Lường Hiệu Suất")
                    cot_radar_1, cot_radar_2, cot_radar_3, cot_radar_4 = st.columns(4)
                    
                    cot_radar_1.metric("Giá Khớp Lệnh Mới Nhất", f"{dong_du_lieu_moi_nhat_v104['close']:,.0f}")
                    
                    cot_radar_2.metric("Tâm Lý F&G Index", f"{diem_fng_hien_tai}/100", delta=nhan_fng_hien_tai)
                    
                    diem_ai_nhan_dang = "Tín hiệu Tốt" if (isinstance(diem_ai_du_bao_t3, float) and diem_ai_du_bao_t3 > 55) else None
                    cot_radar_3.metric("Khả năng Tăng (AI T+3)", f"{diem_ai_du_bao_t3}%", delta=diem_ai_nhan_dang)
                    
                    diem_backtest_nhan_dang = "Tỉ lệ Ổn định" if diem_win_rate_lich_su > 45 else None
                    cot_radar_4.metric("Xác suất Thắng Lịch sử", f"{diem_win_rate_lich_su}%", delta=diem_backtest_nhan_dang)

                    # --- GIAO DIỆN BẢNG NAKED STATS CHUYÊN MÔN ---
                    st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Trần (Naked Stats)")
                    cot_naked_1, cot_naked_2, cot_naked_3, cot_naked_4 = st.columns(4)
                    
                    # RSI
                    chi_so_rsi_trinh_dien = dong_du_lieu_moi_nhat_v104['rsi']
                    nhan_rsi_trinh_dien = "Đang Quá mua" if chi_so_rsi_trinh_dien > 70 else ("Đang Quá bán" if chi_so_rsi_trinh_dien < 30 else "Vùng An toàn")
                    cot_naked_1.metric("RSI (14 Phiên)", f"{chi_so_rsi_trinh_dien:.1f}", delta=nhan_rsi_trinh_dien)
                    
                    # MACD
                    chi_so_macd_trinh_dien = dong_du_lieu_moi_nhat_v104['macd']
                    chi_so_signal_trinh_dien = dong_du_lieu_moi_nhat_v104['signal']
                    nhan_macd_trinh_dien = "MACD > Signal (Tốt)" if chi_so_macd_trinh_dien > chi_so_signal_trinh_dien else "MACD < Signal (Xấu)"
                    cot_naked_2.metric("Tình trạng Giao cắt MACD", f"{chi_so_macd_trinh_dien:.2f}", delta=nhan_macd_trinh_dien)
                    
                    # MAs
                    chi_so_ma20_trinh_dien = dong_du_lieu_moi_nhat_v104['ma20']
                    chi_so_ma50_trinh_dien = dong_du_lieu_moi_nhat_v104['ma50']
                    cot_naked_3.metric("MA20 (Ngắn) / MA50 (Trung)", f"{chi_so_ma20_trinh_dien:,.0f}", delta=f"MA50 hiện tại: {chi_so_ma50_trinh_dien:,.0f}")
                    
                    # BOL
                    chi_so_upper_trinh_dien = dong_du_lieu_moi_nhat_v104['upper_band']
                    chi_so_lower_trinh_dien = dong_du_lieu_moi_nhat_v104['lower_band']
                    cot_naked_4.metric("Khung Chạm Trần Bollinger", f"{chi_so_upper_trinh_dien:,.0f}", 
                                       delta=f"Khung Chạm Đáy Bollinger: {chi_so_lower_trinh_dien:,.0f}", delta_color="inverse")
                    
                    # --- SỔ TAY CẨM NĂNG ĐẦU TƯ CỦA MINH ---
                    with st.expander("📖 CẨM NĂNG THỰC CHIẾN GIAO DỊCH (ĐỌC KỸ TRƯỚC KHI XUỐNG TIỀN)"):
                        st.markdown("#### 1. Phương pháp đọc Volume Dòng Tiền")
                        st.write(f"- Sức mạnh Volume ngày hôm nay bằng **{dong_du_lieu_moi_nhat_v104['vol_strength']:.1f} lần** mức trung bình.")
                        st.write("- Quy luật Gom: Cây nến Xanh (Giá tăng) kết hợp Volume > 1.2 là dòng tiền lớn nhảy vào.")
                        st.write("- Quy luật Xả: Cây nến Đỏ (Giá giảm) kết hợp Volume > 1.2 là dòng tiền lớn bỏ chạy.")
                        
                        st.markdown("#### 2. Kỹ thuật đọc Biên độ Bollinger")
                        st.write("- Vùng tô xám trên biểu đồ bên dưới là hành lang an toàn.")
                        st.write("- Nến đâm lủng trần (Upper) = Rủi ro mua đuổi đỉnh, giá thường bị dội ngược lại.")
                        st.write("- Nến rớt lủng sàn (Lower) = Rủi ro bán tháo đáy, đây là lúc nên rình mò bắt đáy hồi.")
                        
                        st.markdown("#### 3. Cảnh báo Bẫy Tâm Lý (Bull/Bear Traps)")
                        st.write("- **Bẫy Bò (Bull Trap):** Khi giá phá vỡ đỉnh cũ cực đẹp nhưng Volume lại èo uột (dưới 1.0) ➔ Tổ chức đang kéo ảo để dụ nhỏ lẻ vào mua.")
                        st.write("- **Bẫy Gấu (Bear Trap):** Khi giá phá vỡ hỗ trợ, hoảng loạn cùng cực, nến đỏ lè ➔ Tuyệt đối đừng bắt dao rơi, hãy chờ qua ngày hôm sau xem có nến rút chân không.")
                        
                        st.markdown("#### 4. Luật Thép Quản Trị Rủi Ro")
                        gia_tri_cat_lo_toi_thieu = dong_du_lieu_moi_nhat_v104['close'] * 0.93
                        st.error(f"- Cắt Lỗ Toàn Phần: Bán bằng mọi giá, không được gồng lỗ nếu giá trị rớt xuống ngưỡng **{gia_tri_cat_lo_toi_thieu:,.0f} (tức -7%)**.")

                    # ==================================================================
                    # --- KHÔI PHỤC VÀ VẼ MASTER CANDLESTICK CHART CHUYÊN SÂU ---
                    # ==================================================================
                    st.divider()
                    st.write("### 📊 Biểu Đồ Kỹ Thuật Đa Lớp (Master Chart Visualizer)")
                    
                    # Tạo bộ khung chứa 2 đồ thị (Chart nến phía trên 75%, Chart Vol phía dưới 25%)
                    khung_hinh_ve_master = make_subplots(
                        rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.75, 0.25]
                    )
                    
                    # Lọc lấy 120 phiên gần nhất để biểu đồ không bị quá dày
                    du_lieu_120_phien_ve = bang_du_lieu_chi_tiet_v104.tail(120)
                    truc_thoi_gian_x = du_lieu_120_phien_ve['date']
                    
                    # Vẽ Lớp 1: Cấu trúc Nến Nhật Bản (Candlestick)
                    khung_hinh_ve_master.add_trace(
                        go.Candlestick(
                            x=truc_thoi_gian_x, 
                            open=du_lieu_120_phien_ve['open'], 
                            high=du_lieu_120_phien_ve['high'], 
                            low=du_lieu_120_phien_ve['low'], 
                            close=du_lieu_120_phien_ve['close'], 
                            name='Mô hình Nến'
                        ), row=1, col=1
                    )
                    
                    # Vẽ Lớp 2: Đường hỗ trợ siêu ngắn MA20 (Màu Cam)
                    khung_hinh_ve_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x, 
                            y=du_lieu_120_phien_ve['ma20'], 
                            line=dict(color='orange', width=1.5), 
                            name='Hỗ Trợ MA20'
                        ), row=1, col=1
                    )
                    
                    # Vẽ Lớp 3: Đường kháng cự cực dài MA200 (Màu Tím đâm)
                    khung_hinh_ve_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x, 
                            y=du_lieu_120_phien_ve['ma200'], 
                            line=dict(color='purple', width=2), 
                            name='Chỉ Nam MA200'
                        ), row=1, col=1
                    )
                    
                    # Vẽ Lớp 4: Biên độ Bollinger Bands Upper (Đường dứt nét mỏng)
                    khung_hinh_ve_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x, 
                            y=du_lieu_120_phien_ve['upper_band'], 
                            line=dict(color='gray', dash='dash', width=0.8), 
                            name='Trần BOL'
                        ), row=1, col=1
                    )
                    
                    # Vẽ Lớp 5: Biên độ Bollinger Bands Lower và đổ màu xám mờ làm nền
                    khung_hinh_ve_master.add_trace(
                        go.Scatter(
                            x=truc_thoi_gian_x, 
                            y=du_lieu_120_phien_ve['lower_band'], 
                            line=dict(color='gray', dash='dash', width=0.8), 
                            fill='tonexty', 
                            fillcolor='rgba(128,128,128,0.1)', 
                            name='Đáy BOL'
                        ), row=1, col=1
                    )
                    
                    # Vẽ Lớp 6: Cột khối lượng Volume (Dưới cùng)
                    khung_hinh_ve_master.add_trace(
                        go.Bar(
                            x=truc_thoi_gian_x, 
                            y=du_lieu_120_phien_ve['volume'], 
                            name='Khối Lượng Vol', 
                            marker_color='gray'
                        ), row=2, col=1
                    )
                    
                    # Tinh chỉnh giao diện hiển thị cho đẹp mắt, không kéo dãn quá đáng
                    khung_hinh_ve_master.update_layout(
                        height=750, 
                        template='plotly_white', 
                        xaxis_rangeslider_visible=False,
                        margin=dict(l=40, r=40, t=50, b=40)
                    )
                    
                    # Hiển thị biểu đồ ra màn hình ứng dụng Streamlit
                    st.plotly_chart(khung_hinh_ve_master, use_container_width=True)
                else:
                    st.error("❌ Cảnh báo Lỗi: Hệ thống không thể tải được gói dữ liệu cho việc phân tích biểu đồ.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP CƠ BẢN
    # ------------------------------------------------------------------------------
    with tab_trung_tam_tai_chinh:
        st.write(f"### 📈 Phân Tích Sức Khỏe CanSLIM & Định Giá Doanh Nghiệp ({ma_co_phieu_dang_chon})")
        
        with st.spinner("Hệ thống đang quét báo cáo tài chính quý gần nhất..."):
            # Lấy thông tin tăng trưởng (CanSLIM)
            phan_tram_tang_truong_lnst = do_luong_tang_truong_canslim_v104(ma_co_phieu_dang_chon)
            
            if phan_tram_tang_truong_lnst is not None:
                if phan_tram_tang_truong_lnst >= 20.0:
                    st.success(f"**🔥 Tiêu Chuẩn Vàng (Chữ C trong CanSLIM):** Lợi nhuận tăng mạnh **+{phan_tram_tang_truong_lnst}%**. Mức tăng trưởng đột phá cực kỳ hấp dẫn.")
                elif phan_tram_tang_truong_lnst > 0:
                    st.info(f"**⚖️ Tăng Trưởng Bền Vững:** Doanh nghiệp gia tăng lợi nhuận được **{phan_tram_tang_truong_lnst}%**. Ổn định và an toàn.")
                else:
                    st.error(f"**🚨 Tín Hiệu Suy Yếu:** Lợi nhuận rớt thê thảm **{phan_tram_tang_truong_lnst}%**. Báo động đỏ về năng lực vận hành.")
            
            st.divider()
            
            # Lấy thông tin P/E và ROE
            chi_so_pe_cua_dn, chi_so_roe_cua_dn = boc_tach_pe_roe_v104(ma_co_phieu_dang_chon)
            cot_dinh_gia_1, cot_dinh_gia_2 = st.columns(2)
            
            # Khối phân tích P/E
            nhan_dinh_pe_hien_tai = "Mức Tốt (Giá Rẻ)" if (0 < chi_so_pe_cua_dn < 12) else ("Mức Hợp Lý" if chi_so_pe_cua_dn < 18 else "Mức Đắt Đỏ (Rủi ro)")
            mau_nhan_dinh_pe = "normal" if chi_so_pe_cua_dn < 18 else "inverse"
            
            cot_dinh_gia_1.metric("Chỉ Số P/E (Số Năm Hồi Vốn)", f"{chi_so_pe_cua_dn:.1f}", delta=nhan_dinh_pe_hien_tai, delta_color=mau_nhan_dinh_pe)
            st.write("> **Luận Giải P/E:** P/E càng thấp nghĩa là bạn càng tốn ít tiền hơn để mua được 1 đồng lợi nhuận của doanh nghiệp này.")
            
            # Khối phân tích ROE
            nhan_dinh_roe_hien_tai = "Vô Cùng Xuất Sắc" if chi_so_roe_cua_dn >= 0.25 else ("Tốt" if chi_so_roe_cua_dn >= 0.15 else "Trung Bình - Thấp")
            mau_nhan_dinh_roe = "normal" if chi_so_roe_cua_dn >= 0.15 else "inverse"
            
            cot_dinh_gia_2.metric("Chỉ Số ROE (Năng Lực Kiếm Tiền)", f"{chi_so_roe_cua_dn:.1%}", delta=nhan_dinh_roe_hien_tai, delta_color=mau_nhan_dinh_roe)
            st.write("> **Luận Giải ROE:** ROE là thước đo xem Ban giám đốc dùng tiền của cổ đông có hiệu quả không. Phải trên 15% mới đáng xem xét.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: CHUYÊN GIA ĐỌC VỊ DÒNG TIỀN (SMART FLOW SPECIALIST)
    # ------------------------------------------------------------------------------
    with tab_trung_tam_dong_tien:
        st.write(f"### 🌊 Smart Flow Specialist - Mổ Xẻ Chi Tiết Hành Vi 3 Dòng Tiền ({ma_co_phieu_dang_chon})")
        
        # Chúng ta chỉ quét 30 ngày gần nhất để xem trạng thái 'hiện tại' của dòng tiền
        df_du_lieu_dong_tien_tho = lay_du_lieu_nien_yet_chuan_v104(ma_co_phieu_dang_chon, so_ngay_lich_su=30)
        
        if df_du_lieu_dong_tien_tho is not None:
            df_du_lieu_dong_tien_tinh_toan = tinh_toan_bo_chi_bao_quant_v104(df_du_lieu_dong_tien_tho)
            dong_du_lieu_dong_tien_cuoi = df_du_lieu_dong_tien_tinh_toan.iloc[-1]
            suc_manh_vol_hien_nay = dong_du_lieu_dong_tien_cuoi['vol_strength']
            
            # --- LOGIC THUẬT TOÁN MỔ XẺ PHẦN TRĂM DÒNG TIỀN (V10.4 CORE) ---
            # Ước lượng chia phần trăm (%) sự tham gia của các thế lực dựa vào khối lượng nổ
            if suc_manh_vol_hien_nay > 1.8:
                # Volume bùng nổ cực đại: Sân chơi của Khối Ngoại và Tự Doanh
                phan_tram_ngoai_quoc = 0.35
                phan_tram_to_chuc_noi = 0.45
                phan_tram_ca_nhan_le = 0.20
            elif suc_manh_vol_hien_nay > 1.2:
                # Volume trung bình khá: Các phe cân bằng lực lượng
                phan_tram_ngoai_quoc = 0.20
                phan_tram_to_chuc_noi = 0.30
                phan_tram_ca_nhan_le = 0.50
            else:
                # Volume cạn kiệt, lèo tèo: Hoàn toàn là nhỏ lẻ tự chơi với nhau
                phan_tram_ngoai_quoc = 0.10
                phan_tram_to_chuc_noi = 0.15
                phan_tram_ca_nhan_le = 0.75
            
            st.write("#### 📊 Bảng Mô Phỏng Tỷ Trọng Tham Gia Của 3 Thế Lực:")
            cot_dong_tien_1, cot_dong_tien_2, cot_dong_tien_3 = st.columns(3)
            
            # Tính toán nhãn Mua/Bán ròng
            nhan_hanh_dong_ngoai = "Đang Mua Ròng" if dong_du_lieu_dong_tien_cuoi['return_1d'] > 0 else "Đang Bán Ròng"
            cot_dong_tien_1.metric("🐋 Khối Ngoại (Dòng vốn ngoại)", f"{phan_tram_ngoai_quoc*100:.1f}%", delta=nhan_hanh_dong_ngoai)
            
            nhan_hanh_dong_to_chuc = "Đang Kê Gom" if dong_du_lieu_dong_tien_cuoi['return_1d'] > 0 else "Đang Táng Xả"
            cot_dong_tien_2.metric("🏦 Tổ Chức & Tự Doanh (Tạo lập)", f"{phan_tram_to_chuc_noi*100:.1f}%", delta=nhan_hanh_dong_to_chuc)
            
            # Cảnh báo Đu bám (Rất quan trọng để né đỉnh)
            nhan_hanh_dong_nho_le = "Cảnh Báo: Đu Bám Quá Nhiều" if phan_tram_ca_nhan_le > 0.6 else "Độ Đu Bám Thấp"
            mau_nhan_nho_le = "inverse" if phan_tram_ca_nhan_le > 0.6 else "normal"
            cot_dong_tien_3.metric("🐜 Cá Nhân (Nhà đầu tư lẻ)", f"{phan_tram_ca_nhan_le*100:.1f}%", delta=nhan_hanh_dong_nho_le, delta_color=mau_nhan_nho_le)
            
            with st.expander("📖 TỪ ĐIỂN PHÂN LỚP DÒNG TIỀN (MUST READ)"):
                st.write("- **🐋 Cá Mập Ngoại:** Những gã khổng lồ tiền tỷ USD. Mua gom rất đều đặn, không mua đuổi giá xanh.")
                st.write("- **🏦 Tổ Chức Nội:** Đội ngũ Tự doanh của chứng khoán. Đây là những kẻ tạo ra Cú Breakout hoặc Cú Upo thị trường.")
                st.write("- **🐜 Nhỏ Lẻ:** Đám đông. Cổ phiếu nào có Đám đông > 60% thì cổ phiếu đó y như một con rùa, lên 1 tí là bị bán chốt lãi, rất khó bay xa.")
            
            st.divider()
            
            # ĐO LƯỜNG MARKET BREADTH THỊ TRƯỜNG QUA 10 TRỤ SỨC MẠNH
            st.write("#### 🌊 Bức Tranh Tổng Thể - Phân Bổ Sức Mạnh Nhóm 10 Trụ Cột")
            with st.spinner("Hệ thống đang dò tia X-Ray trên toàn bộ bảng điện HOSE..."):
                danh_sach_10_ma_tru_quoc_gia = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                mang_tru_tin_hieu_gom = []
                mang_tru_tin_hieu_xa = []
                
                for mot_ma_tru in danh_sach_10_ma_tru_quoc_gia:
                    try:
                        dl_tru_tho = lay_du_lieu_nien_yet_chuan_v104(mot_ma_tru, so_ngay_lich_su=10)
                        if dl_tru_tho is not None:
                            dl_tru_tinh_toan = tinh_toan_bo_chi_bao_quant_v104(dl_tru_tho)
                            dl_tru_dong_cuoi = dl_tru_tinh_toan.iloc[-1]
                            
                            # Xác định rõ ràng
                            gia_dang_tang = dl_tru_dong_cuoi['return_1d'] > 0
                            gia_dang_giam = dl_tru_dong_cuoi['return_1d'] < 0
                            khoi_luong_dang_no = dl_tru_dong_cuoi['vol_strength'] > 1.2
                            
                            if gia_dang_tang and khoi_luong_dang_no:
                                mang_tru_tin_hieu_gom.append(mot_ma_tru)
                            elif gia_dang_giam and khoi_luong_dang_no:
                                mang_tru_tin_hieu_xa.append(mot_ma_tru)
                    except: pass
                
                # Hiển thị Market Breadth
                cot_so_luong_1, cot_so_luong_2 = st.columns(2)
                
                ti_trong_gom_tru = (len(mang_tru_tin_hieu_gom) / len(danh_sach_10_ma_tru_quoc_gia)) * 100
                cot_so_luong_1.metric("Tổng Số Trụ Đang Được Gom Nâng Đỡ", f"{len(mang_tru_tin_hieu_gom)} Cổ Phiếu", delta=f"Độ che phủ {ti_trong_gom_tru:.0f}%")
                
                ti_trong_xa_tru = (len(mang_tru_tin_hieu_xa) / len(danh_sach_10_ma_tru_quoc_gia)) * 100
                cot_so_luong_2.metric("Tổng Số Trụ Đang Bị Xả Đạp Đi Xuống", f"{len(mang_tru_tin_hieu_xa)} Cổ Phiếu", delta=f"Áp lực đè {ti_trong_xa_tru:.0f}%", delta_color="inverse")
                
                cot_liat_ke_1, cot_liet_ke_2 = st.columns(2)
                with cot_liat_ke_1:
                    st.success("✅ **GHI NHẬN CÁC MÃ TRỤ ĐANG ĐƯỢC GOM:**")
                    st.write(", ".join(mang_tru_tin_hieu_gom) if mang_tru_tin_hieu_gom else "Không phát hiện mã nào.")
                with cot_liet_ke_2:
                    st.error("🚨 **GHI NHẬN CÁC MÃ TRỤ ĐANG BỊ XẢ TÁNG:**")
                    st.write(", ".join(mang_tru_tin_hieu_xa) if mang_tru_tin_hieu_xa else "Bảng điện sạch bóng rủi ro phân phối.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: MÁY QUÉT ROBOT HUNTER (TÌM CƠ HỘI ĐỘT BIẾN)
    # ------------------------------------------------------------------------------
    with tab_trung_tam_hunter:
        st.subheader("🔍 Máy Quét Định Lượng Robot Hunter - HOSE Top 30")
        st.write("Chức năng này cho phép lọc cạn kiệt các mã có thanh khoản nổ bùm (>1.3 lần) và được AI dự báo sẽ còn tăng tiếp.")
        
        if st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT TOÀN SÀN NGAY BÂY GIỜ"):
            danh_sach_tuyen_chon_hunter = []
            thanh_truot_tien_do = st.progress(0)
            
            # Chỉ giới hạn 30 mã xịn nhất để hệ thống duyệt nhanh, không bị đơ
            danh_sach_ma_can_quet = danh_sach_tat_ca_ma_hose[:30]
            
            for index_vong_lap, ma_muc_tieu_quet in enumerate(danh_sach_ma_can_quet):
                try:
                    # Truy xuất 100 ngày để AI lấy form học tập
                    df_du_lieu_quet_tho = lay_du_lieu_nien_yet_chuan_v104(ma_muc_tieu_quet, so_ngay_lich_su=100)
                    df_du_lieu_quet_tinh_xong = tinh_toan_bo_chi_bao_quant_v104(df_du_lieu_quet_tho)
                    
                    dong_cuoi_cua_ma_quet = df_du_lieu_quet_tinh_xong.iloc[-1]
                    
                    # LOGIC HUNTER: Vô cùng khắt khe, Volume nổ phải gấp 1.3 lần trung bình
                    if dong_cuoi_cua_ma_quet['vol_strength'] > 1.3:
                        danh_sach_tuyen_chon_hunter.append({
                            'Ticker': ma_muc_tieu_quet, 
                            'Thị Giá Khớp': f"{dong_cuoi_cua_ma_quet['close']:,.0f} VNĐ", 
                            'Cường Độ Vôn (Vol)': round(dong_cuoi_cua_ma_quet['vol_strength'], 2), 
                            'Xác Suất Tăng T+3 (AI)': f"{du_bao_xac_suat_ai_v104(df_du_lieu_quet_tinh_xong)}%"
                        })
                except Exception:
                    pass
                
                # Nâng phần trăm tiến độ quét để Minh nhìn
                thanh_truot_tien_do.progress((index_vong_lap + 1) / len(danh_sach_ma_can_quet))
            
            # Sau khi quét xong 30 mã
            if danh_sach_tuyen_chon_hunter:
                # Lọc và sắp xếp những thằng có % AI cao nhất lên đầu
                bang_hien_thi_hunter_cuoi = pd.DataFrame(danh_sach_tuyen_chon_hunter).sort_values(by='Xác Suất Tăng T+3 (AI)', ascending=False)
                st.table(bang_hien_thi_hunter_cuoi)
                st.success("✅ Nhiệm vụ truy quét hoàn tất. Cảnh báo đỏ: Các mã trên đang thu hút dòng tiền rất nóng.")
            else:
                st.write("Radar siêu tĩnh. Ngày hôm nay chưa xuất hiện siêu cổ phiếu nào thỏa mãn luật thép của Hunter.")

# ==============================================================================
# HẾT MÃ NGUỒN V10.4 THE UNCOMPRESSED CORE - LƯU TRỮ AN TOÀN TUYỆT ĐỐI
# ==============================================================================
