"""
Estado compartilhado entre pipeline e dashboard.
Escreve/lê de output/state.json.
"""
import json
import os
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(__file__), "output", "state.json")

AGENTS = [
    {"id": "strategist",        "name": "Estrategista", "icon": "brain"},
    {"id": "scriptwriter",      "name": "Roteirista",   "icon": "pen"},
    {"id": "designer",          "name": "Designer",     "icon": "image"},
    {"id": "editor",            "name": "Editor",       "icon": "wand"},
    {"id": "reviewer",          "name": "Revisor",      "icon": "check"},
    {"id": "telegram_approver", "name": "Aprovacao",    "icon": "send"},
    {"id": "publisher",         "name": "Publisher",    "icon": "send"},
]

DEFAULT_STATE = {
    "running": False,
    "current_agent": None,
    "current_run": None,
    "agents": {a["id"]: "idle" for a in AGENTS},
    "last_updated": None,
}


def _load() -> dict:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_STATE.copy()


def _fix_encoding(obj):
    """Corrige double-encoding UTF-8 (latin1 lido como utf-8) recursivamente."""
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


def _save(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def set_running(run_id: str):
    s = _load()
    s["running"] = True
    s["current_run"] = run_id
    s["agents"] = {a["id"]: "idle" for a in AGENTS}
    _save(s)


def set_agent(agent_id: str, status: str, detail: str = None):
    """status: running | done | error"""
    s = _load()
    s["current_agent"] = agent_id if status == "running" else None
    s["agents"][agent_id] = status
    if detail:
        s[f"{agent_id}_detail"] = detail
    _save(s)


def set_done(success: bool, result: dict = None):
    s = _load()
    s["running"] = False
    s["current_agent"] = None
    s["last_result"] = {
        "success": success,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
    _save(s)


def get() -> dict:
    return _load()
