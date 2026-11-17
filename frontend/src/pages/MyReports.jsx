
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import itemService from "../services/itemService";
import { useAuth } from "../context/AuthContext";

export default function MyReports() {
  const { user } = useAuth();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError("");

      const data = await itemService.getItems();

      const myItems = (data.items || []).filter(
        (item) => String(item.user_id) === String(user?.id)
      );

      setItems(myItems);
    } catch (err) {
      setError(
        err.response?.data?.message ||
        "Unable to load your reports."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id) {
      fetchReports();
    } else {
      setLoading(false);
    }
  }, [user?.id]);

  const handleWithdraw = async (itemId) => {
    const confirmed = window.confirm(
      "Are you sure you want to withdraw this report?"
    );

    if (!confirmed) return;

    try {
      await itemService.withdrawItem(itemId);

      setMessage("Report withdrawn successfully.");

      fetchReports();
    } catch (err) {
      setError(
        err.response?.data?.message ||
        "Unable to withdraw report."
      );
    }
  };

  return (
    <div className="min-h-screen bg-background py-10 px-5">

      <div className="max-w-6xl mx-auto">

        <div className="flex justify-between items-center flex-wrap gap-4 mb-8">

          <div>
            <h1 className="text-3xl font-bold">
              My Reports
            </h1>

            <p className="text-gray-500 mt-2">
              Manage your lost and found reports.
            </p>
          </div>

          <div className="flex gap-3">

            <Link
              to="/report-lost"
              className="bg-primary text-white px-4 py-3 rounded-lg"
            >
              Report Lost
            </Link>

            <Link
              to="/report-found"
              className="bg-green-600 text-white px-4 py-3 rounded-lg"
            >
              Report Found
            </Link>

          </div>

        </div>

        {message && (
          <p className="bg-green-50 text-green-700 p-3 rounded-lg mb-5">
            {message}
          </p>
        )}

        {error && (
          <p className="bg-red-50 text-red-600 p-3 rounded-lg mb-5">
            {error}
          </p>
        )}

        {loading ? (
          <p className="text-center py-16">
            Loading your reports...
          </p>
        ) : items.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 text-center">

            <h2 className="text-xl font-bold">
              No Reports Yet
            </h2>

            <p className="text-gray-500 mt-2">
              Your reported items will appear here.
            </p>

          </div>
        ) : (
          <div className="bg-white rounded-2xl overflow-hidden shadow-sm">

            <div className="overflow-x-auto">

              <table className="w-full text-left">

                <thead className="bg-gray-50">
                  <tr>
                    <th className="p-4">Item</th>
                    <th className="p-4">Type</th>
                    <th className="p-4">Date</th>
                    <th className="p-4">Status</th>
                    <th className="p-4">Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {items.map((item) => (
                    <tr key={item.id} className="border-t">

                      <td className="p-4 font-medium">
                        {item.title}
                      </td>

                      <td className="p-4 capitalize">
                        {item.item_type}
                      </td>

                      <td className="p-4">
                        {item.item_date}
                      </td>

                      <td className="p-4">
                        <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-xs">
                          {item.status}
                        </span>
                      </td>

                      <td className="p-4">
                        <div className="flex gap-3">

                          <Link
                            to={`/items/${item.id}`}
                            className="text-primary font-medium"
                          >
                            View
                          </Link>

                          <button
                            onClick={() => handleWithdraw(item.id)}
                            className="text-red-500 font-medium"
                          >
                            Withdraw
                          </button>

                        </div>
                      </td>

                    </tr>
                  ))}
                </tbody>

              </table>

            </div>
          </div>
        )}

      </div>
    </div>
  );
}

