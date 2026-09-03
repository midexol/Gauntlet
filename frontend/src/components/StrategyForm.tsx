import { useState } from "react";

export function StrategyForm({
  onSubmit,
  loading,
}: {
  onSubmit: (description: string) => void;
  loading: boolean;
}) {
  const [description, setDescription] = useState(
    "Buy NVDA when the 10-day SMA crosses above the 30-day SMA, sell when it crosses back below, use 10% position size."
  );

  return (
    <div className="border border-[var(--color-concrete-line)] bg-white/40 p-6">
      <label htmlFor="strategy" className="block text-sm font-semibold mb-2">
        Describe your strategy in plain English
      </label>
      <textarea
        id="strategy"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={3}
        className="w-full border border-[var(--color-concrete-line)] bg-white p-3 font-mono text-sm focus:border-[var(--color-signal-amber)] outline-none"
      />
      <div className="mt-1 text-xs text-[var(--color-ash)]">
        MVP compiles SMA-crossover strategies only — the compiler will tell you plainly if it can't parse yours rather than guessing.
      </div>
      <button
        onClick={() => onSubmit(description)}
        disabled={loading || !description.trim()}
        className="mt-4 bg-[var(--color-ink)] text-[var(--color-concrete)] font-mono font-semibold px-6 py-3 disabled:opacity-40 hover:bg-black transition-colors"
      >
        {loading ? "Compiling…" : "Compile strategy"}
      </button>
    </div>
  );
}
