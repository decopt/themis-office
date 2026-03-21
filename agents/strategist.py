"""
Agente 1 - Estrategista
Define o pilar de conteudo, tema e orientacoes para o post.

Incorpora:
- Content Pillars + Brand Guardian (agency-agents)
- Social Content Framework (marketingskills)
"""
import json
import random
from datetime import datetime
from google import genai
from config import (
    GOOGLE_API_KEY, PRODUCT_NAME, PRODUCT_URL, PRODUCT_DESCRIPTION,
    GEMINI_TEXT_MODEL, CONTENT_PILLARS, PILLAR_WEIGHTS,
    HOOK_TYPES, BRAND_VOICE, TARGET_NICHES, BRAZILIAN_SEASONAL,
)

client = genai.Client(api_key=GOOGLE_API_KEY)


def _pick_pillar() -> dict:
    """Seleciona pilar com base nos pesos estrategicos."""
    return random.choices(CONTENT_PILLARS, weights=PILLAR_WEIGHTS, k=1)[0]


def _seasonal_context() -> str:
    """Retorna contexto sazonal relevante para o mes atual."""
    return BRAZILIAN_SEASONAL.get(datetime.now().month, "")


def _format_types_for_pillar(pillar: dict) -> str:
    formats_map = {
        "carousel": "carrossel (3-5 slides)",
        "single_post": "post unico impactante",
        "tips_post": "post com dica rapida",
        "feature_showcase": "apresentacao de funcionalidade",
        "motivacional": "post motivacional",
    }
    return " ou ".join(formats_map.get(f, f) for f in pillar["best_formats"])


def run(post_count_today: int = 0) -> dict:
    """
    Define a estrategia do proximo post usando pilares estrategicos.
    Retorna um dicionario com pilar, tema, hook, orientacoes visuais e CTA.
    """
    pillar = _pick_pillar()
    hook_type = pillar["default_hook"]
    hook_description = HOOK_TYPES.get(hook_type, "")
    seasonal = _seasonal_context()
    niche_focus = random.sample(TARGET_NICHES, 3)
    formats = _format_types_for_pillar(pillar)
    today = datetime.now().strftime("%A, %d/%m/%Y")

    seasonal_section = f"\nCONTEXTO SAZONAL: {seasonal}" if seasonal else ""

    prompt = f"""Voce e um estrategista de marketing digital especializado em aplicativos de agendamento para pequenos negocios brasileiros.

PRODUTO: {PRODUCT_NAME}
DESCRICAO: {PRODUCT_DESCRIPTION}
SITE: {PRODUCT_URL}
INSTAGRAM: @topagenda.online

VOZ DA MARCA:
{BRAND_VOICE}

PILAR DE CONTEUDO SELECIONADO: {pillar['name']}
OBJETIVO DO PILAR: {pillar['description']}
FORMATOS RECOMENDADOS: {formats}
CTA DO PILAR: {pillar['cta']}

TIPO DE HOOK PARA O PRIMEIRO SLIDE: {hook_type}
COMO CRIAR ESSE HOOK: {hook_description}

NICHOS EM FOCO HOJE: {', '.join(niche_focus)}{seasonal_section}

DATA: {today}
POSTS PUBLICADOS HOJE: {post_count_today}

Com base nesse pilar e contexto, defina uma pauta criativa e ESPECIFICA para o Instagram do Top Agenda.
Seja especifico — evite temas genericos. Pense no que um {niche_focus[0]} ou {niche_focus[1]} sentiria ao ver esse post.

Retorne APENAS um JSON valido:
{{
  "pillar_id": "{pillar['id']}",
  "pillar_name": "{pillar['name']}",
  "content_type": "carousel|single_post|tips_post|feature_showcase|motivacional",
  "slides": 1,
  "theme": "tema especifico e concreto (ex: 'Como o barbeiro X parou de perder clientes por falta de confirmacao')",
  "main_message": "mensagem central que o usuario deve lembrar",
  "hook_type": "{hook_type}",
  "hook_direction": "orientacao especifica de como escrever o hook do slide 1 para esse tema",
  "target_audience": "profissional especifico em situacao real (ex: 'barbeiro que ancora 80% da agenda pelo WhatsApp')",
  "tone": "tom do post (ex: empatico e direto, energizante, provocador e acolhedor)",
  "call_to_action": "{pillar['cta']}",
  "visual_direction": "cena especifica para a foto: nicho, ambiente, mood, o que o profissional esta fazendo",
  "niche_focus": {json.dumps(niche_focus, ensure_ascii=False)},
  "content_pillars": ["{pillar['id']}", "engajamento"]
}}

REGRAS:
- content_type carousel: slides entre 3 e 5
- content_type single_post ou motivacional: slides = 1
- content_type tips_post: slides = 1
- content_type feature_showcase: slides entre 2 e 4
- theme deve ser especifico, nao generico"""

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=prompt
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    strategy = json.loads(text)

    # Garante que slides seja int valido
    try:
        strategy["slides"] = int(strategy["slides"])
    except (ValueError, TypeError, KeyError):
        strategy["slides"] = 1
    strategy["slides"] = max(1, min(5, strategy["slides"]))

    return strategy
