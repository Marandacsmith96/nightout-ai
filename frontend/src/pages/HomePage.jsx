import { Link } from "react-router-dom";
import { Button } from "../components/kit.jsx";

const FEATURES = [
  {
    icon: "🎯",
    title: "Made for your group",
    text: "Size, budget, dietary needs, who wants what — the plan bends around everyone, not the other way around.",
  },
  {
    icon: "📍",
    title: "Real places only",
    text: "Restaurants, bars, and venues pulled from live location data — never invented, with honest price estimates.",
  },
  {
    icon: "💬",
    title: "Change it with chat",
    text: "\u201CMake dinner cheaper\u201D or \u201Cwe want to finish by 10\u201D — just say it, and the night updates around it.",
  },
];

const STEPS = [
  { n: "1", title: "Tell us about the night", text: "City, date, group size, budget, start & end time, and what you're into." },
  { n: "2", title: "AI builds the itinerary", text: "Real venues become a timed, walkable route with per-stop costs." },
  { n: "3", title: "Tweak it together", text: "Chat to swap stops, trim costs, or change the vibe. Lock what you love." },
];

export default function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="container">
          <div className="hero-badge">
            <span className="spark">✦</span> AI night-out planning · real places · made for your group
          </div>
          <h1>
            Less Planning. <span className="gradient">More Living.</span>
          </h1>
          <p className="hero-sub">
            Your perfect night out, planned in seconds. Tell us what you're looking for, and let AI handle the details.
          </p>
          <div className="hero-cta">
            <Link to="/planner">
              <Button size="lg" className="pulse">
                🌙 Plan My Night
              </Button>
            </Link>
            <a href="#how-it-works">
              <Button variant="ghost" size="lg">
                See how it works
              </Button>
            </a>
          </div>
          <p className="hero-notes">Dinner · drinks · live music · games · dancing — one budget, zero group-chat chaos</p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <h2 className="section-title">A night out, minus the <span className="gradient">spreadsheet energy</span></h2>
          <p className="section-sub">
            No more three-hour group texts comparing menus. Enter a few details and get a plan everyone can actually agree on.
          </p>
          <div className="features">
            {FEATURES.map((f, i) => (
              <div className="feature" key={f.title} style={{ animationDelay: `${i * 0.08}s` }}>
                <div className="feature-icon">{f.icon}</div>
                <h3>{f.title}</h3>
                <p>{f.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section" id="how-it-works">
        <div className="container">
          <h2 className="section-title">Three steps to a better night</h2>
          <p className="section-sub">The whole flow takes about a minute.</p>
          <div className="steps">
            {STEPS.map((s) => (
              <div className="step" key={s.n}>
                <div className="step-num">{s.n}</div>
                <div>
                  <h4>{s.title}</h4>
                  <p>{s.text}</p>
                </div>
              </div>
            ))}
          </div>
          <div style={{ textAlign: "center", marginTop: 40 }}>
            <Link to="/planner">
              <Button size="lg">Start planning &rarr;</Button>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
