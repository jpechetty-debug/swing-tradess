import os

# ── Data ────────────────────────────────────────────────────────────────────
PERIOD          = "6mo"          # yfinance lookback  (6 months = ~130 candles)
INTERVAL        = "1d"           # daily candles
MAX_WORKERS     = 10             # concurrent download threads
BATCH_SIZE      = 50             # symbols per yfinance batch-download call
NS_SUFFIX       = ".NS"          # NSE ticker suffix for yfinance

# ── Market Structure ─────────────────────────────────────────────────────────
SWING_WINDOW    = 2              # bars each side to confirm swing high/low
MIN_SWING_BARS  = 10             # min history before declaring a trend
TREND_LOOKBACK  = 4              # last N swing points used for trend snapshot

# ── Support & Resistance ─────────────────────────────────────────────────────
SR_TOUCH_MIN    = 2              # minimum touches for a valid zone
SR_ATR_MULT     = 0.5            # zone width = SR_ATR_MULT × ATR(14)
SR_WINDOW_DAYS  = 120            # candles to search for S&R levels
SR_MAX_LEVELS   = 5              # max S&R levels returned per side

# ── Candlestick ──────────────────────────────────────────────────────────────
MARUBOZU_BODY   = 0.90           # body / range ≥ this → Marubozu
HAMMER_WICK     = 2.0            # lower wick ≥ 2× body → Hammer
DOJI_BODY       = 0.10           # body / range ≤ this → Doji
ENGULF_MULT     = 1.05           # engulfing body must be 5% bigger than prev

# ── Risk Management ──────────────────────────────────────────────────────────
DEFAULT_CAPITAL = 500_000        # ₹5 lakh default trading capital
RISK_PCT        = 0.01           # 1% risk per trade
MIN_RR_T1       = 1.5            # minimum RR to first target (T1)
GOOD_RR_T1      = 2.0            # "Good" threshold
EXCEL_RR_T1     = 3.0            # "Excellent" threshold
STOP_BUFFER_ATR = 0.3            # stop = swing_low – 0.3×ATR

# ── Scorecard Gates ──────────────────────────────────────────────────────────
STRONG_SCORE    = 6              # ≥ 6 → Strong Bullish Setup
SKIP_SCORE      = 4              # < 4 → Skip
GATES_REQUIRED  = 3              # min gates (Trend/Support/Candle/RR) for entry

# ── Screening Filters ────────────────────────────────────────────────────────
MIN_BETA        = 1.0            # minimum beta (relative to Nifty)
MIN_AVG_VOL     = 300_000        # minimum 20-day avg volume
MIN_PRICE       = 20.0           # paise filter – avoid penny stocks
MIN_CANDLES     = 60             # skip if fewer history candles available

import os

# Scan Parameters
SCAN_PERIOD = "1y"
LOOKBACK_PERIOD = 2
ZIGZAG_DEPTH = 20
ZIGZAG_DEVIATION = 0.05

# Risk Parameters
CAPITAL_RISK_PERCENT = 0.01
MIN_RR_RATIO = 1.5

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
