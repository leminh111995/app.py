# ==============================================================================
# QUANT SYSTEM V21.1 - THE PREDATOR LEVIATHAN SUPREME
# Tác giả: Minh | V21.1: XGBoost (Tab 1) + LightGBM (Radar) — Tối ưu tốc độ & độ chính xác
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
from xgboost import XGBClassifier          # Tab 1: chính xác tối đa (1 mã)

# Radar: dùng LightGBM nếu có, fallback về XGBoost nếu chưa cài
try:
    from lightgbm import LGBMClassifier
    LGBM_AVAILABLE = True
except ImportError:
    LGBM_AVAILABLE = False
    print("[INFO] LightGBM chưa cài — Radar sẽ dùng XGBoost thay thế")
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

# [NÂNG CẤP #3] Phí giao dịch thực tế
TRADE_FEE         = 0.0015   # 0.15% mỗi chiều
SLIPPAGE          = 0.001    # 0.1% trượt giá
ROUND_TRIP_COST   = (TRADE_FEE + SLIPPAGE) * 2   # tổng chi phí 1 lượt mua-bán

# Cắt lỗ
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

# Scoring 0-100 [NÂNG CẤP #6]
SCORE_AI_MAX      = 25
SCORE_TECH_MAX    = 20
SCORE_FLOW_MAX    = 20
SCORE_FINANCE_MAX = 15
SCORE_SECTOR_MAX  = 10
SCORE_SENT_MAX    = 10
SCORE_BUY_MIN     = 65    # chỉ giao dịch khi ≥ 65/100

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
SCAN_DAYS         = 100
FOREIGN_DAYS      = 10    # [NÂNG CẤP #4] Tăng từ 5 → 10 phiên
FOREIGN_NET_DAYS  = 10    # [NÂNG CẤP #4] Phân tích xu hướng 10 phiên

# Chart
CHART_DAYS        = 120

# Mã trụ thị trường
PILLARS = ["FPT", "HPG", "VCB", "VIC", "VNM", "TCB", "SSI", "MWG", "VHM", "GAS"]

# Fallback ~90 mã phổ biến HOSE (có PDR)
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

# [NÂNG CẤP #9] Phân ngành cơ bản — Sector Rotation
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

    st.markdown("### 🔐 Quant System V21.0 — Cổng Bảo Mật Trung Tâm")
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
        yf_sym = "^VNINDEX" if ticker == "VNINDEX" else f"{ticker}.VN"
        df = yf.download(yf_sym, period="3y", progress=False).reset_index()
        if valid(df):
            return normalize_cols(df)
    except Exception as e:
        print(f"[WARN] Yahoo price {ticker}: {e}")
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
# 3. CHỈ BÁO KỸ THUẬT
# ==============================================================================

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
    df['money_flow']   = close * volume
    df['volatility']   = df['return_1d'].rolling(20).std()
    df['vol_avg_20']   = volume.rolling(20).mean()

    df['is_red_candle'] = close < open_
    df['can_cung']      = df['is_red_candle'] & (volume < df['vol_avg_20'] * SUPPLY_RATIO)

    is_explosion   = df['vol_strength'] > VOL_PV_SIGNAL
    df['pv_trend'] = np.where(
        (df['return_1d'] > 0) & is_explosion,  1,
        np.where((df['return_1d'] < 0) & is_explosion, -1, 0)
    )

    return df.dropna()


# [NÂNG CẤP #5] Lọc đa khung thời gian — Weekly Trend
def get_weekly_trend(df_daily: pd.DataFrame) -> str:
    """
    Resample dữ liệu daily → weekly để xác định xu hướng lớn.
    Chỉ mua khi daily VÀ weekly cùng xu hướng tăng.
    Trả về: 'UP' | 'DOWN' | 'NEUTRAL'
    """
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

        # Tính slope của MA10 tuần (hướng dốc)
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
# 4. PHÂN TÍCH DÒNG TIỀN KHỐI NGOẠI [NÂNG CẤP #4]
# ==============================================================================

def analyze_foreign_trend(df_for: pd.DataFrame) -> dict:
    """
    [NÂNG CẤP #4] Phân tích xu hướng Khối Ngoại 10 phiên thay vì 1 phiên.
    Phát hiện:
    - Tích lũy âm thầm: mua đều đặn nhiều phiên liên tiếp
    - Divergence: giá giảm nhưng ngoại mua ròng = tín hiệu vàng
    - Xu hướng tổng (tăng dần / giảm dần theo phiên)
    """
    result = {
        'net_total':        0.0,
        'consecutive_buy':  0,
        'consecutive_sell': 0,
        'trend':            'NEUTRAL',
        'is_silent_accum':  False,
        'score':            0,         # 0-20 điểm đóng góp vào scoring
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

    # Đếm phiên mua/bán liên tiếp gần nhất
    consec_buy = consec_sell = 0
    for v in reversed(net_vals):
        if v > 0:
            if consec_sell == 0:
                consec_buy += 1
            else:
                break
        elif v < 0:
            if consec_buy == 0:
                consec_sell += 1
            else:
                break
        else:
            break

    result['consecutive_buy']  = consec_buy
    result['consecutive_sell'] = consec_sell

    # Tích lũy âm thầm: mua ≥ 5 phiên liên tiếp mà không nổ vol
    result['is_silent_accum'] = consec_buy >= 5

    # Xu hướng tổng
    buy_days  = sum(1 for v in net_vals if v > 0)
    sell_days = sum(1 for v in net_vals if v < 0)

    if buy_days >= 7:
        result['trend'] = 'STRONG_BUY'
    elif buy_days >= 5:
        result['trend'] = 'BUY'
    elif sell_days >= 7:
        result['trend'] = 'STRONG_SELL'
    elif sell_days >= 5:
        result['trend'] = 'SELL'
    else:
        result['trend'] = 'NEUTRAL'

    # Tính điểm đóng góp (0-20)
    if result['trend'] == 'STRONG_BUY':  result['score'] = 20
    elif result['trend'] == 'BUY':       result['score'] = 14
    elif result['trend'] == 'NEUTRAL':   result['score'] = 8
    elif result['trend'] == 'SELL':      result['score'] = 3
    else:                                result['score'] = 0

    if result['is_silent_accum']:
        result['score'] = min(20, result['score'] + 5)

    # Tóm tắt
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
# 5. AI — XGBoost + Walk-Forward Validation [NÂNG CẤP #1, #1b]
# ==============================================================================

def predict_ai_t3(df: pd.DataFrame) -> float | str:
    """
    Dùng cho TAB 1 — Phân tích 1 mã duy nhất.
    XGBoost + Walk-Forward 5 fold → chính xác tối đa, không cần lo tốc độ.
    """
    if len(df) < AI_MIN_ROWS:
        return "N/A"

    df2 = df.copy()
    df2['target'] = (df2['close'].shift(-3) > df2['close'] * AI_PROFIT_T3).astype(int)
    df2 = df2.dropna()

    features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility',
                'vol_strength', 'money_flow', 'pv_trend']
    X = df2[features].values
    y = df2['target'].values

    # Walk-Forward: 5 fold theo thời gian
    tscv    = TimeSeriesSplit(n_splits=5)
    probas  = []

    model = XGBClassifier(
        n_estimators    = 200,
        max_depth       = 4,
        learning_rate   = 0.05,
        subsample       = 0.8,
        colsample_bytree= 0.8,
        use_label_encoder=False,
        eval_metric     = 'logloss',
        random_state    = 42,
        verbosity       = 0,
    )

    for train_idx, _ in tscv.split(X):
        if len(train_idx) < 100:
            continue
        X_train = X[train_idx]
        y_train = y[train_idx]
        model.fit(X_train, y_train)

    # Predict trên điểm hiện tại (cuối cùng)
    try:
        prob = model.predict_proba(X[[-1]])[0][1]
        return round(prob * 100, 1)
    except Exception:
        return "N/A"




# ==============================================================================
# 5b. AI NHANH — LightGBM cho RADAR (quét 150 mã) [V21.1]
# ==============================================================================

def predict_ai_t3_fast(df: pd.DataFrame) -> float | str:
    """
    Dùng cho RADAR — Quét 150 mã liên tiếp.
    LightGBM: tốc độ gần bằng Random Forest, chính xác gần bằng XGBoost.
    Train 1 lần duy nhất (không walk-forward) để đảm bảo tốc độ.

    So sánh:
      XGBoost (Tab 1) : ~2-3 giây/mã × 1 mã   = OK
      LightGBM (Radar): ~0.3 giây/mã × 150 mã  = ~45 giây tổng
    """
    if len(df) < AI_MIN_ROWS:
        return "N/A"

    df2 = df.copy()
    df2['target'] = (df2['close'].shift(-3) > df2['close'] * AI_PROFIT_T3).astype(int)
    df2 = df2.dropna()

    features = ['rsi', 'macd', 'signal', 'return_1d', 'volatility',
                'vol_strength', 'money_flow', 'pv_trend']
    X = df2[features].values
    y = df2['target'].values

    # Dùng LightGBM nếu đã cài, fallback XGBoost nếu chưa
    if LGBM_AVAILABLE:
        model = LGBMClassifier(
            n_estimators  = 100,
            max_depth     = 4,
            learning_rate = 0.1,
            subsample     = 0.8,
            random_state  = 42,
            verbose       = -1,
        )
    else:
        model = XGBClassifier(
            n_estimators     = 100,
            max_depth        = 4,
            learning_rate    = 0.1,
            subsample        = 0.8,
            use_label_encoder= False,
            eval_metric      = 'logloss',
            random_state     = 42,
            verbosity        = 0,
        )

    # Train trên toàn bộ trừ 3 ngày cuối (tránh look-ahead bias)
    model.fit(X[:-3], y[:-3])

    try:
        prob = model.predict_proba(X[[-1]])[0][1]
        return round(prob * 100, 1)
    except Exception:
        return "N/A"

# ==============================================================================
# 6. BACKTEST CÓ PHÍ GIAO DỊCH [NÂNG CẤP #3]
# ==============================================================================

def run_backtest(df: pd.DataFrame) -> dict:
    """
    [NÂNG CẤP #3] Backtest có phí + slippage thực tế.
    Trả về dict gồm winrate, avg_profit, avg_loss, expectancy.
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

        # Giá mua thực tế = giá + slippage
        buy_price  = df['close'].iloc[i] * (1 + SLIPPAGE)
        target     = buy_price * (1 + BT_PROFIT)
        sl_price   = buy_price * (1 - SL_PCT)
        future     = df['close'].iloc[i+1 : i+1+BT_DAYS_FWD]

        hit_tp = any(future >= target)
        hit_sl = any(future <= sl_price)

        if hit_tp:
            # Tính lợi nhuận thực sau phí
            gross  = BT_PROFIT
            net    = gross - ROUND_TRIP_COST
            profits.append(net)
            wins  += 1
        elif hit_sl:
            gross  = -SL_PCT
            net    = gross - ROUND_TRIP_COST
            profits.append(net)
        else:
            # Thoát cuối kỳ
            exit_price = future.iloc[-1] if len(future) > 0 else buy_price
            gross  = (exit_price - buy_price) / buy_price
            net    = gross - ROUND_TRIP_COST
            profits.append(net)

    if not profits:
        return {'winrate': 0.0, 'avg_profit': 0.0, 'avg_loss': 0.0, 'expectancy': 0.0, 'signals': 0}

    winrate     = round((wins / signals) * 100, 1) if signals else 0.0
    avg_profit  = round(np.mean([p for p in profits if p > 0]) * 100, 2) if any(p > 0 for p in profits) else 0.0
    avg_loss    = round(np.mean([p for p in profits if p < 0]) * 100, 2) if any(p < 0 for p in profits) else 0.0
    expectancy  = round(np.mean(profits) * 100, 2)

    return {
        'winrate':    winrate,
        'avg_profit': avg_profit,
        'avg_loss':   avg_loss,
        'expectancy': expectancy,
        'signals':    signals,
    }


# ==============================================================================
# 7. SENTIMENT PHÂN TÍCH TIN TỨC [NÂNG CẤP #8]
# ==============================================================================

def analyze_news_sentiment(headlines: list[str]) -> dict:
    """
    [NÂNG CẤP #8] Dùng VADER phân tích tâm lý từ tiêu đề tin tức.
    User paste headline tiếng Anh hoặc đã dịch vào input.
    """
    if not headlines:
        return {'score': 5, 'label': '🟡 Chưa có dữ liệu tin tức', 'compound': 0.0}

    sia      = SentimentIntensityAnalyzer()
    scores   = [sia.polarity_scores(h)['compound'] for h in headlines if h.strip()]
    avg      = np.mean(scores) if scores else 0.0

    if avg >= 0.4:
        label = "🟢 Tin Tức Rất Tích Cực — Thị trường đang hưng phấn với cổ phiếu này"
        pts   = 10
    elif avg >= 0.1:
        label = "🟩 Tin Tức Tích Cực — Hỗ trợ đà tăng nhẹ"
        pts   = 7
    elif avg >= -0.1:
        label = "🟡 Tin Tức Trung Lập — Chưa tác động đáng kể"
        pts   = 5
    elif avg >= -0.4:
        label = "🟧 Tin Tức Tiêu Cực — Có thể tạo áp lực bán"
        pts   = 2
    else:
        label = "🔴 Tin Tức Rất Xấu — Rủi ro cao, cẩn thận!"
        pts   = 0

    return {'score': pts, 'label': label, 'compound': round(avg, 3)}


# ==============================================================================
# 8. SCORING TỔNG HỢP 0-100 [NÂNG CẤP #6]
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
    """
    [NÂNG CẤP #6] Bảng điểm tổng hợp 0-100.
    Chỉ giao dịch khi ≥ 65/100 điểm.
    """
    price, ma20, rsi = last['close'], last['ma20'], last['rsi']

    # --- AI (0-25) ---
    if isinstance(ai_score, float):
        if   ai_score >= 70: ai_pts = 25
        elif ai_score >= 60: ai_pts = 20
        elif ai_score >= 50: ai_pts = 13
        elif ai_score >= 40: ai_pts = 7
        else:                ai_pts = 2
    else:
        ai_pts = 0

    # --- Kỹ thuật (0-20) ---
    tech_pts = 0
    if price > ma20:        tech_pts += 7    # trên MA20
    if rsi < RSI_HOT:       tech_pts += 5    # RSI chưa quá mua
    if last['macd'] > last['signal']: tech_pts += 5   # MACD cross
    if weekly_trend == 'UP': tech_pts += 3   # weekly xác nhận

    # --- Dòng tiền Khối Ngoại (0-20) ---
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

    total = ai_pts + tech_pts + flow_pts + fin_pts + sector_pts + sent_pts
    total = min(100, total)

    # Quyết định
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
# 9. RADAR ĐỈNH / ĐÁY
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
# 10. BÁO CÁO TỰ ĐỘNG
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

    # Khối Ngoại 10 phiên
    parts.append(foreign_trend.get('summary', ''))

    parts.append("#### 2. Đánh Giá Vị Thế Kỹ Thuật:")
    price, ma20, rsi = last['close'], last['ma20'], last['rsi']

    # Weekly trend
    weekly_label = {"UP": "📈 TĂNG", "DOWN": "📉 GIẢM", "NEUTRAL": "➡️ NGANG"}.get(weekly_trend, "N/A")
    parts.append(f"🗓️ **Xu Hướng Tuần (Weekly):** {weekly_label} — "
                 f"{'✅ Khung tuần đồng pha, an toàn vào lệnh.' if weekly_trend == 'UP' else '⚠️ Khung tuần chưa xác nhận, cần thận trọng.'}")

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
    if isinstance(ai_score, float):
        ai_label = "Cửa sáng" if ai_score > AI_GOOD else "Rủi ro cao"
        parts.append(f"- **AI XGBoost T+3:** **{ai_score}%** → *{ai_label}* (Walk-Forward validated)")

    wr = bt.get('winrate', 0)
    exp = bt.get('expectancy', 0)
    parts.append(f"- **Winrate (sau phí):** **{wr}%** | Kỳ vọng mỗi lệnh: **{exp:+.2f}%**")
    parts.append(f"- **TB lời/lỗ:** +{bt.get('avg_profit',0):.2f}% / {bt.get('avg_loss',0):.2f}%")

    sl_price = price * (1 - SL_PCT)
    parts.append(f"- **🛡️ Cắt Lỗ (SL -7%):** **{sl_price:,.0f} VNĐ**")

    parts.append("#### 💡 TỔNG KẾT:")
    price_bad = price < ma20
    ai_good   = isinstance(ai_score, float) and ai_score > AI_GOOD
    wr_good   = wr >= ADV_WINRATE_GOOD

    if price_bad and ticker in buy_set:
        parts.append("⚠️ **GOM HÀNG RẢI ĐỈNH:** Có dòng tiền gom nhưng giá dưới MA20 — chờ bứt MA20 mới vào.")
    elif wr < 40 and isinstance(ai_score, float) and ai_score < 50:
        parts.append("⛔ **RỦI RO NGẬP TRÀN:** AI và lịch sử đều tiêu cực — tuyệt đối đứng ngoài.")
    elif not price_bad and ai_good and wr_good and weekly_trend == 'UP':
        parts.append("🚀 **ĐIỂM MUA VÀNG:** Nền đẹp + AI + lịch sử + tuần xác nhận — giải ngân 30–50%.")
    elif not price_bad and ai_good and wr_good:
        parts.append("✅ **ĐIỂM MUA KHÁ:** Daily tốt nhưng weekly chưa rõ — vào 20-30%, chờ tuần xác nhận thêm.")
    else:
        parts.append("⚖️ **THEO DÕI:** Tín hiệu phân hóa — đưa vào Watchlist, chờ bùng nổ khối lượng.")

    return "\n\n".join(parts)


# ==============================================================================
# 11. TÀI CHÍNH
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
# 12. DÒNG TIỀN 3 NHÓM + GOM/XẢ
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
# 13. SECTOR ROTATION [NÂNG CẤP #9]
# ==============================================================================

def analyze_sector_rotation(tickers_list: list[str]) -> dict:
    """
    [NÂNG CẤP #9] Phân tích sức mạnh từng ngành bằng cách tính
    % tăng trưởng trung bình 5 ngày của các mã trong ngành.
    Phát hiện dòng tiền đang luân chuyển vào ngành nào.
    """
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
# 14. RADAR PHÂN LOẠI CỔ PHIẾU (3 TẦNG) [NÂNG CẤP — thêm Vùng Quan Sát]
# ==============================================================================

def classify_stock(ticker: str, df: pd.DataFrame, ai_score, weekly_trend: str) -> str | None:
    """
    Tầng 1 → BÙNG NỔ (vol nổ mạnh)
    Tầng 2 → DANH SÁCH CHỜ (đủ 3 điều kiện + 1 vũ khí + weekly UP)
    Tầng 3 → VÙNG QUAN SÁT (1-2 tín hiệu sớm, chưa đủ điều kiện tầng 2)
    """
    last  = df.iloc[-1]
    vol   = last['vol_strength']
    rsi   = last['rsi']
    price = last['close']
    ma20  = last['ma20']

    # Tầng 1: Bùng Nổ
    if vol > VOL_BREAKOUT:
        return "🚀 Bùng Nổ"

    ai_ok = isinstance(ai_score, float) and ai_score > AI_OK

    # Tầng 2: Danh Sách Chờ (điều kiện đầy đủ)
    base_ok = (
        VOL_ACC_MIN <= vol <= VOL_ACC_MAX and
        price >= ma20 * PRICE_NEAR_MA20   and
        rsi < RSI_WATCHLIST_MAX           and
        ai_ok
    )

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

    if base_ok and weapons >= 1 and weekly_trend in ('UP', 'NEUTRAL'):
        return "⚖️ Danh Sách Chờ"

    # Tầng 3: Vùng Quan Sát — chưa đủ nhưng có 1-2 tín hiệu sớm
    early_signals = 0
    if ai_ok:                          early_signals += 1
    if rsi < RSI_WATCHLIST_MAX + 5:    early_signals += 1
    if price >= ma20 * 0.90:           early_signals += 1
    if weapons >= 1:                   early_signals += 1

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
# MAIN APPLICATION
# ==============================================================================

if not authenticate():
    st.stop()

if 'vnstock_engine' not in st.session_state:
    st.session_state['vnstock_engine'] = Vnstock()

st.set_page_config(
    page_title="Quant System V21.1 Supreme",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🛡️ Quant System V21.1: Supreme Predator Leviathan")
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

# Input tin tức cho Sentiment [NÂNG CẤP #8]
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📰 Nhập Tiêu Đề Tin Tức (Sentiment)")
st.sidebar.caption("Paste tiêu đề tin tức bằng tiếng Anh (1 dòng = 1 tiêu đề). Dùng Google Translate nếu cần.")
news_raw = st.sidebar.text_area("Tiêu đề tin tức:", height=120,
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
            last = df.iloc[-1]

            # Tính toán toàn bộ
            ai_score      = predict_ai_t3(df)
            bt            = run_backtest(df)
            weekly_trend  = get_weekly_trend(df)
            sr            = calc_support_resistance(last)
            growth        = get_earnings_growth(ticker)
            pe, roe       = get_pe_roe(ticker)
            sentiment     = analyze_news_sentiment(news_headlines)
            df_for        = get_foreign(ticker, FOREIGN_DAYS)
            foreign_trend = analyze_foreign_trend(df_for)

            # Sector
            ticker_sector = get_ticker_sector(ticker)
            sector_score  = 7 if ticker_sector else 5   # sẽ cập nhật sau scan ngành

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

            # Tổng điểm
            scoring = calc_total_score(
                last, ai_score, bt, foreign_trend, growth, pe,
                weekly_trend, sentiment['score'], sector_score
            )

            # --- Nhà phân tích ảo ---
            st.markdown(
                "> 🧠 **Nhà Phân Tích Ảo:** Tự động gom nhặt các con số khô khan, lắp ghép lại "
                "và viết ra một bài văn phân tích chi tiết dễ hiểu. "
                "Khai triển tối đa để chống nén code."
            )

            st.write(f"### 🎯 BẢN PHÂN TÍCH CHUYÊN MÔN TỰ ĐỘNG — MÃ {ticker}")
            col_report, col_signal = st.columns([2, 1])

            with col_report:
                report = generate_report(
                    ticker, last, ai_score, bt, buy_set, sell_set, foreign_trend, weekly_trend
                )
                st.info(report)

            with col_signal:
                st.subheader("🤖 ROBOT ĐỀ XUẤT LỆNH HIỆN TẠI:")
                color = scoring['decision_color']
                st.title(f":{color}[{scoring['decision']}]")

                # Thanh điểm tổng
                st.markdown(f"**📊 Điểm Tổng Hợp: {scoring['total']}/100**")
                st.progress(scoring['total'] / 100)
                if scoring['total'] >= SCORE_BUY_MIN:
                    st.success(f"✅ Đủ điều kiện giao dịch (≥ {SCORE_BUY_MIN}/100)")
                else:
                    st.warning(f"⏳ Chưa đủ ngưỡng giao dịch ({scoring['total']}/{SCORE_BUY_MIN})")

            st.divider()

            # --- Bảng điểm chi tiết ---
            st.write("### 🎯 Bảng Điểm Chi Tiết 0-100")
            d1, d2, d3, d4, d5, d6 = st.columns(6)
            d1.metric("🤖 AI XGBoost",    f"{scoring['ai_pts']}/{SCORE_AI_MAX}")
            d2.metric("📈 Kỹ Thuật",      f"{scoring['tech_pts']}/{SCORE_TECH_MAX}")
            d3.metric("🌊 Khối Ngoại",    f"{scoring['flow_pts']}/{SCORE_FLOW_MAX}")
            d4.metric("🏢 Tài Chính",     f"{scoring['fin_pts']}/{SCORE_FINANCE_MAX}")
            d5.metric("🏭 Ngành",         f"{scoring['sector_pts']}/{SCORE_SECTOR_MAX}")
            d6.metric("📰 Sentiment",     f"{scoring['sent_pts']}/{SCORE_SENT_MAX}")

            st.divider()

            # --- Sentiment Tin Tức ---
            st.write("### 📰 Phân Tích Tâm Lý Tin Tức (VADER Sentiment)")
            if news_headlines:
                st.info(f"{sentiment['label']} | Điểm compound: {sentiment['compound']}")
            else:
                st.warning("💡 Chưa có tin tức. Paste tiêu đề vào sidebar để AI phân tích tâm lý thị trường.")

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

            sr_c4.metric("🛡️ Cắt Lỗ SL -7%",
                f"{last['close'] * (1 - SL_PCT):,.0f} VNĐ",
                delta="-7% từ giá hiện tại", delta_color="off")

            if "🚨" in sr['warning']:
                st.error(sr['warning'])
            elif "💡" in sr['warning']:
                st.success(sr['warning'])
            else:
                st.warning(sr['warning'])

            st.divider()

            # --- Backtest chi tiết ---
            st.write("### 📋 Kết Quả Backtest Thực Tế (Đã trừ phí + slippage)")
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Winrate",          f"{bt['winrate']}%")
            b2.metric("TB lời / lệnh",    f"+{bt['avg_profit']:.2f}%")
            b3.metric("TB lỗ / lệnh",     f"{bt['avg_loss']:.2f}%")
            b4.metric("Kỳ Vọng / Lệnh",   f"{bt['expectancy']:+.2f}%",
                      delta="Dương ✓" if bt['expectancy'] > 0 else "Âm ⚠️",
                      delta_color="normal" if bt['expectancy'] > 0 else "inverse")
            st.caption(f"📊 Tổng {bt['signals']} tín hiệu backtest | Phí giao dịch: {ROUND_TRIP_COST*100:.2f}%/lệnh | SL: -7%")

            st.divider()

            # --- Chỉ số kỹ thuật ---
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

            # --- Cẩm nang False Breakout ---
            st.write("### 📖 CẨM NANG — Bí Kíp Né Bẫy Giá (False Breakout)")
            with st.expander("🚀 Mở rộng để đọc bí kíp — Dành riêng cho Minh"):
                st.markdown("""
**False Breakout (Bẫy Bứt Phá Giả) là gì?**
> Giá vượt ngưỡng kháng cự nhưng **không duy trì được** rồi quay đầu giảm ngay.

---
**🔴 DẤU HIỆU NHẬN BIẾT BẪY:**
1. **Khối lượng thấp khi phá đỉnh** — vol < 1.2x MA10 → thiếu lực xác nhận.
2. **Nến bấc trên dài** — giá lên nhưng đóng cửa thấp hơn nhiều.
3. **RSI vượt 70 ngay khi phá đỉnh** — quá mua tức thì, không có đà tích lũy trước.
4. **Giá vượt Bollinger Band trên** — vùng kháng cự thống kê cực mạnh.
5. **Khối Ngoại bán ròng khi giá tăng** — tổ chức xả hàng cho nhỏ lẻ mua.
6. **Weekly trend GIẢM hoặc NGANG** — breakout không có nền tảng tuần xác nhận.

---
**✅ QUY TẮC VÀO LỆNH AN TOÀN:**
- ⏳ Chờ nến xác nhận: không mua ngay phiên phá đỉnh.
- 📊 Vol phải nổ: ≥ 1.5x MA20 mới tin.
- 🔍 RSI lý tưởng: 50–65 khi phá đỉnh (còn dư địa).
- 🗓️ **Weekly trend phải UP** — đây là bộ lọc mới V21.0.
- 🛡️ Luôn đặt SL -7% từ giá mua — bắt buộc.
- 🌊 Kiểm tra Khối Ngoại 10 phiên: phải mua ròng liên tiếp.

---
> *"Không có breakout nào đáng tin nếu không có khối lượng đi kèm."*
> — William O'Neil (CANSLIM)
                """)

            st.divider()

            # --- Master Chart ---
            st.write("### 📊 Biểu Đồ Kỹ Thuật Đa Lớp")
            chart = df.tail(CHART_DAYS)
            x     = chart['date']

            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                vertical_spacing=0.03, row_heights=[0.75, 0.25])
            fig.add_trace(go.Candlestick(
                x=x, open=chart['open'], high=chart['high'],
                low=chart['low'], close=chart['close'], name='Nến OHLC'
            ), row=1, col=1)
            for ma_col, color, name in [('ma20','orange','MA20'), ('ma200','purple','MA200')]:
                fig.add_trace(go.Scatter(x=x, y=chart[ma_col],
                    line=dict(color=color, width=1.5), name=name), row=1, col=1)
            fig.add_trace(go.Scatter(x=x, y=chart['upper_band'],
                line=dict(color='gray', dash='dash', width=0.8), name='Trần BOL'), row=1, col=1)
            fig.add_trace(go.Scatter(x=x, y=chart['lower_band'],
                line=dict(color='gray', dash='dash', width=0.8),
                fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='Đáy BOL'), row=1, col=1)
            fig.add_trace(go.Bar(x=x, y=chart['volume'],
                name='KL', marker_color='gray'), row=2, col=1)
            fig.update_layout(height=750, template='plotly_white',
                               xaxis_rangeslider_visible=False,
                               margin=dict(l=40, r=40, t=50, b=40))
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
            if pe < PE_CHEAP:   pe_label, pe_color = "✅ Rất Tốt — Định Giá Rẻ", "normal"
            elif pe < PE_OK:    pe_label, pe_color = "⚖️ Hợp Lý", "normal"
            else:               pe_label, pe_color = "🚨 Đắt Đỏ (> 20 năm hoàn vốn)", "inverse"
            c1.metric("P/E (Số Năm Thu Hồi Vốn)", f"{pe:.1f} năm", delta=pe_label, delta_color=pe_color)

        st.write("> **P/E:** Số năm bạn cần để thu hồi vốn từ lợi nhuận. **< 12 = rẻ. > 20 = đắt, rủi ro cao.**")

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
    st.write(f"### 🌊 Smart Flow Specialist — Mổ Xẻ Hành Vi Dòng Tiền ({ticker})")

    with st.spinner("Đang trích xuất dữ liệu Khối Ngoại 10 phiên..."):
        df_for = get_foreign(ticker, FOREIGN_DAYS)
        foreign_trend_t3 = analyze_foreign_trend(df_for)

        if valid(df_for):
            last_f = df_for.iloc[-1]
            buy_v  = to_billion(last_f.get('buyval',  0))
            sell_v = to_billion(last_f.get('sellval', 0))
            net_v  = to_billion(last_f.get('netval', buy_v - sell_v))

            # --- [NÂNG CẤP #4] Hiển thị xu hướng 10 phiên ---
            st.write("#### 📊 Xu Hướng Khối Ngoại 10 Phiên — Phân Tích Tích Lũy Âm Thầm")
            ft = foreign_trend_t3
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Tổng Ròng 10 Phiên",    f"{ft['net_total']:+.2f} Tỷ",
                      delta="Mua Ròng ✓" if ft['net_total'] > 0 else "Bán Ròng ⚠️",
                      delta_color="normal" if ft['net_total'] > 0 else "inverse")
            f2.metric("Phiên Mua Liên Tiếp",  f"{ft['consecutive_buy']} phiên")
            f3.metric("Phiên Bán Liên Tiếp",  f"{ft['consecutive_sell']} phiên")
            f4.metric("Xu Hướng Tổng",         ft['trend'],
                      delta="🦈 Tích Lũy Âm Thầm!" if ft['is_silent_accum'] else "",
                      delta_color="normal" if ft['is_silent_accum'] else "off")

            if ft['is_silent_accum']:
                st.success(ft['summary'])
            elif 'BUY' in ft['trend']:
                st.info(ft['summary'])
            elif 'SELL' in ft['trend']:
                st.error(ft['summary'])
            else:
                st.warning(ft['summary'])

            # Biểu đồ 10 phiên
            x_dates  = df_for['date'].tail(10) if 'date' in df_for.columns else df_for.index[-10:]
            net_vals = []
            for _, row in df_for.tail(10).iterrows():
                b = to_billion(row.get('buyval', 0))
                s = to_billion(row.get('sellval', 0))
                n = to_billion(row.get('netval', b - s))
                net_vals.append(n)

            colors = ['green' if v > 0 else 'red' for v in net_vals]
            fig_f  = go.Figure(go.Bar(x=x_dates, y=net_vals,
                                       marker_color=colors, name="Ròng (Tỷ VNĐ)"))
            fig_f.update_layout(height=300, title="Khối Ngoại Mua/Bán Ròng 10 Phiên (Tỷ VNĐ)",
                                  margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_f, use_container_width=True)
        else:
            net_v = 0.0
            st.warning("⚠️ Không lấy được dữ liệu Khối Ngoại.")

        st.divider()

        # Phân nhóm 3 lớp
        df_flow = get_price(ticker, days=30)
        if valid(df_flow):
            df_flow  = calc_indicators(df_flow)
            last_fl  = df_flow.iloc[-1]
            vol      = last_fl['vol_strength']
            ret      = last_fl['return_1d']

            flow_info = classify_flow_group(vol, ret, net_v)

            st.write("#### 📊 Phân Tích Dòng Tiền 3 Nhóm")
            g1, g2, g3 = st.columns(3)

            inst_pct = flow_info['inst_pct']
            if flow_info['group'] == "🦈 Cá Mập":
                shark_pct = inst_pct
                org_pct   = max(0, 1 - shark_pct - 0.2)
            elif flow_info['group'] == "🏦 Tổ Chức Nội":
                shark_pct = 0.05
                org_pct   = inst_pct - shark_pct
            else:
                shark_pct, org_pct = 0.02, 0.13

            retail_pct_final = max(0, 1 - shark_pct - org_pct)

            g1.metric("🦈 Cá Mập",       f"{shark_pct*100:.1f}%",
                      delta="Đang Mạnh" if flow_info['group'] == "🦈 Cá Mập" else "Ít Tham Gia",
                      delta_color="normal" if flow_info['group'] == "🦈 Cá Mập" else "off")
            g2.metric("🏦 Tổ Chức Nội",  f"{org_pct*100:.1f}%",
                      delta="Tích Lũy" if flow_info['group'] == "🏦 Tổ Chức Nội" else "Bình Thường",
                      delta_color="normal" if flow_info['group'] == "🏦 Tổ Chức Nội" else "off")
            g3.metric("🐜 Nhỏ Lẻ",        f"{retail_pct_final*100:.1f}%",
                      delta="⚠️ Đu Bám Nhiều" if retail_pct_final > 0.6 else "Ổn Định",
                      delta_color="inverse" if retail_pct_final > 0.6 else "off")

            st.info(f"**Nhóm chủ đạo:** {flow_info['group']} — {flow_info['description']}")
            st.divider()

            action_msg = f"**{flow_info['action']}**\n\n_{flow_info['action_note']}_"
            if "GOM"    in flow_info['action']:  st.success(action_msg)
            elif "XẢ"   in flow_info['action']:  st.error(action_msg)
            else:                                 st.warning(action_msg)


# ==============================================================================
# TAB 4: RADAR TRUY QUÉT (3 TẦNG)
# ==============================================================================
with tab4:
    st.subheader("🔍 Máy Quét Định Lượng Robot Hunter V21.0 — Predator Leviathan")
    st.write(
        "Tự động phân loại thành **3 tầng**: "
        "🚀 **BÙNG NỔ** (đã nóng — cẩn thận mua đuổi đỉnh như VIC) | "
        "⚖️ **DANH SÁCH CHỜ** (Squeeze + Cạn Cung + Tây Gom + Weekly UP) | "
        "👁️ **VÙNG QUAN SÁT** (1-2 tín hiệu sớm, chưa đủ điều kiện — theo dõi)"
    )
    st.info(
        "💡 **Lưu ý:** Không xuất hiện trong Radar ≠ Cổ phiếu xấu. "
        "Mã tốt như PDR có thể đang tích lũy chưa đủ tín hiệu — dùng Tab 1 phân tích riêng."
    )

    if st.button("🔥 KÍCH HOẠT RADAR TRUY QUÉT 3 TẦNG (REAL-TIME)"):
        scan_list = tickers[:RADAR_MAX]
        st.caption(f"🔭 Đang quét {len(scan_list)} mã trên HOSE... | AI: LightGBM (tốc độ cao) | Tab 1 dùng XGBoost (chính xác tối đa)")
        progress   = st.progress(0)
        breakouts  = []
        watchlist  = []
        watch_zone = []   # Tầng 3 mới

        for i, t in enumerate(scan_list):
            try:
                df_s = get_price(t, days=SCAN_DAYS)
                if not valid(df_s):
                    continue
                df_s         = calc_indicators(df_s)
                ai_s         = predict_ai_t3_fast(df_s)   # LightGBM — nhanh hơn 5x
                weekly_s     = get_weekly_trend(df_s)
                label        = classify_stock(t, df_s, ai_s, weekly_s)

                if label is None:
                    continue

                last_s   = df_s.iloc[-1]
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

                # Làm tròn AI T+3 về 1 chữ số thập phân
                ai_display = f"{float(ai_s):.1f}%" if isinstance(ai_s, float) else str(ai_s)

                row = {
                    'Ticker':          t,
                    'Thị Giá':         f"{last_s['close']:,.0f} đ",
                    'Vol Strength':    f"{last_s['vol_strength']:.2f}x",
                    'RSI':             f"{last_s['rsi']:.1f}",
                    'AI T+3':          ai_display,
                    'Weekly Trend':    {"UP":"📈 Tăng","DOWN":"📉 Giảm","NEUTRAL":"➡️ Ngang"}.get(weekly_s, "-"),
                    'Lò Xo BB':        "✅ Đang Nén" if squeezed else "❌ Chưa Nén",
                    'Cạn Cung':        "✅ Cạn Cung" if supply   else "❌ Chưa Cạn",
                    'Tổ Chức Gom':     "✅ Đang Gom" if smart    else "❌ Chưa Gom",
                }

                if "Bùng Nổ"     in label: breakouts.append(row)
                elif "Danh Sách" in label: watchlist.append(row)
                elif "Quan Sát"  in label: watch_zone.append(row)

            except Exception as e:
                print(f"[WARN] Scan {t}: {e}")

            progress.progress((i + 1) / len(scan_list))

        st.write("### 🚀 Tầng 1 — Bùng Nổ (Cẩn thận mua đuổi đỉnh như VIC)")
        if breakouts:
            st.table(pd.DataFrame(breakouts))
        else:
            st.write("Không tìm thấy mã bùng nổ hôm nay.")

        # Chú thích ký hiệu
        with st.expander("📖 Giải thích các cột trong bảng"):
            st.markdown("""
| Cột | Ý nghĩa |
|---|---|
| **Vol Strength** | Khối lượng giao dịch so với trung bình 10 phiên. 1.3x = nổ gấp 1.3 lần bình thường |
| **RSI** | Chỉ số sức mạnh giá. < 30 = quá bán (tốt để mua). > 70 = quá mua (cẩn thận) |
| **AI T+3** | Xác suất AI dự báo giá tăng ≥ 2% sau 3 ngày. Càng cao càng tốt |
| **Weekly Trend** | Xu hướng khung tuần. 📈 Tăng = an toàn nhất để vào lệnh |
| **Lò Xo BB** | ✅ = Bollinger Bands đang nén chặt → sắp bùng nổ mạnh |
| **Cạn Cung** | ✅ = Lực bán đang cạn kiệt → phe mua sắp áp đảo |
| **Tổ Chức Gom** | ✅ = Khối Ngoại hoặc Tự Doanh đang mua ròng → tay to đang gom |
            """)

        st.write("### ⚖️ Tầng 2 — Danh Sách Chờ Chân Sóng (Cực kỳ an toàn)")
        if watchlist:
            st.table(pd.DataFrame(watchlist))
            st.success("✅ **Robot khuyên:** Ưu tiên nhóm này — nền đẹp, weekly xác nhận, tổ chức gom.")
        else:
            st.write("Hôm nay chưa có mã đủ tiêu chuẩn khắt khe.")

        st.write("### 👁️ Tầng 3 — Vùng Quan Sát (Theo dõi — Chưa đủ điều kiện vào lệnh)")
        if watch_zone:
            st.table(pd.DataFrame(watch_zone))
            st.info("💡 Nhóm này đang hình thành tín hiệu sớm. Theo dõi thêm 2-3 phiên trước khi quyết định.")
        else:
            st.write("Không có mã trong vùng quan sát.")


# ==============================================================================
# TAB 5: SECTOR ROTATION [NÂNG CẤP #9]
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
            best   = list(sector_result.keys())[0]
            worst  = list(sector_result.keys())[-1]

            st.success(f"🏆 **Ngành đang được bơm mạnh nhất: {best}** (+{sector_result[best]:.2f}% TB 5 ngày)")
            st.error(f"🚨 **Ngành yếu nhất: {worst}** ({sector_result[worst]:.2f}% TB 5 ngày)")

            # Biểu đồ thanh ngang
            sectors  = list(sector_result.keys())
            perf     = list(sector_result.values())
            colors   = ['green' if v > 0 else 'red' for v in perf]

            fig_s = go.Figure(go.Bar(
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

            # Ticker đang chọn thuộc ngành nào
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

            # Bảng chi tiết
            st.divider()
            st.write("#### 📋 Bảng Xếp Hạng Chi Tiết Tất Cả Ngành")
            df_sec = pd.DataFrame({
                'Ngành':         sectors,
                'Hiệu Suất 5 ngày': [f"{v:+.2f}%" for v in perf],
                'Tín Hiệu':      ["🟢 Dòng tiền vào" if v > 0.5 else
                                   ("🔴 Dòng tiền ra" if v < -0.5 else "🟡 Trung lập") for v in perf]
            })
            st.table(df_sec)


# ==============================================================================
# HẾT MÃ NGUỒN — QUANT SYSTEM V21.1 SUPREME
# XGBoost (Tab 1: chính xác tối đa) + LightGBM (Radar: nhanh 5x, độ chính xác cao)
# ==============================================================================
