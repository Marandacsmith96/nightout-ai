import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import HomePage from "./pages/HomePage.jsx";
import PlannerPage from "./pages/PlannerPage.jsx";

export default function App() {
  return (
    <>
      <Navbar />
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
