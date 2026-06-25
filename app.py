# ==============================================================================
# QUANT SYSTEM V24.0 - THE PREDATOR LEVIATHAN APEX
# Tác giả: Minh   |   V24 add-ons by Claude
# ──────────────────────────────────────────────────────────────────────────────
# V22: ATR Stop | ADX+OBV | Kelly | Cache AI | Sharpe+MaxDD | Radar Display
# V23: RS Rating | RSI/MACD Divergence | Market Breadth | VWAP | 52W High |
#      Ichimoku Cloud | Chân Sóng Detection
# V24: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  THÊM (không thay V23 nào):
#    • Market Regime Filter (4 trạng thái thị trường)
#    • Exit Signal System
#    • Smart Flow Proxy (thay foreign flow khi API thiếu)
#    • Vol-Parity Position Sizing
#    • Correlation Check (Quick Pick đa dạng hoá)
#    • A/B Strategy Testing
#    • Risk Thermometer 0-100
#    • Bayesian winrate
#    • Watchlist persistence (Gist + file)
#    • PDF Export, SHAP explain, Parallel scan
#    • Divergence v24 (scipy find_peaks, GIỮ V23 gốc song song)
#  CÁCH DÙNG: V23 base CHẠY Y NGUYÊN. Các V24 function chỉ thêm vào, gọi khi cần.
# ==============================================================================
# --- IMPORTS ---
# ==============================================================================
# Quant System V41 - Rút Chân Detector
# ==============================================================================
# TÍNH NĂNG MỚI: Phát hiện "Rút chân về tham chiếu" (đặc trưng thị trường VN)
#   - Trong phiên giảm sâu rồi BẬT VỀ tham chiếu cuối phiên
#   - Cho thấy lực mua bắt đáy mạnh → thường tăng phiên sau
#
# 3 VỊ TRÍ WIRE:
#   R1 - Section A (Tab Robot Advisor): Box "🦵 Rút Chân"
#   R2 - Tab Radar: Badge "🦵 Rút Chân STRONG"
#   R3 - Tab Early Momentum: Filter + Badge trong card
#
# PHÂN LOẠI:
#   💎 STRONG: recovery ≥85% + drop ≥-4% (lực bắt đáy cực mạnh)
#   🟢 GOOD: recovery ≥70% + drop ≥-3% (lực mua tốt)
#   🟡 MILD: recovery ≥65% + drop ≥-2.5% (hồi nhẹ)
#
# QUALITY SCORE để phân biệt rút chân thật/giả:
#   +10 nếu tại hỗ trợ (gần MA20/MA50)
#   +10 nếu vol nổ (≥1.5x)
#   +10 nếu RSI < 65 (chưa quá mua)
#   -15 nếu trong downtrend mạnh (dead cat bounce)
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V42
# ==============================================================================
# Quant System V40 - Float Analysis + Mini Defensive
# ==============================================================================
# 4 TÍNH NĂNG MỚI (Float):
#   F1 - Float Tier Classifier (HIGH/MED/LOW/VERY_LOW)
#   F2 - Box "📦 Float Analysis" trong Section A (Tab Robot Advisor)
#   F3 - Cảnh báo "Float thấp + Vol nổ = Pump risk"
#   F4 - Badge Float warning trong card Early Momentum & Radar
#
# DEFENSIVE (Mini):
#   D1 - Cache 24h cho trading_stats() — giảm risk hit API
#   D2 - Try/except cứng — fail graceful nếu vnstock vỡ
#
# DATA SOURCE:
#   Hiện tại: vnstock 3.2.6 (trading_stats() trả về free_float_percentage)
#   Tương lai: V41+ sẽ swap sang SSI FastConnect API khi có key
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V41
# ==============================================================================
# Quant System V39 - MA10 Booster (Vạch vàng signal)
# ==============================================================================
# TÍNH NĂNG MỚI:
#   MA10 Cross-Up Signal — phát hiện mã vừa cắt lên MA10 (vạch vàng)
#
# CÁCH 2 (AN TOÀN): Tách function riêng calc_ma10_bonus()
#   - V23 core (calc_total_score) NGUYÊN BẢN
#   - MA10 Bonus là điểm cộng riêng (0-30 điểm)
#   - Có thể bật/tắt, dễ rollback
#
# WIRE 3 CHỖ:
#   M1 - Tab Robot Advisor / Section A: box "🟡 MA10 Signal"
#   M2 - Tab Early Momentum: filter + cột MA10 trên card
#   M3 - Tab Radar: cột MA10 Bonus trong ranking
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V40
# ==============================================================================
# Quant System V38 - Clear Status (Tách rõ XEM/THEO DÕI/ĐÃ MUA)
# ==============================================================================
# 4 GIẢI PHÁP:
#   G1 - Watchlist (theo dõi) tách rõ khỏi Positions (đã mua)
#   G2 - 2 nút riêng: "📌 Thêm Watchlist" vs "💰 Tôi ĐÃ MUA"
#   G4 - Reset nhanh vị thế nhầm (nút xoá với confirm)
#   G5 - Header trạng thái mã ở đầu Tab Robot Advisor
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V39
# ==============================================================================
# Quant System V37 - Early Momentum Scanner
# ==============================================================================
# TÍNH NĂNG MỚI:
#   Tab "🔥 EARLY MOMENTUM" — Phát hiện sớm mã đang trong chuỗi tăng N ngày
#   + E1: avg gain mỗi ngày
#   + E2: xác suất tiếp tục tăng (dựa lịch sử)
#   + E3: cảnh báo RSI quá mua sắp đến
#   + E4: highlight nếu có vol đột biến ngày gần nhất
#
# DISCLAIMER MẠNH:
#   - Mã trong chuỗi tăng KHÔNG có nghĩa "nên mua ngay"
#   - Chỉ ~50% mã tăng 2 ngày sẽ tiếp tục tăng ngày 3
#   - Phải phân tích sâu ở Tab Robot Advisor trước khi vào lệnh
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V38
# ==============================================================================
# Quant System V36 - Combo 4 Features
# ==============================================================================
# 4 TÍNH NĂNG MỚI:
#   N1 - Smart Money Proxy (phát hiện qua price-volume action)
#   N3 - Daily Routine Wizard (tab "🌞 Sáng nay" - quy trình từng bước)
#   N4 - Sector Strength Heatmap mở rộng (20 ngành × 4 timeframes)
#   N6 - Watchlist Theo Ngành (gom theo nhóm)
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V37
# ==============================================================================
# Quant System V35 - Fix V34 dùng E1VFVN30 (vnstock VN-Index 403)
# ==============================================================================
# BUG FIX:
#   - V34 dùng get_vnindex_cached() → 403 Forbidden
#   - V35: Các function V34 nhận df_vni làm tham số (lấy từ session)
#   - Đồng nhất với Tab 6 hiện tại (đã dùng E1VFVN30 thành công)
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V36
# ==============================================================================
# Quant System V34 - VN-Index Decision Helper (Combo B)
# ==============================================================================
# 6 TÍNH NĂNG MỚI vào Tab 6:
#   D1 - Verdict Box (🟢 NÊN MUA / 🟡 THẬN TRỌNG / 🔴 ĐỨNG NGOÀI)
#   D2 - Checklist 10 dấu hiệu (có trọng số → ra điểm tổng)
#   B1 - Market Breadth Dashboard (A/D ratio + % mã trên MA20)
#   B4 - Fear & Greed Index proxy (RSI + Vol + Breadth)
#   B5 - Kháng cự / Hỗ trợ VN-Index gần nhất
#   C1 - Cảnh báo phân kỳ VN-Index (RSI vs Price)
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V35
# ==============================================================================
# Quant System V33 - Rollback về V29 (bỏ Smart Money Scanner)
# ==============================================================================
# LÝ DO ROLLBACK:
#   V30-V32 đã thử thêm Tab Cá Mập (Smart Money Scanner) nhưng:
#   - vnstock 3.2.6 không có API foreign/proprietary trading
#   - FireAnt API bị chặn IP từ Streamlit Cloud (lỗi 403)
#   → Quyết định: TẠM ROLLBACK về V29 (ổn định, không có tính năng "ảo")
#
# NỘI DUNG V33 = V29 ĐẦY ĐỦ:
#   - V23 core (10 functions nguyên bản)
#   - V24: T-M, Q-S-R, H-G, LIQ, Section A/C reorder
#   - V25: Xoá 3 widget duplicate (RR Calc, Trade Journal, Equity Curve)
#   - V26: Xoá Metrics Backtest 4+3 + Chart Signal
#   - V27: Fix KeyError date + ensure_date_col helper
#   - V28: 6 features (L1, L2, A1, A2, P1, R4)
#   - V29: 7 tinh chỉnh (Cache, Try/except, Backup, Cleanup, ...)
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V34 (file mới, không đè)
# ==============================================================================
# Quant System V28 - User Empowerment Combo
# ==============================================================================
# 6 FEATURES MỚI:
#   L1 - Lifetime Stats Dashboard (phân tích sâu trade history)
#   L2 - Pattern Trade Analyzer (tìm pattern thắng/thua của bạn)
#   A1 - Watchlist Rules + Alerts (set rule tự động cảnh báo)
#   A2 - Morning Brief (1 trang tổng hợp khi mở app sáng)
#   P1 - Candlestick Pattern Detector (Hammer, Doji, Engulfing, ...)
#   R4 - Stress Test Portfolio (giả lập VN-Index giảm X%)
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V29 (file mới, không đè)
# ==============================================================================
# Quant System V27_OLD
# ==============================================================================
# Phiên bản: V27
# Bao gồm: V26 + Fix bug:
#   - KeyError 'date' trong "Tương quan ACB vs VN-Index"
#   - Helper ensure_date_col() đảm bảo cột date tồn tại trước khi dùng
#   - Fix lỗi Thanh Khoản hiển thị 0.0 Tỷ (do thiếu cột date)
#
# QUY TẮC VERSIONING:
#   - Update tiếp theo: V28 (file mới, không đè)
# ==============================================================================


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

# ──────────────────────────────────────────────────────────────────────────────
# [V24] IMPORTS BỔ SUNG — Optional dependencies với graceful degrade
# ──────────────────────────────────────────────────────────────────────────────
import os
import json
import io
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

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
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph as RLPar, Spacer,
        Image as RLImage, Table as RLTable, TableStyle,
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
# [V24 END IMPORTS]

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
RSI_WATCHLIST_MAX = 65
# Volume
VOL_BREAKOUT      = 1.5
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
PRICE_NEAR_MA20   = 0.97
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
WAVE_RSI_MAX      = 55          # [V24-HOSE] RSI ≤ 55: chân sóng thực tế HOSE (cũ: 52)
WAVE_RSI_MIN      = 28          # RSI trên 28 = không quá bán thái quá
WAVE_PRICE_MA50   = 0.88        # giá ít nhất 88% MA50
WAVE_SCORE_MIN    = 5           # [V24-HOSE] cần ≥ 5/11 (cũ: 4) — chặt hơn để chất lượng cao
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


# ──────────────────────────────────────────────────────────────────────────────
# [V24] HẰNG SỐ BỔ SUNG
# ──────────────────────────────────────────────────────────────────────────────
REGIME_BREADTH_STRONG = 70
REGIME_BREADTH_OK     = 50
REGIME_BREADTH_WEAK   = 40
REGIME_ADR_STRONG     = 60
REGIME_ADR_OK         = 50

EXIT_RSI_DANGER       = 80
EXIT_RSI_HIGH         = 75
EXIT_VOL_DISTRIBUTION = 2.0
EXIT_SCORE_EXIT_ALL   = 7
EXIT_SCORE_TRIM       = 4
EXIT_SCORE_WATCH      = 2

RISK_PER_TRADE_DEFAULT = 0.01
MAX_POSITION_PCT       = 0.20

CORR_MAX_PAIR     = 0.7
CORR_LOOKBACK     = 60
CORR_FALLBACK_MAX = 0.85

BAYES_PRIOR_WR = 0.5
BAYES_PRIOR_N  = 10

MIN_SIGNALS_RELIABLE = 20
MAX_DATA_DAYS_OLD    = 5

WAVE_MA200_SLOPE_MIN   = 0.998
WAVE_STAGE4_THRESHOLD  = 0.99

SMART_FLOW_LOOKBACK  = 10
SMART_FLOW_MAX_SCORE = 20

WATCHLIST_GIST_FILENAME = 'watchlist.txt'
# [V24 END CONSTANTS]


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
    # [FIX] Vnstock 3.2.6 dùng 'time' thay vì 'date' → auto-rename
    # Hỗ trợ nhiều biến thể: time, Time, TIME, datetime, trading_date
    rename_map = {}
    if 'date' not in df.columns:
        for alt in ['time', 'datetime', 'trading_date', 'tradingdate', 'tradedate']:
            if alt in df.columns:
                rename_map[alt] = 'date'
                break
    if rename_map:
        df = df.rename(columns=rename_map)
    # Nếu index là DatetimeIndex và không có cột date → reset index thành cột date
    if 'date' not in df.columns and isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index()
        if 'index' in df.columns:
            df = df.rename(columns={'index': 'date'})
    return df


def get_date_col(df: pd.DataFrame):
    """[FIX] Lấy series date an toàn từ DataFrame.
    Thử nhiều tên: date → time → index."""
    if df is None or df.empty:
        return None
    if 'date' in df.columns:
        return df['date']
    if 'time' in df.columns:
        return df['time']
    # Fallback: dùng index nếu là DatetimeIndex
    if isinstance(df.index, pd.DatetimeIndex):
        return df.index
    # Cuối cùng: index mặc định (integer)
    return df.index


def ensure_date_col(df: pd.DataFrame) -> pd.DataFrame:
    """[V27-FIX] Đảm bảo DataFrame có cột 'date' để truy cập an toàn.
    Nếu cột 'date' không tồn tại, tự động tạo từ 'time' hoặc index.
    Trả về DataFrame mới (không modify in-place)."""
    if df is None or df.empty:
        return df
    if 'date' in df.columns:
        return df
    df2 = df.copy()
    if 'time' in df2.columns:
        df2['date'] = df2['time']
    elif isinstance(df2.index, pd.DatetimeIndex):
        df2 = df2.reset_index()
        if 'index' in df2.columns:
            df2 = df2.rename(columns={'index': 'date'})
    else:
        # Tạo date giả từ index (integer) — fallback cuối
        df2['date'] = df2.index
    return df2
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
    [V24-FIX] Robust với mọi data source — guard DatetimeIndex.
    """
    df2 = df.copy()
    # [V24-FIX] Đảm bảo có DatetimeIndex trước khi resample
    if 'date' in df2.columns:
        df2['date'] = pd.to_datetime(df2['date'], errors='coerce')
        df2 = df2.dropna(subset=['date'])
        df2 = df2.set_index('date')
    elif 'time' in df2.columns:
        df2['time'] = pd.to_datetime(df2['time'], errors='coerce')
        df2 = df2.dropna(subset=['time'])
        df2 = df2.set_index('time')
    elif not isinstance(df2.index, pd.DatetimeIndex):
        # Không có cách nào convert → trả empty
        return pd.DataFrame(columns=['month', 'avg_ret', 'years', 'std', 'month_name'])
    # Đảm bảo index là DatetimeIndex (nếu reset_index bị nullable)
    if not isinstance(df2.index, pd.DatetimeIndex):
        try:
            df2.index = pd.to_datetime(df2.index, errors='coerce')
        except Exception:
            return pd.DataFrame(columns=['month', 'avg_ret', 'years', 'std', 'month_name'])
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
    recent_highs = []
    for i in range(len(highs)-20, len(highs)-1):
        if i < 3: continue
        if highs[i] == max(highs[max(0,i-3):i+4]):
            recent_highs.append(highs[i])
    if len(recent_highs) >= 2:
        if abs(recent_highs[-1] - recent_highs[-2]) / (recent_highs[-1] + 1e-9) < 0.02:
            result['patterns'].append("🔴 Double Top — Đỉnh kép, cảnh báo đảo chiều giảm")
    # Double Bottom
    recent_lows = []
    for i in range(len(lows)-20, len(lows)-1):
        if i < 3: continue
        if lows[i] == min(lows[max(0,i-3):i+4]):
            recent_lows.append(lows[i])
    if len(recent_lows) >= 2:
        if abs(recent_lows[-1] - recent_lows[-2]) / (recent_lows[-1] + 1e-9) < 0.02:
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
# [#1] QUICK PICK — Tự động đề xuất 3 mã tốt nhất
# ==============================================================================
def quick_pick_stocks(tickers_list: list, ai_min: float = 45.0,
                      n_results: int = 3) -> list[dict]:
    """
    Quét HOSE → lọc theo bộ tiêu chí kết hợp → trả về Top N mã tốt nhất.
    Tiêu chí: AI ≥ ai_min + RSI < 60 + Giá ≥ MA20×0.95 + Chân Sóng ≥ 3/11
    """
    candidates = []
    sample     = list(dict.fromkeys(tickers_list))[:200]
    df_vni     = pd.DataFrame()   # dùng benchmark
    for t in sample:
        try:
            df_q = get_price(t, days=SCAN_DAYS)
            if not valid(df_q) or len(df_q) < 100:
                continue
            df_q   = calc_indicators(df_q)
            # [V24-LIQ] Skip mã thanh khoản thấp
            try:
                _liq_qp = calc_liquidity_tier(df_q)
                if _liq_qp.get('tier') == 'LOW':
                    continue
            except Exception:
                pass
            last_q = df_q.iloc[-1]
            rsi_q  = float(last_q['rsi'])
            price_q= float(last_q['close'])
            ma20_q = float(last_q['ma20'])
            vol_q  = float(last_q['vol_strength'])
            adx_q  = float(last_q.get('adx', 0))
            # Hard filters
            if rsi_q > 60 or rsi_q < 25:     continue
            if price_q < ma20_q * 0.93:       continue
            if vol_q > VOL_BREAKOUT:          continue   # đã bùng nổ rồi
            # AI score
            ai_q = predict_ai_cached(t, price_q)
            if not _is_valid_score(ai_q):     continue
            ai_f = float(ai_q)
            if ai_f < ai_min:                 continue
            # Chân sóng
            w52_q  = calc_52w_info(df_q)
            div_q  = detect_divergence(df_q)
            wave_q = calc_wave_bottom_score(df_q, last_q,
                         near_52w_high=w52_q['near_high'],
                         div_bullish=(div_q['signal']=='BULLISH'))
            rs_q   = calc_rs_rating(df_q, df_vni)
            weekly_q = get_weekly_trend(df_q)
            atr_q  = float(last_q.get('atr', price_q * 0.02))
            sl_q   = price_q - ATR_MULTIPLIER * atr_q
            tp2_q  = price_q + 2 * ATR_MULTIPLIER * atr_q
            tp3_q  = price_q + 3 * ATR_MULTIPLIER * atr_q
            # Composite score
            score_q = (ai_f * 0.4 + rs_q * 0.25 +
                       wave_q['score'] * 4 +
                       (10 if weekly_q=='UP' else 0) +
                       (5 if adx_q > 20 else 0))
            candidates.append({
                'ticker':    t,
                'price':     round(price_q, 0),
                'ai':        round(ai_f, 1),
                'rsi':       round(rsi_q, 1),
                'rs':        round(rs_q, 1),
                'vol':       round(vol_q, 2),
                'adx':       round(adx_q, 1),
                'weekly':    weekly_q,
                'wave':      wave_q['score'],
                'wave_flags':wave_q['flags'],
                'sl':        round(sl_q, 0),
                'tp2':       round(tp2_q, 0),
                'tp3':       round(tp3_q, 0),
                'sl_pct':    round((sl_q-price_q)/price_q*100, 2),
                'tp2_pct':   round((tp2_q-price_q)/price_q*100, 2),
                'sector':    get_ticker_sector(t) or 'Khác',
                'score':     round(score_q, 1),
            })
        except Exception as e:
            print(f"[WARN] quickpick {t}: {e}")
            continue
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:n_results]
# ==============================================================================
# [#2] PORTFOLIO BACKTEST — Backtest danh mục nhiều mã
# ==============================================================================
def portfolio_backtest(tickers_weights: dict, days: int = 500) -> dict:
    """
    Backtest danh mục theo tỷ trọng.
    tickers_weights: {'FPT': 0.4, 'ACB': 0.3, 'HPG': 0.3}
    """
    port_returns = []
    ticker_results = {}
    for t, w in tickers_weights.items():
        try:
            df_p = get_price(t, days=days)
            if not valid(df_p) or len(df_p) < 100:
                continue
            df_p  = calc_indicators(df_p)
            bt_p  = run_backtest(df_p)
            ticker_results[t] = {'weight': w, 'bt': bt_p}
            # Đóng góp vào portfolio return
            for p in bt_p.get('profits', []):
                port_returns.append(p * w)
        except Exception:
            continue
    if not port_returns:
        return {'error': 'Không đủ dữ liệu'}
    port_arr   = np.array(port_returns)
    equity     = np.cumprod([1 + p for p in port_returns])
    rolling_max= np.maximum.accumulate(equity)
    max_dd     = round(((equity - rolling_max)/rolling_max).min()*100, 2)
    rf_daily   = 0.045/252
    excess     = port_arr - rf_daily
    sharpe     = round((excess.mean()/(excess.std()+1e-9))*np.sqrt(252/BT_DAYS_FWD), 2)
    total_ret  = round((equity[-1] - 1) * 100, 2)
    return {
        'total_return':   total_ret,
        'max_drawdown':   max_dd,
        'sharpe':         sharpe,
        'n_signals':      len(port_returns),
        'equity_curve':   equity.tolist(),
        'ticker_results': ticker_results,
    }
# ==============================================================================
# [#3] EVENT VOLUME ANALYSIS — Phân tích biến động trước/sau Vol đột biến
# ==============================================================================
def analyze_volume_events(df: pd.DataFrame, vol_threshold: float = 2.0) -> list[dict]:
    """
    Tìm các ngày Vol đột biến (> vol_threshold × MA10).
    Phân tích giá biến động thế nào trong 5 phiên trước/sau.
    """
    events = []
    if len(df) < 30:
        return events
    for i in range(10, len(df)-5):
        vol_s = df['vol_strength'].iloc[i]
        if vol_s < vol_threshold:
            continue
        ret_before = (df['close'].iloc[i] - df['close'].iloc[i-5]) / df['close'].iloc[i-5] * 100
        ret_after  = (df['close'].iloc[i+5] - df['close'].iloc[i]) / df['close'].iloc[i] * 100
        date_ev    = str(df['date'].iloc[i])[:10] if 'date' in df.columns else i
        events.append({
            'date':       date_ev,
            'vol':        round(float(vol_s), 2),
            'ret_day':    round(float(df['return_1d'].iloc[i])*100, 2),
            'ret_before': round(ret_before, 2),
            'ret_after':  round(ret_after, 2),
            'was_bull':   df['return_1d'].iloc[i] > 0,
        })
    return events
# ==============================================================================
# [#4] SCORE TIMELINE — Lưu & vẽ lịch sử điểm số
# ==============================================================================
def save_score_history(ticker: str, score: float, ai: float) -> None:
    """Lưu điểm vào session_state theo ngày."""
    key = 'score_history'
    if key not in st.session_state:
        st.session_state[key] = {}
    if ticker not in st.session_state[key]:
        st.session_state[key][ticker] = []
    today = now_vn().strftime('%Y-%m-%d')
    history = st.session_state[key][ticker]
    # Tránh lưu trùng cùng ngày
    if not history or history[-1]['date'] != today:
        history.append({'date': today, 'score': score, 'ai': ai})
    st.session_state[key][ticker] = history[-30:]   # giữ 30 điểm gần nhất
def get_score_history(ticker: str) -> list:
    return st.session_state.get('score_history', {}).get(ticker, [])
# ==============================================================================
# [#5] LIQUIDITY ANALYSIS — Phân tích thanh khoản thực
# ==============================================================================
def analyze_liquidity(df: pd.DataFrame, ticker: str) -> dict:
    """
    Ước tính thanh khoản: spread, impact cost, thanh khoản tốt nhất.
    Dùng ATR và Vol để ước tính bid-ask spread và slippage thực tế.
    """
    if len(df) < 20:
        return {}
    last    = df.iloc[-1]
    price   = float(last['close'])
    atr     = float(last.get('atr', price*0.02))
    vol_avg = float(df['volume'].tail(20).mean())
    vol_val = vol_avg * price / 1e9   # tỷ VNĐ/phiên
    # Ước tính spread (ATR-based)
    spread_est  = atr * 0.1           # spread ≈ 10% ATR
    spread_pct  = spread_est / price * 100
    # Impact cost khi mua N tỷ
    impact_1ty  = 1e9 / (vol_avg * price + 1e-9) * atr * 100   # % slippage khi mua 1 tỷ
    impact_5ty  = impact_1ty * 5
    impact_10ty = impact_1ty * 10
    # Phân loại thanh khoản
    if vol_val >= 10:
        liq_label = "🟢 Thanh khoản rất tốt — Vào/ra dễ dàng"
        liq_color = "success"
    elif vol_val >= 3:
        liq_label = "🟡 Thanh khoản khá — Vào/ra bình thường"
        liq_color = "warning"
    elif vol_val >= 1:
        liq_label = "🟠 Thanh khoản trung bình — Cẩn thận khi vào lệnh lớn"
        liq_color = "warning"
    else:
        liq_label = "🔴 Thanh khoản thấp — Rủi ro slippage cao"
        liq_color = "error"
    # Thời điểm thanh khoản tốt (ước tính VN market)
    best_times = "09:15-09:45 (mở cửa) | 14:00-14:30 (chiều) | 14:30-14:45 (đóng cửa ATC)"
    return {
        'vol_avg_bn':  round(vol_val, 2),
        'spread_pct':  round(spread_pct, 3),
        'impact_1ty':  round(impact_1ty, 3),
        'impact_5ty':  round(impact_5ty, 3),
        'impact_10ty': round(impact_10ty, 3),
        'liq_label':   liq_label,
        'liq_color':   liq_color,
        'best_times':  best_times,
    }
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
    🚀 Bùng Nổ | 🎯 Sẵn Sàng Bùng Nổ | 🌱 Đang Tích Lũy Nền | 👁️ Vùng Quan Sát
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
    # TẦNG 2: Sẵn Sàng Bùng Nổ — tiêu chí chặt, an toàn nhất
    base_ok = (
        VOL_ACC_MIN <= vol <= VOL_ACC_MAX and
        price >= ma20 * PRICE_NEAR_MA20   and
        rsi < RSI_WATCHLIST_MAX           and
        ai_ok
    )
    if base_ok and weapons >= 1 and weekly_trend in ('UP', 'NEUTRAL'):
        return "🎯 Sẵn Sàng Bùng Nổ"
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
            return "🌱 Đang Tích Lũy Nền"
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
            # [V24-W3] Cảnh báo mã yếu tương đối
            if rs is not None and rs < 50:
                st.warning(f"⚠️ YẾU TƯƠNG ĐỐI (RS={rs:.0f}<50) — KHÔNG khuyến nghị mua")
            # [V24-W2] Hiện lý do bị đẩy xuống Quan Sát
            if row.get('_liq_warning'):
                st.caption(row['_liq_warning'])
            if row.get('_rs_warning'):
                st.caption(row['_rs_warning'])
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
            # [V39-M3] MA10 badge
            if row.get('MA10 Cross Up'):   badges.append("⭐ MA10 Cross-Up (V39)")
            # [V40-F4] Float warning badge
            float_tier_r = row.get('Float Tier')
            float_pct_r = row.get('Float Pct', 0)
            if float_tier_r == 'VERY_LOW':
                badges.append(f"🔴 Float CỰC thấp ({float_pct_r:.0f}%)")
            elif float_tier_r == 'LOW':
                badges.append(f"🟠 Float thấp ({float_pct_r:.0f}%)")
            # [V41-R2] Rút Chân badge
            rc_sig_r = row.get('RC Signal')
            rc_q_r = row.get('RC Quality', 0)
            if rc_sig_r == 'STRONG' and rc_q_r >= 60:
                badges.append(f"💎 Rút Chân STRONG (Q{rc_q_r})")
            elif rc_sig_r == 'GOOD' and rc_q_r >= 50:
                badges.append(f"🟢 Rút Chân GOOD (Q{rc_q_r})")
            elif rc_sig_r == 'MILD':
                badges.append(f"🟡 Rút Chân MILD")
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
    c4.metric("🎯 Sẵn Sàng Bùng Nổ",  len(watchlist),
              delta="✅ Ưu tiên" if watchlist else None,
              delta_color="normal" if watchlist else "off")
    c5.metric("🌱 Tích Lũy Nền",      len(wave_bottom),
              delta="🎯 Cơ hội sớm" if wave_bottom else None,
              delta_color="normal" if wave_bottom else "off")
    c6.metric("👁️ Quan Sát",       len(watch_zone),  delta_color="off")
    c7.metric("🔥 Đang Tăng Mạnh", len(running_strong),
              delta="Không mua đuổi" if running_strong else None, delta_color="off")
# ==============================================================================


# ==============================================================================
# [V24] NEW FUNCTIONS — Bổ sung tính năng V24 (không thay thế V23)
# ==============================================================================

# ──────────────────────────────────────────────────────────────────────────────
# Bayesian winrate
# ──────────────────────────────────────────────────────────────────────────────
def bayes_winrate(wins: int, total: int,
                   prior_winrate: float = BAYES_PRIOR_WR,
                   prior_n: float = BAYES_PRIOR_N) -> float:
    """[V24] Bayesian-shrunk winrate. Sample nhỏ → kéo về prior 50%.
    Ví dụ: 6/8 = 75% thô → 61% Bayes."""
    if total <= 0:
        return round(prior_winrate * 100, 1)
    adjusted_wins = wins + prior_winrate * prior_n
    adjusted_n    = total + prior_n
    return round(adjusted_wins / adjusted_n * 100, 1)


def is_data_fresh(df, max_days_old: int = MAX_DATA_DAYS_OLD) -> bool:
    """[V24] Check dữ liệu có cập nhật trong N ngày qua không."""
    if not valid(df) or 'date' not in df.columns:
        return False
    try:
        # [V27-FIX] Use get_date_col để tránh KeyError
        _date_series = get_date_col(df)
        if _date_series is None or len(_date_series) == 0:
            return None
        last_date = pd.to_datetime(_date_series.iloc[-1] if hasattr(_date_series, 'iloc') else _date_series[-1])
        days_old = (datetime.now() - last_date).days
        return days_old <= max_days_old
    except Exception:
        return False


def is_backtest_significant(bt: dict, min_signals: int = MIN_SIGNALS_RELIABLE):
    """[V24] Check backtest đủ signals?"""
    n = bt.get('signals', 0)
    if n < min_signals:
        return False, f"⚠️ Chỉ {n} signals — không đủ tin cậy (cần ≥{min_signals})"
    return True, f"✅ Đủ sample ({n} signals)"


# ──────────────────────────────────────────────────────────────────────────────
# Smart Flow Proxy — proxy cho dòng tiền tổ chức khi không có dữ liệu khối ngoại
# ──────────────────────────────────────────────────────────────────────────────
def smart_flow_proxy(df, lookback: int = SMART_FLOW_LOOKBACK) -> dict:
    """[V24] Proxy 'tổ chức gom' khi không có dữ liệu khối ngoại thực tế.
    Output tương thích với foreign_trend dict."""
    if len(df) < lookback + 20:
        return {'score': 0, 'trend': 'UNKNOWN',
                'label': '❓ Thiếu dữ liệu', 'flags': [], 'is_proxy': True}

    recent      = df.tail(lookback)
    obv_z_now   = float(recent['obv_zscore'].iloc[-1]) if 'obv_zscore' in recent.columns else 0
    obv_z_mean  = float(recent['obv_zscore'].mean())   if 'obv_zscore' in recent.columns else 0
    vol_stable  = int(((recent['vol_strength'] >= 0.9) & (recent['vol_strength'] <= 1.6)).sum())
    price_ok    = int((recent['return_1d'] >= -0.02).sum())
    close_above = int((recent['close'] > recent['ma20']).sum())

    score, flags = 0, []
    if obv_z_now > 0.5:    score += 5; flags.append('OBV tích cực')
    if obv_z_mean > 0:     score += 4; flags.append('OBV xu hướng tăng')
    if vol_stable >= 7:    score += 4; flags.append('Vol ổn định')
    if price_ok >= 7:      score += 4; flags.append('Giá giữ vững')
    if close_above >= 6:   score += 3; flags.append('Trên MA20 đa số phiên')

    if   score >= 16: trend, label = 'STRONG_BUY', '🟢🟢 Có dấu hiệu gom mạnh (proxy)'
    elif score >= 11: trend, label = 'BUY',        '🟢 Có dấu hiệu gom (proxy)'
    elif score >= 6:  trend, label = 'NEUTRAL',    '⚪ Trung lập (proxy)'
    else:             trend, label = 'WEAK',       '🔴 Thiếu lực gom (proxy)'

    return {'score': score, 'trend': trend, 'label': label,
            'flags': flags, 'is_proxy': True}


# ──────────────────────────────────────────────────────────────────────────────
# Market Regime Filter
# ──────────────────────────────────────────────────────────────────────────────
def detect_market_regime(df_vni, breadth: dict) -> dict:
    """[V24] Phát hiện trạng thái thị trường (4 regimes)."""
    if not valid(df_vni) or len(df_vni) < 210:
        return {'regime': 'UNKNOWN', 'size_mult': 0.3, 'buy_allowed': True,
                'min_score_buy': SCORE_BUY_MIN + 5,
                'label': '❓ UNKNOWN — Thiếu dữ liệu VN-Index',
                'above_50': False, 'above_200': False,
                'pct_ma20': 0, 'adr': 0}

    vni = df_vni.copy()
    vni['ma50']  = vni['close'].rolling(50).mean()
    vni['ma200'] = vni['close'].rolling(200).mean()
    last = vni.iloc[-1]
    above_50  = bool(last['close'] > last['ma50'])
    above_200 = bool(last['close'] > last['ma200'])
    pct_ma20  = float(breadth.get('pct_above_ma20', 50))
    adr       = float(breadth.get('advance_decline', 50))
    base = {'above_50': above_50, 'above_200': above_200,
            'pct_ma20': pct_ma20, 'adr': adr}

    if above_50 and above_200 and pct_ma20 >= REGIME_BREADTH_STRONG and adr >= REGIME_ADR_STRONG:
        return {**base, 'regime': 'STRONG_BULL', 'size_mult': 1.0,
                'buy_allowed': True, 'min_score_buy': SCORE_BUY_MIN,
                'label': '🟢 STRONG BULL — Mua tích cực'}
    if above_50 and (pct_ma20 >= REGIME_BREADTH_OK or adr >= REGIME_ADR_OK):
        return {**base, 'regime': 'CAUTIOUS_BULL', 'size_mult': 0.6,
                'buy_allowed': True, 'min_score_buy': SCORE_BUY_MIN + 5,
                'label': '🟡 CAUTIOUS BULL — Mua chọn lọc'}
    if (not above_50 and not above_200) and pct_ma20 < REGIME_BREADTH_WEAK:
        return {**base, 'regime': 'BEAR', 'size_mult': 0.0,
                'buy_allowed': False, 'min_score_buy': 999,
                'label': '🔴 BEAR — KHÔNG mở vị thế mới'}
    return {**base, 'regime': 'MIXED', 'size_mult': 0.3,
            'buy_allowed': True, 'min_score_buy': SCORE_BUY_MIN + 10,
            'label': '🟠 MIXED — Chỉ mã siêu mạnh (RS≥80)'}


def render_market_regime_banner(regime: dict, breadth: dict) -> None:
    """[V24] Banner trạng thái thị trường."""
    c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5])
    with c1:
        st.markdown(f"### {regime['label']}")
        st.caption(f"VNI vs MA50: {'✅' if regime['above_50'] else '❌'} | "
                   f"vs MA200: {'✅' if regime['above_200'] else '❌'}")
    with c2:
        st.metric("% > MA20", f"{regime['pct_ma20']:.0f}%",
                  help="Tỷ lệ mã đóng trên MA20")
    with c3:
        st.metric("Adv/Decl", f"{regime['adr']:.0f}%",
                  help="Tỷ lệ mã tăng giá")
    with c4:
        if regime['buy_allowed']:
            st.metric("Điểm BUY tối thiểu", f"{regime['min_score_buy']}/90")
        else:
            st.metric("Vị thế mới", "❌ KHÔNG", delta="Bảo vệ vốn",
                      delta_color="inverse")
    if not regime['buy_allowed']:
        st.error("🔴 Thị trường BEAR — Hệ thống đề nghị KHÔNG mở vị thế mới.")
    elif regime['regime'] == 'MIXED':
        st.warning("🟠 Thị trường phân hoá — chỉ vào lệnh với mã RS Rating ≥ 80.")


# ──────────────────────────────────────────────────────────────────────────────
# Exit Signal System
# ──────────────────────────────────────────────────────────────────────────────
def generate_exit_signal(last, df, entry_price: float, current_price: float,
                          weekly_trend: str, divergence: dict, ai_score) -> dict:
    """[V24] Tín hiệu THOÁT độc lập với SL/TP."""
    red_flags, score = [], 0
    rsi = float(last['rsi'])
    macd, sig = float(last['macd']), float(last['signal'])
    adx = float(last.get('adx', 0))
    vol = float(last['vol_strength'])
    ret = float(last.get('return_1d', 0))

    if rsi >= EXIT_RSI_DANGER:
        red_flags.append(f"🔴 RSI {rsi:.1f} ≥ {EXIT_RSI_DANGER} — vùng quá mua nguy hiểm")
        score += 3
    elif rsi >= EXIT_RSI_HIGH and ret < 0:
        red_flags.append(f"🟠 RSI {rsi:.1f} cao + nến đỏ")
        score += 2

    if len(df) >= 2:
        macd_prev = float(df['macd'].iloc[-2])
        sig_prev  = float(df['signal'].iloc[-2])
        if macd_prev > sig_prev and macd < sig:
            red_flags.append("🔴 MACD vừa cắt xuống signal"); score += 2

    if divergence and divergence.get('signal') == 'BEARISH':
        red_flags.append("🔴 Phân kỳ âm xác nhận"); score += 3
    if weekly_trend == 'DOWN':
        red_flags.append("🔴 Weekly đã đảo về DOWN"); score += 3
    if vol > EXIT_VOL_DISTRIBUTION and ret < -0.02:
        red_flags.append(f"🔴 Distribution day — Vol {vol:.1f}x + giảm {ret*100:.1f}%")
        score += 4
    if len(df) >= 5:
        adx_5d_ago = float(df['adx'].iloc[-5])
        if adx < 20 and adx_5d_ago > 30:
            red_flags.append(f"🟠 ADX suy yếu: {adx_5d_ago:.1f} → {adx:.1f}"); score += 2
    if _is_valid_score(ai_score) and float(ai_score) < 40:
        red_flags.append(f"🔴 AI T+3 chỉ {float(ai_score):.1f}% — đảo chiều"); score += 2

    ma20 = float(last['ma20'])
    if len(df) >= 3 and current_price < ma20 * 0.98:
        was_above = float(df['close'].iloc[-3]) > float(df['ma20'].iloc[-3])
        if was_above:
            red_flags.append("🟠 Vừa rớt khỏi MA20"); score += 2

    pnl_pct = (current_price - entry_price) / entry_price * 100

    if score >= EXIT_SCORE_EXIT_ALL:
        return {'action':'EXIT_ALL','score':score,'flags':red_flags,
                'label':f'🚨 THOÁT TOÀN BỘ — {len(red_flags)} cảnh báo nghiêm trọng',
                'color':'error','pnl_pct':round(pnl_pct,2)}
    if score >= EXIT_SCORE_TRIM:
        return {'action':'TRIM_50','score':score,'flags':red_flags,
                'label':'⚠️ CHỐT 50% — Bảo toàn lợi nhuận, dời SL về breakeven',
                'color':'warning','pnl_pct':round(pnl_pct,2)}
    if score >= EXIT_SCORE_WATCH:
        return {'action':'WATCH','score':score,'flags':red_flags,
                'label':'👁️ THEO DÕI CHẶT — Chuẩn bị tâm lý thoát',
                'color':'warning','pnl_pct':round(pnl_pct,2)}
    return {'action':'HOLD','score':score,
            'flags':red_flags or ['✅ Chưa có red flag'],
            'label':'✅ TIẾP TỤC GIỮ','color':'success',
            'pnl_pct':round(pnl_pct,2)}


def render_exit_signal_card(exit_sig: dict, current_price: float,
                              entry_price: float, shares: int) -> None:
    """[V24] Card hiển thị tín hiệu thoát."""
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.markdown(f"### {exit_sig['label']}")
            st.caption(f"Red flag score: {exit_sig['score']}")
        with c2:
            st.metric("P&L", f"{exit_sig['pnl_pct']:+.2f}%",
                      delta=f"{(current_price-entry_price)*shares:+,.0f} đ")
        with c3:
            action = exit_sig['action']
            if   action == 'EXIT_ALL': st.error("THOÁT NGAY")
            elif action == 'TRIM_50':  st.warning("CHỐT 50%")
            elif action == 'WATCH':    st.warning("THEO DÕI")
            else:                       st.success("GIỮ")
        with st.expander("Chi tiết red flags", expanded=(exit_sig['score']>=2)):
            for f in exit_sig['flags']:
                st.write(f)


# ──────────────────────────────────────────────────────────────────────────────
# Position Sizing — Vol Parity
# ──────────────────────────────────────────────────────────────────────────────
def calc_position_size_vol_parity(capital: float, entry_price: float, atr: float,
                                    risk_per_trade: float = RISK_PER_TRADE_DEFAULT,
                                    max_size_pct: float = MAX_POSITION_PCT,
                                    size_mult: float = 1.0) -> dict:
    """[V24] Position sizing theo dollar-risk constant."""
    if atr <= 0 or entry_price <= 0 or capital <= 0:
        return {'shares':0,'value':0,'size_pct':0,'dollar_risk':0,
                'risk_per_share':0,'sl_price':0,'tp2_price':0,'tp3_price':0}

    risk_per_share = ATR_MULTIPLIER * atr
    dollar_risk    = capital * risk_per_trade * size_mult
    shares_by_risk = dollar_risk / risk_per_share
    max_shares     = (capital * max_size_pct * size_mult) / entry_price
    shares = int(min(shares_by_risk, max_shares) // 100 * 100)
    value  = shares * entry_price

    return {
        'shares': shares, 'value': round(value, 0),
        'size_pct': round(value / capital * 100, 2) if capital > 0 else 0,
        'dollar_risk': round(dollar_risk, 0),
        'risk_per_share': round(risk_per_share, 0),
        'sl_price': round(entry_price - risk_per_share, 0),
        'tp2_price': round(entry_price + 2 * risk_per_share, 0),
        'tp3_price': round(entry_price + 3 * risk_per_share, 0),
        'r_multiple_tp2': 2.0, 'r_multiple_tp3': 3.0,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Correlation Check
# ──────────────────────────────────────────────────────────────────────────────
def diversified_top_pick(candidates: list, n: int = 3,
                          max_corr: float = CORR_MAX_PAIR,
                          days_corr: int = CORR_LOOKBACK) -> list:
    """[V24] Top N candidates với correlation < max_corr."""
    if len(candidates) <= n:
        return candidates[:n]

    price_dict = {}
    for c in candidates:
        t = c.get('ticker')
        if not t: continue
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

    selected = []
    for c in candidates:
        t = c.get('ticker')
        if t not in corr_matrix.columns: continue
        if not selected:
            selected.append(c); continue
        max_pair = max(corr_matrix.loc[t, s['ticker']]
                        for s in selected if s.get('ticker') in corr_matrix.columns)
        if max_pair < max_corr:
            selected.append(c)
            c['_max_corr_to_selected'] = round(float(max_pair), 2)
        if len(selected) >= n: break

    if len(selected) < n:
        for c in candidates:
            if c not in selected and len(selected) < n:
                selected.append(c)

    return selected[:n]


# ──────────────────────────────────────────────────────────────────────────────
# Risk Thermometer
# ──────────────────────────────────────────────────────────────────────────────
def calc_risk_temperature(regime: dict, breadth: dict,
                            portfolio_metrics: dict = None) -> dict:
    """[V24] Nhiệt kế rủi ro 0-100."""
    regime_map = {'STRONG_BULL':10,'CAUTIOUS_BULL':30,'UNKNOWN':50,'MIXED':60,'BEAR':90}
    components = {'market_regime': regime_map.get(regime.get('regime','UNKNOWN'), 50)}

    pct_ma20 = float(breadth.get('pct_above_ma20', 50))
    if   pct_ma20 >= 70: c2 = 10
    elif pct_ma20 >= 50: c2 = 30
    elif pct_ma20 >= 40: c2 = 60
    else:                c2 = 85
    components['breadth'] = c2

    if portfolio_metrics:
        dd = abs(portfolio_metrics.get('dd_pct', 0))
        components['drawdown'] = 10 if dd<3 else (35 if dd<7 else (65 if dd<12 else 90))
        pct_hot = portfolio_metrics.get('pct_rsi_overheat', 0)
        components['rsi_overheat'] = 15 if pct_hot<10 else (40 if pct_hot<30 else (70 if pct_hot<50 else 90))
        conc = portfolio_metrics.get('concentration_sector_pct', 0)
        components['concentration'] = 15 if conc<30 else (45 if conc<50 else (70 if conc<70 else 90))
    else:
        components.update({'drawdown':30,'rsi_overheat':30,'concentration':30})

    weights = {'market_regime':0.40,'breadth':0.15,'drawdown':0.20,
                'rsi_overheat':0.15,'concentration':0.10}
    total = round(sum(components[k] * weights[k] for k in components), 1)

    if   total < 25: emoji, label = '🟢', 'AN TOÀN'
    elif total < 50: emoji, label = '🟡', 'BÌNH THƯỜNG'
    elif total < 75: emoji, label = '🟠', 'CẨN TRỌNG'
    else:            emoji, label = '🔴', 'NGUY HIỂM'

    return {'score':total,'emoji':emoji,'label':label,
            'components':components,'weights':weights}


def render_risk_thermometer(risk: dict) -> None:
    """[V24] Widget nhiệt kế rủi ro."""
    st.markdown(f"### {risk['emoji']} Nhiệt kế rủi ro: **{risk['score']}/100** — {risk['label']}")
    with st.expander("Chi tiết các thành phần"):
        for k in risk['components']:
            c1, c2, c3 = st.columns([2,1,1])
            c1.write(f"**{k.replace('_',' ').title()}**")
            c2.write(f"{risk['components'][k]:.0f}/100")
            c3.write(f"trọng số {risk['weights'][k]*100:.0f}%")


# ──────────────────────────────────────────────────────────────────────────────
# UI helpers — Tooltips
# ──────────────────────────────────────────────────────────────────────────────
METRIC_HELP = {
    'rsi':        'RSI 14: <30 quá bán, >70 quá mua',
    'macd':       'MACD = EMA12 - EMA26. >Signal = bullish',
    'adx':        'ADX: >25 trend mạnh, <20 sideways',
    'obv':        'OBV: tích lũy volume theo chiều giá',
    'atr':        'ATR: thước đo biến động thực tế',
    'rs_rating':  'RS vs VN-Index 3 tháng. 🔥≥80 ✅≥65 🟡≥45 🔴<45',
    'sharpe':     'Sharpe: >1 tốt, >1.5 rất tốt, >2 nghi overfit',
    'max_dd':     'Max DD: % sụt lớn nhất. <10% tốt, >20% nguy hiểm',
    'winrate':    'Tỷ lệ thắng. Sample <30 nên xem Bayesian',
    'expectancy': 'Lợi nhuận kỳ vọng/lệnh (%). >0 = có edge',
    'vwap':       'VWAP 20: giá>VWAP = phe mua chủ động',
    'kelly':      'Half-Kelly: % vốn tối ưu',
    'ai_t3':      'Xác suất AI giá tăng ≥2% trong 3 phiên',
    'wave_bot':   'Chân Sóng: 11 tiêu chí, cần ≥4',
    'divergence': 'Phân kỳ giá vs động lượng',
    '52w_high':   'Tỷ lệ so với đỉnh 52 tuần',
    'regime':     'Trạng thái thị trường tổng thể',
}

def help_for(metric_key: str) -> str:
    """[V24] Lấy tooltip."""
    return METRIC_HELP.get(metric_key, '')


# ──────────────────────────────────────────────────────────────────────────────
# Strategy A/B Testing
# ──────────────────────────────────────────────────────────────────────────────


def compare_strategies(df, strategies: dict) -> pd.DataFrame:
    """[V24] So sánh nhiều variant strategy."""
    rows, equity_curves = [], {}
    for name, params in strategies.items():
        try:
            bt = run_backtest_param(df, **params)
            rows.append({'Strategy':name,'Signals':bt['signals'],
                         'Winrate (%)':bt['winrate'],'Expectancy (%)':bt['expectancy'],
                         'Sharpe':bt['sharpe'],'Max DD (%)':bt['max_drawdown'],
                         'Sigs/Year':bt.get('signals_per_year',0)})
            if bt['profits']:
                equity_curves[name] = np.cumprod([1+p for p in bt['profits']]).tolist()
        except Exception as e:
            rows.append({'Strategy':name,'Error':str(e)[:50]})

    df_out = pd.DataFrame(rows)
    df_out.attrs['equity_curves'] = equity_curves
    return df_out


# ──────────────────────────────────────────────────────────────────────────────
# Parallel scan
# ──────────────────────────────────────────────────────────────────────────────
def scan_parallel(tickers: list, scan_fn,
                   max_workers: int = 10, show_progress: bool = True,
                   timeout_per_task: int = 30) -> list:
    """[V24] Quét song song. scan_fn(ticker) -> result or None."""
    results = []
    total = len(tickers)
    if total == 0: return results

    progress = st.progress(0) if show_progress else None
    status   = st.empty()    if show_progress else None
    done = 0

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(scan_fn, t): t for t in tickers}
        for f in as_completed(futures):
            t = futures[f]
            try:
                r = f.result(timeout=timeout_per_task)
                if r is not None: results.append(r)
            except Exception as e:
                print(f"[WARN] scan_parallel {t}: {e}")
            done += 1
            if show_progress:
                progress.progress(done / total)
                status.caption(f"⏳ Đã quét {done}/{total} (đang xử lý: {t})")

    if show_progress:
        progress.empty(); status.empty()
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Watchlist persistence (Gist + fallback file)
# ──────────────────────────────────────────────────────────────────────────────
def load_watchlist_from_gist() -> list:
    """[V24] Đọc watchlist từ private GitHub Gist."""
    if not HAS_REQUESTS: return []
    try:
        gist_id = st.secrets.get('gist_id', '')
        token   = st.secrets.get('github_token', '')
        if not gist_id or not token: return []
        r = requests.get(f"https://api.github.com/gists/{gist_id}",
                          headers={'Authorization': f'token {token}'}, timeout=5)
        if r.status_code != 200: return []
        data = r.json()
        if WATCHLIST_GIST_FILENAME not in data.get('files', {}):
            return []
        content = data['files'][WATCHLIST_GIST_FILENAME]['content']
        return [x.strip().upper() for x in content.splitlines() if x.strip()]
    except Exception as e:
        print(f"[WARN] save_watchlist: {e}")
        return False


def load_watchlist_from_file(path: str = 'watchlist.json') -> list:
    try:
        if not os.path.exists(path): return []
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_watchlist_to_file(tickers: list, path: str = 'watchlist.json') -> bool:
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(sorted(set(t.upper() for t in tickers)), f,
                      ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def watchlist_persist(tickers: list) -> bool:
    """[V24] Persist: thử Gist trước, fallback file."""
    return save_watchlist_to_gist(tickers) or save_watchlist_to_file(tickers)


def watchlist_load() -> list:
    """[V24] Load: thử Gist trước, fallback file."""
    return load_watchlist_from_gist() or load_watchlist_from_file()


# ──────────────────────────────────────────────────────────────────────────────
# PDF Export
# ──────────────────────────────────────────────────────────────────────────────
def export_stock_report_pdf(ticker: str, scoring: dict, last, bt: dict,
                              ai_score, kelly_pct: float, entry_signal: dict,
                              chart_png_bytes: bytes = None, extra_sections: dict = None):
    """[V24] Xuất báo cáo PDF."""
    if not HAS_REPORTLAB:
        print("[WARN] reportlab chưa cài")
        return None

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
    flow.append(RLPar(f"<i>Thời gian: {datetime.now().strftime('%H:%M %d/%m/%Y')}</i>", body))
    flow.append(Spacer(1, 12))

    flow.append(RLPar("Tổng kết", h2))
    summary = [
        ['Điểm tổng hợp', f"{scoring['total']}/90"],
        ['Quyết định',    scoring['decision']],
        ['Giá hiện tại',  f"{float(last['close']):,.0f}"],
        ['AI T+3',        f"{float(ai_score):.1f}%" if _is_valid_score(ai_score) else "N/A"],
        ['RSI',           f"{float(last['rsi']):.1f}"],
        ['Half-Kelly',    f"{kelly_pct:.1f}% vốn"],
    ]
    t = RLTable(summary, colWidths=[120, 360])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#E7EAF6')),
        ('FONT',(0,0),(-1,-1),'Helvetica',10),
        ('GRID',(0,0),(-1,-1),0.4,colors.grey),
        ('PADDING',(0,0),(-1,-1),6),
    ]))
    flow.append(t); flow.append(Spacer(1, 12))

    flow.append(RLPar("Phân tích điểm số", h2))
    sb = [['Thành phần','Điểm','Tối đa'],
           ['AI',str(scoring['ai_pts']),'25'],
           ['Kỹ thuật',str(scoring['tech_pts']),'20'],
           ['Dòng tiền',str(scoring['flow_pts']),'20'],
           ['Tài chính',str(scoring['fin_pts']),'15'],
           ['Ngành',str(scoring.get('sector_pts',0)),'10']]
    sbt = RLTable(sb, colWidths=[160,80,80])
    sbt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1F3864')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('FONT',(0,0),(-1,-1),'Helvetica',9),
        ('ALIGN',(1,0),(-1,-1),'CENTER'),
        ('GRID',(0,0),(-1,-1),0.4,colors.grey),
        ('PADDING',(0,0),(-1,-1),5),
    ]))
    flow.append(sbt); flow.append(Spacer(1, 12))

    flow.append(RLPar("Hiệu năng backtest", h2))
    btab = [['Win rate',     f"{bt.get('winrate', 0):.1f}%"],
             ['Expectancy',   f"{bt.get('expectancy', 0):+.2f}%"],
             ['Sharpe',       f"{bt.get('sharpe', 0):.2f}"],
             ['Max DD',       f"{bt.get('max_drawdown', 0):.2f}%"],
             ['Số signals',   f"{bt.get('signals', 0)}"]]
    bt_tab = RLTable(btab, colWidths=[160,320])
    bt_tab.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#F2F2F2')),
        ('FONT',(0,0),(-1,-1),'Helvetica',9),
        ('GRID',(0,0),(-1,-1),0.4,colors.grey),
        ('PADDING',(0,0),(-1,-1),5),
    ]))
    flow.append(bt_tab); flow.append(Spacer(1, 12))

    if entry_signal:
        flow.append(RLPar("Tín hiệu vào lệnh", h2))
        flow.append(RLPar(f"<b>{entry_signal.get('action','-')}</b> — "
                            f"Size: {entry_signal.get('size_pct',0)}%", body))
        flow.append(Spacer(1, 12))

    if chart_png_bytes:
        try:
            flow.append(RLPar("Biểu đồ kỹ thuật", h2))
            flow.append(RLImage(io.BytesIO(chart_png_bytes), width=500, height=280))
            flow.append(Spacer(1, 12))
        except Exception as e:
            print(f"[WARN] PDF chart: {e}")

    if extra_sections:
        for title, content in extra_sections.items():
            flow.append(RLPar(title, h2))
            flow.append(RLPar(str(content), body))
            flow.append(Spacer(1, 12))

    flow.append(RLPar("<i>Báo cáo tự động — Quant System V24. Không phải khuyến nghị đầu tư.</i>",
                       ParagraphStyle('F', parent=body, fontSize=8, textColor=colors.grey)))
    doc.build(flow)
    return buf.getvalue()


def streamlit_pdf_download_button(pdf_bytes, ticker: str,
                                    label: str = "📄 Tải báo cáo PDF") -> None:
    """[V24] Nút download PDF."""
    if pdf_bytes is None:
        st.warning("⚠️ Cài reportlab để xuất PDF: `pip install reportlab`")
        return
    st.download_button(label=label, data=pdf_bytes,
                        file_name=f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf")


# ──────────────────────────────────────────────────────────────────────────────
# Divergence với scipy find_peaks (V24 IMPROVED)
# ──────────────────────────────────────────────────────────────────────────────
def detect_divergence_v24(df, lookback: int = None) -> dict:
    """
    [V24 NEW — KHÔNG thay V23] Phân kỳ với find_peaks.
    Dùng tên khác để KHÔNG override V23's detect_divergence.
    Nếu muốn dùng: gọi explicit detect_divergence_v24(df).
    """
    DIV_LOOKBACK_LOCAL = globals().get('DIV_LOOKBACK', 20)
    if lookback is None:
        lookback = DIV_LOOKBACK_LOCAL

    result = {
        'bullish_rsi': False, 'bearish_rsi': False,
        'bullish_macd': False, 'bearish_macd': False,
        'label': '➡️ Không có phân kỳ rõ ràng',
        'signal': 'NONE',
    }
    if len(df) < lookback or not HAS_SCIPY:
        if not HAS_SCIPY:
            result['label'] = '⚠️ Thiếu scipy — divergence V24 không khả dụng'
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

        if len(price_lows) >= 2 and len(rsi_lows) >= 2:
            p1, p2 = price_lows[-2], price_lows[-1]
            r1, r2 = rsi_lows[-2],   rsi_lows[-1]
            if close[p2] < close[p1] * 0.99 and rsi[r2] > rsi[r1] + 2:
                result['bullish_rsi'] = True

        if len(price_highs) >= 2 and len(rsi_highs) >= 2:
            p1, p2 = price_highs[-2], price_highs[-1]
            r1, r2 = rsi_highs[-2],   rsi_highs[-1]
            if close[p2] > close[p1] * 1.01 and rsi[r2] < rsi[r1] - 2:
                result['bearish_rsi'] = True

        if result['bullish_rsi']:
            result['signal'] = 'BULLISH'
            result['label']  = "📈 Phân Kỳ Dương V24 — Động lượng phục hồi"
        elif result['bearish_rsi']:
            result['signal'] = 'BEARISH'
            result['label']  = "📉 Phân Kỳ Âm V24 — Động lượng suy yếu"
    except Exception as e:
        print(f"[WARN] detect_divergence_v24: {e}")
    return result


# ==============================================================================
# [V24] END NEW FUNCTIONS
# ==============================================================================


# ==============================================================================


# ──────────────────────────────────────────────────────────────────────────────
# [V24 WIRE] Executive Summary 1 câu + Market Timing downgrade
# ──────────────────────────────────────────────────────────────────────────────
def generate_executive_summary(ticker, scoring, last, ai_score, wave_info,
                                 weekly_trend, kelly_pct, sl_info, regime):
    """[V24 #1] Tóm tắt 1 câu súc tích cho toàn bộ phân tích.
    Output: dict {'one_liner', 'action', 'badge_color'}."""
    price = float(last['close'])
    rsi = float(last['rsi'])
    ai_disp = f"{float(ai_score):.0f}%" if _is_valid_score(ai_score) else "N/A"

    # Lấy size từ kelly + regime mult
    size_pct = round(kelly_pct * regime.get('size_mult', 1.0), 0)

    # TP gợi ý: dùng ATR nếu có, fallback +10%
    atr = float(last.get('atr', price * 0.02))
    sl_price = int(sl_info['final_sl']) if sl_info else int(price * 0.93)
    tp_price = int(price + 3 * ATR_MULTIPLIER * atr)  # 3R upside

    # Quyết định cuối cùng với downgrade theo regime
    base_decision = scoring['decision']
    downgrade_msg = ""
    if 'STRONG BUY' in base_decision or 'MUA' in base_decision:
        if regime.get('regime') == 'CAUTIOUS_BULL':
            final_action = "MUA THẬN TRỌNG"
            badge_color = "orange"
            downgrade_msg = " [↓ vì thị trường thận trọng]"
        elif regime.get('regime') == 'MIXED':
            final_action = "THEO DÕI"
            badge_color = "orange"
            downgrade_msg = " [↓↓ vì thị trường phân hoá]"
            size_pct = round(size_pct * 0.5, 0)
        elif regime.get('regime') == 'BEAR':
            final_action = "ĐỨNG NGOÀI"
            badge_color = "red"
            downgrade_msg = " [↓↓↓ vì thị trường BEAR]"
            size_pct = 0
        else:
            final_action = "MUA"
            badge_color = "green"
    elif 'WATCHLIST' in base_decision or 'THEO DÕI' in base_decision:
        if regime.get('regime') in ('BEAR', 'MIXED'):
            final_action = "ĐỨNG NGOÀI"
            badge_color = "red"
            downgrade_msg = " [↓ vì thị trường yếu]"
            size_pct = 0
        else:
            final_action = "THEO DÕI"
            badge_color = "orange"
    else:
        final_action = "BÁN / ĐỨNG NGOÀI"
        badge_color = "red"
        size_pct = 0

    weekly_str = {"UP": "Weekly UP", "DOWN": "Weekly DOWN", "NEUTRAL": "Weekly NGANG"}.get(weekly_trend, "Weekly N/A")

    # Câu tóm tắt
    if size_pct > 0:
        one_liner = (f"**{ticker}**: {final_action} {size_pct:.0f}% vốn quanh "
                     f"**{price:,.0f}**, SL **{sl_price:,.0f}**, TP **{tp_price:,.0f}** — "
                     f"AI {ai_disp}, Chân sóng {wave_info['score']}/{wave_info.get('total', 11)}, {weekly_str}.{downgrade_msg}")
    else:
        one_liner = (f"**{ticker}**: {final_action} — Giá {price:,.0f}, "
                     f"AI {ai_disp}, RSI {rsi:.1f}, {weekly_str}.{downgrade_msg}")

    return {'one_liner': one_liner, 'action': final_action,
            'badge_color': badge_color, 'size_pct': size_pct,
            'sl': sl_price, 'tp': tp_price}


def check_exit_signal_simple(last, df) -> dict:
    """[V24 #4] Cảnh báo CHỐT LỜI đơn giản cho mã đang xem.
    Trigger: RSI>70 + giá chạm BB trên + Vol nổ."""
    rsi = float(last['rsi'])
    price = float(last['close'])
    upper_bb = float(last.get('upper_band', price * 1.05))
    vol = float(last['vol_strength'])
    ret = float(last.get('return_1d', 0))

    triggers = []
    score = 0

    if rsi >= 75:
        triggers.append(f"🔴 RSI {rsi:.1f} ≥ 75 — quá mua nguy hiểm")
        score += 3
    elif rsi >= 70:
        triggers.append(f"🟠 RSI {rsi:.1f} ≥ 70 — vùng quá mua")
        score += 2

    # Giá chạm/vượt BB trên (trong 1% là coi như chạm)
    if price >= upper_bb * 0.99:
        triggers.append(f"🟠 Giá chạm BB trên ({upper_bb:,.0f})")
        score += 2

    if vol >= 2.0:
        triggers.append(f"🔴 Vol nổ {vol:.1f}x — distribution")
        score += 3
    elif vol >= 1.5 and ret < 0:
        triggers.append(f"🟠 Vol cao {vol:.1f}x + nến đỏ {ret*100:+.1f}%")
        score += 2

    # Action
    if score >= 6:
        action = "EXIT_ALL"
        label = "🚨 CẢNH BÁO CHỐT LỜI MẠNH — Nên thoát 70-100%"
        pct = "70-100%"
        color = "error"
    elif score >= 4:
        action = "TRIM_50"
        label = "⚠️ CẢNH BÁO CHỐT LỜI — Nên chốt 50%"
        pct = "50%"
        color = "warning"
    elif score >= 2:
        action = "WATCH"
        label = "👁️ THEO DÕI CHẶT — Có dấu hiệu quá mua"
        pct = "30%"
        color = "warning"
    else:
        action = "HOLD"
        label = "✅ Chưa có cảnh báo chốt lời"
        pct = "0%"
        color = "success"

    return {'action': action, 'score': score, 'triggers': triggers,
            'label': label, 'suggested_pct': pct, 'color': color}


def render_exit_alert_card(exit_alert: dict, ticker: str) -> None:
    """[V24] Card cảnh báo chốt lời cho mã đang phân tích."""
    if exit_alert['action'] == 'HOLD':
        return  # Không hiện gì nếu chưa cần chốt

    with st.container(border=True):
        if exit_alert['color'] == 'error':
            st.error(f"### {exit_alert['label']}")
        elif exit_alert['color'] == 'warning':
            st.warning(f"### {exit_alert['label']}")

        st.caption(f"Nếu bạn đang giữ **{ticker}**, hệ thống đề xuất xem xét chốt **{exit_alert['suggested_pct']}** vị thế.")

        with st.expander("Chi tiết các dấu hiệu", expanded=True):
            for t in exit_alert['triggers']:
                st.write(t)


# [V24 WIRE END]

# ──────────────────────────────────────────────────────────────────────────────
# [V24-T2] Win/Loss streak
# ──────────────────────────────────────────────────────────────────────────────
def calc_win_loss_streak(profits: list, n: int = 6) -> dict:
    """[T2] Tính chuỗi thắng/thua N lệnh gần nhất."""
    if not profits:
        return {'streak_str': '—', 'recent_n': 0, 'win_pct': 0,
                'last_result': 'NONE', 'consecutive': 0}
    recent = profits[-n:]
    streak_chars = ['W' if p > 0 else 'L' if p < 0 else '—' for p in recent]
    win_count = sum(1 for c in streak_chars if c == 'W')
    win_pct = win_count / len(recent) * 100

    # Đếm consecutive ở cuối (streak hiện tại)
    last_result = streak_chars[-1] if streak_chars else 'NONE'
    consecutive = 0
    for c in reversed(streak_chars):
        if c == last_result:
            consecutive += 1
        else:
            break

    return {
        'streak_str': ''.join(streak_chars),
        'recent_n': len(recent),
        'win_pct': round(win_pct, 1),
        'last_result': last_result,
        'consecutive': consecutive,
    }


# ──────────────────────────────────────────────────────────────────────────────
# [V24-T4] Confidence Score 0/5 ⭐
# ──────────────────────────────────────────────────────────────────────────────
def calc_confidence_stars(bt: dict, equity_final_pct: float) -> dict:
    """[T4] Đánh giá độ tin cậy backtest 0-5 sao."""
    stars = 0
    criteria = []

    sharpe = bt.get('sharpe', 0)
    if sharpe > 0.5:
        stars += 1; criteria.append(f"✅ Sharpe {sharpe:.2f} > 0.5")
    else:
        criteria.append(f"❌ Sharpe {sharpe:.2f} ≤ 0.5")

    if equity_final_pct > 100:
        stars += 1; criteria.append(f"✅ Equity cuối {equity_final_pct:.1f}% > 100%")
    else:
        criteria.append(f"❌ Equity cuối {equity_final_pct:.1f}% ≤ 100%")

    winrate = bt.get('winrate', 0)
    if winrate > 50:
        stars += 1; criteria.append(f"✅ Winrate {winrate:.1f}% > 50%")
    else:
        criteria.append(f"❌ Winrate {winrate:.1f}% ≤ 50%")

    max_dd = abs(bt.get('max_drawdown', 0))
    if max_dd < 15:
        stars += 1; criteria.append(f"✅ Max DD {max_dd:.1f}% < 15%")
    else:
        criteria.append(f"❌ Max DD {max_dd:.1f}% ≥ 15%")

    signals = bt.get('signals', 0)
    if signals >= 20:
        stars += 1; criteria.append(f"✅ Có {signals} signals ≥ 20")
    else:
        criteria.append(f"❌ Chỉ {signals} signals < 20")

    return {'stars': stars, 'criteria': criteria,
            'label': '⭐' * stars + '☆' * (5 - stars)}


# ──────────────────────────────────────────────────────────────────────────────
# [V24-T5] AI score → ngôn ngữ tự nhiên
# ──────────────────────────────────────────────────────────────────────────────
def ai_score_to_language(ai_score) -> str:
    """[T5] Convert AI score % → câu mô tả tự nhiên."""
    if not _is_valid_score(ai_score):
        return "AI không đủ dữ liệu để dự đoán"
    v = float(ai_score)
    if v >= 80:
        return f"AI rất tin tưởng giá sẽ tăng T+3 ({v:.0f}%)"
    elif v >= 65:
        return f"AI nghiêng về Mua, độ tin cậy cao ({v:.0f}%)"
    elif v >= 50:
        return f"AI nghiêng về Mua, độ tin cậy trung bình ({v:.0f}%)"
    elif v >= 35:
        return f"AI lưỡng lự, nghiêng nhẹ về Bán ({v:.0f}%)"
    else:
        return f"AI nghiêng về Bán/Đứng ngoài ({v:.0f}%)"


# ──────────────────────────────────────────────────────────────────────────────
# [V24-M1] Score Trend 7 ngày
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, max_entries=100)
def _calc_score_trend_7d_cached(ticker: str, date_key: str, weekly_trend: str, sector_score: int = 0) -> list:
    """[F4] Cache wrapper cho score trend."""
    df_c = get_price(ticker)
    if not valid(df_c):
        return []
    df_c = calc_indicators(df_c)
    # Foreign trend dùng smart_flow_proxy đơn giản
    try:
        ft = smart_flow_proxy(df_c)
    except Exception:
        ft = {'score': 10}
    return _calc_score_trend_7d_impl(df_c, ft, weekly_trend, sector_score)


def _calc_score_trend_7d_impl(df: pd.DataFrame, foreign_trend: dict,
                          weekly_trend: str, sector_score: int = 0,
                          n_days: int = 7) -> list:
    """[M1] Tính lại điểm tổng cho 7 phiên gần nhất.
    Để nhanh: chỉ tính tech_pts + flow_pts + sentiment cố định."""
    if len(df) < n_days + 30:
        return []

    scores = []
    for i in range(n_days, 0, -1):
        idx = -i
        try:
            row = df.iloc[idx]
            price = float(row['close'])
            ma20 = float(row['ma20'])
            rsi = float(row['rsi'])
            macd = float(row['macd'])
            sig = float(row['signal'])
            vwap20 = float(row.get('vwap20', ma20))

            # Re-compute tech_pts theo V24 logic
            tp = 0
            if price > ma20: tp += 6
            if price > vwap20: tp += 2
            if rsi < RSI_HOT: tp += 4
            if macd > sig: tp += 5
            if weekly_trend == 'UP': tp += 3
            tp = min(20, tp)

            # Flow giữ nguyên (foreign_trend hôm nay — không tính lại lịch sử)
            fp = int(foreign_trend.get('score', 0))
            # AI giả định trung bình 50% → 13pts (không re-run XGBoost)
            ap = 13
            # Financial + sector cố định
            sec_pts = min(10, int(sector_score))

            total = min(90, ap + tp + fp + 8 + sec_pts)  # 8 là fin_pts trung bình
            scores.append({
                'days_ago': i,
                'date': df['date'].iloc[idx] if 'date' in df.columns else f"D-{i}",
                'price': price,
                'rsi': rsi,
                'score': total,
            })
        except Exception:
            continue
    return scores


# ──────────────────────────────────────────────────────────────────────────────
# [V24-M3] Stop-Loss Calculator độc lập
# ──────────────────────────────────────────────────────────────────────────────
def calc_position_simple(capital: float, entry: float,
                          risk_pct: float = 1.0, atr_pct: float = 2.5) -> dict:
    """[M3] Tính position size đơn giản dựa trên risk%.
    SL = entry - (atr_pct * 2)%; số shares = (capital * risk%) / (entry - SL).
    """
    if capital <= 0 or entry <= 0:
        return {'error': 'Capital và entry phải > 0'}

    sl_pct_from_entry = atr_pct * 2 / 100.0   # ATR × 2 = stop distance
    sl_price = entry * (1 - sl_pct_from_entry)
    tp1_price = entry * (1 + atr_pct * 2 / 100.0)
    tp2_price = entry * (1 + atr_pct * 4 / 100.0)
    tp3_price = entry * (1 + atr_pct * 6 / 100.0)

    dollar_risk = capital * (risk_pct / 100.0)
    risk_per_share = entry - sl_price
    if risk_per_share <= 0:
        return {'error': 'Tỷ lệ rủi ro không hợp lệ'}

    shares_raw = dollar_risk / risk_per_share
    shares = int(shares_raw // 100 * 100)  # bội số 100
    total_cost = shares * entry

    return {
        'entry': round(entry, 0),
        'sl': round(sl_price, 0),
        'tp1': round(tp1_price, 0),
        'tp2': round(tp2_price, 0),
        'tp3': round(tp3_price, 0),
        'shares': shares,
        'total_cost': round(total_cost, 0),
        'dollar_risk': round(dollar_risk, 0),
        'risk_pct': risk_pct,
        'r_multiple_tp1': 1.0,
        'r_multiple_tp2': 2.0,
        'r_multiple_tp3': 3.0,
        'pct_of_capital': round(total_cost / capital * 100, 1),
    }


# ──────────────────────────────────────────────────────────────────────────────
# [V24-M8] Volatility Regime Detection
# ──────────────────────────────────────────────────────────────────────────────
def detect_volatility_regime(df: pd.DataFrame, n_days: int = 60) -> dict:
    """[M8] So sánh ATR/giá hiện tại với phân phối 60 ngày trước."""
    if len(df) < n_days + 20:
        return {'level': 'UNKNOWN', 'label': '❓ Chưa đủ dữ liệu',
                'current_atr_pct': 0, 'percentile': 50,
                'size_recommend': 1.0}

    df_calc = df.tail(n_days + 1).copy()
    df_calc['atr_pct'] = df_calc['atr'] / df_calc['close'] * 100

    current = float(df_calc['atr_pct'].iloc[-1])
    distribution = df_calc['atr_pct'].iloc[:-1]

    # Percentile của current trong distribution
    percentile = (distribution < current).sum() / len(distribution) * 100

    if percentile >= 80:
        return {'level': 'HIGH', 'label': '🔴 Volatility cao (P80+) — Giảm size 50%',
                'current_atr_pct': round(current, 2),
                'percentile': round(percentile, 0),
                'size_recommend': 0.5}
    elif percentile >= 60:
        return {'level': 'ELEVATED', 'label': '🟠 Volatility cao hơn TB — Cân nhắc size 75%',
                'current_atr_pct': round(current, 2),
                'percentile': round(percentile, 0),
                'size_recommend': 0.75}
    elif percentile <= 20:
        return {'level': 'LOW', 'label': '🟢 Volatility thấp — Cơ hội tốt, có thể tăng nhẹ size',
                'current_atr_pct': round(current, 2),
                'percentile': round(percentile, 0),
                'size_recommend': 1.0}
    else:
        return {'level': 'NORMAL', 'label': '⚪ Volatility bình thường',
                'current_atr_pct': round(current, 2),
                'percentile': round(percentile, 0),
                'size_recommend': 1.0}


# ──────────────────────────────────────────────────────────────────────────────
# [V24-M4] Sector Money Flow Map
# ──────────────────────────────────────────────────────────────────────────────
def calc_sector_money_flow(tickers_by_sector: dict, max_per_sector: int = 8) -> list:
    """[M4] Tính dòng tiền từng ngành: % trên MA20, RSI TB, vol_strength TB."""
    results = []
    for sector_name, tickers in tickers_by_sector.items():
        sample = tickers[:max_per_sector]
        n_total = 0
        n_above_ma20 = 0
        rsi_sum = 0
        vol_sum = 0
        ret_sum = 0
        for t in sample:
            try:
                df_t = get_price(t, days=30)
                if not valid(df_t) or len(df_t) < 21:
                    continue
                df_t = calc_indicators(df_t)
                last_t = df_t.iloc[-1]
                n_total += 1
                if last_t['close'] > last_t['ma20']:
                    n_above_ma20 += 1
                rsi_sum += float(last_t['rsi'])
                vol_sum += float(last_t['vol_strength'])
                ret_sum += float(last_t.get('return_1d', 0))
            except Exception:
                continue
        if n_total >= 3:
            results.append({
                'sector': sector_name,
                'n_sample': n_total,
                'pct_above_ma20': round(n_above_ma20 / n_total * 100, 1),
                'rsi_avg': round(rsi_sum / n_total, 1),
                'vol_avg': round(vol_sum / n_total, 2),
                'ret_avg_pct': round(ret_sum / n_total * 100, 2),
                'heat': round(n_above_ma20 / n_total * 100 +
                                (ret_sum / n_total * 100) * 5, 1),
            })
    return sorted(results, key=lambda x: x['heat'], reverse=True)


# ──────────────────────────────────────────────────────────────────────────────
# [V24-M5] Pre-market Checklist
# ──────────────────────────────────────────────────────────────────────────────
def generate_premarket_checklist(watchlist: list, max_check: int = 15) -> dict:
    """[M5] Tạo checklist sáng: top mã trong WL + cảnh báo + vol bất thường."""
    if not watchlist:
        return {'top3': [], 'exit_alerts': [], 'unusual_vol': [], 'error': 'Watchlist trống'}

    sample = list(watchlist)[:max_check]
    results = []
    exit_alerts = []
    unusual_vol = []

    for t in sample:
        try:
            df_t = get_price(t, days=80)
            if not valid(df_t) or len(df_t) < 50:
                continue
            df_t = calc_indicators(df_t)
            last_t = df_t.iloc[-1]
            price = float(last_t['close'])
            rsi = float(last_t['rsi'])
            vol = float(last_t['vol_strength'])

            # Quick score
            score = 0
            if last_t['close'] > last_t['ma20']: score += 25
            if rsi < 65 and rsi > 40: score += 20
            if last_t['macd'] > last_t['signal']: score += 20
            if vol > 1.2 and vol < 2.0: score += 15
            results.append({'ticker': t, 'price': price, 'rsi': rsi,
                            'vol': vol, 'score': score})

            # Exit alert nếu RSI cao + vol nổ
            if rsi >= 75 or (rsi >= 70 and vol >= 1.8):
                exit_alerts.append({'ticker': t, 'rsi': rsi, 'vol': vol,
                                      'reason': f"RSI {rsi:.1f}, Vol {vol:.1f}x"})

            # Vol bất thường (> 2x)
            if vol >= 2.0:
                ret = float(last_t.get('return_1d', 0)) * 100
                unusual_vol.append({'ticker': t, 'vol': vol, 'ret_pct': ret,
                                     'direction': 'UP' if ret > 0 else 'DOWN'})
        except Exception:
            continue

    top3 = sorted(results, key=lambda x: x['score'], reverse=True)[:3]
    return {'top3': top3, 'exit_alerts': exit_alerts,
            'unusual_vol': unusual_vol, 'n_checked': len(results)}


# ──────────────────────────────────────────────────────────────────────────────
# [V24-M2] What-if RSI/Price simulator
# ──────────────────────────────────────────────────────────────────────────────
def whatif_recalc_score(last_real: pd.Series, sim_price: float, sim_rsi: float,
                         macd_up: bool, weekly_trend: str, foreign_trend: dict,
                         growth, pe, ai_score, sector_score: int = 0) -> int:
    """[M2] Tính lại điểm tổng nếu RSI/giá thay đổi (giữ AI score cũ)."""
    ma20 = float(last_real['ma20'])
    vwap20 = float(last_real.get('vwap20', ma20))

    # AI
    if _is_valid_score(ai_score):
        v = float(ai_score)
        if   v >= 70: ai_pts = 25
        elif v >= 60: ai_pts = 20
        elif v >= 50: ai_pts = 13
        elif v >= 40: ai_pts = 7
        else:         ai_pts = 2
    else:
        ai_pts = 0

    # Tech
    tech_pts = 0
    if sim_price > ma20: tech_pts += 6
    if sim_price > vwap20: tech_pts += 2
    if sim_rsi < RSI_HOT: tech_pts += 4
    if macd_up: tech_pts += 5
    if weekly_trend == 'UP': tech_pts += 3
    tech_pts = min(20, tech_pts)

    # Flow / fin / sector
    flow_pts = int(foreign_trend.get('score', 0))
    fin_pts = 0
    if growth is not None:
        if growth >= CANSLIM_GREAT: fin_pts += 8
        elif growth > 0: fin_pts += 4
    if pe is not None:
        if pe < PE_CHEAP: fin_pts += 7
        elif pe < PE_OK: fin_pts += 4
    sec_pts = min(10, int(sector_score))

    return min(90, ai_pts + tech_pts + flow_pts + fin_pts + sec_pts)


# [V24 NEW HELPERS END]

# ──────────────────────────────────────────────────────────────────────────────
# [V24-Q1] Auto-refresh trong trading hours
# ──────────────────────────────────────────────────────────────────────────────
def is_trading_hours_vn() -> bool:
    """[Q1] True nếu đang trong giờ giao dịch HOSE (9h-15h, T2-T6)."""
    now = datetime.now(TZ_VN)
    if now.weekday() >= 5:  # T7, CN
        return False
    h, m = now.hour, now.minute
    # 9:00 - 11:30 và 13:00 - 15:00 (sàn HOSE)
    is_morning = (h == 9) or (h == 10) or (h == 11 and m <= 30)
    is_afternoon = (h == 13) or (h == 14) or (h == 15 and m == 0)
    return is_morning or is_afternoon


# ──────────────────────────────────────────────────────────────────────────────
# [V24-S2] Position Risk Heatmap
# ──────────────────────────────────────────────────────────────────────────────
def calc_position_risk_score(pos: dict, df_current: pd.DataFrame) -> dict:
    """[S2] Tính risk score 0-10 cho 1 vị thế (10=rủi ro cao nhất).
    Dựa trên: SL distance, RSI, ATR/price, P&L hiện tại."""
    if not valid(df_current) or len(df_current) < 30:
        return {'score': 5, 'label': 'N/A', 'flags': []}

    last = df_current.iloc[-1]
    cur_price = float(last['close'])
    entry = float(pos.get('entry', cur_price))
    rsi = float(last['rsi'])
    atr = float(last.get('atr', cur_price * 0.02))
    pnl_pct = (cur_price - entry) / entry * 100

    score = 5  # base
    flags = []

    # P&L
    if pnl_pct < -7:
        score += 3; flags.append(f"❌ Lỗ {pnl_pct:.1f}% (>SL 7%)")
    elif pnl_pct < -3:
        score += 1; flags.append(f"⚠️ Lỗ {pnl_pct:.1f}%")
    elif pnl_pct > 15:
        score -= 1; flags.append(f"💰 Lời {pnl_pct:.1f}% (cân nhắc chốt)")

    # RSI extremes
    if rsi >= 75:
        score += 2; flags.append(f"🔴 RSI {rsi:.0f} quá mua")
    elif rsi < 30:
        score += 2; flags.append(f"🔴 RSI {rsi:.0f} quá bán")

    # Volatility cao
    atr_pct = atr / cur_price * 100
    if atr_pct > 4:
        score += 1; flags.append(f"⚡ Vol cao {atr_pct:.1f}%")

    # MACD bearish cross gần đây
    if len(df_current) >= 3:
        if (df_current['macd'].iloc[-2] > df_current['signal'].iloc[-2]
            and last['macd'] < last['signal']):
            score += 2; flags.append("🔴 MACD vừa cắt xuống")

    # Trên/dưới MA20
    ma20 = float(last['ma20'])
    if cur_price < ma20 * 0.97:
        score += 1; flags.append("⚠️ Rơi dưới MA20")

    score = max(0, min(10, score))
    if score >= 8: label = '🔴 RỦI RO CAO'
    elif score >= 6: label = '🟠 RỦI RO VỪA'
    elif score >= 4: label = '🟡 BÌNH THƯỜNG'
    else: label = '🟢 AN TOÀN'

    return {'score': score, 'label': label, 'flags': flags,
            'pnl_pct': round(pnl_pct, 2), 'rsi': round(rsi, 1)}


# ──────────────────────────────────────────────────────────────────────────────
# [V24-S3] "Hôm nay nên xem mã nào" — Top 3 mã đáng follow
# ──────────────────────────────────────────────────────────────────────────────
def get_daily_recommendations(watchlist: list, max_check: int = 20) -> dict:
    """[S3] Quét watchlist + PILLARS, tìm 3 mã đáng follow hôm nay.
    Tiêu chí: vol bất thường, RSI hồi từ thấp, hoặc breakout MA20."""
    candidates = []
    universe = list(set(watchlist + PILLARS[:10]))[:max_check]

    for t in universe:
        try:
            df = get_price(t, days=60)
            if not valid(df) or len(df) < 40:
                continue
            df = calc_indicators(df)
            last = df.iloc[-1]
            prev = df.iloc[-2]

            rsi = float(last['rsi'])
            price = float(last['close'])
            ma20 = float(last['ma20'])
            vol = float(last['vol_strength'])
            ret = float(last.get('return_1d', 0))

            reasons = []
            score = 0

            # 1. Vol bất thường (>1.8x)
            if vol >= 1.8:
                score += 30
                reasons.append(f"⚡ Vol nổ {vol:.1f}x")

            # 2. RSI hồi phục từ vùng thấp
            if 35 <= rsi <= 55 and float(prev['rsi']) < 40:
                score += 25
                reasons.append(f"🔄 RSI hồi từ {prev['rsi']:.0f} → {rsi:.0f}")

            # 3. Breakout MA20 (vừa vượt MA20)
            if price > ma20 and float(prev['close']) <= float(prev['ma20']):
                score += 30
                reasons.append("🚀 Vừa break MA20")

            # 4. MACD bullish cross gần đây
            if (last['macd'] > last['signal']
                and float(prev['macd']) <= float(prev['signal'])):
                score += 25
                reasons.append("📈 MACD vừa cắt lên")

            # 5. Tăng mạnh hôm nay (>2%)
            if ret > 0.02:
                score += 15
                reasons.append(f"🟢 Tăng {ret*100:.1f}%")

            if score > 0:
                candidates.append({
                    'ticker': t,
                    'score': score,
                    'price': price,
                    'rsi': round(rsi, 1),
                    'vol': round(vol, 2),
                    'ret_pct': round(ret*100, 2),
                    'reasons': reasons,
                })
        except Exception:
            continue

    candidates.sort(key=lambda x: x['score'], reverse=True)
    return {
        'top3': candidates[:3],
        'all': candidates,
        'n_checked': len(universe),
    }


# ──────────────────────────────────────────────────────────────────────────────
# [V24-S5] Daily Commentary auto-generated
# ──────────────────────────────────────────────────────────────────────────────
def generate_daily_commentary(regime: dict, breadth: dict,
                                sector_flow: list = None) -> str:
    """[S5] Sinh câu mô tả thị trường hôm nay tự động."""
    parts = []

    pct_ma20 = regime.get('pct_ma20', 50)
    adr = regime.get('adr', 50)
    rg = regime.get('regime', 'UNKNOWN')

    # Câu 1: tổng quan
    if rg == 'STRONG_BULL':
        parts.append(f"📈 **Thị trường mạnh mẽ** — {pct_ma20:.0f}% mã đang trên MA20, dòng tiền tích cực.")
    elif rg == 'CAUTIOUS_BULL':
        parts.append(f"🟡 **Thị trường tích cực có chọn lọc** — {pct_ma20:.0f}% mã trên MA20.")
    elif rg == 'BEAR':
        parts.append(f"🔴 **Thị trường yếu** — chỉ {pct_ma20:.0f}% mã trên MA20, nên đứng ngoài.")
    elif rg == 'MIXED':
        parts.append(f"🟠 **Thị trường phân hoá** — {pct_ma20:.0f}% mã trên MA20, cần chọn lọc cao.")
    else:
        parts.append(f"❓ **Trạng thái thị trường:** {pct_ma20:.0f}% mã trên MA20.")

    # Câu 2: ngành nóng nhất
    if sector_flow and len(sector_flow) >= 2:
        hot = sector_flow[0]
        cold = sector_flow[-1]
        parts.append(f"🏭 **{hot['sector']}** dẫn dắt "
                       f"({hot['pct_above_ma20']:.0f}% trên MA20); "
                       f"yếu nhất là **{cold['sector']}** ({cold['pct_above_ma20']:.0f}%).")

    # Câu 3: gợi ý hành động
    if rg == 'STRONG_BULL':
        parts.append(f"💡 **Hành động:** Có thể chủ động mua các mã có RS tốt + breakout.")
    elif rg == 'CAUTIOUS_BULL':
        parts.append(f"💡 **Hành động:** Chỉ mua mã có điểm tổng ≥ {regime.get('min_score_buy', 63)}/90.")
    elif rg == 'MIXED':
        parts.append(f"💡 **Hành động:** Chỉ mã siêu mạnh (RS ≥ 80), size nhỏ.")
    elif rg == 'BEAR':
        parts.append(f"💡 **Hành động:** Không mở vị thế mới, bảo vệ vốn.")

    return " ".join(parts)


# ──────────────────────────────────────────────────────────────────────────────
# [V24-R1] Daily Loss Limit Check
# ──────────────────────────────────────────────────────────────────────────────
def check_daily_loss_limit(trades: list, limit_pct: float = 3.0) -> dict:
    """[R1] Kiểm tra mức lỗ trong ngày so với limit."""
    today = datetime.now(TZ_VN).strftime('%Y-%m-%d')
    today_trades = [t for t in trades if t.get('date', '').startswith(today)]

    if not today_trades:
        return {'today_pnl': 0, 'limit_pct': limit_pct,
                'status': 'OK', 'label': '✅ Chưa có trade nào hôm nay',
                'n_trades': 0}

    pnls_today = [t['pnl_pct'] for t in today_trades]
    # Compound P&L hôm nay
    cum_pnl = (np.prod([1 + p/100 for p in pnls_today]) - 1) * 100
    n_wins = sum(1 for p in pnls_today if p > 0)
    n_losses = sum(1 for p in pnls_today if p < 0)

    if cum_pnl <= -limit_pct:
        status = 'STOP'
        label = f'🚫 ĐÃ CHẠM LIMIT — Dừng giao dịch hôm nay'
    elif cum_pnl <= -limit_pct * 0.7:
        status = 'WARNING'
        label = f'⚠️ Sắp chạm limit ({cum_pnl:.1f}% / -{limit_pct}%)'
    elif cum_pnl > 0:
        status = 'GAIN'
        label = f'🟢 Đang LỜI {cum_pnl:+.1f}% hôm nay'
    else:
        status = 'OK'
        label = f'🟡 Lỗ nhẹ {cum_pnl:.1f}% (limit -{limit_pct}%)'

    return {'today_pnl': round(cum_pnl, 2), 'limit_pct': limit_pct,
            'status': status, 'label': label,
            'n_trades': len(today_trades),
            'n_wins': n_wins, 'n_losses': n_losses}


# ──────────────────────────────────────────────────────────────────────────────
# [V24-R2] Auto Position Sizing — kết hợp Vol regime + Kelly + Portfolio
# ──────────────────────────────────────────────────────────────────────────────
def calc_auto_position_size(capital: float, entry: float, atr: float,
                              kelly_pct: float, vol_regime: dict,
                              market_regime: dict, n_existing_positions: int = 0) -> dict:
    """[R2] Tính position size tự động kết hợp 4 yếu tố:
    1. Vol-Parity (dollar risk 1%)
    2. Half-Kelly cap
    3. Volatility regime mult (LOW=1.0, NORMAL=0.85, HIGH=0.5)
    4. Market regime mult
    5. Diversification penalty (đã có N positions → giảm size)
    """
    if atr <= 0 or entry <= 0 or capital <= 0:
        return {'shares': 0, 'value': 0, 'reasoning': ['Input invalid']}

    reasoning = []
    risk_per_share = 2 * atr  # SL = 2 ATR
    base_risk_pct = 1.0   # 1% vốn dollar risk
    base_dollar = capital * (base_risk_pct / 100)

    # 1. Base từ vol parity
    base_shares = base_dollar / risk_per_share
    reasoning.append(f"Base: 1% risk = {base_dollar:,.0f}đ → {base_shares:.0f} cp")

    # 2. Cap by Half-Kelly
    kelly_value = capital * (kelly_pct / 100)
    kelly_shares = kelly_value / entry
    reasoning.append(f"Half-Kelly cap: {kelly_pct:.1f}% vốn = {kelly_shares:.0f} cp")

    # 3. Vol regime mult
    vol_mult = vol_regime.get('size_recommend', 1.0)
    reasoning.append(f"Vol regime ({vol_regime.get('level', 'NORMAL')}): ×{vol_mult}")

    # 4. Market regime mult
    market_mult = market_regime.get('size_mult', 1.0)
    reasoning.append(f"Market regime ({market_regime.get('regime', 'UNKNOWN')}): ×{market_mult}")

    # 5. Diversification penalty
    if n_existing_positions >= 5:
        div_mult = 0.5
        reasoning.append(f"⚠️ Đã có {n_existing_positions} vị thế → ×0.5")
    elif n_existing_positions >= 3:
        div_mult = 0.75
        reasoning.append(f"⚠️ Đã có {n_existing_positions} vị thế → ×0.75")
    else:
        div_mult = 1.0

    # Final
    final_shares_raw = min(base_shares, kelly_shares) * vol_mult * market_mult * div_mult
    final_shares = int(final_shares_raw // 100 * 100)
    final_value = final_shares * entry
    final_pct = final_value / capital * 100 if capital > 0 else 0

    return {
        'shares': final_shares,
        'value': round(final_value, 0),
        'size_pct': round(final_pct, 2),
        'sl_price': round(entry - risk_per_share, 0),
        'tp1_price': round(entry + risk_per_share, 0),
        'tp2_price': round(entry + 2 * risk_per_share, 0),
        'tp3_price': round(entry + 3 * risk_per_share, 0),
        'dollar_risk': round(final_shares * risk_per_share, 0),
        'reasoning': reasoning,
        'limiter': 'Vol-parity' if base_shares < kelly_shares else 'Half-Kelly',
    }


# ──────────────────────────────────────────────────────────────────────────────
# [V24-S1] Smart Alert — Tier change detection
# ──────────────────────────────────────────────────────────────────────────────
V24_TIERS_FILE = 'v24_tier_history.json'

def load_tier_history() -> dict:
    """[S1] Load lịch sử tier của watchlist."""
    try:
        if not os.path.exists(V24_TIERS_FILE):
            return {}
        with open(V24_TIERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_tier_history(history: dict) -> bool:
    try:
        with open(V24_TIERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def detect_tier_changes(watchlist: list) -> list:
    """[S1] So sánh tier hôm nay vs hôm qua, return list các thay đổi."""
    history = load_tier_history()
    today = datetime.now(TZ_VN).strftime('%Y-%m-%d')
    changes = []
    new_history = {}

    for t in watchlist[:30]:  # max 30 mã
        try:
            df = get_price(t, days=60)
            if not valid(df) or len(df) < 40:
                continue
            df = calc_indicators(df)
            last = df.iloc[-1]
            rsi = float(last['rsi'])
            vol = float(last['vol_strength'])
            price = float(last['close'])
            ma20 = float(last['ma20'])
            macd_up = last['macd'] > last['signal']

            # Tier logic đơn giản
            if vol >= 1.5 and price > ma20 and macd_up and 45 < rsi < 70:
                tier = 'BUY'
            elif price > ma20 and macd_up:
                tier = 'WATCH'
            elif rsi >= 75:
                tier = 'OVERHEAT'
            elif price < ma20 * 0.95:
                tier = 'AVOID'
            else:
                tier = 'NEUTRAL'

            new_history[t] = {'tier': tier, 'date': today, 'price': price}

            # So với history cũ
            old = history.get(t)
            if old and old.get('tier') != tier:
                changes.append({
                    'ticker': t,
                    'from': old.get('tier'),
                    'to': tier,
                    'price': price,
                    'date_old': old.get('date'),
                })
        except Exception:
            continue

    save_tier_history(new_history)
    return changes


# ──────────────────────────────────────────────────────────────────────────────
# [V24-R3] Trade Journal Notes
# ──────────────────────────────────────────────────────────────────────────────
# Đã có trades file, mở rộng schema để có note + reason
def save_trade_with_notes(ticker: str, pnl_pct: float,
                            entry_reason: str, exit_reason: str,
                            lesson: str = "") -> bool:
    """[R3] Lưu trade với ghi chú đầy đủ."""
    trades = load_trades_from_file()
    trades.append({
        'ticker': ticker.upper(),
        'pnl_pct': float(pnl_pct),
        'date': datetime.now(TZ_VN).strftime('%Y-%m-%d %H:%M'),
        'entry_reason': entry_reason,
        'exit_reason': exit_reason,
        'lesson': lesson,
        'r_multiple': None,  # sẽ tính nếu có SL info
    })
    return save_trades_to_file(trades)


# [V24 NEW HELPERS DOT 2 END]

# ──────────────────────────────────────────────────────────────────────────────
# [V24-H1] FOMO/Panic Detector
# ──────────────────────────────────────────────────────────────────────────────
def detect_fomo_signals(last: pd.Series, df: pd.DataFrame) -> dict:
    """[H1] Phát hiện dấu hiệu FOMO/Panic trước khi user vào lệnh.
    Trả về dict với mức cảnh báo + danh sách lý do."""
    flags = []
    fomo_score = 0   # 0-10, càng cao càng nguy hiểm
    panic_score = 0

    ret = float(last.get('return_1d', 0))
    vol = float(last['vol_strength'])
    rsi = float(last['rsi'])
    price = float(last['close'])
    ma20 = float(last['ma20'])
    upper_bb = float(last.get('upper_band', price * 1.05))

    # FOMO CLASSIC: Tăng mạnh + Vol nổ + RSI cao (ngưỡng HOSE: ret > 5%)
    if ret > 0.05 and vol > 1.8:
        fomo_score += 4
        flags.append(f"🚨 Đang tăng +{ret*100:.1f}% với Vol {vol:.1f}x — FOMO classic")
    if rsi >= 75:
        fomo_score += 3
        flags.append(f"🔴 RSI {rsi:.0f} ≥ 75 — vùng quá mua")
    if price >= upper_bb * 1.005:
        fomo_score += 2
        flags.append(f"📈 Giá đã vượt BB trên — quá xa MA")
    if price > ma20 * 1.10:
        fomo_score += 2
        flags.append(f"💸 Giá vượt MA20 {(price/ma20-1)*100:.1f}% — đuổi đỉnh")

    # Tăng liên tiếp nhiều phiên
    if len(df) >= 5:
        last_5_returns = df['return_1d'].tail(5).values
        green_streak = sum(1 for r in last_5_returns if r > 0)
        if green_streak >= 4:
            fomo_score += 2
            flags.append(f"🔥 {green_streak}/5 phiên gần nhất xanh — mua đuổi rủi ro cao")

    # PANIC: Giảm mạnh + Vol nổ
    if ret < -0.04 and vol > 1.8:
        panic_score += 5
        flags.append(f"💀 Đang giảm {ret*100:.1f}% với Vol {vol:.1f}x — có thể PANIC SELL")
    if rsi <= 25:
        panic_score += 3
        flags.append(f"🔴 RSI {rsi:.0f} ≤ 25 — quá bán, có thể bắt dao rơi")

    if fomo_score >= 7:
        return {'level': 'FOMO_HIGH', 'fomo': fomo_score, 'panic': panic_score,
                'flags': flags,
                'message': '🚨 CẢNH BÁO FOMO MẠNH — Khuyến nghị KHÔNG mua đuổi'}
    elif fomo_score >= 4:
        return {'level': 'FOMO_MID', 'fomo': fomo_score, 'panic': panic_score,
                'flags': flags,
                'message': '⚠️ Có dấu hiệu FOMO — Cân nhắc đợi pullback'}
    elif panic_score >= 5:
        return {'level': 'PANIC', 'fomo': fomo_score, 'panic': panic_score,
                'flags': flags,
                'message': '💀 CẢNH BÁO BẮT DAO RƠI — Đợi xác nhận đáy'}
    elif fomo_score > 0 or panic_score > 0:
        return {'level': 'WATCH', 'fomo': fomo_score, 'panic': panic_score,
                'flags': flags,
                'message': '👁️ Có vài dấu hiệu cần lưu ý'}
    return {'level': 'OK', 'fomo': 0, 'panic': 0, 'flags': [],
            'message': '✅ Không có dấu hiệu FOMO/Panic'}


# ──────────────────────────────────────────────────────────────────────────────
# [V24-G1] Smart Tooltip — Context-aware
# ──────────────────────────────────────────────────────────────────────────────
def smart_tooltip_rsi(rsi: float, df: pd.DataFrame) -> str:
    """[G1] Tooltip RSI dựa trên lịch sử của chính mã đó."""
    if len(df) < 60:
        return f"RSI = {rsi:.1f}"
    hist = df['rsi'].tail(60)
    avg = hist.mean()
    p20 = hist.quantile(0.2)
    p80 = hist.quantile(0.8)

    parts = [f"RSI hiện tại: {rsi:.1f}"]
    parts.append(f"Trung bình 60 phiên: {avg:.1f}")
    parts.append(f"Vùng thấp (P20): {p20:.1f} | Vùng cao (P80): {p80:.1f}")

    if rsi > p80:
        parts.append("⚠️ Đang ở vùng CAO của mã này — cẩn trọng quá mua")
    elif rsi < p20:
        parts.append("💡 Đang ở vùng THẤP của mã này — có thể là cơ hội")
    elif abs(rsi - avg) < 5:
        parts.append("⚪ Bình thường với mã này")
    return " | ".join(parts)


def smart_tooltip_vol(vol: float, df: pd.DataFrame) -> str:
    """[G1] Tooltip Vol strength dựa lịch sử."""
    if len(df) < 60:
        return f"Vol strength = {vol:.2f}x"
    hist = df['vol_strength'].tail(60)
    p90 = hist.quantile(0.9)
    parts = [f"Vol hiện tại: {vol:.2f}x"]
    parts.append(f"Top 10% mã này: {p90:.2f}x")
    if vol >= p90:
        parts.append("🔥 Vol đột biến so với chính mã này — có sự kiện lớn")
    elif vol >= 1.5:
        parts.append("⚡ Vol cao hơn trung bình")
    elif vol < 0.7:
        parts.append("😴 Vol thấp — kém quan tâm")
    return " | ".join(parts)


# ──────────────────────────────────────────────────────────────────────────────
# [V24-G2] Next Step Recommendations
# ──────────────────────────────────────────────────────────────────────────────
def generate_next_steps(scoring: dict, last: pd.Series, fomo: dict,
                         exec_summary: dict, ticker: str) -> list:
    """[G2] Sinh 3 hành động cụ thể nên làm tiếp theo."""
    steps = []
    price = float(last['close'])
    rsi = float(last['rsi'])
    decision = scoring.get('decision', '')
    action = exec_summary.get('action', '')

    if 'MUA' in action.upper() and fomo['level'] in ('OK', 'WATCH'):
        # Hành động vào lệnh
        sl_pct = 7
        sl_price = price * (1 - sl_pct/100)
        steps.append({
            'icon': '🎯',
            'title': f'Vào lệnh {ticker} với Auto Position Sizing',
            'detail': f'Mở expander "🤖 Auto Position Sizing" để hệ thống tính size phù hợp',
        })
        steps.append({
            'icon': '🔔',
            'title': f'Đặt alert giá ở {sl_price:,.0f}đ',
            'detail': f'Đặt SL cứng tại {sl_price:,.0f}đ (-{sl_pct}%) qua broker',
        })
        steps.append({
            'icon': '📝',
            'title': 'Ghi rõ lý do mua',
            'detail': 'Mở "Quick Add Position" → ghi lý do trong notes (giúp học sau)',
        })
    elif fomo['level'] in ('FOMO_HIGH', 'FOMO_MID'):
        steps.append({
            'icon': '⏳',
            'title': 'CHỜ pullback',
            'detail': f'Đợi giá test lại MA20 ({last["ma20"]:,.0f}đ) trước khi vào',
        })
        steps.append({
            'icon': '🔍',
            'title': 'Quan sát 2-3 phiên',
            'detail': 'Vol có duy trì không? RSI có giảm về 60-65 không?',
        })
        steps.append({
            'icon': '🆚',
            'title': 'So sánh với mã khác',
            'detail': 'Vào tab "🆚 SO SÁNH 2 MÃ" để tìm cơ hội tốt hơn',
        })
    elif 'THEO DÕI' in decision:
        steps.append({
            'icon': '👁️',
            'title': f'Thêm {ticker} vào watchlist',
            'detail': 'Thêm vào sidebar để theo dõi liên tục',
        })
        steps.append({
            'icon': '⏰',
            'title': 'Đặt bookmark xem lại',
            'detail': 'Mở "🔖 Bookmark hành động" để nhắc xem lại sau 1-3 ngày',
        })
        steps.append({
            'icon': '📊',
            'title': 'Theo dõi Score Trend',
            'detail': 'Quan sát biểu đồ Score Trend 7 ngày — điểm có tăng không?',
        })
    else:
        steps.append({
            'icon': '🚫',
            'title': f'BỎ QUA {ticker} hôm nay',
            'detail': f'Điểm chỉ {scoring.get("total", 0)}/90 — chưa đủ điều kiện',
        })
        steps.append({
            'icon': '🔍',
            'title': 'Tìm mã khác',
            'detail': 'Mở Tab 4 "RADAR" hoặc sidebar "Hôm nay xem mã nào"',
        })
        steps.append({
            'icon': '☕',
            'title': 'Hoặc nghỉ ngơi',
            'detail': 'Không có cơ hội tốt = không vào lệnh. Bảo vệ vốn là ưu tiên',
        })

    return steps[:3]


# ──────────────────────────────────────────────────────────────────────────────
# [V24-G3] Why this score? — Explainable AI
# ──────────────────────────────────────────────────────────────────────────────
def explain_score_breakdown(scoring: dict, last: pd.Series,
                              bt: dict, ai_score) -> list:
    """[G3] Giải thích từng nhóm điểm bằng tiếng Việt dễ hiểu."""
    breakdown = []
    rsi = float(last['rsi'])
    price = float(last['close'])
    ma20 = float(last['ma20'])
    macd_up = last['macd'] > last['signal']

    # AI
    ai_pts = scoring.get('ai_pts', 0)
    if ai_pts >= 20:
        ai_msg = f"AI rất tin (≥70%) → +{ai_pts} điểm"
    elif ai_pts >= 13:
        ai_msg = f"AI nghiêng MUA (~60%) → +{ai_pts} điểm"
    elif ai_pts >= 7:
        ai_msg = f"AI trung lập (~50%) → +{ai_pts} điểm"
    else:
        ai_msg = f"AI không tin tưởng → chỉ {ai_pts} điểm"
    breakdown.append({'group': '🤖 AI (0-25)', 'pts': ai_pts, 'max': 25, 'reason': ai_msg})

    # Tech
    tech_pts = scoring.get('tech_pts', 0)
    tech_reasons = []
    if price > ma20: tech_reasons.append("trên MA20")
    if rsi < 68: tech_reasons.append(f"RSI {rsi:.0f} chưa quá mua")
    if macd_up: tech_reasons.append("MACD bullish")
    tech_msg = ", ".join(tech_reasons) if tech_reasons else "Yếu kỹ thuật"
    breakdown.append({'group': '📊 Kỹ thuật (0-20)', 'pts': tech_pts, 'max': 20, 'reason': tech_msg})

    # Flow
    flow_pts = scoring.get('flow_pts', 0)
    if flow_pts >= 14:
        flow_msg = "Dòng tiền vào mạnh"
    elif flow_pts >= 7:
        flow_msg = "Dòng tiền trung bình"
    else:
        flow_msg = "Dòng tiền yếu/ra"
    breakdown.append({'group': '🌊 Dòng tiền (0-20)', 'pts': flow_pts, 'max': 20, 'reason': flow_msg})

    # Fin
    fin_pts = scoring.get('fin_pts', 0)
    if fin_pts >= 12:
        fin_msg = "Tài chính tốt: tăng trưởng cao + P/E hợp lý"
    elif fin_pts >= 6:
        fin_msg = "Tài chính ổn"
    else:
        fin_msg = "Tài chính yếu hoặc không đủ data"
    breakdown.append({'group': '🏢 Tài chính (0-15)', 'pts': fin_pts, 'max': 15, 'reason': fin_msg})

    # Sector
    sec_pts = scoring.get('sector_pts', 0)
    if sec_pts >= 7:
        sec_msg = "Ngành đang nóng"
    else:
        sec_msg = "Ngành bình thường/yếu"
    breakdown.append({'group': '🏭 Ngành (0-10)', 'pts': sec_pts, 'max': 10, 'reason': sec_msg})

    return breakdown


# ──────────────────────────────────────────────────────────────────────────────
# [V24-Qa] Quick Preview — Không cần "Tiến hành phân tích"
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, max_entries=100)
def quick_preview_ticker(ticker: str, date_key: str) -> dict:
    """[Qa+LIQ] Preview nhanh 1 mã + check thanh khoản."""
    try:
        df = get_price(ticker, days=60)
        if not valid(df) or len(df) < 30:
            return {'error': 'Không đủ dữ liệu'}
        df = calc_indicators(df)
        last = df.iloc[-1]
        price = float(last['close'])
        rsi = float(last['rsi'])
        vol = float(last['vol_strength'])
        ret = float(last.get('return_1d', 0))
        ma20 = float(last['ma20'])
        macd_up = last['macd'] > last['signal']

        # [V24-LIQ] Thêm liquidity check
        liq = calc_liquidity_tier(df)

        # Tier nhanh
        if vol >= 1.5 and price > ma20 and macd_up and 40 < rsi < 70:
            tier = '🟢 MUA'
        elif rsi >= 75:
            tier = '🔴 QUÁ MUA'
        elif price < ma20 * 0.95:
            tier = '🔴 YẾU'
        elif price > ma20 and macd_up:
            tier = '🟡 THEO DÕI'
        else:
            tier = '⚪ TRUNG TÍNH'

        return {
            'ticker': ticker,
            'price': price,
            'rsi': rsi,
            'vol': vol,
            'ret_pct': ret * 100,
            'macd_up': macd_up,
            'above_ma20': price > ma20,
            'tier': tier,
            'liq_tier': liq['tier'],
            'liq_vol_avg': liq.get('vol_avg', 0),
            'liq_turnover': liq.get('turnover_avg', 0),
        }
    except Exception as e:
        return {'error': str(e)[:50]}


# ──────────────────────────────────────────────────────────────────────────────
# [V24-Qb] Bookmark hành động
# ──────────────────────────────────────────────────────────────────────────────
V24_BOOKMARKS_FILE = 'v24_bookmarks.json'

def load_bookmarks() -> list:
    """[Qb] Load bookmarks."""
    try:
        if not os.path.exists(V24_BOOKMARKS_FILE):
            return []
        with open(V24_BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_bookmarks(bookmarks: list) -> bool:
    try:
        with open(V24_BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def is_bookmark_due(bookmark: dict) -> bool:
    """[Qb] Check bookmark đã đến hạn xem lại chưa."""
    try:
        remind_at = bookmark.get('remind_at', '')
        if not remind_at:
            return False
        remind_dt = datetime.strptime(remind_at, '%Y-%m-%d %H:%M')
        # Tạo aware datetime
        remind_dt = remind_dt.replace(tzinfo=TZ_VN)
        return datetime.now(TZ_VN) >= remind_dt
    except Exception:
        return False


# [V24 HUMAN HELPERS END]

# ──────────────────────────────────────────────────────────────────────────────
# [V24-LIQ] BỘ LỌC THANH KHOẢN — Loại bỏ mã nhỏ/penny
# ──────────────────────────────────────────────────────────────────────────────
LIQ_PRICE_OK      = 13_000      # Đường 1: Giá ≥ 13K (mid-cap+)
LIQ_VOL_BIG       = 1_000_000   # Đường 2: Vol khủng bù giá thấp
LIQ_TURNOVER_BIG  = 15          # Đường 2: Turnover ≥ 15 tỷ
LIQ_VOL_MIN       = 150_000     # [F6] Tối thiểu chấp nhận (nới 200K→150K để tránh false alarm cho mã trung bình như SSB)
LIQ_TURNOVER_MIN  = 3           # Tối thiểu turnover (tỷ)
LIQ_TRADING_DAYS  = 18          # ≥18/20 phiên có giao dịch


@st.cache_data(ttl=3600, max_entries=500, show_spinner=False)
def calc_liquidity_tier_cached(ticker: str, date_key: str) -> dict:
    """[V24-F1] Cache wrapper cho liquidity tier (theo ticker+date).
    Dùng cho Radar (400 mã) để tránh tính lại mỗi reload."""
    try:
        df_c = get_price(ticker, days=30)
        if not valid(df_c):
            return {'tier': 'UNKNOWN', 'flags': ['Không tải được data'], 'message': 'N/A'}
        return calc_liquidity_tier(df_c)
    except Exception as e:
        return {'tier': 'UNKNOWN', 'flags': [str(e)[:50]], 'message': 'Lỗi'}


def calc_liquidity_tier(df: pd.DataFrame) -> dict:
    """[V24-LIQ+F3] Đánh giá thanh khoản 1 mã. Có try/except defensive."""
    try:
        return _calc_liquidity_tier_impl(df)
    except Exception as _liq_e:
        return {'tier': 'UNKNOWN', 'vol_avg': 0, 'turnover_avg': 0,
                'price': 0, 'flags': [f'Lỗi: {str(_liq_e)[:50]}'],
                'message': '❓ Không tính được — kiểm tra dữ liệu'}


def _calc_liquidity_tier_impl(df: pd.DataFrame) -> dict:
    """[V24-LIQ] Đánh giá thanh khoản 1 mã (implementation)."""
    if not valid(df) or len(df) < 20:
        return {'tier': 'UNKNOWN', 'vol_avg': 0, 'turnover_avg': 0,
                'price': 0, 'flags': ['Không đủ dữ liệu'],
                'message': '❓ Không đủ data để đánh giá'}

    recent20 = df.tail(20)
    vol_avg = float(recent20['volume'].mean())
    price = float(df['close'].iloc[-1])
    turnover_avg = float((recent20['close'] * recent20['volume']).mean() / 1e9)  # tỷ
    trading_days = int((recent20['volume'] > 0).sum())

    flags = []
    flags.append(f"💰 Giá: {price:,.0f}đ")
    flags.append(f"📊 Vol TB 20p: {vol_avg/1000:,.0f}K cp")
    flags.append(f"💸 Turnover TB: {turnover_avg:.1f} tỷ/phiên")
    flags.append(f"📅 Phiên có GD: {trading_days}/20")

    # Phân loại
    # LOW: giá < 13K VÀ (vol < 1M HOẶC turnover < 15 tỷ)
    is_penny = price < LIQ_PRICE_OK and (vol_avg < LIQ_VOL_BIG or turnover_avg < LIQ_TURNOVER_BIG)
    # Hoặc: vol/turnover/trading days quá thấp
    is_illiquid = (vol_avg < LIQ_VOL_MIN or turnover_avg < LIQ_TURNOVER_MIN
                    or trading_days < LIQ_TRADING_DAYS)

    if is_penny or is_illiquid:
        return {'tier': 'LOW', 'vol_avg': vol_avg, 'turnover_avg': turnover_avg,
                'price': price, 'trading_days': trading_days,
                'flags': flags,
                'message': '🔴 THANH KHOẢN THẤP — Khuyến nghị TRÁNH'}

    # HIGH: vol ≥ 1M VÀ turnover ≥ 10 tỷ
    if vol_avg >= LIQ_VOL_BIG and turnover_avg >= 10:
        return {'tier': 'HIGH', 'vol_avg': vol_avg, 'turnover_avg': turnover_avg,
                'price': price, 'trading_days': trading_days,
                'flags': flags,
                'message': '🟢 THANH KHOẢN CAO — Mã trụ, dễ vào/ra'}

    # Còn lại: MED
    return {'tier': 'MED', 'vol_avg': vol_avg, 'turnover_avg': turnover_avg,
            'price': price, 'trading_days': trading_days,
            'flags': flags,
            'message': '🟡 THANH KHOẢN OK — Mã trung bình'}


def render_liquidity_warning(liq: dict, ticker: str) -> None:
    """[V24-LIQ] Hiển thị banner cảnh báo trong Tab 1 nếu LIQ thấp."""
    if liq['tier'] != 'LOW':
        return
    with st.container(border=True):
        st.error(f"### 🚨 CẢNH BÁO THANH KHOẢN THẤP — {ticker}")
        for f in liq['flags']:
            st.write(f)
        st.markdown("---")
        st.markdown("**⚠️ Rủi ro khi mua mã thanh khoản thấp:**")
        st.write("1. **Khó thoát** khi cần (kẹp hàng)")
        st.write("2. **Spread mua-bán rộng** — mua đắt, bán rẻ")
        st.write("3. **Dễ bị thao túng giá** (pump & dump)")
        st.write("4. **Vol thường < size lệnh** → khớp từng phần, giá xấu")
        st.markdown("**→ Khuyến nghị: TRÁNH mã này, tìm mã khác có thanh khoản tốt hơn.**")


@st.cache_data(ttl=3600, max_entries=300)
def is_liquidity_ok(ticker: str, date_key: str) -> bool:
    """[V24-LIQ] Check nhanh: mã có thanh khoản OK không (cho radar/quickpick filter).
    True = MED hoặc HIGH (ok để gợi ý)
    False = LOW (loại).
    Cache theo ngày."""
    try:
        df = get_price(ticker, days=30)
        if not valid(df) or len(df) < 20:
            return False
        liq = calc_liquidity_tier(df)
        return liq['tier'] in ('MED', 'HIGH')
    except Exception:
        return False

# [V24-LIQ END]

# ──────────────────────────────────────────────────────────────────────────────
# [V28-L1] Lifetime Stats — Phân tích sâu trade history
# ──────────────────────────────────────────────────────────────────────────────
def calc_lifetime_stats(trades: list) -> dict:
    """[V28-L1+F3] Tính thống kê lifetime. Có try/except defensive."""
    try:
        return _calc_lifetime_stats_impl(trades)
    except Exception as _ls_e:
        return {'n_total': 0, 'message': f'Lỗi tính stats: {str(_ls_e)[:80]}'}


def _calc_lifetime_stats_impl(trades: list) -> dict:
    """[V28-L1] Implementation."""
    if not trades:
        return {'n_total': 0, 'message': 'Chưa có trade nào — hãy ghi trade vào Journal'}

    pnls = [t.get('pnl_pct', 0) for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    n_total = len(pnls)
    n_wins = len(wins)
    n_losses = len(losses)
    n_breakeven = n_total - n_wins - n_losses

    winrate = n_wins / n_total * 100 if n_total > 0 else 0
    avg_win = sum(wins) / n_wins if wins else 0
    avg_loss = sum(losses) / n_losses if losses else 0
    biggest_win = max(pnls) if pnls else 0
    biggest_loss = min(pnls) if pnls else 0
    expectancy = (winrate/100) * avg_win + ((100-winrate)/100) * avg_loss

    # Profit factor
    sum_wins = sum(wins) if wins else 0
    sum_losses = abs(sum(losses)) if losses else 0
    profit_factor = sum_wins / sum_losses if sum_losses > 0 else float('inf') if sum_wins > 0 else 0

    # R-multiple trung bình (nếu avg_loss != 0)
    avg_r = avg_win / abs(avg_loss) if avg_loss != 0 else 0

    # Equity curve cumulative
    equity = []
    cum = 100
    for p in pnls:
        cum = cum * (1 + p/100)
        equity.append(cum)

    # Streak hiện tại
    last_streak = 0
    last_type = None
    for p in reversed(pnls):
        cur = 'W' if p > 0 else ('L' if p < 0 else 'B')
        if last_type is None:
            last_type = cur; last_streak = 1
        elif cur == last_type:
            last_streak += 1
        else:
            break

    return {
        'n_total': n_total, 'n_wins': n_wins, 'n_losses': n_losses,
        'n_breakeven': n_breakeven,
        'winrate': round(winrate, 1),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'biggest_win': round(biggest_win, 2),
        'biggest_loss': round(biggest_loss, 2),
        'expectancy': round(expectancy, 2),
        'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 999.0,
        'avg_r': round(avg_r, 2),
        'equity_curve': equity,
        'equity_final': round(equity[-1], 1) if equity else 100,
        'last_streak': last_streak,
        'last_streak_type': last_type,
    }


# ──────────────────────────────────────────────────────────────────────────────
# [V28-L2] Pattern Trade Analyzer — Phân tích pattern thắng/thua
# ──────────────────────────────────────────────────────────────────────────────
def analyze_trade_patterns(trades: list) -> dict:
    """[V28-L2+F3] Phân tích pattern. Có try/except defensive."""
    try:
        return _analyze_patterns_impl(trades)
    except Exception as _ap_e:
        return {'message': f'Lỗi phân tích: {str(_ap_e)[:80]}'}


def _analyze_patterns_impl(trades: list) -> dict:
    """[V28-L2] Implementation."""
    if not trades or len(trades) < 5:
        return {'message': f'Cần ≥5 trades để phân tích (hiện: {len(trades)})'}

    insights = []
    # 1. Pattern theo mood
    mood_stats = {}
    for t in trades:
        mood = t.get('mood', '')
        if not mood: continue
        if mood not in mood_stats:
            mood_stats[mood] = {'n': 0, 'wins': 0, 'sum_pnl': 0}
        mood_stats[mood]['n'] += 1
        if t['pnl_pct'] > 0: mood_stats[mood]['wins'] += 1
        mood_stats[mood]['sum_pnl'] += t['pnl_pct']

    for mood, s in mood_stats.items():
        if s['n'] < 3: continue
        wr = s['wins'] / s['n'] * 100
        avg = s['sum_pnl'] / s['n']
        if wr >= 70:
            insights.append(f"✅ Bạn THẮNG {wr:.0f}% khi mood {mood} ({s['n']} trades, TB +{avg:.1f}%)")
        elif wr <= 30:
            insights.append(f"⚠️ Bạn THUA {100-wr:.0f}% khi mood {mood} ({s['n']} trades, TB {avg:+.1f}%) — TRÁNH trade lúc này")

    # 2. Pattern theo ticker (mã yêu thích thắng/thua)
    ticker_stats = {}
    for t in trades:
        tk = t.get('ticker', '')
        if not tk: continue
        if tk not in ticker_stats:
            ticker_stats[tk] = {'n': 0, 'wins': 0, 'sum_pnl': 0}
        ticker_stats[tk]['n'] += 1
        if t['pnl_pct'] > 0: ticker_stats[tk]['wins'] += 1
        ticker_stats[tk]['sum_pnl'] += t['pnl_pct']

    # Top winning ticker
    top_tickers = sorted(ticker_stats.items(),
                           key=lambda x: x[1]['sum_pnl'], reverse=True)
    if top_tickers and top_tickers[0][1]['sum_pnl'] > 5:
        tk, s = top_tickers[0]
        insights.append(f"🏆 Mã thắng nhiều nhất: **{tk}** ({s['n']} trades, tổng +{s['sum_pnl']:.1f}%)")
    # Worst ticker
    if top_tickers and top_tickers[-1][1]['sum_pnl'] < -5:
        tk, s = top_tickers[-1]
        insights.append(f"💀 Mã thua nhiều nhất: **{tk}** ({s['n']} trades, tổng {s['sum_pnl']:.1f}%) — Tránh trade mã này")

    # 3. Pattern theo entry_reason (keyword trong lý do mua)
    reason_keywords = {
        'macd': [], 'rsi': [], 'breakout': [], 'chân sóng': [], 'tích lũy': [],
        'fomo': [], 'volume': [], 'support': [], 'pullback': [],
    }
    for t in trades:
        reason = (t.get('entry_reason', '') or '').lower()
        for kw in reason_keywords:
            if kw in reason:
                reason_keywords[kw].append(t['pnl_pct'])

    for kw, pnls in reason_keywords.items():
        if len(pnls) < 3: continue
        wins = sum(1 for p in pnls if p > 0)
        wr = wins / len(pnls) * 100
        avg = sum(pnls) / len(pnls)
        if wr >= 70:
            insights.append(f"💡 Lý do '{kw}' THẮNG {wr:.0f}% ({len(pnls)} trades, TB +{avg:.1f}%) — Tiếp tục dùng!")
        elif wr <= 30:
            insights.append(f"⚠️ Lý do '{kw}' THUA {100-wr:.0f}% ({len(pnls)} trades, TB {avg:+.1f}%) — Cân nhắc bỏ")

    return {'insights': insights, 'n_analyzed': len(trades),
            'top_ticker': top_tickers[0] if top_tickers else None}


# ──────────────────────────────────────────────────────────────────────────────
# [V28-A1] Watchlist Rules + Alerts
# ──────────────────────────────────────────────────────────────────────────────
V28_WATCH_RULES_FILE = 'v28_watch_rules.json'

def load_watch_rules() -> list:
    """[V28-A1] Load các rule watchlist."""
    try:
        if not os.path.exists(V28_WATCH_RULES_FILE):
            return []
        with open(V28_WATCH_RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_watch_rules(rules: list) -> bool:
    try:
        with open(V28_WATCH_RULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def check_watch_rules(rules: list) -> list:
    """[V28-A1] Kiểm tra các rule, return list các alert đang trigger.
    Mỗi rule format: {'ticker': 'ACB', 'condition': 'rsi_below', 'value': 40}
    Conditions:
      - rsi_below, rsi_above
      - price_below, price_above
      - vol_above (x lần)
      - break_ma20 (giá vượt MA20)
    """
    alerts = []
    for rule in rules:
        try:
            ticker = rule['ticker']
            cond = rule['condition']
            value = rule['value']
            df_r = get_price(ticker, days=30)
            if not valid(df_r):
                continue
            df_r = calc_indicators(df_r)
            last_r = df_r.iloc[-1]

            triggered = False
            msg = ""
            if cond == 'rsi_below':
                if float(last_r['rsi']) < value:
                    triggered = True
                    msg = f"RSI={float(last_r['rsi']):.1f} < {value}"
            elif cond == 'rsi_above':
                if float(last_r['rsi']) > value:
                    triggered = True
                    msg = f"RSI={float(last_r['rsi']):.1f} > {value}"
            elif cond == 'price_below':
                if float(last_r['close']) < value:
                    triggered = True
                    msg = f"Giá={float(last_r['close']):,.0f} < {value:,.0f}"
            elif cond == 'price_above':
                if float(last_r['close']) > value:
                    triggered = True
                    msg = f"Giá={float(last_r['close']):,.0f} > {value:,.0f}"
            elif cond == 'vol_above':
                if float(last_r['vol_strength']) > value:
                    triggered = True
                    msg = f"Vol={float(last_r['vol_strength']):.2f}x > {value}x"
            elif cond == 'break_ma20':
                if float(last_r['close']) > float(last_r['ma20']):
                    triggered = True
                    msg = f"Giá đã vượt MA20"

            if triggered:
                alerts.append({
                    'ticker': ticker,
                    'condition': cond,
                    'value': value,
                    'message': msg,
                    'note': rule.get('note', ''),
                })
        except Exception:
            continue
    return alerts


# ──────────────────────────────────────────────────────────────────────────────
# [V28-A2] Morning Brief — Tổng hợp 1 trang
# ──────────────────────────────────────────────────────────────────────────────
def generate_morning_brief(watchlist: list, regime: dict) -> dict:
    """[V28-A2] Tổng hợp thông tin sáng cho user."""
    result = {
        'regime': regime,
        'top_watchlist': [],
        'biggest_movers': [],
        'unusual_vol': [],
    }
    # Quét top mã trong watchlist
    sample = list(watchlist)[:15] if watchlist else []
    scored = []
    movers = []
    unusual = []
    for t in sample:
        try:
            df_m = get_price(t, days=30)
            if not valid(df_m): continue
            df_m = calc_indicators(df_m)
            last_m = df_m.iloc[-1]
            price = float(last_m['close'])
            rsi = float(last_m['rsi'])
            vol = float(last_m['vol_strength'])
            ret = float(last_m.get('return_1d', 0)) * 100

            # Score nhanh
            score = 0
            if last_m['close'] > last_m['ma20']: score += 25
            if 40 < rsi < 65: score += 20
            if last_m['macd'] > last_m['signal']: score += 20
            if 1.2 < vol < 2.5: score += 15
            scored.append({'ticker': t, 'price': price, 'rsi': rsi,
                            'vol': vol, 'ret_pct': ret, 'score': score})
            # Movers (|ret| > 3%)
            if abs(ret) > 3:
                movers.append({'ticker': t, 'price': price, 'ret_pct': ret})
            # Unusual vol
            if vol > 2.0:
                unusual.append({'ticker': t, 'vol': vol, 'ret_pct': ret})
        except Exception:
            continue

    result['top_watchlist'] = sorted(scored, key=lambda x: x['score'], reverse=True)[:3]
    result['biggest_movers'] = sorted(movers, key=lambda x: abs(x['ret_pct']), reverse=True)[:5]
    result['unusual_vol'] = unusual
    return result


# ──────────────────────────────────────────────────────────────────────────────
# [V28-P1] Candlestick Pattern Detector
# ──────────────────────────────────────────────────────────────────────────────
def detect_candlestick_patterns(df: pd.DataFrame) -> list:
    """[V28-P1+F3] Phát hiện các mẫu nến. Có try/except defensive."""
    try:
        return _detect_candlestick_impl(df)
    except Exception as _cs_e:
        return []


def _detect_candlestick_impl(df: pd.DataFrame) -> list:
    """[V28-P1] Implementation."""
    if len(df) < 5:
        return []

    patterns = []
    # Lấy 5 nến gần nhất
    recent = df.tail(5)
    last = recent.iloc[-1]
    prev = recent.iloc[-2]
    prev2 = recent.iloc[-3]

    # Helper
    body = lambda r: abs(r['close'] - r['open'])
    upper = lambda r: r['high'] - max(r['close'], r['open'])
    lower = lambda r: min(r['close'], r['open']) - r['low']
    is_bullish = lambda r: r['close'] > r['open']
    is_bearish = lambda r: r['close'] < r['open']
    full_range = lambda r: r['high'] - r['low']

    last_body = body(last)
    last_range = full_range(last)
    last_upper = upper(last)
    last_lower = lower(last)

    # 1. HAMMER (đáy đảo chiều) — bullish
    # - lower wick > 2 * body
    # - upper wick < body * 0.3
    # - bullish recent context (giá đã giảm)
    if last_range > 0 and last_body > 0:
        if (last_lower > 2 * last_body and
            last_upper < last_body * 0.5 and
            prev['close'] < prev2['close']):  # recent downtrend
            patterns.append({
                'name': '🔨 Hammer (Búa)',
                'type': 'BULLISH',
                'message': 'Tín hiệu ĐẢO CHIỀU TĂNG — phe mua đã chiếm ưu thế',
            })

    # 2. SHOOTING STAR (đỉnh đảo chiều) — bearish
    # - upper wick > 2 * body
    # - lower wick < body * 0.3
    # - bullish recent context
    if last_range > 0 and last_body > 0:
        if (last_upper > 2 * last_body and
            last_lower < last_body * 0.5 and
            prev['close'] > prev2['close']):  # recent uptrend
            patterns.append({
                'name': '⭐ Shooting Star (Sao đổi ngôi)',
                'type': 'BEARISH',
                'message': 'Tín hiệu ĐẢO CHIỀU GIẢM — phe bán đang quay lại',
            })

    # 3. DOJI (lưỡng lự) — neutral
    if last_range > 0 and last_body < last_range * 0.1:
        patterns.append({
            'name': '➕ Doji',
            'type': 'NEUTRAL',
            'message': 'Lưỡng lự — thị trường chưa quyết định, chờ tín hiệu xác nhận',
        })

    # 4. BULLISH ENGULFING — đảo chiều tăng mạnh
    # Nến trước GIẢM, nến sau TĂNG và bao trùm nến trước
    if is_bearish(prev) and is_bullish(last):
        if (last['open'] <= prev['close'] and
            last['close'] >= prev['open'] and
            body(last) > body(prev) * 1.2):
            patterns.append({
                'name': '🟢 Bullish Engulfing (Nhấn chìm tăng)',
                'type': 'BULLISH',
                'message': 'Tín hiệu ĐẢO CHIỀU TĂNG MẠNH — phe mua áp đảo phe bán',
            })

    # 5. BEARISH ENGULFING — đảo chiều giảm mạnh
    if is_bullish(prev) and is_bearish(last):
        if (last['open'] >= prev['close'] and
            last['close'] <= prev['open'] and
            body(last) > body(prev) * 1.2):
            patterns.append({
                'name': '🔴 Bearish Engulfing (Nhấn chìm giảm)',
                'type': 'BEARISH',
                'message': 'Tín hiệu ĐẢO CHIỀU GIẢM MẠNH — phe bán áp đảo',
            })

    # 6. MORNING STAR (3 nến — đảo chiều đáy) — bullish
    # Nến 1: giảm mạnh
    # Nến 2: small body (doji-like)
    # Nến 3: tăng mạnh
    if (is_bearish(prev2) and body(prev2) > full_range(prev2) * 0.6 and
        body(prev) < full_range(prev) * 0.4 and
        is_bullish(last) and body(last) > full_range(last) * 0.6 and
        last['close'] > (prev2['open'] + prev2['close']) / 2):
        patterns.append({
            'name': '🌟 Morning Star (Sao mai)',
            'type': 'BULLISH',
            'message': 'Mẫu 3 nến đảo chiều TĂNG mạnh từ đáy',
        })

    # 7. EVENING STAR (3 nến — đảo chiều đỉnh) — bearish
    if (is_bullish(prev2) and body(prev2) > full_range(prev2) * 0.6 and
        body(prev) < full_range(prev) * 0.4 and
        is_bearish(last) and body(last) > full_range(last) * 0.6 and
        last['close'] < (prev2['open'] + prev2['close']) / 2):
        patterns.append({
            'name': '🌆 Evening Star (Sao hôm)',
            'type': 'BEARISH',
            'message': 'Mẫu 3 nến đảo chiều GIẢM mạnh từ đỉnh',
        })

    return patterns


# ──────────────────────────────────────────────────────────────────────────────
# [V28-R4] Stress Test Portfolio
# ──────────────────────────────────────────────────────────────────────────────
def stress_test_portfolio(positions: list, vni_drop_pct: float = -5.0) -> dict:
    """[V28-R4] Mô phỏng danh mục nếu VN-Index giảm X%.
    Dùng beta của từng mã để tính dự kiến lỗ."""
    if not positions:
        return {'message': 'Chưa có vị thế nào để stress test'}

    total_value = 0
    total_expected_loss = 0
    detail_rows = []

    for pos in positions:
        try:
            df_p = get_price(pos['ticker'], days=90)
            if not valid(df_p):
                continue
            df_p = calc_indicators(df_p)
            cur_price = float(df_p['close'].iloc[-1])
            shares = pos['shares']
            value = cur_price * shares

            # Tính beta đơn giản từ VN-Index
            try:
                df_vni_st = get_vnindex_cached()
                if valid(df_vni_st) and len(df_vni_st) >= 60:
                    df_p_safe = ensure_date_col(df_p)
                    df_vni_safe = ensure_date_col(df_vni_st)
                    if 'return_1d' in df_p_safe.columns and 'return_1d' in df_vni_safe.columns:
                        df_p_safe['date'] = df_p_safe['date'].astype(str).str[:10]
                        df_vni_safe['date'] = df_vni_safe['date'].astype(str).str[:10]
                        merged = pd.merge(
                            df_p_safe[['date','return_1d']].rename(columns={'return_1d':'r_p'}),
                            df_vni_safe[['date','return_1d']].rename(columns={'return_1d':'r_v'}),
                            on='date').dropna().tail(63)
                        if len(merged) >= 20:
                            cov = np.cov(merged['r_p'], merged['r_v'])
                            beta = cov[0,1] / (cov[1,1] + 1e-9)
                        else:
                            beta = 1.0
                    else:
                        beta = 1.0
                else:
                    beta = 1.0
            except Exception:
                beta = 1.0

            # Expected loss = beta * vni_drop * value
            expected_pct = beta * vni_drop_pct
            expected_loss = value * (expected_pct / 100)

            total_value += value
            total_expected_loss += expected_loss

            detail_rows.append({
                'ticker': pos['ticker'],
                'shares': shares,
                'cur_price': cur_price,
                'value': value,
                'beta': round(beta, 2),
                'expected_loss_pct': round(expected_pct, 2),
                'expected_loss_amount': round(expected_loss, 0),
            })
        except Exception:
            continue

    if total_value == 0:
        return {'message': 'Không tính được — kiểm tra dữ liệu vị thế'}

    overall_pct = total_expected_loss / total_value * 100

    return {
        'vni_drop_pct': vni_drop_pct,
        'total_value': round(total_value, 0),
        'total_expected_loss': round(total_expected_loss, 0),
        'overall_pct': round(overall_pct, 2),
        'detail': detail_rows,
    }




# ──────────────────────────────────────────────────────────────────────────────
# [V29-F1] Cache wrappers cho performance — cache theo date_key (refresh mỗi ngày)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, max_entries=10, show_spinner=False)
def _cached_check_watch_rules(rules_str: str, date_key: str) -> list:
    """[V29-F1] Cache check_watch_rules theo string của rules (5 phút)."""
    try:
        rules = json.loads(rules_str)
        return check_watch_rules(rules)
    except Exception:
        return []


@st.cache_data(ttl=300, max_entries=5, show_spinner=False)
def _cached_morning_brief(watchlist_str: str, regime_str: str, date_key: str) -> dict:
    """[V29-F1] Cache morning brief theo watchlist (5 phút)."""
    try:
        wl = json.loads(watchlist_str)
        rg = json.loads(regime_str)
        return generate_morning_brief(wl, rg)
    except Exception:
        return {'top_watchlist': [], 'biggest_movers': [], 'unusual_vol': []}


@st.cache_data(ttl=600, max_entries=5, show_spinner=False)
def _cached_stress_test(positions_str: str, vni_drop: float, date_key: str) -> dict:
    """[V29-F1] Cache stress test (10 phút)."""
    try:
        positions = json.loads(positions_str)
        return stress_test_portfolio(positions, vni_drop_pct=vni_drop)
    except Exception:
        return {'message': 'Lỗi cache stress test'}


# [V29-F1 END]

# ──────────────────────────────────────────────────────────────────────────────
# [V34] VN-INDEX DECISION HELPER — Combo B (6 tính năng)
# ──────────────────────────────────────────────────────────────────────────────

def calc_vni_decision_score(df_vni_input: pd.DataFrame = None) -> dict:
    """[V34-D1+D2 / V35-FIX] Tính điểm tổng và checklist 10 dấu hiệu của VN-Index.
    Nhận df_vni làm tham số (từ session, đã load E1VFVN30) để tránh 403.
    Fallback: get_vnindex_cached() nếu input None."""
    try:
        if df_vni_input is not None and valid(df_vni_input):
            df_vni = df_vni_input
        else:
            df_vni = get_vnindex_cached()
        if not valid(df_vni) or len(df_vni) < 60:
            return {'verdict': 'UNKNOWN', 'score': 0, 'checks': [],
                    'message': 'Không đủ data VN-Index'}

        df_v = calc_indicators(df_vni.copy()) if 'rsi' not in df_vni.columns else df_vni.copy()
        last = df_v.iloc[-1]
        price = float(last['close'])

        checks = []
        score = 0
        max_score = 0

        # 1. Trên MA20 — trọng số 10
        ma20 = float(last['ma20'])
        ok = price > ma20
        pct_vs_ma = (price - ma20) / ma20 * 100
        checks.append({
            'name': f"VNI trên MA20 ({pct_vs_ma:+.2f}%)",
            'pass': ok, 'weight': 10
        })
        if ok: score += 10
        max_score += 10

        # 2. Trên MA50 — trọng số 10
        if 'ma50' in df_v.columns:
            ma50 = float(last['ma50'])
            ok = price > ma50
            pct = (price - ma50) / ma50 * 100
            checks.append({
                'name': f"VNI trên MA50 ({pct:+.2f}%)",
                'pass': ok, 'weight': 10
            })
            if ok: score += 10
            max_score += 10

        # 3. MA20 > MA50 — trọng số 10
        if 'ma50' in df_v.columns:
            ok = float(last['ma20']) > float(last['ma50'])
            checks.append({
                'name': "MA20 > MA50 (xu hướng tăng)",
                'pass': ok, 'weight': 10
            })
            if ok: score += 10
            max_score += 10

        # 4. RSI VNI trong vùng tốt 40-65 — trọng số 10
        rsi = float(last['rsi'])
        if rsi >= 70:
            ok = False
            note = f"RSI={rsi:.0f} (quá mua, rủi ro)"
        elif rsi <= 30:
            ok = False
            note = f"RSI={rsi:.0f} (quá bán, panic)"
        elif 40 <= rsi <= 65:
            ok = True
            note = f"RSI={rsi:.0f} (vùng khoẻ)"
        else:
            ok = True  # half-credit cho 30-40 hoặc 65-70
            note = f"RSI={rsi:.0f} (trung tính)"
        checks.append({
            'name': note, 'pass': ok, 'weight': 10
        })
        if ok: score += 10
        max_score += 10

        # 5. MACD cắt tăng — trọng số 10
        if 'macd' in df_v.columns and 'signal' in df_v.columns:
            macd_v = float(last['macd'])
            sig_v = float(last['signal'])
            ok = macd_v > sig_v
            checks.append({
                'name': f"MACD VNI {'>' if ok else '<'} Signal",
                'pass': ok, 'weight': 10
            })
            if ok: score += 10
            max_score += 10

        # 6. Volume tăng — trọng số 5
        if 'vol_strength' in df_v.columns:
            vol = float(last['vol_strength'])
            ok = vol > 1.0
            checks.append({
                'name': f"Vol thị trường {vol:.2f}x ({'tăng' if ok else 'yếu'})",
                'pass': ok, 'weight': 5
            })
            if ok: score += 5
            max_score += 5

        # 7. Return 5 ngày dương — trọng số 10
        if len(df_v) >= 6:
            ret_5d = (price - float(df_v['close'].iloc[-6])) / float(df_v['close'].iloc[-6]) * 100
            ok = ret_5d > 0
            checks.append({
                'name': f"VNI 5 ngày: {ret_5d:+.2f}% ({'dương' if ok else 'âm'})",
                'pass': ok, 'weight': 10
            })
            if ok: score += 10
            max_score += 10

        # 8. Return 20 ngày dương — trọng số 10
        if len(df_v) >= 21:
            ret_20d = (price - float(df_v['close'].iloc[-21])) / float(df_v['close'].iloc[-21]) * 100
            ok = ret_20d > 0
            checks.append({
                'name': f"VNI 20 ngày: {ret_20d:+.2f}% ({'dương' if ok else 'âm'})",
                'pass': ok, 'weight': 10
            })
            if ok: score += 10
            max_score += 10

        # 9. Không phải biến động cực đoan (volatility regime) — trọng số 10
        try:
            vol_reg = detect_volatility_regime(df_v)
            ok = vol_reg.get('regime') not in ('EXTREME', 'HIGH_PANIC')
            checks.append({
                'name': f"Volatility: {vol_reg.get('regime', 'N/A')} ({'ổn' if ok else 'cao'})",
                'pass': ok, 'weight': 10
            })
            if ok: score += 10
            max_score += 10
        except Exception:
            pass

        # 10. Bollinger Bands — VNI không chạm BB Upper (quá mua) — trọng số 5
        if 'bb_upper' in df_v.columns:
            bb_up = float(last['bb_upper'])
            ok = price < bb_up * 0.98  # cách BB Upper ít nhất 2%
            checks.append({
                'name': f"VNI cách BB Upper ({((bb_up-price)/price*100):+.2f}%) — {'ổn' if ok else 'gần đỉnh BB'}",
                'pass': ok, 'weight': 5
            })
            if ok: score += 5
            max_score += 5

        # Normalize về thang 100
        score_norm = int(score / max_score * 100) if max_score > 0 else 0

        # Verdict
        if score_norm >= 70:
            verdict = '🟢 NÊN MUA'
            verdict_msg = 'Thị trường thuận lợi — Có thể tăng size lệnh'
            color = 'green'
        elif score_norm >= 50:
            verdict = '🟡 THẬN TRỌNG'
            verdict_msg = 'Tín hiệu trộn — Mua được nhưng size nhỏ + SL chặt'
            color = 'orange'
        elif score_norm >= 30:
            verdict = '🟠 RỦI RO CAO'
            verdict_msg = 'Nhiều dấu hiệu xấu — Chỉ vào với rủi ro thấp, ưu tiên mã leader'
            color = 'orange'
        else:
            verdict = '🔴 ĐỨNG NGOÀI'
            verdict_msg = 'Thị trường yếu — Nên đứng ngoài, chờ tín hiệu rõ ràng'
            color = 'red'

        return {
            'verdict': verdict,
            'verdict_msg': verdict_msg,
            'color': color,
            'score': score_norm,
            'score_raw': score,
            'max_score': max_score,
            'checks': checks,
            'n_passed': sum(1 for c in checks if c['pass']),
            'n_total': len(checks),
        }
    except Exception as e:
        return {'verdict': 'ERROR', 'score': 0, 'checks': [],
                'message': f'Lỗi tính score: {str(e)[:80]}'}


@st.cache_data(ttl=900, max_entries=5, show_spinner=False)
def calc_market_breadth_dashboard(tickers_str: str, date_key: str) -> dict:
    """[V34-B1] Market Breadth: A/D ratio + % mã trên MA20/MA50.
    Đo "sức rộng" của thị trường."""
    try:
        tickers_list = json.loads(tickers_str)
        # Lấy mẫu ngẫu nhiên 50 mã (đủ thống kê, không quá chậm)
        sample = tickers_list[:50] if len(tickers_list) > 50 else tickers_list

        up_count = 0
        down_count = 0
        flat_count = 0
        above_ma20 = 0
        above_ma50 = 0
        total = 0

        for t in sample:
            try:
                df_m = get_price(t, days=60)
                if not valid(df_m) or len(df_m) < 50:
                    continue
                df_m = calc_indicators(df_m)
                last_m = df_m.iloc[-1]
                ret = float(last_m.get('return_1d', 0))

                if ret > 0.001:
                    up_count += 1
                elif ret < -0.001:
                    down_count += 1
                else:
                    flat_count += 1

                price = float(last_m['close'])
                if price > float(last_m['ma20']):
                    above_ma20 += 1
                if 'ma50' in df_m.columns and price > float(last_m['ma50']):
                    above_ma50 += 1
                total += 1
            except Exception:
                continue

        if total == 0:
            return {'message': 'Không quét được mã nào'}

        ad_ratio = up_count / max(down_count, 1)

        return {
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count,
            'total': total,
            'ad_ratio': round(ad_ratio, 2),
            'pct_above_ma20': round(above_ma20 / total * 100, 1),
            'pct_above_ma50': round(above_ma50 / total * 100, 1),
        }
    except Exception as e:
        return {'message': f'Lỗi: {str(e)[:80]}'}


def calc_fear_greed_index(df_vni_input: pd.DataFrame = None) -> dict:
    """[V34-B4 / V35-FIX] Fear & Greed Index proxy.
    Nhận df_vni từ session (E1VFVN30) để tránh 403."""
    try:
        if df_vni_input is not None and valid(df_vni_input):
            df_vni = df_vni_input
        else:
            df_vni = get_vnindex_cached()
        if not valid(df_vni) or len(df_vni) < 50:
            return {'index': 50, 'label': '❓ Không tính được', 'color': 'gray'}

        df_v = calc_indicators(df_vni.copy()) if 'rsi' not in df_vni.columns else df_vni.copy()
        last = df_v.iloc[-1]

        # Thành phần 1: RSI (0-100, càng cao càng GREED)
        rsi = float(last['rsi'])
        rsi_score = rsi  # Đã ở thang 0-100

        # Thành phần 2: Volatility (ngược: vol cao = FEAR)
        # Tính std return 20 phiên
        if 'return_1d' in df_v.columns and len(df_v) >= 20:
            vol_20 = float(df_v['return_1d'].tail(20).std()) * 100
            # vol cao = fear (đảo: 100 - vol*10, capped)
            vol_score = max(0, min(100, 100 - vol_20 * 8))
        else:
            vol_score = 50

        # Thành phần 3: Momentum (return 20 ngày)
        if len(df_v) >= 21:
            ret_20 = (float(last['close']) - float(df_v['close'].iloc[-21])) / float(df_v['close'].iloc[-21]) * 100
            # Map ret_20 từ -10% → 0, +10% → 100
            mom_score = max(0, min(100, 50 + ret_20 * 5))
        else:
            mom_score = 50

        # Thành phần 4: BB position (price vs upper/lower)
        bb_score = 50
        if 'bb_upper' in df_v.columns and 'bb_lower' in df_v.columns:
            bb_up = float(last['bb_upper'])
            bb_lo = float(last['bb_lower'])
            price = float(last['close'])
            if bb_up > bb_lo:
                # Map: BB lower = 0 (fear), BB upper = 100 (greed)
                bb_score = max(0, min(100, (price - bb_lo) / (bb_up - bb_lo) * 100))

        # Tổng hợp (trọng số)
        index = (rsi_score * 0.3 + vol_score * 0.2 + mom_score * 0.3 + bb_score * 0.2)
        index = int(index)

        # Label
        if index >= 75:
            label = '🤑 EXTREME GREED (Quá tham lam)'
            color = 'red'
            advice = '⚠️ Cẩn thận đỉnh — Cân nhắc chốt lời'
        elif index >= 55:
            label = '😊 GREED (Tham lam)'
            color = 'orange'
            advice = 'Thị trường hưng phấn — Mua chọn lọc, không FOMO'
        elif index >= 45:
            label = '😐 NEUTRAL (Trung tính)'
            color = 'yellow'
            advice = 'Thị trường cân bằng — Chờ tín hiệu rõ'
        elif index >= 25:
            label = '😰 FEAR (Sợ hãi)'
            color = 'blue'
            advice = 'Tâm lý yếu — Có thể là cơ hội cho người dũng cảm'
        else:
            label = '😨 EXTREME FEAR (Quá sợ hãi)'
            color = 'green'
            advice = '💎 Cơ hội đáy — Mua dần khi mọi người hoảng loạn'

        return {
            'index': index,
            'label': label,
            'color': color,
            'advice': advice,
            'components': {
                'rsi': round(rsi_score, 1),
                'volatility': round(vol_score, 1),
                'momentum': round(mom_score, 1),
                'bb_position': round(bb_score, 1),
            }
        }
    except Exception as e:
        return {'index': 50, 'label': f'❓ Lỗi: {str(e)[:50]}', 'color': 'gray'}


def calc_vni_support_resistance(df_vni_input: pd.DataFrame = None) -> dict:
    """[V34-B5 / V35-FIX] Tìm mức kháng cự / hỗ trợ gần nhất.
    Nhận df_vni từ session (E1VFVN30)."""
    try:
        if df_vni_input is not None and valid(df_vni_input):
            df_vni = df_vni_input
        else:
            df_vni = get_vnindex_cached()
        if not valid(df_vni) or len(df_vni) < 30:
            return {'message': 'Không đủ data'}

        df_v = calc_indicators(df_vni.copy()) if 'rsi' not in df_vni.columns else df_vni.copy()
        last = df_v.iloc[-1]
        cur_price = float(last['close'])

        # Tìm pivot trong 60 phiên gần nhất
        recent = df_v.tail(60).copy()
        highs = recent['high'].values
        lows = recent['low'].values

        # Tìm các đỉnh local (cao hơn 2 bên trong 3 phiên)
        resistances = []
        supports = []
        for i in range(3, len(highs) - 3):
            # Local high
            if highs[i] > highs[i-1] and highs[i] > highs[i+1] \
                and highs[i] > highs[i-2] and highs[i] > highs[i+2]:
                if highs[i] > cur_price:
                    resistances.append(float(highs[i]))
            # Local low
            if lows[i] < lows[i-1] and lows[i] < lows[i+1] \
                and lows[i] < lows[i-2] and lows[i] < lows[i+2]:
                if lows[i] < cur_price:
                    supports.append(float(lows[i]))

        # Lấy gần nhất
        nearest_res = min(resistances) if resistances else None
        nearest_sup = max(supports) if supports else None

        # Thêm Bollinger Bands làm cản
        bb_upper = float(last.get('bb_upper', 0))
        bb_lower = float(last.get('bb_lower', 0))

        result = {
            'cur_price': cur_price,
            'nearest_resistance': nearest_res,
            'nearest_support': nearest_sup,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
        }

        # Tính khoảng cách %
        if nearest_res:
            result['dist_to_resistance'] = round((nearest_res - cur_price) / cur_price * 100, 2)
        if nearest_sup:
            result['dist_to_support'] = round((cur_price - nearest_sup) / cur_price * 100, 2)

        # Cảnh báo
        warnings = []
        if nearest_res and result.get('dist_to_resistance', 999) < 2:
            warnings.append(f"⚠️ VNI cách kháng cự {nearest_res:,.0f} chỉ {result['dist_to_resistance']:.1f}% — sắp đụng cản")
        if nearest_sup and result.get('dist_to_support', 999) < 2:
            warnings.append(f"⚠️ VNI cách hỗ trợ {nearest_sup:,.0f} chỉ {result['dist_to_support']:.1f}% — nguy hiểm")
        if bb_upper > 0 and cur_price > bb_upper * 0.99:
            warnings.append(f"⚠️ VNI chạm/vượt BB Upper {bb_upper:,.0f} — quá mua kỹ thuật")
        result['warnings'] = warnings

        return result
    except Exception as e:
        return {'message': f'Lỗi: {str(e)[:80]}'}


def detect_vni_divergence(df_vni_input: pd.DataFrame = None) -> dict:
    """[V34-C1 / V35-FIX] Phát hiện phân kỳ giá-RSI.
    Nhận df_vni từ session (E1VFVN30)."""
    try:
        if df_vni_input is not None and valid(df_vni_input):
            df_vni = df_vni_input
        else:
            df_vni = get_vnindex_cached()
        if not valid(df_vni) or len(df_vni) < 30:
            return {'divergence': None, 'message': 'Không đủ data'}

        df_v = calc_indicators(df_vni.copy()) if 'rsi' not in df_vni.columns else df_vni.copy()
        recent = df_v.tail(30).copy().reset_index(drop=True)

        prices = recent['close'].values
        rsis = recent['rsi'].values

        # Tìm 2 đỉnh cao nhất (price)
        # Tìm 2 đáy thấp nhất (price)
        n = len(prices)

        # Lấy top 2 đỉnh
        top_indices = sorted(range(n), key=lambda i: prices[i], reverse=True)[:5]
        top_indices = [i for i in top_indices if 3 < i < n-3][:2]
        # Lấy top 2 đáy
        bot_indices = sorted(range(n), key=lambda i: prices[i])[:5]
        bot_indices = [i for i in bot_indices if 3 < i < n-3][:2]

        divergence = None
        message = "Không phát hiện phân kỳ rõ rệt trong 30 phiên gần nhất"

        if len(top_indices) >= 2:
            top_indices.sort()  # theo thời gian
            i1, i2 = top_indices[0], top_indices[1]
            # Bearish: price tăng, RSI giảm
            if prices[i2] > prices[i1] and rsis[i2] < rsis[i1] - 2:
                divergence = 'BEARISH'
                message = (f"🔴 PHÂN KỲ GIẢM (Bearish): Giá VNI tạo đỉnh cao hơn "
                            f"({prices[i1]:,.0f}→{prices[i2]:,.0f}) nhưng RSI tạo đỉnh thấp hơn "
                            f"({rsis[i1]:.0f}→{rsis[i2]:.0f}) → Cảnh báo đảo chiều GIẢM")

        if not divergence and len(bot_indices) >= 2:
            bot_indices.sort()
            i1, i2 = bot_indices[0], bot_indices[1]
            # Bullish: price giảm, RSI tăng
            if prices[i2] < prices[i1] and rsis[i2] > rsis[i1] + 2:
                divergence = 'BULLISH'
                message = (f"🟢 PHÂN KỲ TĂNG (Bullish): Giá VNI tạo đáy thấp hơn "
                            f"({prices[i1]:,.0f}→{prices[i2]:,.0f}) nhưng RSI tạo đáy cao hơn "
                            f"({rsis[i1]:.0f}→{rsis[i2]:.0f}) → Tín hiệu đảo chiều TĂNG")

        return {'divergence': divergence, 'message': message}
    except Exception as e:
        return {'divergence': None, 'message': f'Lỗi: {str(e)[:80]}'}


# [V34 HELPERS END]

# ──────────────────────────────────────────────────────────────────────────────
# [V36-N1] SMART MONEY PROXY — Phát hiện qua price-volume action
# ──────────────────────────────────────────────────────────────────────────────
def detect_smart_money_proxy(df: pd.DataFrame) -> dict:
    """[V36-N1] Phát hiện dấu hiệu smart money qua price-volume.
    Không cần data foreign/prop thật.

    4 trạng thái:
    - ACCUMULATION (Tích lũy thầm): giá đi ngang/giảm nhẹ + vol thấp đều
    - DISTRIBUTION (Phân phối thầm): giá đi ngang/tăng nhẹ + vol cao bất thường
    - STRONG_BUY: giá tăng mạnh + vol cực cao (institutional buying)
    - STRONG_SELL: giá giảm mạnh + vol bùng (institutional selling)
    """
    try:
        if not valid(df) or len(df) < 20:
            return {'signal': None, 'message': 'Không đủ data'}

        recent = df.tail(10).copy()
        ma_vol = float(df['volume'].tail(20).mean()) if 'volume' in df.columns else 0
        if ma_vol == 0:
            return {'signal': None, 'message': 'Không có vol data'}

        # Tính thông số 10 ngày gần nhất
        prices = recent['close'].values
        vols = recent['volume'].values
        rets = [(prices[i] - prices[i-1]) / prices[i-1] * 100 for i in range(1, len(prices))]

        avg_ret = sum(rets) / len(rets) if rets else 0
        avg_vol_ratio = sum(v / ma_vol for v in vols) / len(vols)
        high_vol_days = sum(1 for v in vols if v > ma_vol * 1.5)
        very_high_vol_days = sum(1 for v in vols if v > ma_vol * 2.5)

        # Phân tích
        signals = []
        primary = None
        message = ""
        confidence = 0   # 0-100

        # 1. STRONG_BUY: giá tăng mạnh + vol cao đều
        if avg_ret > 0.5 and avg_vol_ratio > 1.5 and high_vol_days >= 4:
            primary = 'STRONG_BUY'
            message = f"💎 MUA MẠNH: Giá +{avg_ret:.1f}%/ngày + Vol {avg_vol_ratio:.1f}x (cao đều)"
            confidence = min(95, 60 + high_vol_days * 5 + int(avg_ret * 10))
            signals.append(message)

        # 2. STRONG_SELL: giá giảm mạnh + vol bùng
        elif avg_ret < -0.5 and avg_vol_ratio > 1.5 and high_vol_days >= 4:
            primary = 'STRONG_SELL'
            message = f"🔴 BÁN MẠNH: Giá {avg_ret:.1f}%/ngày + Vol {avg_vol_ratio:.1f}x"
            confidence = min(95, 60 + high_vol_days * 5 + int(abs(avg_ret) * 10))
            signals.append(message)

        # 3. ACCUMULATION: giá ngang/giảm nhẹ + vol thấp đều (smart money gom thầm)
        elif -0.3 < avg_ret < 0.3 and avg_vol_ratio < 1.0 and high_vol_days <= 2:
            primary = 'ACCUMULATION'
            message = f"🤫 TÍCH LŨY THẦM: Giá ngang ({avg_ret:+.1f}%) + Vol thấp ({avg_vol_ratio:.1f}x)"
            confidence = 65
            signals.append(message)
            signals.append("→ Smart money có thể đang gom hàng. Theo dõi break out trong 1-2 tuần.")

        # 4. DISTRIBUTION: giá ngang/tăng nhẹ + vol bất thường cao (smart money xả thầm)
        elif -0.3 < avg_ret < 1.0 and avg_vol_ratio > 1.3 and very_high_vol_days >= 2:
            primary = 'DISTRIBUTION'
            message = f"⚠️ PHÂN PHỐI THẦM: Giá {avg_ret:+.1f}% nhưng Vol bất thường cao ({avg_vol_ratio:.1f}x, {very_high_vol_days} phiên >2.5x)"
            confidence = 70
            signals.append(message)
            signals.append("→ Cảnh báo: Smart money có thể đang xả hàng cho retail. Cẩn thận!")

        # 5. BREAKOUT_ATTEMPT: 1 phiên gần nhất vol cực cao + giá tăng
        last_ret = rets[-1] if rets else 0
        last_vol = vols[-1] / ma_vol if ma_vol > 0 else 0
        if last_ret > 2 and last_vol > 2.5:
            signals.append(f"🔥 Hôm nay: +{last_ret:.1f}% với Vol {last_vol:.1f}x → Breakout có vol")
            if not primary:
                primary = 'STRONG_BUY'
                confidence = 75

        # 6. BLOW_OFF_TOP: 1 phiên cuối tăng cực mạnh + vol khủng (cảnh báo đỉnh)
        if last_ret > 5 and last_vol > 3:
            signals.append(f"🎢 Hôm nay tăng {last_ret:.1f}% Vol {last_vol:.1f}x — Cẩn thận BLOW-OFF (đỉnh)")

        # 7. CAPITULATION: 1 phiên cuối giảm cực mạnh + vol khủng (đáy panic)
        if last_ret < -5 and last_vol > 3:
            signals.append(f"💥 Hôm nay giảm {last_ret:.1f}% Vol {last_vol:.1f}x — Có thể CAPITULATION (đáy panic)")

        if not primary:
            primary = 'NEUTRAL'
            message = "Không có dấu hiệu smart money rõ rệt"
            confidence = 30

        return {
            'signal': primary,
            'message': message,
            'signals': signals,
            'confidence': confidence,
            'avg_ret_10d': round(avg_ret, 2),
            'avg_vol_ratio': round(avg_vol_ratio, 2),
            'high_vol_days': high_vol_days,
            'very_high_vol_days': very_high_vol_days,
        }
    except Exception as e:
        return {'signal': None, 'message': f'Lỗi: {str(e)[:80]}'}


# ──────────────────────────────────────────────────────────────────────────────
# [V36-N4] SECTOR STRENGTH HEATMAP — 4 timeframes
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, max_entries=3, show_spinner=False)
def calc_sector_strength_matrix(date_key: str) -> dict:
    """[V36-N4] Tính ma trận sức mạnh ngành: 4 timeframes (1d, 5d, 20d, 60d).
    Trả về DataFrame để render heatmap."""
    try:
        # Bản đồ ngành → mã đại diện
        SECTOR_MAP = {
            '🏦 Ngân hàng': ['VCB', 'BID', 'CTG', 'ACB', 'TCB', 'MBB', 'STB', 'TPB', 'VPB'],
            '🏢 Bất động sản': ['VHM', 'VIC', 'NVL', 'PDR', 'DXG', 'KDH', 'NLG', 'KBC'],
            '🏗️ Thép': ['HPG', 'HSG', 'NKG'],
            '⛽ Dầu khí': ['GAS', 'PLX', 'PVD', 'PVS', 'BSR'],
            '🛒 Bán lẻ': ['MWG', 'FRT', 'PNJ', 'DGW'],
            '💻 Công nghệ': ['FPT', 'CMG', 'ELC'],
            '🥛 Thực phẩm-Bia': ['VNM', 'MSN', 'SAB', 'KDC'],
            '🚛 Logistics': ['GMD', 'HAH', 'VSC', 'PHP'],
            '⚡ Điện-NL': ['POW', 'PPC', 'NT2', 'GEG', 'REE'],
            '🏭 Hóa chất': ['DGC', 'DPM', 'DCM'],
            '✈️ Hàng không': ['HVN', 'VJC'],
            '🚗 Ô tô': ['VEA', 'TMT'],
            '💊 Dược': ['DHG', 'IMP', 'DBD'],
            '🌾 Nông nghiệp': ['HAG', 'HNG', 'BAF', 'DBC'],
            '🏠 Vật liệu XD': ['HT1', 'BCC', 'VGC'],
        }

        rows = []
        for sector, tickers_s in SECTOR_MAP.items():
            # Tính TB return cho từng timeframe
            ret_1d = []
            ret_5d = []
            ret_20d = []
            ret_60d = []
            n_ok = 0
            for t in tickers_s:
                try:
                    df_s = get_price(t, days=80)
                    if not valid(df_s) or len(df_s) < 65:
                        continue
                    cur = float(df_s['close'].iloc[-1])
                    if len(df_s) >= 2:
                        ret_1d.append((cur - float(df_s['close'].iloc[-2])) / float(df_s['close'].iloc[-2]) * 100)
                    if len(df_s) >= 6:
                        ret_5d.append((cur - float(df_s['close'].iloc[-6])) / float(df_s['close'].iloc[-6]) * 100)
                    if len(df_s) >= 21:
                        ret_20d.append((cur - float(df_s['close'].iloc[-21])) / float(df_s['close'].iloc[-21]) * 100)
                    if len(df_s) >= 61:
                        ret_60d.append((cur - float(df_s['close'].iloc[-61])) / float(df_s['close'].iloc[-61]) * 100)
                    n_ok += 1
                except Exception:
                    continue

            if n_ok == 0:
                continue

            rows.append({
                'sector': sector,
                'n_stocks': n_ok,
                'ret_1d': round(sum(ret_1d)/len(ret_1d), 2) if ret_1d else 0,
                'ret_5d': round(sum(ret_5d)/len(ret_5d), 2) if ret_5d else 0,
                'ret_20d': round(sum(ret_20d)/len(ret_20d), 2) if ret_20d else 0,
                'ret_60d': round(sum(ret_60d)/len(ret_60d), 2) if ret_60d else 0,
            })

        if not rows:
            return {'message': 'Không quét được data'}

        # Sort theo ret_5d giảm dần (xếp ngành mạnh nhất lên đầu)
        rows.sort(key=lambda x: x['ret_5d'], reverse=True)

        return {
            'rows': rows,
            'n_sectors': len(rows),
            'leaders': rows[:3],   # Top 3 ngành dẫn dắt
            'laggards': rows[-3:][::-1],  # 3 ngành tệ nhất
        }
    except Exception as e:
        return {'message': f'Lỗi: {str(e)[:80]}'}


# ──────────────────────────────────────────────────────────────────────────────
# [V36-N6] WATCHLIST THEO NGÀNH (Groups)
# ──────────────────────────────────────────────────────────────────────────────
V36_WL_GROUPS_FILE = 'v36_wl_groups.json'

def load_wl_groups() -> dict:
    """[V36-N6] Load watchlist groups (theo ngành)."""
    try:
        if not os.path.exists(V36_WL_GROUPS_FILE):
            return {}
        with open(V36_WL_GROUPS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_wl_groups(groups: dict) -> bool:
    try:
        with open(V36_WL_GROUPS_FILE, 'w', encoding='utf-8') as f:
            json.dump(groups, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# [V36 HELPERS END]

# ──────────────────────────────────────────────────────────────────────────────
# [V37] EARLY MOMENTUM SCANNER — Phát hiện sớm mã đang trong chuỗi tăng
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600, max_entries=10, show_spinner=False)
def scan_early_momentum(tickers_str: str, min_streak: int, min_gain_per_day: float,
                          filter_rsi: bool, filter_liq: bool,
                          date_key: str, filter_ma10_cross: bool = False,
                          filter_rut_chan: bool = False) -> dict:
    """[V37+V39+V41] Quét mã đang trong chuỗi tăng N ngày liên tiếp.

    Args:
        filter_ma10_cross: [V39] chỉ mã VỪA CẮT LÊN MA10
        filter_rut_chan: [V41] chỉ mã có RÚT CHÂN signal (STRONG/GOOD/MILD)
    """
    try:
        tickers = json.loads(tickers_str)
    except Exception:
        return {'day2': [], 'day3': [], 'day4_plus': [], 'errors': []}

    day2 = []
    day3 = []
    day4_plus = []
    errors = []

    for t in tickers:
        try:
            df_m = get_price(t, days=60)
            if not valid(df_m) or len(df_m) < 30:
                continue
            df_m = calc_indicators(df_m)

            # Filter LIQ
            if filter_liq:
                try:
                    liq = calc_liquidity_tier(df_m)
                    if liq.get('tier') == 'LOW':
                        continue
                except Exception:
                    pass

            last = df_m.iloc[-1]
            price = float(last['close'])
            rsi = float(last['rsi'])
            vol_strength = float(last.get('vol_strength', 1.0))

            # Filter RSI quá mua
            if filter_rsi and rsi >= 75:
                continue

            # Tính chuỗi tăng từ ngày gần nhất ngược về
            closes = df_m['close'].tail(15).tolist()
            streak = 0
            daily_gains = []
            total_gain = 0
            for i in range(len(closes) - 1, 0, -1):
                gain = (closes[i] - closes[i-1]) / closes[i-1] * 100
                if gain >= min_gain_per_day:
                    streak += 1
                    daily_gains.insert(0, round(gain, 2))
                    total_gain += gain
                else:
                    break

            # Loại nếu chưa đủ streak
            if streak < min_streak:
                continue

            avg_gain = total_gain / streak if streak > 0 else 0

            # [E2] Xác suất tiếp tục tăng (heuristic dựa trên patterns lịch sử)
            # Quy tắc thô: streak càng dài, xác suất tiếp tục càng giảm
            # streak=2: ~55%, streak=3: ~45%, streak=4: ~35%, streak=5+: ~25%
            prob_continue = max(20, 65 - streak * 10)
            # Cộng nếu có vol nổ
            if vol_strength > 1.5:
                prob_continue += 10
            # Trừ nếu RSI cao
            if rsi >= 70:
                prob_continue -= 15
            prob_continue = max(15, min(80, prob_continue))

            # [E3] RSI warning
            rsi_warning = None
            if rsi >= 70:
                rsi_warning = f"⚠️ RSI={rsi:.0f} (gần quá mua)"
            elif rsi >= 65:
                rsi_warning = f"🟡 RSI={rsi:.0f} (cẩn thận)"

            # [E4] Vol đột biến
            vol_alert = None
            if vol_strength >= 2.0:
                vol_alert = f"🔥 Vol nổ {vol_strength:.1f}x"
            elif vol_strength >= 1.5:
                vol_alert = f"📊 Vol mạnh {vol_strength:.1f}x"

            # MA20 check
            ma20 = float(last.get('ma20', price))
            above_ma20 = price > ma20

            # [V39-M2] MA10 Booster info
            try:
                ma10_info = calc_ma10_bonus(df_m)
            except Exception:
                ma10_info = {'bonus': 0, 'signal_type': None,
                              'is_cross_up': False, 'cur_ma10': 0,
                              'message': '', 'pct_vs_ma10': 0}

            # [V39] Filter: nếu user yêu cầu chỉ mã cắt lên MA10 → skip nếu không cắt
            if filter_ma10_cross and not ma10_info.get('is_cross_up'):
                continue

            # [V40-F4] Float info (nhẹ, không filter, chỉ hiển thị)
            try:
                _f_date = date_key[:10]  # chỉ lấy YYYY-MM-DD
                float_info = get_float_data_cached(t, _f_date)
                if float_info.get('available'):
                    _ff = float_info['free_float_pct']
                    _fr = float_info['foreigner_pct']
                    _ft = classify_float_tier(_ff, _fr)
                    float_tier = _ft['tier']
                    float_pct = _ff
                else:
                    float_tier = None
                    float_pct = 0
            except Exception:
                float_tier = None
                float_pct = 0

            # [V41-R3] Rút Chân info
            try:
                rc_info = detect_rut_chan(df_m)
                rc_signal = rc_info.get('signal')
                rc_quality = rc_info.get('quality_score', 0)
            except Exception:
                rc_info = {}
                rc_signal = None
                rc_quality = 0

            # [V41] Filter: nếu user yêu cầu chỉ mã rút chân → skip nếu không có
            if filter_rut_chan and not rc_signal:
                continue

            row_data = {
                'ticker': t,
                'price': price,
                'rsi': round(rsi, 1),
                'streak': streak,
                'daily_gains': daily_gains,
                'total_gain': round(total_gain, 2),
                'avg_gain': round(avg_gain, 2),
                'vol_strength': round(vol_strength, 2),
                'above_ma20': above_ma20,
                'prob_continue': prob_continue,
                'rsi_warning': rsi_warning,
                'vol_alert': vol_alert,
                # [V39] MA10 info
                'ma10': round(ma10_info.get('cur_ma10', 0), 2),
                'ma10_bonus': ma10_info.get('bonus', 0),
                'ma10_signal': ma10_info.get('signal_type'),
                'ma10_is_cross_up': ma10_info.get('is_cross_up', False),
                'ma10_pct': ma10_info.get('pct_vs_ma10', 0),
                # [V40-F4] Float info
                'float_tier': float_tier,
                'float_pct': float_pct,
                # [V41-R3] Rút Chân
                'rc_signal': rc_signal,
                'rc_quality': rc_quality,
                'rc_drop_pct': rc_info.get('drop_pct', 0),
                'rc_recovery_pct': rc_info.get('recovery_pct', 0),
            }

            # Phân nhóm
            if streak == 2:
                day2.append(row_data)
            elif streak == 3:
                day3.append(row_data)
            else:  # 4+
                day4_plus.append(row_data)
        except Exception as e:
            errors.append({'ticker': t, 'error': str(e)[:80]})
            continue

    # Sort mỗi nhóm theo prob_continue giảm dần (cao nhất lên đầu)
    day2.sort(key=lambda x: (x['prob_continue'], x['avg_gain']), reverse=True)
    day3.sort(key=lambda x: (x['prob_continue'], x['avg_gain']), reverse=True)
    day4_plus.sort(key=lambda x: (x['prob_continue'], x['avg_gain']), reverse=True)

    return {
        'day2': day2,
        'day3': day3,
        'day4_plus': day4_plus,
        'errors': errors,
        'n_scanned': len(tickers),
        'scan_date': date_key,
    }


def render_momentum_card(row: dict, highlight_color: str = 'blue') -> None:
    """[V37+V39+V40] Render 1 card mã trong Early Momentum Scanner."""
    with st.container(border=True):
        c1, c2, c3 = st.columns([1.5, 3, 1.5])
        with c1:
            st.markdown(f"### `{row['ticker']}`")
            st.caption(f"Giá: **{row['price']:,.0f}**")
            st.caption(f"RSI: {row['rsi']}")
            # [V39] MA10 mini
            if row.get('ma10', 0) > 0:
                pct = row.get('ma10_pct', 0)
                if row.get('ma10_is_cross_up'):
                    st.caption(f"⭐ MA10: {row['ma10']:,.2f} (cross-up!)")
                elif pct > 0:
                    st.caption(f"📊 MA10: {row['ma10']:,.2f} ({pct:+.1f}%)")
                else:
                    st.caption(f"📉 MA10: {row['ma10']:,.2f} ({pct:+.1f}%)")
        with c2:
            gains_str = " → ".join([f"+{g:.1f}%" for g in row['daily_gains']])
            st.markdown(f"**🔥 {row['streak']} ngày liên tiếp:** {gains_str}")
            st.caption(f"Tổng tăng: **+{row['total_gain']:.2f}%** | TB +{row['avg_gain']:.2f}%/ngày")
            if row.get('vol_alert'):
                st.caption(row['vol_alert'])
            if row.get('rsi_warning'):
                st.caption(row['rsi_warning'])
            if not row.get('above_ma20'):
                st.caption("📉 Giá đang DƯỚI MA20 (xu hướng vẫn yếu)")
            else:
                st.caption("📈 Giá trên MA20")
            # [V39] MA10 signal nếu cross_up
            if row.get('ma10_is_cross_up'):
                st.success(f"⭐ **MA10 CROSS-UP** — Vạch vàng signal mới (+{row.get('ma10_bonus', 0)} điểm)")
            # [V40-F4] Float warning badge (nếu data có)
            float_tier = row.get('float_tier')
            float_pct = row.get('float_pct', 0)
            if float_tier == 'VERY_LOW':
                st.error(f"🔴 Float CỰC thấp ({float_pct:.1f}%) — Pump risk cao")
            elif float_tier == 'LOW':
                st.warning(f"🟠 Float thấp ({float_pct:.1f}%) — Cẩn thận biến động")
            # [V41-R3] Rút Chân badge
            rc_sig = row.get('rc_signal')
            if rc_sig == 'STRONG':
                st.success(f"💎 **RÚT CHÂN STRONG** — Giảm {row.get('rc_drop_pct', 0):.1f}% rồi hồi {row.get('rc_recovery_pct', 0):.0f}% (Quality: {row.get('rc_quality', 0)}/100)")
            elif rc_sig == 'GOOD':
                st.info(f"🟢 Rút chân GOOD — Hồi {row.get('rc_recovery_pct', 0):.0f}% (Q: {row.get('rc_quality', 0)}/100)")
            elif rc_sig == 'MILD':
                st.caption(f"🟡 Rút chân nhẹ — Hồi {row.get('rc_recovery_pct', 0):.0f}%")
        with c3:
            # Xác suất tiếp tục tăng
            prob = row['prob_continue']
            if prob >= 60:
                st.success(f"🎯 Tiếp tục: **{prob}%**")
            elif prob >= 40:
                st.info(f"🎯 Tiếp tục: {prob}%")
            else:
                st.warning(f"🎯 Tiếp tục: {prob}%")
            # [V39] MA10 Bonus
            ma10_b = row.get('ma10_bonus', 0)
            if ma10_b > 0:
                st.caption(f"🟡 MA10: +{ma10_b}")
            elif ma10_b < 0:
                st.caption(f"🟡 MA10: {ma10_b}")


# [V37 HELPERS END]

# ──────────────────────────────────────────────────────────────────────────────
# [V39] MA10 BOOSTER — Vạch vàng signal (tách riêng, không động V23 core)
# ──────────────────────────────────────────────────────────────────────────────
def calc_ma10_bonus(df: pd.DataFrame) -> dict:
    """[V39] Tính điểm bonus dựa trên tín hiệu MA10 (vạch vàng).

    Logic:
    - +10 nếu giá > MA10 (cơ bản)
    - +10 nếu MA10 slope DƯƠNG trong 5 phiên (đường vàng uốn lên)
    - +15 nếu vừa CẮT LÊN MA10 trong 3 phiên gần nhất (signal mới, ngon nhất)
    - -10 nếu giá vừa cắt XUỐNG MA10 trong 3 phiên (cảnh báo)
    - Cap 0-30 điểm

    Returns: dict {bonus, signal_type, message, details, is_cross_up, is_cross_down}
    """
    try:
        if not valid(df) or len(df) < 15:
            return {'bonus': 0, 'signal_type': None,
                    'message': 'Không đủ data tính MA10',
                    'details': [], 'is_cross_up': False, 'is_cross_down': False}

        # Đảm bảo có cột ma10
        df_calc = df.copy()
        if 'ma10' not in df_calc.columns:
            df_calc['ma10'] = df_calc['close'].rolling(10).mean()

        # Lấy 6 phiên gần nhất
        recent = df_calc.tail(6).copy().reset_index(drop=True)
        if len(recent) < 6 or pd.isna(recent['ma10'].iloc[-1]):
            return {'bonus': 0, 'signal_type': None,
                    'message': 'MA10 chưa tính được',
                    'details': [], 'is_cross_up': False, 'is_cross_down': False}

        last = recent.iloc[-1]
        cur_price = float(last['close'])
        cur_ma10 = float(last['ma10'])

        bonus = 0
        details = []
        signal_type = 'NEUTRAL'
        is_cross_up = False
        is_cross_down = False

        # 1. Giá > MA10 hay không?
        above_ma10 = cur_price > cur_ma10
        pct_vs_ma10 = (cur_price - cur_ma10) / cur_ma10 * 100
        if above_ma10:
            bonus += 10
            details.append(f"✅ Giá {cur_price:,.2f} > MA10 {cur_ma10:,.2f} ({pct_vs_ma10:+.2f}%)")
        else:
            details.append(f"❌ Giá {cur_price:,.2f} dưới MA10 {cur_ma10:,.2f} ({pct_vs_ma10:+.2f}%)")

        # 2. MA10 slope (dương hay âm trong 5 phiên)
        ma10_5d_ago = float(recent['ma10'].iloc[0])
        if not pd.isna(ma10_5d_ago) and ma10_5d_ago > 0:
            slope_pct = (cur_ma10 - ma10_5d_ago) / ma10_5d_ago * 100
            if slope_pct > 0.3:
                bonus += 10
                details.append(f"✅ MA10 slope DƯƠNG (+{slope_pct:.2f}% trong 5 phiên) — Vạch vàng uốn lên")
            elif slope_pct < -0.3:
                details.append(f"❌ MA10 slope ÂM ({slope_pct:.2f}% trong 5 phiên)")
            else:
                details.append(f"🟡 MA10 slope NGANG ({slope_pct:+.2f}% trong 5 phiên)")

        # 3. Cross-up trong 3 phiên gần nhất?
        # Xét 3 phiên cuối: nếu có phiên nào giá CẮT LÊN MA10 (trước dưới, sau trên)
        for i in range(len(recent) - 3, len(recent)):
            if i < 1: continue
            prev_close = float(recent['close'].iloc[i-1])
            prev_ma10 = float(recent['ma10'].iloc[i-1])
            cur_close_i = float(recent['close'].iloc[i])
            cur_ma10_i = float(recent['ma10'].iloc[i])
            if pd.isna(prev_ma10) or pd.isna(cur_ma10_i): continue
            # Cross up: trước dưới, sau trên
            if prev_close <= prev_ma10 and cur_close_i > cur_ma10_i:
                is_cross_up = True
                bonus += 15
                days_ago = len(recent) - 1 - i
                ago_str = "Hôm nay" if days_ago == 0 else f"{days_ago} phiên trước"
                details.append(f"⭐ VỪA CẮT LÊN MA10 ({ago_str}) — Signal mới, mạnh nhất")
                break
            # Cross down: trước trên, sau dưới
            if prev_close >= prev_ma10 and cur_close_i < cur_ma10_i:
                is_cross_down = True
                bonus -= 10
                days_ago = len(recent) - 1 - i
                ago_str = "Hôm nay" if days_ago == 0 else f"{days_ago} phiên trước"
                details.append(f"🔴 VỪA CẮT XUỐNG MA10 ({ago_str}) — Cảnh báo")
                break

        # Cap bonus 0-30
        bonus = max(-10, min(30, bonus))

        # Xác định signal_type
        if is_cross_up:
            signal_type = 'CROSS_UP'
            message = '⭐ MA10 CROSS-UP — TÍCH CỰC (vừa cắt lên vạch vàng)'
        elif is_cross_down:
            signal_type = 'CROSS_DOWN'
            message = '🔴 MA10 CROSS-DOWN — Cảnh báo (vừa cắt xuống)'
        elif above_ma10 and bonus >= 15:
            signal_type = 'STRONG_ABOVE'
            message = '🟢 Trên MA10 + slope dương — Xu hướng tăng'
        elif above_ma10:
            signal_type = 'ABOVE'
            message = '🟢 Trên MA10 — Tích cực nhẹ'
        elif not above_ma10:
            signal_type = 'BELOW'
            message = '🔴 Dưới MA10 — Xu hướng yếu'
        else:
            signal_type = 'NEUTRAL'
            message = 'Tín hiệu MA10 trung tính'

        return {
            'bonus': bonus,
            'signal_type': signal_type,
            'message': message,
            'details': details,
            'is_cross_up': is_cross_up,
            'is_cross_down': is_cross_down,
            'cur_price': cur_price,
            'cur_ma10': cur_ma10,
            'pct_vs_ma10': round(pct_vs_ma10, 2),
        }
    except Exception as e:
        return {'bonus': 0, 'signal_type': None,
                'message': f'Lỗi: {str(e)[:60]}',
                'details': [], 'is_cross_up': False, 'is_cross_down': False}


# [V39 HELPER END]

# ──────────────────────────────────────────────────────────────────────────────
# [V40-F1+D1+D2] FLOAT ANALYSIS — Cache 24h + Defensive guard
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=86400, max_entries=500, show_spinner=False)
def get_float_data_cached(ticker: str, date_key: str) -> dict:
    """[V40-F1] Lấy data Float từ vnstock trading_stats() — cache 24h.

    Returns dict:
        free_float_pct: float (0-100)
        foreigner_pct: float (0-100)
        max_foreigner_pct: float (0-100)
        room_left_pct: float (0-100) = max_foreigner - foreigner
        outstanding_share: int (optional)
        avg_match_val_1m: float (tỷ)
        available: bool — True nếu có data, False nếu thiếu/lỗi
        error: str — chi tiết lỗi nếu fail
    """
    result = {
        'free_float_pct': 0,
        'foreigner_pct': 0,
        'max_foreigner_pct': 0,
        'room_left_pct': 0,
        'outstanding_share': 0,
        'avg_match_val_1m': 0,
        'available': False,
        'error': None,
    }
    try:
        stk_fin = Vnstock().stock(symbol=ticker, source='VCI')
        df_ts = stk_fin.company.trading_stats()
        if not valid(df_ts):
            result['error'] = 'No data'
            return result
        row_ts = df_ts.iloc[0]
        ff = float(row_ts.get('free_float_percentage', 0) or 0) * 100
        fr = float(row_ts.get('foreigner_percentage', 0) or 0) * 100
        fr_max = float(row_ts.get('maximum_foreign_percentage', 0) or 0) * 100
        avg_val = float(row_ts.get('average_match_value1_month', 0) or 0)
        out_sh = int(row_ts.get('outstanding_share', 0) or 0)

        # Nếu data trả về 0 cả → coi như không có
        if ff == 0 and fr == 0 and fr_max == 0:
            result['error'] = 'All zeros — data có thể thiếu'
            return result

        result.update({
            'free_float_pct': round(ff, 2),
            'foreigner_pct': round(fr, 2),
            'max_foreigner_pct': round(fr_max, 2),
            'room_left_pct': round(max(0, fr_max - fr), 2),
            'outstanding_share': out_sh,
            'avg_match_val_1m': round(avg_val / 1e9, 1),  # đổi sang tỷ
            'available': True,
            'error': None,
        })
        return result
    except Exception as e:
        result['error'] = str(e)[:100]
        return result


def classify_float_tier(free_float_pct: float, foreigner_pct: float = 0) -> dict:
    """[V40-F1] Phân loại Float Tier.

    Tier:
    - 🟢 HIGH: Free Float > 50%
    - 🟡 MEDIUM: 20-50%
    - 🟠 LOW: 10-20%
    - 🔴 VERY_LOW: < 10%
    - ❓ UNKNOWN: data thiếu
    """
    if free_float_pct <= 0:
        return {
            'tier': 'UNKNOWN',
            'tier_emoji': '❓',
            'message': 'Không có data Float — không đánh giá được',
            'color': 'gray',
            'size_advice': 'N/A',
        }

    # Effective float = free float - foreign holding nếu > 10%
    effective_float = free_float_pct - max(0, foreigner_pct - 10)

    if effective_float > 50:
        tier = 'HIGH'
        emoji = '🟢'
        msg = 'Float cao — Nhiều hàng, khó bị làm giá'
        color = 'green'
        size = 'Đầy đủ (≤ 20% NAV)'
    elif effective_float > 20:
        tier = 'MEDIUM'
        emoji = '🟡'
        msg = 'Float trung bình — Bình thường'
        color = 'yellow'
        size = 'Vừa (≤ 15% NAV)'
    elif effective_float > 10:
        tier = 'LOW'
        emoji = '🟠'
        msg = 'Float thấp — Dễ biến động, cẩn thận'
        color = 'orange'
        size = 'Nhỏ (≤ 10% NAV)'
    else:
        tier = 'VERY_LOW'
        emoji = '🔴'
        msg = 'Float CỰC thấp — Dễ bị làm giá, rủi ro cao'
        color = 'red'
        size = 'Rất nhỏ (≤ 5% NAV) hoặc TRÁNH'

    return {
        'tier': tier,
        'tier_emoji': emoji,
        'message': msg,
        'color': color,
        'size_advice': size,
        'effective_float': round(effective_float, 2),
    }


def detect_float_pump_risk(float_data: dict, vol_strength: float,
                              price_change_pct: float) -> dict:
    """[V40-F3] Phát hiện risk "tay to làm giá" khi Float thấp + Vol nổ + Giá nhảy.

    Trigger conditions (cần TẤT CẢ):
    - Free Float < 20% (LOW/VERY_LOW)
    - Vol > 3x TB
    - |Price change| > 5%
    """
    if not float_data.get('available'):
        return {'risk': False, 'message': None}

    ff = float_data.get('free_float_pct', 0)
    if ff <= 0 or ff >= 20:
        return {'risk': False, 'message': None}

    if vol_strength < 3.0:
        return {'risk': False, 'message': None}

    if abs(price_change_pct) < 5.0:
        return {'risk': False, 'message': None}

    return {
        'risk': True,
        'severity': 'HIGH' if ff < 10 else 'MEDIUM',
        'message': (f"⚠️ **PUMP RISK** — Free Float chỉ {ff:.1f}% + Vol {vol_strength:.1f}x + "
                    f"Giá {price_change_pct:+.1f}% trong 1 phiên\n"
                    f"→ CÓ THỂ BỊ LÀM GIÁ. Cực kỳ cẩn thận!"),
    }


# [V40 FLOAT HELPERS END]

# ──────────────────────────────────────────────────────────────────────────────
# [V41] RÚT CHÂN DETECTOR — Phát hiện nến rút chân về tham chiếu
# ──────────────────────────────────────────────────────────────────────────────

def detect_rut_chan(df: pd.DataFrame) -> dict:
    """[V41] Phát hiện nến "rút chân về tham chiếu" - đặc trưng VN market.

    Logic:
    - Phiên giảm sâu trong ngày nhưng cuối phiên hồi gần về open (tham chiếu)
    - Cho thấy có lực mua bắt đáy mạnh
    - Thường báo hiệu sóng tăng

    Phân loại:
    - STRONG: recovery ≥85% + drop ≥-4%
    - GOOD: recovery ≥70% + drop ≥-3%
    - MILD: recovery ≥65% + drop ≥-2.5%
    - None: không đạt

    Returns dict:
        signal: 'STRONG' | 'GOOD' | 'MILD' | None
        recovery_pct: % phục hồi từ đáy
        drop_pct: % giảm sâu nhất trong phiên
        close_vs_open_pct: close so với open
        vol_strength: vol / TB
        quality_score: 0-100 (phân biệt thật/giả)
        is_at_support: bool — tại MA20/MA50 không
        rsi: float
        message: str — mô tả
        warnings: list — cảnh báo nếu là rút chân giả
    """
    try:
        if not valid(df) or len(df) < 20:
            return {'signal': None, 'message': 'Không đủ data'}

        df_calc = df.copy()
        if 'ma10' not in df_calc.columns:
            df_calc['ma10'] = df_calc['close'].rolling(10).mean()
        if 'ma20' not in df_calc.columns:
            df_calc['ma20'] = df_calc['close'].rolling(20).mean()
        if 'ma50' not in df_calc.columns:
            df_calc['ma50'] = df_calc['close'].rolling(50).mean()

        last = df_calc.iloc[-1]
        open_p = float(last['open'])
        close_p = float(last['close'])
        high_p = float(last['high'])
        low_p = float(last['low'])

        if open_p <= 0 or high_p <= low_p:
            return {'signal': None, 'message': 'Data nến không hợp lệ'}

        # Tính chỉ số
        drop_pct = (low_p - open_p) / open_p * 100  # % giảm sâu nhất so với open
        close_vs_open_pct = (close_p - open_p) / open_p * 100  # % close vs open
        range_size = high_p - low_p
        if range_size <= 0:
            return {'signal': None, 'message': 'Range 0'}
        recovery_pct = (close_p - low_p) / range_size * 100  # % phục hồi từ đáy

        # Vol strength
        vol_strength = float(last.get('vol_strength', 1.0))
        rsi = float(last.get('rsi', 50))

        # Trigger check
        signal = None
        # Điều kiện 1: phải đóng cửa gần/trên tham chiếu (close ≥ open * 0.99)
        # → close không thấp hơn open quá 1%
        close_near_or_above_open = close_vs_open_pct >= -1.0

        # Điều kiện 2: phải giảm sâu trong phiên
        # Điều kiện 3: phục hồi mạnh

        if close_near_or_above_open:
            if drop_pct <= -4.0 and recovery_pct >= 85 and vol_strength >= 1.2:
                signal = 'STRONG'
                emoji = '💎'
                msg = (f"{emoji} **RÚT CHÂN STRONG** — Giảm {drop_pct:.1f}% rồi hồi {recovery_pct:.0f}% "
                        f"về tham chiếu (close {close_vs_open_pct:+.2f}% so open)")
            elif drop_pct <= -3.0 and recovery_pct >= 70 and vol_strength >= 1.0:
                signal = 'GOOD'
                emoji = '🟢'
                msg = (f"{emoji} **RÚT CHÂN GOOD** — Giảm {drop_pct:.1f}% rồi hồi {recovery_pct:.0f}% "
                        f"(close {close_vs_open_pct:+.2f}%)")
            elif drop_pct <= -2.5 and recovery_pct >= 65:
                signal = 'MILD'
                emoji = '🟡'
                msg = (f"{emoji} **RÚT CHÂN MILD** — Giảm {drop_pct:.1f}% rồi hồi {recovery_pct:.0f}% "
                        f"(close {close_vs_open_pct:+.2f}%)")

        if signal is None:
            return {
                'signal': None,
                'recovery_pct': round(recovery_pct, 1),
                'drop_pct': round(drop_pct, 2),
                'close_vs_open_pct': round(close_vs_open_pct, 2),
                'message': 'Không có rút chân hôm nay',
            }

        # ─── QUALITY SCORE — Phân biệt rút chân THẬT / GIẢ ───
        quality = 50  # base
        warnings = []
        is_at_support = False

        # +10 nếu tại hỗ trợ kỹ thuật (low gần MA20 hoặc MA50)
        try:
            ma20_v = float(last.get('ma20', 0))
            ma50_v = float(last.get('ma50', 0))
            ma10_v = float(last.get('ma10', 0))
            # Coi là "tại hỗ trợ" nếu low ≤ MA20 hoặc MA50 (giảm xuống chạm MA rồi bật lên)
            if ma20_v > 0 and abs(low_p - ma20_v) / ma20_v < 0.02:
                is_at_support = True
                quality += 10
            elif ma50_v > 0 and abs(low_p - ma50_v) / ma50_v < 0.02:
                is_at_support = True
                quality += 10
            elif ma10_v > 0 and abs(low_p - ma10_v) / ma10_v < 0.02:
                is_at_support = True
                quality += 5  # MA10 ít quan trọng hơn
        except Exception:
            pass

        # +10 nếu vol nổ
        if vol_strength >= 1.5:
            quality += 10

        # +10 nếu RSI < 65 (chưa quá mua)
        if rsi < 65:
            quality += 10
        elif rsi >= 70:
            quality -= 10
            warnings.append(f"⚠️ RSI={rsi:.0f} (quá mua) — Rút chân có thể giả")

        # -15 nếu trong downtrend mạnh (close < MA50 + MA20 < MA50)
        try:
            ma20_v = float(last.get('ma20', 0))
            ma50_v = float(last.get('ma50', 0))
            if ma50_v > 0 and close_p < ma50_v and ma20_v < ma50_v:
                quality -= 15
                warnings.append("⚠️ Đang trong downtrend mạnh — Cảnh báo dead cat bounce")
        except Exception:
            pass

        # +5 nếu close TRÊN open (xanh nhẹ thay vì đứng tham chiếu)
        if close_vs_open_pct > 0:
            quality += 5

        quality = max(0, min(100, quality))

        # Verdict quality
        if quality >= 75:
            quality_verdict = '💎 RÚT CHÂN CHẤT LƯỢNG CAO — Khả năng thật cao'
        elif quality >= 55:
            quality_verdict = '🟢 Chất lượng tốt — Đáng theo dõi'
        elif quality >= 35:
            quality_verdict = '🟡 Chất lượng trung bình — Cần xác nhận thêm'
        else:
            quality_verdict = '🔴 Chất lượng thấp — Có thể là bẫy'

        return {
            'signal': signal,
            'message': msg,
            'recovery_pct': round(recovery_pct, 1),
            'drop_pct': round(drop_pct, 2),
            'close_vs_open_pct': round(close_vs_open_pct, 2),
            'vol_strength': round(vol_strength, 2),
            'rsi': round(rsi, 1),
            'quality_score': quality,
            'quality_verdict': quality_verdict,
            'is_at_support': is_at_support,
            'warnings': warnings,
        }
    except Exception as e:
        return {'signal': None, 'message': f'Lỗi: {str(e)[:80]}'}


# [V41 HELPER END]






# [V28 HELPERS END]





# ──────────────────────────────────────────────────────────────────────────────
# [V24-F3] Persist Portfolio + Trades vào file local (không mất khi reload)
# ──────────────────────────────────────────────────────────────────────────────
V24_POSITIONS_FILE = 'v24_positions.json'
V24_TRADES_FILE    = 'v24_trades.json'

def load_positions_from_file() -> list:
    """[F3+X3] Load positions từ file với backward-compat (fill default fields)."""
    try:
        if not os.path.exists(V24_POSITIONS_FILE):
            return []
        with open(V24_POSITIONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # [X3] Backward compat: fill default cho fields mới
        for pos in data:
            pos.setdefault('reason', '')
            pos.setdefault('added_at', '')
        return data
    except Exception as e:
        print(f"[F3 load_positions] {e}")
        return []


def save_positions_to_file(positions: list) -> bool:
    """[F3] Save positions vào file."""
    try:
        with open(V24_POSITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(positions, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[F3 save_positions] {e}")
        return False


def load_trades_from_file() -> list:
    """[F3+X3] Load trades từ file với backward-compat."""
    try:
        if not os.path.exists(V24_TRADES_FILE):
            return []
        with open(V24_TRADES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # [X3] Backward compat
        for t in data:
            t.setdefault('entry_reason', '')
            t.setdefault('exit_reason', '')
            t.setdefault('lesson', '')
            t.setdefault('mood', '')
        return data
    except Exception as e:
        print(f"[F3 load_trades] {e}")
        return []


def save_trades_to_file(trades: list) -> bool:
    """[F3] Save trades vào file."""
    try:
        with open(V24_TRADES_FILE, 'w', encoding='utf-8') as f:
            json.dump(trades, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[F3 save_trades] {e}")
        return False




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
st.title("🛡️ Quant System V24.0: Apex Predator Leviathan")
st.caption("**V24.0:** V23 + Market Pulse | Executive Summary | Exit Signal | Correlation Check")

# [V24-Q1] AUTO-REFRESH trong trading hours
try:
    if is_trading_hours_vn():
        _last_refresh = st.session_state.get('_v24_last_refresh', 0)
        _now_ts = datetime.now(TZ_VN).timestamp()
        if _now_ts - _last_refresh > 300:  # 5 phút
            st.session_state['_v24_last_refresh'] = _now_ts
        # Auto-refresh checkbox
        ar_col1, ar_col2 = st.columns([3, 1])
        with ar_col2:
            auto_refresh = st.checkbox("🔄 Auto-refresh 5p", value=False,
                                          key="auto_refresh_cb",
                                          help="Tự refresh mỗi 5 phút (chỉ trong giờ giao dịch)")
            if auto_refresh:
                import time
                # Streamlit không có native auto-refresh, dùng JS hack
                st.markdown("""
                <script>
                setTimeout(function() {
                    window.location.reload();
                }, 300000);
                </script>
                """, unsafe_allow_html=True)
                st.caption(f"⏰ Last refresh: {datetime.now(TZ_VN).strftime('%H:%M:%S')}")
except Exception as _q1_err:
    print(f"[Q1] {_q1_err}")
st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────────
# [V24 #2] MINI MARKET PULSE — Thay banner Market Regime (tránh lỗi 403)
# ──────────────────────────────────────────────────────────────────────────────
# Cho phép user tắt banner nếu thấy chậm
if 'show_v24_banner' not in st.session_state:
    st.session_state['show_v24_banner'] = True
# Checkbox đã được chuyển vào tab "Pulse" của sidebar tổng hợp bên dưới

# Mặc định regime an toàn để các tab vẫn đọc được
st.session_state.setdefault('market_regime', {
    'regime': 'UNKNOWN', 'buy_allowed': True,
    'min_score_buy': SCORE_BUY_MIN, 'size_mult': 1.0,
    'label': '❓ UNKNOWN — chưa quét', 'pct_ma20': 50, 'adr': 50,
})

if st.session_state['show_v24_banner']:
    # [V24 NEW] MINI PULSE: chỉ quét 8 mã PILLARS (đã có cache từ V23 quét pillars)
    # KHÔNG gọi VNINDEX, KHÔNG gọi basket lớn → tránh 403
    try:
        if 'v24_pulse_computed' not in st.session_state:
            # [F5] Basket cố định 8 mã đại diện đa ngành (không phụ thuộc PILLARS)
            pillars_sample = ['VCB', 'HPG', 'FPT', 'VNM', 'MWG', 'VHM', 'GAS', 'MSN']
            n_above_ma20 = 0
            n_advancing = 0
            n_total = 0
            for _t in pillars_sample:
                try:
                    _df = get_price(_t, days=30)
                    if not valid(_df) or len(_df) < 21:
                        continue
                    _df = calc_indicators(_df)
                    _l = _df.iloc[-1]
                    n_total += 1
                    if _l['close'] > _l['ma20']:
                        n_above_ma20 += 1
                    if _l.get('return_1d', 0) > 0:
                        n_advancing += 1
                except Exception:
                    continue

            if n_total >= 4:
                pct_ma20 = n_above_ma20 / n_total * 100
                pct_adv  = n_advancing / n_total * 100
                # Suy ra regime đơn giản
                if pct_ma20 >= 70 and pct_adv >= 55:
                    pulse_regime = 'STRONG_BULL'
                    pulse_label  = '🟢 STRONG BULL — Mua tích cực'
                    size_mult    = 1.0
                    buy_allowed  = True
                elif pct_ma20 >= 50:
                    pulse_regime = 'CAUTIOUS_BULL'
                    pulse_label  = '🟡 CAUTIOUS BULL — Mua chọn lọc'
                    size_mult    = 0.6
                    buy_allowed  = True
                elif pct_ma20 >= 30:
                    pulse_regime = 'MIXED'
                    pulse_label  = '🟠 MIXED — Chỉ mã siêu mạnh'
                    size_mult    = 0.3
                    buy_allowed  = True
                else:
                    pulse_regime = 'BEAR'
                    pulse_label  = '🔴 BEAR — KHÔNG mở vị thế mới'
                    size_mult    = 0.0
                    buy_allowed  = False

                st.session_state['market_regime'] = {
                    'regime': pulse_regime, 'label': pulse_label,
                    'size_mult': size_mult, 'buy_allowed': buy_allowed,
                    'min_score_buy': SCORE_BUY_MIN + (5 if pulse_regime == 'CAUTIOUS_BULL'
                                                       else 10 if pulse_regime == 'MIXED'
                                                       else 999 if pulse_regime == 'BEAR' else 0),
                    'pct_ma20': pct_ma20, 'adr': pct_adv,
                    'n_sample': n_total,
                }
                st.session_state['v24_pulse_computed'] = True

        rg = st.session_state['market_regime']
        if rg.get('regime') != 'UNKNOWN':
            # Banner gọn 1 dòng
            pulse_c1, pulse_c2, pulse_c3, pulse_c4 = st.columns([3, 1.2, 1.2, 1.2])
            with pulse_c1:
                st.markdown(f"#### {rg['label']}")
                st.caption(f"📊 Mini Pulse từ {rg.get('n_sample', 8)} mã trụ cột — không gọi VNINDEX/basket")
            pulse_c2.metric("% > MA20", f"{rg.get('pct_ma20', 0):.0f}%")
            pulse_c3.metric("% Tăng", f"{rg.get('adr', 0):.0f}%")
            pulse_c4.metric("Size đề xuất", f"{rg.get('size_mult', 1.0)*100:.0f}%")

            if not rg.get('buy_allowed', True):
                st.error("🔴 BEAR — Hệ thống đề nghị KHÔNG mở vị thế mới")
            elif rg.get('regime') == 'MIXED':
                st.warning("🟠 Thị trường phân hoá — chỉ chọn mã RS Rating ≥ 80")

            # [S5] Daily Commentary
            try:
                _sec_flow = st.session_state.get('_mf_cache', [])
                commentary = generate_daily_commentary(rg, {'pct_above_ma20': rg.get('pct_ma20', 50)},
                                                          _sec_flow)
                with st.expander("📝 Bình luận thị trường hôm nay [S5]", expanded=False):
                    st.markdown(commentary)
            except Exception:
                pass
        else:
            st.caption("📊 Mini Market Pulse: chưa quét được (thử reload)")
    except Exception as e:
        st.caption(f"📊 Mini Market Pulse tạm không khả dụng")
        print(f"[V24 mini pulse] {e}")

st.markdown("---")
# [V24 BANNER END]
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
# [F1] Block đã chuyển vào sidebar tổng hợp bên dưới

# [F1] M3 đã chuyển vào sidebar tổng hợp

# [F1] M5 đã chuyển vào sidebar tổng hợp

# [F1] M6 đã chuyển vào sidebar tổng hợp

# [F1] M7 đã chuyển vào sidebar tổng hợp


# ──────────────────────────────────────────────────────────────────────────────
# [V24-F1] UNIFIED V24 SIDEBAR — Gộp tất cả features vào 1 chỗ với tabs
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🛠️ V24 Toolkit")
    sb_tab_pulse, sb_tab_tools, sb_tab_port = st.tabs(["📊 Pulse", "🛠️ Tools", "💼 Portfolio"])

    # ─── TAB 1: PULSE ───
    with sb_tab_pulse:
        st.session_state['show_v24_banner'] = st.checkbox(
            "📊 Banner Mini Market Pulse",
            value=st.session_state.get('show_v24_banner', True),
            help="Tắt nếu thấy chậm",
            key="sb_pulse_cb")
        regime_sb = st.session_state.get('market_regime', {})
        if regime_sb.get('regime') and regime_sb.get('regime') != 'UNKNOWN':
            ms_c1, ms_c2 = st.columns(2)
            ms_c1.metric("% > MA20", f"{regime_sb.get('pct_ma20', 0):.0f}%")
            ms_c2.metric("% Tăng", f"{regime_sb.get('adr', 0):.0f}%")
            rg_code = regime_sb.get('regime', 'UNKNOWN')
            if rg_code == 'BEAR':
                st.error("🔴 BEAR — Đứng ngoài")
            elif rg_code == 'MIXED':
                st.warning("🟠 MIXED — Chỉ RS≥80")
            elif rg_code == 'STRONG_BULL':
                st.success("🟢 BULL — Mua tích cực")
            elif rg_code == 'CAUTIOUS_BULL':
                st.info("🟡 Cautious — Chọn lọc")
        else:
            st.caption("Đang quét...")

        # [V28-A2] MORNING BRIEF — Tổng hợp 1 trang
        with st.expander("🌅 Morning Brief (A2)", expanded=False):
            st.caption("Tổng hợp thông tin sáng — Mở khi vào app")
            if st.button("📰 Tạo Brief", key="a2_btn"):
                with st.spinner("Đang quét..."):
                    _regime = st.session_state.get('market_regime', {})
                    # [V29-F4] Ưu tiên đọc từ watch_rules tickers > watchlist > PILLARS
                    _rules = load_watch_rules()
                    if _rules:
                        _wl_tickers = list(set(r['ticker'] for r in _rules))
                        st.caption(f"💡 Dùng {len(_wl_tickers)} mã từ Watchlist Rules (A1)")
                    else:
                        _wl_tickers = st.session_state.get('watchlist', PILLARS[:10])
                        st.caption(f"💡 Dùng {len(_wl_tickers)} mã từ watchlist mặc định")
                    # [V29-F1] Dùng cached version
                    import json as _json
                    mb = _cached_morning_brief(
                        _json.dumps(list(_wl_tickers)),
                        _json.dumps(_regime if isinstance(_regime, dict) else {}),
                        datetime.now(TZ_VN).strftime('%Y-%m-%d')
                    )
                    st.session_state['_v28_mb'] = mb
            mb = st.session_state.get('_v28_mb')
            if mb:
                # Market regime
                rg = mb.get('regime', {})
                rg_code = rg.get('regime', 'UNKNOWN')
                if rg_code == 'BEAR':
                    st.error("🔴 BEAR — Đứng ngoài")
                elif rg_code == 'STRONG_BULL':
                    st.success("🟢 BULL — Mua tích cực")
                elif rg_code in ('CAUTIOUS_BULL', 'MIXED'):
                    st.warning(f"🟠 {rg_code}")
                else:
                    st.info(f"❓ {rg_code}")

                # Top watchlist
                if mb.get('top_watchlist'):
                    st.markdown("**🏆 Top 3 watchlist:**")
                    for m in mb['top_watchlist']:
                        st.write(f"• **{m['ticker']}** — {m['score']}/80 "
                                  f"(RSI {m['rsi']:.0f}, {m['ret_pct']:+.1f}%)")

                # Biggest movers
                if mb.get('biggest_movers'):
                    st.markdown("**📊 Biến động lớn:**")
                    for m in mb['biggest_movers'][:3]:
                        arrow = '🟢↑' if m['ret_pct'] > 0 else '🔴↓'
                        st.write(f"• **{m['ticker']}** {arrow} {m['ret_pct']:+.2f}%")

                # Unusual vol
                if mb.get('unusual_vol'):
                    st.markdown("**⚡ Vol bất thường:**")
                    for m in mb['unusual_vol'][:3]:
                        st.write(f"• **{m['ticker']}** Vol {m['vol']:.1f}x ({m['ret_pct']:+.1f}%)")

        # [S1] SMART ALERT — Tier changes
        with st.expander("🔔 Smart Alerts (S1)", expanded=False):
            if st.button("🔄 Check changes", key="s1_btn"):
                with st.spinner("So sánh với phiên trước..."):
                    wl_s1 = st.session_state.get('watchlist', PILLARS[:10])
                    changes = detect_tier_changes(list(wl_s1))
                    st.session_state['_s1_changes'] = changes
            changes = st.session_state.get('_s1_changes', [])
            if changes:
                for c in changes:
                    # Đổi từ AVOID/NEUTRAL → BUY/WATCH = tin tốt
                    upgrade = c['from'] in ('AVOID', 'NEUTRAL') and c['to'] in ('BUY', 'WATCH')
                    downgrade = c['from'] in ('BUY', 'WATCH') and c['to'] in ('AVOID', 'OVERHEAT')
                    if upgrade:
                        st.success(f"⬆️ **{c['ticker']}**: {c['from']} → **{c['to']}** "
                                      f"(giá {c['price']:,.0f})")
                    elif downgrade:
                        st.error(f"⬇️ **{c['ticker']}**: {c['from']} → **{c['to']}** "
                                    f"(giá {c['price']:,.0f})")
                    else:
                        st.info(f"🔄 **{c['ticker']}**: {c['from']} → {c['to']}")
            else:
                st.caption("Chưa có thay đổi (hoặc chưa quét bao giờ)")

    # ─── TAB 2: TOOLS ───
    with sb_tab_tools:
        with st.expander("🧮 Position & SL/TP Calculator", expanded=False):
            st.caption("Tính shares + SL/TP cho BẤT KỲ mã nào.")
            slc_capital = st.number_input("Vốn (đồng)", min_value=1_000_000,
                                             value=100_000_000, step=10_000_000,
                                             format="%d", key="slc_capital")
            slc_entry = st.number_input("Giá vào lệnh", min_value=100.0,
                                           value=50000.0, step=100.0, key="slc_entry")
            slc_risk = st.slider("Rủi ro (% vốn)", 0.5, 3.0, 1.0, 0.1, key="slc_risk")
            slc_atr = st.slider("ATR % (volatility)", 1.0, 5.0, 2.5, 0.1, key="slc_atr",
                                  help="ATR 2.5% là trung bình HOSE")
            if st.button("💡 Tính", key="slc_btn"):
                res = calc_position_simple(slc_capital, slc_entry,
                                              risk_pct=slc_risk, atr_pct=slc_atr)
                if 'error' in res:
                    st.error(res['error'])
                else:
                    st.success(f"📦 **{res['shares']:,} cp** ({res['pct_of_capital']:.1f}% vốn)")
                    st.write(f"💰 Tổng: {res['total_cost']:,.0f}đ")
                    st.write(f"🛡️ SL: {res['sl']:,.0f}đ")
                    st.write(f"🎯 TP1: {res['tp1']:,.0f} | TP2: {res['tp2']:,.0f} | TP3: {res['tp3']:,.0f}")
                    st.caption(f"Rủi ro tối đa: {res['dollar_risk']:,.0f}đ")

        # [V24-Qb] BOOKMARK HÀNH ĐỘNG
        with st.expander("🔖 Bookmark hành động", expanded=False):
            st.caption("Lưu các mã cần xem lại sau với nhắc nhở.")
            # Load bookmarks
            if 'v24_bookmarks' not in st.session_state:
                st.session_state['v24_bookmarks'] = load_bookmarks()
            bookmarks = st.session_state['v24_bookmarks']

            # Form thêm
            with st.form(key="bm_form", clear_on_submit=True):
                bm_c1, bm_c2 = st.columns(2)
                bm_ticker = bm_c1.text_input("Mã", max_chars=4, key="bm_ticker").upper()
                bm_hours = bm_c2.number_input("Sau bao lâu (giờ)?",
                                                  min_value=1, max_value=168,
                                                  value=24, step=1, key="bm_hours")
                bm_note = st.text_input("Ghi chú", key="bm_note",
                                          placeholder="VD: Đợi pullback về MA20")
                if st.form_submit_button("🔖 Thêm bookmark"):
                    if bm_ticker:
                        remind_at = datetime.now(TZ_VN) + timedelta(hours=bm_hours)
                        bookmarks.append({
                            'ticker': bm_ticker,
                            'note': bm_note,
                            'created': datetime.now(TZ_VN).strftime('%Y-%m-%d %H:%M'),
                            'remind_at': remind_at.strftime('%Y-%m-%d %H:%M'),
                        })
                        save_bookmarks(bookmarks)
                        st.success(f"Đã đặt nhắc {bm_ticker} sau {bm_hours}h")

            # Hiển thị bookmarks
            if bookmarks:
                # Sort: due trước
                due_bms = [b for b in bookmarks if is_bookmark_due(b)]
                pending_bms = [b for b in bookmarks if not is_bookmark_due(b)]

                if due_bms:
                    st.markdown("**🔔 Đến hạn xem lại:**")
                    for i, b in enumerate(due_bms):
                        bc1, bc2 = st.columns([4, 1])
                        bc1.error(f"**{b['ticker']}** — {b.get('note', '')}")
                        bc1.caption(f"Hẹn lúc: {b['remind_at']}")
                        if bc2.button("✅", key=f"bm_done_{b['ticker']}_{b['created']}"):
                            bookmarks.remove(b)
                            save_bookmarks(bookmarks)
                            st.rerun()

                if pending_bms:
                    with st.expander(f"⏰ Đang chờ ({len(pending_bms)})"):
                        for b in pending_bms:
                            st.caption(f"📌 **{b['ticker']}** — {b.get('note', '')} (hẹn: {b['remind_at']})")
            else:
                st.caption("Chưa có bookmark nào")

        # [V28-A1] WATCHLIST RULES + ALERTS
        with st.expander("🔔 Watchlist Rules & Alerts (A1)", expanded=False):
            st.caption("Set rule để app tự cảnh báo khi điều kiện đạt.")
            if 'v28_rules' not in st.session_state:
                st.session_state['v28_rules'] = load_watch_rules()

            # Form thêm rule
            with st.form(key="a1_form", clear_on_submit=True):
                a1_t = st.text_input("Mã", max_chars=4, key="a1_t").upper()
                a1_cond = st.selectbox("Điều kiện", [
                    ('rsi_below', 'RSI dưới...'),
                    ('rsi_above', 'RSI trên...'),
                    ('price_below', 'Giá dưới...'),
                    ('price_above', 'Giá trên...'),
                    ('vol_above', 'Vol strength trên (x lần)...'),
                    ('break_ma20', 'Vượt MA20'),
                ], format_func=lambda x: x[1], key="a1_cond")
                a1_val = st.number_input("Giá trị (bỏ qua nếu Vượt MA20)",
                                            value=50.0, key="a1_val")
                a1_note = st.text_input("Ghi chú", key="a1_note",
                                          placeholder="VD: Đợi vào lệnh")
                if st.form_submit_button("➕ Thêm rule"):
                    if a1_t:
                        st.session_state['v28_rules'].append({
                            'ticker': a1_t,
                            'condition': a1_cond[0],
                            'value': a1_val,
                            'note': a1_note,
                        })
                        save_watch_rules(st.session_state['v28_rules'])
                        st.success(f"Đã thêm rule cho {a1_t}")

            # Check alerts
            if st.session_state['v28_rules']:
                if st.button("🔍 Check ngay", key="a1_check"):
                    with st.spinner("Đang quét..."):
                        # [V29-F1] Dùng cached version
                        import json as _json
                        alerts = _cached_check_watch_rules(
                            _json.dumps(st.session_state['v28_rules']),
                            datetime.now(TZ_VN).strftime('%Y-%m-%d-%H')
                        )
                        st.session_state['_a1_alerts'] = alerts
                alerts = st.session_state.get('_a1_alerts', [])
                if alerts:
                    st.markdown(f"**🚨 {len(alerts)} alert đang trigger:**")
                    for a in alerts:
                        st.error(f"**{a['ticker']}** — {a['message']}")
                        if a.get('note'):
                            st.caption(f"   📝 {a['note']}")
                else:
                    st.caption("Chưa quét hoặc không có alert nào")

                # List rules
                with st.expander(f"Quản lý {len(st.session_state['v28_rules'])} rules"):
                    for i, r in enumerate(st.session_state['v28_rules']):
                        rc1, rc2 = st.columns([4, 1])
                        rc1.write(f"• **{r['ticker']}**: {r['condition']} {r['value']} ({r.get('note','')})")
                        if rc2.button("❌", key=f"a1_del_{i}"):
                            st.session_state['v28_rules'].pop(i)
                            save_watch_rules(st.session_state['v28_rules'])
                            st.rerun()
            else:
                st.info("Chưa có rule nào")

        with st.expander("🎯 Hôm nay xem mã nào? [S3]", expanded=False):
            st.caption("Gợi ý 3 mã đáng follow nhất hôm nay từ watchlist + pillars.")
            if st.button("🔍 Quét ngay", key="s3_btn"):
                with st.spinner("Đang quét..."):
                    wl = st.session_state.get('watchlist', PILLARS[:5])
                    s3_res = get_daily_recommendations(wl, max_check=20)
                    st.session_state['_s3_result'] = s3_res
            s3_res = st.session_state.get('_s3_result')
            if s3_res and s3_res.get('top3'):
                st.caption(f"Đã quét {s3_res['n_checked']} mã")
                for i, m in enumerate(s3_res['top3'], 1):
                    with st.container(border=True):
                        st.markdown(f"**#{i} {m['ticker']}** — score {m['score']}")
                        st.caption(f"💰 {m['price']:,.0f} | RSI {m['rsi']:.0f} | Vol {m['vol']:.1f}x | {m['ret_pct']:+.1f}%")
                        for r in m['reasons'][:3]:
                            st.write(f"   {r}")
            elif s3_res:
                st.info("Không có mã nào nổi bật hôm nay")

        # [V29-F7] SESSION CLEANUP
        with st.expander("🧹 Dọn Session (F7)", expanded=False):
            st.caption("Xoá cache tạm để app chạy nhanh hơn (không ảnh hưởng data).")
            ss_count = len(st.session_state)
            st.info(f"Session hiện có {ss_count} keys")
            if st.button("🧹 Dọn cache tạm", key="f7_clean"):
                # Chỉ xoá các key tạm (_v, _a, _st...) — KHÔNG xoá v24_*, v28_*
                keep_prefixes = ('v24_', 'v28_', 'watchlist', 'market_regime',
                                   'liq_chk_', 'qa_preview', 'tab1_')
                to_remove = [k for k in list(st.session_state.keys())
                             if not any(k.startswith(p) for p in keep_prefixes)]
                for k in to_remove:
                    del st.session_state[k]
                st.success(f"✅ Đã xoá {len(to_remove)} keys tạm")
                st.rerun()

        # [V29-F6] BACKUP/RESTORE DATA
        with st.expander("💾 Backup/Restore Data (F6)", expanded=False):
            st.caption("Sao lưu/khôi phục data của bạn (positions, trades, rules...).")
            f6_files = ['v24_positions.json', 'v24_trades.json',
                          'v24_tier_history.json', 'v24_bookmarks.json',
                          'v28_watch_rules.json', 'watchlist.json']

            # Backup: gộp 6 file thành 1 JSON
            if st.button("📥 Tạo backup", key="f6_backup"):
                backup_data = {}
                for f in f6_files:
                    try:
                        if os.path.exists(f):
                            with open(f, 'r', encoding='utf-8') as fp:
                                backup_data[f] = json.load(fp)
                    except Exception:
                        pass
                backup_data['_backup_date'] = datetime.now(TZ_VN).strftime('%Y-%m-%d %H:%M')
                backup_json = json.dumps(backup_data, ensure_ascii=False, indent=2)
                st.download_button(
                    "⬇️ Tải file backup.json",
                    backup_json,
                    file_name=f"quant_backup_{datetime.now(TZ_VN).strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json",
                    key="f6_dl"
                )

            # Restore
            f6_uploaded = st.file_uploader("Khôi phục từ file", type=['json'], key="f6_up")
            if f6_uploaded and st.button("📤 Khôi phục", key="f6_restore"):
                try:
                    restore_data = json.loads(f6_uploaded.read().decode('utf-8'))
                    restored = 0
                    for f in f6_files:
                        if f in restore_data:
                            with open(f, 'w', encoding='utf-8') as fp:
                                json.dump(restore_data[f], fp, ensure_ascii=False, indent=2)
                            restored += 1
                    st.success(f"✅ Đã khôi phục {restored}/{len(f6_files)} files")
                    st.caption("Reload trang để thấy data mới.")
                except Exception as e:
                    st.error(f"Lỗi khôi phục: {e}")

        # [V36-N6] WATCHLIST THEO NGÀNH
        with st.expander("📂 Watchlist theo Ngành (N6)", expanded=False):
            st.caption("Gom watchlist thành nhóm theo ngành — dễ theo dõi.")
            if 'v36_wl_groups' not in st.session_state:
                st.session_state['v36_wl_groups'] = load_wl_groups()
            wl_groups = st.session_state['v36_wl_groups']

            # Tạo group mới
            with st.form(key="v36_wl_form", clear_on_submit=True):
                wl_g_name = st.text_input("Tên nhóm (vd: Ngân hàng)",
                                            max_chars=30, key="v36_wl_name")
                wl_g_tickers = st.text_input("Mã (cách nhau dấu phẩy, vd: VCB,ACB,TCB)",
                                                key="v36_wl_tickers").upper()
                if st.form_submit_button("➕ Thêm nhóm"):
                    if wl_g_name and wl_g_tickers:
                        tickers_list_n6 = [t.strip() for t in wl_g_tickers.split(',') if t.strip()]
                        if tickers_list_n6:
                            wl_groups[wl_g_name] = tickers_list_n6
                            save_wl_groups(wl_groups)
                            st.session_state['v36_wl_groups'] = wl_groups
                            st.success(f"Đã thêm {len(tickers_list_n6)} mã vào nhóm '{wl_g_name}'")

            # List groups hiện có
            if wl_groups:
                st.markdown(f"**📋 {len(wl_groups)} nhóm hiện có:**")
                for g_name, g_tickers in wl_groups.items():
                    with st.container(border=True):
                        gc1, gc2 = st.columns([4, 1])
                        gc1.markdown(f"**{g_name}** ({len(g_tickers)} mã)")
                        gc1.caption(", ".join(g_tickers))
                        if gc2.button("❌", key=f"v36_wl_del_{g_name}"):
                            del wl_groups[g_name]
                            save_wl_groups(wl_groups)
                            st.session_state['v36_wl_groups'] = wl_groups
                            st.rerun()
            else:
                st.info("Chưa có nhóm nào — Thêm nhóm đầu tiên ở trên ↑")

        with st.expander("💧 Kiểm tra Thanh Khoản [V24-LIQ]", expanded=False):
            st.caption("Check thanh khoản mã trước khi mua — tránh mã penny rủi ro.")
            liq_chk_ticker = st.text_input("Nhập mã cần check",
                                              max_chars=4,
                                              key="liq_chk_ticker").upper()
            if st.button("🔍 Kiểm tra", key="liq_chk_btn") and liq_chk_ticker:
                try:
                    df_chk = get_price(liq_chk_ticker, days=30)
                    if not valid(df_chk):
                        st.error(f"Không tải được dữ liệu {liq_chk_ticker}")
                    else:
                        liq_chk = calc_liquidity_tier(df_chk)
                        if liq_chk['tier'] == 'HIGH':
                            st.success(liq_chk['message'])
                        elif liq_chk['tier'] == 'MED':
                            st.info(liq_chk['message'])
                        else:
                            st.error(liq_chk['message'])
                        for f in liq_chk['flags']:
                            st.caption(f)
                except Exception as e:
                    st.error(f"Lỗi: {e}")

        with st.expander("☀️ Pre-market Checklist", expanded=False):
            st.caption("Quét nhanh watchlist mỗi sáng.")
            pm_wl_input = st.text_area(
                "Mã cần check",
                value=','.join(st.session_state.get('watchlist', PILLARS[:5])),
                height=80, key="pm_wl")
            if st.button("🔍 Quét nhanh", key="pm_btn"):
                wl_list = [t.strip().upper() for t in pm_wl_input.split(',') if t.strip()]
                with st.spinner("Quét..."):
                    pm_res = generate_premarket_checklist(wl_list, max_check=15)
                    st.session_state['_pm_result'] = pm_res
            pm_res = st.session_state.get('_pm_result')
            if pm_res:
                if pm_res.get('top3'):
                    st.markdown("**🏆 TOP 3 mã tốt nhất:**")
                    for i, m in enumerate(pm_res['top3'], 1):
                        st.write(f"{i}. **{m['ticker']}** — {m['score']}/100 (RSI {m['rsi']:.0f})")
                if pm_res.get('exit_alerts'):
                    st.markdown("**🚨 Cảnh báo CHỐT:**")
                    for e in pm_res['exit_alerts']:
                        st.error(f"• **{e['ticker']}** — {e['reason']}")
                if pm_res.get('unusual_vol'):
                    st.markdown("**⚡ Vol bất thường:**")
                    for u in pm_res['unusual_vol']:
                        arrow = '🟢↑' if u['direction'] == 'UP' else '🔴↓'
                        st.write(f"• **{u['ticker']}** — Vol {u['vol']:.1f}x {arrow} {u['ret_pct']:+.1f}%")

    # ─── TAB 3: PORTFOLIO ───
    with sb_tab_port:
        # [R1] Daily Loss Limit check
        _trades_for_r1 = st.session_state.get('v24_trades', [])
        if not _trades_for_r1:
            _trades_for_r1 = load_trades_from_file()
        dll_limit = st.number_input("Daily Loss Limit (%)", min_value=1.0,
                                       max_value=10.0, value=3.0, step=0.5,
                                       key="r1_limit",
                                       help="Mức lỗ tối đa/ngày — sẽ cảnh báo khi gần đạt")
        dll = check_daily_loss_limit(_trades_for_r1, limit_pct=dll_limit)
        if dll['status'] == 'STOP':
            st.error(dll['label'])
        elif dll['status'] == 'WARNING':
            st.warning(dll['label'])
        elif dll['status'] == 'GAIN':
            st.success(dll['label'])
        else:
            st.info(dll['label'])
        if dll['n_trades'] > 0:
            st.caption(f"Hôm nay: {dll['n_wins']}W / {dll['n_losses']}L")
        st.divider()
        # Load từ file lần đầu
        if 'v24_positions' not in st.session_state:
            st.session_state['v24_positions'] = load_positions_from_file()
        if 'v24_trades' not in st.session_state:
            st.session_state['v24_trades'] = load_trades_from_file()

        # Sub-tabs: Vị thế / Trades
        pt1, pt2 = st.tabs(["💼 Vị thế", "📈 Trades"])

        with pt1:
            # ── [V38-G4] RESET NHANH VỊ THẾ NHẦM ──
            with st.expander("🗑️ Xoá vị thế nhầm (G4)", expanded=False):
                st.caption(
                    "Nếu bạn đã thêm nhầm vị thế (vd: chỉ xem mã, không thực sự mua) "
                    "→ xoá nhanh ở đây để app không tính lỗ/lời ảo."
                )
                _g4_positions = st.session_state.get('v24_positions', [])
                if not _g4_positions:
                    st.info("✅ Chưa có vị thế nào trong Portfolio")
                else:
                    for _i, _p in enumerate(_g4_positions):
                        _gc1, _gc2 = st.columns([4, 1])
                        _gc1.write(
                            f"• **{_p['ticker']}** — {_p.get('shares', 0):,} cp "
                            f"@ {_p.get('entry', 0):,.0f}đ "
                            f"(thêm: {_p.get('added_at', 'N/A')})"
                        )
                        if _gc2.button("🗑️ Xoá", key=f"v38_g4_del_{_i}_{_p['ticker']}"):
                            _g4_positions.pop(_i)
                            st.session_state['v24_positions'] = _g4_positions
                            save_positions_to_file(_g4_positions)
                            st.success(f"Đã xoá vị thế {_p['ticker']}")
                            st.rerun()
                    # Nút xoá hết (cẩn thận)
                    if st.button("🔥 Xoá TẤT CẢ vị thế (cẩn thận!)", key="v38_g4_clear_all"):
                        if st.session_state.get('_v38_g4_confirm'):
                            st.session_state['v24_positions'] = []
                            save_positions_to_file([])
                            st.session_state['_v38_g4_confirm'] = False
                            st.success("Đã xoá toàn bộ Portfolio")
                            st.rerun()
                        else:
                            st.session_state['_v38_g4_confirm'] = True
                            st.warning("⚠️ Bấm lần nữa để xác nhận xoá HẾT")

            with st.form(key="pf_add_form", clear_on_submit=True):
                pf_c1, pf_c2 = st.columns(2)
                pf_ticker = pf_c1.text_input("Mã", max_chars=4, key="pf_ticker").upper()
                pf_shares = pf_c2.number_input("Số cp", min_value=100, step=100,
                                                  value=1000, key="pf_shares")
                pf_entry = st.number_input("Giá vào", min_value=100.0, step=100.0,
                                              value=50000.0, key="pf_entry")
                # [V24-X2] Thống nhất schema — thêm reason
                pf_reason = st.text_input("Lý do mua (tuỳ chọn)",
                                            key="pf_reason",
                                            placeholder="VD: Chân sóng + MACD bullish")
                if st.form_submit_button("➕ Thêm vị thế"):
                    if pf_ticker:
                        st.session_state['v24_positions'].append({
                            'ticker': pf_ticker, 'shares': pf_shares, 'entry': pf_entry,
                            'reason': pf_reason,
                            'added_at': datetime.now(TZ_VN).strftime('%Y-%m-%d %H:%M'),
                        })
                        save_positions_to_file(st.session_state['v24_positions'])
                        st.success(f"Đã thêm {pf_ticker}")

            positions = st.session_state.get('v24_positions', [])
            if positions:
                total_value = total_cost = 0
                liq_warnings = []  # [V24-F5] Collect LIQ warnings
                time_warnings = []  # [V24-E1] Time-based exit warnings
                for i, pos in enumerate(positions):
                    try:
                        df_p = get_price(pos['ticker'], days=30)
                        if valid(df_p):
                            cur_price = float(df_p['close'].iloc[-1])
                            pnl = (cur_price - pos['entry']) * pos['shares']
                            pnl_pct = (cur_price - pos['entry']) / pos['entry'] * 100
                            total_value += pos['shares'] * cur_price
                            total_cost += pos['shares'] * pos['entry']
                            emoji = '🟢' if pnl >= 0 else '🔴'
                            # [V24-F5] Check LIQ degradation
                            try:
                                _liq_pos = calc_liquidity_tier(df_p)
                                if _liq_pos.get('tier') == 'LOW':
                                    emoji = '⚠️'
                                    liq_warnings.append(f"**{pos['ticker']}** LIQ giảm xuống LOW")
                            except Exception:
                                pass
                            # [V24-E1] Time-based exit cảnh báo
                            try:
                                added_str = pos.get('added_at', '')
                                tier_at_buy = pos.get('tier_at_buy', '')
                                if added_str:
                                    added_dt = datetime.strptime(added_str, '%Y-%m-%d %H:%M').replace(tzinfo=TZ_VN)
                                    days_held = (datetime.now(TZ_VN) - added_dt).days
                                    # Tầng 3 (Tích Lũy): > 21 ngày mà chưa lời 5%
                                    if 'Tích Lũy' in tier_at_buy and days_held > 21 and pnl_pct < 5:
                                        emoji = '⏰'
                                        time_warnings.append(
                                            f"**{pos['ticker']}** giữ {days_held} ngày (Tầng 3) chưa break"
                                        )
                                    # Tầng 2 (Sẵn Sàng): > 14 ngày mà chưa lời 3%
                                    elif 'Sẵn Sàng' in tier_at_buy and days_held > 14 and pnl_pct < 3:
                                        emoji = '⏰'
                                        time_warnings.append(
                                            f"**{pos['ticker']}** giữ {days_held} ngày (Tầng 2) chưa xác nhận"
                                        )
                            except Exception:
                                pass
                            pc1, pc2 = st.columns([3, 1])
                            pc1.markdown(f"{emoji} **{pos['ticker']}** ({pos['shares']:,}) "
                                          f"@{pos['entry']:,.0f}→{cur_price:,.0f} ({pnl_pct:+.1f}%)")
                            if pc2.button("❌", key=f"pf_close_{i}"):
                                st.session_state['v24_positions'].pop(i)
                                save_positions_to_file(st.session_state['v24_positions'])
                                st.rerun()
                    except Exception:
                        pass
                # [V24-F5] Hiện cảnh báo LIQ degradation
                if liq_warnings:
                    st.warning("⚠️ **Cảnh báo LIQ:** " + "; ".join(liq_warnings)
                                + " → Cân nhắc thoát sớm để tránh kẹp hàng")
                # [V24-E1] Hiện cảnh báo time-based
                if time_warnings:
                    st.warning("⏰ **Cảnh báo thời gian giữ:** " + "; ".join(time_warnings))
                    st.caption("Quy tắc: Tầng 2 > 14 ngày chưa break, Tầng 3 > 21 ngày chưa break → đã đợi đủ lâu")
                if total_cost > 0:
                    total_pnl = total_value - total_cost
                    total_pnl_pct = total_pnl / total_cost * 100
                    emoji = '🟢' if total_pnl >= 0 else '🔴'
                    st.metric(f"{emoji} Tổng P&L", f"{total_pnl:+,.0f} đ",
                                delta=f"{total_pnl_pct:+.2f}%")

                    # [V28-R4] STRESS TEST PORTFOLIO
                    with st.expander("🔥 Stress Test (R4)", expanded=False):
                        st.caption("Mô phỏng danh mục nếu VN-Index giảm.")
                        st_drop = st.slider("VN-Index giảm bao nhiêu (%)",
                                             min_value=-15.0, max_value=-1.0,
                                             value=-5.0, step=0.5, key="st_drop")
                        if st.button("Chạy stress test", key="st_run"):
                            with st.spinner("Đang tính..."):
                                # [V29-F1] Dùng cached version
                                import json as _json
                                st_res = _cached_stress_test(
                                    _json.dumps(positions),
                                    float(st_drop),
                                    datetime.now(TZ_VN).strftime('%Y-%m-%d')
                                )
                                st.session_state['_v28_st'] = st_res
                        st_res = st.session_state.get('_v28_st')
                        if st_res:
                            if 'message' in st_res:
                                st.info(st_res['message'])
                            else:
                                st.markdown(f"**Nếu VN-Index giảm {st_res['vni_drop_pct']:.1f}%:**")
                                st_c1, st_c2 = st.columns(2)
                                st_c1.metric("Tổng giá trị DM",
                                              f"{st_res['total_value']/1e6:.1f}M")
                                st_c2.metric("Dự kiến lỗ",
                                              f"{st_res['total_expected_loss']/1e6:.1f}M",
                                              delta=f"{st_res['overall_pct']:.2f}%",
                                              delta_color="inverse")
                                st.markdown("**Chi tiết:**")
                                for d in st_res.get('detail', []):
                                    st.write(f"• **{d['ticker']}** (β={d['beta']}) → "
                                              f"lỗ {d['expected_loss_amount']/1e6:.2f}M "
                                              f"({d['expected_loss_pct']:.1f}%)")

                    # [S2] Position Risk Heatmap
                    with st.expander("🌡️ Risk Heatmap", expanded=False):
                        for pos in positions:
                            try:
                                df_r = get_price(pos['ticker'], days=60)
                                if valid(df_r):
                                    df_r = calc_indicators(df_r)
                                    risk = calc_position_risk_score(pos, df_r)
                                    if risk['score'] >= 8:
                                        st.error(f"{risk['label']} **{pos['ticker']}** — score {risk['score']}/10")
                                    elif risk['score'] >= 6:
                                        st.warning(f"{risk['label']} **{pos['ticker']}** — score {risk['score']}/10")
                                    elif risk['score'] >= 4:
                                        st.info(f"{risk['label']} **{pos['ticker']}** — score {risk['score']}/10")
                                    else:
                                        st.success(f"{risk['label']} **{pos['ticker']}** — score {risk['score']}/10")
                                    for f in risk['flags'][:3]:
                                        st.caption(f"   {f}")
                            except Exception:
                                pass
            else:
                st.info("Chưa có vị thế")

        with pt2:
            with st.form(key="tt_form", clear_on_submit=True):
                tt_c1, tt_c2 = st.columns(2)
                tt_ticker = tt_c1.text_input("Mã", max_chars=4, key="tt_ticker").upper()
                tt_pnl_pct = tt_c2.number_input("% P&L", value=0.0, step=0.5,
                                                    format="%.2f", key="tt_pnl")
                # [R3] Notes & lessons
                tt_entry_reason = st.text_input("Lý do MUA (tuỳ chọn)", key="tt_entry_r",
                                                   placeholder="VD: MACD bullish + chân sóng 7/12")
                tt_exit_reason = st.text_input("Lý do BÁN (tuỳ chọn)", key="tt_exit_r",
                                                  placeholder="VD: RSI 78 quá mua + chốt lời")
                tt_lesson = st.text_area("Bài học rút ra (tuỳ chọn)", height=60,
                                            key="tt_lesson",
                                            placeholder="VD: Lần sau không mua khi VN-Index dưới MA50")
                # [V24-H2] MOOD TRACKER
                tt_mood = st.select_slider(
                    "😊 Cảm xúc khi trade?",
                    options=['😡 Tức giận', '😟 Lo lắng', '😐 Bình thường', '🙂 Tự tin', '😎 Hưng phấn'],
                    value='😐 Bình thường', key="tt_mood",
                    help="Track mood để phân tích sau: bạn thắng/thua khi cảm xúc thế nào?")
                if st.form_submit_button("➕ Ghi trade"):
                    if tt_ticker:
                        st.session_state['v24_trades'].append({
                            'ticker': tt_ticker,
                            'pnl_pct': tt_pnl_pct,
                            'date': datetime.now(TZ_VN).strftime('%Y-%m-%d %H:%M'),
                            'entry_reason': tt_entry_reason,
                            'exit_reason': tt_exit_reason,
                            'lesson': tt_lesson,
                            'mood': tt_mood,
                        })
                        save_trades_to_file(st.session_state['v24_trades'])
                        st.success(f"Đã ghi {tt_ticker} {tt_pnl_pct:+.2f}%")

            trades = st.session_state.get('v24_trades', [])
            if trades:
                pnls = [t['pnl_pct'] for t in trades]
                equity_real = np.cumprod([1 + p/100 for p in pnls]) * 100
                wins = sum(1 for p in pnls if p > 0)
                wr_real = wins / len(pnls) * 100 if pnls else 0
                final_eq = equity_real[-1] if len(equity_real) > 0 else 100
                tt_m1, tt_m2 = st.columns(2)
                tt_m1.metric("WR thực", f"{wr_real:.0f}%")
                tt_m2.metric("Equity", f"{final_eq:.1f}%",
                              delta=f"{final_eq-100:+.1f}%",
                              delta_color="normal" if final_eq >= 100 else "inverse")
                try:
                    fig_tt = go.Figure()
                    fig_tt.add_trace(go.Scatter(
                        x=list(range(1, len(equity_real)+1)),
                        y=equity_real, mode='lines+markers',
                        line=dict(color='green' if final_eq >= 100 else 'red', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(0,200,100,0.15)' if final_eq >= 100 else 'rgba(220,50,50,0.15)',
                    ))
                    fig_tt.add_hline(y=100, line_dash='dot', line_color='gray')
                    fig_tt.update_layout(height=160, margin=dict(l=10, r=10, t=10, b=10),
                                           showlegend=False)
                    st.plotly_chart(fig_tt, use_container_width=True)
                except Exception:
                    pass
                with st.expander("5 trade gần"):
                    for t in trades[-5:][::-1]:
                        emoji = '🟢' if t['pnl_pct'] >= 0 else '🔴'
                        mood = t.get('mood', '')
                        mood_disp = f" | {mood}" if mood else ''
                        st.write(f"{emoji} {t['ticker']} {t['pnl_pct']:+.2f}% ({t['date']}){mood_disp}")
                        if t.get('entry_reason'):
                            st.caption(f"   📥 Mua: {t['entry_reason']}")
                        if t.get('exit_reason'):
                            st.caption(f"   📤 Bán: {t['exit_reason']}")
                        if t.get('lesson'):
                            st.caption(f"   💡 Lesson: {t['lesson']}")
                # [V28-L1+L2] [V29-F2] Lifetime Stats + Pattern Analyzer
                # Dùng container thay expander để tránh nested expander warnings
                st.markdown("---")
                st.markdown("### 📊 Lifetime Stats (L1)")
                with st.container(border=True):
                    ls = calc_lifetime_stats(trades)
                    if 'message' in ls:
                        st.info(ls['message'])
                    else:
                        ls_c1, ls_c2, ls_c3 = st.columns(3)
                        ls_c1.metric("Tổng trade", ls['n_total'])
                        ls_c2.metric("Winrate", f"{ls['winrate']}%")
                        ls_c3.metric("Equity", f"{ls['equity_final']}%",
                                       delta=f"{ls['equity_final']-100:+.1f}%")
                        ls_c4, ls_c5, ls_c6 = st.columns(3)
                        ls_c4.metric("TB lời", f"+{ls['avg_win']}%")
                        ls_c5.metric("TB lỗ", f"{ls['avg_loss']}%")
                        ls_c6.metric("Expectancy",
                                       f"{ls['expectancy']:+.2f}%",
                                       delta="Dương ✓" if ls['expectancy']>0 else "Âm ⚠️",
                                       delta_color="normal" if ls['expectancy']>0 else "inverse")
                        ls_c7, ls_c8, ls_c9 = st.columns(3)
                        ls_c7.metric("Profit Factor", f"{ls['profit_factor']}",
                                       help="≥1.5 là tốt")
                        ls_c8.metric("R-multiple TB", f"{ls['avg_r']}",
                                       help="≥2.0 là tốt — lời gấp 2 lần lỗ")
                        ls_c9.metric("Lệnh lớn nhất",
                                       f"+{ls['biggest_win']}%",
                                       help=f"Lệnh thua tệ nhất: {ls['biggest_loss']}%")
                        # Streak hiện tại
                        if ls['last_streak'] >= 3:
                            if ls['last_streak_type'] == 'W':
                                st.success(f"🔥 Đang có chuỗi {ls['last_streak']} lệnh THẮNG liên tiếp — Cẩn thận tăng size")
                            elif ls['last_streak_type'] == 'L':
                                st.error(f"❄️ Đang có chuỗi {ls['last_streak']} lệnh THUA liên tiếp — Nghỉ 1-2 ngày, xem lại bài học")

                st.markdown("### 🧠 Pattern Trade Analyzer (L2)")
                with st.container(border=True):
                    pa = analyze_trade_patterns(trades)
                    if 'message' in pa:
                        st.info(pa['message'])
                    else:
                        st.caption(f"Đã phân tích {pa['n_analyzed']} trades")
                        if pa.get('insights'):
                            for ins in pa['insights']:
                                st.markdown(f"• {ins}")
                        else:
                            st.info("Chưa có pattern rõ ràng — cần thêm trades")

                if st.button("🗑️ Xoá tất cả", key="tt_clear"):
                    st.session_state['v24_trades'] = []
                    save_trades_to_file([])
                    st.rerun()
            else:
                st.info("Chưa có trade")

# [V24-F1] END UNIFIED SIDEBAR
st.sidebar.header("🕹️ Trung Tâm Giao Dịch Định Lượng")
if st.sidebar.button("🔄 Làm mới danh sách mã (Xóa Cache)"):
    st.cache_data.clear()
    st.rerun()
dropdown = st.sidebar.selectbox("Lựa chọn mã cổ phiếu:", tickers)
st.sidebar.caption(f"📊 Tổng số mã đang theo dõi: {len(tickers)}")
manual   = st.sidebar.text_input("Hoặc nhập trực tiếp (VD: FPT):").strip().upper()
ticker   = manual if manual else dropdown

# [V24-Qa] QUICK PREVIEW — Hiển thị tóm tắt nhanh không cần "Tiến hành phân tích"
try:
    date_key_qa = datetime.now(TZ_VN).strftime('%Y-%m-%d')
    qa_preview = quick_preview_ticker(ticker, date_key_qa)
    if 'error' not in qa_preview:
        with st.sidebar.container(border=True):
            st.markdown(f"#### ⚡ Preview nhanh: **{ticker}**")
            qpv_c1, qpv_c2 = st.columns(2)
            qpv_c1.metric("Giá",
                            f"{qa_preview['price']:,.0f}",
                            delta=f"{qa_preview['ret_pct']:+.2f}%")
            qpv_c2.metric("RSI", f"{qa_preview['rsi']:.0f}")
            st.markdown(f"**{qa_preview['tier']}** | Vol {qa_preview['vol']:.1f}x")
            sig_emoji = '✅' if qa_preview['macd_up'] else '❌'
            ma_emoji = '✅' if qa_preview['above_ma20'] else '❌'
            st.caption(f"MACD {sig_emoji} | MA20 {ma_emoji}")
            # [V24-LIQ] Liquidity badge
            liq_t = qa_preview.get('liq_tier', 'UNKNOWN')
            liq_v = qa_preview.get('liq_vol_avg', 0) / 1000  # K
            liq_tv = qa_preview.get('liq_turnover', 0)
            if liq_t == 'LOW':
                st.error(f"🔴 LIQ THẤP | Vol {liq_v:.0f}K | TO {liq_tv:.1f} tỷ — TRÁNH")
            elif liq_t == 'HIGH':
                st.success(f"🟢 LIQ CAO | Vol {liq_v:.0f}K | TO {liq_tv:.1f} tỷ")
            elif liq_t == 'MED':
                st.info(f"🟡 LIQ OK | Vol {liq_v:.0f}K | TO {liq_tv:.1f} tỷ")
    else:
        st.sidebar.caption(f"⚠️ Preview: {qa_preview['error']}")
except Exception as _qa_err:
    print(f"[Qa] {_qa_err}")

st.sidebar.markdown("---")
news_headlines = []   # Đã bỏ input tin tức
# --- TABS ---
tab_morning, tab1, tab2, tab3, tab4, tab_momentum, tab5, tab6, tab7, tab_compare = st.tabs([
    "🌞 SÁNG NAY",
    "🤖 ROBOT ADVISOR & BẢN PHÂN TÍCH",
    "🏢 BÁO CÁO TÀI CHÍNH & CANSLIM",
    "🌊 BÓC TÁCH DÒNG TIỀN",
    "🔍 RADAR TRUY QUÉT SIÊU CỔ PHIẾU",
    "🔥 EARLY MOMENTUM",
    "🏭 SECTOR ROTATION — DÒNG TIỀN NGÀNH",
    "📊 VN-INDEX & TƯƠNG QUAN",
    "🌡️ HEATMAP & ĐỐI THỦ NGÀNH",
    "🆚 SO SÁNH 2 MÃ [V24]",
])
# ==============================================================================
# [V36-N3] TAB MORNING — Daily Routine Wizard
# ==============================================================================
with tab_morning:
    st.subheader("🌞 Sáng Nay — Daily Routine Wizard")
    st.info(
        "📌 Quy trình từng bước mỗi sáng trước khi giao dịch. "
        "Làm theo thứ tự để không bỏ sót dấu hiệu quan trọng."
    )

    # BƯỚC 1: Trạng thái thị trường
    with st.container(border=True):
        st.markdown("### 1️⃣ Trạng thái Thị trường")
        st.caption("→ Quyết: Có nên mua hôm nay không? Mua mạnh hay thận trọng?")
        m1c1, m1c2 = st.columns(2)
        with m1c1:
            st.markdown("**🚦 Verdict VN-Index**")
            st.caption("Vào **Tab 📊 VN-INDEX** → nhấn '🔄 Tải Dữ Liệu' → Xem Verdict Box")
            st.markdown("- 🟢 NÊN MUA → Vào lệnh full size")
            st.markdown("- 🟡 THẬN TRỌNG → Size 50%, SL chặt")
            st.markdown("- 🔴 ĐỨNG NGOÀI → Không mua")
        with m1c2:
            st.markdown("**😰 Fear & Greed**")
            st.caption("Cùng Tab 📊 VN-INDEX")
            st.markdown("- 🤑 Extreme Greed (≥75) → Chốt lời")
            st.markdown("- 😨 Extreme Fear (≤25) → Cơ hội đáy")
            st.markdown("- 😐 Neutral → Giao dịch bình thường")

    # BƯỚC 2: Quản lý vị thế
    with st.container(border=True):
        st.markdown("### 2️⃣ Check vị thế đang mở")
        st.caption("→ Có mã nào chạm SL/TP? Có cảnh báo gì?")
        positions_m = st.session_state.get('v24_positions', [])
        if not positions_m:
            st.info("✅ Chưa có vị thế nào đang mở")
        else:
            st.write(f"💼 Đang giữ **{len(positions_m)}** vị thế")
            for pm in positions_m:
                try:
                    df_pm = get_price(pm['ticker'], days=5)
                    if valid(df_pm):
                        cur = float(df_pm['close'].iloc[-1])
                        pnl_pct = (cur - pm['entry']) / pm['entry'] * 100
                        emoji = '🟢' if pnl_pct >= 0 else '🔴'
                        st.write(f"{emoji} **{pm['ticker']}** @ {pm['entry']:,.0f} → {cur:,.0f} ({pnl_pct:+.2f}%)")
                        # Warning logic
                        if pnl_pct <= -7:
                            st.error(f"   🚨 {pm['ticker']} lỗ {pnl_pct:.1f}% — CHẠM SL, CÂN NHẮC THOÁT")
                        elif pnl_pct >= 15:
                            st.success(f"   💎 {pm['ticker']} lời {pnl_pct:.1f}% — CÂN NHẮC CHỐT 50%")
                except Exception:
                    continue
        st.markdown("**Vào sidebar 💼 Portfolio để xem chi tiết hơn**")

    # BƯỚC 3: Quét cơ hội mới
    with st.container(border=True):
        st.markdown("### 3️⃣ Quét cơ hội mới")
        st.caption("→ Tìm mã đáng phân tích sâu hôm nay")
        st.markdown("- **Tab 🔍 RADAR** → Quét toàn HOSE, xem Tầng 1/2/3")
        st.markdown("- **Tab 🏭 SECTOR** → Xem ngành nào đang leading")
        st.markdown("- **Tab 📊 VN-INDEX** → Xem Market Breadth")
        # Quick Pick nếu có
        morning_alerts = st.session_state.get('_a1_alerts', [])
        if morning_alerts:
            st.warning(f"🔔 Bạn có {len(morning_alerts)} alert Watchlist Rules đang trigger — Check sidebar 🛠️ Tools")

    # BƯỚC 4: Pre-trade Checklist
    with st.container(border=True):
        st.markdown("### 4️⃣ Trước khi vào lệnh")
        st.caption("→ Bắt buộc làm để tránh impulse trading")
        st.markdown("**Chọn mã muốn mua → Nhập vào sidebar → Tab 🤖 Robot Advisor**")
        st.markdown("Mỗi mã sẽ có:")
        st.markdown("- ✅ Pre-trade Checklist 5 ô bắt buộc tick")
        st.markdown("- 📊 Position Sizing tự động")
        st.markdown("- 🚨 FOMO Detector cảnh báo nếu mua đuổi")
        st.markdown("- 🔴 LIQ_LOW filter loại mã penny")

    # BƯỚC 5: Sau khi vào lệnh
    with st.container(border=True):
        st.markdown("### 5️⃣ Sau khi mua")
        st.caption("→ Để hệ thống theo dõi giúp bạn")
        st.markdown("- **Thêm vị thế** qua Quick Add (nút ➕ ở Tab Robot Advisor)")
        st.markdown("- **Đặt SL cứng tại broker** ngay sau khi mua")
        st.markdown("- **Ghi vào Trade Journal** lý do mua + mood (sidebar 💼 Portfolio → tab Trades)")

    st.markdown("---")
    st.caption("💡 **Tip:** Làm đủ 5 bước mỗi sáng → giảm 80% lệnh thua do bốc đồng")

# ==============================================================================
# TAB 1: ROBOT ADVISOR
# ==============================================================================
with tab1:
    # ── [V38-G5] HEADER TRẠNG THÁI MÃ ──
    # Phân biệt rõ: chỉ phân tích / đang theo dõi / đang giữ vị thế
    try:
        _v38_positions = st.session_state.get('v24_positions', []) or load_positions_from_file()
        _v38_watchlist = st.session_state.get('watchlist', []) or []
        _v38_my_pos = [p for p in _v38_positions if p.get('ticker') == ticker]
        _v38_in_wl = ticker in _v38_watchlist

        with st.container(border=True):
            if _v38_my_pos:
                # ĐANG GIỮ VỊ THẾ
                _pos = _v38_my_pos[0]
                try:
                    _df_cur = get_price(ticker, days=3)
                    _cur_price = float(_df_cur['close'].iloc[-1]) if valid(_df_cur) else _pos['entry']
                except Exception:
                    _cur_price = _pos['entry']
                _pnl_pct = (_cur_price - _pos['entry']) / _pos['entry'] * 100
                _pnl_amt = (_cur_price - _pos['entry']) * _pos['shares']

                gc1, gc2, gc3 = st.columns([1.5, 2, 2])
                with gc1:
                    st.error(f"### 💰 ĐANG GIỮ VỊ THẾ")
                    st.caption(f"Mã: **{ticker}**")
                with gc2:
                    st.metric(f"Mua @ {_pos['entry']:,.0f}",
                                f"Hiện: {_cur_price:,.0f}",
                                delta=f"{_pnl_pct:+.2f}%",
                                delta_color="normal" if _pnl_pct >= 0 else "inverse")
                    st.caption(f"📦 {_pos['shares']:,} cp | Vào lệnh: {_pos.get('added_at', 'N/A')}")
                with gc3:
                    st.metric("Lãi/Lỗ (đồng)",
                                f"{_pnl_amt:+,.0f}",
                                delta_color="normal" if _pnl_amt >= 0 else "inverse")
                    if _pos.get('reason'):
                        st.caption(f"📝 Lý do mua: {_pos['reason'][:60]}")
            elif _v38_in_wl:
                # ĐANG THEO DÕI (Watchlist)
                gc1, gc2 = st.columns([1, 3])
                gc1.info(f"### 📌 ĐANG THEO DÕI")
                gc2.markdown(f"**{ticker}** đang trong Watchlist của bạn — chỉ theo dõi, "
                              "chưa có vị thế. Không tính lỗ/lời.")
            else:
                # CHỈ ĐANG PHÂN TÍCH
                gc1, gc2 = st.columns([1, 3])
                gc1.success(f"### 🔍 CHỈ ĐANG PHÂN TÍCH")
                gc2.markdown(f"**{ticker}** chưa có trong Watchlist hoặc Portfolio. "
                              "Bạn chỉ đang xem xét. KHÔNG có lỗ/lời ảo.")
    except Exception as _v38_g5_err:
        st.caption(f"(Header trạng thái lỗi: {_v38_g5_err})")

    # [#7] Hiển thị kết quả cũ nếu đã phân tích (giữ khi switch tab)
    if st.session_state.get('tab1_ticker') == ticker and st.session_state.get('tab1_done'):
        st.info(f"💾 Đang hiển thị kết quả phân tích đã lưu cho **{ticker}**. Bấm nút bên dưới để phân tích lại.")
    col_btn, col_clear = st.columns([3, 1])
    with col_btn:
        run_analysis = st.button(f"⚡ TIẾN HÀNH PHÂN TÍCH ĐỊNH LƯỢNG TOÀN DIỆN MÃ {ticker}")
    # [F2] Theo dõi ticker hiện tại để clear cached equity khi đổi mã
    if run_analysis and st.session_state.get('_v24_last_analyzed_ticker') != ticker:
        st.session_state.pop('_v24_equity_final', None)
        st.session_state.pop('_v24_confidence', None)
        st.session_state.pop('_v24_streak', None)
        st.session_state['_v24_last_analyzed_ticker'] = ticker
    with col_clear:
        if st.button("🗑️ Xóa kết quả cũ", key="auto_btn_X_a_k_t_qu__c_1"):
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

            # [V24 #2] Market Timing Filter — áp downgrade SAU scoring (không sửa V23)
            try:
                _v24_regime = st.session_state.get('market_regime', None)
                if _v24_regime is not None:
                    _rg = _v24_regime.get('regime', 'UNKNOWN')
                    _orig_decision = scoring['decision']
                    _orig_color = scoring.get('decision_color', 'green')
                    # Downgrade theo regime
                    if _rg == 'BEAR':
                        scoring['decision'] = "🔴 BEAR MARKET — ĐỨNG NGOÀI [V24 downgrade]"
                        scoring['decision_color'] = "red"
                        scoring['_v24_downgraded'] = True
                        scoring['_orig_decision'] = _orig_decision
                    elif _rg == 'MIXED' and ('MUA' in _orig_decision or 'STRONG BUY' in _orig_decision):
                        scoring['decision'] = "⚖️ THEO DÕI (V24: hạ 1 bậc do MIXED)"
                        scoring['decision_color'] = "orange"
                        scoring['_v24_downgraded'] = True
                        scoring['_orig_decision'] = _orig_decision
                    elif _rg == 'CAUTIOUS_BULL' and 'STRONG BUY' in _orig_decision:
                        scoring['decision'] = "🟡 MUA THẬN TRỌNG (V24: CAUTIOUS market)"
                        scoring['decision_color'] = "orange"
                        scoring['_v24_downgraded'] = True
                        scoring['_orig_decision'] = _orig_decision
            except Exception as _mtf_err:
                print(f"[V24 market timing filter] {_mtf_err}")
            # [NÂNG CẤP #12] Kelly
            kelly_pct = calc_kelly(bt['winrate'], bt['avg_profit'], abs(bt['avg_loss']))
            # [NÂNG CẤP #10] ATR Trailing Stop
            atr_val  = float(last.get('atr', last['close'] * 0.02))
            sl_info  = calc_trailing_stop(float(last['close']), atr_val)

            # ═══════════════════════════════════════════════════════════════
            # [V24-X1] SECTION A: TÓM TẮT NHANH (đặt ĐẦU để user thấy ngay)
            # ═══════════════════════════════════════════════════════════════

            # [V24-LIQ+F4] Banner cảnh báo PRIORITY (LIQ là cảnh báo cấp 1, ưu tiên hiển thị riêng)
            try:
                _liq_check = calc_liquidity_tier(df)
                st.session_state['_v24_liq'] = _liq_check
                # LIQ_LOW là cảnh báo nghiêm trọng → hiển thị riêng, gắn cờ để bỏ qua FOMO/Exit detail dài
                if _liq_check.get('tier') == 'LOW':
                    render_liquidity_warning(_liq_check, ticker)
                    st.session_state['_v24_critical_warning'] = True
                else:
                    st.session_state['_v24_critical_warning'] = False
            except Exception as _liq_err:
                print(f"[V24-LIQ] {_liq_err}")


            # ── [V24 #1] EXECUTIVE SUMMARY 1 CÂU (đặt ĐẦU kết quả) ──
            try:
                regime_for_summary = st.session_state.get('market_regime', {
                    'regime': 'UNKNOWN', 'size_mult': 1.0, 'buy_allowed': True})
                exec_summary = generate_executive_summary(
                    ticker, scoring, last, ai_score, wave_info,
                    weekly_trend, kelly_pct, sl_info, regime_for_summary)

                # [V24-T3] Downgrade thêm nếu backtest equity tệ
                _eq_final = st.session_state.get('_v24_equity_final', None)
                if _eq_final is not None and _eq_final < 90 and 'MUA' in exec_summary.get('action', ''):
                    exec_summary['one_liner'] += f" ⚠️ Backtest lỗ {100-_eq_final:.0f}% — cân nhắc kỹ"
                    exec_summary['badge_color'] = 'orange'

                # [V24-LIQ] Downgrade nếu thanh khoản thấp
                _liq_es = st.session_state.get('_v24_liq', {'tier': 'UNKNOWN'})
                if _liq_es.get('tier') == 'LOW' and 'MUA' in exec_summary.get('action', ''):
                    exec_summary['action'] = 'TRÁNH (LIQ THẤP)'
                    exec_summary['one_liner'] += " 🔴 Thanh khoản thấp — KHÔNG khuyến nghị"
                    exec_summary['badge_color'] = 'red'

                # [V24-T5] Thêm câu AI tự nhiên
                _ai_lang = ai_score_to_language(ai_score)
                exec_summary['ai_language'] = _ai_lang
                badge = exec_summary['badge_color']
                ai_lang_html = exec_summary.get('ai_language', '')
                ai_lang_block = f'<div style="font-size:13px; color:#666; margin-top:8px;">🤖 {ai_lang_html}</div>' if ai_lang_html else ''
                st.markdown(f"""
                <div style="padding:15px; border-radius:10px;
                            background-color:{'#d4edda' if badge=='green' else '#fff3cd' if badge=='orange' else '#f8d7da'};
                            border-left:5px solid {'#28a745' if badge=='green' else '#ffc107' if badge=='orange' else '#dc3545'};
                            margin-bottom:15px;">
                    <div style="font-size:14px; color:#555; margin-bottom:5px;">📌 <b>TÓM TẮT 1 CÂU</b></div>
                    <div style="font-size:16px; color:#222;">{exec_summary['one_liner']}</div>
                    {ai_lang_block}
                </div>
                """, unsafe_allow_html=True)
                st.session_state['_exec_summary'] = exec_summary
            except Exception as _es_err:
                print(f"[V24 exec summary] {_es_err}")


            # ── [V24-G2] NEXT STEPS — 3 hành động cụ thể ──
            try:
                _es_for_g2 = st.session_state.get('_exec_summary', {'action': 'WAIT'})
                _fomo_for_g2 = st.session_state.get('_v24_fomo', {'level': 'OK'})
                next_steps = generate_next_steps(scoring, last, _fomo_for_g2,
                                                   _es_for_g2, ticker)
                with st.expander("👉 BƯỚC TIẾP THEO — Bạn nên làm gì?", expanded=True):
                    for i, step in enumerate(next_steps, 1):
                        st.markdown(f"**{step['icon']} {i}. {step['title']}**")
                        st.caption(f"   {step['detail']}")
            except Exception as _g2_err:
                print(f"[G2] {_g2_err}")


            # ── [V24-H1+F4] FOMO/PANIC DETECTOR (gom vào expander nếu đã có LIQ critical) ──
            try:
                fomo_info = detect_fomo_signals(last, df)
                st.session_state['_v24_fomo'] = fomo_info
                _has_critical = st.session_state.get('_v24_critical_warning', False)
                if fomo_info['level'] == 'FOMO_HIGH':
                    if _has_critical:
                        # Đã có LIQ critical, gom FOMO vào expander để không overload
                        with st.expander(f"🚨 Có thêm cảnh báo FOMO mạnh", expanded=False):
                            for f in fomo_info['flags']:
                                st.write(f)
                    else:
                        st.error(f"### {fomo_info['message']}")
                        with st.container(border=True):
                            for f in fomo_info['flags']:
                                st.write(f)
                            st.markdown("---")
                            st.markdown("**💭 Hãy tự hỏi:**")
                            st.write("• Tại sao bạn muốn mua NGAY BÂY GIỜ?")
                            st.write("• Bạn có FOMO không?")
                            st.write("• Có mã nào khác đẹp hơn không?")
                            st.write("• Đợi pullback có được không?")
                elif fomo_info['level'] == 'FOMO_MID':
                    st.warning(f"### {fomo_info['message']}")
                    with st.expander("Chi tiết dấu hiệu FOMO", expanded=True):
                        for f in fomo_info['flags']:
                            st.write(f)
                elif fomo_info['level'] == 'PANIC':
                    st.error(f"### {fomo_info['message']}")
                    with st.expander("Chi tiết dấu hiệu Panic", expanded=True):
                        for f in fomo_info['flags']:
                            st.write(f)
                        st.markdown("**💭 Trước khi 'bắt dao rơi':**")
                        st.write("• Đợi 1-2 phiên xác nhận đáy")
                        st.write("• Vol có giảm dần không?")
                        st.write("• Có hỗ trợ vững chắc không?")
                elif fomo_info['level'] == 'WATCH':
                    with st.expander("👁️ Có vài dấu hiệu cần lưu ý", expanded=False):
                        for f in fomo_info['flags']:
                            st.write(f)
            except Exception as _h1_err:
                print(f"[H1] {_h1_err}")


            # ── [V24 #4-B] CẢNH BÁO CHỐT LỜI cho mã đang xem ──
            try:
                exit_alert = check_exit_signal_simple(last, df)
                render_exit_alert_card(exit_alert, ticker)
            except Exception as _ex_err:
                print(f"[V24 exit alert] {_ex_err}")


            # ── [V24-M1] SCORE TREND 7 NGÀY ──
            try:
                _score_trend = calc_score_trend_7d(df, foreign_trend, weekly_trend,
                                                     sector_score=sector_score, n_days=7)
                if _score_trend and len(_score_trend) >= 5:
                    # Sparkline mini
                    trend_scores = [s['score'] for s in _score_trend]
                    trend_dates = [s.get('date', f"D-{s['days_ago']}") for s in _score_trend]
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(
                        x=trend_dates, y=trend_scores,
                        mode='lines+markers+text',
                        text=[f"{s}" for s in trend_scores],
                        textposition='top center',
                        line=dict(color='#1F3864', width=2),
                        marker=dict(size=8),
                        fill='tozeroy', fillcolor='rgba(31,56,100,0.1)',
                    ))
                    fig_trend.add_hline(y=SCORE_BUY_MIN, line_dash='dash',
                                          line_color='green', annotation_text="Ngưỡng MUA")
                    fig_trend.update_layout(
                        height=200, margin=dict(l=30, r=30, t=40, b=30),
                        title=f"📈 Xu hướng Điểm Tổng Hợp 7 phiên gần nhất — {ticker}",
                        showlegend=False, yaxis=dict(range=[0, 90]),
                        xaxis=dict(showgrid=False),
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)

                    delta_score = trend_scores[-1] - trend_scores[0]
                    if delta_score >= 10:
                        st.success(f"📈 Điểm tăng mạnh +{delta_score:.0f} điểm trong 7 phiên — Đang khoẻ lên")
                    elif delta_score <= -10:
                        st.warning(f"📉 Điểm giảm -{abs(delta_score):.0f} điểm trong 7 phiên — Đang suy yếu")
            except Exception as _m1_err:
                print(f"[V24-M1] {_m1_err}")


            # ── [V24-M8] VOLATILITY REGIME ──
            try:
                vol_regime = detect_volatility_regime(df, n_days=60)
                vc1, vc2, vc3 = st.columns([2, 1, 1])
                with vc1:
                    if vol_regime['level'] == 'HIGH':
                        st.error(vol_regime['label'])
                    elif vol_regime['level'] == 'ELEVATED':
                        st.warning(vol_regime['label'])
                    elif vol_regime['level'] == 'LOW':
                        st.success(vol_regime['label'])
                    else:
                        st.info(vol_regime['label'])
                vc2.metric("ATR / Giá", f"{vol_regime['current_atr_pct']:.2f}%")
                vc3.metric("Percentile 60d", f"{vol_regime['percentile']:.0f}%")
            except Exception as _m8_err:
                print(f"[V24-M8] {_m8_err}")


            # ── [V36-N1] SMART MONEY PROXY ──
            try:
                smp = detect_smart_money_proxy(df)
                if smp.get('signal') and smp['signal'] != 'NEUTRAL':
                    with st.container(border=True):
                        st.markdown("##### 💰 Smart Money Proxy")
                        sig = smp['signal']
                        if sig == 'STRONG_BUY':
                            st.success(f"💎 **MUA MẠNH** (Confidence: {smp['confidence']}%)")
                        elif sig == 'STRONG_SELL':
                            st.error(f"🔴 **BÁN MẠNH** (Confidence: {smp['confidence']}%)")
                        elif sig == 'ACCUMULATION':
                            st.info(f"🤫 **TÍCH LŨY THẦM** — Có thể smart money đang gom (Conf: {smp['confidence']}%)")
                        elif sig == 'DISTRIBUTION':
                            st.warning(f"⚠️ **PHÂN PHỐI THẦM** — Có thể smart money đang xả (Conf: {smp['confidence']}%)")
                        for s in smp.get('signals', []):
                            st.caption(f"• {s}")
                        st.caption(f"📊 TB 10 ngày: giá {smp['avg_ret_10d']:+.2f}%/ngày, "
                                      f"vol {smp['avg_vol_ratio']:.2f}x, "
                                      f"{smp['high_vol_days']} phiên vol >1.5x, "
                                      f"{smp['very_high_vol_days']} phiên vol >2.5x")
            except Exception as _smp_err:
                print(f"[V36-N1] {_smp_err}")

            # ── [V39-M1] MA10 BOOSTER — Vạch vàng signal ──
            try:
                ma10_res = calc_ma10_bonus(df)
                with st.container(border=True):
                    st.markdown("##### 🟡 MA10 Signal (Vạch vàng)")
                    sig_type = ma10_res.get('signal_type')
                    if sig_type == 'CROSS_UP':
                        st.success(f"### {ma10_res['message']}")
                    elif sig_type == 'CROSS_DOWN':
                        st.error(f"### {ma10_res['message']}")
                    elif sig_type == 'STRONG_ABOVE':
                        st.success(ma10_res['message'])
                    elif sig_type == 'ABOVE':
                        st.info(ma10_res['message'])
                    elif sig_type == 'BELOW':
                        st.warning(ma10_res['message'])
                    else:
                        st.info(ma10_res.get('message', ''))

                    for d in ma10_res.get('details', []):
                        st.caption(d)

                    # Hiển thị điểm bonus + tổng kết hợp
                    bonus = ma10_res.get('bonus', 0)
                    ma10_c1, ma10_c2 = st.columns(2)
                    if bonus > 0:
                        ma10_c1.metric("🎯 MA10 Bonus", f"+{bonus} điểm",
                                          delta="Tích cực" if bonus >= 15 else "Nhẹ")
                    elif bonus < 0:
                        ma10_c1.metric("🎯 MA10 Bonus", f"{bonus} điểm",
                                          delta="Cảnh báo", delta_color="inverse")
                    else:
                        ma10_c1.metric("🎯 MA10 Bonus", "0 điểm", delta="Trung tính")

                    # Tổng điểm V39 = điểm V23 + MA10 bonus
                    _v23_score = total_score if 'total_score' in dir() else 0
                    _v39_total = _v23_score + bonus
                    ma10_c2.metric("📊 Điểm V39 (V23 + MA10)",
                                      f"{_v39_total:.0f}",
                                      delta=f"V23: {_v23_score:.0f} | MA10: {bonus:+d}",
                                      delta_color="off")
            except Exception as _ma10_err:
                st.caption(f"[V39-M1 lỗi]: {_ma10_err}")

            # ── [V40-F2+F3] FLOAT ANALYSIS — Số CP lưu hành & cảnh báo Pump Risk ──
            try:
                _date_key_f = datetime.now(TZ_VN).strftime('%Y-%m-%d')
                float_data = get_float_data_cached(ticker, _date_key_f)
                with st.container(border=True):
                    st.markdown("##### 📦 Float Analysis (V40)")

                    if not float_data.get('available'):
                        st.info(
                            f"ℹ️ Không có data Float cho {ticker} "
                            f"(lý do: {float_data.get('error', 'N/A')[:60]})"
                        )
                    else:
                        ff = float_data['free_float_pct']
                        fr = float_data['foreigner_pct']
                        fr_max = float_data['max_foreigner_pct']
                        room = float_data['room_left_pct']
                        out_sh = float_data['outstanding_share']
                        avg_val = float_data['avg_match_val_1m']

                        # Classifier
                        ft = classify_float_tier(ff, fr)
                        tier = ft['tier']
                        emoji = ft['tier_emoji']

                        # Hiển thị tier verdict
                        if tier == 'HIGH':
                            st.success(f"### {emoji} FLOAT {tier} — {ft['message']}")
                        elif tier == 'MEDIUM':
                            st.info(f"### {emoji} FLOAT {tier} — {ft['message']}")
                        elif tier == 'LOW':
                            st.warning(f"### {emoji} FLOAT {tier} — {ft['message']}")
                        elif tier == 'VERY_LOW':
                            st.error(f"### {emoji} FLOAT {tier} — {ft['message']}")

                        # Metrics
                        fc1, fc2, fc3, fc4 = st.columns(4)
                        fc1.metric("Free Float", f"{ff:.1f}%",
                                     help="% CP có thể giao dịch tự do (loại trừ CP bị khoá)")
                        fc2.metric("Khối ngoại giữ", f"{fr:.1f}%",
                                     delta=f"Room còn {room:.1f}%",
                                     delta_color="off")
                        fc3.metric("Effective Float",
                                     f"~{ft.get('effective_float', 0):.1f}%",
                                     help="Free Float - phần ngoại giữ chặt (>10%)")
                        if avg_val > 0:
                            fc4.metric("Giá trị khớp TB 1 tháng",
                                         f"{avg_val:.1f} tỷ/phiên")

                        # Outstanding shares (nếu có)
                        if out_sh > 0:
                            st.caption(f"📊 Tổng CP lưu hành: **{out_sh:,}** cp")

                        # Size advice
                        st.markdown(f"💡 **Khuyến nghị size lệnh:** {ft['size_advice']}")

                        # F3: Pump risk detection
                        try:
                            _last = df.iloc[-1]
                            _vol = float(_last.get('vol_strength', 1.0))
                            _ret_1d = float(_last.get('return_1d', 0)) * 100
                            pump = detect_float_pump_risk(float_data, _vol, _ret_1d)
                            if pump.get('risk'):
                                st.error(pump['message'])
                        except Exception:
                            pass

                        st.caption(f"💾 Cache 24h | Data: vnstock trading_stats()")
            except Exception as _f_err:
                st.caption(f"[V40-F2 lỗi]: {_f_err}")

            # ── [V41-R1] RÚT CHÂN DETECTOR ──
            try:
                rc = detect_rut_chan(df)
                with st.container(border=True):
                    st.markdown("##### 🦵 Rút Chân Detector (V41)")
                    if rc.get('signal'):
                        sig = rc['signal']
                        if sig == 'STRONG':
                            st.success(f"### {rc['message']}")
                        elif sig == 'GOOD':
                            st.info(f"### {rc['message']}")
                        elif sig == 'MILD':
                            st.warning(f"### {rc['message']}")

                        # Metrics
                        rc1, rc2, rc3, rc4 = st.columns(4)
                        rc1.metric("Giảm sâu nhất", f"{rc['drop_pct']:.2f}%",
                                     help="% giảm so với open trong phiên")
                        rc2.metric("Phục hồi từ đáy", f"{rc['recovery_pct']:.0f}%",
                                     help="% close phục hồi trong range cao-thấp")
                        rc3.metric("Close vs Open", f"{rc['close_vs_open_pct']:+.2f}%")
                        rc4.metric("Vol strength", f"{rc['vol_strength']:.2f}x")

                        # Quality verdict
                        st.markdown(f"**{rc['quality_verdict']}**")
                        qc1, qc2 = st.columns([1, 3])
                        qc1.metric("Quality", f"{rc['quality_score']}/100")
                        with qc2:
                            if rc.get('is_at_support'):
                                st.success("✅ Rút chân TẠI HỖ TRỢ (gần MA) — tín hiệu mạnh")
                            for w in rc.get('warnings', []):
                                st.warning(w)

                        # Hành động đề xuất
                        if rc['quality_score'] >= 75 and sig in ('STRONG', 'GOOD'):
                            st.success(
                                "💡 **Đề xuất hành động:** Đáng cân nhắc vào lệnh phiên sau "
                                "với size vừa + SL chặt dưới low hôm nay 1-2%"
                            )
                        elif rc['quality_score'] < 35:
                            st.error(
                                "⚠️ **Đề xuất hành động:** TRÁNH — Rút chân chất lượng thấp, có thể là bẫy"
                            )
                        else:
                            st.info(
                                "💡 **Đề xuất hành động:** Theo dõi phiên sau xác nhận trước khi vào lệnh"
                            )
                    else:
                        st.caption(f"ℹ️ {rc.get('message', 'Không có rút chân hôm nay')}")
                        if rc.get('drop_pct') is not None and rc.get('drop_pct') < -1:
                            st.caption(
                                f"📊 Phiên nay: giảm sâu nhất {rc['drop_pct']:.2f}%, "
                                f"phục hồi {rc.get('recovery_pct', 0):.0f}%, "
                                f"close {rc.get('close_vs_open_pct', 0):+.2f}% so open"
                            )
            except Exception as _rc_err:
                st.caption(f"[V41-R1 lỗi]: {_rc_err}")

            # ── [V28-P1] CANDLESTICK PATTERN DETECTOR ──
            try:
                patterns_detected = detect_candlestick_patterns(df)
                if patterns_detected:
                    with st.container(border=True):
                        st.markdown("##### 🕯️ Mẫu nến phát hiện (3-5 phiên gần nhất)")
                        for p in patterns_detected:
                            if p['type'] == 'BULLISH':
                                st.success(f"**{p['name']}** — {p['message']}")
                            elif p['type'] == 'BEARISH':
                                st.error(f"**{p['name']}** — {p['message']}")
                            else:
                                st.info(f"**{p['name']}** — {p['message']}")
            except Exception as _p1_err:
                print(f"[V28-P1] {_p1_err}")

            # ── [V24-G3] WHY THIS SCORE? ──
            try:
                with st.expander(f"🤔 Tại sao điểm tổng = {scoring['total']}/90? (Click để xem)"):
                    breakdown = explain_score_breakdown(scoring, last, bt, ai_score)
                    for b in breakdown:
                        bc1, bc2 = st.columns([1, 3])
                        bc1.markdown(f"**{b['group']}**: {b['pts']}/{b['max']}")
                        bc2.caption(b['reason'])
                    st.divider()
                    if scoring['total'] >= SCORE_BUY_MIN:
                        st.success(f"✅ Tổng {scoring['total']}/90 đã vượt ngưỡng MUA ({SCORE_BUY_MIN})")
                    else:
                        st.warning(f"⏳ Tổng {scoring['total']}/90 chưa đủ ngưỡng MUA (cần ≥{SCORE_BUY_MIN})")
            except Exception as _g3_err:
                print(f"[G3] {_g3_err}")


            # ═══════════════════════════════════════════════════════════════
            # SECTION B: PHÂN TÍCH CHI TIẾT (V23 charts, backtest, indicators)
            # ═══════════════════════════════════════════════════════════════










            st.markdown(
                "> 🧠 **Nhà Phân Tích Ảo V24.0:** Tự động tổng hợp dữ liệu đa chiều — "
                "ATR Trailing Stop | ADX/OBV AI | Kelly Sizing | Sharpe/MaxDD | Market Regime."
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
            # [V26] Đã xoá Metrics 4+3 (Winrate, Sharpe, DD, Tín hiệu BT) — không cần xem
            # GIỮ T1/T2/T4 bên dưới để cảnh báo backtest âm
            # ── #1 EQUITY CURVE + #5 SIGNAL MARKERS ──
            profits_list  = bt.get('profits', [])
            signals_data  = bt.get('signals_data', [])
            if profits_list:
                equity_curve = np.cumprod([1 + p for p in profits_list]) * 100
                equity_final_pct = float(equity_curve[-1])

                # [V24-T1] Cảnh báo equity âm
                if equity_final_pct < 90:
                    st.error(f"🚨 **CHIẾN LƯỢC LỖ {100-equity_final_pct:.1f}%** trên mã {ticker} — Nên cân nhắc kỹ trước khi mua")
                elif equity_final_pct < 100:
                    st.warning(f"⚠️ **Backtest gần hoà vốn** ({equity_final_pct:.1f}%) — Chiến lược chưa có edge rõ ràng trên mã này")
                elif bt.get('expectancy', 0) < 0:
                    st.warning(f"⚠️ Expectancy âm ({bt['expectancy']:+.2f}%) — Cẩn trọng")

                # [V24-T2] Win/Loss streak
                streak_info = calc_win_loss_streak(profits_list, n=6)
                # [V24-T4] Confidence Score
                conf_info = calc_confidence_stars(bt, equity_final_pct)

                strk_c1, strk_c2 = st.columns([2, 1])
                with strk_c1:
                    streak_color = '🟢' if streak_info['win_pct'] >= 50 else '🔴'
                    st.markdown(f"**{streak_color} {streak_info['recent_n']} lệnh gần nhất:** "
                                  f"`{streak_info['streak_str']}` ({streak_info['win_pct']:.0f}%)")
                    if streak_info['last_result'] == 'L' and streak_info['consecutive'] >= 3:
                        st.caption(f"⚠️ Chuỗi {streak_info['consecutive']} lệnh thua liên tiếp — strategy đang lạnh")
                    elif streak_info['last_result'] == 'W' and streak_info['consecutive'] >= 3:
                        st.caption(f"🔥 Chuỗi {streak_info['consecutive']} lệnh thắng liên tiếp — strategy đang nóng")
                with strk_c2:
                    st.markdown(f"**Độ tin cậy:** {conf_info['label']}")
                    st.caption(f"{conf_info['stars']}/5 ⭐")

                with st.expander("Chi tiết tiêu chí Confidence Score"):
                    for c in conf_info['criteria']:
                        st.write(c)
                st.session_state['_v24_equity_final'] = equity_final_pct
                st.session_state['_v24_confidence'] = conf_info['stars']
                st.session_state['_v24_streak'] = streak_info
                # [V26] Đã xoá Chart signal markers backtest — không cần xem
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
                st.markdown("**🌱 Tích Lũy Nền Score**")
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
            x     = get_date_col(chart)
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
            st.session_state['tab1_liq']     = analyze_liquidity(df, ticker)
            # [#4] Lưu lịch sử điểm
            save_score_history(ticker, scoring['total'],
                               float(ai_score) if _is_valid_score(ai_score) else 0.0)
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
        # [V25] Đã xoá Risk/Reward Calculator (V23) — dùng Auto Position Sizing R2 + Stop-Loss Calc M3 thay thế
        # [V25] Đã xoá Trade Journal Theo Dõi Lệnh Đang Mở (V23) — dùng Position Manager V24 ở sidebar
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
        # ── [#4] SCORE TIMELINE ──
        st.write("### 📈 Lịch Sử Điểm Số — Score Timeline")
        score_hist = get_score_history(ticker)
        if len(score_hist) >= 2:
            sh_dates  = [h['date'] for h in score_hist]
            sh_scores = [h['score'] for h in score_hist]
            sh_ai     = [h['ai'] for h in score_hist]
            fig_sh = go.Figure()
            fig_sh.add_trace(go.Scatter(x=sh_dates, y=sh_scores, mode="lines+markers",
                name="Điểm Tổng Hợp", line=dict(color="royalblue", width=2), marker=dict(size=8)))
            fig_sh.add_trace(go.Scatter(x=sh_dates, y=sh_ai, mode="lines+markers",
                name="AI T+3 (%)", line=dict(color="orange", width=1.5, dash="dot"), marker=dict(size=6)))
            fig_sh.add_hline(y=SCORE_BUY_MIN, line_dash="dot", line_color="green",
                             annotation_text=f"Ngưỡng mua {SCORE_BUY_MIN}")
            fig_sh.update_layout(height=300, template="plotly_white",
                title=f"Xu Hướng Điểm Số {ticker}", yaxis_title="Điểm",
                margin=dict(l=20,r=20,t=50,b=20), legend=dict(orientation="h",yanchor="bottom",y=1.02))
            st.plotly_chart(fig_sh, use_container_width=True)
            trend_s = sh_scores[-1] - sh_scores[0]
            if trend_s > 5:   st.success(f"📈 Điểm tăng {trend_s:+.0f} qua {len(sh_scores)} lần — tích cực.")
            elif trend_s < -5: st.warning(f"📉 Điểm giảm {trend_s:+.0f} — cần theo dõi.")
            else:              st.info(f"➡️ Điểm ổn định, dao động {trend_s:+.0f} điểm.")
        else:
            st.caption("Phân tích thêm vài lần để thấy xu hướng điểm số theo thời gian.")
        st.divider()
        # ── [#5] LIQUIDITY ANALYSIS ──
        st.write("### 💧 Phân Tích Thanh Khoản")
        liq = st.session_state.get("tab1_liq", {})
        if liq:
            lq_fn = {"success":st.success,"warning":st.warning,"error":st.error}
            lq_fn.get(liq["liq_color"], st.info)(liq["liq_label"])
            lq1,lq2,lq3,lq4 = st.columns(4)
            lq1.metric("GT Khớp Lệnh TB", f"{liq['vol_avg_bn']:.1f} Tỷ/phiên")
            lq2.metric("Spread Ước Tính",  f"{liq['spread_pct']:.3f}%")
            lq3.metric("Impact Cost 1 Tỷ", f"{liq['impact_1ty']:.3f}%")
            lq4.metric("Impact Cost 5 Tỷ", f"{liq['impact_5ty']:.3f}%")
            st.caption(f"⏰ **Thời điểm tốt nhất:** {liq['best_times']}")
        st.divider()
        # ── [#3] VOL EVENT ANALYSIS ──
        st.write("### ⚡ Phân Tích Biến Động Sau Vol Đột Biến")
        if df_cached is not None:
            events_vol = analyze_volume_events(df_cached)
            if events_vol:
                bull_a = sum(1 for e in events_vol if e["ret_after"] > 0)
                bear_a = len(events_vol) - bull_a
                ev1,ev2,ev3 = st.columns(3)
                ev1.metric("Số sự kiện Vol đột biến", len(events_vol))
                ev2.metric("Tăng sau 5 phiên", f"{bull_a} ({bull_a/len(events_vol)*100:.0f}%)")
                ev3.metric("Giảm sau 5 phiên", f"{bear_a} ({bear_a/len(events_vol)*100:.0f}%)")
                if bull_a > bear_a * 1.5:
                    st.success(f"✅ Vol đột biến thường tăng tiếp — tín hiệu mua đáng tin với {ticker}.")
                elif bear_a > bull_a * 1.5:
                    st.warning(f"⚠️ Vol đột biến thường giảm sau — cẩn thận khi Vol nổ.")
                else:
                    st.info("🟡 Vol đột biến 50/50 — không có pattern rõ ràng.")
                with st.expander("📋 Chi tiết sự kiện"):
                    df_ev = pd.DataFrame([{"Ngày":e["date"],"Vol":f"{e['vol']:.1f}x",
                        "% Ngày đó":f"{e['ret_day']:+.1f}%","5 ngày trước":f"{e['ret_before']:+.1f}%",
                        "5 ngày sau":f"{e['ret_after']:+.1f}%",
                        "Kết quả":"✅" if e["ret_after"]>0 else "🔴"} for e in events_vol[-10:]])
                    st.dataframe(df_ev, use_container_width=True, hide_index=True)
            else:
                st.caption("Chưa có sự kiện Vol đột biến trong lịch sử.")
        st.divider()
        # ── [#2] PORTFOLIO BACKTEST ──
        st.write("### 📦 Portfolio Backtest — Kiểm Tra Danh Mục")
        port_input = st.text_input(
            "Nhập mã và tỷ trọng (VD: FPT:40, ACB:30, HPG:30):",
            placeholder="FPT:40, ACB:30, HPG:30",
            key="port_input"
        )
        if st.button("📊 Chạy Portfolio Backtest", key="port_btn") and port_input:
            try:
                parts = [p.strip() for p in port_input.split(',')]
                tw = {}
                for p in parts:
                    if ':' in p:
                        sym, w = p.split(':')
                        tw[sym.strip().upper()] = float(w.strip()) / 100
                total_w = sum(tw.values())
                if total_w > 0:
                    tw = {k: v/total_w for k,v in tw.items()}   # normalize về 100%
                with st.spinner(f"Đang backtest {len(tw)} mã..."):
                    port_res = portfolio_backtest(tw)
                st.session_state['port_result'] = port_res
            except Exception as e:
                st.error(f"❌ Lỗi nhập liệu: {e}")
        if st.session_state.get('port_result'):
            pr = st.session_state['port_result']
            if 'error' in pr:
                st.error(pr['error'])
            else:
                pc1, pc2, pc3, pc4 = st.columns(4)
                pc1.metric("Tổng Return",   f"{pr['total_return']:+.2f}%",
                           delta_color="normal" if pr['total_return']>0 else "inverse")
                pc2.metric("Sharpe",        f"{pr['sharpe']:.2f}")
                pc3.metric("Max Drawdown",  f"{pr['max_drawdown']:.2f}%", delta_color="inverse")
                pc4.metric("Số Tín Hiệu",   f"{pr['n_signals']}")
                # Equity curve
                if pr.get('equity_curve'):
                    eq = pr['equity_curve']
                    fig_port = go.Figure(go.Scatter(
                        y=[v*100 for v in eq],
                        mode='lines', name='Portfolio',
                        fill='tozeroy',
                        fillcolor='rgba(0,180,100,0.1)',
                        line=dict(color='green' if eq[-1]>=1 else 'red', width=2),
                    ))
                    fig_port.add_hline(y=100, line_dash='dot', line_color='gray')
                    fig_port.update_layout(height=300, template='plotly_white',
                        title="Portfolio Equity Curve (%)",
                        yaxis_title="% Vốn", margin=dict(l=20,r=20,t=50,b=20))
                    st.plotly_chart(fig_port, use_container_width=True)
                # Từng mã
                st.write("**Đóng Góp Từng Mã:**")
                for t_p, d_p in pr.get('ticker_results', {}).items():
                    bt_p = d_p['bt']
                    st.caption(
                        f"**{t_p}** ({d_p['weight']*100:.0f}%) — "
                        f"Winrate: {bt_p['winrate']}% | "
                        f"Kỳ vọng: {bt_p['expectancy']:+.2f}% | "
                        f"Sharpe: {bt_p['sharpe']:.2f}"
                    )
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






            # ═══════════════════════════════════════════════════════════════
            # [V24-X1] SECTION C: HÀNH ĐỘNG (quản lý vị thế cho mã này)
            # ═══════════════════════════════════════════════════════════════

            # ── [V24 #4-A] PORTFOLIO POSITION CHECK ──
            with st.expander(f"💼 Tôi đang giữ {ticker} — Kiểm tra Exit Signal"):
                pc_c1, pc_c2, pc_c3 = st.columns(3)
                pc_entry = pc_c1.number_input(
                    f"Giá vào lệnh {ticker}",
                    min_value=0.0, value=float(last['close']),
                    step=100.0, key=f"pc_entry_{ticker}")
                pc_shares = pc_c2.number_input(
                    "Số lượng (cp)",
                    min_value=0, value=1000, step=100, key=f"pc_shares_{ticker}")
                pc_current = pc_c3.number_input(
                    "Giá hiện tại",
                    min_value=0.0, value=float(last['close']),
                    step=100.0, key=f"pc_current_{ticker}")

                if pc_entry > 0 and pc_shares > 0:
                    try:
                        ex_signal = generate_exit_signal(
                            last, df, pc_entry, pc_current,
                            weekly_trend, divergence, ai_score)
                        render_exit_signal_card(ex_signal, pc_current, pc_entry, pc_shares)
                    except Exception as _pc_err:
                        st.warning(f"Không tính được exit signal: {_pc_err}")


            # ── [V24-Q5 + V38-G1+G2] QUICK ADD: Tách rõ Watchlist vs Đã mua ──
            with st.expander(f"📌 Thao tác với {ticker}", expanded=False):
                st.caption(
                    "⚠️ **Phân biệt rõ:**\\n"
                    "• 📌 **Thêm Watchlist** = chỉ theo dõi, KHÔNG tính lỗ/lời\\n"
                    "• 💰 **Tôi ĐÃ MUA** = thực sự đã giao dịch, sẽ vào Portfolio (lỗ/lời thật)"
                )

                v38_tab_wl, v38_tab_buy = st.tabs(["📌 Thêm Watchlist", "💰 Tôi ĐÃ MUA"])

                # ─── G2-A: TAB WATCHLIST (theo dõi, không tính P&L) ───
                with v38_tab_wl:
                    st.markdown(f"### 📌 Thêm **{ticker}** vào Watchlist")
                    st.caption("Chỉ để theo dõi, KHÔNG vào Portfolio, KHÔNG tính lỗ/lời.")
                    wl_note = st.text_input(
                        "Ghi chú (tuỳ chọn)",
                        key=f"v38_wl_note_{ticker}",
                        placeholder="VD: Chờ break MA20 mới vào"
                    )
                    if st.button(f"📌 Thêm {ticker} vào Watchlist",
                                  key=f"v38_wl_add_{ticker}",
                                  type="primary"):
                        if 'watchlist' not in st.session_state:
                            st.session_state['watchlist'] = list(PILLARS[:10])
                        if ticker not in st.session_state['watchlist']:
                            st.session_state['watchlist'].append(ticker)
                            try:
                                with open('watchlist.json', 'w', encoding='utf-8') as f:
                                    json.dump(list(st.session_state['watchlist']), f, ensure_ascii=False)
                            except Exception:
                                pass
                            st.success(f"✅ Đã thêm **{ticker}** vào Watchlist (chỉ theo dõi)")
                            if wl_note:
                                st.caption(f"📝 Ghi chú: {wl_note}")
                        else:
                            st.info(f"{ticker} đã có trong Watchlist")

                # ─── G2-B: TAB ĐÃ MUA (vào Portfolio thật) ───
                with v38_tab_buy:
                    st.markdown(f"### 💰 Tôi ĐÃ MUA **{ticker}**")
                    st.warning(
                        "⚠️ **Chỉ ấn nếu bạn ĐÃ THỰC SỰ giao dịch trên broker. "
                        "Sau khi thêm, app sẽ tính lỗ/lời theo giá entry.**"
                    )

                    qa_c1, qa_c2 = st.columns(2)
                    qa_shares = qa_c1.number_input("Số cp đã mua", min_value=100, step=100,
                                                      value=1000, key=f"qa_shares_{ticker}")
                    qa_entry = qa_c2.number_input("Giá vào lệnh thực tế", min_value=100.0, step=100.0,
                                                    value=float(last['close']),
                                                    key=f"qa_entry_{ticker}")

                    # [V24-F3] Cảnh báo LIQ_LOW
                    _liq_q5 = st.session_state.get('_v24_liq', {'tier': 'UNKNOWN'})
                    if _liq_q5.get('tier') == 'LOW':
                        st.error(f"🔴 **CẢNH BÁO:** {ticker} có thanh khoản thấp — KHÔNG khuyến nghị mua")
                        st.caption(f"Vol TB: {_liq_q5.get('vol_avg', 0)/1000:.0f}K | Turnover: {_liq_q5.get('turnover_avg', 0):.1f} tỷ")

                    # [V24-H3] PRE-TRADE CHECKLIST (giờ là "post-trade confirmation")
                    st.markdown("**📋 Xác nhận quyết định mua của bạn:**")
                    ck1 = st.checkbox("✅ Tôi đã xác định SL rõ ràng", key=f"ck1_{ticker}")
                    ck2 = st.checkbox("✅ Size lệnh KHÔNG quá 20% vốn", key=f"ck2_{ticker}")
                    ck3 = st.checkbox("✅ Tôi KHÔNG FOMO khi mua", key=f"ck3_{ticker}")
                    ck4 = st.checkbox("✅ Tôi có lý do CỤ THỂ để mua", key=f"ck4_{ticker}")
                    ck5 = st.checkbox("✅ Đã có chiến lược thoát (TP/SL)", key=f"ck5_{ticker}")
                    ck_liq = True
                    if _liq_q5.get('tier') == 'LOW':
                        ck_liq = st.checkbox(f"⚠️ Tôi BIẾT {ticker} có LIQ thấp & chấp nhận rủi ro",
                                                key=f"ck_liq_{ticker}")
                    all_checked = ck1 and ck2 and ck3 and ck4 and ck5 and ck_liq

                    qa_reason = ""
                    if all_checked:
                        qa_reason = st.text_input("📝 Lý do mua (bắt buộc)",
                                                     key=f"qa_reason_{ticker}",
                                                     placeholder="VD: Chân sóng 7/12 + MACD bullish")

                    if st.button(f"💰 Xác nhận: TÔI ĐÃ MUA {qa_shares:,} cp {ticker}",
                                  key=f"qa_add_{ticker}",
                                  type="primary",
                                  disabled=not (all_checked and qa_reason)):
                        if 'v24_positions' not in st.session_state:
                            st.session_state['v24_positions'] = load_positions_from_file()
                        _liq_save = st.session_state.get('_v24_liq', {'tier': 'UNKNOWN'})
                        _label_save = label if 'label' in dir() else 'UNKNOWN'
                        st.session_state['v24_positions'].append({
                            'ticker': ticker, 'shares': qa_shares, 'entry': qa_entry,
                            'reason': qa_reason,
                            'added_at': datetime.now(TZ_VN).strftime('%Y-%m-%d %H:%M'),
                            'tier_at_buy': _label_save,
                            'liq_tier_at_buy': _liq_save.get('tier', 'UNKNOWN'),
                        })
                        save_positions_to_file(st.session_state['v24_positions'])
                        st.success(f"✅ Đã thêm vào Portfolio: {qa_shares:,} cp {ticker} @ {qa_entry:,.0f}đ")
                        st.balloons()
                    if not all_checked:
                        st.caption("⏳ Hãy tick đủ checklist + ghi lý do để mở nút xác nhận")


            # ── [V24-R2] AUTO POSITION SIZING ──
            with st.expander(f"🤖 Auto Position Sizing cho {ticker} [R2]"):
                r2_c1, r2_c2 = st.columns(2)
                r2_capital = r2_c1.number_input("Vốn (đồng)", min_value=1_000_000,
                                                   value=100_000_000, step=10_000_000,
                                                   format="%d", key=f"r2_cap_{ticker}")
                r2_atr = float(last.get('atr', last['close'] * 0.02))
                r2_c2.metric("ATR hiện tại", f"{r2_atr:,.0f}")

                # Lấy regime + vol regime
                _r2_regime = st.session_state.get('market_regime', {})
                _r2_vol = vol_regime if 'vol_regime' in dir() else {'size_recommend': 1.0, 'level': 'UNKNOWN'}
                _r2_npos = len(st.session_state.get('v24_positions', []))

                if st.button(f"💡 Tính size tối ưu cho {ticker}", key=f"r2_btn_{ticker}"):
                    r2_res = calc_auto_position_size(
                        r2_capital, float(last['close']), r2_atr,
                        kelly_pct, _r2_vol, _r2_regime, _r2_npos)
                    if r2_res['shares'] > 0:
                        st.success(f"📦 Đề xuất: **{r2_res['shares']:,} cp** ({r2_res['size_pct']}% vốn)")
                        st.write(f"💰 Tổng: {r2_res['value']:,.0f}đ")
                        st.write(f"🛡️ SL: {r2_res['sl_price']:,.0f} (rủi ro: {r2_res['dollar_risk']:,.0f}đ)")
                        st.write(f"🎯 TP1: {r2_res['tp1_price']:,.0f} | TP2: {r2_res['tp2_price']:,.0f} | TP3: {r2_res['tp3_price']:,.0f}")
                        st.caption(f"Limited by: {r2_res['limiter']}")
                        with st.expander("Logic tính size"):
                            for r in r2_res['reasoning']:
                                st.write(f"• {r}")
                    else:
                        st.warning("Không tính được — kiểm tra input")


            # ── [V24-M2] WHAT-IF SIMULATOR ──
            with st.expander("🔮 What-if: Mô phỏng giá/RSI thay đổi"):
                st.caption("Trượt thanh để xem điểm tổng thay đổi thế nào nếu giá hoặc RSI thay đổi.")
                wif_c1, wif_c2, wif_c3 = st.columns(3)
                cur_price = float(last['close'])
                cur_rsi = float(last['rsi'])
                wif_price = wif_c1.slider(
                    "Giá giả định",
                    min_value=float(cur_price * 0.85),
                    max_value=float(cur_price * 1.15),
                    value=cur_price, step=100.0,
                    key=f"wif_p_{ticker}")
                wif_rsi = wif_c2.slider(
                    "RSI giả định", 20.0, 90.0, cur_rsi, 1.0,
                    key=f"wif_r_{ticker}")
                wif_macd = wif_c3.checkbox(
                    "MACD bullish?",
                    value=bool(last['macd'] > last['signal']),
                    key=f"wif_m_{ticker}")
                try:
                    new_score = whatif_recalc_score(
                        last, wif_price, wif_rsi, wif_macd, weekly_trend,
                        foreign_trend, growth, pe, ai_score,
                        sector_score=sector_score)
                    delta_score = new_score - scoring['total']
                    st.metric(f"Điểm tổng MỚI",
                                f"{new_score}/90",
                                delta=f"{delta_score:+d} điểm")
                    if new_score >= SCORE_BUY_MIN:
                        st.success(f"✅ Đạt ngưỡng MUA ({SCORE_BUY_MIN}/90)")
                    else:
                        st.warning(f"⏳ Chưa đạt ngưỡng MUA ({new_score}/{SCORE_BUY_MIN})")
                except Exception as _m2_err:
                    st.warning(f"Không tính được: {_m2_err}")


            # ── [V24 #1] NHẮC LẠI EXECUTIVE SUMMARY CUỐI BÀI ──
            _es = st.session_state.get('_exec_summary')
            if _es:
                st.divider()
                st.markdown("### 📌 KẾT LUẬN")
                badge = _es['badge_color']
                st.markdown(f"""
                <div style="padding:15px; border-radius:10px;
                            background-color:{'#d4edda' if badge=='green' else '#fff3cd' if badge=='orange' else '#f8d7da'};
                            border-left:5px solid {'#28a745' if badge=='green' else '#ffc107' if badge=='orange' else '#dc3545'};">
                    <div style="font-size:17px; color:#222;">{_es['one_liner']}</div>
                </div>
                """, unsafe_allow_html=True)

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
        _dt_pf = get_date_col(df_price_flow)
        if _dt_pf is not None:
            price_dates = [str(d)[:10] for d in _dt_pf.tail(10).tolist()]
        else:
            price_dates = []
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
            _dt_pf2 = get_date_col(df_price_flow)
            if _dt_pf2 is not None and hasattr(_dt_pf2, 'astype'):
                day_row = df_price_flow[_dt_pf2.astype(str).str[:10] == d]
            else:
                day_row = pd.DataFrame()
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
        # [FIX] Vnstock 3.2.6 trả về cột 'time' (không phải 'date'); yfinance trả 'date'
        if 'date' in df_obv2.columns:
            x_obv = df_obv2['date']
        elif 'time' in df_obv2.columns:
            x_obv = df_obv2['time']
        else:
            x_obv = df_obv2.index
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
    # [V24-E2] Disclaimer rõ ràng
    st.info(
        "📌 **Lưu ý quan trọng:** App này **KHÔNG khuyến nghị mua/bán**. "
        "Đây là phân tích kỹ thuật để hỗ trợ ra quyết định. "
        "Mọi rủi ro và kết quả thuộc về bạn. "
        "Tầng 1/2 = rủi ro thấp hơn; Tầng 3 = rủi ro cao, có thể đợi 2-4 tuần; "
        "Tầng 4/5 = chỉ theo dõi, KHÔNG mua."
    )
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
        if st.button("▶️ Chạy Hiệu Chỉnh Ngưỡng (50 mã mẫu)", key="auto_btn_Ch_y_Hi_u_Ch_nh_N_2"):
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
    # ── [#1] QUICK PICK ──
    st.write("### 🎯 Quick Pick — Cho Tôi 3 Mã Tốt Nhất Hôm Nay")
    # [V24-E2] Disclaimer
    st.caption(
        "⚠️ Đây là **xếp hạng phân tích kỹ thuật**, KHÔNG phải khuyến nghị mua. "
        "Kiểm tra RS Rating ≥ 50, Tầng phù hợp, và cảnh báo trong card trước khi quyết định. "
        "App không chịu trách nhiệm cho mọi quyết định giao dịch."
    )
    qp_c1, qp_c2 = st.columns([1, 3])
    ai_min_qp = qp_c1.slider("AI T+3 tối thiểu (%):", 35, 65, 45, 5)
    qp_use_diversify = qp_c2.checkbox(
        "🌐 Đa dạng hoá (tránh trùng ngành/tương quan cao)",
        value=True,
        help="V24: Lọc các mã có correlation < 0.7 với nhau để đa dạng portfolio")
    if qp_c2.button("🎯 Tìm 3 Mã Tốt Nhất Ngay", key="quickpick_btn"):
        with st.spinner(f"Đang quét tìm mã AI ≥ {ai_min_qp}%..."):
            qp_results = quick_pick_stocks(tickers, ai_min=float(ai_min_qp))
            # [V24 #3] Áp Correlation Check nếu user bật
            if qp_use_diversify and qp_results and len(qp_results) > 3:
                try:
                    # quick_pick_stocks trả về top 3, nên cần mở rộng để chọn lại
                    # Tạm thời chỉ áp diversify trên kết quả hiện có
                    qp_results = diversified_top_pick(qp_results, n=3, max_corr=0.7)
                except Exception as _qp_div_err:
                    print(f"[V24 quickpick diversify] {_qp_div_err}")
        st.session_state['qp_results'] = qp_results
    if st.session_state.get('qp_results'):
        qp_list = st.session_state['qp_results']
        if qp_list:
            st.success(f"✅ Tìm được {len(qp_list)} mã — xếp theo điểm tổng hợp:")
            for i, q in enumerate(qp_list, 1):
                with st.container(border=True):
                    qc1, qc2, qc3, qc4 = st.columns([1.5, 2, 2, 2])
                    with qc1:
                        st.markdown(f"### #{i} `{q['ticker']}`")
                        st.caption(f"Ngành: {q['sector']}")
                        st.caption(f"Giá: **{q['price']:,.0f}**")
                    with qc2:
                        st.metric("🤖 AI T+3",    f"{q['ai']}%")
                        st.metric("📊 RSI",        f"{q['rsi']}")
                    with qc3:
                        st.metric("📈 RS Rating",  f"{q['rs']:.0f}")
                        st.metric("🌱 Tích Lũy",  f"{q['wave']}/11")
                    with qc4:
                        st.metric("🛡️ Stop Loss",  f"{q['sl']:,.0f}",
                                  delta=f"{q['sl_pct']:+.1f}%", delta_color="inverse")
                        st.metric("🎯 TP (R:R=2)", f"{q['tp2']:,.0f}",
                                  delta=f"{q['tp2_pct']:+.1f}%", delta_color="normal")
                    if q['wave_flags']:
                        st.caption("✅ " + " | ".join(q['wave_flags'][:3]))
        else:
            st.warning(f"Không tìm được mã nào đủ điều kiện AI ≥ {ai_min_qp}% hôm nay. Thử giảm ngưỡng.")
    st.divider()
    col_quick, col_full, col_fast = st.columns(3)
    run_quick = col_quick.button("⚡ Quét Nhanh (150 mã HOSE)")
    run_full  = col_full.button("🔭 Quét Toàn HOSE (~400 mã) — mất ~15 phút")
    run_fast  = col_fast.button("🏃 Điểm Danh Siêu Nhanh (không AI) — ~3 phút", key="auto_btn_i_m_Danh_Si_u_Nha_3")
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
                # [V39-M3] MA10 Booster info — thêm vào row Radar
                try:
                    _ma10_r = calc_ma10_bonus(df_s)
                    row['MA10 Bonus'] = _ma10_r.get('bonus', 0)
                    row['MA10 Signal'] = _ma10_r.get('signal_type')
                    row['MA10 Cross Up'] = bool(_ma10_r.get('is_cross_up', False))
                except Exception:
                    row['MA10 Bonus'] = 0
                    row['MA10 Signal'] = None
                    row['MA10 Cross Up'] = False

                # [V40-F4] Float info — thêm vào row Radar (chỉ hiển thị, không filter)
                try:
                    _float_r = get_float_data_cached(t, date_key[:10] if isinstance(date_key, str) else datetime.now(TZ_VN).strftime('%Y-%m-%d'))
                    if _float_r.get('available'):
                        _ff_r = _float_r['free_float_pct']
                        _fr_r = _float_r['foreigner_pct']
                        _ft_r = classify_float_tier(_ff_r, _fr_r)
                        row['Float Tier'] = _ft_r['tier']
                        row['Float Pct'] = _ff_r
                    else:
                        row['Float Tier'] = None
                        row['Float Pct'] = 0
                except Exception:
                    row['Float Tier'] = None
                    row['Float Pct'] = 0

                # [V41-R2] Rút Chân info — thêm vào row Radar
                try:
                    _rc_r = detect_rut_chan(df_s)
                    row['RC Signal'] = _rc_r.get('signal')
                    row['RC Quality'] = _rc_r.get('quality_score', 0)
                    row['RC Drop'] = _rc_r.get('drop_pct', 0)
                    row['RC Recovery'] = _rc_r.get('recovery_pct', 0)
                except Exception:
                    row['RC Signal'] = None
                    row['RC Quality'] = 0
                # [V24-LIQ+F2] Đẩy mã LIQ_LOW xuống Tầng 4 (Quan sát) — không push 2 lần
                try:
                    _liq_rd = calc_liquidity_tier_cached(t, date_key)
                    _is_low_liq = _liq_rd.get('tier') == 'LOW'
                except Exception:
                    _is_low_liq = False

                # [V24-W2] Filter RS Rating < 50 (yếu tương đối) ra khỏi Tầng 1/2/3
                _rs_val = row.get('RS Raw', 50)
                _is_weak_rs = (_rs_val is not None) and (_rs_val < 50)

                if _is_low_liq:
                    # Mã LIQ_LOW chỉ vào watch_zone (Tầng 4) — không phụ thuộc label
                    row['_liq_warning'] = '🔴 LIQ thấp'
                    watch_zone.append(row)
                elif _is_weak_rs and ("Bùng Nổ Mua" in label or "Sẵn Sàng" in label or "Tích Lũy" in label):
                    # [V24-W2] Mã yếu tương đối (RS < 50) đẩy xuống Quan Sát
                    row['_rs_warning'] = f'⚠️ RS yếu ({_rs_val:.0f})'
                    watch_zone.append(row)
                else:
                    # Phân loại bình thường theo label
                    if   "Bùng Nổ Mua" in label: breakouts.append(row)
                    elif "Bán Tháo"     in label: sell_dumps.append(row)
                    elif "Sẵn Sàng"     in label: watchlist.append(row)
                    elif "Tích Lũy"     in label: wave_bottom.append(row)
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
        st.write("### 🎯 Tầng 2 — Sẵn Sàng Bùng Nổ")
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
        st.write("### 🌱 Tầng 3 — Đang Tích Lũy Nền (Vào sớm)")
        # [V24-W1] Warning rõ về rủi ro Tầng 3
        with st.container(border=True):
            st.warning(
                "⚠️ **TẦNG NÀY RỦI RO CAO** — Vào SỚM trước khi mã xác nhận break.\n\n"
                "📌 **Quy tắc bắt buộc:**\n"
                "• Size nhỏ: chỉ 10–15% vốn cho 1 mã\n"
                "• SL CHẶT: -5% (không phải -7% như mã Tầng 2)\n"
                "• Kiên nhẫn: có thể đợi **2–4 tuần** mới có kết quả\n"
                "• Chỉ vào nếu RS Rating ≥ 50 (tránh mã yếu tương đối)"
            )
        st.caption("Đang tích lũy nền. Vào nhỏ 10–15% vốn, SL chặt theo ATR.")
        if wave_bottom:
            if use_cards:
                for r in wave_bottom: render_radar_card(r, "blue")
            else:
                render_radar_table(wave_bottom)
            st.info(f"🌱 {len(wave_bottom)} mã đang tích lũy nền. Chờ thêm 1–2 phiên xác nhận trước khi vào.")
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
| 🎯 Sẵn Sàng Bùng Nổ | Đã sẵn sàng — có thể nổ bất kỳ phiên nào | Ưu tiên vào lệnh |
| 🌱 Đang Tích Lũy Nền | Đang tích lũy nền /12 tiêu chí | Vào sớm size nhỏ, SL chặt |
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
# [V37] TAB EARLY MOMENTUM — Phát hiện sớm mã trong chuỗi tăng
# ==============================================================================
with tab_momentum:
    st.subheader("🔥 Early Momentum Scanner")
    st.info(
        "📌 Quét các mã đang trong **chuỗi tăng liên tiếp N ngày** — phát hiện sớm "
        "khi mới ở ngày 2-3 để có thể vào lệnh kịp thời."
    )
    st.warning(
        "⚠️ **DISCLAIMER QUAN TRỌNG:** "
        "Mã trong chuỗi tăng KHÔNG có nghĩa 'nên mua ngay'.\\n"
        "• Chỉ ~50% mã tăng 2 ngày sẽ tiếp tục tăng ngày 3\\n"
        "• Phải vào Tab 🤖 Robot Advisor phân tích SÂU trước khi vào lệnh\\n"
        "• Coi đây là **danh sách CANDIDATE để xem xét**, không phải khuyến nghị mua"
    )

    # ── BỘ ĐIỀU KHIỂN ──
    with st.container(border=True):
        em_c1, em_c2, em_c3 = st.columns(3)

        em_streak = em_c1.slider(
            "📅 Số ngày tăng tối thiểu:",
            min_value=2, max_value=5, value=2, step=1,
            key="em_streak"
        )

        em_min_gain = em_c2.slider(
            "📈 % tăng tối thiểu/ngày:",
            min_value=0.0, max_value=3.0, value=0.5, step=0.1,
            key="em_min_gain"
        )

        em_universe = em_c3.radio(
            "🎯 Phạm vi quét:",
            ['Toàn HOSE (~400 mã, 1-2 phút)',
             'Watchlist của tôi',
             'PILLARS top 30'],
            key="em_universe"
        )

        em_f_c1, em_f_c2, em_f_c3 = st.columns(3)
        em_filter_rsi = em_f_c1.checkbox(
            "Chỉ mã RSI < 75 (chưa quá mua)",
            value=True, key="em_filter_rsi"
        )
        em_filter_liq = em_f_c2.checkbox(
            "Loại mã LIQ_LOW (penny)",
            value=True, key="em_filter_liq"
        )
        em_filter_ma10 = em_f_c3.checkbox(
            "⭐ Chỉ mã CẮT LÊN MA10 (V39)",
            value=False, key="em_filter_ma10",
            help="Chỉ giữ mã vừa cắt lên vạch vàng MA10 trong 3 phiên gần nhất"
        )
        # [V41-R3] Thêm checkbox filter Rút Chân
        em_filter_rc = st.checkbox(
            "🦵 Chỉ mã có RÚT CHÂN hôm nay (V41) — phiên giảm sâu rồi hồi mạnh",
            value=False, key="em_filter_rc",
            help="Chỉ giữ mã có signal Rút Chân STRONG/GOOD/MILD trong phiên gần nhất"
        )

    # ── NÚT QUÉT ──
    if st.button("🔍 Quét Early Momentum", type="primary", key="em_scan_btn"):
        # Xác định universe
        if 'Toàn HOSE' in em_universe:
            try:
                universe_em = list(tickers)
            except Exception:
                universe_em = list(PILLARS)
        elif 'PILLARS' in em_universe:
            universe_em = list(PILLARS[:30])
        else:
            universe_em = st.session_state.get('watchlist', PILLARS[:10])
            universe_em = list(universe_em) if universe_em else list(PILLARS[:10])

        with st.spinner(f"Đang quét {len(universe_em)} mã..."):
            em_result = scan_early_momentum(
                json.dumps(universe_em),
                int(em_streak),
                float(em_min_gain),
                bool(em_filter_rsi),
                bool(em_filter_liq),
                datetime.now(TZ_VN).strftime('%Y-%m-%d-%H'),
                filter_ma10_cross=bool(em_filter_ma10),
                filter_rut_chan=bool(em_filter_rc),
            )
            st.session_state['_v37_em_result'] = em_result

    # ── KẾT QUẢ ──
    em_result = st.session_state.get('_v37_em_result')
    if em_result:
        n_day2 = len(em_result['day2'])
        n_day3 = len(em_result['day3'])
        n_day4 = len(em_result['day4_plus'])
        n_total = n_day2 + n_day3 + n_day4

        st.markdown(f"### 📊 Tìm thấy **{n_total}** mã (quét {em_result['n_scanned']} mã)")

        if n_total == 0:
            st.warning(
                f"Không có mã nào đạt tiêu chí ≥ {em_streak} ngày tăng "
                f"({em_min_gain}%/ngày). Thử giảm tiêu chí hoặc đổi phạm vi quét."
            )

        # Ngày 2 — Vào lệnh sớm nhất
        if n_day2 > 0:
            st.markdown(f"#### 🌱 NGÀY 2 — Vào lệnh sớm ({n_day2} mã)")
            st.caption(
                "Mã mới tăng 2 ngày — Vào sớm có rủi ro cao nhưng tiềm năng lời lớn nếu trend tiếp tục. "
                "Size nhỏ + SL chặt -3%."
            )
            for r in em_result['day2']:
                render_momentum_card(r, 'green')

        # Ngày 3 — Đã xác nhận
        if n_day3 > 0:
            st.markdown(f"#### 🌿 NGÀY 3 — Đã xác nhận xu hướng ({n_day3} mã)")
            st.caption(
                "Mã đã tăng 3 ngày — Trend đã rõ hơn, độ tin cậy cao hơn ngày 2. "
                "Size vừa + SL -5%."
            )
            for r in em_result['day3']:
                render_momentum_card(r, 'blue')

        # Ngày 4+ — Đã chạy lâu, cẩn thận đỉnh
        if n_day4 > 0:
            st.markdown(f"#### 🔥 NGÀY 4+ — Đã chạy lâu, CẨN THẬN ({n_day4} mã)")
            st.caption(
                "⚠️ Mã đã tăng ≥ 4 ngày — Rủi ro đảo chiều CAO. "
                "Nếu vào, ưu tiên trailing stop chặt. Hoặc chờ pullback."
            )
            for r in em_result['day4_plus']:
                render_momentum_card(r, 'orange')

        # Errors
        if em_result.get('errors'):
            with st.expander(f"⚠️ {len(em_result['errors'])} mã không quét được"):
                for e in em_result['errors'][:20]:
                    st.caption(f"• {e['ticker']}: {e['error']}")

        st.caption(f"Cache 10 phút | Quét lúc: {em_result.get('scan_date', '')}")
    else:
        st.caption("👆 Cấu hình rồi nhấn 'Quét Early Momentum' để bắt đầu")

# ==============================================================================
# TAB 5: SECTOR ROTATION
# ==============================================================================
with tab5:
    st.subheader("🏭 Sector Rotation — Bản Đồ Dòng Tiền Luân Chuyển Ngành")

    # [V36-N4] SECTOR STRENGTH MATRIX (4 timeframes)
    with st.container(border=True):
        st.markdown("### 🌡️ Ma trận Sức mạnh Ngành (4 khung thời gian)")
        st.caption("Xếp hạng 15 ngành theo TB return 1d, 5d, 20d, 60d. Cache 15 phút.")
        if st.button("📊 Quét Sector Strength", key="v36_n4_btn"):
            with st.spinner("Đang quét 15 ngành (~1-2 phút)..."):
                _date_key_n4 = datetime.now(TZ_VN).strftime('%Y-%m-%d-%H')
                ssm = calc_sector_strength_matrix(_date_key_n4)
                st.session_state['_v36_ssm'] = ssm
        ssm = st.session_state.get('_v36_ssm')
        if ssm:
            if 'message' in ssm:
                st.warning(ssm['message'])
            elif ssm.get('rows'):
                # Render DataFrame
                df_ssm = pd.DataFrame(ssm['rows'])
                df_show = df_ssm[['sector', 'n_stocks', 'ret_1d', 'ret_5d', 'ret_20d', 'ret_60d']]
                df_show.columns = ['Ngành', '# mã', '1 ngày %', '5 ngày %', '20 ngày %', '60 ngày %']

                # Style: gradient màu theo return
                def color_ret(val):
                    if val > 2:
                        return 'background-color: #16a34a; color: white;'  # đậm xanh
                    elif val > 0.5:
                        return 'background-color: #86efac;'  # xanh nhạt
                    elif val < -2:
                        return 'background-color: #dc2626; color: white;'  # đậm đỏ
                    elif val < -0.5:
                        return 'background-color: #fca5a5;'  # đỏ nhạt
                    return ''

                try:
                    styled = df_show.style.map(
                        color_ret, subset=['1 ngày %', '5 ngày %', '20 ngày %', '60 ngày %']
                    ).format({'1 ngày %': '{:+.2f}', '5 ngày %': '{:+.2f}',
                                '20 ngày %': '{:+.2f}', '60 ngày %': '{:+.2f}'})
                    st.dataframe(styled, use_container_width=True, hide_index=True)
                except Exception:
                    st.dataframe(df_show, use_container_width=True, hide_index=True)

                # Highlight leaders & laggards
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.markdown("**🏆 Top 3 ngành LEADING:**")
                    for l in ssm.get('leaders', []):
                        st.success(f"• {l['sector']}: +{l['ret_5d']:.2f}% (5d)")
                with sc2:
                    st.markdown("**📉 Top 3 ngành LAGGING:**")
                    for l in ssm.get('laggards', []):
                        st.error(f"• {l['sector']}: {l['ret_5d']:+.2f}% (5d)")

    st.markdown("---")
    st.write(
        "Phát hiện dòng tiền đang **chảy vào ngành nào** dựa trên "
        "hiệu suất trung bình 5 ngày của các mã đại diện trong mỗi ngành."
    )
    st.warning("⏱️ Quét ngành mất 2-3 phút. Chạy 1 lần/ngày là đủ.")
    if st.button("🔭 QUÉT DÒNG TIỀN LUÂN CHUYỂN NGÀNH", key="auto_btn_QU_T_D_NG_TI_N_LU_4"):
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
    # ── [V24-M4] SECTOR MONEY FLOW MAP ──
    st.divider()
    st.write("### 🌊 Sector Money Flow Map [V24]")
    st.caption("Bản đồ dòng tiền các ngành: % mã trên MA20, RSI TB, return TB hôm nay.")
    if st.button("🔄 Refresh Money Flow", key="mf_refresh_btn"):
        st.session_state.pop('_mf_cache', None)
    if '_mf_cache' not in st.session_state:
        with st.spinner("Đang quét dòng tiền các ngành..."):
            try:
                # Lấy ticker mỗi ngành từ SECTOR_MAP (đã có trong V23)
                tickers_by_sec = {}
                for tk, sec in SECTOR_MAP.items():
                    if sec not in tickers_by_sec:
                        tickers_by_sec[sec] = []
                    tickers_by_sec[sec].append(tk)
                mf_data = calc_sector_money_flow(tickers_by_sec, max_per_sector=6)
                st.session_state['_mf_cache'] = mf_data
            except Exception as _mf_err:
                st.warning(f"Không tính được: {_mf_err}")
                st.session_state['_mf_cache'] = []

    mf_data = st.session_state.get('_mf_cache', [])
    if mf_data:
        df_mf = pd.DataFrame(mf_data)
        # Format
        df_mf_display = df_mf[['sector', 'pct_above_ma20', 'rsi_avg',
                                  'vol_avg', 'ret_avg_pct', 'heat', 'n_sample']].copy()
        df_mf_display.columns = ['Ngành', '% > MA20', 'RSI TB',
                                    'Vol TB (x)', 'Return TB %', 'Heat Score', 'Sample']
        st.dataframe(df_mf_display, use_container_width=True, hide_index=True)
        # Top 3 hottest
        if len(mf_data) >= 3:
            st.success(f"🔥 **3 ngành nóng nhất:** "
                        f"{mf_data[0]['sector']}, {mf_data[1]['sector']}, {mf_data[2]['sector']}")
        # Coldest
        if len(mf_data) >= 2:
            coldest = mf_data[-1]
            st.warning(f"❄️ **Ngành yếu nhất:** {coldest['sector']} "
                        f"({coldest['pct_above_ma20']:.0f}% trên MA20)")

with tab6:
    st.subheader(f"📊 Phân Tích VN-Index & Tương Quan với {ticker}")
    if st.button("🔄 Xóa Cache VNI (bấm nếu lần trước lỗi)", key="auto_btn_X_a_Cache_VNI__b_m_5"):
        get_vnindex_cached.clear()
        st.session_state.pop('vni_loaded', None)
        st.success("✅ Cache VNI đã xóa — bấm 'Tải Dữ Liệu' để tải lại.")
    if st.button("🔄 Tải Dữ Liệu VN-Index & Phân Tích", key="auto_btn_T_i_D__Li_u_VN_Ind_6"):
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

        # ═══════════════════════════════════════════════════════════════
        # [V34] VN-INDEX DECISION HELPER — Combo B (D1+D2+B1+B4+B5+C1)
        # ═══════════════════════════════════════════════════════════════
        st.markdown("---")
        st.markdown("## 🚦 NÊN MUA / ĐỨNG NGOÀI?")
        st.caption("⚠️ Đây là REFERENCE, không phải khuyến nghị. Bạn tự chịu trách nhiệm quyết định.")

        # ── D1+D2: Verdict Box + Checklist ──
        try:
            _date_key = datetime.now(TZ_VN).strftime('%Y-%m-%d-%H')
            v34_decision = calc_vni_decision_score(df_vni)

            if v34_decision.get('score') is not None:
                # Big verdict box
                with st.container(border=True):
                    vc1, vc2 = st.columns([2, 3])
                    with vc1:
                        if v34_decision['color'] == 'green':
                            st.success(f"# {v34_decision['verdict']}")
                        elif v34_decision['color'] == 'orange':
                            st.warning(f"# {v34_decision['verdict']}")
                        else:
                            st.error(f"# {v34_decision['verdict']}")
                        st.metric("Điểm tổng", f"{v34_decision['score']}/100")
                        st.caption(f"Đạt {v34_decision['n_passed']}/{v34_decision['n_total']} tiêu chí")
                    with vc2:
                        st.markdown(f"### 💡 Lý do")
                        st.info(v34_decision['verdict_msg'])

                # D2: Checklist 10 dấu hiệu
                with st.expander("📋 Chi tiết 10 dấu hiệu (D2)", expanded=False):
                    st.caption("Mỗi dấu hiệu có trọng số khác nhau, ✅ pass = cộng điểm, ❌ fail = 0 điểm")
                    for c in v34_decision['checks']:
                        emoji = '✅' if c['pass'] else '❌'
                        st.markdown(f"{emoji} **{c['name']}** _(trọng số: {c['weight']})_")
            else:
                st.info(v34_decision.get('message', 'Không tính được verdict'))
        except Exception as _d1_err:
            st.warning(f"Lỗi D1: {_d1_err}")

        # ── B4: Fear & Greed Index ──
        try:
            fgi = calc_fear_greed_index(df_vni)
            with st.container(border=True):
                fg_c1, fg_c2 = st.columns([1, 2])
                with fg_c1:
                    st.markdown("### 😰 Fear & Greed")
                    st.metric("Index", f"{fgi['index']}/100")
                    if fgi['color'] == 'green':
                        st.success(fgi['label'])
                    elif fgi['color'] == 'blue':
                        st.info(fgi['label'])
                    elif fgi['color'] == 'yellow':
                        st.warning(fgi['label'])
                    elif fgi['color'] == 'orange':
                        st.warning(fgi['label'])
                    elif fgi['color'] == 'red':
                        st.error(fgi['label'])
                with fg_c2:
                    st.markdown("### 💡 Lời khuyên")
                    st.info(fgi.get('advice', ''))
                    # Components
                    comp = fgi.get('components', {})
                    if comp:
                        with st.expander("🔬 4 thành phần"):
                            st.write(f"• **RSI** (30%): {comp.get('rsi', 0)}")
                            st.write(f"• **Volatility** (20%): {comp.get('volatility', 0)}")
                            st.write(f"• **Momentum** (30%): {comp.get('momentum', 0)}")
                            st.write(f"• **BB Position** (20%): {comp.get('bb_position', 0)}")
        except Exception as _fg_err:
            st.warning(f"Lỗi F&G: {_fg_err}")

        # ── B1: Market Breadth Dashboard ──
        try:
            with st.container(border=True):
                st.markdown("### 📊 Market Breadth — Sức rộng thị trường")
                if st.button("🔍 Quét Breadth", key="v34_breadth_btn"):
                    with st.spinner("Đang quét 50 mã đại diện..."):
                        _bd_tickers = list(PILLARS) + ['ACB', 'BID', 'CTG', 'STB', 'TPB',
                                                          'NVL', 'PDR', 'KDH', 'DXG', 'KBC',
                                                          'GVR', 'PLX', 'POW', 'MSN', 'SAB']
                        bd = calc_market_breadth_dashboard(
                            json.dumps(_bd_tickers),
                            _date_key
                        )
                        st.session_state['_v34_bd'] = bd

                bd = st.session_state.get('_v34_bd')
                if bd and 'total' in bd:
                    bd_c1, bd_c2, bd_c3 = st.columns(3)
                    bd_c1.metric("🟢 Tăng / 🔴 Giảm",
                                  f"{bd['up_count']}/{bd['down_count']}",
                                  delta=f"A/D = {bd['ad_ratio']}")
                    bd_c2.metric("📈 Trên MA20",
                                  f"{bd['pct_above_ma20']}%",
                                  delta="Mạnh" if bd['pct_above_ma20'] > 60 else ("Yếu" if bd['pct_above_ma20'] < 40 else "Trung bình"))
                    bd_c3.metric("📈 Trên MA50",
                                  f"{bd['pct_above_ma50']}%",
                                  delta="Mạnh" if bd['pct_above_ma50'] > 60 else ("Yếu" if bd['pct_above_ma50'] < 40 else "Trung bình"))
                    if bd['ad_ratio'] >= 1.5:
                        st.success(f"💪 A/D = {bd['ad_ratio']} > 1.5 → Thị trường có sức rộng tăng tốt")
                    elif bd['ad_ratio'] <= 0.7:
                        st.error(f"⚠️ A/D = {bd['ad_ratio']} < 0.7 → Phần lớn mã đang giảm")
                    else:
                        st.info(f"A/D = {bd['ad_ratio']} → Thị trường cân bằng")
                elif bd:
                    st.info(bd.get('message', ''))
                else:
                    st.caption("Nhấn 'Quét Breadth' để xem")
        except Exception as _bd_err:
            st.warning(f"Lỗi Breadth: {_bd_err}")

        # ── B5: Kháng cự / Hỗ trợ VN-Index ──
        try:
            sr = calc_vni_support_resistance(df_vni)
            with st.container(border=True):
                st.markdown("### 🎯 Kháng cự / Hỗ trợ VN-Index")
                if 'message' in sr:
                    st.info(sr['message'])
                else:
                    sr_c1, sr_c2, sr_c3 = st.columns(3)
                    sr_c1.metric("Giá hiện tại", f"{sr['cur_price']:,.0f}")
                    if sr.get('nearest_resistance'):
                        sr_c2.metric("🔴 Kháng cự gần nhất",
                                       f"{sr['nearest_resistance']:,.0f}",
                                       delta=f"+{sr.get('dist_to_resistance', 0):.2f}%",
                                       delta_color="off")
                    if sr.get('nearest_support'):
                        sr_c3.metric("🟢 Hỗ trợ gần nhất",
                                       f"{sr['nearest_support']:,.0f}",
                                       delta=f"-{sr.get('dist_to_support', 0):.2f}%",
                                       delta_color="off")
                    # BB
                    if sr.get('bb_upper'):
                        st.caption(f"📊 BB Upper: {sr['bb_upper']:,.0f} | BB Lower: {sr.get('bb_lower', 0):,.0f}")
                    # Warnings
                    if sr.get('warnings'):
                        for w in sr['warnings']:
                            st.warning(w)
                    else:
                        st.success("✅ Không có cảnh báo kháng cự/hỗ trợ gần")
        except Exception as _sr_err:
            st.warning(f"Lỗi S/R: {_sr_err}")

        # ── C1: Cảnh báo phân kỳ VN-Index ──
        try:
            div = detect_vni_divergence(df_vni)
            with st.container(border=True):
                st.markdown("### 🔀 Cảnh báo Phân Kỳ VN-Index")
                if div.get('divergence') == 'BEARISH':
                    st.error(div['message'])
                elif div.get('divergence') == 'BULLISH':
                    st.success(div['message'])
                else:
                    st.info(div.get('message', 'Không phát hiện phân kỳ'))
        except Exception as _div_err:
            st.warning(f"Lỗi phân kỳ: {_div_err}")

        st.markdown("---")
        st.caption("⚠️ **Disclaimer:** Các chỉ báo trên là phân tích kỹ thuật REFERENCE, KHÔNG phải khuyến nghị mua/bán. Quyết định và rủi ro thuộc về bạn.")
        # [V34 END]

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
            # [V27-FIX] Đảm bảo cột date tồn tại TRƯỚC khi truy cập columns
            df_vni_safe = ensure_date_col(df_vni)
            df_stk_safe = ensure_date_col(df_stk)
            # Kiểm tra columns cần thiết
            req_cols = ['date', 'close', 'return_1d']
            missing_vni = [c for c in req_cols if c not in df_vni_safe.columns]
            missing_stk = [c for c in req_cols if c not in df_stk_safe.columns]
            if missing_vni or missing_stk:
                st.warning(f"⚠️ Dữ liệu thiếu cột: VNI={missing_vni}, {ticker}={missing_stk}")
                df_merged = pd.DataFrame()
            else:
                # Ghép 2 df theo ngày
                df_vni_r = df_vni_safe[['date','close','return_1d']].copy().rename(
                    columns={'close':'close_vni','return_1d':'ret_vni'})
                df_stk_r = df_stk_safe[['date','close','return_1d']].copy().rename(
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
                xv = get_date_col(chart_vni)
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

# ==============================================================================
# [V24-Q4] TAB COMPARE — So sánh 2 mã side-by-side
# ==============================================================================
with tab_compare:
    st.write("### 🆚 So sánh 2 mã cùng lúc")
    st.caption("Phân tích nhanh 2 mã để chọn mã tốt hơn vào lệnh.")

    cmp_c1, cmp_c2 = st.columns(2)
    cmp_t1 = cmp_c1.text_input("Mã 1", value="FPT", max_chars=4, key="cmp_t1").upper()
    cmp_t2 = cmp_c2.text_input("Mã 2", value="HPG", max_chars=4, key="cmp_t2").upper()

    if st.button("🚀 So sánh", key="cmp_btn"):
        if cmp_t1 and cmp_t2 and cmp_t1 != cmp_t2:
            with st.spinner(f"Đang phân tích {cmp_t1} vs {cmp_t2}..."):
                try:
                    df1 = get_price(cmp_t1)
                    df2 = get_price(cmp_t2)
                    if not valid(df1) or not valid(df2):
                        st.error("Không tải được dữ liệu cho 1 trong 2 mã")
                    else:
                        df1 = calc_indicators(df1)
                        df2 = calc_indicators(df2)
                        l1 = df1.iloc[-1]
                        l2 = df2.iloc[-1]
                        # AI
                        date_key = datetime.now(TZ_VN).strftime('%Y-%m-%d')
                        try:
                            ai1 = predict_ai_cached(cmp_t1, float(l1['close']))
                            ai2 = predict_ai_cached(cmp_t2, float(l2['close']))
                        except Exception:
                            ai1, ai2 = "N/A", "N/A"
                        # Backtest nhanh
                        bt1 = run_backtest(df1)
                        bt2 = run_backtest(df2)
                        # Wave bottom
                        w1 = calc_wave_bottom_score(df1, l1)
                        w2 = calc_wave_bottom_score(df2, l2)
                        # Weekly
                        wk1 = get_weekly_trend(df1)
                        wk2 = get_weekly_trend(df2)

                        st.session_state['_cmp_results'] = {
                            't1': cmp_t1, 'l1': l1, 'ai1': ai1, 'bt1': bt1, 'w1': w1, 'wk1': wk1,
                            't2': cmp_t2, 'l2': l2, 'ai2': ai2, 'bt2': bt2, 'w2': w2, 'wk2': wk2,
                        }
                except Exception as _cmp_err:
                    st.error(f"Lỗi: {_cmp_err}")
        else:
            st.warning("Nhập 2 mã KHÁC nhau")

    cmp_res = st.session_state.get('_cmp_results')
    if cmp_res:
        t1, t2 = cmp_res['t1'], cmp_res['t2']
        l1, l2 = cmp_res['l1'], cmp_res['l2']

        # Bảng so sánh
        st.markdown(f"### {t1} vs {t2}")
        comparison_rows = [
            ['Chỉ số', t1, t2, 'Mã tốt hơn'],
            ['💰 Giá', f"{float(l1['close']):,.0f}", f"{float(l2['close']):,.0f}", '—'],
            ['📊 RSI',
                f"{float(l1['rsi']):.1f}",
                f"{float(l2['rsi']):.1f}",
                t1 if 40 <= l1['rsi'] <= 65 else (t2 if 40 <= l2['rsi'] <= 65 else '—')],
            ['📈 MACD',
                '✅' if l1['macd'] > l1['signal'] else '❌',
                '✅' if l2['macd'] > l2['signal'] else '❌',
                t1 if (l1['macd'] > l1['signal']) and not (l2['macd'] > l2['signal']) else
                (t2 if (l2['macd'] > l2['signal']) and not (l1['macd'] > l1['signal']) else '=')],
            ['📐 ADX',
                f"{float(l1.get('adx', 0)):.1f}",
                f"{float(l2.get('adx', 0)):.1f}",
                t1 if l1.get('adx', 0) > l2.get('adx', 0) else t2],
            ['⚡ Vol strength',
                f"{float(l1['vol_strength']):.2f}x",
                f"{float(l2['vol_strength']):.2f}x",
                t1 if l1['vol_strength'] > l2['vol_strength'] else t2],
            ['🤖 AI T+3',
                f"{cmp_res['ai1']:.1f}%" if _is_valid_score(cmp_res['ai1']) else "N/A",
                f"{cmp_res['ai2']:.1f}%" if _is_valid_score(cmp_res['ai2']) else "N/A",
                t1 if (_is_valid_score(cmp_res['ai1']) and _is_valid_score(cmp_res['ai2']) and
                       float(cmp_res['ai1']) > float(cmp_res['ai2'])) else
                (t2 if (_is_valid_score(cmp_res['ai1']) and _is_valid_score(cmp_res['ai2'])) else '?')],
            ['🌊 Chân sóng',
                f"{cmp_res['w1']['score']}/{cmp_res['w1'].get('total', 11)}",
                f"{cmp_res['w2']['score']}/{cmp_res['w2'].get('total', 11)}",
                t1 if cmp_res['w1']['score'] > cmp_res['w2']['score'] else
                (t2 if cmp_res['w2']['score'] > cmp_res['w1']['score'] else '=')],
            ['📅 Weekly',
                cmp_res['wk1'], cmp_res['wk2'],
                t1 if cmp_res['wk1'] == 'UP' and cmp_res['wk2'] != 'UP' else
                (t2 if cmp_res['wk2'] == 'UP' and cmp_res['wk1'] != 'UP' else '=')],
            ['📊 BT Winrate',
                f"{cmp_res['bt1']['winrate']:.1f}%",
                f"{cmp_res['bt2']['winrate']:.1f}%",
                t1 if cmp_res['bt1']['winrate'] > cmp_res['bt2']['winrate'] else t2],
            ['📈 BT Sharpe',
                f"{cmp_res['bt1']['sharpe']:.2f}",
                f"{cmp_res['bt2']['sharpe']:.2f}",
                t1 if cmp_res['bt1']['sharpe'] > cmp_res['bt2']['sharpe'] else t2],
            ['📉 BT Max DD',
                f"{cmp_res['bt1']['max_drawdown']:.1f}%",
                f"{cmp_res['bt2']['max_drawdown']:.1f}%",
                t1 if cmp_res['bt1']['max_drawdown'] > cmp_res['bt2']['max_drawdown'] else t2],
        ]
        df_cmp = pd.DataFrame(comparison_rows[1:], columns=comparison_rows[0])
        st.dataframe(df_cmp, use_container_width=True, hide_index=True)

        # Đếm winner
        winner_count = {t1: 0, t2: 0}
        for row in comparison_rows[1:]:
            if row[3] == t1: winner_count[t1] += 1
            elif row[3] == t2: winner_count[t2] += 1
        st.divider()
        cv1, cv2, cv3 = st.columns(3)
        cv1.metric(f"🏆 {t1} thắng", winner_count[t1])
        cv2.metric(f"🏆 {t2} thắng", winner_count[t2])
        if winner_count[t1] > winner_count[t2]:
            cv3.success(f"🥇 **{t1}** tốt hơn ({winner_count[t1]} vs {winner_count[t2]})")
        elif winner_count[t2] > winner_count[t1]:
            cv3.success(f"🥇 **{t2}** tốt hơn ({winner_count[t2]} vs {winner_count[t1]})")
        else:
            cv3.info("⚖️ Cân bằng")

        # Vẽ giá overlay 60 phiên gần nhất
        try:
            df1_recent = df1.tail(60).reset_index(drop=True) if (df1 := get_price(t1)) is not None else None
            df2_recent = df2.tail(60).reset_index(drop=True) if (df2 := get_price(t2)) is not None else None
            if df1_recent is not None and df2_recent is not None:
                # Normalize về 100
                n1 = df1_recent['close'] / df1_recent['close'].iloc[0] * 100
                n2 = df2_recent['close'] / df2_recent['close'].iloc[0] * 100
                fig_cmp = go.Figure()
                fig_cmp.add_trace(go.Scatter(y=n1, name=t1, line=dict(color='blue', width=2)))
                fig_cmp.add_trace(go.Scatter(y=n2, name=t2, line=dict(color='orange', width=2)))
                fig_cmp.update_layout(title="So sánh % thay đổi giá 60 phiên (cơ sở 100)",
                                        height=350,
                                        yaxis_title="Cơ sở 100",
                                        xaxis_title="Phiên")
                st.plotly_chart(fig_cmp, use_container_width=True)
        except Exception:
            pass
