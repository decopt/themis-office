import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

const CYAN = "#00E5FF";
const GOLD = "#D4AF37";

interface HumanFigureProps {
  position: [number, number, number];
  rotation?: [number, number, number];
  color?: string;
  suitColor?: string;
  isOwner?: boolean;
  status?: string;
}

export const HumanFigure = ({ position, rotation = [0, 0, 0], color = "#E8C4A0", suitColor = "#1A1A2E", isOwner = false, status = "idle" }: HumanFigureProps) => {
  const groupRef = useRef<THREE.Group>(null);
  const leftArmRef = useRef<THREE.Mesh>(null);
  const rightArmRef = useRef<THREE.Mesh>(null);
  const headRef = useRef<THREE.Mesh>(null);

  const isActive = status === "running";

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();

    // ── OWNER (manager at center desk) ─────────────────────
    if (isOwner) {
      if (status === "running") {
        // Pensando / deliberando — inclina levemente para trás, cabeça vira devagar
        if (groupRef.current) {
          groupRef.current.rotation.x = -0.04 + Math.sin(t * 0.6) * 0.015;
          groupRef.current.scale.y = 1 + Math.sin(t * 1.2) * 0.003;
        }
        if (headRef.current) {
          headRef.current.rotation.y = Math.sin(t * 0.4) * 0.18; // olha para os lados
          headRef.current.rotation.x = -0.05 + Math.sin(t * 0.8) * 0.04;
          headRef.current.position.y = 1.62 + Math.sin(t * 1.0) * 0.008;
        }
        // Braço direito sobe levemente (mão no queixo / pensando)
        if (rightArmRef.current) {
          rightArmRef.current.rotation.x = 0.6 + Math.sin(t * 1.2) * 0.05;
          rightArmRef.current.rotation.z = -0.3;
        }
        if (leftArmRef.current) {
          leftArmRef.current.rotation.x = 1.0;
          leftArmRef.current.rotation.z = 0;
        }
      } else if (status === "done") {
        // Aprovando! — braço direito sobe celebrando, cabeça acena
        if (groupRef.current) {
          groupRef.current.rotation.x = Math.sin(t * 2) * 0.01;
          groupRef.current.scale.y = 1 + Math.sin(t * 3) * 0.006;
        }
        if (headRef.current) {
          // Acenando com a cabeça (nodding)
          headRef.current.rotation.x = Math.sin(t * 4) * 0.12;
          headRef.current.rotation.y = Math.sin(t * 2) * 0.05;
          headRef.current.position.y = 1.62 + Math.sin(t * 4) * 0.015;
        }
        // Braço direito levantado — gesto de aprovação
        if (rightArmRef.current) {
          rightArmRef.current.rotation.x = -0.8 + Math.sin(t * 3) * 0.12;
          rightArmRef.current.rotation.z = -0.2;
        }
        if (leftArmRef.current) {
          leftArmRef.current.rotation.x = 1.1;
          leftArmRef.current.rotation.z = 0;
        }
      } else if (status === "error") {
        // Rejeitou — cabeça balança (shake), braços relaxados
        if (groupRef.current) {
          groupRef.current.rotation.x = 0;
          groupRef.current.scale.y = 1 + Math.sin(t * 1.5) * 0.003;
        }
        if (headRef.current) {
          headRef.current.rotation.y = Math.sin(t * 5) * 0.15; // balança
          headRef.current.rotation.x = 0;
          headRef.current.position.y = 1.62;
        }
        if (leftArmRef.current) { leftArmRef.current.rotation.x = 1.1; leftArmRef.current.rotation.z = 0; }
        if (rightArmRef.current) { rightArmRef.current.rotation.x = 1.1; rightArmRef.current.rotation.z = 0; }
      } else {
        // Idle — respiração sutil, olha para o monitor
        if (groupRef.current) {
          groupRef.current.rotation.x = 0;
          groupRef.current.scale.y = 1 + Math.sin(t * 1.2) * 0.004;
        }
        if (headRef.current) {
          headRef.current.position.y = 1.62 + Math.sin(t * 1.0) * 0.005;
          headRef.current.rotation.x = -0.05; // olha levemente para baixo (monitor)
          headRef.current.rotation.y = Math.sin(t * 0.3) * 0.06;
        }
        if (leftArmRef.current) { leftArmRef.current.rotation.x = 1.1; leftArmRef.current.rotation.z = 0; }
        if (rightArmRef.current) { rightArmRef.current.rotation.x = 1.1; rightArmRef.current.rotation.z = 0; }
      }
      return; // owner tem animação própria
    }

    // ── AGENTES IA ──────────────────────────────────────────
    if (groupRef.current) {
      if (isActive) {
        groupRef.current.rotation.x = Math.sin(t * 2) * 0.015;
        groupRef.current.scale.y = 1 + Math.sin(t * 2.5) * 0.005;
      } else {
        groupRef.current.rotation.x = 0;
        groupRef.current.scale.y = 1 + Math.sin(t * 1.5) * 0.003;
      }
    }
    if (leftArmRef.current) {
      leftArmRef.current.rotation.z = 0;
      leftArmRef.current.rotation.x = isActive ? 1.1 + Math.sin(t * 6) * 0.15 : 1.1;
    }
    if (rightArmRef.current) {
      rightArmRef.current.rotation.z = 0;
      rightArmRef.current.rotation.x = isActive ? 1.1 + Math.sin(t * 6 + 1.5) * 0.15 : 1.1;
    }
    if (headRef.current) {
      if (isActive) {
        headRef.current.position.y = 1.62 + Math.sin(t * 3) * 0.01;
        headRef.current.rotation.x = Math.sin(t * 1.5) * 0.05;
      } else {
        headRef.current.position.y = 1.62;
        headRef.current.rotation.x = 0;
      }
    }
  });

  const bodyColor = isOwner ? "#2A1810" : suitColor;
  const accentColor = isOwner ? GOLD : CYAN;
  const pantsColor = isOwner ? "#1A1A1A" : "#222233";
  const shoeColor = isOwner ? "#2A1810" : "#111";

  return (
    <group ref={groupRef} position={position} rotation={rotation}>
      {/* === HEAD === */}
      <mesh ref={headRef} position={[0, 1.62, 0]} castShadow>
        <sphereGeometry args={[0.11, 16, 16]} />
        <meshStandardMaterial color={color} roughness={0.6} />
      </mesh>

      {/* Hair */}
      <mesh position={[0, 1.7, 0]} castShadow>
        <sphereGeometry args={[0.105, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.55]} />
        <meshStandardMaterial color={isOwner ? "#3D2B1F" : "#1A1A1A"} roughness={0.9} />
      </mesh>

      {/* === NECK === */}
      <mesh position={[0, 1.48, 0]}>
        <cylinderGeometry args={[0.04, 0.045, 0.08, 8]} />
        <meshStandardMaterial color={color} roughness={0.6} />
      </mesh>

      {/* === TORSO (jacket/suit) === */}
      {/* Upper torso */}
      <mesh position={[0, 1.3, 0]} castShadow>
        <boxGeometry args={[0.3, 0.3, 0.16]} />
        <meshStandardMaterial color={bodyColor} roughness={0.5} />
      </mesh>
      {/* Lower torso */}
      <mesh position={[0, 1.08, 0]} castShadow>
        <boxGeometry args={[0.28, 0.16, 0.15]} />
        <meshStandardMaterial color={bodyColor} roughness={0.5} />
      </mesh>

      {/* Shirt collar */}
      <mesh position={[0, 1.42, 0.075]}>
        <boxGeometry args={[0.12, 0.04, 0.02]} />
        <meshStandardMaterial color="#F0F0F0" roughness={0.5} />
      </mesh>

      {/* Tie */}
      <mesh position={[0, 1.28, 0.085]}>
        <boxGeometry args={[0.035, 0.22, 0.008]} />
        <meshStandardMaterial
          color={accentColor}
          emissive={isOwner ? "#000" : CYAN}
          emissiveIntensity={isOwner ? 0 : 0.2}
        />
      </mesh>

      {/* === SHOULDERS === */}
      <mesh position={[-0.19, 1.38, 0]}>
        <sphereGeometry args={[0.055, 8, 8]} />
        <meshStandardMaterial color={bodyColor} roughness={0.5} />
      </mesh>
      <mesh position={[0.19, 1.38, 0]}>
        <sphereGeometry args={[0.055, 8, 8]} />
        <meshStandardMaterial color={bodyColor} roughness={0.5} />
      </mesh>

      {/* === UPPER ARMS === */}
      <mesh position={[-0.22, 1.22, 0]} rotation={[0.1, 0, 0.12]}>
        <capsuleGeometry args={[0.035, 0.18, 4, 8]} />
        <meshStandardMaterial color={bodyColor} roughness={0.5} />
      </mesh>
      <mesh position={[0.22, 1.22, 0]} rotation={[0.1, 0, -0.12]}>
        <capsuleGeometry args={[0.035, 0.18, 4, 8]} />
        <meshStandardMaterial color={bodyColor} roughness={0.5} />
      </mesh>

      {/* === FOREARMS (reaching forward to type) === */}
      <mesh ref={leftArmRef} position={[-0.23, 1.08, 0.12]} rotation={[1.1, 0, 0]}>
        <capsuleGeometry args={[0.03, 0.16, 4, 8]} />
        <meshStandardMaterial color={color} roughness={0.6} />
      </mesh>
      <mesh ref={rightArmRef} position={[0.23, 1.08, 0.12]} rotation={[1.1, 0, 0]}>
        <capsuleGeometry args={[0.03, 0.16, 4, 8]} />
        <meshStandardMaterial color={color} roughness={0.6} />
      </mesh>

      {/* === HANDS === */}
      <mesh position={[-0.23, 0.97, 0.27]}>
        <sphereGeometry args={[0.025, 8, 8]} />
        <meshStandardMaterial color={color} roughness={0.6} />
      </mesh>
      <mesh position={[0.23, 0.97, 0.27]}>
        <sphereGeometry args={[0.025, 8, 8]} />
        <meshStandardMaterial color={color} roughness={0.6} />
      </mesh>

      {/* === UPPER LEGS (seated — thighs horizontal on chair) === */}
      <mesh position={[-0.08, 0.92, 0.12]} rotation={[1.55, 0, 0.05]}>
        <capsuleGeometry args={[0.048, 0.22, 4, 8]} />
        <meshStandardMaterial color={pantsColor} roughness={0.5} />
      </mesh>
      <mesh position={[0.08, 0.92, 0.12]} rotation={[1.55, 0, -0.05]}>
        <capsuleGeometry args={[0.048, 0.22, 4, 8]} />
        <meshStandardMaterial color={pantsColor} roughness={0.5} />
      </mesh>

      {/* === KNEES === */}
      <mesh position={[-0.08, 0.82, 0.32]}>
        <sphereGeometry args={[0.05, 8, 8]} />
        <meshStandardMaterial color={pantsColor} roughness={0.5} />
      </mesh>
      <mesh position={[0.08, 0.82, 0.32]}>
        <sphereGeometry args={[0.05, 8, 8]} />
        <meshStandardMaterial color={pantsColor} roughness={0.5} />
      </mesh>

      {/* === LOWER LEGS (hanging down from knee) === */}
      <mesh position={[-0.08, 0.6, 0.34]} rotation={[0.05, 0, 0]}>
        <capsuleGeometry args={[0.04, 0.24, 4, 8]} />
        <meshStandardMaterial color={pantsColor} roughness={0.5} />
      </mesh>
      <mesh position={[0.08, 0.6, 0.34]} rotation={[0.05, 0, 0]}>
        <capsuleGeometry args={[0.04, 0.24, 4, 8]} />
        <meshStandardMaterial color={pantsColor} roughness={0.5} />
      </mesh>

      {/* === SHOES (on the floor) === */}
      <mesh position={[-0.08, 0.44, 0.38]}>
        <boxGeometry args={[0.08, 0.04, 0.14]} />
        <meshStandardMaterial color={shoeColor} roughness={0.3} metalness={0.1} />
      </mesh>
      <mesh position={[0.08, 0.44, 0.38]}>
        <boxGeometry args={[0.08, 0.04, 0.14]} />
        <meshStandardMaterial color={shoeColor} roughness={0.3} metalness={0.1} />
      </mesh>

      {/* Owner golden aura */}
      {isOwner && (
        <pointLight position={[0, 1.8, 0]} intensity={0.4} color={GOLD} distance={2.5} />
      )}
    </group>
  );
};

export default HumanFigure;
