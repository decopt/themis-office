import { useAgentStatus } from "@/hooks/use-agent-status";

const AGENT_DESCRIPTIONS: Record<string, string> = {
  strategist:   "Define temas, pilares e estrategia de conteudo para o Instagram",
  scriptwriter: "Cria roteiros, legendas e hashtags otimizadas para engajamento",
  designer:     "Gera imagens e carrosseis com design profissional",
  editor:       "Edita, melhora e aplica filtros nas imagens geradas",
  reviewer:     "Avalia qualidade, score e aprova o conteudo antes de publicar",
  publisher:    "Publica o post no Instagram via Graph API",
};

const AGENT_ICONS: Record<string, string> = {
  strategist:   "🧠",
  scriptwriter: "✍️",
  designer:     "🎨",
  editor:       "🪄",
  reviewer:     "✅",
  publisher:    "🚀",
};

const STATUS_LABELS: Record<string, string> = {
  idle:    "Aguardando",
  running: "Trabalhando...",
  done:    "Concluido",
  error:   "Erro",
};

const STATUS_COLORS: Record<string, string> = {
  idle:    "text-muted-foreground",
  running: "text-cyan-glow animate-pulse-glow",
  done:    "text-green-400",
  error:   "text-red-400",
};

export const HUD = () => {
  const { agents, agentsMeta, stats, running, pipelineLabel, triggerRun } = useAgentStatus();

  return (
    <div className="absolute inset-0 pointer-events-none z-10">
      {/* Title */}
      <div className="absolute top-6 left-1/2 -translate-x-1/2 text-center">
        <h1 className="font-display text-2xl md:text-4xl tracking-[0.3em] text-gold animate-breathe">
          TOP AGENDA
        </h1>
        <p className="text-xs md:text-sm tracking-[0.5em] text-muted-foreground mt-1 font-body">
          EQUIPE DE MARKETING IA
        </p>
      </div>

      {/* Left panel — first 3 agents */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 space-y-2">
        {agentsMeta.slice(0, 3).map((agent, i) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            status={agents[agent.id] || "idle"}
            index={i}
          />
        ))}
      </div>

      {/* Right panel — last 3 agents */}
      <div className="absolute right-4 top-1/2 -translate-y-1/2 space-y-2">
        {agentsMeta.slice(3).map((agent, i) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            status={agents[agent.id] || "idle"}
            index={i + 3}
          />
        ))}
      </div>

      {/* Run button */}
      <div className="absolute bottom-20 left-1/2 -translate-x-1/2 pointer-events-auto">
        <button
          onClick={triggerRun}
          disabled={running}
          className="bg-gold/90 hover:bg-gold text-background font-display tracking-wider text-xs px-6 py-2 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-[0_0_20px_rgba(212,175,55,0.4)]"
        >
          {running ? "⚡ EXECUTANDO..." : "▶ EXECUTAR PIPELINE"}
        </button>
      </div>

      {/* Bottom status bar */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
        <div className="bg-card/80 backdrop-blur-sm border border-border rounded-lg px-6 py-2 flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${running ? 'bg-cyan-glow animate-pulse-glow' : 'bg-green-500'}`} />
            <span className="text-xs text-muted-foreground font-body">{pipelineLabel}</span>
          </div>
          {stats && (
            <>
              <div className="w-px h-4 bg-border" />
              <span className="text-xs text-gold font-display tracking-wider">
                {stats.posts_today}/{stats.max_today} posts hoje
              </span>
              <div className="w-px h-4 bg-border" />
              <span className="text-xs text-muted-foreground font-body">
                Score: {stats.avg_score || "—"}/100
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

interface AgentMeta {
  id: string;
  name: string;
  icon: string;
}

const AgentCard = ({ agent, status, index }: { agent: AgentMeta; status: string; index: number }) => (
  <div
    className={`bg-card/70 backdrop-blur-sm border rounded-lg px-3 py-2 min-w-[160px] transition-all ${
      status === 'running' ? 'border-cyan-glow/50 shadow-[0_0_12px_rgba(0,229,255,0.15)]' :
      status === 'done'    ? 'border-green-500/30' :
      status === 'error'   ? 'border-red-500/30' :
      'border-border'
    }`}
    style={{ animationDelay: `${index * 0.5}s` }}
  >
    <div className="flex items-center gap-2 mb-1">
      <span className={`w-1.5 h-1.5 rounded-full ${
        status === 'running' ? 'bg-cyan-glow animate-pulse-glow' :
        status === 'done'    ? 'bg-green-500' :
        status === 'error'   ? 'bg-red-500' :
        'bg-muted-foreground/50'
      }`} />
      <span className="text-xs font-display text-gold tracking-wider">
        {AGENT_ICONS[agent.id] || "🤖"} {agent.name}
      </span>
    </div>
    <p className="text-[10px] text-muted-foreground font-body">{AGENT_DESCRIPTIONS[agent.id] || agent.icon}</p>
    <p className={`text-[10px] font-body ${STATUS_COLORS[status] || STATUS_COLORS.idle}`}>
      {STATUS_LABELS[status] || status}
    </p>
  </div>
);

export default HUD;
