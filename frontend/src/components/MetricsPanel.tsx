import type { BaselineMetrics } from "../lib/api";

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="lift-on-hover rounded-xl border border-[var(--color-concrete-line)] bg-white/40 p-3">
      <div className="text-[11px] text-[var(--color-ash)]">{label}</div>
      <div className="font-mono text-lg">{value}</div>
    </div>
  );
}

export function MetricsPanel({ metrics }: { metrics: BaselineMetrics }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <Metric label="Total return" value={`${metrics.total_return_pct.toFixed(2)}%`} />
      <Metric
        label={metrics.benchmark_symbol ? `Benchmark (${metrics.benchmark_symbol})` : "Benchmark"}
        value={`${metrics.benchmark_return_pct.toFixed(2)}%`}
      />
      <Metric label="Max drawdown" value={`${metrics.max_drawdown_pct.toFixed(2)}%`} />
      <Metric label="Sharpe" value={metrics.sharpe_ratio.toFixed(2)} />
      <Metric label="Trades" value={String(metrics.trade_count)} />
      <Metric label="Win rate" value={`${metrics.win_rate_pct.toFixed(1)}%`} />
      <Metric label="Profit factor" value={metrics.profit_factor.toFixed(2)} />
    </div>
  );
}
