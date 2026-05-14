import pandas as pd
from core.swings import get_last_swings

def classify_trend(df: pd.DataFrame) -> str:
    """
    Classifies trend based on last 4 swing points.
    Uptrend: Higher High and Higher Low
    Downtrend: Lower High and Lower Low
    Sideways: Mixed signals
    """
    last_swings = get_last_swings(df, count=4)
    if len(last_swings) < 4:
        return "INSUFFICIENT DATA"
    
    highs = last_swings[last_swings['Type'] == 'High']['Price'].tolist()
    lows = last_swings[last_swings['Type'] == 'Low']['Price'].tolist()
    
    if len(highs) < 2 or len(lows) < 2:
        return "MIXED"
    
    # Uptrend: Current High > Prev High AND Current Low > Prev Low
    is_uptrend = highs[-1] > highs[-2] and lows[-1] > lows[-2]
    
    # Downtrend: Current High < Prev High AND Current Low < Prev Low
    is_downtrend = highs[-1] < highs[-2] and lows[-1] < lows[-2]
    
    if is_uptrend:
        return "UPTREND"
    elif is_downtrend:
        return "DOWNTREND"
    else:
        return "SIDEWAYS"
