"""
Swing High/Low Detection
Identifies swing points based on body-close local extrema.
"""

from dataclasses import dataclass
from typing import Optional
import pandas as pd
import numpy as np

from config.settings import SWING_WINDOW


@dataclass
class SwingPoint:
    index: int          # DataFrame integer position
    date: object        # pandas Timestamp
    price: float        # Close price at swing point
    kind: str           # 'high' or 'low'


def detect_swings(df: pd.DataFrame, window: int = SWING_WINDOW) -> pd.DataFrame:
    """
    Identifies swing highs and lows using BODY closes (not wicks).
    Adds Swing_High and Swing_Low columns to the DataFrame.
    """
    df = df.copy()
    df["Swing_High"] = np.nan
    df["Swing_Low"]  = np.nan
    
    closes = df["Close"].values
    dates  = df.index

    for i in range(window, len(closes) - window):
        # ── Swing High: candle body close is local maximum ───────────────────
        window_closes = closes[i - window: i + window + 1]
        if closes[i] == window_closes.max():
            df.loc[dates[i], "Swing_High"] = float(closes[i])

        # ── Swing Low: candle body close is local minimum ────────────────────
        if closes[i] == window_closes.min():
            df.loc[dates[i], "Swing_Low"] = float(closes[i])

    return df


def get_last_swings(df: pd.DataFrame, count: int = 4):
    """
    Returns the last 'count' confirmed swing points as a list of SwingPoint objects.
    """
    highs = df[df["Swing_High"].notna()]
    lows  = df[df["Swing_Low"].notna()]
    
    swing_points = []
    
    # Extract highs
    for idx, row in highs.iterrows():
        pos = df.index.get_loc(idx)
        swing_points.append(SwingPoint(pos, idx, float(row["Swing_High"]), "high"))
        
    # Extract lows
    for idx, row in lows.iterrows():
        pos = df.index.get_loc(idx)
        swing_points.append(SwingPoint(pos, idx, float(row["Swing_Low"]), "low"))
        
    # Sort by index and return last count
    swing_points.sort(key=lambda x: x.index)
    return swing_points[-count:]
