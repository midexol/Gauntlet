"""
Metrics derived from a backtest run. Pure math — no LLM.
"""
import numpy as np
import pandas as pd


def compute_metrics(equity_curve: pd.Series, trades: list[dict], benchmark_curve: pd.Series) -> dict:
    if len(equity_curve) == 0:
        return {
            "total_return_pct": 0.0, "benchmark_return_pct": 0.0,
            "max_drawdown_pct": 0.0, "trade_count": 0, "win_rate_pct": 0.0,
            "profit_factor": 0.0, "sharpe_ratio": 0.0,
        }

    total_return_pct = (equity_curve.iloc[-1] - 1.0) * 100
    benchmark_return_pct = (benchmark_curve.iloc[-1] - 1.0) * 100

    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_drawdown_pct = float(drawdown.min() * 100)

    trade_count = len(trades)
    wins = [t for t in trades if t["return_pct"] > 0]
    losses = [t for t in trades if t["return_pct"] <= 0]
    win_rate_pct = (len(wins) / trade_count * 100) if trade_count else 0.0

    gross_profit = sum(t["return_pct"] for t in wins)
    gross_loss = abs(sum(t["return_pct"] for t in losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (float("inf") if gross_profit > 0 else 0.0)

    # Daily returns from equity curve for a simple annualized Sharpe (rf = 0)
    daily_returns = equity_curve.pct_change().dropna()
    if len(daily_returns) > 1 and daily_returns.std() > 0:
        sharpe_ratio = float((daily_returns.mean() / daily_returns.std()) * np.sqrt(252))
    else:
        sharpe_ratio = 0.0

    return {
        "total_return_pct": round(float(total_return_pct), 3),
        "benchmark_return_pct": round(float(benchmark_return_pct), 3),
        "max_drawdown_pct": round(max_drawdown_pct, 3),
        "trade_count": trade_count,
        "win_rate_pct": round(win_rate_pct, 2),
        "profit_factor": round(profit_factor, 3) if profit_factor != float("inf") else 999.0,
        "sharpe_ratio": round(sharpe_ratio, 3),
    }
