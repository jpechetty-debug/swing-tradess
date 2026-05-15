"""
Support & Resistance Zones
Identifies horizontal price bands based on cluster of close prices + wick rejections.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd

from config.settings import (
    SR_TOUCH_MIN, SR_ATR_MULT, SR_WINDOW_DAYS, SR_MAX_LEVELS
)


@dataclass
class SRZone:
    price: float          # mid-point of the zone
    low:   float          # lower boundary
    high:  float          # upper boundary
    touches: int          # number of reactions
    zone_type: str        # 'support' | 'resistance' | 'flip'
    is_major: bool        # True if touches ≥ 3


def _find_price_clusters(
    prices: np.ndarray,
    tolerance: float,
) -> list[tuple[float, int]]:
    """
    Groups prices within `tolerance` of each other.
    Returns list of (cluster_mid, touch_count).
    """
    prices = np.sort(prices)
    clusters: list[list[float]] = []
    used = np.zeros(len(prices), dtype=bool)

    for i, p in enumerate(prices):
        if used[i]:
            continue
        cluster = [p]
        for j in range(i + 1, len(prices)):
            if abs(prices[j] - p) <= tolerance:
                cluster.append(prices[j])
                used[j] = True
        clusters.append(cluster)

    return [
        (float(np.mean(c)), len(c))
        for c in clusters
        if len(c) >= SR_TOUCH_MIN
    ]


def find_sr_zones(df: pd.DataFrame) -> dict[str, list[SRZone]]:
    """
    Detects support and resistance zones over the last SR_WINDOW_DAYS candles.

    Returns a dict with keys:
      'support'    → list[SRZone] below current price
      'resistance' → list[SRZone] above current price
      'flip'       → zones near current price (±1 ATR) with polarity change
    """
    window = df.tail(SR_WINDOW_DAYS).copy()
    current_price = float(window["Close"].iloc[-1])
    atr           = float(window["ATR14"].iloc[-1]) if "ATR14" in window.columns else 1e-9
    tolerance     = atr * SR_ATR_MULT

    # ── Gather candidate price points (swing highs, swing lows, close clusters)
    candidate_prices = np.concatenate([
        window["High"].values,
        window["Low"].values,
        window["Close"].values,
    ])

    clusters = _find_price_clusters(candidate_prices, tolerance)

    supports:    list[SRZone] = []
    resistances: list[SRZone] = []
    flips:       list[SRZone] = []

    for mid, touches in clusters:
        zone_low  = mid - tolerance * 0.5
        zone_high = mid + tolerance * 0.5
        is_major  = touches >= 3

        # ── Classify relative to current price ───────────────────────────────
        if mid < current_price - tolerance:
            z = SRZone(mid, zone_low, zone_high, touches, "support", is_major)
            supports.append(z)
        elif mid > current_price + tolerance:
            z = SRZone(mid, zone_low, zone_high, touches, "resistance", is_major)
            resistances.append(z)
        else:
            # Price is sitting ON this zone → potential flip / polarity
            z = SRZone(mid, zone_low, zone_high, touches, "flip", is_major)
            flips.append(z)

    # Sort: supports descending (nearest first), resistances ascending
    supports.sort(key=lambda z: z.price, reverse=True)
    resistances.sort(key=lambda z: z.price)

    return {
        "support":    supports[:SR_MAX_LEVELS],
        "resistance": resistances[:SR_MAX_LEVELS],
        "flip":       flips,
        "is_near_support": any(abs(current_price - z.price) <= atr for z in supports[:1])
    }


def nearest_support(zones: dict) -> SRZone | None:
    """Returns the closest support zone below current price."""
    sup = zones.get("support", [])
    return sup[0] if sup else None


def nearest_resistance(zones: dict) -> SRZone | None:
    """Returns the closest resistance zone above current price."""
    res = zones.get("resistance", [])
    return res[0] if res else None


def at_support(df: pd.DataFrame, zones: dict, atr: float) -> bool:
    """True if last close is within 1 ATR of the nearest support zone."""
    z = nearest_support(zones)
    if z is None:
        return False
    last_close = float(df["Close"].iloc[-1])
    return abs(last_close - z.price) <= atr


def clear_path_to_resistance(
    df: pd.DataFrame, zones: dict, atr: float
) -> bool:
    """
    True if there is NO major resistance within 2× the risk distance
    between current price and first target (nearest resistance).
    """
    r1 = nearest_resistance(zones)
    r2_list = zones.get("resistance", [])[1:]   # second resistance onwards

    if r1 is None:
        return True   # no resistance found – open sky

    last_close = float(df["Close"].iloc[-1])
    gap_to_r1  = r1.price - last_close

    # Check if any major resistance sits between entry and first target
    for z in r2_list:
        if z.is_major and (z.price - last_close) < gap_to_r1 * 0.5:
            return False

    return gap_to_r1 > atr   # at least 1 ATR gap to first target
