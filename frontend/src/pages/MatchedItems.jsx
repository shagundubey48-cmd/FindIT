import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import itemService from "../services/itemService";
import { getCombinedMatches } from "../services/matchingService";
import Loader from "../components/Loader";
import { getErrorMessage, titleCase } from "../utils/helpers";

export default function MatchedItems() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedId = searchParams.get("item") || "";

  const [myItems, setMyItems] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loadingItems, setLoadingItems] = useState(true);
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [error, setError] = useState("");

  // The user's own active reports (the items we can find matches for).
  useEffect(() => {
    const load = async () => {
      try {
        const data = await itemService.getItems();
        setMyItems(
          (data.items || []).filter((item) => item.user_id === user?.id)
        );
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoadingItems(false);
      }
    };

    if (user?.id) load();
    else setLoadingItems(false);
  }, [user?.id]);

  useEffect(() => {
    if (!selectedId) {
      setMatches([]);
      return;
    }

    const load = async () => {
      try {
        setLoadingMatches(true);
        setError("");
        const { data } = await getCombinedMatches(selectedId);
        setMatches(data.matches || []);
      } catch (err) {
        setMatches([]);
        setError(getErrorMessage(err));
      } finally {
        setLoadingMatches(false);
      }
    };

    load();
  }, [selectedId]);

  if (loadingItems) return <Loader />;

  return (
    <main className="mx-auto max-w-5xl px-5 py-10">
      <h1 className="text-3xl font-bold">Matched items</h1>
      <p className="mt-2 text-slate-500">
        Pick one of your reports to see possible matches.
      </p>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

      {myItems.length === 0 ? (
        <div className="mt-6 rounded-2xl border bg-white p-10 text-center text-slate-500">
          You have no active reports.{" "}
          <Link to="/report-lost" className="text-primary">Report an item</Link>
        </div>
      ) : (
        <select
          value={selectedId}
          onChange={(e) => setSearchParams(e.target.value ? { item: e.target.value } : {})}
          className="mt-6 w-full rounded-lg border bg-white px-4 py-3"
        >
          <option value="">Select one of your reports</option>
          {myItems.map((item) => (
            <option key={item.id} value={item.id}>
              {titleCase(item.item_type)} — {item.title}
            </option>
          ))}
        </select>
      )}

      {loadingMatches ? (
        <Loader text="Looking for matches..." />
      ) : selectedId && matches.length === 0 && !error ? (
        <p className="mt-6 text-center text-slate-500">No matches found yet.</p>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {matches.map((m) => (
            <article key={m.id} className="rounded-2xl border bg-white p-5">
              {m.image_url && (
                <img src={m.image_url} alt={m.title} className="mb-3 h-40 w-full rounded-xl object-cover" />
              )}
              <div className="flex items-start justify-between gap-2">
                <h2 className="font-bold">{m.title}</h2>
                <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
                  {m.match_score}% match
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-500">{m.location}, {m.campus}</p>
              <p className="mt-2 text-xs text-slate-400">
                {titleCase(m.match_type)} · text {m.text_score}
                {m.image_score != null ? ` · image ${m.image_score}` : ""}
              </p>
              <Link to={`/items/${m.id}`} className="mt-3 inline-block text-sm font-medium text-primary">
                View item →
              </Link>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
