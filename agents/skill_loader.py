"""
Carrega o arquivo de skill .md de um agente.
Os skills ficam em references/agents/<nome>.md
"""
import os

AGENTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "references", "agents"
)


def load(agent_name: str, max_chars: int = 3000) -> str:
    """
    Retorna o conteudo do skill file do agente, ou string vazia se nao existir.
    Uso: skill = skill_loader.load("strategist")
    """
    path = os.path.join(AGENTS_DIR, f"{agent_name}.md")
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:max_chars]
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"  [SkillLoader] Erro ao ler {agent_name}.md: {e}")
        return ""
