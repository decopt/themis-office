"""
Agente 2 - Roteirista
Cria o roteiro completo: textos dos slides, legenda (estrutura AIDA) e hashtags (3 camadas).

Incorpora:
- Hook Framework (agency-agents Content Creator)
- AIDA Copywriting (marketingskills copywriting skill)
- 3-tier hashtag strategy (marketingskills social-content skill)
"""
import json
import random
from agents import skill_loader, llm
from config import (
    PRODUCT_NAME, PRODUCT_URL, INSTAGRAM_HANDLE,
    HOOK_TYPES, BRAND_VOICE,
)

SKILL = skill_loader.load("scriptwriter")


# Hashtags da marca (sempre incluidas)
HASHTAGS_BRANDED = [
    "#topagenda", "#agendadigital", "#agendamentoonline",
    "#sistemadeagendamento", "#agendaprofissional",
]

# Hashtags por nicho (camada 1 — alta especificidade)
HASHTAGS_NICHE = {
    "cabeleireiro": ["#salaobeleza", "#cabeleireiro", "#salaodebeleza", "#hairstylist", "#cabelobrasil"],
    "barbeiro":     ["#barbearia", "#barbeiro", "#barba", "#barberlife", "#barbeirosbrasil"],
    "manicure":     ["#manicure", "#unhas", "#naildesign", "#nailart", "#manicurebrasil"],
    "pedicure":     ["#pedicure", "#unhasdospes"],
    "nutricionista":["#nutricionista", "#nutricao", "#saude", "#alimentacaosaudavel", "#emagrecimento"],
    "esteticista":  ["#estetica", "#esteticista", "#beleza", "#skincare", "#esteticabrasil"],
    "personal":     ["#personaltrainer", "#fitness", "#treino", "#academia", "#emagrecimento"],
    "massagista":   ["#massagem", "#massagista", "#bemestar", "#relaxamento"],
    "fisioterapeuta":["#fisioterapia", "#fisioterapeuta", "#saude", "#reabilitacao"],
    "tatuador":     ["#tatuagem", "#tatuador", "#tattoo", "#tattooartist", "#tattoolife"],
    "dentista":     ["#dentista", "#odontologia", "#saude", "#sorriso", "#clinicaodontologica"],
    "psicologo":    ["#psicologo", "#psicologia", "#saudemental", "#terapia"],
    "default":      ["#pequenegocios", "#empreendedor", "#empreendedorismo", "#prestadordeservico"],
}

# Hashtags de medio alcance (camada 2 — contexto)
HASHTAGS_MEDIUM = [
    "#produtividade", "#organizacao", "#gestaodetempo", "#rotina", "#foco",
    "#empreendedorismo", "#pequenegocios", "#trabalhoporconta",
    "#atendimento", "#profissional", "#gestao", "#agendamento",
    "#automatizacao", "#clientesfidelizados",
]

# Hashtags de amplo alcance (camada 3 — descoberta)
HASHTAGS_BROAD = [
    "#brasil", "#dicas", "#dicasdenegocios", "#trabalho", "#sucesso",
    "#negocios", "#empreender", "#dicasdeprodutividade",
]


def _get_niche_hashtags(niche_focus: list) -> list:
    """Seleciona hashtags de nicho com base nos nichos em foco."""
    tags = []
    for niche in niche_focus:
        for key in HASHTAGS_NICHE:
            if key in niche.lower():
                tags.extend(HASHTAGS_NICHE[key])
                break
    if not tags:
        tags = HASHTAGS_NICHE["default"]
    return list(dict.fromkeys(tags))[:10]


def run(strategy: dict) -> dict:
    """
    Cria o roteiro completo baseado na estrategia.
    Retorna textos dos slides, legenda AIDA e hashtags em 3 camadas.
    """
    slides_count = strategy.get("slides", 1)
    hook_type = strategy.get("hook_type", "pergunta_provocativa")
    hook_description = HOOK_TYPES.get(hook_type, "")
    hook_direction = strategy.get("hook_direction", "")
    niche_focus = strategy.get("niche_focus", ["profissional"])
    pillar_name = strategy.get("pillar_name", strategy.get("content_type", ""))

    skill_section = f"\n{SKILL}\n---\n" if SKILL else ""

    prompt = f"""{skill_section}Voce e um redator especializado em conteudo de alta conversao para Instagram de pequenos negocios brasileiros.

PRODUTO: {PRODUCT_NAME} — {PRODUCT_URL}
INSTAGRAM: {INSTAGRAM_HANDLE}

VOZ DA MARCA:
{BRAND_VOICE}

ESTRATEGIA RECEBIDA:
- Pilar: {pillar_name}
- Tema especifico: {strategy.get('theme')}
- Mensagem central: {strategy.get('main_message')}
- Publico-alvo: {strategy.get('target_audience')}
- Tom: {strategy.get('tone')}
- CTA: {strategy.get('call_to_action')}
- Numero de slides: {slides_count}
- Nichos em foco: {', '.join(niche_focus)}

━━━ REGRA DO HOOK (SLIDE 1 — O MAIS IMPORTANTE) ━━━
Tipo de hook escolhido: {hook_type}
Como criar: {hook_description}
Orientacao especifica: {hook_direction}

O SLIDE 1 e o que aparece no feed antes do usuario clicar.
Ele precisa PARAR O SCROLL em menos de 2 segundos.
Seja especifico ao nicho. Fale de uma DOR REAL.

━━━ ESTRUTURA DA CAPTION (FORMATO AIDA) ━━━
A - ATENCAO: 1 linha de abertura forte — repete ou expande o hook.
I - INTERESSE: 1-2 linhas de empatia — mostre que voce entende a dor.
D - DESEJO: 1-2 linhas com o beneficio concreto do Top Agenda.
A - ACAO: 1 linha de CTA. Sempre termine com: "Acesse topagenda.online e comece gratis hoje 👇"

CAPTION TOTAL: maximo 150 palavras. Seja direto e objetivo.

Crie o roteiro completo. Retorne APENAS um JSON valido:
{{
  "slides": [
    {{
      "slide_number": 1,
      "headline": "HOOK EM MAIUSCULAS, max 7 palavras, sem emoji — o gancho principal",
      "body_text": "complemento direto que reforça o hook, max 10 palavras, sem emoji"
    }}
  ],
  "caption": "legenda curta AIDA em portugues brasileiro com emojis, maximo 150 palavras, termina com CTA e link",
  "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
  "alt_text": "descricao acessivel da imagem principal em portugues"
}}

REGRAS CRITICAS:
- headline e body_text NUNCA devem ter emojis (viram quadrados na imagem)
- headline: MAIUSCULAS, max 7 palavras, deve ser o hook — especifico e impactante
- body_text: max 10 palavras, sem emoji, complementa o headline
- Caption: MAXIMO 150 PALAVRAS — seja direto, sem enrolacao
- hashtags: EXATAMENTE 3 a 5 hashtags — apenas os mais relevantes para o nicho
- Para carrossel: cada slide deve ter uma ideia propria que avança a narrativa
- Slide 1 = hook / Slides do meio = desenvolvimento / Ultimo slide = CTA"""

    text = llm.generate(prompt, max_tokens=8192, json_mode=True)
    text = llm.extract_json(text)
    script = json.loads(text)

    # Garante entre 3 e 5 hashtags: usa as do LLM + completa com branded/niche se faltar
    llm_tags = script.get("hashtags", [])[:5]
    if len(llm_tags) < 3:
        niche_tags = _get_niche_hashtags(niche_focus)
        for tag in HASHTAGS_BRANDED + niche_tags:
            if tag not in llm_tags:
                llm_tags.append(tag)
            if len(llm_tags) >= 5:
                break
    script["hashtags"] = llm_tags[:5]

    return script
