"""
Atualizador de Referencias — Top Agenda Instagram Bot

Uso: python update_references.py

Le as URLs em references/sources.md, acessa cada uma com Playwright,
tira screenshot e usa Gemini Vision para analisar os padroes de conteudo.
Os resultados sao salvos em references/patterns/<nome>.md

Execute manualmente ou configure um cron semanal.
Requer: playwright install chromium (uma vez)
"""
import os
import re
import sys
import base64
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REFERENCES_DIR = os.path.join(os.path.dirname(__file__), "references")
PATTERNS_DIR = os.path.join(REFERENCES_DIR, "patterns")


def _extract_urls(sources_path: str) -> list[dict]:
    """Extrai URLs e descricoes do sources.md."""
    urls = []
    try:
        with open(sources_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("references/sources.md nao encontrado")
        return []

    # Busca linhas com URL (comecando com - https://)
    for line in content.splitlines():
        line = line.strip()
        # Pula comentarios
        if line.startswith("#"):
            continue
        match = re.match(r'^-\s+(https?://\S+)\s*(?:—\s*(.+))?', line)
        if match:
            url = match.group(1).strip()
            description = match.group(2).strip() if match.group(2) else ""
            # Cria nome de arquivo a partir da URL
            name = re.sub(r'https?://(www\.)?', '', url)
            name = re.sub(r'[^\w]', '_', name).strip('_')[:50]
            urls.append({"url": url, "name": name, "description": description})

    return urls


def _screenshot_url(url: str, width: int = 1080, height: int = 1080) -> bytes | None:
    """Tira screenshot de uma URL com Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright nao instalado. Execute: pip install playwright && playwright install chromium")
        return None

    html_path = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
            page = browser.new_page(
                viewport={"width": width, "height": height},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)  # aguarda lazy-load
            screenshot_bytes = page.screenshot(full_page=False, type="jpeg", quality=85)
            browser.close()
            return screenshot_bytes
    except Exception as e:
        print(f"  Erro ao acessar {url}: {e}")
        return None


def _analyze_with_gemini(screenshot_bytes: bytes, url: str, description: str) -> str:
    """Usa Gemini Vision para analisar o screenshot e extrair padroes."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("  google-genai nao instalado")
        return ""

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("  GOOGLE_API_KEY nao configurada")
        return ""

    client = genai.Client(api_key=api_key)

    # Codifica imagem como base64
    img_b64 = base64.b64encode(screenshot_bytes).decode()

    prompt = f"""Voce e um analista de marketing digital especializado em Instagram para pequenos negocios brasileiros.

Analise este screenshot da pagina: {url}
Descricao: {description if description else "conta/pagina de referencia"}

Analise visualmente o conteudo e extraia:

1. **PADROES VISUAIS:** Quais sao os elementos visuais predominantes? (cores, tipografia, estilo de foto, layout)

2. **PADROES DE CONTEUDO:** Que tipo de conteudo aparece? (educativo, promocional, inspiracional, humor)

3. **LINGUAGEM E TOM:** Como e o texto? (formal/informal, tecnico/simples, comprido/curto)

4. **HOOKS E TITULOS:** Quais padroes de hook aparecem? O que chama atencao?

5. **ESTRUTURA DE POST:** Como os posts sao estruturados? (carrossel, post unico, reels?)

6. **INSIGHTS APLICAVEIS:** O que o Top Agenda pode aprender e adaptar para o publico de barbeiros,
   cabeleireiros, manicures e profissionais de beleza brasileiros?

Seja especifico e pratico. Foque em padroes replicaveis, nao em detalhes genericos."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=screenshot_bytes, mime_type="image/jpeg"),
                types.Part.from_text(text=prompt)
            ]
        )
        return response.text.strip()
    except Exception as e:
        print(f"  Gemini Vision erro: {e}")
        return ""


def _save_pattern(name: str, url: str, description: str, analysis: str):
    """Salva o arquivo de pattern em references/patterns/."""
    os.makedirs(PATTERNS_DIR, exist_ok=True)
    path = os.path.join(PATTERNS_DIR, f"{name}.md")

    content = f"""# Analise de Referencia: {url}

**Descricao:** {description if description else "Sem descricao"}
**Data da analise:** {datetime.now().strftime("%d/%m/%Y %H:%M")}
**URL:** {url}

---

{analysis}
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Pattern salvo: references/patterns/{name}.md")


def main():
    print("=" * 55)
    print("Top Agenda — Atualizador de Referencias")
    print("=" * 55)

    sources_path = os.path.join(REFERENCES_DIR, "sources.md")
    urls = _extract_urls(sources_path)

    if not urls:
        print("\nNenhuma URL encontrada em references/sources.md")
        print("Adicione URLs no formato:")
        print("  - https://www.instagram.com/conta/ — descricao da conta")
        return

    print(f"\n{len(urls)} URL(s) encontrada(s) para analisar:")
    for u in urls:
        print(f"  - {u['url']}")

    print()
    for i, entry in enumerate(urls, 1):
        url = entry["url"]
        name = entry["name"]
        description = entry["description"]

        print(f"[{i}/{len(urls)}] Analisando: {url}")

        # Screenshot
        print(f"  Tirando screenshot...")
        screenshot = _screenshot_url(url)
        if not screenshot:
            print(f"  Pulando — screenshot falhou")
            continue

        # Analise Gemini Vision
        print(f"  Analisando com Gemini Vision...")
        analysis = _analyze_with_gemini(screenshot, url, description)
        if not analysis:
            print(f"  Pulando — analise falhou")
            continue

        # Salva
        _save_pattern(name, url, description, analysis)
        print(f"  OK\n")

    print("=" * 55)
    print("Concluido! Execute o bot para usar as novas referencias.")
    print("=" * 55)


if __name__ == "__main__":
    main()
