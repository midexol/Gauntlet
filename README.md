# GAUNTLET

Don't ask AI what to trade. Ask it whether your strategy deserves to trade.

An adversarial AI strategy-validation layer built for the Alpaca AI Trading
Agents Hackathon (Aug 28 – Sep 4, 2026). Compiles a natural-language trading
strategy into explicit rules, backtests it, attacks it with five independent
stress tests, produces a Strategy Robustness Score, and gates paper-trading
execution behind a deterministic risk gate.

Idea → Strategy → Attack → Robustness → Gate → Paper Trade → Monitor

## Structure

```
backend/    FastAPI + Alpaca + the crash-test pipeline (see backend/README.md)
frontend/   React dashboard wired to the live backend (see frontend/README.md)
dev.sh      Runs both together for local development
```

## Quickest path to running it locally

```bash
# backend
cd backend && pip install -r requirements.txt
cp ../.env.example ../.env   # fill in Alpaca paper keys + LLM key
cd ..

# frontend
cd frontend && npm install
cp .env.example .env
cd ..

# both together
./dev.sh
```

Then open `http://localhost:5173`. First thing to check: the green
"Alpaca connected" dot near the top of the page — if it's red, your keys
in `.env` need fixing before anything else will work.

## Non-goals

No live-money trading (hard-blocked at three separate points in the
backend). No options. No ML price prediction. Strategy compiler MVP
scope is SMA-crossover only.

## Submission checklist (lablab.ai)

- [ ] Deploy backend (Railway/Render) and frontend (Vercel/Netlify) — see
      `frontend/README.md` for the specifics
- [ ] Public GitHub repo
- [ ] Demo video (≤5 min, MP4)
- [ ] Slide deck (PDF)
- [ ] Check your team dashboard's submission form for any Alpaca-specific
      extra requirements before the Sep 4 15:00 UTC deadline
