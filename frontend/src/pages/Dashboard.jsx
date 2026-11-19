import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useNotifications } from "../hooks/useNotifications";
import Loader from "../components/Loader";
import { getErrorMessage } from "../utils/helpers";

const quickLinks = [
  ["/report-lost", "Report a lost item"],
  ["/report-found", "Report a found item"],
  ["/my-reports", "My reports"],
  ["/matched-items", "Matched items"],
  ["/my-claims", "My claims"],
  ["/my-handovers", "My handovers"],
  ["/messages", "Messages"],
  ["/feedback", "Feedback"],
];

export default function Dashboard() {
  const { user } = useAuth();
  const { unreadCount } = useNotifications();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get("/statistics/summary");
        setStats(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const cards = stats
    ? [
        ["Lost reports", stats.total_lost_reports],
        ["Found reports", stats.total_found_reports],
        ["Items recovered", stats.items_recovered],
        ["Recovery rate", `${stats.recovery_rate}%`],
        ["Active items", stats.active_items],
      ]
    : [];

  return (
    <main className="mx-auto max-w-6xl px-5 py-10">
      <h1 className="text-3xl font-bold">
        Welcome{user?.name ? `, ${user.name}` : ""}
      </h1>
      <p className="mt-2 text-slate-500">
        You have {unreadCount} unread notification{unreadCount === 1 ? "" : "s"}.{" "}
        <Link to="/notifications" className="text-primary">View</Link>
      </p>

      {error && (
        <p className="mt-6 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>
      )}

      {loading ? (
        <Loader />
      ) : (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {cards.map(([label, value]) => (
            <div key={label} className="rounded-2xl border bg-white p-5">
              <p className="text-sm text-slate-500">{label}</p>
              <p className="mt-2 text-3xl font-bold">{value}</p>
            </div>
          ))}
        </div>
      )}

      <h2 className="mb-4 mt-10 text-xl font-bold">Quick actions</h2>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {quickLinks.map(([to, label]) => (
          <Link
            key={to}
            to={to}
            className="rounded-xl border bg-white p-4 text-center font-medium text-slate-700 hover:border-indigo-400 hover:text-primary"
          >
            {label}
          </Link>
        ))}
      </div>
    </main>
  );
}
