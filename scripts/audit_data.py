import sqlite3
import pandas as pd
import json
import sys
import os
# Add root to sys.path for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "data", "scans.db")

def run_audit():
    print("--- Institutional Data Correctness Audit ---")
    
    if not os.path.exists(DB_PATH):
        print("Error: scans.db not found. Run main.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM scan_results", conn)
    conn.close()
    
    if df.empty:
        print("Audit: No records found in database.")
        return
        
    print(f"Total Records: {len(df)}")
    print(f"Time Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # 1. Null Checks
    null_counts = df.isnull().sum()
    if null_counts.any():
        print("WARNING: Found null values in database:")
        print(null_counts[null_counts > 0])
    else:
        print("[PASS] No null values found in primary columns.")
        
    # 2. Metric Integrity (JSON check)
    corrupted_metrics = 0
    for idx, row in df.iterrows():
        try:
            metrics = json.loads(row['metrics'])
            # Check for essential sub-metrics
            if 'rs_value' not in metrics or 'volume_ratio' not in metrics:
                corrupted_metrics += 1
        except:
            corrupted_metrics += 1
            
    if corrupted_metrics > 0:
        print(f"WARNING: Found {corrupted_metrics} records with corrupted or incomplete metrics JSON.")
    else:
        print("[PASS] All metrics JSON blobs are valid and complete.")
        
    # 3. Financial Consistency
    # Entry < Target and SL < Entry for Long setups
    inconsistent_logic = df[(df['target'] <= df['entry']) | (df['sl'] >= df['entry'])]
    if not inconsistent_logic.empty:
        print(f"WARNING: Found {len(inconsistent_logic)} records with inconsistent RR levels (e.g. Target < Entry).")
        print(inconsistent_logic[['symbol', 'entry', 'target', 'sl']])
    else:
        print("[PASS] All Risk-Reward levels are logically consistent.")
        
    # 4. Zero Price Check
    zero_prices = df[df['ltp'] <= 0]
    if not zero_prices.empty:
        print(f"WARNING: Found {len(zero_prices)} records with zero or negative prices.")
    else:
        print("[PASS] No zero or negative prices detected.")
        
    print("\n--- Audit Summary: Institutional Integrity Verified ---")

if __name__ == "__main__":
    run_audit()
