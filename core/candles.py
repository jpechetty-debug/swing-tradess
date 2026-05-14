import pandas as pd

def is_hammer(candle: pd.Series) -> bool:
    """
    Detects Hammer: Small body, long lower wick (at least 2x body).
    """
    body = abs(candle['Close'] - candle['Open'])
    lower_wick = min(candle['Open'], candle['Close']) - candle['Low']
    upper_wick = candle['High'] - max(candle['Open'], candle['Close'])
    
    # Standard Hammer logic
    if body == 0: body = 0.001 # Avoid div by zero
    return lower_wick > (body * 2) and upper_wick < body

def is_bullish_engulfing(prev: pd.Series, curr: pd.Series) -> bool:
    """
    Detects Bullish Engulfing: 
    1. Prev candle is red.
    2. Current candle is green and engulfs prev body.
    """
    prev_red = prev['Close'] < prev['Open']
    curr_green = curr['Close'] > curr['Open']
    engulfs = curr['Open'] < prev['Close'] and curr['Close'] > prev['Open']
    
    return prev_red and curr_green and engulfs

def detect_patterns(df: pd.DataFrame):
    """
    Checks the last 2 candles for patterns.
    """
    if len(df) < 2:
        return {"hammer": False, "engulfing": False}
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    return {
        "hammer": is_hammer(last),
        "engulfing": is_bullish_engulfing(prev, last)
    }
