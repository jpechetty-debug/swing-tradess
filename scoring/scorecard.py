"""
8-Point Scorecard & 4-Gate Entry Framework
Converts all technical signals into a standardised score and verdict.
"""

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd

from config.settings import STRONG_SCORE, SKIP_SCORE, GATES_REQUIRED, MIN_BETA
from core.trend    import TrendSnapshot
from core.support_resistance  import SRZone, nearest_support, at_support, clear_path_to_resistance
from core.candles         import CandleSignal
from scoring.rr_engine        import RiskProfile


# ── Score item ────────────────────────────────────────────────────────────────
@dataclass
class ScoreItem:
    criterion: str
    status:    str    # 'MET' | 'PARTIAL' | 'NOT MET'
    note:      str


# ── Full result ───────────────────────────────────────────────────────────────
@dataclass
class ScorecardResult:
    symbol:          str
    cmp:             float           # Current Market Price
    score:           int             # 0-8
    max_score:       int = 8
    items:           list[ScoreItem] = field(default_factory=list)

    # Gates
    gate_trend:      str = "NO"      # YES / PARTIAL / NO
    gate_support:    str = "NO"
    gate_candle:     str = "NO"
    gate_rr:         str = "NO"
    gates_met:       int = 0

    # Final verdict
    verdict:         str = "NEUTRAL SIDEWAYS"
    verdict_color:   str = "GREY"    # GREEN / BLUE / AMBER / GREY / RED

    # Key levels
    support_zone:    Optional[float] = None
    resistance_zone: Optional[float] = None
    trend_state:     str = ""
    candle_pattern:  str = ""
    rr_t1:           Optional[float] = None
    rr_grade:        str = ""
    stop_loss:       Optional[float] = None
    target1:         Optional[float] = None
    beta:            float = 0.0
    avg_vol_20:      float = 0.0
    atr14:           float = 0.0


def _met(cond: bool, partial_cond: bool = False) -> str:
    if cond:      return "MET"
    if partial_cond: return "PARTIAL"
    return "NOT MET"


def _score(status: str) -> int:
    return {"MET": 1, "PARTIAL": 0, "NOT MET": 0}[status]


# ── Main scoring function ─────────────────────────────────────────────────────
def calculate_score(
    symbol:    str,
    df:        pd.DataFrame,
    trend:     TrendSnapshot,
    sr_zones:  dict,
    candle:    CandleSignal,
    risk:      Optional[RiskProfile],
    beta:      float,
) -> ScorecardResult:
    """
    Evaluates all 8 scorecard criteria and 4 entry gates.
    """
    cmp   = float(df["Close"].iloc[-1])
    atr   = float(df["ATR14"].iloc[-1]) if "ATR14" in df.columns else 1e-9
    vol20 = float(df["AvgVol20"].iloc[-1]) if "AvgVol20" in df.columns else 0

    items:  list[ScoreItem] = []
    score = 0

    # ── 1. Uptrend Confirmed ─────────────────────────────────────────────────
    is_uptrend   = trend.state == "UPTREND"
    is_possible  = trend.state == "REVERSAL_ATTEMPT"
    s1 = _met(is_uptrend, is_possible)
    items.append(ScoreItem(
        "Uptrend Confirmed (HH + HL on Daily)",
        s1, trend.description
    ))
    score += _score(s1)

    # ── 2. Price at / near Support ────────────────────────────────────────────
    near_sup = at_support(df, sr_zones, atr)
    sup_zone = nearest_support(sr_zones)
    sup_price = sup_zone.price if sup_zone else None
    s2 = _met(near_sup)
    items.append(ScoreItem(
        "Price at Proven Support Zone",
        s2,
        f"Nearest support: ₹{sup_price:.2f}" if sup_price else "No support zone found."
    ))
    score += _score(s2)

    # ── 3. Bullish Candle Signal ──────────────────────────────────────────────
    bull_candle = candle.sentiment == "BULLISH"
    mod_candle  = candle.sentiment == "NEUTRAL" and candle.pattern in ("INSIDE_BAR",)
    s3 = _met(bull_candle, mod_candle)
    items.append(ScoreItem(
        "Bullish Reversal Candle at Support",
        s3, f"{candle.pattern} – {candle.description}"
    ))
    score += _score(s3)

    # ── 4. Support Reaction Count ─────────────────────────────────────────────
    sup_touches  = sup_zone.touches if sup_zone else 0
    major_zone   = sup_zone.is_major if sup_zone else False
    s4 = _met(sup_touches >= 3, sup_touches == 2)
    items.append(ScoreItem(
        "Support Zone Reaction Count ≥ 2",
        s4, f"Touch count: {sup_touches}" + (" (Major Zone)" if major_zone else "")
    ))
    score += _score(s4)

    # ── 5. RR Ratio Viability ─────────────────────────────────────────────────
    rr_ok = risk.rr_viable if risk else False
    rr_partial = (risk.rr_t1 >= 1.0) if risk else False
    s5 = _met(rr_ok, rr_partial and not rr_ok)
    items.append(ScoreItem(
        f"RR Ratio ≥ {1.5} to First Target",
        s5,
        f"RR T1: {risk.rr_t1:.2f} ({risk.rr_grade})" if risk else "Cannot compute RR."
    ))
    score += _score(s5)

    # ── 6. Clear Path to First Target ────────────────────────────────────────
    clear_path = clear_path_to_resistance(df, sr_zones, atr)
    res_zone   = sr_zones.get("resistance", [])
    res_price  = res_zone[0].price if res_zone else None
    s6 = _met(clear_path)
    items.append(ScoreItem(
        "Clear Path to T1 (No Major Resistance)",
        s6,
        f"T1 resistance: ₹{res_price:.2f}" if res_price else "No resistance found above."
    ))
    score += _score(s6)

    # ── 7. Breakout / Consolidation Structure ────────────────────────────────
    inside_bar     = candle.pattern == "INSIDE_BAR"
    body_ratio_10d = df["Close"].pct_change().abs().tail(10).mean()
    low_volatility = body_ratio_10d < 0.015    # <1.5% avg daily move = compression
    s7 = _met(inside_bar or low_volatility)
    items.append(ScoreItem(
        "Consolidation / Breakout Structure",
        s7,
        "Inside bar or low-volatility compression visible." if (inside_bar or low_volatility)
        else "No compression structure detected."
    ))
    score += _score(s7)

    # ── 8. Volume Confirmation ────────────────────────────────────────────────
    last_vol  = float(df["Volume"].iloc[-1])
    vol_up    = vol20 > 0 and last_vol > vol20
    s8 = _met(vol_up)
    items.append(ScoreItem(
        "Volume Expansion on Signal Candle",
        s8,
        f"Last vol: {last_vol:,.0f} vs 20-day avg: {vol20:,.0f}"
    ))
    score += _score(s8)

    # ── 4 Entry Gates ────────────────────────────────────────────────────────
    g_trend   = "YES" if is_uptrend else ("PARTIAL" if is_possible else "NO")
    g_support = "YES" if near_sup else "NO"
    g_candle  = "YES" if bull_candle else ("PARTIAL" if mod_candle else "NO")
    g_rr      = "YES" if rr_ok else ("PARTIAL" if rr_partial else "NO")

    gates_met = sum(1 for g in [g_trend, g_support, g_candle, g_rr] if g == "YES")
    gates_met += sum(0.5 for g in [g_trend, g_support, g_candle, g_rr] if g == "PARTIAL")
    gates_met = int(gates_met)

    # ── Verdict ───────────────────────────────────────────────────────────────
    if score >= STRONG_SCORE and gates_met >= GATES_REQUIRED:
        verdict       = "STRONG BULLISH SETUP"
        verdict_color = "GREEN"
    elif score >= STRONG_SCORE - 1 and gates_met >= GATES_REQUIRED - 1:
        verdict       = "WATCH FOR BREAKOUT"
        verdict_color = "BLUE"
    elif score >= SKIP_SCORE:
        verdict       = "RETEST OPPORTUNITY"
        verdict_color = "AMBER"
    else:
        verdict       = "SKIP / NEUTRAL"
        verdict_color = "GREY"

    if trend.state == "DOWNTREND":
        verdict       = "DOWNTREND – AVOID LONG"
        verdict_color = "RED"

    return ScorecardResult(
        symbol         = symbol,
        cmp            = round(cmp, 2),
        score          = score,
        items          = items,
        gate_trend     = g_trend,
        gate_support   = g_support,
        gate_candle    = g_candle,
        gate_rr        = g_rr,
        gates_met      = gates_met,
        verdict        = verdict,
        verdict_color  = verdict_color,
        support_zone   = round(sup_price, 2) if sup_price else None,
        resistance_zone= round(res_price, 2) if res_price else None,
        trend_state    = trend.state,
        candle_pattern = candle.pattern,
        rr_t1          = risk.rr_t1 if risk else None,
        rr_grade       = risk.rr_grade if risk else "",
        stop_loss      = risk.stop_loss if risk else None,
        target1        = risk.target1 if risk else None,
        beta           = round(beta, 2),
        avg_vol_20     = round(vol20, 0),
        atr14          = round(atr, 2),
    )
