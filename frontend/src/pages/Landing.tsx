import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Hero } from "../components/Hero";
import { AnimatedBackground } from "../components/AnimatedBackground";

const STEPS = [
  { n: 1, label: "Idea", desc: "You describe a strategy in plain English." },
  { n: 2, label: "Strategy", desc: "A compiler agent turns it into strict, validated rules — or refuses rather than guessing." },
  { n: 3, label: "Attack", desc: "Five independent stress tests try to break it." },
  { n: 4, label: "Robustness", desc: "A weighted score, 0 to 100, no LLM involved in the math." },
  { n: 5, label: "Gate", desc: "A deterministic verdict: PASS, CONDITIONAL, or BLOCK." },
  { n: 6, label: "Paper trade", desc: "If it's not blocked, a real order goes to Alpaca — paper only." },
  { n: 7, label: "Monitor", desc: "Afterward, it watches for the exact failure it already flagged." },
];

const TESTS = [
  { title: "Historical robustness", weight: "25%", desc: "Does it hold across different market eras, or only on average?" },
  { title: "Parameter sensitivity", weight: "20%", desc: "Does a small input tweak collapse performance? Signals curve fitting." },
  { title: "Drawdown resilience", weight: "20%", desc: "How bad is the worst decline, and how long does it stay underwater?" },
  { title: "Volatility stress", weight: "20%", desc: "How does it perform specifically in the highest-volatility windows?" },
  { title: "Market reversal", weight: "15%", desc: "Does exit logic limit damage when the trend suddenly flips?" },
];

function SectionKicker({ children }: { children: ReactNode }) {
  return <div className="text-[13px] font-mono tracking-[0.2em] uppercase text-[var(--color-ash)]">{children}</div>;
}

export default function Landing() {
  return (
    <div className="relative">
      <AnimatedBackground variant="dark" />
      <div className="bg-[var(--color-ink)]">
        <Hero />
      </div>

      {/* The agent, explained */}
      <section className="relative px-6 md:px-16 py-20 bg-[var(--color-concrete)]">
        <div className="max-w-5xl mx-auto">
          <SectionKicker>What the agent actually does</SectionKicker>
          <div className="font-display font-extrabold uppercase text-4xl md:text-5xl mt-3 max-w-3xl">
            It doesn't ask what to trade. It asks whether your strategy has earned the right to.
          </div>
          <div className="mt-6 max-w-2xl text-[var(--color-ash)] leading-relaxed">
            Most AI trading tools stop at generating an idea. GAUNTLET picks up right where they
            leave off — it's the skeptic in the room, running your strategy through the same
            gauntlet a professional risk desk would, before a single dollar of paper money moves.
          </div>

          <div className="mt-12 grid md:grid-cols-7 gap-4">
            {STEPS.map((s) => (
              <div
                key={s.n}
                className="lift-on-hover rounded-xl border border-[var(--color-concrete-line)] bg-white/60 p-4"
              >
                <div className="w-8 h-8 rounded-full border-2 border-[var(--color-signal-amber)] text-[var(--color-signal-amber)] font-mono text-sm font-semibold flex items-center justify-center">
                  {s.n}
                </div>
                <div className="mt-3 font-mono text-sm font-semibold uppercase tracking-wide">{s.label}</div>
                <div className="mt-1.5 text-xs text-[var(--color-ash)] leading-relaxed">{s.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* The 5 crash tests */}
      <section className="relative px-6 md:px-16 py-20 bg-[var(--color-ink)] text-[var(--color-concrete)]">
        <div className="max-w-5xl mx-auto">
          <SectionKicker>The five attacks</SectionKicker>
          <div className="font-display font-extrabold uppercase text-4xl md:text-5xl mt-3 max-w-3xl">
            Five independent attacks. One robustness score.
          </div>

          <div className="mt-12 grid md:grid-cols-5 gap-4">
            {TESTS.map((t) => (
              <div key={t.title} className="lift-on-hover rounded-xl border border-[var(--color-panel-line)] bg-[var(--color-panel)] p-5">
                <div className="text-xs font-mono text-[var(--color-signal-amber)] font-semibold">{t.weight} weight</div>
                <div className="mt-2 font-semibold text-sm leading-snug">{t.title}</div>
                <div className="mt-2 text-xs text-[var(--color-ash)] leading-relaxed">{t.desc}</div>
              </div>
            ))}
          </div>

          <div className="mt-8 text-sm text-[var(--color-ash)]">
            No LLM anywhere in this math — every score is plain, reproducible pandas and numpy.
          </div>
        </div>
      </section>

      {/* Safety architecture */}
      <section className="relative px-6 md:px-16 py-20 bg-[var(--color-concrete)]">
        <div className="max-w-5xl mx-auto">
          <SectionKicker>Why it can be trusted</SectionKicker>
          <div className="font-display font-extrabold uppercase text-4xl md:text-5xl mt-3 max-w-3xl">
            The agent never touches the math.
          </div>

          <div className="mt-12 grid md:grid-cols-2 gap-6">
            <div className="lift-on-hover rounded-xl border border-[var(--color-concrete-line)] bg-white/60 p-7">
              <div className="text-xs font-mono font-semibold tracking-[0.2em] text-[var(--color-signal-amber-dim)]">RULE 1</div>
              <div className="mt-2 font-semibold text-lg">Scoring is deterministic.</div>
              <div className="mt-3 text-sm text-[var(--color-ash)] leading-relaxed">
                The two agents compile English into rules, and explain already-computed numbers in
                prose. Neither can alter a score, a verdict, or the gate decision.
              </div>
            </div>
            <div className="lift-on-hover rounded-xl border border-[var(--color-concrete-line)] bg-white/60 p-7">
              <div className="text-xs font-mono font-semibold tracking-[0.2em] text-[var(--color-signal-amber-dim)]">RULE 2</div>
              <div className="mt-2 font-semibold text-lg">Live trading is hard blocked.</div>
              <div className="mt-3 text-sm text-[var(--color-ash)] leading-relaxed">
                Not a config flag — enforced at three separate points in the code: client init, the
                risk gate, and order submission.
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="hazard-stripe" />

      {/* CTA */}
      <section className="relative px-6 md:px-16 py-24 bg-[var(--color-ink)] text-[var(--color-concrete)] text-center">
        <div className="max-w-2xl mx-auto">
          <div className="font-display font-extrabold uppercase text-4xl md:text-5xl">Ready to run one through it?</div>
          <p className="mt-4 text-[var(--color-ash)]">
            Describe a strategy in plain English. Watch it get attacked five different ways.
          </p>
          <Link
            to="/run"
            className="mt-8 inline-block rounded-lg bg-[var(--color-signal-amber)] text-[var(--color-ink)] font-mono font-semibold px-8 py-4 hover:brightness-110 hover:-translate-y-0.5 transition-all"
          >
            Run a strategy through it
          </Link>
        </div>
      </section>

      <footer className="bg-[var(--color-ink)] text-[var(--color-ash)] px-6 py-8 text-xs font-mono border-t border-[var(--color-panel-line)]">
        GAUNTLET — built for the Alpaca AI Trading Agents Hackathon.
      </footer>
    </div>
  );
}
