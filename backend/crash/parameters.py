"""
Test 2/5: Parameter Sensitivity.
Reruns the backtest with the fast/slow SMA windows nudged +/-10% and +/-20%.
A strategy whose returns collapse from a tiny parameter change was curve-fit
to this exact dataset, not discovering a real edge.
"""
import pandas as pd

from backtest.engine import run_backtest
from backtest.metrics import compute_metrics
from models.strategy import CrashTestResult, SmaCrossRule, Strategy

PERTURBATIONS = [-0.2, -0.1, 0.1, 0.2]


def _perturb(strategy: Strategy, pct: float) -> Strategy:
    def bump(v: int) -> int:
        return max(2, round(v * (1 + pct)))

    new = strategy.model_copy(deep=True)
    new.entry = SmaCrossRule(type="sma_cross", fast=bump(strategy.entry.fast), slow=bump(strategy.entry.slow), direction=strategy.entry.direction)
    new.exit = SmaCrossRule(type="sma_cross", fast=bump(strategy.exit.fast), slow=bump(strategy.exit.slow), direction=strategy.exit.direction)
    return new


def run(df: pd.DataFrame, strategy: Strategy) -> CrashTestResult:
    base_result = run_backtest(df, strategy)
    base_metrics = compute_metrics(base_result["equity_curve"], base_result["trades"], base_result["benchmark_curve"])
    base_return = base_metrics["total_return_pct"]

    variant_returns = []
    variant_details = []
    for pct in PERTURBATIONS:
        variant = _perturb(strategy, pct)
        if variant.entry.fast >= variant.entry.slow or variant.exit.fast >= variant.exit.slow:
            continue  # skip nonsensical fast>=slow combos
        result = run_backtest(df, variant)
        m = compute_metrics(result["equity_curve"], result["trades"], result["benchmark_curve"])
        variant_returns.append(m["total_return_pct"])
        variant_details.append({
            "perturbation_pct": pct * 100,
            "entry_fast": variant.entry.fast, "entry_slow": variant.entry.slow,
            "return_pct": m["total_return_pct"],
        })

    if not variant_details:
        return CrashTestResult(
            test_type="parameter_sensitivity", score=0, severity="high", passed=False,
            failure_reason="No valid parameter neighbors could be tested (window collisions).",
        )

    # A robust strategy keeps the SAME SIGN as the base case across neighbors.
    same_sign = sum(1 for r in variant_returns if (r > 0) == (base_return > 0))
    sign_stability_pct = same_sign / len(variant_returns) * 100

    # Penalize large magnitude swings even when sign holds.
    avg_abs_delta = sum(abs(r - base_return) for r in variant_returns) / len(variant_returns)
    magnitude_penalty = min(avg_abs_delta, 40)

    score = max(0.0, min(100.0, sign_stability_pct - magnitude_penalty))
    severity = "low" if score >= 80 else "medium" if score >= 60 else "high"
    passed = score >= 60

    return CrashTestResult(
        test_type="parameter_sensitivity",
        score=round(score, 1),
        severity=severity,
        passed=passed,
        metrics={"base_return_pct": base_return, "sign_stability_pct": round(sign_stability_pct, 1), "avg_abs_delta_pct": round(avg_abs_delta, 2)},
        failure_reason="" if passed else "Return sign/magnitude is unstable under small parameter changes — likely overfit.",
        evidence={"variants": variant_details},
    )
