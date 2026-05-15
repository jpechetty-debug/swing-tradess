import sys
import os
import datetime
import logging
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.symbols import get_universe
from scanner.scan_engine import run_universe_scan
from reports.generator import generate_report

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger(__name__)

def main():
    print("""
    =========================================
    INSTITUTIONAL SWING SCANNER v2.0
    =========================================
    """)
    
    # 1. Get Universe
    symbols = get_universe()
    log.info(f"Loaded {len(symbols)} stocks for scanning.")
    
    # 2. Run Parallel Scan
    t_start = time.time()
    results = run_universe_scan(symbols, max_workers=20)
    elapsed = time.time() - t_start
    
    if not results:
        log.error("No results found in scan. Check data connection or symbols list.")
        return
    
    # 3. Print Summary
    top_5 = sorted(results, key=lambda x: x['score'], reverse=True)[:5]
    
    print("\n--- TOP 5 INSTITUTIONAL SETUPS ---")
    for i, s in enumerate(top_5, 1):
        print(f"{i}. {s['symbol']} | Score: {s['score']}/8 | Verdict: {s['verdict']} | RR: {s['rr']}")
    
    # 4. Generate Institutional Excel Report
    log.info("Generating multi-sheet Excel report...")
    report_path = generate_report(results, elapsed=elapsed)
    
    print(f"\nScan complete in {elapsed:.1f}s")
    print(f"Report saved to: {report_path}")
    print("=========================================")

if __name__ == "__main__":
    main()
