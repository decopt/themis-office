import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const WALNUT = "#3D2B1F";
const GOLD = "#D4AF37";
const LEATHER = "#2A1810";

export const MainDesk = () => {
  return (
    <group position={[0, 0, -3]}>
      {/* Large executive desk */}
      {/* Desktop surface */}
      <mesh position={[0, 0.85, 0]} castShadow receiveShadow>
        <boxGeometry args={[3.5, 0.08, 1.4]} />
        <meshStandardMaterial color={WALNUT} roughness={0.35} metalness={0.05} />
      </mesh>
      {/* Leather inlay */}
      <mesh position={[0, 0.895, 0]}>
        <boxGeometry args={[2.8, 0.005, 1]} />
        <meshStandardMaterial color={LEATHER} roughness={0.7} />
      </mesh>
      {/* Gold trim around desk */}
      <mesh position={[0, 0.87, 0.7]}>
        <boxGeometry args={[3.5, 0.04, 0.02]} />
        <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
      </mesh>
      <mesh position={[0, 0.87, -0.7]}>
        <boxGeometry args={[3.5, 0.04, 0.02]} />
        <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
      </mesh>
      {/* Left panel */}
      <mesh position={[-1.6, 0.42, 0]} castShadow>
        <boxGeometry args={[0.08, 0.84, 1.4]} />
        <meshStandardMaterial color={WALNUT} roughness={0.35} />
      </mesh>
      {/* Right panel */}
      <mesh position={[1.6, 0.42, 0]} castShadow>
        <boxGeometry args={[0.08, 0.84, 1.4]} />
        <meshStandardMaterial color={WALNUT} roughness={0.35} />
      </mesh>
      {/* Back panel */}
      <mesh position={[0, 0.42, -0.66]} castShadow>
        <boxGeometry args={[3.12, 0.84, 0.08]} />
        <meshStandardMaterial color={WALNUT} roughness={0.35} />
      </mesh>
      {/* Drawers (left) */}
      <mesh position={[-1.1, 0.55, 0.3]}>
        <boxGeometry args={[0.8, 0.15, 0.6]} />
        <meshStandardMaterial color="#4A3728" roughness={0.4} />
      </mesh>
      <mesh position={[-1.1, 0.35, 0.3]}>
        <boxGeometry args={[0.8, 0.15, 0.6]} />
        <meshStandardMaterial color="#4A3728" roughness={0.4} />
      </mesh>
      {/* Drawer handles (gold) */}
      <mesh position={[-1.1, 0.55, 0.62]}>
        <boxGeometry args={[0.2, 0.02, 0.02]} />
        <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
      </mesh>
      <mesh position={[-1.1, 0.35, 0.62]}>
        <boxGeometry args={[0.2, 0.02, 0.02]} />
        <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
      </mesh>

      {/* Monitor on desk */}
      <Monitor position={[0, 0.9, -0.2]} />

      {/* Keyboard on desk */}
      <DeskKeyboard position={[0, 0.9, 0.25]} />

      {/* Executive Chair — rotated to face desk */}
      <ExecutiveChair position={[0, 0, 1.2]} rotation={[0, Math.PI, 0]} />

      {/* Scales of Justice decoration */}
      <ScalesOfJustice position={[1.4, 0.9, -0.1]} />
    </group>
  );
};

const Monitor = ({ position }: { position: [number, number, number] }) => {
  const { canvas, texture } = useMemo(() => {
    const c = document.createElement("canvas");
    c.width = 512;
    c.height = 320;
    const tex = new THREE.CanvasTexture(c);
    tex.minFilter = THREE.LinearFilter;
    tex.magFilter = THREE.LinearFilter;
    return { canvas: c, texture: tex };
  }, []);

  const ownerLines = [
    "$ top-agenda v2.0",
    "> pipeline: online ✓",
    "> agents: 6 connected",
    "> instagram: authenticated",
    "$ last post: score 98/100",
    "> engagement: 4.2%",
    "> reach: 12.4k",
    "$ schedule: seg, qua, sex",
    "> next run: pending...",
    "> status: all systems OK",
  ];

  useFrame(({ clock }) => {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const t = clock.getElapsedTime();
    const w = canvas.width;
    const h = canvas.height;

    ctx.fillStyle = "#0a0a0a";
    ctx.fillRect(0, 0, w, h);
    ctx.font = "14px monospace";

    const visible = Math.min(ownerLines.length, Math.floor(t * 0.8) + 1);
    for (let i = 0; i < visible; i++) {
      const line = ownerLines[i];
      if (line.startsWith("$")) ctx.fillStyle = "#00E5FF";
      else if (line.startsWith(">")) ctx.fillStyle = "#aaaaaa";
      else ctx.fillStyle = "#666666";
      ctx.fillText(line, 10, 22 + i * 22);
    }

    if (Math.sin(t * 4) > 0) {
      ctx.fillStyle = "#00E5FF";
      ctx.fillText("█", 10, 22 + visible * 22);
    }

    texture.needsUpdate = true;
  });

  return (
    <group position={position}>
      {/* Stand */}
      <mesh position={[0, 0.15, 0]}>
        <cylinderGeometry args={[0.15, 0.2, 0.3, 8]} />
        <meshStandardMaterial color="#222" metalness={0.8} roughness={0.2} />
      </mesh>
      {/* Screen */}
      <mesh position={[0, 0.55, 0]} castShadow>
        <boxGeometry args={[1.0, 0.6, 0.03]} />
        <meshStandardMaterial color="#111" roughness={0.3} />
      </mesh>
      {/* Terminal display */}
      <mesh position={[0, 0.55, 0.02]}>
        <planeGeometry args={[0.9, 0.5]} />
        <meshBasicMaterial map={texture} transparent opacity={0.95} />
      </mesh>
    </group>
  );
};

const ExecutiveChair = ({ position, rotation = [0, 0, 0] as [number, number, number] }: { position: [number, number, number]; rotation?: [number, number, number] }) => (
  <group position={position} rotation={rotation}>
    {/* Base */}
    <mesh position={[0, 0.1, 0]}>
      <cylinderGeometry args={[0.3, 0.3, 0.05, 16]} />
      <meshStandardMaterial color="#222" metalness={0.8} roughness={0.2} />
    </mesh>
    {/* Pole */}
    <mesh position={[0, 0.3, 0]}>
      <cylinderGeometry args={[0.04, 0.04, 0.4, 8]} />
      <meshStandardMaterial color="#333" metalness={0.8} roughness={0.2} />
    </mesh>
    {/* Seat */}
    <mesh position={[0, 0.52, 0]}>
      <boxGeometry args={[0.5, 0.08, 0.5]} />
      <meshStandardMaterial color={LEATHER} roughness={0.6} />
    </mesh>
    {/* Backrest */}
    <mesh position={[0, 0.85, -0.22]}>
      <boxGeometry args={[0.48, 0.6, 0.06]} />
      <meshStandardMaterial color={LEATHER} roughness={0.6} />
    </mesh>
    {/* Armrests */}
    <mesh position={[-0.28, 0.65, 0]}>
      <boxGeometry args={[0.04, 0.2, 0.35]} />
      <meshStandardMaterial color={WALNUT} roughness={0.4} />
    </mesh>
    <mesh position={[0.28, 0.65, 0]}>
      <boxGeometry args={[0.04, 0.2, 0.35]} />
      <meshStandardMaterial color={WALNUT} roughness={0.4} />
    </mesh>
  </group>
);

const ScalesOfJustice = ({ position }: { position: [number, number, number] }) => (
  <group position={position}>
    {/* Base */}
    <mesh position={[0, 0.02, 0]}>
      <cylinderGeometry args={[0.08, 0.1, 0.04, 8]} />
      <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
    </mesh>
    {/* Pole */}
    <mesh position={[0, 0.2, 0]}>
      <cylinderGeometry args={[0.012, 0.012, 0.36, 8]} />
      <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
    </mesh>
    {/* Beam */}
    <mesh position={[0, 0.38, 0]}>
      <boxGeometry args={[0.25, 0.01, 0.01]} />
      <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
    </mesh>
    {/* Pans */}
    <mesh position={[-0.11, 0.33, 0]}>
      <cylinderGeometry args={[0.04, 0.04, 0.008, 8]} />
      <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
    </mesh>
    <mesh position={[0.11, 0.35, 0]}>
      <cylinderGeometry args={[0.04, 0.04, 0.008, 8]} />
      <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.1} />
    </mesh>
  </group>
);

const DeskKeyboard = ({ position }: { position: [number, number, number] }) => {
  const rows = [
    { z: -0.05, keys: 14, width: 0.035 },
    { z: -0.02, keys: 13, width: 0.037 },
    { z: 0.01, keys: 12, width: 0.038 },
    { z: 0.04, keys: 10, width: 0.037 },
    { z: 0.065, keys: 1, width: 0.22 },
  ];

  return (
    <group position={position}>
      <mesh rotation={[-0.1, 0, 0]}>
        <boxGeometry args={[0.55, 0.012, 0.16]} />
        <meshStandardMaterial color="#1a1a1a" roughness={0.4} metalness={0.5} />
      </mesh>
      {rows.map((row, ri) => {
        const keys = [];
        for (let k = 0; k < row.keys; k++) {
          const totalW = row.keys * (row.width + 0.005);
          const x = -totalW / 2 + k * (row.width + 0.005) + row.width / 2;
          keys.push(
            <mesh key={`${ri}-${k}`} position={[x, 0.01, row.z]} rotation={[-0.1, 0, 0]}>
              <boxGeometry args={[row.width, 0.007, ri === 4 ? 0.016 : 0.02]} />
              <meshStandardMaterial color="#222" roughness={0.5} metalness={0.3} />
            </mesh>
          );
        }
        return keys;
      })}
    </group>
  );
};

const LEATHER_DARK = "#2A1810";

export default MainDesk;
