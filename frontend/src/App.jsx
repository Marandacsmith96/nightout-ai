import { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";
import PlannerPage from "./pages/PlannerPage.jsx";
import { api } from "./api/client.js";

export default function App() {
  const [demoMode, setDemoMode] = useState(null); // null = unknown yet

  useEffect(() => {
    api
      .health()
      .then((h) => setDemoMode(Boolean(h.demo_mode)))
      .catch(() => setDemoMode(false)); // backend offline: no banner, app still usable
  }, []);

  return (
    <>
      <Navbar />
      {demoMode === true && (
        <div className="demo-banner" role="note">
          🧪 Demo mode — showing clearly-labeled sample places. Add Google Places API keys for live venue results.
        </div>
      )}
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/planner" element={<PlannerPage />} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="container footer-inner">
          <span>NightOut AI — planning and recommendations only. No bookings, no payments.</span>
          <span>Price estimates may exclude taxes &amp; tips.</span>
        </div>
      </footer>
    </>
  );
}
