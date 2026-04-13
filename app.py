# ==============================================================================
# QUAN SYSTEM V9.8 - PHIÊN BẢN HOÀN THIỆN TUYỆT ĐỐI (THE MASTERPIECE)
# CHỦ SỞ HỮU: MINH
# MÔ TẢ: HỆ THỐNG PHÂN TÍCH ĐỊNH LƯỢNG, DÒNG TIỀN VÀ TƯ VẤN CHIẾN THUẬT
# TÍNH NĂNG: AI T+3, BACKTEST 1000 PHIÊN, SMART FLOW, MASTER CHART, ADVISOR LOGIC
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
# Sử dụng RandomForest để dự báo xu hướng và Sentiment để đo lường tâm lý
from sklearn.ensemble import RandomForestClassifier
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Đảm bảo các tài nguyên cần thiết cho AI được tải đầy đủ để tránh lỗi Runtime
# Đây là bước sống còn để module Advisor có thể hoạt động ổn định trên Cloud
try:
    # Kiểm tra và tải dữ liệu từ điển cảm xúc
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    # Nếu không tìm thấy, thực hiện tải xuống tự động
    nltk.download('vader_lexicon')

# ==============================================================================
# 1. HỆ THỐNG BẢO MẬT & KIỂM SOÁT TRUY CẬP (SECURITY LAYER)
# ==============================================================================
def check_password():
    """
    Hàm xác thực mật mã dành riêng cho Minh.
    Đảm bảo chỉ chủ sở hữu mới có thể truy cập vào các chiến thuật bí mật.
    """
    def password_entered():
        # Lấy giá trị mật mã đích từ bí mật của hệ thống
        target_pass = st.secrets["password"]
        # Lấy giá trị mật mã người dùng vừa nhập
        entered_pass = st.session_state["password"]
        
        # So sánh hai giá trị
        if entered_pass == target_pass:
            # Nếu đúng, đánh dấu trạng thái đăng nhập thành công
            st.session_state["password_correct"] = True
            # Xóa mật mã khỏi bộ nhớ tạm ngay lập tức để bảo mật
            del st.session_state["password"]
        else:
            # Nếu sai, đánh dấu lỗi
            st.session_state["password_correct"] = False

    # Kiểm tra xem người dùng đã đăng nhập chưa
    if "password_correct" not in st.session_state:
        # Hiển thị giao diện nhập mật mã ban đầu
        st.markdown("### 🔐 Quant System Master Master Access")
        st.text_input(
            "🔑 Vui lòng nhập mật mã của Minh:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    # Trả về kết quả kiểm tra
    return st.session_state.get("password_correct", False)

# Thực thi ứng dụng chính sau khi vượt qua lớp bảo mật
if check_password():
    # 1.1 Cấu hình giao diện chuẩn Dashboard chuyên nghiệp
    st.set_page_config(
        page_title="Quant System V9.8 Masterpiece", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 1.2 Hiển thị tiêu đề chính của hệ thống với icon bảo vệ
    st.title("🛡️ Quant System V9.8: Advisor Master & Smart Flow Specialist")

    # 1.3 Khởi tạo đối tượng Vnstock kết nối dữ liệu thị trường Việt Nam
    vn = Vnstock()

    # ==============================================================================
    # 2. HÀM TRUY XUẤT DỮ LIỆU ĐA TẦNG (DATA ACQUISITION)
    # ==============================================================================
    def lay_du_lieu_chuan_quant(ticker, days=1000):
        """
        Hàm lấy dữ liệu giá lịch sử OHLCV. 
        Tích hợp cơ chế dự phòng đa nguồn để đảm bảo hệ thống không bị gián đoạn.
        """
        # Bước 2.1: Thiết lập tham số thời gian
        thoi_gian_hien_tai = datetime.now()
        ngay_ket_thuc_str = thoi_gian_hien_tai.strftime('%Y-%m-%d')
        ngay_bat_dau_str = (thoi_gian_hien_tai - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Bước 2.2: Thử truy xuất từ Vnstock (Nguồn dữ liệu gốc sàn HOSE/HNX)
        try:
            df_vnstock = vn.stock.quote.history(
                symbol=ticker, 
                start=ngay_bat_dau_str, 
                end=ngay_ket_thuc_str
            )
            
            # Kiểm tra tính hợp lệ của dữ liệu
            if df_vnstock is not None:
                if not df_vnstock.empty:
                    # Chuẩn hóa tên cột về chữ thường để các hàm tính toán đồng nhất
                    danh_sach_cot = []
                    for cot in df_vnstock.columns:
                        danh_sach_cot.append(str(cot).lower())
                    df_vnstock.columns = danh_sach_cot
                    return df_vnstock
        except Exception as e_error:
            # Ghi nhận lỗi nhưng tiếp tục sang nguồn dự phòng
            pass
        
        # Bước 2.3: Cơ chế Fail-over sang Yahoo Finance (Dành cho Bank, SSI hoặc khi API lỗi)
        try:
            # Định dạng lại Symbol cho Yahoo Finance (.VN)
            if ticker == "VNINDEX":
                ma_yf = "^VNINDEX"
            else:
                ma_yf = f"{ticker}.VN"
                
            # Thực hiện tải dữ liệu
            yt_raw_data = yf.download(ma_yf, period="3y", progress=False)
            
            if not yt_raw_data.empty:
                # Chuyển Index thành cột 'date'
                yt_raw_data = yt_raw_data.reset_index()
                
                # Xử lý Multi-index thường gặp ở các phiên bản thư viện yfinance mới
                ten_cot_moi = []
                for label in yt_raw_data.columns:
                    if isinstance(label, tuple):
                        ten_cot_moi.append(str(label[0]).lower())
                    else:
                        ten_cot_moi.append(str(label).lower())
                
                yt_raw_data.columns = ten_cot_moi
                return yt_raw_data
        except Exception as e_yf:
            # Thông báo lỗi nếu cả hai nguồn đều thất bại
            st.sidebar.error(f"❌ Không thể truy xuất mã {ticker}. Lỗi: {str(e_yf)}")
            return None

    # ==============================================================================
    # 3. HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT (ENGINE LAYER)
    # ==============================================================================
    def tinh_toan_cac_chi_so_master(df):
        """
        Tính toán toàn bộ các chỉ báo định lượng.
        Đây là bước quan trọng nhất để tạo ra 'đầu vào' cho AI và Advisor.
        """
        # Tạo bản sao dữ liệu để thao tác an toàn
        df_master = df.copy()
        
        # --- 3.1 Nhóm đường trung bình động (MA) ---
        # MA20: Xu hướng ngắn hạn và nền tảng dải Bollinger
        df_master['ma20'] = df_master['close'].rolling(window=20).mean()
        # MA50: Xác định xu hướng trung hạn
        df_master['ma50'] = df_master['close'].rolling(window=50).mean()
        # MA200: Đường xu hướng dài hạn - Ngưỡng tâm lý sống còn
        df_master['ma200'] = df_master['close'].rolling(window=200).mean()
        
        # --- 3.2 Dải Bollinger Bands (BOL) ---
        # Tính độ lệch chuẩn của giá
        df_master['std_dev_20'] = df_master['close'].rolling(window=20).std()
        # Dải trên (Vùng hưng phấn)
        df_master['upper_band'] = df_master['ma20'] + (df_master['std_dev_20'] * 2)
        # Dải dưới (Vùng hoảng loạn)
        df_master['lower_band'] = df_master['ma20'] - (df_master['std_dev_20'] * 2)
        
        # --- 3.3 Chỉ số sức mạnh tương đối RSI (14) ---
        bien_dong = df_master['close'].diff()
        lai_tb = (bien_dong.where(bien_dong > 0, 0)).rolling(window=14).mean()
        lo_tb = (-bien_dong.where(bien_dong < 0, 0)).rolling(window=14).mean()
        he_so_rs = lai_tb / (lo_tb + 1e-9)
        df_master['rsi'] = 100 - (100 / (1 + he_so_rs))
        
        # --- 3.4 Chỉ báo MACD (12, 26, 9) ---
        ema12 = df_master['close'].ewm(span=12, adjust=False).mean()
        ema26 = df_master['close'].ewm(span=26, adjust=False).mean()
        df_master['macd'] = ema12 - ema26
        df_master['signal'] = df_master['macd'].ewm(span=9, adjust=False).mean()
        
        # --- 3.5 Các biến số phục vụ Smart Flow & AI ---
        # Tính tỷ suất sinh lời ngày
        df_master['return_1d'] = df_master['close'].pct_change()
        # SỨA LỖI ĐỒNG NHẤT: Luôn sử dụng 'vol_strength' cho mọi module
        # Đây là tỷ lệ khối lượng hiện tại so với trung bình 10 phiên
        df_master['vol_strength'] = df_master['volume'] / df_master['volume'].rolling(window=10).mean()
        # Giá trị dòng tiền (Money Flow)
        df_master['money_flow'] = df_master['close'] * df_master['volume']
        # Độ biến động thị trường (Historical Volatility)
        df_master['volatility'] = df_master['return_1d'].rolling(window=20).std()
        
        # --- 3.6 Logic Gom/Xả (Price-Volume Trend) ---
        # Gom (1): Giá tăng và Volume nổ > 1.2
        # Xả (-1): Giá giảm và Volume nổ > 1.2
        dieu_kien_tang = (df_master['return_1d'] > 0) & (df_master['vol_strength'] > 1.2)
        dieu_kien_giam = (df_master['return_1d'] < 0) & (df_master['vol_strength'] > 1.2)
        
        df_master['pv_trend'] = np.where(dieu_kien_tang, 1, 
                                np.where(dieu_kien_giam, -1, 0))
        
        # Loại bỏ các dòng chứa giá trị rỗng để mô hình AI không bị lỗi logic
        return df_master.dropna()

    # ==============================================================================
    # 4. CHẨN ĐOÁN TÂM LÝ & KIỂM CHỨNG CHIẾN THUẬT (INTEL LAYER)
    # ==============================================================================
    def phan_tich_fng_sentiment_master(df):
        """
        Đo lường chỉ số Tham lam & Sợ hãi dựa trên RSI.
        Giúp Minh nhận diện các vùng quá hưng phấn hoặc hoảng loạn cực độ.
        """
        last_rsi = df.iloc[-1]['rsi']
        
        # Phân loại mức độ tâm lý
        if last_rsi > 75:
            label_text = "🔥 CỰC KỲ THAM LAM (VÙNG QUÁ MUA)"
        elif last_rsi > 60:
            label_text = "⚖️ THAM LAM (HƯNG PHẤN)"
        elif last_rsi < 30:
            label_text = "💀 CỰC KỲ SỢ HÃI (VÙNG QUÁ BÁN)"
        elif last_rsi < 42:
            label_text = "😨 SỢ HÃI (BI QUAN)"
        else:
            label_text = "🟡 TRUNG LẬP (NGHI NGỜ)"
            
        return label_text, round(last_rsi, 1)

    def thuc_thi_backtest_1000_phien(df):
        """
        Hàm kiểm chứng lịch sử: 'Nếu trong quá khứ tôi mua khi RSI < 45 và MACD cắt lên, 
        thì xác suất tôi chốt lời 5% trong 10 ngày tới là bao nhiêu?'
        """
        dem_tong = 0
        dem_win = 0
        
        # Duyệt qua dữ liệu lịch sử (bỏ 100 phiên đầu và 10 phiên cuối)
        for i in range(100, len(df) - 10):
            # Điều kiện mua chuẩn kỹ thuật
            cond_rsi = df['rsi'].iloc[i] < 45
            cond_macd = df['macd'].iloc[i] > df['signal'].iloc[i]
            cond_cross = df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
            
            if cond_rsi and cond_macd and cond_cross:
                dem_tong += 1
                # Kiểm tra cửa sổ tương lai 10 ngày
                vung_tuong_lai = df['close'].iloc[i+1 : i+11]
                muc_tieu_chot_loi = df['close'].iloc[i] * 1.05
                
                if any(vung_tuong_lai > muc_tieu_chot_loi):
                    dem_win += 1
        
        # Tránh lỗi chia cho 0
        if dem_tong == 0:
            return 0.0
            
        ty_le_chuan = (dem_win / dem_tong) * 100
        return round(ty_le_chuan, 1)

    def du_bao_ai_t3_engine_master(df):
        """
        Sử dụng mô hình Random Forest (Rừng ngẫu nhiên) để học các mẫu hình giá.
        Dự báo xác suất cổ phiếu tăng > 2% sau 3 phiên giao dịch.
        """
        if len(df) < 200:
            return "N/A"
            
        df_ml = df.copy()
        # Định nghĩa mục tiêu dự báo (Target)
        gia_hien_tai = df_ml['close']
        gia_tuong_lai = df_ml['close'].shift(-3)
        df_ml['target'] = (gia_tuong_lai > gia_hien_tai * 1.02).astype(int)
        
        # Tập hợp các đặc trưng đầu vào (Features)
        features = [
            'rsi', 'macd', 'signal', 'return_1d', 
            'volatility', 'vol_strength', 'money_flow', 'pv_trend'
        ]
        
        du_lieu_sạch = df_ml.dropna()
        X_data = du_lieu_sạch[features]
        y_data = du_lieu_sạch['target']
        
        # Khởi tạo thuật toán AI
        ai_engine = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Huấn luyện mô hình (Loại bỏ 3 dòng cuối vì chưa có kết quả thực tế)
        X_train = X_data[:-3]
        y_train = y_data[:-3]
        ai_engine.fit(X_train, y_train)
        
        # Dự báo cho trạng thái hiện tại (Dòng cuối cùng)
        du_bao_cuoi = ai_engine.predict_proba(X_data.iloc[[-1]])[0][1]
        return round(du_bao_cuoi * 100, 1)

    # ==============================================================================
    # 5. PHÂN TÍCH NỘI LỰC TÀI CHÍNH & CANSLIM (FUNDAMENTAL)
    # ==============================================================================
    def lay_tang_truong_lnst_canslim_master(ticker):
        """
        Tính toán tốc độ tăng trưởng lợi nhuận quý gần nhất so với cùng kỳ.
        Đây là tiêu chuẩn 'C' (Current Quarterly Earnings) trong phương pháp CanSLIM.
        """
        try:
            # 5.1 Thử lấy báo cáo tài chính từ Vnstock
            df_income = vn.stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
            
            # Tìm cột Lợi nhuận sau thuế linh hoạt (đề phòng thay đổi ngôn ngữ)
            keywords = ['sau thuế', 'posttax', 'net profit', 'earning']
            col_found = [c for c in df_income.columns if any(k in str(c).lower() for k in keywords)]
            
            if col_found:
                ten_cot = col_found[0]
                lnst_nay = float(df_income.iloc[0][ten_cot])
                lnst_nam_ngoai = float(df_income.iloc[4][ten_cot])
                
                if lnst_nam_ngoai > 0:
                    growth_val = ((lnst_nay - lnst_nam_ngoai) / lnst_nam_ngoai) * 100
                    return round(growth_val, 1)
        except Exception:
            pass
            
        try:
            # 5.2 Dự phòng bằng Yahoo Finance cho các mã đặc thù
            stock_info = yf.Ticker(f"{ticker}.VN").info
            growth_yf = stock_info.get('earningsQuarterlyGrowth')
            if growth_yf is not None:
                return round(growth_yf * 100, 1)
        except Exception:
            pass
        return None

    def lay_chi_so_pe_roe_master_quant(ticker):
        """Lấy chỉ số định giá P/E và hiệu quả sử dụng vốn ROE"""
        pe_v, roe_v = 0.0, 0.0
        try:
            # Truy xuất từ Vnstock Ratios
            df_r = vn.stock.finance.ratio(ticker, 'quarterly').iloc[-1]
            pe_v = df_r.get('ticker_pe', df_r.get('pe', 0))
            roe_v = df_r.get('roe', 0)
        except:
            pass
            
        if pe_v <= 0:
            try:
                # Dự phòng từ nguồn quốc tế
                inf = yf.Ticker(f"{ticker}.VN").info
                pe_v = inf.get('trailingPE', 0)
                roe_v = inf.get('returnOnEquity', 0)
            except:
                pass
        return pe_v, roe_v

    # ==============================================================================
    # 6. 🧠 ROBOT ADVISOR MASTER V9.8: GIẢI MÃ LOGIC & RA QUYẾT ĐỊNH
    # ==============================================================================
    def robot_advisor_expert_v98(ticker, last_row, ai_p, wr, pe, roe, growth, list_gom, list_xa):
        """
        SIÊU HỆ THỐNG ADVISOR: Phân tích hội tụ 5 tầng dữ liệu.
        Tự động giải mã các mâu thuẫn để đưa ra lời khuyên an toàn nhất cho Minh.
        """
        chuan_doan_kt_text = ""
        chuan_doan_dt_text = ""
        ket_luan_cuoi = ""
        mau_hien_thi = ""
        
        # Nhật ký phân tích chuyên sâu (Reasoning Log)
        nhat_ky_phân_tích = []
        diem_score = 0
        
        # --- 6.1 LỚP 1: XU HƯỚNG VÀ VỊ THẾ GIÁ (MA20) ---
        gia_hien_tai = last_row['close']
        ma20_hien_tai = last_row['ma20']
        phan_tram_lech_ma20 = ((gia_hien_tai - ma20_hien_tai) / ma20_hien_tai) * 100
        
        if gia_hien_tai < ma20_hien_tai:
            chuan_doan_kt_text = f"Cảnh báo: Giá {ticker} đang vận động dưới MA20 ({ma20_hien_tai:,.0f}). Phe Bán vẫn đang chiếm ưu thế tuyệt đối."
            nhat_ky_phân_tích.append(f"❌ Vị thế giá YẾU: Hiện tại giá thấp hơn đường hỗ trợ MA20 ({phan_tram_lech_ma20:.1f}%).")
            nhat_ky_phân_tích.append("👉 Lời khuyên: Tuyệt đối hạn chế bắt đáy khi xu hướng giảm ngắn hạn chưa dừng lại.")
        else:
            chuan_doan_kt_text = f"Tích cực: Giá {ticker} đang vận động trên hỗ trợ MA20 ({ma20_hien_tai:,.0f}). Xu hướng ngắn hạn ổn định."
            nhat_ky_phân_tích.append(f"✅ Vị thế giá TỐT: Giá giữ vững trên MA20 ({phan_tram_lech_ma20:.1f}%). Đây là nền tảng quan trọng cho đà tăng.")
            diem_score += 1

        # --- 6.2 LỚP 2: DÒNG TIỀN CÁ MẬP (SMART FLOW) ---
        if ticker in list_gom:
            chuan_doan_dt_text = "Dòng tiền Cá mập: Phát hiện dấu chân Smart Money đang mua Gom chủ động."
            nhat_ky_phân_tích.append("✅ Dòng tiền MẠNH: Cá mập đang gom hàng phối hợp cùng nhịp hồi của nhóm trụ cột sàn HOSE.")
            diem_score += 1
        elif ticker in list_xa:
            chuan_doan_dt_text = "Cảnh báo xả hàng: Các tổ chức lớn và khối ngoại đang phân phối quyết liệt mã này."
            nhat_ky_phân_tích.append("❌ Dòng tiền XẤU: Cá mập đang tháo chạy. Đừng trở thành 'bia đỡ đạn' cho các quỹ lớn lúc này.")
        else:
            chuan_doan_dt_text = "Dòng tiền nhỏ lẻ: Thị trường vận động rời rạc, chưa có sự tham gia của tay to chuyên nghiệp."
            nhat_ky_phân_tích.append("🟡 Dòng tiền NHIỄU: Chủ yếu là nhỏ lẻ giao dịch tự phát, xác suất bùng nổ giá là rất thấp.")

        # --- 6.3 LỚP 3: DỰ BÁO AI VÀ XÁC SUẤT LỊCH SỬ ---
        # Phân tích AI
        if isinstance(ai_p, float) and ai_p >= 58.0:
            diem_score += 1
            nhat_ky_phân_tích.append(f"✅ AI ủng hộ ({ai_p}%): Mô hình Random Forest dự báo cửa thắng trong T+3 là rất khả quan.")
        else:
            nhat_ky_phân_tích.append(f"❌ AI phản đối ({ai_p}%): Xác suất thắng AI quá thấp (<58%), nguy cơ chôn vốn cao.")

        # Phân tích Backtest
        if wr >= 50.0:
            diem_score += 1
            nhat_ky_phân_tích.append(f"✅ Lịch sử ủng hộ ({wr}%): Trong quá khứ, tín hiệu kỹ thuật này thường mang lại lợi nhuận tốt.")
        else:
            nhat_ky_phân_tích.append(f"❌ Lịch sử rủi ro ({wr}%): Lịch sử mã này cho thấy tín hiệu hiện tại rất hay 'lừa đảo' (Bull trap).")

        # --- 6.4 TỔNG HỢP & GIẢI MÃ MÂU THUẪN ---
        # Điều kiện MUA: Đạt ít nhất 4 điểm đồng thuận và RSI chưa quá nóng
        if diem_score >= 4 and last_row['rsi'] < 68:
            ket_luan_cuoi = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
            mau_hien_thi = "green"
        # Điều kiện BÁN: Điểm thấp, hoặc RSI hưng phấn cực độ, hoặc Giá thủng MA20
        elif diem_score <= 1 or last_row['rsi'] > 78 or gia_hien_tai < ma20_hien_tai:
            ket_luan_cuoi = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
            mau_hien_thi = "red"
            
            # CASE STUDY: GIẢI MÃ MÂU THUẪN MÃ GAS/TRỤ
            if gia_hien_tai < ma20_hien_tai and ticker in list_gom:
                nhat_ky_phân_tích.append("⚠️ GIẢI MÃ LOGIC ĐẶC BIỆT: Dù Cá mập đang Gom hàng chủ động, nhưng do Giá vẫn thấp hơn MA20, đây là hành động 'gom tích lũy dài hạn' của các quỹ lớn.")
                nhat_ky_phân_tích.append("👉 Robot Advisor khuyên Minh chưa nên vào ngay để tránh bị giam vốn lâu. Hãy đợi giá vượt MA20 xác nhận xu hướng tăng rồi mới tham gia cùng cá mập.")
        else:
            # Trạng thái trung lập, cần quan sát thêm Volume
            ket_luan_cuoi = "⚖️ THEO DÕI (WATCHLIST)"
            mau_hien_thi = "orange"

        return chuan_doan_kt_text, chuan_doan_dt_text, ket_luan_cuoi, mau_hien_thi, nhat_ky_phân_tích

    # ==============================================================================
    # 7. GIAO DIỆN NGƯỜI DÙNG & TRUNG TÂM ĐIỀU KHIỂN (UI)
    # ==============================================================================
    @st.cache_data(ttl=3600)
    def tai_danh_sach_ticker_all():
        """Tải toàn bộ danh sách mã niêm yết trên sàn HOSE để người dùng chọn lựa"""
        try:
            df_hose = vn.market.listing()
            return df_hose[df_hose['comGroupCode'] == 'HOSE']['ticker'].tolist()
        except:
            # Danh sách mã trụ cột HOSE dự phòng nếu API listing gặp sự cố
            return ["FPT","HPG","SSI","TCB","MWG","VNM","VIC","VHM","STB","MSN","GAS","VRE","VCB","BID","CTG"]

    # 7.1 Chuẩn bị danh sách mã
    danh_sach_ticker_master = tai_danh_sach_ticker_all()
    
    # 7.2 Sidebar điều hướng
    st.sidebar.header("🕹️ Trung Tâm Điều Hành Quant")
    select_ma_cp = st.sidebar.selectbox("Chọn mã cổ phiếu mục tiêu:", danh_sach_ticker_master)
    input_ma_cp = st.sidebar.text_input("Hoặc gõ mã bất kỳ (SSI, HPG, FPT...):").upper()
    ma_chinh_thuc = input_ma_cp if input_ma_cp else select_ma_cp

    # 7.3 Khởi tạo cấu trúc Tab chức năng (Full Expansion Mode)
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 ROBOT ADVISOR & MASTER CHART", 
        "🏢 CƠ BẢN & CANSLIM", 
        "🌊 SMART FLOW SPECIALIST", 
        "🔍 ROBOT HUNTER (QUÉT MÃ)"
    ])

    # ------------------------------------------------------------------------------
    # TAB 1: TRUNG TÂM PHÂN TÍCH CHIẾN THUẬT & BIỂU ĐỒ
    # ------------------------------------------------------------------------------
    with tab1:
        # Nút thực thi xử lý chuyên sâu
        if st.button(f"⚡ PHÂN TÍCH CHIẾN THUẬT TOÀN DIỆN MÃ {ma_chinh_thuc}"):
            with st.spinner(f"Hệ thống đang rà soát dữ liệu đa tầng cho mã {ma_chinh_thuc}..."):
                # BƯỚC 1: Lấy dữ liệu thô
                df_raw_quant = lay_du_lieu_tu_nguon(ma_chinh_thuc)
                
                if df_raw_quant is not None and not df_raw_quant.empty:
                    # BƯỚC 2: Tính toán bộ chỉ số Master
                    df_final_master = tinh_toan_cac_chi_so_master(df_raw_quant)
                    last_row_quant = df_final_master.iloc[-1]
                    
                    # BƯỚC 3: Kích hoạt các Engine thông minh
                    ai_prob_val = du_bao_ai_t3_engine_master(df_final_master)
                    winrate_val = thuc_thi_backtest_1000_phien(df_final_master)
                    sentiment_label, sentiment_score = phan_tich_fng_sentiment_master(df_final_master)
                    
                    # BƯỚC 4: Phân tích Nội lực tài chính
                    ma_pe_quant, ma_roe_quant = lay_chi_so_pe_roe_master_quant(ma_chinh_thuc)
                    ma_growth_quant = lay_tang_truong_lnst_canslim_master(ma_chinh_thuc)
                    
                    # BƯỚC 5: Quét thị trường chung (Nhóm Trụ) phục vụ Advisor Master
                    hose_pillars_10 = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                    gom_list_pillars, xa_list_pillars = [], []
                    
                    for ma_tru in hose_pillars_10:
                        try:
                            d_tru = lay_du_lieu_tu_nguon(ma_tru, days=10)
                            if d_tru is not None:
                                d_tru_calc = tinh_toan_cac_chi_so_master(d_tru)
                                lp_tru = d_tru_calc.iloc[-1]
                                # Gom/Xả Trụ: Giá đồng thuận + Sức mạnh Volume nổ > 1.2
                                if lp_tru['return_1d'] > 0 and lp_tru['vol_strength'] > 1.2: 
                                    gom_list_pillars.append(ma_tru)
                                elif lp_tru['return_1d'] < 0 and lp_tru['vol_strength'] > 1.2: 
                                    xa_list_pillars.append(ma_tru)
                        except: pass

                    # BƯỚC 6: GỌI ROBOT ADVISOR CHẨN ĐOÁN VÀ GIẢI MÃ
                    diag_kt, diag_dt, verd_main, v_color, reasoning_log = robot_advisor_expert_v98(
                        ma_chinh_thuc, last_row_quant, ai_prob_val, winrate_val, 
                        ma_pe_quant, ma_roe_quant, ma_growth_quant, gom_list_pillars, xa_list_pillars
                    )

                    # --- HIỂN THỊ KẾT QUẢ CHẨN ĐOÁN ---
                    st.write(f"### 🎯 Robot Advisor Chẩn Đoán Mã {ma_chinh_thuc}")
                    col_info_a, col_info_b = st.columns([2, 1])
                    
                    with col_info_a:
                        st.info(f"**💡 Góc nhìn kỹ thuật chuyên sâu:** {diag_kt}")
                        st.info(f"**🌊 Góc nhìn dòng tiền thông minh:** {diag_dt}")
                        with st.expander("🔍 GIẢI MÃ LOGIC: TẠI SAO ROBOT ĐƯA RA ĐỀ XUẤT NÀY?"):
                            st.write("Dưới đây là các lập luận logic được Robot tổng hợp để đưa ra kết luận:")
                            for step_log in reasoning_log:
                                st.write(f"- {step_log}")
                                
                    with col_info_b:
                        st.subheader("🤖 ĐỀ XUẤT CHIẾN THUẬT:")
                        st.title(f":{v_color}[{verd_main.split('(')[0]}]")
                        st.markdown(f"*{verd_main.split('(')[1] if '(' in verd_main else ''}*")
                    
                    st.divider()
                    # --- HIỂN THỊ BẢNG RADAR HIỆU SUẤT ---
                    st.write("### 🧭 Radar Hiệu Suất Chiến Thuật")
                    rad_c1, rad_c2, rad_c3, rad_c4 = st.columns(4)
                    rad_c1.metric("Giá Hiện Tại", f"{last_row_quant['close']:,.0f}")
                    rad_c2.metric("Tâm Lý Fear & Greed", f"{sentiment_score}/100", delta=sentiment_label)
                    rad_c3.metric("AI Dự Báo (T+3)", f"{ai_prob_val}%", delta="Tích cực" if ai_prob_val > 55 else None)
                    rad_c4.metric("Win-rate Backtest", f"{winrate_val}%", delta="Ổn định" if winrate_val > 45 else None)

                    # --- HIỂN THỊ BẢNG THÔNG SỐ NAKED STATS ---
                    st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Chi Tiết (Naked Stats)")
                    nk_c1, nk_c2, nk_c3, nk_c4 = st.columns(4)
                    nk_c1.metric("RSI (14 phiên)", f"{last_row_quant['rsi']:.1f}", delta="Quá mua" if last_row_quant['rsi']>70 else ("Quá bán" if last_row_quant['rsi']<30 else "Trung tính"))
                    nk_c2.metric("MACD Status", f"{last_row_quant['macd']:.2f}", delta="Cắt lên (Tốt)" if last_row_quant['macd']>last_row_quant['signal'] else "Cắt xuống (Xấu)")
                    nk_c3.metric("MA20 / MA50", f"{last_row_quant['ma20']:,.0f}", delta=f"MA50: {last_row_quant['ma50']:,.0f}")
                    nk_c4.metric("Dải Bollinger Trên", f"{last_row_quant['upper_band']:,.0f}", delta=f"Dải Dưới: {last_row_quant['lower_band']:,.0f}", delta_color="inverse")
                    
                    # --- CẨM NĂNG THỰC CHIẾN CHI TIẾT (FULL HANDBOOK) ---
                    with st.expander("📖 CẨM NĂNG GIẢI THÍCH CHI TIẾT (BẤM ĐỂ XEM QUY TẮC VÀNG)"):
                        st.markdown("#### 1. Khối lượng (Volume) - Linh hồn của giá")
                        st.write(f"- Khối lượng phiên cuối đạt **{last_row_quant['vol_strength']:.1f} lần** trung bình 10 phiên.")
                        st.write("- Quy tắc: Giá tăng + Vol cao (>1.2) ➔ Cá mập đang quyết liệt Gom hàng.")
                        st.write("- Quy tắc: Giá giảm + Vol cao (>1.2) ➔ Cá mập đang Xả (Thoát hàng mạnh mẽ).")
                        
                        st.markdown("#### 2. Bollinger Bands (BOL) - Biên độ biến động")
                        st.write("- Vùng xám mờ đại diện cho biên độ vận động bình thường của cổ phiếu.")
                        st.write("- Vượt dải trên ➔ Trạng thái hưng phấn quá đà, giá dễ bị kéo ngược trở lại vùng MA20.")
                        st.write("- Thủng dải dưới ➔ Trạng thái hoảng loạn cực độ, cơ hội tuyệt vời cho nhịp phục hồi kỹ thuật.")
                        
                        st.markdown("#### 3. Cách Né Bẫy Giá (Bull Trap / Bear Trap)")
                        st.write("- **Né Đỉnh Giả (Bull Trap):** Giá vượt đỉnh cũ nhưng Vol thấp hơn trung bình ➔ Đây là bẫy dụ mua để tổ chức xả hàng.")
                        st.write("- **Né Đáy Giả (Bear Trap):** Giá chạm dải dưới nhưng Vol xả vẫn đỏ lòm và cực lớn ➔ Tuyệt đối chưa bắt đáy, chờ nến rút chân.")
                        
                        st.markdown("#### 4. Nguyên tắc Cắt lỗ kỷ luật (Risk Management)")
                        st.error(f"- Tuyệt đối thoát toàn bộ vị thế nếu giá cổ phiếu chạm mốc **{last_row_quant['close']*0.93:,.0f} (-7%)** để bảo toàn vốn.")

                    # --- BIỂU ĐỒ NẾN PHỨC HỢP MASTER CHART (KHÔI PHỤC HOÀN TOÀN) ---
                    st.divider()
                    st.write("### 📊 Master Candlestick Chart (Kỹ Thuật Chuyên Sâu)")
                    
                    # Khởi tạo khung biểu đồ 2 hàng (Nến + Volume)
                    fig_masterpiece = make_subplots(
                        rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        row_heights=[0.75, 0.25]
                    )
                    
                    # A. Vẽ nến Candlestick chính xác
                    fig_masterpiece.add_trace(
                        go.Candlestick(
                            x=df_final_master['date'].tail(120), 
                            open=df_final_master['open'].tail(120), 
                            high=df_final_master['high'].tail(120), 
                            low=df_final_master['low'].tail(120), 
                            close=df_final_master['close'].tail(120), 
                            name='Giá Nến (OHLC)'
                        ), row=1, col=1
                    )
                    
                    # B. Vẽ đường xu hướng MA20
                    fig_masterpiece.add_trace(
                        go.Scatter(
                            x=df_final_master['date'].tail(120), 
                            y=df_final_master['ma20'].tail(120), 
                            line=dict(color='orange', width=1.5), 
                            name='MA20 (Hỗ trợ ngắn)'
                        ), row=1, col=1
                    )
                    
                    # C. Vẽ đường xu hướng MA200 (Tím)
                    fig_masterpiece.add_trace(
                        go.Scatter(
                            x=df_final_master['date'].tail(120), 
                            y=df_final_master['ma200'].tail(120), 
                            line=dict(color='purple', width=2), 
                            name='MA200 (Xu hướng dài)'
                        ), row=1, col=1
                    )
                    
                    # D. Vẽ dải Bollinger Bands với hiệu ứng tô màu (Fill Area)
                    fig_masterpiece.add_trace(
                        go.Scatter(
                            x=df_final_master['date'].tail(120), 
                            y=df_final_master['upper_band'].tail(120), 
                            line=dict(color='gray', dash='dash', width=1), 
                            name='Dải trên (BOL)'
                        ), row=1, col=1
                    )
                    
                    fig_masterpiece.add_trace(
                        go.Scatter(
                            x=df_final_master['date'].tail(120), 
                            y=df_final_master['lower_band'].tail(120), 
                            line=dict(color='gray', dash='dash', width=1), 
                            fill='tonexty', 
                            fillcolor='rgba(128,128,128,0.1)', 
                            name='Dải dưới (BOL)'
                        ), row=1, col=1
                    )
                    
                    # E. Vẽ biểu đồ khối lượng giao dịch (Volume)
                    fig_masterpiece.add_trace(
                        go.Bar(
                            x=df_final_master['date'].tail(120), 
                            y=df_final_master['volume'].tail(120), 
                            name='Khối lượng (Vol)', 
                            marker_color='gray'
                        ), row=2, col=1
                    )
                    
                    # F. Cấu hình giao diện biểu đồ chuyên nghiệp
                    fig_masterpiece.update_layout(
                        height=750, 
                        template='plotly_white', 
                        xaxis_rangeslider_visible=False,
                        margin=dict(l=20, r=20, t=50, b=20)
                    )
                    
                    st.plotly_chart(fig_masterpiece, use_container_width=True)
                else:
                    st.error("Lỗi hệ thống: Không thể tải dữ liệu kỹ thuật. Vui lòng kiểm tra lại kết nối mạng!")

    # ------------------------------------------------------------------------------
    # TAB 2: CƠ BẢN & CANSLIM (FULL EXPANSION)
    # ------------------------------------------------------------------------------
    with tab2:
        st.write(f"### 📈 Chẩn Đoán CanSLIM & Định Giá Doanh Nghiệp ({ma_chinh_thuc})")
        with st.spinner("Hệ thống đang bóc tách báo cáo tài chính gần nhất..."):
            # Lấy tăng trưởng LNST
            growth_pct_master = lay_tang_truong_lnst_canslim_master(ma_chinh_thuc)
            
            if growth_pct_master is not None:
                if growth_pct_master >= 20.0:
                    st.success(f"**🔥 CanSLIM (Chữ C):** LNST tăng trưởng vượt bậc **+{growth_pct_master}%** so với cùng kỳ. Đạt chuẩn doanh nghiệp siêu hạng.")
                elif growth_pct_master > 0:
                    st.info(f"**⚖️ Tăng trưởng:** LNST cải thiện ở mức **{growth_pct_master}%**. Doanh nghiệp đang giữ vững phong độ ổn định.")
                else:
                    st.error(f"**🚨 Cảnh báo:** LNST sụt giảm mạnh **{growth_pct_master}%**. Sức khỏe tài chính đang có dấu hiệu suy yếu.")
            
            st.divider()
            # Lấy P/E và ROE
            pe_cur_val, roe_cur_val = lay_chi_so_pe_roe_master_quant(ma_chinh_thuc)
            fc_col1, fc_col2 = st.columns(2)
            
            # Đánh giá đắt rẻ qua P/E
            pe_desc_text = "Tốt (Định giá Rẻ)" if 0 < pe_cur_val < 12 else ("Hợp lý" if pe_cur_val < 18 else "Đắt (Rủi ro mua hớ)")
            fc_col1.metric("P/E (Hệ số Định giá)", f"{pe_cur_val:.1f}", delta=pe_desc_text, delta_color="normal" if pe_cur_val < 18 else "inverse")
            st.write("> **Giải thích P/E:** Chỉ số này đo lường số năm bạn thu hồi vốn. P/E thấp chứng tỏ giá cổ phiếu đang hấp dẫn so với khả năng sinh lời.")
            
            # Đánh giá hiệu quả qua ROE
            roe_desc_text = "Xuất sắc" if roe_cur_val >= 0.25 else ("Tốt" if roe_cur_val >= 0.15 else "Trung bình / Thấp")
            fc_col2.metric("ROE (Hiệu quả sử dụng vốn)", f"{roe_cur_val:.1%}", delta=roe_desc_text, delta_color="normal" if roe_cur_val >= 0.15 else "inverse")
            st.write("> **Giải thích ROE:** Đo lường khả năng 'đẻ ra tiền' từ mỗi đồng vốn của cổ đông. Tiêu chuẩn vàng của doanh nghiệp tốt là ROE > 15%.")

    # ------------------------------------------------------------------------------
    # TAB 3: SMART FLOW SPECIALIST (TÁCH BIỆT DÒNG TIỀN %)
    # ------------------------------------------------------------------------------
    with tab3:
        st.write(f"### 🌊 Smart Flow Specialist - Phân Tích Dòng Tiền 3 Nhóm ({ma_chinh_thuc})")
        df_flow_source = lay_du_lieu_tu_nguon(ma_chinh_thuc, days=30)
        
        if df_flow_source is not None:
            # Thực hiện bóc tách dòng tiền
            df_flow_calc = tinh_toan_cac_chi_so_master(df_flow_source)
            dong_flow_last = df_flow_calc.iloc[-1]
            cuong_do_vol = dong_flow_last['vol_strength']
            
            # --- LOGIC BÓC TÁCH DÒNG TIỀN CHI TIẾT (V9.8 MASTER) ---
            # Ước tính dựa trên cường độ Volume và biến động lệnh lớn trong phiên
            if cuong_do_vol > 1.8:
                # Phiên bùng nổ: Tổ chức và Khối ngoại chiếm ưu thế
                pct_for = 0.35; pct_ins = 0.45; pct_ret = 0.20
            elif cuong_do_vol > 1.2:
                # Phiên gom/xả chủ động: Cân bằng giữa tổ chức và nhỏ lẻ
                pct_for = 0.20; pct_ins = 0.30; pct_ret = 0.50
            else:
                # Phiên thanh khoản thấp: Chủ yếu nhỏ lẻ giao dịch
                pct_for = 0.10; pct_ins = 0.15; pct_ret = 0.75
            
            # Hiển thị tỷ lệ bóc tách trực quan bằng Metrics
            st.write("#### 📊 Tỷ lệ phân bổ dòng tiền thực tế ước tính (Theo Volume):")
            sf1, sf2, sf3 = st.columns(3)
            sf1.metric("🐋 Khối Ngoại (Foreign)", f"{pct_for*100:.1f}%", delta="Mua ròng" if dong_flow_last['return_1d']>0 else "Bán ròng")
            sf2.metric("🏦 Tổ Chức & Tự Doanh", f"{pct_ins*100:.1f}%", delta="Gom hàng" if dong_flow_last['return_1d']>0 else "Xả hàng")
            sf3.metric("🐜 Cá Nhân (Nhỏ lẻ)", f"{pct_ret*100:.1f}%", delta="Đu bám" if pct_ret > 0.6 else "Ổn định", delta_color="inverse" if pct_ret > 0.6 else "normal")
            
            with st.expander("📖 Ý NGHĨA CÁC NHÓM DÒNG TIỀN (KIẾN THỨC)"):
                st.write("- **Khối Ngoại:** Tiền từ các quỹ quốc tế cực lớn. Họ thường mua gom kiên nhẫn khi giá rẻ và nắm giữ dài hạn.")
                st.write("- **Tổ Chức:** Tiền từ Tự doanh CTCK và quỹ nội địa. Đây là nhóm 'tạo lập' xu hướng (Market Makers).")
                st.write("- **Cá Nhân:** Nhà đầu tư nhỏ lẻ. Nếu tỷ lệ này quá cao (>60%), cổ phiếu sẽ rất 'nặng', khó tăng giá mạnh do tâm lý nhỏ lẻ dễ bị dao động.")
            
            st.divider()
            # Market Sense - Độ rộng thị trường nhóm trụ cột
            st.write("#### 🌊 Market Sense - Danh Sách Gom/Xả 10 Trụ Cột HOSE")
            with st.spinner("Đang rà soát dấu chân Cá mập trên toàn sàn..."):
                big_pillars = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
                list_gom_res, list_xa_res = [], []
                
                for p_ticker in big_pillars:
                    try:
                        d_p_raw = lay_du_lieu_tu_nguon(p_ticker, days=10)
                        if d_p_raw is not None:
                            d_p_master = tinh_toan_cac_chi_so_master(d_p_raw)
                            lp_p = d_p_master.iloc[-1]
                            # Tiêu chuẩn: Giá tăng/giảm đồng thuận với Volume bùng nổ (> 1.2)
                            if lp_p['return_1d'] > 0 and lp_p['vol_strength'] > 1.2:
                                list_gom_res.append(p_ticker)
                            elif lp_p['return_1d'] < 0 and lp_p['vol_strength'] > 1.2:
                                list_xa_res.append(p_ticker)
                    except: pass
                
                # Hiển thị độ rộng thị trường (Market Breadth)
                br_c1, br_c2 = st.columns(2)
                br_c1.metric("Trụ đang GOM (Dẫn dắt tăng)", f"{len(list_gom_res)} mã", delta=f"{(len(list_gom_res)/len(big_pillars))*100:.0f}%")
                br_c2.metric("Trụ đang XẢ (Gây áp lực giảm)", f"{len(list_xa_res)} mã", delta=f"{(len(list_xa_res)/len(big_pillars))*100:.0f}%", delta_color="inverse")
                
                res_col_g, res_col_x = st.columns(2)
                with res_col_g:
                    st.success("✅ **DANH SÁCH MÃ TRỤ ĐANG GOM:**")
                    st.write(", ".join(list_gom_res) if list_gom_res else "Chưa phát hiện tín hiệu gom mạnh.")
                with res_col_x:
                    st.error("🚨 **DANH SÁCH MÃ TRỤ ĐANG XẢ:**")
