"""
Bot Telegram — listener de comandos em background.
Roda em thread separada junto com o scheduler/dashboard.

Comandos:
  /gerar  — dispara o pipeline imediatamente
  /status — mostra o estado atual dos agentes
  /ajuda  — lista os comandos disponiveis
"""
import threading
import time

import requests

import state
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID

_pipeline_lock = threading.Lock()
_running = False


def _api(method: str, poll: bool = False, **kwargs) -> dict:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    timeout = 35 if poll else 15  # long-poll precisa de timeout maior que o servidor
    try:
        r = requests.post(url, timeout=timeout, **kwargs)
        return r.json()
    except Exception as e:
        print(f"  [TelegramBot] Erro API ({method}): {e}")
        return {}


def _send(text: str, parse_mode: str = "HTML"):
    _api("sendMessage", json={
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
    })


def _handle_gerar():
    """Dispara o pipeline em thread separada."""
    global _running

    current = state.get()
    if current.get("running"):
        _send("Pipeline ja esta rodando. Aguarde terminar antes de /gerar novamente.")
        return

    if not _pipeline_lock.acquire(blocking=False):
        _send("Pipeline ja esta sendo iniciado.")
        return

    _send("Pipeline iniciado! Voce recebera as imagens para aprovacao em alguns minutos.")

    def run_pipeline():
        global _running
        try:
            _running = True
            import pipeline
            pipeline.run()
        except Exception as e:
            _send(f"Erro no pipeline: {e}")
        finally:
            _running = False
            _pipeline_lock.release()

    t = threading.Thread(target=run_pipeline, daemon=True)
    t.start()


def _handle_status():
    """Retorna o estado atual dos agentes."""
    current = state.get()
    running = current.get("running", False)
    agents = current.get("agents", {})
    last_result = current.get("last_result", {})

    status_icon = {"done": "OK", "running": "...", "error": "ERRO", "idle": "-"}

    lines = ["<b>Status do Pipeline</b>\n"]

    if running:
        agent = current.get("current_agent", "")
        lines.append(f"Em execucao — agente atual: {agent}\n")
    else:
        lines.append("Idle (aguardando proximo horario ou /gerar)\n")

    lines.append("<b>Agentes:</b>")
    for agent_id, status in agents.items():
        icon = status_icon.get(status, status)
        detail = current.get(f"{agent_id}_detail", "")
        detail_str = f" — {detail}" if detail else ""
        lines.append(f"  {icon} {agent_id}{detail_str}")

    if last_result:
        result = last_result.get("result", {})
        success = last_result.get("success")
        ts = last_result.get("timestamp", "")[:16].replace("T", " ")
        score = result.get("score", "?")
        status_str = result.get("status", "?")
        lines.append(f"\n<b>Ultimo resultado:</b> {status_str} | Score: {score}/100 | {ts}")

    _send("\n".join(lines))


def _handle_parar():
    """Força reset do pipeline travado."""
    current = state.get()
    if not current.get("running"):
        _send("Pipeline nao esta rodando. Nada a parar.")
        return
    state.reset()
    _send("Pipeline resetado. Use /gerar para iniciar novamente.")


def _handle_ajuda():
    _send(
        "<b>Comandos disponiveis:</b>\n\n"
        "/gerar — cria e envia um novo post para aprovacao\n"
        "/status — mostra o estado atual do pipeline\n"
        "/parar — reseta pipeline travado\n"
        "/ajuda — exibe esta mensagem"
    )


def _get_offset() -> int:
    resp = _api("getUpdates", json={"limit": 1, "offset": -1, "timeout": 0})
    if resp.get("ok") and resp.get("result"):
        return resp["result"][-1]["update_id"] + 1
    return 0


def _poll_loop():
    """Loop principal de polling para comandos."""
    offset = _get_offset()
    print("[TelegramBot] Listener de comandos iniciado.")

    while True:
        try:
            resp = _api("getUpdates", poll=True, json={"offset": offset, "timeout": 25, "limit": 10})

            if not resp.get("ok"):
                time.sleep(5)
                continue

            for upd in resp.get("result", []):
                offset = upd["update_id"] + 1

                msg = upd.get("message", {})
                if not msg:
                    continue

                # Aceita apenas mensagens do admin
                if str(msg.get("from", {}).get("id")) != str(TELEGRAM_ADMIN_CHAT_ID):
                    continue

                text = msg.get("text", "").strip().lower().split()[0] if msg.get("text") else ""

                if text in ("/gerar", "/gerar@instatopagenda_bot"):
                    print("[TelegramBot] Comando /gerar recebido")
                    _handle_gerar()
                elif text in ("/status", "/status@instatopagenda_bot"):
                    print("[TelegramBot] Comando /status recebido")
                    _handle_status()
                elif text in ("/parar", "/parar@instatopagenda_bot", "/reset"):
                    print("[TelegramBot] Comando /parar recebido")
                    _handle_parar()
                elif text in ("/ajuda", "/ajuda@instatopagenda_bot", "/start", "/help"):
                    _handle_ajuda()

        except Exception as e:
            print(f"[TelegramBot] Erro no loop: {e}")
            time.sleep(10)


def start_background():
    """Inicia o listener em thread daemon (nao bloqueia o processo principal)."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        print("[TelegramBot] Token/chat_id nao configurado — listener nao iniciado.")
        return

    t = threading.Thread(target=_poll_loop, daemon=True, name="TelegramBotListener")
    t.start()
    return t
