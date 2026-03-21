import { Canvas } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera, Html } from "@react-three/drei";
import { Suspense } from "react";
import Room from "./Room";
import MainDesk from "./MainDesk";
import AIWorkstation from "./AIWorkstation";
import HumanFigure from "./HumanFigure";
import { useAgentStatus } from "@/hooks/use-agent-status";

const AGENT_IDS = ["strategist", "scriptwriter", "designer", "editor", "reviewer", "publisher", "telegram_approver"];

const AI_AGENTS = [
  { id: "strategist",   name: "Estrategista" },
  { id: "scriptwriter", name: "Roteirista" },
  { id: "designer",     name: "Designer" },
  { id: "editor",       name: "Editor" },
  { id: "reviewer",     name: "Revisor" },
  { id: "publisher",    name: "Publisher" },
];

const SUIT_COLORS = [
  "#5838c4", "#0ea5e9", "#f59e0b", "#22c55e", "#ec4899", "#f97316",
];

const SKIN_TONES = ["#E8C4A0", "#D4A574", "#C68E5B", "#B87A4A", "#A0785C", "#8D6E4C"];

const IDLE_PHRASES: Record<string, string[]> = {
  strategist:   ["Analisando tendencias...", "Pesquisando nicho...", "Planejando conteudo..."],
  scriptwriter: ["Esperando briefing...", "Revisando templates...", "Organizando ideias..."],
  designer:     ["Ajustando paleta...", "Preparando canvas...", "Buscando referencias..."],
  editor:       ["Calibrando filtros...", "Testando presets...", "Pronto para editar..."],
  reviewer:     ["Checklist pronto...", "Aguardando review...", "Critérios definidos..."],
  publisher:    ["API conectada ✓", "Token válido ✓", "Aguardando post..."],
};

const RUNNING_PHRASES: Record<string, string[]> = {
  strategist:   ["Definindo tema...", "Analisando pilares...", "Scoring topics..."],
  scriptwriter: ["Escrevendo roteiro...", "Criando caption...", "Gerando hashtags..."],
  designer:     ["Gerando slide 1...", "Renderizando...", "Aplicando estilo..."],
  editor:       ["Ajustando cores...", "Aplicando filtros...", "Criando story..."],
  reviewer:     ["Verificando texto...", "Avaliando imagens...", "Calculando score..."],
  publisher:    ["Fazendo upload...", "Criando container...", "Publicando post..."],
};

const ERROR_PHRASES: Record<string, string> = {
  strategist:   "Erro na estratégia!",
  scriptwriter: "Falha no roteiro!",
  designer:     "Erro ao gerar imagens!",
  editor:       "Falha na edição!",
  reviewer:     "Reprovado! Refazendo...",
  publisher:    "Erro ao publicar!",
};

const DONE_PHRASES: Record<string, string> = {
  strategist:   "Tema definido ✓",
  scriptwriter: "Roteiro pronto ✓",
  designer:     "Imagens geradas ✓",
  editor:       "Edição concluída ✓",
  reviewer:     "Aprovado ✓",
  publisher:    "Publicado ✓",
};

const SpeechBubble = ({ position, text, status }: { position: [number, number, number]; text: string; status: string }) => {
  const bgColor = status === "error" ? "rgba(239,68,68,0.9)"
    : status === "running" ? "rgba(0,229,255,0.9)"
    : status === "done" ? "rgba(34,197,94,0.9)"
    : "rgba(60,60,60,0.85)";

  return (
    <Html position={position} center distanceFactor={8} sprite>
      <div style={{
        background: bgColor,
        color: "#fff",
        padding: "4px 10px",
        borderRadius: "10px",
        fontSize: "11px",
        fontFamily: "monospace",
        whiteSpace: "nowrap",
        maxWidth: "180px",
        overflow: "hidden",
        textOverflow: "ellipsis",
        boxShadow: `0 0 8px ${bgColor}`,
        border: "1px solid rgba(255,255,255,0.15)",
        pointerEvents: "none",
        userSelect: "none",
      }}>
        {text}
        <div style={{
          position: "absolute",
          bottom: "-6px",
          left: "50%",
          transform: "translateX(-50%)",
          width: 0,
          height: 0,
          borderLeft: "6px solid transparent",
          borderRight: "6px solid transparent",
          borderTop: `6px solid ${bgColor}`,
        }} />
      </div>
    </Html>
  );
};

const getBubbleText = (agentId: string, status: string, detail?: string): string => {
  if (status === "error") {
    return detail || ERROR_PHRASES[agentId] || "Erro!";
  }
  if (status === "done") {
    return detail || DONE_PHRASES[agentId] || "Concluído ✓";
  }
  if (status === "running") {
    if (detail) return detail;
    const phrases = RUNNING_PHRASES[agentId] || ["Trabalhando..."];
    return phrases[Math.floor(Date.now() / 3000) % phrases.length];
  }
  // idle
  const phrases = IDLE_PHRASES[agentId] || ["Aguardando..."];
  return phrases[Math.floor(Date.now() / 5000) % phrases.length];
};

const ThemisSceneInner = () => {
  const { agents, agentDetails } = useAgentStatus();

  const leftPositions: [number, number, number][] = [
    [-4.5, 0, -2],
    [-4.5, 0, 1],
    [-4.5, 0, 4],
  ];
  const rightPositions: [number, number, number][] = [
    [4.5, 0, -2],
    [4.5, 0, 1],
    [4.5, 0, 4],
  ];

  return (
    <>
      <Room />
      <MainDesk />

      {/* OWNER sitting at main desk — conectado ao telegram_approver */}
      {(() => {
        const approvalStatus = agents["telegram_approver"] || "idle";
        const ownerPhrases: Record<string, string[]> = {
          idle:    ["Monitorando agentes...", "Aguardando pipeline...", "Tudo sob controle."],
          running: ["Analisando o post...", "Hmm, deixa eu ver...", "Avaliando..."],
          done:    ["Post aprovado! ✓", "Publicado com sucesso!", "Excelente trabalho!"],
          error:   ["Post rejeitado.", "Vamos recriar isso.", "Pode melhorar."],
        };
        const phrases = ownerPhrases[approvalStatus] || ownerPhrases.idle;
        const ownerBubbleText = phrases[Math.floor(Date.now() / 4000) % phrases.length];
        return (
          <group>
            <HumanFigure
              position={[0, -0.58, -1.8]}
              rotation={[0, Math.PI, 0]}
              isOwner={true}
              color="#E8C4A0"
              status={approvalStatus}
            />
            <SpeechBubble
              position={[0, 1.2, -1.8]}
              text={ownerBubbleText}
              status={approvalStatus}
            />
          </group>
        );
      })()}

      {/* Left side: Estrategista, Roteirista, Designer */}
      {leftPositions.map((pos, i) => {
        const agentId = AGENT_IDS[i];
        const status = agents[agentId] || "idle";
        const bubbleText = getBubbleText(agentId, status, agentDetails[agentId]);
        return (
          <group key={`left-${i}`}>
            <AIWorkstation
              position={pos}
              rotation={[0, Math.PI / 2, 0]}
              agentName={AI_AGENTS[i].name}
              agentIndex={i}
              status={status}
            />
            <HumanFigure
              position={[pos[0] + 0.6, pos[1] - 0.58, pos[2]]}
              rotation={[0, -Math.PI / 2, 0]}
              color={SKIN_TONES[i]}
              suitColor={SUIT_COLORS[i]}
              status={status}
            />
            <SpeechBubble
              position={[pos[0] + 0.6, pos[1] + 1.3, pos[2]]}
              text={bubbleText}
              status={status}
            />
          </group>
        );
      })}

      {/* Right side: Editor, Revisor, Publisher */}
      {rightPositions.map((pos, i) => {
        const agentId = AGENT_IDS[i + 3];
        const status = agents[agentId] || "idle";
        const bubbleText = getBubbleText(agentId, status, agentDetails[agentId]);
        return (
          <group key={`right-${i}`}>
            <AIWorkstation
              position={pos}
              rotation={[0, -Math.PI / 2, 0]}
              agentName={AI_AGENTS[i + 3].name}
              agentIndex={i + 3}
              status={status}
            />
            <HumanFigure
              position={[pos[0] - 0.6, pos[1] - 0.58, pos[2]]}
              rotation={[0, Math.PI / 2, 0]}
              color={SKIN_TONES[i + 3]}
              suitColor={SUIT_COLORS[i + 3]}
              status={status}
            />
            <SpeechBubble
              position={[pos[0] - 0.6, pos[1] + 1.3, pos[2]]}
              text={bubbleText}
              status={status}
            />
          </group>
        );
      })}
    </>
  );
};

export const ThemisScene = () => {
  return (
    <Canvas shadows style={{ width: "100vw", height: "100vh", background: "#1A1510" }}>
      <PerspectiveCamera makeDefault position={[0, 5, 9]} fov={55} />
      <OrbitControls
        target={[0, 1.5, -1]}
        maxPolarAngle={Math.PI / 2.1}
        minDistance={4}
        maxDistance={15}
        enablePan={false}
      />

      <ambientLight intensity={0.25} color="#FFF5E0" />

      <directionalLight
        position={[2, 8, -5]}
        intensity={1.2}
        color="#FFF8E7"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={25}
        shadow-camera-left={-10}
        shadow-camera-right={10}
        shadow-camera-top={10}
        shadow-camera-bottom={-10}
      />

      <directionalLight position={[-3, 6, -3]} intensity={0.4} color="#FFE4B5" />
      <pointLight position={[0, 4, 8]} intensity={0.3} color="#FFF5E0" distance={15} />

      <Suspense fallback={null}>
        <ThemisSceneInner />
      </Suspense>
    </Canvas>
  );
};

export default ThemisScene;
