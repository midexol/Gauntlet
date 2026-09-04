// Purely decorative: three large, blurred, slow-drifting color fields behind
// the content. Fixed to the viewport so it reads as one continuous living
// background across the whole page rather than a per-section repeat.
// prefers-reduced-motion is already handled globally in index.css.
export function AnimatedBackground({ variant = "dark" }: { variant?: "dark" | "light" }) {
  const base = variant === "dark" ? "#0e1116" : "#ecefec";
  return (
    <div
      aria-hidden
      className="fixed inset-0 -z-10 overflow-hidden pointer-events-none"
      style={{ background: base }}
    >
      <div
        className="absolute rounded-full"
        style={{
          width: "60vw",
          height: "60vw",
          top: "-15vw",
          left: "-10vw",
          background: "radial-gradient(circle, var(--color-signal-amber) 0%, transparent 70%)",
          opacity: variant === "dark" ? 0.16 : 0.12,
          filter: "blur(60px)",
          animation: "drift-a 26s ease-in-out infinite",
        }}
      />
      <div
        className="absolute rounded-full"
        style={{
          width: "50vw",
          height: "50vw",
          bottom: "-20vw",
          right: "-15vw",
          background: "radial-gradient(circle, var(--color-signal-red) 0%, transparent 70%)",
          opacity: variant === "dark" ? 0.1 : 0.08,
          filter: "blur(70px)",
          animation: "drift-b 32s ease-in-out infinite",
        }}
      />
      <div
        className="absolute rounded-full"
        style={{
          width: "40vw",
          height: "40vw",
          top: "30vh",
          left: "50vw",
          background: "radial-gradient(circle, var(--color-signal-green) 0%, transparent 70%)",
          opacity: variant === "dark" ? 0.07 : 0.06,
          filter: "blur(80px)",
          animation: "drift-c 38s ease-in-out infinite",
        }}
      />
    </div>
  );
}
