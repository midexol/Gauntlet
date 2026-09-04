"""
Monitoring layer (spec section 16). After a strategy is paper trading, this
checks whether CURRENT market conditions resemble the conditions under which
one of its crash tests failed, and raises a Crash Alert if so. Pure
comparison logic — no LLM, deterministic and re-runnable.
"""
import pandas as pd

from crash.engine import run_all
from models.strategy import Strategy


def check_failure_regime(recent_df: pd.DataFrame, strategy: Strategy, crash_test_summary: dict) -> dict:
    """
    recent_df: latest bars (e.g. last 20-30 days) fetched fresh from Alpaca.
    crash_test_summary: the ORIGINAL crash_test_summary computed at compile time —
        compared against, never recomputed silently, so alerts are always
        traceable to "this matches the same failure mode we already found."

    Returns: {"alert": bool, "matched_test": str|None, "message": str, "current_metrics": dict}
    """
    if len(recent_df) < 20:
        return {"alert": False, "matched_test": None, "message": "Not enough recent bars to evaluate.", "current_metrics": {}}

    recent_returns = recent_df["close"].pct_change().dropna()
    current_vol = float(recent_returns.std())
    current_dd = float(((recent_df["close"] - recent_df["close"].cummax()) / recent_df["close"].cummax()).min() * 100)

    high_severity = set(crash_test_summary.get("high_severity_tests", []))
    current_metrics = {"recent_volatility": round(current_vol, 5), "recent_drawdown_pct": round(current_dd, 2)}

    # Volatility regime match: if volatility_stress was a known weak point and current
    # rolling vol is elevated vs this strategy's own history, that's the same failure mode recurring.
    if "volatility_stress" in high_severity and current_vol > recent_returns.rolling(10).std().mean() * 1.5:
        return {
            "alert": True,
            "matched_test": "volatility_stress",
            "message": (
                f"CRASH ALERT: current volatility ({current_vol:.4f}) is elevated and this strategy "
                f"scored HIGH severity on the volatility stress test at compile time — this is the "
                f"same failure regime it was flagged for."
            ),
            "current_metrics": current_metrics,
        }

    if "drawdown_resilience" in high_severity and current_dd <= -abs(current_dd) and abs(current_dd) > 5:
        return {
            "alert": True,
            "matched_test": "drawdown_resilience",
            "message": (
                f"CRASH ALERT: strategy is currently drawing down {current_dd:.1f}% and previously "
                f"scored HIGH severity on drawdown resilience — recommend blocking new entries."
            ),
            "current_metrics": current_metrics,
        }

    # Trend-reversal regime match: split the recent window in half and compare
    # returns. A sign flip between the two halves, with enough combined swing,
    # is the live version of the synthetic reversal the crash test simulates.
    mid = len(recent_df) // 2
    first_half_return_pct = float((recent_df["close"].iloc[mid] / recent_df["close"].iloc[0] - 1) * 100)
    second_half_return_pct = float((recent_df["close"].iloc[-1] / recent_df["close"].iloc[mid] - 1) * 100)
    swing_pct = abs(first_half_return_pct) + abs(second_half_return_pct)
    current_metrics["first_half_return_pct"] = round(first_half_return_pct, 2)
    current_metrics["second_half_return_pct"] = round(second_half_return_pct, 2)

    trend_flipped = (first_half_return_pct > 0) != (second_half_return_pct > 0)
    if "market_reversal" in high_severity and trend_flipped and swing_pct > 5:
        return {
            "alert": True,
            "matched_test": "market_reversal",
            "message": (
                f"CRASH ALERT: the recent trend flipped sign (first half {first_half_return_pct:+.1f}%, "
                f"second half {second_half_return_pct:+.1f}%) and this strategy previously scored HIGH "
                f"severity on the market reversal test — this is the same failure regime it was flagged for."
            ),
            "current_metrics": current_metrics,
        }

    return {"alert": False, "matched_test": None, "message": "No known failure regime currently matched.", "current_metrics": current_metrics}
