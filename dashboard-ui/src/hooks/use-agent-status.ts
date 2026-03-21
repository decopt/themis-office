import { useState, useEffect, useCallback } from "react";

interface AgentMeta {
  id: string;
  name: string;
  icon: string;
}

interface Stats {
  posts_today: number;
  max_today: number;
  total_published: number;
  avg_score: number;
  schedule: string[];
}

interface StatusResponse {
  running: boolean;
  current_agent: string | null;
  agents: Record<string, string>;
  agent_details: Record<string, string>;
  agents_meta: AgentMeta[];
  last_result?: {
    success: boolean;
    timestamp: string;
  };
  stats: Stats;
}

// Fallback agents when API is not reachable
const FALLBACK_AGENTS: AgentMeta[] = [
  { id: "strategist",   name: "Estrategista", icon: "brain" },
  { id: "scriptwriter", name: "Roteirista",   icon: "pen" },
  { id: "designer",     name: "Designer",     icon: "image" },
  { id: "editor",       name: "Editor",       icon: "wand" },
  { id: "reviewer",     name: "Revisor",      icon: "check" },
  { id: "publisher",    name: "Publisher",     icon: "send" },
];

export function useAgentStatus() {
  const [agents, setAgents] = useState<Record<string, string>>({});
  const [agentDetails, setAgentDetails] = useState<Record<string, string>>({});
  const [agentsMeta, setAgentsMeta] = useState<AgentMeta[]>(FALLBACK_AGENTS);
  const [stats, setStats] = useState<Stats | null>(null);
  const [running, setRunning] = useState(false);
  const [pipelineLabel, setPipelineLabel] = useState("6 Agentes Ativos");

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/status");
      const data: StatusResponse = await res.json();

      setAgents(data.agents || {});
      setAgentDetails(data.agent_details || {});
      if (data.agents_meta?.length) setAgentsMeta(data.agents_meta);
      setStats(data.stats || null);
      setRunning(data.running || false);

      if (data.running) {
        const current = data.agents_meta?.find(a => a.id === data.current_agent);
        setPipelineLabel(current ? `⚡ ${current.name} trabalhando...` : "⚡ Executando...");
      } else if (data.last_result) {
        const time = data.last_result.timestamp
          ? new Date(data.last_result.timestamp).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })
          : "";
        setPipelineLabel(
          data.last_result.success
            ? `✓ Concluido ${time}`
            : `✕ Falhou ${time}`
        );
      } else {
        setPipelineLabel("6 Agentes Ativos");
      }
    } catch {
      // API not available — keep fallback
    }
  }, []);

  const triggerRun = useCallback(async () => {
    try {
      const res = await fetch("/api/run", { method: "POST" });
      const data = await res.json();
      if (data.error) {
        console.error(data.error);
      }
    } catch (e) {
      console.error("Erro ao iniciar pipeline", e);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  return { agents, agentDetails, agentsMeta, stats, running, pipelineLabel, triggerRun };
}
