"""
Runs all 5 crash tests and combines them into the single Strategy Robustness
Score (0-100) that drives the risk gate. Weights map 1:1 to the 5 test types:

    historical_robustness  -> 25%  (does it hold across different eras)
    parameter_sensitivity  -> 20%  (is it curve-fit / fragile to tuning)
    drawdown_resilience    -> 20%  (worst-case pain, matches the hard DD limit)
    volatility_stress      -> 20%  (regime robustness: how it behaves when vol spikes)
    market_reversal        -> 15%  (shock resilience: sudden trend flip)

Pure aggregation — no LLM involved in the score itself, per spec Global Agent Rules.
"""
import pandas as pd

from crash import drawdown, parameters, regime, shocks
from models.strategy import CrashTestResult, Strategy

WEIGHTS = {
    "historical_robustness": 0.25,
    "parameter_sensitivity": 0.20,
    "drawdown_resilience": 0.20,
    "volatility_stress": 0.20,
    "market_reversal": 0.15,
}


def run_all(df: pd.DataFrame, strategy: Strategy) -> dict:
    results: list[CrashTestResult] = [
        regime.run(df, strategy),
        parameters.run(df, strategy),
        drawdown.run(df, strategy),
        shocks.volatility_stress(df, strategy),
        shocks.market_reversal(df, strategy),
    ]

    weighted_score = sum(r.score * WEIGHTS[r.test_type] for r in results)
    failed_tests = [r.test_type for r in results if not r.passed]
    high_severity = [r.test_type for r in results if r.severity == "high"]

    return {
        "robustness_score": round(weighted_score, 1),
        "component_scores": {r.test_type: r.score for r in results},
        "weights": WEIGHTS,
        "failed_tests": failed_tests,
        "high_severity_tests": high_severity,
        "results": [r.model_dump() for r in results],
    }
