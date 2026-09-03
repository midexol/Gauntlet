import { useEffect, useState } from "react";
import { verifyAlpaca } from "../lib/api";

type Status = "checking" | "connected" | "unreachable";

export function BackendStatus() {
  const [status, setStatus] = useState<Status>("checking");
  const [detail, setDetail] = useState<string>("");

  useEffect(() => {
    verifyAlpaca()
      .then((res) => {
        setStatus("connected");
        setDetail(res.paper_mode ? "paper mode" : "live mode");
      })
      .catch((e) => {
        setStatus("unreachable");
        setDetail(e?.detail?.config_problems?.join(", ") || e.message || "unreachable");
      });
  }, []);

  const dotColor =
    status === "connected" ? "var(--color-signal-green)" : status === "unreachable" ? "var(--color-signal-red)" : "var(--color-signal-amber)";

  return (
    <div className="flex items-center gap-2 text-xs font-mono text-[var(--color-ash)]">
      <span className="w-2 h-2 rounded-full inline-block" style={{ background: dotColor }} />
      {status === "checking" && "checking Alpaca connection…"}
      {status === "connected" && `Alpaca connected · ${detail}`}
      {status === "unreachable" && `Alpaca unreachable · ${detail}`}
    </div>
  );
}
