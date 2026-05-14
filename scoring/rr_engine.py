import pandas as pd
from core.swings import get_last_swings

def calculate_levels(df: pd.DataFrame):
    """
    Calculates Entry, Target, and Stop Loss based on market structure.
    Entry: LTP (Last Traded Price)
    Stop Loss: Last confirmed Swing Low
    Target: Last confirmed Swing High (if above Entry) or 2:1 RR
    """
    if df.empty:
        return None
    
    ltp = df['Close'].iloc[-1]
    last_swings = get_last_swings(df, count=6)
    
    highs = last_swings[last_swings['Type'] == 'High']
    lows = last_swings[last_swings['Type'] == 'Low']
    
    if lows.empty:
        # Fallback SL: 2% below LTP
        sl = ltp * 0.98
    else:
        sl = lows['Price'].iloc[-1]
        
    risk = ltp - sl
    if risk <= 0:
        # If price is already below SL, invalid setup
        risk = ltp * 0.02
        sl = ltp * 0.98
        
    if not highs.empty and highs['Price'].iloc[-1] > ltp:
        target = highs['Price'].iloc[-1]
    else:
        # Fallback Target: 2:1 RR
        target = ltp + (risk * 2)
        
    rr = (target - ltp) / risk if risk > 0 else 0
    potential_pct = ((target - ltp) / ltp) * 100
    
    return {
        "ltp": ltp,
        "entry": ltp,
        "target": target,
        "sl": sl,
        "rr": rr,
        "potential_pct": potential_pct
    }
