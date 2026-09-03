import type { CrashTestResult } from "../lib/api";

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

export function ComponentScores({ results }: { results: CrashTestResult[] }) {
  return (
    <div className="space-y-3">
      {results.map((r) => (
        <div key={r.test_type}>
          <div className="flex justify-between text-xs font-mono mb-1">
            <span>{LABELS[r.test_type] ?? r.test_type}</span>
            <span style={{ color: severityColor[r.severity] }}>{r.score.toFixed(1)}</span>
          </div>
          <div className="h-2 bg-[var(--color-panel-line)] w-full">
            <div
              className="h-2"
              style={{ width: `${Math.min(100, r.score)}%`, background: severityColor[r.severity] }}
            />
          </div>
          {!r.passed && r.failure_reason && (
            <div className="text-[11px] text-[var(--color-signal-red)] mt-1">{r.failure_reason}</div>
          )}
        </div>
      ))}
    </div>
  );
}
