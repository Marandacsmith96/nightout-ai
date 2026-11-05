/* NightOut AI — small reusable UI pieces.
   Kept deliberately tiny and dependency-free. */

export function Button({ children, variant = "primary", size = "", className = "", ...rest }) {
  const cls = ["btn", variant === "ghost" ? "btn-ghost" : "btn-primary", size ? `btn-${size}` : "", className].join(" ").trim();
  return (
    <button className={cls} {...rest}>
      {children}
    </button>
  );
}

/** Toggle pill used for multi-select and single-select option rows. */
export function Chip({ label, active, onClick, single = false }) {
  return (
    <button type="button" className={`chip${active ? " on" : ""}${single ? " single" : ""}`} onClick={onClick} aria-pressed={active}>
      {label}
    </button>
  );
}

export function Field({ label, hint, error, children, full = false, className = "" }) {
  return (
    <div className={`field${full ? " full" : ""} ${className}`.trim()}>
      <label>
        {label}
        {hint ? <span className="hint"> — {hint}</span> : null}
      </label>
      {children}
      {error ? <span className="field-error">{error}</span> : null}
    </div>
  );
}

export function Stepper({ value, min = 1, max = 20, onChange, label }) {
  return (
    <div className="stepper" role="group" aria-label={label}>
      <button type="button" onClick={() => onChange(Math.max(min, value - 1))} aria-label="Decrease">
        −
      </button>
      <span className="stepper-val">{value}</span>
      <button type="button" onClick={() => onChange(Math.min(max, value + 1))} aria-label="Increase">
        +
      </button>
    </div>
  );
}

/** Budget slider with a live-fill track; value synced from presets and custom input. */
export function BudgetSlider({ value, min = 5, max = 250, step = 5, onChange }) {
  const fill = ((value - min) / (max - min)) * 100;
  return (
    <div className="range-wrap">
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <span style={{ fontSize: 13, color: "var(--muted)" }}>Budget per person</span>
        <span className="range-val">${value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ "--fill": `${fill}%` }}
        aria-label="Budget per person in dollars"
      />
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11.5, color: "var(--muted-2)", marginTop: 4 }}>
        <span>${min}</span>
        <span>${max}+</span>
      </div>
    </div>
  );
}

export function LoadingOverlay({ title = "Planning your perfect night…", sub = "Picking real places that fit your group, budget, and time — this only takes a few seconds." }) {
  return (
    <div className="overlay" role="status" aria-live="polite">
      <div className="spinner" />
      <div className="overlay-title">{title}</div>
      <div className="overlay-sub">{sub}</div>
    </div>
  );
}
