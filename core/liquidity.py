import pandas as pd

def check_liquidity(df: pd.DataFrame, min_turnover_cr: float = 1.0):
    """
    Checks if the stock has sufficient liquidity for institutional entry.
    min_turnover_cr: Minimum daily turnover in Crores (1 Crore = 10,000,000).
    """
    if df.empty:
        return False
        
    ltp = df['Close'].iloc[-1]
    avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
    
    # Turnover in Crores
    avg_turnover_cr = float((ltp * avg_volume) / 10_000_000)
    
    return {
        "avg_turnover_cr": avg_turnover_cr,
        "is_liquid": bool(avg_turnover_cr >= min_turnover_cr)
    }
