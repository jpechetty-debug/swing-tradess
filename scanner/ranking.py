def get_top_setups(results: list, count: int = 5):
    """
    Ranks setups by Score (primary) and RR ratio (secondary).
    """
    # Filter for Bullish only
    bullish = [r for r in results if r['trend'] == 'UPTREND']
    
    # Sort by score DESC, then RR DESC
    sorted_results = sorted(bullish, key=lambda x: (x['score'], x['rr']), reverse=True)
    
    return sorted_results[:count]
