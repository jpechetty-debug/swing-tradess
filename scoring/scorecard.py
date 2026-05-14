def calculate_score(data: dict) -> int:
    """
    Evaluates the 8-point scorecard.
    Expects data keys: trend, support_near, bullish_candle, reaction_count, 
    rr_ratio, clear_path, breakout_structure, volume_confirmation.
    """
    score = 0
    
    # 1. Uptrend Confirmed
    if data.get('trend') == "UPTREND":
        score += 1
        
    # 2. Support Proximity (Placeholder until S&R engine)
    if data.get('support_near'):
        score += 1
        
    # 3. Bullish Candle Signal
    if data.get('bullish_candle'):
        score += 1
        
    # 4. Support Reaction Count (Placeholder)
    if data.get('reaction_count', 0) >= 2:
        score += 1
        
    # 5. RR Ratio Viability
    if data.get('rr_ratio', 0) >= 1.5:
        score += 1
        
    # 6. Clear Path to Run (Placeholder)
    if data.get('clear_path'):
        score += 1
        
    # 7. Breakout Structure (Placeholder)
    if data.get('breakout_structure'):
        score += 1
        
    # 8. Volume Confirmation
    if data.get('volume_confirmation'):
        score += 1
        
    # 9. Relative Strength Positive
    if data.get('rs_positive'):
        score += 1
        
    # 10. Liquidity Pass
    if not data.get('is_liquid'):
        # Penalize illiquid stocks
        score -= 2
        
    return score

def get_setup_rating(score: int) -> str:
    if score >= 8: return "STRONG BULLISH"
    if score >= 6: return "WATCH"
    if score >= 4: return "NEUTRAL"
    return "SKIP"
