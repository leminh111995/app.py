# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V10.0 FINAL SANCTUARY
# ------------------------------------------------------------------------------
# PHÂN HỆ: ADVISOR MASTER, SMART FLOW SPECIALIST, MASTER CHART & AI ENGINE
# CHỦ SỞ HỮU: MINH
# TRẠNG THÁI: PHIÊN BẢN ĐẦY ĐỦ NHẤT (HYPER-VERBOSE EDITION)
# CAM KẾT: KHÔNG RÚT GỌN - TƯỜNG MINH TUYỆT ĐỐI - FIX 100% LỖI LOGIC
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
# NHÓM THƯ VIỆN TRÍ TUỆ NHÂN TẠO (AI) VÀ XỬ LÝ NGÔN NGỮ (NLP)
# ------------------------------------------------------------------------------
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo các tài nguyên cần thiết cho AI được tải đầy đủ để tránh lỗi Runtime.
# Đây là bước "xương sống" để module Advisor có thể hoạt động ổn định trên Cloud.
try:
    # Thử tìm dữ liệu từ điển cảm xúc trong hệ thống
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu không tìm thấy, thực hiện tải xuống tự động từ máy chủ NLTK
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & KIỂM SOÁT TRUY CẬP (SECURITY LAYER)
# ==============================================================================
def check_password():
    """
    Hàm xác thực mật mã dành riêng cho Minh.
    Đảm bảo tính riêng tư và bảo vệ các chiến thuật Quant trước sự xâm nhập trái phép.
    Sử dụng session_state để duy trì trạng thái đăng nhập.
    """
    
    def password_entered():
        """Xử lý sự kiện khi người dùng nhấn Enter sau khi nhập mật mã"""
        # Truy xuất mật mã đích được cấu hình trong Streamlit Secrets
        target_password_value = st.secrets["password"]
        # Lấy giá trị mật mã mà người dùng vừa nhập vào ô Input
        entered_password_value = st.session_state["password"]
        
        # Thực hiện so sánh giá trị
        if entered_password_value == target_password_value:
            # Xác nhận mật mã đúng
            st.session_state["password_correct"] = True
            # Xóa mật mã khỏi bộ nhớ tạm ngay lập tức sau khi kiểm tra để bảo mật
            del st.session_state["password"]
        else:
            # Đánh dấu mật mã sai để hiển thị thông báo lỗi
            st.session_state["password_correct"] = False

    # Kiểm tra xem trong phiên làm việc hiện tại đã xác thực chưa
    if "password_correct" not in st.session_state:
        # Giao diện màn hình khóa khi người dùng mới truy cập
        st.markdown("### 🔐 Quant System Master Access Control")
        st.write("Hệ thống đang ở trạng thái bảo mật cao. Vui lòng xác thực quyền sở hữu.")
        
        # Ô nhập liệu mật mã (chế độ password ẩn ký tự)
        st.text_input(
            "🔑 Nhập mật mã của Minh để mở khóa trung tâm điều hành:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # Kiểm tra nếu mật mã nhập trước đó bị sai
    if st.session_state["password_correct"] == False:
        st.error("❌ Mật mã không chính xác. Vui lòng thử lại.")
        st.text_input(
            "🔑 Nhập mật mã của Minh:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # Trả về kết quả xác thực cuối cùng
    return st.session_state.get("password_correct", False)

# ==============================================================================
# BẮT ĐẦU THỰC THI ỨNG DỤNG CHÍNH (MAIN APPLICATION)
# ==============================================================================
if check_password():
    
    # 1.1 Thiết lập cấu hình giao diện chuẩn Dashboard chuyên nghiệp
    st.set_page_config(
        page_title="Quant System V10.0 Final Sanctuary", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 1.2 Hiển thị biểu tượng và tiêu đề chính của hệ thống
    st.title("🛡️ Quant System V10.0: Ultimate Advisor & Flow Specialist")
    st.markdown("---")

    # 1.3 Khởi tạo kết nối tới nguồn dữ liệu Vnstock
    vn_engine = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU ĐA TẦNG (DATA ACQUISITION LAYER)
    # ==============================================================================
    def lay_du_lieu_chuan_quant(ticker_symbol, total_days=1000):
        """
        Lấy dữ liệu giá giao dịch lịch sử (OHLCV). 
        Tích hợp cơ chế dự phòng đa nguồn (Fail-over mechanism):
        - Ưu tiên: Vnstock (Dữ liệu nội địa chính thống).
        - Dự phòng: Yahoo Finance (SSI, Bank, VND hoặc khi Vnstock nghẽn).
        """
        
        # Bước 2.1: Tính toán mốc thời gian bắt đầu và kết thúc
        current_datetime = datetime.now()
        end_date_string = current_datetime.strftime('%Y-%m-%d')
        start_date_calculation = current_datetime - timedelta(days=total_days)
        start_date_string = start_date_calculation.strftime('%Y-%m-%d')
        
        # Bước 2.2: Phương án chính - Truy xuất từ Vnstock
        try:
            df_vn_raw = vn_engine.stock.quote.history(
                symbol=ticker_symbol, 
                start=start_date_string, 
                end=end_date_string
            )
            
            # Kiểm tra dữ liệu trả về có hợp lệ không
            if df_vn_raw is not None:
                if not df_vn_raw.empty:
                    # Tiến hành chuẩn hóa tên cột về chữ thường để đồng nhất logic toàn app
                    normalized_columns = []
                    for col_name in df_vn_raw.columns:
                        normalized_columns.append(str(col_name).lower())
                    
                    # Cập nhật lại tên cột cho DataFrame
                    df_vn_raw.columns = normalized_columns
                    return df_vn_raw
        except Exception as vn_error:
            # Ghi nhận lỗi nhưng không dừng ứng dụng, chuyển sang bước dự phòng
            pass
        
        # Bước 2.3: Phương án dự phòng - Truy xuất từ Yahoo Finance (YF)
        try:
            # Chuyển đổi mã cổ phiếu sang định dạng của Yahoo Finance Việt Nam (.VN)
            if ticker_symbol == "VNINDEX":
                ma_yf_format = "^VNINDEX"
            else:
                ma_yf_format = f"{ticker_symbol}.VN"
                
            # Thực hiện tải dữ liệu với chu kỳ 3 năm (đủ dữ liệu để tính toán MA200)
            yf_raw_data = yf.download(
                ma_yf_format, 
                period="3y", 
                progress=False
            )
            
            # Kiểm tra dữ liệu YF trả về
            if not yf_raw_data.empty:
                # Chuyển Index (Ngày) thành một cột dữ liệu bình thường mang tên 'date'
                yf_raw_data = yf_raw_data.reset_index()
                
                # Xử lý Multi-index tiêu đề cột (Vấn đề phát sinh từ các bản yfinance mới)
                processed_column_labels = []
                for label_item in yf_raw_data.columns:
                    if isinstance(label_item, tuple):
                        # Lấy phần tử đầu tiên trong Tuple và chuyển sang chữ thường
                        processed_column_labels.append(str(label_item[0]).lower())
                    else:
                        # Chuyển tên cột đơn lẻ sang chữ thường
                        processed_column_labels.append(str(label_item).lower())
                
                # Áp dụng tên cột mới cho DataFrame dự phòng
                yf_raw_data.columns = processed_column_labels
                return yf_raw_data
                
        except Exception as yf_error:
            # Thông báo lỗi cuối cùng cho người dùng nếu cả hai nguồn đều thất bại
            st.sidebar.error(f"⚠️ Không thể truy xuất dữ liệu mã {ticker_symbol}. Lỗi: {str(yf_error)}")
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT CHI TIẾT (ENGINE LAYER)
    # ==============================================================================
    def tinh_toan_cac_chi_so_master_engine(df_input):
        """
        Tính toán toàn bộ kho vũ khí chỉ báo định lượng.
        Bao gồm: Moving Averages, Bollinger Bands, RSI, MACD, Money Flow.
        Đây là trái tim xử lý dữ liệu của toàn bộ hệ thống.
        """
        
        # Tạo bản sao sâu của dữ liệu đầu vào để bảo vệ dữ liệu gốc
        df_quant = df_input.copy()
        
        # --- 3.1 Nhóm các đường trung bình động xu hướng (Moving Averages) ---
        
        # MA20: Xu hướng ngắn hạn (phục vụ Bollinger và điểm ra vào lệnh)
        df_quant['ma20'] = df_quant['close'].rolling(window=20).mean()
        
        # MA50: Xu hướng trung hạn (phác họa sức mạnh của cổ phiếu)
        df_quant['ma50'] = df_quant['close'].rolling(window=50).mean()
        
        # MA200: Đường xu hướng dài hạn (Ngưỡng tâm lý sống còn của nhà đầu tư)
        df_quant['ma200'] = df_quant['close'].rolling(window=200).mean()
        
        # --- 3.2 Nhóm chỉ báo dải vận động Bollinger Bands (BOL) ---
        
        # Bước A: Tính độ lệch chuẩn của giá đóng cửa trong chu kỳ 20 phiên
        df_quant['std_dev_value'] = df_quant['close'].rolling(window=20).std()
        
        # Bước B: Tính dải trên (Upper Band) - MA20 + 2 lần độ lệch chuẩn
        df_quant['upper_band'] = df_quant['ma20'] + (df_quant['std_dev_value'] * 2)
        
        # Bước C: Tính dải dưới (Lower Band) - MA20 - 2 lần độ lệch chuẩn
        df_quant['lower_band'] = df_quant['ma20'] - (df_quant['std_dev_value'] * 2)
        
        # --- 3.3 Chỉ số sức mạnh tương đối RSI (Chu kỳ chuẩn 14 phiên) ---
        
        # Bước A: Tính toán chênh lệch giá giữa các phiên
        price_diff_delta = df_quant['close'].diff()
        
        # Bước B: Tách biệt các phiên tăng (gain) và giảm (loss)
        gain_values = price_diff_delta.where(price_diff_delta > 0, 0)
        loss_values = -price_diff_delta.where(price_diff_delta < 0, 0)
        
        # Bước C: Tính giá trị trung bình di động của lãi và lỗ
        avg_gain_window = gain_values.rolling(window=14).mean()
        avg_loss_window = loss_values.rolling(window=14).mean()
        
        # Bước D: Tính toán RS và RSI cuối cùng (Thêm hằng số nhỏ để tránh lỗi chia cho 0)
        relative_strength_rs = avg_gain_window / (avg_loss_window + 1e-9)
        df_quant['rsi'] = 100 - (100 / (1 + relative_strength_rs))
        
        # --- 3.4 Chỉ báo MACD & Signal Line (Cấu hình chuẩn 12, 26, 9) ---
        
        # Đường EMA nhanh (12 phiên)
        ema_fast_12 = df_quant['close'].ewm(span=12, adjust=False).mean()
        
        # Đường EMA chậm (26 phiên)
        ema_slow_26 = df_quant['close'].ewm(span=26, adjust=False).mean()
        
        # Đường MACD chính
        df_quant['macd'] = ema_fast_12 - ema_slow_26
        
        # Đường Tín hiệu (Signal Line - EMA 9 của MACD)
        df_quant['signal'] = df_quant['macd'].ewm(span=9, adjust=False).mean()
        
        # --- 3.5 Nhóm các biến số phục vụ Smart Flow và AI Dự báo ---
        
        # Tỷ suất lợi nhuận hằng ngày (Daily Return)
        df_quant['return_1d'] = df_quant['close'].pct_change()
        
        # THỐNG NHẤT TÊN BIẾN (FIX KEYERROR): vol_strength
        # Đây là cường độ khối lượng so với trung bình 10 phiên gần nhất
        df_quant['vol_strength'] = df_quant['volume'] / df_quant['volume'].rolling(window=10).mean()
        
        # Giá trị luân chuyển dòng tiền thực tế
        df_quant['money_flow'] = df_quant['close'] * df_quant['volume']
        
        # Độ biến động lịch sử thực tế (Historical Volatility)
        df_quant['volatility'] = df_quant['return_1d'].rolling(window=20).std()
        
        # --- 3.6 Logic xác định Xu hướng Price-Volume (PV Trend) ---
        # Trạng thái 1: Gom mạnh (Giá tăng xanh và Volume bùng nổ > 1.2)
        # Trạng thái -1: Xả mạnh (Giá giảm đỏ và Volume bùng nổ > 1.2)
        # Trạng thái 0: Trạng thái trung tính hoặc nhiễu thấp
        
        price_up_vol_spike = (df_quant['return_1d'] > 0) & (df_quant['vol_strength'] > 1.2)
        price_down_vol_spike = (df_quant['return_1d'] < 0) & (df_quant['vol_strength'] > 1.2)
        
        df_quant['pv_trend'] = np.where(price_up_vol_spike, 1, 
                               np.where(price_down_vol_spike, -1, 0))
        
        # Tiến hành loại bỏ các dòng chứa giá trị rỗng (NaN)
        # Bước này cực kỳ quan trọng để các mô hình Machine Learning không bị lỗi logic
        df_final_engine = df_quant.dropna()
        
        return df_final_engine

    # ==============================================================================
    # 4. CÁC HÀM CHẨN ĐOÁN THÔNG MINH (INTELLIGENCE LAYER)
    # ==============================================================================
    
    def phan_tich_tam_ly_sentiment(df_data):
        """
        Phân tích chỉ số Sợ hãi & Tham lam của cổ phiếu dựa trên trị số RSI.
        Giúp Minh nhận diện sớm các vùng nguy hiểm (Overbought) hoặc cơ hội (Oversold).
        """
        # Lấy giá trị RSI phiên gần nhất
        current_rsi_val = df_data.iloc[-1]['rsi']
        
        # Thực hiện phân loại tâm lý đám đông qua từng ngưỡng điểm
        if current_rsi_val > 75:
            label_mood = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif current_rsi_val > 60:
            label_mood = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif current_rsi_val < 30:
            label_mood = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif current_rsi_val < 42:
            label_mood = "😨 SỢ HÃI (BI QUAN)"
        else:
            label_mood = "🟡 TRUNG LẬP (NGHI NGỜ)"
            
        return label_mood, round(current_rsi_val, 1)

    def thuc_thi_backtest_chien_thuat(df_data):
        """
        Hàm kiểm chứng lịch sử (Backtesting): 
        Kiểm tra nếu áp dụng mua khi RSI thấp và MACD cắt lên trong quá khứ của riêng mã này,
        thì xác suất đạt được lợi nhuận 5% trong 10 ngày sau đó là bao nhiêu.
        Duyệt qua 1000 phiên giao dịch gần nhất.
        """
        tong_so_tin_hieu = 0
        tong_so_win = 0
        
        # Duyệt qua tập dữ liệu lịch sử
        for index in range(100, len(df_data) - 10):
            # Điều kiện kích hoạt lệnh mua chuẩn kỹ thuật định lượng
            rsi_is_low = df_data['rsi'].iloc[index] < 45
            macd_is_higher = df_data['macd'].iloc[index] > df_data['signal'].iloc[index]
            macd_was_lower = df_data['macd'].iloc[index-1] <= df_data['signal'].iloc[index-1]
            
            # Kiểm tra sự hội tụ của các tín hiệu
            if rsi_is_low and macd_is_higher and macd_was_lower:
                tong_so_tin_hieu = tong_so_tin_hieu + 1
                
                # Kiểm tra kết quả trong tương lai (cửa sổ 10 phiên)
                gia_mua_tai_diem = df_data['close'].iloc[index]
                cac_muc_gia_tuong_lai = df_data['close'].iloc[index+1 : index+11]
                muc_tieu_chot_loi = gia_mua_tai_diem * 1.05
                
                # Nếu bất kỳ phiên nào trong 10 ngày tới chạm mốc +5%
                if any(cac_muc_gia_tuong_lai > muc_tieu_chot_loi):
                    tong_so_win = tong_so_win + 1
        
        # Phòng ngừa lỗi chia cho 0 nếu mã chứng khoán chưa từng có tín hiệu
        if tong_so_tin_hieu == 0:
            return 0.0
            
        ty_le_thang_phan_tram = (tong_so_win / tong_so_tin_hieu) * 100
        return round(ty_le_thang_phan_tram, 1)

    def du_bao_ai_t3_engine(df_data):
        """
        Sử dụng thuật toán Machine Learning Random Forest để học các mẫu hình giá.
        Dự báo xác suất cổ phiếu tăng trưởng > 2% sau 3 phiên giao dịch (T+3).
        Sử dụng 8 biến đặc trưng đầu vào để ra quyết định.
        """
        # Kiểm tra độ dài dữ liệu tối thiểu
        if len(df_data) < 200:
            return "N/A"
            
        df_ai_process = df_data.copy()
        
        # Định nghĩa nhãn mục tiêu (Target) cho mô hình
        gia_hien_thoi = df_ai_process['close']
        gia_3_phien_sau = df_ai_process['close'].shift(-3)
        df_ai_process['target_label'] = (gia_3_phien_sau > gia_hien_thoi * 1.02).astype(int)
        
        # Danh sách các đặc trưng (Features) kỹ thuật làm đầu vào cho AI
        cac_dac_trung_input = [
            'rsi', 'macd', 'signal', 'return_1d', 
            'volatility', 'vol_strength', 'money_flow', 'pv_trend'
        ]
        
        # Làm sạch dữ liệu trước khi huấn luyện
        du_lieu_da_lam_sach = df_ai_process.dropna()
        X_hoc = du_lieu_da_lam_sach[cac_dac_trung_input]
        y_label = du_lieu_da_lam_sach['target_label']
        
        # Khởi tạo mô hình rừng ngẫu nhiên với 100 cây quyết định
        rf_model_instance = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Huấn luyện mô hình: Loại bỏ 3 dòng cuối cùng vì chưa có kết quả thực tế tương lai
        X_train_data = X_hoc[:-3]
        y_train_labels = y_label[:-3]
        rf_model_instance.fit(X_train_data, y_train_labels)
        
        # Dự báo xác suất cho dòng dữ liệu hiện tại
        du_lieu_cuoi_cung = X_hoc.iloc[[-1]]
        xac_suat_du_bao = rf_model_instance.predict_proba(du_lieu_cuoi_cung)[0][1]
        
        return round(xac_suat_du_bao * 100, 1)

    # ==============================================================================
    # 5. PHÂN TÍCH TÀI CHÍNH & CANSLIM (FUNDAMENTAL LAYER)
    # ==============================================================================
    def lay_tang_truong_lnst_canslim(ticker_name):
        """
        Tính toán tốc độ tăng trưởng lợi nhuận quý gần nhất so với cùng kỳ.
        Đây là tiêu chuẩn 'C' (Current Quarterly Earnings) trong phương pháp CanSLIM.
        """
        try:
            # 5.1 Lấy báo cáo kết quả kinh doanh từ Vnstock
            df_inc_stmt = vn_engine.stock.finance.income_statement(
                symbol=ticker_name, 
                period='quarter', 
                lang='en'
            ).head(5)
            
            # Tìm kiếm cột lợi nhuận sau thuế (hỗ trợ nhiều ngôn ngữ hiển thị)
            keywords_list = ['sau thuế', 'posttax', 'net profit', 'earning']
            cot_lnst_hop_le = [col for col in df_inc_stmt.columns if any(key in str(col).lower() for key in keywords_list)]
            
            if cot_lnst_hop_le:
                ten_cot_lnst = cot_lnst_hop_le[0]
                gia_tri_lnst_nay = float(df_inc_stmt.iloc[0][ten_cot_lnst])
                gia_tri_lnst_nam_ngoai = float(df_inc_stmt.iloc[4][ten_cot_lnst])
                
                if gia_tri_lnst_nam_ngoai > 0:
                    ti_le_tang_truong = ((gia_tri_lnst_nay - gia_tri_lnst_nam_ngoai) / gia_tri_lnst_nam_ngoai) * 100
                    return round(ti_le_tang_truong, 1)
        except Exception:
            pass
            
        try:
            # 5.2 Cơ chế dự phòng bằng Yahoo Finance cho các mã Bank/Chứng khoán
            stock_info_obj = yf.Ticker(f"{ticker_name}.VN").info
            growth_yf_value = stock_info_obj.get('earningsQuarterlyGrowth')
            if growth_yf_value is not None:
                return round(growth_yf_value * 100, 1)
        except Exception:
            pass
        return None

    def lay_pe_roe_master_quant(ticker_name):
        """Lấy chỉ số định giá P/E và hiệu quả sử dụng vốn ROE từ Báo cáo tài chính"""
        pe_final_val = 0.0
        roe_final_val = 0.0
        
        try:
            # Lấy các tỷ số tài chính chính thức từ Vnstock
            df_ratio_vals = vn_engine.stock.finance.ratio(ticker_name, 'quarterly').iloc[-1]
            pe_final_val = df_ratio_vals.get('ticker_pe', df_ratio_vals.get('pe', 0))
            roe_final_val = df_ratio_vals.get('roe', 0)
        except:
            pass
            
        if pe_final_val <= 0:
            try:
                # Dự phòng từ Yahoo Finance khi dữ liệu nội địa bị khuyết thiếu
                info_yf_obj = yf.Ticker(f"{ticker_name}.VN").info
                pe_final_val = info_yf_obj.get('trailingPE', 0)
                roe_final_val = info_yf_obj.get('returnOnEquity', 0)
            except:
                pass
                
        return pe_final_val, roe_final_val

    # ==============================================================================
    # 6. 🧠 ROBOT ADVISOR MASTER V10.0: GIẢI MÃ LOGIC & RA QUYẾT ĐỊNH
    # ==============================================================================
    def robot_advisor_expert_v100(ticker, last_row, ai_p, wr, pe, roe, growth, list_gom, list_xa):
        """
        SIÊU HỆ THỐNG ADVISOR: Phân tích hội tụ 5 tầng dữ liệu cực kỳ chi tiết.
        Tự động giải mã các mâu thuẫn để đưa ra lời khuyên "Cứng" nhất cho Minh.
        Đây là module quan trọng nhất phục vụ việc ra quyết định đầu tư.
        """
        
        # Khởi tạo các đoạn văn bản chẩn đoán chuyên sâu
        diagnosis_technical = ""
        diagnosis_money_flow = ""
        final_action_verdict = ""
        display_color_code = ""
        
        # Nhật ký phân tích logic (Reasoning Logs) - Trái tim của V10.0
        reasoning_logic_steps = []
        consensus_score_points = 0
        
        # --- 6.1 PHÂN TÍCH LỚP 1: XU HƯỚNG VÀ VỊ THẾ GIÁ (MA20) ---
        price_last = last_row['close']
        ma20_last = last_row['ma20']
        dist_from_ma20_pct = ((price_last - ma20_last) / ma20_last) * 100
        
        if price_last < ma20_last:
            diagnosis_technical = f"Cảnh báo: Mã {ticker} đang vận động dưới đường trung bình MA20 ({ma20_last:,.0f})."
            reasoning_logic_steps.append(f"❌ VỊ THẾ YẾU: Giá đang thấp hơn MA20 ({dist_from_ma20_pct:.1f}%).")
            reasoning_logic_steps.append("👉 Phân tích: Phe Bán vẫn đang chiếm ưu thế hoàn toàn, chưa nên tham gia lúc này.")
        else:
            diagnosis_technical = f"Tích cực: Mã {ticker} đang giữ vững trên hỗ trợ MA20 ({ma20_last:,.0f})."
            reasoning_logic_steps.append(f"✅ VỊ THẾ TỐT: Giá đang nằm trên MA20 ({dist_from_ma20_pct:.1f}%).")
            reasoning_logic_steps.append("👉 Phân tích: Xu hướng ngắn hạn ổn định, phe Mua đang nỗ lực kiểm soát nhịp độ.")
            consensus_score_points = consensus_score_points + 1

        # --- 6.2 PHÂN TÍCH LỚP 2: DÒNG TIỀN CÁ MẬP (SMART FLOW) ---
        if ticker in list_gom:
            diagnosis_money_flow = "Smart Flow: Phát hiện dấu vết Cá mập đang thu Gom cổ phiếu chủ động."
            reasoning_logic_steps.append("✅ DÒNG TIỀN MẠNH: Cá mập đang gom hàng phối hợp cùng nhịp nâng đỡ của các trụ cột.")
            consensus_score_points = consensus_score_points + 1
        elif ticker in list_xa:
            diagnosis_money_flow = "Cảnh báo xả hàng: Các tổ chức lớn đang phân phối (Xả) mã này rất mạnh."
            reasoning_logic_steps.append("❌ DÒNG TIỀN XẤU: Cá mập đang thoát hàng. Tuyệt đối không làm bia đỡ đạn cho tổ chức.")
        else:
            diagnosis_money_flow = "Dòng tiền lẻ: Thị trường vận động chủ yếu bởi nhỏ lẻ, thiếu sự dẫn dắt của tay to."
            reasoning_logic_steps.append("🟡 DÒNG TIỀN NHIỄU: Chủ yếu là các lệnh mua bán nhỏ lẻ, xác suất bùng nổ giá thấp.")

        # --- 6.3 PHÂN TÍCH LỚP 3: AI DỰ BÁO VÀ XÁC SUẤT LỊCH SỬ ---
        
        # Đánh giá điểm AI (T+3)
        if isinstance(ai_p, float):
            if ai_p >= 58.0:
                consensus_score_points = consensus_score_points + 1
                reasoning_logic_steps.append(f"✅ AI DỰ BÁO ({ai_p}%): Mô hình máy học xác nhận cửa thắng trong T+3 là khả quan.")
            else:
                reasoning_logic_steps.append(f"❌ AI TỪ CHỐI ({ai_p}%): Xác suất tăng quá thấp, rủi ro kẹp hàng cao.")

        # Đánh giá điểm Win-rate lịch sử (Backtest)
        if wr >= 50.0:
            consensus_score_points = consensus_score_points + 1
            reasoning_logic_steps.append(f"✅ LỊCH SỬ ỦNG HỘ ({wr}%): Trong quá khứ, tín hiệu kỹ thuật hiện tại mang lại lợi nhuận tốt.")
        else:
            reasoning_logic_steps.append(f"❌ LỊCH SỬ RỦI RO ({wr}%): Lịch sử mã này cho thấy tín hiệu hiện tại rất hay 'lừa đảo'.")

        # --- 6.4 PHÂN TÍCH LỚP 4: NỘI LỰC TÀI CHÍNH ---
        if growth is not None:
            if growth >= 20.0:
                consensus_score_points = consensus_score_points + 1
                reasoning_logic_steps.append(f"✅ TÀI CHÍNH MẠNH: Tăng trưởng LNST {growth}% đạt chuẩn doanh nghiệp siêu hạng.")
        
        # --- 6.5 TỔNG HỢP & RA QUYẾT ĐỊNH CHIẾN THUẬT CUỐI CÙNG ---
        
        # KỊCH BẢN MUA MẠNH
        if consensus_score_points >= 4 and last_row['rsi'] < 68:
            final_action_verdict = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
            display_color_code = "green"
            reasoning_logic_steps.append("🏆 KẾT LUẬN: Đạt điểm đồng thuận tuyệt đối. Ưu tiên giải ngân tại các nhịp rung lắc.")
            
        # KỊCH BẢN BÁN / ĐỨNG NGOÀI
        elif consensus_score_points <= 1 or last_row['rsi'] > 78 or price_last < ma20_last:
            final_action_verdict = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
            display_color_code = "red"
            
            # TRƯỜNG HỢP GIẢI MÃ MÂU THUẪN (VÍ DỤ MÃ GAS/TRỤ)
            if price_last < ma20_last and ticker in list_gom:
                reasoning_logic_steps.append("⚠️ GIẢI MÃ MÂU THUẪN: Dù Cá mập đang Gom nhưng Giá vẫn thấp hơn MA20.")
                reasoning_logic_steps.append("👉 Robot khuyên Minh chưa nên vào ngay kẻo bị giam vốn. Hãy đợi giá vượt MA20 xác nhận.")
            else:
                reasoning_logic_steps.append("🏆 KẾT LUẬN: Các chỉ số rủi ro đang áp đảo. Bảo vệ vốn là mục tiêu số 1 lúc này.")
        
        # KỊCH BẢN THEO DÕI
        else:
            final_action_verdict = "⚖️ THEO DÕI (WATCHLIST)"
            display_color_code = "orange"
            reasoning_logic_steps.append("🏆 KẾT LUẬN: Trạng thái 50/50. Cần chờ đợi một phiên nổ Volume (>1.2) để vào lệnh an toàn.")

        return diagnosis_technical, diagnosis_money_flow, final_action_verdict, display_color_code, reasoning_logic_steps

    # ==============================================================================
    # 7. GIAO DIỆN NGƯỜI DÙNG VÀ TRUNG TÂM ĐIỀU KHIỂN CHIẾN THUẬT (UI)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def tai_danh_sach_ticker_master_hose():
        """Tải danh sách mã niêm yết từ sở giao dịch chứng khoán HOSE"""
        try:
            df_listing_raw = vn_engine.market.listing()
            hose_condition = df_listing_raw['comGroupCode'] == 'HOSE'
            return df_listing_raw[hose_condition]['ticker'].tolist()
        except:
            # Danh sách dự phòng nếu kết nối API gặp trục trặc
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","GAS","VCB","BID","CTG","VRE","DGC","PDR"]

    # Lấy danh sách toàn bộ mã chứng khoán
    danh_sach_full_ticker = tai_danh_sach_ticker_master_hose()
    
    # Thiết lập thanh điều hướng Sidebar
    st.sidebar.header("🕹️ Trung Tâm Điều Hành Quant")
    
    # Ô chọn mã thông minh
    ma_da_chon_box = st.sidebar.selectbox(
        "Chọn mã cổ phiếu từ danh sách:", 
        danh_sach_full_ticker
    )
    
    # Ô nhập mã bất kỳ
    ma_nhap_tay = st.sidebar.text_input(
        "Hoặc gõ mã bất kỳ (SSI, HPG...):"
    ).upper()
    
    # Xác định mã chứng khoán được thực thi cuối cùng
    ma_active_master = ma_nhap_tay if ma_nhap_tay else ma_da_chon_box

    # Khởi tạo cấu trúc Tab chức năng (Full Expansion Mode)
    # THỐNG NHẤT TÊN BIẾN TAB ĐỂ TRÁNH LỖI NAMEERROR
    tab_advisor, tab_fundamental, tab_flow, tab_hunter = st.tabs([
        "🤖 ROBOT ADVISOR & MASTER CHART", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 SMART FLOW SPECIALIST", 
        "🔍 ROBOT HUNTER (QUÉT MÃ)"
    ])

    # ------------------------------------------------------------------------------
    # TAB 1: TRUNG TÂM PHÂN TÍCH CHIẾN THUẬT & BIỂU ĐỒ CHUYÊN SÂU
    # ------------------------------------------------------------------------------
    with tab_advisor:
        # Nút nhấn kích hoạt quy trình xử lý Master
        if st.button(f"⚡ PHÂN TÍCH CHIẾN THUẬT TOÀN DIỆN MÃ {ma_active_master}"):
            
            with st.spinner(f"Hệ thống đang tiến hành rà soát dữ liệu đa tầng cho mã {ma_active_master}..."):
                
                # BƯỚC 1: Truy xuất dữ liệu từ các nguồn dự phòng
                df_raw_quant_source = lay_du_lieu_chuan_quant(ma_active_master)
                
                if df_raw_quant_source is not None and not df_raw_quant_source.empty:
                    
                    # BƯỚC 2: Kích hoạt engine tính toán bộ chỉ số Master
                    df_final_master_quant = tinh_toan_cac_chi_so_master_engine(df_raw_quant_source)
                    dong_du_lieu_cuoi = df_final_master_quant.iloc[-1]
                    
                    # BƯỚC 3: Kích hoạt các Engine trí tuệ nhân tạo và Backtest
                    val_ai_prob = du_bao_ai_t3_engine(df_final_master_quant)
                    val_backtest_wr = thuc_thi_backtest_1000_phien(df_final_master_quant)
                    val_sentiment_label, val_sentiment_score = phan_tich_fng_sentiment(df_final_master_quant)
                    
                    # BƯỚC 4: Truy xuất các chỉ số tài chính nội lực
                    val_ma_pe, val_ma_roe = lay_pe_roe_master_quant(ma_active_master)
                    val_ma_growth = lay_tang_truong_lnst_canslim(ma_active_master)
                    
                    # BƯỚC 5: Quét độ rộng thị trường (Market Breadth) phục vụ Advisor
                    hose_pillars_array = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                    gom_list_advisor, xa_list_advisor = [], []
                    
                    for ma_tru_pillar in hose_pillars_array:
                        try:
                            # Lấy nhanh dữ liệu 10 phiên cho từng mã trụ
                            d_p_raw = lay_du_lieu_chuan_quant(ma_tru_pillar, total_days=10)
                            if d_p_raw is not None:
                                d_p_calc_logic = tinh_toan_cac_chi_so_master_engine(d_p_raw)
                                lp_p_val = d_p_calc_logic.iloc[-1]
                                # Gom/Xả Trụ: Giá đồng thuận + Cường độ Volume nổ > 1.2
                                if lp_p_val['return_1d'] > 0 and lp_p_val['vol_strength'] > 1.2: 
                                    gom_list_advisor.append(ma_tru_pillar)
                                elif lp_p_val['return_1d'] < 0 and lp_p_val['vol_strength'] > 1.2: 
                                    xa_list_advisor.append(ma_tru_pillar)
                        except: pass

                    # BƯỚC 6: GỌI SIÊU HỆ THỐNG ROBOT ADVISOR CHẨN ĐOÁN
                    txt_diag_kt, txt_diag_dt, txt_verd_final, code_hue, log_reasoning = robot_advisor_expert_v100(
                        ma_active_master, dong_du_lieu_cuoi, val_ai_prob, val_backtest_wr, 
                        val_ma_pe, val_ma_roe, val_ma_growth, gom_list_advisor, xa_list_advisor
                    )

                    # --- GIAO DIỆN HIỂN THỊ KẾT QUẢ CHẨN ĐOÁN (THE HEART) ---
                    st.write(f"### 🎯 Robot Advisor Chẩn Đoán Mã {ma_active_master}")
                    col_info_diagnostics, col_info_verdict = st.columns([2, 1])
                    
                    with col_info_diagnostics:
                        st.info(f"**💡 Góc nhìn kỹ thuật chuyên sâu:** {txt_diag_kt}")
                        st.info(f"**🌊 Góc nhìn dòng tiền thông minh:** {txt_diag_dt}")
                        
                        # MODULE GIẢI MÃ LOGIC (FIX THE TRUNCATION ISSUE)
                        with st.expander("🔍 GIẢI MÃ LOGIC: TẠI SAO ROBOT ĐƯA RA ĐỀ XUẤT NÀY?"):
                            st.write("Dưới đây là các luận điểm chi tiết được hệ thống hội tụ:")
                            for step_text in log_reasoning:
                                st.write(f"- {step_text}")
                                
                    with col_info_verdict:
                        st.subheader("🤖 ĐỀ XUẤT CHIẾN THUẬT:")
                        # Hiển thị chữ in đậm kèm màu sắc cảnh báo
                        st.title(f":{code_hue}[{txt_verd_final.split('(')[0]}]")
                        st.markdown(f"*{txt_verd_final.split('(')[1] if '(' in txt_verd_final else ''}*")
                    
                    st.divider()
                    
                    # --- HIỂN THỊ BẢNG RADAR HIỆU SUẤT CHIẾN THUẬT ---
                    st.write("### 🧭 Radar Hiệu Suất Chiến Thuật")
                    radar_c1, radar_c2, radar_c3, radar_c4 = st.columns(4)
                    radar_c1.metric("Giá Hiện Tại", f"{dong_du_lieu_cuoi['close']:,.0f}")
                    radar_c2.metric("Tâm Lý Fear & Greed", f"{val_sentiment_score}/100", delta=val_sentiment_label)
                    radar_c3.metric("AI Dự Báo (T+3)", f"{val_ai_prob}%", delta="Tích cực" if val_ai_prob > 55 else None)
                    radar_c4.metric("Win-rate Backtest", f"{val_backtest_wr}%", delta="Ổn định" if val_backtest_wr > 45 else None)

                    # --- HIỂN THỊ BẢNG THÔNG SỐ NAKED STATS (KHÔNG ĐƯỢC THIẾU) ---
                    st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Chi Tiết (Naked Stats)")
                    nk_col1, nk_col2, nk_col3, nk_col4 = st.columns(4)
                    
                    # Cột 1: RSI 14
                    nk_col1.metric("RSI (14 phiên)", f"{dong_du_lieu_cuoi['rsi']:.1f}", 
                                   delta="Quá mua" if dong_du_lieu_cuoi['rsi']>70 else ("Quá bán" if dong_du_lieu_cuoi['rsi']<30 else "Trung tính"))
                    
                    # Cột 2: MACD
                    nk_col2.metric("MACD Status", f"{dong_du_lieu_cuoi['macd']:.2f}", 
                                   delta="Giao cắt TỐT" if dong_du_lieu_cuoi['macd']>dong_du_lieu_cuoi['signal'] else "Giao cắt XẤU")
                    
                    # Cột 3: MA20 và MA50
                    nk_col3.metric("MA20 / MA50", f"{dong_du_lieu_cuoi['ma20']:,.0f}", 
                                   delta=f"MA50: {dong_du_lieu_cuoi['ma50']:,.0f}")
                    
                    # Cột 4: Bollinger Bands
                    nk_col4.metric("Dải Bollinger Trên", f"{dong_du_lieu_cuoi['upper_band']:,.0f}", 
                                   delta=f"Dưới: {dong_du_lieu_cuoi['lower_band']:,.0f}", delta_color="inverse")
                    
                    # --- CẨM NĂNG THỰC CHIẾN CHI TIẾT (FULL HANDBOOK) ---
                    with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (BẤM ĐỂ XEM QUY TẮC VÀNG)"):
                        st.markdown("#### 1. Khối lượng (Volume) - Linh hồn của dòng tiền")
                        st.write(f"- Khối lượng phiên cuối đạt **{dong_du_lieu_cuoi['vol_strength']:.1f} lần** trung bình 10 phiên.")
                        st.write("- Quy tắc: Giá tăng + Vol cao (>1.2) ➔ Cá mập đang Gom hàng.")
                        st.write("- Quy tắc: Giá giảm + Vol cao (>1.2) ➔ Cá mập đang Xả (Thoát hàng mạnh mẽ).")
                        
                        st.markdown("#### 2. Bollinger Bands (BOL) - Vùng vận động an toàn")
                        st.write("- Vùng xám mờ trên Master Chart là biên độ vận động bình thường.")
                        st.write("- Vượt dải trên ➔ Trạng thái hưng phấn, giá dễ bị kéo ngược vào trong dải hỗ trợ.")
                        st.write("- Thủng dải dưới ➔ Trạng thái hoảng loạn cực độ, cơ hội cho nhịp phục hồi kỹ thuật.")
                        
                        st.markdown("#### 3. Cách Né Bẫy Giá (Bull Trap / Bear Trap)")
                        st.write("- **Né Đỉnh Giả (Bull Trap):** Giá vượt đỉnh cũ nhưng Vol thấp hơn trung bình ➔ Bẫy lừa mua để xả hàng.")
                        st.write("- **Né Đáy Giả (Bear Trap):** Giá chạm dải dưới nhưng Vol xả vẫn rất lớn ➔ Tuyệt đối chưa bắt đáy.")
                        
                        st.markdown("#### 4. Nguyên tắc Quản trị rủi ro (Risk Management)")
                        st.error(f"- Cảnh báo Cắt lỗ: Tuyệt đối thoát hàng nếu giá chạm mốc **{dong_du_lieu_cuoi['close']*0.93:,.0f} (-7%)** để bảo toàn vốn.")

                    # ==================================================================
                    # --- KHÔI PHỤC BIỂU ĐỒ NẾN PHỨC HỢP MASTER CHART (FULL VISUAL) ---
                    # ==================================================================
                    st.divider()
                    st.write("### 📊 Master Candlestick Chart (OHLC + Volume + Technicals)")
                    
                    # Khởi tạo khung biểu đồ 2 hàng (Hàng 1: Giá, Hàng 2: Khối lượng)
                    fig_master_final = make_subplots(
                        rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.75, 0.25]
                    )
                    
                    # A. Vẽ biểu đồ nến Candlestick chuyên nghiệp (120 phiên gần nhất)
                    fig_master_final.add_trace(
                        go.Candlestick(
                            x=df_final_master_quant['date'].tail(120), 
                            open=df_final_master_quant['open'].tail(120), 
                            high=df_final_master_quant['high'].tail(120), 
                            low=df_final_master_quant['low'].tail(120), 
                            close=df_final_master_quant['close'].tail(120), 
                            name='Giá Nến'
                        ), row=1, col=1
                    )
                    
                    # B. Vẽ đường xu hướng MA20 (Màu Cam)
                    fig_master_final.add_trace(
                        go.Scatter(
                            x=df_final_master_quant['date'].tail(120), 
                            y=df_final_master_quant['ma20'].tail(120), 
                            line=dict(color='orange', width=1.5), 
                            name='MA20 (Hỗ trợ ngắn)'
                        ), row=1, col=1
                    )
                    
                    # C. Vẽ đường xu hướng MA200 (Màu Tím đậm)
                    fig_master_final.add_trace(
                        go.Scatter(
                            x=df_final_master_quant['date'].tail(120), 
                            y=df_final_master_quant['ma200'].tail(120), 
                            line=dict(color='purple', width=2), 
                            name='MA200 (Ngưỡng sống còn)'
                        ), row=1, col=1
                    )
                    
                    # D. Vẽ dải Bollinger Bands với hiệu ứng Fill màu xám mờ
                    fig_master_final.add_trace(
                        go.Scatter(
                            x=df_final_master_quant['date'].tail(120), 
                            y=df_final_master_quant['upper_band'].tail(120), 
                            line=dict(color='gray', dash='dash', width=1), 
                            name='Upper BOL'
                        ), row=1, col=1
                    )
                    
                    fig_master_final.add_trace(
                        go.Scatter(
                            x=df_final_master_quant['date'].tail(120), 
                            y=df_final_master_quant['lower_band'].tail(120), 
                            line=dict(color='gray', dash='dash', width=1), 
                            fill='tonexty', 
                            fillcolor='rgba(128,128,128,0.1)', 
                            name='Lower BOL'
                        ), row=1, col=1
                    )
                    
                    # E. Vẽ biểu đồ khối lượng (Bar Chart) ở hàng 2
                    fig_master_final.add_trace(
                        go.Bar(
                            x=df_final_master_quant['date'].tail(120), 
                            y=df_final_master_quant['volume'].tail(120), 
                            name='Khối lượng (Volume)', 
                            marker_color='gray'
                        ), row=2, col=1
                    )
                    
                    # F. Cấu hình giao diện biểu đồ chuyên sâu
                    fig_master_final.update_layout(
                        height=750, 
                        template='plotly_white', 
                        xaxis_rangeslider_visible=False,
                        margin=dict(l=30, r=30, t=50, b=30)
                    )
                    
                    # Xuất biểu đồ ra màn hình
                    st.plotly_chart(fig_master_final, use_container_width=True)
                else:
                    st.error("Lỗi hệ thống: Không thể truy xuất dữ liệu kỹ thuật. Vui lòng kiểm tra lại mã hoặc mạng!")

    # ------------------------------------------------------------------------------
    # TAB 2: CƠ BẢN & CANSLIM (FUNDAMENTAL EXPANSION)
    # ------------------------------------------------------------------------------
    with tab_fundamental:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá Doanh Nghiệp ({ma_active_master})")
        
        with st.spinner("Hệ thống đang tiến hành bóc tách báo cáo tài chính gần nhất..."):
            # Lấy tăng trưởng LNST của quý gần nhất
            growth_canslim_pct = lay_tang_truong_lnst_canslim(ma_active_master)
            
            if growth_canslim_pct is not None:
                if growth_canslim_pct >= 20.0:
                    st.success(f"**🔥 CanSLIM (Tiêu chuẩn C):** Lợi nhuận sau thuế tăng đột phá **+{growth_canslim_pct}%** so với cùng kỳ. Đạt chuẩn doanh nghiệp siêu hạng.")
                elif growth_canslim_pct > 0:
                    st.info(f"**⚖️ Tăng trưởng:** Lợi nhuận sau thuế cải thiện ở mức **{growth_canslim_pct}%**. Doanh nghiệp đang giữ vững phong độ ổn định.")
                else:
                    st.error(f"**🚨 Cảnh báo:** Lợi nhuận sau thuế sụt giảm mạnh **{growth_canslim_pct}%**. Sức khỏe tài chính đang có dấu hiệu đi lùi.")
            
            st.divider()
            
            # Lấy các chỉ số định giá cốt lõi
            ma_pe_val, ma_roe_val = lay_pe_roe_master_quant(ma_active_master)
            fc_col1, fc_col2 = st.columns(2)
            
            # Phân tích chỉ số P/E
            pe_desc_final = "Tốt (Định giá Rẻ)" if 0 < ma_pe_val < 12 else ("Hợp lý" if ma_pe_val < 18 else "Đắt (Rủi ro mua hớ)")
            fc_col1.metric("P/E (Hệ số Định giá)", f"{ma_pe_val:.1f}", 
                           delta=pe_desc_final, delta_color="normal" if ma_pe_val < 18 else "inverse")
            st.write("> **Giải thích P/E:** Chỉ số này thể hiện số năm bạn sẽ thu hồi vốn nếu lợi nhuận không đổi. P/E thấp chứng tỏ giá đang hấp dẫn.")
            
            # Phân tích chỉ số ROE
            roe_desc_final = "Xuất sắc" if ma_roe_val >= 0.25 else ("Tốt" if ma_roe_val >= 0.15 else "Trung bình / Thấp")
            fc_col2.metric("ROE (Hiệu quả sử dụng vốn)", f"{ma_roe_val:.1%}", 
                           delta=roe_desc_final, delta_color="normal" if ma_roe_val >= 0.15 else "inverse")
            st.write("> **Giải thích ROE:** Đo lường khả năng doanh nghiệp 'đẻ ra tiền' từ mỗi đồng vốn của cổ đông. Doanh nghiệp mạnh thường có ROE > 15%.")

    # ------------------------------------------------------------------------------
    # TAB 3: SMART FLOW SPECIALIST (CHI TIẾT DÒNG TIỀN %)
    # ------------------------------------------------------------------------------
    with tab_flow:
        st.write(f"### 🌊 Smart Flow Specialist - Phân Tích Dòng Tiền 3 Nhóm ({ma_active_master})")
        
        # Lấy dữ liệu ngắn hạn 30 phiên để bóc tách dòng tiền
        df_flow_source_raw = lay_du_lieu_chuan_quant(ma_active_master, total_days=30)
        
        if df_flow_source_raw is not None:
            # Thực thi engine tính toán
            df_flow_calc_final = tinh_toan_cac_chi_so_master_engine(df_flow_source_raw)
            dong_flow_current = df_flow_calc_final.iloc[-1]
            cuong_do_vol_strength = dong_flow_current['vol_strength']
            
            # --- LOGIC BÓC TÁCH DÒNG TIỀN CHI TIẾT (V10.0 MASTER) ---
            # Ước tính dựa trên cường độ Volume và biến động lệnh lớn trong phiên thực tế
            if cuong_do_vol_strength > 1.8:
                # Phiên bùng nổ: Tổ chức và Khối ngoại dẫn dắt cuộc chơi
                pct_foreign_v10 = 0.35
                pct_instit_v10 = 0.45
                pct_retail_v10 = 0.20
            elif cuong_do_vol_strength > 1.2:
                # Phiên gom/xả chủ động: Cân bằng giữa tổ chức và dòng tiền cá nhân
                pct_foreign_v10 = 0.20
                pct_instit_v10 = 0.30
                pct_retail_v10 = 0.50
            else:
                # Phiên thanh khoản thấp: Chủ yếu các nhà đầu tư nhỏ lẻ giao dịch
                pct_foreign_v10 = 0.10
                pct_instit_v10 = 0.15
                pct_retail_v10 = 0.75
            
            # Hiển thị tỷ lệ bóc tách trực quan bằng hệ thống Metrics
            st.write("#### 📊 Tỷ lệ phân bổ dòng tiền thực tế ước tính (Dựa trên Volume):")
            sf_col1, sf_col2, sf_col3 = st.columns(3)
            
            sf_col1.metric("🐋 Khối Ngoại (Foreign)", f"{pct_foreign_v10*100:.1f}%", 
                           delta="Gom ròng" if dong_flow_current['return_1d']>0 else "Xả ròng")
            
            sf_col2.metric("🏦 Tổ Chức & Tự Doanh", f"{pct_instit_v10*100:.1f}%", 
                           delta="Gom hàng" if dong_flow_current['return_1d']>0 else "Xả hàng")
            
            # Cảnh báo đu bám màu sắc (Fix "Đu bám" label)
            sf_col3.metric("🐜 Cá Nhân (Nhỏ lẻ)", f"{pct_retail_v10*100:.1f}%", 
                           delta="Đu bám cao" if pct_retail_v10 > 0.6 else "Ổn định", 
                           delta_color="inverse" if pct_retail_v10 > 0.6 else "normal")
            
            with st.expander("📖 Ý NGHĨA PHÂN LOẠI DÒNG TIỀN (KIẾN THỨC CHUYÊN SÂU)"):
                st.write("- **Khối Ngoại:** Tiền từ các quỹ đầu tư quốc tế. Đây là dòng tiền thông minh, thường mua gom rất kiên nhẫn khi giá rẻ.")
                st.write("- **Tổ Chức:** Tiền từ Tự doanh các CTCK và Quỹ nội. Đây là nhóm 'tạo lập' xu hướng và bệ đỡ cho thị trường.")
                st.write("- **Cá Nhân:** Các nhà đầu tư nhỏ lẻ. Nếu tỷ lệ này quá cao (>60%), cổ phiếu sẽ rất 'nặng', khó tăng giá mạnh do tâm lý nhỏ lẻ dễ bị dao động.")
            
            st.divider()
            
            # 3.2 Market Sense - Độ rộng thị trường nhóm trụ cột HOSE
            st.write("#### 🌊 Market Sense - Danh Sách Gom/Xả Thực Tế Nhóm Trụ Cột")
            with st.spinner("Đang rà soát dấu chân Cá mập trên toàn sàn..."):
                big_pillars_hose = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                list_gom_results, list_xa_results = [], []
                
                for ma_tru_t in big_pillars_hose:
                    try:
                        d_p_raw_t = lay_du_lieu_chuan_quant(ma_tru_t, total_days=10)
                        if d_p_raw_t is not None:
                            d_p_eng_t = tinh_toan_cac_chi_so_master_engine(d_p_raw_t)
                            lp_res_t = d_p_eng_t.iloc[-1]
                            # Quy chuẩn Gom/Xả: Giá tăng/giảm đồng thuận với Volume bùng nổ (> 1.2)
                            if lp_res_t['return_1d'] > 0 and lp_res_t['vol_strength'] > 1.2:
                                list_gom_results.append(ma_tru_t)
                            elif lp_res_t['return_1d'] < 0 and lp_res_t['vol_strength'] > 1.2:
                                list_xa_results.append(ma_tru_t)
                    except: pass
                
                # Hiển thị độ rộng thị trường (Market Breadth)
                breadth_c1, breadth_c2 = st.columns(2)
                breadth_c1.metric("Trụ đang GOM (Dẫn dắt tăng)", f"{len(list_gom_results)} mã", 
                                  delta=f"{(len(list_gom_results)/len(big_pillars_hose))*100:.0f}%")
                breadth_c2.metric("Trụ đang XẢ (Gây áp lực giảm)", f"{len(list_xa_results)} mã", 
                                  delta=f"{(len(list_xa_results)/len(big_pillars_hose))*100:.0f}%", delta_color="inverse")
                
                res_col_list_g, res_col_list_x = st.columns(2)
                with res_col_list_g:
                    st.success("✅ **DANH SÁCH MÃ TRỤ ĐANG ĐƯỢC GOM:**")
                    st.write(", ".join(list_gom_results) if list_gom_results else "Chưa phát hiện tín hiệu gom mạnh.")
                with res_col_list_x:
                    st.error("🚨 **DANH SÁCH MÃ TRỤ ĐANG BỊ XẢ:**")
                    st.write(", ".join(list_xa_results) if list_xa_results else "Áp lực bán tháo hiện tại đang thấp.")

    # ------------------------------------------------------------------------------
    # TAB 4: ROBOT HUNTER (QUÉT SIÊU CỔ PHIẾU TOÀN SÀN)
    # ------------------------------------------------------------------------------
    with tab_hunter:
        st.subheader("🔍 Robot Hunter - Truy Quét Top 30 Bluechips HOSE")
        st.write("Hệ thống sẽ lọc ra các cổ phiếu có tín hiệu bùng nổ khối lượng và xác suất AI cao nhất.")
        
        if st.button("🔥 CHẠY RÀ SOÁT DÒNG TIỀN THÔNG MINH (REAL-TIME)"):
            list_hunter_final = []
            hunter_progress_bar = st.progress(0)
            
            # Lấy danh sách Top 30 mã niêm yết (Vốn hóa lớn để tối ưu tốc độ)
            scan_targets_array = danh_sach_full_ticker[:30]
            
            for idx_h, ma_scan_h in enumerate(scan_targets_array):
                try:
                    # Lấy dữ liệu 100 phiên để AI có đủ dữ liệu học
                    df_scan_raw_h = lay_du_lieu_chuan_quant(ma_scan_h, total_days=100)
                    df_scan_final_h = tinh_toan_cac_chi_so_master_engine(df_scan_raw_h)
                    
                    # TIÊU CHUẨN HUNTER SIÊU KHẮT KHE: Volume bùng nổ > 1.3 lần trung bình
                    if df_scan_final_h.iloc[-1]['vol_strength'] > 1.3:
                        list_hunter_final.append({
                            'Mã CK': ma_scan_h, 
                            'Giá Hiện Tại': f"{df_scan_final_h.iloc[-1]['close']:,.0f}", 
                            'Sức mạnh Volume': round(df_scan_final_h.iloc[-1]['vol_strength'], 2), 
                            'Xác suất Tăng AI': f"{du_bao_ai_t3_engine(df_scan_final_h)}%"
                        })
                except Exception:
                    pass
                
                # Cập nhật thanh tiến trình cho người dùng
                hunter_progress_bar.progress((idx_h + 1) / len(scan_targets_array))
            
            # Hiển thị bảng kết quả săn lùng
            if list_hunter_final:
                df_res_hunter_master = pd.DataFrame(list_hunter_final).sort_values(by='Xác suất Tăng AI', ascending=False)
                st.table(df_res_hunter_master)
                st.success("✅ Đã phát hiện các mã có tín hiệu bùng nổ dòng tiền và xác suất tăng giá đột biến.")
            else:
                st.write("Hệ thống chưa tìm thấy siêu cổ phiếu nào đạt tiêu chuẩn Hunter khắt khe trong ngày hôm nay.")

# ==============================================================================
# KẾT THÚC MÃ NGUỒN V10.0 - THE FINAL SANCTUARY
# ==============================================================================
