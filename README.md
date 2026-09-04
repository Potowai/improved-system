# AI Benchmark & Price Explorer

An interactive dashboard comparing **Chatbot Arena Elo ratings** vs **API pricing** for 110+ LLMs — with a SQLite backend and a Flask REST API.

![screenshot](https://img.shields.io/badge/models-112-blue) ![stack](https://img.shields.io/badge/stack-HTML%20%7C%20Flask%20%7C%20SQLite-orange)

## Features

- 📊 Interactive scatter chart (Chart.js) — Elo vs price, logarithmic or linear scale
- 🔍 Filter by provider, search, min Elo, max price
- 🗄️ SQLite database with full CRUD REST API (Flask)
- 🔄 HTML auto-connects to live API; falls back to built-in data if server is offline
- 110+ models covered: OpenAI GPT-5.x, Anthropic Claude 4.x/5.x, Google Gemini, Meta, DeepSeek, Mistral, Alibaba Qwen, and more

## Files

| File | Description |
|------|-------------|
| `ai_benchmark_explorer.html` | Frontend — open in any browser |
| `server.py` | Flask REST API (port 5050) |
| `seed_db.py` | Seeds `ai_models.db` with all 112 models |
| `ai_models.db` | Pre-seeded SQLite database |

## Quick Start (local)

```bash
# 1. Install dependencies
pip install -r requirements.txt   # flask, flask-cors, gunicorn

# 2. Seed the database (already included, but re-run to reset)
python seed_db.py

# 3. Start the API server (also serves the frontend at http://localhost:5050/)
python server.py
# → open http://localhost:5050/ in your browser
# Windows alt: waitress-serve --listen=0.0.0.0:5050 server:app

# 4. Or open the file directly (uses localhost:5050/api as fallback)
open ai_benchmark_explorer.html
```

The app auto-seeds `ai_models.db` on first boot, so no manual seeding is needed in production.

## Deploy

This repo is ready to deploy as a **single service** (Flask serves both `/api` and the HTML at `/`). All configs are included: `Dockerfile`, `requirements.txt`, `Procfile`, `render.yaml`, `fly.toml`.

### Option 1 — Render (free, 1-click, recommended)

1. Push to GitHub (already at `Potowai/improved-system`)
2. Go to https://dashboard.render.com → **New + → Blueprint** → connect the repo
3. Render reads `render.yaml` and creates the service. Build/start are:
   ```yaml
   buildCommand: pip install -r requirements.txt && python seed_db.py
   startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 server:app
   ```
4. Or manual: **New Web Service** → Python → set build/start above, health check `/health`.

Frontend will be at `https://<your-app>.onrender.com/` and API at `https://<your-app>.onrender.com/api`.

### Option 2 — Fly.io

```bash
fly launch --no-deploy   # picks up fly.toml
fly deploy
fly open
```
Uses `Dockerfile` (python:3.11-slim + gunicorn). Scale: `fly scale memory 512`.

### Option 3 — Railway / Heroku-like PaaS

Railway / Heroku / Koyeb auto-detect `Procfile`:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 server:app
```
Set env `PORT` (auto) and deploy from GitHub. No extra config.

### Option 4 — Docker (self-host / VPS / Coolify)

```bash
docker build -t ai-explorer .
docker run -p 5050:5050 ai-explorer
# → http://localhost:5050
```

Or `docker compose`:
```yaml
services:
  app:
    build: .
    ports: ["5050:5050"]
```

### Option 5 — GitHub Pages (frontend only)

Frontend works without the API (falls back to built-in `rawModels` with derived `input_cache`/`output`):
```bash
git checkout --orphan gh-pages
cp ai_benchmark_explorer.html index.html
git add index.html && git commit -m "gh-pages" && git push origin gh-pages
```
Set Pages → Source `gh-pages`. For live DB, point `?api=https://your-api.onrender.com/api` or host the API separately.

### Env

- `PORT` — server port (default 5050, Render/Fly/Railway set it automatically)
- SQLite file `ai_models.db` is ephemeral on free tiers; it auto-reseeds if missing via `seed_db.py`.

### Verify deploy

```bash
curl https://your-app.onrender.com/health
# {"status":"ok","models":112}
curl "https://your-app.onrender.com/api/models?max_daily_cost=2&provider=OpenAI"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Frontend (`ai_benchmark_explorer.html`) |
| `GET` | `/health` | Health check → `{"status":"ok","models":112}` |
| `GET` | `/api/models` | All models — supports `?q=`, `?provider=`, `?min_elo=`, `?max_daily_cost=` (legacy `?max_input=`) |
| `GET` | `/api/models/<id>` | Single model by ID |
| `GET` | `/api/providers` | Distinct provider list |
| `POST` | `/api/models` | Add a model `{ model, provider, elo, input, input_cache, output }` |
| `PUT` | `/api/models/<id>` | Update a model |
| `DELETE` | `/api/models/<id>` | Delete a model |

X-axis / filter is **estimated daily cost**: `((2000*input_cache + 50*output)/1M)*1200` = `(2000 cached + 50 out) ×50×24`.

### Example

```bash
# Get all OpenAI models with Elo ≥ 1400 and daily cost ≤ $5 (1200 req/day)
curl "http://localhost:5050/api/models?provider=OpenAI&min_elo=1400&max_daily_cost=5"

# Add a new model (input_cache/output auto-derived if omitted)
curl -X POST http://localhost:5050/api/models \
  -H "Content-Type: application/json" \
  -d '{"model":"GPT-6","provider":"OpenAI","elo":1550,"input":10.00,"input_cache":2.5,"output":30}'

# Health
curl http://localhost:5050/health
```

## Data Sources

- Arena Elo ratings: [Chatbot Arena / LMArena](https://arena.ai) (as of early September 2026)
- Pricing: [BenchLM](https://benchlm.ai), [Morph](https://morphllm.com/openai-api-pricing), official provider docs

## Stack

- **Frontend**: Vanilla JS, Chart.js (CDN)
- **Backend**: Python 3, Flask, Flask-CORS
- **Database**: SQLite 3 (via Python `sqlite3` stdlib)
