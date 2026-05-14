import yfinance as yf
import pandas as pd
import os
from config.settings import DATA_DIR, SCAN_PERIOD

def fetch_stock_data(symbol: str, period: str = SCAN_PERIOD) -> pd.DataFrame:
    """
    Fetches historical daily data for a given NSE symbol.
    Appends .NS if not present.
    """
    if not symbol.endswith(".NS"):
        yf_symbol = f"{symbol}.NS"
    else:
        yf_symbol = symbol
        
    print(f"Fetching data for {yf_symbol}...")
    try:
        df = yf.download(yf_symbol, period=period, interval="1d", progress=False)
        if df.empty:
            print(f"Warning: No data found for {yf_symbol}")
            return pd.DataFrame()
            
        # Clean columns if multi-index (sometimes happens with yfinance)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        print(f"Error fetching {yf_symbol}: {e}")
        return pd.DataFrame()

def save_to_local(df: pd.DataFrame, symbol: str):
    """
    Saves dataframe to local parquet for faster access.
    """
    if df.empty:
        return
    
    filename = os.path.join(DATA_DIR, f"{symbol}.parquet")
    df.to_parquet(filename)
    print(f"Saved {symbol} data to {filename}")

def load_from_local(symbol: str) -> pd.DataFrame:
    """
    Loads data from local parquet.
    """
    filename = os.path.join(DATA_DIR, f"{symbol}.parquet")
    if os.path.exists(filename):
        return pd.read_parquet(filename)
    return pd.DataFrame()
