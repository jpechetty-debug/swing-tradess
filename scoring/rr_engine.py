"""
Risk Management & Position Sizing
Implements the 1% Risk Rule with structural stop-loss placement.
Computes RR ratios to T1 (first resistance) and T2 (second resistance).
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np

from config.settings import (
    DEFAULT_CAPITAL, RISK_PCT, STOP_BUFFER_ATR,
    MIN_RR_T1, GOOD_RR_T1, EXCEL_RR_T1,
)


@dataclass
class RiskProfile:
    capital:       float
    entry:         float
    stop_loss:     float
    target1:       float
    target2:       Optional[float]
    risk_per_share:  float
    risk_capital:    float        # = capital × RISK_PCT
    position_size:   int          # number of shares
    position_value:  float        # entry × shares
    rr_t1:           float        # reward / risk to T1
    rr_t2:           Optional[float]
    rr_grade:        str          # POOR / ACCEPTABLE / GOOD / EXCELLENT
    rr_viable:       bool         # meets MIN_RR_T1 threshold
    stop_pct:        float        # stop distance as % of entry


def _grade_rr(rr: float) -> tuple[str, bool]:
    if rr < MIN_RR_T1:
        return "POOR", False
    elif rr < GOOD_RR_T1:
        return "ACCEPTABLE", True
    elif rr < EXCEL_RR_T1:
        return "GOOD", True
    else:
        return "EXCELLENT", True


def calculate_levels(
    entry: float,
    swing_low: float,
    target1: float,
    atr: float,
    target2: Optional[float] = None,
    capital: float = DEFAULT_CAPITAL,
) -> RiskProfile:
    """
    Computes full risk profile for a long swing entry.
    Renamed from calculate_risk to calculate_levels for scan_engine.py compatibility.

    stop_loss = swing_low – STOP_BUFFER_ATR × ATR
    (places stop just below the structural swing low)
    """
    stop_loss = swing_low - STOP_BUFFER_ATR * atr
    stop_loss = max(stop_loss, entry * 0.85)    # hard floor: -15% max

    risk_per_share = entry - stop_loss
    if risk_per_share <= 0:
        risk_per_share = atr if atr > 0 else 1.0   # fallback

    risk_capital  = capital * RISK_PCT
    position_size = max(1, int(risk_capital / risk_per_share))
    position_value = position_size * entry

    reward_t1 = target1 - entry
    rr_t1     = reward_t1 / risk_per_share if risk_per_share > 0 else 0.0
    rr_grade, rr_viable = _grade_rr(rr_t1)

    rr_t2 = None
    if target2 is not None:
        reward_t2 = target2 - entry
        rr_t2 = reward_t2 / risk_per_share if risk_per_share > 0 else 0.0

    stop_pct = (risk_per_share / entry) * 100

    return RiskProfile(
        capital        = capital,
        entry          = round(entry, 2),
        stop_loss      = round(stop_loss, 2),
        target1        = round(target1, 2),
        target2        = round(target2, 2) if target2 else None,
        risk_per_share = round(risk_per_share, 2),
        risk_capital   = round(risk_capital, 2),
        position_size  = position_size,
        position_value = round(position_value, 2),
        rr_t1          = round(rr_t1, 2),
        rr_t2          = round(rr_t2, 2) if rr_t2 else None,
        rr_grade       = rr_grade,
        rr_viable      = rr_viable,
        stop_pct       = round(stop_pct, 2),
    )
