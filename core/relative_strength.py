import pandas as pd
import threading
from data.downloader import fetch_stock_data

_INDEX_CACHE = {}
_CACHE_LOCK = threading.Lock()

def calculate_relative_strength(stock_df: pd.DataFrame, index_symbol: str = "^NSEI", window: int = 60):
    """
    Calculates Relative Strength of the stock compared to an index (default: Nifty 50).
    """
    if len(stock_df) < window:
        return 0.0
        
    with _CACHE_LOCK:
        if index_symbol not in _INDEX_CACHE:
            print(f"Fetching reference index {index_symbol}...")
            _INDEX_CACHE[index_symbol] = fetch_stock_data(index_symbol)
            
        index_df = _INDEX_CACHE[index_symbol]
    if index_df.empty:
        return 0.0
        
    # Align dates
    combined = pd.DataFrame({
        "stock": stock_df['Close'],
        "index": index_df['Close']
    }).dropna()
    
    if combined.empty:
        return 0.0
        
    combined['RS'] = combined['stock'] / combined['index']
    
    # RS Change over window
    rs_start = combined['RS'].iloc[-window]
    rs_end = combined['RS'].iloc[-1]
    
    rs_momentum = (rs_end / rs_start) - 1
    
    return float(rs_momentum * 100) # Returns percentage RS momentum


def compute_beta(df: pd.DataFrame, index_df: pd.DataFrame) -> float:
    """
    Computes 6-month beta of stock vs index.
    """
    try:
        stock_ret = df["Close"].pct_change().dropna()
        index_ret = index_df["Close"].pct_change().dropna()
        aligned   = pd.concat([stock_ret, index_ret], axis=1).dropna()
        aligned.columns = ["stock", "index"]
        if len(aligned) < 30:
            return 0.0
        cov = aligned.cov().iloc[0, 1]
        var = aligned["index"].var()
        return float(cov / var) if var != 0 else 0.0
    except Exception:
        return 0.0
