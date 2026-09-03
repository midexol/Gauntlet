"""
Crash Analyst Agent. Takes the already-computed crash test results (numbers
never touched by an LLM) and explains, in plain English, what failed and why
it matters for a trader. This agent produces prose ONLY — it must never be
allowed to alter a score, a pass/fail flag, or the gate decision.
"""
import json

from agents.llm_client import LLMClientError, call_llm

SYSTEM_PROMPT = """You are a risk analyst explaining stress-test results to a trader.

You will be given JSON with: the robustness score, per-test scores, which \
tests failed, and their evidence/metrics. Write a short plain-English \
explanation (150-250 words) covering:
1. The headline verdict (is this strategy robust or fragile, and why)
2. The 1-2 most concerning failed tests, referencing their ACTUAL numbers from the JSON
3. One concrete, actionable suggestion (e.g. reduce position size, widen SMA windows, add a stop)

Hard rules:
- Only reference numbers that appear in the provided JSON. Never invent a \
statistic, date, or figure that isn't there.
- Do not change or contradict the pass/fail verdicts given to you.
- Plain text only, no markdown headers, conversational but precise."""


def explain(crash_test_summary: dict) -> dict:
    """Returns {"ok": True, "explanation": str} or {"ok": False, "error": str, "reason": str}."""
    evidence_payload = json.dumps(crash_test_summary, default=str)
    try:
        explanation = call_llm(SYSTEM_PROMPT, evidence_payload, max_tokens=500)
    except LLMClientError as e:
        return {"ok": False, "error": "llm_unavailable", "reason": str(e)}

    return {"ok": True, "explanation": explanation.strip()}
