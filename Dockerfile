# Production image for the AI Benchmark Explorer
FROM python:3.11-slim

WORKDIR /app

# System deps (sqlite is built-in, but add curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Seed DB at build time so image is ready (also auto-seeds at runtime if missing)
RUN python seed_db.py || true

EXPOSE 5050
ENV PORT=5050
ENV PYTHONUNBUFFERED=1

# Use gunicorn for production (2 workers, safe for SQLite reads)
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "2", "--timeout", "60", "server:app"]
