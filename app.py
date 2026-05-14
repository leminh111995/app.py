# ==============================================================================
# QUANT SYSTEM V24.0 — UPGRADE PACK
# ------------------------------------------------------------------------------
# Tác giả gốc: Minh   |   Bản nâng cấp: Claude review
# Phiên bản:   V24.0 Upgrade Pack (đính kèm cho V23 base)
#
# Mục tiêu: Sửa bug P0 + bổ sung tính năng V24 đã đề xuất.
#
# KHÔNG bao gồm (theo yêu cầu):
#   • Telegram / Email alerts
#   • Drawdown Circuit Breaker (auto pause khi N lệnh thua liên tiếp)
#
# Quy ước nhãn function:
#   • [REPLACE] — Thay thế trực tiếp hàm cùng tên trong V23
#   • [NEW]     — Thêm mới, chưa có trong V23
#   • [PATCH]   — Sửa nhẹ phần code có sẵn (xem chú thích từng hàm)
#
# Cách tích hợp gợi ý:
#   1. Copy toàn bộ file này vào dự án (cùng thư mục với V23).
#   2. Mở V23, thay từng hàm [REPLACE] bằng phiên bản tương ứng ở đây.
#   3. Thêm các hàm [NEW] vào đúng section đề xuất (xem chú thích).
#   4. Cập nhật CONSTANTS ở đầu V23 với các hằng mới ở mục #0 bên dưới.
#   5. Wire UI: xem mục #16 cho các snippet ghép vào main app.
# ==============================================================================

import os
import json
import io
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import streamlit as st
import requests
from xgboost import XGBClassifier
from sklearn.model_selection import TimeSeriesSplit

# ---- Optional dependencies (graceful degrade nếu chưa cài) -------------------
try:
    from scipy.signal import find_peaks
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

try:
    from sklearn.calibration import CalibratedClassifierCV
    HAS_CALIBRATION = True
except ImportError:
    HAS_CALIBRATION = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph as RLPar, Spacer, Image as RLImage, Table as RLTable, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


# ==============================================================================
# #0. HẰNG SỐ MỚI — Thêm vào section CONSTANTS của V23
# ==============================================================================

# ---- Market Regime Filter ----
REGIME_BREADTH_STRONG = 70   # % mã trên MA20 → STRONG_BULL
REGIME_BREADTH_OK     = 50   # % mã trên MA20 → CAUTIOUS_BULL
REGIME_BREADTH_WEAK   = 40   # % mã trên MA20 → BEAR
REGIME_ADR_STRONG     = 60   # advance-decline ratio cho STRONG_BULL
REGIME_ADR_OK         = 50   # advance-decline ratio cho CAUTIOUS_BULL

# ---- Exit Signal ----
EXIT_RSI_DANGER       = 80
EXIT_RSI_HIGH         = 75
EXIT_VOL_DISTRIBUTION = 2.0    # vol_strength threshold cho distribution day
EXIT_SCORE_EXIT_ALL   = 7      # tổng red flags score → THOÁT TOÀN BỘ
EXIT_SCORE_TRIM       = 4      # tổng red flags score → CHỐT 50%
EXIT_SCORE_WATCH      = 2      # tổng red flags score → THEO DÕI

# ---- Position Sizing (Vol Parity) ----
RISK_PER_TRADE_DEFAULT = 0.01  # 1% vốn/lệnh dollar-risk
MAX_POSITION_PCT       = 0.20  # cap 20% vốn/mã

# ---- Correlation Check ----
CORR_MAX_PAIR     = 0.7
CORR_LOOKBACK     = 60         # ngày tính correlation
CORR_FALLBACK_MAX = 0.85       # nới lỏng nếu không đủ candidate

# ---- Bayesian Winrate ----
BAYES_PRIOR_WR = 0.5           # prior 50%
BAYES_PRIOR_N  = 10            # prior 10 trades tưởng tượng

# ---- Min thresholds for reliability ----
MIN_SIGNALS_RELIABLE = 20      # số signal tối thiểu cho backtest đáng tin
MAX_DATA_DAYS_OLD    = 5       # dữ liệu cũ > 5 ngày = stale

# ---- Stage 2 (Wave Bottom + MA200) ----
WAVE_MA200_SLOPE_MIN = 0.998   # MA200 không giảm > 0.2%/5 phiên = "phẳng/lên"
WAVE_STAGE4_THRESHOLD = 0.99   # MA200 giảm > 1%/5 phiên = Stage 4 downtrend

# ---- Smart Flow Proxy (lấp foreign stub) ----
SMART_FLOW_LOOKBACK = 10
SMART_FLOW_MAX_SCORE = 20      # giữ tương đương SCORE_FLOW_MAX cũ

# ---- Watchlist persistence ----
WATCHLIST_GIST_FILENAME = 'watchlist.txt'


# ==============================================================================
# #1. CORE FIXES — Các hàm bị bug, cần thay thế nguyên hàm
# ==============================================================================

# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] calc_obv — Vectorized, nhanh hơn 50-100x
#   Vị trí cũ: ~dòng 563 (section 3. CHỈ BÁO KỸ THUẬT)
# ──────────────────────────────────────────────────────────────────────────────
def calc_obv(df: pd.DataFrame) -> pd.Series:
    """
    [V24] On-Balance Volume — vectorized.
    OBV[t] = OBV[t-1] + sign(close.diff()) × volume
    """
    sign = np.sign(df['close'].diff()).fillna(0)
    return (sign * df['volume']).cumsum()


# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] _run_xgb — Walk-forward ĐÚNG cách + Probability Calibration
#   Vị trí cũ: ~dòng 943 (section 5. AI)
# ──────────────────────────────────────────────────────────────────────────────
def _run_xgb(df: pd.DataFrame, return_explain: bool = False):
    """
    [V24] Walk-forward validation đúng cách + Calibration tự chọn.
    - Mỗi fold tạo MỚI một model (không ghi đè), thu thập OOF predictions.
    - Dùng model fold cuối (lớn nhất) để dự đoán điểm hiện tại.
    - Nếu HAS_CALIBRATION: bọc CalibratedClassifierCV để có xác suất chuẩn.

    Trả về:
      • float (% xác suất 0-100) — nếu return_explain=False
      • dict {'prob', 'cv_auc', 'top_drivers'} — nếu return_explain=True
    """
    # Cần các hằng số sau từ V23: AI_MIN_ROWS, AI_PROFIT_T3
    AI_MIN_ROWS  = globals().get('AI_MIN_ROWS', 200)
    AI_PROFIT_T3 = globals().get('AI_PROFIT_T3', 1.02)

    if len(df) < AI_MIN_ROWS:
        return ("N/A" if not return_explain
                else {'prob': "N/A", 'cv_auc': None, 'top_drivers': []})

    df2 = df.copy()
    df2['target'] = (df2['close'].shift(-3) > df2['close'] * AI_PROFIT_T3).astype(int)
    df2 = df2.dropna()

    features = [
        'rsi', 'macd', 'signal', 'return_1d', 'volatility',
        'vol_strength', 'money_flow', 'pv_trend', 'adx', 'obv_zscore',
    ]
    features = [f for f in features if f in df2.columns]
    if len(features) < 5 or len(df2) < AI_MIN_ROWS:
        return ("N/A" if not return_explain
                else {'prob': "N/A", 'cv_auc': None, 'top_drivers': []})

    X = df2[features].values
    y = df2['target'].values

    n_neg, n_pos = max(1, (y == 0).sum()), max(1, (y == 1).sum())
    spw = round(n_neg / n_pos, 2)

    def _make_base_model():
        return XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            scale_pos_weight=spw, min_child_weight=5,
            use_label_encoder=False, eval_metric='logloss',
            random_state=42, verbosity=0,
        )

    tscv = TimeSeriesSplit(n_splits=5)
    oof_true: list[int]   = []
    oof_proba: list[float] = []
    last_model = None
    last_train_idx = None

    for train_idx, val_idx in tscv.split(X):
        if len(train_idx) < 100:
            continue
        m = _make_base_model()
        try:
            m.fit(X[train_idx], y[train_idx])
            oof_proba.extend(m.predict_proba(X[val_idx])[:, 1].tolist())
            oof_true.extend(y[val_idx].tolist())
            last_model = m
            last_train_idx = train_idx
        except Exception as e:
            print(f"[WARN] _run_xgb fold: {e}")
            continue

    if last_model is None:
        return ("N/A" if not return_explain
                else {'prob': "N/A", 'cv_auc': None, 'top_drivers': []})

    # ── Tính CV AUC trên OOF ──
    cv_auc = None
    if len(oof_proba) >= 30 and len(set(oof_true)) == 2:
        try:
            from sklearn.metrics import roc_auc_score
            cv_auc = round(roc_auc_score(oof_true, oof_proba), 3)
        except Exception:
            cv_auc = None

    # ── Calibration trên fold cuối ──
    final_model = last_model
    if HAS_CALIBRATION and last_train_idx is not None and len(last_train_idx) >= 150:
        try:
            calib = CalibratedClassifierCV(
                estimator=_make_base_model(), method='isotonic', cv=3,
            )
            calib.fit(X[last_train_idx], y[last_train_idx])
            final_model = calib
        except Exception as e:
            print(f"[WARN] calibration failed, fallback raw: {e}")

    # ── Predict điểm hiện tại ──
    try:
        prob = float(final_model.predict_proba(X[[-1]])[0][1])
    except Exception:
        return ("N/A" if not return_explain
                else {'prob': "N/A", 'cv_auc': cv_auc, 'top_drivers': []})

    prob_pct = round(prob * 100, 1)

    if not return_explain:
        return prob_pct

    # ── SHAP top drivers (chỉ khi return_explain=True) ──
    top_drivers = []
    if HAS_SHAP:
        try:
            # SHAP TreeExplainer chỉ với XGBoost gốc, không qua CalibratedClassifierCV
            tree_model = last_model
            explainer = shap.TreeExplainer(tree_model)
            shap_vals = explainer.shap_values(X[[-1]])[0]
            paired = sorted(
                zip(features, shap_vals),
                key=lambda x: abs(x[1]), reverse=True,
            )[:5]
            top_drivers = [
                {
                    'feature': f,
                    'shap': round(float(s), 3),
                    'direction': '↑' if s > 0 else '↓',
                    'value': round(float(X[-1, features.index(f)]), 3),
                }
                for f, s in paired
            ]
        except Exception as e:
            print(f"[WARN] SHAP explain failed: {e}")

    return {'prob': prob_pct, 'cv_auc': cv_auc, 'top_drivers': top_drivers}


# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] predict_ai_cached — Cache theo NGÀY (không theo last_close)
#   Vị trí cũ: ~dòng 915
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def predict_ai_cached(ticker: str, date_key: str):
    """
    [V24] Cache AI prediction theo (ticker, ngày).
    Trong cùng 1 ngày sẽ giữ kết quả → tránh tốn API/CPU mỗi lần refresh.
    date_key dạng 'YYYY-MM-DD'.

    Lưu ý: caller cần tự generate date_key, ví dụ:
        date_key = datetime.now(TZ_VN).strftime('%Y-%m-%d')
        ai = predict_ai_cached(t, date_key)
    """
    # Cần get_price, valid, calc_indicators từ V23
    get_price       = globals().get('get_price')
    valid           = globals().get('valid')
    calc_indicators = globals().get('calc_indicators')
    if not all([get_price, valid, calc_indicators]):
        # Nếu chạy độc lập, return placeholder
        return "N/A"

    df = get_price(ticker)
    if not valid(df):
        return "N/A"
    df = calc_indicators(df)
    return _run_xgb(df)


def predict_ai_cached_with_explain(ticker: str, date_key: str) -> dict:
    """
    [NEW] Phiên bản trả về cả SHAP top drivers — KHÔNG cache vì SHAP nặng.
    Dùng cho tab Robot Advisor (single stock deep-dive), không cho radar scan.
    """
    get_price       = globals().get('get_price')
    valid           = globals().get('valid')
    calc_indicators = globals().get('calc_indicators')
    if not all([get_price, valid, calc_indicators]):
        return {'prob': "N/A", 'cv_auc': None, 'top_drivers': []}
    df = get_price(ticker)
    if not valid(df):
        return {'prob': "N/A", 'cv_auc': None, 'top_drivers': []}
    df = calc_indicators(df)
    return _run_xgb(df, return_explain=True)


# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] run_backtest — Sharpe annualization ĐÚNG + Bayesian winrate
#   Vị trí cũ: ~dòng 1039 (section 6. BACKTEST)
# ──────────────────────────────────────────────────────────────────────────────
def run_backtest(df: pd.DataFrame) -> dict:
    """
    [V24] Backtest với Sharpe annualize đúng (signals/year)
          + Bayesian winrate (shrink về 50% khi sample nhỏ).
    """
    # Lấy hằng số V23
    BT_RSI_BUY      = globals().get('BT_RSI_BUY', 45)
    BT_PROFIT       = globals().get('BT_PROFIT', 0.05)
    BT_DAYS_FWD     = globals().get('BT_DAYS_FWD', 10)
    SLIPPAGE        = globals().get('SLIPPAGE', 0.001)
    SL_PCT          = globals().get('SL_PCT', 0.07)
    ROUND_TRIP_COST = globals().get('ROUND_TRIP_COST', 0.005)

    wins = 0
    profits: list[float] = []
    signals_data: list[dict] = []
    n = len(df)

    for i in range(100, n - BT_DAYS_FWD):
        rsi_ok = df['rsi'].iloc[i] < BT_RSI_BUY
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
        return {'winrate': 0.0, 'winrate_bayes': 0.0,
                'avg_profit': 0.0, 'avg_loss': 0.0,
                'expectancy': 0.0, 'signals': 0,
                'sharpe': 0.0, 'max_drawdown': 0.0,
                'signals_per_year': 0,
                'profits': [], 'signals_data': []}

    # ── Winrate thô + Bayesian ──
    n_trades   = len(profits)
    winrate    = round((wins / n_trades) * 100, 1)
    winrate_bayes = bayes_winrate(wins, n_trades,
                                    prior_winrate=BAYES_PRIOR_WR,
                                    prior_n=BAYES_PRIOR_N)

    avg_profit = (round(np.mean([p for p in profits if p > 0]) * 100, 2)
                  if any(p > 0 for p in profits) else 0.0)
    avg_loss   = (round(np.mean([p for p in profits if p < 0]) * 100, 2)
                  if any(p < 0 for p in profits) else 0.0)
    expectancy = round(np.mean(profits) * 100, 2)

    # ── Sharpe annualize ĐÚNG ──
    arr = np.array(profits)
    avg_hold_days   = BT_DAYS_FWD
    rf_per_trade    = 0.045 * (avg_hold_days / 252)   # rf theo holding period
    excess          = arr - rf_per_trade

    # Signals/year thực tế từ dates
    signals_per_year = 12.0  # fallback bảo thủ
    if signals_data and 'date' in df.columns:
        try:
            first_dt = pd.to_datetime(signals_data[0]['date'])
            last_dt  = pd.to_datetime(signals_data[-1]['date'])
            years = max(0.25, (last_dt - first_dt).days / 365.25)
            signals_per_year = n_trades / years
        except Exception:
            pass

    if excess.std() < 1e-9:
        sharpe = 0.0
    else:
        sharpe = round((excess.mean() / excess.std()) * np.sqrt(signals_per_year), 2)

    # ── Max Drawdown trên equity curve ──
    equity      = np.cumprod([1 + p for p in profits])
    rolling_max = np.maximum.accumulate(equity)
    max_dd      = round(((equity - rolling_max) / rolling_max).min() * 100, 2)

    return {
        'winrate':           winrate,
        'winrate_bayes':     winrate_bayes,
        'avg_profit':        avg_profit,
        'avg_loss':          avg_loss,
        'expectancy':        expectancy,
        'signals':           n_trades,
        'sharpe':            sharpe,
        'max_drawdown':      max_dd,
        'signals_per_year':  round(signals_per_year, 1),
        'profits':           profits,
        'signals_data':      signals_data,
    }


# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] detect_divergence — Dùng scipy find_peaks tìm swing points thực
#   Vị trí cũ: ~dòng 1783 (section [V23 #18] DIVERGENCE)
# ──────────────────────────────────────────────────────────────────────────────
def detect_divergence(df: pd.DataFrame, lookback: int = None) -> dict:
    """
    [V24] Phân kỳ RSI/MACD với scipy.signal.find_peaks.
    So sánh 2 swing points gần nhất thay vì min/max thô của 2 nửa lookback.
    Giảm false positives đáng kể.
    """
    DIV_LOOKBACK = globals().get('DIV_LOOKBACK', 20)
    if lookback is None:
        lookback = DIV_LOOKBACK

    result = {
        'bullish_rsi': False, 'bearish_rsi': False,
        'bullish_macd': False, 'bearish_macd': False,
        'label': '➡️ Không có phân kỳ rõ ràng',
        'signal': 'NONE',
    }

    if len(df) < lookback or not HAS_SCIPY:
        if not HAS_SCIPY:
            result['label'] = '⚠️ Thiếu scipy — divergence không khả dụng'
        return result

    try:
        w = df.tail(lookback).reset_index(drop=True)
        close = w['close'].values
        rsi   = w['rsi'].values
        macd  = w['macd'].values

        dist   = max(3, lookback // 5)
        prom_p = (close.max() - close.min()) * 0.02 if close.max() > close.min() else 1
        prom_r = 3.0

        price_lows,  _ = find_peaks(-close, distance=dist, prominence=prom_p)
        rsi_lows,    _ = find_peaks(-rsi,   distance=dist, prominence=prom_r)
        price_highs, _ = find_peaks(close,  distance=dist, prominence=prom_p)
        rsi_highs,   _ = find_peaks(rsi,    distance=dist, prominence=prom_r)
        macd_lows,   _ = find_peaks(-macd,  distance=dist)
        macd_highs,  _ = find_peaks(macd,   distance=dist)

        # Bullish RSI: 2 đáy giá gần nhất → giá lower low, RSI higher low
        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            p1, p2 = price_lows[-2], price_lows[-1]
            r1, r2 = rsi_lows[-2],   rsi_lows[-1]
            if close[p2] < close[p1] * 0.99 and rsi[r2] > rsi[r1] + 2:
                result['bullish_rsi'] = True

        # Bearish RSI: 2 đỉnh giá gần nhất → giá higher high, RSI lower high
        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            p1, p2 = price_highs[-2], price_highs[-1]
            r1, r2 = rsi_highs[-2],   rsi_highs[-1]
            if close[p2] > close[p1] * 1.01 and rsi[r2] < rsi[r1] - 2:
                result['bearish_rsi'] = True

        # Bullish MACD
        if len(price_lows) >= 2 and len(macd_lows) >= 2:
            p1, p2 = price_lows[-2], price_lows[-1]
            m1, m2 = macd_lows[-2],  macd_lows[-1]
            if close[p2] < close[p1] * 0.99 and macd[m2] > macd[m1]:
                result['bullish_macd'] = True

        # Bearish MACD
        if len(price_highs) >= 2 and len(macd_highs) >= 2:
            p1, p2 = price_highs[-2], price_highs[-1]
            m1, m2 = macd_highs[-2],  macd_highs[-1]
            if close[p2] > close[p1] * 1.01 and macd[m2] < macd[m1]:
                result['bearish_macd'] = True

        # Tổng hợp label
        if result['bullish_rsi'] or result['bullish_macd']:
            names = [n for n, k in [('RSI', 'bullish_rsi'), ('MACD', 'bullish_macd')]
                     if result[k]]
            result['signal'] = 'BULLISH'
            result['label']  = f"📈 Phân Kỳ Dương ({'+'.join(names)}) — Động lượng phục hồi"
        elif result['bearish_rsi'] or result['bearish_macd']:
            names = [n for n, k in [('RSI', 'bearish_rsi'), ('MACD', 'bearish_macd')]
                     if result[k]]
            result['signal'] = 'BEARISH'
            result['label']  = f"📉 Phân Kỳ Âm ({'+'.join(names)}) — Động lượng suy yếu"

    except Exception as e:
        print(f"[WARN] detect_divergence: {e}")

    return result


# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] get_vnindex_cached — Weighted basket (turnover proxy float-cap)
#   Vị trí cũ: ~dòng 407 (section 2. TRUY XUẤT DỮ LIỆU)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_vnindex_cached() -> pd.DataFrame:
    """
    [V24] VN-Index proxy weighted theo turnover 60 phiên (đại diện float-cap).
    Top 15 mã vốn hoá lớn nhất HOSE → bao phủ ~70% market cap.
    """
    from vnstock import Vnstock
    DATE_FMT = globals().get('DATE_FMT', '%Y-%m-%d')

    start = (datetime.now() - timedelta(days=400)).strftime(DATE_FMT)
    end   = datetime.now().strftime(DATE_FMT)
    vci   = Vnstock().stock(symbol='ACB', source='VCI')

    # Tầng 1: thử symbol VNINDEX trực tiếp
    for sym in ['VNINDEX', 'VN30', 'E1VFVN30']:
        try:
            df = vci.quote.history(symbol=sym, start=start, end=end)
            if df is not None and not df.empty and len(df) >= 30:
                df.columns = [str(c).lower() for c in df.columns]
                return df
        except Exception:
            pass

    # Tầng 2: weighted basket
    BASKET = [
        "VCB", "VHM", "VIC", "HPG", "VNM", "GAS", "MSN", "SAB",
        "FPT", "TCB", "MWG", "BID", "CTG", "ACB", "VPB",
    ]
    price_data: dict[str, pd.Series] = {}
    turnover:   dict[str, float]     = {}

    for sym in BASKET:
        try:
            df_s = vci.quote.history(symbol=sym, start=start, end=end)
            if df_s is None or df_s.empty:
                continue
            df_s.columns = [str(c).lower() for c in df_s.columns]
            if 'close' not in df_s.columns or 'date' not in df_s.columns:
                continue
            df_s['date'] = pd.to_datetime(df_s['date']).dt.strftime('%Y-%m-%d')
            price_data[sym] = df_s.set_index('date')['close']
            recent60 = df_s.tail(60)
            turnover[sym] = float((recent60['close'] * recent60['volume']).sum())
        except Exception:
            continue

    if len(price_data) < 5:
        return pd.DataFrame()

    df_basket = pd.DataFrame(price_data).dropna(how='all').ffill()
    base = df_basket.iloc[0]
    norm = df_basket.div(base) * 1000
    weights = pd.Series(turnover).reindex(df_basket.columns).fillna(0)
    if weights.sum() <= 0:
        weights = pd.Series(1.0, index=df_basket.columns)
    weights = weights / weights.sum()
    weighted_index = (norm * weights).sum(axis=1)

    return pd.DataFrame({
        'date':   df_basket.index.tolist(),
        'open':   weighted_index.values,
        'high':   norm.max(axis=1).values,
        'low':    norm.min(axis=1).values,
        'close':  weighted_index.values,
        'volume': df_basket.sum(axis=1).values,
    }).reset_index(drop=True)


# ==============================================================================
# #2. SMART FLOW PROXY — Lấp foreign flow stub
# ==============================================================================

# ──────────────────────────────────────────────────────────────────────────────
# [NEW] smart_flow_proxy
#   Thêm vào sau section 14 DÒNG TIỀN 3 NHÓM (~dòng 1665).
#   Dùng để thay thế output của fetch_all_flows/get_foreign trong scoring.
# ──────────────────────────────────────────────────────────────────────────────
def smart_flow_proxy(df: pd.DataFrame, lookback: int = SMART_FLOW_LOOKBACK) -> dict:
    """
    [V24] Proxy 'tổ chức gom' khi không có dữ liệu khối ngoại thực tế.
    Trả về dict tương thích với foreign_trend dùng trong calc_total_score.

    Tiêu chí (20 điểm max — giữ tương đương SCORE_FLOW_MAX cũ):
      • OBV hiện tại tích cực z > 0.5     → +5
      • OBV trung bình lookback > 0       → +4
      • Vol ổn định (0.9-1.6x) ≥ 7/10 ph  → +4
      • Giá không giảm > 2%/phiên ≥ 7/10  → +4
      • Đóng trên MA20 ≥ 6/10 phiên       → +3
    """
    if len(df) < lookback + 20:
        return {
            'score': 0, 'trend': 'UNKNOWN',
            'label': '❓ Thiếu dữ liệu', 'flags': [],
        }

    recent      = df.tail(lookback)
    obv_z_now   = float(recent['obv_zscore'].iloc[-1]) if 'obv_zscore' in recent.columns else 0
    obv_z_mean  = float(recent['obv_zscore'].mean())   if 'obv_zscore' in recent.columns else 0
    vol_stable  = int(((recent['vol_strength'] >= 0.9) & (recent['vol_strength'] <= 1.6)).sum())
    price_ok    = int((recent['return_1d'] >= -0.02).sum())
    close_above = int((recent['close'] > recent['ma20']).sum())

    score = 0
    flags: list[str] = []

    if obv_z_now > 0.5:    score += 5; flags.append('OBV tích cực')
    if obv_z_mean > 0:     score += 4; flags.append('OBV xu hướng tăng')
    if vol_stable >= 7:    score += 4; flags.append('Vol ổn định')
    if price_ok >= 7:      score += 4; flags.append('Giá giữ vững')
    if close_above >= 6:   score += 3; flags.append('Trên MA20 đa số phiên')

    if   score >= 16: trend, label = 'STRONG_BUY', '🟢🟢 Có dấu hiệu gom mạnh (proxy)'
    elif score >= 11: trend, label = 'BUY',        '🟢 Có dấu hiệu gom (proxy)'
    elif score >= 6:  trend, label = 'NEUTRAL',    '⚪ Trung lập (proxy)'
    else:             trend, label = 'WEAK',       '🔴 Thiếu lực gom (proxy)'

    return {
        'score': score, 'trend': trend, 'label': label,
        'flags': flags,
        'is_proxy': True,    # đánh dấu để UI hiển thị "(proxy)"
    }


# ==============================================================================
# #3. MARKET REGIME FILTER — Bộ lọc trạng thái thị trường
# ==============================================================================

def detect_market_regime(df_vni: pd.DataFrame, breadth: dict) -> dict:
    """
    [NEW] [V24] Phát hiện trạng thái thị trường + đề xuất size lệnh.

    Returns:
        regime         — 'STRONG_BULL' | 'CAUTIOUS_BULL' | 'MIXED' | 'BEAR' | 'UNKNOWN'
        size_mult      — hệ số nhân cho position size (0.0 - 1.0)
        buy_allowed    — có cho phép mở vị thế mới không
        min_score_buy  — ngưỡng điểm tổng hợp tối thiểu để mua (động theo regime)
        label          — chuỗi hiển thị
    """
    valid = globals().get('valid', lambda x: x is not None and not x.empty)
    SCORE_BUY_MIN = globals().get('SCORE_BUY_MIN', 58)

    if not valid(df_vni) or len(df_vni) < 210:
        return {
            'regime': 'UNKNOWN', 'size_mult': 0.3, 'buy_allowed': True,
            'min_score_buy': SCORE_BUY_MIN + 5,
            'label': '❓ UNKNOWN — Thiếu dữ liệu VN-Index, mua chọn lọc',
            'above_50': False, 'above_200': False,
            'pct_ma20': 0, 'adr': 0,
        }

    vni = df_vni.copy()
    vni['ma50']  = vni['close'].rolling(50).mean()
    vni['ma200'] = vni['close'].rolling(200).mean()
    last = vni.iloc[-1]

    above_50  = bool(last['close'] > last['ma50'])
    above_200 = bool(last['close'] > last['ma200'])
    pct_ma20  = float(breadth.get('pct_above_ma20', 50))
    adr       = float(breadth.get('advance_decline', 50))

    if above_50 and above_200 and pct_ma20 >= REGIME_BREADTH_STRONG and adr >= REGIME_ADR_STRONG:
        return {
            'regime': 'STRONG_BULL', 'size_mult': 1.0, 'buy_allowed': True,
            'min_score_buy': SCORE_BUY_MIN,
            'label': '🟢 STRONG BULL — Mua tích cực',
            'above_50': above_50, 'above_200': above_200,
            'pct_ma20': pct_ma20, 'adr': adr,
        }

    if above_50 and (pct_ma20 >= REGIME_BREADTH_OK or adr >= REGIME_ADR_OK):
        return {
            'regime': 'CAUTIOUS_BULL', 'size_mult': 0.6, 'buy_allowed': True,
            'min_score_buy': SCORE_BUY_MIN + 5,
            'label': '🟡 CAUTIOUS BULL — Mua chọn lọc',
            'above_50': above_50, 'above_200': above_200,
            'pct_ma20': pct_ma20, 'adr': adr,
        }

    if (not above_50 and not above_200) and pct_ma20 < REGIME_BREADTH_WEAK:
        return {
            'regime': 'BEAR', 'size_mult': 0.0, 'buy_allowed': False,
            'min_score_buy': 999,
            'label': '🔴 BEAR — KHÔNG mở vị thế mới',
            'above_50': above_50, 'above_200': above_200,
            'pct_ma20': pct_ma20, 'adr': adr,
        }

    return {
        'regime': 'MIXED', 'size_mult': 0.3, 'buy_allowed': True,
        'min_score_buy': SCORE_BUY_MIN + 10,
        'label': '🟠 MIXED — Chỉ mã siêu mạnh (RS≥80)',
        'above_50': above_50, 'above_200': above_200,
        'pct_ma20': pct_ma20, 'adr': adr,
    }


def render_market_regime_banner(regime: dict, breadth: dict) -> None:
    """
    [NEW] Banner trạng thái thị trường — đặt đầu mỗi tab.
    """
    c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])
    with c1:
        st.markdown(f"### {regime['label']}")
        st.caption(f"VNI vs MA50: {'✅' if regime['above_50'] else '❌'} | "
                   f"vs MA200: {'✅' if regime['above_200'] else '❌'}")
    with c2:
        st.metric("% > MA20", f"{regime['pct_ma20']:.0f}%",
                  help="Tỷ lệ mã đang đóng trên MA20 — chỉ số sức khoẻ thị trường")
    with c3:
        st.metric("Adv/Decl", f"{regime['adr']:.0f}%",
                  help="Tỷ lệ mã tăng giá trong phiên")
    with c4:
        if regime['buy_allowed']:
            st.metric("Điểm BUY tối thiểu", f"{regime['min_score_buy']}/90",
                      help="Điểm tổng hợp tối thiểu để xét mua")
        else:
            st.metric("Vị thế mới", "❌ KHÔNG",
                      delta="Bảo vệ vốn",
                      delta_color="inverse")

    if not regime['buy_allowed']:
        st.error("🔴 Thị trường BEAR — Hệ thống đề nghị KHÔNG mở vị thế mới. "
                 "Tập trung quản trị rủi ro các vị thế đang có.")
    elif regime['regime'] == 'MIXED':
        st.warning("🟠 Thị trường phân hoá — chỉ vào lệnh với mã có RS Rating ≥ 80 "
                   "và điểm tổng hợp vượt ngưỡng cao hơn.")


# ==============================================================================
# #4. EXIT SIGNAL SYSTEM — Tín hiệu THOÁT độc lập
# ==============================================================================

def generate_exit_signal(
    last: pd.Series, df: pd.DataFrame,
    entry_price: float, current_price: float,
    weekly_trend: str, divergence: dict, ai_score,
) -> dict:
    """
    [NEW] [V24] Đánh giá có nên thoát không, ĐỘC LẬP với SL/TP tự động.

    Trả về:
        action     — 'HOLD' | 'WATCH' | 'TRIM_50' | 'EXIT_ALL'
        score      — tổng điểm red flag
        flags      — list lý do
        label      — chuỗi hiển thị
        color      — 'success' | 'warning' | 'error'
        pnl_pct    — % P&L hiện tại
    """
    _is_valid_score = globals().get('_is_valid_score',
                                     lambda x: isinstance(x, (int, float, np.floating))
                                     and not np.isnan(float(x)))

    red_flags: list[str] = []
    score = 0
    rsi = float(last['rsi'])
    macd, sig = float(last['macd']), float(last['signal'])
    adx = float(last.get('adx', 0))
    vol = float(last['vol_strength'])
    ret = float(last.get('return_1d', 0))

    # 1. RSI quá mua cực đoan
    if rsi >= EXIT_RSI_DANGER:
        red_flags.append(f"🔴 RSI {rsi:.1f} ≥ {EXIT_RSI_DANGER} — vùng quá mua nguy hiểm")
        score += 3
    elif rsi >= EXIT_RSI_HIGH and ret < 0:
        red_flags.append(f"🟠 RSI {rsi:.1f} cao + nến đỏ")
        score += 2

    # 2. MACD bearish cross gần đây
    if len(df) >= 2:
        macd_prev = float(df['macd'].iloc[-2])
        sig_prev  = float(df['signal'].iloc[-2])
        if macd_prev > sig_prev and macd < sig:
            red_flags.append("🔴 MACD vừa cắt xuống signal")
            score += 2

    # 3. Phân kỳ âm
    if divergence and divergence.get('signal') == 'BEARISH':
        red_flags.append("🔴 Phân kỳ âm xác nhận")
        score += 3

    # 4. Weekly trend đảo chiều
    if weekly_trend == 'DOWN':
        red_flags.append("🔴 Weekly đã đảo về DOWN")
        score += 3

    # 5. Distribution day (Vol bùng nổ + nến đỏ)
    if vol > EXIT_VOL_DISTRIBUTION and ret < -0.02:
        red_flags.append(f"🔴 Distribution day — Vol {vol:.1f}x + giảm {ret*100:.1f}%")
        score += 4

    # 6. ADX suy yếu nhanh (trend đang tan)
    if len(df) >= 5:
        adx_5d_ago = float(df['adx'].iloc[-5])
        if adx < 20 and adx_5d_ago > 30:
            red_flags.append(f"🟠 ADX suy yếu nhanh: {adx_5d_ago:.1f} → {adx:.1f}")
            score += 2

    # 7. AI score sụt mạnh
    if _is_valid_score(ai_score) and float(ai_score) < 40:
        red_flags.append(f"🔴 AI T+3 chỉ {float(ai_score):.1f}% — đảo chiều")
        score += 2

    # 8. Mất MA20 sau khi đang trên
    ma20 = float(last['ma20'])
    if len(df) >= 3 and current_price < ma20 * 0.98:
        was_above = float(df['close'].iloc[-3]) > float(df['ma20'].iloc[-3])
        if was_above:
            red_flags.append("🟠 Vừa rớt khỏi MA20")
            score += 2

    pnl_pct = (current_price - entry_price) / entry_price * 100

    if score >= EXIT_SCORE_EXIT_ALL:
        return {
            'action': 'EXIT_ALL', 'score': score, 'flags': red_flags,
            'label': f'🚨 THOÁT TOÀN BỘ — {len(red_flags)} cảnh báo nghiêm trọng',
            'color': 'error', 'pnl_pct': round(pnl_pct, 2),
        }
    if score >= EXIT_SCORE_TRIM:
        return {
            'action': 'TRIM_50', 'score': score, 'flags': red_flags,
            'label': '⚠️ CHỐT 50% — Bảo toàn lợi nhuận, dời SL về breakeven',
            'color': 'warning', 'pnl_pct': round(pnl_pct, 2),
        }
    if score >= EXIT_SCORE_WATCH:
        return {
            'action': 'WATCH', 'score': score, 'flags': red_flags,
            'label': '👁️ THEO DÕI CHẶT — Chuẩn bị tâm lý thoát',
            'color': 'warning', 'pnl_pct': round(pnl_pct, 2),
        }
    return {
        'action': 'HOLD', 'score': score,
        'flags': red_flags or ['✅ Chưa có red flag'],
        'label': '✅ TIẾP TỤC GIỮ', 'color': 'success',
        'pnl_pct': round(pnl_pct, 2),
    }


def render_exit_signal_card(exit_sig: dict, current_price: float,
                             entry_price: float, shares: int) -> None:
    """[NEW] Card hiển thị tín hiệu thoát."""
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"### {exit_sig['label']}")
            st.caption(f"Red flag score: {exit_sig['score']}")
        with c2:
            st.metric("P&L", f"{exit_sig['pnl_pct']:+.2f}%",
                      delta=f"{(current_price-entry_price)*shares:+,.0f} đ")
        with c3:
            if exit_sig['action'] == 'EXIT_ALL':
                st.error("THOÁT NGAY")
            elif exit_sig['action'] == 'TRIM_50':
                st.warning("CHỐT 50%")
            elif exit_sig['action'] == 'WATCH':
                st.warning("THEO DÕI")
            else:
                st.success("GIỮ")

        with st.expander("Chi tiết red flags", expanded=(exit_sig['score'] >= 2)):
            for f in exit_sig['flags']:
                st.write(f)


# ==============================================================================
# #5. POSITION SIZING — Volatility Parity
# ==============================================================================

def calc_position_size_vol_parity(
    capital: float,
    entry_price: float,
    atr: float,
    risk_per_trade: float = RISK_PER_TRADE_DEFAULT,
    max_size_pct: float = MAX_POSITION_PCT,
    size_mult: float = 1.0,
) -> dict:
    """
    [NEW] [V24] Position sizing theo dollar-risk constant.

    Args:
        capital         — tổng vốn (đồng)
        entry_price     — giá vào dự kiến
        atr             — ATR hiện tại
        risk_per_trade  — % vốn chấp nhận mất mỗi lệnh (mặc định 1%)
        max_size_pct    — % vốn tối đa cho 1 mã (mặc định 20%)
        size_mult       — hệ số nhân từ market regime (0.0-1.0)

    Returns:
        shares, value, size_pct, dollar_risk, risk_per_share, tp2_price, tp3_price
    """
    ATR_MULTIPLIER = globals().get('ATR_MULTIPLIER', 2.0)

    if atr <= 0 or entry_price <= 0 or capital <= 0:
        return {
            'shares': 0, 'value': 0, 'size_pct': 0,
            'dollar_risk': 0, 'risk_per_share': 0,
            'sl_price': 0, 'tp2_price': 0, 'tp3_price': 0,
            'r_multiple_tp2': 0, 'r_multiple_tp3': 0,
        }

    risk_per_share = ATR_MULTIPLIER * atr
    dollar_risk    = capital * risk_per_trade * size_mult
    shares_by_risk = dollar_risk / risk_per_share if risk_per_share > 0 else 0

    # Cap theo max position
    max_shares_by_cap = (capital * max_size_pct * size_mult) / entry_price

    raw_shares = min(shares_by_risk, max_shares_by_cap)
    # Bội số 100 (lô chẵn HOSE)
    shares = int(raw_shares // 100 * 100)
    value  = shares * entry_price
    size_pct = (value / capital * 100) if capital > 0 else 0

    sl_price  = entry_price - risk_per_share
    tp2_price = entry_price + 2 * risk_per_share   # +2R
    tp3_price = entry_price + 3 * risk_per_share   # +3R

    return {
        'shares':         shares,
        'value':          round(value, 0),
        'size_pct':       round(size_pct, 2),
        'dollar_risk':    round(dollar_risk, 0),
        'risk_per_share': round(risk_per_share, 0),
        'sl_price':       round(sl_price, 0),
        'tp2_price':      round(tp2_price, 0),
        'tp3_price':      round(tp3_price, 0),
        'r_multiple_tp2': 2.0,
        'r_multiple_tp3': 3.0,
        'size_mult_applied': size_mult,
    }


def combine_kelly_and_vol_parity(
    kelly_pct: float,
    vol_parity_result: dict,
    capital: float,
) -> dict:
    """
    [NEW] Kết hợp Half-Kelly và Vol-Parity — lấy MIN để bảo thủ.

    Kelly nói "với edge này, max bao nhiêu vốn/lệnh".
    Vol-parity nói "với volatility này, bao nhiêu vốn để dollar-risk = 1%".
    Lấy phương án nhỏ hơn = thận trọng hơn.
    """
    kelly_value     = capital * (kelly_pct / 100.0)
    parity_value    = vol_parity_result.get('value', 0)
    final_value     = min(kelly_value, parity_value)

    entry_price = (vol_parity_result.get('value', 0) /
                   max(1, vol_parity_result.get('shares', 1)))
    if entry_price <= 0:
        entry_price = 1

    final_shares = int(final_value / entry_price // 100 * 100)
    final_value  = final_shares * entry_price

    return {
        'kelly_value':    round(kelly_value, 0),
        'parity_value':   round(parity_value, 0),
        'final_value':    round(final_value, 0),
        'final_shares':   final_shares,
        'final_size_pct': round(final_value / capital * 100, 2) if capital > 0 else 0,
        'limiter':        'Kelly' if kelly_value < parity_value else 'Vol-Parity',
    }


# ==============================================================================
# #6. CORRELATION CHECK — Quick Pick đa dạng hoá
# ==============================================================================

def diversified_top_pick(
    candidates: list[dict],
    n: int = 3,
    max_corr: float = CORR_MAX_PAIR,
    days_corr: int = CORR_LOOKBACK,
) -> list[dict]:
    """
    [NEW] [V24] Chọn Top N từ candidates đảm bảo correlation thấp.
    Greedy algorithm: lấy candidate có score cao nhất trước, sau đó chỉ thêm
    candidate khác nếu correlation với mọi candidate đã chọn < max_corr.

    Args:
        candidates — list dict đã sort theo score giảm dần, mỗi dict có 'ticker'
        n          — số candidate cuối cùng muốn lấy
        max_corr   — ngưỡng correlation tối đa cho phép giữa các cặp
        days_corr  — số ngày tính correlation

    Returns: list[dict] tối đa n phần tử, ít tương quan nhau.
    """
    get_price = globals().get('get_price')
    valid     = globals().get('valid', lambda x: x is not None and not x.empty)

    if len(candidates) <= n or get_price is None:
        return candidates[:n]

    # Lấy giá đóng cửa của tất cả candidates
    price_dict: dict[str, pd.Series] = {}
    for c in candidates:
        t = c.get('ticker')
        if not t:
            continue
        try:
            df_c = get_price(t, days=days_corr + 10)
            if valid(df_c) and len(df_c) >= days_corr and 'close' in df_c.columns:
                if 'date' in df_c.columns:
                    df_c = df_c.copy()
                    df_c['date'] = pd.to_datetime(df_c['date']).dt.strftime('%Y-%m-%d')
                    price_dict[t] = df_c.set_index('date')['close'].tail(days_corr)
        except Exception:
            continue

    if len(price_dict) < n:
        return candidates[:n]

    returns_df = pd.DataFrame(price_dict).pct_change().dropna()
    if returns_df.empty or len(returns_df) < 20:
        return candidates[:n]

    corr_matrix = returns_df.corr().abs()

    # Greedy selection
    selected: list[dict] = []
    for c in candidates:
        t = c.get('ticker')
        if t not in corr_matrix.columns:
            continue
        if not selected:
            selected.append(c)
            continue
        max_pair_corr = max(
            corr_matrix.loc[t, s['ticker']]
            for s in selected
            if s.get('ticker') in corr_matrix.columns
        )
        if max_pair_corr < max_corr:
            selected.append(c)
            c['_max_corr_to_selected'] = round(float(max_pair_corr), 2)
        if len(selected) >= n:
            break

    # Fallback: nếu filter quá khắt, nới max_corr lên CORR_FALLBACK_MAX
    if len(selected) < n:
        for c in candidates:
            if c in selected:
                continue
            t = c.get('ticker')
            if t not in corr_matrix.columns:
                continue
            if not selected:
                selected.append(c)
                continue
            max_pair_corr = max(
                corr_matrix.loc[t, s['ticker']]
                for s in selected
                if s.get('ticker') in corr_matrix.columns
            )
            if max_pair_corr < CORR_FALLBACK_MAX:
                selected.append(c)
                c['_max_corr_to_selected'] = round(float(max_pair_corr), 2)
                c['_fallback'] = True
            if len(selected) >= n:
                break

    # Final fallback: vẫn chưa đủ, lấy theo score
    if len(selected) < n:
        for c in candidates:
            if c not in selected:
                selected.append(c)
            if len(selected) >= n:
                break

    return selected[:n]


# ==============================================================================
# #7. STRATEGY A/B TESTING — So sánh chiến lược
# ==============================================================================

def run_backtest_param(
    df: pd.DataFrame,
    rsi_buy: float = 45,
    profit_target: float = 0.05,
    days_fwd: int = 10,
    use_wave_filter: bool = False,
    use_macd_cross: bool = True,
    use_adx_filter: bool = False,
    adx_min: float = 20,
) -> dict:
    """
    [NEW] Backtest tham số hoá — dùng cho A/B testing strategy variants.
    Cùng cấu trúc với run_backtest nhưng cho phép override params.
    """
    SLIPPAGE        = globals().get('SLIPPAGE', 0.001)
    SL_PCT          = globals().get('SL_PCT', 0.07)
    ROUND_TRIP_COST = globals().get('ROUND_TRIP_COST', 0.005)
    WAVE_RSI_MAX    = globals().get('WAVE_RSI_MAX', 52)
    WAVE_RSI_MIN    = globals().get('WAVE_RSI_MIN', 28)

    wins = 0
    profits: list[float] = []
    signals_data: list[dict] = []
    n = len(df)

    for i in range(100, n - days_fwd):
        rsi_now  = df['rsi'].iloc[i]
        rsi_ok   = rsi_now < rsi_buy

        # MACD cross filter
        if use_macd_cross:
            macd_cross = (
                df['macd'].iloc[i]   > df['signal'].iloc[i] and
                df['macd'].iloc[i-1] <= df['signal'].iloc[i-1]
            )
        else:
            macd_cross = df['macd'].iloc[i] > df['signal'].iloc[i]

        if not (rsi_ok and macd_cross):
            continue

        # Wave filter
        if use_wave_filter:
            if not (WAVE_RSI_MIN <= rsi_now <= WAVE_RSI_MAX):
                continue
            ma20 = df['ma20'].iloc[i]
            if df['close'].iloc[i] > ma20 * 1.05:
                continue

        # ADX filter
        if use_adx_filter and 'adx' in df.columns:
            if df['adx'].iloc[i] < adx_min:
                continue

        buy_price = df['close'].iloc[i] * (1 + SLIPPAGE)
        target    = buy_price * (1 + profit_target)
        sl_price  = buy_price * (1 - SL_PCT)
        future    = df['close'].iloc[i+1 : i+1+days_fwd]
        hit_tp    = any(future >= target)
        hit_sl    = any(future <= sl_price)
        date_i    = df['date'].iloc[i] if 'date' in df.columns else i

        if hit_tp:
            p = profit_target - ROUND_TRIP_COST
            profits.append(p); wins += 1
            signals_data.append({'date': date_i, 'result': 'WIN',  'pnl': p})
        elif hit_sl:
            p = -SL_PCT - ROUND_TRIP_COST
            profits.append(p)
            signals_data.append({'date': date_i, 'result': 'LOSS', 'pnl': p})
        else:
            exit_price = future.iloc[-1] if len(future) > 0 else buy_price
            p = (exit_price - buy_price) / buy_price - ROUND_TRIP_COST
            profits.append(p)
            signals_data.append({'date': date_i, 'result': 'HOLD', 'pnl': p})

    if not profits:
        return {'winrate': 0.0, 'expectancy': 0.0, 'sharpe': 0.0,
                'max_drawdown': 0.0, 'signals': 0,
                'profits': [], 'signals_data': []}

    n_trades = len(profits)
    winrate  = round((wins / n_trades) * 100, 1)

    arr           = np.array(profits)
    rf_per_trade  = 0.045 * (days_fwd / 252)
    excess        = arr - rf_per_trade

    signals_per_year = 12.0
    if signals_data and 'date' in df.columns:
        try:
            first_dt = pd.to_datetime(signals_data[0]['date'])
            last_dt  = pd.to_datetime(signals_data[-1]['date'])
            years = max(0.25, (last_dt - first_dt).days / 365.25)
            signals_per_year = n_trades / years
        except Exception:
            pass

    sharpe = (round((excess.mean() / excess.std()) * np.sqrt(signals_per_year), 2)
              if excess.std() > 1e-9 else 0.0)

    equity = np.cumprod([1 + p for p in profits])
    rolling_max = np.maximum.accumulate(equity)
    max_dd = round(((equity - rolling_max) / rolling_max).min() * 100, 2)

    expectancy = round(np.mean(profits) * 100, 2)

    return {
        'winrate':           winrate,
        'expectancy':        expectancy,
        'sharpe':            sharpe,
        'max_drawdown':      max_dd,
        'signals':           n_trades,
        'signals_per_year':  round(signals_per_year, 1),
        'profits':           profits,
        'signals_data':      signals_data,
    }


def compare_strategies(df: pd.DataFrame, strategies: dict) -> pd.DataFrame:
    """
    [NEW] So sánh nhiều variant strategy trên cùng dữ liệu.

    Args:
        df         — DataFrame đã có indicators
        strategies — dict {strategy_name: {kwargs for run_backtest_param}}
                     ví dụ:
                     {
                         'baseline':   {'rsi_buy': 45},
                         'with_wave':  {'rsi_buy': 45, 'use_wave_filter': True},
                         'with_adx':   {'rsi_buy': 45, 'use_adx_filter': True},
                     }

    Returns: DataFrame so sánh các metric chính.
    """
    rows: list[dict] = []
    equity_curves: dict[str, list[float]] = {}

    for name, params in strategies.items():
        try:
            bt = run_backtest_param(df, **params)
            rows.append({
                'Strategy':    name,
                'Signals':     bt['signals'],
                'Winrate (%)': bt['winrate'],
                'Expectancy (%)': bt['expectancy'],
                'Sharpe':      bt['sharpe'],
                'Max DD (%)':  bt['max_drawdown'],
                'Sigs/Year':   bt.get('signals_per_year', 0),
            })
            if bt['profits']:
                equity = np.cumprod([1 + p for p in bt['profits']]).tolist()
                equity_curves[name] = equity
        except Exception as e:
            rows.append({
                'Strategy':    name,
                'Signals':     0,
                'Winrate (%)': 0.0,
                'Expectancy (%)': 0.0,
                'Sharpe':      0.0,
                'Max DD (%)':  0.0,
                'Sigs/Year':   0,
                'Error':       str(e)[:50],
            })

    df_out = pd.DataFrame(rows)
    df_out.attrs['equity_curves'] = equity_curves
    return df_out


# ==============================================================================
# #8. REFINEMENTS — Tinh chỉnh các tính năng hiện có
# ==============================================================================

# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] calc_wave_bottom_score — Thêm tiêu chí #12: Stage 2 (MA200)
#   Vị trí cũ: ~dòng 2175
# ──────────────────────────────────────────────────────────────────────────────
def calc_wave_bottom_score(
    df: pd.DataFrame,
    last: pd.Series,
    smart_flow: bool = False,
    near_52w_high: bool = False,
    div_bullish: bool = False,
) -> dict:
    """
    [V24] Hệ thống 12 tiêu chí chân sóng (thêm MA200 Stage 2 filter).
    Cần ≥ WAVE_SCORE_MIN điểm = chân sóng hợp lệ.
    """
    WAVE_RSI_MAX    = globals().get('WAVE_RSI_MAX', 52)
    WAVE_RSI_MIN    = globals().get('WAVE_RSI_MIN', 28)
    WAVE_PRICE_MA50 = globals().get('WAVE_PRICE_MA50', 0.88)
    WAVE_SCORE_MIN  = globals().get('WAVE_SCORE_MIN', 4)

    score  = 0
    flags: list[str] = []
    price  = float(last['close'])
    ma20   = float(last['ma20'])
    ma50   = float(last.get('ma50', ma20))
    ma200  = float(last.get('ma200', np.nan))
    rsi    = float(last['rsi'])
    bb_low = float(last['lower_band'])
    bb_wid = float(last['bb_width'])
    adx    = float(last.get('adx', 0))
    obv_z  = float(last.get('obv_zscore', 0))

    # ── HARD DISQUALIFIERS ──
    if rsi > WAVE_RSI_MAX:
        return {'score': 0, 'total': 12, 'flags': [], 'is_wave_bottom': False,
                'label': f'❌ RSI {rsi:.1f} quá cao — đã bứt tốc'}
    if rsi < WAVE_RSI_MIN:
        return {'score': 0, 'total': 12, 'flags': [], 'is_wave_bottom': False,
                'label': f'❌ RSI {rsi:.1f} quá thấp — downtrend mạnh'}
    if price > ma20 * 1.05:
        return {'score': 0, 'total': 12, 'flags': [], 'is_wave_bottom': False,
                'label': f'❌ Giá vượt MA20 quá 5% — đã bứt phá'}
    if adx >= 35:
        return {'score': 0, 'total': 12, 'flags': [], 'is_wave_bottom': False,
                'label': f'❌ ADX {adx:.1f} ≥ 35 — đang trend mạnh'}

    # ── NEW HARD DISQUALIFIER: MA200 dốc xuống (Stage 4) ──
    if not np.isnan(ma200) and len(df) >= 5:
        ma200_5d_ago = float(df['ma200'].iloc[-5])
        if not np.isnan(ma200_5d_ago) and ma200 < ma200_5d_ago * WAVE_STAGE4_THRESHOLD:
            return {'score': 0, 'total': 12, 'flags': [], 'is_wave_bottom': False,
                    'label': '❌ MA200 đang dốc xuống — Stage 4 downtrend'}

    # 1-8: Tiêu chí kỹ thuật (giữ như V23)
    if WAVE_RSI_MIN <= rsi <= WAVE_RSI_MAX:
        score += 1; flags.append("RSI vùng hồi phục")
    if price >= ma50 * WAVE_PRICE_MA50:
        score += 1; flags.append("Gần MA50")

    bb_min30 = float(df['bb_width'].tail(30).min())
    if bb_wid <= bb_min30 * 1.3:
        score += 1; flags.append("BB Squeeze")

    if df['can_cung'].tail(7).sum() >= 2:
        score += 1; flags.append("Cạn Cung")

    if obv_z > 0.3:
        score += 1; flags.append("OBV tích lũy")

    if 10 < adx < 25:
        score += 1; flags.append("ADX sideways")

    if bb_low * 0.98 <= price <= ma20 * 1.02:
        score += 1; flags.append("Vùng hỗ trợ kép BB-MA20")

    ret = float(last.get('return_1d', 0))
    vol = float(last['vol_strength'])
    if ret > 0 and 0.7 <= vol <= 1.4:
        score += 1; flags.append("Giá xanh nhẹ + Vol bình thường")

    # 9-11: Bổ sung V23
    if smart_flow:
        score += 1; flags.append("Tổ Chức gom")
    if near_52w_high:
        score += 1; flags.append("Gần đỉnh 52W")
    if div_bullish:
        score += 1; flags.append("Phân kỳ dương")

    # 12: [V24 MỚI] Stage 2 — giá trên MA200, MA200 phẳng/dốc lên
    if not np.isnan(ma200) and len(df) >= 5:
        ma200_5d_ago = float(df['ma200'].iloc[-5])
        if not np.isnan(ma200_5d_ago):
            ma200_slope_ok = ma200 >= ma200_5d_ago * WAVE_MA200_SLOPE_MIN
            if price >= ma200 and ma200_slope_ok:
                score += 1; flags.append("Stage 2 (>MA200, MA200 ↗)")

    is_wave_bottom = score >= WAVE_SCORE_MIN
    total_criteria = 12   # V24: tăng từ 11 → 12
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


# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] calc_indicators — Thêm VWAP20 + MA200 vẫn ffill được
#   Vị trí cũ: ~dòng 589
#   Lưu ý: thay vì viết lại toàn bộ, đây là patch tối thiểu — chỉ thêm 2 dòng.
# ──────────────────────────────────────────────────────────────────────────────
def calc_indicators_patch_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """
    [PATCH] Thêm column 'vwap20' vào df đã qua calc_indicators V23.
    Gọi sau calc_indicators để bổ sung VWAP cho scoring.

    Tích hợp đề xuất: Tốt nhất là sửa trực tiếp calc_indicators, thêm dòng:
        df['vwap20'] = calc_vwap(df, days=20)
    ngay trước khi dropna.
    """
    calc_vwap = globals().get('calc_vwap')
    if calc_vwap is None or 'high' not in df.columns:
        return df
    df = df.copy()
    df['vwap20'] = calc_vwap(df, days=20)
    return df


# ──────────────────────────────────────────────────────────────────────────────
# [REPLACE] calc_total_score — Thêm VWAP vào tech_pts, bỏ sent_pts
#   Vị trí cũ: ~dòng 1209
# ──────────────────────────────────────────────────────────────────────────────
def calc_total_score(
    last: pd.Series,
    ai_score,
    bt: dict,
    foreign_trend: dict,
    growth,
    pe,
    weekly_trend: str,
    sentiment_score: int = 0,    # giữ tham số để khỏi vỡ caller, nhưng không dùng
    sector_score: int = 0,
    market_regime: dict = None,  # MỚI: nhận regime để áp ngưỡng động
) -> dict:
    """
    [V24] Scoring tổng hợp:
      • Thêm tiêu chí "giá trên VWAP" vào tech_pts.
      • Bỏ sent_pts (sentiment đang là dead code).
      • Áp dụng min_score_buy từ market_regime nếu có.
    Tổng tối đa giữ nguyên = 90.
    """
    _is_valid_score = globals().get('_is_valid_score',
                                     lambda x: isinstance(x, (int, float, np.floating))
                                     and not np.isnan(float(x)))
    RSI_HOT          = globals().get('RSI_HOT', 68)
    CANSLIM_GREAT    = globals().get('CANSLIM_GREAT', 20.0)
    PE_CHEAP         = globals().get('PE_CHEAP', 12)
    PE_OK            = globals().get('PE_OK', 20)
    SCORE_BUY_MIN    = globals().get('SCORE_BUY_MIN', 58)

    price = float(last['close'])
    ma20  = float(last['ma20'])
    rsi   = float(last['rsi'])
    vwap20 = float(last.get('vwap20', ma20))

    # --- AI (0-25) ---
    if _is_valid_score(ai_score):
        v = float(ai_score)
        if   v >= 70: ai_pts = 25
        elif v >= 60: ai_pts = 20
        elif v >= 50: ai_pts = 13
        elif v >= 40: ai_pts = 7
        else:         ai_pts = 2
    else:
        ai_pts = 0

    # --- Kỹ thuật (0-20) — thêm VWAP ---
    tech_pts = 0
    if price > ma20:                     tech_pts += 6   # giảm từ 7→6
    if price > vwap20:                   tech_pts += 2   # MỚI: VWAP support
    if rsi < RSI_HOT:                    tech_pts += 4   # giảm từ 5→4
    if last['macd'] > last['signal']:    tech_pts += 5
    if weekly_trend == 'UP':             tech_pts += 3
    tech_pts = min(20, tech_pts)

    # --- Dòng tiền (0-20) ---
    flow_pts = int(foreign_trend.get('score', 0))

    # --- Tài chính (0-15) ---
    fin_pts = 0
    if growth is not None:
        if   growth >= CANSLIM_GREAT: fin_pts += 8
        elif growth > 0:              fin_pts += 4
    if pe is not None:
        if   pe < PE_CHEAP: fin_pts += 7
        elif pe < PE_OK:    fin_pts += 4

    # --- Ngành (0-10) ---
    sector_pts = min(10, int(sector_score))

    total = min(90, ai_pts + tech_pts + flow_pts + fin_pts + sector_pts)

    # --- Áp ngưỡng động từ market regime ---
    if market_regime is not None:
        if not market_regime.get('buy_allowed', True):
            decision       = "🔴 BEAR MARKET — ĐỨNG NGOÀI"
            decision_color = "red"
        else:
            min_buy = market_regime.get('min_score_buy', SCORE_BUY_MIN)
            if total >= min_buy and rsi < RSI_HOT:
                decision       = "🚀 MUA / NẮM GIỮ (STRONG BUY)"
                decision_color = "green"
            elif total >= 45:
                decision       = "⚖️ THEO DÕI (WATCHLIST)"
                decision_color = "orange"
            else:
                decision       = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)"
                decision_color = "red"
    else:
        if total >= SCORE_BUY_MIN and rsi < RSI_HOT:
            decision, decision_color = "🚀 MUA / NẮM GIỮ (STRONG BUY)", "green"
        elif total >= 45:
            decision, decision_color = "⚖️ THEO DÕI (WATCHLIST)", "orange"
        else:
            decision, decision_color = "🚨 BÁN / ĐỨNG NGOÀI (BEARISH)", "red"

    return {
        'total':          total,
        'ai_pts':         ai_pts,
        'tech_pts':       tech_pts,
        'flow_pts':       flow_pts,
        'fin_pts':        fin_pts,
        'sector_pts':     sector_pts,
        'sent_pts':       0,   # giữ key cho compat nhưng = 0
        'decision':       decision,
        'decision_color': decision_color,
        'regime_applied': market_regime['regime'] if market_regime else 'NONE',
    }


# ──────────────────────────────────────────────────────────────────────────────
# [NEW] bayes_winrate — Bayesian shrinkage
# ──────────────────────────────────────────────────────────────────────────────
def bayes_winrate(
    wins: int,
    total: int,
    prior_winrate: float = BAYES_PRIOR_WR,
    prior_n: float = BAYES_PRIOR_N,
) -> float:
    """
    [NEW] Bayesian-shrunk winrate.
    Khi sample nhỏ, kéo về prior_winrate; khi lớn ≈ winrate thô.

    Ví dụ: 6 wins / 8 trades:
        Thô:     6/8 = 75%
        Bayes:   (6 + 0.5×10) / (8 + 10) = 11/18 ≈ 61.1%
    """
    if total <= 0:
        return round(prior_winrate * 100, 1)
    adjusted_wins = wins + prior_winrate * prior_n
    adjusted_n    = total + prior_n
    return round(adjusted_wins / adjusted_n * 100, 1)


# ──────────────────────────────────────────────────────────────────────────────
# [NEW] is_data_fresh — Kiểm tra dữ liệu mới
# ──────────────────────────────────────────────────────────────────────────────
def is_data_fresh(df: pd.DataFrame, max_days_old: int = MAX_DATA_DAYS_OLD) -> bool:
    """
    [NEW] Kiểm tra dữ liệu có cập nhật trong N ngày qua không.
    """
    valid = globals().get('valid', lambda x: x is not None and not x.empty)
    if not valid(df) or 'date' not in df.columns:
        return False
    try:
        last_date = pd.to_datetime(df['date'].iloc[-1])
        days_old = (datetime.now() - last_date).days
        return days_old <= max_days_old
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────────────
# [NEW] is_backtest_significant — Đủ sample size?
# ──────────────────────────────────────────────────────────────────────────────
def is_backtest_significant(
    bt: dict,
    min_signals: int = MIN_SIGNALS_RELIABLE,
) -> tuple[bool, str]:
    """
    [NEW] Kiểm tra backtest có đủ signals để tin metric không.
    """
    n = bt.get('signals', 0)
    if n < min_signals:
        return False, f"⚠️ Chỉ {n} signals — không đủ tin cậy (cần ≥{min_signals})"
    return True, f"✅ Đủ sample ({n} signals)"


# ==============================================================================
# #9. PERFORMANCE — Cache + Parallel
# ==============================================================================

@st.cache_data(ttl=3600, max_entries=500)
def calc_indicators_cached(ticker: str, date_key: str) -> pd.DataFrame:
    """
    [NEW] [V24] Cache calc_indicators theo (ticker, ngày).
    Tránh re-compute cùng dữ liệu nhiều lần trong 1 session.

    date_key dạng 'YYYY-MM-DD'. Gọi:
        date_key = datetime.now(TZ_VN).strftime('%Y-%m-%d')
        df = calc_indicators_cached(t, date_key)
    """
    get_price       = globals().get('get_price')
    valid           = globals().get('valid')
    calc_indicators = globals().get('calc_indicators')
    if not all([get_price, valid, calc_indicators]):
        return pd.DataFrame()

    df = get_price(ticker)
    if not valid(df):
        return pd.DataFrame()
    df = calc_indicators(df)
    # Thêm VWAP nếu calc_vwap có
    df = calc_indicators_patch_vwap(df)
    return df


def scan_parallel(
    tickers: list[str],
    scan_fn,
    max_workers: int = 10,
    show_progress: bool = True,
    timeout_per_task: int = 30,
) -> list:
    """
    [NEW] [V24] Quét song song danh sách ticker.

    Args:
        tickers          — list mã cần quét
        scan_fn          — function(ticker) -> result_or_None
        max_workers      — số thread đồng thời (10 an toàn với Vnstock)
        show_progress    — hiện progress bar Streamlit
        timeout_per_task — timeout/ticker (giây)

    Returns: list các result không None.
    """
    results = []
    total = len(tickers)
    if total == 0:
        return results

    progress = st.progress(0) if show_progress else None
    status   = st.empty()    if show_progress else None
    done = 0

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(scan_fn, t): t for t in tickers}
        for f in as_completed(futures):
            t = futures[f]
            try:
                r = f.result(timeout=timeout_per_task)
                if r is not None:
                    results.append(r)
            except Exception as e:
                print(f"[WARN] scan_parallel {t}: {e}")
            done += 1
            if show_progress:
                progress.progress(done / total)
                status.caption(f"⏳ Đã quét {done}/{total} (đang xử lý: {t})")

    if show_progress:
        progress.empty()
        status.empty()
    return results


# ==============================================================================
# #10. WATCHLIST PERSISTENCE — Lưu xuyên session qua GitHub Gist
# ==============================================================================

def load_watchlist_from_gist() -> list[str]:
    """
    [NEW] Đọc watchlist từ private GitHub Gist.

    Cần setup trong .streamlit/secrets.toml:
        gist_id      = "abc123..."
        github_token = "ghp_..."

    Trả về list ticker, hoặc [] nếu chưa setup/lỗi.
    """
    try:
        gist_id = st.secrets.get('gist_id', '')
        token   = st.secrets.get('github_token', '')
        if not gist_id or not token:
            return []
        r = requests.get(
            f"https://api.github.com/gists/{gist_id}",
            headers={'Authorization': f'token {token}'},
            timeout=5,
        )
        if r.status_code != 200:
            return []
        data = r.json()
        if WATCHLIST_GIST_FILENAME not in data.get('files', {}):
            return []
        content = data['files'][WATCHLIST_GIST_FILENAME]['content']
        return [x.strip().upper() for x in content.splitlines() if x.strip()]
    except Exception as e:
        print(f"[WARN] load_watchlist: {e}")
        return []


def save_watchlist_to_gist(tickers: list[str]) -> bool:
    """[NEW] Ghi watchlist lên Gist."""
    try:
        gist_id = st.secrets.get('gist_id', '')
        token   = st.secrets.get('github_token', '')
        if not gist_id or not token:
            return False
        body = {
            'files': {
                WATCHLIST_GIST_FILENAME: {
                    'content': '\n'.join(sorted(set(t.upper() for t in tickers)))
                }
            }
        }
        r = requests.patch(
            f"https://api.github.com/gists/{gist_id}",
            headers={'Authorization': f'token {token}'},
            json=body, timeout=5,
        )
        return r.status_code == 200
    except Exception as e:
        print(f"[WARN] save_watchlist: {e}")
        return False


def load_watchlist_from_file(path: str = 'watchlist.json') -> list[str]:
    """[NEW] Fallback: lưu watchlist vào file JSON local."""
    try:
        if not os.path.exists(path):
            return []
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_watchlist_to_file(tickers: list[str], path: str = 'watchlist.json') -> bool:
    """[NEW] Fallback: ghi watchlist vào file JSON local."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(sorted(set(t.upper() for t in tickers)), f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def watchlist_persist(tickers: list[str]) -> bool:
    """
    [NEW] Persist watchlist: thử Gist trước, fallback file.
    """
    if save_watchlist_to_gist(tickers):
        return True
    return save_watchlist_to_file(tickers)


def watchlist_load() -> list[str]:
    """
    [NEW] Load watchlist: thử Gist trước, fallback file.
    """
    wl = load_watchlist_from_gist()
    if wl:
        return wl
    return load_watchlist_from_file()


# ==============================================================================
# #11. RISK THERMOMETER — Nhiệt kế rủi ro tổng hợp
# (KHÔNG bao gồm auto-pause logic — theo yêu cầu user)
# ==============================================================================

def calc_risk_temperature(
    regime: dict,
    breadth: dict,
    portfolio_metrics: dict = None,
) -> dict:
    """
    [NEW] [V24] Nhiệt kế rủi ro 0-100 tổng hợp 3-5 nguồn.

    portfolio_metrics (tuỳ chọn) có thể chứa:
        'dd_pct'                  — drawdown hiện tại
        'pct_rsi_overheat'        — % vị thế RSI > 70
        'concentration_sector_pct'— % vốn trong 1 ngành lớn nhất
        'avg_atr_pct'             — ATR trung bình của portfolio (%/giá)
    """
    components = {}

    # 1. Market regime (40%)
    regime_map = {
        'STRONG_BULL': 10,
        'CAUTIOUS_BULL': 30,
        'UNKNOWN': 50,
        'MIXED': 60,
        'BEAR': 90,
    }
    c1 = regime_map.get(regime.get('regime', 'UNKNOWN'), 50)
    components['market_regime'] = c1

    # 2. Breadth (15%)
    pct_ma20 = float(breadth.get('pct_above_ma20', 50))
    if   pct_ma20 >= 70: c2 = 10
    elif pct_ma20 >= 50: c2 = 30
    elif pct_ma20 >= 40: c2 = 60
    else:                c2 = 85
    components['breadth'] = c2

    # 3. Drawdown (20%)
    if portfolio_metrics:
        dd = abs(portfolio_metrics.get('dd_pct', 0))
        if   dd < 3:   c3 = 10
        elif dd < 7:   c3 = 35
        elif dd < 12:  c3 = 65
        else:          c3 = 90
    else:
        c3 = 30
    components['drawdown'] = c3

    # 4. RSI overheat (15%)
    if portfolio_metrics:
        pct_hot = portfolio_metrics.get('pct_rsi_overheat', 0)
        if   pct_hot < 10: c4 = 15
        elif pct_hot < 30: c4 = 40
        elif pct_hot < 50: c4 = 70
        else:              c4 = 90
    else:
        c4 = 30
    components['rsi_overheat'] = c4

    # 5. Concentration (10%)
    if portfolio_metrics:
        conc = portfolio_metrics.get('concentration_sector_pct', 0)
        if   conc < 30:  c5 = 15
        elif conc < 50:  c5 = 45
        elif conc < 70:  c5 = 70
        else:            c5 = 90
    else:
        c5 = 30
    components['concentration'] = c5

    weights = {'market_regime': 0.40, 'breadth': 0.15,
               'drawdown': 0.20, 'rsi_overheat': 0.15, 'concentration': 0.10}
    total = sum(components[k] * weights[k] for k in components)
    total = round(total, 1)

    if   total < 25: emoji, label, color = '🟢', 'AN TOÀN',    'success'
    elif total < 50: emoji, label, color = '🟡', 'BÌNH THƯỜNG', 'warning'
    elif total < 75: emoji, label, color = '🟠', 'CẨN TRỌNG',  'warning'
    else:            emoji, label, color = '🔴', 'NGUY HIỂM',  'error'

    return {
        'score':      total,
        'emoji':      emoji,
        'label':      label,
        'color':      color,
        'components': components,
        'weights':    weights,
    }


def render_risk_thermometer(risk: dict) -> None:
    """[NEW] Widget compact hiển thị nhiệt kế rủi ro."""
    st.markdown(f"### {risk['emoji']} Nhiệt kế rủi ro: **{risk['score']}/100** "
                f"— {risk['label']}")
    with st.expander("Chi tiết các thành phần"):
        comp = risk['components']
        w    = risk['weights']
        for k in comp:
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"**{k.replace('_', ' ').title()}**")
            c2.write(f"{comp[k]:.0f}/100")
            c3.write(f"trọng số {w[k]*100:.0f}%")


# ==============================================================================
# #12. PDF EXPORT — Báo cáo phân tích 1 mã
# ==============================================================================

def export_stock_report_pdf(
    ticker: str,
    scoring: dict,
    last: pd.Series,
    bt: dict,
    ai_score,
    kelly_pct: float,
    entry_signal: dict,
    chart_png_bytes: bytes = None,
    extra_sections: dict = None,
) -> bytes | None:
    """
    [NEW] [V24] Xuất báo cáo PDF cho 1 mã.

    extra_sections (tuỳ chọn): dict {'tên_section': 'nội dung HTML/text'}.

    Returns: bytes của PDF, hoặc None nếu thiếu reportlab.
    """
    if not HAS_REPORTLAB:
        print("[WARN] reportlab chưa cài. pip install reportlab")
        return None

    _is_valid_score = globals().get('_is_valid_score',
                                     lambda x: isinstance(x, (int, float, np.floating))
                                     and not np.isnan(float(x)))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=40, bottomMargin=40,
                            leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Title'], fontSize=18, spaceAfter=10)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13,
                        spaceAfter=6, textColor=colors.HexColor('#1F3864'))
    body = styles['Normal']

    flow = []
    flow.append(RLPar(f"BÁO CÁO PHÂN TÍCH — {ticker}", h1))
    flow.append(RLPar(
        f"<i>Thời gian: {datetime.now().strftime('%H:%M %d/%m/%Y')}</i>", body))
    flow.append(Spacer(1, 12))

    # Tổng kết
    flow.append(RLPar("Tổng kết", h2))
    summary_data = [
        ['Điểm tổng hợp', f"{scoring['total']}/90"],
        ['Quyết định',    scoring['decision']],
        ['Giá hiện tại',  f"{float(last['close']):,.0f}"],
        ['AI T+3',        f"{float(ai_score):.1f}%" if _is_valid_score(ai_score) else "N/A"],
        ['RSI',           f"{float(last['rsi']):.1f}"],
        ['Half-Kelly',    f"{kelly_pct:.1f}% vốn"],
    ]
    t = RLTable(summary_data, colWidths=[120, 360])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7EAF6')),
        ('FONT',       (0, 0), (-1, -1), 'Helvetica', 10),
        ('VALIGN',     (0, 0), (-1, -1), 'TOP'),
        ('GRID',       (0, 0), (-1, -1), 0.4, colors.grey),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 12))

    # Breakdown scoring
    flow.append(RLPar("Phân tích điểm số", h2))
    sb_data = [
        ['Thành phần', 'Điểm', 'Tối đa'],
        ['AI',        str(scoring['ai_pts']),     '25'],
        ['Kỹ thuật',  str(scoring['tech_pts']),   '20'],
        ['Dòng tiền', str(scoring['flow_pts']),   '20'],
        ['Tài chính', str(scoring['fin_pts']),    '15'],
        ['Ngành',     str(scoring['sector_pts']), '10'],
    ]
    sb = RLTable(sb_data, colWidths=[160, 80, 80])
    sb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F3864')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONT',       (0, 0), (-1, -1), 'Helvetica', 9),
        ('ALIGN',      (1, 0), (-1, -1), 'CENTER'),
        ('GRID',       (0, 0), (-1, -1), 0.4, colors.grey),
        ('PADDING',    (0, 0), (-1, -1), 5),
    ]))
    flow.append(sb)
    flow.append(Spacer(1, 12))

    # Backtest
    flow.append(RLPar("Hiệu năng backtest", h2))
    bt_data = [
        ['Win rate (thô)',    f"{bt.get('winrate', 0):.1f}%"],
        ['Win rate (Bayes)',  f"{bt.get('winrate_bayes', 0):.1f}%"],
        ['Expectancy',        f"{bt.get('expectancy', 0):+.2f}%"],
        ['Sharpe',            f"{bt.get('sharpe', 0):.2f}"],
        ['Max DD',            f"{bt.get('max_drawdown', 0):.2f}%"],
        ['Số signals',        f"{bt.get('signals', 0)}"],
    ]
    btab = RLTable(bt_data, colWidths=[160, 320])
    btab.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F2F2F2')),
        ('FONT',       (0, 0), (-1, -1), 'Helvetica', 9),
        ('GRID',       (0, 0), (-1, -1), 0.4, colors.grey),
        ('PADDING',    (0, 0), (-1, -1), 5),
    ]))
    flow.append(btab)
    flow.append(Spacer(1, 12))

    # Entry signal
    if entry_signal:
        flow.append(RLPar("Tín hiệu vào lệnh", h2))
        flow.append(RLPar(f"<b>{entry_signal.get('action', '-')}</b> — "
                          f"Size đề xuất: {entry_signal.get('size_pct', 0)}%", body))
        flow.append(RLPar(f"Entry: {entry_signal.get('entry', '-'):,} | "
                          f"SL: {entry_signal.get('sl', '-'):,} ({entry_signal.get('sl_pct', 0):+.1f}%) | "
                          f"TP2: {entry_signal.get('tp2', '-'):,} | "
                          f"TP3: {entry_signal.get('tp3', '-'):,}", body))
        flow.append(Spacer(1, 12))

    # Chart
    if chart_png_bytes:
        try:
            flow.append(RLPar("Biểu đồ kỹ thuật", h2))
            flow.append(RLImage(io.BytesIO(chart_png_bytes), width=500, height=280))
            flow.append(Spacer(1, 12))
        except Exception as e:
            print(f"[WARN] PDF chart embed: {e}")

    # Extra sections
    if extra_sections:
        for title, content in extra_sections.items():
            flow.append(RLPar(title, h2))
            flow.append(RLPar(str(content), body))
            flow.append(Spacer(1, 12))

    flow.append(Spacer(1, 12))
    flow.append(RLPar("<i>Báo cáo tự động sinh bởi Quant System V24. "
                      "Không phải khuyến nghị đầu tư.</i>",
                      ParagraphStyle('Footer', parent=body, fontSize=8,
                                      textColor=colors.grey)))

    doc.build(flow)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


def streamlit_pdf_download_button(
    pdf_bytes: bytes,
    ticker: str,
    label: str = "📄 Tải báo cáo PDF",
) -> None:
    """[NEW] Helper hiển thị nút download PDF trong Streamlit."""
    if pdf_bytes is None:
        st.warning("⚠️ Cài đặt reportlab để xuất PDF: `pip install reportlab`")
        return
    st.download_button(
        label=label,
        data=pdf_bytes,
        file_name=f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
    )


# ==============================================================================
# #13. UI HELPERS — Tooltips, Mobile responsive
# ==============================================================================

# Dictionary tooltip dùng chung — gọi METRIC_HELP['rsi'] để lấy tooltip text
METRIC_HELP = {
    'rsi':        'Relative Strength Index 14: <30 quá bán, >70 quá mua',
    'macd':       'MACD = EMA12 - EMA26. >Signal = bullish',
    'adx':        'Average Directional Index: >25 = trend mạnh, <20 = sideways',
    'obv':        'On-Balance Volume: tích lũy volume theo chiều giá',
    'atr':        'Average True Range: thước đo biến động thực tế',
    'rs_rating':  'Relative Strength vs VN-Index 3 tháng. 🔥≥80 | ✅≥65 | 🟡≥45 | 🔴<45',
    'sharpe':     'Sharpe Ratio: >1 tốt, >1.5 rất tốt, >2 cần kiểm tra overfit',
    'max_dd':     'Max Drawdown: % sụt lớn nhất từ peak. <10% tốt, >20% nguy hiểm',
    'winrate':    'Tỷ lệ thắng. Lưu ý: với sample <30, xem winrate Bayesian thay vì thô',
    'expectancy': 'Lợi nhuận kỳ vọng mỗi lệnh (%). >0 = có edge',
    'vwap':       'Volume Weighted Average Price 20 phiên. Giá>VWAP = phe mua chủ động',
    'kelly':      'Half-Kelly Criterion: % vốn tối ưu cho lệnh dựa trên winrate/avg_profit',
    'ai_t3':      'Xác suất AI dự đoán giá tăng ≥2% trong 3 phiên tới',
    'wave_bot':   'Chân Sóng (Wave Bottom): 12 tiêu chí, cần ≥4 điểm',
    'divergence': 'Phân kỳ giá vs động lượng. Dương = sắp đảo tăng; Âm = sắp đảo giảm',
    '52w_high':   'Tỷ lệ so với đỉnh 52 tuần. Trong 8% đỉnh = CANSLIM Stage 2',
    'regime':     'Trạng thái thị trường tổng thể: STRONG_BULL / CAUTIOUS / MIXED / BEAR',
}


def help_for(metric_key: str) -> str:
    """[NEW] Lấy tooltip cho 1 metric. Trả về '' nếu không có."""
    return METRIC_HELP.get(metric_key, '')


def is_mobile_viewport() -> bool:
    """
    [NEW] Best-effort detect mobile.
    Streamlit chưa có API native. Dùng session_state flag user có thể toggle.
    """
    return st.session_state.get('is_mobile', False)


def responsive_columns(weights: list, mobile_stack: bool = True):
    """
    [NEW] Trả về list cột — trên mobile có thể stack thành 1 cột.
    """
    if is_mobile_viewport() and mobile_stack:
        return [st.container() for _ in weights]
    return st.columns(weights)


# ==============================================================================
# #14. SHAP EXPLAIN — Hiển thị "vì sao AI nói thế"
# ==============================================================================

def render_ai_explanation_card(ai_result: dict) -> None:
    """
    [NEW] [V24] Render card AI prediction + SHAP top drivers.
    ai_result là output từ predict_ai_cached_with_explain.
    """
    _is_valid_score = globals().get('_is_valid_score',
                                     lambda x: isinstance(x, (int, float, np.floating))
                                     and not np.isnan(float(x)))

    with st.container(border=True):
        prob = ai_result.get('prob')
        cv_auc = ai_result.get('cv_auc')
        drivers = ai_result.get('top_drivers', [])

        c1, c2 = st.columns([2, 3])
        with c1:
            if _is_valid_score(prob):
                v = float(prob)
                if   v >= 70: badge = '🔥 Rất tốt'
                elif v >= 55: badge = '✅ Tốt'
                elif v >= 45: badge = '🟡 Trung bình'
                else:         badge = '🔴 Rủi ro'
                st.metric("🤖 AI T+3", f"{v:.1f}%",
                          help=help_for('ai_t3'))
                st.caption(badge)
                if cv_auc is not None:
                    st.caption(f"Độ tin cậy CV (AUC): {cv_auc:.2f}")
            else:
                st.metric("🤖 AI T+3", "N/A")

        with c2:
            if drivers:
                st.markdown("**Top đặc trưng ảnh hưởng:**")
                for d in drivers:
                    icon = '↑' if d['direction'] == '↑' else '↓'
                    color = 'green' if d['direction'] == '↑' else 'red'
                    st.markdown(
                        f"<span style='color:{color}'>{icon}</span> "
                        f"<code>{d['feature']}</code> = {d['value']} "
                        f"<span style='color:gray'>(SHAP {d['shap']:+.3f})</span>",
                        unsafe_allow_html=True,
                    )
            elif not HAS_SHAP:
                st.caption("💡 Cài `shap` để xem chi tiết: `pip install shap`")


# ==============================================================================
# #15. QUICK PICK NÂNG CẤP — Tích hợp Correlation Check + Regime Filter
# ==============================================================================

def quick_pick_stocks_v24(
    tickers_list: list[str],
    market_regime: dict,
    ai_min: float = 45.0,
    n_results: int = 3,
    parallel: bool = True,
    max_corr: float = CORR_MAX_PAIR,
) -> list[dict]:
    """
    [REPLACE] [V24] Quick Pick nâng cấp với:
      • Bỏ qua nếu regime = BEAR (không gợi ý mã nào)
      • Áp min_score_buy động theo regime
      • Quét song song (nếu parallel=True)
      • Diversified top-pick (correlation check)
    """
    # Nếu BEAR market, không gợi ý gì
    if not market_regime.get('buy_allowed', True):
        return []

    # Lấy hằng số V23
    SCAN_DAYS         = globals().get('SCAN_DAYS', 200)
    VOL_BREAKOUT      = globals().get('VOL_BREAKOUT', 1.3)
    ATR_MULTIPLIER    = globals().get('ATR_MULTIPLIER', 2.0)
    PRICE_NEAR_MA20   = globals().get('PRICE_NEAR_MA20', 0.95)

    valid                = globals().get('valid')
    get_price            = globals().get('get_price')
    calc_indicators      = globals().get('calc_indicators')
    calc_52w_info        = globals().get('calc_52w_info')
    calc_rs_rating       = globals().get('calc_rs_rating')
    calc_wave_bottom_fn  = globals().get('calc_wave_bottom_score', calc_wave_bottom_score)
    get_weekly_trend     = globals().get('get_weekly_trend')
    get_ticker_sector    = globals().get('get_ticker_sector')

    if not all([valid, get_price, calc_indicators, calc_52w_info,
                calc_rs_rating, get_weekly_trend]):
        return []

    date_key = datetime.now().strftime('%Y-%m-%d')
    sample = list(dict.fromkeys(tickers_list))[:200]

    def _eval_ticker(t: str) -> dict | None:
        try:
            df_q = get_price(t, days=SCAN_DAYS)
            if not valid(df_q) or len(df_q) < 100:
                return None
            if not is_data_fresh(df_q):
                return None
            df_q = calc_indicators(df_q)
            df_q = calc_indicators_patch_vwap(df_q)
            last_q  = df_q.iloc[-1]
            rsi_q   = float(last_q['rsi'])
            price_q = float(last_q['close'])
            ma20_q  = float(last_q['ma20'])
            vol_q   = float(last_q['vol_strength'])
            adx_q   = float(last_q.get('adx', 0))

            # Hard filters
            if rsi_q > 60 or rsi_q < 25:    return None
            if price_q < ma20_q * 0.93:      return None
            if vol_q > VOL_BREAKOUT:         return None

            # AI score (cached theo ngày)
            ai_q = predict_ai_cached(t, date_key)
            _is_valid_score = globals().get('_is_valid_score',
                                             lambda x: isinstance(x, (int, float, np.floating))
                                             and not np.isnan(float(x)))
            if not _is_valid_score(ai_q):    return None
            ai_f = float(ai_q)
            if ai_f < ai_min:                return None

            # Wave bottom + ngữ cảnh
            w52   = calc_52w_info(df_q)
            div_q = detect_divergence(df_q)
            smart = smart_flow_proxy(df_q)
            wave  = calc_wave_bottom_fn(
                df_q, last_q,
                smart_flow=(smart['trend'] in ('BUY', 'STRONG_BUY')),
                near_52w_high=w52['near_high'],
                div_bullish=(div_q['signal'] == 'BULLISH'),
            )

            df_vni = globals().get('df_vni', pd.DataFrame())
            rs_q = calc_rs_rating(df_q, df_vni)

            # Lọc thêm theo regime
            if market_regime.get('regime') == 'MIXED' and rs_q < 80:
                return None

            weekly_q = get_weekly_trend(df_q)
            atr_q    = float(last_q.get('atr', price_q * 0.02))
            sl_q     = price_q - ATR_MULTIPLIER * atr_q
            tp2_q    = price_q + 2 * ATR_MULTIPLIER * atr_q
            tp3_q    = price_q + 3 * ATR_MULTIPLIER * atr_q

            score_q = (
                ai_f * 0.4 +
                rs_q * 0.25 +
                wave['score'] * 4 +
                (10 if weekly_q == 'UP' else 0) +
                (5 if adx_q > 20 else 0)
            )

            return {
                'ticker':    t,
                'price':     round(price_q, 0),
                'ai':        round(ai_f, 1),
                'rsi':       round(rsi_q, 1),
                'rs':        round(rs_q, 1),
                'vol':       round(vol_q, 2),
                'adx':       round(adx_q, 1),
                'weekly':    weekly_q,
                'wave':      wave['score'],
                'wave_total': wave['total'],
                'wave_flags': wave['flags'],
                'sl':        round(sl_q, 0),
                'tp2':       round(tp2_q, 0),
                'tp3':       round(tp3_q, 0),
                'sl_pct':    round((sl_q - price_q) / price_q * 100, 2),
                'tp2_pct':   round((tp2_q - price_q) / price_q * 100, 2),
                'sector':    (get_ticker_sector(t) if get_ticker_sector else None) or 'Khác',
                'score':     round(score_q, 1),
                'smart_flow_label': smart['label'],
                'div_label':        div_q['label'],
            }
        except Exception as e:
            print(f"[WARN] _eval_ticker {t}: {e}")
            return None

    # Chạy quét — parallel hoặc tuần tự
    if parallel:
        candidates = scan_parallel(sample, _eval_ticker, max_workers=10)
    else:
        candidates = []
        for t in sample:
            r = _eval_ticker(t)
            if r is not None:
                candidates.append(r)

    candidates.sort(key=lambda x: x['score'], reverse=True)

    # Áp correlation check để đa dạng hoá
    top = diversified_top_pick(candidates, n=n_results, max_corr=max_corr)
    return top


def render_quick_pick_v24(picks: list[dict]) -> None:
    """[NEW] Render Quick Pick với cảnh báo correlation."""
    if not picks:
        st.info("ℹ️ Không có mã nào đạt tiêu chí hiện tại "
                "(có thể do market regime BEAR hoặc tiêu chí khắt khe).")
        return

    for i, p in enumerate(picks, 1):
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([1.2, 1.5, 1.5, 1.5, 2])
            c1.markdown(f"### #{i} `{p['ticker']}`")
            c1.caption(f"💰 {p['price']:,.0f}")
            c2.metric("🤖 AI", f"{p['ai']}%", help=help_for('ai_t3'))
            c3.metric("📈 RS", f"{p['rs']:.0f}", help=help_for('rs_rating'))
            c4.metric("📊 RSI", f"{p['rsi']}")
            c5.metric("🌊 Chân Sóng", f"{p['wave']}/{p.get('wave_total', 12)}",
                      help=help_for('wave_bot'))

            cols2 = st.columns(4)
            cols2[0].caption(f"🎯 SL: {p['sl']:,.0f} ({p['sl_pct']:+.1f}%)")
            cols2[1].caption(f"🎯 TP2: {p['tp2']:,.0f} ({p['tp2_pct']:+.1f}%)")
            cols2[2].caption(f"📐 ADX: {p['adx']} | Vol: {p['vol']}x")
            cols2[3].caption(f"🏢 {p['sector']} | {p['weekly']}")

            if p.get('_max_corr_to_selected'):
                corr_val = p['_max_corr_to_selected']
                if p.get('_fallback'):
                    st.warning(f"⚠️ Correlation cao với mã khác trong top: {corr_val} "
                               "(nới quy tắc do không đủ candidate)")
                else:
                    st.caption(f"✅ Correlation tối đa với top khác: {corr_val} < {CORR_MAX_PAIR}")

            with st.expander("Chi tiết tín hiệu"):
                st.write(f"**Smart Flow:** {p['smart_flow_label']}")
                st.write(f"**Divergence:** {p['div_label']}")
                if p.get('wave_flags'):
                    st.write("**Chân Sóng flags:** " + ", ".join(p['wave_flags']))


# ==============================================================================
# #16. INTEGRATION SNIPPETS — Đoạn code wire vào main app
# ==============================================================================

INTEGRATION_GUIDE = """
================================================================================
HƯỚNG DẪN TÍCH HỢP V24 VÀO V23 (TÓM TẮT)
================================================================================

BƯỚC 1 — IMPORT
  Thêm vào đầu file V23, sau các import có sẵn:
  ```
  from quant_v24_upgrade_pack import (
      # Core fixes
      calc_obv, _run_xgb, predict_ai_cached, predict_ai_cached_with_explain,
      run_backtest, detect_divergence, get_vnindex_cached,
      # New features
      smart_flow_proxy, detect_market_regime, render_market_regime_banner,
      generate_exit_signal, render_exit_signal_card,
      calc_position_size_vol_parity, combine_kelly_and_vol_parity,
      diversified_top_pick,
      run_backtest_param, compare_strategies,
      # Refinements
      calc_wave_bottom_score, calc_total_score,
      calc_indicators_patch_vwap, bayes_winrate,
      is_data_fresh, is_backtest_significant,
      # Performance
      calc_indicators_cached, scan_parallel,
      # Watchlist
      watchlist_load, watchlist_persist,
      # Risk thermometer (không có auto-pause)
      calc_risk_temperature, render_risk_thermometer,
      # PDF
      export_stock_report_pdf, streamlit_pdf_download_button,
      # UI helpers
      help_for, METRIC_HELP, responsive_columns, is_mobile_viewport,
      # AI explain
      render_ai_explanation_card,
      # Quick pick V24
      quick_pick_stocks_v24, render_quick_pick_v24,
  )
  ```

BƯỚC 2 — THAY HẰNG SỐ
  Copy block CONSTANTS (#0) sang section CONSTANTS của V23.
  Hoặc đơn giản hơn: thêm 1 dòng `from quant_v24_upgrade_pack import *`
  rồi xoá các hằng số trùng tên ở V23.

BƯỚC 3 — calc_indicators NÊN THÊM VWAP
  Trong calc_indicators của V23, NGAY TRƯỚC dòng dropna, thêm:
  ```
  df['vwap20'] = calc_vwap(df, days=20)
  ai_cols = [..., 'vwap20']   # thêm vào danh sách dropna nếu muốn ép có
  ```
  Hoặc dùng calc_indicators_patch_vwap(df) sau khi gọi calc_indicators.

BƯỚC 4 — Wire vào MAIN APPLICATION
  Sau authenticate(), trước st.tabs(...):

  ```
  # ---- Lấy VN-Index + breadth ----
  df_vni  = get_vnindex_cached()
  sample  = tuple(PILLARS + FALLBACK_TICKERS[:40])
  breadth = calc_market_breadth(sample)

  # ---- Market Regime ----
  regime = detect_market_regime(df_vni, breadth)
  st.session_state['market_regime'] = regime

  # ---- Risk Thermometer ----
  # portfolio_metrics có thể None nếu chưa có position tracking
  portfolio_metrics = st.session_state.get('portfolio_metrics', None)
  risk = calc_risk_temperature(regime, breadth, portfolio_metrics)
  st.session_state['risk_temperature'] = risk

  # ---- Banner xuyên 7 tab ----
  render_market_regime_banner(regime, breadth)
  with st.expander("🌡️ Nhiệt kế rủi ro chi tiết"):
      render_risk_thermometer(risk)
  ```

BƯỚC 5 — Gọi calc_total_score với regime
  Trong tab Robot Advisor / Radar / nơi gọi calc_total_score:
  ```
  scoring = calc_total_score(
      last, ai_score, bt, foreign_trend, growth, pe,
      weekly_trend, sentiment_score=0,
      sector_score=sector_score,
      market_regime=st.session_state.get('market_regime'),   # MỚI
  )
  ```

BƯỚC 6 — Thay foreign_trend bằng smart_flow_proxy
  Vì get_foreign trả None, dùng smart_flow_proxy:
  ```
  # foreign_trend = analyze_foreign_flow(...)   # cũ — luôn trả 0
  foreign_trend = smart_flow_proxy(df)           # MỚI
  ```

BƯỚC 7 — AI explain trong tab Robot Advisor
  ```
  date_key = datetime.now(TZ_VN).strftime('%Y-%m-%d')
  ai_result = predict_ai_cached_with_explain(ticker, date_key)
  render_ai_explanation_card(ai_result)
  ai_score = ai_result['prob']   # dùng tiếp như float trong scoring
  ```

BƯỚC 8 — Quick Pick V24 (thay thế quick_pick_stocks)
  ```
  picks = quick_pick_stocks_v24(
      tickers_list,
      market_regime=regime,
      ai_min=50,
      n_results=3,
      parallel=True,
      max_corr=0.7,
  )
  render_quick_pick_v24(picks)
  ```

BƯỚC 9 — Exit Signal trong Trade Journal
  Khi user nhập vị thế mở:
  ```
  exit_sig = generate_exit_signal(
      last, df,
      entry_price=entry_price,
      current_price=last['close'],
      weekly_trend=weekly,
      divergence=detect_divergence(df),
      ai_score=ai_score,
  )
  render_exit_signal_card(exit_sig, last['close'], entry_price, shares)
  ```

BƯỚC 10 — Vol-Parity Position Sizing
  Trong tab Robot Advisor sau Kelly:
  ```
  capital = st.number_input("Vốn (đồng)", value=100_000_000, step=10_000_000)
  vp = calc_position_size_vol_parity(
      capital, entry_price=last['close'],
      atr=last['atr'],
      risk_per_trade=0.01,
      max_size_pct=0.20,
      size_mult=regime['size_mult'],
  )
  combined = combine_kelly_and_vol_parity(kelly_pct, vp, capital)
  st.write(f"Đề xuất mua **{combined['final_shares']:,}** cp "
           f"(~{combined['final_size_pct']}% vốn, limited by {combined['limiter']})")
  ```

BƯỚC 11 — PDF Export
  ```
  if st.button("📄 Xuất báo cáo PDF"):
      pdf = export_stock_report_pdf(
          ticker, scoring, last, bt, ai_score, kelly_pct, entry_signal,
          chart_png_bytes=fig.to_image(format='png'),
      )
      streamlit_pdf_download_button(pdf, ticker)
  ```

BƯỚC 12 — Watchlist persistence
  Trong sidebar:
  ```
  if 'watchlist' not in st.session_state:
      st.session_state.watchlist = watchlist_load()

  wl = st.text_area("Watchlist (mỗi dòng 1 mã)",
                    value='\\n'.join(st.session_state.watchlist))
  new_wl = [x.strip().upper() for x in wl.splitlines() if x.strip()]
  if new_wl != st.session_state.watchlist:
      if st.button("💾 Lưu"):
          if watchlist_persist(new_wl):
              st.session_state.watchlist = new_wl
              st.success("Đã lưu")
          else:
              st.error("Lưu thất bại — kiểm tra st.secrets")
  ```

BƯỚC 13 — Tooltips
  Mọi st.metric/st.column_config nên có help=help_for('...'):
  ```
  st.metric("📊 RSI", f"{rsi:.1f}", help=help_for('rsi'))
  st.metric("🤖 AI T+3", f"{ai:.1f}%", help=help_for('ai_t3'))
  ```

BƯỚC 14 — A/B Strategy Lab (Tab mới đề xuất)
  ```
  with st.tabs([..., "🧪 Strategy Lab"])[-1]:
      strategies = {
          'baseline':       {'rsi_buy': 45, 'use_macd_cross': True},
          'with_wave':      {'rsi_buy': 45, 'use_macd_cross': True, 'use_wave_filter': True},
          'with_adx':       {'rsi_buy': 45, 'use_macd_cross': True, 'use_adx_filter': True, 'adx_min': 20},
          'wave_and_adx':   {'rsi_buy': 45, 'use_macd_cross': True, 'use_wave_filter': True,
                              'use_adx_filter': True, 'adx_min': 20},
      }
      results = compare_strategies(df, strategies)
      st.dataframe(results, use_container_width=True, hide_index=True)
      # Plot equity curves overlay
      equity_curves = results.attrs.get('equity_curves', {})
      if equity_curves:
          fig = go.Figure()
          for name, eq in equity_curves.items():
              fig.add_trace(go.Scatter(y=eq, name=name, mode='lines'))
          fig.update_layout(title="Equity Curves", xaxis_title="Trade #",
                            yaxis_title="Equity multiple", height=400)
          st.plotly_chart(fig, use_container_width=True)
  ```

================================================================================
CẦN CÀI THÊM DEPENDENCIES
================================================================================

requirements.txt (thêm):
  scipy>=1.10        # divergence find_peaks
  shap>=0.42         # AI explain (optional)
  reportlab>=4.0     # PDF export (optional)

Các dep optional sẽ graceful-degrade nếu không cài (xem HAS_* flags ở đầu file).

================================================================================
KIỂM TRA SAU TÍCH HỢP
================================================================================

1. Chạy: streamlit run app.py
2. Kiểm tra log console không có ImportError
3. Test các điểm:
   • Banner regime hiện đầu trang
   • AI prediction vẫn ra số bình thường (không "N/A" hàng loạt)
   • Backtest có Sharpe khác V23 cũ (sẽ thấp hơn — ĐÚNG)
   • Wave Bottom hiển thị "/12" thay vì "/11"
   • Smart Flow hiển thị "(proxy)" trong label
   • Quick Pick xong → có thông báo correlation
4. Compare 3-5 mã cố định giữa V23 và V24:
   • Điểm scoring có khác ~5-10 (do thêm VWAP và bỏ sent)
   • AI score có khác do walk-forward sửa
   • Sharpe trong backtest THẤP hơn V23 (vì annualize đúng)
5. Nếu BEAR market, Quick Pick trả list rỗng — KHÔNG phải bug.

================================================================================
"""


def print_integration_guide():
    """[NEW] In hướng dẫn tích hợp."""
    print(INTEGRATION_GUIDE)


# ==============================================================================
# #17. SELF-TEST (chạy độc lập để kiểm tra module load OK)
# ==============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("QUANT V24 UPGRADE PACK — SELF TEST")
    print("=" * 70)
    print(f"HAS_SCIPY:       {HAS_SCIPY}")
    print(f"HAS_SHAP:        {HAS_SHAP}")
    print(f"HAS_CALIBRATION: {HAS_CALIBRATION}")
    print(f"HAS_REPORTLAB:   {HAS_REPORTLAB}")
    print("-" * 70)

    # Test bayes_winrate
    print(f"bayes_winrate(6, 8)   = {bayes_winrate(6, 8)} (kỳ vọng ~61%)")
    print(f"bayes_winrate(60, 80) = {bayes_winrate(60, 80)} (kỳ vọng ~72%)")
    print(f"bayes_winrate(0, 0)   = {bayes_winrate(0, 0)} (kỳ vọng 50%)")

    # Test calc_obv vectorized
    df_test = pd.DataFrame({
        'close':  [10, 11, 11, 10, 12, 13],
        'volume': [100, 200, 150, 300, 400, 250],
    })
    obv = calc_obv(df_test)
    print(f"calc_obv vectorized OK: {list(obv.values)}")

    # Test calc_position_size_vol_parity
    vp = calc_position_size_vol_parity(
        capital=100_000_000, entry_price=50_000, atr=1_500,
    )
    print(f"Vol parity 100M, entry 50K, ATR 1.5K → "
          f"shares={vp['shares']}, value={vp['value']:,.0f}, "
          f"risk={vp['dollar_risk']:,.0f}")

    # Test calc_risk_temperature (giả lập)
    fake_regime  = {'regime': 'CAUTIOUS_BULL'}
    fake_breadth = {'pct_above_ma20': 55, 'advance_decline': 52}
    risk = calc_risk_temperature(fake_regime, fake_breadth)
    print(f"Risk temp (CAUTIOUS_BULL, 55% ma20): "
          f"{risk['score']}/100 — {risk['label']}")

    print("=" * 70)
    print("✅ SELF TEST PASSED — module loaded OK")
    print("Run print_integration_guide() để xem hướng dẫn tích hợp đầy đủ.")
    print("=" * 70)
