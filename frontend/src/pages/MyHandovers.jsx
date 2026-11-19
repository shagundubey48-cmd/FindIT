import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getMyHandovers } from "../services/handoverService";
import Loader from "../components/Loader";
import { formatDateTime, getErrorMessage } from "../utils/helpers";

export default function MyHandovers() {
  const { user } = useAuth();
  const [handovers, setHandovers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await getMyHandovers();
        setHandovers(data.handovers || []);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  return (
    <main className="mx-auto max-w-4xl px-5 py-10">
      <h1 className="text-3xl font-bold">My handovers</h1>
      <p className="mt-2 text-slate-500">Items handed back to their owners.</p>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

      {loading ? (
        <Loader />
      ) : handovers.length === 0 ? (
        <div className="mt-6 rounded-2xl border bg-white p-10 text-center text-slate-500">
          No handovers yet.
        </div>
      ) : (
        <div className="mt-6 space-y-4">
          {handovers.map((h) => (
            <article key={h.id} className="rounded-2xl border bg-white p-5">
              <h2 className="font-bold">{h.item_title}</h2>
              <p className="mt-1 text-sm text-slate-500">
                Handed over {formatDateTime(h.handed_over_at)} by {h.administrator_name}
              </p>
              {h.handover_notes && <p className="mt-2 text-sm">{h.handover_notes}</p>}
              <div className="mt-3 flex gap-4 text-sm">
                <Link to={`/items/${h.item_id}`} className="text-primary">View item</Link>
                {h.received_by === user?.id && (
                  <Link to="/feedback" className="text-primary">Give feedback</Link>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
