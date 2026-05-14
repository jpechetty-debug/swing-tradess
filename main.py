import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.symbols import get_universe
from scanner.scan_engine import run_universe_scan
from scanner.ranking import get_top_setups
from reports.stock_card import generate_html_report
from data.storage import save_scan_results

def main():
    # 1. Get Universe
    symbols = get_universe()
    
    # 2. Run Parallel Scan
    results = run_universe_scan(symbols, max_workers=10)
    
    # 3. Rank and Filter
    top_5 = get_top_setups(results, count=5)
    
    print(f"\n--- TOP 5 DAILY SETUPS ---")
    for i, s in enumerate(top_5, 1):
        print(f"{i}. {s['symbol']} | Score: {s['score']}/8 | Target: {s['target']:.2f} (+{s['potential_pct']:.2f}%)")
    
    # 4. Generate Visual Report
    generate_html_report(top_5)
    
    # 5. Save to Audit Trail
    save_scan_results(results)
    
    print("\nView the visual report at: reports/top_5_report.html")

if __name__ == "__main__":
    main()
