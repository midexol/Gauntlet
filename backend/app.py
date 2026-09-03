"""
GAUNTLET backend — full pipeline.

Idea -> Strategy -> Attack -> Robustness -> Gate -> Paper Trade -> Monitor

Run: uvicorn app:app --reload
Docs: http://localhost:8000/docs  (usable as a demo surface without a frontend)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.crash_analyst import explain as crash_analyst_explain
from agents.strategy_compiler import compile_strategy
from alpaca_client import AlpacaClientError, get_alpaca_client
from backtest.engine import run_backtest
from backtest.metrics import compute_metrics
from config import settings
from crash.engine import run_all as run_crash_tests
from db import database
from models.strategy import Strategy
from risk.gate import evaluate_gate
from trading.monitor import check_failure_regime
from trading.paper import GateNotSatisfiedError, submit_paper_order

app = FastAPI(title="GAUNTLET", version="0.2.0")

# The frontend (Vite dev server / deployed static host) runs on a different
# origin than this API, so the browser needs explicit CORS permission.
# CRASH_TEST_ALLOWED_ORIGINS is a comma-separated list; defaults cover local dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- health / connectivity ----------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/verify-alpaca")
def verify_alpaca():
    problems = settings.validate()
    if problems:
        raise HTTPException(status_code=500, detail={"config_problems": problems})
    try:
        client = get_alpaca_client()
        account = client.get_account()
        bars = client.get_daily_bars("NVDA", days_back=60)
        return {"account": account, "sample_symbol": "NVDA", "bars_returned": len(bars), "paper_mode": settings.ALPACA_PAPER}
    except AlpacaClientError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 1. compile ----------

class CompileRequest(BaseModel):
    description: str


@app.post("/compile-strategy")
def compile_strategy_endpoint(req: CompileRequest):
    result = compile_strategy(req.description)
    if not result["ok"]:
        raise HTTPException(status_code=422, detail={"error": result["error"], "reason": result["reason"]})
    strategy: Strategy = result["strategy"]
    run_id = database.create_run(strategy.model_dump())
    return {"run_id": run_id, "strategy": strategy.model_dump()}


# ---------- 2 & 3. backtest + crash test (run together — the score needs both) ----------

@app.post("/crash-test/{run_id}")
def crash_test_endpoint(run_id: int):
    record = database.get_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run_id not found")

    strategy = Strategy(**record["strategy_json"])
    try:
        client = get_alpaca_client()
        bars_df = client.get_daily_bars(strategy.symbol, days_back=400)
    except AlpacaClientError as e:
        raise HTTPException(status_code=502, detail=str(e))

    baseline = run_backtest(bars_df, strategy)
    baseline_metrics = compute_metrics(baseline["equity_curve"], baseline["trades"], baseline["benchmark_curve"])

    # Override the self-referential buy&hold benchmark with the strategy's actual
    # stated benchmark (e.g. QQQ), aligned to the same date range as the traded symbol.
    try:
        benchmark_df = client.get_daily_bars(strategy.benchmark, days_back=400)
        benchmark_df = benchmark_df.loc[
            (benchmark_df.index >= bars_df.index.min()) & (benchmark_df.index <= bars_df.index.max())
        ]
        if len(benchmark_df) >= 2:
            benchmark_return_pct = (benchmark_df["close"].iloc[-1] / benchmark_df["close"].iloc[0] - 1) * 100
            baseline_metrics["benchmark_symbol"] = strategy.benchmark
            baseline_metrics["benchmark_return_pct"] = round(float(benchmark_return_pct), 3)
    except AlpacaClientError:
        # Benchmark symbol unavailable — keep the traded-symbol buy&hold fallback
        # already in baseline_metrics rather than failing the whole crash test.
        baseline_metrics["benchmark_symbol"] = f"{strategy.symbol} (buy&hold fallback — {strategy.benchmark} unavailable)"

    crash_summary = run_crash_tests(bars_df, strategy)

    database.update_run(run_id, crash_test_summary=crash_summary)
    return {"run_id": run_id, "baseline_metrics": baseline_metrics, "crash_test_summary": crash_summary}


@app.get("/crash-test/{run_id}/explain")
def crash_test_explain_endpoint(run_id: int):
    record = database.get_run(run_id)
    if record is None or record["crash_test_summary_json"] is None:
        raise HTTPException(status_code=404, detail="run_id not found or crash test not yet run")
    result = crash_analyst_explain(record["crash_test_summary_json"])
    if not result["ok"]:
        raise HTTPException(status_code=502, detail={"error": result["error"], "reason": result["reason"]})
    return {"run_id": run_id, "explanation": result["explanation"]}


# ---------- 4. gate ----------

@app.post("/risk-gate/{run_id}")
def risk_gate_endpoint(run_id: int):
    record = database.get_run(run_id)
    if record is None or record["crash_test_summary_json"] is None:
        raise HTTPException(status_code=404, detail="run_id not found or crash test not yet run")

    strategy = Strategy(**record["strategy_json"])
    decision = evaluate_gate(record["crash_test_summary_json"], strategy.position_size_pct, settings.ALPACA_PAPER)
    database.update_run(run_id, gate_decision=decision)
    return {"run_id": run_id, "gate_decision": decision}


# ---------- 5. paper trade ----------

class PaperTradeRequest(BaseModel):
    side: str = "buy"


@app.post("/paper-trade/{run_id}")
def paper_trade_endpoint(run_id: int, req: PaperTradeRequest):
    record = database.get_run(run_id)
    if record is None or record["gate_decision_json"] is None:
        raise HTTPException(status_code=404, detail="run_id not found or gate not yet evaluated")

    strategy = Strategy(**record["strategy_json"])
    try:
        order = submit_paper_order(strategy.symbol, strategy.position_size_pct, req.side, record["gate_decision_json"])
    except GateNotSatisfiedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except AlpacaClientError as e:
        raise HTTPException(status_code=502, detail=str(e))

    database.update_run(run_id, order=order)
    return {"run_id": run_id, "order": order}


# ---------- 6. monitor ----------

@app.get("/monitor/{run_id}")
def monitor_endpoint(run_id: int):
    record = database.get_run(run_id)
    if record is None or record["crash_test_summary_json"] is None:
        raise HTTPException(status_code=404, detail="run_id not found or crash test not yet run")

    strategy = Strategy(**record["strategy_json"])
    try:
        client = get_alpaca_client()
        recent_df = client.get_daily_bars(strategy.symbol, days_back=30)
    except AlpacaClientError as e:
        raise HTTPException(status_code=502, detail=str(e))

    alert = check_failure_regime(recent_df, strategy, record["crash_test_summary_json"])
    return {"run_id": run_id, **alert}


# ---------- audit trail ----------

@app.get("/runs")
def list_runs_endpoint(limit: int = 20):
    return database.list_runs(limit)


@app.get("/runs/{run_id}")
def get_run_endpoint(run_id: int):
    record = database.get_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run_id not found")
    return record
