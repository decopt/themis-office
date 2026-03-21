import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { Text } from "@react-three/drei";

const MARBLE_COLOR = "#F5F5F0";
const WALNUT_COLOR = "#3D2B1F";
const GOLD_COLOR = "#D4AF37";

export const Room = () => {
  return (
    <group>
      {/* Floor - Marble */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color={MARBLE_COLOR} roughness={0.15} metalness={0.05} />
      </mesh>

      {/* Floor grid pattern */}
      {Array.from({ length: 10 }).map((_, i) =>
        Array.from({ length: 10 }).map((_, j) => {
          const isAlternate = (i + j) % 2 === 0;
          return (
            <mesh
              key={`tile-${i}-${j}`}
              rotation={[-Math.PI / 2, 0, 0]}
              position={[i * 2 - 9, 0.001, j * 2 - 9]}
              receiveShadow
            >
              <planeGeometry args={[2, 2]} />
              <meshStandardMaterial
                color={isAlternate ? "#EDEDDF" : "#F5F5F0"}
                roughness={0.12}
                metalness={0.05}
              />
            </mesh>
          );
        })
      )}

      {/* Ceiling */}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 6, 0]}>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial color="#E8E4D8" roughness={0.8} />
      </mesh>

      {/* Walls */}
      <mesh position={[0, 3, -10]} receiveShadow>
        <planeGeometry args={[20, 6]} />
        <meshStandardMaterial color="#EDE8DC" roughness={0.6} />
      </mesh>
      <mesh position={[0, 3, 10]} rotation={[0, Math.PI, 0]}>
        <planeGeometry args={[20, 6]} />
        <meshStandardMaterial color="#EDE8DC" roughness={0.6} />
      </mesh>
      <mesh position={[-10, 3, 0]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[20, 6]} />
        <meshStandardMaterial color="#EDE8DC" roughness={0.6} />
      </mesh>
      <mesh position={[10, 3, 0]} rotation={[0, -Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[20, 6]} />
        <meshStandardMaterial color="#EDE8DC" roughness={0.6} />
      </mesh>

      {/* Wall columns - skip center on back wall so text is visible */}
      {[-8, -4, 4, 8].map((x) => (
        <group key={`col-back-${x}`}>
          <Column position={[x, 0, -9.8]} />
        </group>
      ))}
      {[-8, -4, 0, 4, 8].map((x) => (
        <group key={`col-left-${x}`}>
          <Column position={[-9.8, 0, x]} rotation={[0, Math.PI / 2, 0]} />
        </group>
      ))}

      {/* Arched windows */}
      {[-6, -2, 2, 6].map((x) => (
        <ArchedWindow key={`win-${x}`} position={[x, 2.5, -9.7]} />
      ))}

      {/* Gold trim along ceiling */}
      <mesh position={[0, 5.9, -9.9]}>
        <boxGeometry args={[20, 0.15, 0.1]} />
        <meshStandardMaterial color={GOLD_COLOR} metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[-9.9, 5.9, 0]} rotation={[0, Math.PI / 2, 0]}>
        <boxGeometry args={[20, 0.15, 0.1]} />
        <meshStandardMaterial color={GOLD_COLOR} metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[9.9, 5.9, 0]} rotation={[0, Math.PI / 2, 0]}>
        <boxGeometry args={[20, 0.15, 0.1]} />
        <meshStandardMaterial color={GOLD_COLOR} metalness={0.8} roughness={0.2} />
      </mesh>

      {/* ===== WALL TEXT: "Equipe De Marketing TOP AGENDA" ===== */}
      {/* Back wall banner - decorative plaque */}
      <mesh position={[0, 4.5, -9.85]}>
        <boxGeometry args={[8, 1.2, 0.08]} />
        <meshStandardMaterial color={WALNUT_COLOR} roughness={0.35} metalness={0.05} />
      </mesh>
      {/* Gold border around plaque */}
      <mesh position={[0, 4.5, -9.8]}>
        <boxGeometry args={[8.1, 1.3, 0.02]} />
        <meshStandardMaterial color={GOLD_COLOR} metalness={0.9} roughness={0.1} />
      </mesh>

      {/* Main title text */}
      <Text
        position={[0, 4.7, -9.78]}
        fontSize={0.35}
        color="#D4AF37"
        anchorX="center"
        anchorY="middle"
        maxWidth={7}
      >
        EQUIPE DE MARKETING
      </Text>

      {/* Brand name */}
      <Text
        position={[0, 4.25, -9.78]}
        fontSize={0.45}
        color="#F5F5F0"
        anchorX="center"
        anchorY="middle"
        maxWidth={7}
      >
        TOP AGENDA
      </Text>

      {/* Spotlight on the wall text */}
      <spotLight
        position={[0, 5.8, -7]}
        target-position={[0, 4.5, -9.85]}
        intensity={1.5}
        color="#FFF8E7"
        angle={0.4}
        penumbra={0.5}
        distance={8}
      />
    </group>
  );
};

const Column = ({ position, rotation }: { position: [number, number, number]; rotation?: [number, number, number] }) => (
  <group position={position} rotation={rotation}>
    <mesh position={[0, 0.15, 0]} castShadow>
      <boxGeometry args={[0.6, 0.3, 0.6]} />
      <meshStandardMaterial color={MARBLE_COLOR} roughness={0.15} />
    </mesh>
    <mesh position={[0, 3, 0]} castShadow>
      <cylinderGeometry args={[0.18, 0.22, 5.4, 16]} />
      <meshStandardMaterial color={MARBLE_COLOR} roughness={0.15} />
    </mesh>
    <mesh position={[0, 5.8, 0]} castShadow>
      <boxGeometry args={[0.55, 0.3, 0.55]} />
      <meshStandardMaterial color={MARBLE_COLOR} roughness={0.15} />
    </mesh>
    <mesh position={[0, 5.6, 0]}>
      <torusGeometry args={[0.22, 0.03, 8, 16]} />
      <meshStandardMaterial color={GOLD_COLOR} metalness={0.9} roughness={0.1} />
    </mesh>
  </group>
);

const ArchedWindow = ({ position }: { position: [number, number, number] }) => (
  <group position={position}>
    <mesh>
      <boxGeometry args={[1.6, 3, 0.05]} />
      <meshStandardMaterial color={GOLD_COLOR} metalness={0.6} roughness={0.3} opacity={0.3} transparent />
    </mesh>
    <pointLight position={[0, 0, 0.5]} intensity={0.8} color="#FFF8E7" distance={8} />
  </group>
);

export default Room;
