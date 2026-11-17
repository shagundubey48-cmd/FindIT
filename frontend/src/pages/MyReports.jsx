
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import itemService from "../services/itemService";

export default function MyReports() {
  const { user } = useAuth();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchMyReports = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const data = await itemService.getItems();

      const myItems = (data.items || []).filter(
        (item) => Number(item.user_id) === Number(user?.id)
      );

      setItems(myItems);
    } catch (err) {
      setError(
        err.response?.data?.message || "Unable to load your reports."
      );
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchMyReports();
  }, [fetchMyReports]);

  async function handleWithdraw(itemId) {
    const confirmed = window.confirm(
      "Are you sure you want to withdraw this report?"
    );

    if (!confirmed) return;

    try {
      await itemService.withdrawItem(itemId);
      setItems((previous) =>
        previous.filter((item) => item.id !== itemId)
      );
    } catch (err) {
      alert(
        err.response?.data?.message || "Unable to withdraw this report."
      );
    }
  }

  if (loading) {
    return <p className="py-16 text-center">Loading your reports...</p>;
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="mb-2 text-3xl font-bold text-gray-900">
        My Reports
      </h1>

      <p className="mb-8 text-gray-600">
        Manage your active lost and found reports.
      </p>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {items.length === 0 ? (
        <div className="rounded-xl border border-gray-200 bg-white p-10 text-center">
          <p className="text-gray-600">You have no active reports.</p>
          <div className="mt-5 flex justify-center gap-3">
            <Link
              to="/report-lost"
              className="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
            >
              Report Lost Item
            </Link>
            <Link
              to="/report-found"
              className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700"
            >
              Report Found Item
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex flex-col justify-between gap-4 rounded-xl border border-gray-200 bg-white p-5 sm:flex-row sm:items-center"
            >
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-semibold">{item.title}</h2>
                  <span className="rounded-full bg-gray-100 px-2 py-1 text-xs capitalize">
                    {item.item_type}
                  </span>
                </div>

                <p className="mt-1 text-sm text-gray-500">
                  {item.category} · {item.campus} · {item.item_date}
                </p>

                <p className="mt-1 text-sm text-gray-500">
                  Status: {item.status}
                </p>
              </div>

              <div className="flex gap-3">
                <Link
                  to={`/items/${item.id}`}
                  className="rounded-lg border border-indigo-600 px-4 py-2 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
                >
                  View
                </Link>

                <button
                  onClick={() => handleWithdraw(item.id)}
                  className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
                >
                  Withdraw
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
