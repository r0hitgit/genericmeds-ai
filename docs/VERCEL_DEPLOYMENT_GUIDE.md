# Vercel Deployment Guide for GenericMeds AI

This repository is pre-configured for full-stack deployment on **Vercel** combining a **FastAPI** serverless backend and a high-performance **Vite + React** single-page application.

---

## Architecture Overview on Vercel

```
Incoming Request
       │
       ▼
 ┌────────────── Vercel Edge Network ──────────────┐
 │                                                 │
 │  Static Files (/assets/*, /favicon.*, /)        │
 │  ─► Served directly from Edge CDN               │
 │     (Zero latency, 0ms cold starts)             │
 │                                                 │
 │  API Routes (/api/*, /health, /docs)            │
 │  ─► Rewritten to Serverless Python Function     │
 │     api/index.py (FastAPI ASGI Runtime)         │
 │                                                 │
 └─────────────────────────────────────────────────┘
```

---

## Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to GitHub**:
   Ensure all changes are pushed to your repository:
   ```bash
   git push origin main
   ```

2. **Open Vercel**:
   Go to [vercel.com/new](https://vercel.com/new) and log in with your GitHub account.

3. **Import Project**:
   - Find and select **`r0hitgit/genericmeds-ai`**.
   - Click **Import**.

4. **Project Settings**:
   - **Framework Preset**: *Other* (detected automatically via `vercel.json`).
   - **Root Directory**: `./` (leave default).
   - **Build Command**: `cd frontend && npm install && npm run build` (detected automatically).
   - **Output Directory**: `app/static` (detected automatically).

5. **Environment Variables (Optional)**:
   Add any of the following variables in the Vercel dashboard:
   | Key | Value / Purpose |
   |---|---|
   | `GEMINI_API_KEY` | *(Optional)* Google Gemini API key for live AI Clinical Assistant responses |
   | `LLM_PROVIDER` | `gemini` (or `mock` for local simulation) |
   | `ENVIRONMENT` | `production` |
   | `ADMIN_API_KEY` | Your secret admin key for data management routes |

6. **Deploy**:
   - Click **Deploy**.
   - Vercel will install frontend dependencies, build static assets, package Python serverless functions, and generate your live deployment URL (e.g., `https://genericmeds-ai.vercel.app`).

---

## Method 2: Deploy via Terminal (CLI)

You can deploy directly from your local terminal using `npx`:

```bash
# 1. Login to Vercel (first time only)
npx vercel login

# 2. Deploy preview build
npx vercel

# 3. Deploy to production
npx vercel --prod
```

---

## Key Files Configured

- **[`vercel.json`](file:///Users/rohitverma/.gemini/antigravity/scratch/genericmeds-ai/vercel.json)**:
  Defines build command, output directory, and rewrites `/api/*`, `/health`, and `/docs` to `api/index.py`.
- **[`api/index.py`](file:///Users/rohitverma/.gemini/antigravity/scratch/genericmeds-ai/api/index.py)**:
  Exposes the FastAPI instance (`app`) for Vercel's Python serverless execution environment.
- **[`package.json`](file:///Users/rohitverma/.gemini/antigravity/scratch/genericmeds-ai/package.json)**:
  Provides root `build` and `vercel-build` scripts.
- **[`app/core/config.py`](file:///Users/rohitverma/.gemini/antigravity/scratch/genericmeds-ai/app/core/config.py)**:
  Automatically detects serverless environments (`VERCEL=1`) and mounts the SQLite catalogue safely into `/tmp` partition for maximum read/write performance.
- **[`genericmeds.db`](file:///Users/rohitverma/.gemini/antigravity/scratch/genericmeds-ai/genericmeds.db)**:
  Pre-seeded 12MB database with over 2,500 medicines, bioequivalent alternatives, and verified Jan Aushadhi Kendras.
