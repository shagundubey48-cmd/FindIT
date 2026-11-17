
import { Link, Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";

import LostItems from "./pages/LostItems";
import FoundItems from "./pages/FoundItems";
import ReportLost from "./pages/ReportLost";
import ReportFound from "./pages/ReportFound";
import ItemDetails from "./pages/ItemDetails";
import MyReports from "./pages/MyReports";

function ProtectedRoute() {
  const { user, loading } = useAuth();

  if (loading) {
    return <p className="py-16 text-center">Loading...</p>;
  }

  return user ? <Outlet /> : <Navigate to="/login" replace />;
}

function GuestRoute() {
  const { user, loading } = useAuth();

  if (loading) {
    return <p className="py-16 text-center">Loading...</p>;
  }

  return user ? <Navigate to="/" replace /> : <Outlet />;
}

function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4">
        <Link to="/" className="text-2xl font-bold text-indigo-600">
          FindIT
        </Link>

        <div className="flex flex-wrap items-center gap-4 text-sm font-medium">
          <Link to="/lost-items" className="text-gray-700 hover:text-indigo-600">
            Lost Items
          </Link>

          <Link to="/found-items" className="text-gray-700 hover:text-indigo-600">
            Found Items
          </Link>

          {user ? (
            <>
              <Link to="/report-lost" className="text-gray-700 hover:text-indigo-600">
                Report Lost
              </Link>

              <Link to="/report-found" className="text-gray-700 hover:text-indigo-600">
                Report Found
              </Link>

              <Link to="/my-reports" className="text-gray-700 hover:text-indigo-600">
                My Reports
              </Link>

              <button
                onClick={logout}
                className="rounded-lg bg-gray-100 px-4 py-2 text-gray-700 hover:bg-gray-200"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-indigo-600">
                Login
              </Link>

              <Link
                to="/register"
                className="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

function Home() {
  return (
    <div className="bg-gray-50">
      <section className="mx-auto max-w-7xl px-4 py-24 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          Lost Something?
          <span className="block text-indigo-600">Find It with FindIT.</span>
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
          A campus lost and found platform that helps students report,
          discover and recover misplaced belongings.
        </p>

        <div className="mt-10 flex flex-wrap justify-center gap-4">
          <Link
            to="/lost-items"
            className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white hover:bg-indigo-700"
          >
            Browse Lost Items
          </Link>

          <Link
            to="/found-items"
            className="rounded-lg border border-indigo-600 px-6 py-3 font-semibold text-indigo-600 hover:bg-indigo-50"
          >
            Browse Found Items
          </Link>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-6 px-4 pb-20 md:grid-cols-3">
        <div className="rounded-xl bg-white p-7 shadow-sm">
          <h2 className="text-xl font-semibold">Report Lost Items</h2>
          <p className="mt-3 text-gray-600">
            Add details about belongings you have misplaced on campus.
          </p>
        </div>

        <div className="rounded-xl bg-white p-7 shadow-sm">
          <h2 className="text-xl font-semibold">Report Found Items</h2>
          <p className="mt-3 text-gray-600">
            Help fellow students by reporting items you have found.
          </p>
        </div>

        <div className="rounded-xl bg-white p-7 shadow-sm">
          <h2 className="text-xl font-semibold">Find Possible Matches</h2>
          <p className="mt-3 text-gray-600">
            Explore item reports and check possible text-based matches.
          </p>
        </div>
      </section>
    </div>
  );
}

function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white py-6 text-center text-sm text-gray-500">
      © {new Date().getFullYear()} FindIT — Campus Lost and Found
    </footer>
  );
}

function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />

        <Route element={<GuestRoute />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        <Route path="/verify-email" element={<VerifyEmail />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/lost-items" element={<LostItems />} />
          <Route path="/found-items" element={<FoundItems />} />
          <Route path="/items/:id" element={<ItemDetails />} />
          <Route path="/report-lost" element={<ReportLost />} />
          <Route path="/report-found" element={<ReportFound />} />
          <Route path="/my-reports" element={<MyReports />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
