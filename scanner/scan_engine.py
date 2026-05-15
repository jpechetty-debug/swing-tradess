import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor
from data.downloader import fetch_stock_data
from core.swings import detect_swings
from core.trend import classify_trend
from core.candles import detect_patterns
from core.support_resistance import find_sr_zones, nearest_support, nearest_resistance
from core.volume import analyze_volume
from core.liquidity import check_liquidity
from core.relative_strength import calculate_relative_strength, compute_beta, _INDEX_CACHE, _CACHE_LOCK
from data.dq_gates import run_dq_checks
from scoring.rr_engine import calculate_levels
from scoring.scorecard import calculate_score

log = logging.getLogger(__name__)

def analyze_stock(symbol: str, capital: float = 500000):
    """
    Performs full analysis for a single stock using the institutional framework.
    """
    try:
        df = fetch_stock_data(symbol)
        if df.empty or len(df) < 60:
            return None
        
        # Phase 6: DQ Gates
        passed, msg = run_dq_checks(df)
        if not passed:
            log.debug(f"DQ Filter: {symbol} failed - {msg}")
            return None
        
        # 1. Market Structure
        df = detect_swings(df)
        trend = classify_trend(df)
        # print(f"Trend for {symbol}: {trend.state}")
        
        # 2. Support & Resistance
        sr_data = find_sr_zones(df)
        # print(f"SR Zones for {symbol}: {len(sr_data.get('support', []))} supports")
        sup_zone = nearest_support(sr_data)
        res_zone = nearest_resistance(sr_data)
        
        # 3. Candlestick Patterns
        patterns = detect_patterns(df)
        
        # 4. Indicators & Metrics
        volume_data = analyze_volume(df)
        liq_data = check_liquidity(df)
        rs_value = calculate_relative_strength(df)
        
        # 5. Beta vs Nifty 50
        index_symbol = "^NSEI"
        with _CACHE_LOCK:
            if index_symbol not in _INDEX_CACHE:
                _INDEX_CACHE[index_symbol] = fetch_stock_data(index_symbol)
            index_df = _INDEX_CACHE[index_symbol]
        
        beta = compute_beta(df, index_df) if not index_df.empty else 1.0
        
        # 6. Risk Management
        risk = None
        if sup_zone and res_zone:
            atr = df["ATR14"].iloc[-1] if "ATR14" in df.columns else 0.0
            risk = calculate_levels(
                entry    = float(df["Close"].iloc[-1]),
                swing_low = sup_zone.price,
                target1  = res_zone.price,
                atr      = atr,
                capital  = capital
            )
        
        # 7. Final Scoring
        score_result = calculate_score(
            symbol   = symbol,
            df       = df,
            trend    = trend,
            sr_zones = sr_data,
            candle   = patterns,
            risk     = risk,
            beta     = beta
        )
        
        # Map ScorecardResult to dictionary for legacy compatibility if needed, 
        # or just return the object. Let's return a unified dict.
        return {
            "symbol": symbol,
            "score": score_result.score,
            "verdict": score_result.verdict,
            "verdict_color": score_result.verdict_color,
            "ltp": score_result.cmp,
            "entry": risk.entry if risk else score_result.cmp,
            "target": risk.target1 if risk else score_result.target1,
            "sl": risk.stop_loss if risk else score_result.stop_loss,
            "rr": risk.rr_t1 if risk else 0.0,
            "rr_grade": risk.rr_grade if risk else "",
            "trend_state": trend.state,
            "trend_desc": trend.description,
            "pattern": patterns.pattern,
            "pattern_desc": patterns.description,
            "beta": beta,
            "rs_value": rs_value,
            "is_liquid": liq_data["is_liquid"],
            "score_items": score_result.items,
            "gates_met": score_result.gates_met,
            "gate_trend": score_result.gate_trend,
            "gate_support": score_result.gate_support,
            "gate_candle": score_result.gate_candle,
            "gate_rr": score_result.gate_rr,
            "support_zone": score_result.support_zone,
            "avg_vol_20": score_result.avg_vol_20,
            "atr14": score_result.atr14
        }

    except Exception as e:
        log.error(f"Error analyzing {symbol}: {e}")
        return None

def run_universe_scan(symbols: list, max_workers: int = 10, capital: float = 500000):
    """
    Scans a list of symbols in parallel.
    """
    log.info(f"Starting Institutional Universe Scan for {len(symbols)} stocks...")
    results = []
    
    # Pre-fetch index data
    index_symbol = "^NSEI"
    with _CACHE_LOCK:
        if index_symbol not in _INDEX_CACHE:
            _INDEX_CACHE[index_symbol] = fetch_stock_data(index_symbol)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(analyze_stock, symbol, capital): symbol for symbol in symbols}
        for i, future in enumerate(futures):
            res = future.result()
            if res:
                results.append(res)
            
            if (i + 1) % 50 == 0:
                log.info(f"Progress: {i+1}/{len(symbols)} scanned. Qualified: {len(results)}")
                
    return results
