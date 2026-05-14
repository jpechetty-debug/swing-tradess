import pandas as pd
import numpy as np

def detect_swings(df: pd.DataFrame, lookback: int = 2) -> pd.DataFrame:
    """
    Detects swing highs and lows.
    A swing high is a peak higher than 'lookback' neighbors on both sides.
    A swing low is a trough lower than 'lookback' neighbors on both sides.
    """
    df = df.copy()
    df['Swing_High'] = np.nan
    df['Swing_Low'] = np.nan
    
    for i in range(lookback, len(df) - lookback):
        current_high = df['High'].iloc[i]
        current_low = df['Low'].iloc[i]
        
        # Check Highs
        is_high = True
        for j in range(1, lookback + 1):
            if df['High'].iloc[i-j] >= current_high or df['High'].iloc[i+j] > current_high:
                is_high = False
                break
        if is_high:
            df.loc[df.index[i], 'Swing_High'] = current_high
            
        # Check Lows
        is_low = True
        for j in range(1, lookback + 1):
            if df['Low'].iloc[i-j] <= current_low or df['Low'].iloc[i+j] < current_low:
                is_low = False
                break
        if is_low:
            df.loc[df.index[i], 'Swing_Low'] = current_low
            
    return df

def get_last_swings(df: pd.DataFrame, count: int = 4):
    """
    Returns the last 'count' confirmed swing points.
    Returns a list of tuples: (index, price, type['High'/'Low'])
    """
    highs = df[df['Swing_High'].notna()][['Swing_High']].rename(columns={'Swing_High': 'Price'})
    highs['Type'] = 'High'
    
    lows = df[df['Swing_Low'].notna()][['Swing_Low']].rename(columns={'Swing_Low': 'Price'})
    lows['Type'] = 'Low'
    
    combined = pd.concat([highs, lows]).sort_index()
    return combined.tail(count)
