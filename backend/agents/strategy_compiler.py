"""
Strategy Compiler Agent. Converts a natural-language strategy description
into the strict Strategy contract (models/strategy.py). MVP scope: sma_cross
only. The agent is NOT allowed to invent parameters the user didn't specify
or imply — if something's missing/ambiguous, it must say so rather than guess,
per the spec's 'never fabricate' global rule.
"""
import json

from agents.llm_client import LLMClientError, call_llm
from models.strategy import Strategy

SYSTEM_PROMPT = """You compile a trader's plain-English strategy description into a strict JSON object.

Rules:
- MVP only supports SMA crossover strategies (sma_cross entry and exit rules).
- If the user's description doesn't map cleanly onto SMA crossover (e.g. mentions RSI, MACD, \
options, or ML predictions), respond with exactly: {"error": "unsupported_strategy", "reason": "<why>"}
- If required numbers are missing or ambiguous (e.g. no window lengths given), respond with exactly: \
{"error": "ambiguous", "reason": "<what's missing>"}
- Never invent a fast/slow window, symbol, or position size the user did not state or clearly imply.
- On success, respond with ONLY this JSON shape, no markdown fences, no commentary:
{
  "name": "<short strategy name>",
  "symbol": "<ticker, uppercase>",
  "timeframe": "1Day",
  "entry": {"type": "sma_cross", "fast": <int>, "slow": <int>, "direction": "above"|"below"},
  "exit": {"type": "sma_cross", "fast": <int>, "slow": <int>, "direction": "above"|"below"},
  "position_size_pct": <number 0-100>,
  "benchmark": "<ticker, default QQQ if unstated>"
}"""


def compile_strategy(nl_description: str) -> dict:
    """
    Returns either {"ok": True, "strategy": Strategy} or {"ok": False, "error": str, "reason": str}.
    Validates the LLM's JSON against the pydantic contract before trusting it —
    an LLM producing syntactically-valid-but-wrong JSON must not reach the backtester.
    """
    try:
        raw = call_llm(SYSTEM_PROMPT, nl_description)
    except LLMClientError as e:
        return {"ok": False, "error": "llm_unavailable", "reason": str(e)}

    try:
        parsed = json.loads(raw.strip())
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid_json", "reason": "Compiler did not return valid JSON."}

    if "error" in parsed:
        return {"ok": False, "error": parsed["error"], "reason": parsed.get("reason", "")}

    try:
        strategy = Strategy(**parsed)
    except Exception as e:  # noqa: BLE001 — pydantic ValidationError, surfaced verbatim to the caller
        return {"ok": False, "error": "schema_mismatch", "reason": str(e)}

    return {"ok": True, "strategy": strategy}
