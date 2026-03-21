"""
Agente 6 - Aprovador Telegram
Envia imagens + roteiro para o admin aprovar antes de publicar.
Botoes: Aprovar | Rejeitar | Agendar | Recriar
"""
import html
import json
import os
import time

import requests

from config import TELEGRAM_ADMIN_CHAT_ID, TELEGRAM_BOT_TOKEN

POLL_TIMEOUT = 600   # 10 minutos para o admin responder
POLL_INTERVAL = 2    # intervalo entre checks


def _api(method: str, poll: bool = False, **kwargs) -> dict:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    timeout = 35 if poll else 15
    try:
        r = requests.post(url, timeout=timeout, **kwargs)
        return r.json()
    except Exception as e:
        print(f"  [Telegram] Erro na API ({method}): {e}")
        return {}


def _send_images(image_paths: list):
    """Envia as imagens como album (media group)."""
    if not image_paths:
        return

    if len(image_paths) == 1:
        with open(image_paths[0], "rb") as f:
            _api("sendPhoto",
                 data={"chat_id": TELEGRAM_ADMIN_CHAT_ID},
                 files={"photo": f})
        return

    media = []
    files = {}
    for i, path in enumerate(image_paths):
        key = f"photo{i}"
        media.append({"type": "photo", "media": f"attach://{key}"})
        files[key] = open(path, "rb")

    try:
        _api("sendMediaGroup",
             data={"chat_id": TELEGRAM_ADMIN_CHAT_ID, "media": json.dumps(media)},
             files=files)
    finally:
        for f in files.values():
            f.close()


def _e(text: str) -> str:
    """Escapa texto para HTML do Telegram."""
    return html.escape(str(text))


def _send_approval_message(script: dict, strategy: dict, review: dict) -> int | None:
    """Envia mensagem com resumo do post e botoes de aprovacao."""
    score     = review.get("score", 0)
    hook_s    = review.get("hook_score", "?")
    voice_s   = review.get("voice_score", "?")
    aida_s    = review.get("aida_score", "?")
    relev_s   = review.get("relevance_score", "?")

    caption_full = script.get("caption", "")
    caption_preview = caption_full[:400] + ("..." if len(caption_full) > 400 else "")

    slides = script.get("slides", [])
    slide_lines = "\n".join(
        f"  Slide {s['slide_number']}: {_e(s.get('headline', ''))}"
        for s in slides
    )

    strengths = review.get("strengths", [])
    strengths_text = ""
    if strengths:
        strengths_text = "\n<b>Pontos fortes:</b>\n" + "\n".join(f"  + {_e(s)}" for s in strengths[:2]) + "\n"

    text = (
        f"<b>Top Agenda - Aprovacao de Post</b>\n\n"
        f"<b>Score IA:</b> {score}/100\n"
        f"Hook: {hook_s}/25 | Voz: {voice_s}/25 | AIDA: {aida_s}/25 | Relevancia: {relev_s}/25\n\n"
        f"<b>Pilar:</b> {_e(strategy.get('pillar_name', strategy.get('content_type', '')))}\n"
        f"<b>Tema:</b> {_e(strategy.get('theme', ''))}\n"
        f"<b>Publico:</b> {_e(strategy.get('target_audience', ''))}\n\n"
        f"<b>Slides:</b>\n{slide_lines}\n\n"
        f"<b>Caption:</b>\n{_e(caption_preview)}\n"
        f"{strengths_text}\n"
        f"O que deseja fazer com este post?"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Aprovar", "callback_data": "approve"},
                {"text": "Rejeitar", "callback_data": "reject"},
            ],
            [
                {"text": "Agendar", "callback_data": "schedule"},
                {"text": "Recriar", "callback_data": "recreate"},
            ],
        ]
    }

    resp = _api("sendMessage", json={
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": keyboard,
    })

    if resp.get("ok"):
        return resp["result"]["message_id"]

    print(f"  [Telegram] Erro ao enviar mensagem de aprovacao: {resp.get('description')}")
    return None


def _get_offset() -> int:
    """Retorna offset apos o ultimo update existente."""
    resp = _api("getUpdates", json={"limit": 1, "offset": -1, "timeout": 0})
    if resp.get("ok") and resp.get("result"):
        return resp["result"][-1]["update_id"] + 1
    return 0


def _ask_schedule_time() -> str | None:
    """Apos clicar em Agendar, pede o horario e aguarda resposta de texto."""
    _api("sendMessage", json={
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": "Para qual horario agendar? Responda no formato HH:MM (ex: 18:00)",
        "reply_markup": {"force_reply": True, "selective": True},
    })

    offset = _get_offset()
    deadline = time.time() + 120  # 2 minutos para digitar

    while time.time() < deadline:
        resp = _api("getUpdates", json={"offset": offset, "timeout": 20, "limit": 5})
        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1
            msg = upd.get("message", {})
            if (str(msg.get("from", {}).get("id")) == str(TELEGRAM_ADMIN_CHAT_ID)
                    and msg.get("text")):
                scheduled_time = msg["text"].strip()
                _api("sendMessage", json={
                    "chat_id": TELEGRAM_ADMIN_CHAT_ID,
                    "text": f"Post agendado para <b>{_e(scheduled_time)}</b>.",
                    "parse_mode": "HTML",
                })
                return scheduled_time

    _api("sendMessage", json={
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": "Tempo esgotado. Agendamento cancelado - post nao publicado.",
        "parse_mode": "HTML",
    })
    return None


def _poll_decision() -> dict:
    """Faz polling aguardando o admin clicar num botao."""
    offset   = _get_offset()
    deadline = time.time() + POLL_TIMEOUT

    print(f"  [Telegram] Aguardando decisao (timeout: {POLL_TIMEOUT // 60} min)...")

    while time.time() < deadline:
        resp = _api("getUpdates", poll=True, json={"offset": offset, "timeout": 30, "limit": 10})

        if not resp.get("ok"):
            time.sleep(POLL_INTERVAL)
            continue

        for upd in resp.get("result", []):
            offset = upd["update_id"] + 1

            cb = upd.get("callback_query")
            if not cb:
                continue

            # Aceita so cliques do admin
            if str(cb.get("from", {}).get("id")) != str(TELEGRAM_ADMIN_CHAT_ID):
                continue

            action = cb.get("data")
            msg_id = cb.get("message", {}).get("message_id")

            _api("answerCallbackQuery", json={"callback_query_id": cb["id"]})

            # Remove os botões da mensagem original para evitar cliques repetidos
            if msg_id:
                confirmations_text = {
                    "approve":  "Acao registrada: APROVAR\nPublicando agora...",
                    "reject":   "Acao registrada: REJEITAR\nPost nao sera publicado.",
                    "recreate": "Acao registrada: RECRIAR\nGerando novo post...",
                    "schedule": "Acao registrada: AGENDAR\nInforme o horario.",
                }
                _api("editMessageText", json={
                    "chat_id": TELEGRAM_ADMIN_CHAT_ID,
                    "message_id": msg_id,
                    "text": confirmations_text.get(action, f"Acao: {action}"),
                    "parse_mode": "HTML",
                })

            if action == "schedule":
                scheduled_time = _ask_schedule_time()
                return {"action": "schedule", "scheduled_time": scheduled_time}

            return {"action": action, "scheduled_time": None}

    # Timeout sem resposta — nao publica por seguranca
    _api("sendMessage", json={
        "chat_id": TELEGRAM_ADMIN_CHAT_ID,
        "text": "Tempo esgotado sem resposta. Post nao publicado automaticamente.",
        "parse_mode": "HTML",
    })
    return {"action": "timeout", "scheduled_time": None}


def run(image_paths: list, script: dict, strategy: dict, review: dict) -> dict:
    """
    Envia conteudo para aprovacao no Telegram e aguarda decisao.

    Retorna:
        {"action": "approve"|"reject"|"schedule"|"recreate"|"timeout",
         "scheduled_time": "HH:MM" ou None}
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_CHAT_ID:
        print("  [Telegram] Token/chat_id nao configurado - aprovacao automatica")
        return {"action": "approve", "scheduled_time": None}

    print(f"  [Telegram] Enviando {len(image_paths)} imagem(ns) para aprovacao...")
    _send_images(image_paths)

    msg_id = _send_approval_message(script, strategy, review)
    if not msg_id:
        print("  [Telegram] Falha ao enviar - aprovacao automatica")
        return {"action": "approve", "scheduled_time": None}

    return _poll_decision()
