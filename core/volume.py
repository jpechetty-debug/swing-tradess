import pandas as pd
import numpy as np

def analyze_volume(df: pd.DataFrame, window: int = 20):
    """
    Analyzes volume for institutional accumulation.
    Returns:
    - is_high_volume: Current volume > Average volume.
    - volume_ratio: Current volume / Average volume.
    - volume_trend: Increasing or Decreasing.
    """
    if len(df) < window:
        return {"is_high_volume": False, "volume_ratio": 1.0, "volume_trend": "NEUTRAL"}
    
    avg_volume = df['Volume'].rolling(window=window).mean()
    current_volume = df['Volume'].iloc[-1]
    prev_volume = df['Volume'].iloc[-2]
    
    volume_ratio = float(current_volume / avg_volume.iloc[-1]) if avg_volume.iloc[-1] > 0 else 1.0
    is_high_volume = bool(current_volume > avg_volume.iloc[-1])
    
    volume_trend = "UP" if current_volume > prev_volume else "DOWN"
    
    return {
        "is_high_volume": is_high_volume,
        "volume_ratio": volume_ratio,
        "volume_trend": volume_trend,
        "accumulation": bool(is_high_volume and df['Close'].iloc[-1] > df['Open'].iloc[-1])
    }
