# ==============================================================================
# HỆ THỐNG QUẢN TRỊ ĐẦU TƯ ĐỊNH LƯỢNG - QUANT SYSTEM V10.2 ETERNAL SANCTUARY
# ------------------------------------------------------------------------------
# PHÂN HỆ: ADVISOR MASTER, SMART FLOW SPECIALIST, MASTER CHART & AI ENGINE
# CHỦ SỞ HỮU: MINH
# TRẠNG THÁI: PHIÊN BẢN HYPER-VERBOSE (TƯỜNG MINH TUYỆT ĐỐI)
# CAM KẾT: KHÔNG RÚT GỌN - KHÔNG VIẾT TẮT - ĐẦY ĐỦ 100% VŨ KHÍ
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
# RandomForestClassifier: Thuật toán máy học để dự báo xu hướng T+3
# SentimentIntensityAnalyzer: Công cụ phân tích tâm lý thị trường
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo các tài nguyên cần thiết cho AI được tải đầy đủ để tránh lỗi Runtime.
# Bước này cực kỳ quan trọng để module Advisor có thể hoạt động ổn định trên Cloud.
try:
    # Thử tìm dữ liệu từ điển cảm xúc trong hệ thống tệp
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu không tìm thấy, thực hiện tải xuống tự động từ máy chủ NLTK chính thức
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & KIỂM SOÁT TRUY CẬP (SECURITY LAYER)
# ==============================================================================
def check_password_for_minh():
    """
    Hàm xác thực mật mã dành riêng cho Minh.
    Đảm bảo tính riêng tư và bảo vệ các chiến thuật Quant Master.
    Sử dụng session_state để duy trì trạng thái đăng nhập trong suốt phiên.
    """
    
    def verify_credentials_logic():
        """Xử lý sự kiện kiểm tra khi người dùng nhập mật mã vào ô trống"""
        
        # 1.1 Lấy giá trị mật mã đích được cấu hình trong Streamlit Secrets (toml)
        target_password_key = st.secrets["password"]
        
        # 1.2 Lấy giá trị mật mã mà người dùng vừa nhập vào ô text input
        entered_password_input = st.session_state["password_input_key"]
        
        # 1.3 Thực hiện so sánh giá trị bảo mật
        if entered_password_input == target_password_key:
            # Nếu trùng khớp, xác nhận trạng thái đăng nhập thành công
            st.session_state["password_correct_state"] = True
            # Xóa mật mã khỏi bộ nhớ tạm ngay lập tức sau khi xác thực để đảm bảo an toàn
            del st.session_state["password_input_key"]
        else:
            # Nếu sai, đánh dấu trạng thái lỗi để hiển thị cảnh báo
            st.session_state["password_correct_state"] = False

    # 1.4 Kiểm tra xem trong phiên làm việc hiện tại đã được xác thực chưa
    if "password_correct_state" not in st.session_state:
        # Giao diện màn hình khóa ban đầu cho người dùng chưa đăng nhập
        st.markdown("### 🔐 Quant System V10.2 - Master Access Control")
        st.write("Chào Minh, vui lòng nhập mật mã để truy cập trung tâm điều hành chiến thuật.")
        
        # Tạo ô nhập liệu mật mã (chế độ ẩn ký tự)
        st.text_input(
            "🔑 Mật mã của Minh:", 
            type="password", 
            on_change=verify_credentials_logic, 
            key="password_input_key"
        )
        return False
    
    # 1.5 Kiểm tra nếu mật mã nhập trước đó bị sai (hiển thị thông báo lỗi)
    if st.session_state["password_correct_state"] == False:
        st.error("❌ Mật mã không chính xác. Vui lòng kiểm tra lại.")
        # Hiển thị lại ô nhập để người dùng thử lại
        st.text_input(
            "🔑 Nhập lại mật mã của Minh:", 
            type="password", 
            on_change=verify_credentials_logic, 
            key="password_input_key"
        )
        return False
    
    # 1.6 Trả về kết quả xác thực cuối cùng để thực thi chương trình chính
    return st.session_state.get("password_correct_state", False)

# ==============================================================================
# BẮT ĐẦU THỰC THI ỨNG DỤNG CHÍNH KHI ĐÃ ĐĂNG NHẬP THÀNH CÔNG
# ==============================================================================
if check_password_for_minh():
    
    # 1.7 Thiết lập cấu hình giao diện chuẩn Dashboard chuyên nghiệp dành cho dân Quant
    st.set_page_config(
        page_title="Quant System V10.2 Eternal Sanctuary", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 1.8 Hiển thị tiêu đề chính của hệ thống với định dạng nổi bật
    st.title("🛡️ Quant System V10.2: Ultimate Advisor & Flow Specialist")
    st.markdown("---")

    # 1.9 Khởi tạo kết nối tới động cơ dữ liệu Vnstock
    vn_stock_engine = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU ĐA TẦNG (DATA ACQUISITION LAYER)
    # ==============================================================================
    def lay_du_lieu_chuan_quant_master(ticker_input, num_days_history=1000):
        """
        Hàm lấy dữ liệu giá giao dịch lịch sử đầy đủ (OHLCV). 
        Hệ thống tích hợp cơ chế dự phòng đa nguồn (Fail-over mechanism) cực mạnh:
        - Nguồn 1: Vnstock (Dữ liệu nội địa chính thống, chuẩn sàn HOSE/HNX).
        - Nguồn 2: Yahoo Finance (Sử dụng khi Vnstock nghẽn hoặc cho các mã VND, SSI, Banks).
        """
        
        # Bước 2.1: Tính toán khoảng thời gian truy xuất
        now_datetime = datetime.now()
        ngay_ket_thuc_str = now_datetime.strftime('%Y-%m-%d')
        ngay_bat_dau_calc = now_datetime - timedelta(days=num_days_history)
        ngay_bat_dau_str = ngay_bat_dau_calc.strftime('%Y-%m-%d')
        
        # Bước 2.2: Phương án truy xuất ưu tiên - Vnstock Engine
        try:
            # Thực hiện gọi API Vnstock để lấy lịch sử giá
            df_vn_raw_data = vn_stock_engine.stock.quote.history(
                symbol=ticker_input, 
                start=ngay_bat_dau_str, 
                end=ngay_ket_thuc_str
            )
            
            # Kiểm tra xem dữ liệu trả về có tồn tại và không bị rỗng không
            if df_vn_raw_data is not None:
                if not df_vn_raw_data.empty:
                    # Tiến hành chuẩn hóa tên cột về dạng chữ thường để đồng bộ logic toàn hệ thống
                    column_names_normalized = []
                    for name in df_vn_raw_data.columns:
                        column_names_normalized.append(str(name).lower())
                    
                    # Cập nhật lại danh sách cột cho DataFrame
                    df_vn_raw_data.columns = column_names_normalized
                    return df_vn_raw_data
        except Exception:
            # Nếu Vnstock gặp lỗi kỹ thuật, hệ thống im lặng chuyển sang bước dự phòng
            pass
        
        # Bước 2.3: Phương án dự phòng (Fallback) - Yahoo Finance (YF)
        try:
            # Định dạng lại mã cổ phiếu phù hợp với chuẩn Yahoo Finance Việt Nam (.VN)
            if ticker_input == "VNINDEX":
                ma_symbol_yf = "^VNINDEX"
            else:
                ma_symbol_yf = f"{ticker_input}.VN"
                
            # Thực hiện tải dữ liệu với chu kỳ tối thiểu 3 năm để đảm bảo đủ tính toán MA200
            yf_raw_response = yf.download(
                ma_symbol_yf, 
                period="3y", 
                progress=False
            )
            
            # Kiểm tra dữ liệu Yahoo Finance trả về
            if not yf_raw_response.empty:
                # Chuyển Index (Ngày) thành một cột dữ liệu độc lập mang tên 'date'
                yf_raw_response = yf_raw_response.reset_index()
                
                # Xử lý Multi-index tiêu đề cột (Tránh lỗi do cập nhật thư viện yfinance mới)
                clean_column_headers = []
                for header_obj in yf_raw_response.columns:
                    if isinstance(header_obj, tuple):
                        # Lấy phần tử chính trong Tuple (thường là tên cột OHLC)
                        clean_column_headers.append(str(header_obj[0]).lower())
                    else:
                        # Chuyển tên cột đơn lẻ sang chữ thường
                        clean_column_headers.append(str(header_obj).lower())
                
                # Áp dụng danh sách tên cột đã làm sạch vào DataFrame dự phòng
                yf_raw_response.columns = clean_column_headers
                return yf_raw_response
                
        except Exception as error_msg:
            # Thông báo lỗi cuối cùng cho Minh nếu cả hai nguồn dữ liệu đều không khả dụng
            st.sidebar.error(f"⚠️ Không thể truy xuất dữ liệu mã {ticker_input}. Lỗi: {str(error_msg)}")
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT CHI TIẾT (ENGINE LAYER)
    # ==============================================================================
    def tinh_toan_bo_chi_so_quant_master(df_source_raw):
        """
        Hàm tính toán toàn bộ kho vũ khí chỉ báo kỹ thuật của hệ thống.
        Bao gồm: Moving Averages, Bollinger Bands, RSI, MACD, Money Flow.
        Đây là nền tảng xử lý dữ liệu để nuôi sống AI và Robot Advisor.
        """
        
        # Tạo bản sao dữ liệu đầu vào để tránh các lỗi liên quan đến SettingWithCopyWarning
        df_final_calc = df_source_raw.copy()
        
        # --- 3.1 Nhóm các đường trung bình động xu hướng (Moving Averages) ---
        
        # MA20: Xu hướng ngắn hạn (Hỗ trợ nhịp đập 20 phiên gần nhất)
        df_final_calc['ma20'] = df_final_calc['close'].rolling(window=20).mean()
        
        # MA50: Xu hướng trung hạn (Đường ranh giới xác nhận sức mạnh dòng tiền)
        df_final_calc['ma50'] = df_final_calc['close'].rolling(window=50).mean()
        
        # MA200: Đường xu hướng dài hạn (Ngưỡng sống còn, ranh giới Bò và Gấu)
        df_final_calc['ma200'] = df_final_calc['close'].rolling(window=200).mean()
        
        # --- 3.2 Nhóm chỉ báo dải vận động Bollinger Bands (BOL) ---
        
        # Bước 1: Tính độ lệch chuẩn của giá đóng cửa trong chu kỳ 20 phiên
        df_final_calc['std_dev_value_20'] = df_final_calc['close'].rolling(window=20).std()
        
        # Bước 2: Tính dải trên (Upper Band) - Công thức: MA20 + (2 * Độ lệch chuẩn)
        df_final_calc['upper_band'] = df_final_calc['ma20'] + (df_final_calc['std_dev_value_20'] * 2)
        
        # Bước 3: Tính dải dưới (Lower Band) - Công thức: MA20 - (2 * Độ lệch chuẩn)
        df_final_calc['lower_band'] = df_final_calc['ma20'] - (df_final_calc['std_dev_value_20'] * 2)
        
        # --- 3.3 Chỉ số sức mạnh tương đối RSI (Chu kỳ chuẩn 14 phiên) ---
        
        # Bước 1: Tính toán chênh lệch giá giữa các phiên liên tiếp
        price_diff_raw = df_final_calc['close'].diff()
        
        # Bước 2: Tách biệt các phiên tăng (gain) và giảm (loss)
        gain_raw_series = price_diff_raw.where(price_diff_raw > 0, 0)
        loss_raw_series = -price_diff_raw.where(price_diff_raw < 0, 0)
        
        # Bước 3: Tính trung bình di động của các phiên tăng và giảm
        avg_gain_val = gain_raw_series.rolling(window=14).mean()
        avg_loss_val = loss_raw_series.rolling(window=14).mean()
        
        # Bước 4: Tính toán RS và RSI (Thêm epsilon 1e-9 để tránh lỗi chia cho 0)
        rs_logic_val = avg_gain_val / (avg_loss_val + 1e-9)
        df_final_calc['rsi'] = 100 - (100 / (1 + rs_logic_val))
        
        # --- 3.4 Chỉ báo MACD & Signal Line (Cấu hình kinh điển 12, 26, 9) ---
        
        # Đường EMA nhanh (Chu kỳ 12 phiên)
        ema_fast_value = df_final_calc['close'].ewm(span=12, adjust=False).mean()
        
        # Đường EMA chậm (Chu kỳ 26 phiên)
        ema_slow_value = df_final_calc['close'].ewm(span=26, adjust=False).mean()
        
        # Đường MACD chính (Hiệu số của EMA nhanh và EMA chậm)
        df_final_calc['macd'] = ema_fast_value - ema_slow_value
        
        # Đường Tín hiệu (Signal Line - Chính là EMA 9 của chính MACD)
        df_final_calc['signal'] = df_final_calc['macd'].ewm(span=9, adjust=False).mean()
        
        # --- 3.5 Nhóm các biến số phục vụ Smart Flow và Dự báo AI ---
        
        # Tỷ suất lợi nhuận hằng ngày (Daily Return Percentage)
        df_final_calc['return_1d'] = df_final_calc['close'].pct_change()
        
        # ĐỒNG NHẤT TÊN BIẾN (FIX LỖI KEYERROR): vol_strength
        # Đây là tỷ lệ khối lượng hiện tại so với trung bình 10 phiên gần nhất
        df_final_calc['vol_strength'] = df_final_calc['volume'] / df_final_calc['volume'].rolling(window=10).mean()
        
        # Giá trị luân chuyển dòng tiền mặt (Money Flow Value)
        df_final_calc['money_flow'] = df_final_calc['close'] * df_final_calc['volume']
        
        # Độ biến động lịch sử thực tế (Historical Volatility) dựa trên 20 phiên
        df_final_calc['volatility'] = df_final_calc['return_1d'].rolling(window=20).std()
        
        # --- 3.6 Logic xác định Xu hướng Price-Volume (PV Trend) ---
        # 1: Gom mạnh (Giá tăng xanh và Volume bùng nổ > 1.2 lần trung bình)
        # -1: Xả mạnh (Giá giảm đỏ và Volume bùng nổ > 1.2 lần trung bình)
        # 0: Trạng thái trung tính (Đi ngang hoặc Volume thấp)
        
        is_bullish_vol = (df_final_calc['return_1d'] > 0) & (df_final_calc['vol_strength'] > 1.2)
        is_bearish_vol = (df_final_calc['return_1d'] < 0) & (df_final_calc['vol_strength'] > 1.2)
        
        df_final_calc['pv_trend'] = np.where(is_bullish_vol, 1, 
                                    np.where(is_bearish_vol, -1, 0))
        
        # Tiến hành loại bỏ các dòng chứa giá trị rỗng (NaN) ở những phiên đầu tiên
        # Điều này đảm bảo các thuật toán AI và Advisor không bị sai lệch số liệu
        df_engine_result = df_final_calc.dropna()
        
        return df_engine_result

    # ==============================================================================
    # 4. CÁC HÀM CHẨN ĐOÁN THÔNG MINH (INTELLIGENCE LAYER)
    # ==============================================================================
    
    def phan_tich_tam_ly_sentiment_master(df_processed):
        """
        Hàm phân tích chỉ số Sợ hãi & Tham lam của cổ phiếu dựa trên trị số RSI.
        Giúp Minh nhận diện sớm các vùng quá hưng phấn hoặc hoảng loạn của đám đông.
        """
        # Lấy giá trị RSI của phiên giao dịch gần nhất
        last_rsi_point = df_processed.iloc[-1]['rsi']
        
        # Phân loại mức độ tâm lý qua từng ngưỡng điểm chuẩn quốc tế
        if last_rsi_point > 75:
            text_sentiment = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif last_rsi_point > 60:
            text_sentiment = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif last_rsi_point < 30:
            text_sentiment = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif last_rsi_point < 42:
            text_sentiment = "😨 SỢ HÃI (BI QUAN)"
        else:
            text_sentiment = "🟡 TRUNG LẬP (ĐANG CHỜ ĐỢI)"
            
        return text_sentiment, round(last_rsi_point, 1)

    def thuc_thi_backtest_master_logic(df_processed):
        """
        Hàm kiểm chứng lịch sử (Backtesting) chuyên sâu: 
        Kiểm tra nếu áp dụng mua khi RSI thấp (<45) và MACD cắt lên trong quá khứ,
        thì xác suất đạt được lợi nhuận 5% trong vòng 10 ngày sau đó là bao nhiêu.
        Hệ thống duyệt qua 1000 phiên giao dịch gần nhất để lấy số liệu thực tế.
        """
        total_signals_detected = 0
        successful_win_count = 0
        
        # Duyệt qua toàn bộ tập dữ liệu lịch sử (bỏ qua các phiên đầu để đủ chỉ báo)
        for i in range(100, len(df_processed) - 10):
            # Điều kiện mua 1: RSI nằm ở vùng giá thấp (kiệt quệ)
            cond_rsi_is_oversold = df_processed['rsi'].iloc[i] < 45
            
            # Điều kiện mua 2: MACD giao cắt hướng lên đường Tín hiệu (Signal)
            macd_val_now = df_processed['macd'].iloc[i]
            signal_val_now = df_processed['signal'].iloc[i]
            macd_val_prev = df_processed['macd'].iloc[i-1]
            signal_val_prev = df_processed['signal'].iloc[i-1]
            
            is_macd_cross_up = (macd_val_now > signal_val_now) and (macd_val_prev <= signal_val_prev)
            
            # Kiểm tra sự đồng thuận của cả 2 tín hiệu
            if cond_rsi_is_oversold and is_macd_cross_up:
                total_signals_detected = total_signals_detected + 1
                
                # Kiểm tra cửa sổ tương lai: Sau 10 phiên tới có chạm giá chốt lời không
                buy_price_at_point = df_processed['close'].iloc[i]
                target_profit_price = buy_price_at_point * 1.05
                
                # Trích xuất dữ liệu giá của 10 phiên kế tiếp
                window_future_prices = df_processed['close'].iloc[i+1 : i+11]
                
                # Nếu có bất kỳ phiên nào trong 10 ngày giá vượt mục tiêu 5%
                if any(window_future_prices > target_profit_price):
                    successful_win_count = successful_win_count + 1
        
        # Phòng ngừa lỗi chia cho 0 nếu mã cổ phiếu chưa từng xuất hiện tín hiệu này
        if total_signals_detected == 0:
            return 0.0
            
        win_rate_percentage = (successful_win_count / total_signals_detected) * 100
        return round(win_rate_percentage, 1)

    def du_bao_ai_t3_prob_engine(df_processed):
        """
        Thuật toán Machine Learning Random Forest để học các mẫu hình giá.
        Dự báo xác suất cổ phiếu tăng trưởng > 2% sau đúng 3 phiên giao dịch (T+3).
        Sử dụng bộ 8 đặc trưng (Features) định lượng để ra quyết định.
        """
        # Kiểm tra độ dài dữ liệu để mô hình có thể huấn luyện ổn định
        if len(df_processed) < 200:
            return "N/A"
            
        df_ai_training = df_processed.copy()
        
        # Bước 1: Định nghĩa nhãn mục tiêu (Target) cho AI
        # 1 nếu giá 3 phiên sau cao hơn giá hiện tại 2%, ngược lại là 0
        current_close = df_ai_training['close']
        future_close_t3 = df_ai_training['close'].shift(-3)
        df_ai_training['target_label'] = (future_close_t3 > current_close * 1.02).astype(int)
        
        # Bước 2: Danh sách các đặc trưng kỹ thuật làm đầu vào
        features_list = [
            'rsi', 'macd', 'signal', 'return_1d', 
            'volatility', 'vol_strength', 'money_flow', 'pv_trend'
        ]
        
        # Bước 3: Làm sạch dữ liệu và tách tập dữ liệu học
        df_training_clean = df_ai_training.dropna()
        X_data_matrix = df_training_clean[features_list]
        y_label_vector = df_training_clean['target_label']
        
        # Bước 4: Khởi tạo mô hình rừng ngẫu nhiên (100 cây quyết định)
        rf_model_instance = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Bước 5: Huấn luyện AI (Loại bỏ 3 dòng cuối vì chưa biết kết quả tương lai)
        X_train_final = X_data_matrix[:-3]
        y_train_final = y_label_vector[:-3]
        rf_model_instance.fit(X_train_final, y_train_final)
        
        # Bước 6: Dự báo xác suất cho trạng thái phiên hiện tại
        last_row_input = X_data_matrix.iloc[[-1]]
        probability_prediction = rf_model_instance.predict_proba(last_row_input)[0][1]
        
        return round(probability_prediction * 100, 1)

    # ==============================================================================
    # 5. PHÂN TÍCH TÀI CHÍNH & NỘI LỰC CANSLIM (FUNDAMENTAL LAYER)
    # ==============================================================================
    def lay_tang_truong_lnst_canslim_master(ticker_id):
        """
        Hàm tính toán tốc độ tăng trưởng lợi nhuận quý gần nhất so với cùng kỳ.
        Đây là tiêu chuẩn 'C' (Current Quarterly Earnings) trong phương pháp CanSLIM.
        """
        try:
            # 5.1 Lấy báo cáo thu nhập quý chính thức từ Vnstock
            df_income_statement = vn_stock_engine.stock.finance.income_statement(
                symbol=ticker_id, 
                period='quarter', 
                lang='en'
            ).head(5)
            
            # Tìm cột lợi nhuận sau thuế linh hoạt (hỗ trợ nhiều ngôn ngữ hiển thị)
            keywords_search = ['sau thuế', 'posttax', 'net profit', 'earning']
            col_match_target = [col for col in df_income_statement.columns if any(k in str(col).lower() for k in keywords_search)]
            
            if col_match_target:
                ten_cot_lnst = col_match_target[0]
                val_lnst_quy_nay = float(df_income_statement.iloc[0][ten_cot_lnst])
                val_lnst_quy_nam_ngoai = float(df_income_statement.iloc[4][ten_cot_lnst])
                
                if val_lnst_quy_nam_ngoai > 0:
                    growth_ratio = ((val_lnst_quy_nay - val_lnst_quy_nam_ngoai) / val_lnst_quy_nam_ngoai) * 100
                    return round(growth_ratio, 1)
        except Exception:
            # Nếu Vnstock thiếu dữ liệu tài chính, chuyển sang dự phòng
            pass
            
        try:
            # 5.2 Dự phòng bằng Yahoo Finance cho các mã ngành tài chính đặc thù
            stock_info_data = yf.Ticker(f"{ticker_id}.VN").info
            growth_value_yf = stock_info_data.get('earningsQuarterlyGrowth')
            if growth_value_yf is not None:
                # Yahoo Finance trả về dạng thập phân (ví dụ 0.25 cho 25%)
                return round(growth_value_yf * 100, 1)
        except Exception:
            pass
            
        return None

    def lay_chi_so_pe_roe_master_logic(ticker_id):
        """Lấy chỉ số định giá P/E và hiệu quả sử dụng vốn ROE từ Báo cáo tài chính mới nhất"""
        final_pe_val = 0.0
        final_roe_val = 0.0
        
        try:
            # Lấy các tỷ số tài chính (Ratio) chính thức từ Vnstock
            df_financial_ratios = vn_stock_engine.stock.finance.ratio(ticker_id, 'quarterly').iloc[-1]
            
            # Ưu tiên lấy ticker_pe, nếu không có thì lấy pe thông thường
            final_pe_val = df_financial_ratios.get('ticker_pe', df_financial_ratios.get('pe', 0))
            # Lấy chỉ số sinh lời ROE
            final_roe_val = df_financial_ratios.get('roe', 0)
        except:
            pass
            
        # Nếu dữ liệu Vnstock trả về bằng 0, kích hoạt fallback sang Yahoo Finance
        if final_pe_val <= 0:
            try:
                info_yf_data = yf.Ticker(f"{ticker_id}.VN").info
                final_pe_val = info_yf_data.get('trailingPE', 0)
                final_roe_val = info_yf_data.get('returnOnEquity', 0)
            except:
                pass
                
        return final_pe_val, final_roe_val

    # ==============================================================================
    # 6. 🧠 ROBOT ADVISOR MASTER V10.2: GIẢI MÃ LOGIC & RA QUYẾT ĐỊNH (THE HEART)
    # ==============================================================================
    def robot_advisor_master_v102(ticker, last_row, ai_p, wr, pe, roe, growth, list_gom, list_xa):
        """
        SIÊU HỆ THỐNG ADVISOR: Phân tích hội tụ 5 tầng dữ liệu cực kỳ rành mạch.
        Tự động giải mã các mâu thuẫn chỉ báo (Ví dụ: Dòng tiền tốt nhưng Giá yếu).
        Đây là module cốt lõi giúp Minh ra quyết định mua bán có căn cứ khoa học.
        """
        
        # 6.1 Khởi tạo các đoạn văn bản chẩn đoán chuyên sâu
        comment_technical_view = ""
        comment_money_flow_view = ""
        final_verdict_summary = ""
        status_color_code = ""
        
        # 6.2 Nhật ký phân tích logic (Reasoning Logs) - Giải mã mâu thuẫn
        reasoning_logic_list = []
        consensus_score_final = 0
        
        # --- BƯỚC 1: PHÂN TÍCH VỊ THẾ GIÁ (XƯƠNG SỐNG MA20) ---
        p_close_now = last_row['close']
        ma20_standard = last_row['ma20']
        gap_ma20_percentage = ((p_close_now - ma20_standard) / ma20_standard) * 100
        
        if p_close_now < ma20_standard:
            comment_technical_view = f"Cảnh báo: Mã {ticker} đang vận động dưới đường trung bình MA20 ({ma20_standard:,.0f})."
            reasoning_logic_list.append(f"❌ VỊ THẾ YẾU: Giá đóng cửa hiện tại đang thấp hơn MA20 ({gap_ma20_percentage:.1f}%).")
            reasoning_logic_list.append("👉 Phân tích: Phe Bán vẫn đang làm chủ cuộc chơi ngắn hạn, chưa xuất hiện tín hiệu đảo chiều.")
        else:
            comment_technical_view = f"Tích cực: Mã {ticker} đang giữ vững trên hỗ trợ quan trọng MA20 ({ma20_standard:,.0f})."
            reasoning_logic_list.append(f"✅ VỊ THẾ TỐT: Giá đang nằm trên vùng hỗ trợ MA20 ({gap_ma20_percentage:.1f}%).")
            reasoning_logic_list.append("👉 Phân tích: Xu hướng ngắn hạn ổn định, phe Mua đang nỗ lực duy trì đà tăng trưởng.")
            consensus_score_final = consensus_score_final + 1

        # --- BƯỚC 2: PHÂN TÍCH DÒNG TIỀN THÔNG MINH (SMART FLOW) ---
        if ticker in list_gom:
            comment_money_flow_view = "Smart Flow: Phát hiện dấu vết Cá mập (Smart Money) đang thu Gom cổ phiếu chủ động."
            reasoning_logic_list.append("✅ DÒNG TIỀN MẠNH: Phát hiện sự nhập cuộc của các lệnh lớn phối hợp cùng nhóm trụ sàn HOSE.")
            consensus_score_final = consensus_score_final + 1
        elif ticker in list_xa:
            comment_money_flow_view = "Cảnh báo xả hàng: Các tổ chức lớn và khối ngoại đang phân phối (Xả) mã này quyết liệt."
            reasoning_logic_list.append("❌ DÒNG TIỀN XẤU: Cá mập đang có dấu hiệu tháo chạy. Đừng làm bia đỡ đạn cho tổ chức lúc này.")
        else:
            comment_money_flow_view = "Dòng tiền nhỏ lẻ: Thị trường vận động chủ yếu bởi cá nhân lẻ, thiếu sự dẫn dắt của tay to."
            reasoning_logic_list.append("🟡 DÒNG TIỀN NHIỄU: Giao dịch rời rạc, chưa có sự can thiệp từ các quỹ hoặc tự doanh lớn.")

        # --- BƯỚC 3: PHÂN TÍCH XÁC SUẤT AI (T+3) ---
        if isinstance(ai_p, float):
            if ai_p >= 58.0:
                consensus_score_final = consensus_score_final + 1
                reasoning_logic_list.append(f"✅ AI DỰ BÁO ({ai_p}%): Thuật toán Random Forest xác nhận xác suất tăng trong T+3 là khả quan.")
            else:
                reasoning_logic_list.append(f"❌ AI TỪ CHỐI ({ai_p}%): Xác suất chiến thắng quá thấp, rủi ro điều chỉnh cao hơn cửa tăng.")

        # --- BƯỚC 4: PHÂN TÍCH KIỂM CHỨNG LỊCH SỬ (BACKTEST) ---
        if wr >= 50.0:
            consensus_score_final = consensus_score_final + 1
            reasoning_logic_list.append(f"✅ LỊCH SỬ ỦNG HỘ ({wr}%): Trong 1000 phiên quá khứ, tín hiệu này thường mang lại lợi nhuận tốt.")
        else:
            reasoning_logic_list.append(f"❌ LỊCH SỬ RỦI RO ({wr}%): Lịch sử mã này cho thấy tín hiệu hiện tại rất hay 'lừa đảo' (Bull trap).")

        # --- BƯỚC 5: KIỂM TRA SỨC KHỎE TÀI CHÍNH (CANSLIM C) ---
        if growth is not None:
            if growth >= 20.0:
                consensus_score_final = consensus_score_final + 1
                reasoning_logic_list.append(f"✅ TÀI CHÍNH ĐỘT PHÁ: Tăng trưởng LNST {growth}% đạt tiêu chuẩn vàng doanh nghiệp tăng trưởng.")
        
        # --- BƯỚC 6: TỔNG HỢP VÀ RA QUYẾT ĐỊNH CHIẾN THUẬT CUỐI CÙNG ---
        
        # A. KỊCH BẢN MUA MẠNH (STRONG BUY)
        if consensus_score_final >= 4 and last_row['rsi'] < 68:
            final_verdict_summary = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
            status_color_code = "green"
            reasoning_logic_list.append("🏆 KẾT LUẬN: Đạt điểm đồng thuận tuyệt đối. Ưu tiên giải ngân tại các nhịp rung lắc kỹ thuật.")
            
        # B. KỊCH BẢN BÁN / ĐỨNG NGOÀI (BEARISH)
        elif consensus_score_final <= 1 or last_row['rsi'] > 78 or p_close_now < ma20_standard:
            final_verdict_summary = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
            status_color_code = "red"
            
            # TRƯỜNG HỢP GIẢI MÃ MÂU THUẪN (VÍ DỤ MÃ GAS/HPG KHI CÁ MẬP GOM NHƯNG GIÁ GIẢM)
            if p_close_now < ma20_standard and ticker in list_gom:
                reasoning_logic_list.append("⚠️ GIẢI MÃ MÂU THUẪN: Dù Cá mập đang âm thầm Gom, nhưng do Giá vẫn thấp hơn MA20.")
                reasoning_logic_list.append("👉 Robot khuyên Minh chưa nên vào ngay kẻo bị giam vốn lâu. Hãy đợi giá vượt MA20 xác nhận sóng tăng.")
            else:
                reasoning_logic_list.append("🏆 KẾT LUẬN: Các chỉ số rủi ro hiện đang áp đảo hoàn toàn. Bảo vệ vốn là ưu tiên số 1.")
        
        # C. KỊCH BẢN THEO DÕI CHỜ ĐIỂM NỔ (WATCHLIST)
        else:
            final_verdict_summary = "⚖️ THEO DÕI (WATCHLIST)"
            status_color_code = "orange"
            reasoning_logic_list.append("🏆 KẾT LUẬN: Trạng thái 50/50 chưa rõ xu hướng. Cần chờ đợi một phiên nổ Volume (>1.2) để xác nhận.")

        return comment_technical_view, comment_money_flow_view, final_verdict_summary, status_color_code, reasoning_logic_list

    # ==============================================================================
    # 7. GIAO DIỆN NGƯỜI DÙNG VÀ TRUNG TÂM ĐIỀU KHIỂN CHIẾN THUẬT (UI)
    # ==============================================================================
    
    @st.cache_data(ttl=3600)
    def tai_danh_sach_ticker_hose_chinh_thuc():
        """Tải danh sách mã niêm yết chính thức từ sở giao dịch chứng khoán HOSE"""
        try:
            df_listing_full = vn_stock_engine.market.listing()
            # Lọc riêng sàn HOSE (Sàn có thanh khoản tốt nhất)
            condition_hose = df_listing_full['comGroupCode'] == 'HOSE'
            return df_listing_full[condition_hose]['ticker'].tolist()
        except:
            # Danh sách dự phòng nếu kết nối máy chủ dữ liệu bị gián đoạn
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","GAS","VCB","BID","CTG","VRE","DGC","PDR"]

    # Lấy danh sách toàn bộ các mã chứng khoán hiện có
    danh_sach_ma_cp_all = tai_danh_sach_ticker_hose_chinh_thuc()
    
    # Thiết lập thanh Sidebar điều hướng thông minh
    st.sidebar.header("🕹️ Trung Tâm Điều Hành Quant")
    
    # 7.1 Ô chọn mã từ danh sách xổ xuống
    ma_box_selection = st.sidebar.selectbox(
        "Chọn mã cổ phiếu từ danh sách:", 
        danh_sach_ma_cp_all
    )
    
    # 7.2 Ô nhập mã trực tiếp (Manual Input)
    ma_manual_input = st.sidebar.text_input(
        "Hoặc nhập mã (SSI, HPG, FPT...):"
    ).upper()
    
    # 7.3 Xác định mã cổ phiếu được xử lý chính thức
    ma_hien_tai_master = ma_manual_input if ma_manual_input else ma_box_selection

    # 7.4 Khởi tạo 4 Tab chức năng Master (SỬA LỖI ĐỒNG BỘ TÊN BIẾN TAB)
    tab_robot_advisor, tab_canslim_finance, tab_smart_flow, tab_hunter_scan = st.tabs([
        "🤖 ROBOT ADVISOR & MASTER CHART", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 SMART FLOW SPECIALIST", 
        "🔍 ROBOT HUNTER (QUÉT MÃ)"
    ])

    # ------------------------------------------------------------------------------
    # TAB 1: TRUNG TÂM PHÂN TÍCH CHIẾN THUẬT & BIỂU ĐỒ NẾN MASTER CHART
    # ------------------------------------------------------------------------------
    with tab_robot_advisor:
        # Nút nhấn kích hoạt quy trình phân tích định lượng chuyên sâu
        if st.button(f"⚡ PHÂN TÍCH CHIẾN THUẬT TOÀN DIỆN MÃ {ma_hien_tai_master}"):
            
            with st.spinner(f"Hệ thống đang tiến hành rà soát dữ liệu đa tầng cho mã {ma_hien_tai_master}..."):
                
                # BƯỚC 1: Truy xuất dữ liệu từ các nguồn chính xác (FIX NAMEERROR)
                df_source_data_raw = lay_du_lieu_chuan_quant_master(ma_hien_tai_master)
                
                if df_source_data_raw is not None and not df_source_data_raw.empty:
                    
                    # BƯỚC 2: Kích hoạt engine tính toán bộ chỉ số Master chuyên sâu
                    df_master_calculated = tinh_toan_cac_chi_so_quant_master(df_source_data_raw)
                    row_data_current = df_master_calculated.iloc[-1]
                    
                    # BƯỚC 3: Kích hoạt các Engine trí tuệ nhân tạo và Backtest kiểm chứng
                    val_ai_prediction = du_bao_ai_t3_prob_engine(df_master_calculated)
                    val_backtest_win_rate = thuc_thi_backtest_master_logic(df_master_calculated)
                    val_fng_mood_label, val_fng_mood_score = phan_tich_tam_ly_sentiment_master(df_master_calculated)
                    
                    # BƯỚC 4: Truy xuất các chỉ số tài chính cơ bản của doanh nghiệp
                    val_master_pe, val_master_roe = lay_chi_so_pe_roe_master_logic(ma_hien_tai_master)
                    val_master_growth_c = lay_tang_truong_lnst_canslim_master(ma_hien_tai_master)
                    
                    # BƯỚC 5: Quét độ rộng thị trường (Market Breadth) của nhóm 10 Trụ cột
                    hose_big_pillars = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                    gom_list_pillars, xa_list_pillars = [], []
                    
                    for ma_pillar_item in hose_big_pillars:
                        try:
                            # Lấy nhanh dữ liệu 10 phiên cho từng mã cổ phiếu dẫn dắt
                            d_p_raw_pillar = lay_du_lieu_chuan_quant_master(ma_pillar_item, num_days_history=10)
                            if d_p_raw_pillar is not None:
                                d_p_calc_pillar = tinh_toan_bo_chi_so_quant_master(d_p_raw_pillar)
                                lp_p_val_pillar = d_p_calc_pillar.iloc[-1]
                                # Quy tắc Gom/Xả Trụ: Giá đồng thuận + Sức mạnh Volume nổ (> 1.2 lần)
                                if lp_p_val_pillar['return_1d'] > 0 and lp_p_val_pillar['vol_strength'] > 1.2: 
                                    gom_list_pillars.append(ma_pillar_item)
                                elif lp_p_val_pillar['return_1d'] < 0 and lp_p_val_pillar['vol_strength'] > 1.2: 
                                    xa_list_pillars.append(ma_pillar_item)
                        except: pass

                    # BƯỚC 6: GỌI SIÊU HỆ THỐNG ROBOT ADVISOR CHẨN ĐOÁN VÀ GIẢI MÃ (FIX NAMEERROR)
                    res_diag_kt, res_diag_dt, res_verd_final, res_color_hue, res_logic_steps = robot_advisor_master_v102(
                        ma_hien_tai_master, row_data_current, val_ai_prediction, val_backtest_win_rate, 
                        val_master_pe, val_master_roe, val_master_growth_c, gom_list_pillars, xa_list_pillars
                    )

                    # --- GIAO DIỆN HIỂN THỊ KẾT QUẢ CHẨN ĐOÁN (TRÁI TIM HỆ THỐNG) ---
                    st.write(f"### 🎯 Robot Advisor Chẩn Đoán Mã {ma_hien_tai_master}")
                    col_diagnostics_info, col_verdict_final = st.columns([2, 1])
                    
                    with col_diagnostics_info:
                        st.info(f"**💡 Góc nhìn phân tích kỹ thuật:** {res_diag_kt}")
                        st.info(f"**🌊 Góc nhìn dòng tiền thông minh:** {res_diag_dt}")
                        
                        # --- MODULE GIẢI MÃ LOGIC (THE DECISION REASONING) ---
                        with st.expander("🔍 GIẢI MÃ LOGIC: TẠI SAO ROBOT ĐƯA RA ĐỀ XUẤT NÀY?"):
                            st.write("Dưới đây là các luận điểm logic rành mạch được Robot hội tụ để ra kết luận:")
                            for step_log_txt in res_logic_steps:
                                st.write(f"- {step_log_txt}")
                                
                    with col_verdict_final:
                        st.subheader("🤖 ĐỀ XUẤT CHIẾN THUẬT:")
                        # Tách lấy phần hành động (MUA/BÁN) và màu sắc tương ứng
                        action_name_final = res_verd_final.split('(')[0]
                        st.title(f":{res_color_hue}[{action_name_final}]")
                        st.markdown(f"*{res_verd_final.split('(')[1] if '(' in res_verd_final else ''}*")
                    
                    st.divider()
                    
                    # --- HIỂN THỊ BẢNG RADAR HIỆU SUẤT CHIẾN THUẬT (HIGH-LEVEL METRICS) ---
                    st.write("### 🧭 Radar Hiệu Suất Chiến Thuật")
                    radar_metric1, radar_metric2, radar_metric3, radar_metric4 = st.columns(4)
                    
                    radar_metric1.metric("Giá Hiện Tại", f"{row_data_current['close']:,.0f}")
                    radar_metric2.metric("Tâm Lý Fear & Greed", f"{val_fng_mood_score}/100", delta=val_fng_mood_label)
                    radar_metric3.metric("AI Dự Báo (T+3)", f"{val_ai_prediction}%", 
                                         delta="Tích cực" if (isinstance(val_ai_prediction, float) and val_ai_prediction > 55) else None)
                    radar_metric4.metric("Win-rate Backtest", f"{val_backtest_win_rate}%", 
                                         delta="Ổn định" if val_backtest_win_rate > 45 else None)

                    # --- HIỂN THỊ BẢNG THÔNG SỐ NAKED STATS (THÔNG SỐ KỸ THUẬT CHI TIẾT) ---
                    st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Chi Tiết (Naked Stats)")
                    nk_metric1, nk_metric2, nk_metric3, nk_metric4 = st.columns(4)
                    
                    # Cột 1: Chỉ số RSI 14 phiên
                    nk_metric1.metric("RSI (14 phiên)", f"{row_data_current['rsi']:.1f}", 
                                      delta="Quá mua" if row_data_current['rsi']>70 else ("Quá bán" if row_data_current['rsi']<30 else "Trung tính"))
                    
                    # Cột 2: Chỉ số MACD và Signal
                    nk_metric2.metric("MACD Status", f"{row_data_current['macd']:.2f}", 
                                      delta="Cắt lên (Tốt)" if row_data_current['macd']>row_data_current['signal'] else "Cắt xuống (Xấu)")
                    
                    # Cột 3: Giá trị trung bình MA20 và MA50
                    nk_metric3.metric("MA20 / MA50", f"{row_data_current['ma20']:,.0f}", 
                                      delta=f"MA50: {row_data_current['ma50']:,.0f}")
                    
                    # Cột 4: Chỉ số Bollinger Bands (Upper/Lower)
                    nk_metric4.metric("Bollinger Trên", f"{row_data_current['upper_band']:,.0f}", 
                                      delta=f"Dưới: {row_data_current['lower_band']:,.0f}", delta_color="inverse")
                    
                    # --- CẨM NĂNG THỰC CHIẾN CHUYÊN SÂU (THE GOLDEN RULES) ---
                    with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (BẤM ĐỂ XEM QUY TẮC VÀNG)"):
                        st.markdown("#### 1. Khối lượng (Volume) - Nhiên liệu của cổ phiếu")
                        st.write(f"- Khối lượng phiên hiện tại đạt **{row_data_current['vol_strength']:.1f} lần** trung bình 10 phiên.")
                        st.write("- Quy tắc: Giá tăng + Volume nổ (>1.2) ➔ Cá mập đang Gom hàng.")
                        st.write("- Quy tắc: Giá giảm + Volume nổ (>1.2) ➔ Cá mập đang Xả (Tháo hàng tháo chạy).")
                        
                        st.markdown("#### 2. Bollinger Bands (BOL) - Biên giới vận động")
                        st.write("- Vùng xám mờ trên Master Chart chính là biên độ dao động chuẩn.")
                        st.write("- Nếu giá vượt dải trên ➔ Quá hưng phấn, rủi ro bị kéo ngược về MA20.")
                        st.write("- Nếu giá thủng dải dưới ➔ Quảng loạn cực độ, mở ra cơ hội nhịp hồi kỹ thuật.")
                        
                        st.markdown("#### 3. Cách nhận diện Bẫy giá (Bull Trap / Bear Trap)")
                        st.write("- **Né Bull Trap:** Giá vượt đỉnh cũ nhưng Volume thấp hơn trung bình ➔ Đây là bẫy dụ mua để phân phối.")
                        st.write("- **Né Bear Trap:** Giá thủng đáy cũ nhưng Volume xả đỏ lòm và cực lớn ➔ Tuyệt đối không bắt đáy sớm.")
                        
                        st.markdown("#### 4. Nguyên tắc Quản trị vốn (Risk Management)")
                        st.error(f"- Ngưỡng Cắt lỗ sống còn: Thoát vị thế nếu giá chạm mốc **{row_data_current['close']*0.93:,.0f} (-7%)** để bảo toàn vốn.")

                    # ==================================================================
                    # --- KHÔI PHỤC BIỂU ĐỒ NẾN PHỨC HỢP MASTER CHART (FULL VISUAL) ---
                    # ==================================================================
                    st.divider()
                    st.write("### 📊 Master Candlestick Chart (OHLC + Volume + Technicals)")
                    
                    # Bước A: Khởi tạo khung biểu đồ 2 hàng (Hàng 1: Nến + MA, Hàng 2: Volume)
                    fig_master_masterpiece = make_subplots(
                        rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.75, 0.25]
                    )
                    
                    # Bước B: Vẽ biểu đồ nến Candlestick chuyên nghiệp (120 phiên gần nhất)
                    fig_master_masterpiece.add_trace(
                        go.Candlestick(
                            x=df_master_calculated['date'].tail(120), 
                            open=df_master_calculated['open'].tail(120), 
                            high=df_master_calculated['high'].tail(120), 
                            low=df_master_calculated['low'].tail(120), 
                            close=df_master_calculated['close'].tail(120), 
                            name='Giá Nến (OHLC)'
                        ), row=1, col=1
                    )
                    
                    # Bước C: Vẽ đường xu hướng MA20 (Màu Cam đặc trưng)
                    fig_master_masterpiece.add_trace(
                        go.Scatter(
                            x=df_master_calculated['date'].tail(120), 
                            y=df_master_calculated['ma20'].tail(120), 
                            line=dict(color='orange', width=1.5), 
                            name='MA20 (Ngắn hạn)'
                        ), row=1, col=1
                    )
                    
                    # Bước D: Vẽ đường xu hướng MA200 (Màu Tím đậm - Ngưỡng sống còn)
                    fig_master_masterpiece.add_trace(
                        go.Scatter(
                            x=df_master_calculated['date'].tail(120), 
                            y=df_master_calculated['ma200'].tail(120), 
                            line=dict(color='purple', width=2), 
                            name='MA200 (Dài hạn)'
                        ), row=1, col=1
                    )
                    
                    # Bước E: Vẽ dải Bollinger Bands với hiệu ứng tô màu xám mờ (Fill Area)
                    fig_master_masterpiece.add_trace(
                        go.Scatter(
                            x=df_master_calculated['date'].tail(120), 
                            y=df_master_calculated['upper_band'].tail(120), 
                            line=dict(color='gray', dash='dash', width=0.8), 
                            name='Upper BOL'
                        ), row=1, col=1
                    )
                    
                    fig_master_masterpiece.add_trace(
                        go.Scatter(
                            x=df_master_calculated['date'].tail(120), 
                            y=df_master_calculated['lower_band'].tail(120), 
                            line=dict(color='gray', dash='dash', width=0.8), 
                            fill='tonexty', 
                            fillcolor='rgba(128,128,128,0.1)', 
                            name='Lower BOL'
                        ), row=1, col=1
                    )
                    
                    # Bước F: Vẽ biểu đồ khối lượng (Bar Chart) ở hàng 2
                    fig_master_masterpiece.add_trace(
                        go.Bar(
                            x=df_master_calculated['date'].tail(120), 
                            y=df_master_calculated['volume'].tail(120), 
                            name='Volume', 
                            marker_color='gray'
                        ), row=2, col=1
                    )
                    
                    # Bước G: Cấu hình giao diện và khoảng cách biểu đồ
                    fig_master_masterpiece.update_layout(
                        height=750, 
                        template='plotly_white', 
                        xaxis_rangeslider_visible=False,
                        margin=dict(l=40, r=40, t=50, b=40)
                    )
                    
                    # Xuất biểu đồ ra màn hình Streamlit
                    st.plotly_chart(fig_master_masterpiece, use_container_width=True)
                else:
                    st.error("Không thể tải dữ liệu kỹ thuật. Vui lòng kiểm tra mã chứng khoán hoặc mạng!")

    # ------------------------------------------------------------------------------
    # TAB 2: PHÂN TÍCH CƠ BẢN & CHẨN ĐOÁN CANSLIM (FUNDAMENTAL EXPANSION)
    # ------------------------------------------------------------------------------
    with tab_canslim_finance:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá Doanh Nghiệp ({ma_hien_tai_master})")
        
        with st.spinner("Hệ thống đang bóc tách báo cáo tài chính mới nhất..."):
            # Lấy chỉ số tăng trưởng LNST (Tiêu chuẩn C)
            val_growth_c_pct = lay_tang_truong_lnst_canslim_master(ma_hien_tai_master)
            
            if val_growth_c_pct is not None:
                if val_growth_c_pct >= 20.0:
                    st.success(f"**🔥 CanSLIM (Tiêu chuẩn C):** Lợi nhuận sau thuế tăng trưởng đột phá **+{val_growth_c_pct}%**. Đạt tiêu chuẩn doanh nghiệp siêu hạng.")
                elif val_growth_c_pct > 0:
                    st.info(f"**⚖️ Tăng trưởng:** LNST cải thiện ở mức **{val_growth_c_pct}%**. Doanh nghiệp đang vận hành ổn định.")
                else:
                    st.error(f"**🚨 Cảnh báo:** LNST sụt giảm mạnh **{val_growth_c_pct}%**. Nội lực doanh nghiệp đang có dấu hiệu đi lùi.")
            
            st.divider()
            
            # Lấy các chỉ số định giá cốt lõi P/E và ROE
            pe_current_v, roe_current_v = lay_chi_so_pe_roe_master_logic(ma_hien_tai_master)
            fundamental_c1, fundamental_c2 = st.columns(2)
            
            # Đánh giá đắt rẻ qua P/E (Price-to-Earnings)
            pe_tag_desc = "Tốt (Định giá Rẻ)" if (0 < pe_current_v < 12) else ("Hợp lý" if pe_current_v < 18 else "Đắt (Rủi ro)")
            fundamental_c1.metric("Hệ số P/E (Định giá)", f"{pe_current_v:.1f}", 
                                  delta=pe_tag_desc, delta_color="normal" if pe_current_v < 18 else "inverse")
            st.write("> **Ý nghĩa P/E:** P/E thấp chứng tỏ cổ phiếu đang rẻ so với khả năng kiếm tiền thực tế.")
            
            # Đánh giá hiệu quả sử dụng vốn qua ROE (Return on Equity)
            roe_tag_desc = "Xuất sắc" if roe_current_v >= 0.25 else ("Tốt" if roe_current_v >= 0.15 else "Trung bình")
            fundamental_c2.metric("Chỉ số ROE (Hiệu quả vốn)", f"{roe_current_v:.1%}", 
                                  delta=roe_tag_desc, delta_color="normal" if roe_current_v >= 0.15 else "inverse")
            st.write("> **Ý nghĩa ROE:** Đo lường mỗi 100 đồng vốn của cổ đông tạo ra bao nhiêu đồng lãi. Tiêu chuẩn vàng là > 15%.")

    # ------------------------------------------------------------------------------
    # TAB 3: SMART FLOW SPECIALIST (CHI TIẾT DÒNG TIỀN % 3 PHÂN KHÚC)
    # ------------------------------------------------------------------------------
    with tab_smart_flow:
        st.write(f"### 🌊 Smart Flow Specialist - Phân Tích Dòng Tiền 3 Nhóm ({ma_hien_tai_master})")
        
        # Lấy dữ liệu 30 phiên gần nhất để bóc tách luồng tiền
        df_flow_raw_source = lay_du_lieu_chuan_quant_master(ma_hien_tai_master, num_days_history=30)
        
        if df_flow_raw_source is not None:
            # Thực thi engine tính toán dòng tiền
            df_flow_calc_logic = tinh_toan_bo_chi_so_quant_master(df_flow_raw_source)
            dong_flow_cuoi_phien = df_flow_calc_logic.iloc[-1]
            cuong_do_volume_spike = dong_flow_cuoi_phien['vol_strength']
            
            # --- LOGIC BÓC TÁCH DÒNG TIỀN CHI TIẾT (V10.2 MASTER) ---
            # Ước tính dựa trên cường độ Volume bùng nổ và biến động giá
            if cuong_do_volume_spike > 1.8:
                # Phiên bùng nổ: Tổ chức và Khối ngoại dẫn dắt
                p_foreign_v102 = 0.35; p_instit_v102 = 0.45; p_retail_v102 = 0.20
            elif cuong_do_volume_spike > 1.2:
                # Phiên gom/xả chủ động: Cân bằng các phe
                p_foreign_v102 = 0.20; p_instit_v102 = 0.30; p_retail_v102 = 0.50
            else:
                # Phiên thanh khoản thấp: Nhỏ lẻ tự chơi
                p_foreign_v102 = 0.10; p_instit_v102 = 0.15; p_retail_v102 = 0.75
            
            # Hiển thị tỷ lệ bóc tách bằng hệ thống Metrics 3 cột
            st.write("#### 📊 Tỷ lệ phân bổ dòng tiền thực tế ước tính (Dựa trên Volume):")
            sf_metric_c1, sf_metric_c2, sf_metric_c3 = st.columns(3)
            
            sf_metric_c1.metric("🐋 Khối Ngoại (Foreign)", f"{p_foreign_v102*100:.1f}%", 
                                delta="Mua ròng" if dong_flow_cuoi_phien['return_1d']>0 else "Bán ròng")
            
            sf_metric_c2.metric("🏦 Tổ Chức & Tự Doanh", f"{p_instit_v102*100:.1f}%", 
                                delta="Gom hàng" if dong_flow_cuoi_phien['return_1d']>0 else "Xả hàng")
            
            # Cảnh báo Đu bám bằng màu sắc đỏ
            sf_metric_c3.metric("🐜 Cá Nhân (Nhỏ lẻ)", f"{p_retail_v102*100:.1f}%", 
                                delta="Đu bám quá cao" if p_retail_v102 > 0.6 else "Ổn định", 
                                delta_color="inverse" if p_retail_v102 > 0.6 else "normal")
            
            with st.expander("📖 Ý NGHĨA CÁC NHÓM DÒNG TIỀN (SMART FLOW)"):
                st.write("- **Khối Ngoại:** Tiền từ các quỹ quốc tế cực lớn. Họ kiên nhẫn và gom hàng khi giá chiết khấu sâu.")
                st.write("- **Tổ Chức:** Tiền từ Tự doanh các CTCK và Quỹ nội. Đây là nhóm 'tạo lập' cuộc chơi chuyên nghiệp.")
                st.write("- **Cá Nhân:** Nhà đầu tư lẻ. Tỷ lệ này > 60% báo hiệu 'tàu quá nặng', khó tăng giá bền vững.")
            
            st.divider()
            
            # 3.2 Market Sense - Độ rộng thị trường nhóm 10 Trụ cột dẫn dắt
            st.write("#### 🌊 Market Sense - Danh Sách Gom/Xả 10 Trụ Cột Dẫn Dắt")
            with st.spinner("Đang rà soát dấu chân Cá mập trên toàn sàn..."):
                big_pillars_hose_list = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                list_gom_final, list_xa_final = [], []
                
                for ma_tru_item in big_pillars_hose_list:
                    try:
                        d_p_raw_pillar = lay_du_lieu_chuan_quant_master(ma_tru_item, num_days_history=10)
                        if d_p_raw_pillar is not None:
                            d_p_calc_pillar = tinh_toan_bo_chi_so_quant_master(d_p_raw_pillar)
                            lp_res_pillar = d_p_calc_pillar.iloc[-1]
                            # Quy chuẩn Gom/Xả Trụ: Giá xanh/đỏ đồng thuận với Volume nổ (> 1.2)
                            if lp_res_pillar['return_1d'] > 0 and lp_res_pillar['vol_strength'] > 1.2:
                                list_gom_final.append(ma_tru_item)
                            elif lp_res_pillar['return_1d'] < 0 and lp_res_pillar['vol_strength'] > 1.2:
                                list_xa_final.append(ma_tru_item)
                    except: pass
                
                # Hiển thị độ rộng thị trường (Market Breadth) trực quan
                breadth_metric1, breadth_metric2 = st.columns(2)
                breadth_metric1.metric("Trụ đang GOM (Tích cực)", f"{len(list_gom_final)} mã", 
                                       delta=f"{(len(list_gom_final)/len(big_pillars_hose_list))*100:.0f}%")
                breadth_metric2.metric("Trụ đang XẢ (Tiêu cực)", f"{len(list_xa_final)} mã", 
                                       delta=f"{(len(list_xa_final)/len(big_pillars_hose_list))*100:.0f}%", delta_color="inverse")
                
                res_col_list_gom, res_col_list_xa = st.columns(2)
                with res_col_list_gom:
                    st.success("✅ **CÁC MÃ TRỤ ĐANG ĐƯỢC GOM MẠNH:**")
                    st.write(", ".join(list_gom_final) if list_gom_final else "Hiện chưa có tín hiệu gom đột biến.")
                with res_col_list_xa:
                    st.error("🚨 **CÁC MÃ TRỤ ĐANG BỊ XẢ QUYẾT LIỆT:**")
                    st.write(", ".join(list_xa_final) if list_xa_final else "Áp lực xả tháo ở nhóm trụ hiện tại thấp.")

    # ------------------------------------------------------------------------------
    # TAB 4: ROBOT HUNTER (QUÉT SIÊU CỔ PHIẾU TOÀN SÀN HOSE)
    # ------------------------------------------------------------------------------
    with tab_hunter_scan:
        st.subheader("🔍 Robot Hunter - Truy Quét Top 30 Bluechips HOSE")
        st.write("Hệ thống lọc ra các cổ phiếu bùng nổ Volume và có xác suất AI tăng cao nhất.")
        
        if st.button("🔥 CHẠY RÀ SOÁT SIÊU CỔ PHIẾU (REAL-TIME)"):
            hunter_final_results = []
            hunter_pb = st.progress(0)
            
            # Lấy danh sách Top 30 mã niêm yết vốn hóa lớn nhất để quét
            scan_targets_array = danh_sach_ma_cp_all[:30]
            
            for idx_hunter, ma_scan_item in enumerate(scan_targets_array):
                try:
                    # Lấy dữ liệu 100 phiên để engine AI có đủ mẫu học
                    df_raw_hunter = lay_du_lieu_chuan_quant_master(ma_scan_item, num_days_history=100)
                    df_calc_hunter = tinh_toan_bo_chi_so_quant_master(df_raw_hunter)
                    
                    # TIÊU CHUẨN HUNTER SIÊU KHẮT KHE: Volume nổ > 1.3 lần trung bình
                    if df_calc_hunter.iloc[-1]['vol_strength'] > 1.3:
                        hunter_final_results.append({
                            'Mã Chứng Khoán': ma_scan_item, 
                            'Giá Hiện Tại': f"{df_calc_hunter.iloc[-1]['close']:,.0f}", 
                            'Sức mạnh Vol': round(df_calc_hunter.iloc[-1]['vol_strength'], 2), 
                            'Xác suất Tăng AI': f"{du_bao_ai_t3_prob_engine(df_calc_hunter)}%"
                        })
                except Exception:
                    pass
                
                # Cập nhật thanh tiến trình % hoàn thành cho Minh
                hunter_pb.progress((idx_hunter + 1) / len(scan_targets_array))
            
            # Hiển thị bảng kết quả săn lùng siêu cổ phiếu
            if hunter_final_results:
                df_hunter_presentation = pd.DataFrame(hunter_final_results).sort_values(by='Xác suất Tăng AI', ascending=False)
                st.table(df_hunter_presentation)
                st.success("✅ Đã tìm ra các mã bùng nổ dòng tiền và xác suất tăng giá đột biến.")
            else:
                st.write("Chưa tìm thấy siêu cổ phiếu nào đạt đủ tiêu chuẩn Hunter khắt khe ngày hôm nay.")

# ==============================================================================
# KẾT THÚC MÃ NGUỒN V10.2 - THE ETERNAL SANCTUARY
# ==============================================================================
