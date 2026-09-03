import type { GateDecision } from "../lib/api";

const styles: Record<GateDecision["decision"], { bg: string; text: string }> = {
  PASS: { bg: "var(--color-signal-green)", text: "#04140b" },
  CONDITIONAL: { bg: "var(--color-signal-amber)", text: "#221200" },
  BLOCK: { bg: "var(--color-signal-red)", text: "#1a0303" },
};

export function GateVerdict({ gate }: { gate: GateDecision }) {
  const s = styles[gate.decision];
  return (
    <div style={{ background: s.bg, color: s.text }} className="p-5">
      <div className="font-display font-extrabold text-3xl uppercase tracking-tight">{gate.decision}</div>
      <div className="text-sm font-mono opacity-80 mt-1">robustness score {gate.score.toFixed(1)}</div>
      <ul className="mt-3 space-y-1 text-sm font-mono">
        {gate.reasons.map((r, i) => (
          <li key={i}>· {r}</li>
        ))}
      </ul>
    </div>
  );
}
