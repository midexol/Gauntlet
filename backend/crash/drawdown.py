"""
Test 3/5: Drawdown Resilience.
Uses the full-period backtest and scores how severe the worst peak-to-trough
decline was, and how long it took to recover, against the configured
MAX_DRAWDOWN_LIMIT_PCT (this is the one test that directly feeds the risk
gate's hard drawdown check too, so the numbers must match exactly).
"""
import pandas as pd

from backtest.engine import run_backtest
from backtest.metrics import compute_metrics
from config import settings
from models.strategy import CrashTestResult, Strategy


def _longest_recovery_days(equity_curve: pd.Series) -> int:
    running_max = equity_curve.cummax()
    underwater = equity_curve < running_max
    longest = current = 0
    for is_under in underwater:
        current = current + 1 if is_under else 0
        longest = max(longest, current)
    return longest


def run(df: pd.DataFrame, strategy: Strategy) -> CrashTestResult:
    result = run_backtest(df, strategy)
    m = compute_metrics(result["equity_curve"], result["trades"], result["benchmark_curve"])
    max_dd = abs(m["max_drawdown_pct"])
    recovery_days = _longest_recovery_days(result["equity_curve"])

    limit = settings.MAX_DRAWDOWN_LIMIT_PCT
    # Score decays linearly to 0 as drawdown approaches 2x the configured limit.
    score = max(0.0, min(100.0, 100 * (1 - max_dd / (limit * 2))))

    # Recovery-time penalty: long underwater stretches (>25% of the sample) knock points off
    recovery_ratio = recovery_days / len(df) if len(df) else 0
    if recovery_ratio > 0.25:
        score = max(0.0, score - 15)

    severity = "low" if score >= 80 else "medium" if score >= 60 else "high"
    passed = max_dd <= limit

    return CrashTestResult(
        test_type="drawdown_resilience",
        score=round(score, 1),
        severity=severity,
        passed=passed,
        metrics={"max_drawdown_pct": max_dd, "configured_limit_pct": limit, "longest_underwater_days": recovery_days},
        failure_reason="" if passed else f"Max drawdown {max_dd:.1f}% exceeds the configured {limit:.1f}% limit.",
        evidence={"equity_curve_points": len(result["equity_curve"])},
    )
