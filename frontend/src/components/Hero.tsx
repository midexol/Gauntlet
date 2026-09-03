import { Gauge } from "./Gauge";

export function Hero({ onScrollToForm }: { onScrollToForm: () => void }) {
  return (
    <section className="bg-[var(--color-ink)] text-[var(--color-concrete)] px-6 md:px-16 pt-16 pb-20">
      <div className="max-w-6xl mx-auto grid md:grid-cols-[1.3fr_1fr] gap-12 items-center">
        <div>
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
            Describe a strategy in plain English. GAUNTLET compiles it into
            explicit rules, backtests it, then attacks it with five
            independent stress tests — different market eras, shaken
            parameters, a volatility spike, a synthetic trend reversal. Every
            strategy gets a robustness score before a deterministic gate
            decides whether it's even allowed to touch paper money.
          </p>

          <div className="mt-9 flex flex-wrap gap-4">
            <button
              onClick={onScrollToForm}
              className="bg-[var(--color-signal-amber)] text-[var(--color-ink)] font-mono font-semibold px-6 py-3 hover:brightness-110 transition-[filter]"
            >
              Run a strategy through it
            </button>
            <a
              href="https://github.com"
              className="border border-[var(--color-panel-line)] px-6 py-3 font-mono text-sm hover:border-[var(--color-signal-amber)] transition-colors"
            >
              View the code
            </a>
          </div>
        </div>

        <div className="justify-self-center bg-[var(--color-panel)] border border-[var(--color-panel-line)] p-6">
          <div className="text-xs text-[var(--color-ash)] mb-2">robustness score — live example</div>
          <Gauge value={89.7} label="PASS · 89.7 / 100" textColor="var(--color-concrete)" />
          <div className="mt-3 text-[11px] text-[var(--color-ash)] leading-relaxed">
            This dial reads real numbers from your own strategies below —
            not a mockup.
          </div>
        </div>
      </div>
    </section>
  );
}
