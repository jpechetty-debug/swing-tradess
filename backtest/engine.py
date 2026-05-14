import pandas as pd
import numpy as np

def run_backtest(df: pd.DataFrame, entry_signal: pd.Series, target_pct: float = 5.0, sl_pct: float = 3.0):
    """
    Vectorized backtester for a single stock.
    entry_signal: Boolean series indicating when to enter.
    """
    if df.empty or entry_signal.sum() == 0:
        return {"trades": 0, "win_rate": 0, "total_return": 0}
        
    df = df.copy()
    df['Signal'] = entry_signal
    
    trades = []
    for i in range(len(df)):
        if df['Signal'].iloc[i]:
            entry_price = df['Close'].iloc[i]
            target = entry_price * (1 + target_pct/100)
            stop = entry_price * (1 - sl_pct/100)
            
            # Look forward
            future = df.iloc[i+1:i+20] # 20-day holding window
            if future.empty:
                continue
                
            hit_target = future[future['High'] >= target]
            hit_stop = future[future['Low'] <= stop]
            
            if not hit_target.empty and (hit_stop.empty or hit_target.index[0] < hit_stop.index[0]):
                trades.append(target_pct)
            elif not hit_stop.empty:
                trades.append(-sl_pct)
            else:
                # Time exit
                final_return = ((future['Close'].iloc[-1] / entry_price) - 1) * 100
                trades.append(final_return)
                
    if not trades:
        return {"trades": 0, "win_rate": 0, "total_return": 0}
        
    returns = np.array(trades)
    return {
        "trades": len(trades),
        "win_rate": (returns > 0).mean() * 100,
        "total_return": returns.sum(),
        "avg_return": returns.mean()
    }
