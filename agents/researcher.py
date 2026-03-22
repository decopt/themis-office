"""
Agente 0 - Pesquisador
Combina referencias locais (.md) com pesquisa web em tempo real.

Fluxo:
1. Le brand.md + domain-framework.md + patterns/*.md (base de conhecimento)
2. Scraping com Playwright: DuckDuckGo (2 queries) + Google Trends BR
3. Analisa o texto coletado com Gemini → extrai insights acionaveis
4. Retorna contexto consolidado para o Estrategista

Se o Playwright ou a web falharem, cai graciosamente para so os .md locais.
"""
import os
from pathlib import Path
from datetime import datetime
from agents import llm, skill_loader

SKILL = skill_loader.load("researcher")

REFERENCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references")

# Queries de pesquisa — ajuste conforme necessidade
SEARCH_QUERIES = [
    "salao barbearia manicure dicas instagram engajamento 2025",
    "pequenos negocios autonomo agenda clientes fidelizacao brasil",
]


# ── Helpers locais ─────────────────────────────────────────────

def _read_file(path: str, max_chars: int = 2000) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()[:max_chars]
    except Exception:
        return ""


def _load_patterns() -> list:
    patterns_dir = os.path.join(REFERENCES_DIR, "patterns")
    if not os.path.exists(patterns_dir):
        return []
    results = []
    for path in Path(patterns_dir).glob("*.md"):
        content = _read_file(str(path), 1200)
        if content:
            results.append({"source": path.stem, "content": content})
    return results


# ── Web scraping ───────────────────────────────────────────────

def _scrape_web(queries: list) -> str:
    """
    Abre um unico browser Playwright e faz todas as pesquisas.
    Retorna texto combinado para analise.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [Pesquisador] Playwright nao disponivel — pulando pesquisa web")
        return ""

    results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])

            # DuckDuckGo: uma pagina por query
            for query in queries:
                print(f"  [Pesquisador] Buscando: {query[:55]}...")
                try:
                    page = browser.new_page()
                    url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}&kl=br-pt"
                    page.goto(url, wait_until="domcontentloaded", timeout=20000)

                    titles   = page.locator(".result__title").all_text_contents()
                    snippets = page.locator(".result__snippet").all_text_contents()

                    items = []
                    for t, s in zip(titles[:7], snippets[:7]):
                        t, s = t.strip(), s.strip()
                        if t and s:
                            items.append(f"• {t}: {s}")

                    if items:
                        results.append(f"Busca '{query}':\n" + "\n".join(items))
                    page.close()
                except Exception as e:
                    print(f"  [Pesquisador] Busca falhou ({query[:30]}): {e}")

            # Google Trends Brasil
            print("  [Pesquisador] Coletando Google Trends Brasil...")
            try:
                page = browser.new_page()
                page.goto(
                    "https://trends.google.com/trending?geo=BR",
                    wait_until="networkidle", timeout=25000
                )
                page.wait_for_timeout(2000)
                text = page.inner_text("body")
                lines = [l.strip() for l in text.splitlines()
                         if len(l.strip()) > 8 and not l.strip().startswith(("©", "http"))]
                if lines:
                    results.append("Trending Google Brasil:\n" + "\n".join(lines[:30]))
                page.close()
            except Exception as e:
                print(f"  [Pesquisador] Google Trends falhou: {e}")

            browser.close()

    except Exception as e:
        print(f"  [Pesquisador] Browser error: {e}")

    return "\n\n".join(results)


# ── Analise com IA ─────────────────────────────────────────────

def _analyze_web(web_text: str) -> str:
    """Usa Gemini para transformar texto bruto em insights acionaveis."""
    today = datetime.now().strftime("%d/%m/%Y")
    skill_section = f"{SKILL}\n---\n" if SKILL else ""
    prompt = f"""{skill_section}Hoje e {today}.

Analise os textos abaixo coletados da web (buscas e tendencias).

Seu objetivo: extrair 4-5 INSIGHTS ESPECIFICOS E ACIONAVEIS para criar posts no Instagram
do Top Agenda — app de agendamento para barbeiros, cabeleireiros, manicures, esteticistas
e outros profissionais autonomos brasileiros.

Para cada insight responda:
- O que esta em alta ou sendo discutido
- Como isso se conecta com a dor do autonomo (agenda, clientes, organizacao)
- Sugestao de angulo para um post

TEXTOS COLETADOS:
{web_text[:3500]}

Liste os insights numerados, em portugues, de forma objetiva. Max 400 palavras."""

    try:
        return llm.generate(prompt, max_tokens=600)
    except Exception as e:
        print(f"  [Pesquisador] Analise Gemini falhou: {e}")
        return ""


# ── Entry point ────────────────────────────────────────────────

def run() -> str:
    """
    Retorna contexto consolidado (referencias locais + pesquisa web)
    para o Estrategista usar ao definir o tema do proximo post.
    """
    sections = []

    # 1. Framework de dominio
    domain = _read_file(os.path.join(REFERENCES_DIR, "domain-framework.md"), 2000)
    if domain:
        sections.append(f"=== FRAMEWORK DO DOMINIO ===\n{domain}")

    # 2. Brand guidelines
    brand = _read_file(os.path.join(REFERENCES_DIR, "brand.md"), 1500)
    if brand:
        sections.append(f"=== GUIA DA MARCA ===\n{brand}")

    # 3. Pesquisa web em tempo real
    web_raw = _scrape_web(SEARCH_QUERIES)
    if web_raw:
        print(f"  [Pesquisador] {len(web_raw)} chars coletados — analisando com IA...")
        analysis = _analyze_web(web_raw)
        if analysis:
            sections.append(f"=== TENDENCIAS E INSIGHTS WEB (TEMPO REAL) ===\n{analysis}")
    else:
        print("  [Pesquisador] Pesquisa web sem resultados — usando apenas referencias locais")

    # 4. Patterns manuais
    for p in _load_patterns():
        sections.append(f"=== REFERENCIA: {p['source']} ===\n{p['content']}")

    if not sections:
        return ""

    context = "\n\n".join(sections)
    print(f"  [Pesquisador] Contexto final: {len(context)} chars")
    return context
