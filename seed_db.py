"""
seed_db.py — Creates ai_models.db and seeds it with all rawModels data.
Run once (or re-run to reset): python3 seed_db.py
"""

import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_models.db")

RAW_MODELS = [
    # ── 2026 Frontier Giants ─────────────────────────────────────────────────
    ("Claude Fable 5.1",            "Anthropic",   1507, 10.00),
    ("Claude Fable 5.1 Max",        "Anthropic",   1504, 15.00),
    ("Claude Opus 4.6 (High)",      "Anthropic",   1505,  5.00),
    ("Claude Opus 4.7 (High)",      "Anthropic",   1502,  5.00),
    ("Muse Spark 1.2 (xHigh)",      "Meta",        1499,  1.25),
    ("Claude Opus 4.6",             "Anthropic",   1498,  5.00),
    ("Grok 4.6",                    "xAI",         1496,  2.00),
    ("Claude Opus 4.7",             "Anthropic",   1494,  5.00),
    ("Gemini 3.8 Flash High",       "Google",      1494,  0.75),
    ("Claude Opus 5 (High)",        "Anthropic",   1493,  5.00),
    ("Muse Spark 1.1",              "Meta",        1492,  1.25),
    ("Gemini 3.7 Flash High",       "Google",      1491,  0.75),
    ("Kimi K3 Max",                 "Moonshot AI", 1489,  3.00),
    ("Claude Sonnet 5 (High)",      "Anthropic",   1486,  2.00),
    ("GPT-5.5",                     "OpenAI",      1485,  5.00),
    ("GPT-5.6 Sol",                 "OpenAI",      1483,  5.00),
    ("GLM 5.3 Max",                 "Zhipu AI",    1482,  1.40),
    ("Qwen 3.8 Max",                "Alibaba",     1480,  2.00),
    ("Gemini 3.1 Pro",              "Google",      1480,  2.00),
    ("GPT-5.6 Terra",               "OpenAI",      1479,  2.00),
    ("Muse Spark",                  "Meta",        1474,  1.25),
    ("GLM 5.3 Flash",               "Zhipu AI",    1473,  0.15),
    ("Gemini 3.5 Flash",            "Google",      1470,  1.50),
    ("Ernie 5.1",                   "Baidu",       1468,  0.59),
    ("GLM 5.2 (Max)",               "Zhipu AI",    1468,  1.40),
    ("DeepSeek V4 Pro",             "DeepSeek",    1460,  0.43),
    ("GPT-5.6 Luna",                "OpenAI",      1445,  0.20),
    ("DeepSeek V4 Flash",           "DeepSeek",    1435,  0.14),
    ("DeepSeek V3.2",               "DeepSeek",    1423,  0.28),
    ("Mistral Large 3",             "Mistral",     1420,  3.00),
    ("Qwen 3.8-Flash-Next",         "Alibaba",     1410,  0.20),
    ("Llama 4 Scout",               "Meta",        1400,  0.11),
    ("DeepSeek R1",                 "DeepSeek",    1395,  0.55),
    # ── OpenAI — GPT-5.x family ──────────────────────────────────────────────
    ("GPT-5.5 Pro",                 "OpenAI",      1490, 30.00),
    ("GPT-5.4 Pro",                 "OpenAI",      1480, 30.00),
    ("GPT-5.4",                     "OpenAI",      1473,  2.50),
    ("GPT-5.4 Mini",                "OpenAI",      1440,  0.75),
    ("GPT-5.4 Nano",                "OpenAI",      1415,  0.20),
    ("GPT-5.3",                     "OpenAI",      1460,  1.75),
    ("GPT-5.2",                     "OpenAI",      1445,  1.25),
    ("GPT-5.1",                     "OpenAI",      1430,  1.25),
    ("GPT-5",                       "OpenAI",      1415,  1.25),
    ("GPT-5 Mini",                  "OpenAI",      1385,  0.25),
    ("GPT-5 Nano",                  "OpenAI",      1355,  0.05),
    # ── OpenAI — GPT-4.x & o-series ──────────────────────────────────────────
    ("GPT-4.1",                     "OpenAI",      1310, 10.00),
    ("GPT-4.1 Mini",                "OpenAI",      1285,  0.40),
    ("GPT-4.1 Nano",                "OpenAI",      1260,  0.10),
    ("GPT-4.5 Preview",             "OpenAI",      1300, 75.00),
    ("o4-mini",                     "OpenAI",      1375,  1.10),
    ("o4-mini (High)",              "OpenAI",      1385,  1.10),
    ("o3",                          "OpenAI",      1390,  2.00),
    ("o3-pro",                      "OpenAI",      1400, 20.00),
    ("o3-mini",                     "OpenAI",      1360,  1.10),
    ("o1",                          "OpenAI",      1355, 15.00),
    ("o1-preview",                  "OpenAI",      1335, 15.00),
    ("o1-mini",                     "OpenAI",      1305,  3.00),
    ("GPT-4o",                      "OpenAI",      1286,  2.50),
    ("GPT-4o-mini",                 "OpenAI",      1270,  0.15),
    ("GPT-4 Turbo (0409)",          "OpenAI",      1248, 10.00),
    ("GPT-3.5 Turbo",               "OpenAI",      1110,  0.50),
    # ── Anthropic — Claude 4.x & 5.x ─────────────────────────────────────────
    ("Claude Fable 5",              "Anthropic",   1500, 10.00),
    ("Claude Opus 5",               "Anthropic",   1490,  5.00),
    ("Claude Sonnet 5",             "Anthropic",   1480,  2.00),
    ("Claude Haiku 4.5",            "Anthropic",   1390,  1.00),
    ("Claude Opus 4.8",             "Anthropic",   1478,  5.00),
    ("Claude Opus 4.5",             "Anthropic",   1462,  5.00),
    ("Claude Opus 4.1",             "Anthropic",   1448,  5.00),
    ("Claude Sonnet 4.6",           "Anthropic",   1430,  3.00),
    ("Claude Sonnet 4.5",           "Anthropic",   1415,  3.00),
    ("Claude Sonnet 4",             "Anthropic",   1400,  3.00),
    ("Claude Opus 4",               "Anthropic",   1392,  5.00),
    ("Claude 3.7 Sonnet (Thinking)","Anthropic",   1395,  3.00),
    # ── Anthropic — Claude 3.x legacy ────────────────────────────────────────
    ("Claude 3.5 Sonnet (Oct)",     "Anthropic",   1340,  3.00),
    ("Claude 3.5 Haiku",            "Anthropic",   1250,  0.80),
    ("Claude 3 Opus",               "Anthropic",   1240, 15.00),
    ("Claude 3 Sonnet",             "Anthropic",   1175,  3.00),
    ("Claude 3 Haiku",              "Anthropic",   1155,  0.25),
    ("Claude 2.1",                  "Anthropic",   1120,  8.00),
    # ── Google ────────────────────────────────────────────────────────────────
    ("Gemini 2.0 Flash Thinking",   "Google",      1375,  0.15),
    ("Gemini 2.0 Pro Exp",          "Google",      1360,  0.50),
    ("Gemini 2.0 Flash",            "Google",      1345,  0.10),
    ("Gemini 1.5 Pro (002)",        "Google",      1305,  1.25),
    ("Gemini 1.5 Flash (002)",      "Google",      1260,  0.075),
    ("Gemini 1.5 Flash-8B",         "Google",      1210,  0.0375),
    ("Gemini 1.0 Ultra",            "Google",      1215,  7.00),
    # ── Meta ──────────────────────────────────────────────────────────────────
    ("Llama 3.3 70B Instruct",      "Meta",        1310,  0.60),
    ("Llama 3.1 405B Instruct",     "Meta",        1285,  2.50),
    ("Llama 3.1 70B Instruct",      "Meta",        1255,  0.50),
    ("Llama 3.1 8B Instruct",       "Meta",        1180,  0.10),
    ("Llama 3.2 90B Vision",        "Meta",        1240,  0.90),
    ("Llama 3 70B Instruct",        "Meta",        1210,  0.50),
    ("Llama 2 70B Chat",            "Meta",        1090,  0.70),
    # ── DeepSeek ──────────────────────────────────────────────────────────────
    ("DeepSeek V3",                 "DeepSeek",    1360,  0.14),
    ("DeepSeek V2.5",               "DeepSeek",    1310,  0.14),
    ("DeepSeek Coder V2 (236B)",    "DeepSeek",    1265,  0.14),
    # ── Alibaba Qwen ──────────────────────────────────────────────────────────
    ("Qwen 3.7 Plus",               "Alibaba",     1370,  0.50),
    ("QwQ-32B-Preview",             "Alibaba",     1350,  0.40),
    ("Qwen 2.5 Max",                "Alibaba",     1340,  1.60),
    ("Qwen 2.5 72B Instruct",       "Alibaba",     1260,  0.35),
    ("Qwen 2.5 32B Instruct",       "Alibaba",     1220,  0.20),
    ("Qwen 2 72B Instruct",         "Alibaba",     1225,  0.40),
    # ── Mistral ───────────────────────────────────────────────────────────────
    ("Mistral Large 2 (2407)",      "Mistral",     1300,  2.00),
    ("Pixtral Large 124B",          "Mistral",     1280,  2.00),
    ("Mistral Small 3 (24B)",       "Mistral",     1220,  0.20),
    ("Mixtral 8x22B Instruct",      "Mistral",     1220,  0.90),
    ("Mistral NeMo 12B",            "Mistral",     1195,  0.15),
    # ── Open Source ───────────────────────────────────────────────────────────
    ("Nous Hermes 3 (405B)",        "Open Source", 1280,  2.50),
    ("Jamba 1.5 Large",             "Open Source", 1245,  2.00),
    ("Solar Pro Preview",           "Open Source", 1240,  0.60),
    ("InternLM 2.5 20B",            "Open Source", 1210,  0.25),
    ("DBRX Instruct",               "Open Source", 1195,  0.60),
    ("Snowflake Arctic",            "Open Source", 1180,  0.80),
]

def _derive_prices(input_price: float):
    """Derive plausible cached-input and output prices from a base input price.
    Real-world ratios vary wildly; we use a simple heuristic that looks plausible:
      - cached input ~ 25% of input (0.25x), floored at $0.01
      - output ~ 3x input for expensive models, 4x for very cheap, 2.5x mid-range
    """
    cached = round(max(0.01, input_price * 0.25), 4)
    # trim trailing zeros via rounding but keep storage precise
    if input_price >= 5:
        output = round(input_price * 3.0, 2)
    elif input_price < 0.5:
        output = round(input_price * 4.0, 2)
    else:
        output = round(input_price * 2.5, 2)
    return cached, output


def seed():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS models;
        CREATE TABLE models (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            model       TEXT    NOT NULL,
            provider    TEXT    NOT NULL,
            elo         INTEGER NOT NULL,
            input       REAL    NOT NULL,
            input_cache REAL    NOT NULL DEFAULT 0,
            output      REAL    NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_provider ON models(provider);
        CREATE INDEX IF NOT EXISTS idx_elo      ON models(elo);
    """)

    # Expand 4-tuple RAW_MODELS -> 6-tuple with derived prices.
    # If someone has already edited RAW_MODELS to 6-tuples, respect that.
    expanded = []
    for row in RAW_MODELS:
        if len(row) == 6:
            expanded.append(row)
        else:
            model, provider, elo, inp = row
            cache, out = _derive_prices(float(inp))
            expanded.append((model, provider, elo, inp, cache, out))

    cur.executemany(
        "INSERT INTO models (model, provider, elo, input, input_cache, output) VALUES (?, ?, ?, ?, ?, ?)",
        expanded
    )
    con.commit()
    count = cur.execute("SELECT COUNT(*) FROM models").fetchone()[0]
    print(f"Seeded {count} models into {DB_PATH}")
    con.close()

if __name__ == "__main__":
    seed()
