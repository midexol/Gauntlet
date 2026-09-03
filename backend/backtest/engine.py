"""
Deterministic backtest engine. No LLM involved anywhere in this file —
per spec Global Agent Rules, math/scoring must be reproducible and auditable.
"""
import pandas as pd

from backtest.strategies import generate_signals
from models.strategy import Strategy


def run_backtest(df: pd.DataFrame, strategy: Strategy) -> dict:
    """
    df: OHLC daily bars, ascending date order, columns ['open','high','low','close'].
    Returns: {
        'equity_curve': pd.Series indexed by date,
        'trades': list[dict],
        'benchmark_curve': pd.Series (buy & hold of df itself, used unless a
                             separate benchmark series is supplied upstream),
    }
    """
    signals = generate_signals(df, strategy)
    signals = signals.dropna(subset=["close"]).copy()

    capital = 1.0  # normalized starting equity — position_size_pct scales exposure, not dollars
    equity = []
    trades = []
    entry_price = None
    entry_date = None
    shares_frac = 0.0  # fraction of capital deployed

    dates = signals.index
    for i in range(len(signals)):
        row = signals.iloc[i]
        pos = row["filled_position"]
        price_open = row["open"]

        # Detect a fresh entry (0 -> 1) using filled_position transitions
        prev_pos = signals.iloc[i - 1]["filled_position"] if i > 0 else 0

        if pos == 1 and prev_pos == 0:
            entry_price = float(price_open)
            entry_date = dates[i]
            shares_frac = strategy.position_size_pct / 100.0

        if pos == 0 and prev_pos == 1 and entry_price is not None:
            exit_price = float(price_open)
            trade_return = (exit_price - entry_price) / entry_price
            capital *= 1 + (trade_return * shares_frac)
            trades.append({
                "entry_date": str(entry_date.date()) if hasattr(entry_date, "date") else str(entry_date),
                "exit_date": str(dates[i].date()) if hasattr(dates[i], "date") else str(dates[i]),
                "entry_price": round(entry_price, 4),
                "exit_price": round(exit_price, 4),
                "return_pct": round(float(trade_return) * 100, 3),
            })
            entry_price = None
            entry_date = None

        # Mark-to-market equity for open positions using close price
        if pos == 1 and entry_price is not None:
            unrealized = (row["close"] - entry_price) / entry_price
            equity.append(capital * (1 + unrealized * shares_frac))
        else:
            equity.append(capital)

    # Close any still-open position at the final bar's close (avoid dangling unrealized-only trades)
    if entry_price is not None:
        exit_price = float(signals.iloc[-1]["close"])
        trade_return = (exit_price - entry_price) / entry_price
        capital *= 1 + (trade_return * shares_frac)
        trades.append({
            "entry_date": str(entry_date.date()) if hasattr(entry_date, "date") else str(entry_date),
            "exit_date": str(dates[-1].date()) if hasattr(dates[-1], "date") else str(dates[-1]),
            "entry_price": round(entry_price, 4),
            "exit_price": round(exit_price, 4),
            "return_pct": round(float(trade_return) * 100, 3),
            "note": "closed_at_backtest_end",
        })
        equity[-1] = capital

    equity_curve = pd.Series(equity, index=dates, name="equity")
    benchmark_curve = signals["close"] / signals["close"].iloc[0]

    return {
        "equity_curve": equity_curve,
        "trades": trades,
        "benchmark_curve": benchmark_curve,
    }
