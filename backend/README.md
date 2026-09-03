# GAUNTLET — backend

FastAPI service that runs the full pipeline: compile a natural-language
strategy, backtest it, attack it with five crash tests, score it, gate it,
and (if allowed) submit a paper trade. Every score/scoring number is plain
pandas/numpy math — the only two places an LLM is involved are the strategy
compiler (turns English into the strict `Strategy` contract) and the crash
analyst (explains already-computed numbers in prose; it can't change them).

## Setup

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate      # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp ../.env.example ../.env  # fill in the values below
uvicorn app:app --reload --port 8000
```

Opens on `http://localhost:8000`. Interactive docs at `/docs` — usable as a
demo surface without the frontend if anything misbehaves live.

## Environment variables

All config is loaded once in `config.py` — nothing else reads `os.environ`
directly. Set these in `.env` at the repo root (shared with the frontend's
`../.env.example`, but the frontend only needs `VITE_API_URL`):

| Variable | Required | Notes |
|---|---|---|
| `ALPACA_API_KEY` / `ALPACA_SECRET_KEY` | yes | Alpaca **paper** trading keys — https://app.alpaca.markets/paper/dashboard/overview |
| `ALPACA_PAPER` | yes | Must be `true`. The backend hard-blocks startup and every order path if it isn't — this build does not support live trading. |
| `ALPACA_DATA_FEED` | no | `iex` (default, free) or `sip` if your account is entitled to it |
| `LLM_API_KEY` | yes | Gemini API key (from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)), used by the strategy compiler and crash analyst agents |
| `LLM_MODEL` | no | Defaults to `gemini-3.6-flash` if unset |
| `ROBUSTNESS_MIN_PASS` / `ROBUSTNESS_MIN_CONDITIONAL` | no | Risk gate score thresholds (spec §7-8), default 80 / 60 |
| `MAX_DRAWDOWN_LIMIT_PCT` / `MAX_POSITION_SIZE_PCT` | no | Risk gate hard limits, default 20% / 10% |
| `CRASH_TEST_ALLOWED_ORIGINS` | no | Comma-separated CORS allowlist for browser origins, default covers `localhost:5173` |

Hitting `GET /verify-alpaca` after startup is the fastest way to check your
keys are correct — it returns account info and a sample bar count, or a
clear `config_problems` list if something's missing.

## Structure

```
app.py              FastAPI routes — one per pipeline stage
agents/              strategy_compiler.py (NL -> Strategy contract), crash_analyst.py (results -> prose), llm_client.py (single Gemini call site)
alpaca_client.py     single point of contact with Alpaca — data + paper order submission
backtest/            deterministic engine, metrics, SMA-cross signal generation
crash/               the 5 stress tests + engine.py that weights them into the robustness score
risk/gate.py         deterministic PASS/CONDITIONAL/BLOCK decision — no LLM involved
trading/             paper.py (order submission, re-checks the gate itself), monitor.py (post-trade failure-regime alerts)
db/database.py       SQLite audit trail (backend/crash_test.db, gitignored) — every run, score, gate decision, and order
models/strategy.py   the pydantic contracts (Strategy, CrashTestResult) everything else is validated against
```

## Running tests

No automated test suite exists yet (the top-level `tests/` directory is a
placeholder). `/docs` (Swagger UI) is the current way to manually exercise
each endpoint against real Alpaca paper data.

## Deploying (Railway / Render)

Point the service at `backend/`, start command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Set every env var from the table above (real Alpaca paper keys + LLM key),
and add your deployed frontend's URL to `CRASH_TEST_ALLOWED_ORIGINS`.
