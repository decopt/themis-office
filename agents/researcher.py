"""
Agente 0 - Pesquisador
Le os arquivos de referencias (references/) e retorna um contexto condensado
para o Estrategista usar ao definir o tema do proximo post.

Nao faz chamadas externas — apenas consolida o conhecimento dos .md files.
Para atualizar os patterns com analise de URLs, execute: python update_references.py
"""
import os
from pathlib import Path

REFERENCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "references")


def _read_file(path: str, max_chars: int = 3000) -> str:
    """Le arquivo com limite de caracteres."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:max_chars] if len(content) > max_chars else content
    except Exception:
        return ""


def _load_patterns() -> list[dict]:
    """Carrega todos os arquivos de patterns gerados pelo update_references.py."""
    patterns_dir = os.path.join(REFERENCES_DIR, "patterns")
    if not os.path.exists(patterns_dir):
        return []

    results = []
    for path in Path(patterns_dir).glob("*.md"):
        if path.name == ".gitkeep":
            continue
        content = _read_file(str(path), max_chars=1500)
        if content:
            results.append({"source": path.stem, "content": content})

    return results


def run() -> str:
    """
    Consolida o conhecimento de referencias em um contexto para o Estrategista.
    Retorna string vazia se nao houver referencias uteis.
    """
    sections = []

    # 1. Framework de dominio
    domain_path = os.path.join(REFERENCES_DIR, "domain-framework.md")
    if os.path.exists(domain_path):
        domain = _read_file(domain_path, max_chars=2500)
        if domain:
            sections.append(f"=== FRAMEWORK DO DOMINIO ===\n{domain}")

    # 2. Brand guidelines
    brand_path = os.path.join(REFERENCES_DIR, "brand.md")
    if os.path.exists(brand_path):
        brand = _read_file(brand_path, max_chars=2000)
        if brand:
            sections.append(f"=== GUIA DA MARCA ===\n{brand}")

    # 3. Patterns gerados automaticamente (analise de URLs)
    patterns = _load_patterns()
    if patterns:
        pattern_text = "\n\n".join(
            f"--- Referencia: {p['source']} ---\n{p['content']}"
            for p in patterns
        )
        sections.append(f"=== ANALISE DE REFERENCIAS EXTERNAS ===\n{pattern_text}")

    # 4. Notas manuais de sources.md (secao de observacoes)
    sources_path = os.path.join(REFERENCES_DIR, "sources.md")
    if os.path.exists(sources_path):
        sources = _read_file(sources_path, max_chars=2000)
        # Extrai apenas a parte de observacoes manuais (apos "## Posts de Alto Desempenho")
        if "Posts de Alto Desempenho" in sources:
            obs_section = sources.split("Posts de Alto Desempenho", 1)[1]
            if obs_section.strip():
                sections.append(f"=== OBSERVACOES DE CONTEUDO DE ALTO DESEMPENHO ===\n{obs_section[:1500]}")

    if not sections:
        return ""

    context = "\n\n".join(sections)
    print(f"  [Pesquisador] Contexto carregado: {len(context)} chars, {len(patterns)} pattern(s) externo(s)")
    return context
