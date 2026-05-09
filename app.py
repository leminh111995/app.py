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
VN30_BASKET = [
    "VCB", "BID", "CTG", "MBB", "TCB", "VPB", "HDB", "STB", "ACB", "TPB",
    "VIC", "VHM", "VRE", "NVL",
    "VNM", "SAB", "MSN", "MCH",
    "FPT", "MWG",
    "HPG", "GAS", "PLX", "POW", "GVR",
    "SSI", "VJC", "BVH", "KDH", "PDR",
]
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

def _normalize_flow_df(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Chuẩn hóa DataFrame dòng tiền về cột chuẩn: date, buyval, sellval, netval.
    Xử lý tất cả tên cột có thể từ các source khác nhau của Vnstock.
    """
    if not valid(df):
        return None
    df = df.copy()
    # Chuẩn hóa tên cột về lowercase không dấu
    df.columns = [str(c).lower().strip() for c in df.columns]

    # Map date
    for c in ['date', 'tradingdate', 'trading_date', 'time', 'ngay']:
        if c in df.columns:
            df['date'] = pd.to_datetime(df[c]).dt.strftime('%Y-%m-%d')
            break
    else:
        df['date'] = pd.to_datetime(df.index).strftime('%Y-%m-%d')

    # Map buyval
    for c in ['buyval', 'buy_val', 'buyvalue', 'buy_value', 'gtmua',
              'totalbuyvol', 'buyvol', 'foreignbuyvalue', 'propbuyvol']:
        if c in df.columns:
            df['buyval'] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            break
    else:
        df['buyval'] = 0.0

    # Map sellval
    for c in ['sellval', 'sell_val', 'sellvalue', 'sell_value', 'gtban',
              'totalsellvol', 'sellvol', 'foreignsellvalue', 'propsellvol']:
        if c in df.columns:
            df['sellval'] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            break
    else:
        df['sellval'] = 0.0

    # Map netval
    for c in ['netval', 'net_val', 'netvalue', 'net_value', 'gtrong',
              'netvol', 'foreignnetvalue', 'propnetvol']:
        if c in df.columns:
            df['netval'] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            break
    else:
        df['netval'] = df['buyval'] - df['sellval']

    result = df[['date', 'buyval', 'sellval', 'netval']].dropna(subset=['date'])
    return result if len(result) > 0 else None


def fetch_all_flows(ticker: str, days: int = FOREIGN_DAYS) -> dict:
    """
    Thử TẤT CẢ endpoints có thể cho Foreign + Proprietary trong 1 lần gọi.
    Trả về {'foreign': df | None, 'proprietary': df | None, 'source': str}
    """
    start, end = date_range(days)
    SOURCES    = ['VCI', 'TCBS', 'SSI', 'FPTS']

    # ── Tất cả cách lấy Foreign ──
    foreign_attempts = [
        lambda: engine().stock.trade.foreign_trade(symbol=ticker, start=start, end=end),
        lambda: engine().stock.trading.foreign(symbol=ticker, start=start, end=end),
        lambda: engine().stock.trade.foreign(symbol=ticker, start=start, end=end),
    ]
    for src in SOURCES:
        for method_name in ['trade.foreign_trade', 'trading.foreign_trade',
                            'trading.foreign', 'trade.foreign']:
            def _make_attempt(s=src, m=method_name):
                def attempt():
                    stk = Vnstock().stock(symbol=ticker, source=s)
                    parts = m.split('.')
                    obj = stk
                    for p in parts[:-1]:
                        obj = getattr(obj, p)
                    return getattr(obj, parts[-1])(start=start, end=end)
                return attempt
            foreign_attempts.append(_make_attempt())

    # ── Tất cả cách lấy Proprietary ──
    prop_attempts = [
        lambda: engine().stock.trade.proprietary_trade(symbol=ticker, start=start, end=end),
        lambda: engine().stock.trading.proprietary(symbol=ticker, start=start, end=end),
        lambda: engine().stock.trade.proprietary(symbol=ticker, start=start, end=end),
    ]
    for src in SOURCES:
        for method_name in ['trade.proprietary_trade', 'trading.proprietary_trade',
                            'trading.proprietary', 'trade.proprietary']:
            def _make_prop(s=src, m=method_name):
                def attempt():
                    stk = Vnstock().stock(symbol=ticker, source=s)
                    parts = m.split('.')
                    obj = stk
                    for p in parts[:-1]:
                        obj = getattr(obj, p)
                    return getattr(obj, parts[-1])(start=start, end=end)
                return attempt
            prop_attempts.append(_make_prop())

    # ── Thử Foreign ──
    df_foreign = None
    foreign_src = 'none'
    for i, attempt in enumerate(foreign_attempts):
        try:
            raw = attempt()
            df_foreign = _normalize_flow_df(raw)
            if df_foreign is not None and len(df_foreign) > 0:
                foreign_src = f'attempt_{i}'
                print(f"[OK] Foreign {ticker} via attempt_{i}")
                break
        except Exception as e:
            print(f"[WARN] Foreign attempt_{i} {ticker}: {e}")
            continue

    # ── Thử Proprietary ──
    df_prop = None
    prop_src = 'none'
    for i, attempt in enumerate(prop_attempts):
        try:
            raw = attempt()
            df_prop = _normalize_flow_df(raw)
            if df_prop is not None and len(df_prop) > 0:
                prop_src = f'attempt_{i}'
                print(f"[OK] Proprietary {ticker} via attempt_{i}")
                break
        except Exception as e:
            print(f"[WARN] Prop attempt_{i} {ticker}: {e}")
            continue

    return {
        'foreign':     df_foreign,
        'proprietary': df_prop,
        'source':      f'F:{foreign_src} P:{prop_src}',
    }


# Giữ lại get_foreign/get_proprietary để tương thích với code cũ
def get_foreign(ticker: str, days: int = FOREIGN_DAYS) -> pd.DataFrame | None:
    return fetch_all_flows(ticker, days)['foreign']

def get_proprietary(ticker: str, days: int = FOREIGN_DAYS) -> pd.DataFrame | None:
    return fetch_all_flows(ticker, days)['proprietary']

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
news_headlines = []   # Đã bỏ input tin tức

# --- TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH",
    "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM",
    "🌊 BÓC TÁCH DÒNG TIỀN",
    "🔍 RADAR TRUY QUÉT SIÊU CỔ PHIẾU",
    "🏭 SECTOR ROTATION — DÒNG TIỀN NGÀNH",
    "📊 VN-INDEX & TƯƠNG QUAN",
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

            # --- Bảng điểm ---
            st.write("### 🎯 Bảng Điểm Chi Tiết 0-90")
            d1, d2, d3, d4, d5 = st.columns(5)
            d1.metric("🤖 AI XGBoost",  f"{scoring['ai_pts']}/{SCORE_AI_MAX}")
            d2.metric("📈 Kỹ Thuật",    f"{scoring['tech_pts']}/{SCORE_TECH_MAX}")
            d3.metric("🌊 Khối Ngoại",  f"{scoring['flow_pts']}/{SCORE_FLOW_MAX}")
            d4.metric("🏢 Tài Chính",   f"{scoring['fin_pts']}/{SCORE_FINANCE_MAX}")
            d5.metric("🏭 Ngành",       f"{scoring['sector_pts']}/{SCORE_SECTOR_MAX}")

            # Thanh điểm trực quan
            st.caption("Thanh điểm trực quan:")
            cols_bar = st.columns(3)
            items = [
                ("🤖 AI",        scoring['ai_pts'],     SCORE_AI_MAX),
                ("📈 Kỹ thuật",  scoring['tech_pts'],   SCORE_TECH_MAX),
                ("🌊 Ngoại",     scoring['flow_pts'],   SCORE_FLOW_MAX),
                ("🏢 Tài chính", scoring['fin_pts'],    SCORE_FINANCE_MAX),
                ("🏭 Ngành",     scoring['sector_pts'], SCORE_SECTOR_MAX),
            ]
            for i, (label, pts, max_pts) in enumerate(items):
                with cols_bar[i % 3]:
                    st.markdown(f"**{label}**")
                    st.progress(pts / max_pts)
                    st.caption(f"{pts}/{max_pts} điểm")

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
    col_quick, col_full = st.columns(2)
    run_quick = col_quick.button("⚡ Quét Nhanh (150 mã HOSE)")
    run_full  = col_full.button("🔭 Quét Toàn HOSE (~400 mã) — mất ~15 phút")

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
                ai_s     = predict_ai_t3(df_s)
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
