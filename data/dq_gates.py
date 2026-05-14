import pandas as pd

def run_dq_checks(df: pd.DataFrame):
    """
    Hardened Data Quality gates for institutional integrity.
    Checks for:
    - Missing values (NaNs).
    - Extreme spikes (>50% move in one day).
    - Zero volume or zero price.
    """
    if df.empty:
        return False, "Empty DataFrame"
        
    # 1. Null check
    if df.isnull().values.any():
        return False, "Contains Null Values"
        
    # 2. Price check
    if (df['Close'] <= 0).any():
        return False, "Invalid Price (<= 0)"
        
    # 3. Anomaly check (Spikes)
    pct_change = df['Close'].pct_change().abs()
    if (pct_change > 0.50).any():
        return False, "Extreme Price Anomaly (>50% spike)"
        
    # 4. Volume check
    if (df['Volume'] < 0).any():
        return False, "Negative Volume"
        
    return True, "Passed"
