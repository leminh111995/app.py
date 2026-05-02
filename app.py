# ==============================================================================
# QUANT SYSTEM V20.0 - THE PREDATOR LEVIATHAN
# Tác giả: Minh | Clean Code Edition — Viết lại hoàn toàn
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
VOL_INST_HIGH     = 1.8     # tổ chức chiếm 55%
VOL_INST_MID      = 1.2     # tổ chức chiếm 40%
VOL_PV_SIGNAL     = 1.2     # ngưỡng pv_trend

# Bollinger
BB_SQUEEZE_TOL    = 1.2     # sai số chấp nhận khi xác nhận nén

# Cạn Cung
SUPPLY_RATIO      = 0.8     # vol < 80% MA20 → cạn cung

# Giá so MA20
PRICE_NEAR_MA20   = 0.95    # giá >= 95% MA20 → an toàn

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

# Tài chính
CANSLIM_GREAT     = 20.0
PE_CHEAP          = 12
PE_OK             = 18
ROE_EXCELLENT     = 0.25
ROE_GOOD          = 0.15

# Radar
RADAR_MAX         = 30
SCAN_DAYS         = 100
FOREIGN_DAYS      = 5
FOREIGN_NET_DAYS  = 3

# Chart
CHART_DAYS        = 120

# Mã trụ thị trường
PILLARS = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]
FALLBACK_TICKERS  = ["FPT", "HPG", "SSI", "TCB", "MWG", "VNM", "VIC", "VHM", "STB", "MSN", "GAS"]


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
    df = None

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

    # Làm sạch cột trùng
    df = df.loc[:, ~df.columns.duplicated()]

    # Ép kiểu số
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Forward-fill lỗ hổng
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
    std20           = close.rolling(20).std()
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
    ema12     = close.ewm(span=12, adjust=False).mean()
    ema26     = close.ewm(span=26, adjust=False).mean()
    df['macd']   = ema12 - ema26
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # --- Volume & Flow ---
    df['return_1d']   = close.pct_change()
    vol_avg10         = volume.rolling(10).mean()
    df['vol_strength'] = volume / (vol_avg10 + 1e-9)
    df['money_flow']  = close * volume
    df['volatility']  = df['return_1d'].rolling(20).std()
    df['vol_avg_20']  = volume.rolling(20).mean()

    # --- Cạn Cung ---
    df['is_red_candle'] = close < open_
    df['can_cung'] = df['is_red_candle'] & (volume < df['vol_avg_20'] * SUPPLY_RATIO)

    # --- PV Trend ---
    is_explosion = df['vol_strength'] > VOL_PV_SIGNAL
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
    if   rsi > 75:        label = "🔥 CỰC KỲ THAM LAM (Vùng Quá Mua)"
    elif rsi > 60:        label = "⚖️ THAM LAM (Hưng Phấn)"
    elif rsi < RSI_OVERSOLD: label = "💀 CỰC KỲ SỢ HÃI (Vùng Quá Bán)"
    elif rsi < RSI_COLD:  label = "😨 SỢ HÃI (Bi Quan)"
    else:                 label = "🟡 TRUNG LẬP (Đi Ngang)"
    return label, round(rsi, 1)


def run_backtest(df: pd.DataFrame) -> float:
    """
    Backtest: Mua khi RSI < 45 & MACD cắt lên.
    Mục tiêu: +5% trong 10 ngày.
    Trả về winrate (%).
    """
    signals = wins = 0
    n = len(df)

    for i in range(100, n - BT_DAYS_FWD):
        rsi_ok = df['rsi'].iloc[i] < BT_RSI_BUY
        macd_cross = (
            df['macd'].iloc[i]   > df['signal'].iloc[i] and
            df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
        )
        if rsi_ok and macd_cross:
            signals += 1
            buy_price = df['close'].iloc[i]
            target    = buy_price * (1 + BT_PROFIT)
            future    = df['close'].iloc[i+1 : i+1+BT_DAYS_FWD]
            if any(future > target):
                wins += 1

    return round((wins / signals) * 100, 1) if signals else 0.0


def predict_ai_t3(df: pd.DataFrame) -> float | str:
    """
    Random Forest: dự báo xác suất tăng ≥ 2% sau T+3.
    Train trên lịch sử, dự báo ngày hiện tại.
    """
    if len(df) < AI_MIN_ROWS:
        return "N/A"

    df2 = df.copy()
    df2['target'] = (df2['close'].shift(-3) > df2['close'] * AI_PROFIT_T3).astype(int)
    df2 = df2.dropna()

    features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility', 'vol_strength', 'money_flow', 'pv_trend']
    X, y = df2[features], df2['target']

    # Bỏ 3 ngày cuối để tránh look-ahead bias
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X[:-3], y[:-3])

    prob = model.predict_proba(X.iloc[[-1]])[0][1]
    return round(prob * 100, 1)


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
    # Phương án A: Vnstock
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

    # Phương án B: Yahoo Finance
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

    # Phương án A: Vnstock
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

    # Phương án B: Yahoo Finance
    if pe is None:
        try:
            info = yf.Ticker(f"{ticker}.VN").info
            pe  = info.get('trailingPE') or pe
            roe = roe or info.get('returnOnEquity')
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

    buy  = score >= ADV_BUY_SCORE  and rsi < RSI_HOT
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
    Trả về nhãn phân loại hoặc None nếu không đạt.
    """
    last  = df.iloc[-1]
    vol   = last['vol_strength']
    rsi   = last['rsi']
    price = last['close']
    ma20  = last['ma20']

    # --- Tầng 1: Bùng Nổ ---
    if vol > VOL_BREAKOUT:
        return "🚀 Bùng Nổ (Dòng tiền nóng)"

    # --- Tầng 2: Điều kiện cơ bản ---
    ai_ok    = isinstance(ai_score, float) and ai_score > AI_OK
    base_ok  = (
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
    """Tải danh sách mã HOSE, cache 1 giờ để tránh gọi API liên tục."""
    try:
        df = engine().market.listing()
        return df[df['comGroupCode'] == 'HOSE']['ticker'].tolist()
    except Exception:
        return FALLBACK_TICKERS


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
tickers = load_hose_tickers()
st.sidebar.header("🕹️ Trung Tâm Giao Dịch Định Lượng")
dropdown = st.sidebar.selectbox("Lựa chọn mã cổ phiếu:", tickers)
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
# TAB 1: ROBOT ADVISOR & BẢN PHÂN TÍCH TỰ ĐỘNG
# ==============================================================================
with tab1:
    if st.button(f"⚡ PHÂN TÍCH ĐỊNH LƯỢNG TOÀN DIỆN — MÃ {ticker}"):
        with st.spinner(f"Đang đồng bộ dữ liệu đa tầng cho {ticker}..."):

            # --- Lấy & tính chỉ báo ---
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

            # --- Market Breadth: quét 10 mã trụ ---
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

            # --- Bố cục chính ---
            st.write(f"### 🎯 BẢN PHÂN TÍCH TỰ ĐỘNG — MÃ {ticker}")
            col_report, col_signal = st.columns([2, 1])

            with col_report:
                report = generate_report(ticker, last, ai_score, winrate, buy_set, sell_set)
                st.info(report)

            with col_signal:
                st.subheader("🤖 ROBOT ĐỀ XUẤT LỆNH:")
                signal, color = advisor_signal(last, ai_score, winrate, growth)
                st.title(f":{color}[{signal}]")

            st.divider()

            # --- Bảng Radar ---
            st.write("### 🧭 Bảng Radar Hiệu Suất Tổng Quan")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Giá Khớp Lệnh",       f"{last['close']:,.0f}")
            c2.metric("Tâm Lý F&G",           f"{sent_val}/100",  delta=sent_label)
            c3.metric("AI T+3 Dự Báo",        f"{ai_score}%",
                      delta="Tín hiệu Tốt" if isinstance(ai_score, float) and ai_score > AI_GOOD else None)
            c4.metric("Winrate Lịch Sử",      f"{winrate}%",
                      delta="Ổn định" if winrate > ADV_WINRATE_GOOD else None)

            st.divider()

            # --- Naked Stats ---
            st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật Trần")
            n1, n2, n3, n4 = st.columns(4)

            rsi_v = last['rsi']
            n1.metric("RSI (14 Phiên)", f"{rsi_v:.1f}",
                      delta="Quá Mua" if rsi_v > RSI_OVERBOUGHT else
                            ("Quá Bán" if rsi_v < RSI_OVERSOLD else "Vùng An Toàn"))

            macd_v, sig_v = last['macd'], last['signal']
            n2.metric("MACD vs Signal", f"{macd_v:.2f}",
                      delta="MACD > Signal ✓" if macd_v > sig_v else "MACD < Signal ✗")

            n3.metric("MA20 / MA50", f"{last['ma20']:,.0f}",
                      delta=f"MA50: {last['ma50']:,.0f}")

            n4.metric("Trần Bollinger", f"{last['upper_band']:,.0f}",
                      delta=f"Đáy: {last['lower_band']:,.0f}", delta_color="inverse")

            # --- Master Chart ---
            st.divider()
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

        # P/E
        if pe is None:
            c1.metric("P/E (Số Năm Hoàn Vốn)", "N/A",
                      delta="Lỗi API / Thiếu dữ liệu", delta_color="off")
        else:
            if pe < PE_CHEAP:
                pe_label, pe_color = "Rất Tốt (Định Giá Rẻ)", "normal"
            elif pe < PE_OK:
                pe_label, pe_color = "Khá Hợp Lý", "normal"
            else:
                pe_label, pe_color = "Đắt Đỏ (Rủi ro)", "inverse"
            c1.metric("P/E (Số Năm Hoàn Vốn)", f"{pe:.1f}",
                      delta=pe_label, delta_color=pe_color)

        st.write("> **P/E:** Càng thấp = mua được 1 đồng lợi nhuận càng rẻ. N/A = API đang bảo trì.")

        # ROE
        if roe is None:
            c2.metric("ROE (Sinh Lời Trên Vốn)", "N/A",
                      delta="Lỗi API / Thiếu dữ liệu", delta_color="off")
        else:
            if roe >= ROE_EXCELLENT:
                roe_label, roe_color = "Vô Cùng Xuất Sắc", "normal"
            elif roe >= ROE_GOOD:
                roe_label, roe_color = "Tốt", "normal"
            else:
                roe_label, roe_color = "Dưới Chuẩn", "inverse"
            c2.metric("ROE (Sinh Lời Trên Vốn)", f"{roe:.1%}",
                      delta=roe_label, delta_color=roe_color)

        st.write("> **ROE:** Phải ≥ 15% mới đáng xem xét đầu tư dài hạn.")


# ==============================================================================
# TAB 3: DÒNG TIỀN THÔNG MINH
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
            x_dates = df_for['date'].tail(10) if 'date' in df_for.columns else df_for.index[-10:]
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
            st.warning("⚠️ Không lấy được dữ liệu Khối Ngoại. Chuyển sang mô hình Ước Lượng.")

    st.divider()

    # --- Ước lượng tỷ lệ tổ chức / nhỏ lẻ theo Volume ---
    df_flow = get_price(ticker, days=30)
    if valid(df_flow):
        df_flow  = calc_indicators(df_flow)
        last_fl  = df_flow.iloc[-1]
        vol      = last_fl['vol_strength']

        inst_pct   = 0.55 if vol > VOL_INST_HIGH else (0.40 if vol > VOL_INST_MID else 0.15)
        retail_pct = 1 - inst_pct

        st.write("#### 📊 Tỷ Lệ Dòng Tiền Tổ Chức vs Nhỏ Lẻ (AI Ước Tính theo Volume):")
        c1, c2 = st.columns(2)
        inst_act = "Đang Tích Cực Kê Gom" if last_fl['return_1d'] > 0 else "Đang Nhồi Lệnh Xả"
        c1.metric("🏦 Tổ Chức & Tự Doanh", f"{inst_pct*100:.1f}%", delta=inst_act)

        retail_label = "Cảnh Báo: Nhỏ Lẻ Đu Bám Nhiều" if retail_pct > 0.6 else "Ổn Định"
        retail_color = "inverse" if retail_pct > 0.6 else "normal"
        c2.metric("🐜 Cá Nhân (Nhỏ Lẻ)", f"{retail_pct*100:.1f}%",
                  delta=retail_label, delta_color=retail_color)


# ==============================================================================
# TAB 4: RADAR TRUY QUÉT SIÊU CỔ PHIẾU
# ==============================================================================
with tab4:
    st.subheader("🔍 Máy Quét Robot Hunter V20.0 — Predator Leviathan")
    st.write(
        "Tự động phân loại **BÙNG NỔ** (đã chạy nóng) và "
        "**DANH SÁCH CHỜ** (Squeeze + Cạn Cung + Tây/Tự Doanh Gom) "
        "để tránh mua đuổi đỉnh."
    )

    if st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT 2 TẦNG (REAL-TIME)"):
        scan_list  = tickers[:RADAR_MAX]
        progress   = st.progress(0)
        breakouts  = []
        watchlist  = []

        for i, t in enumerate(scan_list):
            try:
                df_s = get_price(t, days=SCAN_DAYS)
                if not valid(df_s):
                    continue

                df_s    = calc_indicators(df_s)
                ai_s    = predict_ai_t3(df_s)
                label   = classify_stock(t, df_s, ai_s)

                if label is None:
                    continue

                last_s  = df_s.iloc[-1]

                # Xác định trạng thái 3 vũ khí để hiển thị bảng
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
                    'Ticker':             t,
                    'Thị Giá':            f"{last_s['close']:,.0f} VNĐ",
                    'Vol Strength':        round(last_s['vol_strength'], 2),
                    'RSI':                f"{last_s['rsi']:.1f}",
                    'AI T+3':             f"{ai_s}%",
                    'Lò Xo Bollinger':    "🌀 Nén Chặt" if squeezed else "-",
                    'Cạn Cung':           "💧 Cạn Cung" if supply   else "-",
                    'Tổ Chức Gom':        "🦈 Đang Gom" if smart    else "-",
                }

                (breakouts if "Bùng Nổ" in label else watchlist).append(row)

            except Exception as e:
                print(f"[WARN] Scan {t}: {e}")

            progress.progress((i + 1) / len(scan_list))

        # --- Kết quả ---
        st.write("### 🚀 Nhóm Bùng Nổ (Đã nổ Vol — Cẩn thận mua đuổi đỉnh)")
        if breakouts:
            st.table(pd.DataFrame(breakouts))
        else:
            st.write("Không tìm thấy mã bùng nổ hôm nay.")

        st.write("### ⚖️ Nhóm Danh Sách Chờ (Gom Chân Sóng — Cực kỳ an toàn)")
        if watchlist:
            st.table(pd.DataFrame(watchlist))
            st.success(
                "✅ **Robot khuyên:** Ưu tiên giải ngân vào nhóm này — "
                "giá sát MA20, hội tụ tín hiệu nén lò xo / cạn cung, rủi ro đu đỉnh cực thấp."
            )
        else:
            st.write("Hôm nay chưa có mã tích lũy chân sóng đủ tiêu chuẩn.")


# ==============================================================================
# HẾT MÃ NGUỒN — QUANT SYSTEM V20.0 CLEAN CODE EDITION
# ==============================================================================
