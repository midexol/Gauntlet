// Single point of contact with the CRASH TEST backend. Every network call
// in the app goes through here — components never call fetch() directly.
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: unknown;
  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : JSON.stringify(detail));
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? body);
  }
  return res.json();
}

// ---- types matching the backend's pydantic models ----

export interface SmaCrossRule {
  fast: number;
  slow: number;
  direction: "above" | "below";
}

export interface Strategy {
  name: string;
  symbol: string;
  timeframe: string;
  entry: SmaCrossRule;
  exit: SmaCrossRule;
  position_size_pct: number;
  benchmark: string;
}

export interface CrashTestResult {
  test_type: string;
  score: number;
  severity: "low" | "medium" | "high";
  passed: boolean;
  metrics: Record<string, unknown>;
  failure_reason: string;
  evidence: Record<string, unknown>;
}

export interface CrashTestSummary {
  robustness_score: number;
  component_scores: Record<string, number>;
  weights: Record<string, number>;
  failed_tests: string[];
  high_severity_tests: string[];
  results: CrashTestResult[];
}

export interface GateDecision {
  decision: "PASS" | "CONDITIONAL" | "BLOCK";
  score: number;
  reasons: string[];
}

export interface BaselineMetrics {
  total_return_pct: number;
  benchmark_return_pct: number;
  benchmark_symbol?: string;
  max_drawdown_pct: number;
  trade_count: number;
  win_rate_pct: number;
  profit_factor: number;
  sharpe_ratio: number;
}

// ---- pipeline calls ----

export const compileStrategy = (description: string) =>
  request<{ run_id: number; strategy: Strategy }>("/compile-strategy", {
    method: "POST",
    body: JSON.stringify({ description }),
  });

export const runCrashTest = (runId: number) =>
  request<{ run_id: number; baseline_metrics: BaselineMetrics; crash_test_summary: CrashTestSummary }>(
    `/crash-test/${runId}`,
    { method: "POST" }
  );

export const explainCrashTest = (runId: number) =>
  request<{ run_id: number; explanation: string }>(`/crash-test/${runId}/explain`);

export const runRiskGate = (runId: number) =>
  request<{ run_id: number; gate_decision: GateDecision }>(`/risk-gate/${runId}`, { method: "POST" });

export const submitPaperTrade = (runId: number, side: "buy" | "sell" = "buy") =>
  request<{ run_id: number; order: Record<string, unknown> }>(`/paper-trade/${runId}`, {
    method: "POST",
    body: JSON.stringify({ side }),
  });

export const checkMonitor = (runId: number) =>
  request<{ run_id: number; alert: boolean; matched_test: string | null; message: string }>(
    `/monitor/${runId}`
  );

export const listRuns = () => request<Array<{ id: number; created_at: string; strategy: Strategy }>>("/runs");

export const verifyAlpaca = () =>
  request<{ account: Record<string, unknown>; bars_returned: number; paper_mode: boolean }>("/verify-alpaca");
