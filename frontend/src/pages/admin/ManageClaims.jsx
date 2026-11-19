import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAdminClaims } from "../../services/adminService";
import Loader from "../../components/Loader";
import { formatDate, getErrorMessage, statusClasses, titleCase } from "../../utils/helpers";

const FILTERS = ["all", "pending", "approved", "rejected"];

export default function ManageClaims() {
  const [claims, setClaims] = useState([]);
  const [filter, setFilter] = useState("pending");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAdminClaims()
      .then((res) => setClaims(res.data.claims || []))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;

  const rows = claims.filter((c) => filter === "all" || c.status === filter);

  return (
    <main className="mx-auto max-w-6xl px-5 py-10">
      <h1 className="mb-6 text-3xl font-bold">Manage claims</h1>
      {error && <p className="mb-4 rounded bg-red-50 p-3 text-red-700">{error}</p>}

      <div className="mb-5 flex flex-wrap gap-2">
        {FILTERS.map((name) => (
          <button
            key={name}
            onClick={() => setFilter(name)}
            className={`rounded-full px-4 py-2 text-sm ${filter === name ? "bg-primary text-white" : "border bg-white"}`}
          >
            {titleCase(name)}
          </button>
        ))}
      </div>

      {rows.length === 0 ? (
        <p className="rounded-2xl border bg-white p-10 text-center text-slate-500">No claims.</p>
      ) : (
        <div className="space-y-3">
          {rows.map((c) => (
            <article key={c.id} className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border bg-white p-5">
              <div>
                <h2 className="font-bold">{c.item_title}</h2>
                <p className="text-sm text-slate-500">{c.claimant_name} · {c.claimant_email}</p>
                <p className="text-xs text-slate-400">{formatDate(c.created_at)}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClasses(c.status)}`}>
                  {titleCase(c.status)}
                </span>
                <Link to={`/admin/claims/${c.id}`} className="rounded-lg bg-primary px-4 py-2 text-sm text-white">
                  Review
                </Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
