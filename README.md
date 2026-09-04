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

## Quick Start

```bash
# 1. Install dependencies
pip install flask flask-cors

# 2. Seed the database (already included, but re-run to reset)
python3 seed_db.py

# 3. Start the API server
python3 server.py

# 4. Open the frontend
open ai_benchmark_explorer.html
```

The HTML connects to `http://localhost:5050/api` automatically.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/models` | All models — supports `?q=`, `?provider=`, `?min_elo=`, `?max_input=` |
| `GET` | `/api/models/<id>` | Single model by ID |
| `GET` | `/api/providers` | Distinct provider list |
| `POST` | `/api/models` | Add a model `{ model, provider, elo, input }` |
| `PUT` | `/api/models/<id>` | Update a model |
| `DELETE` | `/api/models/<id>` | Delete a model |

### Example

```bash
# Get all OpenAI models with Elo ≥ 1400
curl "http://localhost:5050/api/models?provider=OpenAI&min_elo=1400"

# Add a new model
curl -X POST http://localhost:5050/api/models \
  -H "Content-Type: application/json" \
  -d '{"model":"GPT-6","provider":"OpenAI","elo":1550,"input":10.00}'
```

## Data Sources

- Arena Elo ratings: [Chatbot Arena / LMArena](https://arena.ai) (as of early September 2026)
- Pricing: [BenchLM](https://benchlm.ai), [Morph](https://morphllm.com/openai-api-pricing), official provider docs

## Stack

- **Frontend**: Vanilla JS, Chart.js (CDN)
- **Backend**: Python 3, Flask, Flask-CORS
- **Database**: SQLite 3 (via Python `sqlite3` stdlib)
