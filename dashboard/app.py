"""
Dashboard web para monitorar o pipeline do Instagram Bot.
Serve o frontend React (build) + API JSON.
"""
import json
import logging
import os
import sys
import threading

# Adiciona o diretório pai ao path para importar os módulos do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, send_from_directory, request
import state
from config import OUTPUT_DIR, MAX_POSTS_PER_DAY, POST_TIMES

# Suprime log spam de polling (GET /api/status e /api/posts a cada 3s)
class _PollFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return "/api/status" not in msg and "/api/posts" not in msg

logging.getLogger("werkzeug").addFilter(_PollFilter())


def _fix_encoding(obj):
    """Corrige double-encoding UTF-8 em strings vindas do state.json."""
    if isinstance(obj, str):
        try:
            return obj.encode("latin1").decode("utf-8")
        except Exception:
            return obj
    if isinstance(obj, dict):
        return {k: _fix_encoding(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_fix_encoding(i) for i in obj]
    return obj

# React build directory (montado pelo Docker)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

LOG_FILE = os.path.join(OUTPUT_DIR, "pipeline_log.json")
AGENTS_META = state.AGENTS


def _load_logs(limit=20) -> list:
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
        return list(reversed(logs[-limit:]))
    except Exception:
        return []


def _count_today(logs: list) -> int:
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    return sum(
        1 for log in logs
        if log.get("timestamp", "").startswith(today)
        and log.get("status") in ("published", "simulated")
    )


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/status")
def api_status():
    current = state.get()
    logs = _load_logs(50)
    posts_today = _count_today(logs)
    total_published = sum(1 for l in logs if l.get("status") in ("published", "simulated"))
    avg_score = 0
    scored = [l.get("score") for l in logs if l.get("score") is not None]
    if scored:
        avg_score = round(sum(scored) / len(scored))

    # Collect agent details (what each agent is doing/did)
    agent_details = {}
    for a in AGENTS_META:
        detail = current.get(f"{a['id']}_detail")
        if detail:
            agent_details[a["id"]] = detail

    return jsonify(_fix_encoding({
        "running": current.get("running", False),
        "current_agent": current.get("current_agent"),
        "agents": current.get("agents", {}),
        "agent_details": agent_details,
        "agents_meta": state.AGENTS,
        "last_updated": current.get("last_updated"),
        "last_result": current.get("last_result"),
        "stats": {
            "posts_today": posts_today,
            "max_today": MAX_POSTS_PER_DAY,
            "total_published": total_published,
            "avg_score": avg_score,
            "schedule": POST_TIMES,
        }
    }))


@app.route("/api/posts")
def api_posts():
    logs = _load_logs(20)
    posts = []
    for log in logs:
        if log.get("status") in ("published", "simulated", "error", "failed"):
            images = log.get("images", [])
            post = {
                "run_id": log.get("run_id", "—"),
                "status": log.get("status"),
                "timestamp": log.get("timestamp"),
                "theme": log.get("theme", "—"),
                "content_type": log.get("content_type", "—"),
                "score": log.get("score"),
                "images_count": log.get("images_count", 0),
                "caption_preview": log.get("caption_preview", ""),
                "hashtags_count": log.get("hashtags_count", 0),
                "duration_seconds": log.get("duration_seconds", 0),
                "error": log.get("error"),
                "thumbnail": images[0] if images else None,
            }
            posts.append(post)
    return jsonify(posts)


@app.route("/api/run", methods=["POST"])
def api_run():
    """Dispara o pipeline manualmente."""
    current = state.get()
    if current.get("running"):
        return jsonify({"error": "Pipeline já está rodando"}), 409

    def run_async():
        import pipeline
        pipeline.run()

    t = threading.Thread(target=run_async, daemon=True)
    t.start()
    return jsonify({"message": "Pipeline iniciado!"})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Força reset do estado quando pipeline fica travado."""
    state.reset()
    return jsonify({"message": "Estado resetado. Pipeline liberado."})


@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)


# Catch-all: serve index.html for React Router client-side routes
@app.route("/<path:path>")
def catch_all(path):
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.isfile(file_path):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, "index.html")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Limpa estado stale (container reiniciou mas state.json ficou com running=True)
    if state.get().get("running"):
        print("[Dashboard] Estado stale detectado (running=True) — resetando.")
        state.reset()

    # Inicia listener de comandos Telegram em background
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        import telegram_bot
        telegram_bot.start_background()
    except Exception as e:
        print(f"[Dashboard] TelegramBot nao iniciado: {e}")

    print("Dashboard rodando em http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)
