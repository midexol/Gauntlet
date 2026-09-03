import { useEffect, useState } from "react";

// A dashboard-cluster style gauge, 0-100, sweeping like a speedometer needle.
// Sweeps to its value once on mount/update — the one orchestrated motion
// moment in the whole app, not a scattered per-element animation.
export function Gauge({
  value,
  label,
  size = 220,
  textColor = "var(--color-ink)",
}: {
  value: number | null;
  label: string;
  size?: number;
  textColor?: string;
}) {
  const [animated, setAnimated] = useState(0);

  useEffect(() => {
    if (value === null) {
      setAnimated(0);
      return;
    }
    let frame: number;
    const start = performance.now();
    const duration = 900;
    const from = 0;
    const to = value;
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      setAnimated(from + (to - from) * eased);
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  const clamped = Math.max(0, Math.min(100, animated));
  // Gauge sweeps from -120deg to +120deg (240deg total arc)
  const angle = -120 + (clamped / 100) * 240;
  const cx = size / 2;
  const cy = size / 2;
  const r = size * 0.38;

  const color =
    value === null ? "var(--color-ash)" : value >= 80 ? "var(--color-signal-green)" : value >= 60 ? "var(--color-signal-amber)" : "var(--color-signal-red)";

  // arc path helper
  const polarToXY = (deg: number, radius: number) => {
    const rad = (deg - 90) * (Math.PI / 180);
    return [cx + radius * Math.cos(rad), cy + radius * Math.sin(rad)];
  };
  const arcPath = (startDeg: number, endDeg: number, radius: number) => {
    const [x1, y1] = polarToXY(startDeg, radius);
    const [x2, y2] = polarToXY(endDeg, radius);
    const largeArc = endDeg - startDeg > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`;
  };

  const [needleX, needleY] = polarToXY(angle, r * 0.92);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.82} viewBox={`0 0 ${size} ${size * 0.82}`}>
        {/* track */}
        <path d={arcPath(-120, 120, r)} fill="none" stroke="var(--color-panel-line)" strokeWidth={10} strokeLinecap="round" />
        {/* zone markers: red / amber / green bands */}
        <path d={arcPath(-120, -24, r)} stroke="var(--color-signal-red)" strokeWidth={4} fill="none" strokeLinecap="round" opacity={0.5} />
        <path d={arcPath(-24, 24, r)} stroke="var(--color-signal-amber)" strokeWidth={4} fill="none" strokeLinecap="round" opacity={0.5} />
        <path d={arcPath(24, 120, r)} stroke="var(--color-signal-green)" strokeWidth={4} fill="none" strokeLinecap="round" opacity={0.5} />
        {/* needle */}
        <line x1={cx} y1={cy} x2={needleX} y2={needleY} stroke={color} strokeWidth={3} strokeLinecap="round" />
        <circle cx={cx} cy={cy} r={5} fill={color} />
        {/* value readout */}
        <text x={cx} y={cy + size * 0.2} textAnchor="middle" fontFamily="IBM Plex Mono" fontSize={size * 0.16} fontWeight={600} fill={textColor}>
          {value === null ? "--" : Math.round(clamped)}
        </text>
      </svg>
      <div className="text-xs tracking-wide mt-1" style={{ color: textColor === "var(--color-ink)" ? "var(--color-ash)" : textColor }}>{label}</div>
    </div>
  );
}
