"""
Atualizador de Referencias — Top Agenda Instagram Bot

Uso: python update_references.py

Le as URLs em references/sources.md, acessa cada uma com Playwright,
tira screenshot e gera um arquivo .md esqueleto em references/patterns/<nome>.md
para preenchimento manual ou analise futura.

Execute manualmente quando quiser atualizar as referencias.
Requer: playwright install chromium (uma vez)
"""
import os
import re
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


def _save_pattern(name: str, url: str, description: str, analysis: str):
    """Salva o arquivo de pattern em references/patterns/."""
    os.makedirs(PATTERNS_DIR, exist_ok=True)
    path = os.path.join(PATTERNS_DIR, f"{name}.md")

    content = f"""# Referencia: {url}

**Descricao:** {description if description else "Sem descricao"}
**Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}
**URL:** {url}

---

## Padroes Visuais
<!-- O que chama atencao no design? Cores, layout, tipografia -->


## Tipo de Conteudo
<!-- Educativo, promocional, inspiracional, humor? -->


## Linguagem e Tom
<!-- Formal/informal, tecnico/simples? Exemplos de frases marcantes -->


## Hooks e Titulos
<!-- Quais formatos de hook aparecem? -->


## Insights Aplicaveis
<!-- O que o Top Agenda pode adaptar para barbeiros, cabeleireiros, manicures? -->

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

        # Screenshot (opcional — util para consulta manual)
        print(f"  Tirando screenshot...")
        screenshot = _screenshot_url(url)
        if screenshot:
            img_path = os.path.join(PATTERNS_DIR, f"{name}.jpg")
            os.makedirs(PATTERNS_DIR, exist_ok=True)
            with open(img_path, "wb") as f:
                f.write(screenshot)
            print(f"  Screenshot salvo: references/patterns/{name}.jpg")

        # Gera esqueleto .md para preenchimento manual
        _save_pattern(name, url, description, "")
        print(f"  Preencha manualmente: references/patterns/{name}.md\n")

    print("=" * 55)
    print("Concluido! Preencha os arquivos .md em references/patterns/")
    print("e execute o bot para usar as novas referencias.")
    print("=" * 55)


if __name__ == "__main__":
    main()
