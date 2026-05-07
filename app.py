# ==============================================================================
# QUANT SYSTEM V23.0 - THE PREDATOR LEVIATHAN SUPREME
# Tác giả: Minh
# V22: ATR Stop | ADX+OBV | Kelly | Cache AI | Sharpe+MaxDD | Radar Display
# V23: RS Rating | RSI/MACD Divergence | Market Breadth | VWAP | 52W High
#      Ichimoku Cloud | Chân Sóng Detection nâng cao
# ==============================================================================

# --- IMPORTS ---
import streamlit as st
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# ==============================================================================
# CONSTANTS
# ==============================================================================
DATE_FMT          = '%Y-%m-%d'
TZ_VN             = ZoneInfo("Asia/Ho_Chi_Minh")
HISTORY_DAYS      = 1000

# RSI
RSI_PERIOD        = 14
RSI_OVERBOUGHT    = 70
RSI_OVERSOLD      = 30
RSI_HOT           = 68
RSI_COLD          = 42
RSI_WATCHLIST_MAX = 62

# Volume
VOL_BREAKOUT      = 1.3
VOL_ACC_MIN       = 0.8
VOL_ACC_MAX       = 1.2
VOL_SHARK         = 2.5
VOL_INST_HIGH     = 1.8
VOL_INST_MID      = 1.2
VOL_PV_SIGNAL     = 1.2

# Bollinger
BB_SQUEEZE_TOL    = 1.2

# Cạn Cung
SUPPLY_RATIO      = 0.8

# Giá so MA20
PRICE_NEAR_MA20   = 0.95

# Phí giao dịch thực tế
TRADE_FEE         = 0.0015
SLIPPAGE          = 0.001
ROUND_TRIP_COST   = (TRADE_FEE + SLIPPAGE) * 2

# [NÂNG CẤP #10] ATR Trailing Stop
ATR_PERIOD        = 14
ATR_MULTIPLIER    = 2.0    # SL = giá mua - 2×ATR

# Cắt lỗ fallback (khi ATR không tính được)
SL_PCT            = 0.07

# Backtest
BT_RSI_BUY        = 45
BT_PROFIT         = 0.05
BT_DAYS_FWD       = 10

# AI
AI_MIN_ROWS       = 200
AI_PROFIT_T3      = 1.02
AI_GOOD           = 55.0
AI_OK             = 48.0

# Scoring 0-100
SCORE_AI_MAX      = 25
SCORE_TECH_MAX    = 20
SCORE_FLOW_MAX    = 20
SCORE_FINANCE_MAX = 15
SCORE_SECTOR_MAX  = 10
SCORE_SENT_MAX    = 10
SCORE_BUY_MIN     = 65

# Advisor
ADV_AI_BUY        = 58.0
ADV_GROWTH_BUY    = 15.0
ADV_RSI_SELL      = 78
ADV_WINRATE_GOOD  = 50.0

# Tài chính
CANSLIM_GREAT     = 20.0
PE_CHEAP          = 12
PE_OK             = 20
ROE_EXCELLENT     = 0.25
ROE_GOOD          = 0.15

# Radar
RADAR_MAX         = 150
SCAN_DAYS         = 200   # đủ cho AI_MIN_ROWS=200
FOREIGN_DAYS      = 10
FOREIGN_NET_DAYS  = 10

# Chart
CHART_DAYS        = 120

# [V23] RS Rating
RS_LOOKBACK       = 63          # ~3 tháng giao dịch
RS_GOOD           = 70          # RS ≥ 70 = mạnh hơn thị trường

# [V23] 52-Week High
W52_NEAR_PCT      = 0.92        # trong vòng 8% đỉnh 52 tuần = gần đỉnh

# [V23] Divergence
DIV_LOOKBACK      = 20          # số phiên nhìn lại để tìm phân kỳ

# [V23] Chân Sóng (Wave Bottom) — tiêu chí mở rộng
WAVE_RSI_MAX      = 52          # RSI dưới 52 = chưa quá mua
WAVE_RSI_MIN      = 28          # RSI trên 28 = không quá bán thái quá
WAVE_PRICE_MA50   = 0.88        # giá ít nhất 88% MA50
WAVE_SCORE_MIN    = 3           # cần ≥ 3 điểm chân sóng

# Mã trụ thị trường
PILLARS = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]

# Fallback ~90 mã phổ biến HOSE
FALLBACK_TICKERS = [
    "ACB","BCG","BID","BVH","CTD","CTG","DBC","DCM","DGC","DGW",
    "DIG","DPM","DXG","EIB","FPT","GAS","GEX","GMD","HDB","HDG",
    "HPG","HSG","KDH","LPB","MBB","MSN","MWG","NLG","NVL","OCB",
    "PDR","PHR","PLX","PNJ","POW","PVD","REE","SAB","SSI","STB",
    "TCB","TPB","VCB","VCI","VHM","VIC","VIX","VJC","VND","VNM",
    "VPB","VRE","VTP","DXS","DGW","FRT","GEG","HAH","HVN","IMP",
    "KBC","KDC","KOS","MCH","MSB","NKG","PAN","PC1","PTB","PVT",
    "SBT","SHB","SRC","SSB","TCH","VGC","VHC","VSH","ANV","ASM",
    "BAF","BSR","BTP","C4G","CAV","CII","CMG","CTI","DAH","DCL",
]

# Phân ngành
SECTOR_MAP = {
    "Ngân Hàng":       ["VCB","TCB","MBB","BID","CTG","ACB","HDB","LPB","TPB","STB","SSB","MSB","SHB","EIB"],
    "Bất Động Sản":    ["VHM","VIC","NVL","PDR","DXG","KDH","NLG","DIG","BCG","HDG","DXS","CEO","SCR"],
    "Chứng Khoán":     ["SSI","VCI","VND","HCM","BSI","VIX","FTS","MBS","SHS","TVS"],
    "Công Nghệ":       ["FPT","CMG","ELC","ITD","VGI","SAM","SGT"],
    "Thép & VLXD":     ["HPG","HSG","NKG","VGC","BMP","HT1","CSV","TCO"],
    "Dầu Khí":         ["GAS","PVD","PVT","POW","PLX","BSR","OIL","PVC"],
    "Tiêu Dùng":       ["VNM","SAB","MCH","KDC","PNJ","MWG","FRT","DBC","VHC","ANV"],
    "Dệt May":         ["MSH","TNG","STK","TCM","GMC","PPH"],
    "Logistics":       ["GMD","HAH","VSC","TMS","VTP","STG","SCS"],
    "Điện & NL TT":    ["REE","PC1","GEG","VSH","SBA","TMP","HND"],
}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def now_vn() -> datetime:
    return datetime.now(TZ_VN)

def date_range(days: int) -> tuple[str, str]:
    today = now_vn()
    return (
        (today - timedelta(days=days)).strftime(DATE_FMT),
        today.strftime(DATE_FMT)
    )

def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    if len(df.columns) == 0:
        return df
    if isinstance(df.columns[0], tuple):
        df.columns = [str(c[0]).lower() for c in df.columns]
    else:
        df.columns = [str(c).lower() for c in df.columns]
    return df

def valid(df) -> bool:
    return df is not None and not df.empty

def to_billion(val) -> float:
    v = float(val or 0)
    return v / 1e9 if abs(v) > 1e6 else v

def engine() -> Vnstock:
    return st.session_state['vnstock_engine']

# ==============================================================================
# 1. BẢO MẬT
# ==============================================================================
def authenticate() -> bool:
    KEY = "authenticated"
    if st.session_state.get(KEY, False):
        return True
    st.markdown("### 🔐 Quant System V22.0 — Cổng Bảo Mật Trung Tâm")
    st.info("Hệ thống phân tích định lượng chuyên sâu. Vui lòng xác thực danh tính.")
    pwd = st.text_input("🔑 Nhập mật mã truy cập:", type="password")
    if pwd:
        if pwd == st.secrets.get("password", ""):
            st.session_state[KEY] = True
            st.rerun()
        else:
            st.error("❌ Mật mã không hợp lệ.")
    return False

# ==============================================================================
# 2. TRUY XUẤT DỮ LIỆU
# ==============================================================================
def get_price(ticker: str, days: int = HISTORY_DAYS) -> pd.DataFrame | None:
    start, end = date_range(days)
    try:
        df = engine().stock.quote.history(symbol=ticker, start=start, end=end)
        if valid(df):
            return normalize_cols(df)
    except Exception as e:
        print(f"[WARN] Vnstock price {ticker}: {e}")
    try:
        yf_sym  = "^VNINDEX" if ticker == "VNINDEX" else f"{ticker}.VN"
        # Tính period động thay vì cứng "3y"
        yf_days = max(days + 30, 90)
        period  = f"{min(yf_days // 365 + 1, 5)}y"
        df = yf.download(yf_sym, period=period, progress=False).reset_index()
        if valid(df):
            return normalize_cols(df)
    except Exception as e:
        print(f"[WARN] Yahoo price {ticker}: {e}")
    return None


@st.cache_data(ttl=3600)
def get_vnindex_cached() -> pd.DataFrame | None:
    """
    Lấy dữ liệu VN-Index với nhiều phương án fallback.
    Cache 1 giờ — dùng chung cho tất cả RS Rating calculations.
    """
    # Phương án 1: Vnstock market index
    for sym in ['VNINDEX', 'VN-INDEX', 'VNI']:
        try:
            df = engine().stock.quote.history(symbol=sym, start='2023-01-01',
                                               end=now_vn().strftime(DATE_FMT))
            if valid(df) and len(df) >= 30:
                df = normalize_cols(df)
                print(f"[OK] VNINDEX via vnstock symbol={sym}")
                return df
        except Exception:
            continue

    # Phương án 2: yfinance ^VNINDEX
    for yf_sym in ['^VNINDEX', 'VNINDEX', '^VNI']:
        try:
            df = yf.download(yf_sym, period='2y', progress=False).reset_index()
            if valid(df) and len(df) >= 30:
                df = normalize_cols(df)
                print(f"[OK] VNINDEX via yfinance symbol={yf_sym}")
                return df
        except Exception:
            continue

    print("[WARN] Không lấy được VN-Index từ bất kỳ nguồn nào.")
    return None

def get_foreign(ticker: str, days: int = FOREIGN_DAYS) -> pd.DataFrame | None:
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

def get_proprietary(ticker: str, days: int = FOREIGN_DAYS) -> pd.DataFrame | None:
    start, end = date_range(days)
    try:
        df = engine().stock.trade.proprietary_trade(symbol=ticker, start=start, end=end)
        if valid(df):
            return normalize_cols(df)
    except Exception as e:
        print(f"[WARN] Proprietary {ticker}: {e}")
    return None

# ==============================================================================
# 3. CHỈ BÁO KỸ THUẬT (có thêm ATR, ADX, OBV — NÂNG CẤP #10 #11)
# ==============================================================================
def calc_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    """[NÂNG CẤP #10] Average True Range — đo độ biến động thực tế."""
    high  = df['high']
    low   = df['low']
    close = df['close']
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


def calc_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """[NÂNG CẤP #11] Average Directional Index — đo sức mạnh xu hướng."""
    high  = df['high']
    low   = df['low']
    atr14 = calc_atr(df, period)
    plus_dm  = (high.diff()).clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    plus_di  = 100 * plus_dm.ewm(span=period, adjust=False).mean()  / (atr14 + 1e-9)
    minus_di = 100 * minus_dm.ewm(span=period, adjust=False).mean() / (atr14 + 1e-9)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-9)) * 100
    return dx.ewm(span=period, adjust=False).mean()


def calc_obv(df: pd.DataFrame) -> pd.Series:
    """[NÂNG CẤP #11] On-Balance Volume — tích lũy dòng tiền thực."""
    obv = [0]
    closes = df['close'].values
    volumes = df['volume'].values
    for i in range(1, len(df)):
        if closes[i] > closes[i - 1]:
            obv.append(obv[-1] + volumes[i])
        elif closes[i] < closes[i - 1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=df.index)


def calc_indicators(df_raw: pd.DataFrame) -> pd.DataFrame:
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

    df['ma20']  = close.rolling(20).mean()
    df['ma50']  = close.rolling(50).mean()
    df['ma200'] = close.rolling(200).mean()

    std20            = close.rolling(20).std()
    df['upper_band'] = df['ma20'] + 2 * std20
    df['lower_band'] = df['ma20'] - 2 * std20
    df['bb_width']   = (df['upper_band'] - df['lower_band']) / (df['ma20'] + 1e-9)

    delta    = close.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/RSI_PERIOD, min_periods=RSI_PERIOD, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/RSI_PERIOD, min_periods=RSI_PERIOD, adjust=False).mean()
    rs       = avg_gain / (avg_loss + 1e-9)
    df['rsi'] = 100 - (100 / (1 + rs))

    ema12        = close.ewm(span=12, adjust=False).mean()
    ema26        = close.ewm(span=26, adjust=False).mean()
    df['macd']   = ema12 - ema26
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    df['return_1d']    = close.pct_change()
    vol_avg10          = volume.rolling(10).mean()
    df['vol_strength'] = volume / (vol_avg10 + 1e-9)
    # money_flow chuẩn hóa z-score — tránh giá trị hàng tỷ làm lệch AI
    raw_mf             = close * volume
    mf_mean            = raw_mf.rolling(20).mean()
    mf_std             = raw_mf.rolling(20).std()
    df['money_flow']   = (raw_mf - mf_mean) / (mf_std + 1e-9)
    df['volatility']   = df['return_1d'].rolling(20).std()
    df['vol_avg_20']   = volume.rolling(20).mean()

    df['is_red_candle'] = close < open_
    df['can_cung']      = df['is_red_candle'] & (volume < df['vol_avg_20'] * SUPPLY_RATIO)

    is_explosion   = df['vol_strength'] > VOL_PV_SIGNAL
    df['pv_trend'] = np.where(
        (df['return_1d'] > 0) & is_explosion,  1,
        np.where((df['return_1d'] < 0) & is_explosion, -1, 0)
    )

    # [NÂNG CẤP #10] ATR — cho Trailing Stop
    df['atr'] = calc_atr(df, ATR_PERIOD)

    # [NÂNG CẤP #11] ADX + OBV
    df['adx'] = calc_adx(df)
    df['obv']  = calc_obv(df)
    # Chuẩn hóa OBV thành z-score để đưa vào AI
    obv_mean = df['obv'].rolling(20).mean()
    obv_std  = df['obv'].rolling(20).std()
    df['obv_zscore'] = (df['obv'] - obv_mean) / (obv_std + 1e-9)

    # Chỉ dropna theo các cột AI thực sự cần — MA200 NaN không ảnh hưởng
    ai_cols = [
        'rsi', 'macd', 'signal', 'return_1d', 'volatility',
        'vol_strength', 'money_flow', 'pv_trend', 'adx', 'obv_zscore',
        'ma20', 'bb_width', 'upper_band', 'lower_band', 'atr',
    ]
    drop_cols = [c for c in ai_cols if c in df.columns]
    return df.dropna(subset=drop_cols)


def get_weekly_trend(df_daily: pd.DataFrame) -> str:
    try:
        df = df_daily.copy()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        weekly = df['close'].resample('W').last()
        weekly_ma10 = weekly.rolling(10).mean()
        if len(weekly) < 12:
            return 'NEUTRAL'
        last_close = weekly.iloc[-1]
        last_ma10  = weekly_ma10.iloc[-1]
        slope = (weekly_ma10.iloc[-1] - weekly_ma10.iloc[-4]) / (weekly_ma10.iloc[-4] + 1e-9)
        if last_close > last_ma10 and slope > 0.01:
            return 'UP'
        elif last_close < last_ma10 and slope < -0.01:
            return 'DOWN'
        else:
            return 'NEUTRAL'
    except Exception as e:
        print(f"[WARN] weekly trend: {e}")
        return 'NEUTRAL'

# ==============================================================================
# 4. PHÂN TÍCH DÒNG TIỀN KHỐI NGOẠI
# ==============================================================================
def analyze_foreign_trend(df_for: pd.DataFrame) -> dict:
    result = {
        'net_total':        0.0,
        'consecutive_buy':  0,
        'consecutive_sell': 0,
        'trend':            'NEUTRAL',
        'is_silent_accum':  False,
        'score':            0,
        'summary':          '',
    }
    if not valid(df_for):
        return result
    df = df_for.tail(10).copy()
    net_vals = []
    for _, row in df.iterrows():
        buy  = to_billion(row.get('buyval',  0))
        sell = to_billion(row.get('sellval', 0))
        net  = to_billion(row.get('netval', buy - sell))
        net_vals.append(net)
    if not net_vals:
        return result
    result['net_total'] = sum(net_vals)
    consec_buy = consec_sell = 0
    for v in reversed(net_vals):
        if v > 0:
            if consec_sell == 0: consec_buy  += 1
            else:                break
        elif v < 0:
            if consec_buy == 0:  consec_sell += 1
            else:                break
        else:
            break
    result['consecutive_buy']  = consec_buy
    result['consecutive_sell'] = consec_sell
    result['is_silent_accum']  = consec_buy >= 5
    buy_days  = sum(1 for v in net_vals if v > 0)
    sell_days = sum(1 for v in net_vals if v < 0)
    if   buy_days  >= 7: result['trend'] = 'STRONG_BUY'
    elif buy_days  >= 5: result['trend'] = 'BUY'
    elif sell_days >= 7: result['trend'] = 'STRONG_SELL'
    elif sell_days >= 5: result['trend'] = 'SELL'
    else:                result['trend'] = 'NEUTRAL'
    if   result['trend'] == 'STRONG_BUY':  result['score'] = 20
    elif result['trend'] == 'BUY':          result['score'] = 14
    elif result['trend'] == 'NEUTRAL':      result['score'] = 8
    elif result['trend'] == 'SELL':         result['score'] = 3
    else:                                   result['score'] = 0
    if result['is_silent_accum']:
        result['score'] = min(20, result['score'] + 5)
    if result['is_silent_accum']:
        result['summary'] = (
            f"🦈 **TÍN HIỆU VÀNG — Tích Lũy Âm Thầm!** "
            f"Khối Ngoại mua ròng {consec_buy} phiên liên tiếp "
            f"(tổng {result['net_total']:.1f} tỷ VNĐ). "
            f"Đây là dấu hiệu tay to gom hàng trước sóng lớn."
        )
    elif result['trend'] in ('STRONG_BUY', 'BUY'):
        result['summary'] = (
            f"✅ Khối Ngoại mua ròng trong {buy_days}/10 phiên gần nhất "
            f"(tổng +{result['net_total']:.1f} tỷ VNĐ). Dòng tiền ngoại đang ủng hộ."
        )
    elif result['trend'] in ('STRONG_SELL', 'SELL'):
        result['summary'] = (
            f"🚨 Khối Ngoại bán ròng trong {sell_days}/10 phiên gần nhất "
            f"(tổng {result['net_total']:.1f} tỷ VNĐ). Cảnh báo thoát hàng."
        )
    else:
        result['summary'] = (
            f"🟡 Khối Ngoại giao dịch trung lập ({buy_days} phiên mua, "
            f"{sell_days} phiên bán trong 10 phiên gần nhất)."
        )
    return result

# ==============================================================================
# 5. AI — XGBoost + Walk-Forward + ADX/OBV Features [NÂNG CẤP #11 #13]
# ==============================================================================
@st.cache_data(ttl=1800)
def predict_ai_cached(ticker: str, last_close: float) -> float | str:
    """
    [NÂNG CẤP #13] Cache AI prediction 30 phút.
    last_close dùng làm cache key — tự invalidate khi giá thay đổi.
    """
    df = get_price(ticker)
    if not valid(df):
        return "N/A"
    df = calc_indicators(df)
    return _run_xgb(df)


def predict_ai_t3(df: pd.DataFrame) -> float | str:
    """Wrapper — dùng trực tiếp khi đã có df (Radar scan)."""
    return _run_xgb(df)


def _run_xgb(df: pd.DataFrame) -> float | str:
    """
    [NÂNG CẤP #1]  XGBClassifier Walk-Forward Validation.
    [NÂNG CẤP #11] Thêm adx, obv_zscore vào features.
    """
    if len(df) < AI_MIN_ROWS:
        return "N/A"
    df2 = df.copy()
    df2['target'] = (df2['close'].shift(-3) > df2['close'] * AI_PROFIT_T3).astype(int)
    df2 = df2.dropna()
    features = [
        'rsi', 'macd', 'signal', 'return_1d', 'volatility',
        'vol_strength', 'money_flow', 'pv_trend',
        'adx', 'obv_zscore',
    ]
    features = [f for f in features if f in df2.columns]
    X = df2[features].values
    y = df2['target'].values

    # Tính scale_pos_weight để xử lý class imbalance
    n_neg = max(1, (y == 0).sum())
    n_pos = max(1, (y == 1).sum())
    spw   = round(n_neg / n_pos, 2)

    tscv  = TimeSeriesSplit(n_splits=5)
    model = XGBClassifier(
        n_estimators      = 200,
        max_depth         = 4,
        learning_rate     = 0.05,
        subsample         = 0.8,
        colsample_bytree  = 0.8,
        scale_pos_weight  = spw,      # xử lý mất cân bằng lớp
        min_child_weight  = 5,        # tránh overfit trên tập nhỏ
        use_label_encoder = False,
        eval_metric       = 'logloss',
        random_state      = 42,
        verbosity         = 0,
    )
    for train_idx, _ in tscv.split(X):
        if len(train_idx) < 100:
            continue
        model.fit(X[train_idx], y[train_idx])
    try:
        prob = model.predict_proba(X[[-1]])[0][1]
        return round(prob * 100, 1)
    except Exception:
        return "N/A"

# ==============================================================================
# 6. BACKTEST — Có Sharpe + Max Drawdown [NÂNG CẤP #14]
# ==============================================================================
def run_backtest(df: pd.DataFrame) -> dict:
    """
    [NÂNG CẤP #3]  Backtest có phí + slippage.
    [NÂNG CẤP #14] Thêm Sharpe Ratio và Max Drawdown.
    """
    signals = wins = 0
    profits = []
    n       = len(df)
    for i in range(100, n - BT_DAYS_FWD):
        rsi_ok     = df['rsi'].iloc[i] < BT_RSI_BUY
        macd_cross = (
            df['macd'].iloc[i]   > df['signal'].iloc[i] and
            df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
        )
        if not (rsi_ok and macd_cross):
            continue
        signals += 1
        buy_price = df['close'].iloc[i] * (1 + SLIPPAGE)
        target    = buy_price * (1 + BT_PROFIT)
        sl_price  = buy_price * (1 - SL_PCT)
        future    = df['close'].iloc[i+1 : i+1+BT_DAYS_FWD]
        hit_tp = any(future >= target)
        hit_sl = any(future <= sl_price)
        if hit_tp:
            profits.append(BT_PROFIT - ROUND_TRIP_COST)
            wins += 1
        elif hit_sl:
            profits.append(-SL_PCT - ROUND_TRIP_COST)
        else:
            exit_price = future.iloc[-1] if len(future) > 0 else buy_price
            gross      = (exit_price - buy_price) / buy_price
            profits.append(gross - ROUND_TRIP_COST)

    if not profits:
        return {
            'winrate': 0.0, 'avg_profit': 0.0, 'avg_loss': 0.0,
            'expectancy': 0.0, 'signals': 0,
            'sharpe': 0.0, 'max_drawdown': 0.0,     # [NÂNG CẤP #14]
        }

    winrate    = round((wins / signals) * 100, 1) if signals else 0.0
    avg_profit = round(np.mean([p for p in profits if p > 0]) * 100, 2) if any(p > 0 for p in profits) else 0.0
    avg_loss   = round(np.mean([p for p in profits if p < 0]) * 100, 2) if any(p < 0 for p in profits) else 0.0
    expectancy = round(np.mean(profits) * 100, 2)

    # [NÂNG CẤP #14] Sharpe Ratio
    rf_daily = 0.045 / 252          # lãi suất phi rủi ro VN ~4.5%/năm
    excess   = np.array(profits) - rf_daily
    sharpe   = round((excess.mean() / (excess.std() + 1e-9)) * np.sqrt(252 / BT_DAYS_FWD), 2)

    # [NÂNG CẤP #14] Max Drawdown
    equity      = np.cumprod([1 + p for p in profits])
    rolling_max = np.maximum.accumulate(equity)
    drawdowns   = (equity - rolling_max) / rolling_max
    max_dd      = round(drawdowns.min() * 100, 2)

    return {
        'winrate':      winrate,
        'avg_profit':   avg_profit,
        'avg_loss':     avg_loss,
        'expectancy':   expectancy,
        'signals':      signals,
        'sharpe':       sharpe,          # [NÂNG CẤP #14]
        'max_drawdown': max_dd,          # [NÂNG CẤP #14]
    }

# ==============================================================================
# 7. KELLY CRITERION — Position Sizing [NÂNG CẤP #12]
# ==============================================================================
def calc_kelly(winrate: float, avg_profit: float, avg_loss: float) -> float:
    """
    [NÂNG CẤP #12] Half-Kelly Criterion.
    Trả về % vốn tối ưu cho mỗi lệnh (giới hạn max 25%).
    """
    if avg_loss == 0 or winrate == 0:
        return 0.0
    w = winrate / 100
    b = abs(avg_profit / avg_loss)    # tỷ lệ lời/lỗ
    kelly = w - (1 - w) / b
    half_kelly = max(0.0, min(kelly / 2, 0.25))
    return round(half_kelly * 100, 1)

# ==============================================================================
# 8. SENTIMENT
# ==============================================================================
def analyze_news_sentiment(headlines: list[str]) -> dict:
    if not headlines:
        return {'score': 5, 'label': '🟡 Chưa có dữ liệu tin tức', 'compound': 0.0}
    sia    = SentimentIntensityAnalyzer()
    scores = [sia.polarity_scores(h)['compound'] for h in headlines if h.strip()]
    avg    = np.mean(scores) if scores else 0.0
    if   avg >= 0.4:  label, pts = "🟢 Tin Tức Rất Tích Cực — Thị trường đang hưng phấn với cổ phiếu này", 10
    elif avg >= 0.1:  label, pts = "🟩 Tin Tức Tích Cực — Hỗ trợ đà tăng nhẹ", 7
    elif avg >= -0.1: label, pts = "🟡 Tin Tức Trung Lập — Chưa tác động đáng kể", 5
    elif avg >= -0.4: label, pts = "🟧 Tin Tức Tiêu Cực — Có thể tạo áp lực bán", 2
    else:             label, pts = "🔴 Tin Tức Rất Xấu — Rủi ro cao, cẩn thận!", 0
    return {'score': pts, 'label': label, 'compound': round(avg, 3)}

# ==============================================================================
# 9. SCORING TỔNG HỢP 0-100
# ==============================================================================
def calc_total_score(
    last: pd.Series,
    ai_score,
    bt: dict,
    foreign_trend: dict,
    growth,
    pe,
    weekly_trend: str,
    sentiment_score: int,
    sector_score: int,
) -> dict:
    price, ma20, rsi = last['close'], last['ma20'], last['rsi']

    # --- AI (0-25) ---
    if _is_valid_score(ai_score):
        if   ai_score >= 70: ai_pts = 25
        elif ai_score >= 60: ai_pts = 20
        elif ai_score >= 50: ai_pts = 13
        elif ai_score >= 40: ai_pts = 7
        else:                ai_pts = 2
    else:
        ai_pts = 0

    # --- Kỹ thuật (0-20) ---
    tech_pts = 0
    if price > ma20:                     tech_pts += 7
    if rsi < RSI_HOT:                    tech_pts += 5
    if last['macd'] > last['signal']:    tech_pts += 5
    if weekly_trend == 'UP':             tech_pts += 3

    # --- Dòng tiền (0-20) ---
    flow_pts = foreign_trend.get('score', 0)

    # --- Tài chính (0-15) ---
    fin_pts = 0
    if growth is not None:
        if   growth >= CANSLIM_GREAT: fin_pts += 8
        elif growth > 0:              fin_pts += 4
    if pe is not None:
        if   pe < PE_CHEAP: fin_pts += 7
        elif pe < PE_OK:    fin_pts += 4

    # --- Ngành (0-10) ---
    sector_pts = min(10, sector_score)

    # --- Sentiment (0-10) ---
    sent_pts = min(10, sentiment_score)

    total = min(100, ai_pts + tech_pts + flow_pts + fin_pts + sector_pts + sent_pts)

    if total >= SCORE_BUY_MIN and rsi < RSI_HOT:
        decision       = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
        decision_color = "green"
    elif total >= 45:
        decision       = "⚖️ THEO DÕI (WATCHLIST)"
        decision_color = "orange"
    else:
        decision       = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
        decision_color = "red"

    return {
        'total':          total,
        'ai_pts':         ai_pts,
        'tech_pts':       tech_pts,
        'flow_pts':       flow_pts,
        'fin_pts':        fin_pts,
        'sector_pts':     sector_pts,
        'sent_pts':       sent_pts,
        'decision':       decision,
        'decision_color': decision_color,
    }

# ==============================================================================
# 10. ATR TRAILING STOP [NÂNG CẤP #10]
# ==============================================================================
def calc_trailing_stop(buy_price: float, atr_value: float) -> dict:
    """
    [NÂNG CẤP #10] SL động dựa trên ATR.
    Trailing SL = giá mua - ATR_MULTIPLIER × ATR
    So sánh với SL cứng 7% — lấy giá nào cao hơn (bảo vệ hơn).
    """
    atr_sl    = buy_price - ATR_MULTIPLIER * atr_value
    fixed_sl  = buy_price * (1 - SL_PCT)
    final_sl  = max(atr_sl, fixed_sl)   # lấy giá bảo vệ hơn (cao hơn)
    sl_pct    = round((final_sl - buy_price) / buy_price * 100, 2)
    return {
        'atr_sl':   round(atr_sl, 0),
        'fixed_sl': round(fixed_sl, 0),
        'final_sl': round(final_sl, 0),
        'sl_pct':   sl_pct,
    }

# ==============================================================================
# 11. RADAR ĐỈNH / ĐÁY
# ==============================================================================
def calc_support_resistance(last: pd.Series) -> dict:
    price = last['close']
    ma20  = last['ma20']
    upper = last['upper_band']
    rsi   = last['rsi']
    dist_to_support    = round((price - ma20)  / (ma20  + 1e-9) * 100, 2)
    dist_to_resistance = round((upper - price) / (price + 1e-9) * 100, 2)
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
# 12. BÁO CÁO TỰ ĐỘNG
# ==============================================================================
def generate_report(ticker, last, ai_score, bt, buy_set, sell_set, foreign_trend, weekly_trend) -> str:
    parts = []
    parts.append("#### 1. Đọc Vị Hành Vi Dòng Tiền (Smart Flow):")
    vol = last['vol_strength']
    if ticker in buy_set:
        parts.append(f"✅ **Tích Cực:** Dòng tiền lớn đang **GOM HÀNG CHỦ ĐỘNG** tại {ticker}. "
                     f"Khối lượng nổ gấp {vol:.1f} lần, kèm nến xanh xác nhận.")
    elif ticker in sell_set:
        parts.append(f"🚨 **Cảnh Báo:** Dòng tiền lớn đang **XẢ HÀNG QUYẾT LIỆT**. "
                     f"Khối lượng bán gấp {vol:.1f} lần, nến đỏ đè áp lực.")
    else:
        parts.append("🟡 **Trung Lập:** Dòng tiền chưa đột biến. Chủ yếu giao dịch nhỏ lẻ.")
    parts.append(foreign_trend.get('summary', ''))
    parts.append("#### 2. Đánh Giá Vị Thế Kỹ Thuật:")
    price, ma20, rsi = last['close'], last['ma20'], last['rsi']
    weekly_label = {"UP": "📈 TĂNG", "DOWN": "📉 GIẢM", "NEUTRAL": "➡️ NGANG"}.get(weekly_trend, "N/A")
    parts.append(f"🗓️ **Xu Hướng Tuần (Weekly):** {weekly_label} — "
                 f"{'✅ Khung tuần đồng pha, an toàn vào lệnh.' if weekly_trend == 'UP' else '⚠️ Khung tuần chưa xác nhận, cần thận trọng.'}")
    # ADX mới
    adx_val = last.get('adx', 0)
    if adx_val > 25:
        parts.append(f"📐 **ADX = {adx_val:.1f} — Xu Hướng Mạnh.** Tín hiệu kỹ thuật đáng tin cậy hơn.")
    else:
        parts.append(f"📐 **ADX = {adx_val:.1f} — Xu Hướng Yếu/Sideways.** Thận trọng với breakout giả.")
    if price < ma20:
        parts.append(f"❌ **Xu Hướng Xấu:** Giá ({price:,.0f}) DƯỚI MA20 ({ma20:,.0f}). Phe bán áp đảo.")
    else:
        parts.append(f"✅ **Xu Hướng Tốt:** Giá ({price:,.0f}) TRÊN MA20 ({ma20:,.0f}). Cấu trúc tăng được bảo vệ.")
    if rsi > RSI_OVERBOUGHT:
        parts.append(f"⚠️ **RSI = {rsi:.1f} — Quá Mua.** Dễ điều chỉnh bất cứ lúc nào.")
    elif rsi < 35:
        parts.append(f"💡 **RSI = {rsi:.1f} — Quá Bán.** Lực bán cạn, khả năng hồi cao.")
    else:
        parts.append(f"📊 **RSI = {rsi:.1f} — Vùng Ổn Định.**")
    parts.append("#### 3. Xác Suất Định Lượng (AI & Backtest Thực Tế):")
    if _is_valid_score(ai_score):
        ai_label = "Cửa sáng" if float(ai_score) > AI_GOOD else "Rủi ro cao"
        parts.append(f"- **AI XGBoost T+3:** **{float(ai_score):.1f}%** → *{ai_label}* (Walk-Forward + ADX/OBV validated)")
    wr  = bt.get('winrate', 0)
    exp = bt.get('expectancy', 0)
    parts.append(f"- **Winrate (sau phí):** **{wr}%** | Kỳ vọng mỗi lệnh: **{exp:+.2f}%**")
    parts.append(f"- **TB lời/lỗ:** +{bt.get('avg_profit',0):.2f}% / {bt.get('avg_loss',0):.2f}%")
    parts.append(f"- **Sharpe Ratio:** {bt.get('sharpe', 0):.2f} | **Max Drawdown:** {bt.get('max_drawdown', 0):.2f}%")
    # [NÂNG CẤP #10] ATR-based SL
    atr_val  = last.get('atr', price * 0.02)
    sl_info  = calc_trailing_stop(price, atr_val)
    parts.append(f"- **🛡️ ATR Trailing Stop:** **{sl_info['final_sl']:,.0f} VNĐ** ({sl_info['sl_pct']:+.1f}%)")
    parts.append("#### 💡 TỔNG KẾT:")
    price_bad = price < ma20
    ai_good   = _is_valid_score(ai_score) and float(ai_score) > AI_GOOD
    wr_good   = wr >= ADV_WINRATE_GOOD
    if price_bad and ticker in buy_set:
        parts.append("⚠️ **GOM HÀNG RẢI ĐỈNH:** Có dòng tiền gom nhưng giá dưới MA20 — chờ bứt MA20 mới vào.")
    elif wr < 40 and _is_valid_score(ai_score) and float(ai_score) < 50:
        parts.append("⛔ **RỦI RO NGẬP TRÀN:** AI và lịch sử đều tiêu cực — tuyệt đối đứng ngoài.")
    elif not price_bad and ai_good and wr_good and weekly_trend == 'UP':
        parts.append("🚀 **ĐIỂM MUA VÀNG:** Nền đẹp + AI + lịch sử + tuần xác nhận — giải ngân 30–50%.")
    elif not price_bad and ai_good and wr_good:
        parts.append("✅ **ĐIỂM MUA KHÁ:** Daily tốt nhưng weekly chưa rõ — vào 20-30%, chờ tuần xác nhận thêm.")
    else:
        parts.append("⚖️ **THEO DÕI:** Tín hiệu phân hóa — đưa vào Watchlist, chờ bùng nổ khối lượng.")
    return "\n\n".join(parts)

# ==============================================================================
# 13. TÀI CHÍNH
# ==============================================================================
def get_earnings_growth(ticker: str) -> float | None:
    try:
        df = engine().stock.finance.income_statement(symbol=ticker, period='quarter', lang='en').head(5)
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
        print(f"[WARN] Earnings {ticker}: {e}")
    try:
        g = yf.Ticker(f"{ticker}.VN").info.get('earningsQuarterlyGrowth')
        if g is not None:
            return round(g * 100, 1)
    except Exception:
        pass
    return None

def get_pe_roe(ticker: str) -> tuple:
    pe = roe = None
    try:
        row = engine().stock.finance.ratio(ticker, 'quarterly').iloc[-1]
        raw_pe  = row.get('ticker_pe', row.get('pe'))
        raw_roe = row.get('roe')
        if raw_pe is not None:
            v = float(raw_pe)
            if not np.isnan(v) and v > 0: pe = v
        if raw_roe is not None:
            v = float(raw_roe)
            if not np.isnan(v) and v > 0: roe = v
    except Exception as e:
        print(f"[WARN] PE/ROE {ticker}: {e}")
    if pe is None:
        try:
            info = yf.Ticker(f"{ticker}.VN").info
            pe   = info.get('trailingPE') or pe
            roe  = roe or info.get('returnOnEquity')
        except Exception:
            pass
    return pe, roe

# ==============================================================================
# 14. DÒNG TIỀN 3 NHÓM + GOM/XẢ
# ==============================================================================
def calc_net_flow(df: pd.DataFrame, days: int = 3) -> float:
    total_buy = total_sell = 0.0
    for _, row in df.tail(days).iterrows():
        total_buy  += float(row.get('buyval',  0) or 0)
        total_sell += float(row.get('sellval', 0) or 0)
    return total_buy - total_sell

def classify_flow_group(vol: float, ret: float, net_flow: float) -> dict:
    if vol >= VOL_SHARK:
        group, pct, desc = "🦈 Cá Mập", 0.65, "Tay to / Quỹ ngoại đang hoạt động mạnh"
    elif vol >= VOL_INST_HIGH:
        group, pct, desc = "🏦 Tổ Chức Nội", 0.45, "Tổ chức nội địa / Tự doanh tích cực"
    else:
        group, pct, desc = "🐜 Nhỏ Lẻ", 0.15, "Cá nhân nhỏ lẻ chiếm chủ đạo"
    retail_pct = 1 - pct
    is_accumulate = ret > 0 and vol >= VOL_PV_SIGNAL and net_flow >= 0
    is_distribute = ret < 0 and vol >= VOL_PV_SIGNAL and net_flow < 0
    if is_accumulate:
        action, action_color = "🟢 GOM HÀNG", "normal"
        action_note = "Giá tăng + Vol nổ + Dòng tiền ròng dương → Xác nhận tích lũy thực sự"
    elif is_distribute:
        action, action_color = "🔴 XẢ HÀNG", "inverse"
        action_note = "Giá giảm + Vol nổ + Dòng tiền ròng âm → Xác nhận phân phối thực sự"
    else:
        action, action_color = "🟡 TRUNG LẬP", "off"
        action_note = "Chưa đủ 3 điều kiện Gom/Xả đồng thời"
    return {
        'group': group, 'inst_pct': pct, 'retail_pct': retail_pct,
        'description': desc, 'action': action,
        'action_color': action_color, 'action_note': action_note,
    }

# ==============================================================================
# 15. SECTOR ROTATION
# ==============================================================================
def analyze_sector_rotation(tickers_list: list[str]) -> dict:
    sector_scores = {}
    for sector, malist in SECTOR_MAP.items():
        gains = []
        for ma in malist:
            if ma not in tickers_list:
                continue
            try:
                df = get_price(ma, days=20)
                if not valid(df):
                    continue
                df = calc_indicators(df)
                ret5 = (df['close'].iloc[-1] - df['close'].iloc[-5]) / (df['close'].iloc[-5] + 1e-9)
                gains.append(ret5)
            except Exception:
                continue
        if gains:
            sector_scores[sector] = round(np.mean(gains) * 100, 2)
    return dict(sorted(sector_scores.items(), key=lambda x: x[1], reverse=True))

def get_ticker_sector(ticker: str) -> str | None:
    for sector, malist in SECTOR_MAP.items():
        if ticker in malist:
            return sector
    return None

# ==============================================================================
# [V23 #17] RS RATING — Xếp hạng sức mạnh so với VN-Index
# ==============================================================================
def calc_rs_rating(df: pd.DataFrame, df_vnindex: pd.DataFrame | None) -> float:
    """
    [V23 #17] RS Rating 0-100 so với VN-Index.
    - Dùng tail(RS_LOOKBACK) thay vì iloc[-RS_LOOKBACK] để tránh crash khi df ngắn
    - Nếu không có VN-Index, tính RS dựa trên hiệu suất tuyệt đối (không so sánh)
    - Chuẩn hóa về 0-100: excess +20% → 100, excess -20% → 0
    """
    try:
        # Lấy close trong RS_LOOKBACK phiên gần nhất
        stock_window = df['close'].dropna().tail(RS_LOOKBACK)
        if len(stock_window) < 20:      # cần ít nhất 20 phiên
            return 50.0
        stock_ret = (stock_window.iloc[-1] - stock_window.iloc[0]) / (stock_window.iloc[0] + 1e-9)

        if valid(df_vnindex) and len(df_vnindex) >= 20:
            mkt_window = df_vnindex['close'].dropna().tail(RS_LOOKBACK)
            mkt_ret    = (mkt_window.iloc[-1] - mkt_window.iloc[0]) / (mkt_window.iloc[0] + 1e-9)
        else:
            # Fallback: không có VN-Index → chuẩn hóa hiệu suất tuyệt đối
            # Giả định thị trường tăng trung bình 8%/63 phiên (~15%/năm)
            mkt_ret = 0.08

        excess = stock_ret - mkt_ret
        # Map excess [-20%, +20%] → [0, 100]
        score  = (excess + 0.20) / 0.40 * 100
        return round(max(0.0, min(100.0, score)), 1)

    except Exception as e:
        print(f"[WARN] calc_rs_rating: {e}")
        return 50.0


def _rs_badge(rs: float) -> str:
    if   rs >= 90: return f"🔥 {rs:.0f} (Siêu mạnh)"
    elif rs >= 70: return f"✅ {rs:.0f} (Mạnh hơn thị trường)"
    elif rs >= 50: return f"🟡 {rs:.0f} (Ngang thị trường)"
    else:          return f"🔴 {rs:.0f} (Yếu hơn thị trường)"


# ==============================================================================
# [V23 #18] DIVERGENCE DETECTION — Phân kỳ RSI & MACD
# ==============================================================================
def detect_divergence(df: pd.DataFrame, lookback: int = DIV_LOOKBACK) -> dict:
    """
    Bullish divergence:  Giá lower low  nhưng RSI higher low  → sắp đảo chiều tăng
    Bearish divergence:  Giá higher high nhưng RSI lower high → sắp đảo chiều giảm
    """
    result = {'bullish_rsi': False, 'bearish_rsi': False,
              'bullish_macd': False, 'bearish_macd': False,
              'label': '', 'signal': 'NONE'}
    try:
        window = df.tail(lookback)
        if len(window) < lookback:
            return result
        close = window['close'].values
        rsi   = window['rsi'].values
        macd  = window['macd'].values

        # Tìm đáy giá và đáy RSI trong nửa đầu vs nửa sau
        mid = lookback // 2
        price_prev_low = close[:mid].min()
        price_last_low = close[mid:].min()
        rsi_prev_low   = rsi[:mid].min()
        rsi_last_low   = rsi[mid:].min()

        price_prev_high = close[:mid].max()
        price_last_high = close[mid:].max()
        rsi_prev_high   = rsi[:mid].max()
        rsi_last_high   = rsi[mid:].max()
        macd_prev_high  = macd[:mid].max()
        macd_last_high  = macd[mid:].max()

        # Bullish RSI divergence
        if price_last_low < price_prev_low * 0.99 and rsi_last_low > rsi_prev_low + 3:
            result['bullish_rsi'] = True
        # Bearish RSI divergence
        if price_last_high > price_prev_high * 1.01 and rsi_last_high < rsi_prev_high - 3:
            result['bearish_rsi'] = True
        # Bullish MACD divergence
        macd_prev_low = macd[:mid].min()
        macd_last_low = macd[mid:].min()
        if price_last_low < price_prev_low * 0.99 and macd_last_low > macd_prev_low + 0.01:
            result['bullish_macd'] = True
        # Bearish MACD divergence
        if price_last_high > price_prev_high * 1.01 and macd_last_high < macd_prev_high - 0.01:
            result['bearish_macd'] = True

        if result['bullish_rsi'] or result['bullish_macd']:
            indicators = []
            if result['bullish_rsi']:  indicators.append("RSI")
            if result['bullish_macd']: indicators.append("MACD")
            result['signal'] = 'BULLISH'
            result['label']  = f"📈 Phân Kỳ Dương ({'+'.join(indicators)}) — Giá giảm nhưng động lượng đang phục hồi"
        elif result['bearish_rsi'] or result['bearish_macd']:
            indicators = []
            if result['bearish_rsi']:  indicators.append("RSI")
            if result['bearish_macd']: indicators.append("MACD")
            result['signal'] = 'BEARISH'
            result['label']  = f"📉 Phân Kỳ Âm ({'+'.join(indicators)}) — Giá tăng nhưng động lượng suy yếu"
        else:
            result['label'] = "➡️ Không có phân kỳ rõ ràng"
    except Exception as e:
        print(f"[WARN] divergence: {e}")
    return result


# ==============================================================================
# [V23 #20] VWAP — Volume Weighted Average Price
# ==============================================================================
def calc_vwap(df: pd.DataFrame, days: int = 20) -> pd.Series:
    """
    VWAP rolling 20 phiên — đường giá trung bình thực sự theo khối lượng.
    Giá trên VWAP = phe mua chiếm ưu thế. Dưới VWAP = phe bán chiếm ưu thế.
    """
    typical = (df['high'] + df['low'] + df['close']) / 3
    tp_vol  = typical * df['volume']
    vwap    = tp_vol.rolling(days).sum() / df['volume'].rolling(days).sum()
    return vwap


# ==============================================================================
# [V23 #21] 52-WEEK HIGH PROXIMITY
# ==============================================================================
def calc_52w_info(df: pd.DataFrame) -> dict:
    """
    Phân tích vị trí giá so với đỉnh & đáy 52 tuần (~252 phiên).
    Gần đỉnh 52 tuần = tín hiệu CANSLIM mạnh nhất (Stage 2 breakout).
    """
    window_252 = df['close'].tail(252)
    high_52w = window_252.max()
    low_52w  = window_252.min()
    price    = df['close'].iloc[-1]
    pct_from_high = (price - high_52w) / high_52w * 100
    pct_from_low  = (price - low_52w)  / low_52w  * 100
    near_high = price >= high_52w * W52_NEAR_PCT
    near_low  = price <= low_52w  * 1.08
    if near_high:
        label = f"🏆 Gần Đỉnh 52 Tuần ({pct_from_high:.1f}%) — Vùng Stage 2 Breakout"
    elif near_low:
        label = f"💧 Gần Đáy 52 Tuần (+{pct_from_low:.1f}%) — Vùng rủi ro"
    else:
        label = f"📍 Giữa vùng ({pct_from_high:.1f}% dưới đỉnh, +{pct_from_low:.1f}% từ đáy)"
    return {
        'high_52w':       round(high_52w, 0),
        'low_52w':        round(low_52w,  0),
        'pct_from_high':  round(pct_from_high, 1),
        'pct_from_low':   round(pct_from_low,  1),
        'near_high':      near_high,
        'near_low':       near_low,
        'label':          label,
    }


# ==============================================================================
# [V23 #23] ICHIMOKU CLOUD
# ==============================================================================
def calc_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ichimoku Kinko Hyo — hệ thống xác định xu hướng đa tầng thời gian.
    Tenkan (9) | Kijun (26) | Senkou A | Senkou B (52) | Chikou
    """
    high = df['high']
    low  = df['low']
    def mid(h, l, n): return (h.rolling(n).max() + l.rolling(n).min()) / 2
    df = df.copy()
    df['ichi_tenkan']  = mid(high, low, 9)
    df['ichi_kijun']   = mid(high, low, 26)
    df['ichi_senkouA'] = ((df['ichi_tenkan'] + df['ichi_kijun']) / 2).shift(26)
    df['ichi_senkouB'] = mid(high, low, 52).shift(26)
    df['ichi_chikou']  = df['close'].shift(-26)
    return df


def ichimoku_signal(last: pd.Series) -> dict:
    """Đọc tín hiệu Ichimoku từ dòng cuối."""
    price    = last['close']
    tenkan   = last.get('ichi_tenkan',  np.nan)
    kijun    = last.get('ichi_kijun',   np.nan)
    senkou_a = last.get('ichi_senkouA', np.nan)
    senkou_b = last.get('ichi_senkouB', np.nan)
    if any(np.isnan(v) for v in [tenkan, kijun, senkou_a, senkou_b]):
        return {'signal': 'UNKNOWN', 'label': '❓ Chưa đủ dữ liệu Ichimoku'}
    cloud_top    = max(senkou_a, senkou_b)
    cloud_bottom = min(senkou_a, senkou_b)
    above_cloud  = price > cloud_top
    below_cloud  = price < cloud_bottom
    tenkan_cross = tenkan > kijun      # TK cắt KJ lên = bullish
    cloud_bull   = senkou_a > senkou_b # Mây xanh = bullish cloud
    if above_cloud and tenkan_cross and cloud_bull:
        signal = 'STRONG_BULL'
        label  = "☁️ Ichimoku: **Rất Tích Cực** — Giá trên mây, TK×KJ dương, mây xanh"
    elif above_cloud and tenkan_cross:
        signal = 'BULL'
        label  = "☁️ Ichimoku: **Tích Cực** — Giá trên mây + TK cắt KJ lên"
    elif above_cloud:
        signal = 'NEUTRAL_BULL'
        label  = "☁️ Ichimoku: **Trung Lập Tốt** — Giá trên mây nhưng TK/KJ chưa xác nhận"
    elif below_cloud:
        signal = 'BEAR'
        label  = "☁️ Ichimoku: **Tiêu Cực** — Giá dưới mây, xu hướng giảm"
    else:
        signal = 'INSIDE_CLOUD'
        label  = "☁️ Ichimoku: **Giằng Co** — Giá đang trong mây, chờ phá vỡ"
    return {'signal': signal, 'label': label,
            'above_cloud': above_cloud, 'cloud_bull': cloud_bull}


# ==============================================================================
# [V23 #19] MARKET BREADTH — Sức khỏe thị trường tổng thể
# ==============================================================================
@st.cache_data(ttl=1800)
def calc_market_breadth(sample_tickers: tuple) -> dict:
    """
    Quét mẫu 50 mã để đo sức khỏe thị trường:
    - % mã trên MA20
    - % mã có RSI < 50 (chưa quá mua)
    - Tỷ lệ tăng/giảm
    """
    above_ma20 = rsi_healthy = advancing = total = 0
    for t in sample_tickers:
        try:
            df = get_price(t, days=60)
            if not valid(df) or len(df) < 25:
                continue
            df = calc_indicators(df)
            last = df.iloc[-1]
            total += 1
            if last['close'] > last['ma20']:           above_ma20   += 1
            if last['rsi'] < 55:                       rsi_healthy  += 1
            if last['return_1d'] > 0:                  advancing    += 1
        except Exception:
            continue
    if total == 0:
        return {'total': 0, 'pct_above_ma20': 0, 'pct_rsi_ok': 0,
                'advance_decline': 0, 'market_status': 'UNKNOWN'}
    pct_ma20 = above_ma20 / total * 100
    pct_rsi  = rsi_healthy / total * 100
    adr      = advancing / total * 100
    if   pct_ma20 >= 70 and adr >= 60: status = "🟢 Thị Trường Mạnh (Bull Phase)"
    elif pct_ma20 >= 50 and adr >= 50: status = "🟡 Thị Trường Trung Lập"
    elif pct_ma20 < 40:                status = "🔴 Thị Trường Yếu (Bear Phase)"
    else:                              status = "🟠 Thị Trường Phân Hóa"
    return {
        'total':           total,
        'pct_above_ma20':  round(pct_ma20, 1),
        'pct_rsi_ok':      round(pct_rsi,  1),
        'advance_decline': round(adr,       1),
        'market_status':   status,
    }


# ==============================================================================
# [V23 #24] WAVE BOTTOM SCORE — Bộ dò chân sóng nâng cao
# ==============================================================================
def calc_wave_bottom_score(df: pd.DataFrame, last: pd.Series) -> dict:
    """
    Hệ thống điểm riêng để phát hiện cổ phiếu đang ở CHÂN SÓNG.
    Mỗi điều kiện đúng = +1 điểm. Tổng ≥ WAVE_SCORE_MIN = chân sóng hợp lệ.

    Tiêu chí rộng hơn Tầng 2 — bắt sớm hơn, trước khi weekly xác nhận.
    """
    score  = 0
    flags  = []
    price  = last['close']
    ma20   = last['ma20']
    ma50   = last.get('ma50', ma20)
    rsi    = last['rsi']
    bb_low = last['lower_band']
    bb_wid = last['bb_width']
    adx    = last.get('adx', 0)
    obv_z  = last.get('obv_zscore', 0)

    # ── HARD DISQUALIFIERS — loại ngay, không tính điểm ──
    # Quá mua: RSI > WAVE_RSI_MAX (52) → đã bứt tốc, không phải chân sóng
    if rsi > WAVE_RSI_MAX:
        return {'score': 0, 'flags': [], 'is_wave_bottom': False,
                'label': f'❌ RSI {rsi:.1f} quá cao — đã bứt tốc, không phải chân sóng'}
    # Quá bán cực đoan: RSI < WAVE_RSI_MIN → downtrend mạnh, chưa đủ an toàn
    if rsi < WAVE_RSI_MIN:
        return {'score': 0, 'flags': [], 'is_wave_bottom': False,
                'label': f'❌ RSI {rsi:.1f} quá thấp — downtrend mạnh'}
    # Giá đã vượt MA20 > 5% → không còn là chân sóng nữa
    if price > ma20 * 1.05:
        return {'score': 0, 'flags': [], 'is_wave_bottom': False,
                'label': f'❌ Giá vượt MA20 quá 5% — cổ phiếu đã bứt phá'}
    # ADX ≥ 35: xu hướng đang bùng nổ mạnh → không phải tích lũy nền
    if adx >= 35:
        return {'score': 0, 'flags': [], 'is_wave_bottom': False,
                'label': f'❌ ADX {adx:.1f} ≥ 35 — xu hướng bùng nổ, không phải nền'}

    # 1. RSI trong vùng hồi phục (không quá mua, không quá bán thái quá)
    if WAVE_RSI_MIN <= rsi <= WAVE_RSI_MAX:
        score += 1
        flags.append("RSI vùng hồi phục")

    # 2. Giá gần/trên MA50 (nền trung hạn còn tốt)
    if price >= ma50 * WAVE_PRICE_MA50:
        score += 1
        flags.append("Gần MA50")

    # 3. BB đang co lại (Squeeze) — năng lượng đang tích tụ
    bb_min30 = df['bb_width'].tail(30).min()
    if bb_wid <= bb_min30 * 1.3:
        score += 1
        flags.append("BB Squeeze")

    # 4. Cạn Cung — Vol thấp trên nến đỏ (người bán cạn kiệt)
    if df['can_cung'].tail(7).sum() >= 2:
        score += 1
        flags.append("Cạn Cung")

    # 5. OBV đang tích lũy dương (dòng tiền thực chảy vào)
    if obv_z > 0.3:
        score += 1
        flags.append("OBV tích lũy")

    # 6. ADX thấp = sideways = đang tích lũy nền (không phải downtrend mạnh)
    if 10 < adx < 25:
        score += 1
        flags.append("ADX sideways")

    # 7. Giá đang nằm giữa Lower BB và MA20 (vùng hỗ trợ kép)
    if bb_low * 0.98 <= price <= ma20 * 1.02:
        score += 1
        flags.append("Nằm vùng hỗ trợ kép BB-MA20")

    # 8. Giá tăng nhẹ phiên gần nhất trên Vol bình thường (rục rịch thoát đáy)
    ret = last.get('return_1d', 0)
    vol = last['vol_strength']
    if ret > 0 and 0.7 <= vol <= 1.4:
        score += 1
        flags.append("Giá xanh nhẹ + Vol bình thường")

    is_wave_bottom = score >= WAVE_SCORE_MIN
    if is_wave_bottom:
        label = f"🌊 Chân Sóng ({score}/8 điều kiện: {', '.join(flags)})"
    else:
        label = f"Chưa đủ tiêu chí chân sóng ({score}/8)"
    return {
        'score':           score,
        'flags':           flags,
        'is_wave_bottom':  is_wave_bottom,
        'label':           label,
    }


# ==============================================================================
# 16. RADAR — PHÂN LOẠI CỔ PHIẾU 4 TẦNG (V23: thêm Chân Sóng)
def classify_stock(ticker: str, df: pd.DataFrame, ai_score, weekly_trend: str) -> str | None:
    """
    [V23] Phân loại 4 tầng:
    🚀 Bùng Nổ | ⚖️ Danh Sách Chờ | 🌊 Chân Sóng (mới) | 👁️ Vùng Quan Sát
    """
    last  = df.iloc[-1]
    vol   = last['vol_strength']
    rsi   = last['rsi']
    price = last['close']
    ma20  = last['ma20']

    # TẦNG 1: Bùng Nổ
    if vol > VOL_BREAKOUT:
        return "🚀 Bùng Nổ"

    ai_ok = _is_valid_score(ai_score) and float(ai_score) > AI_OK

    # --- Kiểm tra vũ khí tích lũy ---
    bb_now    = last['bb_width']
    bb_min20  = df['bb_width'].tail(20).min()
    squeezed  = bb_now <= bb_min20 * BB_SQUEEZE_TOL
    supply_ex = df['can_cung'].tail(5).any()
    smart     = False
    for get_fn in [get_foreign, get_proprietary]:
        fd = get_fn(ticker, FOREIGN_DAYS)
        if valid(fd) and calc_net_flow(fd, 3) > 0:
            smart = True
            break
    weapons = sum([squeezed, supply_ex, smart])

    # TẦNG 2: Danh Sách Chờ — tiêu chí chặt, an toàn nhất
    base_ok = (
        VOL_ACC_MIN <= vol <= VOL_ACC_MAX and
        price >= ma20 * PRICE_NEAR_MA20   and
        rsi < RSI_WATCHLIST_MAX           and
        ai_ok
    )
    if base_ok and weapons >= 1 and weekly_trend in ('UP', 'NEUTRAL'):
        return "⚖️ Danh Sách Chờ"

    # TẦNG 3: Chân Sóng [V23 #24] — bắt sớm trước khi weekly xác nhận
    wave = calc_wave_bottom_score(df, last)
    if wave['is_wave_bottom']:
        ma50          = last.get('ma50', ma20)
        not_downtrend = price >= ma50 * 0.85      # không quá xa MA50
        rsi_in_range  = WAVE_RSI_MIN <= rsi <= WAVE_RSI_MAX  # RSI phải trong vùng hồi phục
        price_not_hot = price <= ma20 * 1.05      # giá không được vượt MA20 quá 5% (đã bứt tốc rồi)
        adx_not_surge = last.get('adx', 0) < 35  # ADX < 35: chưa phải xu hướng bùng nổ
        if not_downtrend and rsi_in_range and price_not_hot and adx_not_surge:
            return "🌊 Chân Sóng"

    # TẦNG 4: Vùng Quan Sát — tín hiệu sớm, cần theo dõi thêm
    early_signals = 0
    if ai_ok:                        early_signals += 1
    if rsi < RSI_WATCHLIST_MAX + 5:  early_signals += 1
    if price >= ma20 * 0.90:         early_signals += 1
    if weapons >= 1:                 early_signals += 1
    if wave['score'] >= 2:           early_signals += 1   # [V23] wave partial
    if early_signals >= 2:
        return "👁️ Vùng Quan Sát"
    return None

# ==============================================================================
# CACHE: DANH SÁCH MÃ HOSE
# ==============================================================================
@st.cache_data(ttl=3600)
def load_hose_tickers() -> list[str]:
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
            for col in ['comGroupCode', 'exchange', 'market']:
                if col in df.columns:
                    result = df[df[col].str.upper() == 'HOSE']['ticker'].tolist()
                    if len(result) > 50:
                        return result
            if 'ticker' in df.columns and len(df) > 50:
                return df['ticker'].tolist()
        except Exception as e:
            print(f"[WARN] attempt: {e}")
            continue
    return FALLBACK_TICKERS

# ==============================================================================
# HELPER: HIỂN THỊ BẢNG RADAR ĐẸP [NÂNG CẤP #15 — Display]
# ==============================================================================
def _score_to_bar(score: float, max_score: float = 100) -> str:
    """Tạo thanh tiến trình dạng text emoji."""
    pct    = score / max_score
    filled = int(pct * 10)
    empty  = 10 - filled
    return "🟩" * filled + "⬜" * empty + f"  {score:.0f}/{max_score:.0f}"

def _is_valid_score(ai_score) -> bool:
    """Kiểm tra numpy.float64 lẫn Python float đều pass."""
    return isinstance(ai_score, (float, np.floating)) and not np.isnan(float(ai_score))

def _ai_badge(ai_score) -> str:
    if not _is_valid_score(ai_score):
        return "❓ N/A"
    v = float(ai_score)
    if   v >= 70: return f"🔥 {v:.1f}% (Rất tốt)"
    elif v >= 55: return f"✅ {v:.1f}% (Tốt)"
    elif v >= 45: return f"🟡 {v:.1f}% (Trung bình)"
    else:         return f"🔴 {v:.1f}% (Rủi ro)"

def _rsi_badge(rsi: float) -> str:
    if   rsi > RSI_OVERBOUGHT: return f"🔴 {rsi:.1f} (Quá mua)"
    elif rsi < RSI_OVERSOLD:   return f"💙 {rsi:.1f} (Quá bán)"
    elif rsi < 50:             return f"🟢 {rsi:.1f} (Lý tưởng)"
    else:                      return f"🟡 {rsi:.1f}"

def _weekly_badge(w: str) -> str:
    return {"UP": "📈 TĂNG", "DOWN": "📉 GIẢM", "NEUTRAL": "➡️ NGANG"}.get(w, "-")

def _vol_badge(vol: float) -> str:
    if   vol >= VOL_SHARK:     return f"🦈 {vol:.2f}x"
    elif vol >= VOL_BREAKOUT:  return f"🔥 {vol:.2f}x"
    elif vol >= VOL_ACC_MIN:   return f"✅ {vol:.2f}x"
    else:                      return f"🔵 {vol:.2f}x"

def render_radar_card(row: dict, tier_color: str = "blue") -> None:
    """[V23] Hiển thị 1 cổ phiếu dạng card — thêm RS Rating, Divergence, 52W, Chân Sóng."""
    ticker = row['Ticker']
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns([1.2, 1.5, 1.5, 1.5, 2.5])
        with c1:
            st.markdown(f"### `{ticker}`")
            st.caption(f"Thị giá: **{row['Thị Giá']}**")
            rs = row.get('RS Raw', 50)
            st.caption(_rs_badge(rs))
        with c2:
            st.metric("🤖 AI T+3", f"{row['AI T+3 Raw']:.1f}%" if _is_valid_score(row['AI T+3 Raw']) else "N/A")
            st.caption(_ai_badge(row['AI T+3 Raw']))
        with c3:
            st.metric("📊 RSI", f"{row['RSI Raw']:.1f}")
            st.caption(_rsi_badge(row['RSI Raw']))
        with c4:
            st.metric("📦 Vol", f"{row['Vol Raw']:.2f}x")
            st.caption(_vol_badge(row['Vol Raw']))
        with c5:
            st.caption(f"🗓️ Weekly: {_weekly_badge(row['Weekly Raw'])}")
            # Badges tín hiệu đặc biệt
            badges = []
            if row.get('Lò Xo BB'):       badges.append("✅ BB Squeeze")
            if row.get('Cạn Cung'):        badges.append("✅ Cạn Cung")
            if row.get('Tổ Chức Gom'):     badges.append("✅ Tổ Chức Gom")
            if row.get('52W High'):        badges.append("✅ Gần Đỉnh 52W")
            if row.get('Div Bullish'):     badges.append("✅ Phân Kỳ Dương")
            if row.get('Div Bearish'):     badges.append("⚠️ Phân Kỳ Âm")
            if row.get('Wave Bottom'):     badges.append(f"✅ Chân Sóng ({row.get('Wave Score',0)}/8)")
            if badges:
                st.success(" | ".join(badges[:3]))   # max 3 badge để gọn
                if len(badges) > 3:
                    st.caption(" | ".join(badges[3:]))
            else:
                st.caption("Chưa có tín hiệu đặc biệt")
            if row.get('ADX Raw', 0) > 25:
                st.caption(f"📐 ADX: **{row.get('ADX Raw',0):.1f}** (Xu hướng mạnh)")


def render_radar_table(rows: list[dict]) -> None:
    """[V23] Bảng tổng hợp với RS Rating, Divergence, 52W High, Chân Sóng."""
    if not rows:
        return
    display_rows = []
    for r in rows:
        ai_raw = r.get('AI T+3 Raw', 'N/A')
        if _is_valid_score(ai_raw):
            v = float(ai_raw)
            if   v >= 70: ai_text = f"🔥 {v:.1f}%"
            elif v >= 55: ai_text = f"✅ {v:.1f}%"
            elif v >= 45: ai_text = f"🟡 {v:.1f}%"
            else:         ai_text = f"🔴 {v:.1f}%"
        else:
            ai_text = "⏳ N/A"

        rs = r.get('RS Raw', 50)
        if   rs >= 80: rs_text = f"🔥 {rs:.0f}"
        elif rs >= 65: rs_text = f"✅ {rs:.0f}"
        elif rs >= 45: rs_text = f"🟡 {rs:.0f}"
        else:          rs_text = f"🔴 {rs:.0f}"

        display_rows.append({
            'Ticker':       r['Ticker'],
            'Thị Giá':      r['Thị Giá'],
            'AI T+3':       ai_text,
            'RS Rating':    rs_text,
            'RSI':          round(r.get('RSI Raw', 0), 1),
            'Vol':          f"{r.get('Vol Raw', 0):.2f}x",
            'ADX':          round(r.get('ADX Raw', 0), 1),
            'Weekly':       _weekly_badge(r.get('Weekly Raw', 'NEUTRAL')),
            'BB Sqz':       "✅" if r.get('Lò Xo BB')    else "—",
            'Cạn Cung':     "✅" if r.get('Cạn Cung')    else "—",
            'Tổ Chức':      "✅" if r.get('Tổ Chức Gom') else "—",
            '52W↑':         "✅" if r.get('52W High')    else "—",
            'Div':          "✅" if r.get('Div Bullish') else ("⚠️" if r.get('Div Bearish') else "—"),
            'Chân Sóng':    f"✅{r.get('Wave Score',0)}/8" if r.get('Wave Bottom') else "—",
        })
    df_display = pd.DataFrame(display_rows)
    st.dataframe(
        df_display,
        use_container_width=True,
        column_config={
            "Ticker":    st.column_config.TextColumn("Mã CK",    width="small"),
            "Thị Giá":   st.column_config.TextColumn("Thị Giá",  width="small"),
            "AI T+3":    st.column_config.TextColumn("🤖 AI T+3",
                help="🔥≥70% Rất tốt | ✅≥55% Tốt | 🟡≥45% TB | 🔴<45% Yếu"),
            "RS Rating": st.column_config.TextColumn("📈 RS",
                help="Sức mạnh vs VN-Index 3 tháng. 🔥≥80 | ✅≥65 | 🟡≥45 | 🔴<45"),
            "RSI":       st.column_config.NumberColumn("RSI",    format="%.1f", width="small"),
            "Vol":       st.column_config.TextColumn("Vol",      width="small"),
            "ADX":       st.column_config.NumberColumn("ADX",    format="%.1f", width="small",
                help="ADX > 25 = xu hướng mạnh"),
            "Weekly":    st.column_config.TextColumn("Weekly",   width="small"),
            "BB Sqz":    st.column_config.TextColumn("BB Sqz",   width="small"),
            "Cạn Cung":  st.column_config.TextColumn("Cạn Cung", width="small"),
            "Tổ Chức":   st.column_config.TextColumn("Tổ Chức",  width="small"),
            "52W↑":      st.column_config.TextColumn("52W↑",     width="small"),
            "Div":       st.column_config.TextColumn("Div",      width="small"),
            "Chân Sóng": st.column_config.TextColumn("Chân Sóng",width="small"),
        },
        hide_index=True,
    )


def render_radar_summary_banner(breakouts, watchlist, wave_bottom, watch_zone) -> None:
    """[V23] Banner tổng kết 4 tầng."""
    b, w, wv, z = len(breakouts), len(watchlist), len(wave_bottom), len(watch_zone)
    total = b + w + wv + z
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📊 Tổng tín hiệu", total)
    c2.metric("🚀 Bùng Nổ", b,
              delta="⚠️ Cẩn thận mua đuổi" if b > 0 else None, delta_color="off")
    c3.metric("⚖️ Danh Sách Chờ", w,
              delta="✅ Ưu tiên nhóm này" if w > 0 else None,
              delta_color="normal" if w > 0 else "off")
    c4.metric("🌊 Chân Sóng", wv,
              delta="🎯 Cơ hội sớm" if wv > 0 else None,
              delta_color="normal" if wv > 0 else "off")
    c5.metric("👁️ Quan Sát", z,
              delta="Theo dõi thêm" if z > 0 else None, delta_color="off")

# ==============================================================================
# MAIN APPLICATION
# ==============================================================================
if not authenticate():
    st.stop()

if 'vnstock_engine' not in st.session_state:
    st.session_state['vnstock_engine'] = Vnstock()

st.set_page_config(
    page_title="Quant System V22.0 Supreme",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ Quant System V22.0: Supreme Predator Leviathan")
st.caption("**V22.0:** ATR Trailing Stop | ADX+OBV AI Features | Kelly Sizing | Sharpe+MaxDD | Radar Display Nâng Cao")
st.markdown("---")

# --- SIDEBAR ---
tickers = load_hose_tickers()
st.sidebar.header("🕹️ Trung Tâm Giao Dịch Định Lượng")

if st.sidebar.button("🔄 Làm mới danh sách mã (Xóa Cache)"):
    st.cache_data.clear()
    st.rerun()

dropdown = st.sidebar.selectbox("Lựa chọn mã cổ phiếu:", tickers)
st.sidebar.caption(f"📊 Tổng số mã đang theo dõi: {len(tickers)}")
manual   = st.sidebar.text_input("Hoặc nhập trực tiếp (VD: FPT):").strip().upper()
ticker   = manual if manual else dropdown

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📰 Nhập Tiêu Đề Tin Tức (Sentiment)")
st.sidebar.caption("Paste tiêu đề tin tức bằng tiếng Anh (1 dòng = 1 tiêu đề).")
news_raw       = st.sidebar.text_area("Tiêu đề tin tức:", height=120,
                                       placeholder="e.g. FPT reports strong Q3 profit growth...")
news_headlines = [l.strip() for l in news_raw.splitlines() if l.strip()]

# --- TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH",
    "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM",
    "🌊 BÓC TÁCH DÒNG TIỀN",
    "🔍 RADAR TRUY QUÉT SIÊU CỔ PHIẾU",
    "🏭 SECTOR ROTATION — DÒNG TIỀN NGÀNH",
])

# ==============================================================================
# TAB 1: ROBOT ADVISOR
# ==============================================================================
with tab1:
    if st.button(f"⚡ TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG TOÀN DIỆN MÃ {ticker}"):
        with st.spinner(f"Đang đồng bộ dữ liệu đa tầng cho {ticker}..."):
            df_raw = get_price(ticker)
            if not valid(df_raw):
                st.error("❌ Không thể tải dữ liệu giá. Vui lòng F5 lại.")
                st.stop()
            df   = calc_indicators(df_raw)
            df   = calc_ichimoku(df)             # [V23 #23]
            df['vwap'] = calc_vwap(df)           # [V23 #20]
            last = df.iloc[-1]

            # [NÂNG CẤP #13] Dùng cache cho AI
            ai_score      = predict_ai_cached(ticker, float(last['close']))
            bt            = run_backtest(df)
            weekly_trend  = get_weekly_trend(df)
            sr            = calc_support_resistance(last)
            growth        = get_earnings_growth(ticker)
            pe, roe       = get_pe_roe(ticker)
            sentiment     = analyze_news_sentiment(news_headlines)
            df_for        = get_foreign(ticker, FOREIGN_DAYS)
            foreign_trend = analyze_foreign_trend(df_for)

            # [V23] New indicators
            df_vnindex    = get_vnindex_cached()
            rs_rating     = calc_rs_rating(df, df_vnindex)
            divergence    = detect_divergence(df)
            info_52w      = calc_52w_info(df)
            ichi_sig      = ichimoku_signal(last)
            wave_info     = calc_wave_bottom_score(df, last)

            ticker_sector = get_ticker_sector(ticker)
            sector_score  = 7 if ticker_sector else 5

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

            scoring = calc_total_score(
                last, ai_score, bt, foreign_trend, growth, pe,
                weekly_trend, sentiment['score'], sector_score
            )

            # [NÂNG CẤP #12] Kelly
            kelly_pct = calc_kelly(bt['winrate'], bt['avg_profit'], abs(bt['avg_loss']))

            # [NÂNG CẤP #10] ATR Trailing Stop
            atr_val  = float(last.get('atr', last['close'] * 0.02))
            sl_info  = calc_trailing_stop(float(last['close']), atr_val)

            st.markdown(
                "> 🧠 **Nhà Phân Tích Ảo V22.0:** Tự động tổng hợp dữ liệu đa chiều — "
                "ATR Trailing Stop | ADX/OBV AI | Kelly Sizing | Sharpe/MaxDD."
            )
            st.write(f"### 🎯 BẢN PHÂN TÍCH CHUYÊN MÔN TỰ ĐỘNG — MÃ {ticker}")

            col_report, col_signal = st.columns([2, 1])
            with col_report:
                report = generate_report(
                    ticker, last, ai_score, bt, buy_set, sell_set, foreign_trend, weekly_trend
                )
                st.info(report)

            with col_signal:
                st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                color = scoring['decision_color']
                st.title(f":{color}[{scoring['decision']}]")
                st.markdown(f"**📊 Điểm Tổng Hợp: {scoring['total']}/100**")
                st.progress(scoring['total'] / 100)
                if scoring['total'] >= SCORE_BUY_MIN:
                    st.success(f"✅ Đủ điều kiện giao dịch (≥ {SCORE_BUY_MIN}/100)")
                else:
                    st.warning(f"⏳ Chưa đủ ngưỡng ({scoring['total']}/{SCORE_BUY_MIN})")

                # [NÂNG CẤP #12] Kelly
                st.divider()
                st.metric("💰 Kelly Position Size", f"{kelly_pct}% vốn",
                          delta="Half-Kelly — an toàn", delta_color="off")
                st.caption("Kích thước vị thế tối ưu dựa trên lịch sử winrate & tỷ lệ lời/lỗ.")

            st.divider()

            # --- Bảng điểm ---
            st.write("### 🎯 Bảng Điểm Chi Tiết 0-100")
            d1, d2, d3, d4, d5, d6 = st.columns(6)
            d1.metric("🤖 AI XGBoost",  f"{scoring['ai_pts']}/{SCORE_AI_MAX}")
            d2.metric("📈 Kỹ Thuật",    f"{scoring['tech_pts']}/{SCORE_TECH_MAX}")
            d3.metric("🌊 Khối Ngoại",  f"{scoring['flow_pts']}/{SCORE_FLOW_MAX}")
            d4.metric("🏢 Tài Chính",   f"{scoring['fin_pts']}/{SCORE_FINANCE_MAX}")
            d5.metric("🏭 Ngành",       f"{scoring['sector_pts']}/{SCORE_SECTOR_MAX}")
            d6.metric("📰 Sentiment",   f"{scoring['sent_pts']}/{SCORE_SENT_MAX}")

            # Thanh điểm từng hạng mục — dễ nhìn hơn
            st.caption("Thanh điểm trực quan:")
            cols_bar = st.columns(3)
            items = [
                ("🤖 AI",       scoring['ai_pts'],     SCORE_AI_MAX),
                ("📈 Kỹ thuật", scoring['tech_pts'],   SCORE_TECH_MAX),
                ("🌊 Ngoại",    scoring['flow_pts'],   SCORE_FLOW_MAX),
                ("🏢 Tài chính",scoring['fin_pts'],    SCORE_FINANCE_MAX),
                ("🏭 Ngành",    scoring['sector_pts'], SCORE_SECTOR_MAX),
                ("📰 Sentiment",scoring['sent_pts'],   SCORE_SENT_MAX),
            ]
            for i, (label, pts, max_pts) in enumerate(items):
                with cols_bar[i % 3]:
                    st.markdown(f"**{label}**")
                    st.progress(pts / max_pts)
                    st.caption(f"{pts}/{max_pts} điểm")

            st.divider()

            # --- Sentiment ---
            st.write("### 📰 Phân Tích Tâm Lý Tin Tức (VADER Sentiment)")
            if news_headlines:
                st.info(f"{sentiment['label']} | Điểm compound: {sentiment['compound']}")
            else:
                st.warning("💡 Chưa có tin tức. Paste tiêu đề vào sidebar để AI phân tích tâm lý.")

            st.divider()

            # --- [NÂNG CẤP #10] ATR Trailing Stop (thay SL cứng) ---
            st.write("### 🛡️ Quản Lý Rủi Ro — ATR Trailing Stop [V22.0]")
            sl1, sl2, sl3, sl4 = st.columns(4)
            sl1.metric("ATR Hiện Tại", f"{atr_val:,.0f} VNĐ",
                       delta=f"~{atr_val/last['close']*100:.1f}% biến động/phiên")
            sl2.metric("🛡️ ATR Stop (×2)", f"{sl_info['atr_sl']:,.0f} VNĐ",
                       delta=f"{sl_info['sl_pct']:+.1f}% từ giá hiện tại",
                       delta_color="inverse")
            sl3.metric("SL Cứng (-7%)", f"{sl_info['fixed_sl']:,.0f} VNĐ",
                       delta="-7.0%", delta_color="inverse")
            sl4.metric("✅ SL Cuối (bảo vệ hơn)", f"{sl_info['final_sl']:,.0f} VNĐ",
                       delta="= max(ATR SL, SL cứng)", delta_color="off")
            st.caption("💡 **V22.0 dùng ATR Trailing Stop** — tự điều chỉnh theo biến động thực tế thay vì cắt lỗ cứng. "
                       "Khi thị trường biến động cao, ATR SL rộng hơn để tránh bị dừng lỗ oan.")

            st.divider()

            # --- Radar Đỉnh/Đáy ---
            st.write("### 📡 Radar Đỉnh / Đáy — Vị Trí Giá Hiện Tại")
            sr_c1, sr_c2, sr_c3, sr_c4 = st.columns(4)
            sr_c1.metric("Khoảng cách đến MA20",
                f"{sr['dist_to_support']:+.2f}%",
                delta="Trên MA20 ✓" if sr['dist_to_support'] > 0 else "Dưới MA20 ⚠️",
                delta_color="normal" if sr['dist_to_support'] > 0 else "inverse")
            sr_c2.metric("Room đến Kháng Cự BB",
                f"{sr['dist_to_resistance']:+.2f}%",
                delta="Chưa chạm trần ✓" if sr['dist_to_resistance'] > 3 else "Gần trần ⚠️",
                delta_color="normal" if sr['dist_to_resistance'] > 3 else "inverse")
            sr_c3.metric("🗓️ Xu Hướng Weekly",
                {"UP": "📈 TĂNG", "DOWN": "📉 GIẢM", "NEUTRAL": "➡️ NGANG"}.get(weekly_trend, "N/A"),
                delta="Đồng pha ✓" if weekly_trend == 'UP' else "Chưa xác nhận",
                delta_color="normal" if weekly_trend == 'UP' else "off")
            sr_c4.metric("📐 ADX Sức Mạnh Xu Hướng",
                f"{last.get('adx', 0):.1f}",
                delta="Xu hướng mạnh ✓" if last.get('adx', 0) > 25 else "Sideways ⚠️",
                delta_color="normal" if last.get('adx', 0) > 25 else "off")
            if "🚨" in sr['warning']:  st.error(sr['warning'])
            elif "💡" in sr['warning']: st.success(sr['warning'])
            else:                       st.warning(sr['warning'])

            st.divider()

            # --- [NÂNG CẤP #14] Backtest đầy đủ ---
            st.write("### 📋 Kết Quả Backtest Thực Tế (Đã trừ phí + slippage)")
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Winrate",         f"{bt['winrate']}%")
            b2.metric("TB lời / lệnh",   f"+{bt['avg_profit']:.2f}%")
            b3.metric("TB lỗ / lệnh",    f"{bt['avg_loss']:.2f}%")
            b4.metric("Kỳ Vọng / Lệnh",  f"{bt['expectancy']:+.2f}%",
                      delta="Dương ✓" if bt['expectancy'] > 0 else "Âm ⚠️",
                      delta_color="normal" if bt['expectancy'] > 0 else "inverse")

            # [NÂNG CẤP #14] Hàng 2 — Sharpe + MaxDD
            b5, b6, b7, b8 = st.columns(4)
            b5.metric("📈 Sharpe Ratio", f"{bt['sharpe']:.2f}",
                      delta="Tốt (>1)" if bt['sharpe'] > 1 else ("OK (>0)" if bt['sharpe'] > 0 else "Âm ⚠️"),
                      delta_color="normal" if bt['sharpe'] > 0 else "inverse")
            b6.metric("📉 Max Drawdown", f"{bt['max_drawdown']:.2f}%",
                      delta="Rủi ro cao" if bt['max_drawdown'] < -20 else "Chấp nhận được",
                      delta_color="inverse" if bt['max_drawdown'] < -20 else "off")
            b7.metric("📊 Tín hiệu BT",  f"{bt['signals']} lệnh")
            b8.metric("💰 Kelly Size",    f"{kelly_pct}% vốn",
                      delta="Half-Kelly", delta_color="off")

            st.caption(
                f"📊 {bt['signals']} tín hiệu | Phí: {ROUND_TRIP_COST*100:.2f}%/lệnh | "
                f"ATR SL động | Sharpe tính trên lãi suất phi rủi ro VN ~4.5%/năm"
            )
            st.divider()

            # --- Chỉ số kỹ thuật ---
            st.write("### 🎛️ Bảng Chỉ Số Kỹ Thuật")
            n1, n2, n3, n4, n5, n6 = st.columns(6)
            rsi_v = last['rsi']
            n1.metric("RSI (14)", f"{rsi_v:.1f}",
                      delta="Quá Mua" if rsi_v > RSI_OVERBOUGHT else
                            ("Quá Bán" if rsi_v < RSI_OVERSOLD else "Vùng Ổn"))
            macd_v, sig_v = last['macd'], last['signal']
            n2.metric("MACD vs Signal", f"{macd_v:.2f}",
                      delta="✓ Cross Up" if macd_v > sig_v else "✗ Cross Down")
            n3.metric("MA20 / MA50", f"{last['ma20']:,.0f}",
                      delta=f"MA50: {last['ma50']:,.0f}")
            n4.metric("Trần Bollinger", f"{last['upper_band']:,.0f}",
                      delta=f"Đáy: {last['lower_band']:,.0f}", delta_color="inverse")
            adx_v = last.get('adx', 0)
            n5.metric("ADX (Xu hướng)", f"{adx_v:.1f}",
                      delta="Mạnh ✓" if adx_v > 25 else "Yếu",
                      delta_color="normal" if adx_v > 25 else "off")
            n6.metric("OBV Z-Score", f"{last.get('obv_zscore', 0):.2f}",
                      delta="Tích lũy" if last.get('obv_zscore', 0) > 0.5 else "Phân phối" if last.get('obv_zscore', 0) < -0.5 else "Trung lập",
                      delta_color="normal" if last.get('obv_zscore', 0) > 0.5 else "inverse" if last.get('obv_zscore', 0) < -0.5 else "off")

            st.divider()

            # --- [V23] RS Rating + Divergence + 52W + Ichimoku ---
            st.write("### 🆕 V23.0 — Phân Tích Nâng Cao")
            v23_c1, v23_c2, v23_c3 = st.columns(3)

            with v23_c1:
                st.markdown("**📈 RS Rating (Sức mạnh so VN-Index)**")
                st.metric("RS Rating", f"{rs_rating:.0f}/100",
                          delta="Mạnh hơn thị trường ✓" if rs_rating >= RS_GOOD else "Yếu hơn thị trường ⚠️",
                          delta_color="normal" if rs_rating >= RS_GOOD else "inverse")
                st.progress(rs_rating / 100)
                st.caption(_rs_badge(rs_rating))

            with v23_c2:
                st.markdown("**📊 Phân Kỳ RSI/MACD (Divergence)**")
                if divergence['signal'] == 'BULLISH':
                    st.success(divergence['label'])
                elif divergence['signal'] == 'BEARISH':
                    st.error(divergence['label'])
                else:
                    st.info(divergence['label'])

            with v23_c3:
                st.markdown("**🏆 Vị Trí 52 Tuần**")
                st.metric("Đỉnh 52W", f"{info_52w['high_52w']:,.0f}",
                          delta=f"{info_52w['pct_from_high']:.1f}% dưới đỉnh",
                          delta_color="normal" if info_52w['near_high'] else "off")
                st.metric("Đáy 52W", f"{info_52w['low_52w']:,.0f}",
                          delta=f"+{info_52w['pct_from_low']:.1f}% từ đáy",
                          delta_color="off")
                if info_52w['near_high']: st.success(info_52w['label'])
                elif info_52w['near_low']: st.warning(info_52w['label'])
                else: st.caption(info_52w['label'])

            st.divider()

            # Ichimoku + Wave Bottom
            ichi_c, wave_c = st.columns(2)
            with ichi_c:
                st.markdown("**☁️ Ichimoku Cloud**")
                sig = ichi_sig['signal']
                if 'BULL' in sig:   st.success(ichi_sig['label'])
                elif sig == 'BEAR': st.error(ichi_sig['label'])
                else:               st.warning(ichi_sig['label'])

            with wave_c:
                st.markdown("**🌊 Chân Sóng Score (V23)**")
                st.progress(wave_info['score'] / 8)
                st.caption(f"{wave_info['score']}/8 tiêu chí")
                if wave_info['is_wave_bottom']:
                    st.success(wave_info['label'])
                else:
                    if wave_info['flags']:
                        st.info(f"Đạt được: {', '.join(wave_info['flags'])}\n\nCần thêm {WAVE_SCORE_MIN - wave_info['score']} tiêu chí nữa.")
                    else:
                        st.warning("Chưa có tiêu chí chân sóng nào đạt.")

            # --- Cẩm nang ---
            st.write("### 📖 CẨM NANG — Bí Kíp Né Bẫy Giá (False Breakout)")
            with st.expander("🚀 Mở rộng để đọc bí kíp — Dành riêng cho Minh"):
                st.markdown("""
**False Breakout (Bẫy Bứt Phá Giả) là gì?**
> Giá vượt ngưỡng kháng cự nhưng **không duy trì được** rồi quay đầu giảm ngay.

---

**🔴 DẤU HIỆU NHẬN BIẾT BẪY:**
1. **Khối lượng thấp khi phá đỉnh** — vol < 1.2x MA10 → thiếu lực xác nhận.
2. **Nến bấc trên dài** — giá lên nhưng đóng cửa thấp hơn nhiều.
3. **RSI vượt 70 ngay khi phá đỉnh** — quá mua tức thì.
4. **Giá vượt Bollinger Band trên** — vùng kháng cự thống kê cực mạnh.
5. **Khối Ngoại bán ròng khi giá tăng** — tổ chức xả hàng cho nhỏ lẻ mua.
6. **Weekly trend GIẢM hoặc NGANG** — breakout không có nền tuần xác nhận.
7. **[V22.0] ADX < 25** — xu hướng yếu, breakout dễ là giả.

---

**✅ QUY TẮC VÀO LỆNH AN TOÀN:**
- ⏳ Chờ nến xác nhận: không mua ngay phiên phá đỉnh.
- 📊 Vol phải nổ: ≥ 1.5x MA20 mới tin.
- 🔍 RSI lý tưởng: 50–65 khi phá đỉnh.
- 🗓️ **Weekly trend phải UP**.
- 📐 **[V22.0] ADX > 25** — xu hướng đủ mạnh để breakout thật.
- 🛡️ Luôn dùng **ATR Trailing Stop** — tự điều chỉnh theo biến động.
- 🌊 Kiểm tra Khối Ngoại 10 phiên: phải mua ròng liên tiếp.
- 💰 **[V22.0] Kelly Sizing** — không vào quá % Kelly khuyến nghị.

---
> *"Không có breakout nào đáng tin nếu không có khối lượng đi kèm."*
> — William O'Neil (CANSLIM)
                """)

            st.divider()

            # --- Master Chart ---
            st.write("### 📊 Biểu Đồ Kỹ Thuật Đa Lớp (VWAP + Ichimoku)")
            chart = df.tail(CHART_DAYS)
            x     = chart['date']
            fig   = make_subplots(rows=3, cols=1, shared_xaxes=True,
                                  vertical_spacing=0.03, row_heights=[0.60, 0.20, 0.20])
            fig.add_trace(go.Candlestick(
                x=x, open=chart['open'], high=chart['high'],
                low=chart['low'], close=chart['close'], name='Nến OHLC'
            ), row=1, col=1)
            for ma_col, color, name in [('ma20','orange','MA20'), ('ma200','purple','MA200')]:
                fig.add_trace(go.Scatter(x=x, y=chart[ma_col],
                    line=dict(color=color, width=1.5), name=name), row=1, col=1)
            # [V23 #20] VWAP
            if 'vwap' in chart.columns:
                fig.add_trace(go.Scatter(x=x, y=chart['vwap'],
                    line=dict(color='cyan', width=1.5, dash='dot'), name='VWAP'), row=1, col=1)
            # Bollinger Bands
            fig.add_trace(go.Scatter(x=x, y=chart['upper_band'],
                line=dict(color='gray', dash='dash', width=0.8), name='Trần BOL'), row=1, col=1)
            fig.add_trace(go.Scatter(x=x, y=chart['lower_band'],
                line=dict(color='gray', dash='dash', width=0.8),
                fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='Đáy BOL'), row=1, col=1)
            # [V23 #23] Ichimoku Cloud
            if 'ichi_senkouA' in chart.columns and 'ichi_senkouB' in chart.columns:
                fig.add_trace(go.Scatter(x=x, y=chart['ichi_senkouA'],
                    line=dict(color='rgba(0,200,0,0)', width=0),
                    fillcolor='rgba(0,200,0,0.15)', fill='tonexty',
                    name='Kumo (Mây)', showlegend=True), row=1, col=1)
                fig.add_trace(go.Scatter(x=x, y=chart['ichi_senkouB'],
                    line=dict(color='rgba(200,0,0,0.4)', width=1),
                    name='Senkou B'), row=1, col=1)
                fig.add_trace(go.Scatter(x=x, y=chart['ichi_tenkan'],
                    line=dict(color='red', width=1, dash='dot'), name='Tenkan'), row=1, col=1)
                fig.add_trace(go.Scatter(x=x, y=chart['ichi_kijun'],
                    line=dict(color='blue', width=1, dash='dot'), name='Kijun'), row=1, col=1)
            # Volume
            fig.add_trace(go.Bar(x=x, y=chart['volume'],
                name='KL', marker_color='gray'), row=2, col=1)
            # ADX
            if 'adx' in chart.columns:
                fig.add_trace(go.Scatter(x=x, y=chart['adx'],
                    line=dict(color='royalblue', width=1.5), name='ADX'), row=3, col=1)
                fig.add_hline(y=25, line_dash="dot", line_color="red",
                              annotation_text="ADX=25", row=3, col=1)
            fig.update_layout(height=900, template='plotly_white',
                               xaxis_rangeslider_visible=False,
                               margin=dict(l=40, r=40, t=50, b=40))
            fig.update_yaxes(title_text="Giá", row=1, col=1)
            fig.update_yaxes(title_text="KL",  row=2, col=1)
            fig.update_yaxes(title_text="ADX", row=3, col=1)
            st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# TAB 2: TÀI CHÍNH & CANSLIM
# ==============================================================================
with tab2:
    st.write(f"### 📈 Phân Tích Sức Khỏe Tài Chính — {ticker}")
    with st.spinner("Đang quét báo cáo tài chính..."):
        growth = get_earnings_growth(ticker)
        if growth is not None:
            if growth >= CANSLIM_GREAT:
                st.success(f"🔥 **Tiêu Chuẩn Vàng (Chữ C CANSLIM):** LNST tăng **+{growth}%**.")
            elif growth > 0:
                st.info(f"⚖️ **Tăng Trưởng Bền Vững:** LNST tăng **{growth}%**.")
            else:
                st.error(f"🚨 **Suy Yếu Nặng:** LNST giảm **{growth}%**.")
        else:
            st.warning("⚠️ Không lấy được dữ liệu LNST.")
        st.divider()
        pe, roe = get_pe_roe(ticker)
        c1, c2  = st.columns(2)
        if pe is None:
            c1.metric("P/E (Số Năm Thu Hồi Vốn)", "N/A", delta="Lỗi API", delta_color="off")
        else:
            if pe < PE_CHEAP:  pe_label, pe_color = "✅ Rất Tốt — Định Giá Rẻ", "normal"
            elif pe < PE_OK:   pe_label, pe_color = "⚖️ Hợp Lý", "normal"
            else:              pe_label, pe_color = "🚨 Đắt Đỏ (> 20 năm hoàn vốn)", "inverse"
            c1.metric("P/E (Số Năm Thu Hồi Vốn)", f"{pe:.1f} năm", delta=pe_label, delta_color=pe_color)
        st.write("> **P/E:** Số năm bạn cần để thu hồi vốn từ lợi nhuận. **< 12 = rẻ. > 20 = đắt.**")
        if roe is None:
            c2.metric("ROE (Sinh Lời Trên Vốn)", "N/A", delta="Lỗi API", delta_color="off")
        else:
            if roe >= ROE_EXCELLENT: roe_label, roe_color = "✅ Xuất Sắc (≥ 25%)", "normal"
            elif roe >= ROE_GOOD:    roe_label, roe_color = "⚖️ Tốt (15–25%)", "normal"
            else:                    roe_label, roe_color = "🚨 Dưới Chuẩn (< 15%)", "inverse"
            c2.metric("ROE (Sinh Lời Trên Vốn)", f"{roe:.1%}", delta=roe_label, delta_color=roe_color)
        st.write("> **ROE:** Phải ≥ 15% mới đáng xem xét đầu tư dài hạn.")

# ==============================================================================
# TAB 3: DÒNG TIỀN THÔNG MINH
# ==============================================================================
with tab3:
    st.write(f"### 🌊 Smart Flow Specialist — Mổ Xẻ Dòng Tiền 3 Bên ({ticker})")
    st.caption("So sánh **Khối Ngoại / Tự Doanh / Nhỏ Lẻ** theo từng phiên — xác định ai đang gom, ai đang xả.")

    with st.spinner("Đang tổng hợp dữ liệu dòng tiền 3 bên..."):
        df_for  = get_foreign(ticker,     FOREIGN_DAYS)
        df_prop = get_proprietary(ticker, FOREIGN_DAYS)
        df_price_flow = get_price(ticker, days=15)
        if valid(df_price_flow):
            df_price_flow = calc_indicators(df_price_flow)
        foreign_trend_t3 = analyze_foreign_trend(df_for)

    # ── Chuẩn bị dữ liệu 10 phiên ──
    def _extract_flow(df_src, days=10):
        """Trả về dict {date: {'buy': x, 'sell': y, 'net': z}} từ df ngoại/tự doanh."""
        if not valid(df_src):
            return {}
        rows = {}
        for _, r in df_src.tail(days).iterrows():
            d   = str(r.get('date', r.name))[:10]
            buy = to_billion(r.get('buyval',  0))
            sel = to_billion(r.get('sellval', 0))
            net = to_billion(r.get('netval',  buy - sel))
            rows[d] = {'buy': buy, 'sell': sel, 'net': net}
        return rows

    flow_foreign = _extract_flow(df_for,  10)
    flow_prop    = _extract_flow(df_prop, 10)

    # Lấy danh sách ngày chung (ưu tiên theo ngày của ngoại)
    all_dates = sorted(set(list(flow_foreign.keys()) + list(flow_prop.keys())))[-10:]

    # Nhỏ Lẻ ước tính = Tổng giá trị thị trường - Ngoại - Tự doanh
    retail_nets = []
    foreign_nets, prop_nets = [], []
    date_labels = []

    for d in all_dates:
        f_net = flow_foreign.get(d, {}).get('net', 0)
        p_net = flow_prop.get(d,    {}).get('net', 0)

        # Ước tính tổng giá trị phiên từ price data (close × volume)
        retail_net = 0.0
        if valid(df_price_flow) and 'date' in df_price_flow.columns:
            day_row = df_price_flow[df_price_flow['date'].astype(str).str[:10] == d]
            if not day_row.empty:
                total_val = to_billion(day_row.iloc[0]['close'] * day_row.iloc[0]['volume'])
                # Retail ≈ tổng phiên - |ngoại mua+bán| - |tự doanh mua+bán|
                f_gross = to_billion(df_for.loc[df_for['date'].astype(str).str[:10] == d, 'buyval'].sum()
                                     + df_for.loc[df_for['date'].astype(str).str[:10] == d, 'sellval'].sum()
                                     ) if valid(df_for) and 'date' in df_for.columns else 0
                p_gross = to_billion(df_prop.loc[df_prop['date'].astype(str).str[:10] == d, 'buyval'].sum()
                                     + df_prop.loc[df_prop['date'].astype(str).str[:10] == d, 'sellval'].sum()
                                     ) if valid(df_prop) and 'date' in df_prop.columns else 0
                retail_net = (total_val - f_gross - p_gross) * 0.1  # rough proxy

        foreign_nets.append(f_net)
        prop_nets.append(p_net)
        retail_nets.append(retail_net)
        date_labels.append(d[-5:])   # MM-DD

    # ── Chart 1: Grouped Bar — Net Flow 3 bên ──
    st.write("#### 📊 Dòng Tiền Ròng 3 Bên — 10 Phiên Gần Nhất (Tỷ VNĐ)")
    st.caption("Mua ròng (+) = thanh xanh | Bán ròng (−) = thanh đỏ theo từng bên")

    fig_multi = go.Figure()
    fig_multi.add_trace(go.Bar(
        x=date_labels, y=foreign_nets,
        name="🌏 Khối Ngoại",
        marker_color=['rgba(0,180,0,0.85)' if v >= 0 else 'rgba(220,0,0,0.85)' for v in foreign_nets],
        text=[f"{v:+.1f}" for v in foreign_nets],
        textposition='outside',
    ))
    fig_multi.add_trace(go.Bar(
        x=date_labels, y=prop_nets,
        name="🏦 Tự Doanh",
        marker_color=['rgba(0,100,255,0.75)' if v >= 0 else 'rgba(255,100,0,0.75)' for v in prop_nets],
        text=[f"{v:+.1f}" for v in prop_nets],
        textposition='outside',
    ))
    # Net tổng (Ngoại + Tự Doanh) dạng đường
    combined = [f + p for f, p in zip(foreign_nets, prop_nets)]
    fig_multi.add_trace(go.Scatter(
        x=date_labels, y=combined,
        name="📈 Tổng Ròng (Ngoại+TD)",
        mode='lines+markers',
        line=dict(color='gold', width=2.5),
        marker=dict(size=8),
    ))
    fig_multi.update_layout(
        barmode='group',
        height=380,
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Tỷ VNĐ",
        xaxis_title="Phiên giao dịch",
    )
    fig_multi.add_hline(y=0, line_color='black', line_width=1)
    st.plotly_chart(fig_multi, use_container_width=True)

    # ── Đọc tín hiệu tổng hợp 3 bên ──
    st.write("#### 🔍 Đọc Tín Hiệu Tổng Hợp")
    f_total  = sum(foreign_nets)
    p_total  = sum(prop_nets)
    combined_total = f_total + p_total

    sig_c1, sig_c2, sig_c3, sig_c4 = st.columns(4)
    sig_c1.metric("🌏 Ngoại Ròng 10P",  f"{f_total:+.1f} Tỷ",
                  delta="Mua ròng ✓" if f_total > 0 else "Bán ròng ⚠️",
                  delta_color="normal" if f_total > 0 else "inverse")
    sig_c2.metric("🏦 Tự Doanh Ròng 10P", f"{p_total:+.1f} Tỷ",
                  delta="Gom hàng ✓" if p_total > 0 else "Thoát hàng ⚠️",
                  delta_color="normal" if p_total > 0 else "inverse")
    sig_c3.metric("📊 Tổng Smart Money", f"{combined_total:+.1f} Tỷ",
                  delta="Tổ chức đồng thuận ✓" if combined_total > 0 else "Tổ chức rút lui ⚠️",
                  delta_color="normal" if combined_total > 0 else "inverse")
    # Đếm phiên đồng thuận gom (cả 2 bên cùng mua ròng)
    consensus_buy  = sum(1 for f, p in zip(foreign_nets, prop_nets) if f > 0 and p > 0)
    consensus_sell = sum(1 for f, p in zip(foreign_nets, prop_nets) if f < 0 and p < 0)
    sig_c4.metric("🤝 Phiên Đồng Thuận",
                  f"Gom: {consensus_buy} | Xả: {consensus_sell}",
                  delta="Đồng gom mạnh! ✓" if consensus_buy >= 5 else
                        ("Đồng xả! ⚠️" if consensus_sell >= 5 else "Phân hóa"),
                  delta_color="normal" if consensus_buy >= 5 else
                              ("inverse" if consensus_sell >= 5 else "off"))

    # ── Box đọc vị tổng ──
    if consensus_buy >= 6:
        st.success(
            f"🚨 **TÍN HIỆU VÀNG — Đồng Thuận Gom Mạnh!** "
            f"Cả Khối Ngoại lẫn Tự Doanh cùng mua ròng **{consensus_buy}/10 phiên**. "
            f"Smart money đang tích lũy phối hợp — xác suất tạo sóng rất cao."
        )
    elif f_total > 0 and p_total > 0:
        st.success(
            f"✅ **Tích Cực:** Cả 2 bên tổ chức đều mua ròng trong 10 phiên "
            f"(Ngoại {f_total:+.1f}Tỷ | TD {p_total:+.1f}Tỷ). Nền tảng dòng tiền vững."
        )
    elif f_total > 0 and p_total < 0:
        st.warning(
            f"⚠️ **Phân Kỳ Dòng Tiền:** Khối Ngoại mua ròng ({f_total:+.1f}Tỷ) "
            f"nhưng Tự Doanh đang xả ({p_total:+.1f}Tỷ). "
            f"Nội bộ thị trường chưa đồng thuận — vào lệnh nhỏ, theo dõi thêm."
        )
    elif f_total < 0 and p_total > 0:
        st.warning(
            f"⚠️ **Phân Kỳ Dòng Tiền:** Tự Doanh gom ({p_total:+.1f}Tỷ) "
            f"nhưng Khối Ngoại đang rút ({f_total:+.1f}Tỷ). "
            f"Dòng tiền nội địa tích cực, nhưng thiếu lực ngoại."
        )
    elif consensus_sell >= 5:
        st.error(
            f"🚨 **CẢNH BÁO ĐỎ:** Cả 2 bên tổ chức đồng loạt xả hàng "
            f"({consensus_sell}/10 phiên cùng bán ròng). Đứng ngoài chờ đáy."
        )
    else:
        st.info("🟡 Dòng tiền tổ chức đang phân hóa — chưa có tín hiệu rõ ràng từ hai phía.")

    st.divider()

    # ── Chart 2: Stacked Buy/Sell — Ngoại chi tiết ──
    st.write("#### 📊 Chi Tiết Mua/Bán Từng Bên (Gross Value)")
    if valid(df_for) or valid(df_prop):
        fig_detail = make_subplots(
            rows=1, cols=2,
            subplot_titles=("🌏 Khối Ngoại — Mua vs Bán (Tỷ)", "🏦 Tự Doanh — Mua vs Bán (Tỷ)"),
            shared_yaxes=False,
        )
        # Ngoại
        if valid(df_for) and 'date' in df_for.columns:
            f10 = df_for.tail(10)
            f_dates = f10['date'].astype(str).str[-5:].tolist()
            f_buys  = [to_billion(r.get('buyval',  0)) for _, r in f10.iterrows()]
            f_sells = [-to_billion(r.get('sellval', 0)) for _, r in f10.iterrows()]
            fig_detail.add_trace(go.Bar(x=f_dates, y=f_buys,  name="Ngoại Mua",
                                        marker_color='rgba(0,180,0,0.8)'), row=1, col=1)
            fig_detail.add_trace(go.Bar(x=f_dates, y=f_sells, name="Ngoại Bán",
                                        marker_color='rgba(220,0,0,0.8)'), row=1, col=1)
        # Tự Doanh
        if valid(df_prop) and 'date' in df_prop.columns:
            p10 = df_prop.tail(10)
            p_dates = p10['date'].astype(str).str[-5:].tolist()
            p_buys  = [to_billion(r.get('buyval',  0)) for _, r in p10.iterrows()]
            p_sells = [-to_billion(r.get('sellval', 0)) for _, r in p10.iterrows()]
            fig_detail.add_trace(go.Bar(x=p_dates, y=p_buys,  name="TD Mua",
                                        marker_color='rgba(0,100,255,0.8)'), row=1, col=2)
            fig_detail.add_trace(go.Bar(x=p_dates, y=p_sells, name="TD Bán",
                                        marker_color='rgba(255,100,0,0.8)'), row=1, col=2)
        fig_detail.update_layout(
            barmode='relative', height=320, template='plotly_white',
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation='h', yanchor='bottom', y=1.05),
        )
        fig_detail.add_hline(y=0, line_color='black', line_width=0.8, row=1, col=1)
        fig_detail.add_hline(y=0, line_color='black', line_width=0.8, row=1, col=2)
        st.plotly_chart(fig_detail, use_container_width=True)
    else:
        st.warning("⚠️ Không có đủ dữ liệu để vẽ chart chi tiết.")

    st.divider()

    # ── Dòng tiền 3 nhóm + Gom/Xả (giữ nguyên từ V22) ──
    net_v = sum(foreign_nets) if foreign_nets else 0.0
    df_flow = get_price(ticker, days=30)
    if valid(df_flow):
        df_flow   = calc_indicators(df_flow)
        last_fl   = df_flow.iloc[-1]
        vol       = last_fl['vol_strength']
        ret       = last_fl['return_1d']
        flow_info = classify_flow_group(vol, ret, net_v)
        st.write("#### 📊 Phân Tích Tỷ Trọng Dòng Tiền 3 Nhóm")
        g1, g2, g3 = st.columns(3)
        inst_pct = flow_info['inst_pct']
        if flow_info['group'] == "🦈 Cá Mập":
            shark_pct = inst_pct;  org_pct = max(0, 1 - shark_pct - 0.2)
        elif flow_info['group'] == "🏦 Tổ Chức Nội":
            shark_pct = 0.05;      org_pct = inst_pct - shark_pct
        else:
            shark_pct, org_pct = 0.02, 0.13
        retail_pct_final = max(0, 1 - shark_pct - org_pct)
        g1.metric("🦈 Cá Mập",      f"{shark_pct*100:.1f}%",
                  delta="Đang Mạnh" if flow_info['group'] == "🦈 Cá Mập" else "Ít Tham Gia",
                  delta_color="normal" if flow_info['group'] == "🦈 Cá Mập" else "off")
        g2.metric("🏦 Tổ Chức Nội", f"{org_pct*100:.1f}%",
                  delta="Tích Lũy"  if flow_info['group'] == "🏦 Tổ Chức Nội" else "Bình Thường",
                  delta_color="normal" if flow_info['group'] == "🏦 Tổ Chức Nội" else "off")
        g3.metric("🐜 Nhỏ Lẻ",      f"{retail_pct_final*100:.1f}%",
                  delta="⚠️ Đu Bám Nhiều" if retail_pct_final > 0.6 else "Ổn Định",
                  delta_color="inverse" if retail_pct_final > 0.6 else "off")
        st.info(f"**Nhóm chủ đạo:** {flow_info['group']} — {flow_info['description']}")
        st.divider()
        action_msg = f"**{flow_info['action']}**\n\n_{flow_info['action_note']}_"
        if "GOM"  in flow_info['action']:  st.success(action_msg)
        elif "XẢ" in flow_info['action']:  st.error(action_msg)
        else:                               st.warning(action_msg)

# ==============================================================================
# TAB 4: RADAR TRUY QUÉT [NÂNG CẤP #15 — Hiển Thị Nâng Cao]
# ==============================================================================
with tab4:
    st.subheader("🔍 Máy Quét Định Lượng Robot Hunter V22.0 — Predator Leviathan")
    st.write(
        "Tự động phân loại thành **3 tầng**: "
        "🚀 **BÙNG NỔ** | ⚖️ **DANH SÁCH CHỜ** | 👁️ **VÙNG QUAN SÁT**"
    )
    st.info(
        "💡 **V22.0:** Bảng kết quả hiển thị **Progress Bar AI**, **màu sắc theo ngưỡng**, "
        "**ADX sức mạnh xu hướng**, và **Card view** cho từng mã — dễ đọc hơn hoàn toàn."
    )

    view_mode = st.radio(
        "Chế độ hiển thị kết quả:",
        ["📊 Bảng Tổng Hợp (nhanh)", "🃏 Card Chi Tiết (đầy đủ)"],
        horizontal=True
    )

    if st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT 4 TẦNG (REAL-TIME) — V23.0"):
        # [V19] Market Breadth trước khi scan
        st.write("#### 🏥 Sức Khỏe Thị Trường (Market Breadth)")
        with st.spinner("Đang đo sức khỏe thị trường..."):
            sample_50 = tuple(list(dict.fromkeys(tickers))[:50])
            breadth   = calc_market_breadth(sample_50)
        if breadth['total'] > 0:
            mb1, mb2, mb3, mb4 = st.columns(4)
            mb1.metric("Trạng thái thị trường", breadth['market_status'])
            mb2.metric("% Mã trên MA20", f"{breadth['pct_above_ma20']:.1f}%",
                       delta="Mạnh ✓" if breadth['pct_above_ma20'] >= 60 else "Yếu ⚠️",
                       delta_color="normal" if breadth['pct_above_ma20'] >= 60 else "inverse")
            mb3.metric("% RSI lành mạnh (<55)", f"{breadth['pct_rsi_ok']:.1f}%",
                       delta="Chưa quá mua ✓" if breadth['pct_rsi_ok'] >= 50 else "Đang nóng",
                       delta_color="normal" if breadth['pct_rsi_ok'] >= 50 else "off")
            mb4.metric("Tỷ lệ mã tăng/giảm", f"{breadth['advance_decline']:.1f}%",
                       delta="Nhiều mã xanh ✓" if breadth['advance_decline'] >= 55 else "Phân hóa",
                       delta_color="normal" if breadth['advance_decline'] >= 55 else "off")
            st.caption(f"💡 Dựa trên {breadth['total']} mã mẫu. "
                       "Breadth > 60% = thị trường bull thực sự, an toàn để tìm mua. "
                       "Breadth < 40% = cẩn thận, chỉ mua mã RS Rating cao.")
        st.divider()

        scan_list = list(dict.fromkeys(tickers))[:RADAR_MAX]
        st.caption(f"🔭 Đang quét {len(scan_list)} mã trên HOSE...")
        progress    = st.progress(0)
        breakouts   = []
        watchlist   = []
        wave_bottom = []   # [V23 #24] Tầng mới
        watch_zone  = []

        # Lấy VN-Index 1 lần (cached) cho RS Rating toàn bộ scan
        df_vnidx = get_vnindex_cached()

        for i, t in enumerate(scan_list):
            try:
                df_s = get_price(t, days=SCAN_DAYS)
                if not valid(df_s):
                    continue
                df_s     = calc_indicators(df_s)
                ai_s     = predict_ai_t3(df_s)
                weekly_s = get_weekly_trend(df_s)
                label    = classify_stock(t, df_s, ai_s, weekly_s)
                if label is None:
                    continue
                last_s   = df_s.iloc[-1]

                # Tín hiệu cơ bản
                bb_now   = last_s['bb_width']
                bb_min20 = df_s['bb_width'].tail(20).min()
                squeezed = bb_now <= bb_min20 * BB_SQUEEZE_TOL
                supply   = df_s['can_cung'].tail(5).any()
                smart    = False
                for fn in [get_foreign, get_proprietary]:
                    fd = fn(t, FOREIGN_DAYS)
                    if valid(fd) and calc_net_flow(fd, 3) > 0:
                        smart = True
                        break

                # [V23] RS Rating, Divergence, 52W, Wave Bottom
                rs_s    = calc_rs_rating(df_s, df_vnidx)
                div_s   = detect_divergence(df_s)
                w52_s   = calc_52w_info(df_s)
                wave_s  = calc_wave_bottom_score(df_s, last_s)

                row = {
                    'Ticker':       t,
                    'Thị Giá':      f"{last_s['close']:,.0f}",
                    'Vol Raw':      float(last_s['vol_strength']),
                    'RSI Raw':      float(last_s['rsi']),
                    'AI T+3 Raw':   ai_s,
                    'Weekly Raw':   weekly_s,
                    'ADX Raw':      float(last_s.get('adx', 0)),
                    'RS Raw':       rs_s,
                    'Lò Xo BB':     bool(squeezed),
                    'Cạn Cung':     bool(supply),
                    'Tổ Chức Gom':  bool(smart),
                    '52W High':     bool(w52_s['near_high']),
                    'Div Bullish':  bool(div_s['signal'] == 'BULLISH'),
                    'Div Bearish':  bool(div_s['signal'] == 'BEARISH'),
                    'Wave Bottom':  bool(wave_s['is_wave_bottom']),
                    'Wave Score':   wave_s['score'],
                }
                if "Bùng Nổ"     in label: breakouts.append(row)
                elif "Danh Sách" in label: watchlist.append(row)
                elif "Chân Sóng" in label: wave_bottom.append(row)   # [V23]
                elif "Quan Sát"  in label: watch_zone.append(row)
            except Exception as e:
                print(f"[WARN] Scan {t}: {e}")
            progress.progress((i + 1) / len(scan_list))

        # --- Banner tổng kết ---
        st.divider()
        render_radar_summary_banner(breakouts, watchlist, wave_bottom, watch_zone)
        st.divider()

        use_cards = "Card" in view_mode

        # ── TẦNG 1: BÙNG NỔ ──
        st.write("### 🚀 Tầng 1 — Bùng Nổ")
        st.caption("⚠️ Vol đã nổ mạnh — cẩn thận mua đuổi đỉnh. Chờ điều chỉnh về MA20 mới vào.")
        if breakouts:
            if use_cards:
                for r in breakouts: render_radar_card(r, "red")
            else:
                render_radar_table(breakouts)
        else:
            st.success("✅ Không có mã bùng nổ hôm nay.")

        st.divider()

        # ── TẦNG 2: DANH SÁCH CHỜ ──
        st.write("### ⚖️ Tầng 2 — Danh Sách Chờ Chân Sóng")
        st.caption("Nền đẹp + Weekly xác nhận + Tổ chức đang gom. Đây là nhóm ưu tiên nhất.")
        if watchlist:
            if use_cards:
                for r in watchlist: render_radar_card(r, "green")
            else:
                render_radar_table(watchlist)
            st.success(f"✅ {len(watchlist)} mã đủ tiêu chuẩn. Phân tích chi tiết từng mã ở Tab 1 trước khi vào lệnh.")
        else:
            st.info("Hôm nay chưa có mã đủ tiêu chuẩn — thị trường cần thêm thời gian tích lũy.")

        st.divider()

        # ── TẦNG 3: CHÂN SÓNG [V23 MỚI] ──
        st.write("### 🌊 Tầng 3 — Chân Sóng (V23 — Bắt sóng sớm)")
        st.caption(
            "Phát hiện mã đang tích lũy nền, chưa bứt phá nhưng đủ tiêu chí chân sóng. "
            "**Rủi ro cao hơn Tầng 2** — vào nhỏ (10–15% vốn), đặt SL chặt theo ATR."
        )
        if wave_bottom:
            if use_cards:
                for r in wave_bottom: render_radar_card(r, "blue")
            else:
                render_radar_table(wave_bottom)
            st.info(
                f"🌊 {len(wave_bottom)} mã đang ở vùng chân sóng tiềm năng. "
                "Chờ thêm 1–2 phiên xác nhận (Vol nổ + Nến xanh) trước khi vào lệnh chính thức."
            )
        else:
            st.write("Không có mã chân sóng hôm nay.")

        st.divider()

        # ── TẦNG 4: VÙNG QUAN SÁT ──
        st.write("### 👁️ Tầng 4 — Vùng Quan Sát (Tín hiệu sớm)")
        st.caption("Có 1–2 tín hiệu sớm. Chưa đủ điều kiện — theo dõi 2–3 phiên tiếp theo.")
        if watch_zone:
            if use_cards:
                for r in watch_zone: render_radar_card(r, "gray")
            else:
                render_radar_table(watch_zone)
            st.info(f"💡 {len(watch_zone)} mã đang hình thành tín hiệu.")
        else:
            st.write("Không có mã trong vùng quan sát.")

        # ── Hướng dẫn đọc bảng ──
        st.divider()
        with st.expander("📖 Hướng dẫn đọc bảng kết quả Radar V23.0"):
            st.markdown("""
| Cột | Ý nghĩa | Ngưỡng tốt |
|-----|---------|-----------|
| **AI T+3** | Xác suất tăng ≥2% sau 3 phiên (XGBoost) | ≥ 55% = tốt, ≥ 70% = rất tốt |
| **RS Rating** | Sức mạnh so VN-Index 3 tháng (0–100) | ≥ 70 = mạnh hơn thị trường |
| **RSI** | Chỉ số quá mua/bán | 35–52 = vùng hồi phục lý tưởng |
| **Vol** | Khối lượng / TB 10 phiên | 0.8–1.2x = tích lũy, > 1.3x = bùng nổ |
| **ADX** | Sức mạnh xu hướng | > 25 = xu hướng rõ ràng |
| **Weekly** | Xu hướng khung tuần | 📈 TĂNG = an toàn nhất |
| **BB Sqz** 🌀 | Bollinger Band co lại — chuẩn bị bùng | Có = tốt |
| **Cạn Cung** 💧 | Vol thấp trên nến đỏ — người bán cạn | Có = tốt |
| **Tổ Chức** 🦈 | Ngoại/tự doanh mua ròng 3 phiên | Có = tốt |
| **52W ↑** 🏆 | Giá gần đỉnh 52 tuần (trong 8%) | Có = CANSLIM mạnh |
| **Div** | 📈 Phân kỳ dương (sắp tăng) / 📉 âm (cảnh báo) | 📈 = tốt |
| **Chân Sóng** 🌊 | Điểm chân sóng /8 tiêu chí [V23] | ≥ 3 = đáng chú ý |
            """)

# ==============================================================================
# TAB 5: SECTOR ROTATION
# ==============================================================================
with tab5:
    st.subheader("🏭 Sector Rotation — Bản Đồ Dòng Tiền Luân Chuyển Ngành")
    st.write(
        "Phát hiện dòng tiền đang **chảy vào ngành nào** dựa trên "
        "hiệu suất trung bình 5 ngày của các mã đại diện trong mỗi ngành."
    )
    st.warning("⏱️ Quét ngành mất 2-3 phút. Chạy 1 lần/ngày là đủ.")
    if st.button("🔭 QUÉT DÒNG TIỀN LUÂN CHUYỂN NGÀNH"):
        with st.spinner("Đang quét hiệu suất toàn ngành..."):
            sector_result = analyze_sector_rotation(tickers)
        if sector_result:
            best  = list(sector_result.keys())[0]
            worst = list(sector_result.keys())[-1]
            st.success(f"🏆 **Ngành đang được bơm mạnh nhất: {best}** (+{sector_result[best]:.2f}% TB 5 ngày)")
            st.error(f"🚨 **Ngành yếu nhất: {worst}** ({sector_result[worst]:.2f}% TB 5 ngày)")
            sectors = list(sector_result.keys())
            perf    = list(sector_result.values())
            colors  = ['green' if v > 0 else 'red' for v in perf]
            fig_s   = go.Figure(go.Bar(
                x=perf, y=sectors, orientation='h',
                marker_color=colors, text=[f"{v:+.2f}%" for v in perf],
                textposition='outside'
            ))
            fig_s.update_layout(
                height=500, title="Hiệu Suất Trung Bình 5 Ngày Theo Ngành (%)",
                xaxis_title="% Tăng/Giảm", template='plotly_white',
                margin=dict(l=150, r=60, t=50, b=40)
            )
            st.plotly_chart(fig_s, use_container_width=True)
            ticker_sec = get_ticker_sector(ticker)
            if ticker_sec:
                sec_perf = sector_result.get(ticker_sec, 0)
                rank     = list(sector_result.keys()).index(ticker_sec) + 1
                if sec_perf > 0:
                    st.success(f"📍 **{ticker}** thuộc ngành **{ticker_sec}** — "
                               f"Xếp hạng #{rank}/{len(sector_result)} | "
                               f"Hiệu suất ngành: {sec_perf:+.2f}%")
                else:
                    st.warning(f"📍 **{ticker}** thuộc ngành **{ticker_sec}** — "
                               f"Xếp hạng #{rank}/{len(sector_result)} | "
                               f"Hiệu suất ngành: {sec_perf:+.2f}% (Ngành đang yếu)")
            else:
                st.info(f"ℹ️ {ticker} chưa được phân loại ngành trong hệ thống.")
            st.divider()
            st.write("#### 📋 Bảng Xếp Hạng Chi Tiết")
            df_sec = pd.DataFrame({
                'Ngành':              sectors,
                'Hiệu Suất 5 Ngày':  perf,
                'Tín Hiệu':          ["🟢 Dòng tiền vào" if v > 0.5 else
                                       ("🔴 Dòng tiền ra" if v < -0.5 else "🟡 Trung lập") for v in perf]
            })
            st.dataframe(
                df_sec,
                use_container_width=True,
                column_config={
                    "Hiệu Suất 5 Ngày": st.column_config.ProgressColumn(
                        "Hiệu Suất 5 Ngày (%)",
                        min_value=-5,
                        max_value=5,
                        format="%+.2f%%",
                    ),
                    "Ngành": st.column_config.TextColumn("Ngành"),
                    "Tín Hiệu": st.column_config.TextColumn("Tín Hiệu"),
                },
                hide_index=True,
            )

# ==============================================================================
# HẾT MÃ NGUỒN — QUANT SYSTEM V22.0 SUPREME
# NÂNG CẤP: #10 ATR Stop | #11 ADX+OBV | #12 Kelly | #13 Cache AI | #14 Sharpe+MaxDD
# NÂNG CẤP: #15 Radar Display — Table màu ProgressBar + Card View + Summary Banner
# ==============================================================================
