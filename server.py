"""
server.py — Lightweight Flask API over ai_models.db
Endpoints:
  GET  /api/models          — all models (supports ?provider=&min_elo=&max_input=&q=)
  GET  /api/models/<id>     — single model by id
  GET  /api/providers       — distinct provider list
  POST /api/models          — insert a new model  { model, provider, elo, input }
  PUT  /api/models/<id>     — update a model
  DELETE /api/models/<id>   — delete a model
"""

import sqlite3, json
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = "/home/claude/ai_models.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
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
    max_input  = request.args.get("max_input", type=float, default=9999)

    sql    = "SELECT * FROM models WHERE elo >= ? AND input <= ?"
    params = [min_elo, max_input]

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
        db = get_db()
        cur = db.execute(
            "INSERT INTO models (model, provider, elo, input) VALUES (?, ?, ?, ?)",
            [data["model"], data["provider"], int(data["elo"]), float(data["input"])]
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
    cur = db.execute("SELECT id FROM models WHERE id = ?", [model_id])
    if cur.fetchone() is None:
        return jsonify({"error": "Not found"}), 404
    db.execute(
        "UPDATE models SET model=?, provider=?, elo=?, input=? WHERE id=?",
        [data["model"], data["provider"], int(data["elo"]), float(data["input"]), model_id]
    )
    db.commit()
    return jsonify({"message": "Updated"})


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
