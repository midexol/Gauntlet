# GAUNTLET — frontend

A real dashboard wired to the GAUNTLET backend — every number on screen
comes from a live API call, nothing is mocked. Built with Vite + React +
TypeScript + Tailwind v4, self-hosted fonts (no external CDN dependency
during a demo).

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL if the backend isn't on localhost:8000
npm run dev
```

Opens on `http://localhost:5173`. Make sure the backend is running first
(see `../backend/README.md`) and that `CRASH_TEST_ALLOWED_ORIGINS` in the
backend's `.env` includes `http://localhost:5173` (it does by default).

## What's real vs what's a placeholder

- Every score, gate decision, metric, and order on screen is a live response
  from your backend — the hero's example gauge (89.7) is the only
  hardcoded number in the app, clearly labeled as an example.
- The GitHub link in the hero points to https://github.com/midexol/Gauntlet.

## Production build

```bash
npm run build      # outputs to dist/
npm run preview    # serve the production build locally to sanity-check it
```

## Deploying for the hackathon submission

lablab.ai requires a working prototype reachable by URL. Two free options
that work well for a weekend:

**Frontend:**
- **Netlify**: the repo root has a `netlify.toml` (base `frontend/`,
  build `npm run build`, publish `dist`) — connect the repo and it's
  preconfigured. Add `VITE_API_URL` (your deployed backend's URL) in
  Site settings > Environment variables.
- **Vercel**: connect the repo, set Root Directory to `frontend/` in
  the project settings (Vercel auto-detects Vite for the rest), and
  add `VITE_API_URL` as an environment variable.

**Backend:** see `backend/README.md`'s deploy section — a `render.yaml`
blueprint and a `backend/Procfile` (for Railway) are both in the repo.
Whichever you use, add your deployed frontend's URL to
`CRASH_TEST_ALLOWED_ORIGINS` once you have it.

Once both are live, `/docs` on your backend also works as a fallback demo
surface if anything in the frontend misbehaves live on stage.
