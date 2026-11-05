import { useRef, useState } from "react";
import PlannerForm from "../components/PlannerForm.jsx";
import { LoadingOverlay } from "../components/kit.jsx";
import { formatTime, summarizeNight } from "../lib/nightOptions.js";

export default function PlannerPage() {
  const [plan, setPlan] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const resultsRef = useRef(null);

  function handleGenerate(payload) {
    setGenerating(true);
    // Phase 1: exercise the loading UI; Phase 3 replaces this with the real
    // backend call (api.generateNight).
    setTimeout(() => {
      setGenerating(false);
      setResult(payload);
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    }, 1600);
  }

  return (
    <div className="container" style={{ paddingTop: 44, paddingBottom: 30 }}>
      <h1 style={{ fontSize: "clamp(28px, 4.5vw, 40px)", fontWeight: 800, marginBottom: 6 }}>
        Plan <span className="gradient">My Night</span>
      </h1>
      <p style={{ color: "var(--muted)", maxWidth: 640, margin: "0 0 30px" }}>
        A minute of details now saves an hour of group-chat chaos later.
      </p>

      <div className="planner-grid">
        <section className="panel">
          <h2>Your night, your way</h2>
          <p className="panel-sub">Everything below can be changed later by chatting with the AI.</p>
          <PlannerForm onPlanChange={setPlan} onGenerate={handleGenerate} />
        </section>

        <aside className="panel live-summary">
          <h3>Your night so far</h3>
          {summarizeNight(plan).map(([k, v]) => (
            <div className="live-row" key={k}>
              <span>{k}</span>
              <span>{v}</span>
            </div>
          ))}
          {plan?.notes ? (
            <div style={{ marginTop: 12, fontSize: 12.5, color: "var(--muted-2)" }}>
              “{plan.notes.length > 140 ? plan.notes.slice(0, 140) + "…" : plan.notes}”
            </div>
          ) : null}
        </aside>
      </div>

      {result ? (
        <section ref={resultsRef} style={{ marginTop: 34 }} className="panel">
          <h2>Your night out request</h2>
          <p className="panel-sub">Everything below was captured — the AI generator connects here in Phase 3.</p>
          <div className="results-summary">
            <h3>✓ Request ready — {result.city}{result.state ? ", " + result.state : ""}</h3>
            <ul>
              <li>
                {new Date(result.date).toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })} ·{" "}
                {result.groupSize} {result.groupSize === 1 ? "person" : "people"} · ${result.budget}/person
              </li>
              <li>
                {formatTime(result.startTime)} – {formatTime(result.endTime)} ·{" "}
                {result.endTime <= result.startTime ? "ends after midnight · " : ""}
                getting around by {result.transport.toLowerCase()}
              </li>
              <li>Activities: {result.activities.join(", ")}</li>
              <li>
                Atmosphere: {result.atmosphere} · Distance: {result.distance.toLowerCase()}
                {result.restrictions.length ? ` · Food: ${result.restrictions.join(", ")}` : ""}
              </li>
            </ul>
            <div className="results-note">
              This is the form's confirmation — the real venue search and itinerary generation (with live places,
              budget tracking, and the edit chat) arrive in Phases 2–3.
            </div>
          </div>
        </section>
      ) : null}

      {generating ? <LoadingOverlay /> : null}
    </div>
  );
}
