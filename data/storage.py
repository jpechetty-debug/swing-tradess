import sqlite3
import json
import datetime
import os
import pandas as pd
from config.settings import BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "data", "scans.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT,
            score INTEGER,
            trend TEXT,
            ltp REAL,
            entry REAL,
            target REAL,
            sl REAL,
            metrics TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_scan_results(results: list):
    """
    Saves a list of scan results to the database.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for r in results:
        # Serialize nested metrics
        metrics = json.dumps({
            "rr": float(r.get('rr', 0)),
            "potential_pct": float(r.get('potential_pct', 0)),
            "volume_ratio": float(r.get('volume_ratio', 0)),
            "rs_value": float(r.get('rs_value', 0)),
            "pattern": r.get('pattern', 'UNKNOWN')
        })
        
        cursor.execute("""
            INSERT INTO scan_results (timestamp, symbol, score, trend, ltp, entry, target, sl, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, r['symbol'], r['score'], r['trend'], 
            float(r['ltp'] or 0.0), float(r['entry'] or 0.0), float(r['target'] or 0.0), float(r['sl'] or 0.0),
            metrics
        ))
        
    conn.commit()
    conn.close()
    print(f"Saved {len(results)} results to {DB_PATH}")

def get_history(symbol: str = None):
    """
    Retrieves historical scan results.
    """
    conn = sqlite3.connect(DB_PATH)
    if symbol:
        df = pd.read_sql_query("SELECT * FROM scan_results WHERE symbol = ? ORDER BY timestamp DESC", conn, params=(symbol,))
    else:
        df = pd.read_sql_query("SELECT * FROM scan_results ORDER BY timestamp DESC", conn)
    conn.close()
    return df
