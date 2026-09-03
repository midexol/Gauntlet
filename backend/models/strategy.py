"""
Strategy data contract — matches spec section 13 exactly.
This is the ONLY shape the Strategy Compiler Agent is allowed to output;
the backend validates against it before anything touches the backtester.
"""
from typing import Literal

from pydantic import BaseModel, Field


class SmaCrossRule(BaseModel):
    type: Literal["sma_cross"] = "sma_cross"
    fast: int = Field(gt=0)
    slow: int = Field(gt=0)
    direction: Literal["above", "below"]


class Assumptions(BaseModel):
    fill_model: str = "next_bar_open"
    fees: str = "documented_assumption"
    slippage: str = "documented_assumption"


class Strategy(BaseModel):
    name: str
    symbol: str
    timeframe: str = "1Day"
    entry: SmaCrossRule
    exit: SmaCrossRule
    position_size_pct: float = Field(gt=0, le=100)
    benchmark: str = "QQQ"
    assumptions: Assumptions = Assumptions()


class CrashTestResult(BaseModel):
    """Matches spec section 13's crash-test result contract."""
    test_type: Literal[
        "historical_robustness",
        "parameter_sensitivity",
        "drawdown_resilience",
        "volatility_stress",
        "market_reversal",
    ]
    score: float = Field(ge=0, le=100)
    severity: Literal["low", "medium", "high"]
    passed: bool
    metrics: dict = {}
    failure_reason: str = ""
    evidence: dict = {}
