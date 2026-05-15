import datetime
import os
from config.settings import REPORTS_DIR

def generate_html_report(top_setups: list):
    """
    Generates a premium HTML report with stock cards.
    """
    timestamp = datetime.datetime.now().strftime("%d %b %I:%M %p")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #f8f9fa; padding: 20px; }}
            .card {{ 
                background: #fffbe6; border-radius: 12px; border: 1px solid #ffe58f; 
                margin-bottom: 20px; padding: 20px; position: relative; max-width: 800px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            }}
            .hot {{
                position: absolute; top: 0; right: 0; background: #ff7875; color: white;
                padding: 4px 12px; border-radius: 0 12px 0 12px; font-weight: bold; font-size: 12px;
            }}
            .header {{ display: flex; align-items: center; justify-content: space-between; }}
            .symbol {{ font-size: 24px; font-weight: bold; color: #262626; }}
            .status {{ background: #f6ffed; border: 1px solid #b7eb8f; color: #52c41a; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
            .tags {{ margin-top: 10px; }}
            .tag {{ background: #f0f0f0; border: 1px solid #d9d9d9; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }}
            .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 20px; border-top: 1px solid #f0f0f0; padding-top: 20px; }}
            .metric {{ text-align: center; }}
            .label {{ font-size: 12px; color: #8c8c8c; text-transform: uppercase; }}
            .value {{ font-size: 18px; font-weight: bold; margin-top: 5px; }}
            .green {{ color: #52c41a; }}
            .red {{ color: #ff4d4f; }}
            .blue {{ color: #1890ff; }}
            .analysis {{ margin-top: 20px; font-size: 14px; color: #595959; border-top: 1px dashed #d9d9d9; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>Institutional Swing Scanner - Top 5 Setups</h1>
        <p>Report Generated: {timestamp}</p>
    """
    
    for stock in top_setups:
        html += f"""
        <div class="card">
            <div class="hot">HOT</div>
            <div class="header">
                <div>
                    <div class="symbol">{stock['symbol']}</div>
                    <div style="font-size: 12px; color: #8c8c8c;">NSE:{stock['symbol']}-EQ</div>
                </div>
                <div class="status">● ACTIVE</div>
            </div>
            <div class="tags">
                <span class="tag">STOCK</span>
                <span class="tag" style="background: #e6fffb; color: #13c2c2;">BUY</span>
                <span class="tag" style="background: #fff7e6; color: #fa8c16;">SWING</span>
                <span class="tag" style="background: #f6ffed; color: #52c41a;">Risk: LOW</span>
            </div>
            <div style="font-size: 10px; color: #8c8c8c; margin-top: 5px;">Data as of: {stock.get('timestamp', 'Live')}</div>
            <div class="grid">
                <div class="metric">
                    <div class="label">Entry</div>
                    <div class="value">₹{stock['entry']:.2f}</div>
                </div>
                <div class="metric">
                    <div class="label">Target</div>
                    <div class="value green">₹{stock['target']:.2f}</div>
                    <div class="label green">+{stock['potential_pct']:.2f}%</div>
                </div>
                <div class="metric">
                    <div class="label">SL</div>
                    <div class="value red">₹{stock['sl']:.2f}</div>
                </div>
                <div class="metric">
                    <div class="label">Potential</div>
                    <div class="value blue">{stock['potential_pct']:.2f}%</div>
                </div>
            </div>
            <div class="analysis">
                🛡️ Analysis: Score {stock['score']}/8. Trend is {stock['trend']}. Potential RR ratio of {stock['rr']:.2f}.
            </div>
        </div>
        """
        
    html += "</body></html>"
    
    report_path = os.path.join(REPORTS_DIR, "top_5_report.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report generated: {report_path}")
