import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate("/login");
  };

  const closeMenu = () => setMenuOpen(false);

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand" onClick={closeMenu}>
        Job Portal
      </Link>

      <button
        className="navbar-mobile-toggle"
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label="Toggle navigation"
      >
        {menuOpen ? "\u2715" : "\u2630"}
      </button>

      <div className={`navbar-links${menuOpen ? " open" : ""}`}>
        <Link to="/jobs" onClick={closeMenu}>Jobs</Link>
        {user ? (
          <>
            <Link to="/dashboard" onClick={closeMenu}>Dashboard</Link>
            {user.role === "candidate" && (
              <Link to="/my-applications" onClick={closeMenu}>My Applications</Link>
            )}
            {user.role === "recruiter" && (
              <>
                <Link to="/recruiter-dashboard" onClick={closeMenu}>My Jobs</Link>
                <Link to="/company" onClick={closeMenu}>Company</Link>
              </>
            )}
            <span className="navbar-user">{user.email}</span>
            <button onClick={handleLogout}>Sign out</button>
          </>
        ) : (
          <>
            <Link to="/login" onClick={closeMenu}>Sign in</Link>
            <Link to="/register" onClick={closeMenu} className="navbar-cta">Get started</Link>
          </>
        )}
      </div>
    </nav>
  );
}
