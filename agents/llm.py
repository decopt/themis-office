"""
Helper central de LLM — Gemini 2.5 Flash via REST API.
Usado por todos os agentes de texto (strategist, scriptwriter, reviewer, researcher).
"""
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
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
