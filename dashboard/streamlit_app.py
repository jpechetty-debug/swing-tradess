import streamlit as st
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.symbols import get_universe
from scanner.scan_engine import run_universe_scan
from scanner.ranking import get_top_setups
from data.storage import get_history

# Page Config
st.set_page_config(page_title="Institutional Swing Scanner", page_icon="📈", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1890ff; color: white; }
    .card { 
        background: #fffbe6; border-radius: 12px; border: 1px solid #ffe58f; 
        padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .symbol-title { font-size: 24px; font-weight: bold; color: #262626; }
    .metric-value { font-size: 18px; font-weight: bold; color: #1890ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Institutional Swing Scanner")
st.markdown("### High-Fidelity Market Structure Analysis")

# Sidebar
st.sidebar.header("Scan Configuration")
universe = st.sidebar.selectbox("Universe", ["Nifty 50", "Full NSE (2500)"])
workers = st.sidebar.slider("Parallel Workers", 1, 50, 20)
min_score = st.sidebar.slider("Min Scorecard", 1, 8, 5)

# Phase 6: Data Freshness
try:
    history = get_history()
    if history is not None and not history.empty:
        last_scan = history['timestamp'].max()
        st.sidebar.info(f"📅 **Data Freshness:**\nLast Scan: {last_scan}")
    else:
        st.sidebar.warning("⚠️ No historical data found.")
except Exception:
    st.sidebar.warning("⚠️ Could not retrieve scan history.")

if st.sidebar.button("🚀 Start Scan"):
    with st.spinner("Scanning Universe..."):
        symbols = get_universe()
        results = run_universe_scan(symbols, max_workers=workers)
        
        # Apply Min Score Filter
        filtered_results = [r for r in results if r['score'] >= min_score]
        
        # Filtering and Ranking
        top_setups = get_top_setups(filtered_results, count=5)
        
        # Store in session state
        st.session_state['scan_results'] = filtered_results
        st.session_state['top_setups'] = top_setups

# Display Results
if 'top_setups' in st.session_state and len(st.session_state['top_setups']) > 0:
    st.header("🔥 Top 5 Daily Setups")
    cols = st.columns(len(st.session_state['top_setups']))
    
    for i, setup in enumerate(st.session_state['top_setups']):
        with cols[i]:
            st.markdown(f"""
                <div class="card">
                    <div class="symbol-title">{setup['symbol']}</div>
                    <div style="font-size: 12px; color: #8c8c8c;">Score: {setup['score']}/8</div>
                    <hr>
                    <div class="metric-value">₹{float(setup['entry'] or 0):,.2f}</div>
                    <div style="font-size: 12px; color: #8c8c8c;">Target: ₹{float(setup['target'] or 0):,.2f}</div>
                    <div style="font-size: 12px; color: #52c41a;">+{float(setup['potential_pct'] or 0):.2f}% Potential</div>
                </div>
            """, unsafe_allow_html=True)
elif 'top_setups' in st.session_state:
    st.warning(f"No setups found meeting the score threshold of {min_score}.")
else:
    st.info("👈 Click 'Start Scan' in the sidebar to begin analysis.")
