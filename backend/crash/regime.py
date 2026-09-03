"""
Test 1/5: Historical Robustness.
Splits the available history into N contiguous sub-periods, re-runs the
backtest on each, and scores consistency. A strategy that only works on the
full-period average but flips negative in individual chunks is fragile —
that's exactly the kind of overfit the spec calls out as unacceptable.
"""
import numpy as np
import pandas as pd

from backtest.engine import run_backtest
from backtest.metrics import compute_metrics
from models.strategy import CrashTestResult, Strategy

N_SPLITS = 3


def run(df: pd.DataFrame, strategy: Strategy) -> CrashTestResult:
    if len(df) < N_SPLITS * 60:
        # Not enough data to split meaningfully — fail closed rather than fabricate a score.
        return CrashTestResult(
            test_type="historical_robustness", score=0, severity="high", passed=False,
            failure_reason="Insufficient history to split into sub-periods (need more daily bars).",
        )

    chunk_size = len(df) // N_SPLITS
    period_returns = []
    period_details = []

    for i in range(N_SPLITS):
        start = i * chunk_size
        end = len(df) if i == N_SPLITS - 1 else (i + 1) * chunk_size
        chunk = df.iloc[start:end]
        if len(chunk) < 30:
            continue
        result = run_backtest(chunk, strategy)
        m = compute_metrics(result["equity_curve"], result["trades"], result["benchmark_curve"])
        period_returns.append(m["total_return_pct"])
        period_details.append({
            "period": i + 1,
            "start": str(chunk.index[0].date()) if hasattr(chunk.index[0], "date") else str(chunk.index[0]),
            "end": str(chunk.index[-1].date()) if hasattr(chunk.index[-1], "date") else str(chunk.index[-1]),
            "return_pct": m["total_return_pct"],
        })

    if not period_returns:
        return CrashTestResult(
            test_type="historical_robustness", score=0, severity="high", passed=False,
            failure_reason="No sub-period produced enough bars to backtest.",
        )

    profitable_periods = sum(1 for r in period_returns if r > 0)
    consistency_pct = profitable_periods / len(period_returns) * 100

    # Score blends consistency (did it work in most periods) with dispersion
    # (how wildly did results swing between periods — high variance = fragile).
    std_dev = float(np.std(period_returns))
    dispersion_penalty = min(std_dev / 2, 40)  # cap penalty so one wild period can't zero the score alone
    score = max(0.0, min(100.0, consistency_pct - dispersion_penalty))

    severity = "low" if score >= 80 else "medium" if score >= 60 else "high"
    passed = score >= 60

    return CrashTestResult(
        test_type="historical_robustness",
        score=round(score, 1),
        severity=severity,
        passed=passed,
        metrics={"period_returns_pct": period_returns, "consistency_pct": round(consistency_pct, 1), "std_dev_pct": round(std_dev, 2)},
        failure_reason="" if passed else f"Only {profitable_periods}/{len(period_returns)} historical sub-periods were profitable.",
        evidence={"periods": period_details},
    )
