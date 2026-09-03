"""
Test 4/5: Volatility Stress — how does the strategy do specifically during
the highest-volatility windows in the data (where slippage/whipsaw hurt most)?

Test 5/5: Market Reversal — synthetic shock test. Takes the back half of the
data and flips daily returns' sign to simulate a sudden regime reversal,
then checks whether the strategy's exit logic limits the damage.
Both are pure numpy/pandas — no LLM, fully reproducible.
"""
import numpy as np
import pandas as pd

from backtest.engine import run_backtest
from backtest.metrics import compute_metrics
from models.strategy import CrashTestResult, Strategy


def volatility_stress(df: pd.DataFrame, strategy: Strategy) -> CrashTestResult:
    daily_returns = df["close"].pct_change()
    rolling_vol = daily_returns.rolling(20).std()

    if rolling_vol.dropna().empty:
        return CrashTestResult(
            test_type="volatility_stress", score=0, severity="high", passed=False,
            failure_reason="Not enough bars to compute a 20-day rolling volatility window.",
        )

    threshold = rolling_vol.quantile(0.75)
    high_vol_mask = rolling_vol >= threshold
    high_vol_df = df[high_vol_mask.reindex(df.index).fillna(False)]

    if len(high_vol_df) < 20:
        return CrashTestResult(
            test_type="volatility_stress", score=50, severity="medium", passed=True,
            failure_reason="Too few high-volatility bars to isolate a reliable sub-test; treated as neutral.",
        )

    result = run_backtest(high_vol_df, strategy)
    m = compute_metrics(result["equity_curve"], result["trades"], result["benchmark_curve"])

    # Score: reward positive/flat performance during high-vol windows, penalize deep drawdown there specifically.
    return_component = max(0.0, min(60.0, 30 + m["total_return_pct"]))
    drawdown_component = max(0.0, 40 - abs(m["max_drawdown_pct"]))
    score = min(100.0, return_component + drawdown_component)

    severity = "low" if score >= 80 else "medium" if score >= 60 else "high"
    passed = score >= 60

    return CrashTestResult(
        test_type="volatility_stress",
        score=round(score, 1),
        severity=severity,
        passed=passed,
        metrics={"high_vol_return_pct": m["total_return_pct"], "high_vol_max_drawdown_pct": m["max_drawdown_pct"], "high_vol_bars_tested": len(high_vol_df)},
        failure_reason="" if passed else "Strategy loses money or draws down heavily specifically during high-volatility windows.",
        evidence={"volatility_threshold": round(float(threshold), 5)},
    )


def market_reversal(df: pd.DataFrame, strategy: Strategy) -> CrashTestResult:
    if len(df) < 60:
        return CrashTestResult(
            test_type="market_reversal", score=0, severity="high", passed=False,
            failure_reason="Insufficient history to construct a synthetic reversal scenario.",
        )

    shocked = df.copy()
    mid = len(shocked) // 2
    daily_returns = shocked["close"].pct_change().fillna(0)
    reversed_returns = daily_returns.copy()
    reversed_returns.iloc[mid:] = -daily_returns.iloc[mid:]  # flip trend sign for the back half

    new_close = [shocked["close"].iloc[0]]
    for r in reversed_returns.iloc[1:]:
        new_close.append(new_close[-1] * (1 + r))
    shocked["close"] = new_close
    # Approximate open as prior close shifted, keeping the fill model consistent
    shocked["open"] = shocked["close"].shift(1).fillna(shocked["close"].iloc[0])

    result = run_backtest(shocked, strategy)
    m = compute_metrics(result["equity_curve"], result["trades"], result["benchmark_curve"])

    # Score rewards the strategy for exiting/limiting loss when the trend it was riding reverses.
    dd = abs(m["max_drawdown_pct"])
    score = max(0.0, min(100.0, 100 - dd * 2))
    severity = "low" if score >= 80 else "medium" if score >= 60 else "high"
    passed = score >= 60

    return CrashTestResult(
        test_type="market_reversal",
        score=round(score, 1),
        severity=severity,
        passed=passed,
        metrics={"shocked_return_pct": m["total_return_pct"], "shocked_max_drawdown_pct": m["max_drawdown_pct"]},
        failure_reason="" if passed else "Strategy takes a large drawdown when the underlying trend synthetically reverses.",
        evidence={"reversal_point_index": mid},
    )
