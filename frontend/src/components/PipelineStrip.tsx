export type StageStatus = "pending" | "active" | "done" | "error";

export interface Stage {
  n: number;
  label: string;
  status: StageStatus;
}

const statusStyle: Record<StageStatus, string> = {
  pending: "border-[var(--color-panel-line)] text-[var(--color-ash)]",
  active: "border-[var(--color-signal-amber)] text-[var(--color-signal-amber)]",
  done: "border-[var(--color-signal-green)] text-[var(--color-signal-green)]",
  error: "border-[var(--color-signal-red)] text-[var(--color-signal-red)]",
};

export function PipelineStrip({ stages }: { stages: Stage[] }) {
  return (
    <div className="bg-[var(--color-ink)] px-6 md:px-16 py-5">
      <div className="max-w-6xl mx-auto flex flex-wrap gap-3">
        {stages.map((s) => (
          <div
            key={s.n}
            className={`flex items-center gap-2 border px-3 py-2 font-mono text-xs ${statusStyle[s.status]}`}
          >
            <span className="opacity-70">{String(s.n).padStart(2, "0")}</span>
            <span>{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
