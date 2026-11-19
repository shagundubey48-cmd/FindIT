import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAdminDashboard } from "../../services/adminService";
import Loader from "../../components/Loader";
import { getErrorMessage, titleCase } from "../../utils/helpers";

const links = [
  ["/admin/claims", "Manage claims"],
  ["/admin/items", "Manage items"],
  ["/admin/users", "Manage users"],
  ["/admin/unclaimed", "Unclaimed items"],
  ["/admin/statistics", "Statistics"],
];

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAdminDashboard()
      .then((res) => setData(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;

  return (
    <main className="mx-auto max-w-6xl px-5 py-10">
      <h1 className="mb-6 text-3xl font-bold">Admin dashboard</h1>
      {error && <p className="mb-4 rounded bg-red-50 p-3 text-red-700">{error}</p>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Object.entries(data || {}).map(([key, value]) => (
          <div key={key} className="rounded-2xl border bg-white p-5">
            <p className="text-sm text-slate-500">{titleCase(key)}</p>
            <p className="mt-2 text-3xl font-bold">{String(value)}</p>
          </div>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        {links.map(([to, label]) => (
          <Link key={to} to={to} className="rounded-xl border bg-white px-5 py-3 font-medium text-primary hover:border-indigo-400">
            {label}
          </Link>
        ))}
      </div>
    </main>
  );
}
