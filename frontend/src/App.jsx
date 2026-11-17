
import { Routes, Route, Navigate, Link, Outlet } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";

import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";

function Home() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className="min-h-screen bg-background">

      <nav className="flex items-center justify-between px-6 md:px-12 py-5 bg-white shadow-sm">

        <Link to="/" className="text-2xl font-bold text-primary">
          FindIT.
        </Link>

        <div className="flex gap-5 items-center">

          <a href="#about" className="hover:text-primary hidden sm:block">
            About
          </a>

          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="text-primary font-semibold">
                Dashboard
              </Link>

              <button
                onClick={logout}
                className="bg-red-500 text-white px-5 py-2 rounded-lg"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-primary">
                Login
              </Link>

              <Link
                to="/register"
                className="bg-primary text-white px-5 py-2 rounded-lg"
              >
                Get Started
              </Link>
            </>
          )}

        </div>
      </nav>

      <section className="max-w-6xl mx-auto px-6 py-24 text-center">

        <p className="text-primary font-semibold mb-4">
          AI POWERED CAMPUS LOST & FOUND
        </p>

        <h1 className="text-4xl md:text-6xl font-bold text-dark leading-tight">
          Lost Something?
          <br />
          <span className="text-primary">
            Let's Find It Together.
          </span>
        </h1>

        <p className="text-gray-500 mt-6 max-w-2xl mx-auto">
          FindIT helps students report lost and found belongings
          and intelligently match items using AI.
        </p>

        <div className="flex flex-wrap justify-center gap-4 mt-8">

          <Link
            to={isAuthenticated ? "/dashboard" : "/login"}
            className="bg-primary text-white px-7 py-3 rounded-xl"
          >
            Report Lost Item
          </Link>

          <Link
            to="/found-items"
            className="border border-primary text-primary px-7 py-3 rounded-xl"
          >
            Explore Found Items
          </Link>

        </div>
      </section>

      <section id="about" className="bg-white py-16 px-6">

        <h2 className="text-3xl font-bold text-center mb-10">
          How FindIT Works
        </h2>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">

          {[
            ["01", "Report an Item", "Report your lost or found belongings."],
            ["02", "AI Matching", "Find similar items through intelligent matching."],
            ["03", "Get It Back", "Verify ownership and arrange a handover."]
          ].map(([number, title, description]) => (
            <div key={number} className="p-8 rounded-2xl bg-background">
              <span className="text-primary text-3xl font-bold">
                {number}
              </span>

              <h3 className="text-xl font-bold mt-4">
                {title}
              </h3>

              <p className="text-gray-500 mt-2">
                {description}
              </p>
            </div>
          ))}

        </div>
      </section>

      <footer className="text-center py-8 text-gray-500">
        © 2026 FindIT. Campus Lost & Found Platform.
      </footer>

    </div>
  );
}

function Dashboard() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen p-8 bg-background">

      <h1 className="text-3xl font-bold">
        Welcome, {user?.name || "Student"}!
      </h1>

      <p className="text-gray-500 mt-3">
        Your FindIT dashboard is ready.
      </p>

      <div className="grid md:grid-cols-2 gap-5 mt-10">

        <Link
          to="/report-lost"
          className="bg-white p-7 rounded-xl shadow-sm hover:shadow-md"
        >
          <h2 className="text-xl font-bold text-primary">
            Report Lost Item
          </h2>
          <p className="text-gray-500 mt-2">
            Report something you have lost.
          </p>
        </Link>

        <Link
          to="/found-items"
          className="bg-white p-7 rounded-xl shadow-sm hover:shadow-md"
        >
          <h2 className="text-xl font-bold text-primary">
            Browse Found Items
          </h2>
          <p className="text-gray-500 mt-2">
            Search for your missing belongings.
          </p>
        </Link>

      </div>

    </div>
  );
}

function Placeholder({ title }) {
  return (
    <div className="min-h-screen flex flex-col gap-4 items-center justify-center">
      <h1 className="text-3xl font-bold">{title}</h1>
      <Link to="/" className="text-primary">
        Back to Home
      </Link>
    </div>
  );
}

function GuestRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="p-10 text-center">Loading...</div>;
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Outlet />;
}

export default function App() {
  return (
    <Routes>

      <Route path="/" element={<Home />} />

      <Route element={<GuestRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      <Route path="/verify/:token" element={<VerifyEmail />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/report-lost" element={<Placeholder title="Report Lost Item" />} />
      </Route>

      <Route path="/found-items" element={<Placeholder title="Found Items" />} />

      <Route path="*" element={<Placeholder title="404 - Page Not Found" />} />

    </Routes>
  );
}
