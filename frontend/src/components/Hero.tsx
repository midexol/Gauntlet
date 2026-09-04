import { Link } from "react-router-dom";
import { Gauge } from "./Gauge";

export function Hero() {
  return (
    <section className="relative px-6 md:px-16 pt-16 pb-20 text-[var(--color-concrete)]">
      <div className="max-w-6xl mx-auto grid md:grid-cols-[1.3fr_1fr] gap-12 items-center">
        <div>
          <div className="inline-block text-[11px] font-mono tracking-[0.2em] uppercase text-[var(--color-signal-amber)] border border-[var(--color-signal-amber-dim)] rounded-full px-3 py-1 mb-6">
            An AI agent that grades other strategies
          </div>

          <div className="font-display font-extrabold uppercase leading-[0.95] text-[13vw] md:text-6xl tracking-tight">
            Most trading
            <br />
            bots crash.
            <br />
            <span className="text-[var(--color-signal-amber)]">This one runs</span>
            <br />
            the gauntlet first.
          </div>

          <p className="mt-8 max-w-xl text-[var(--color-ash)] text-base leading-relaxed">
            GAUNTLET is an agent, not a form. Hand it a strategy in plain
            English and it does the work a skeptical risk desk would: compile
            it into explicit rules, backtest it, attack it with five
            independent stress tests, and hand back a robustness score with
            its reasoning attached. A second agent explains what it found in
            plain language — it can describe the numbers, never change them.
            A deterministic gate makes the final call on whether the strategy
            is even allowed to touch paper money.
          </p>

          <div className="mt-9 flex flex-wrap gap-4">
            <Link
              to="/run"
              className="rounded-lg bg-[var(--color-signal-amber)] text-[var(--color-ink)] font-mono font-semibold px-6 py-3 hover:brightness-110 hover:-translate-y-0.5 transition-all inline-block"
            >
              Run a strategy through it
            </Link>
            <a
              href="https://github.com/midexol/Gauntlet"
              className="rounded-lg border border-[var(--color-panel-line)] px-6 py-3 font-mono text-sm hover:border-[var(--color-signal-amber)] hover:-translate-y-0.5 transition-all"
            >
              View the code
            </a>
          </div>
        </div>

        <div className="lift-on-hover justify-self-center rounded-2xl bg-[var(--color-panel)] border border-[var(--color-panel-line)] p-6">
          <div className="text-xs text-[var(--color-ash)] mb-2">robustness score &middot; illustrative example</div>
          <Gauge value={89.7} label="PASS · 89.7 / 100" textColor="var(--color-concrete)" />
          <div className="mt-3 text-[11px] text-[var(--color-ash)] leading-relaxed">
            Every dial and number on the run page reads real numbers from
            your own strategy — not a mockup.
          </div>
        </div>
      </div>
    </section>
  );
}
