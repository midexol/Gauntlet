import { useEffect, useState } from "react";
import { Gauge } from "./Gauge";
import type { CrashTestResult } from "../lib/api";

// The 5 crash tests, revealed one at a time instead of all at once — each
// one "lands" with a colored flash, then the gauge sweeps in once every
// attack has resolved. All real data, just paced out.

const LABELS: Record<string, string> = {
  historical_robustness: "Historical robustness",
  parameter_sensitivity: "Parameter sensitivity",
  drawdown_resilience: "Drawdown resilience",
  volatility_stress: "Volatility stress",
  market_reversal: "Market reversal",
};

const severityColor: Record<string, string> = {
  low: "var(--color-signal-green)",
  medium: "var(--color-signal-amber)",
  high: "var(--color-signal-red)",
};

const STAGGER_MS = 420;

function prefersReducedMotion() {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function CrashSequence({
  results,
  robustnessScore,
}: {
  results: CrashTestResult[];
  robustnessScore: number;
}) {
  const [revealedCount, setRevealedCount] = useState(0);
  const [showGauge, setShowGauge] = useState(false);

  useEffect(() => {
    if (prefersReducedMotion()) {
      setRevealedCount(results.length);
      setShowGauge(true);
      return;
    }
    setRevealedCount(0);
    setShowGauge(false);
    const timers: number[] = [];
    results.forEach((_, i) => {
      timers.push(window.setTimeout(() => setRevealedCount((c) => Math.max(c, i + 1)), i * STAGGER_MS));
    });
    timers.push(window.setTimeout(() => setShowGauge(true), results.length * STAGGER_MS + 150));
    return () => timers.forEach(clearTimeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [results, robustnessScore]);

  return (
    <div className="grid md:grid-cols-[220px_1fr] gap-8 items-center">
      <div className={`transition-opacity duration-500 ${showGauge ? "opacity-100" : "opacity-0"}`}>
        <Gauge value={showGauge ? robustnessScore : null} label="robustness score" />
      </div>

      <div className="space-y-3">
        {results.map((r, i) => {
          const revealed = i < revealedCount;
          const color = severityColor[r.severity];
          return (
            <div
              key={r.test_type}
              className="p-1 -m-1"
              style={revealed ? ({ ["--flash-color" as string]: color, animation: "attack-flash 550ms ease-out" }) : undefined}
            >
              <div className="flex justify-between text-xs font-mono mb-1">
                <span>{LABELS[r.test_type] ?? r.test_type}</span>
                {revealed ? (
                  <span style={{ color }}>{r.score.toFixed(1)}</span>
                ) : (
                  <span className="text-[var(--color-ash)]" style={{ animation: "attack-pending 1.1s ease-in-out infinite" }}>
                    attacking&hellip;
                  </span>
                )}
              </div>
              <div className="h-2 bg-[var(--color-panel-line)] w-full overflow-hidden">
                {revealed ? (
                  <div className="h-2 transition-[width] duration-500" style={{ width: `${Math.min(100, r.score)}%`, background: color }} />
                ) : (
                  <div className="h-2 w-1/3 bg-[var(--color-ash)]" style={{ animation: "attack-pending 1.1s ease-in-out infinite" }} />
                )}
              </div>
              {revealed && !r.passed && r.failure_reason && (
                <div className="text-[11px] text-[var(--color-signal-red)] mt-1">{r.failure_reason}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
