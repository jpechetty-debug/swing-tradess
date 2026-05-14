import pandas as pd
from core.swings import get_last_swings

def find_sr_zones(df: pd.DataFrame, tolerance_pct: float = 0.01):
    """
    Identifies support and resistance zones by clustering recent swing points.
    """
    last_swings = get_last_swings(df, count=10)
    if last_swings.empty:
        return {"support": [], "resistance": []}
    
    ltp = df['Close'].iloc[-1]
    
    # Simple logic: Highs above LTP are resistance, Lows below LTP are support
    resistance = last_swings[(last_swings['Type'] == 'High') & (last_swings['Price'] > ltp)]
    support = last_swings[(last_swings['Type'] == 'Low') & (last_swings['Price'] < ltp)]
    
    return {
        "support": support['Price'].tolist(),
        "resistance": resistance['Price'].tolist(),
        "is_near_support": not support.empty and (abs(ltp - support['Price'].iloc[-1]) / ltp) < tolerance_pct
    }
