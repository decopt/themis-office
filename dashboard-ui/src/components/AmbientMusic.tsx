import { useState, useCallback, useRef, useEffect } from "react";

const VOLUME = 0.12; // ~12% volume

export const AmbientMusic = () => {
  const [playing, setPlaying] = useState(false);
  const ctxRef = useRef<AudioContext | null>(null);
  const nodesRef = useRef<AudioNode[]>([]);

  const startMusic = useCallback(() => {
    if (ctxRef.current) return;

    const ctx = new AudioContext();
    ctxRef.current = ctx;
    const master = ctx.createGain();
    master.gain.value = VOLUME;
    master.connect(ctx.destination);

    // Warm pad: layered detuned oscillators
    const padFreqs = [130.81, 164.81, 196.0, 261.63]; // C3, E3, G3, C4
    padFreqs.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      osc.type = "sine";
      osc.frequency.value = freq;
      osc.detune.value = (i - 1.5) * 4; // slight detune for warmth

      const gain = ctx.createGain();
      gain.gain.value = 0.06;

      // Slow tremolo
      const lfo = ctx.createOscillator();
      lfo.type = "sine";
      lfo.frequency.value = 0.15 + i * 0.05;
      const lfoGain = ctx.createGain();
      lfoGain.gain.value = 0.015;
      lfo.connect(lfoGain);
      lfoGain.connect(gain.gain);
      lfo.start();

      // Low-pass filter for warmth
      const filter = ctx.createBiquadFilter();
      filter.type = "lowpass";
      filter.frequency.value = 600;
      filter.Q.value = 0.5;

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(master);
      osc.start();

      nodesRef.current.push(osc, lfo);
    });

    // Subtle high shimmer
    const shimmer = ctx.createOscillator();
    shimmer.type = "triangle";
    shimmer.frequency.value = 523.25; // C5
    const shimGain = ctx.createGain();
    shimGain.gain.value = 0.008;
    const shimFilter = ctx.createBiquadFilter();
    shimFilter.type = "bandpass";
    shimFilter.frequency.value = 500;
    shimFilter.Q.value = 2;
    shimmer.connect(shimFilter);
    shimFilter.connect(shimGain);
    shimGain.connect(master);
    shimmer.start();
    nodesRef.current.push(shimmer);

    setPlaying(true);
  }, []);

  const stopMusic = useCallback(() => {
    nodesRef.current.forEach(n => {
      if (n instanceof OscillatorNode) n.stop();
    });
    nodesRef.current = [];
    ctxRef.current?.close();
    ctxRef.current = null;
    setPlaying(false);
  }, []);

  useEffect(() => {
    return () => {
      if (ctxRef.current) {
        nodesRef.current.forEach(n => {
          if (n instanceof OscillatorNode) try { n.stop(); } catch {}
        });
        ctxRef.current.close();
      }
    };
  }, []);

  return (
    <button
      onClick={playing ? stopMusic : startMusic}
      className="absolute top-6 right-6 z-20 bg-card/70 backdrop-blur-sm border border-border rounded-lg px-3 py-1.5 text-xs text-muted-foreground hover:text-gold transition-colors cursor-pointer"
      title={playing ? "Pausar música" : "Tocar música ambiente"}
    >
      {playing ? "🔊 Som" : "🔇 Som"}
    </button>
  );
};

export default AmbientMusic;
