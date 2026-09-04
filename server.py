"""
server.py — Lightweight Flask API over ai_models.db
Endpoints:
  GET  /api/models          — all models (supports ?provider=&min_elo=&max_input=&q=)
  GET  /api/models/<id>     — single model by id
  GET  /api/providers       — distinct provider list
  POST /api/models          — insert a new model  { model, provider, elo, input, input_cache, output }
  PUT  /api/models/<id>     — update a model
  DELETE /api/models/<id>   — delete a model
Pricing fields (per 1M tokens):
  input       — input price
  input_cache — cached input price (e.g. prompt caching)
  output      — output price
"""

import sqlite3, json, os
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_models.db")
HTML_FILE = "ai_benchmark_explorer.html"


def _init_db_if_needed():
    """Create/seed DB on first boot (ephemeral FS on PaaS like Render)."""
    need = True
    if os.path.exists(DB_PATH):
        try:
            con = sqlite3.connect(DB_PATH)
            cur = con.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='models'")
            need = cur.fetchone()[0] == 0
            if not need:
                cur = con.execute("SELECT COUNT(*) FROM models")
                need = cur.fetchone()[0] == 0
            con.close()
        except Exception:
            need = True
    if need:
        try:
            import seed_db
            seed_db.seed()
            print(f"DB initialized at {DB_PATH}")
        except Exception as e:
            print(f"DB init failed: {e}")


# run once at import (gunicorn) and on direct run
try:
    _init_db_if_needed()
except Exception:
    pass


def _ensure_price_columns(db):
    """Auto-migrate old DBs that only have `input` column."""
    cols = {r[1] for r in db.execute("PRAGMA table_info(models)").fetchall()}
    if "input_cache" not in cols:
        db.execute("ALTER TABLE models ADD COLUMN input_cache REAL NOT NULL DEFAULT 0")
    if "output" not in cols:
        db.execute("ALTER TABLE models ADD COLUMN output REAL NOT NULL DEFAULT 0")
    # backfill zeros with derived values if needed
    if "input_cache" not in cols or "output" not in cols:
        for row in db.execute("SELECT id, input, input_cache, output FROM models").fetchall():
            need_cache = row["input_cache"] is None or row["input_cache"] == 0
            need_out = row["output"] is None or row["output"] == 0
            if need_cache or need_out:
                inp = float(row["input"] or 0)
                cache = round(max(0.01, inp * 0.25), 4) if need_cache else row["input_cache"]
                if inp >= 5:
                    out = round(inp * 3.0, 2)
                elif inp < 0.5:
                    out = round(inp * 4.0, 2)
                else:
                    out = round(inp * 2.5, 2)
                out = out if need_out else row["output"]
                db.execute("UPDATE models SET input_cache=?, output=? WHERE id=?", [cache, out, row["id"]])
        db.commit()


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        try:
            _ensure_price_columns(db)
        except sqlite3.OperationalError:
            pass  # table doesn't exist yet (first run before seed)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def row_to_dict(row):
    return dict(row)


# ── GET /api/providers ────────────────────────────────────────────────────────
@app.get("/api/providers")
def get_providers():
    cur = get_db().execute("SELECT DISTINCT provider FROM models ORDER BY provider")
    return jsonify([r["provider"] for r in cur.fetchall()])


# ── GET /api/models ───────────────────────────────────────────────────────────
@app.get("/api/models")
def get_models():
    q          = request.args.get("q", "").strip()
    provider   = request.args.get("provider", "").strip()
    min_elo    = request.args.get("min_elo",  type=float, default=0)
    max_input  = request.args.get("max_input",  type=float, default=None)
    max_daily  = request.args.get("max_daily_cost", type=float, default=None)

    # daily cost = ((2000*input_cache + 50*output)/1e6)*1200 = (2000*input_cache+50*output)*0.0012
    # support both max_input (legacy per-1M filter) and max_daily_cost (new X-axis)
    sql    = "SELECT *, ((2000*input_cache + 50*output)*0.0012) AS daily_cost FROM models WHERE elo >= ?"
    params = [min_elo]

    if max_daily is not None:
        sql += " AND ((2000*input_cache + 50*output)*0.0012) <= ?"
        params.append(max_daily)
    elif max_input is not None:
        sql += " AND input <= ?"
        params.append(max_input)

    if provider and provider != "ALL":
        sql += " AND provider = ?"
        params.append(provider)

    if q:
        sql += " AND (model LIKE ? OR provider LIKE ?)"
        like = f"%{q}%"
        params += [like, like]

    sql += " ORDER BY elo DESC"
    cur = get_db().execute(sql, params)
    return jsonify([row_to_dict(r) for r in cur.fetchall()])


# ── GET /api/models/<id> ──────────────────────────────────────────────────────
@app.get("/api/models/<int:model_id>")
def get_model(model_id):
    cur = get_db().execute("SELECT * FROM models WHERE id = ?", [model_id])
    row = cur.fetchone()
    if row is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(row_to_dict(row))


# ── POST /api/models ──────────────────────────────────────────────────────────
@app.post("/api/models")
def create_model():
    data = request.get_json(force=True)
    try:
        inp = float(data["input"])
        # support both snake and legacy keys, with sensible defaults
        input_cache = data.get("input_cache", data.get("inputCache", data.get("cached_input", None)))
        output_price = data.get("output", data.get("output_price", data.get("outputPrice", None)))
        if input_cache is None:
            input_cache = round(max(0.01, inp * 0.25), 4)
        else:
            input_cache = float(input_cache)
        if output_price is None:
            output_price = round(inp * 3.0, 2) if inp >= 5 else round(inp * 4.0, 2) if inp < 0.5 else round(inp * 2.5, 2)
        else:
            output_price = float(output_price)

        db = get_db()
        cur = db.execute(
            "INSERT INTO models (model, provider, elo, input, input_cache, output) VALUES (?, ?, ?, ?, ?, ?)",
            [data["model"], data["provider"], int(data["elo"]), inp, input_cache, output_price]
        )
        db.commit()
        return jsonify({"id": cur.lastrowid, "message": "Created"}), 201
    except (KeyError, ValueError) as e:
        return jsonify({"error": str(e)}), 400


# ── PUT /api/models/<id> ──────────────────────────────────────────────────────
@app.put("/api/models/<int:model_id>")
def update_model(model_id):
    data = request.get_json(force=True)
    db = get_db()
    cur = db.execute("SELECT * FROM models WHERE id = ?", [model_id])
    existing = cur.fetchone()
    if existing is None:
        return jsonify({"error": "Not found"}), 404
    try:
        # allow partial updates — fallback to existing values
        model = data.get("model", existing["model"])
        provider = data.get("provider", existing["provider"])
        elo = int(data.get("elo", existing["elo"]))
        inp = float(data.get("input", existing["input"]))
        input_cache = data.get("input_cache", data.get("inputCache", data.get("cached_input", existing["input_cache"])))
        output_price = data.get("output", data.get("output_price", data.get("outputPrice", existing["output"])))
        input_cache = float(input_cache)
        output_price = float(output_price)
        # if caller updated input but didn't explicitly update derived prices, keep existing derived unless they were default
        db.execute(
            "UPDATE models SET model=?, provider=?, elo=?, input=?, input_cache=?, output=? WHERE id=?",
            [model, provider, elo, inp, input_cache, output_price, model_id]
        )
        db.commit()
        return jsonify({"message": "Updated"})
    except (ValueError, KeyError) as e:
        return jsonify({"error": str(e)}), 400


# ── DELETE /api/models/<id> ───────────────────────────────────────────────────
@app.delete("/api/models/<int:model_id>")
def delete_model(model_id):
    db = get_db()
    cur = db.execute("SELECT id FROM models WHERE id = ?", [model_id])
    if cur.fetchone() is None:
        return jsonify({"error": "Not found"}), 404
    db.execute("DELETE FROM models WHERE id = ?", [model_id])
    db.commit()
    return jsonify({"message": "Deleted"})


# ── Frontend + health ───────────────────────────────────────────────────────
@app.get("/")
def serve_frontend():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), HTML_FILE)


@app.get("/health")
def health():
    try:
        c = get_db().execute("SELECT COUNT(*) FROM models").fetchone()[0]
        return jsonify({"status": "ok", "models": c})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)
