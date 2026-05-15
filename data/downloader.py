"""
Data Downloader – batch-downloads NSE OHLCV data via yfinance.
Adds ATR-14 and 20-day average volume columns.
"""

import logging
import time
from typing import Optional
import numpy as np
import pandas as pd
import yfinance as yf
import os

from config.settings import (
    PERIOD, INTERVAL, BATCH_SIZE, NS_SUFFIX,
    MIN_CANDLES, MIN_AVG_VOL, MIN_PRICE, DATA_DIR
)

log = logging.getLogger(__name__)


# ── ATR ──────────────────────────────────────────────────────────────────────
def _atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    hi, lo, cl = df["High"], df["Low"], df["Close"]
    prev = cl.shift(1)
    tr = pd.concat(
        [hi - lo, (hi - prev).abs(), (lo - prev).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


# ── Single ticker ────────────────────────────────────────────────────────────
def fetch_stock_data(symbol: str) -> Optional[pd.DataFrame]:
    """Download daily OHLCV for one NSE symbol. Returns None on failure."""
    if not symbol.endswith(NS_SUFFIX) and not symbol.startswith("^"):
        ticker = symbol + NS_SUFFIX
    else:
        ticker = symbol

    try:
        df = yf.download(ticker, period=PERIOD, interval=INTERVAL,
                         auto_adjust=True, progress=False)
        if df is None or len(df) < MIN_CANDLES:
            return pd.DataFrame()
            
        # Clean columns if multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        if df.empty:
            return pd.DataFrame()

        # Add indicators
        df["ATR14"]   = _atr(df, 14)
        df["AvgVol20"] = df["Volume"].rolling(20).mean()
        df = df.dropna()
        df.attrs["symbol"] = symbol
        return df
    except Exception as e:
        log.debug(f"{symbol}: fetch error – {e}")
        return pd.DataFrame()


# ── Batch download ────────────────────────────────────────────────────────────
def fetch_batch(symbols: list[str], delay: float = 1.0) -> dict[str, pd.DataFrame]:
    """
    Downloads symbols in batches.
    Returns dict {symbol: DataFrame}.
    """
    results: dict[str, pd.DataFrame] = {}
    batches = [
        symbols[i: i + BATCH_SIZE]
        for i in range(0, len(symbols), BATCH_SIZE)
    ]

    for idx, batch in enumerate(batches):
        tickers = [s + (NS_SUFFIX if not s.endswith(NS_SUFFIX) else "") for s in batch]
        log.info(f"Batch {idx+1}/{len(batches)}: downloading {len(batch)} symbols …")
        try:
            raw = yf.download(
                tickers, period=PERIOD, interval=INTERVAL,
                auto_adjust=True, progress=False, group_by="ticker",
                threads=True,
            )
        except Exception as e:
            log.warning(f"Batch {idx+1} download error: {e}")
            time.sleep(delay * 2)
            continue

        for sym in batch:
            ticker = sym + (NS_SUFFIX if not sym.endswith(NS_SUFFIX) else "")
            try:
                if len(batch) == 1:
                    df = raw.copy()
                else:
                    df = raw[ticker].copy()

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

                if len(df) < MIN_CANDLES:
                    continue
                
                # Indicators
                df["ATR14"]    = _atr(df, 14)
                df["AvgVol20"] = df["Volume"].rolling(20).mean()
                df = df.dropna()
                df.attrs["symbol"] = sym
                results[sym] = df

            except Exception as e:
                log.debug(f"{sym}: parse error – {e}")

        time.sleep(delay)   # polite rate-limiting

    log.info(f"Fetch complete: {len(results)} usable stocks.")
    return results


def save_to_local(df: pd.DataFrame, symbol: str):
    """Saves dataframe to local parquet."""
    if df.empty:
        return
    filename = os.path.join(DATA_DIR, f"{symbol}.parquet")
    df.to_parquet(filename)


def load_from_local(symbol: str) -> pd.DataFrame:
    """Loads data from local parquet."""
    filename = os.path.join(DATA_DIR, f"{symbol}.parquet")
    if os.path.exists(filename):
        return pd.read_parquet(filename)
    return pd.DataFrame()
