"""
Helper central de LLM — Gemini 2.5 Flash via REST API.
Usado por todos os agentes de texto (strategist, scriptwriter, reviewer, researcher).

Nota: gemini-2.5-flash é um modelo de thinking — retorna parts com thought=True
(raciocínio interno) e parts com thought=False (resposta final). Sempre usar
a resposta final, ignorando os thought parts.
"""
import re
import os
import requests

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def generate(prompt: str, max_tokens: int = 1024, json_mode: bool = False) -> str:
    gen_config = {"maxOutputTokens": max_tokens}
    if json_mode:
        gen_config["responseMimeType"] = "application/json"

    resp = requests.post(
        GEMINI_URL,
        params={"key": GEMINI_API_KEY},
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": gen_config,
        },
        timeout=60,
    )
    resp.raise_for_status()

    # Filtra thought parts (raciocínio interno do modelo thinking)
    parts = resp.json()["candidates"][0]["content"]["parts"]
    text_parts = [p["text"] for p in parts if not p.get("thought", False) and "text" in p]
    return "\n".join(text_parts).strip()


def extract_json(text: str) -> str:
    """Extrai o primeiro objeto JSON do texto, ignorando markdown e texto extra."""
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'```', '', text)
    text = text.strip()
    start = text.find('{')
    if start == -1:
        return text
    depth = 0
    in_string = False
    escape_next = False
    for i, c in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue
        if c == '\\' and in_string:
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
        if not in_string:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return text[start:]
