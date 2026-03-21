import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const MARBLE = "#F5F5F0";
const GOLD = "#D4AF37";
const CYAN = "#00E5FF";
const GREEN = "#22c55e";
const RED = "#ef4444";

const STATUS_COLORS: Record<string, string> = {
  idle: CYAN,
  running: CYAN,
  done: GREEN,
  error: RED,
};

interface AIWorkstationProps {
  position: [number, number, number];
  rotation?: [number, number, number];
  agentName: string;
  agentIndex: number;
  status?: string;
}

export const AIWorkstation = ({ position, rotation = [0, 0, 0], agentName, agentIndex, status = "idle" }: AIWorkstationProps) => {
  const glowRef = useRef<THREE.PointLight>(null);
  const screenRef = useRef<THREE.Mesh>(null);
  const kbRef = useRef<THREE.Mesh>(null);

  const isActive = status === "running";
  const screenColor = STATUS_COLORS[status] || CYAN;

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const phase = agentIndex * 0.8;

    if (glowRef.current) {
      if (isActive) {
        // Fast pulsing glow when running
        glowRef.current.intensity = 1.2 + Math.sin(t * 3 + phase) * 0.8;
        glowRef.current.color.set(screenColor);
      } else if (status === "done") {
        glowRef.current.intensity = 0.6;
        glowRef.current.color.set(GREEN);
      } else if (status === "error") {
        glowRef.current.intensity = 0.4 + Math.sin(t * 5) * 0.4;
        glowRef.current.color.set(RED);
      } else {
        glowRef.current.intensity = 0.3 + Math.sin(t * 0.5 + phase) * 0.15;
        glowRef.current.color.set(CYAN);
      }
    }

    if (screenRef.current) {
      const mat = screenRef.current.material as THREE.MeshStandardMaterial;
      if (isActive) {
        mat.emissive.set(screenColor);
        mat.emissiveIntensity = 0.6 + Math.sin(t * 2.5 + phase) * 0.3;
      } else if (status === "done") {
        mat.emissive.set(GREEN);
        mat.emissiveIntensity = 0.4;
      } else if (status === "error") {
        mat.emissive.set(RED);
        mat.emissiveIntensity = 0.3 + Math.sin(t * 6) * 0.3;
      } else {
        mat.emissive.set(CYAN);
        mat.emissiveIntensity = 0.15 + Math.sin(t * 0.5 + phase) * 0.1;
      }
    }

    // Keyboard glow pulses when typing
    if (kbRef.current) {
      const kbMat = kbRef.current.material as THREE.MeshStandardMaterial;
      if (isActive) {
        kbMat.emissiveIntensity = 0.3 + Math.sin(t * 4 + phase) * 0.2;
        kbMat.opacity = 0.3 + Math.sin(t * 4 + phase) * 0.15;
      } else {
        kbMat.emissiveIntensity = 0.1;
        kbMat.opacity = 0.1;
      }
    }
  });

  return (
    <group position={position} rotation={rotation}>
      {/* Marble pedestal base */}
      <mesh position={[0, 0.2, 0]} castShadow>
        <boxGeometry args={[0.9, 0.4, 0.6]} />
        <meshStandardMaterial color={MARBLE} roughness={0.12} metalness={0.05} />
      </mesh>
      {/* Gold trim on pedestal */}
      <mesh position={[0, 0.4, 0]}>
        <boxGeometry args={[0.92, 0.02, 0.62]} />
        <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
      </mesh>

      {/* Desk surface (glass) */}
      <mesh position={[0, 0.45, 0]} castShadow>
        <boxGeometry args={[1.0, 0.03, 0.65]} />
        <meshStandardMaterial color="#E8E8E0" roughness={0.05} metalness={0.1} opacity={0.9} transparent />
      </mesh>

      {/* Holographic display stand */}
      <mesh position={[0, 0.55, -0.15]}>
        <cylinderGeometry args={[0.03, 0.05, 0.18, 8]} />
        <meshStandardMaterial color="#2A2A2A" metalness={0.9} roughness={0.1} />
      </mesh>

      {/* Screen / holographic display */}
      <mesh ref={screenRef} position={[0, 0.85, -0.15]} castShadow>
        <boxGeometry args={[0.7, 0.45, 0.015]} />
        <meshStandardMaterial
          color="#0A0A0A"
          emissive={screenColor}
          emissiveIntensity={isActive ? 0.8 : 0.2}
          roughness={0.2}
          metalness={0.5}
        />
      </mesh>

      {/* Terminal text overlay on screen */}
      <TerminalScreen
        position={[0, 0.85, -0.135]}
        agentName={agentName}
        agentIndex={agentIndex}
        status={status}
      />

      {/* Screen border glow */}
      <mesh position={[0, 0.85, -0.14]}>
        <planeGeometry args={[0.72, 0.47]} />
        <meshStandardMaterial
          color={screenColor}
          emissive={screenColor}
          emissiveIntensity={isActive ? 0.3 : 0.08}
          transparent
          opacity={isActive ? 0.2 : 0.08}
        />
      </mesh>

      {/* Physical keyboard on desk */}
      <Keyboard position={[0, 0.465, 0.1]} status={status} kbRef={kbRef} />

      {/* Cyan point light glow */}
      <pointLight
        ref={glowRef}
        position={[0, 0.9, 0.1]}
        intensity={isActive ? 1.5 : 0.3}
        color={screenColor}
        distance={isActive ? 5 : 3}
      />

      {/* Status indicator light on desk edge */}
      <mesh position={[0.42, 0.46, 0.3]}>
        <sphereGeometry args={[0.02, 8, 8]} />
        <meshStandardMaterial
          color={screenColor}
          emissive={screenColor}
          emissiveIntensity={isActive ? 2 : (status === "done" ? 1 : 0.3)}
        />
      </mesh>

      {/* AI Avatar - floating holographic sphere */}
      <AIAvatar position={[0, 1.25, -0.15]} agentIndex={agentIndex} status={status} />

      {/* Chair — rotated 180 so backrest faces away from desk */}
      <SimpleChair position={[0, 0, 0.6]} rotation={[0, Math.PI, 0]} />
    </group>
  );
};

const AIAvatar = ({ position, agentIndex, status = "idle" }: { position: [number, number, number]; agentIndex: number; status?: string }) => {
  const ref = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  const isActive = status === "running";
  const avatarColor = STATUS_COLORS[status] || CYAN;

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (ref.current) {
      // Faster bobbing when active
      const speed = isActive ? 2.5 : 0.8;
      const amp = isActive ? 0.06 : 0.03;
      ref.current.position.y = position[1] + Math.sin(t * speed + agentIndex) * amp;
    }
    if (ringRef.current) {
      const speed = isActive ? 1.5 : 0.3;
      ringRef.current.rotation.y = t * speed + agentIndex;
      ringRef.current.rotation.x = Math.sin(t * 0.2) * 0.3;
    }
  });

  return (
    <group>
      <mesh ref={ref} position={position}>
        <sphereGeometry args={[isActive ? 0.08 : 0.06, 16, 16]} />
        <meshStandardMaterial
          color={avatarColor}
          emissive={avatarColor}
          emissiveIntensity={isActive ? 1.5 : 0.5}
          transparent
          opacity={isActive ? 0.9 : 0.6}
        />
      </mesh>
      <mesh ref={ringRef} position={position}>
        <torusGeometry args={[isActive ? 0.13 : 0.1, 0.008, 8, 32]} />
        <meshStandardMaterial
          color={isActive ? avatarColor : GOLD}
          metalness={0.9}
          roughness={0.1}
          emissive={isActive ? avatarColor : GOLD}
          emissiveIntensity={isActive ? 0.6 : 0.2}
        />
      </mesh>
    </group>
  );
};

/* ── Terminal screen with scrolling CMD text ── */
const TERMINAL_LINES: Record<string, string[]> = {
  strategist: [
    "$ analyzing trends...",
    "> fetching instagram insights",
    "> pillar: educacional",
    "> pillar: autoridade",
    "> theme: agendamento online",
    "$ scoring topics...",
    "> topic score: 94/100",
    "> audience match: 97%",
    "$ generating content plan...",
    "> slots: seg, qua, sex",
    "> format: carousel",
    "OK strategy ready ✓",
  ],
  scriptwriter: [
    "$ writing script...",
    "> hook: pergunta provocativa",
    "> slides: 4",
    "> CTA: link na bio",
    "$ generating caption...",
    "> chars: 1847/2200",
    "> emojis: 12",
    "$ hashtag research...",
    "> hashtags: 30",
    "> reach estimate: 12.4k",
    "OK script complete ✓",
  ],
  designer: [
    "$ generating images...",
    "> style: modern minimal",
    "> palette: brand colors",
    "> slide 1/4 rendering...",
    "> slide 2/4 rendering...",
    "> slide 3/4 rendering...",
    "> slide 4/4 rendering...",
    "$ applying brand overlay",
    "> logo placement: bottom-right",
    "> resolution: 1080x1350",
    "OK design exported ✓",
  ],
  editor: [
    "$ editing images...",
    "> contrast: +12%",
    "> saturation: +8%",
    "> sharpness: enhanced",
    "> filter: warm tone",
    "$ processing slide 1...",
    "$ processing slide 2...",
    "$ processing slide 3...",
    "$ processing slide 4...",
    "> story version created",
    "OK edits applied ✓",
  ],
  reviewer: [
    "$ quality check...",
    "> text: no typos ✓",
    "> images: high-res ✓",
    "> brand: consistent ✓",
    "> CTA: present ✓",
    "$ scoring content...",
    "> engagement pred: 4.2%",
    "> quality: 98/100",
    "> approved: true",
    "OK review passed ✓",
  ],
  publisher: [
    "$ connecting to API...",
    "> auth: token valid ✓",
    "> endpoint: graph.facebook",
    "$ uploading media...",
    "> img 1/4 uploaded",
    "> img 2/4 uploaded",
    "> img 3/4 uploaded",
    "> img 4/4 uploaded",
    "$ creating carousel...",
    "> container ID: 178887...",
    "$ publishing post...",
    "OK published ✓",
  ],
};

const TerminalScreen = ({
  position,
  agentName,
  agentIndex,
  status = "idle",
}: {
  position: [number, number, number];
  agentName: string;
  agentIndex: number;
  status?: string;
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const isActive = status === "running";

  const agentKey = ["strategist", "scriptwriter", "designer", "editor", "reviewer", "publisher"][agentIndex] || "strategist";
  const lines = TERMINAL_LINES[agentKey] || TERMINAL_LINES.strategist;

  const { canvas, texture } = useMemo(() => {
    const c = document.createElement("canvas");
    c.width = 512;
    c.height = 320;
    const tex = new THREE.CanvasTexture(c);
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    return { canvas: c, texture: tex };
  }, []);

  useFrame(({ clock }) => {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const t = clock.getElapsedTime();
    const w = canvas.width;
    const h = canvas.height;

    // Dark terminal background
    ctx.fillStyle = "#0a0a0a";
    ctx.fillRect(0, 0, w, h);

    const fontSize = 14;
    ctx.font = `${fontSize}px monospace`;
    const lineHeight = 20;
    const maxVisible = Math.floor(h / lineHeight) - 1;

    if (isActive) {
      // Scrolling terminal lines
      const scrollOffset = Math.floor(t * 1.8 + agentIndex * 3) % lines.length;
      const visibleCount = Math.min(maxVisible, Math.floor((t * 1.8 + agentIndex * 3) % (lines.length + 3)));

      for (let i = 0; i <= Math.min(visibleCount, maxVisible); i++) {
        const lineIdx = (scrollOffset + i) % lines.length;
        const line = lines[lineIdx];
        const y = 20 + i * lineHeight;

        if (line.startsWith("$")) {
          ctx.fillStyle = "#00E5FF";
        } else if (line.startsWith(">")) {
          ctx.fillStyle = "#aaaaaa";
        } else if (line.startsWith("OK")) {
          ctx.fillStyle = "#22c55e";
        } else {
          ctx.fillStyle = "#666666";
        }

        ctx.fillText(line, 10, y);
      }

      // Blinking cursor
      if (Math.sin(t * 6) > 0) {
        const cursorY = 20 + Math.min(visibleCount, maxVisible) * lineHeight;
        ctx.fillStyle = "#00E5FF";
        ctx.fillText("█", 10, cursorY);
      }
    } else if (status === "done") {
      ctx.fillStyle = "#22c55e";
      ctx.font = `${fontSize}px monospace`;
      ctx.fillText("$ task complete", 10, 20);
      ctx.fillText("> all checks passed ✓", 10, 40);
      ctx.fillText("> status: DONE", 10, 60);
    } else if (status === "error") {
      ctx.fillStyle = "#ef4444";
      ctx.font = `${fontSize}px monospace`;
      ctx.fillText("$ ERROR", 10, 20);
      ctx.fillText("> process failed", 10, 40);
      if (Math.sin(t * 4) > 0) {
        ctx.fillText("! retry required", 10, 60);
      }
    } else {
      // Idle — dim prompt
      ctx.fillStyle = "#333333";
      ctx.font = `${fontSize}px monospace`;
      ctx.fillText("$ _", 10, 20);
      ctx.fillStyle = "#222222";
      ctx.fillText("> awaiting instructions...", 10, 40);
    }

    texture.needsUpdate = true;
  });

  return (
    <mesh ref={meshRef} position={position}>
      <planeGeometry args={[0.64, 0.4]} />
      <meshBasicMaterial map={texture} transparent opacity={0.95} />
    </mesh>
  );
};

/* ── Physical 3D Keyboard ── */
const Keyboard = ({
  position,
  status = "idle",
  kbRef,
}: {
  position: [number, number, number];
  status?: string;
  kbRef: React.RefObject<THREE.Mesh | null>;
}) => {
  const isActive = status === "running";
  const keyColor = "#1a1a1a";
  const baseColor = "#111111";

  // Key rows layout — each row has offset X, Y, Z and number of keys
  const rows = [
    { z: -0.06, keys: 12, width: 0.032 },
    { z: -0.025, keys: 11, width: 0.034 },
    { z: 0.01, keys: 10, width: 0.036 },
    { z: 0.045, keys: 9, width: 0.034 },
    { z: 0.075, keys: 1, width: 0.2 }, // spacebar
  ];

  return (
    <group position={position}>
      {/* Keyboard base */}
      <mesh rotation={[-0.15, 0, 0]}>
        <boxGeometry args={[0.48, 0.012, 0.18]} />
        <meshStandardMaterial color={baseColor} roughness={0.4} metalness={0.6} />
      </mesh>

      {/* Key rows */}
      {rows.map((row, ri) => {
        const keys = [];
        for (let k = 0; k < row.keys; k++) {
          const totalWidth = row.keys * (row.width + 0.005);
          const x = -totalWidth / 2 + k * (row.width + 0.005) + row.width / 2;
          keys.push(
            <mesh key={`${ri}-${k}`} position={[x, 0.01, row.z]} rotation={[-0.15, 0, 0]}>
              <boxGeometry args={[row.width, 0.008, ri === 4 ? 0.018 : 0.022]} />
              <meshStandardMaterial
                color={keyColor}
                roughness={0.5}
                metalness={0.3}
                emissive={isActive ? "#00E5FF" : "#000000"}
                emissiveIntensity={isActive ? 0.15 : 0}
              />
            </mesh>
          );
        }
        return keys;
      })}

      {/* Glow plane under keys (replaces old holographic keyboard) */}
      <mesh ref={kbRef} position={[0, 0.005, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[0.5, 0.2]} />
        <meshStandardMaterial
          color="#00E5FF"
          emissive="#00E5FF"
          emissiveIntensity={isActive ? 0.3 : 0.05}
          transparent
          opacity={isActive ? 0.15 : 0.03}
        />
      </mesh>
    </group>
  );
};

const SimpleChair = ({ position, rotation = [0, 0, 0] }: { position: [number, number, number]; rotation?: [number, number, number] }) => (
  <group position={position} rotation={rotation}>
    <mesh position={[0, 0.25, 0]}>
      <boxGeometry args={[0.4, 0.03, 0.4]} />
      <meshStandardMaterial color="#2A1810" roughness={0.6} />
    </mesh>
    {[[-0.16, 0.12, -0.16], [0.16, 0.12, -0.16], [-0.16, 0.12, 0.16], [0.16, 0.12, 0.16]].map((pos, i) => (
      <mesh key={i} position={pos as [number, number, number]}>
        <cylinderGeometry args={[0.015, 0.015, 0.25, 6]} />
        <meshStandardMaterial color="#333" metalness={0.8} roughness={0.2} />
      </mesh>
    ))}
    <mesh position={[0, 0.45, -0.18]}>
      <boxGeometry args={[0.38, 0.38, 0.025]} />
      <meshStandardMaterial color="#2A1810" roughness={0.6} />
    </mesh>
  </group>
);

export default AIWorkstation;
