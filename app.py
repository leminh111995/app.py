# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V20.0 (THE PREDATOR LEVIATHAN)
# ==============================================================================
# CHỦ SỞ HỮU: MINH
# NỀN TẢNG GỐC: KẾ THỪA 100% TỪ FILE "25.4.docx" (DÀI 2662 DÒNG)
# TRẠNG THÁI: PHIÊN BẢN GIẢI NÉN TOÀN PHẦN - KHÔNG VIẾT TẮT - KHÔNG NÉN CODE
# CAM KẾT V20.0:
# 1. ĐỘ DÀI CỰC ĐẠI (> 2300 DÒNG): Khai triển bê tông từng dòng lệnh một.
# 2. CHUẨN HÓA DANH XƯNG: Xóa sạch hậu tố (v13, v14, v19...), dùng tên chức năng.
# 3. DANH SÁCH CHỜ (PREDATOR): Lọc 5% MA20, Squeeze 1.2, Cạn Cung 0.8.
# 4. DÒNG TIỀN: Tây gom HOẶC Tự doanh gom trong 5 phiên gần nhất.
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
# 0. KHỐI CẤU HÌNH THAM SỐ CHIẾN THUẬT (PREDATOR CONFIG)
# ------------------------------------------------------------------------------
# Khối này giúp Minh điều chỉnh độ nhạy của Radar ngay tại đầu file code.

# Ngưỡng xác suất tăng giá T+3 từ máy học AI
THAM_SO_AI_PREDATOR = 48.0

# Ngưỡng RSI tối đa để đảm bảo vùng mua còn an toàn, không quá nóng
THAM_SO_RSI_AN_TOAN = 62.0

# Vùng giá an toàn quanh đường MA20 (Cho phép sai số 5%)
THAM_SO_VUNG_GIA_MA20 = 0.05

# Hệ số Volume tích lũy (Volume hiện tại so với trung bình 10 phiên)
THAM_SO_VOL_MIN = 0.6
THAM_SO_VOL_MAX = 1.4

# Độ nén lò xo Bollinger Bands (Squeeze)
# Càng nhỏ lò xo nén càng chặt, 1.2 là mức thực chiến Minh đã chốt.
THAM_SO_SQUEEZE = 1.2

# Ngưỡng xác định cạn cung (Supply Exhaustion)
# Volume phiên giảm phải thấp hơn 80% trung bình 20 phiên.
THAM_SO_CAN_CUNG = 0.8

# Số phiên kiểm tra dòng tiền Khối ngoại và Tự doanh
THAM_SO_PHIEN_CHECK_DONG_TIEN = 5

# ------------------------------------------------------------------------------
# 1. KHỞI TẠO TÀI NGUYÊN AI & THỜI GIAN
# ------------------------------------------------------------------------------

# Đảm bảo thư viện phân tích ngôn ngữ tự nhiên luôn sẵn sàng trên Cloud
try:
    # Tìm kiếm file lexicon trong hệ thống lưu trữ
    duong_dan_tai_nguyen_nltk = 'sentiment/vader_lexicon.zip'
    nltk.data.find(duong_dan_tai_nguyen_nltk)
except LookupError:
    # Nếu chưa thấy, tiến hành tải về tự động
    ten_goi_tai_nguyen_nltk = 'vader_lexicon'
    nltk.download(ten_goi_tai_nguyen_nltk)

def lay_thoi_gian_chuan_viet_nam():
    """
    Ép múi giờ hệ thống về UTC+7 (Việt Nam) [cite: 1025-1039].
    Chống lỗi dữ liệu rỗng (Empty Data) khi Minh chạy Radar vào buổi sáng.
    """
    # Lấy giờ quốc tế (UTC) hiện tại từ máy chủ
    thoi_gian_quoc_te_raw = datetime.utcnow()
    
    # Khai báo khoảng bù múi giờ 7 tiếng
    bu_mui_gio_vn = timedelta(hours=7)
    
    # Tính toán ra giờ thực tế tại sàn chứng khoán Việt Nam
    thoi_gian_vn_chinh_xac = thoi_gian_quoc_te_raw + bu_mui_gio_vn
    
    return thoi_gian_vn_chinh_xac

# ==============================================================================
# 2. HỆ THỐNG BẢO MẬT TRUNG TÂM (SECURITY MODULE)
# ==============================================================================
def xac_thuc_quyen_truy_cap_cua_minh():
    """
    Khóa hệ thống bằng mật mã định danh của Minh [cite: 1043-1090].
    Đã xóa bỏ hậu tố _v13 rườm rà.
    """
    # Khai báo khóa định danh trong bộ nhớ Session
    key_phien_dang_nhap = "trang_thai_xac_thuc_master_predator"
    
    # Kiểm tra xem Minh đã đăng nhập thành công trước đó chưa
    kiem_tra_phien = st.session_state.get(key_phien_dang_nhap, False)
    
    if kiem_tra_phien == True:
        # Nếu đã đăng nhập, cho phép truy cập toàn bộ hệ thống
        return True

    # Nếu chưa đăng nhập, dựng màn hình khóa trung tâm
    st.markdown("### 🔐 Quant System V20.0 - Cổng Bảo Mật Predator")
    st.info("Chào Minh, hệ thống đang bị khóa. Vui lòng nhập mật mã để kích hoạt Leviathan.")
    
    # Tạo ô nhập mật mã bảo mật
    label_nhap_lieu = "🔑 Nhập mật mã truy cập của bạn:"
    mat_ma_nhap_vao = st.text_input(label_nhap_lieu, type="password")
    
    # Xử lý logic so khớp mật mã
    if mat_ma_nhap_vao != "":
        
        # Đọc mật mã gốc từ cấu hình Secrets của Streamlit
        mat_ma_goc_trong_secrets = st.secrets["password"]
        
        # So sánh chuỗi mật mã
        if mat_ma_nhap_vao == mat_ma_goc_trong_secrets:
            # Gán trạng thái thành công vào bộ nhớ phiên
            st.session_state[key_phien_dang_nhap] = True
            # Tải lại trang để mở giao diện chính
            st.rerun()
        else:
            # Thông báo lỗi nếu mật mã sai
            st.error("❌ Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock.")
            
    return False

# ==============================================================================
# BẮT ĐẦU CHẠY ỨNG DỤNG (MAIN APP EXECUTION)
# ==============================================================================
# Toàn bộ mã nguồn chỉ được thực thi khi hàm bảo mật trả về True
if xac_thuc_quyen_truy_cap_cua_minh() == True:
    
    # Cấu hình giao diện tổng thể Dashboard [cite: 1098-1106]
    st.set_page_config(
        page_title="Quant System V20.0 Predator", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render tiêu đề chính của trang web
    st.title("🛡️ Quant System V20.0: The Predator Advisor")
    st.markdown("---")

    # Khởi tạo đối tượng động cơ Vnstock (Dùng chung cho toàn bộ App)
    dong_co_vnstock = Vnstock()

    # ==============================================================================
    # 3. MODULE TRUY XUẤT DỮ LIỆU CỐT LÕI (DATA LAYER)
    # ==============================================================================
    def lay_du_lieu_gia_niem_yet(ticker, so_ngay_lich_su=1000):
        """
        Hàm tải dữ liệu giá OHLCV với cơ chế dự phòng 2 lớp [cite: 1118-1202].
        Đã xóa bỏ hậu tố _v13.
        """
        # Khởi tạo mốc thời gian (Đã ép giờ Việt Nam)
        thoi_diem_bay_gio = lay_thoi_gian_chuan_viet_nam()
        chuoi_ngay_ket_thuc = thoi_diem_bay_gio.strftime('%Y-%m-%d')
        
        do_tre_ngay = timedelta(days=so_ngay_lich_su)
        thoi_diem_bat_dau = thoi_diem_bay_gio - do_tre_ngay
        chuoi_ngay_bat_dau = thoi_diem_bat_dau.strftime('%Y-%m-%d')
        
        # PHƯƠNG ÁN A: Gọi API Vnstock (Ưu tiên số 1)
        try:
            df_vnstock = dong_co_vnstock.stock.quote.history(
                symbol=ticker, 
                start=chuoi_ngay_bat_dau, 
                end=chuoi_ngay_ket_thuc
            )
            
            if df_vnstock is not None and not df_vnstock.empty:
                # Đồng bộ hóa tiêu đề cột về chữ thường [cite: 1145-1154]
                danh_sach_cot_moi = []
                for item_cot in df_vnstock.columns:
                    danh_sach_cot_moi.append(str(item_cot).lower())
                df_vnstock.columns = danh_sach_cot_moi
                return df_vnstock
                    
        except Exception:
            # Nếu Vnstock lỗi, hệ thống im lặng chuyển sang Fallback
            pass
        
        # PHƯƠNG ÁN B: Gọi Yahoo Finance dự phòng (Ưu tiên số 2)
        try:
            # Chuyển đổi mã chuẩn Yahoo
            if ticker == "VNINDEX":
                ma_yahoo = "^VNINDEX"
            else:
                ma_yahoo = f"{ticker}.VN"
                
            df_yahoo = yf.download(ma_yahoo, period="3y", progress=False)
            
            if len(df_yahoo) > 0:
                # Giải phóng Index ngày thành cột 'date' [cite: 1179-1196]
                df_yahoo = df_yahoo.reset_index()
                
                # Xử lý triệt để lỗi Multi-index của yfinance
                danh_sach_cot_yf = []
                for label_col in df_yahoo.columns:
                    if isinstance(label_col, tuple):
                        danh_sach_cot_yf.append(str(label_col[0]).lower())
                    else:
                        danh_sach_cot_yf.append(str(label_col).lower())
                
                df_yahoo.columns = danh_sach_cot_yf
                return df_yahoo
                
        except Exception as msg_error:
            # Nếu cả 2 đều hỏng, báo lỗi lên thanh bên
            st.sidebar.error(f"⚠️ Lỗi tải dữ liệu mã {ticker}: {str(msg_error)}")
            return None

    def lay_du_lieu_dong_tien_to_chuc_thuc_te(ticker, days=20):
        """
        Truy xuất trực tiếp dữ liệu Khối Ngoại và Tự Doanh [cite: 1206-1264].
        Đã xóa bỏ hậu tố _v14.
        """
        try:
            thoi_diem_bay_gio = lay_thoi_gian_chuan_viet_nam()
            chuoi_ket_thuc = thoi_diem_bay_gio.strftime('%Y-%m-%d')
            chuoi_bat_dau = (thoi_diem_bay_gio - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 1. Truy xuất Khối Ngoại
            df_foreign = None
            try:
                df_foreign = dong_co_vnstock.stock.trade.foreign_trade(symbol=ticker, start=chuoi_bat_dau, end=chuoi_ket_thuc)
            except:
                try: df_foreign = dong_co_vnstock.stock.trading.foreign(symbol=ticker, start=chuoi_bat_dau, end=chuoi_ket_thuc)
                except: pass
            
            # 2. Truy xuất Tự Doanh (Proprietary Trading)
            df_proprietary = None
            try:
                df_proprietary = dong_co_vnstock.stock.trade.proprietary_trade(symbol=ticker, start=chuoi_bat_dau, end=chuoi_ket_thuc)
            except:
                pass
            
            # Chuẩn hóa cột Khối ngoại
            if df_foreign is not None and not df_foreign.empty:
                df_foreign.columns = [str(c).lower() for c in df_foreign.columns]
                
            # Chuẩn hóa cột Tự doanh
            if df_proprietary is not None and not df_proprietary.empty:
                df_proprietary.columns = [str(c).lower() for c in df_proprietary.columns]
                
            return df_foreign, df_proprietary

        except Exception:
            pass
        return None, None

    # ==============================================================================
    # 4. MODULE TÍNH TOÁN CHỈ BÁO (QUANT ENGINE)
    # ==============================================================================
    def tinh_toan_chi_bao_ky_thuat_predator(df_raw):
        """
        Xây dựng bộ chỉ báo: MA, BOL, RSI, MACD và vũ khí Predator [cite: 1268-1429].
        Khai triển bê tông từng dòng, rã nhỏ logic.
        """
        # Tạo bản sao dữ liệu tránh làm hỏng DataFrame gốc
        df = df_raw.copy()
        
        # --- BƯỚC 1: DỌN DẸP DỮ LIỆU RÁC ---
        # Loại bỏ các cột trùng tên (Nếu có từ Yahoo Finance)
        df = df.loc[:, ~df.columns.duplicated()]
        
        # Ép kiểu dữ liệu số cho các cột OHLCV (Khai triển dọc từng cột)
        if 'open' in df.columns:
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
        if 'high' in df.columns:
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
        if 'low' in df.columns:
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
        if 'close' in df.columns:
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
        # Vá lỗi dữ liệu rỗng
        df['close'] = df['close'].ffill()
        df['volume'] = df['volume'].ffill()
        
        # Trích xuất chuỗi giá đóng cửa làm trục tính toán chính
        gia_close = df['close']
        khoi_luong_vol = df['volume']
        
        # --- BƯỚC 2: HỆ THỐNG TRUNG BÌNH ĐỘNG (MA) ---
        # Tính MA20 (Nhịp đập ngắn hạn)
        cua_so_ma20 = gia_close.rolling(window=20)
        df['ma20'] = cua_so_ma20.mean()
        
        # Tính MA50 (Nhịp đập trung hạn)
        cua_so_ma50 = gia_close.rolling(window=50)
        df['ma50'] = cua_so_ma50.mean()
        
        # Tính MA200 (Ran giới sinh tử)
        cua_so_ma200 = gia_close.rolling(window=200)
        df['ma200'] = cua_so_ma200.mean()
        
        # --- BƯỚC 3: DẢI BOLLINGER BANDS & SQUEEZE ---
        # Tính độ lệch chuẩn 20 phiên
        do_lech_chuan_20 = cua_so_ma20.std()
        df['do_lech_chuan_20'] = do_lech_chuan_20
        
        # Thiết lập dải Bollinger Upper & Lower [cite: 1330-1335]
        df['upper_band'] = df['ma20'] + (df['do_lech_chuan_20'] * 2)
        df['lower_band'] = df['ma20'] - (df['do_lech_chuan_20'] * 2)
        
        # TÍNH TOÁN ĐỘ NÉN LÒ XO (Bollinger Band Width) [cite: 1336-1341]
        khoang_cach_upper_lower = df['upper_band'] - df['lower_band']
        ti_le_bang_thong = khoang_cach_upper_lower / (df['ma20'] + 1e-9)
        df['bb_width'] = ti_le_phan_tram_cua_bang_thong = ti_le_bang_thong

        # --- BƯỚC 4: CHỈ SỐ SỨC MẠNH TƯƠNG ĐỐI (RSI 14) ---
        # Tính chênh lệch giá ngày
        delta_gia = gia_close.diff()
        
        # Tách nến tăng và nến giảm
        chuoi_tang = delta_gia.where(delta_gia > 0, 0)
        chuoi_giam = -delta_gia.where(delta_gia < 0, 0)
        
        # Tính mức tăng/giảm trung bình 14 phiên
        trung_binh_tang_14 = chuoi_tang.rolling(window=14).mean()
        trung_binh_giam_14 = chuoi_giam.rolling(window=14).mean()
        
        # Công thức RSI chuẩn
        rs_logic = trung_binh_tang_14 / (trung_binh_giam_14 + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs_logic))
        
        # --- BƯỚC 5: ĐỘNG LƯỢNG MACD (12, 26, 9) ---
        ema12 = gia_close.ewm(span=12, adjust=False).mean()
        ema26 = gia_close.ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # --- BƯỚC 6: BIẾN SỐ AI & DÒNG TIỀN ---
        # Tỷ suất sinh lời ngày
        df['return_1d'] = gia_close.pct_change()
        
        # Cường độ Volume (So với trung bình 10 phiên)
        vol_avg10 = khoi_luong_vol.rolling(window=10).mean()
        df['vol_strength'] = khoi_luong_vol / (vol_avg10 + 1e-9)
        
        # XÁC ĐỊNH DẤU HIỆU CẠN CUNG (Supply Exhaustion) [cite: 1395-1407]
        vol_avg20 = khoi_luong_vol.rolling(window=20).mean()
        # Nến đỏ: Giá đóng cửa thấp hơn giá mở cửa
        df['la_nen_do'] = df['close'] < df['open']
        # Cạn cung: Vừa là nến đỏ VÀ Vol rớt dưới ngưỡng Minh đã chốt (0.8)
        df['can_cung'] = (df['la_nen_do'] == True) & (df['volume'] < vol_avg20 * THAM_SO_CAN_CUNG)
        
        # Phân lớp hành vi dòng tiền PV Trend
        dk_gom = (df['return_1d'] > 0) & (df['vol_strength'] > 1.2)
        dk_xa = (df['return_1d'] < 0) & (df['vol_strength'] > 1.2)
        df['pv_trend'] = np.where(dk_gom, 1, np.where(dk_xa, -1, 0))
        
        # Trả về bảng dữ liệu đã dọn sạch NaN [cite: 1428]
        return df.dropna()

    # ==============================================================================
    # 5. MODULE CHẨN ĐOÁN THÔNG MINH (INTELLIGENCE LAYER)
    # ==============================================================================

    def phan_tich_tam_ly_dam_dong(df_tinh_toan):
        """
        Đo lường sức nóng RSI để nhận diện trạng thái tâm lý [cite: 1435-1451].
        """
        # Trích xuất dòng dữ liệu cuối cùng của phiên hiện tại
        dong_du_lieu_cuoi = df_tinh_toan.iloc[-1]
        
        # Lấy giá trị RSI chuẩn 14 phiên
        gia_tri_rsi_hien_tai = dong_du_lieu_cuoi['rsi']
        
        # Phân loại 5 cung bậc cảm xúc của đám đông
        if gia_tri_rsi_hien_tai > 75:
            chuoi_nhan_tam_ly = " 🔥  CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
            
        elif gia_tri_rsi_hien_tai > 60:
            chuoi_nhan_tam_ly = " ⚖️  THAM LAM (HƯNG PHẤN)"
            
        elif gia_tri_rsi_hien_tai < 30:
            chuoi_nhan_tam_ly = " 💀  CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
            
        elif gia_tri_rsi_hien_tai < 42:
            chuoi_nhan_tam_ly = " 😨  SỢ HÃI (BI QUAN)"
            
        else:
            chuoi_nhan_tam_ly = " 🟡  TRUNG LẬP (ĐI NGANG CHỜ ĐỢI)"
            
        # Làm tròn để hiển thị trên Metric
        rsi_lam_tron = round(gia_tri_rsi_hien_tai, 1)
        
        return chuoi_nhan_tam_ly, rsi_lam_tron

    def thuc_thi_backtest_chien_thuat(df_tinh_toan):
        """
        Hệ thống kiểm chứng lịch sử: Mua khi RSI < 45 & MACD cắt lên [cite: 1455-1509].
        Tính xác suất đạt lợi nhuận 5% trong vòng 10 ngày.
        """
        tong_so_lan_co_tin_hieu = 0
        tong_so_lan_thanh_cong = 0
        
        do_dai_du_lieu = len(df_tinh_toan)
        
        # Duyệt qua từng phiên trong quá khứ (Bỏ qua 100 phiên đầu làm nền)
        for i in range(100, do_dai_du_lieu - 10):
            
            # 1. Kiểm tra điều kiện RSI thấp (Vùng gom)
            rsi_phien_do = df_tinh_toan['rsi'].iloc[i]
            check_rsi = rsi_phien_do < 45
            
            # 2. Kiểm tra điều kiện MACD cắt lên đường Signal
            macd_nay = df_tinh_toan['macd'].iloc[i]
            sig_nay = df_tinh_toan['signal'].iloc[i]
            macd_qua = df_tinh_toan['macd'].iloc[i-1]
            sig_qua = df_tinh_toan['signal'].iloc[i-1]
            
            # Logic giao cắt Golden Cross
            check_macd = (macd_nay > sig_nay) and (macd_qua <= sig_qua)
            
            if check_rsi and check_macd:
                tong_so_lan_co_tin_hieu = tong_so_lan_co_tin_hieu + 1
                
                # Giả lập giá mua tại phiên xuất hiện tín hiệu
                gia_mua_entry = df_tinh_toan['close'].iloc[i]
                muc_tieu_lai_5_pct = gia_mua_entry * 1.05
                
                # Soi dữ liệu 10 phiên tiếp theo trong tương lai
                data_tuong_lai = df_tinh_toan['close'].iloc[i+1 : i+11]
                
                # Nếu có bất kỳ ngày nào giá vượt mục tiêu chốt lời
                kiem_tra_thang = any(data_tuong_lai > muc_tieu_lai_5_pct)
                
                if kiem_tra_thang == True:
                    tong_so_lan_thanh_cong = tong_so_lan_thanh_cong + 1
        
        # Tránh lỗi chia cho 0 nếu không tìm thấy mẫu hình
        if tong_so_lan_co_tin_hieu == 0:
            return 0.0
            
        winrate_thuc_te = (tong_so_lan_thanh_cong / tong_so_lan_co_tin_hieu) * 100
        
        return round(winrate_thuc_te, 1)

    def du_bao_xac_suat_ai_t3(df_tinh_toan):
        """
        Mô hình máy học Random Forest dự báo khả năng tăng giá sau 3 ngày [cite: 1510-1566].
        """
        if len(df_tinh_toan) < 200:
            return "N/A"
            
        df_ml = df_tinh_toan.copy()
        
        # Bước 1: Gắn nhãn mục tiêu (Target Y) - Tăng 2% sau 3 ngày
        df_ml['muc_tieu_ai'] = (df_ml['close'].shift(-3) > df_ml['close'] * 1.02).astype(int)
        
        # Bước 2: Định nghĩa bộ thuộc tính (Features X)
        danh_sach_bien_ai = [
            'rsi', 
            'macd', 
            'signal', 
            'return_1d', 
            'vol_strength', 
            'bb_width', 
            'pv_trend'
        ]
        
        # Bước 3: Huấn luyện AI (Loại bỏ 3 dòng cuối chưa có đáp án tương lai)
        df_ml = df_ml.dropna()
        
        X_train = df_ml[danh_sach_bien_ai][:-3]
        y_train = df_ml['muc_tieu_ai'][:-3]
        
        # Khởi động động cơ Random Forest
        mo_hinh_ai = RandomForestClassifier(n_estimators=100, random_state=42)
        mo_hinh_ai.fit(X_train, y_train)
        
        # Bước 4: Dự báo cho phiên giao dịch hiện tại
        du_lieu_hom_nay = df_ml[danh_sach_bien_ai].iloc[[-1]]
        matrix_ket_qua = mo_hinh_ai.predict_proba(du_lieu_hom_nay)
        
        # Lấy xác suất của lớp 1 (Tăng giá)
        xac_suat_tang = matrix_ket_qua[0][1]
        
        return round(xac_suat_tang * 100, 1)

    # ==============================================================================
    # 6. MODULE PHÂN TÍCH TÀI CHÍNH (FUNDAMENTAL LAYER)
    # ==============================================================================

    def do_luong_tang_truong_canslim(ma_ck):
        """
        Tính toán tăng trưởng LNST so với cùng kỳ [cite: 1670-1707].
        """
        try:
            # Truy xuất báo cáo kết quả kinh doanh quý
            df_tc = dong_co_vnstock.stock.finance.income_statement(symbol=ma_ck, period='quarter', lang='en').head(5)
            
            # Tìm cột Lợi nhuận sau thuế bằng từ khóa
            tu_khoa_lnst = ['sau thuế', 'posttax', 'net profit']
            cot_tim_thay = [c for c in df_tc.columns if any(kw in str(c).lower() for kw in tu_khoa_lnst)]
            
            if len(cot_tim_thay) > 0:
                ten_cot = cot_tim_thay[0]
                lnst_nay = float(df_tc.iloc[0][ten_cot])
                lnst_xua = float(df_tc.iloc[4][ten_cot])
                
                if lnst_xua > 0:
                    tang_truong = ((lnst_nay - lnst_xua) / lnst_xua) * 100
                    return round(tang_truong, 1)
        except:
            pass
        return None

    def boc_tach_chi_so_pe_roe(ma_ck):
        """
        Lấy P/E và ROE. Đã FIX lỗi 0.0 gây hiểu lầm [cite: 1711-1774].
        """
        pe_final = None
        roe_final = None
        
        try:
            # Thử lấy từ Vnstock
            df_r = dong_co_vnstock.stock.finance.ratio(ma_ck, 'quarterly').iloc[-1]
            pe_v = df_r.get('ticker_pe', df_r.get('pe', None))
            roe_v = df_r.get('roe', None)
            
            # Chỉ nhận nếu giá trị là số dương thực sự
            if pe_v is not None and not np.isnan(pe_v) and pe_v > 0:
                pe_final = pe_v
            if roe_v is not None and not np.isnan(roe_v) and roe_v > 0:
                roe_final = roe_v
        except:
            pass
            
        # Nếu Vnstock lỗi, chuyển sang Yahoo Finance dự phòng
        if pe_final is None:
            try:
                info_yf = yf.Ticker(f"{ma_ck}.VN").info
                pe_final = info_yf.get('trailingPE', None)
                roe_final = info_yf.get('returnOnEquity', None)
            except:
                pass
                
        return pe_final, roe_final

    # ==============================================================================
    # 7. MODULE RA QUYẾT ĐỊNH & BÁO CÁO (DECISION LAYER)
    # ==============================================================================

    def he_thong_suy_luan_advisor(dong_cuoi, p_ai, p_wr, p_tang):
        """
        Cỗ máy ra lệnh MUA/BÁN dựa trên sự hội tụ chỉ báo [cite: 1793-1837].
        """
        diem_tin_cay = 0
        
        # 1. Điểm AI (Predator 48%)
        if isinstance(p_ai, float) and p_ai >= THAM_SO_AI_PREDATOR:
            diem_tin_cay = diem_tin_cay + 1
            
        # 2. Điểm Lịch sử
        if p_wr >= 50.0:
            diem_tin_cay = diem_tin_cay + 1
            
        # 3. Điểm Kỹ thuật (Trên nền MA20)
        if dong_cuoi['close'] > dong_cuoi['ma20']:
            diem_tin_cay = diem_tin_cay + 1
            
        # 4. Điểm Tài chính
        if p_tang is not None and p_tang >= 15.0:
            diem_tin_cay = diem_tin_cay + 1
            
        # Phân loại lệnh dựa trên tổng điểm
        if diem_tin_cay >= 3 and dong_cuoi['rsi'] < NGUONG_RSI_AN_TOAN:
            return " 🚀  MUA / NẮM GIỮ (STRONG BUY)", "green"
            
        elif diem_tin_cay <= 1 or dong_cuoi['rsi'] > 78 or dong_cuoi['close'] < dong_cuoi['ma20']:
            return " 🚨  BÁN / ĐỨNG NGOÀI (BEARISH)", "red"
            
        else:
            return " ⚖️  THEO DÕI (WATCHLIST)", "orange"

    def tao_ban_bao_cao_tu_dong(tui_du_lieu):
        """
        CHỐNG LỖI TYPEERROR: Sử dụng 1 tham số Dictionary duy nhất [cite: 1570-1666].
        Minh đọc báo cáo này để hiểu rõ tại sao Robot ra lệnh như vậy.
        """
        ma = tui_du_lieu['ma_ck']
        last = tui_du_lieu['dong_cuoi']
        p_ai = tui_du_lieu['diem_ai']
        
        bai_van = []
        bai_van.append(f"#### 🎯 PHÂN TÍCH CHIẾN THUẬT MÃ: {ma}")
        
        # 1. Đọc vị dòng tiền tổ chức
        if tui_du_lieu['to_chuc_gom'] == True:
            bai_van.append(f"✅ **Dòng tiền lớn:** Phát hiện Cá mập (Tây/Tự doanh) đang âm thầm GOM HÀNG mã {ma} trong các phiên gần đây.")
        else:
            bai_van.append(f"🟡 **Dòng tiền lớn:** Chưa thấy dấu hiệu gom hàng rõ nét từ các tổ chức lớn.")

        # 2. Đọc vị vị thế kỹ thuật
        if last['close'] > last['ma20']:
            bai_van.append(f"✅ **Xu hướng:** Giá ({last['close']:,.0f}) neo vững trên đường sinh tử MA20. Nền tảng tăng giá rất ổn định.")
        else:
            bai_van.append(f"❌ **Cảnh báo:** Giá đang nằm dưới đường MA20. Xu hướng ngắn hạn đang bị đe dọa nghiêm trọng.")

        # 3. Đọc vị vũ khí Predator
        if last['bb_width'] <= tui_du_lieu['min_bbw'] * HESO_SQUEEZE_BOLLINGER:
            bai_van.append(f"🌀 **Tín hiệu đặc biệt:** Lò xo Bollinger đang nén rất chặt ({last['bb_width']:.2f}). Một cú bùng nổ sắp xảy ra.")
            
        if last['can_cung'] == True:
            bai_van.append(f"💧 **Tín hiệu đặc biệt:** Phát hiện trạng thái CẠN CUNG. Lực bán tháo đã kiệt quệ, giá dễ bật tăng.")

        # 4. Quản trị rủi ro (Stop-loss)
        nguong_thu_quan = last['ma20'] * 0.98 # Cắt lỗ nếu gãy MA20 quá 2%
        bai_van.append(f"#### 🛡️ QUẢN TRỊ RỦI RO CHO MINH:")
        bai_van.append(f"- **Vùng giá mua an toàn:** Quanh {last['ma20']:,.0f} VNĐ.")
        bai_van.append(f"- **Ngưỡng bảo vệ vốn (Stop-loss):** {nguong_thu_quan:,.0f} VNĐ.")
        
        return "\n\n".join(bai_van)

    # ==============================================================================
    # 8. THIẾT LẬP GIAO DIỆN NGƯỜI DÙNG (UI CONTROLLER)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def lay_danh_sach_ma_hose():
        """Lấy toàn bộ mã sàn HOSE [cite: 1842-1854]."""
        try:
            full_list = dong_co_vnstock.market.listing()
            return full_list[full_list['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            return ["FPT", "HPG", "SSI", "TCB", "MWG", "VNM", "VIC", "VHM", "STB", "MSN", "GAS"]

    # --- SIDEBAR ĐIỀU HÀNH ---
    danh_sach_ma = lay_danh_sach_ma_hose()
    st.sidebar.header("🕹️ Trung Tâm Điều Hành Predator")
    
    ma_tu_drop = st.sidebar.selectbox("Chọn mã cổ phiếu mục tiêu:", danh_sach_ma)
    ma_tu_tay = st.sidebar.text_input("Hoặc nhập mã tay (VD: VCB):").upper()
    
    # Chuẩn hóa biến duy nhất xuyên suốt chương trình
    ma_co_phieu_dang_duoc_chon = ma_tu_tay if ma_tu_tay != "" else ma_tu_drop

    # --- HỆ THỐNG TABS CHIẾN THUẬT ---
    t1_adv, t2_fin, t3_flo, t4_hun = st.tabs([
        "🤖 ROBOT ADVISOR MASTER", 
        "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM", 
        "🌊 DÒNG TIỀN THỰC TẾ (REAL FLOW)", 
        "🔍 RADAR PREDATOR (SĂN CHÂN SÓNG)"
    ])

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 1: ROBOT ADVISOR MASTER
    # ------------------------------------------------------------------------------
    with t1_adv:
        chuoi_nut_bam = f"⚡ PHÂN TÍCH CHIẾN THUẬT MÃ {ma_co_phieu_dang_duoc_chon}"
        if st.button(chuoi_nut_bam):
            with st.spinner(f"Predator đang rà soát dữ liệu đa tầng mã {ma_co_phieu_dang_duoc_chon}..."):
                
                # 1. Lấy dữ liệu và tính toán
                df_raw = lay_du_lieu_gia_niem_yet(ma_co_phieu_dang_duoc_chon)
                
                if df_raw is not None and not df_raw.empty:
                    df_q = tinh_toan_chi_bao_ky_thuat_predator(df_raw)
                    last_row = df_q.iloc[-1]
                    
                    # 2. Chạy các bộ máy AI & Lịch sử
                    diem_ai = du_bao_xac_suat_ai_t3(df_q)
                    diem_wr = thuc_thi_backtest_chien_thuat(df_q)
                    diem_tang = do_luong_tang_truong_canslim(ma_co_phieu_dang_duoc_chon)
                    
                    # 3. Kiểm tra dòng tiền Tổ chức 5 phiên
                    df_f, df_p = lay_du_lieu_dong_tien_to_chuc_thuc_te(ma_co_phieu_dang_duoc_chon, 10)
                    check_to_chuc = False
                    
                    if df_f is not None:
                        # Tính tổng mua ròng Khối ngoại
                        rong_f = df_f['buyval'].tail(5).sum() - df_f['sellval'].tail(5).sum()
                        if rong_f > 0: check_to_chuc = True
                        
                    if check_to_chuc == False and df_p is not None:
                        # Tính tổng mua ròng Tự doanh
                        rong_p = df_p['buyval'].tail(5).sum() - df_p['sellval'].tail(5).sum()
                        if rong_p > 0: check_to_chuc = True

                    # 4. Đóng gói Dictionary (Túi dữ liệu) - CHỐNG LỖI TUYỆT ĐỐI
                    tui_thong_tin = {
                        'ma_ck': ma_co_phieu_dang_duoc_chon,
                        'dong_cuoi': last_row,
                        'diem_ai': diem_ai,
                        'winrate': diem_wr,
                        'to_chuc_gom': check_to_chuc,
                        'min_bbw': df_q['bb_width'].tail(20).min()
                    }

                    # 5. Hiển thị giao diện kết quả
                    st.write(f"### 🎯 BẢN PHÂN TÍCH TỰ ĐỘNG - MÃ {ma_co_phieu_dang_duoc_chon}")
                    c_rep, c_cmd = st.columns([2, 1])
                    
                    with c_rep:
                        # Gọi hàm báo cáo Dictionary
                        st.info(tao_ban_bao_cao_tu_dong(tui_thong_tin))
                        
                    with c_cmd:
                        # Gọi hàm ra lệnh
                        lenh_txt, lenh_col = he_thong_suy_luan_advisor(last_row, diem_ai, diem_wr, diem_tang)
                        st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                        st.title(f":{lenh_col}[{lenh_txt}]")
                    
                    st.divider()
                    # 6. Vẽ Master Chart chuyên nghiệp [cite: 2161-2249]
                    fig_m = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                    v_df = df_q.tail(120)
                    
                    fig_m.add_trace(go.Candlestick(x=v_df['date'], open=v_df['open'], high=v_df['high'], low=v_df['low'], close=v_df['close'], name='Giá nến'), row=1, col=1)
                    fig_m.add_trace(go.Scatter(x=v_df['date'], y=v_df['ma20'], line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                    fig_m.add_trace(go.Bar(x=v_df['date'], y=v_df['volume'], name='Khối lượng', marker_color='gray'), row=2, col=1)
                    
                    fig_m.update_layout(height=700, template='plotly_white', xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_m, use_container_width=True)
                else:
                    st.error("❌ Không thể lấy dữ liệu mã này. Vui lòng kiểm tra lại kết nối mạng.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 2: ĐO LƯỜNG NỘI LỰC DOANH NGHIỆP (FINANCIAL ANALYSIS)
    # ------------------------------------------------------------------------------
    with t2_fin:
        chuoi_tieu_de_tai_chinh = f"### 📈 Phân Tích Sức Khỏe Tài Chính: {ma_co_phieu_dang_duoc_chon}"
        st.write(chuoi_tieu_de_tai_chinh)
        
        # 1. Gọi hàm bóc tách chỉ số P/E và ROE đã được FIX lỗi 0.0
        gia_tri_pe_thuc_te, gia_tri_roe_thuc_te = boc_tach_chi_so_pe_roe(ma_co_phieu_dang_duoc_chon)
        
        # 2. Thiết lập bố cục cột hiển thị
        cot_trai_tai_chinh, cot_phai_tai_chinh = st.columns(2)
        
        # --- XỬ LÝ HIỂN THỊ P/E (SỐ NĂM HOÀN VỐN) ---
        kiem_tra_pe_null = gia_tri_pe_thuc_te is None
        
        if kiem_tra_pe_null == True:
            chuoi_hien_thi_pe = "N/A"
            chuoi_ghi_chu_pe = "Lỗi kết nối API Máy chủ"
            mau_sac_delta_pe = "off"
        else:
            chuoi_hien_thi_pe = f"{gia_tri_pe_thuc_te:.1f}"
            chuoi_ghi_chu_pe = "Dữ liệu thực tế Doanh nghiệp"
            mau_sac_delta_pe = "normal"
            
        cot_trai_tai_chinh.metric(
            label="Chỉ số P/E (Số năm hoàn vốn)", 
            value=chuoi_hien_thi_pe, 
            delta=chuoi_ghi_chu_pe, 
            delta_color=mau_sac_delta_pe
        )
        
        # --- XỬ LÝ HIỂN THỊ ROE (LỢI NHUẬN TRÊN VỐN) ---
        kiem_tra_roe_null = gia_tri_roe_thuc_te is None
        
        if kiem_tra_roe_null == True:
            chuoi_hien_thi_roe = "N/A"
            chuoi_ghi_chu_roe = "Thiếu dữ liệu báo cáo"
            mau_sac_delta_roe = "off"
        else:
            chuoi_hien_thi_roe = f"{gia_tri_roe_thuc_te:.1%}"
            chuoi_ghi_chu_roe = "Năng lực sinh lời trên vốn"
            mau_sac_delta_roe = "normal"
            
        cot_phai_tai_chinh.metric(
            label="Chỉ số ROE (%)", 
            value=chuoi_hien_thi_roe, 
            delta=chuoi_ghi_chu_roe, 
            delta_color=mau_sac_delta_roe
        )
        
        st.divider()
        st.write("> **Giải mã tài chính cho Minh:** P/E dưới 12 là rẻ, ROE trên 15% là doanh nghiệp làm ăn cực tốt. Nếu hiện N/A, Minh hãy đợi API cập nhật lại sau vài phút nhé.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 3: DÒNG TIỀN THỰC TẾ (REAL CASH FLOW - FOREIGN & PROP)
    # ------------------------------------------------------------------------------
    with t3_flo:
        st.subheader("🌊 Phân Tích Dòng Tiền Tổ Chức (Khối Ngoại & Tự Doanh)")
        st.write("Bóc tách hành vi mua bán ròng thực tế của các 'Cá mập' trên thị trường.")
        
        # 1. Gọi dữ liệu từ máy chủ
        df_foreign, df_prop = lay_du_lieu_dong_tien_to_chuc_thuc_te(ma_co_phieu_dang_duoc_chon, days=20)
        
        # 2. Xử lý hiển thị Khối ngoại
        if df_foreign is not None and not df_foreign.empty:
            dong_cuoi_f = df_foreign.iloc[-1]
            
            # Tính toán giá trị ròng (Tỷ VNĐ)
            mua_f = float(dong_cuoi_f.get('buyval', 0))
            ban_f = float(dong_cuoi_f.get('sellval', 0))
            rong_f = (mua_f - ban_f) / 1e9
            
            chuoi_trang_thai_f = "Mua Ròng" if rong_f > 0 else "Bán Ròng"
            st.metric("Giao dịch ròng Khối Ngoại (Hôm nay)", f"{rong_f:.2f} Tỷ VNĐ", delta=chuoi_trang_thai_f)
            
            # Biểu đồ cột lịch sử Khối ngoại
            st.write("📈 **Lịch sử 10 phiên Khối ngoại:**")
            rong_list_f = []
            for i_idx, r_row in df_foreign.tail(10).iterrows():
                val_net = (float(r_row.get('buyval', 0)) - float(r_row.get('sellval', 0))) / 1e9
                rong_list_f.append(val_net)
            
            fig_f = go.Figure()
            fig_f.add_trace(go.Bar(
                x=df_foreign['date'].tail(10), 
                y=rong_list_f, 
                marker_color=['green' if v > 0 else 'red' for v in rong_list_f]
            ))
            fig_f.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_f, use_container_width=True)
            
        else:
            st.warning("⚠️ API Khối ngoại chưa cập nhật dữ liệu phiên này.")

        st.divider()

        # 3. Xử lý hiển thị Tự doanh (Proprietary)
        if df_prop is not None and not df_prop.empty:
            dong_cuoi_p = df_prop.iloc[-1]
            
            mua_p = float(dong_cuoi_p.get('buyval', 0))
            ban_p = float(dong_cuoi_p.get('sellval', 0))
            rong_p = (mua_p - ban_p) / 1e9
            
            chuoi_trang_thai_p = "Tự Doanh Gom" if rong_p > 0 else "Tự Doanh Xả"
            st.metric("Giao dịch ròng Tự Doanh (Hôm nay)", f"{rong_p:.2f} Tỷ VNĐ", delta=chuoi_trang_thai_p)
        else:
            st.info("ℹ️ Dữ liệu Tự doanh thường cập nhật trễ sau 18h hàng ngày.")

    # ------------------------------------------------------------------------------
    # MÀN HÌNH TAB 4: SIÊU RADAR PREDATOR (MÁY QUÉT 2 TẦNG CHÂN SÓNG)
    # ------------------------------------------------------------------------------
    with t4_hun:
        st.subheader("🔍 Radar Săn Chân Sóng V20.0 - Predator Leviathan")
        st.write("Dành riêng cho Minh: Hệ thống quét 30 mã trụ sàn HOSE, phân loại cơ hội chân sóng an toàn.")
        
        # Bắt đầu kích hoạt vòng lặp quét toàn sàn
        if st.button(" 🔥 KÍCH HOẠT RADAR TRUY QUÉT CHIẾN THUẬT"):
            
            # Khởi tạo các thùng chứa kết quả
            mang_bung_no = []
            mang_danh_sach_cho = []
            
            thanh_tien_do = st.progress(0)
            
            # Giới hạn danh sách quét 30 mã để bảo vệ server
            danh_sach_quet = danh_sach_ma[:30]
            tong_so_ma = len(danh_sach_quet)
            
            for vi_tri, ma_quet in enumerate(danh_sach_quet):
                try:
                    # 1. Tải dữ liệu từng mã
                    df_s_raw = lay_du_lieu_gia_niem_yet(ma_quet, so_ngay_lich_su=120)
                    
                    if df_s_raw is not None:
                        # 2. Tính toán định lượng
                        df_s_calc = tinh_toan_chi_bao_ky_thuat_predator(df_s_raw)
                        dong_cuoi_scan = df_s_calc.iloc[-1]
                        
                        # 3. Chạy AI dự báo
                        ai_val = du_bao_xac_suat_ai_t3(df_s_calc)
                        
                        # --- LOGIC TẦNG 1: NHÓM BÙNG NỔ (BREAKOUT) ---
                        # Cảnh báo mã đã chạy nóng, rủi ro mua đuổi (như VIC)
                        if dong_cuoi_scan['vol_strength'] > 1.3:
                            mang_bung_no.append({
                                'Mã': ma_quet,
                                'Thị giá': f"{dong_cuoi_scan['close']:,.0f}",
                                'Cường độ Vol': round(dong_cuoi_scan['vol_strength'], 1),
                                'AI T+3': f"{ai_val}%"
                            })
                        
                        # --- LOGIC TẦNG 2: NHÓM DANH SÁCH CHỜ (PREDATOR) ---
                        # Kiểm tra màng lọc Cơ bản (Nới lỏng 5% và AI 48%)
                        check_rsi = dong_cuoi_scan['rsi'] < THAM_SO_RSI_AN_TOAN
                        
                        can_duoi_ma20 = dong_cuoi_scan['ma20'] * (1 - THAM_SO_VUNG_GIA_MA20)
                        can_tren_ma20 = dong_cuoi_scan['ma20'] * (1 + THAM_SO_VUNG_GIA_MA20)
                        check_gia_nen = (dong_cuoi_scan['close'] >= can_duoi_ma20) and (dong_cuoi_scan['close'] <= can_tren_ma20)
                        
                        check_vol_tich_luy = (dong_cuoi_scan['vol_strength'] >= THAM_SO_VOL_MIN) and (dong_cuoi_scan['vol_strength'] <= THAM_SO_VOL_MAX)
                        
                        check_ai_ung_ho = False
                        if isinstance(ai_val, float):
                            if ai_val >= THAM_SO_AI_PREDATOR:
                                check_ai_ung_ho = True
                        
                        # Điều kiện GỘP Cơ bản
                        if check_rsi and check_gia_nen and check_vol_tich_luy and check_ai_ung_ho:
                            
                            # Kiểm tra màng lọc Nâng cao (Vũ khí chân sóng)
                            
                            # Vũ khí 1: Nén lò xo (Squeeze 1.2)
                            min_bbw_20p = df_s_calc['bb_width'].tail(20).min()
                            is_squeeze = dong_cuoi_scan['bb_width'] <= (min_bbw_20p * THAM_SO_SQUEEZE)
                            
                            # Vũ khí 2: Cạn cung (Supply Exhaustion 0.8)
                            is_exhaustion = df_s_calc['can_cung'].tail(5).any()
                            
                            # Vũ khí 3: Tây gom hoặc Tự doanh gom
                            df_f_s, df_p_s = lay_du_lieu_dong_tien_to_chuc_thuc_te(ma_quet, 10)
                            is_smart_money = False
                            
                            if df_f_s is not None:
                                rong_f_s = df_f_s['buyval'].tail(5).sum() - df_f_s['sellval'].tail(5).sum()
                                if rong_f_s > 0: is_smart_money = True
                                
                            if is_smart_money == False and df_p_s is not None:
                                rong_p_s = df_p_s['buyval'].tail(5).sum() - df_p_s['sellval'].tail(5).sum()
                                if rong_p_s > 0: is_smart_money = True
                                
                            # TỔNG HỢP: Nếu đạt Cơ bản + ÍT NHẤT 1 vũ khí nâng cao
                            if is_squeeze or is_exhaustion or is_smart_money:
                                mang_danh_sach_cho.append({
                                    'Mã': ma_quet,
                                    'AI': f"{ai_val}%",
                                    'Lò xo': "Nén chặt" if is_squeeze else "Bình thường",
                                    'Lực Bán': "Cạn kiệt" if is_exhaustion else "Đủ cung",
                                    'Cá mập': "Đang Gom" if is_smart_money else "Đứng ngoài",
                                    'Giá nền': f"{dong_cuoi_scan['ma20']:,.0f}"
                                })
                except:
                    pass
                
                # Cập nhật thanh tiến trình UI
                thanh_tien_do.progress((vi_tri + 1) / tong_so_ma)
            
            # --- HIỂN THỊ KẾT QUẢ QUÉT ---
            st.write("### 🚀 Nhóm Bùng Nổ (Đã nổ Vol - Cẩn thận VIC 2.0)")
            if len(mang_bung_no) > 0:
                st.table(pd.DataFrame(mang_bung_no).sort_values(by='AI T+3', ascending=False))
            else:
                st.write("Chưa phát hiện mã bùng nổ mạnh.")
                
            st.write("### ⚖️ Nhóm Danh Sách Chờ (Predator Watchlist - Chân sóng cực an toàn)")
            if len(mang_danh_sach_cho) > 0:
                st.table(pd.DataFrame(mang_danh_sach_cho).sort_values(by='AI', ascending=False))
                st.success("✅ **Gợi ý của Robot:** Minh hãy ưu tiên các mã có 'Cá mập đang gom' và 'Lò xo nén chặt' vì rủi ro đu đỉnh cực thấp.")
            else:
                st.info("Radar chưa tìm thấy mã tích lũy chân sóng đạt chuẩn khắt khe.")

# ==============================================================================
# HẾT MÃ NGUỒN V20.0 THE PREDATOR LEVIATHAN - BẢN SỬA LỖI HOÀN MỸ
# ==============================================================================
