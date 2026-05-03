# ==============================================================================
# QUANT SYSTEM V20.0 - THE PREDATOR LEVIATHAN
# Tác giả: Minh | Clean Code Edition — Final Build (9 Fixes Applied)
# ==============================================================================

# --- IMPORTS ---
import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo          # Python 3.9+
except ImportError:
    from backports.zoneinfo import ZoneInfo  # fallback
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
import nltk

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# CONSTANTS — Tập trung tất cả ngưỡng số vào đây để dễ chỉnh sau
# ==============================================================================
DATE_FMT          = '%Y-%m-%d'
TZ_VN             = ZoneInfo("Asia/Ho_Chi_Minh")
HISTORY_DAYS      = 1000

# RSI
RSI_PERIOD        = 14
RSI_OVERBOUGHT    = 70
RSI_OVERSOLD      = 30
RSI_HOT           = 68      # ngưỡng chống FOMO khi mua
RSI_COLD          = 42
RSI_WATCHLIST_MAX = 62

# Volume
VOL_BREAKOUT      = 1.3     # nổ vol → nhóm bùng nổ
VOL_ACC_MIN       = 0.8     # vol tích lũy (min)
VOL_ACC_MAX       = 1.2     # vol tích lũy (max)
VOL_SHARK         = 2.5     # [FIX #1] Cá mập: vol đột biến > 2.5x
VOL_INST_HIGH     = 1.8     # [FIX #1] Tổ chức nội: vol > 1.8x
VOL_INST_MID      = 1.2     # [FIX #1] Nhỏ lẻ: vol < 1.2x
VOL_PV_SIGNAL     = 1.2     # ngưỡng pv_trend

# Bollinger
BB_SQUEEZE_TOL    = 1.2     # sai số chấp nhận khi xác nhận nén

# Cạn Cung
SUPPLY_RATIO      = 0.8     # vol < 80% MA20 → cạn cung

# Giá so MA20
PRICE_NEAR_MA20   = 0.95    # giá >= 95% MA20 → an toàn

# Cắt lỗ — [FIX #3] Cố định -7% từ giá hiện tại
SL_PCT            = 0.07

# Backtest
BT_RSI_BUY        = 45
BT_PROFIT         = 0.05    # mục tiêu 5%
BT_DAYS_FWD       = 10

# AI
AI_MIN_ROWS       = 200
AI_PROFIT_T3      = 1.02    # tăng ≥ 2% sau 3 ngày
AI_GOOD           = 55.0
AI_OK             = 48.0

# Advisor điểm số
ADV_BUY_SCORE     = 3
ADV_SELL_SCORE    = 1
ADV_AI_BUY        = 58.0
ADV_GROWTH_BUY    = 15.0
ADV_RSI_SELL      = 78
ADV_WINRATE_GOOD  = 50.0

# Tài chính — [FIX #4] P/E đắt khi > 20
CANSLIM_GREAT     = 20.0
PE_CHEAP          = 12
PE_OK             = 20      # [FIX #4] sửa từ 18 → 20
ROE_EXCELLENT     = 0.25
ROE_GOOD          = 0.15

# Radar — [FIX #8] Tăng từ 30 → 150 để quét đủ toàn bộ HOSE
RADAR_MAX         = 150
SCAN_DAYS         = 100
FOREIGN_DAYS      = 5
FOREIGN_NET_DAYS  = 3

# Chart
CHART_DAYS        = 120

# Mã trụ thị trường
PILLARS = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
FALLBACK_TICKERS = [
    "ACB","BCG","BID","BVH","CTD","CTG","DBC","DCM","DGC","DGW",
    "DIG","DPM","DXG","EIB","FPT","GAS","GEX","GMD","HDB","HDG",
    "HPG","HSG","KDH","LPB","MBB","MSN","MWG","NLG","NVL","OCB",
    "PDR","PHR","PLX","PNJ","POW","PVD","REE","SAB","SSI","STB",
    "TCB","TPB","VCB","VCI","VHM","VIC","VIX","VJC","VND","VNM",
    "VPB","VRE","VTP","DXS","DGW","FRT","GEG","HAH","HHV","HVN",
    "IMP","KBC","KDC","KOS","MCH","MIG","MSB","NKG","PAN","PC1",
    "PTB","PVT","SBT","SHB","SRC","SSB","TCH","VGC","VHC","VSH",
]


# ==============================================================================
# HELPER FUNCTIONS — Các hàm tiện ích dùng chung
# ==============================================================================

def now_vn() -> datetime:
    """Thời gian hiện tại theo múi giờ Việt Nam (UTC+7)."""
    return datetime.now(TZ_VN)


def date_range(days: int) -> tuple[str, str]:
    """Trả về (start_date, end_date) dạng string theo múi giờ VN."""
    today = now_vn()
    return (
        (today - timedelta(days=days)).strftime(DATE_FMT),
        today.strftime(DATE_FMT)
    )


def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Chuẩn hóa tên cột về chữ thường, xử lý cả MultiIndex."""
    if len(df.columns) == 0:
        return df
    if isinstance(df.columns[0], tuple):
        df.columns = [str(c[0]).lower() for c in df.columns]
    else:
        df.columns = [str(c).lower() for c in df.columns]
    return df


def valid(df) -> bool:
    """True nếu df không None và không rỗng."""
    return df is not None and not df.empty


def to_billion(val) -> float:
    """Quy đổi VNĐ sang tỷ VNĐ nếu cần."""
    v = float(val or 0)
    return v / 1e9 if abs(v) > 1e6 else v


def calc_net_flow(df: pd.DataFrame, days: int = 3) -> float:
    """Tính giá trị ròng (mua - bán) trong N ngày gần nhất."""
    total_buy = total_sell = 0.0
    for _, row in df.tail(days).iterrows():
        total_buy  += float(row.get('buyval',  0) or 0)
        total_sell += float(row.get('sellval', 0) or 0)
    return total_buy - total_sell


def engine() -> Vnstock:
    """Trả về Vnstock engine từ session state."""
    return st.session_state['vnstock_engine']


# ==============================================================================
# 1. BẢO MẬT & PHÂN QUYỀN
# ==============================================================================

def authenticate() -> bool:
    """Hiển thị màn hình đăng nhập. Trả về True nếu đã xác thực."""
    KEY = "authenticated"
    if st.session_state.get(KEY, False):
        return True

    st.markdown("### 🔐 Quant System V20.0 — Cổng Bảo Mật Trung Tâm")
    st.info("Hệ thống phân tích định lượng chuyên sâu. Vui lòng xác thực danh tính.")
    pwd = st.text_input("🔑 Nhập mật mã truy cập:", type="password")

    if pwd:
        if pwd == st.secrets.get("password", ""):
            st.session_state[KEY] = True
            st.rerun()
        else:
            st.error("❌ Mật mã không hợp lệ. Vui lòng kiểm tra lại phím Caps Lock.")
    return False


# ==============================================================================
# 2. TRUY XUẤT DỮ LIỆU GIÁ
# ==============================================================================

def get_price(ticker: str, days: int = HISTORY_DAYS) -> pd.DataFrame | None:
    """
    Tải dữ liệu OHLCV.
    Ưu tiên Vnstock → fallback Yahoo Finance.
    """
    start, end = date_range(days)

    # Phương án A: Vnstock
    try:
        df = engine().stock.quote.history(symbol=ticker, start=start, end=end)
        if valid(df):
            return normalize_cols(df)
    except Exception as e:
        print(f"[WARN] Vnstock price {ticker}: {e}")

    # Phương án B: Yahoo Finance
    try:
        yf_sym = "^VNINDEX" if ticker == "VNINDEX" else f"{ticker}.VN"
        df = yf.download(yf_sym, period="3y", progress=False).reset_index()
        if valid(df):
            return normalize_cols(df)
    except Exception as e:
        st.sidebar.error(f"⚠️ Lỗi tải dữ liệu {ticker}: {e}")

    return None


def get_foreign(ticker: str, days: int = 20) -> pd.DataFrame | None:
    """Truy xuất dữ liệu giao dịch Khối Ngoại (thử 2 API endpoint)."""
    start, end = date_range(days)

    for method in [
        lambda: engine().stock.trade.foreign_trade(symbol=ticker, start=start, end=end),
        lambda: engine().stock.trading.foreign(symbol=ticker, start=start, end=end),
    ]:
        try:
            df = method()
            if valid(df):
                return normalize_cols(df)
        except Exception:
            continue

    return None


def get_proprietary(ticker: str, days: int = 20) -> pd.DataFrame | None:
    """Truy xuất dữ liệu giao dịch Tự Doanh."""
    start, end = date_range(days)
    try:
        df = engine().stock.trade.proprietary_trade(symbol=ticker, start=start, end=end)
        if valid(df):
            return normalize_cols(df)
    except Exception as e:
        print(f"[WARN] Proprietary {ticker}: {e}")
    return None


# ==============================================================================
# 3. BỘ CHỈ BÁO KỸ THUẬT
# ==============================================================================

def calc_indicators(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Tính toán đầy đủ bộ chỉ báo kỹ thuật.
    RSI dùng Wilder's Smoothing (EWM) — chuẩn chính xác như sàn.
    """
    df = df_raw.copy()
    df = df.loc[:, ~df.columns.duplicated()]

    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in ['close', 'open', 'volume']:
        df[col] = df[col].ffill()

    close  = df['close']
    open_  = df['open']
    volume = df['volume']

    # --- Moving Averages ---
    df['ma20']  = close.rolling(20).mean()
    df['ma50']  = close.rolling(50).mean()
    df['ma200'] = close.rolling(200).mean()

    # --- Bollinger Bands ---
    std20            = close.rolling(20).std()
    df['upper_band'] = df['ma20'] + 2 * std20
    df['lower_band'] = df['ma20'] - 2 * std20
    df['bb_width']   = (df['upper_band'] - df['lower_band']) / (df['ma20'] + 1e-9)

    # --- RSI chuẩn Wilder's (EWM) ---
    delta    = close.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/RSI_PERIOD, min_periods=RSI_PERIOD, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/RSI_PERIOD, min_periods=RSI_PERIOD, adjust=False).mean()
    rs       = avg_gain / (avg_loss + 1e-9)
    df['rsi'] = 100 - (100 / (1 + rs))

    # --- MACD (12, 26, 9) ---
    ema12        = close.ewm(span=12, adjust=False).mean()
    ema26        = close.ewm(span=26, adjust=False).mean()
    df['macd']   = ema12 - ema26
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # --- Volume & Flow ---
    df['return_1d']    = close.pct_change()
    vol_avg10          = volume.rolling(10).mean()
    df['vol_strength'] = volume / (vol_avg10 + 1e-9)
    df['money_flow']   = close * volume
    df['volatility']   = df['return_1d'].rolling(20).std()
    df['vol_avg_20']   = volume.rolling(20).mean()

    # --- Cạn Cung ---
    df['is_red_candle'] = close < open_
    df['can_cung']      = df['is_red_candle'] & (volume < df['vol_avg_20'] * SUPPLY_RATIO)

    # --- PV Trend ---
    is_explosion   = df['vol_strength'] > VOL_PV_SIGNAL
    df['pv_trend'] = np.where(
        (df['return_1d'] > 0) & is_explosion,  1,
        np.where(
            (df['return_1d'] < 0) & is_explosion, -1, 0
        )
    )

    return df.dropna()


# ==============================================================================
# 4. AI & PHÂN TÍCH ĐỊNH LƯỢNG
# ==============================================================================

def analyze_sentiment(df: pd.DataFrame) -> tuple[str, float]:
    """Phân tích tâm lý dựa trên RSI phiên gần nhất."""
    rsi = df.iloc[-1]['rsi']
    if   rsi > 75:              label = "🔥 CỰC KỲ THAM LAM (Vùng Quá Mua)"
    elif rsi > 60:              label = "⚖️ THAM LAM (Hưng Phấn)"
    elif rsi < RSI_OVERSOLD:    label = "💀 CỰC KỲ SỢ HÃI (Vùng Quá Bán)"
    elif rsi < RSI_COLD:        label = "😨 SỢ HÃI (Bi Quan)"
    else:                       label = "🟡 TRUNG LẬP (Đi Ngang)"
    return label, round(rsi, 1)


def run_backtest(df: pd.DataFrame) -> float:
    """
    Backtest: Mua khi RSI < 45 & MACD cắt lên.
    Mục tiêu: +5% trong 10 ngày.
    """
    signals = wins = 0
    n = len(df)

    for i in range(100, n - BT_DAYS_FWD):
        rsi_ok     = df['rsi'].iloc[i] < BT_RSI_BUY
        macd_cross = (
            df['macd'].iloc[i]   > df['signal'].iloc[i] and
            df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
        )
        if rsi_ok and macd_cross:
            signals   += 1
            buy_price  = df['close'].iloc[i]
            target     = buy_price * (1 + BT_PROFIT)
            future     = df['close'].iloc[i+1 : i+1+BT_DAYS_FWD]
            if any(future > target):
                wins += 1

    return round((wins / signals) * 100, 1) if signals else 0.0


def predict_ai_t3(df: pd.DataFrame) -> float | str:
    """
    Random Forest: dự báo xác suất tăng ≥ 2% sau T+3.
    Train trên lịch sử, tránh look-ahead bias bằng cách bỏ 3 ngày cuối khi train.
    """
    if len(df) < AI_MIN_ROWS:
        return "N/A"

    df2 = df.copy()
    df2['target'] = (df2['close'].shift(-3) > df2['close'] * AI_PROFIT_T3).astype(int)
    df2 = df2.dropna()

    features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility',
                'vol_strength', 'money_flow', 'pv_trend']
    X, y = df2[features], df2['target']

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X[:-3], y[:-3])

    prob = model.predict_proba(X.iloc[[-1]])[0][1]
    return round(prob * 100, 1)


# ==============================================================================
# [FIX #2] RADAR ĐỈNH / ĐÁY — Tính % khoảng cách MA20 & Bollinger
# ==============================================================================

def calc_support_resistance(last: pd.Series) -> dict:
    """
    Tính % khoảng cách từ giá hiện tại đến:
    - Hỗ trợ: MA20 (phía dưới)
    - Kháng cự: Bollinger Band trên (phía trên)
    Dương = còn room tăng / chưa chạm hỗ trợ.
    Âm   = đã vượt / đã thủng.
    """
    price = last['close']
    ma20  = last['ma20']
    upper = last['upper_band']
    rsi   = last['rsi']

    dist_to_support    = round((price - ma20)  / (ma20  + 1e-9) * 100, 2)  # >0: trên MA20
    dist_to_resistance = round((upper - price) / (price + 1e-9) * 100, 2)  # >0: chưa chạm trần

    # Cảnh báo RSI + BB
    if rsi > RSI_OVERBOUGHT and dist_to_resistance < 2:
        warning = "🚨 Đỉnh Kép: RSI Quá Mua + Chạm Trần Bollinger — Nguy cơ đảo chiều rất cao!"
    elif rsi < RSI_OVERSOLD and dist_to_support < -3:
        warning = "💡 Đáy Sâu: RSI Quá Bán + Thủng MA20 — Cơ hội hồi kỹ thuật ngắn hạn."
    elif dist_to_resistance < 3:
        warning = "⚠️ Sắp Chạm Kháng Cự Bollinger — Cẩn thận xả hàng vùng đỉnh."
    elif dist_to_support < -2:
        warning = "⚠️ Đã Thủng MA20 — Kiểm tra lại xu hướng ngắn hạn."
    else:
        warning = "✅ Vùng An Toàn — Giá đang ở giữa hỗ trợ và kháng cự."

    return {
        'dist_to_support':    dist_to_support,
        'dist_to_resistance': dist_to_resistance,
        'warning':            warning,
    }


# ==============================================================================
# 5. BÁO CÁO TỰ ĐỘNG
# ==============================================================================

def generate_report(
    ticker: str,
    last: pd.Series,
    ai_score,
    winrate: float,
    buy_set: set,
    sell_set: set
) -> str:
    """Tạo bản phân tích văn bản tự động từ các chỉ số."""
    parts = []

    # --- 1. Dòng tiền ---
    parts.append("#### 1. Đọc Vị Hành Vi Dòng Tiền (Smart Flow):")
    vol = last['vol_strength']
    if ticker in buy_set:
        parts.append(f"✅ **Tích Cực:** Dòng tiền lớn đang **GOM HÀNG CHỦ ĐỘNG** tại {ticker}. "
                     f"Khối lượng nổ đột biến gấp {vol:.1f} lần, kèm nến xanh xác nhận.")
    elif ticker in sell_set:
        parts.append(f"🚨 **Cảnh Báo:** Dòng tiền lớn đang **XẢ HÀNG QUYẾT LIỆT**. "
                     f"Khối lượng bán ồ ạt gấp {vol:.1f} lần, nến đỏ đè áp lực.")
    else:
        parts.append("🟡 **Trung Lập:** Dòng tiền chưa đột biến. Chủ yếu giao dịch nhỏ lẻ.")

    # --- 2. Kỹ thuật ---
    parts.append("#### 2. Đánh Giá Vị Thế Kỹ Thuật:")
    price, ma20, rsi = last['close'], last['ma20'], last['rsi']

    if price < ma20:
        parts.append(f"❌ **Xu Hướng Xấu:** Giá ({price:,.0f}) đang **DƯỚI** MA20 ({ma20:,.0f}). "
                     f"Phe bán áp đảo — chưa nên bắt đáy.")
    else:
        parts.append(f"✅ **Xu Hướng Tốt:** Giá ({price:,.0f}) đang **TRÊN** MA20 ({ma20:,.0f}). "
                     f"Cấu trúc tăng ngắn hạn được bảo vệ.")

    if rsi > RSI_OVERBOUGHT:
        parts.append(f"⚠️ **Cảnh Báo Quá Mua:** RSI = {rsi:.1f} — dễ điều chỉnh bất cứ lúc nào.")
    elif rsi < 35:
        parts.append(f"💡 **Cơ Hội:** RSI = {rsi:.1f} (Quá Bán) — lực bán gần cạn, khả năng hồi cao.")
    else:
        parts.append(f"📉 **Tâm Lý Ổn Định:** RSI = {rsi:.1f}.")

    # --- 3. AI & Lịch sử ---
    parts.append("#### 3. Xác Suất Định Lượng (AI & Lịch Sử):")
    if isinstance(ai_score, float):
        ai_label = "Cửa sáng, nên xem xét" if ai_score > AI_GOOD else "Rủi ro cao, cẩn thận"
        parts.append(f"- **AI Dự Báo T+3:** **{ai_score}%** → *{ai_label}*")

    wr_label = "Tín hiệu uy tín" if winrate >= ADV_WINRATE_GOOD else "Cẩn thận — dễ là bẫy"
    parts.append(f"- **Winrate Lịch Sử:** **{winrate}%** → *{wr_label}*")

    # [FIX #3] Cắt lỗ -7% từ giá hiện tại
    sl_price = price * (1 - SL_PCT)
    parts.append(f"- **🛡️ Mức Cắt Lỗ (SL -7%):** **{sl_price:,.0f} VNĐ** "
                 f"*(= Giá hiện tại {price:,.0f} × 0.93)*")

    # --- 4. Tổng kết ---
    parts.append("#### 💡 TỔNG KẾT:")
    price_bad = price < ma20
    ai_good   = isinstance(ai_score, float) and ai_score > AI_GOOD
    wr_good   = winrate >= ADV_WINRATE_GOOD

    if price_bad and ticker in buy_set:
        parts.append("⚠️ **GOM HÀNG RẢI ĐỈNH:** Có dòng tiền gom nhưng giá vẫn dưới MA20 — "
                     "pha tích lũy của quỹ lớn. Hãy chờ bứt MA20 rồi mới vào.")
    elif winrate < 40 and isinstance(ai_score, float) and ai_score < 50:
        parts.append("⛔ **RỦI RO NGẬP TRÀN:** AI và lịch sử đều tiêu cực — "
                     "khả năng cao là bẫy tăng. Tuyệt đối đứng ngoài.")
    elif not price_bad and ai_good and wr_good:
        parts.append("🚀 **ĐIỂM MUA VÀNG:** Nền đẹp + AI đồng thuận + lịch sử xác nhận. "
                     "Có thể giải ngân 30–50% vị thế.")
    else:
        parts.append("⚖️ **THEO DÕI (50/50):** Tín hiệu phân hóa — "
                     "đưa vào Watchlist, chờ phiên bùng nổ khối lượng xác nhận.")

    return "\n\n".join(parts)


# ==============================================================================
# 6. TÀI CHÍNH CƠ BẢN (CANSLIM)
# ==============================================================================

def get_earnings_growth(ticker: str) -> float | None:
    """Đo lường tăng trưởng LNST so cùng kỳ (Chữ C trong CANSLIM)."""
    try:
        df = engine().stock.finance.income_statement(
            symbol=ticker, period='quarter', lang='en'
        ).head(5)
        profit_col = next(
            (c for c in df.columns
             if any(k in str(c).lower() for k in ['sau thuế', 'posttax', 'net profit', 'earning'])),
            None
        )
        if profit_col:
            now_p  = float(df.iloc[0][profit_col])
            prev_p = float(df.iloc[4][profit_col])
            if prev_p > 0:
                return round((now_p - prev_p) / prev_p * 100, 1)
    except Exception as e:
        print(f"[WARN] Earnings Vnstock {ticker}: {e}")

    try:
        g = yf.Ticker(f"{ticker}.VN").info.get('earningsQuarterlyGrowth')
        if g is not None:
            return round(g * 100, 1)
    except Exception as e:
        print(f"[WARN] Earnings Yahoo {ticker}: {e}")

    return None


def get_pe_roe(ticker: str) -> tuple:
    """Lấy P/E và ROE. Fallback Yahoo nếu Vnstock lỗi."""
    pe = roe = None

    try:
        row = engine().stock.finance.ratio(ticker, 'quarterly').iloc[-1]
        raw_pe  = row.get('ticker_pe', row.get('pe'))
        raw_roe = row.get('roe')

        if raw_pe is not None:
            v = float(raw_pe)
            if not np.isnan(v) and v > 0:
                pe = v
        if raw_roe is not None:
            v = float(raw_roe)
            if not np.isnan(v) and v > 0:
                roe = v
    except Exception as e:
        print(f"[WARN] PE/ROE Vnstock {ticker}: {e}")

    if pe is None:
        try:
            info = yf.Ticker(f"{ticker}.VN").info
            pe   = info.get('trailingPE') or pe
            roe  = roe or info.get('returnOnEquity')
        except Exception as e:
            print(f"[WARN] PE/ROE Yahoo {ticker}: {e}")

    return pe, roe


# ==============================================================================
# 7. ROBOT ADVISOR
# ==============================================================================

def advisor_signal(last: pd.Series, ai_score, winrate: float, growth) -> tuple[str, str]:
    """
    Tính điểm tổng hợp và xuất lệnh MUA / BÁN / THEO DÕI.
    Thang điểm 0–4: AI, Winrate, Kỹ thuật, Tài chính.
    """
    score = 0
    price, ma20, rsi = last['close'], last['ma20'], last['rsi']

    if isinstance(ai_score, float) and ai_score >= ADV_AI_BUY:   score += 1
    if winrate >= ADV_WINRATE_GOOD:                               score += 1
    if price > ma20:                                              score += 1
    if growth is not None and growth >= ADV_GROWTH_BUY:           score += 1

    buy  = score >= ADV_BUY_SCORE and rsi < RSI_HOT
    sell = score <= ADV_SELL_SCORE or rsi > ADV_RSI_SELL or price < ma20

    if buy:
        return "🚀 MUA / NẮM GIỮ (STRONG BUY)", "green"
    elif sell:
        return "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)", "red"
    else:
        return "⚖️ THEO DÕI (WATCHLIST)", "orange"


# ==============================================================================
# 8. RADAR PHÂN LOẠI CỔ PHIẾU (2 TẦNG)
# ==============================================================================

def classify_stock(ticker: str, df: pd.DataFrame, ai_score) -> str | None:
    """
    Tầng 1 → BÙNG NỔ nếu vol nổ mạnh.
    Tầng 2 → DANH SÁCH CHỜ nếu đạt điều kiện cơ bản
              + ít nhất 1 trong 3 vũ khí (Squeeze / Cạn Cung / Smart Money).
    """
    last  = df.iloc[-1]
    vol   = last['vol_strength']
    rsi   = last['rsi']
    price = last['close']
    ma20  = last['ma20']

    # Tầng 1: Bùng Nổ
    if vol > VOL_BREAKOUT:
        return "🚀 Bùng Nổ (Dòng tiền nóng)"

    # Tầng 2: Điều kiện cơ bản
    ai_ok   = isinstance(ai_score, float) and ai_score > AI_OK
    base_ok = (
        VOL_ACC_MIN <= vol <= VOL_ACC_MAX and
        price >= ma20 * PRICE_NEAR_MA20   and
        rsi < RSI_WATCHLIST_MAX           and
        ai_ok
    )
    if not base_ok:
        return None

    # Vũ khí 1: Nén Lò Xo Bollinger
    bb_now    = last['bb_width']
    bb_min20  = df['bb_width'].tail(20).min()
    squeezed  = bb_now <= bb_min20 * BB_SQUEEZE_TOL

    # Vũ khí 2: Cạn Cung
    supply_ex = df['can_cung'].tail(5).any()

    # Vũ khí 3: Smart Money (Khối Ngoại hoặc Tự Doanh Gom)
    smart_money = False
    for get_fn in [get_foreign, get_proprietary]:
        flow_df = get_fn(ticker, FOREIGN_DAYS)
        if valid(flow_df) and calc_net_flow(flow_df, FOREIGN_NET_DAYS) > 0:
            smart_money = True
            break

    if squeezed or supply_ex or smart_money:
        return "⚖️ Danh Sách Chờ (Vùng Gom An Toàn)"

    return None


# ==============================================================================
# 9. CACHE: DANH SÁCH MÃ HOSE
# ==============================================================================

@st.cache_data(ttl=3600)
def load_hose_tickers() -> list[str]:
    """
    Tải danh sách mã HOSE, cache 1 giờ.
    Thử nhiều cách gọi API — Vnstock hay đổi cú pháp giữa các phiên bản.
    KHÔNG dùng engine()/session_state vì cache_data chạy context riêng.
    """
    stock = Vnstock()

    attempts = [
        lambda: stock.market.listing(),
        lambda: Vnstock().stock(symbol='ACB', source='VCI').listing.all_symbols(),
    ]

    for attempt in attempts:
        try:
            df = attempt()
            if df is None or df.empty:
                continue
            # Lọc HOSE — thử nhiều tên cột khác nhau
            for col in ['comGroupCode', 'exchange', 'market']:
                if col in df.columns:
                    result = df[df[col].str.upper() == 'HOSE']['ticker'].tolist()
                    if len(result) > 50:
                        return result
            # Không lọc được thì trả về tất cả
            if 'ticker' in df.columns and len(df) > 50:
                return df['ticker'].tolist()
        except Exception as e:
            print(f"[WARN] attempt failed: {e}")
            continue

    print("[WARN] load_hose_tickers: API lỗi, dùng danh sách dự phòng 90 mã")
    return FALLBACK_TICKERS


# ==============================================================================
# [FIX #1] PHÂN NHÓM DÒNG TIỀN 3 LỚP
# ==============================================================================

def classify_flow_group(vol: float, ret: float, net_flow: float) -> dict:
    """
    [FIX #1] Chia dòng tiền thành 3 nhóm:
      🦈 Cá Mập    — vol nổ > 2.5x, dòng tiền ròng dương mạnh
      🏦 Tổ Chức Nội — vol 1.2–2.5x, tổ chức tích lũy
      🐜 Nhỏ Lẻ    — vol < 1.2x, chủ yếu cá nhân

    [FIX #6] Màu sắc Gom/Xả kết hợp 3 yếu tố:
      - Hướng giá (ret > 0 hay < 0)
      - Khối lượng (vol_strength)
      - Dòng tiền ròng (net_flow)
    """
    # Xác định nhóm
    if vol >= VOL_SHARK:
        group       = "🦈 Cá Mập"
        pct         = 0.65
        description = "Tay to / Quỹ ngoại đang hoạt động mạnh"
    elif vol >= VOL_INST_HIGH:
        group       = "🏦 Tổ Chức Nội"
        pct         = 0.45
        description = "Tổ chức nội địa / Tự doanh tích cực"
    else:
        group       = "🐜 Nhỏ Lẻ"
        pct         = 0.15
        description = "Cá nhân nhỏ lẻ chiếm chủ đạo"

    retail_pct = 1 - pct

    # [FIX #6] Logic Gom/Xả đúng: phải hội đủ cả 3 điều kiện
    is_accumulate = ret > 0 and vol >= VOL_PV_SIGNAL and net_flow >= 0
    is_distribute = ret < 0 and vol >= VOL_PV_SIGNAL and net_flow < 0

    if is_accumulate:
        action       = "🟢 GOM HÀNG"
        action_color = "normal"
        action_note  = "Giá tăng + Vol nổ + Dòng tiền ròng dương → Xác nhận tích lũy thực sự"
    elif is_distribute:
        action       = "🔴 XẢ HÀNG"
        action_color = "inverse"
        action_note  = "Giá giảm + Vol nổ + Dòng tiền ròng âm → Xác nhận phân phối thực sự"
    else:
        action       = "🟡 TRUNG LẬP"
        action_color = "off"
        action_note  = "Tín hiệu chưa đủ rõ — chưa đủ 3 điều kiện Gom/Xả đồng thời"

    return {
        'group':        group,
        'inst_pct':     pct,
        'retail_pct':   retail_pct,
        'description':  description,
        'action':       action,
        'action_color': action_color,
        'action_note':  action_note,
    }


# ==============================================================================
# MAIN APPLICATION
# ==============================================================================

if not authenticate():
    st.stop()

# Khởi tạo Vnstock engine một lần duy nhất vào session
if 'vnstock_engine' not in st.session_state:
    st.session_state['vnstock_engine'] = Vnstock()

st.set_page_config(
    page_title="Quant System V20.0 Predator",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🛡️ Quant System V20.0: Master Advisor & Predator Radar")
st.markdown("---")

# --- SIDEBAR ---
tickers  = load_hose_tickers()
st.sidebar.header("🕹️ Trung Tâm Giao Dịch Định Lượng")

# Nút xóa cache — dùng khi danh sách mã không cập nhật đúng
if st.sidebar.button("🔄 Làm mới danh sách mã (Xóa Cache)"):
    st.cache_data.clear()
    st.rerun()

dropdown = st.sidebar.selectbox("Lựa chọn mã cổ phiếu:", tickers)
st.sidebar.caption(f"📊 Tổng số mã đang theo dõi: {len(tickers)}")
manual   = st.sidebar.text_input("Hoặc nhập trực tiếp (VD: FPT):").strip().upper()
ticker   = manual if manual else dropdown

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH",
    "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM",
    "🌊 BÓC TÁCH DÒNG TIỀN",
    "🔍 RADAR TRUY QUÉT SIÊU CỔ PHIẾU",
])


# ==============================================================================
# TAB 1: ROBOT ADVISOR & BẢN PHÂN TÍCH TỰ ĐỘNG  [FIX #7: đúng tab1]
# ==============================================================================
with tab1:
    if st.button(f"⚡ TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG TOÀN DIỆN MÃ CỔ PHIẾU {ticker}"):
        with st.spinner(f"Đang đồng bộ dữ liệu đa tầng cho {ticker}..."):

            df_raw = get_price(ticker)
            if not valid(df_raw):
                st.error("❌ Không thể tải dữ liệu giá. Vui lòng F5 lại.")
                st.stop()

            df   = calc_indicators(df_raw)
            last = df.iloc[-1]

            ai_score = predict_ai_t3(df)
            winrate  = run_backtest(df)
            sent_label, sent_val = analyze_sentiment(df)
            growth   = get_earnings_growth(ticker)
            sr       = calc_support_resistance(last)   # [FIX #2]

            # Market Breadth
            buy_set, sell_set = set(), set()
            for p in PILLARS:
                try:
                    dp = get_price(p, days=10)
                    if valid(dp):
                        dp = calc_indicators(dp)
                        rp = dp.iloc[-1]
                        if rp['return_1d'] > 0 and rp['vol_strength'] > VOL_PV_SIGNAL:
                            buy_set.add(p)
                        elif rp['return_1d'] < 0 and rp['vol_strength'] > VOL_PV_SIGNAL:
                            sell_set.add(p)
                except Exception:
                    pass

            # --- Nhà phân tích ảo ---
            st.markdown(
                "> 🧠 **Nhà Phân Tích Ảo:** Tự động gom nhặt các con số khô khan, lắp ghép lại "
                "và viết ra một bài văn phân tích chi tiết dễ hiểu. "
                "Khai triển tối đa để chống nén code."
            )

            st.write(f"### 🎯 BẢN PHÂN TÍCH CHUYÊN MÔN TỰ ĐỘNG — MÃ {ticker}")
            col_report, col_signal = st.columns([2, 1])

            with col_report:
                report = generate_report(ticker, last, ai_score, winrate, buy_set, sell_set)
                st.info(report)

            with col_signal:
                st.subheader("🤖 ROBOT ĐỀ XUẤT LỆNH HIỆN TẠI:")
                signal, color = advisor_signal(last, ai_score, winrate, growth)
                st.title(f":{color}[{signal}]")

            st.divider()

            # --- [FIX #2] Radar Đỉnh / Đáy ---
            st.write("### 📡 Radar Đỉnh / Đáy — Vị Trí Giá Hiện Tại")
            sr_col1, sr_col2, sr_col3 = st.columns(3)

            sr_col1.metric(
                "📉 Khoảng cách đến Hỗ Trợ MA20",
                f"{sr['dist_to_support']:+.2f}%",
                delta="Trên MA20 ✓" if sr['dist_to_support'] > 0 else "Dưới MA20 ⚠️",
                delta_color="normal" if sr['dist_to_support'] > 0 else "inverse"
            )
            sr_col2.metric(
                "📈 Room còn lại đến Kháng Cự BB",
                f"{sr['dist_to_resistance']:+.2f}%",
                delta="Chưa chạm trần ✓" if sr['dist_to_resistance'] > 3 else "Gần trần ⚠️",
                delta_color="normal" if sr['dist_to_resistance'] > 3 else "inverse"
            )
            sr_col3.metric(
                "🛡️ Cắt Lỗ (SL -7%)",
                f"{last['close'] * (1 - SL_PCT):,.0f} VNĐ",
                delta="-7% từ giá hiện tại",
                delta_color="off"
            )
            if "🚨" in sr['warning']:
                st.error(sr['warning'])
            elif "💡" in sr['warning']:
                st.success(sr['warning'])
            else:
                st.warning(sr['warning'])

            st.divider()

            # --- Bảng Radar ---
            st.write("### 🧭 Bảng Radar Hiệu Suất Tổng Quan")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Giá Khớp Lệnh",   f"{last['close']:,.0f}")
            c2.metric("Tâm Lý F&G",       f"{sent_val}/100",  delta=sent_label)
            c3.metric("AI T+3 Dự Báo",    f"{ai_score}%",
                      delta="Tín hiệu Tốt" if isinstance(ai_score, float) and ai_score > AI_GOOD else None)
            c4.metric("Winrate Lịch Sử",  f"{winrate}%",
                      delta="Ổn định" if winrate > ADV_WINRATE_GOOD else None)

            st.divider()

            # --- Naked Stats ---
            st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Trần")
            n1, n2, n3, n4 = st.columns(4)

            rsi_v = last['rsi']
            n1.metric("RSI (14 Phiên)", f"{rsi_v:.1f}",
                      delta="Quá Mua"  if rsi_v > RSI_OVERBOUGHT else
                            ("Quá Bán" if rsi_v < RSI_OVERSOLD   else "Vùng An Toàn"))

            macd_v, sig_v = last['macd'], last['signal']
            n2.metric("MACD vs Signal", f"{macd_v:.2f}",
                      delta="MACD > Signal ✓" if macd_v > sig_v else "MACD < Signal ✗")

            n3.metric("MA20 / MA50", f"{last['ma20']:,.0f}",
                      delta=f"MA50: {last['ma50']:,.0f}")

            n4.metric("Trần Bollinger", f"{last['upper_band']:,.0f}",
                      delta=f"Đáy: {last['lower_band']:,.0f}", delta_color="inverse")

            st.divider()

            # [FIX #5] CẨM NANG: Bí kíp Né Bẫy Giá (False Breakout)
            st.write("### 📖 CẨM NANG — Bí Kíp Né Bẫy Giá (False Breakout)")
            with st.expander("🚀 Mở rộng để đọc bí kíp — Dành riêng cho Minh"):
                st.markdown("""
**False Breakout (Bẫy Bứt Phá Giả) là gì?**
> Giá vượt ngưỡng kháng cự nhưng **không duy trì được** rồi quay đầu giảm ngay — đây là bẫy
> phổ biến nhất mà nhỏ lẻ bị dính phải khi thấy giá "phá đỉnh" và mua đuổi.

---

**🔴 DẤU HIỆU NHẬN BIẾT BẪY:**

1. **Khối lượng thấp khi phá đỉnh** — Giá tăng nhưng vol < 1.2x MA10 → thiếu lực xác nhận.
2. **Nến bấc trên dài** — Giá lên nhưng đóng cửa thấp hơn nhiều → phe bán mạnh hơn.
3. **RSI vượt 70 ngay khi phá đỉnh** — Quá mua tức thì, không có đà tích lũy trước.
4. **Giá vượt Bollinger Band trên** — Vùng kháng cự thống kê cực mạnh, xác suất đảo chiều cao.
5. **Khối Ngoại / Tự Doanh bán ròng khi giá tăng** — Tổ chức xả hàng cho nhỏ lẻ mua.

---

**✅ QUY TẮC VÀO LỆNH AN TOÀN (Tránh Bẫy):**

- ⏳ **Chờ nến xác nhận:** Không mua ngay phiên phá đỉnh — chờ nến tiếp theo đóng cửa trên
  kháng cự mới vào.
- 📊 **Vol phải nổ:** Khối lượng phiên phá đỉnh phải ≥ 1.5x MA20 mới tin.
- 🔍 **Kiểm tra RSI:** RSI lý tưởng khi phá đỉnh là 50–65 (còn dư địa), tránh khi RSI > 70.
- 🛡️ **Luôn đặt SL -7%:** Mua xong đặt ngay lệnh cắt lỗ -7% từ giá mua — bắt buộc.
- 🏦 **Xem dòng tiền ròng:** Sang Tab 3 kiểm tra Khối Ngoại/Tự Doanh đang Gom hay Xả.

---

**💡 GHI NHỚ:**
> "Không có breakout nào đáng tin nếu không có khối lượng đi kèm."
> — Nguyên tắc vàng của William O'Neil (CANSLIM)
                """)

            st.divider()

            # --- Master Chart ---
            st.write("### 📊 Biểu Đồ Kỹ Thuật Đa Lớp Chuyên Nghiệp")
            chart = df.tail(CHART_DAYS)
            x     = chart['date']

            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                vertical_spacing=0.03, row_heights=[0.75, 0.25]
            )
            fig.add_trace(go.Candlestick(
                x=x, open=chart['open'], high=chart['high'],
                low=chart['low'],  close=chart['close'], name='Nến OHLC'
            ), row=1, col=1)
            fig.add_trace(go.Scatter(x=x, y=chart['ma20'],
                line=dict(color='orange', width=1.5), name='MA20'), row=1, col=1)
            fig.add_trace(go.Scatter(x=x, y=chart['ma200'],
                line=dict(color='purple', width=2),  name='MA200'), row=1, col=1)
            fig.add_trace(go.Scatter(x=x, y=chart['upper_band'],
                line=dict(color='gray', dash='dash', width=0.8), name='Trần BOL'), row=1, col=1)
            fig.add_trace(go.Scatter(x=x, y=chart['lower_band'],
                line=dict(color='gray', dash='dash', width=0.8),
                fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='Đáy BOL'), row=1, col=1)
            fig.add_trace(go.Bar(x=x, y=chart['volume'],
                name='Khối Lượng', marker_color='gray'), row=2, col=1)
            fig.update_layout(
                height=750, template='plotly_white',
                xaxis_rangeslider_visible=False,
                margin=dict(l=40, r=40, t=50, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)


# ==============================================================================
# TAB 2: TÀI CHÍNH CƠ BẢN & CANSLIM
# ==============================================================================
with tab2:
    st.write(f"### 📈 Phân Tích Sức Khỏe Tài Chính — {ticker}")

    with st.spinner("Đang quét báo cáo thu nhập quý gần nhất..."):
        growth = get_earnings_growth(ticker)

        if growth is not None:
            if growth >= CANSLIM_GREAT:
                st.success(f"🔥 **Tiêu Chuẩn Vàng (Chữ C CANSLIM):** LNST tăng mạnh **+{growth}%**.")
            elif growth > 0:
                st.info(f"⚖️ **Tăng Trưởng Bền Vững:** LNST tăng **{growth}%**.")
            else:
                st.error(f"🚨 **Suy Yếu Nặng:** LNST giảm **{growth}%**.")
        else:
            st.warning("⚠️ Không lấy được dữ liệu LNST.")

        st.divider()
        pe, roe = get_pe_roe(ticker)
        c1, c2  = st.columns(2)

        # [FIX #4] P/E ngưỡng >20 + giải thích "Số năm thu hồi vốn"
        if pe is None:
            c1.metric("P/E (Số Năm Thu Hồi Vốn)", "N/A",
                      delta="Lỗi API / Thiếu dữ liệu", delta_color="off")
        else:
            if pe < PE_CHEAP:
                pe_label, pe_color = "✅ Rất Tốt — Định Giá Rẻ", "normal"
            elif pe < PE_OK:
                pe_label, pe_color = "⚖️ Hợp Lý — Vùng Trung Bình", "normal"
            else:
                pe_label, pe_color = "🚨 Đắt Đỏ — Rủi Ro Cao (> 20 năm hoàn vốn)", "inverse"
            c1.metric("P/E (Số Năm Thu Hồi Vốn)", f"{pe:.1f} năm",
                      delta=pe_label, delta_color=pe_color)

        st.write(
            "> **P/E là gì?** Bạn bỏ ra P/E năm để thu hồi vốn từ lợi nhuận công ty. "
            "P/E = 15 → mất 15 năm hoàn vốn. **Dưới 12 = rẻ. Trên 20 = đắt, rủi ro cao.**"
        )

        # ROE
        if roe is None:
            c2.metric("ROE (Sinh Lời Trên Vốn)", "N/A",
                      delta="Lỗi API / Thiếu dữ liệu", delta_color="off")
        else:
            if roe >= ROE_EXCELLENT:
                roe_label, roe_color = "✅ Vô Cùng Xuất Sắc (≥ 25%)", "normal"
            elif roe >= ROE_GOOD:
                roe_label, roe_color = "⚖️ Tốt (15–25%)", "normal"
            else:
                roe_label, roe_color = "🚨 Dưới Chuẩn (< 15%)", "inverse"
            c2.metric("ROE (Sinh Lời Trên Vốn)", f"{roe:.1%}",
                      delta=roe_label, delta_color=roe_color)

        st.write("> **ROE:** Đo hiệu quả dùng vốn. Phải ≥ 15% mới đáng xem xét đầu tư dài hạn.")


# ==============================================================================
# TAB 3: DÒNG TIỀN THÔNG MINH  [FIX #1, #6]
# ==============================================================================
with tab3:
    st.write(f"### 🌊 Smart Flow Specialist — Mổ Xẻ Hành Vi Dòng Tiền ({ticker})")

    # --- Dữ liệu Khối Ngoại thực tế ---
    st.write("#### 📊 Giao Dịch Khối Ngoại Thực Tế (Tỷ VNĐ):")
    with st.spinner("Đang trích xuất dữ liệu Khối Ngoại..."):
        df_for = get_foreign(ticker)

        if valid(df_for):
            last_f = df_for.iloc[-1]
            buy_v  = to_billion(last_f.get('buyval',  0))
            sell_v = to_billion(last_f.get('sellval', 0))
            net_v  = to_billion(last_f.get('netval', buy_v - sell_v))

            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng Mua (Khối Ngoại)", f"{buy_v:.2f} Tỷ")
            c2.metric("Tổng Bán (Khối Ngoại)", f"{sell_v:.2f} Tỷ")
            c3.metric("Giao Dịch Ròng", f"{net_v:.2f} Tỷ",
                      delta="Mua Ròng ✓" if net_v > 0 else "Bán Ròng ⚠️",
                      delta_color="normal" if net_v > 0 else "inverse")

            # Biểu đồ 10 phiên
            x_dates  = df_for['date'].tail(10) if 'date' in df_for.columns else df_for.index[-10:]
            net_vals = []
            for _, row in df_for.tail(10).iterrows():
                b = to_billion(row.get('buyval',  0))
                s = to_billion(row.get('sellval', 0))
                n = to_billion(row.get('netval',  b - s))
                net_vals.append(n)

            colors = ['green' if v > 0 else 'red' for v in net_vals]
            fig_f  = go.Figure(go.Bar(x=x_dates, y=net_vals,
                                       marker_color=colors, name="Ròng (Tỷ VNĐ)"))
            fig_f.update_layout(height=300, title="Khối Ngoại Mua/Bán Ròng (Tỷ VNĐ)",
                                  margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_f, use_container_width=True)
        else:
            net_v = 0.0
            st.warning("⚠️ Không lấy được dữ liệu Khối Ngoại. Chuyển sang mô hình Ước Lượng.")

    st.divider()

    # [FIX #1 + #6] Phân nhóm dòng tiền 3 lớp + Logic Gom/Xả chuẩn
    df_flow = get_price(ticker, days=30)
    if valid(df_flow):
        df_flow  = calc_indicators(df_flow)
        last_fl  = df_flow.iloc[-1]
        vol      = last_fl['vol_strength']
        ret      = last_fl['return_1d']

        flow_info = classify_flow_group(vol, ret, net_v)

        st.write("#### 📊 Phân Tích Dòng Tiền 3 Nhóm (AI Ước Tính theo Volume + Flow):")
        g1, g2, g3 = st.columns(3)

        # Nhóm chiếm % nhiều nhất = nhóm đang hoạt động chính
        inst_pct   = flow_info['inst_pct']
        retail_pct = flow_info['retail_pct']

        if flow_info['group'] == "🦈 Cá Mập":
            shark_pct = inst_pct           # Cá mập chiếm phần lớn
            org_pct   = max(0, 1 - shark_pct - retail_pct)
        elif flow_info['group'] == "🏦 Tổ Chức Nội":
            shark_pct = 0.05              # Cá mập nhỏ
            org_pct   = inst_pct - shark_pct
        else:
            shark_pct = 0.02
            org_pct   = 0.13

        retail_pct_final = max(0, 1 - shark_pct - org_pct)

        g1.metric("🦈 Cá Mập (Quỹ Ngoại / Tay To)",
                  f"{shark_pct*100:.1f}%",
                  delta="Đang Hoạt Động Mạnh" if flow_info['group'] == "🦈 Cá Mập" else "Ít Tham Gia",
                  delta_color="normal" if flow_info['group'] == "🦈 Cá Mập" else "off")

        g2.metric("🏦 Tổ Chức Nội (Tự Doanh / Quỹ Nội)",
                  f"{org_pct*100:.1f}%",
                  delta="Đang Tích Lũy" if flow_info['group'] == "🏦 Tổ Chức Nội" else "Bình Thường",
                  delta_color="normal" if flow_info['group'] == "🏦 Tổ Chức Nội" else "off")

        g3.metric("🐜 Nhỏ Lẻ (Cá Nhân)",
                  f"{retail_pct_final*100:.1f}%",
                  delta="⚠️ Đu Bám Nhiều" if retail_pct_final > 0.6 else "Ổn Định",
                  delta_color="inverse" if retail_pct_final > 0.6 else "off")

        st.info(f"**Nhóm chủ đạo:** {flow_info['group']} — {flow_info['description']}")

        st.divider()

        # [FIX #6] Hành động Gom/Xả với màu sắc đúng
        st.write("#### 🎯 Kết Luận Hành Vi Dòng Tiền:")
        action_msg = f"**{flow_info['action']}**\n\n_{flow_info['action_note']}_"

        if "GOM" in flow_info['action']:
            st.success(action_msg)
        elif "XẢ" in flow_info['action']:
            st.error(action_msg)
        else:
            st.warning(action_msg)


# ==============================================================================
# TAB 4: RADAR TRUY QUÉT SIÊU CỔ PHIẾU  [FIX #7: đúng tab4, #8: RADAR_MAX=150, #9: ghi chú]
# ==============================================================================
with tab4:
    st.subheader("🔍 Máy Quét Định Lượng Robot Hunter V20.0 — Predator Leviathan")
    st.write(
        "Giải pháp tối thượng dành cho Minh: Tự động phân loại cổ phiếu thành "
        "**BÙNG NỔ** (đã chạy nóng — Cẩn thận rủi ro mua đuổi đỉnh như VIC) và "
        "**DANH SÁCH CHỜ CHÂN SÓNG** (tích hợp 3 vũ khí: Squeeze, Cạn Cung, "
        "Tây/Tự Doanh Gom) để tránh mua đuổi đỉnh."
    )

    # [FIX #9] Ghi chú quan trọng
    st.info(
        "💡 **Lưu ý quan trọng:** Không xuất hiện trong Radar ≠ Cổ phiếu xấu. "
        "Radar chỉ lọc những mã **đang hội tụ đủ tín hiệu kỹ thuật tại thời điểm quét**. "
        "Mã tốt như PDR có thể đang ở giai đoạn tích lũy chưa đủ Vol nổ — "
        "hãy dùng Tab 1 để phân tích riêng từng mã."
    )

    if st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT 2 TẦNG (REAL-TIME)"):
        # [FIX #8] Quét 150 mã thay vì 30 để không bỏ sót PDR và các mã P-Z
        scan_list = tickers[:RADAR_MAX]
        st.caption(f"🔭 Đang quét {len(scan_list)} mã trên HOSE...")

        progress  = st.progress(0)
        breakouts = []
        watchlist = []

        for i, t in enumerate(scan_list):
            try:
                df_s = get_price(t, days=SCAN_DAYS)
                if not valid(df_s):
                    continue

                df_s  = calc_indicators(df_s)
                ai_s  = predict_ai_t3(df_s)
                label = classify_stock(t, df_s, ai_s)

                if label is None:
                    continue

                last_s = df_s.iloc[-1]

                bb_now   = last_s['bb_width']
                bb_min20 = df_s['bb_width'].tail(20).min()
                squeezed = bb_now <= bb_min20 * BB_SQUEEZE_TOL
                supply   = df_s['can_cung'].tail(5).any()
                smart    = False
                for fn in [get_foreign, get_proprietary]:
                    fd = fn(t, FOREIGN_DAYS)
                    if valid(fd) and calc_net_flow(fd, FOREIGN_NET_DAYS) > 0:
                        smart = True
                        break

                row = {
                    'Ticker':           t,
                    'Thị Giá':          f"{last_s['close']:,.0f} VNĐ",
                    'Vol Strength':     round(last_s['vol_strength'], 2),
                    'RSI':              f"{last_s['rsi']:.1f}",
                    'AI T+3':           f"{ai_s}%",
                    'Lò Xo Bollinger':  "🌀 Nén Chặt" if squeezed else "-",
                    'Cạn Cung':         "💧 Cạn Cung" if supply   else "-",
                    'Tổ Chức Gom':      "🦈 Đang Gom" if smart    else "-",
                }

                (breakouts if "Bùng Nổ" in label else watchlist).append(row)

            except Exception as e:
                print(f"[WARN] Scan {t}: {e}")

            progress.progress((i + 1) / len(scan_list))

        # --- Kết quả ---
        st.write("### 🚀 Nhóm Bùng Nổ (Đã nổ Vol — Cẩn thận rủi ro mua đuổi đỉnh như VIC)")
        if breakouts:
            st.table(pd.DataFrame(breakouts))
        else:
            st.write("Không tìm thấy mã bùng nổ mạnh hôm nay.")

        st.write("### ⚖️ Nhóm Danh Sách Chờ Chân Sóng (Gom chân sóng — Cực kỳ an toàn)")
        if watchlist:
            st.table(pd.DataFrame(watchlist))
            st.success(
                "✅ **Robot khuyên:** Ưu tiên giải ngân vào nhóm này — "
                "giá sát MA20, hội tụ tín hiệu Nén Lò Xo / Cạn Cung / Tổ Chức Gom, "
                "rủi ro đu đỉnh cực thấp."
            )
        else:
            st.write("Hôm nay chưa có mã tích lũy chân sóng đủ tiêu chuẩn khắt khe.")


# ==============================================================================
# HẾT MÃ NGUỒN — QUANT SYSTEM V20.0 FINAL BUILD (9 FIXES APPLIED)
# ==============================================================================
