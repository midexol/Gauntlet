import { useState } from "react";
import { explainCrashTest } from "../lib/api";

export function ExplainPanel({ runId }: { runId: number }) {
  const [text, setText] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExplanation = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await explainCrashTest(runId);
      setText(res.explanation);
    } catch (e: any) {
      setError(
        e?.detail?.reason ||
          "The crash analyst couldn't run — likely no LLM_API_KEY configured on the backend."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="lift-on-hover rounded-xl border border-[var(--color-concrete-line)] p-5 bg-white/40">
      <div className="flex items-center justify-between">
        <div className="text-sm font-semibold">Ask the crash analyst to explain this</div>
        <button
          onClick={fetchExplanation}
          disabled={loading}
          className="rounded-lg text-xs font-mono border border-[var(--color-ink)] px-3 py-1.5 disabled:opacity-40 hover:bg-[var(--color-ink)] hover:text-[var(--color-concrete)] transition-colors"
        >
          {loading ? "Thinking…" : text ? "Regenerate" : "Explain"}
        </button>
      </div>
      {error && <div className="mt-3 text-sm text-[var(--color-signal-red)]">{error}</div>}
      {text && <p className="mt-3 text-sm leading-relaxed whitespace-pre-wrap">{text}</p>}
    </div>
  );
}
