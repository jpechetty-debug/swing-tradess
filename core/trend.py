"""
Trend Classification
Uses swing points to determine market structure state.
"""

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd
from core.swings import get_last_swings, SwingPoint
from config.settings import TREND_LOOKBACK


@dataclass
class TrendSnapshot:
    state: str                       # UPTREND / DOWNTREND / SIDEWAYS / REVERSAL_ATTEMPT
    last_swing_high: Optional[float] = None
    last_swing_low:  Optional[float] = None
    swing_highs: list[float] = field(default_factory=list)
    swing_lows:  list[float] = field(default_factory=list)
    description: str = ""


def classify_trend(df: pd.DataFrame, lookback: int = TREND_LOOKBACK) -> TrendSnapshot:
    """
    Uses the last N swing points to classify trend state.
    """
    swings = get_last_swings(df, count=lookback * 2)
    
    swing_highs = [s for s in swings if s.kind == "high"]
    swing_lows  = [s for s in swings if s.kind == "low"]

    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return TrendSnapshot(
            state="INSUFFICIENT_DATA",
            description="Not enough swing points to classify trend."
        )

    # Most recent N points
    recent_highs = [sp.price for sp in swing_highs[-lookback:]]
    recent_lows  = [sp.price for sp in swing_lows[-lookback:]]

    def _is_ascending(seq): return all(x < y for x, y in zip(seq, seq[1:]))
    def _is_descending(seq): return all(x > y for x, y in zip(seq, seq[1:]))

    hh = _is_ascending(recent_highs)   # Higher Highs
    hl = _is_ascending(recent_lows)    # Higher Lows
    ll = _is_descending(recent_lows)   # Lower Lows
    lh = _is_descending(recent_highs)  # Lower Highs

    if hh and hl:
        state = "UPTREND"
        desc  = "HH + HL confirmed – bullish structure intact."
    elif lh and ll:
        state = "DOWNTREND"
        desc  = "LH + LL confirmed – bearish structure intact."
    elif hh and ll:
        state = "REVERSAL_ATTEMPT"
        desc  = "HH with LL – potential reversal, wait for confirmation."
    elif lh and hl:
        state = "REVERSAL_ATTEMPT"
        desc  = "LH with HL – compression, wait for breakout direction."
    else:
        state = "SIDEWAYS"
        desc  = "Mixed swing points – no clear trend bias."

    return TrendSnapshot(
        state        = state,
        last_swing_high = recent_highs[-1] if recent_highs else None,
        last_swing_low  = recent_lows[-1]  if recent_lows  else None,
        swing_highs  = recent_highs,
        swing_lows   = recent_lows,
        description  = desc,
    )
