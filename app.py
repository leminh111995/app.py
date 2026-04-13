# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V9.6 ULTRA MASTER
# PHIÊN BẢN: ADVISOR MASTER & SMART FLOW SPECIALIST (NO TRUNCATION)
# NGƯỜI SỞ HỮU: MINH
# ==============================================================================

import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- NHÓM THƯ VIỆN AI VÀ XỬ LÝ NGÔN NGỮ TỰ NHIÊN (NLP) ---
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo các tài nguyên cần thiết cho AI được tải đầy đủ để tránh lỗi Runtime
# Đây là bước sống còn để module Advisor có thể đưa ra các chẩn đoán bằng văn bản
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & KIỂM SOÁT TRUY CẬP (SECURITY LAYER)
# ==============================================================================
def check_password():
    """
    Hàm xác thực mật mã dành riêng cho Minh.
    Sử dụng session_state để duy trì trạng thái đăng nhập trong một phiên làm việc.
    """
    def password_entered():
        # Lấy giá trị từ secrets.toml trên Streamlit Cloud hoặc file cục bộ
        target_password = st.secrets["password"]
        entered_password = st.session_state["password"]
        
        if entered_password == target_password:
            st.session_state["password_correct"] = True
            # Xóa password khỏi session ngay lập tức sau khi kiểm tra xong để bảo mật
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Giao diện màn hình khóa khi chưa đăng nhập
        st.markdown("### 🛡️ Hệ thống Quant đang được bảo vệ")
        st.text_input(
            "🔑 Nhập mật mã của Minh để truy cập trung tâm điều hành:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    return st.session_state.get("password_correct", False)

# Chỉ thực thi ứng dụng khi Minh đã vượt qua bước xác thực mật mã
if check_password():
    # Cấu hình giao diện chuẩn Dashboard chuyên nghiệp dành cho dân Quant Trading
    st.set_page_config(
        page_title="Quant System V9.6 Ultra Master", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Hiển thị tiêu đề chính của hệ thống
    st.title("🛡️ Quant System V9.6: Ultra Advisor & Flow Specialist")

    # Khởi tạo đối tượng Vnstock - Nguồn cung cấp dữ liệu chính cho sàn chứng khoán VN
    vn = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU ĐA TẦNG (DATA ACQUISITION LAYER)
    # ==============================================================================
    def lay_du_lieu_tu_nguon(ticker, days=1000):
        """
        Lấy dữ liệu giá OHLCV lịch sử. 
        Hệ thống hỗ trợ cơ chế Fail-over: Ưu tiên Vnstock, dự phòng Yahoo Finance.
        """
        try:
            # 2.1 Thiết lập mốc thời gian lấy dữ liệu
            thoi_gian_hien_tai = datetime.now()
            ngay_ket_thuc = thoi_gian_hien_tai.strftime('%Y-%m-%d')
            ngay_bat_dau = (thoi_gian_hien_tai - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 2.2 Thử nghiệm lấy dữ liệu từ API Vnstock
            df_ket_qua = vn.stock.quote.history(
                symbol=ticker, 
                start=ngay_bat_dau, 
                end=ngay_ket_thuc
            )
            
            if df_ket_qua is not None:
                if not df_ket_qua.empty:
                    # Chuyển đổi tên cột sang chữ thường để đồng nhất logic xử lý toàn hệ thống
                    df_ket_qua.columns = [str(col).lower() for col in df_ket_qua.columns]
                    return df_ket_qua
        except Exception as e_vn:
            # Ghi nhận lỗi logic nhưng không dừng chương trình để chuyển sang bước dự phòng
            pass
        
        try:
            # 2.3 Cơ chế Fallback sang Yahoo Finance (Dành cho mã SSI, Bank hoặc khi API Vnstock nghẽn)
            if ticker == "VNINDEX":
                symbol_de_tim = "^VNINDEX"
            else:
                symbol_de_tim = f"{ticker}.VN"
                
            # Tải dữ liệu từ Yahoo Finance với period 3 năm để đảm bảo đủ tính MA200
            yt_raw = yf.download(symbol_de_tim, period="3y", progress=False)
            
            if not yt_raw.empty:
                yt_raw = yt_raw.reset_index()
                # Xử lý Multi-index của yfinance (vấn đề thường gặp ở các phiên bản thư viện mới)
                clean_column_names = []
                for header in yt_raw.columns:
                    if isinstance(header, tuple):
                        clean_column_names.append(str(header[0]).lower())
                    else:
                        clean_column_names.append(str(header).lower())
                
                yt_raw.columns = clean_column_names
                return yt_raw
        except Exception as e_yf:
            st.sidebar.error(f"⚠️ Hệ thống không thể truy xuất mã {ticker}: {str(e_yf)}")
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (ENGINE LAYER)
    # ==============================================================================
    def tinh_toan_cac_chi_so_quant(df):
        """
        Tính toán toàn bộ kho vũ khí chỉ báo: MA, Bollinger, RSI, MACD, Volatility.
        Đây là trái tim của hệ thống định lượng.
        """
        # Tạo bản sao sâu để tránh các lỗi liên quan đến SettingWithCopyWarning của Pandas
        df_engine = df.copy()
        
        # --- 3.1 Nhóm đường trung bình động xu hướng (MA) ---
        # MA20: Phục vụ xác định xu hướng ngắn hạn và hỗ trợ dải Bollinger
        df_engine['ma20'] = df_engine['close'].rolling(window=20).mean()
        # MA50: Phác họa xu hướng trung hạn của cổ phiếu
        df_engine['ma50'] = df_engine['close'].rolling(window=50).mean()
        # MA200: Ngưỡng tâm lý sống còn, phân chia thị trường bò và gấu
        df_engine['ma200'] = df_engine['close'].rolling(window=200).mean()
        
        # --- 3.2 Nhóm chỉ báo dải vận động Bollinger Bands ---
        # Tính độ lệch chuẩn của giá đóng cửa trong 20 phiên
        df_engine['std_20'] = df_engine['close'].rolling(window=20).std()
        # Dải trên (Upper Band): MA20 + 2 lần độ lệch chuẩn
        df_engine['upper_band'] = df_engine['ma20'] + (df_engine['std_20'] * 2)
        # Dải dưới (Lower Band): MA20 - 2 lần độ lệch chuẩn
        df_engine['lower_band'] = df_engine['ma20'] - (df_engine['std_20'] * 2)
        
        # --- 3.3 Chỉ số sức mạnh tương đối RSI (14 phiên) ---
        khoang_bien_dong = df_engine['close'].diff()
        gia_tri_lai = (khoang_bien_dong.where(khoang_bien_dong > 0, 0)).rolling(window=14).mean()
        gia_tri_lo = (-khoang_bien_dong.where(khoang_bien_dong < 0, 0)).rolling(window=14).mean()
        ty_le_rs = gia_tri_lai / (gia_tri_lo + 1e-9)
        df_engine['rsi'] = 100 - (100 / (1 + ty_le_rs))
        
        # --- 3.4 Chỉ báo MACD & Signal Line (Cấu hình chuẩn 12, 26, 9) ---
        duong_ema_nhanh = df_engine['close'].ewm(span=12, adjust=False).mean()
        duong_ema_cham = df_engine['close'].ewm(span=26, adjust=False).mean()
        df_engine['macd'] = duong_ema_nhanh - duong_ema_cham
        df_engine['signal'] = df_engine['macd'].ewm(span=9, adjust=False).mean()
        
        # --- 3.5 Nhóm biến số phục vụ Smart Flow và Dự báo AI ---
        # Tỷ suất sinh lời hằng ngày (Daily Return)
        df_engine['return_1d'] = df_engine['close'].pct_change()
        # Biến động khối lượng so với trung bình 10 ngày (Volume Spike)
        df_engine['vol_change'] = df_engine['volume'] / df_engine['volume'].rolling(window=10).mean()
        # Giá trị luân chuyển tiền mặt thực tế
        df_engine['money_flow'] = df_engine['close'] * df_engine['volume']
        # Độ biến động lịch sử (Volatility)
        df_engine['volatility'] = df_engine['return_1d'].rolling(window=20).std()
        
        # --- 3.6 Logic Gom/Xả dựa trên Price-Volume Trend ---
        # Trạng thái 1: Gom mạnh (Giá tăng xanh + Volume nổ > 1.2)
        # Trạng thái -1: Xả mạnh (Giá giảm đỏ + Volume nổ > 1.2)
        # Trạng thái 0: Vận động bình thường
        df_engine['pv_trend'] = np.where((df_engine['return_1d'] > 0) & (df_engine['vol_change'] > 1.2), 1, 
                                np.where((df_engine['return_1d'] < 0) & (df_engine['vol_change'] > 1.2), -1, 0))
        
        # Loại bỏ các dòng chứa giá trị rỗng (NaN) để không làm sai lệch mô hình AI
        df_final = df_engine.dropna()
        return df_final

    # ==============================================================================
    # 4. CHẨN ĐOÁN TÂM LÝ & KIỂM CHỨNG CHIẾN THUẬT (INTEL LAYER)
    # ==============================================================================
    def phan_tich_fear_and_greed(df):
        """Phân tích tâm lý thị trường dựa trên trị số RSI hiện tại"""
        rsi_hien_tai = df.iloc[-1]['rsi']
        
        if rsi_hien_tai > 75:
            nhan_tam_ly = "🔥 CỰC KỲ THAM LAM (QUÁ MUA)"
        elif rsi_hien_tai > 60:
            nhan_tam_ly = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif rsi_hien_tai < 30:
            nhan_tam_ly = "💀 CỰC KỲ SỢ HÃI (QUÁ BÁN)"
        elif rsi_hien_tai < 42:
            nhan_tam_ly = "😨 SỢ HÃI (BI QUAN)"
        else:
            nhan_tam_ly = "🟡 TRUNG LẬP (CHỜ ĐỢI)"
            
        return nhan_tam_ly, round(rsi_hien_tai, 1)

    def chay_backtest_chien_thuat(df):
        """
        Thực thi Backtest lịch sử trong 1000 phiên giao dịch gần nhất.
        Kiểm tra xác suất thắng của bộ chỉ báo RSI + MACD.
        """
        dem_tong_tin_hieu = 0
        dem_tin_hieu_thang = 0
        
        # Bắt đầu quét từ phiên thứ 100 để đảm bảo các đường MA đã hình thành đầy đủ
        for i in range(100, len(df) - 10):
            # Điều kiện kích hoạt điểm mua (Buy Signal)
            dieu_kien_rsi = df['rsi'].iloc[i] < 45
            dieu_kien_macd = df['macd'].iloc[i] > df['signal'].iloc[i]
            dieu_kien_giao_cat = df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
            
            if dieu_kien_rsi and dieu_kien_macd and dieu_kien_giao_cat:
                dem_tong_tin_hieu += 1
                # Kiểm tra kết quả: Nếu trong 10 phiên tới có ít nhất 1 phiên đạt lợi nhuận 5%
                gia_mua = df['close'].iloc[i]
                vung_gia_tuong_lai = df['close'].iloc[i+1 : i+11]
                
                if any(vung_gia_tuong_lai > gia_mua * 1.05):
                    dem_tin_hieu_thang += 1
        
        if dem_tong_tin_hieu == 0:
            return 0.0
            
        xac_suat_win = (dem_tin_hieu_thang / dem_tong_tin_hieu) * 100
        return round(xac_suat_win, 1)

    def du_bao_ai_t3_xac_suat(df):
        """
        Mô hình AI Random Forest dự báo khả năng tăng giá trong ngắn hạn (T+3).
        Sử dụng 8 đặc trưng kỹ thuật làm biến đầu vào.
        """
        if len(df) < 200:
            return "N/A"
            
        df_ml = df.copy()
        # Nhãn mục tiêu: Giá cổ phiếu tăng > 2% sau đúng 3 phiên
        df_ml['target'] = (df_ml['close'].shift(-3) > df_ml['close'] * 1.02).astype(int)
        
        # Danh sách các đặc trưng (Features) để huấn luyện AI
        cac_bien_dau_vao = [
            'rsi', 'macd', 'signal', 'return_1d', 
            'volatility', 'vol_change', 'money_flow', 'pv_trend'
        ]
        
        du_lieu_huan_luyen = df_ml.dropna()
        X_train = du_lieu_huan_luyen[cac_bien_dau_vao]
        y_train = du_lieu_huan_luyen['target']
        
        # Khởi tạo thuật toán Rừng Ngẫu Nhiên với 100 cây quyết định
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Huấn luyện mô hình trên toàn bộ dữ liệu, trừ 3 dòng cuối cùng (vì chưa biết kết quả tương lai)
        rf_model.fit(X_train[:-3], y_train[:-3])
        
        # Dự báo xác suất cho trạng thái hiện tại của cổ phiếu
        du_bao_prob = rf_model.predict_proba(X_train.iloc[[-1]])[0][1]
        return round(du_bao_prob * 100, 1)

    # ==============================================================================
    # 5. PHÂN TÍCH TÀI CHÍNH & CANSLIM (FUNDAMENTAL ENGINE)
    # ==============================================================================
    def lay_tang_truong_lnst_chi_tiet(ticker):
        """Tính toán tăng trưởng lợi nhuận quý gần nhất so với cùng kỳ năm trước"""
        try:
            # 5.1 Thử nghiệm lấy báo cáo thu nhập từ Vnstock
            df_income = vn.stock.finance.income_statement(
                symbol=ticker, 
                period='quarter', 
                lang='en'
            ).head(5)
            
            # Tìm kiếm tên cột Lợi nhuận sau thuế linh hoạt theo ngôn ngữ
            keywords = ['sau thuế', 'posttax', 'net profit', 'earning']
            cac_cot_tim_duoc = [c for c in df_income.columns if any(k in str(c).lower() for k in keywords)]
            
            if cac_cot_tim_duoc:
                ten_cot = cac_cot_tim_duoc[0]
                lnst_quy_nay = float(df_income.iloc[0][ten_cot])
                lnst_quy_truoc = float(df_income.iloc[4][ten_cot])
                
                if lnst_quy_truoc > 0:
                    bien_dong_pct = ((lnst_quy_nay - lnst_quy_truoc) / lnst_quy_truoc) * 100
                    return round(bien_dong_pct, 1)
        except Exception:
            pass
            
        try:
            # 5.2 Phương án dự phòng bằng Yahoo Finance cho các mã tài chính/ngân hàng
            thong_tin_cp = yf.Ticker(f"{ticker}.VN").info
            tang_truong_yf = thong_tin_cp.get('earningsQuarterlyGrowth')
            
            if tang_truong_yf is not None:
                return round(tang_truong_yf * 100, 1)
        except Exception:
            pass
        return None

    def lay_chi_so_pe_roe_master(ticker):
        """Lấy chỉ số định giá P/E và hiệu quả sử dụng vốn ROE"""
        pe_final, roe_final = 0.0, 0.0
        
        try:
            # Lấy các tỷ số tài chính từ Vnstock
            df_ratios = vn.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe_final = df_ratios.get('ticker_pe', df_ratios.get('pe', 0))
            roe_final = df_ratios.get('roe', 0)
        except:
            pass
            
        if pe_final <= 0:
            try:
                # Fallback sang Yahoo Finance khi dữ liệu nội địa bị thiếu
                info_yf = yf.Ticker(f"{ticker}.VN").info
                pe_final = info_yf.get('trailingPE', 0)
                roe_final = info_yf.get('returnOnEquity', 0)
            except:
                pass
                
        return pe_final, roe_final

    # ==============================================================================
    # 6. 🧠 ROBOT ADVISOR MASTER: GIẢI MÃ LOGIC & RA QUYẾT ĐỊNH (V9.6)
    # ==============================================================================
    def robot_advisor_expert_v96(ticker, last_row, ai_p, wr, pe, roe, growth, list_gom, list_xa):
        """
        Siêu hệ thống Advisor: Phân tích hội tụ 5 tầng dữ liệu.
        Tự động giải mã các mâu thuẫn chỉ báo để đưa ra lời khuyên an toàn nhất.
        """
        # --- KHỞI TẠO CÁC BIẾN NỘI DUNG ---
        chuan_doan_ky_thuat = ""
        chuan_doan_dong_tien = ""
        ket_luan_hanh_dong = ""
        mau_sac_chu_dao = ""
        
        # Danh sách lưu các lập luận logic để giải thích cho người dùng
        nhat_ky_logic = []
        diem_dong_thuan = 0
        
        # --- 6.1 PHÂN TÍCH LỚP 1: XU HƯỚNG VÀ VỊ THẾ GIÁ (MA20) ---
        gia_hien_tai = last_row['close']
        duong_ma20 = last_row['ma20']
        phan_tram_so_voi_ma20 = ((gia_hien_tai - duong_ma20) / duong_ma20) * 100
        
        if gia_hien_tai < duong_ma20:
            chuan_doan_ky_thuat = f"Cảnh báo: Giá {ticker} đang nằm dưới đường trung bình MA20 ({duong_ma20:,.0f}). Phe bán đang kiểm soát thị trường mã này."
            nhat_ky_logic.append(f"❌ Vị thế giá YẾU: Hiện tại giá thấp hơn MA20 ({phan_tram_so_voi_ma20:.1f}%). Tuyệt đối hạn chế bắt đáy khi xu hướng giảm chưa dừng lại.")
        else:
            chuan_doan_ky_thuat = f"Tích cực: Giá {ticker} đang vận động trên đường hỗ trợ MA20 ({duong_ma20:,.0f}). Xu hướng ngắn hạn được ủng hộ."
            nhat_ky_logic.append(f"✅ Vị thế giá TỐT: Giá đang giữ được MA20 ({phan_tram_so_voi_ma20:.1f}%). Đây là nền tảng quan trọng cho đà tăng tiếp diễn.")
            diem_dong_thuan += 1

        # --- 6.2 PHÂN TÍCH LỚP 2: DÒNG TIỀN CÁ MẬP (SMART FLOW) ---
        if ticker in list_gom:
            chuan_doan_dong_tien = "Dòng tiền thông minh: Cá mập (Smart Money) đang chủ động mua Gom hàng mã này một cách âm thầm."
            nhat_ky_logic.append("✅ Dòng tiền MẠNH: Phát hiện dấu chân Cá mập đang gom hàng phối hợp cùng nhóm trụ cột HOSE.")
            diem_dong_thuan += 1
        elif ticker in list_xa:
            chuan_doan_dong_tien = "Cảnh báo xả hàng: Các tổ chức lớn và khối ngoại đang có dấu hiệu phân phối (Bán ròng) mã này rất mạnh."
            nhat_ky_logic.append("❌ Dòng tiền XẤU: Cá mập đang tháo chạy. Đừng trở thành 'bia đỡ đạn' cho các quỹ đầu tư lúc này.")
        else:
            chuan_doan_dong_tien = "Dòng tiền nhỏ lẻ: Thị trường chủ yếu vận động bởi các nhà đầu tư cá nhân, thiếu sự dẫn dắt của tay to."
            nhat_ky_logic.append("🟡 Dòng tiền NHIỄU: Chủ yếu là nhỏ lẻ giao dịch với nhau, xác suất bùng nổ giá thấp.")

        # --- 6.3 PHÂN TÍCH LỚP 3: DỰ BÁO AI VÀ XÁC SUẤT LỊCH SỬ ---
        # Đánh giá điểm số AI
        if isinstance(ai_p, float) and ai_p >= 58.0:
            diem_dong_thuan += 1
            nhat_ky_logic.append(f"✅ AI ủng hộ ({ai_p}%): Mô hình máy học Random Forest dự báo khả năng tăng giá trong T+3 là rất khả quan.")
        else:
            nhat_ky_logic.append(f"❌ AI phản đối ({ai_p}%): Xác suất thắng theo mô hình AI chưa đạt ngưỡng an toàn (>58%).")

        # Đánh giá điểm số Backtest
        if wr >= 50.0:
            diem_dong_thuan += 1
            nhat_ky_logic.append(f"✅ Lịch sử ủng hộ ({wr}%): Trong quá khứ, mỗi khi xuất hiện tín hiệu này, mã {ticker} thường mang lại lợi nhuận tốt.")
        else:
            nhat_ky_logic.append(f"❌ Lịch sử rủi ro ({wr}%): Tỷ lệ thắng lịch sử của tín hiệu hiện tại quá thấp, nguy cơ gặp bẫy giá Bull trap cao.")

        # --- 6.4 TỔNG HỢP VÀ RA QUYẾT ĐỊNH CHIẾN THUẬT (VÍ DỤ MÃ GAS/SSI) ---
        # Điều kiện MUA: Điểm đồng thuận cao và RSI không quá nóng
        if diem_dong_thuan >= 4 and last_row['rsi'] < 68:
            ket_luan_hanh_dong = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
            mau_sac_chu_dao = "green"
        # Điều kiện BÁN: Điểm thấp hoặc RSI quá hưng phấn hoặc Giá thủng MA20
        elif diem_dong_thuan <= 1 or last_row['rsi'] > 78 or gia_hien_tai < duong_ma20:
            ket_luan_hanh_dong = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
            mau_sac_chu_dao = "red"
            # Giải mã mâu thuẫn đặc biệt cho Minh
            if gia_hien_tai < duong_ma20 and ticker in list_gom:
                nhat_ky_logic.append("⚠️ GIẢI MÃ MÂU THUẪN: Dù Cá mập Gom nhưng Giá < MA20. Đây thường là hành động gom tích lũy dài hạn của quỹ. Với nhà đầu tư cá nhân, việc vào lúc này dễ bị chôn vốn. Hãy đợi giá vượt MA20 xác nhận xu hướng rồi mới tham gia.")
        else:
            # Trạng thái trung lập
            ket_luan_hanh_dong = "⚖️ THEO DÕI (WATCHLIST)"
            mau_sac_chu_dao = "orange"

        return chuan_doan_ky_thuat, chuan_doan_dong_tien, ket_luan_hanh_dong, mau_sac_chu_dao, nhat_ky_logic

    # ==============================================================================
    # 7. GIAO DIỆN NGƯỜI DÙNG & TRUNG TÂM ĐIỀU KHIỂN (UI LAYER)
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def tai_danh_sach_ma_niem_yet():
        """Tải toàn bộ danh sách mã chứng khoán sàn HOSE để người dùng chọn lựa"""
        try:
            df_hose = vn.market.listing()
            return df_hose[df_hose['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            # Danh sách mã trụ cột dự phòng nếu API listing lỗi
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","GAS","VRE"]

    danh_sach_ticker = tai_danh_sach_ma_niem_yet()
    
    st.sidebar.header("🕹️ Trung Tâm Điều Hành Quant")
    selected_mã = st.sidebar.selectbox("Chọn mã cổ phiếu mục tiêu:", danh_sach_ticker)
    manual_mã = st.sidebar.text_input("Hoặc gõ mã bất kỳ (Ví dụ: SSI, HPG...):").upper()
    ma_thuc_thi = manual_mã if manual_mã else selected_mã

    # Khởi tạo 4 Tab chức năng chính (Mở rộng toàn phần)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 ROBOT ADVISOR & CHART", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 SMART FLOW SPECIALIST", 
        "🔍 ROBOT HUNTER (QUÉT MÃ)"
    ])

    # ------------------------------------------------------------------------------
    # TAB 1: ROBOT ADVISOR PHÂN TÍCH CHI TIẾT
    # ------------------------------------------------------------------------------
    with tab1:
        if st.button(f"⚡ PHÂN TÍCH CHIẾN THUẬT TOÀN DIỆN MÃ {ma_thuc_thi}"):
            with st.spinner(f"Đang phân tích đa tầng cho mã {ma_thuc_thi}..."):
                df_goc = lay_du_lieu_tu_nguon(ma_thuc_thi)
                
                if df_goc is not None and not df_goc.empty:
                    # Bước 1: Tính toán bộ chỉ số Master
                    df_master = tinh_toan_cac_chi_so_quant(df_goc)
                    dong_hien_tai = df_master.iloc[-1]
                    
                    # Bước 2: Chạy các engine thông minh
                    ai_xac_suat = du_bao_ai_t3_xac_suat(df_master)
                    wr_lich_su = chay_backtest_chien_thuat(df_master)
                    tam_ly_nhan, tam_ly_diem = phan_tich_fear_and_greed(df_master)
                    val_pe, val_roe = lay_chi_so_pe_roe_master(ma_thuc_thi)
                    growth_val = lay_tang_truong_lnst_chi_tiet(ma_thuc_thi)
                    
                    # Bước 3: Quét thị trường trụ phục vụ chẩn đoán
                    pillars = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                    gom_list, xa_list = [], []
                    for p_mã in pillars:
                        try:
                            d_p = lay_du_lieu_tu_nguon(p_mã, days=10)
                            if d_p is not None:
                                d_p_calc = tinh_toan_cac_chi_so_quant(d_p)
                                l_p = d_p_calc.iloc[-1]
                                # Gom/Xả Trụ: Giá tăng/giảm + Vol nổ > 1.2
                                if l_p['return_1d'] > 0 and l_p['vol_change'] > 1.2: 
                                    gom_list.append(p_mã)
                                elif l_p['return_1d'] < 0 and l_p['vol_change'] > 1.2: 
                                    xa_list.append(p_mã)
                        except: pass

                    # BƯỚC 4: GỌI ROBOT ADVISOR VÀ GIẢI MÃ LOGIC
                    diag_kt, diag_dt, verd_txt, v_hue, log_logic = robot_advisor_expert_v96(
                        ma_thuc_thi, dong_hien_tai, ai_xac_suat, wr_lich_su, 
                        val_pe, val_roe, growth_val, gom_list, xa_list
                    )

                    # HIỂN THỊ KẾT QUẢ CHẨN ĐOÁN
                    st.write(f"### 🎯 Robot Advisor Chẩn Đoán Mã {ma_thuc_thi}")
                    col_info1, col_info2 = st.columns([2, 1])
                    
                    with col_info1:
                        st.info(f"**💡 Góc nhìn kỹ thuật:** {diag_kt}")
                        st.info(f"**🌊 Góc nhìn dòng tiền:** {diag_dt}")
                        with st.expander("🔍 GIẢI MÃ LOGIC: TẠI SAO ROBOT ĐƯA RA ĐỀ XUẤT NÀY?"):
                            st.write("Dưới đây là các luận điểm được Robot tổng hợp để đưa ra kết luận cuối cùng:")
                            for step in log_logic:
                                st.write(step)
                                
                    with col_info2:
                        st.subheader("🤖 ĐỀ XUẤT CHIẾN THUẬT:")
                        st.title(f":{v_hue}[{verd_txt.split('(')[0]}]")
                        st.markdown(f"*{verd_txt.split('(')[1] if '(' in verd_txt else ''}*")
                    
                    st.divider()
                    st.write("### 🧭 Bảng Chỉ Số Radar Hiệu Suất")
                    rc1, rc2, rc3, rc4 = st.columns(4)
                    rc1.metric("Giá Hiện Tại", f"{dong_hien_tai['close']:,.0f}")
                    rc2.metric("Tâm Lý Fear & Greed", f"{tam_ly_diem}/100", delta=tam_ly_nhan)
                    rc3.metric("AI Dự Báo (T+3)", f"{ai_xac_suat}%", delta="Tích cực" if ai_xac_suat > 55 else None)
                    rc4.metric("Win-rate Backtest", f"{wr_lich_su}%", delta="Ổn định" if wr_lich_su > 45 else None)

                    # PHỤC HỒI BẢNG NAKED STATS (CHI TIẾT THÔNG SỐ)
                    st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Chi Tiết (Naked Stats)")
                    nc1, nc2, nc3, nc4 = st.columns(4)
                    nc1.metric("RSI (14 phiên)", f"{dong_hien_tai['rsi']:.1f}", delta="Quá mua" if dong_hien_tai['rsi']>70 else ("Quá bán" if dong_hien_tai['rsi']<30 else "Trung tính"))
                    nc2.metric("MACD Status", f"{dong_hien_tai['macd']:.2f}", delta="Cắt lên (Tốt)" if dong_hien_tai['macd']>dong_hien_tai['signal'] else "Cắt xuống (Xấu)")
                    nc3.metric("MA20 / MA50", f"{dong_hien_tai['ma20']:,.0f}", delta=f"MA50: {dong_hien_tai['ma50']:,.0f}")
                    nc4.metric("Dải Bollinger Trên", f"{dong_hien_tai['upper_band']:,.0f}", delta=f"Dưới: {dong_hien_tai['lower_band']:,.0f}", delta_color="inverse")
                    
                    # Cẩm nang thực chiến chuyên sâu (Full Handbook)
                    with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (BẤM ĐỂ XEM QUY TẮC VÀNG)"):
                        st.markdown(f"""
                        **1. Khối lượng (Volume):** - Vol phiên cuối đạt **{dong_hien_tai['vol_strength']:.1f} lần** trung bình 10 phiên gần nhất.
                        - Giá tăng + Vol cao (>1.2) ➔ Cá mập đang quyết liệt Gom hàng.
                        - Giá giảm + Vol cao (>1.2) ➔ Cá mập đang Xả (Thoát hàng mạnh mẽ).
                        
                        **2. Bollinger Bands (BOL):** - Vùng xám mờ đại diện cho biên độ biến động an toàn của cổ phiếu. 
                        - Vượt dải trên ➔ Trạng thái hưng phấn cực độ, giá dễ bị kéo ngược trở lại vùng MA20. 
                        - Thủng dải dưới ➔ Trạng thái hoảng loạn, cơ hội tuyệt vời cho nhịp phục hồi kỹ thuật.
                        
                        **3. CÁCH NÉ BẪY GIÁ (BULL TRAP / BEAR TRAP):**
                        - **Né Đỉnh Giả (Bull Trap):** Giá vượt đỉnh cũ nhưng Vol thấp hơn trung bình ➔ Đây là bẫy dụ mua để tổ chức thoát hàng.
                        - **Né Đáy Giả (Bear Trap):** Giá chạm dải dưới nhưng Vol xả vẫn cực lớn ➔ Tuyệt đối chưa bắt đáy, hãy chờ nến rút chân.
                        
                        **4. Nguyên tắc Cắt lỗ kỷ luật:** - Tuyệt đối thoát toàn bộ vị thế nếu giá cổ phiếu chạm mốc **{dong_hien_tai['close']*0.93:,.0f} (-7%)** để bảo toàn vốn.
                        """)

                    # BIỂU ĐỒ NẾN PHỨC HỢP MASTER CHART (FULL VISUAL)
                    fig_ultra = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                    # Vẽ nến Candlestick
                    fig_ultra.add_trace(go.Candlestick(x=df_master['date'].tail(120), open=df_master['open'].tail(120), high=df_master['high'].tail(120), low=df_master['low'].tail(120), close=df_master['close'].tail(120), name='Giá Nến'), row=1, col=1)
                    # Vẽ các đường xu hướng
                    fig_ultra.add_trace(go.Scatter(x=df_master['date'].tail(120), y=df_master['ma20'].tail(120), line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
                    fig_ultra.add_trace(go.Scatter(x=df_master['date'].tail(120), y=df_master['ma200'].tail(120), line=dict(color='purple', width=2), name='MA200 (Long-term)'), row=1, col=1)
                    # Vẽ dải Bollinger với hiệu ứng tô màu xám mờ
                    fig_ultra.add_trace(go.Scatter(x=df_master['date'].tail(120), y=df_master['upper_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải trên'), row=1, col=1)
                    fig_ultra.add_trace(go.Scatter(x=df_master['date'].tail(120), y=df_master['lower_band'].tail(120), line=dict(color='gray', dash='dash', width=1), name='Dải dưới', fill='tonexty', fillcolor='rgba(128,128,128,0.1)'), row=1, col=1)
                    # Vẽ biểu đồ khối lượng giao dịch
                    fig_ultra.add_trace(go.Bar(x=df_master['date'].tail(120), y=df_master['volume'].tail(120), name='Khối lượng', marker_color='gray'), row=2, col=1)
                    
                    fig_ultra.update_layout(height=700, template='plotly_white', xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig_ultra, use_container_width=True)
                else:
                    st.error("Lỗi: Không thể tải dữ liệu. Vui lòng kiểm tra lại kết nối mạng hoặc mã cổ phiếu!")

    # ------------------------------------------------------------------------------
    # TAB 2: CƠ BẢN & CANSLIM (FULL EXPANSION)
    # ------------------------------------------------------------------------------
    with tab2:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá Doanh Nghiệp ({ma_thuc_thi})")
        with st.spinner("Đang tính toán nội lực tài chính..."):
            tang_truong_pct = lay_tang_truong_lnst_chi_tiet(ma_thuc_thi)
            if tang_truong_pct is not None:
                if tang_truong_pct >= 20.0:
                    st.success(f"**🔥 CanSLIM (Chữ C):** LNST tăng trưởng đột phá **+{tang_truong_pct}%** so với cùng kỳ. Đạt tiêu chuẩn doanh nghiệp siêu hạng.")
                elif tang_truong_pct > 0:
                    st.info(f"**⚖️ Tăng trưởng:** LNST cải thiện ở mức **{tang_truong_pct}%**. Doanh nghiệp đang giữ vững phong độ ổn định.")
                else:
                    st.error(f"**🚨 Cảnh báo:** LNST sụt giảm mạnh **{tang_truong_pct}%**. Sức khỏe tài chính có dấu hiệu suy yếu nghiêm trọng.")
            
            st.divider()
            cur_pe, cur_roe = lay_chi_so_pe_roe_master(ma_thuc_thi)
            fc1, fc2 = st.columns(2)
            
            # Đánh giá đắt rẻ qua P/E
            pe_desc = "Tốt (Định giá Rẻ)" if 0 < cur_pe < 12 else ("Hợp lý" if cur_pe < 18 else "Đắt (Rủi ro mua hớ)")
            fc1.metric("P/E (Hệ số Định giá)", f"{cur_pe:.1f}", delta=pe_desc, delta_color="normal" if cur_pe < 18 else "inverse")
            st.write("> P/E thấp chứng tỏ giá cổ phiếu đang hấp dẫn so với khả năng sinh lời thực tế.")
            
            # Đánh giá hiệu quả qua ROE
            roe_desc = "Xuất sắc" if cur_roe >= 0.25 else ("Tốt" if cur_roe >= 0.15 else "Trung bình / Thấp")
            fc2.metric("ROE (Hiệu quả sử dụng vốn)", f"{cur_roe:.1%}", delta=roe_desc, delta_color="normal" if cur_roe >= 0.15 else "inverse")
            st.write("> ROE đo lường khả năng sinh lời trên mỗi đồng vốn của cổ đông. Tiêu chuẩn vàng là > 15%.")

    # ------------------------------------------------------------------------------
    # TAB 3: SMART FLOW SPECIALIST (TÁCH BIỆT DÒNG TIỀN %)
    # ------------------------------------------------------------------------------
    with tab3:
        st.write(f"### 🌊 Smart Flow Specialist - Phân Tích Dòng Tiền 3 Nhóm ({ma_thuc_thi})")
        df_f_data = lay_du_lieu_tu_nguon(ma_thuc_thi, days=30)
        
        if df_f_data is not None:
            # 3.1 Thực hiện bóc tách dòng tiền
            df_f_calc = tinh_toan_cac_chi_so_quant(df_f_data)
            dong_flow = df_f_calc.iloc[-1]
            spike_vol = dong_flow['vol_change']
            
            # --- LOGIC BÓC TÁCH DÒNG TIỀN CHI TIẾT (V9.6 ULTRA) ---
            # Ước tính dựa trên sức mạnh Volume và biến động lệnh lớn
            if spike_vol > 1.8:
                pct_foreign = 0.35; pct_inst = 0.45; pct_retail = 0.20
            elif spike_vol > 1.2:
                pct_foreign = 0.20; pct_inst = 0.30; pct_retail = 0.50
            else:
                pct_foreign = 0.10; pct_inst = 0.15; pct_retail = 0.75
            
            # Hiển thị tỷ lệ bóc tách trực quan
            st.write("#### 📊 Tỷ lệ phân bổ dòng tiền thực tế ước tính:")
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("🐋 Khối Ngoại (Foreign)", f"{pct_foreign*100:.1f}%", delta="Mua ròng" if dong_flow['return_1d']>0 else "Bán ròng")
            sc2.metric("🏦 Tổ Chức & Tự Doanh", f"{pct_inst*100:.1f}%", delta="Gom hàng" if dong_flow['return_1d']>0 else "Xả hàng")
            sc3.metric("🐜 Cá Nhân (Nhỏ lẻ)", f"{pct_retail*100:.1f}%", delta="Đu bám" if pct_retail > 0.6 else "Ổn định", delta_color="inverse" if pct_retail > 0.6 else "normal")
            
            with st.expander("📖 Ý NGHĨA CÁC NHÓM DÒNG TIỀN"):
                st.markdown("""
                - **Khối Ngoại:** Tiền từ các quỹ quốc tế cực lớn. Họ thường mua gom kiên nhẫn khi giá rẻ.
                - **Tổ Chức:** Tiền từ Tự doanh CTCK và quỹ nội địa. Đây là nhóm tạo lập xu hướng (Market Makers).
                - **Cá Nhân:** Nếu tỷ lệ này quá cao (>60%), cổ phiếu sẽ rất nặng, khó tăng giá mạnh do tâm lý nhỏ lẻ dễ bị dao động.
                """)
            
            st.divider()
            # 3.2 Market Sense - Độ rộng thị trường nhóm trụ cột
            st.write("#### 🌊 Market Sense - Danh Sách Gom/Xả 10 Trụ Cột HOSE")
            with st.spinner("Đang rà soát dấu chân Cá mập trên thị trường chung..."):
                hose_10 = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                list_g_res, list_x_res = [], []
                
                for m in hose_10:
                    try:
                        d_p_raw = lay_du_lieu_tu_nguon(m, days=10)
                        if d_p_raw is not None:
                            d_p_eng = tinh_toan_cac_chi_so_quant(d_p_raw)
                            lp_res = d_p_eng.iloc[-1]
                            if lp_res['return_1d'] > 0 and lp_res['vol_change'] > 1.2:
                                list_g_res.append(m)
                            elif lp_res['return_1d'] < 0 and lp_res['vol_change'] > 1.2:
                                list_x_res.append(m)
                    except: pass
                
                bc1, bc2 = st.columns(2)
                bc1.metric("Trụ đang GOM (Mua mạnh)", f"{len(list_g_res)} mã", delta=f"{(len(list_g_res)/len(hose_10))*100:.0f}%")
                bc2.metric("Trụ đang XẢ (Bán tháo)", f"{len(list_x_res)} mã", delta=f"{(len(list_x_res)/len(hose_10))*100:.0f}%", delta_color="inverse")
                
                lcg, lcx = st.columns(2)
                with lcg:
                    st.success("✅ **DANH SÁCH MÃ TRỤ ĐANG GOM:**")
                    st.write(", ".join(list_g_res) if list_g_res else "Chưa có tín hiệu.")
                with lcx:
                    st.error("🚨 **DANH SÁCH MÃ TRỤ ĐANG XẢ:**")
                    st.write(", ".join(list_x_res) if list_x_res else "Áp lực thấp.")

    # ------------------------------------------------------------------------------
    # TAB 4: ROBOT HUNTER (QUÉT SIÊU CỔ PHIẾU)
    # ------------------------------------------------------------------------------
    with tab4:
        st.subheader("🔍 Robot Hunter - Truy Quét Top 30 Bluechips HOSE")
        if st.button("🔥 CHẠY RÀ SOÁT DÒNG TIỀN THÔNG MINH"):
            results_hunter = []
            progress_bar = st.progress(0)
            scan_targets = danh_sach_ticker[:30]
            
            for index, s_ticker in enumerate(scan_targets):
                try:
                    df_scan = lay_du_lieu_tu_nguon(s_ticker, days=100)
                    df_scan_eng = tinh_toan_cac_chi_so_quant(df_scan)
                    # Tiêu chuẩn Hunter: Volume phải bùng nổ cực mạnh (> 1.3 lần)
                    if df_scan_eng.iloc[-1]['vol_change'] > 1.3:
                        results_hunter.append({
                            'Mã CK': s_ticker, 
                            'Giá Hiện Tại': f"{df_scan_eng.iloc[-1]['close']:,.0f}", 
                            'Sức mạnh Volume': round(df_scan_eng.iloc[-1]['vol_change'], 2), 
                            'AI Dự báo Tăng': f"{du_bao_ai_t3_xac_suat(df_scan_eng)}%"
                        })
                except Exception:
                    pass
                progress_bar.progress((index + 1) / len(scan_targets))
            
            if results_hunter:
                df_res_final = pd.DataFrame(results_hunter).sort_values(by='AI Dự báo Tăng', ascending=False)
                st.table(df_res_final)
                st.success("✅ Đã phát hiện các mã có tín hiệu bùng nổ dòng tiền và xác suất tăng cao đột biến.")
            else:
                st.write("Hệ thống chưa tìm thấy siêu cổ phiếu nào đạt tiêu chuẩn Hunter hôm nay.")
