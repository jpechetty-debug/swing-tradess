import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from data.downloader import fetch_stock_data
from core.swings import detect_swings
from core.trend import classify_trend
from core.candles import detect_patterns
from core.support_resistance import find_sr_zones
from core.volume import analyze_volume
from core.liquidity import check_liquidity
from core.relative_strength import calculate_relative_strength
from data.dq_gates import run_dq_checks
from scoring.rr_engine import calculate_levels
from scoring.scorecard import calculate_score

def analyze_stock(symbol: str):
    """
    Performs full analysis for a single stock.
    """
    try:
        df = fetch_stock_data(symbol)
        if df.empty or len(df) < 50:
            return None
        
        # Phase 6: DQ Gates
        passed, msg = run_dq_checks(df)
        if not passed:
            print(f"DQ Filter: {symbol} failed - {msg}")
            return None
        
        df = detect_swings(df)
        trend = classify_trend(df)
        patterns = detect_patterns(df)
        sr_data = find_sr_zones(df)
        levels = calculate_levels(df)
        volume_data = analyze_volume(df)
        liq_data = check_liquidity(df)
        rs_value = calculate_relative_strength(df)
        
        if not levels:
            return None

        # Build Scorecard
        scan_data = {
            "trend": trend,
            "support_near": sr_data["is_near_support"],
            "bullish_candle": patterns["hammer"] or patterns["engulfing"],
            "reaction_count": len(sr_data["support"]),
            "rr_ratio": levels["rr"],
            "volume_confirmation": volume_data["is_high_volume"],
            "rs_positive": rs_value > 0,
            "is_liquid": liq_data["is_liquid"],
            "clear_path": True, # Placeholder
            "breakout_structure": False
        }
        
        score = calculate_score(scan_data)
        
        return {
            "symbol": symbol,
            "trend": trend,
            "score": score,
            "ltp": levels["ltp"],
            "entry": levels["entry"],
            "target": levels["target"],
            "sl": levels["sl"],
            "potential_pct": levels["potential_pct"],
            "rr": levels["rr"],
            "volume_ratio": volume_data["volume_ratio"],
            "rs_value": rs_value,
            "is_liquid": liq_data["is_liquid"],
            "patterns": patterns,
            "sr": sr_data
        }
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

def run_universe_scan(symbols: list, max_workers: int = 10):
    """
    Scans a list of symbols in parallel.
    """
    print(f"Starting Universe Scan for {len(symbols)} stocks...")
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(analyze_stock, symbol): symbol for symbol in symbols}
        for future in futures:
            res = future.result()
            if res:
                results.append(res)
                
    return results
