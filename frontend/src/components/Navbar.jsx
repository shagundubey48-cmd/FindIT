import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import NotificationBell from "./NotificationBell";

// Links available to every signed-in user.
const userLinks = [
  ["/dashboard", "Dashboard"],
  ["/lost-items", "Lost Items"],
  ["/found-items", "Found Items"],
  ["/report-lost", "Report Lost"],
  ["/report-found", "Report Found"],
  ["/my-reports", "My Reports"],
  ["/matched-items", "Matched Items"],
  ["/my-claims", "My Claims"],
  ["/my-handovers", "My Handovers"],
  ["/messages", "Messages"],
  ["/feedback", "Feedback"],
];

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setOpen(false);
    navigate("/login");
  };

  const linkClass = ({ isActive }) =>
    `block whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium ${
      isActive
        ? "bg-indigo-50 text-indigo-700"
        : "text-slate-600 hover:bg-slate-100"
    }`;

  return (
    <header className="sticky top-0 z-40 border-b bg-white/95 backdrop-blur">
      <nav className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3">
        <Link to="/" className="shrink-0 text-2xl font-bold text-primary">
          FindIT.
        </Link>

        {/* Desktop navigation; scroll horizontally when the screen is narrow. */}
        <div className="hidden min-w-0 flex-1 items-center justify-start gap-1 overflow-x-auto lg:flex">
          {isAuthenticated &&
            userLinks.map(([to, label]) => (
              <NavLink key={to} to={to} className={linkClass}>
                {label}
              </NavLink>
            ))}
          {isAuthenticated && user?.is_admin && (
            <NavLink to="/admin" className={linkClass}>
              Admin Dashboard
            </NavLink>
          )}
        </div>

        <div className="hidden shrink-0 items-center gap-3 lg:flex">
          {isAuthenticated ? (
            <>
              <NotificationBell />
              <Link
                to="/profile"
                className="text-sm font-medium text-slate-700 hover:text-primary"
              >
                {user?.name || "Profile"}
              </Link>
              <button
                onClick={handleLogout}
                className="rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="rounded-lg px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
              >
                Register
              </Link>
            </>
          )}
        </div>

        {/* Mobile menu toggle */}
        <button
          className="rounded-lg p-2 text-slate-700 hover:bg-slate-100 lg:hidden"
          onClick={() => setOpen((value) => !value)}
          aria-label="Toggle menu"
          aria-expanded={open}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {/* Mobile navigation */}
      {open && (
        <div
          className="space-y-1 border-t bg-white px-4 py-3 lg:hidden"
          onClick={() => setOpen(false)}
        >
          {isAuthenticated ? (
            <>
              {userLinks.map(([to, label]) => (
                <NavLink key={to} to={to} className={linkClass}>
                  {label}
                </NavLink>
              ))}
              <NavLink to="/notifications" className={linkClass}>
                Notifications
              </NavLink>
              <NavLink to="/profile" className={linkClass}>
                Profile
              </NavLink>
              {user?.is_admin && (
                <NavLink to="/admin" className={linkClass}>
                  Admin Dashboard
                </NavLink>
              )}
              <button
                onClick={handleLogout}
                className="block w-full rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={linkClass}>
                Login
              </NavLink>
              <NavLink to="/register" className={linkClass}>
                Register
              </NavLink>
            </>
          )}
        </div>
      )}
    </header>
  );
}
