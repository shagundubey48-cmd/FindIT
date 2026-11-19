import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyClaims } from "../services/claimService";
import Loader from "../components/Loader";
import { formatDate, getErrorMessage, statusClasses, titleCase } from "../utils/helpers";

export default function MyClaims() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await getMyClaims();
        setClaims(data.claims || []);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  return (
    <main className="mx-auto max-w-5xl px-5 py-10">
      <h1 className="text-3xl font-bold">My claims</h1>
      <p className="mt-2 text-slate-500">Ownership claims you have submitted.</p>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

      {loading ? (
        <Loader />
      ) : claims.length === 0 ? (
        <div className="mt-6 rounded-2xl border bg-white p-10 text-center text-slate-500">
          You have not claimed any items yet.{" "}
          <Link to="/found-items" className="text-primary">Browse found items</Link>
        </div>
      ) : (
        <div className="mt-6 space-y-4">
          {claims.map((claim) => (
            <article key={claim.id} className="rounded-2xl border bg-white p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="font-bold">{claim.item_title}</h2>
                  <p className="text-xs text-slate-400">Submitted {formatDate(claim.created_at)}</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClasses(claim.status)}`}>
                  {titleCase(claim.status)}
                </span>
              </div>
              {claim.admin_remarks && (
                <p className="mt-3 text-sm text-slate-600">
                  <span className="font-medium">Admin remarks:</span> {claim.admin_remarks}
                </p>
              )}
              <Link to={`/claims/${claim.id}`} className="mt-4 inline-block text-sm font-medium text-primary">
                View details →
              </Link>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
