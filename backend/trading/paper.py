"""
Paper trading execution layer. This module is the last line of defense for
the 'never trade live, never bypass the gate' rule — it re-checks the gate
decision itself rather than trusting the caller, and never touches the
Alpaca SDK directly (goes through AlpacaClient.submit_market_order only).
"""
from alpaca_client import AlpacaClientError, get_alpaca_client
from config import settings


class GateNotSatisfiedError(RuntimeError):
    pass


def submit_paper_order(symbol: str, notional_pct_of_equity: float, side: str, gate_decision: dict) -> dict:
    """
    gate_decision: the dict returned by risk.gate.evaluate_gate() for THIS strategy run.
    Refuses to submit anything unless the gate says PASS or CONDITIONAL —
    this check happens here again, not just at the API layer, so no code
    path can reach Alpaca without it.

    Sizing is based on portfolio_value (total account equity), not
    buying_power (which includes margin/leverage) — position_size_pct is a
    stated fraction of the strategy's capital, not of borrowing capacity.
    """
    if gate_decision["decision"] not in ("PASS", "CONDITIONAL"):
        raise GateNotSatisfiedError(
            f"Risk gate decision was {gate_decision['decision']} — refusing to submit order."
        )
    if not settings.ALPACA_PAPER:
        raise GateNotSatisfiedError("ALPACA_PAPER is not true — refusing to submit any order.")
    if side not in ("buy", "sell"):
        raise ValueError(f"Invalid side: {side}")

    client = get_alpaca_client()
    account = client.get_account()
    notional = round(account["portfolio_value"] * (notional_pct_of_equity / 100.0), 2)

    # CONDITIONAL gate trades at reduced size — half the requested notional — per section 8.
    if gate_decision["decision"] == "CONDITIONAL":
        notional = round(notional * 0.5, 2)

    if notional <= 0:
        raise GateNotSatisfiedError("Computed order notional is $0 — check portfolio value / position size.")

    try:
        order = client.submit_market_order(symbol, notional, side)
    except AlpacaClientError:
        raise  # already a clear, specific error from the client — don't rewrap it

    order["gate_decision"] = gate_decision["decision"]
    return order
