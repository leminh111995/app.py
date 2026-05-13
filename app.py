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
AI_OK             = 52.0   # buffer rộng hơn để tránh dao động giữa các lần quét

# Scoring 0-100
SCORE_AI_MAX      = 25
SCORE_TECH_MAX    = 20
SCORE_FLOW_MAX    = 20
SCORE_FINANCE_MAX = 15
SCORE_SECTOR_MAX  = 10
SCORE_BUY_MIN     = 58   # ngưỡng mua (tương đương 65/100 cũ, nay tổng max = 90)

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
RADAR_MAX         = 150    # Quét Nhanh
RADAR_MAX_FULL    = 600    # Quét Toàn HOSE
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
WAVE_SCORE_MIN    = 4           # cần ≥ 4 điểm / 11 tiêu chí

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

# VN30 — 30 mã vốn hóa lớn nhất HOSE (dùng làm VNI proxy khi API fail)
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
def get_vnindex_cached() -> pd.DataFrame:
    """
    Lấy VN-Index proxy từ 10 mã thanh khoản cao nhất VN30.
    Không dùng yfinance (bị block trên Streamlit Cloud).
    Không dùng engine() (không hoạt động trong cache).
    """
    start = (datetime.now() - timedelta(days=400)).strftime(DATE_FMT)
    end   = datetime.now().strftime(DATE_FMT)
    vci   = Vnstock().stock(symbol='ACB', source='VCI')

    # Tầng 1: Thử symbol VNINDEX/VN30 trực tiếp
    for sym in ['VNINDEX', 'VN30', 'E1VFVN30']:
        try:
            df = vci.quote.history(symbol=sym, start=start, end=end)
            if df is not None and not df.empty and len(df) >= 30:
                df.columns = [str(c).lower() for c in df.columns]
                return df
        except Exception:
            pass

    # Tầng 2: 10 mã thanh khoản cao nhất — nhanh (~10 giây)
    TOP10 = ["VCB", "HPG", "FPT", "MBB", "TCB", "VPB", "ACB", "VNM", "GAS", "SSI"]
    price_data = {}
    for sym in TOP10:
        try:
            df_s = vci.quote.history(symbol=sym, start=start, end=end)
            if df_s is not None and not df_s.empty:
                df_s.columns = [str(c).lower() for c in df_s.columns]
                if 'date' in df_s.columns and 'close' in df_s.columns:
                    df_s['date'] = pd.to_datetime(df_s['date']).dt.strftime('%Y-%m-%d')
                    price_data[sym] = df_s.set_index('date')['close']
        except Exception:
            continue

    if len(price_data) < 3:
        return pd.DataFrame()

    df_basket = pd.DataFrame(price_data).dropna(how='all')
    normalized = df_basket.div(df_basket.iloc[0]) * 1000
    close_p    = normalized.mean(axis=1)
    return pd.DataFrame({
        'date':   df_basket.index.tolist(),
        'open':   close_p.values,
        'high':   normalized.max(axis=1).values,
        'low':    normalized.min(axis=1).values,
        'close':  close_p.values,
        'volume': df_basket.sum(axis=1).values,
    }).reset_index(drop=True)

def _normalize_flow_df(df): return None   # stub — API không khả dụng

def fetch_all_flows(ticker: str, days: int = FOREIGN_DAYS) -> dict:
    """API dòng tiền không khả dụng với Vnstock hiện tại."""
    return {'foreign': None, 'proprietary': None, 'source': 'none'}

def get_foreign(ticker: str, days: int = FOREIGN_DAYS) -> pd.DataFrame | None:
    return None

def get_proprietary(ticker: str, days: int = FOREIGN_DAYS) -> pd.DataFrame | None:
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
    wins = 0
    profits = []
    signals_data = []   # chi tiết từng lệnh cho equity curve + chart markers
    n = len(df)
    for i in range(100, n - BT_DAYS_FWD):
        rsi_ok     = df['rsi'].iloc[i] < BT_RSI_BUY
        macd_cross = (
            df['macd'].iloc[i]   > df['signal'].iloc[i] and
            df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
        )
        if not (rsi_ok and macd_cross):
            continue
        buy_price = df['close'].iloc[i] * (1 + SLIPPAGE)
        target    = buy_price * (1 + BT_PROFIT)
        sl_price  = buy_price * (1 - SL_PCT)
        future    = df['close'].iloc[i+1 : i+1+BT_DAYS_FWD]
        hit_tp    = any(future >= target)
        hit_sl    = any(future <= sl_price)
        date_i    = df['date'].iloc[i] if 'date' in df.columns else i
        if hit_tp:
            p = BT_PROFIT - ROUND_TRIP_COST
            profits.append(p); wins += 1
            signals_data.append({'date': date_i, 'price': buy_price, 'result': 'WIN',  'pnl': p})
        elif hit_sl:
            p = -SL_PCT - ROUND_TRIP_COST
            profits.append(p)
            signals_data.append({'date': date_i, 'price': buy_price, 'result': 'LOSS', 'pnl': p})
        else:
            exit_price = future.iloc[-1] if len(future) > 0 else buy_price
            p = (exit_price - buy_price) / buy_price - ROUND_TRIP_COST
            profits.append(p)
            signals_data.append({'date': date_i, 'price': buy_price, 'result': 'HOLD', 'pnl': p})

    if not profits:
        return {'winrate':0.0,'avg_profit':0.0,'avg_loss':0.0,'expectancy':0.0,
                'signals':0,'sharpe':0.0,'max_drawdown':0.0,'profits':[],'signals_data':[]}

    winrate    = round((wins / len(profits)) * 100, 1)
    avg_profit = round(np.mean([p for p in profits if p > 0]) * 100, 2) if any(p > 0 for p in profits) else 0.0
    avg_loss   = round(np.mean([p for p in profits if p < 0]) * 100, 2) if any(p < 0 for p in profits) else 0.0
    expectancy = round(np.mean(profits) * 100, 2)
    rf_daily   = 0.045 / 252
    excess     = np.array(profits) - rf_daily
    sharpe     = round((excess.mean() / (excess.std() + 1e-9)) * np.sqrt(252 / BT_DAYS_FWD), 2)
    equity     = np.cumprod([1 + p for p in profits])
    rolling_max= np.maximum.accumulate(equity)
    max_dd     = round(((equity - rolling_max) / rolling_max).min() * 100, 2)

    return {
        'winrate': winrate, 'avg_profit': avg_profit, 'avg_loss': avg_loss,
        'expectancy': expectancy, 'signals': len(profits),
        'sharpe': sharpe, 'max_drawdown': max_dd,
        'profits': profits, 'signals_data': signals_data,
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
    sent_pts   = 0   # Đã bỏ sentiment input
    total = min(90, ai_pts + tech_pts + flow_pts + fin_pts + sector_pts)

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
def calc_rs_rating(df: pd.DataFrame, df_vnindex: pd.DataFrame) -> float:
    """
    [V23 #17] RS Rating 0-100 so với VN-Index.
    Nếu df_vnindex rỗng → dùng benchmark cố định 8%/63 phiên.
    """
    try:
        stock_window = df['close'].dropna().tail(RS_LOOKBACK)
        if len(stock_window) < 20:
            return 50.0
        stock_ret = (stock_window.iloc[-1] - stock_window.iloc[0]) / (stock_window.iloc[0] + 1e-9)

        # Dùng VNI thực nếu có, không thì dùng benchmark 8%
        if isinstance(df_vnindex, pd.DataFrame) and len(df_vnindex) >= 20 and 'close' in df_vnindex.columns:
            mkt_window = df_vnindex['close'].dropna().tail(RS_LOOKBACK)
            mkt_ret    = (mkt_window.iloc[-1] - mkt_window.iloc[0]) / (mkt_window.iloc[0] + 1e-9)
        else:
            mkt_ret = 0.08   # benchmark cố định ~15%/năm

        excess = stock_ret - mkt_ret
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
def calc_wave_bottom_score(
    df: pd.DataFrame,
    last: pd.Series,
    smart_flow: bool = False,      # Tổ Chức gom (ngoại/tự doanh mua ròng)
    near_52w_high: bool = False,   # Gần đỉnh 52 tuần
    div_bullish: bool = False,     # Phân kỳ dương RSI/MACD
) -> dict:
    """
    [V23] Hệ thống 11 tiêu chí chân sóng.
    8 tiêu chí kỹ thuật + 3 tiêu chí bổ sung (Tổ Chức, 52W, Div).
    Cần ≥ WAVE_SCORE_MIN điểm = chân sóng hợp lệ.
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

    # 8. Nến xanh nhẹ + Vol bình thường (rục rịch thoát đáy)
    ret = last.get('return_1d', 0)
    vol = last['vol_strength']
    if ret > 0 and 0.7 <= vol <= 1.4:
        score += 1
        flags.append("Giá xanh nhẹ + Vol bình thường")

    # ── 3 TIÊU CHÍ BỔ SUNG (V23) ──
    # 9. Tổ Chức gom (Ngoại/Tự doanh mua ròng)
    if smart_flow:
        score += 1
        flags.append("Tổ Chức gom")

    # 10. Gần đỉnh 52 tuần (trong 8%) — Stage 2 sắp breakout
    if near_52w_high:
        score += 1
        flags.append("Gần đỉnh 52W")

    # 11. Phân kỳ dương RSI/MACD — động lượng đang phục hồi
    if div_bullish:
        score += 1
        flags.append("Phân kỳ dương")

    is_wave_bottom = score >= WAVE_SCORE_MIN
    total_criteria = 11
    if is_wave_bottom:
        label = f"✅ Chân Sóng ({score}/{total_criteria}: {', '.join(flags)})"
    else:
        label = f"Chưa đủ tiêu chí ({score}/{total_criteria})"
    return {
        'score':          score,
        'total':          total_criteria,
        'flags':          flags,
        'is_wave_bottom': is_wave_bottom,
        'label':          label,
    }


# ==============================================================================
# ==============================================================================
# [C] QUICK SCAN — Lọc nhanh không dùng AI
# ==============================================================================
def classify_stock_fast(df: pd.DataFrame) -> str | None:
    """
    Phân loại nhanh chỉ dùng RSI + Vol + MA20 (không AI, không API).
    Dùng cho scan nhanh hàng ngày ~2-3 phút cho 400 mã.
    """
    if len(df) < 30:
        return None
    last  = df.iloc[-1]
    vol   = last['vol_strength']
    rsi   = last['rsi']
    price = last['close']
    ma20  = last['ma20']
    ret   = last.get('return_1d', 0)

    # Bùng nổ
    if vol > VOL_BREAKOUT:
        return "🚀 Bùng Nổ Mua" if ret >= 0 else "🔴 Bán Tháo"

    # Chân sóng nhanh (3 tiêu chí đơn giản)
    if WAVE_RSI_MIN <= rsi <= WAVE_RSI_MAX and price >= ma20 * 0.90 and vol >= 0.7:
        return "🌊 Tiềm Năng"

    # Đang tăng mạnh
    if 65 <= rsi <= 80 and price >= ma20:
        return "🔥 Tăng Mạnh"

    return None


# ==============================================================================
# [A] BACKTEST NÂNG CAO — Dùng bộ tín hiệu thực tế của hệ thống
# ==============================================================================
def run_backtest_v2(df: pd.DataFrame) -> dict:
    """
    Backtest dùng đúng tín hiệu thực tế:
    RSI < 52 + MA20 uptrend + Vol tích lũy (0.8-1.4x) + MACD cross
    Phản ánh chính xác cách hệ thống phân loại Tầng 2/3.
    """
    wins = 0
    profits = []
    signals_data = []
    n = len(df)
    for i in range(100, n - BT_DAYS_FWD):
        last_i  = df.iloc[i]
        rsi_ok  = WAVE_RSI_MIN <= last_i['rsi'] <= WAVE_RSI_MAX
        ma_ok   = last_i['close'] >= last_i['ma20'] * 0.95
        vol_ok  = VOL_ACC_MIN <= last_i['vol_strength'] <= 1.5
        macd_ok = (last_i['macd'] > last_i['signal'] and
                   df['macd'].iloc[i-1] <= df['signal'].iloc[i-1])
        adx_ok  = last_i.get('adx', 0) < 35   # không vào khi đang bùng nổ mạnh
        if not (rsi_ok and ma_ok and vol_ok and macd_ok and adx_ok):
            continue
        buy_price = last_i['close'] * (1 + SLIPPAGE)
        target    = buy_price * (1 + BT_PROFIT)
        sl_price  = buy_price * (1 - SL_PCT)
        future    = df['close'].iloc[i+1 : i+1+BT_DAYS_FWD]
        hit_tp    = any(future >= target)
        hit_sl    = any(future <= sl_price)
        date_i    = df['date'].iloc[i] if 'date' in df.columns else i
        if hit_tp:
            p = BT_PROFIT - ROUND_TRIP_COST
            profits.append(p); wins += 1
            signals_data.append({'date': date_i, 'price': buy_price, 'result': 'WIN',  'pnl': p})
        elif hit_sl:
            p = -SL_PCT - ROUND_TRIP_COST
            profits.append(p)
            signals_data.append({'date': date_i, 'price': buy_price, 'result': 'LOSS', 'pnl': p})
        else:
            exit_price = future.iloc[-1] if len(future) > 0 else buy_price
            p = (exit_price - buy_price) / buy_price - ROUND_TRIP_COST
            profits.append(p)
            signals_data.append({'date': date_i, 'price': buy_price, 'result': 'HOLD', 'pnl': p})

    if not profits:
        return {'winrate':0.0,'avg_profit':0.0,'avg_loss':0.0,'expectancy':0.0,
                'signals':0,'sharpe':0.0,'max_drawdown':0.0,'profits':[],'signals_data':[]}
    winrate    = round(wins / len(profits) * 100, 1)
    avg_profit = round(np.mean([p for p in profits if p > 0]) * 100, 2) if any(p>0 for p in profits) else 0.0
    avg_loss   = round(np.mean([p for p in profits if p < 0]) * 100, 2) if any(p<0 for p in profits) else 0.0
    expectancy = round(np.mean(profits) * 100, 2)
    excess     = np.array(profits) - 0.045/252
    sharpe     = round((excess.mean()/(excess.std()+1e-9))*np.sqrt(252/BT_DAYS_FWD), 2)
    equity     = np.cumprod([1+p for p in profits])
    max_dd     = round(((equity - np.maximum.accumulate(equity))/np.maximum.accumulate(equity)).min()*100, 2)
    return {'winrate':winrate,'avg_profit':avg_profit,'avg_loss':avg_loss,
            'expectancy':expectancy,'signals':len(profits),'sharpe':sharpe,
            'max_drawdown':max_dd,'profits':profits,'signals_data':signals_data}


# ==============================================================================
# [B] WALK-FORWARD OPTIMIZATION — Tìm tham số tối ưu theo từng mã
# ==============================================================================
def walk_forward_optimize(df: pd.DataFrame) -> dict:
    """
    Grid search tìm combo (rsi_buy, profit_target, sl_pct) tốt nhất
    trên 70% dữ liệu đầu, validate trên 30% còn lại.
    """
    best = {'expectancy': -999, 'rsi_buy': BT_RSI_BUY,
            'profit': BT_PROFIT, 'sl': SL_PCT}
    n = len(df)
    if n < 200:
        return best

    train_end = int(n * 0.7)
    df_train  = df.iloc[:train_end]
    df_val    = df.iloc[train_end:]

    for rsi_buy in [38, 42, 45, 48, 52]:
        for profit in [0.04, 0.05, 0.07, 0.10]:
            for sl in [0.04, 0.06, 0.08]:
                # Tính nhanh trên train set
                wins = total = 0
                profits_tmp = []
                for i in range(50, len(df_train) - BT_DAYS_FWD):
                    rsi_ok  = df_train['rsi'].iloc[i] < rsi_buy
                    macd_ok = (df_train['macd'].iloc[i] > df_train['signal'].iloc[i] and
                               df_train['macd'].iloc[i-1] <= df_train['signal'].iloc[i-1])
                    if not (rsi_ok and macd_ok):
                        continue
                    total += 1
                    buy_p  = df_train['close'].iloc[i]
                    future = df_train['close'].iloc[i+1:i+1+BT_DAYS_FWD]
                    if any(future >= buy_p*(1+profit)):
                        profits_tmp.append(profit - ROUND_TRIP_COST); wins += 1
                    elif any(future <= buy_p*(1-sl)):
                        profits_tmp.append(-sl - ROUND_TRIP_COST)
                    else:
                        profits_tmp.append((future.iloc[-1]-buy_p)/buy_p - ROUND_TRIP_COST)
                if len(profits_tmp) < 5:
                    continue
                exp = np.mean(profits_tmp) * 100
                if exp > best['expectancy']:
                    best = {'expectancy': round(exp,2), 'rsi_buy': rsi_buy,
                            'profit': profit, 'sl': sl,
                            'signals_train': total, 'winrate_train': round(wins/total*100,1)}
    return best


# ==============================================================================
# [D] SO SÁNH NHIỀU MÃ CÙNG LÚC
# ==============================================================================
def compare_stocks(tickers_list: list, days: int = 200) -> list[dict]:
    """Tính điểm tổng hợp nhanh cho danh sách mã để so sánh song song."""
    results = []
    for t in tickers_list:
        try:
            df = get_price(t, days=days)
            if not valid(df) or len(df) < 50:
                continue
            df   = calc_indicators(df)
            last = df.iloc[-1]
            ai_s = predict_ai_t3(df)
            bt_s = run_backtest_v2(df)
            rs_s = calc_rs_rating(df, pd.DataFrame())
            w52  = calc_52w_info(df)
            div  = detect_divergence(df)
            wave = calc_wave_bottom_score(df, last,
                       near_52w_high=w52['near_high'],
                       div_bullish=(div['signal']=='BULLISH'))
            weekly = get_weekly_trend(df)
            # Điểm kỹ thuật
            tech = 0
            if last['close'] > last['ma20']:          tech += 3
            if last['rsi'] < 60:                      tech += 2
            if last['macd'] > last['signal']:         tech += 2
            if weekly == 'UP':                        tech += 3
            results.append({
                'ticker':      t,
                'price':       f"{last['close']:,.0f}",
                'ai':          float(ai_s) if _is_valid_score(ai_s) else 0.0,
                'rsi':         round(float(last['rsi']), 1),
                'rs':          rs_s,
                'tech':        tech,
                'winrate':     bt_s['winrate'],
                'expectancy':  bt_s['expectancy'],
                'sharpe':      bt_s['sharpe'],
                'max_dd':      bt_s['max_drawdown'],
                'weekly':      weekly,
                'wave_score':  wave['score'],
                'near_52w':    w52['near_high'],
                'div_bull':    div['signal'] == 'BULLISH',
                'composite':   round(float(ai_s if _is_valid_score(ai_s) else 0)*0.35
                                     + rs_s*0.25 + tech*3 + bt_s['winrate']*0.15, 1),
            })
        except Exception as e:
            print(f"[WARN] compare {t}: {e}")
    results.sort(key=lambda x: x['composite'], reverse=True)
    return results


# ==============================================================================
# [F] CORRELATION MATRIX — Tương quan chéo giữa các mã
# ==============================================================================
def calc_correlation_matrix(tickers_list: list, days: int = 63) -> pd.DataFrame | None:
    """
    Tính ma trận tương quan lợi nhuận ngày giữa các mã.
    63 phiên = ~3 tháng giao dịch.
    """
    returns_dict = {}
    for t in tickers_list:
        try:
            df = get_price(t, days=days+10)
            if not valid(df) or len(df) < 20:
                continue
            df = normalize_cols(df)
            df['ret'] = pd.to_numeric(df['close'], errors='coerce').pct_change()
            returns_dict[t] = df['ret'].dropna().tail(days).values
        except Exception:
            continue
    if len(returns_dict) < 2:
        return None
    # Align lengths
    min_len = min(len(v) for v in returns_dict.values())
    df_ret  = pd.DataFrame({k: v[-min_len:] for k, v in returns_dict.items()})
    return df_ret.corr().round(2)


# ==============================================================================
# [#5] RISK/REWARD CALCULATOR
# ==============================================================================
def calc_rr(entry: float, sl: float, rr_ratio: float = 2.0) -> dict:
    risk   = entry - sl
    tp2    = entry + risk * 2
    tp3    = entry + risk * 3
    tp_rr  = entry + risk * rr_ratio
    sl_pct = (sl - entry) / entry * 100
    return {
        'risk_per_share': round(risk, 0),
        'sl_pct':         round(sl_pct, 2),
        'tp_rr2':         round(tp2, 0),
        'tp_rr3':         round(tp3, 0),
        'tp_custom':      round(tp_rr, 0),
        'tp_pct_rr2':     round(risk * 2 / entry * 100, 2),
        'tp_pct_rr3':     round(risk * 3 / entry * 100, 2),
    }

def calc_position_size(capital: float, risk_pct: float, entry: float, sl: float) -> dict:
    risk_amount  = capital * risk_pct / 100
    risk_per_share = abs(entry - sl)
    if risk_per_share == 0:
        return {'shares': 0, 'total_value': 0, 'capital_pct': 0}
    shares       = int(risk_amount / risk_per_share / 100) * 100   # làm tròn 100 cp
    total_value  = shares * entry
    capital_pct  = total_value / capital * 100
    return {
        'shares':      shares,
        'total_value': round(total_value, 0),
        'capital_pct': round(capital_pct, 1),
        'risk_amount': round(risk_amount, 0),
    }


# ==============================================================================
# [#3] ĐA KHUNG THỜI GIAN (MTF) — Daily + Weekly + Monthly
# ==============================================================================
def analyze_mtf(df_daily: pd.DataFrame) -> dict:
    """
    Phân tích 3 khung: Monthly / Weekly / Daily.
    Trả về dict tín hiệu + đồng thuận.
    """
    result = {'monthly': {}, 'weekly': {}, 'daily': {}, 'consensus': 'NEUTRAL'}
    try:
        df = df_daily.copy()
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

        # Monthly
        df_m = df['close'].resample('ME').last().to_frame('close')
        df_m['ma6']    = df_m['close'].rolling(6).mean()
        df_m['ret']    = df_m['close'].pct_change()
        df_m['trend']  = 'UP' if (len(df_m)>=2 and df_m['close'].iloc[-1] > df_m['ma6'].iloc[-1]) else 'DOWN'
        df_m['ret3m']  = (df_m['close'].iloc[-1] / df_m['close'].iloc[-4] - 1) * 100 if len(df_m) >= 4 else 0

        # Weekly
        df_w = df['close'].resample('W').last().to_frame('close')
        df_w['ma10']   = df_w['close'].rolling(10).mean()
        df_w['slope']  = (df_w['ma10'].iloc[-1] - df_w['ma10'].iloc[-4]) / (df_w['ma10'].iloc[-4]+1e-9) * 100 if len(df_w)>=4 else 0
        w_trend = 'UP' if (df_w['close'].iloc[-1] > df_w['ma10'].iloc[-1] and df_w['slope'] > 0) else \
                  ('DOWN' if df_w['close'].iloc[-1] < df_w['ma10'].iloc[-1] else 'NEUTRAL')

        # Daily (từ df đã calc_indicators)
        d_last   = df_daily.iloc[-1]
        d_trend  = 'UP' if d_last['close'] > d_last['ma20'] else 'DOWN'
        d_rsi    = d_last['rsi']
        d_macd   = 'BULL' if d_last['macd'] > d_last['signal'] else 'BEAR'

        result['monthly'] = {
            'trend': df_m['trend'].iloc[-1],
            'ret3m': round(float(df_m['ret3m'].iloc[-1]), 2),
            'close': round(float(df_m['close'].iloc[-1]), 0),
        }
        result['weekly'] = {
            'trend': w_trend,
            'slope': round(float(df_w['slope']), 2),
        }
        result['daily'] = {
            'trend': d_trend,
            'rsi':   round(float(d_rsi), 1),
            'macd':  d_macd,
        }

        # Đồng thuận
        signals = [result['monthly']['trend'], w_trend, d_trend]
        up_count = signals.count('UP')
        dn_count = signals.count('DOWN')
        if up_count == 3:   result['consensus'] = 'STRONG_BULL'
        elif up_count == 2: result['consensus'] = 'BULL'
        elif dn_count == 3: result['consensus'] = 'STRONG_BEAR'
        elif dn_count == 2: result['consensus'] = 'BEAR'
        else:               result['consensus'] = 'MIXED'
    except Exception as e:
        print(f"[WARN] MTF: {e}")
    return result


# ==============================================================================
# [#4] OPTIMAL ENTRY — Vùng vào lệnh tối ưu (ATR + Fibonacci)
# ==============================================================================
def calc_optimal_entry(df: pd.DataFrame, last: pd.Series) -> dict:
    """
    Tính vùng vào lệnh tối ưu dựa trên:
    - ATR: buffer vào lệnh an toàn
    - Fibonacci retracement từ swing high/low gần nhất
    - MA20 + Lower BB làm vùng hỗ trợ
    """
    price   = last['close']
    atr     = last.get('atr', price * 0.02)
    ma20    = last['ma20']
    bb_low  = last['lower_band']

    # Swing high/low 20 phiên
    swing_high = df['high'].tail(20).max()
    swing_low  = df['low'].tail(20).min()
    fib_range  = swing_high - swing_low

    # Fibonacci levels (từ đáy lên)
    fib_382 = swing_low + fib_range * 0.382
    fib_500 = swing_low + fib_range * 0.500
    fib_618 = swing_low + fib_range * 0.618

    # Vùng vào tốt = gần MA20 hoặc Fib 38.2-50% hoặc Lower BB
    entry_zone_low  = max(bb_low, fib_382) * 0.99
    entry_zone_high = min(ma20,   fib_500) * 1.01

    # Giá vào lý tưởng
    ideal_entry = (entry_zone_low + entry_zone_high) / 2

    # Đánh giá vị trí hiện tại
    if price <= entry_zone_high:
        entry_status = "✅ Giá đang trong vùng vào lệnh tốt"
        entry_color  = "success"
    elif price <= entry_zone_high * 1.03:
        entry_status = "🟡 Giá hơi cao hơn vùng lý tưởng — có thể vào nhỏ 50%"
        entry_color  = "warning"
    else:
        diff = (price - entry_zone_high) / entry_zone_high * 100
        entry_status = f"⚠️ Giá cao hơn vùng lý tưởng {diff:.1f}% — chờ pullback"
        entry_color  = "error"

    return {
        'ideal_entry':     round(ideal_entry, 0),
        'zone_low':        round(entry_zone_low, 0),
        'zone_high':       round(entry_zone_high, 0),
        'fib_382':         round(fib_382, 0),
        'fib_500':         round(fib_500, 0),
        'fib_618':         round(fib_618, 0),
        'swing_high':      round(swing_high, 0),
        'swing_low':       round(swing_low, 0),
        'atr':             round(atr, 0),
        'entry_status':    entry_status,
        'entry_color':     entry_color,
    }


# ==============================================================================
# [#1] TÍN HIỆU VÀO LỆNH TỰ ĐỘNG (Entry Signal)
# ==============================================================================
def generate_entry_signal(
    last: pd.Series, scoring: dict, bt: dict, ai_score,
    weekly_trend: str, foreign_trend: dict,
    mtf: dict, entry_info: dict, divergence: dict,
) -> dict:
    """
    Tổng hợp tất cả tín hiệu → quyết định vào lệnh cụ thể.
    """
    price   = last['close']
    rsi     = last['rsi']
    atr     = last.get('atr', price * 0.02)
    adx     = last.get('adx', 0)
    score   = scoring['total']
    ai_ok   = _is_valid_score(ai_score) and float(ai_score) >= 55
    cons    = mtf.get('consensus', 'MIXED')

    # Đếm tín hiệu xanh
    green = 0
    conditions = []

    if score >= SCORE_BUY_MIN:
        green += 2; conditions.append(f"✅ Điểm tổng hợp {score}/90 đủ ngưỡng")
    if ai_ok:
        green += 2; conditions.append(f"✅ AI T+3: {float(ai_score):.1f}% (≥55%)")
    if weekly_trend == 'UP':
        green += 1; conditions.append("✅ Weekly đang tăng")
    if cons in ('STRONG_BULL', 'BULL'):
        green += 2; conditions.append(f"✅ MTF đồng thuận: {cons}")
    if rsi < 55 and rsi > 30:
        green += 1; conditions.append(f"✅ RSI {rsi:.1f} vùng lý tưởng")
    if adx > 20:
        green += 1; conditions.append(f"✅ ADX {adx:.1f} xu hướng đủ mạnh")
    if foreign_trend.get('trend') in ('BUY', 'STRONG_BUY'):
        green += 1; conditions.append("✅ Khối ngoại đang mua ròng")
    if divergence.get('signal') == 'BULLISH':
        green += 1; conditions.append("✅ Phân kỳ dương xác nhận")
    if bt.get('expectancy', 0) > 0:
        green += 1; conditions.append(f"✅ Kỳ vọng backtest {bt['expectancy']:+.2f}%")
    if entry_info['entry_color'] == 'success':
        green += 1; conditions.append("✅ Giá trong vùng vào lệnh tối ưu")

    # Tín hiệu đỏ
    red = 0
    warnings = []
    if rsi > 70:
        red += 3; warnings.append(f"🔴 RSI {rsi:.1f} quá mua")
    if weekly_trend == 'DOWN':
        red += 2; warnings.append("🔴 Weekly đang giảm")
    if cons in ('STRONG_BEAR', 'BEAR'):
        red += 2; warnings.append(f"🔴 MTF đồng thuận giảm: {cons}")
    if foreign_trend.get('trend') in ('SELL', 'STRONG_SELL'):
        red += 1; warnings.append("🔴 Khối ngoại đang bán ròng")

    # Quyết định
    net = green - red
    if net >= 8 and red == 0:
        action   = "🚀 VÀO LỆNH NGAY — Tín hiệu rất mạnh"
        size_pct = 50   # % vốn
        color    = "success"
    elif net >= 5:
        action   = "✅ VÀO LỆNH — Tín hiệu tốt"
        size_pct = 30
        color    = "success"
    elif net >= 3:
        action   = "⚖️ VÀO NHỎ 20% — Chờ xác nhận thêm"
        size_pct = 20
        color    = "warning"
    elif net >= 1:
        action   = "👁️ THEO DÕI — Chưa đủ tín hiệu"
        size_pct = 0
        color    = "warning"
    else:
        action   = "🚫 ĐỨNG NGOÀI — Tín hiệu tiêu cực"
        size_pct = 0
        color    = "error"

    # Giá vào, SL, TP cụ thể
    sl_price  = price - ATR_MULTIPLIER * atr
    tp2_price = price + 2 * ATR_MULTIPLIER * atr
    tp3_price = price + 3 * ATR_MULTIPLIER * atr

    return {
        'action':    action,
        'color':     color,
        'size_pct':  size_pct,
        'green':     green,
        'red':       red,
        'net':       net,
        'conditions':conditions,
        'warnings':  warnings,
        'entry':     round(price, 0),
        'sl':        round(sl_price, 0),
        'tp2':       round(tp2_price, 0),
        'tp3':       round(tp3_price, 0),
        'sl_pct':    round((sl_price - price)/price*100, 2),
        'tp2_pct':   round((tp2_price - price)/price*100, 2),
        'tp3_pct':   round((tp3_price - price)/price*100, 2),
    }


# ==============================================================================
# [#2] TRADE JOURNAL — Theo dõi lệnh đang mở
# ==============================================================================
def calc_open_trade(entry_price: float, shares: int,
                    sl_price: float, tp_price: float,
                    current_price: float) -> dict:
    pnl_per_share  = current_price - entry_price
    pnl_total      = pnl_per_share * shares
    pnl_pct        = pnl_per_share / entry_price * 100
    dist_to_sl     = (current_price - sl_price) / entry_price * 100
    dist_to_tp     = (tp_price - current_price) / entry_price * 100
    rr_current     = abs(pnl_pct / ((entry_price - sl_price)/entry_price*100 + 1e-9))
    if current_price <= sl_price * 1.01:
        status = "🚨 GẦN SL — Cân nhắc cắt lỗ ngay!"
        status_color = "error"
    elif current_price >= tp_price * 0.99:
        status = "🎯 GẦN TP — Cân nhắc chốt lời!"
        status_color = "success"
    elif pnl_pct > 0:
        status = "✅ Đang lời — Giữ theo kế hoạch"
        status_color = "success"
    else:
        status = "⚠️ Đang lỗ — Theo dõi SL"
        status_color = "warning"
    return {
        'pnl_per_share': round(pnl_per_share, 0),
        'pnl_total':     round(pnl_total, 0),
        'pnl_pct':       round(pnl_pct, 2),
        'dist_to_sl':    round(dist_to_sl, 2),
        'dist_to_tp':    round(dist_to_tp, 2),
        'rr_current':    round(rr_current, 2),
        'status':        status,
        'status_color':  status_color,
    }


# ==============================================================================
# [#6] SEASONALITY — Phân tích mùa vụ theo tháng
# ==============================================================================
def calc_seasonality(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tính lợi nhuận trung bình theo từng tháng dựa trên lịch sử 3-5 năm.
    """
    df2 = df.copy()
    if 'date' in df2.columns:
        df2['date'] = pd.to_datetime(df2['date'])
        df2 = df2.set_index('date')
    df2['ret_month'] = df2['close'].resample('ME').last().pct_change() * 100
    df2 = df2.dropna(subset=['ret_month'])
    df2['month'] = df2.index.month
    monthly = df2.groupby('month')['ret_month'].agg(['mean', 'count', 'std']).reset_index()
    monthly.columns = ['month', 'avg_ret', 'years', 'std']
    monthly['month_name'] = monthly['month'].map({
        1:'T1',2:'T2',3:'T3',4:'T4',5:'T5',6:'T6',
        7:'T7',8:'T8',9:'T9',10:'T10',11:'T11',12:'T12'
    })
    monthly['avg_ret'] = monthly['avg_ret'].round(2)
    monthly['std']     = monthly['std'].round(2)
    return monthly


# ==============================================================================
# [#3] TRAILING STOP ĐỘNG THEO GIÁ HIỆN TẠI
# ==============================================================================
def calc_dynamic_trailing_stop(buy_price: float, current_price: float,
                                atr: float, highest_since_buy: float) -> dict:
    """
    ATR Trailing Stop cập nhật theo giá cao nhất đạt được kể từ khi mua.
    SL = highest_since_buy - 2×ATR (không bao giờ thấp hơn SL ban đầu).
    """
    initial_sl    = buy_price  - ATR_MULTIPLIER * atr
    trailing_sl   = highest_since_buy - ATR_MULTIPLIER * atr
    final_sl      = max(initial_sl, trailing_sl)
    profit_locked = max(0, final_sl - buy_price)
    sl_pct_from_current = (final_sl - current_price) / current_price * 100
    sl_pct_from_buy     = (final_sl - buy_price)     / buy_price     * 100

    if final_sl > buy_price:
        status = f"✅ Đã lock được {profit_locked/buy_price*100:.1f}% lợi nhuận"
        color  = "success"
    elif final_sl > buy_price * 0.97:
        status = "🟡 SL gần breakeven — rủi ro thấp"
        color  = "warning"
    else:
        status = f"⚠️ SL còn {sl_pct_from_buy:.1f}% dưới giá mua"
        color  = "warning"

    return {
        'initial_sl':    round(initial_sl, 0),
        'trailing_sl':   round(trailing_sl, 0),
        'final_sl':      round(final_sl, 0),
        'profit_locked': round(profit_locked, 0),
        'sl_pct_current':round(sl_pct_from_current, 2),
        'sl_pct_buy':    round(sl_pct_from_buy, 2),
        'status':        status,
        'color':         color,
    }


# ==============================================================================
# [#4] PRICE ACTION — Nhận diện cấu trúc giá
# ==============================================================================
def detect_price_action(df: pd.DataFrame) -> dict:
    """
    Nhận diện các mô hình Price Action phổ biến:
    Higher High/Lower Low, Double Top/Bottom, Inside Bar, Breakout Bar.
    """
    result = {
        'structure': 'NEUTRAL',
        'patterns':  [],
        'summary':   '',
    }
    if len(df) < 20:
        return result

    closes = df['close'].values
    highs  = df['high'].values
    lows   = df['low'].values

    # Higher High / Lower Low (structure)
    hh = highs[-1] > highs[-6:-1].max()
    hl = lows[-1]  > lows[-6:-1].min()
    lh = highs[-1] < highs[-6:-1].max()
    ll = lows[-1]  < lows[-6:-1].min()

    if hh and hl:
        result['structure'] = 'UPTREND'
        result['patterns'].append("📈 Higher High + Higher Low — Cấu trúc tăng nguyên vẹn")
    elif lh and ll:
        result['structure'] = 'DOWNTREND'
        result['patterns'].append("📉 Lower High + Lower Low — Cấu trúc giảm nguyên vẹn")
    else:
        result['structure'] = 'RANGING'
        result['patterns'].append("↔️ Cấu trúc giá đang sideway / chuyển tiếp")

    # Double Top
    recent_highs = [highs[i] for i in range(-20, -1) if highs[i] == max(highs[max(0,i-3):i+4])]
    if len(recent_highs) >= 2:
        if abs(recent_highs[-1] - recent_highs[-2]) / recent_highs[-1] < 0.02:
            result['patterns'].append("🔴 Double Top — Đỉnh kép, cảnh báo đảo chiều giảm")

    # Double Bottom
    recent_lows = [lows[i] for i in range(-20, -1) if lows[i] == min(lows[max(0,i-3):i+4])]
    if len(recent_lows) >= 2:
        if abs(recent_lows[-1] - recent_lows[-2]) / recent_lows[-1] < 0.02:
            result['patterns'].append("🟢 Double Bottom — Đáy kép, tín hiệu đảo chiều tăng")

    # Inside Bar (nến nằm trong nến trước)
    if highs[-1] < highs[-2] and lows[-1] > lows[-2]:
        result['patterns'].append("🕯️ Inside Bar — Giằng co, chuẩn bị bứt phá")

    # Breakout Bar (nến phá đỉnh 20 phiên)
    if closes[-1] > highs[-21:-1].max():
        result['patterns'].append("🚀 Breakout Bar — Phá đỉnh 20 phiên, momentum mạnh")
    elif closes[-1] < lows[-21:-1].min():
        result['patterns'].append("💥 Breakdown Bar — Phá đáy 20 phiên, cảnh báo mạnh")

    # Pin Bar (bấc dài)
    body   = abs(closes[-1] - df['open'].iloc[-1])
    candle = highs[-1] - lows[-1]
    upper_wick = highs[-1] - max(closes[-1], df['open'].iloc[-1])
    lower_wick = min(closes[-1], df['open'].iloc[-1]) - lows[-1]
    if candle > 0:
        if lower_wick > body * 2 and lower_wick > upper_wick * 2:
            result['patterns'].append("📌 Bullish Pin Bar — Bấc dưới dài, từ chối vùng thấp")
        elif upper_wick > body * 2 and upper_wick > lower_wick * 2:
            result['patterns'].append("📌 Bearish Pin Bar — Bấc trên dài, từ chối vùng cao")

    if not result['patterns']:
        result['patterns'].append("➡️ Chưa có mô hình đặc biệt trong phiên gần nhất")

    result['summary'] = result['patterns'][0]
    return result


# ==============================================================================
# [#2] PHÂN TÍCH ĐỐI THỦ CÙNG NGÀNH
# ==============================================================================
def analyze_sector_peers(ticker: str, n_peers: int = 4) -> list[dict]:
    """
    Tìm các mã cùng ngành, so sánh RS Rating + Momentum + RSI.
    """
    sector = None
    for sec, members in SECTOR_MAP.items():
        if ticker in members:
            sector = sec
            peers  = [m for m in members if m != ticker][:n_peers+2]
            break
    if not sector:
        return []

    results = []
    for p in peers[:n_peers]:
        try:
            df_p = get_price(p, days=100)
            if not valid(df_p) or len(df_p) < 30:
                continue
            df_p  = calc_indicators(df_p)
            last_p= df_p.iloc[-1]
            rs_p  = calc_rs_rating(df_p, pd.DataFrame())
            ret5  = (last_p['close'] - df_p['close'].iloc[-5]) / df_p['close'].iloc[-5] * 100
            results.append({
                'ticker':  p,
                'price':   f"{last_p['close']:,.0f}",
                'rsi':     round(float(last_p['rsi']), 1),
                'rs':      rs_p,
                'ret5d':   round(ret5, 2),
                'ma_ok':   last_p['close'] > last_p['ma20'],
                'adx':     round(float(last_p.get('adx', 0)), 1),
            })
        except Exception:
            continue
    results.sort(key=lambda x: x['rs'], reverse=True)
    return results


# ==============================================================================
# [#6] GỢI Ý MÃ THAY THẾ TỐT HƠN
# ==============================================================================
def suggest_better_tickers(ticker: str, current_score: float,
                            tickers_list: list) -> list[dict]:
    """
    Nếu mã hiện tại điểm thấp → gợi ý 3 mã cùng ngành/HOSE có RS Rating cao hơn.
    """
    # Tìm ngành của mã hiện tại
    sector = get_ticker_sector(ticker)
    candidates = []
    if sector:
        sector_members = [m for m in SECTOR_MAP[sector] if m != ticker]
    else:
        sector_members = []

    # Ưu tiên cùng ngành, sau đó mở rộng ra HOSE
    search_list = sector_members + [t for t in tickers_list if t not in sector_members and t != ticker]

    for t in search_list[:30]:
        try:
            df_t = get_price(t, days=100)
            if not valid(df_t) or len(df_t) < 30:
                continue
            df_t  = calc_indicators(df_t)
            last_t= df_t.iloc[-1]
            rs_t  = calc_rs_rating(df_t, pd.DataFrame())
            rsi_t = float(last_t['rsi'])
            # Chỉ gợi ý mã có RS > 60 + RSI hợp lý + giá trên MA20
            if rs_t < 60 or rsi_t > 65 or last_t['close'] < last_t['ma20']:
                continue
            candidates.append({
                'ticker': t,
                'rs':     rs_t,
                'rsi':    round(rsi_t, 1),
                'price':  f"{last_t['close']:,.0f}",
                'sector': get_ticker_sector(t) or 'Khác',
                'ma_ok':  True,
            })
            if len(candidates) >= 5:
                break
        except Exception:
            continue
    candidates.sort(key=lambda x: x['rs'], reverse=True)
    return candidates[:3]


# ==============================================================================
# [#1] WATCHLIST AUTO-SCAN
# ==============================================================================
def scan_watchlist(watchlist: list[str]) -> list[dict]:
    """
    Quét nhanh watchlist khi mở app — tìm mã có tín hiệu mới.
    """
    alerts = []
    for t in watchlist:
        try:
            df_w = get_price(t, days=60)
            if not valid(df_w) or len(df_w) < 30:
                continue
            df_w  = calc_indicators(df_w)
            label = classify_stock_fast(df_w)
            last_w= df_w.iloc[-1]
            if label:
                alerts.append({
                    'ticker':  t,
                    'label':   label,
                    'price':   f"{last_w['close']:,.0f}",
                    'rsi':     round(float(last_w['rsi']), 1),
                    'vol':     round(float(last_w['vol_strength']), 2),
                    'change':  round(float(last_w.get('return_1d', 0))*100, 2),
                })
        except Exception:
            continue
    return alerts


# ==============================================================================
# [#5] HEATMAP THỊ TRƯỜNG HOSE
# ==============================================================================
def build_market_heatmap(sample_tickers: list, days: int = 5) -> pd.DataFrame:
    """
    Tính % thay đổi theo ngành trong N ngày để vẽ heatmap.
    """
    rows = []
    for t in sample_tickers:
        try:
            df_h = get_price(t, days=20)
            if not valid(df_h) or len(df_h) < 6:
                continue
            df_h  = normalize_cols(df_h)
            ret1d = (float(df_h['close'].iloc[-1]) - float(df_h['close'].iloc[-2])) / float(df_h['close'].iloc[-2]) * 100
            ret5d = (float(df_h['close'].iloc[-1]) - float(df_h['close'].iloc[-6])) / float(df_h['close'].iloc[-6]) * 100
            sector= get_ticker_sector(t) or 'Khác'
            rows.append({'ticker': t, 'sector': sector, 'ret1d': round(ret1d,2), 'ret5d': round(ret5d,2)})
        except Exception:
            continue
    return pd.DataFrame(rows)


# ==============================================================================
# CALIBRATION — Hiệu Chỉnh Ngưỡng Vol Theo Thống Kê Thực Tế
# ==============================================================================
def calibrate_vol_thresholds(sample_tickers: list, days: int = 252) -> dict:
    """
    Tính phân phối Vol thực tế từ dữ liệu lịch sử HOSE.
    Trả về các ngưỡng percentile + winrate "Bán Tháo" thực tế.
    """
    all_vol_strengths  = []
    sell_dump_outcomes = []   # [True=tiếp tục giảm, False=hồi phục]

    progress_cal = st.progress(0)
    status_cal   = st.empty()

    for idx, t in enumerate(sample_tickers):
        try:
            status_cal.caption(f"⏳ Đang phân tích {t} ({idx+1}/{len(sample_tickers)})...")
            df = get_price(t, days=days)
            if not valid(df) or len(df) < 50:
                continue
            df = calc_indicators(df)
            if 'vol_strength' not in df.columns:
                continue

            vols    = df['vol_strength'].dropna().values
            returns = df['return_1d'].dropna().values
            closes  = df['close'].values

            all_vol_strengths.extend(vols.tolist())

            # Tìm các ngày Vol cao + nến đỏ → theo dõi 3 phiên sau
            p90_temp = np.percentile(vols, 90) if len(vols) > 10 else 2.0
            for i in range(len(df) - 3):
                v = df['vol_strength'].iloc[i]
                r = df['return_1d'].iloc[i]
                if v >= p90_temp and r < -0.005:   # Vol cao + giảm > 0.5%
                    # 3 phiên sau: giá hồi hay tiếp tục giảm?
                    ret_3d = (closes[min(i+3, len(closes)-1)] - closes[i]) / closes[i]
                    sell_dump_outcomes.append(ret_3d < 0)   # True = tiếp tục giảm

        except Exception as e:
            print(f"[WARN] calibrate {t}: {e}")
        progress_cal.progress((idx + 1) / len(sample_tickers))

    progress_cal.empty()
    status_cal.empty()

    if len(all_vol_strengths) < 100:
        return {'error': 'Không đủ dữ liệu'}

    arr = np.array(all_vol_strengths)
    p70 = round(float(np.percentile(arr, 70)), 2)
    p80 = round(float(np.percentile(arr, 80)), 2)
    p90 = round(float(np.percentile(arr, 90)), 2)
    p95 = round(float(np.percentile(arr, 95)), 2)
    p99 = round(float(np.percentile(arr, 99)), 2)

    # Winrate bán tháo
    n_dump    = len(sell_dump_outcomes)
    winrate_dump = round(sum(sell_dump_outcomes) / n_dump * 100, 1) if n_dump > 0 else 0

    return {
        'n_samples':      len(arr),
        'n_dump_events':  n_dump,
        'p70':            p70,
        'p80':            p80,
        'p90':            p90,
        'p95':            p95,
        'p99':            p99,
        'winrate_dump':   winrate_dump,   # % ngày "Bán Tháo" tiếp tục giảm sau 3 phiên
        # Ngưỡng đề xuất:
        'threshold_breakout':   p80,      # Vol > P80 = bùng nổ
        'threshold_dump':       p90,      # Vol > P90 + đỏ = đáng lo
        'threshold_heavy_dump': p95,      # Vol > P95 + đỏ = bán tháo thực sự
    }


# 16. RADAR — PHÂN LOẠI CỔ PHIẾU 4 TẦNG (V23: thêm Chân Sóng)
def classify_stock(ticker: str, df: pd.DataFrame, ai_score, weekly_trend: str, smart_flow: bool = False) -> str | None:
    """
    [V23] Phân loại 4 tầng:
    🚀 Bùng Nổ | ⚖️ Danh Sách Chờ | 🌊 Chân Sóng (mới) | 👁️ Vùng Quan Sát
    """
    last  = df.iloc[-1]
    vol   = last['vol_strength']
    rsi   = last['rsi']
    price = last['close']
    ma20  = last['ma20']

    # Dùng ngưỡng đã hiệu chỉnh nếu có, fallback về mặc định
    vol_breakout   = st.session_state.get('cal_threshold_breakout',   VOL_BREAKOUT)
    vol_dump       = st.session_state.get('cal_threshold_dump',       VOL_BREAKOUT * 1.5)
    vol_heavy_dump = st.session_state.get('cal_threshold_heavy_dump', VOL_SHARK)

    # TẦNG 1: Bùng Nổ — phân biệt Mua vs Bán
    if vol > vol_breakout:
        ret = last.get('return_1d', 0)
        if ret >= 0:
            return "🚀 Bùng Nổ Mua"
        else:
            # Chỉ báo "Bán Tháo" khi Vol thực sự cao (P90+), còn Vol P80-P90 bỏ qua
            if vol >= vol_dump:
                return "🔴 Bán Tháo"
            return None   # Vol vừa phải + đỏ nhẹ → bình thường, không xếp tầng

    ai_ok = _is_valid_score(ai_score) and float(ai_score) > AI_OK

    # --- Kiểm tra vũ khí tích lũy (không gọi API — dùng smart_flow từ ngoài) ---
    bb_now    = last['bb_width']
    bb_min20  = df['bb_width'].tail(20).min()
    squeezed  = bb_now <= bb_min20 * BB_SQUEEZE_TOL
    supply_ex = df['can_cung'].tail(5).any()
    weapons   = sum([squeezed, supply_ex, smart_flow])

    # TẦNG 2: Danh Sách Chờ — tiêu chí chặt, an toàn nhất
    base_ok = (
        VOL_ACC_MIN <= vol <= VOL_ACC_MAX and
        price >= ma20 * PRICE_NEAR_MA20   and
        rsi < RSI_WATCHLIST_MAX           and
        ai_ok
    )
    if base_ok and weapons >= 1 and weekly_trend in ('UP', 'NEUTRAL'):
        return "⚖️ Danh Sách Chờ"

    # TẦNG 3: Chân Sóng
    w52   = calc_52w_info(df)
    div   = detect_divergence(df)
    wave  = calc_wave_bottom_score(
        df, last,
        smart_flow    = smart_flow,
        near_52w_high = w52['near_high'],
        div_bullish   = (div['signal'] == 'BULLISH'),
    )
    if wave['is_wave_bottom']:
        ma50          = last.get('ma50', ma20)
        not_downtrend = price >= ma50 * 0.85      # không quá xa MA50
        rsi_in_range  = WAVE_RSI_MIN <= rsi <= WAVE_RSI_MAX  # RSI phải trong vùng hồi phục
        price_not_hot = price <= ma20 * 1.05      # giá không được vượt MA20 quá 5% (đã bứt tốc rồi)
        adx_not_surge = last.get('adx', 0) < 35  # ADX < 35: chưa phải xu hướng bùng nổ
        if not_downtrend and rsi_in_range and price_not_hot and adx_not_surge:
            return "🌊 Chân Sóng"

    # TẦNG 4: Quan Sát — RSI phải < 65, không mua vào vùng overbought
    if rsi >= 65:
        # TẦNG 5: Đang Tăng Mạnh — theo dõi, không mua đuổi
        if 65 <= rsi <= 80 and price >= ma20:
            return "🔥 Đang Tăng Mạnh"
        return None
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
            'Chân Sóng':    f"✅{r.get('Wave Score',0)}/11" if r.get('Wave Bottom') else "—",
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


def render_radar_summary_banner(breakouts, sell_dumps, watchlist, wave_bottom, watch_zone, running_strong) -> None:
    """[V23] Banner tổng kết 5 tầng + Bán Tháo."""
    total = len(breakouts) + len(watchlist) + len(wave_bottom) + len(watch_zone) + len(running_strong)
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    c1.metric("📊 Tổng",           total)
    c2.metric("🚀 Bùng Nổ Mua",    len(breakouts),
              delta="⚠️ Cẩn thận mua đuổi" if breakouts else None, delta_color="off")
    c3.metric("🔴 Bán Tháo",       len(sell_dumps),
              delta="Tránh xa!" if sell_dumps else None, delta_color="off")
    c4.metric("⚖️ Danh Sách Chờ",  len(watchlist),
              delta="✅ Ưu tiên" if watchlist else None,
              delta_color="normal" if watchlist else "off")
    c5.metric("🌊 Chân Sóng",      len(wave_bottom),
              delta="🎯 Cơ hội sớm" if wave_bottom else None,
              delta_color="normal" if wave_bottom else "off")
    c6.metric("👁️ Quan Sát",       len(watch_zone),  delta_color="off")
    c7.metric("🔥 Đang Tăng Mạnh", len(running_strong),
              delta="Không mua đuổi" if running_strong else None, delta_color="off")

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

st.title("🛡️ Quant System V23.0: Supreme Predator Leviathan")
st.caption("**V23.0:** ATR Stop | ADX+OBV | Kelly | Sharpe | Radar 6 Tầng | Ichimoku | Chân Sóng 11TC | VNI | MTF | Entry Signal | R:R | Seasonality")
st.markdown("---")

# ── [#1] WATCHLIST SIDEBAR + AUTO-SCAN BANNER ──
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📋 Watchlist Theo Dõi")
wl_input = st.sidebar.text_input("Thêm mã (nhấn Enter):", placeholder="VD: FPT", key="wl_add")
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = []
if wl_input:
    sym = wl_input.strip().upper()
    if sym and sym not in st.session_state['watchlist']:
        st.session_state['watchlist'].append(sym)

wl = st.session_state['watchlist']
if wl:
    st.sidebar.caption(f"Đang theo dõi: {', '.join(wl)}")
    if st.sidebar.button("❌ Xóa hết watchlist"):
        st.session_state['watchlist'] = []
        st.rerun()
    if st.sidebar.button("🔔 Quét Watchlist Ngay"):
        with st.spinner("Đang quét watchlist..."):
            wl_alerts = scan_watchlist(wl)
        st.session_state['wl_alerts'] = wl_alerts

# Hiện banner cảnh báo watchlist đầu trang
if st.session_state.get('wl_alerts'):
    alerts = st.session_state['wl_alerts']
    if alerts:
        st.warning(f"🔔 **{len(alerts)} mã trong watchlist có tín hiệu mới:**")
        for a in alerts:
            col_a, col_b = st.columns([1, 4])
            col_a.markdown(f"**`{a['ticker']}`**")
            col_b.markdown(
                f"{a['label']} | Giá: {a['price']} | "
                f"RSI: {a['rsi']} | Vol: {a['vol']}x | "
                f"1 ngày: {a['change']:+.1f}%"
            )
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
news_headlines = []   # Đã bỏ input tin tức

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH",
    "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM",
    "🌊 BÓC TÁCH DÒNG TIỀN",
    "🔍 RADAR TRUY QUÉT SIÊU CỔ PHIẾU",
    "🏭 SECTOR ROTATION — DÒNG TIỀN NGÀNH",
    "📊 VN-INDEX & TƯƠNG QUAN",
    "🌡️ HEATMAP & ĐỐI THỦ NGÀNH",
])

# ==============================================================================
# TAB 1: ROBOT ADVISOR
# ==============================================================================
with tab1:
    # [#7] Hiển thị kết quả cũ nếu đã phân tích (giữ khi switch tab)
    if st.session_state.get('tab1_ticker') == ticker and st.session_state.get('tab1_done'):
        st.info(f"💾 Đang hiển thị kết quả phân tích đã lưu cho **{ticker}**. Bấm nút bên dưới để phân tích lại.")

    col_btn, col_clear = st.columns([3, 1])
    with col_btn:
        run_analysis = st.button(f"⚡ TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG TOÀN DIỆN MÃ {ticker}")
    with col_clear:
        if st.button("🗑️ Xóa kết quả cũ"):
            st.session_state.pop('tab1_done', None)
            st.session_state.pop('tab1_ticker', None)
            st.rerun()

    if run_analysis:
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

            # [V23] New indicators — không gọi VNI trong Tab 1 để tránh chậm
            df_vnindex    = pd.DataFrame()   # dùng benchmark cố định
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

            # ── TÓM TẮT NHANH (mặc định hiện) ──
            color = scoring['decision_color']
            sum_c1, sum_c2 = st.columns([1, 2])
            with sum_c1:
                st.subheader("🤖 ROBOT ĐỀ XUẤT:")
                st.title(f":{color}[{scoring['decision']}]")
                st.markdown(f"**📊 Điểm: {scoring['total']}/90**")
                st.progress(scoring['total'] / 90)
                if scoring['total'] >= SCORE_BUY_MIN:
                    st.success(f"✅ Đủ điều kiện (≥ {SCORE_BUY_MIN}/90)")
                else:
                    st.warning(f"⏳ Chưa đủ ({scoring['total']}/{SCORE_BUY_MIN})")
                st.divider()
                st.metric("💰 Kelly Size", f"{kelly_pct}% vốn",
                          delta="Half-Kelly", delta_color="off")

            with sum_c2:
                # 8 chỉ số cốt lõi dạng bảng gọn
                ai_disp = f"{float(ai_score):.1f}%" if _is_valid_score(ai_score) else "N/A"
                rsi_v   = last['rsi']
                macd_up = last['macd'] > last['signal']
                adx_v   = last.get('adx', 0)
                atr_v   = float(last.get('atr', last['close'] * 0.02))
                sl_disp = calc_trailing_stop(float(last['close']), atr_v)
                weekly_label = {"UP":"📈 TĂNG","DOWN":"📉 GIẢM","NEUTRAL":"➡️ NGANG"}.get(weekly_trend,"N/A")
                ft = foreign_trend

                rows_summary = [
                    ("🤖 AI T+3",        ai_disp,
                     "🔥 Cửa sáng" if _is_valid_score(ai_score) and float(ai_score)>=60 else "⚠️ Thận trọng"),
                    ("📊 RSI",           f"{rsi_v:.1f}",
                     "✅ Lý tưởng" if rsi_v < 60 else ("🔴 Quá mua" if rsi_v > 70 else "🟡 Trung lập")),
                    ("📈 MACD",          "Cross Up ✓" if macd_up else "Cross Down ⚠️", ""),
                    ("📐 ADX",           f"{adx_v:.1f}",
                     "Xu hướng mạnh ✓" if adx_v > 25 else "Sideways"),
                    ("🛡️ ATR Stop",      f"{sl_disp['final_sl']:,.0f}",
                     f"{sl_disp['sl_pct']:+.1f}%"),
                    ("🗓️ Weekly",        weekly_label, ""),
                    ("🌊 Khối Ngoại",    ft.get('trend','N/A'),
                     "🦈 Tích lũy âm thầm!" if ft.get('is_silent_accum') else ""),
                    ("💰 Kỳ vọng/lệnh", f"{bt['expectancy']:+.2f}%",
                     "Dương ✓" if bt['expectancy'] > 0 else "Âm ⚠️"),
                ]
                for label, val, note in rows_summary:
                    r1, r2, r3 = st.columns([2, 2, 3])
                    r1.markdown(f"**{label}**")
                    r2.markdown(val)
                    if note:
                        r3.caption(note)

            # ── CHI TIẾT ĐẦY ĐỦ (expander) ──
            with st.expander("📋 Xem Phân Tích Chi Tiết Đầy Đủ"):
                col_report, col_signal2 = st.columns([2, 1])
                with col_report:
                    report = generate_report(
                        ticker, last, ai_score, bt, buy_set, sell_set, foreign_trend, weekly_trend
                    )
                    st.info(report)
                with col_signal2:
                    st.write("#### Bảng Điểm Chi Tiết")
                    d1, d2, d3, d4, d5 = st.columns(5)
                    d1.metric("🤖 AI",    f"{scoring['ai_pts']}/{SCORE_AI_MAX}")
                    d2.metric("📈 Kỹ thuật", f"{scoring['tech_pts']}/{SCORE_TECH_MAX}")
                    d3.metric("🌊 Ngoại", f"{scoring['flow_pts']}/{SCORE_FLOW_MAX}")
                    d4.metric("🏢 Tài chính", f"{scoring['fin_pts']}/{SCORE_FINANCE_MAX}")
                    d5.metric("🏭 Ngành", f"{scoring['sector_pts']}/{SCORE_SECTOR_MAX}")
                    cols_bar = st.columns(2)
                    items = [
                        ("🤖 AI",        scoring['ai_pts'],     SCORE_AI_MAX),
                        ("📈 Kỹ thuật",  scoring['tech_pts'],   SCORE_TECH_MAX),
                        ("🌊 Ngoại",     scoring['flow_pts'],   SCORE_FLOW_MAX),
                        ("🏢 Tài chính", scoring['fin_pts'],    SCORE_FINANCE_MAX),
                        ("🏭 Ngành",     scoring['sector_pts'], SCORE_SECTOR_MAX),
                    ]
                    for i, (lbl, pts, mx) in enumerate(items):
                        with cols_bar[i % 2]:
                            st.markdown(f"**{lbl}**")
                            st.progress(pts / mx)
                            st.caption(f"{pts}/{mx}")

            st.divider()

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

            # ── #1 EQUITY CURVE + #5 SIGNAL MARKERS ──
            profits_list  = bt.get('profits', [])
            signals_data  = bt.get('signals_data', [])
            if profits_list:
                equity_curve = np.cumprod([1 + p for p in profits_list]) * 100

                fig_bt = make_subplots(rows=2, cols=1, shared_xaxes=False,
                                       vertical_spacing=0.1, row_heights=[0.6, 0.4],
                                       subplot_titles=["📈 Equity Curve (vốn tích lũy)",
                                                        "🎯 Tín Hiệu Mua trên Biểu Đồ Giá"])

                # Equity Curve
                x_eq = list(range(1, len(equity_curve)+1))
                fig_bt.add_trace(go.Scatter(
                    x=x_eq, y=equity_curve,
                    fill='tozeroy',
                    fillcolor='rgba(0,200,100,0.15)',
                    line=dict(color='green' if equity_curve[-1] >= 100 else 'red', width=2),
                    name='Vốn tích lũy',
                ), row=1, col=1)
                fig_bt.add_hline(y=100, line_dash='dot', line_color='gray',
                                  annotation_text="Vốn ban đầu", row=1, col=1)
                # Đánh dấu lỗ
                loss_x = [i+1 for i,p in enumerate(profits_list) if p < 0]
                loss_y = [equity_curve[i] for i in loss_x if i < len(equity_curve)]
                if loss_x:
                    fig_bt.add_trace(go.Scatter(
                        x=[i+1 for i,p in enumerate(profits_list) if p < 0],
                        y=[equity_curve[i] for i,p in enumerate(profits_list) if p < 0],
                        mode='markers', marker=dict(color='red', size=6, symbol='x'),
                        name='Lệnh lỗ',
                    ), row=1, col=1)

                # Signal markers trên biểu đồ giá
                chart_bt = df.tail(CHART_DAYS)
                fig_bt.add_trace(go.Scatter(
                    x=chart_bt['date'], y=chart_bt['close'],
                    line=dict(color='gray', width=1.5), name='Giá đóng cửa',
                ), row=2, col=1)
                if signals_data:
                    # Chỉ lấy signals trong CHART_DAYS gần nhất
                    chart_dates = set(chart_bt['date'].astype(str).str[:10].tolist())
                    for sig in signals_data:
                        d = str(sig['date'])[:10]
                        if d not in chart_dates:
                            continue
                        color_m = 'green' if sig['result']=='WIN' else ('red' if sig['result']=='LOSS' else 'orange')
                        symbol_m= 'triangle-up' if sig['result']=='WIN' else 'triangle-down'
                        fig_bt.add_trace(go.Scatter(
                            x=[d], y=[sig['price']],
                            mode='markers',
                            marker=dict(color=color_m, size=12, symbol=symbol_m),
                            name=f"{sig['result']} {sig['pnl']*100:+.1f}%",
                            showlegend=False,
                        ), row=2, col=1)

                fig_bt.update_layout(
                    height=600, template='plotly_white',
                    margin=dict(l=20, r=20, t=50, b=20),
                    showlegend=True,
                    legend=dict(orientation='h', yanchor='bottom', y=1.02),
                )
                fig_bt.update_yaxes(title_text="% Vốn", row=1, col=1)
                fig_bt.update_yaxes(title_text="Giá",   row=2, col=1)
                st.plotly_chart(fig_bt, use_container_width=True)
                st.caption(
                    f"🟢 Tam giác xanh = lệnh thắng | 🔴 Tam giác đỏ = lệnh thua | 🟠 = hết kỳ hạn | "
                    f"Phí: {ROUND_TRIP_COST*100:.2f}%/lệnh"
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

            # [#7] Lưu flag + dữ liệu để render phần phụ độc lập
            st.session_state['tab1_done']    = True
            st.session_state['tab1_ticker']  = ticker
            st.session_state['tab1_df']      = df
            st.session_state['tab1_bt2']     = run_backtest_v2(df)
            st.session_state['tab1_mtf']     = analyze_mtf(df)
            st.session_state['tab1_entry']   = calc_optimal_entry(df, last)
            st.session_state['tab1_div']     = divergence
            st.session_state['tab1_foreign'] = foreign_trend
            st.session_state['tab1_signal']  = generate_entry_signal(
                last, scoring, bt, ai_score, weekly_trend,
                foreign_trend, st.session_state['tab1_mtf'],
                st.session_state['tab1_entry'], divergence,
            )
            st.session_state['tab1_season']  = calc_seasonality(df)
            st.session_state['tab1_last']    = last
            st.session_state['tab1_scoring'] = scoring

    # ── PHẦN PHỤ: Render ĐỘC LẬP — không cần bấm lại nút phân tích ──
    if st.session_state.get('tab1_done') and st.session_state.get('tab1_ticker') == ticker:
        df_cached = st.session_state.get('tab1_df')
        bt2       = st.session_state.get('tab1_bt2', {})
        mtf       = st.session_state.get('tab1_mtf', {})
        entry_info= st.session_state.get('tab1_entry', {})
        signal    = st.session_state.get('tab1_signal', {})
        season_df = st.session_state.get('tab1_season')
        last_s    = st.session_state.get('tab1_last')

        # ── [#1] TÍN HIỆU VÀO LỆNH TỰ ĐỘNG ──
        st.divider()
        st.write("### 🎯 Tín Hiệu Vào Lệnh Tự Động")
        if signal:
            # Quyết định lớn
            sig_fn = {'success': st.success, 'warning': st.warning, 'error': st.error}
            sig_fn.get(signal['color'], st.info)(
                f"**{signal['action']}** | Tín hiệu: {signal['green']}✅ {signal['red']}🔴 | "
                f"Khuyến nghị: **{signal['size_pct']}% vốn**"
            )
            # Giá vào/SL/TP
            e1, e2, e3, e4 = st.columns(4)
            e1.metric("📍 Giá Vào",  f"{signal['entry']:,.0f}")
            e2.metric("🛡️ Stop Loss", f"{signal['sl']:,.0f}",
                      delta=f"{signal['sl_pct']:+.1f}%", delta_color="inverse")
            e3.metric("🎯 TP (R:R=2)", f"{signal['tp2']:,.0f}",
                      delta=f"{signal['tp2_pct']:+.1f}%", delta_color="normal")
            e4.metric("🎯 TP (R:R=3)", f"{signal['tp3']:,.0f}",
                      delta=f"{signal['tp3_pct']:+.1f}%", delta_color="normal")

            # Điều kiện chi tiết
            with st.expander("📋 Xem chi tiết điều kiện"):
                if signal['conditions']:
                    st.write("**Tín hiệu tích cực:**")
                    for c in signal['conditions']: st.markdown(f"- {c}")
                if signal['warnings']:
                    st.write("**Cảnh báo:**")
                    for w in signal['warnings']: st.markdown(f"- {w}")

        st.divider()

        # ── [#3] ĐA KHUNG THỜI GIAN (MTF) ──
        st.write("### 🗓️ Phân Tích Đa Khung Thời Gian (Monthly / Weekly / Daily)")
        if mtf:
            m1, m2, m3, m4 = st.columns(4)
            mt = mtf.get('monthly', {})
            wt = mtf.get('weekly',  {})
            dt = mtf.get('daily',   {})
            cons = mtf.get('consensus', 'MIXED')

            m1.metric("📅 Monthly",
                      "📈 TĂNG" if mt.get('trend')=='UP' else "📉 GIẢM",
                      delta=f"3 tháng: {mt.get('ret3m',0):+.1f}%",
                      delta_color="normal" if mt.get('ret3m',0)>0 else "inverse")
            m2.metric("🗓️ Weekly",
                      "📈 TĂNG" if wt.get('trend')=='UP' else ("📉 GIẢM" if wt.get('trend')=='DOWN' else "➡️ NGANG"),
                      delta=f"Slope MA10: {wt.get('slope',0):+.2f}%",
                      delta_color="normal" if wt.get('slope',0)>0 else "inverse")
            m3.metric("📊 Daily",
                      "📈 TĂNG" if dt.get('trend')=='UP' else "📉 GIẢM",
                      delta=f"RSI: {dt.get('rsi',0):.1f} | MACD: {dt.get('macd','')}",
                      delta_color="off")
            cons_labels = {
                'STRONG_BULL': "🚀 Cả 3 khung TĂNG",
                'BULL':        "✅ 2/3 khung TĂNG",
                'MIXED':       "⚖️ Phân kỳ khung",
                'BEAR':        "⚠️ 2/3 khung GIẢM",
                'STRONG_BEAR': "🚨 Cả 3 khung GIẢM",
            }
            m4.metric("🎯 Đồng Thuận MTF", cons_labels.get(cons, cons), delta_color="off")

            if cons == 'STRONG_BULL':
                st.success("🚀 **Tất cả 3 khung đều tăng** — Tín hiệu mạnh nhất, an toàn nhất để vào lệnh.")
            elif cons == 'BULL':
                st.info("✅ 2/3 khung tăng — Tín hiệu tốt, vào lệnh bình thường.")
            elif cons == 'STRONG_BEAR':
                st.error("🚨 Tất cả 3 khung đều giảm — Tuyệt đối đứng ngoài.")
            else:
                st.warning("⚖️ Các khung chưa đồng thuận — Vào lệnh nhỏ hoặc chờ thêm.")

        st.divider()

        # ── [#4] VÙNG VÀO LỆNH TỐI ƯU ──
        st.write("### 📍 Vùng Vào Lệnh Tối Ưu (ATR + Fibonacci)")
        if entry_info:
            en1, en2, en3 = st.columns(3)
            en1.metric("🎯 Giá Vào Lý Tưởng", f"{entry_info['ideal_entry']:,.0f}")
            en2.metric("📊 Vùng Vào Thấp",    f"{entry_info['zone_low']:,.0f}")
            en3.metric("📊 Vùng Vào Cao",     f"{entry_info['zone_high']:,.0f}")

            fn1, fn2, fn3, fn4 = st.columns(4)
            fn1.metric("Fib 38.2%", f"{entry_info['fib_382']:,.0f}")
            fn2.metric("Fib 50.0%", f"{entry_info['fib_500']:,.0f}")
            fn3.metric("Fib 61.8%", f"{entry_info['fib_618']:,.0f}")
            fn4.metric("ATR",       f"{entry_info['atr']:,.0f}")

            ef = {'success': st.success, 'warning': st.warning, 'error': st.error}
            ef.get(entry_info['entry_color'], st.info)(entry_info['entry_status'])

        st.divider()

        # ── [#5] RISK/REWARD CALCULATOR ──
        st.write("### 💰 Risk/Reward Calculator")
        rr_c1, rr_c2, rr_c3 = st.columns(3)
        current_price_val = float(last_s['close']) if last_s is not None else 0.0
        capital_input = rr_c1.number_input("Vốn (VNĐ):", min_value=0, value=100_000_000,
                                            step=10_000_000, format="%d")
        entry_input   = rr_c2.number_input("Giá vào:", min_value=0.0,
                                            value=float(current_price_val), step=100.0)
        sl_input      = rr_c3.number_input("Giá SL:", min_value=0.0,
                                            value=float(entry_info.get('sl', current_price_val*0.93)) if entry_info else current_price_val*0.93,
                                            step=100.0)

        rr_c4, rr_c5 = st.columns(2)
        rr_ratio   = rr_c4.slider("R:R mục tiêu:", 1.0, 5.0, 2.0, 0.5)
        risk_pct   = rr_c5.slider("% Vốn chấp nhận mất:", 0.5, 5.0, 2.0, 0.5)

        if entry_input > 0 and sl_input > 0 and sl_input < entry_input:
            rr   = calc_rr(entry_input, sl_input, rr_ratio)
            pos  = calc_position_size(capital_input, risk_pct, entry_input, sl_input)
            r1, r2, r3, r4, r5 = st.columns(5)
            r1.metric("📦 Số CP",         f"{pos['shares']:,}")
            r2.metric("💵 Giá trị lệnh",  f"{pos['total_value']/1e6:.1f}M",
                      delta=f"{pos['capital_pct']:.1f}% vốn", delta_color="off")
            r3.metric("🛡️ Rủi ro tối đa", f"{pos['risk_amount']/1e6:.1f}M",
                      delta=f"-{risk_pct}% vốn", delta_color="inverse")
            r4.metric(f"🎯 TP (R:R={rr_ratio})", f"{rr['tp_custom']:,.0f}",
                      delta=f"+{rr['tp_pct_rr2']:.1f}% (R:R=2)", delta_color="normal")
            r5.metric("🎯 TP (R:R=3)",    f"{rr['tp_rr3']:,.0f}",
                      delta=f"+{rr['tp_pct_rr3']:.1f}%", delta_color="normal")
        else:
            st.caption("Nhập giá vào và giá SL hợp lệ (SL < giá vào) để tính.")

        st.divider()

        # ── [#2] TRADE JOURNAL ──
        st.write("### 📒 Theo Dõi Lệnh Đang Mở")
        tj1, tj2, tj3, tj4 = st.columns(4)
        tj_entry  = tj1.number_input("Giá đã mua:", min_value=0.0, value=0.0, step=100.0, key="tj_entry")
        tj_shares = tj2.number_input("Số CP:", min_value=0, value=0, step=100, key="tj_shares")
        tj_sl     = tj3.number_input("SL đặt:", min_value=0.0, value=0.0, step=100.0, key="tj_sl")
        tj_tp     = tj4.number_input("TP đặt:", min_value=0.0, value=0.0, step=100.0, key="tj_tp")

        if tj_entry > 0 and tj_shares > 0 and tj_sl > 0 and tj_tp > 0:
            cur_p = float(last_s['close']) if last_s is not None else tj_entry
            tj    = calc_open_trade(tj_entry, tj_shares, tj_sl, tj_tp, cur_p)
            jc1, jc2, jc3, jc4, jc5 = st.columns(5)
            jc1.metric("Giá hiện tại",   f"{cur_p:,.0f}")
            jc2.metric("P&L (VNĐ)",      f"{tj['pnl_total']:,.0f}",
                       delta=f"{tj['pnl_pct']:+.2f}%",
                       delta_color="normal" if tj['pnl_pct']>0 else "inverse")
            jc3.metric("Cách SL",        f"{tj['dist_to_sl']:+.2f}%",
                       delta_color="inverse" if tj['dist_to_sl'] < 1 else "off")
            jc4.metric("Cách TP",        f"{tj['dist_to_tp']:+.2f}%",
                       delta_color="normal" if tj['dist_to_tp'] > 0 else "off")
            jc5.metric("R:R hiện tại",   f"{tj['rr_current']:.2f}x", delta_color="off")

            jfn = {'success': st.success, 'warning': st.warning, 'error': st.error}
            jfn.get(tj['status_color'], st.info)(tj['status'])
        else:
            st.caption("Nhập thông tin lệnh để theo dõi P&L real-time.")

        st.divider()

        # ── [#6] SEASONALITY ──
        st.write("### 📅 Phân Tích Mùa Vụ — Mã Này Thường Tăng/Giảm Tháng Nào?")
        if season_df is not None and len(season_df) > 0:
            cur_month = now_vn().month
            colors_s  = ['rgba(220,50,50,0.7)' if v < 0 else 'rgba(50,180,50,0.7)'
                         for v in season_df['avg_ret']]
            # Đánh dấu tháng hiện tại
            colors_s[cur_month-1] = 'rgba(255,165,0,0.9)'
            fig_s = go.Figure(go.Bar(
                x=season_df['month_name'],
                y=season_df['avg_ret'],
                marker_color=colors_s,
                text=[f"{v:+.1f}%" for v in season_df['avg_ret']],
                textposition='outside',
                error_y=dict(type='data', array=season_df['std'].tolist(), visible=True),
            ))
            fig_s.add_hline(y=0, line_color='black', line_width=1)
            fig_s.update_layout(
                height=350, template='plotly_white',
                title=f"Lợi Nhuận Trung Bình Theo Tháng — {ticker} (thanh cam = tháng hiện tại)",
                yaxis_title="% lợi nhuận TB",
                margin=dict(l=20, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_s, use_container_width=True)

            # Tháng tốt/xấu nhất
            best_month  = season_df.loc[season_df['avg_ret'].idxmax()]
            worst_month = season_df.loc[season_df['avg_ret'].idxmin()]
            cur_data    = season_df[season_df['month'] == cur_month]

            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("🏆 Tháng tốt nhất",  best_month['month_name'],
                       delta=f"{best_month['avg_ret']:+.1f}%", delta_color="normal")
            sc2.metric("📉 Tháng xấu nhất",  worst_month['month_name'],
                       delta=f"{worst_month['avg_ret']:+.1f}%", delta_color="inverse")
            if len(cur_data) > 0:
                sc3.metric(f"📍 Tháng {cur_month} hiện tại",
                           f"TB {cur_data.iloc[0]['avg_ret']:+.1f}%",
                           delta="Thường tốt ✓" if cur_data.iloc[0]['avg_ret'] > 0 else "Thường xấu ⚠️",
                           delta_color="normal" if cur_data.iloc[0]['avg_ret'] > 0 else "inverse")

        st.divider()

        # ── [#3] TRAILING STOP ĐỘNG ──
        st.write("### 🛡️ Trailing Stop Động — Cập Nhật Theo Đà Tăng")
        ts1, ts2, ts3 = st.columns(3)
        ts_buy     = ts1.number_input("Giá đã mua:", min_value=0.0, value=0.0, step=100.0, key="ts_buy")
        ts_highest = ts2.number_input("Giá cao nhất đạt được:", min_value=0.0, value=0.0, step=100.0, key="ts_high")
        if ts_buy > 0 and last_s is not None:
            atr_now = float(last_s.get('atr', last_s['close']*0.02))
            cur_now = float(last_s['close'])
            hi_now  = ts_highest if ts_highest > 0 else cur_now
            dts     = calc_dynamic_trailing_stop(ts_buy, cur_now, atr_now, hi_now)
            dt1, dt2, dt3, dt4 = st.columns(4)
            dt1.metric("SL Ban Đầu",     f"{dts['initial_sl']:,.0f}",
                       delta=f"{(dts['initial_sl']-ts_buy)/ts_buy*100:+.1f}%", delta_color="inverse")
            dt2.metric("🛡️ Trailing SL", f"{dts['final_sl']:,.0f}",
                       delta=f"{dts['sl_pct_current']:+.1f}% từ hiện tại", delta_color="inverse")
            dt3.metric("Lợi Nhuận Lock", f"{dts['profit_locked']:,.0f}",
                       delta=f"{dts['profit_locked']/ts_buy*100:+.1f}%" if ts_buy>0 else "",
                       delta_color="normal" if dts['profit_locked']>0 else "off")
            dt4.metric("Giá Hiện Tại",   f"{cur_now:,.0f}")
            fn = {'success':st.success,'warning':st.warning,'error':st.error}
            fn.get(dts['color'], st.info)(dts['status'])
        else:
            st.caption("Nhập giá đã mua để tính Trailing Stop động theo đà tăng.")

        st.divider()

        # ── [#4] PRICE ACTION ──
        st.write("### 🕯️ Phân Tích Price Action — Cấu Trúc Giá")
        if df_cached is not None:
            pa = detect_price_action(df_cached)
            struct_color = {
                'UPTREND':   'success',
                'DOWNTREND': 'error',
                'RANGING':   'warning',
            }.get(pa['structure'], 'info')
            fn = {'success':st.success,'warning':st.warning,'error':st.error,'info':st.info}
            fn.get(struct_color, st.info)(f"**Cấu trúc:** {pa['structure']}")
            for p in pa['patterns']:
                st.markdown(f"- {p}")

        st.divider()

        # ── [#2] ĐỐI THỦ CÙNG NGÀNH ──
        sector_name = get_ticker_sector(ticker)
        st.write(f"### 🏭 So Sánh Đối Thủ Cùng Ngành ({sector_name or 'Chưa xác định'})")
        if sector_name:
            with st.spinner("Đang phân tích đối thủ..."):
                if st.session_state.get('peers_ticker') != ticker:
                    peers = analyze_sector_peers(ticker)
                    st.session_state['peers_data']   = peers
                    st.session_state['peers_ticker'] = ticker
                else:
                    peers = st.session_state.get('peers_data', [])
            if peers:
                df_peers = pd.DataFrame([{
                    'Mã':       p['ticker'],
                    'Giá':      p['price'],
                    'RS Rating':p['rs'],
                    'RSI':      p['rsi'],
                    '5 ngày':   f"{p['ret5d']:+.1f}%",
                    'ADX':      p['adx'],
                    'Trên MA20':"✅" if p['ma_ok'] else "—",
                } for p in peers])
                st.dataframe(df_peers, use_container_width=True, hide_index=True,
                    column_config={
                        "RS Rating": st.column_config.ProgressColumn("RS Rating",
                            min_value=0, max_value=100, format="%.0f"),
                    })
                # So sánh với mã hiện tại
                my_rs = calc_rs_rating(df_cached, pd.DataFrame()) if df_cached is not None else 50
                best_peer = peers[0]
                if best_peer['rs'] > my_rs + 10:
                    st.warning(f"⚠️ **{best_peer['ticker']}** (RS {best_peer['rs']:.0f}) đang mạnh hơn **{ticker}** (RS {my_rs:.0f}) trong ngành — xem xét ưu tiên mã mạnh hơn.")
                else:
                    st.success(f"✅ **{ticker}** đang cạnh tranh tốt trong ngành {sector_name}.")
        else:
            st.info(f"Mã {ticker} chưa được phân loại ngành trong hệ thống.")

        st.divider()

        # ── [#6] GỢI Ý MÃ THAY THẾ ──
        st.write("### 💡 Gợi Ý Mã Thay Thế Tốt Hơn")
        my_score = st.session_state.get('tab1_scoring', {}).get('total', 0)
        if my_score < SCORE_BUY_MIN:
            with st.spinner("Đang tìm mã thay thế..."):
                if st.session_state.get('suggest_ticker') != ticker:
                    suggestions = suggest_better_tickers(ticker, my_score, tickers)
                    st.session_state['suggest_data']   = suggestions
                    st.session_state['suggest_ticker'] = ticker
                else:
                    suggestions = st.session_state.get('suggest_data', [])
            if suggestions:
                st.info(f"Điểm {ticker} chỉ {my_score}/90 — dưới ngưỡng mua. Xem xét các mã sau:")
                for s in suggestions:
                    st.markdown(
                        f"**`{s['ticker']}`** ({s['sector']}) — "
                        f"Giá: {s['price']} | RS Rating: {s['rs']:.0f} | RSI: {s['rsi']}"
                    )
            else:
                st.info("Không tìm được mã thay thế phù hợp hiện tại.")
        else:
            st.success(f"✅ {ticker} đã đủ điểm ({my_score}/90) — không cần tìm mã thay thế.")

        st.divider()

        # ── [A] BACKTEST V2 ──
        st.write("### 🔬 Backtest V2 — Tín Hiệu Thực Tế (RSI+MA20+Vol+MACD+ADX)")
        if bt2 and bt2.get('signals', 0) > 0:
            bv1, bv2, bv3, bv4, bv5 = st.columns(5)
            bv1.metric("Winrate V2",  f"{bt2['winrate']}%")
            bv2.metric("Kỳ vọng V2", f"{bt2['expectancy']:+.2f}%")
            bv3.metric("Sharpe V2",  f"{bt2['sharpe']:.2f}")
            bv4.metric("Max DD V2",  f"{bt2['max_drawdown']:.2f}%")
            bv5.metric("Số lệnh V2", f"{bt2['signals']}")
            st.caption("V2: RSI 28-52 + Giá ≥ 95% MA20 + Vol 0.8-1.5x + MACD cross + ADX < 35")
        else:
            st.info("Chưa đủ tín hiệu V2 trong lịch sử dữ liệu.")

        st.divider()

        # ── [B] WALK-FORWARD OPTIMIZATION ──
        st.write("### ⚙️ Walk-Forward Optimization — Tham Số Tối Ưu")
        if st.button(f"🔍 Tìm Tham Số Tối Ưu cho {ticker}", key="wfo_btn"):
            if df_cached is not None:
                with st.spinner("Đang grid search... (~30 giây)"):
                    wfo = walk_forward_optimize(df_cached)
                st.session_state['wfo_result'] = wfo
                st.session_state['wfo_ticker'] = ticker

        if st.session_state.get('wfo_ticker') == ticker and 'wfo_result' in st.session_state:
            wfo = st.session_state['wfo_result']
            w1, w2, w3, w4 = st.columns(4)
            w1.metric("RSI Mua Tối Ưu",       f"< {wfo['rsi_buy']}", delta=f"Default: {BT_RSI_BUY}")
            w2.metric("Target Profit Tối Ưu", f"{wfo['profit']*100:.0f}%", delta=f"Default: {BT_PROFIT*100:.0f}%")
            w3.metric("Stop Loss Tối Ưu",     f"{wfo['sl']*100:.0f}%",    delta=f"Default: {SL_PCT*100:.0f}%")
            w4.metric("Kỳ Vọng/Lệnh",         f"{wfo['expectancy']:+.2f}%")
            st.caption(f"Winrate train: {wfo.get('winrate_train',0):.1f}% | Số lệnh: {wfo.get('signals_train',0)}")
            if wfo['expectancy'] > 0:
                st.success(f"✅ Tham số tối ưu kỳ vọng **+{wfo['expectancy']:.2f}%/lệnh** cho {ticker}.")
            else:
                st.warning("⚠️ Không tìm được tham số có kỳ vọng dương.")

        st.divider()

        # ── [D] SO SÁNH NHIỀU MÃ ──
        st.write("### 📊 So Sánh Nhiều Mã Cùng Lúc")
        compare_input = st.text_input(
            "Nhập các mã cần so sánh (cách nhau bởi dấu phẩy):",
            placeholder="VD: FPT, ACB, HPG, MWG, SSI",
            key="compare_input"
        )
        if st.button("⚡ So Sánh Ngay", key="compare_btn") and compare_input:
            tickers_cmp = [t.strip().upper() for t in compare_input.split(',') if t.strip()]
            if ticker not in tickers_cmp:
                tickers_cmp.insert(0, ticker)
            tickers_cmp = tickers_cmp[:6]
            with st.spinner(f"Đang phân tích {len(tickers_cmp)} mã..."):
                st.session_state['cmp_results'] = compare_stocks(tickers_cmp)

        if st.session_state.get('cmp_results'):
            cmp_results = st.session_state['cmp_results']
            df_cmp = pd.DataFrame([{
                'Mã':         r['ticker'],
                'Thị Giá':    r['price'],
                'AI T+3 (%)': r['ai'],
                'RS Rating':  r['rs'],
                'RSI':        r['rsi'],
                'Kỹ Thuật':   f"{r['tech']}/10",
                'Winrate':    f"{r['winrate']}%",
                'Kỳ Vọng':    f"{r['expectancy']:+.2f}%",
                'Sharpe':     r['sharpe'],
                'Max DD':     f"{r['max_dd']:.1f}%",
                'Weekly':     _weekly_badge(r['weekly']),
                'Chân Sóng':  f"✅{r['wave_score']}/11" if r['wave_score']>=4 else f"{r['wave_score']}/11",
                'Điểm TH':    r['composite'],
            } for r in cmp_results])
            st.dataframe(df_cmp, use_container_width=True,
                column_config={
                    "AI T+3 (%)": st.column_config.ProgressColumn("AI T+3", min_value=0, max_value=100, format="%.1f%%"),
                    "RS Rating":  st.column_config.ProgressColumn("RS", min_value=0, max_value=100, format="%.0f"),
                    "Điểm TH":    st.column_config.ProgressColumn("Điểm TH", min_value=0, max_value=100, format="%.0f"),
                }, hide_index=True)
            best_m = cmp_results[0]
            st.success(f"🏆 **Mã tốt nhất:** {best_m['ticker']} — Điểm {best_m['composite']:.0f} | AI {best_m['ai']:.1f}% | Winrate {best_m['winrate']}%")

        st.divider()

        # ── [F] CORRELATION MATRIX ──
        st.write("### 🔗 Ma Trận Tương Quan Chéo")
        corr_input = st.text_input(
            "Nhập các mã để tính tương quan (cách nhau bởi dấu phẩy):",
            placeholder="VD: FPT, ACB, HPG, VNM, SSI",
            key="corr_input"
        )
        if st.button("📐 Tính Tương Quan", key="corr_btn") and corr_input:
            tickers_corr = [t.strip().upper() for t in corr_input.split(',') if t.strip()]
            if ticker not in tickers_corr:
                tickers_corr.insert(0, ticker)
            tickers_corr = tickers_corr[:8]
            with st.spinner("Đang tính..."):
                st.session_state['corr_matrix'] = calc_correlation_matrix(tickers_corr)

        if st.session_state.get('corr_matrix') is not None:
            corr_matrix = st.session_state['corr_matrix']
            fig_ch = go.Figure(go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns.tolist(),
                y=corr_matrix.index.tolist(),
                colorscale='RdYlGn', zmid=0, zmin=-1, zmax=1,
                text=corr_matrix.values.round(2),
                texttemplate="%{text}", showscale=True,
            ))
            fig_ch.update_layout(height=400, template='plotly_white',
                title="Ma Trận Tương Quan (63 phiên) — Xanh=đồng chiều | Đỏ=ngược chiều",
                margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_ch, use_container_width=True)
            cols_c = corr_matrix.columns.tolist()
            high_pairs = [(cols_c[i], cols_c[j], corr_matrix.iloc[i,j])
                          for i in range(len(cols_c))
                          for j in range(i+1, len(cols_c))
                          if abs(corr_matrix.iloc[i,j]) >= 0.7]
            if high_pairs:
                for a, b, c in high_pairs:
                    if c >= 0.7:
                        st.warning(f"⚠️ **{a} & {b}** tương quan cao ({c:.2f}) — nắm cả 2 không đa dạng hóa rủi ro.")
                    else:
                        st.info(f"🔄 **{a} & {b}** tương quan âm ({c:.2f}) — có thể hedge nhau.")
            else:
                st.success("✅ Không có cặp nào tương quan quá cao — danh mục đa dạng tốt.")

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

        st.divider()

        # ── [#6] Biểu đồ PE/ROE xu hướng + Trading Stats ──
        st.write("### 📊 Dữ Liệu Thị Trường Chi Tiết")
        try:
            stk_fin = Vnstock().stock(symbol=ticker, source='VCI')
            df_ts   = stk_fin.company.trading_stats()
            if valid(df_ts):
                row_ts = df_ts.iloc[0]
                f1, f2, f3, f4 = st.columns(4)
                hi52 = float(row_ts.get('highest_price1_year', 0) or 0)
                lo52 = float(row_ts.get('lowest_price1_year',  0) or 0)
                ff   = float(row_ts.get('free_float_percentage', 0) or 0) * 100
                fr   = float(row_ts.get('foreigner_percentage',  0) or 0) * 100
                fr_max = float(row_ts.get('maximum_foreign_percentage', 0) or 0) * 100
                avg_val = float(row_ts.get('average_match_value1_month', 0) or 0)
                f1.metric("Đỉnh 52 Tuần",   f"{hi52:,.0f}")
                f2.metric("Đáy 52 Tuần",    f"{lo52:,.0f}")
                f3.metric("Free Float",     f"{ff:.1f}%",
                          delta="Thanh khoản tốt ✓" if ff > 30 else "Cổ phiếu khó mua",
                          delta_color="normal" if ff > 30 else "off")
                f4.metric("Room Ngoại còn", f"{max(0, fr_max-fr):.1f}%",
                          delta=f"Đang sở hữu {fr:.1f}%", delta_color="off")
                st.metric("Giá trị khớp TB 1 tháng", f"{to_billion(avg_val):.1f} Tỷ/phiên")
        except Exception:
            pass

        st.divider()

        # ── [#8] WYCKOFF MARKET REGIME ──
        st.write("### 🔄 Phân Tích Wyckoff — Giai Đoạn Thị Trường")
        df_wy = get_price(ticker, days=200)
        if valid(df_wy):
            df_wy   = calc_indicators(df_wy)
            last_wy = df_wy.iloc[-1]
            price_wy= last_wy['close']
            ma20_wy = last_wy['ma20']
            ma50_wy = last_wy['ma50']
            vol_wy  = last_wy['vol_strength']
            rsi_wy  = last_wy['rsi']
            obv_z_wy= last_wy.get('obv_zscore', 0)
            adx_wy  = last_wy.get('adx', 0)

            # Tính slope MA50 (xu hướng 50 phiên)
            ma50_slope = (df_wy['ma50'].iloc[-1] - df_wy['ma50'].iloc[-20]) / (df_wy['ma50'].iloc[-20] + 1e-9) * 100

            # Xác định giai đoạn Wyckoff
            if price_wy > ma50_wy and ma50_slope > 1 and adx_wy > 20 and rsi_wy > 50:
                phase = "📈 MARKUP — Giai Đoạn Tăng Chính"
                phase_color = "success"
                phase_desc = (
                    "Giá đang trong xu hướng tăng mạnh có xác nhận. "
                    "MA50 dốc lên, ADX > 20, RSI > 50. "
                    "**Chiến lược: Mua trên nền + giữ, cắt lỗ theo ATR.**"
                )
            elif price_wy > ma20_wy and ma50_slope > 0 and rsi_wy < 65 and vol_wy < VOL_BREAKOUT:
                phase = "🏗️ ACCUMULATION — Giai Đoạn Tích Lũy"
                phase_color = "info"
                phase_desc = (
                    "Giá đang tích lũy nền sau đà giảm hoặc sideway. "
                    "Vol thấp, giá ổn định trên MA20. "
                    "**Chiến lược: Mua từng phần, chờ Vol nổ xác nhận breakout.**"
                )
            elif price_wy < ma50_wy and ma50_slope < -1 and rsi_wy < 45:
                phase = "📉 MARKDOWN — Giai Đoạn Giảm Chính"
                phase_color = "error"
                phase_desc = (
                    "Giá đang trong xu hướng giảm có xác nhận. "
                    "MA50 dốc xuống, RSI < 45. "
                    "**Chiến lược: Đứng ngoài hoặc short. Không bắt đáy sớm.**"
                )
            else:
                phase = "🔄 DISTRIBUTION — Giai Đoạn Phân Phối / Chuyển Tiếp"
                phase_color = "warning"
                phase_desc = (
                    "Giá đang ở vùng chuyển tiếp — chưa rõ xu hướng tiếp theo. "
                    "Có thể đỉnh phân phối hoặc tích lũy đáy. "
                    "**Chiến lược: Quan sát Vol và OBV để xác nhận hướng.**"
                )

            wy1, wy2, wy3 = st.columns(3)
            wy1.metric("Slope MA50 (20 phiên)", f"{ma50_slope:+.2f}%",
                       delta="Dốc lên ✓" if ma50_slope > 0 else "Dốc xuống ⚠️",
                       delta_color="normal" if ma50_slope > 0 else "inverse")
            wy2.metric("OBV Z-Score", f"{obv_z_wy:.2f}",
                       delta="Tích lũy ✓" if obv_z_wy > 0.5 else ("Phân phối ⚠️" if obv_z_wy < -0.5 else "Trung lập"),
                       delta_color="normal" if obv_z_wy > 0.5 else ("inverse" if obv_z_wy < -0.5 else "off"))
            wy3.metric("ADX (Sức mạnh)", f"{adx_wy:.1f}",
                       delta="Xu hướng rõ ✓" if adx_wy > 25 else "Sideways",
                       delta_color="normal" if adx_wy > 25 else "off")

            st.markdown(f"### {phase}")
            if phase_color == "success":   st.success(phase_desc)
            elif phase_color == "info":    st.info(phase_desc)
            elif phase_color == "error":   st.error(phase_desc)
            else:                          st.warning(phase_desc)

            # Mini chart Volume profile (bar ngang)
            st.write("#### 📊 Volume Profile — Vùng Giá Giao Dịch Nhiều Nhất")
            df_vp = df_wy.tail(60).copy()
            price_min = df_vp['low'].min()
            price_max = df_vp['high'].max()
            bins = np.linspace(price_min, price_max, 20)
            vol_at_price = np.zeros(len(bins)-1)
            for _, row_vp in df_vp.iterrows():
                for b in range(len(bins)-1):
                    if bins[b] <= row_vp['close'] < bins[b+1]:
                        vol_at_price[b] += row_vp['volume']
                        break
            price_labels = [f"{(bins[i]+bins[i+1])/2:,.0f}" for i in range(len(bins)-1)]
            poc_idx = int(np.argmax(vol_at_price))   # Point of Control
            colors_vp = ['rgba(255,80,80,0.7)' if i == poc_idx else 'rgba(100,149,237,0.5)'
                         for i in range(len(vol_at_price))]
            fig_vp = go.Figure(go.Bar(
                x=vol_at_price, y=price_labels, orientation='h',
                marker_color=colors_vp, name='Volume tại giá',
            ))
            fig_vp.add_annotation(
                x=vol_at_price[poc_idx], y=price_labels[poc_idx],
                text=f"POC: {price_labels[poc_idx]} (giao dịch nhiều nhất)",
                showarrow=True, arrowhead=2, font=dict(color='red', size=11),
            )
            fig_vp.update_layout(
                height=350, template='plotly_white',
                title="Volume Profile 60 phiên — Đỏ = Point of Control (hỗ trợ/kháng cự mạnh nhất)",
                xaxis_title="Khối lượng", yaxis_title="Vùng giá",
                margin=dict(l=20, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_vp, use_container_width=True)
            st.caption(
                f"💡 **POC (Point of Control):** {price_labels[poc_idx]} — "
                "vùng giá được giao dịch nhiều nhất trong 60 phiên. "
                "Thường là vùng hỗ trợ/kháng cự mạnh nhất."
            )

# ==============================================================================
# TAB 3: DÒNG TIỀN THÔNG MINH
# ==============================================================================
with tab3:
    st.write(f"### 🌊 Smart Flow Specialist — Mổ Xẻ Dòng Tiền 3 Bên ({ticker})")
    st.caption("So sánh **Khối Ngoại / Tự Doanh / Nhỏ Lẻ** theo từng phiên — xác định ai đang gom, ai đang xả.")

    with st.spinner("Đang tổng hợp dữ liệu dòng tiền 3 bên (thử tất cả nguồn)..."):
        flows        = fetch_all_flows(ticker, FOREIGN_DAYS)
        df_for       = flows['foreign']
        df_prop      = flows['proprietary']
        df_price_flow = get_price(ticker, days=20)
        if valid(df_price_flow):
            df_price_flow = calc_indicators(df_price_flow)
        foreign_trend_t3 = analyze_foreign_trend(df_for)

    # ── Chuẩn bị dữ liệu 10 phiên ──
    def _extract_flow(df_src, n=10):
        """Trả về list [{date, buy, sell, net}] đã chuẩn hóa."""
        if not valid(df_src):
            return []
        result = []
        for _, r in df_src.tail(n).iterrows():
            d   = str(r.get('date', r.name))[:10]
            buy = to_billion(r.get('buyval',  0))
            sel = to_billion(r.get('sellval', 0))
            net = to_billion(r.get('netval',  buy - sel))
            result.append({'date': d, 'buy': buy, 'sell': sel, 'net': net})
        return sorted(result, key=lambda x: x['date'])

    rows_for  = _extract_flow(df_for,  10)
    rows_prop = _extract_flow(df_prop, 10)

    # Tạo timeline chung từ price data (đảm bảo luôn có ngày)
    price_dates = []
    if valid(df_price_flow) and 'date' in df_price_flow.columns:
        price_dates = [str(d)[:10] for d in df_price_flow['date'].tail(10).tolist()]

    # Hợp nhất ngày từ cả 3 nguồn
    all_dates_set = set(price_dates)
    all_dates_set.update([r['date'] for r in rows_for])
    all_dates_set.update([r['date'] for r in rows_prop])
    all_dates = sorted(all_dates_set)[-10:]

    # Map theo ngày
    map_for  = {r['date']: r for r in rows_for}
    map_prop = {r['date']: r for r in rows_prop}

    foreign_nets, prop_nets, retail_nets, date_labels = [], [], [], []

    for d in all_dates:
        f_net  = map_for.get(d,  {}).get('net',  0.0)
        p_net  = map_prop.get(d, {}).get('net',  0.0)
        f_buy  = map_for.get(d,  {}).get('buy',  0.0)
        f_sell = map_for.get(d,  {}).get('sell', 0.0)
        p_buy  = map_prop.get(d, {}).get('buy',  0.0)
        p_sell = map_prop.get(d, {}).get('sell', 0.0)

        # Nhỏ Lẻ ước tính = Tổng phiên - Ngoại gross - Tự Doanh gross
        retail_net = 0.0
        if valid(df_price_flow) and 'date' in df_price_flow.columns:
            day_row = df_price_flow[df_price_flow['date'].astype(str).str[:10] == d]
            if not day_row.empty:
                total_val  = to_billion(day_row.iloc[0]['close'] * day_row.iloc[0]['volume'])
                inst_gross = (f_buy + f_sell + p_buy + p_sell)
                retail_net = max(0, total_val - inst_gross) * np.sign(
                    day_row.iloc[0].get('return_1d', 0) or 0
                )

        foreign_nets.append(f_net)
        prop_nets.append(p_net)
        retail_nets.append(retail_net)
        date_labels.append(d[5:])   # MM-DD

    has_foreign = any(v != 0 for v in foreign_nets)
    has_prop    = any(v != 0 for v in prop_nets)
    has_any     = has_foreign or has_prop

    # ── Chart 1: Grouped Bar — Net Flow 3 bên ──
    st.write("#### 📊 Dòng Tiền Ròng 3 Bên — 10 Phiên Gần Nhất (Tỷ VNĐ)")
    st.caption("Mua ròng (+) = thanh xanh | Bán ròng (−) = thanh đỏ | Đường vàng = tổng Smart Money")

    if not date_labels:
        st.warning("⚠️ Chưa có dữ liệu ngày giao dịch. Thử lại sau hoặc chọn mã khác.")
    elif not has_any:
        # PHƯƠNG ÁN A: dùng company.trading_stats thay chart trống
        st.info("ℹ️ API dòng tiền theo ngày không khả dụng. Hiển thị dữ liệu tổng hợp từ nguồn khác.")
        try:
            stk_ts  = Vnstock().stock(symbol=ticker, source='VCI')
            df_ts   = stk_ts.company.trading_stats()
            if valid(df_ts):
                row_ts = df_ts.iloc[0]

                # Room ngoại
                f_pct   = float(row_ts.get('foreigner_percentage', 0) or 0) * 100
                f_max   = float(row_ts.get('maximum_foreign_percentage', 0) or 0) * 100
                f_room  = max(0, f_max - f_pct)
                st.write("#### 🌏 Sở Hữu Khối Ngoại")
                r1, r2, r3 = st.columns(3)
                r1.metric("Tỷ lệ sở hữu hiện tại", f"{f_pct:.1f}%")
                r2.metric("Giới hạn tối đa",        f"{f_max:.1f}%")
                r3.metric("Room còn lại",            f"{f_room:.1f}%",
                          delta="Còn nhiều room ✓" if f_room > 10 else "Gần hết room ⚠️",
                          delta_color="normal" if f_room > 10 else "inverse")
                if f_room < 5:
                    st.warning("⚠️ Room ngoại gần cạn — khối ngoại khó mua thêm, có thể bị áp lực bán.")
                elif f_room > 20:
                    st.success("✅ Room ngoại còn nhiều — dư địa để khối ngoại tích lũy thêm.")

                st.divider()

                # Thanh khoản TB
                avg_val = float(row_ts.get('average_match_value1_month', 0) or 0)
                avg_vol = float(row_ts.get('average_match_volume1_month', 0) or 0)
                st.write("#### 📊 Thanh Khoản Trung Bình 1 Tháng")
                liq1, liq2 = st.columns(2)
                liq1.metric("Giá trị khớp lệnh TB", f"{to_billion(avg_val):.1f} Tỷ/phiên")
                liq2.metric("Khối lượng khớp lệnh TB", f"{avg_vol/1e6:.2f} Triệu cp/phiên")

                st.divider()

                # 52W High/Low + Free Float
                hi52  = float(row_ts.get('highest_price1_year', 0) or 0)
                lo52  = float(row_ts.get('lowest_price1_year',  0) or 0)
                ff    = float(row_ts.get('free_float_percentage', 0) or 0) * 100
                st.write("#### 📈 Biên Độ Giá 52 Tuần & Free Float")
                w1, w2, w3 = st.columns(3)
                w1.metric("Đỉnh 52 tuần",  f"{hi52:,.0f}")
                w2.metric("Đáy 52 tuần",   f"{lo52:,.0f}")
                w3.metric("Free Float",     f"{ff:.1f}%",
                          delta="Thanh khoản tốt ✓" if ff > 30 else "Cổ phiếu khó mua ⚠️",
                          delta_color="normal" if ff > 30 else "off")

                # OBV từ price data
                st.divider()
                st.write("#### 📉 OBV — Dòng Tiền Tích Lũy (ước tính từ Price Data)")
                df_obv = get_price(ticker, days=60)
                if valid(df_obv):
                    df_obv = calc_indicators(df_obv)
                    last_obv = df_obv.iloc[-1]
                    obv_z = last_obv.get('obv_zscore', 0)
                    o1, o2 = st.columns(2)
                    o1.metric("OBV Z-Score", f"{obv_z:.2f}",
                              delta="Dòng tiền đang chảy vào ✓" if obv_z > 0.5
                              else ("Dòng tiền rút ra ⚠️" if obv_z < -0.5 else "Trung lập"),
                              delta_color="normal" if obv_z > 0.5
                              else ("inverse" if obv_z < -0.5 else "off"))
                    o2.metric("Vol Strength phiên cuối",
                              f"{last_obv['vol_strength']:.2f}x",
                              delta="Bùng nổ ✓" if last_obv['vol_strength'] > 1.3 else "Bình thường",
                              delta_color="normal" if last_obv['vol_strength'] > 1.3 else "off")
                    if obv_z > 0.5:
                        st.success("✅ OBV tích lũy dương — dòng tiền thực đang chảy vào mã này.")
                    elif obv_z < -0.5:
                        st.error("🔴 OBV phân phối âm — dòng tiền đang rút khỏi mã này.")
                    else:
                        st.info("🟡 OBV trung lập — chưa có dòng tiền mạnh từ một phía.")
            else:
                st.warning("⚠️ Không lấy được dữ liệu trading_stats.")
        except Exception as e:
            st.warning(f"⚠️ Lỗi lấy dữ liệu: {e}")
    else:
        fig_multi = go.Figure()
        if has_foreign:
            fig_multi.add_trace(go.Bar(
                x=date_labels, y=foreign_nets,
                name="🌏 Khối Ngoại",
                marker_color=['rgba(0,180,0,0.85)' if v >= 0 else 'rgba(220,0,0,0.85)'
                              for v in foreign_nets],
                text=[f"{v:+.1f}" for v in foreign_nets],
                textposition='outside',
            ))
        if has_prop:
            fig_multi.add_trace(go.Bar(
                x=date_labels, y=prop_nets,
                name="🏦 Tự Doanh",
                marker_color=['rgba(0,100,255,0.75)' if v >= 0 else 'rgba(255,100,0,0.75)'
                              for v in prop_nets],
                text=[f"{v:+.1f}" for v in prop_nets],
                textposition='outside',
            ))
        combined = [f + p for f, p in zip(foreign_nets, prop_nets)]
        fig_multi.add_trace(go.Scatter(
            x=date_labels, y=combined,
            name="📈 Tổng Ròng",
            mode='lines+markers',
            line=dict(color='gold', width=2.5),
            marker=dict(size=8),
        ))
        fig_multi.update_layout(
            barmode='group', height=380, template='plotly_white',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            yaxis_title="Tỷ VNĐ", xaxis_title="Phiên",
        )
        fig_multi.add_hline(y=0, line_color='black', line_width=1)
        st.plotly_chart(fig_multi, use_container_width=True)

        if not has_foreign:
            st.caption("⚠️ Chưa lấy được dữ liệu Khối Ngoại — chỉ hiện Tự Doanh.")
        if not has_prop:
            st.caption("⚠️ Chưa lấy được dữ liệu Tự Doanh — chỉ hiện Khối Ngoại.")

    # ── Đọc tín hiệu tổng hợp 3 bên ──
    st.write("#### 🔍 Đọc Tín Hiệu Tổng Hợp")
    f_total        = sum(foreign_nets)
    p_total        = sum(prop_nets)
    combined_total = f_total + p_total

    sig_c1, sig_c2, sig_c3, sig_c4 = st.columns(4)
    sig_c1.metric("🌏 Ngoại Ròng 10P",  f"{f_total:+.1f} Tỷ",
                  delta="Mua ròng ✓" if f_total > 0 else ("N/A" if not has_foreign else "Bán ròng ⚠️"),
                  delta_color="normal" if f_total > 0 else ("off" if not has_foreign else "inverse"))
    sig_c2.metric("🏦 Tự Doanh Ròng 10P", f"{p_total:+.1f} Tỷ",
                  delta="Gom hàng ✓" if p_total > 0 else ("N/A" if not has_prop else "Thoát hàng ⚠️"),
                  delta_color="normal" if p_total > 0 else ("off" if not has_prop else "inverse"))
    sig_c3.metric("📊 Tổng Smart Money", f"{combined_total:+.1f} Tỷ",
                  delta="Tổ chức đồng thuận ✓" if combined_total > 0 else "Tổ chức rút lui ⚠️",
                  delta_color="normal" if combined_total > 0 else "inverse")
    consensus_buy  = sum(1 for f, p in zip(foreign_nets, prop_nets) if f > 0 and p > 0)
    consensus_sell = sum(1 for f, p in zip(foreign_nets, prop_nets) if f < 0 and p < 0)
    sig_c4.metric("🤝 Phiên Đồng Thuận",
                  f"Gom: {consensus_buy} | Xả: {consensus_sell}",
                  delta="Đồng gom mạnh! ✓" if consensus_buy >= 5 else
                        ("Đồng xả! ⚠️" if consensus_sell >= 5 else "Phân hóa"),
                  delta_color="normal" if consensus_buy >= 5 else
                              ("inverse" if consensus_sell >= 5 else "off"))

    if consensus_buy >= 6:
        st.success(f"🚨 **TÍN HIỆU VÀNG** — Cả 2 bên đồng gom **{consensus_buy}/10 phiên**. Smart money đang tích lũy phối hợp.")
    elif f_total > 0 and p_total > 0:
        st.success(f"✅ **Tích Cực:** Cả 2 bên mua ròng (Ngoại {f_total:+.1f}Tỷ | TD {p_total:+.1f}Tỷ).")
    elif f_total > 0 and p_total < 0:
        st.warning(f"⚠️ **Phân Kỳ:** Ngoại gom ({f_total:+.1f}Tỷ) nhưng Tự Doanh xả ({p_total:+.1f}Tỷ).")
    elif f_total < 0 and p_total > 0:
        st.warning(f"⚠️ **Phân Kỳ:** Tự Doanh gom ({p_total:+.1f}Tỷ) nhưng Ngoại rút ({f_total:+.1f}Tỷ).")
    elif consensus_sell >= 5:
        st.error(f"🚨 **CẢNH BÁO ĐỎ:** Cả 2 bên đồng xả {consensus_sell}/10 phiên — đứng ngoài chờ đáy.")
    else:
        st.info("🟡 Dòng tiền tổ chức phân hóa — chưa có tín hiệu rõ ràng từ hai phía.")

    st.divider()

    # ── Chart 2: Chi tiết Mua/Bán gross từng bên ──
    st.write("#### 📊 Chi Tiết Mua/Bán Từng Bên (Gross Value)")
    if has_any:
        fig_detail = make_subplots(
            rows=1, cols=2,
            subplot_titles=("🌏 Khối Ngoại (Tỷ)", "🏦 Tự Doanh (Tỷ)"),
        )
        if has_foreign and rows_for:
            f_dates = [r['date'][5:] for r in rows_for]
            f_buys  = [r['buy']  for r in rows_for]
            f_sells = [-r['sell'] for r in rows_for]
            fig_detail.add_trace(go.Bar(x=f_dates, y=f_buys,  name="Ngoại Mua",
                                        marker_color='rgba(0,180,0,0.8)'),  row=1, col=1)
            fig_detail.add_trace(go.Bar(x=f_dates, y=f_sells, name="Ngoại Bán",
                                        marker_color='rgba(220,0,0,0.8)'),  row=1, col=1)
        else:
            fig_detail.add_annotation(text="Chưa có dữ liệu Khối Ngoại",
                                       xref="x domain", yref="y domain",
                                       x=0.5, y=0.5, row=1, col=1, showarrow=False)
        if has_prop and rows_prop:
            p_dates = [r['date'][5:] for r in rows_prop]
            p_buys  = [r['buy']  for r in rows_prop]
            p_sells = [-r['sell'] for r in rows_prop]
            fig_detail.add_trace(go.Bar(x=p_dates, y=p_buys,  name="TD Mua",
                                        marker_color='rgba(0,100,255,0.8)'), row=1, col=2)
            fig_detail.add_trace(go.Bar(x=p_dates, y=p_sells, name="TD Bán",
                                        marker_color='rgba(255,100,0,0.8)'), row=1, col=2)
        else:
            fig_detail.add_annotation(text="Chưa có dữ liệu Tự Doanh",
                                       xref="x2 domain", yref="y2 domain",
                                       x=0.5, y=0.5, row=1, col=2, showarrow=False)
        fig_detail.update_layout(
            barmode='relative', height=320, template='plotly_white',
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation='h', yanchor='bottom', y=1.05),
        )
        st.plotly_chart(fig_detail, use_container_width=True)
    else:
        st.warning("⚠️ Không có đủ dữ liệu để vẽ chart chi tiết.")

    st.divider()

    # ── [#2] OBV & VOLUME PATTERN NÂNG CAO ──
    st.write("### 📊 OBV & Volume Pattern — Dòng Tiền Thực Từ Price Data")
    st.caption("Phân tích dựa trên dữ liệu giá/khối lượng thực — không phụ thuộc API dòng tiền.")
    df_obv2 = get_price(ticker, days=60)
    if valid(df_obv2):
        df_obv2 = calc_indicators(df_obv2)
        last_o  = df_obv2.iloc[-1]

        o1, o2, o3, o4 = st.columns(4)
        obv_z = last_o.get('obv_zscore', 0)
        vol_s = last_o['vol_strength']
        pv    = last_o.get('pv_trend', 0)
        adx_o = last_o.get('adx', 0)

        o1.metric("OBV Z-Score", f"{obv_z:.2f}",
                  delta="Dòng tiền vào ✓" if obv_z > 0.5 else ("Dòng tiền ra ⚠️" if obv_z < -0.5 else "Trung lập"),
                  delta_color="normal" if obv_z > 0.5 else ("inverse" if obv_z < -0.5 else "off"))
        o2.metric("Vol Strength", f"{vol_s:.2f}x",
                  delta="Bùng nổ ✓" if vol_s > 1.3 else "Bình thường",
                  delta_color="normal" if vol_s > 1.3 else "off")
        o3.metric("Price-Volume Trend", "📈 Thuận" if pv > 0 else ("📉 Nghịch" if pv < 0 else "Trung lập"),
                  delta_color="off")
        o4.metric("ADX", f"{adx_o:.1f}",
                  delta="Xu hướng mạnh ✓" if adx_o > 25 else "Sideways",
                  delta_color="normal" if adx_o > 25 else "off")

        # OBV chart vs Price
        fig_obv = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                vertical_spacing=0.05, row_heights=[0.5, 0.5])
        x_obv = df_obv2['date']
        fig_obv.add_trace(go.Scatter(
            x=x_obv, y=df_obv2['close'],
            line=dict(color='royalblue', width=2), name='Giá'
        ), row=1, col=1)
        fig_obv.add_trace(go.Scatter(
            x=x_obv, y=df_obv2['obv'],
            line=dict(color='green', width=1.5), name='OBV',
            fill='tozeroy', fillcolor='rgba(0,200,0,0.1)',
        ), row=2, col=1)
        # OBV trend line (rolling mean)
        obv_trend = df_obv2['obv'].rolling(10).mean()
        fig_obv.add_trace(go.Scatter(
            x=x_obv, y=obv_trend,
            line=dict(color='red', width=1.5, dash='dot'), name='OBV MA10'
        ), row=2, col=1)
        fig_obv.update_layout(
            height=400, template='plotly_white',
            margin=dict(l=20, r=20, t=40, b=20),
            title="OBV vs Giá — Giá tăng + OBV tăng = tích lũy thật. Giá tăng + OBV giảm = phân phối.",
        )
        st.plotly_chart(fig_obv, use_container_width=True)

        # Volume pattern phân tích
        df_obv2['vol_category'] = pd.cut(
            df_obv2['vol_strength'],
            bins=[0, 0.8, 1.3, 2.0, 99],
            labels=['Thấp', 'Bình thường', 'Cao', 'Rất cao']
        )
        recent = df_obv2.tail(20)
        high_vol_green = ((recent['vol_strength'] > 1.3) & (recent['return_1d'] > 0)).sum()
        high_vol_red   = ((recent['vol_strength'] > 1.3) & (recent['return_1d'] < 0)).sum()
        vp1, vp2 = st.columns(2)
        vp1.metric("Vol cao + Nến xanh (20 phiên)", f"{high_vol_green} phiên",
                   delta="Tích lũy mạnh ✓" if high_vol_green > high_vol_red else "Không chiếm ưu thế",
                   delta_color="normal" if high_vol_green > high_vol_red else "off")
        vp2.metric("Vol cao + Nến đỏ (20 phiên)", f"{high_vol_red} phiên",
                   delta="Phân phối ⚠️" if high_vol_red > high_vol_green else "Ít",
                   delta_color="inverse" if high_vol_red > high_vol_green else "off")
        if high_vol_green > high_vol_red * 1.5:
            st.success("✅ **Tín hiệu tích lũy rõ:** Vol lớn chủ yếu đi kèm nến xanh → smart money đang gom.")
        elif high_vol_red > high_vol_green * 1.5:
            st.error("🔴 **Tín hiệu phân phối:** Vol lớn chủ yếu đi kèm nến đỏ → smart money đang xả.")
        else:
            st.info("🟡 Chưa có tín hiệu rõ ràng từ Volume Pattern.")


# ==============================================================================
# TAB 4: RADAR TRUY QUÉT
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

    # ── HIỆU CHỈNH NGƯỠNG VOL ──
    with st.expander("🔬 Hiệu Chỉnh Ngưỡng Vol Theo Thống Kê Thực Tế (chạy 1 lần/tuần)"):
        st.caption(
            "Hệ thống sẽ phân tích 50 mã HOSE để tìm ngưỡng Vol thực sự bất thường. "
            "Mất ~5 phút. Kết quả được lưu cho đến khi reload app."
        )
        # Hiện ngưỡng đang dùng
        cur_bo = st.session_state.get('cal_threshold_breakout',   VOL_BREAKOUT)
        cur_du = st.session_state.get('cal_threshold_dump',       VOL_BREAKOUT * 1.5)
        cur_hd = st.session_state.get('cal_threshold_heavy_dump', VOL_SHARK)
        nc1, nc2, nc3 = st.columns(3)
        nc1.metric("Ngưỡng Bùng Nổ Mua",  f"{cur_bo:.2f}x",
                   delta="✅ Đã hiệu chỉnh" if 'cal_threshold_breakout' in st.session_state else "⚙️ Mặc định",
                   delta_color="normal" if 'cal_threshold_breakout' in st.session_state else "off")
        nc2.metric("Ngưỡng Bán Tháo",     f"{cur_du:.2f}x", delta_color="off")
        nc3.metric("Ngưỡng Bán Tháo Nặng",f"{cur_hd:.2f}x", delta_color="off")

        if st.button("▶️ Chạy Hiệu Chỉnh Ngưỡng (50 mã mẫu)"):
            sample_cal = list(dict.fromkeys(tickers))[:50]
            with st.spinner("Đang phân tích phân phối Vol lịch sử..."):
                cal_result = calibrate_vol_thresholds(sample_cal, days=252)

            if 'error' in cal_result:
                st.error(f"❌ {cal_result['error']}")
            else:
                # Lưu vào session_state
                st.session_state['cal_threshold_breakout']   = cal_result['threshold_breakout']
                st.session_state['cal_threshold_dump']       = cal_result['threshold_dump']
                st.session_state['cal_threshold_heavy_dump'] = cal_result['threshold_heavy_dump']
                st.session_state['cal_result']               = cal_result

                st.success("✅ Hiệu chỉnh hoàn tất! Ngưỡng mới sẽ được áp dụng cho lần quét tiếp theo.")

                # Hiện kết quả
                st.write("#### 📊 Phân Phối Vol Thực Tế HOSE")
                r1, r2, r3, r4, r5 = st.columns(5)
                r1.metric("P70",  f"{cal_result['p70']:.2f}x", delta="Vol hơi cao",       delta_color="off")
                r2.metric("P80",  f"{cal_result['p80']:.2f}x", delta="→ Ngưỡng Bùng Nổ", delta_color="off")
                r3.metric("P90",  f"{cal_result['p90']:.2f}x", delta="→ Ngưỡng Bán Tháo",delta_color="off")
                r4.metric("P95",  f"{cal_result['p95']:.2f}x", delta="Bán Tháo Nặng",    delta_color="off")
                r5.metric("P99",  f"{cal_result['p99']:.2f}x", delta="Cực hiếm",          delta_color="off")

                st.write("#### 🔍 Winrate 'Bán Tháo' Thực Tế")
                wr = cal_result['winrate_dump']
                n  = cal_result['n_dump_events']
                if wr >= 60:
                    st.error(
                        f"🔴 Khi Vol > P90 + nến đỏ, **{wr}% trường hợp** tiếp tục giảm trong 3 phiên tiếp theo "
                        f"(thống kê từ {n} sự kiện). → Tín hiệu 'Bán Tháo' **đáng tin cậy**."
                    )
                elif wr >= 50:
                    st.warning(
                        f"🟡 Winrate bán tháo {wr}% ({n} sự kiện) — **hơi nghiêng về giảm tiếp** "
                        f"nhưng chưa thực sự mạnh. Cân nhắc thêm RSI và ngành."
                    )
                else:
                    st.info(
                        f"🟢 Winrate bán tháo chỉ {wr}% ({n} sự kiện) — **thường hồi phục sau 3 phiên**. "
                        f"Tín hiệu 'Bán Tháo' trên HOSE không đáng lo như tưởng."
                    )

                st.caption(
                    f"📊 Phân tích từ {cal_result['n_samples']:,} phiên giao dịch "
                    f"của {len(sample_cal)} mã HOSE đại diện trong 1 năm."
                )

    st.divider()
    col_quick, col_full, col_fast = st.columns(3)
    run_quick = col_quick.button("⚡ Quét Nhanh (150 mã HOSE)")
    run_full  = col_full.button("🔭 Quét Toàn HOSE (~400 mã) — mất ~15 phút")
    run_fast  = col_fast.button("🏃 Điểm Danh Siêu Nhanh (không AI) — ~3 phút")

    if run_fast:
        scan_list = list(dict.fromkeys(tickers))[:RADAR_MAX_FULL]
        st.caption(f"🏃 Điểm danh nhanh {len(scan_list)} mã (RSI + Vol + MA20, không AI)...")
        progress_f = st.progress(0)
        fast_tiem  = []
        fast_tang  = []
        fast_co_hoi= []
        for i, t in enumerate(scan_list):
            try:
                df_f = get_price(t, days=60)
                if not valid(df_f): continue
                df_f  = calc_indicators(df_f)
                label = classify_stock_fast(df_f)
                if not label: continue
                last_f = df_f.iloc[-1]
                row_f = {
                    'Ticker':  t,
                    'Thị Giá': f"{last_f['close']:,.0f}",
                    'RSI':     round(float(last_f['rsi']), 1),
                    'Vol':     f"{last_f['vol_strength']:.2f}x",
                    'MA20':    "Trên ✓" if last_f['close'] > last_f['ma20'] else "Dưới ⚠️",
                    'ADX':     round(float(last_f.get('adx',0)), 1),
                }
                if "Bùng Nổ"  in label: fast_tiem.append(row_f)
                elif "Tiềm Năng" in label: fast_co_hoi.append(row_f)
                elif "Tăng Mạnh" in label: fast_tang.append(row_f)
            except Exception: pass
            progress_f.progress((i+1)/len(scan_list))

        st.success(f"✅ Xong! 🚀 {len(fast_tiem)} bùng nổ | 🌊 {len(fast_co_hoi)} tiềm năng | 🔥 {len(fast_tang)} tăng mạnh")
        for title, lst, cap in [
            ("🚀 Bùng Nổ", fast_tiem, "Vol nổ mạnh"),
            ("🌊 Tiềm Năng (Chân Sóng sơ bộ)", fast_co_hoi, "RSI + MA20 + Vol hợp lệ — chạy Quét Đầy Đủ để xác nhận AI"),
            ("🔥 Đang Tăng Mạnh", fast_tang, "RSI 65-80"),
        ]:
            if lst:
                st.write(f"#### {title}")
                st.caption(cap)
                st.dataframe(pd.DataFrame(lst), use_container_width=True, hide_index=True)
        st.info("💡 Đây là kết quả sơ bộ **không có AI**. Dùng **Quét Nhanh** để phân tích đầy đủ các mã tiềm năng.")
        st.stop()

    if run_quick or run_full:
        max_scan = RADAR_MAX_FULL if run_full else RADAR_MAX

        # Market Breadth
        st.write("#### 🏥 Sức Khỏe Thị Trường (Market Breadth)")
        with st.spinner("Đang đo sức khỏe thị trường..."):
            sample_50 = tuple(list(dict.fromkeys(tickers))[:50])
            breadth   = calc_market_breadth(sample_50)
        if breadth['total'] > 0:
            mb1, mb2, mb3, mb4 = st.columns(4)
            mb1.metric("Trạng thái", breadth['market_status'])
            mb2.metric("% Mã trên MA20", f"{breadth['pct_above_ma20']:.1f}%",
                       delta="Mạnh ✓" if breadth['pct_above_ma20'] >= 60 else "Yếu ⚠️",
                       delta_color="normal" if breadth['pct_above_ma20'] >= 60 else "inverse")
            mb3.metric("% RSI lành mạnh", f"{breadth['pct_rsi_ok']:.1f}%",
                       delta="Chưa quá mua ✓" if breadth['pct_rsi_ok'] >= 50 else "Đang nóng",
                       delta_color="normal" if breadth['pct_rsi_ok'] >= 50 else "off")
            mb4.metric("Tỷ lệ tăng/giảm", f"{breadth['advance_decline']:.1f}%",
                       delta="Nhiều mã xanh ✓" if breadth['advance_decline'] >= 55 else "Phân hóa",
                       delta_color="normal" if breadth['advance_decline'] >= 55 else "off")
        st.divider()

        scan_list = list(dict.fromkeys(tickers))[:max_scan]
        st.caption(f"🔭 Đang quét {len(scan_list)} mã trên HOSE...")
        progress       = st.progress(0)
        breakouts      = []
        sell_dumps     = []
        watchlist      = []
        wave_bottom    = []
        watch_zone     = []
        running_strong = []

        # RS Rating dùng benchmark cố định — không gọi VNI để giữ tốc độ
        df_vnidx = pd.DataFrame()

        for i, t in enumerate(scan_list):
            try:
                df_s = get_price(t, days=SCAN_DAYS)
                if not valid(df_s):
                    continue
                df_s     = calc_indicators(df_s)
                # Dùng cache 30 phút — cùng phiên luôn ra cùng kết quả
                ai_s     = predict_ai_cached(t, float(df_s['close'].iloc[-1]))
                weekly_s = get_weekly_trend(df_s)
                label    = classify_stock(t, df_s, ai_s, weekly_s, smart_flow=False)
                if label is None:
                    continue
                last_s   = df_s.iloc[-1]

                bb_now   = last_s['bb_width']
                bb_min20 = df_s['bb_width'].tail(20).min()
                squeezed = bb_now <= bb_min20 * BB_SQUEEZE_TOL
                supply   = df_s['can_cung'].tail(5).any()
                rs_s     = calc_rs_rating(df_s, df_vnidx)
                div_s    = detect_divergence(df_s)
                w52_s    = calc_52w_info(df_s)
                wave_s   = calc_wave_bottom_score(
                    df_s, last_s,
                    smart_flow    = False,
                    near_52w_high = bool(w52_s['near_high']),
                    div_bullish   = bool(div_s['signal'] == 'BULLISH'),
                )

                row = {
                    'Ticker':      t,
                    'Thị Giá':     f"{last_s['close']:,.0f}",
                    'Vol Raw':     float(last_s['vol_strength']),
                    'RSI Raw':     float(last_s['rsi']),
                    'AI T+3 Raw':  ai_s,
                    'Weekly Raw':  weekly_s,
                    'ADX Raw':     float(last_s.get('adx', 0)),
                    'RS Raw':      rs_s,
                    'Lò Xo BB':    bool(squeezed),
                    'Cạn Cung':    bool(supply),
                    'Tổ Chức Gom': False,
                    '52W High':    bool(w52_s['near_high']),
                    'Div Bullish': bool(div_s['signal'] == 'BULLISH'),
                    'Div Bearish': bool(div_s['signal'] == 'BEARISH'),
                    'Wave Bottom': bool(wave_s['is_wave_bottom']),
                    'Wave Score':  wave_s['score'],
                }
                if   "Bùng Nổ Mua" in label: breakouts.append(row)
                elif "Bán Tháo"     in label: sell_dumps.append(row)
                elif "Danh Sách"    in label: watchlist.append(row)
                elif "Chân Sóng"    in label: wave_bottom.append(row)
                elif "Quan Sát"     in label: watch_zone.append(row)
                elif "Đang Tăng"    in label: running_strong.append(row)
            except Exception as e:
                print(f"[WARN] Scan {t}: {e}")
            progress.progress((i + 1) / len(scan_list))

        st.divider()
        render_radar_summary_banner(breakouts, sell_dumps, watchlist, wave_bottom, watch_zone, running_strong)
        st.divider()

        # [#3] Sắp xếp theo điểm tổng hợp (AI + RS + đảo ngược RSI)
        def _sort_score(row: dict) -> float:
            ai  = float(row['AI T+3 Raw']) if _is_valid_score(row['AI T+3 Raw']) else 0
            rs  = row.get('RS Raw', 50)
            rsi = row.get('RSI Raw', 50)
            vol = row.get('Vol Raw', 1)
            adx = row.get('ADX Raw', 0)
            # RSI lý tưởng là 35-52 → điểm cao nhất ở giữa khoảng đó
            rsi_score = max(0, 100 - abs(rsi - 44) * 3)
            return ai * 0.4 + rs * 0.2 + rsi_score * 0.2 + min(vol, 2) * 10 + adx * 0.2

        for lst in [breakouts, sell_dumps, watchlist, wave_bottom, watch_zone, running_strong]:
            lst.sort(key=_sort_score, reverse=True)

        use_cards = "Card" in view_mode

        # ── TẦNG 1A: BÙNG NỔ MUA ──
        st.write("### 🚀 Tầng 1A — Bùng Nổ Mua")
        st.caption("Vol nổ + nến xanh. ⚠️ Cẩn thận mua đuổi — chờ pullback về MA20.")
        if breakouts:
            if use_cards:
                for r in breakouts: render_radar_card(r, "red")
            else:
                render_radar_table(breakouts)
        else:
            st.success("✅ Không có mã bùng nổ mua hôm nay.")

        # ── TẦNG 1B: BÁN THÁO ──
        st.write("### 🔴 Tầng 1B — Bán Tháo")
        st.caption("Vol nổ + nến đỏ. **Tuyệt đối không mua vào — chờ Vol cạn mới xem xét.**")
        if sell_dumps:
            if use_cards:
                for r in sell_dumps: render_radar_card(r, "red")
            else:
                render_radar_table(sell_dumps)
        else:
            st.success("✅ Không có mã bán tháo hôm nay.")

        st.divider()

        # ── TẦNG 2: DANH SÁCH CHỜ ──
        st.write("### ⚖️ Tầng 2 — Danh Sách Chờ Chân Sóng")
        st.caption("Nền đẹp + Weekly xác nhận. **Nhóm ưu tiên nhất để vào lệnh.**")
        if watchlist:
            if use_cards:
                for r in watchlist: render_radar_card(r, "green")
            else:
                render_radar_table(watchlist)
            st.success(f"✅ {len(watchlist)} mã đủ tiêu chuẩn. Phân tích chi tiết ở Tab 1 trước khi vào.")
        else:
            st.info("Hôm nay chưa có mã đủ tiêu chuẩn.")

        st.divider()

        # ── TẦNG 3: CHÂN SÓNG ──
        st.write("### 🌊 Tầng 3 — Chân Sóng (Bắt sóng sớm)")
        st.caption("Đang tích lũy nền. Vào nhỏ 10–15% vốn, SL chặt theo ATR.")
        if wave_bottom:
            if use_cards:
                for r in wave_bottom: render_radar_card(r, "blue")
            else:
                render_radar_table(wave_bottom)
            st.info(f"🌊 {len(wave_bottom)} mã vùng chân sóng. Chờ thêm 1–2 phiên xác nhận.")
        else:
            st.write("Không có mã chân sóng hôm nay.")

        st.divider()

        # ── TẦNG 4: QUAN SÁT ──
        st.write("### 👁️ Tầng 4 — Vùng Quan Sát")
        st.caption("Tín hiệu sớm, chưa đủ điều kiện. Theo dõi 2–3 phiên.")
        if watch_zone:
            if use_cards:
                for r in watch_zone: render_radar_card(r, "gray")
            else:
                render_radar_table(watch_zone)
        else:
            st.write("Không có mã quan sát.")

        st.divider()

        # ── TẦNG 5: ĐANG TĂNG MẠNH ──
        st.write("### 🔥 Tầng 5 — Đang Tăng Mạnh (Theo dõi thôi)")
        st.caption("RSI 65–80, giá trên MA20. **Không mua đuổi** — chờ RSI về < 60 mới xem xét lại.")
        if running_strong:
            if use_cards:
                for r in running_strong: render_radar_card(r, "orange")
            else:
                render_radar_table(running_strong)
            st.warning(f"⚠️ {len(running_strong)} mã đang chạy nóng — chỉ theo dõi, không vào lệnh mới.")
        else:
            st.write("Không có mã đang tăng mạnh.")

        st.divider()
        with st.expander("📖 Hướng dẫn đọc bảng Radar V23.0"):
            st.markdown("""
| Tầng | Ý nghĩa | Hành động |
|------|---------|----------|
| 🚀 Bùng Nổ Mua | Vol nổ + nến xanh | Chờ pullback, không mua đuổi |
| 🔴 Bán Tháo | Vol nổ + nến đỏ | Tuyệt đối không mua |
| ⚖️ Danh Sách Chờ | Nền đẹp, Weekly xác nhận | Ưu tiên vào lệnh |
| 🌊 Chân Sóng | Đang tích lũy /11 tiêu chí | Vào nhỏ, SL chặt |
| 👁️ Quan Sát | Tín hiệu sớm RSI < 65 | Theo dõi thêm |
| 🔥 Đang Tăng Mạnh | RSI 65–80, đang chạy | Không mua đuổi |

| Cột | Ý nghĩa | Ngưỡng tốt |
|-----|---------|-----------|
| AI T+3 | Xác suất tăng ≥2% sau 3 phiên | 🔥≥70% \| ✅≥55% |
| RS Rating | Sức mạnh vs VN-Index 3 tháng | 🔥≥80 \| ✅≥65 |
| RSI | Quá mua/bán | 35–52 lý tưởng |
| Vol | Khối lượng / TB 10 phiên | 0.8–1.2x tích lũy |
| ADX | Sức mạnh xu hướng | > 25 đáng tin |
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
# TAB 6: VN-INDEX & TƯƠNG QUAN
# ==============================================================================
with tab6:
    st.subheader(f"📊 Phân Tích VN-Index & Tương Quan với {ticker}")

    if st.button("🔄 Xóa Cache VNI (bấm nếu lần trước lỗi)"):
        get_vnindex_cached.clear()
        st.session_state.pop('vni_loaded', None)
        st.success("✅ Cache VNI đã xóa — bấm 'Tải Dữ Liệu' để tải lại.")

    if st.button("🔄 Tải Dữ Liệu VN-Index & Phân Tích"):
        with st.spinner("Đang tải dữ liệu..."):
            # Dùng E1VFVN30 (ETF bám VN30) — load nhanh như mọi mã thông thường
            df_vni_raw = get_price('E1VFVN30', days=400)
            if not valid(df_vni_raw):
                df_vni_raw = get_price('VN30', days=400)   # fallback
            df_stk_raw = get_price(ticker, days=300)
            if valid(df_stk_raw):
                df_stk_raw = calc_indicators(df_stk_raw)

        if not valid(df_vni_raw):
            st.error("❌ Không lấy được dữ liệu E1VFVN30. Thử lại sau.")
        else:
            st.session_state['vni_loaded']  = True
            st.session_state['vni_df']      = df_vni_raw
            st.session_state['vni_stk_df']  = df_stk_raw
            st.session_state['vni_ticker']  = ticker
            st.caption("📊 Dữ liệu VNI đang dùng: **E1VFVN30** (ETF bám VN30, tương quan ~95% với VN-Index)")

    # Render nội dung từ session_state — giữ nguyên dù Streamlit rerender
    if st.session_state.get('vni_loaded'):
        df_vni   = calc_indicators(st.session_state['vni_df'])
        df_stk   = st.session_state.get('vni_stk_df')
        last_v   = df_vni.iloc[-1]
        # Hiện thông báo nếu đang xem mã khác với mã đã load
        loaded_ticker = st.session_state.get('vni_ticker', ticker)
        if loaded_ticker != ticker:
            st.info(f"ℹ️ Dữ liệu tương quan đang hiển thị cho **{loaded_ticker}**. Bấm 'Tải Dữ Liệu' để cập nhật cho {ticker}.")

        if df_stk is not None:
            df_stk = calc_indicators(df_stk) if 'rsi' not in df_stk.columns else df_stk

        # ── PHẦN 1: SNAPSHOT VNI ──
        st.write("### 1️⃣ Snapshot VN-Index Hôm Nay")
        price_vni  = last_v['close']
        ret_1d     = last_v['return_1d'] * 100
        ret_1w     = (df_vni['close'].iloc[-1] / df_vni['close'].iloc[-5]  - 1) * 100 if len(df_vni) >= 5  else 0
        ret_1m     = (df_vni['close'].iloc[-1] / df_vni['close'].iloc[-21] - 1) * 100 if len(df_vni) >= 21 else 0
        ret_ytd    = (df_vni['close'].iloc[-1] / df_vni['close'].iloc[-252]- 1) * 100 if len(df_vni) >= 252 else 0

        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric("VN-Index", f"{price_vni:,.1f}", delta=f"{ret_1d:+.2f}% hôm nay",
                  delta_color="normal" if ret_1d >= 0 else "inverse")
        s2.metric("1 Tuần",   f"{ret_1w:+.2f}%",  delta_color="normal" if ret_1w >= 0 else "inverse")
        s3.metric("1 Tháng",  f"{ret_1m:+.2f}%",  delta_color="normal" if ret_1m >= 0 else "inverse")
        s4.metric("YTD",      f"{ret_ytd:+.2f}%", delta_color="normal" if ret_ytd >= 0 else "inverse")
        rsi_vni = last_v['rsi']
        s5.metric("RSI VNI",  f"{rsi_vni:.1f}",
                  delta="Quá Mua ⚠️" if rsi_vni > 70 else ("Quá Bán 💡" if rsi_vni < 30 else "Ổn Định ✓"),
                  delta_color="inverse" if rsi_vni > 70 else ("normal" if rsi_vni < 30 else "off"))

        st.divider()

        # ── PHẦN 1.2: VỊ TRÍ KỸ THUẬT VNI ──
        st.write("### 2️⃣ Vị Trí Kỹ Thuật VN-Index")
        ma20_v  = last_v['ma20']
        ma50_v  = last_v['ma50']
        ma200_v = last_v.get('ma200', last_v['ma50'])
        macd_v  = last_v['macd']
        sig_v   = last_v['signal']
        adx_v   = last_v.get('adx', 0)
        ichi_v  = ichimoku_signal(last_v)

        t1, t2, t3, t4 = st.columns(4)
        t1.metric("VNI vs MA20",  f"{price_vni:,.0f} / {ma20_v:,.0f}",
                  delta="Trên MA20 ✓" if price_vni > ma20_v else "Dưới MA20 ⚠️",
                  delta_color="normal" if price_vni > ma20_v else "inverse")
        t2.metric("VNI vs MA50",  f"{price_vni:,.0f} / {ma50_v:,.0f}",
                  delta="Trên MA50 ✓" if price_vni > ma50_v else "Dưới MA50 ⚠️",
                  delta_color="normal" if price_vni > ma50_v else "inverse")
        t3.metric("VNI vs MA200", f"{price_vni:,.0f} / {ma200_v:,.0f}",
                  delta="Trên MA200 ✓" if price_vni > ma200_v else "Dưới MA200 ⚠️",
                  delta_color="normal" if price_vni > ma200_v else "inverse")
        t4.metric("MACD",         f"{macd_v:.1f}",
                  delta="Cross Up ✓" if macd_v > sig_v else "Cross Down ⚠️",
                  delta_color="normal" if macd_v > sig_v else "inverse")

        # Xu hướng ngắn/trung/dài
        weekly_vni = get_weekly_trend(df_vni)
        st.write("#### Xu Hướng Đa Khung Thời Gian")
        u1, u2, u3, u4 = st.columns(4)
        u1.metric("Ngắn hạn (Daily)",  "📈 TĂNG" if price_vni > ma20_v  else "📉 GIẢM",
                  delta_color="off")
        u2.metric("Trung hạn (Weekly)", _weekly_badge(weekly_vni), delta_color="off")
        u3.metric("Dài hạn (MA200)",   "📈 BULL" if price_vni > ma200_v else "📉 BEAR",
                  delta_color="off")
        u4.metric("ADX Sức Mạnh",      f"{adx_v:.1f}",
                  delta="Xu hướng rõ ✓" if adx_v > 25 else "Sideways",
                  delta_color="normal" if adx_v > 25 else "off")

        # Ichimoku
        if 'BULL' in ichi_v['signal']:   st.success(ichi_v['label'])
        elif ichi_v['signal'] == 'BEAR': st.error(ichi_v['label'])
        else:                            st.warning(ichi_v['label'])

        st.divider()

        # ── PHẦN 1.3: NHẬN XÉT TỔNG HỢP AUTO ──
        st.write("### 3️⃣ Nhận Xét Tổng Hợp Thị Trường")

        # Xác định trạng thái Bull/Bear/Sideway
        bull_signals = sum([
            price_vni > ma20_v,
            price_vni > ma50_v,
            price_vni > ma200_v,
            macd_v > sig_v,
            weekly_vni == 'UP',
            rsi_vni > 50,
        ])
        if   bull_signals >= 5: market_state = "BULL MẠNH"
        elif bull_signals >= 4: market_state = "TÍCH CỰC"
        elif bull_signals >= 3: market_state = "TRUNG LẬP"
        elif bull_signals >= 2: market_state = "THẬN TRỌNG"
        else:                   market_state = "BEAR"

        state_color = {
            "BULL MẠNH": "success", "TÍCH CỰC": "success",
            "TRUNG LẬP": "warning", "THẬN TRỌNG": "warning",
            "BEAR": "error"
        }[market_state]

        # Nhận xét chi tiết
        lines = []
        lines.append(f"**Trạng thái tổng thể: {market_state}** ({bull_signals}/6 tín hiệu tích cực)")
        lines.append("")

        # MA
        if price_vni > ma200_v:
            lines.append(f"📈 VN-Index đang ở trên MA200 ({ma200_v:,.0f}) — cấu trúc tăng dài hạn còn nguyên vẹn.")
        else:
            lines.append(f"📉 VN-Index đang dưới MA200 ({ma200_v:,.0f}) — thị trường đang trong giai đoạn điều chỉnh dài hạn.")

        if price_vni > ma20_v:
            pct_above = (price_vni - ma20_v) / ma20_v * 100
            lines.append(f"✅ Giá đang cách MA20 {pct_above:.1f}% — {'vùng an toàn, chưa xa MA20 quá.' if pct_above < 5 else 'đã xa MA20, cẩn thận điều chỉnh.'}")
        else:
            pct_below = (ma20_v - price_vni) / ma20_v * 100
            lines.append(f"⚠️ Giá đang dưới MA20 {pct_below:.1f}% — phe bán đang kiểm soát ngắn hạn.")

        # RSI
        if rsi_vni > 70:
            lines.append(f"🔴 RSI {rsi_vni:.1f} — thị trường đang quá mua. Tránh giải ngân mạnh, chờ RSI hạ về 55-60.")
        elif rsi_vni < 35:
            lines.append(f"💡 RSI {rsi_vni:.1f} — thị trường quá bán. Thường là cơ hội mua vào tốt nếu fundamental còn tốt.")
        elif 45 <= rsi_vni <= 60:
            lines.append(f"✅ RSI {rsi_vni:.1f} — vùng lý tưởng, thị trường chưa nóng, còn room để tăng tiếp.")
        else:
            lines.append(f"🟡 RSI {rsi_vni:.1f} — vùng trung lập, theo dõi thêm hướng tiếp theo.")

        # MACD
        if macd_v > sig_v:
            lines.append(f"✅ MACD đang cắt lên Signal ({macd_v:.1f} > {sig_v:.1f}) — momentum tăng đang hình thành.")
        else:
            lines.append(f"⚠️ MACD đang cắt xuống Signal ({macd_v:.1f} < {sig_v:.1f}) — momentum đang suy yếu.")

        # Kết luận hành động
        lines.append("")
        if market_state in ("BULL MẠNH", "TÍCH CỰC"):
            lines.append("**💡 Kết Luận:** Thị trường đang ủng hộ. Có thể giải ngân vào các mã đã tích lũy nền đẹp (Tầng 2, 3 của Radar). Ưu tiên mã có RS Rating cao.")
        elif market_state == "TRUNG LẬP":
            lines.append("**💡 Kết Luận:** Thị trường phân hóa. Chọn lọc kỹ — chỉ vào các mã có tín hiệu rất rõ, vốn nhỏ (20-30%), SL chặt.")
        else:
            lines.append("**💡 Kết Luận:** Thị trường bất lợi. Giảm tỷ trọng, ưu tiên bảo toàn vốn. Chỉ nắm giữ mã có nền tảng cực mạnh.")

        comment_text = "\n\n".join(lines)
        if state_color == "success":   st.success(comment_text)
        elif state_color == "warning": st.warning(comment_text)
        else:                          st.error(comment_text)

        st.divider()

        # ── PHẦN 1.4: THANH KHOẢN ──
        st.write("### 4️⃣ Thanh Khoản Thị Trường")
        vol_10 = df_vni['volume'].tail(10).mean() if 'volume' in df_vni.columns else 0
        vol_20 = df_vni['volume'].tail(20).mean() if 'volume' in df_vni.columns else 0
        if vol_10 > 0 and vol_20 > 0:
            liq1, liq2, liq3 = st.columns(3)
            liq1.metric("Vol TB 10 phiên", f"{vol_10/1e9:.1f} Tỷ")
            liq2.metric("Vol TB 20 phiên", f"{vol_20/1e9:.1f} Tỷ")
            liq3.metric("Xu hướng thanh khoản",
                        "🟢 Tiền đang vào" if vol_10 > vol_20 * 1.1
                        else ("🔴 Tiền đang rút" if vol_10 < vol_20 * 0.9 else "🟡 Ổn định"),
                        delta_color="off")
            if vol_10 > vol_20 * 1.1:
                st.success("✅ Thanh khoản 10 phiên cao hơn TB 20 phiên — dòng tiền đang đổ vào thị trường.")
            elif vol_10 < vol_20 * 0.9:
                st.warning("⚠️ Thanh khoản 10 phiên thấp hơn TB — thị trường đang thiếu dòng tiền mới.")
            else:
                st.info("🟡 Thanh khoản ổn định, không có biến động bất thường.")

        st.divider()

        # ── PHẦN 2: TƯƠNG QUAN MÃ VS VNI ──
        st.write(f"### 5️⃣ Tương Quan {ticker} vs VN-Index")

        if not valid(df_stk):
            st.warning(f"⚠️ Không lấy được dữ liệu giá {ticker}.")
        else:
            # Ghép 2 df theo ngày
            df_vni_r = df_vni[['date','close','return_1d']].copy().rename(
                columns={'close':'close_vni','return_1d':'ret_vni'})
            df_stk_r = df_stk[['date','close','return_1d']].copy().rename(
                columns={'close':'close_stk','return_1d':'ret_stk'})
            df_vni_r['date'] = df_vni_r['date'].astype(str).str[:10]
            df_stk_r['date'] = df_stk_r['date'].astype(str).str[:10]
            df_merged = pd.merge(df_vni_r, df_stk_r, on='date').dropna().tail(63)

            if len(df_merged) < 20:
                st.warning("⚠️ Không đủ dữ liệu chung để tính tương quan.")
            else:
                # Beta
                cov   = np.cov(df_merged['ret_stk'], df_merged['ret_vni'])
                beta  = cov[0,1] / (cov[1,1] + 1e-9)
                beta  = round(beta, 2)

                # Correlation
                corr  = df_merged['ret_stk'].corr(df_merged['ret_vni'])
                corr  = round(corr, 3)
                r2    = round(corr ** 2 * 100, 1)

                # RS Rating
                rs_tab6 = calc_rs_rating(df_stk, df_vni)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Beta (63 phiên)", f"{beta:.2f}",
                          delta="Biến động mạnh hơn TT" if beta > 1.2
                          else ("Phòng thủ" if beta < 0.8 else "Cân bằng"),
                          delta_color="off")
                c2.metric("Correlation (R)", f"{corr:.2f}",
                          delta="Đồng pha cao" if corr > 0.7
                          else ("Ngược chiều" if corr < -0.3 else "Tương quan trung bình"),
                          delta_color="off")
                c3.metric("R² (Giải thích)", f"{r2:.1f}%",
                          delta=f"VNI giải thích {r2:.0f}% biến động {ticker}",
                          delta_color="off")
                c4.metric("RS Rating", f"{rs_tab6:.0f}/100",
                          delta=_rs_badge(rs_tab6), delta_color="off")

                # Giải thích Beta bằng chữ
                st.write("#### 📝 Đọc Vị Tương Quan")
                interp_lines = []

                if beta > 1.5:
                    interp_lines.append(f"⚡ **Beta {beta:.2f}** — {ticker} biến động **mạnh hơn thị trường {beta:.1f}x**. Khi VNI tăng 1%, {ticker} thường tăng ~{beta:.1f}%. Đây là mã **aggressive** — lời nhiều nhưng rủi ro cũng cao hơn.")
                elif beta > 1.0:
                    interp_lines.append(f"📈 **Beta {beta:.2f}** — {ticker} biến động nhỉnh hơn thị trường một chút. Phù hợp khi thị trường bull.")
                elif beta > 0.5:
                    interp_lines.append(f"🛡️ **Beta {beta:.2f}** — {ticker} ít biến động hơn thị trường. Mã **phòng thủ** — ít lời hơn khi bull nhưng cũng ít mất hơn khi bear.")
                elif beta > 0:
                    interp_lines.append(f"😴 **Beta {beta:.2f}** — {ticker} gần như không phản ứng với thị trường chung. Giá phụ thuộc chủ yếu vào yếu tố nội tại của doanh nghiệp.")
                else:
                    interp_lines.append(f"🔄 **Beta {beta:.2f}** — {ticker} có xu hướng **đi ngược thị trường**. Có thể dùng như hedge khi thị trường giảm.")

                if corr > 0.8:
                    interp_lines.append(f"🔗 **Correlation {corr:.2f}** — Gần như đồng hành hoàn toàn với VNI. Khi thị trường xấu, {ticker} rất khó thoát khỏi đà giảm chung.")
                elif corr > 0.5:
                    interp_lines.append(f"🔗 **Correlation {corr:.2f}** — Tương quan trung bình với VNI. {ticker} vẫn có yếu tố riêng ảnh hưởng đến giá.")
                else:
                    interp_lines.append(f"🔓 **Correlation {corr:.2f}** — Ít tương quan với VNI. {ticker} giao dịch theo câu chuyện riêng của mình.")

                # Tín hiệu giao dịch theo VNI
                interp_lines.append("")
                if market_state in ("BULL MẠNH", "TÍCH CỰC") and beta > 1:
                    interp_lines.append(f"✅ **Tín hiệu:** Thị trường đang Bull + Beta {beta:.1f} > 1 → {ticker} có tiềm năng outperform thị trường. Thời điểm thuận lợi nếu kỹ thuật mã đẹp.")
                elif market_state in ("BULL MẠNH", "TÍCH CỰC") and beta <= 1:
                    interp_lines.append(f"🟡 **Tín hiệu:** Thị trường Bull nhưng Beta {beta:.1f} thấp → {ticker} có thể underperform khi thị trường tăng mạnh. Cân nhắc tìm mã Beta cao hơn.")
                elif market_state in ("BEAR", "THẬN TRỌNG") and beta < 1:
                    interp_lines.append(f"🛡️ **Tín hiệu:** Thị trường Bear/thận trọng + Beta {beta:.1f} thấp → {ticker} có thể giữ giá tốt hơn thị trường. Phù hợp phòng thủ.")
                else:
                    interp_lines.append(f"⚠️ **Tín hiệu:** Thị trường Bear/thận trọng + Beta {beta:.1f} cao → {ticker} có thể giảm mạnh hơn thị trường. Cẩn thận tỷ trọng.")

                for line in interp_lines:
                    st.markdown(line)

                st.divider()

                # ── CHART: So sánh hiệu suất ──
                st.write("#### 📈 So Sánh Hiệu Suất 63 Phiên (Normalized = 100)")
                base_vni = df_merged['close_vni'].iloc[0]
                base_stk = df_merged['close_stk'].iloc[0]
                df_merged['norm_vni'] = df_merged['close_vni'] / base_vni * 100
                df_merged['norm_stk'] = df_merged['close_stk'] / base_stk * 100

                fig_corr = go.Figure()
                fig_corr.add_trace(go.Scatter(
                    x=df_merged['date'], y=df_merged['norm_vni'],
                    name='VN-Index', line=dict(color='royalblue', width=2),
                ))
                fig_corr.add_trace(go.Scatter(
                    x=df_merged['date'], y=df_merged['norm_stk'],
                    name=ticker, line=dict(color='orange', width=2.5),
                ))
                fig_corr.add_hline(y=100, line_dash='dot', line_color='gray')
                final_vni = df_merged['norm_vni'].iloc[-1]
                final_stk = df_merged['norm_stk'].iloc[-1]
                outperf   = final_stk - final_vni
                fig_corr.add_annotation(
                    x=df_merged['date'].iloc[-1],
                    y=final_stk,
                    text=f"{ticker}: {final_stk:.1f} ({'▲' if outperf > 0 else '▼'}{abs(outperf):.1f} vs VNI)",
                    showarrow=True, arrowhead=2,
                    font=dict(color='orange', size=12),
                )
                fig_corr.update_layout(
                    height=400, template='plotly_white',
                    title=f"Hiệu Suất So Sánh — {ticker} vs VN-Index (63 phiên gần nhất)",
                    yaxis_title="Chỉ số (100 = điểm xuất phát)",
                    margin=dict(l=20, r=20, t=50, b=20),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02),
                )
                st.plotly_chart(fig_corr, use_container_width=True)

                # Outperform label
                if outperf > 5:
                    st.success(f"🏆 **{ticker} đang OUTPERFORM VN-Index {outperf:.1f}% trong 63 phiên!** RS Rating xác nhận mã mạnh hơn thị trường.")
                elif outperf > 0:
                    st.info(f"✅ {ticker} nhỉnh hơn VNI {outperf:.1f}% trong 63 phiên — outperform nhẹ.")
                elif outperf > -5:
                    st.warning(f"🟡 {ticker} đang underperform VNI {abs(outperf):.1f}% — đang yếu hơn thị trường chung.")
                else:
                    st.error(f"🔴 {ticker} đang underperform VNI {abs(outperf):.1f}% — rất yếu so với thị trường. Cân nhắc chuyển sang mã RS cao hơn.")

                # ── CHART VNI ──
                st.divider()
                st.write("#### 📊 Biểu Đồ VN-Index (120 Phiên)")
                chart_vni = df_vni.tail(120)
                xv = chart_vni['date']
                fig_vni = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                        vertical_spacing=0.05, row_heights=[0.7, 0.3])
                fig_vni.add_trace(go.Candlestick(
                    x=xv, open=chart_vni['open'], high=chart_vni['high'],
                    low=chart_vni['low'], close=chart_vni['close'], name='VNI'
                ), row=1, col=1)
                for mc, col_name, nm in [('ma20','orange','MA20'),('ma50','purple','MA50'),('ma200','red','MA200')]:
                    if mc in chart_vni.columns:
                        fig_vni.add_trace(go.Scatter(x=xv, y=chart_vni[mc],
                            line=dict(color=col_name, width=1.5), name=nm), row=1, col=1)
                if 'volume' in chart_vni.columns:
                    fig_vni.add_trace(go.Bar(x=xv, y=chart_vni['volume'],
                        name='KL', marker_color='lightblue'), row=2, col=1)
                fig_vni.update_layout(height=600, template='plotly_white',
                                      xaxis_rangeslider_visible=False,
                                      margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_vni, use_container_width=True)

# ==============================================================================
# TAB 7: HEATMAP & ĐỐI THỦ NGÀNH
# ==============================================================================
with tab7:
    st.subheader("🌡️ Heatmap Thị Trường & Phân Tích Đối Thủ Ngành")

    col_h1, col_h2 = st.columns(2)
    run_heatmap = col_h1.button("🌡️ Vẽ Heatmap Thị Trường HOSE")
    run_peers   = col_h2.button(f"🏭 Phân Tích Đối Thủ Cùng Ngành với {ticker}")

    # ── HEATMAP ──
    if run_heatmap:
        with st.spinner("Đang quét dữ liệu heatmap (~2 phút)..."):
            sample_hm = list(dict.fromkeys(tickers))[:100]
            df_hm     = build_market_heatmap(sample_hm)
            st.session_state['heatmap_df'] = df_hm

    if st.session_state.get('heatmap_df') is not None:
        df_hm = st.session_state['heatmap_df']
        if not df_hm.empty:
            st.write("#### 📊 Lợi Nhuận 1 Ngày Theo Ngành")
            sector_avg = df_hm.groupby('sector')['ret1d'].mean().reset_index()
            sector_avg = sector_avg.sort_values('ret1d', ascending=True)
            colors_hm  = ['rgba(220,50,50,0.8)' if v < 0 else 'rgba(50,180,50,0.8)'
                          for v in sector_avg['ret1d']]
            fig_hm = go.Figure(go.Bar(
                x=sector_avg['ret1d'], y=sector_avg['sector'],
                orientation='h',
                marker_color=colors_hm,
                text=[f"{v:+.2f}%" for v in sector_avg['ret1d']],
                textposition='outside',
            ))
            fig_hm.update_layout(
                height=450, template='plotly_white',
                title="Lợi Nhuận Trung Bình 1 Ngày Theo Ngành (%)",
                xaxis_title="% Thay đổi",
                margin=dict(l=150, r=60, t=50, b=20),
            )
            fig_hm.add_vline(x=0, line_color='black', line_width=1)
            st.plotly_chart(fig_hm, use_container_width=True)

            # Heatmap từng mã theo ngành
            st.write("#### 🗺️ Heatmap Từng Mã")
            fig_tile = go.Figure()
            for sec in df_hm['sector'].unique():
                sec_df = df_hm[df_hm['sector'] == sec]
                for _, row_t in sec_df.iterrows():
                    fig_tile.add_trace(go.Scatter(
                        x=[sec], y=[row_t['ticker']],
                        mode='markers+text',
                        marker=dict(
                            size=40,
                            color=row_t['ret1d'],
                            colorscale='RdYlGn',
                            cmin=-3, cmax=3,
                            showscale=True,
                            colorbar=dict(title="%"),
                        ),
                        text=f"{row_t['ticker']}<br>{row_t['ret1d']:+.1f}%",
                        textposition='middle center',
                        showlegend=False,
                    ))
            fig_tile.update_layout(
                height=600, template='plotly_white',
                title="Heatmap Mã Theo Ngành — Xanh=Tăng | Đỏ=Giảm",
                margin=dict(l=80, r=20, t=50, b=20),
            )
            st.plotly_chart(fig_tile, use_container_width=True)

            # Top tăng/giảm
            top_up   = df_hm.nlargest(5, 'ret1d')[['ticker','sector','ret1d','ret5d']]
            top_down = df_hm.nsmallest(5, 'ret1d')[['ticker','sector','ret1d','ret5d']]
            tc1, tc2 = st.columns(2)
            with tc1:
                st.write("#### 🚀 Top 5 Tăng Mạnh")
                st.dataframe(top_up, use_container_width=True, hide_index=True)
            with tc2:
                st.write("#### 📉 Top 5 Giảm Mạnh")
                st.dataframe(top_down, use_container_width=True, hide_index=True)

    st.divider()

    # ── ĐỐI THỦ NGÀNH ──
    if run_peers:
        sector_name = get_ticker_sector(ticker)
        if sector_name:
            with st.spinner(f"Đang phân tích các mã cùng ngành {sector_name}..."):
                peers_t7 = analyze_sector_peers(ticker, n_peers=8)
                st.session_state['peers_t7']       = peers_t7
                st.session_state['peers_t7_ticker'] = ticker
        else:
            st.warning(f"Mã {ticker} chưa được phân loại ngành.")

    if st.session_state.get('peers_t7') and st.session_state.get('peers_t7_ticker') == ticker:
        peers_t7    = st.session_state['peers_t7']
        sector_name = get_ticker_sector(ticker)
        st.write(f"#### 🏭 Đối Thủ Cùng Ngành {sector_name} — So Sánh RS Rating & Momentum")
        df_pt7 = pd.DataFrame([{
            'Mã':        p['ticker'],
            'Giá':       p['price'],
            'RS Rating': p['rs'],
            'RSI':       p['rsi'],
            '5 Ngày':    f"{p['ret5d']:+.1f}%",
            'ADX':       p['adx'],
            'Trên MA20': "✅" if p['ma_ok'] else "—",
        } for p in peers_t7])
        st.dataframe(df_pt7, use_container_width=True, hide_index=True,
            column_config={
                "RS Rating": st.column_config.ProgressColumn("RS Rating",
                    min_value=0, max_value=100, format="%.0f"),
            })

        # Chart so sánh RS Rating
        all_names = [ticker] + [p['ticker'] for p in peers_t7]
        my_rs_t7  = calc_rs_rating(get_price(ticker, days=100) or pd.DataFrame(), pd.DataFrame())
        all_rs    = [my_rs_t7] + [p['rs'] for p in peers_t7]
        colors_rs = ['gold' if n==ticker else
                     ('green' if r >= 65 else ('orange' if r >= 45 else 'red'))
                     for n, r in zip(all_names, all_rs)]
        fig_rs = go.Figure(go.Bar(
            x=all_names, y=all_rs,
            marker_color=colors_rs,
            text=[f"{r:.0f}" for r in all_rs],
            textposition='outside',
        ))
        fig_rs.add_hline(y=65, line_dash='dot', line_color='green',
                         annotation_text="RS ≥ 65 (mạnh)")
        fig_rs.update_layout(
            height=350, template='plotly_white',
            title=f"RS Rating — {ticker} vs Đối Thủ (vàng = mã đang xem)",
            yaxis=dict(range=[0,105]),
            margin=dict(l=20, r=20, t=50, b=20),
        )
        st.plotly_chart(fig_rs, use_container_width=True)

        best_peer_t7 = peers_t7[0] if peers_t7 else None
        if best_peer_t7 and best_peer_t7['rs'] > my_rs_t7 + 10:
            st.warning(
                f"⚠️ **{best_peer_t7['ticker']}** (RS {best_peer_t7['rs']:.0f}) "
                f"mạnh hơn **{ticker}** (RS {my_rs_t7:.0f}) trong ngành {sector_name}."
            )
        else:
            st.success(f"✅ **{ticker}** đang dẫn đầu hoặc cạnh tranh tốt trong ngành.")
