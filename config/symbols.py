# Institutional NSE Universe
# In production, this can fetch from:
# https://archives.nseindia.com/content/indices/ind_nifty50list.csv

NIFTY_50 = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "LICI", "ITC", "HINDUNILVR",
    "LT", "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA", "ADANIENT", "KOTAKBANK", "TITAN", "ONGC", "TATAMOTORS",
    "NTPC", "AXISBANK", "ADANIPORTS", "ULTRACEMCO", "ASIANPAINT", "COALINDIA", "POWERGRID", "TATASTEEL", "M&M", "JSWSTEEL",
    "BAJAJFINSV", "GRASIM", "NESTLEIND", "TECHM", "HINDALCO", "SBILIFE", "BRITANNIA", "CIPLA", "INDUSINDBK", "EICHERMOT",
    "ADANIPOWER", "TATACONSUM", "DIVISLAB", "DRREDDY", "BPCL", "BAJAJ-AUTO", "SHRIRAMFIN", "HEROMOTOCO", "APOLLOHOSP", "BEL"
]

# For a full scan of 2500 stocks, we would fetch the master list.
def get_universe():
    return NIFTY_50 # Defaulting to Nifty 50 for speed and quality
