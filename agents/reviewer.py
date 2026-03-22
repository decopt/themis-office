"""
Agente 5 - Revisor
Analisa o conteúdo e decide se aprova ou solicita ajuste.
"""
import json
import os
import anthropic
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, PRODUCT_NAME

client = anthropic.Anthropic(base_url=OLLAMA_BASE_URL, api_key="ollama")

MAX_CAPTION_LENGTH = 2200
MIN_HASHTAGS = 10
MAX_HASHTAGS = 30


import re

def _strip_emoji(text: str) -> str:
    text = re.sub(r'[\U0001F000-\U0010FFFF]', '', text)
    text = re.sub(r'[\u2600-\u27BF]', '', text)
    return text.strip()


def _check_basics(script: dict, image_paths: list) -> list:
    """Verificações técnicas básicas antes de chamar a IA."""
    issues = []

    caption = script.get("caption", "")
    if len(caption) > MAX_CAPTION_LENGTH:
        issues.append(f"Caption muito longa: {len(caption)} chars (máx {MAX_CAPTION_LENGTH})")

    hashtags = script.get("hashtags", [])
    if len(hashtags) < MIN_HASHTAGS:
        issues.append(f"Poucos hashtags: {len(hashtags)} (mín {MIN_HASHTAGS})")
    if len(hashtags) > MAX_HASHTAGS:
        issues.append(f"Hashtags demais: {len(hashtags)} (máx {MAX_HASHTAGS})")

    slides = script.get("slides", [])
    if not slides:
        issues.append("Nenhum slide no roteiro")

    # Verifica texto de cada slide (o que vai aparecer NA IMAGEM)
    for slide in slides:
        headline = slide.get("headline", "")
        body     = slide.get("body_text", "")
        n        = slide.get("slide_number", "?")

        # Emojis em texto de imagem viram quadrados
        if headline != _strip_emoji(headline):
            issues.append(f"Slide {n}: headline tem emoji (vira quadrado na imagem) — remova: '{headline}'")
        if body != _strip_emoji(body):
            issues.append(f"Slide {n}: body_text tem emoji (vira quadrado na imagem) — remova: '{body}'")

        # Textos muito longos não cabem na imagem
        if len(headline.split()) > 10:
            issues.append(f"Slide {n}: headline muito longa ({len(headline.split())} palavras, máx 10)")
        if len(body.split()) > 25:
            issues.append(f"Slide {n}: body_text muito longo ({len(body.split())} palavras, máx 25)")

    if not image_paths:
        issues.append("Nenhuma imagem gerada")

    for path in image_paths:
        if not os.path.exists(path):
            issues.append(f"Arquivo não encontrado: {path}")
        elif os.path.getsize(path) < 10000:
            issues.append(f"Imagem muito pequena: {path}")

    return issues


def run(strategy: dict, script: dict, image_paths: list) -> dict:
    """
    Revisa o conteúdo completo.
    Retorna: {"approved": bool, "score": int, "issues": [], "suggestions": ""}
    """
    # Verificações técnicas
    basic_issues = _check_basics(script, image_paths)
    if basic_issues:
        return {
            "approved": False,
            "score": 0,
            "issues": basic_issues,
            "suggestions": "Corrigir problemas técnicos antes de prosseguir."
        }

    # Revisão por IA
    slides_summary = "\n".join([
        f"Slide {s['slide_number']}: {s.get('headline', '')} | {s.get('body_text', '')}"
        for s in script.get("slides", [])
    ])

    pillar_name = strategy.get("pillar_name", strategy.get("content_type", ""))

    prompt = f"""Voce e um revisor de marketing e Brand Guardian especializado em Instagram para pequenos negocios brasileiros.

Sua funcao: garantir que cada post seja profissional, fiel a voz da marca e com potencial real de engajamento.

PRODUTO: {PRODUCT_NAME}
VOZ DA MARCA: amigavel, direto e empoderador — parceiro do pequeno empreendedor brasileiro. Sem ingles desnecessario ou termos tecnicos.
PILAR DO POST: {pillar_name}
PUBLICO-ALVO: {strategy.get('target_audience')}
TOM ESPERADO: {strategy.get('tone')}
CTA ESPERADO: {strategy.get('call_to_action')}

CONTEUDO PARA REVISAO:

Slides (texto que aparece NA IMAGEM):
{slides_summary}

Caption:
{script.get('caption', '')}

Hashtags ({len(script.get('hashtags', []))}):
{' '.join(script.get('hashtags', []))}

━━━ AVALIE NOS 4 CRITERIOS (cada um vale ate 25 pontos) ━━━

1. FORCA DO HOOK — SLIDE 1 (0-25 pts)
   O headline do slide 1 para o scroll em 2 segundos?
   E especifico para um nicho ou situacao real (nao generico)?
   Fala de uma dor real ou faz uma promessa concreta?
   [25: hook poderoso e especifico | 15: bom mas pode melhorar | 5: generico ou fraco]

2. VOZ DA MARCA (0-25 pts)
   Usa linguagem simples do dia a dia?
   Tem empatia real com a dor do pequeno empreendedor?
   Evita ingles desnecessario e termos tecnicos?
   O tom e proximo, humano e confiante — sem ser arrogante?
   [25: perfeito na voz | 15: adequado | 5: formal demais ou artificioso]

3. ESTRUTURA AIDA DA CAPTION (0-25 pts)
   A (Atencao): abre forte, repete ou expande o hook?
   I (Interesse): contexto e empatia com a situacao do profissional?
   D (Desejo): beneficios concretos do Top Agenda mencionados?
   A (Acao): CTA claro com link topagenda.online?
   [25: AIDA completo e fluido | 15: estrutura presente mas fraca | 5: caption generica]

4. ESPECIFICIDADE E CONVERSAO (0-25 pts)
   Fala com um nicho especifico (salao, barbearia, clinica)?
   Menciona um beneficio concreto do Top Agenda?
   Tem potencial de gerar saves, comentarios ou cliques?
   O CTA e claro e remove uma objecao?
   [25: especifico, relevante e com alto potencial | 15: medio | 5: muito generico]

SCORE FINAL = soma dos 4 criterios (max 100). Aprovado se score >= 80.

Retorne APENAS um JSON valido:
{{
  "approved": true ou false,
  "score": numero de 0 a 100,
  "hook_score": numero de 0 a 25,
  "voice_score": numero de 0 a 25,
  "aida_score": numero de 0 a 25,
  "relevance_score": numero de 0 a 25,
  "issues": ["problema especifico 1", "problema especifico 2"],
  "suggestions": "sugestoes acionaveis e especificas de melhoria",
  "strengths": ["ponto forte 1", "ponto forte 2"]
}}"""

    response = client.messages.create(
        model=OLLAMA_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    review = json.loads(text)

    # Garante consistência: approved só é True se score >= 80
    score = review.get("score", 0)
    if score < 80:
        review["approved"] = False
    elif score >= 80 and not review.get("approved"):
        review["approved"] = True  # score alto mas approved=False é inconsistente

    hook_s     = review.get("hook_score", "?")
    voice_s    = review.get("voice_score", "?")
    aida_s     = review.get("aida_score", "?")
    relev_s    = review.get("relevance_score", "?")
    print(f"  [Revisor] Score: {score}/100 | Hook:{hook_s} Voz:{voice_s} AIDA:{aida_s} Relev:{relev_s} | Aprovado: {review.get('approved')}")

    if review.get("issues"):
        for issue in review["issues"]:
            print(f"  [Revisor] Issue: {issue}")

    return review
