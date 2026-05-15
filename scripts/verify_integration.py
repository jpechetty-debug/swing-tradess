import logging
import sys
import time
from scanner.scan_engine import run_universe_scan
from reports.generator import generate_report

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def test_scan():
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC", "LT", "ASIANPAINT"]
    
    t_start = time.time()
    results = run_universe_scan(symbols, max_workers=5)
    elapsed = time.time() - t_start
    
    print(f"\nScan complete in {elapsed:.1f}s")
    print(f"Total results: {len(results)}")
    
    if results:
        print("\nTop Results:")
        for r in sorted(results, key=lambda x: x['score'], reverse=True)[:5]:
            print(f"{r['symbol']}: Score={r['score']}, Verdict={r['verdict']}, RR={r['rr']}")
            
        print("\nGenerating Report...")
        report_path = generate_report(results, elapsed=elapsed)
        print(f"Report saved to: {report_path}")
    else:
        print("No qualified results found.")

if __name__ == "__main__":
    test_scan()
