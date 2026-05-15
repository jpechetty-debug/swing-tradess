"""
Candlestick Pattern Detector
Reads the last candle (and second-to-last for two-bar patterns).
Returns a structured CandleSignal.
"""

from dataclasses import dataclass
import pandas as pd

from config.settings import MARUBOZU_BODY, HAMMER_WICK, DOJI_BODY, ENGULF_MULT


@dataclass
class CandleSignal:
    pattern:   str    # e.g. 'HAMMER', 'BULLISH_ENGULFING', etc.
    sentiment: str    # 'BULLISH' | 'BEARISH' | 'NEUTRAL'
    strength:  str    # 'STRONG' | 'MODERATE' | 'WEAK'
    description: str


def _body_size(o, c):  return abs(c - o)
def _range_size(h, l): return h - l if h > l else 1e-9
def _upper_wick(o, c, h): return h - max(o, c)
def _lower_wick(o, c, l): return min(o, c) - l


def detect_patterns(df: pd.DataFrame) -> CandleSignal:
    """Detect candlestick pattern of the last candle(s) in df."""

    if len(df) < 2:
        return CandleSignal("INSUFFICIENT_DATA", "NEUTRAL", "WEAK", "")

    # ── Last candle ──────────────────────────────────────────────────────────
    c = df.iloc[-1]
    o1, h1, l1, c1 = float(c["Open"]), float(c["High"]), float(c["Low"]), float(c["Close"])
    body1   = _body_size(o1, c1)
    rng1    = _range_size(h1, l1)
    uw1     = _upper_wick(o1, c1, h1)
    lw1     = _lower_wick(o1, c1, l1)
    bull1   = c1 > o1

    # ── Second-to-last candle (for two-bar patterns) ─────────────────────────
    p = df.iloc[-2]
    o2, h2, l2, c2 = float(p["Open"]), float(p["High"]), float(p["Low"]), float(p["Close"])
    body2 = _body_size(o2, c2)
    bull2 = c2 > o2

    # ── Volume context ───────────────────────────────────────────────────────
    vol_expansion = (
        float(df["Volume"].iloc[-1]) > float(df["AvgVol20"].iloc[-1])
        if "AvgVol20" in df.columns else False
    )

    # ── Pattern rules (priority order) ──────────────────────────────────────

    # 1. Bullish Marubozu
    if bull1 and body1 / rng1 >= MARUBOZU_BODY:
        return CandleSignal(
            "BULLISH_MARUBOZU", "BULLISH", "STRONG",
            "Large green body, no wicks – buyers controlled entire session."
        )

    # 2. Bearish Marubozu
    if not bull1 and body1 / rng1 >= MARUBOZU_BODY:
        return CandleSignal(
            "BEARISH_MARUBOZU", "BEARISH", "STRONG",
            "Large red body, no wicks – sellers controlled entire session."
        )

    # 3. Bullish Engulfing
    if (
        bull1 and not bull2
        and c1 > o2 * ENGULF_MULT
        and o1 < c2
        and body1 > body2 * ENGULF_MULT
    ):
        return CandleSignal(
            "BULLISH_ENGULFING", "BULLISH", "STRONG",
            "Green candle fully engulfs prior red – demand overwhelming supply."
        )

    # 4. Bearish Engulfing
    if (
        not bull1 and bull2
        and o1 > c2 * ENGULF_MULT
        and c1 < o2
        and body1 > body2 * ENGULF_MULT
    ):
        return CandleSignal(
            "BEARISH_ENGULFING", "BEARISH", "STRONG",
            "Red candle fully engulfs prior green – supply overwhelming demand."
        )

    # 5. Hammer (bullish rejection at low)
    if (
        bull1
        and lw1 >= HAMMER_WICK * body1
        and uw1 < body1
        and body1 / rng1 >= 0.15
    ):
        return CandleSignal(
            "HAMMER", "BULLISH", "STRONG",
            "Long lower wick – buyers aggressively rejected lower prices."
        )

    # 6. Inverted Hammer / Shooting Star at resistance
    if (
        uw1 >= HAMMER_WICK * body1
        and lw1 < body1
        and body1 / rng1 >= 0.10
    ):
        sentiment = "BEARISH" if not bull1 else "NEUTRAL"
        return CandleSignal(
            "SHOOTING_STAR" if not bull1 else "INVERTED_HAMMER",
            sentiment, "MODERATE",
            "Long upper wick – sellers rejected higher prices."
        )

    # 7. Inside Bar (volatility compression)
    if h1 <= h2 and l1 >= l2:
        return CandleSignal(
            "INSIDE_BAR", "NEUTRAL", "MODERATE",
            "Price contained within prior candle – compression before breakout."
        )

    # 8. Doji
    if body1 / rng1 <= DOJI_BODY:
        return CandleSignal(
            "DOJI", "NEUTRAL", "WEAK",
            "Open ≈ Close – indecision; wait for directional confirmation."
        )

    # 9. Bullish Pin Bar
    if bull1 and lw1 > 2 * body1 and uw1 < 0.5 * body1:
        return CandleSignal(
            "BULLISH_PIN_BAR", "BULLISH", "MODERATE",
            "Tiny body with long lower tail – rejection of lower prices."
        )

    # 10. Bearish Pin Bar
    if not bull1 and uw1 > 2 * body1 and lw1 < 0.5 * body1:
        return CandleSignal(
            "BEARISH_PIN_BAR", "BEARISH", "MODERATE",
            "Tiny body with long upper tail – rejection of higher prices."
        )

    # 11. Bullish / Bearish candle (plain)
    if bull1 and body1 / rng1 >= 0.50:
        strength = "STRONG" if vol_expansion else "MODERATE"
        return CandleSignal(
            "BULLISH_CANDLE", "BULLISH", strength,
            "Solid green candle – buyers in control."
        )

    if not bull1 and body1 / rng1 >= 0.50:
        return CandleSignal(
            "BEARISH_CANDLE", "BEARISH", "MODERATE",
            "Solid red candle – sellers in control."
        )

    return CandleSignal(
        "INDECISION", "NEUTRAL", "WEAK",
        "No strong pattern detected – mixed signals."
    )
