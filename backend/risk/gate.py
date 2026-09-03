"""
Risk Gate. Deterministic and auditable on purpose — this is the component
whose whole job is to NOT be talked into anything by an LLM. Every decision
here must be traceable to a number, not a model's opinion.
"""
from config import settings


def evaluate_gate(crash_test_summary: dict, position_size_pct: float, paper_mode: bool) -> dict:
    """
    crash_test_summary: output of crash.engine.run_all()
    Returns: {decision: 'BLOCK'|'CONDITIONAL'|'PASS', reasons: [...], score: float}
    """
    reasons = []
    score = crash_test_summary["robustness_score"]

    # --- Hard blocks (any one of these is an automatic BLOCK, regardless of score) ---
    if not paper_mode:
        reasons.append("Live trading mode is not permitted by this system — paper mode only.")

    if position_size_pct > settings.MAX_POSITION_SIZE_PCT:
        reasons.append(
            f"Requested position size {position_size_pct:.1f}% exceeds the hard cap of "
            f"{settings.MAX_POSITION_SIZE_PCT:.1f}%."
        )

    dd_result = next(
        (r for r in crash_test_summary["results"] if r["test_type"] == "drawdown_resilience"), None
    )
    if dd_result and dd_result["metrics"].get("max_drawdown_pct", 0) > settings.MAX_DRAWDOWN_LIMIT_PCT:
        reasons.append(
            f"Backtested max drawdown {dd_result['metrics']['max_drawdown_pct']:.1f}% exceeds the "
            f"configured limit of {settings.MAX_DRAWDOWN_LIMIT_PCT:.1f}%."
        )

    if reasons:
        return {"decision": "BLOCK", "score": score, "reasons": reasons}

    # --- Score-based tiers (only reached if no hard block fired) ---
    if score >= settings.ROBUSTNESS_MIN_PASS:
        return {
            "decision": "PASS",
            "score": score,
            "reasons": [f"Robustness score {score:.1f} meets the {settings.ROBUSTNESS_MIN_PASS:.0f} PASS threshold."],
        }

    if score >= settings.ROBUSTNESS_MIN_CONDITIONAL:
        return {
            "decision": "CONDITIONAL",
            "score": score,
            "reasons": [
                f"Robustness score {score:.1f} is between {settings.ROBUSTNESS_MIN_CONDITIONAL:.0f} and "
                f"{settings.ROBUSTNESS_MIN_PASS:.0f} — allowed to paper trade at reduced size with monitoring.",
                *(f"Weak test: {t}" for t in crash_test_summary["failed_tests"]),
            ],
        }

    return {
        "decision": "BLOCK",
        "score": score,
        "reasons": [
            f"Robustness score {score:.1f} is below the {settings.ROBUSTNESS_MIN_CONDITIONAL:.0f} minimum.",
            *(f"Failed: {t}" for t in crash_test_summary["failed_tests"]),
        ],
    }
