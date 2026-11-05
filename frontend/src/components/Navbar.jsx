import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="nav">
      <div className="container nav-inner">
        <Link to="/" className="brand">
          <span className="brand-dot" aria-hidden="true" />
          NightOut AI
        </Link>
        <div className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/planner">Plan My Night</Link>
        </div>
      </div>
    </nav>
  );
}
