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
