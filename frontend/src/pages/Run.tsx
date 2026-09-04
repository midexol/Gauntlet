import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { PipelineStrip, type Stage, type StageStatus } from "../components/PipelineStrip";
import { StrategyForm } from "../components/StrategyForm";
import { CrashSequence } from "../components/CrashSequence";
import { GateVerdict } from "../components/GateVerdict";
import { MetricsPanel } from "../components/MetricsPanel";
import { ExplainPanel } from "../components/ExplainPanel";
import { BackendStatus } from "../components/BackendStatus";
import { AnimatedBackground } from "../components/AnimatedBackground";
import {
  ApiError,
  compileStrategy,
  runCrashTest,
  runRiskGate,
  submitPaperTrade,
  checkMonitor,
  type Strategy,
  type CrashTestSummary,
  type GateDecision,
  type BaselineMetrics,
} from "../lib/api";

type Phase = "idle" | "compiled" | "crash-tested" | "gated" | "traded" | "monitored";

const STAGE_LABELS = ["Compile", "Backtest", "Crash test", "Risk gate", "Paper trade", "Monitor"];

export default function Run() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [runId, setRunId] = useState<number | null>(null);
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [baselineMetrics, setBaselineMetrics] = useState<BaselineMetrics | null>(null);
  const [crashSummary, setCrashSummary] = useState<CrashTestSummary | null>(null);
  const [gate, setGate] = useState<GateDecision | null>(null);
  const [orderResult, setOrderResult] = useState<Record<string, unknown> | null>(null);
  const [monitorMsg, setMonitorMsg] = useState<string | null>(null);

  // "crash-tested" reflects the single /crash-test call completing BOTH the
  // baseline backtest and the 5 stress tests — so it marks 3 stages done at
  // once (Compile, Backtest, Crash test), not 2. This maps each phase to how
  // many pipeline stages are actually complete, not just "current index".
  const stagesCompleted: Record<Phase, number> = {
    idle: 0,
    compiled: 1,
    "crash-tested": 3,
    gated: 4,
    traded: 5,
    monitored: 6,
  };

  const stages: Stage[] = useMemo(
    () =>
      STAGE_LABELS.map((label, i) => {
        const done = stagesCompleted[phase];
        let status: StageStatus = "pending";
        if (i < done) status = "done";
        else if (i === done && busy) status = "active";
        return { n: i + 1, label, status };
      }),
    [phase, busy]
  );

  const describeError = (e: unknown) => {
    if (e instanceof ApiError) {
      const d = e.detail as any;
      if (d?.reason) return d.reason;
      if (typeof d === "string") return d;
      return JSON.stringify(d);
    }
    return e instanceof Error ? e.message : "Something went wrong.";
  };

  const handleCompile = async (description: string) => {
    setBusy("compile");
    setError(null);
    try {
      const res = await compileStrategy(description);
      setRunId(res.run_id);
      setStrategy(res.strategy);
      setPhase("compiled");
    } catch (e) {
      setError(describeError(e));
    } finally {
      setBusy(null);
    }
  };

  const handleCrashTest = async () => {
    if (!runId) return;
    setBusy("crash-test");
    setError(null);
    try {
      const res = await runCrashTest(runId);
      setBaselineMetrics(res.baseline_metrics);
      setCrashSummary(res.crash_test_summary);
      setPhase("crash-tested");
    } catch (e) {
      setError(describeError(e));
    } finally {
      setBusy(null);
    }
  };

  const handleGate = async () => {
    if (!runId) return;
    setBusy("gate");
    setError(null);
    try {
      const res = await runRiskGate(runId);
      setGate(res.gate_decision);
      setPhase("gated");
    } catch (e) {
      setError(describeError(e));
    } finally {
      setBusy(null);
    }
  };

  const handlePaperTrade = async () => {
    if (!runId) return;
    setBusy("trade");
    setError(null);
    try {
      const res = await submitPaperTrade(runId, "buy");
      setOrderResult(res.order);
      setPhase("traded");
    } catch (e) {
      setError(describeError(e));
    } finally {
      setBusy(null);
    }
  };

  const handleMonitor = async () => {
    if (!runId) return;
    setBusy("monitor");
    setError(null);
    try {
      const res = await checkMonitor(runId);
      setMonitorMsg(res.message);
      setPhase("monitored");
    } catch (e) {
      setError(describeError(e));
    } finally {
      setBusy(null);
    }
  };

  const reset = () => {
    setPhase("idle");
    setRunId(null);
    setStrategy(null);
    setBaselineMetrics(null);
    setCrashSummary(null);
    setGate(null);
    setOrderResult(null);
    setMonitorMsg(null);
    setError(null);
  };

  return (
    <div className="relative min-h-screen">
      <AnimatedBackground variant="light" />

      <div className="bg-[var(--color-ink)] px-6 md:px-16 py-5">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link to="/" className="font-display font-extrabold uppercase text-[var(--color-concrete)] text-lg tracking-tight hover:text-[var(--color-signal-amber)] transition-colors">
            Gauntlet
          </Link>
          <Link to="/" className="text-xs font-mono text-[var(--color-ash)] hover:text-[var(--color-signal-amber)] transition-colors">
            &larr; back to overview
          </Link>
        </div>
      </div>

      <PipelineStrip stages={stages} />

      <main className="max-w-4xl mx-auto px-6 py-14 space-y-10">
        <div className="flex items-center justify-between">
          <BackendStatus />
          {runId && (
            <button onClick={reset} className="text-xs font-mono text-[var(--color-ash)] underline">
              start a new strategy
            </button>
          )}
        </div>

        <div>
          {phase === "idle" ? (
            <StrategyForm onSubmit={handleCompile} loading={busy === "compile"} />
          ) : (
            <div className="lift-on-hover rounded-xl border border-[var(--color-concrete-line)] p-5 bg-white/40">
              <div className="text-xs text-[var(--color-ash)] mb-1">compiled strategy · run #{runId}</div>
              <div className="font-mono text-sm">
                {strategy?.name} — {strategy?.symbol} · SMA {strategy?.entry.fast}/{strategy?.entry.slow} · {strategy?.position_size_pct}% size
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="rounded-xl border border-[var(--color-signal-red)] text-[var(--color-signal-red)] p-4 text-sm">
            {error}
          </div>
        )}

        {phase === "compiled" && (
          <button
            onClick={handleCrashTest}
            disabled={busy === "crash-test"}
            className="rounded-lg bg-[var(--color-ink)] text-[var(--color-concrete)] font-mono font-semibold px-6 py-3 disabled:opacity-40 hover:-translate-y-0.5 transition-transform"
          >
            {busy === "crash-test" ? "Running backtest + 5 crash tests…" : "Run the crash test"}
          </button>
        )}

        {crashSummary && baselineMetrics && (
          <div className="space-y-6">
            <CrashSequence results={crashSummary.results} robustnessScore={crashSummary.robustness_score} />
            <MetricsPanel metrics={baselineMetrics} />
            <ExplainPanel runId={runId!} />
          </div>
        )}

        {phase === "crash-tested" && (
          <button
            onClick={handleGate}
            disabled={busy === "gate"}
            className="rounded-lg bg-[var(--color-ink)] text-[var(--color-concrete)] font-mono font-semibold px-6 py-3 disabled:opacity-40 hover:-translate-y-0.5 transition-transform"
          >
            {busy === "gate" ? "Evaluating risk gate…" : "Evaluate risk gate"}
          </button>
        )}

        {gate && <GateVerdict gate={gate} />}

        {phase === "gated" && gate?.decision !== "BLOCK" && (
          <button
            onClick={handlePaperTrade}
            disabled={busy === "trade"}
            className="rounded-lg bg-[var(--color-signal-amber)] text-[var(--color-ink)] font-mono font-semibold px-6 py-3 disabled:opacity-40 hover:-translate-y-0.5 transition-transform"
          >
            {busy === "trade" ? "Submitting paper order…" : "Submit paper trade"}
          </button>
        )}
        {phase === "gated" && gate?.decision === "BLOCK" && (
          <div className="text-sm text-[var(--color-ash)]">
            This strategy was blocked — it never reaches Alpaca. That's the gate doing its job.
          </div>
        )}

        {orderResult && (
          <div className="rounded-xl border border-[var(--color-concrete-line)] p-4 font-mono text-sm bg-white/40">
            order #{String(orderResult.order_id)} · {String(orderResult.side)} {String(orderResult.symbol)} · $
            {String(orderResult.notional)} · {String(orderResult.status)}
          </div>
        )}

        {phase === "traded" && (
          <button
            onClick={handleMonitor}
            disabled={busy === "monitor"}
            className="rounded-lg bg-[var(--color-ink)] text-[var(--color-concrete)] font-mono font-semibold px-6 py-3 disabled:opacity-40 hover:-translate-y-0.5 transition-transform"
          >
            {busy === "monitor" ? "Checking failure regime…" : "Check monitor / kill-switch"}
          </button>
        )}

        {monitorMsg && (
          <div className="rounded-xl border border-[var(--color-concrete-line)] p-4 text-sm bg-white/40">{monitorMsg}</div>
        )}
      </main>

      <div className="hazard-stripe" />

      <footer className="bg-[var(--color-ink)] text-[var(--color-ash)] px-6 py-8 text-xs font-mono">
        GAUNTLET — built for the Alpaca AI Trading Agents Hackathon. Every number above came from a live call to the backend, not a mockup.
      </footer>
    </div>
  );
}
