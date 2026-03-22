import os
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
PUBLIC_IMAGE_BASE_URL = os.getenv("PUBLIC_IMAGE_BASE_URL", "http://5.189.147.171:8080")

# Telegram — aprovacao humana antes de publicar
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
POST_TIMES = os.getenv("POST_TIMES", "09:00,12:00,18:00").split(",")
MAX_POSTS_PER_DAY = int(os.getenv("MAX_POSTS_PER_DAY", "3"))

# Produto
PRODUCT_NAME = "Top Agenda"
PRODUCT_URL = "https://topagenda.online"
PRODUCT_DESCRIPTION = "App de agenda e produtividade brasileiro para organizar tarefas, rotinas e compromissos do dia a dia."

# Identidade visual (cores reais do Top Agenda)
BRAND_PRIMARY_COLOR = (27, 111, 187)    # azul
BRAND_GREEN_COLOR   = (77, 182, 72)     # verde
BRAND_SECONDARY_COLOR = (255, 255, 255) # branco
BRAND_ACCENT_COLOR = (255, 193, 7)      # amarelo CTA

# Instagram
INSTAGRAM_HANDLE = "@topagenda.online"

# Pastas (env var permite override local; Docker usa /app/output e /app/assets)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")
ASSETS_DIR = os.getenv("ASSETS_DIR", "/app/assets")

# Ollama — modelo local gratuito (roda na VPS)
OLLAMA_BASE_URL  = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL     = os.getenv("OLLAMA_MODEL", "qwen3.5")

# ── Pilares de Conteúdo Estratégicos ─────────────────────────
# Inspirado em: agency-agents (Content Creator + Brand Guardian)
#               marketingskills (social-content + copywriting skills)
CONTENT_PILLARS = [
    {
        "id": "problema_solucao",
        "name": "Problema e Solucao",
        "description": (
            "Mostre a dor real do dono de negocio e como o Top Agenda resolve. "
            "Ex: perder horas no WhatsApp marcando horario, esquecer de confirmar cliente, "
            "agenda bagunçada no caderno, cliente que some sem avisar."
        ),
        "best_formats": ["carousel", "single_post"],
        "default_hook": "pergunta_provocativa",
        "cta": "Comece gratis hoje",
    },
    {
        "id": "educacao",
        "name": "Educacao e Dicas",
        "description": (
            "Ensine algo util: como organizar agenda de atendimentos, como nao perder clientes, "
            "como cobrar confirmacao de horario, como divulgar link de agendamento, "
            "como automatizar lembretes."
        ),
        "best_formats": ["carousel", "tips_post"],
        "default_hook": "lista_numerada",
        "cta": "Experimente gratis",
    },
    {
        "id": "prova_social",
        "name": "Quem Usa o Top Agenda",
        "description": (
            "Mostre os tipos de profissionais que usam: cabeleireiro, barbeiro, manicure, "
            "nutricionista, esteticista, personal trainer. "
            "Foco em transformacao: como ficou mais organizado e profissional."
        ),
        "best_formats": ["carousel", "feature_showcase"],
        "default_hook": "identificacao_nicho",
        "cta": "Junte-se a milhares de profissionais",
    },
    {
        "id": "produto",
        "name": "Funcionalidade em Destaque",
        "description": (
            "Destaque uma feature especifica: link de agendamento personalizado, "
            "lembretes automaticos por WhatsApp, gestao de clientes, relatorio de atendimentos, "
            "horarios disponiveis 24h, cancelamento sem constrangimento."
        ),
        "best_formats": ["feature_showcase", "carousel"],
        "default_hook": "promessa_direta",
        "cta": "Ver como funciona",
    },
    {
        "id": "conversao",
        "name": "Conversao Direta",
        "description": (
            "Oferta direta com beneficio imediato: 14 dias gratis sem cartao, "
            "cancela quando quiser, comeca em 5 minutos. Remove objecoes de preco e complexidade."
        ),
        "best_formats": ["single_post"],
        "default_hook": "promessa_direta",
        "cta": "14 dias gratis — sem cartao de credito",
    },
    {
        "id": "inspiracao",
        "name": "Inspiracao Empreendedora",
        "description": (
            "Frases e insights para donos de negocio. Foco em autonomia, crescimento, "
            "valorizar o proprio trabalho, organizacao como diferencial competitivo."
        ),
        "best_formats": ["single_post", "motivacional"],
        "default_hook": "afirmacao_controversa",
        "cta": "Organize seu negocio",
    },
]

# Pesos de frequencia por pilar (soma = 100)
PILLAR_WEIGHTS = [25, 25, 20, 15, 10, 5]

# Tipos de hook para o primeiro slide (para o scroll)
HOOK_TYPES = {
    "pergunta_provocativa": (
        "Pergunta que faz o usuario parar o scroll — fala de uma dor especifica. "
        "Ex: 'Voce ainda marca horario pelo WhatsApp?' / 'Seu negocio perde clientes toda semana?'"
    ),
    "lista_numerada": (
        "Promessa numerada que gera curiosidade imediata. "
        "Ex: '5 erros que fazem voce perder clientes' / '3 formas de nunca mais perder horario'"
    ),
    "identificacao_nicho": (
        "Fala diretamente com um tipo de profissional em uma situacao real. "
        "Ex: 'Para todo cabeleireiro que ainda usa caderno de horario' / 'Se voce e barbeiro, isso e para voce'"
    ),
    "promessa_direta": (
        "Beneficio claro e imediato, sem rodeios. "
        "Ex: 'Receba agendamentos 24h sem responder uma mensagem' / 'Organize sua agenda em 5 minutos'"
    ),
    "afirmacao_controversa": (
        "Afirmacao que desafia o status quo e provoca reacao. "
        "Ex: 'Agenda no papel esta matando seu negocio' / 'WhatsApp nao e sistema de agendamento'"
    ),
    "estatistica": (
        "Dado ou numero surpreendente que gera reflexao. "
        "Ex: '1 em cada 3 clientes nao volta sem confirmacao automatica' / 'Profissionais organizados faturam mais'"
    ),
}

# Voz da marca (Brand Voice — agency-agents Brand Guardian)
BRAND_VOICE = (
    "Tom: amigavel, direto e empoderador — como um parceiro do pequeno empreendedor brasileiro. "
    "Personalidade: confiante sem ser arrogante, especialista sem ser distante. "
    "Linguagem: simples, do dia a dia, sem ingles desnecessario, sem termos tecnicos. "
    "Evitar: superlativos vazios ('incrivel', 'revolucionario'), promessas impossiveis, formalidade excessiva. "
    "Usar: numeros concretos quando possivel, empatia real com as dores do empreendedor, humor leve."
)

# Nichos alvo de pequenos negocios brasileiros
TARGET_NICHES = [
    "cabeleireiro", "barbeiro", "manicure", "pedicure",
    "nutricionista", "esteticista", "personal trainer",
    "massagista", "fisioterapeuta", "acupunturista",
    "tatuador", "designer de sobrancelha", "micropigmentador",
    "dentista", "psicologo", "professor particular",
]

# Contexto sazonal brasileiro por mes
BRAZILIAN_SEASONAL = {
    2: "Carnaval — agenda pos-feriado, retomada de atendimentos",
    3: "Marco — Dia Internacional da Mulher (8/3), homenagem as empreendedoras",
    5: "Maio — Dia das Maes (2o domingo), saloes e clinicas no pico de demanda",
    6: "Junho — Dia dos Namorados (12/6), saloes e spas em alta",
    8: "Agosto — Dia dos Pais (2o domingo), barbearias lotadas",
    9: "Setembro Amarelo — saude mental, equilibrio vida e trabalho do empreendedor",
    10: "Outubro Rosa — clinicas e esteticistas em alta, saude da mulher",
    11: "Novembro — Black Friday, agenda cheia, importancia de sistema organizado",
    12: "Dezembro — saloes e barbearias no pico, virada do ano e planejamento",
}
