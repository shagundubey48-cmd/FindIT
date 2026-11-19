import { useEffect, useState } from "react";
import { getAdminStatistics } from "../../services/adminService";
import Loader from "../../components/Loader";
import { getErrorMessage } from "../../utils/helpers";

function Stat({ label, value }) {
  return (
    <div className="rounded-2xl border bg-white p-5">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold">{value ?? "—"}</p>
    </div>
  );
}

export default function AdminStatistics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAdminStatistics()
      .then((res) => setData(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;

  return (
    <main className="mx-auto max-w-6xl px-5 py-10">
      <h1 className="mb-6 text-3xl font-bold">Statistics</h1>
      {error && <p className="mb-4 rounded bg-red-50 p-3 text-red-700">{error}</p>}

      {data && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Stat label="Lost reports" value={data.total_lost_reports} />
            <Stat label="Found reports" value={data.total_found_reports} />
            <Stat label="Items recovered" value={data.items_recovered} />
            <Stat label="Recovery rate" value={`${data.recovery_rate}%`} />
            <Stat label="Active items" value={data.active_items} />
            <Stat
              label="Avg. recovery time"
              value={data.average_recovery_days != null ? `${data.average_recovery_days} days` : null}
            />
            <Stat label="Claims approval rate" value={`${data.claims?.approval_rate ?? 0}%`} />
            <Stat
              label="Avg. feedback rating"
              value={data.feedback?.average_rating != null ? `${data.feedback.average_rating} / 5` : null}
            />
          </div>

          <h2 className="mb-3 mt-10 text-xl font-bold">Claims</h2>
          <div className="grid gap-4 sm:grid-cols-4">
            <Stat label="Total" value={data.claims?.total} />
            <Stat label="Pending" value={data.claims?.pending} />
            <Stat label="Approved" value={data.claims?.approved} />
            <Stat label="Rejected" value={data.claims?.rejected} />
          </div>

          <h2 className="mb-3 mt-10 text-xl font-bold">By category</h2>
          <div className="overflow-x-auto rounded-2xl border bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-3">Category</th>
                  <th className="p-3">Found</th>
                  <th className="p-3">Recovered</th>
                  <th className="p-3">Rate</th>
                </tr>
              </thead>
              <tbody>
                {(data.by_category || []).map((row) => (
                  <tr key={row.category} className="border-t">
                    <td className="p-3">{row.category}</td>
                    <td className="p-3">{row.found}</td>
                    <td className="p-3">{row.recovered}</td>
                    <td className="p-3">{row.recovery_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <h2 className="mb-3 mt-10 text-xl font-bold">Monthly trend</h2>
          <div className="overflow-x-auto rounded-2xl border bg-white">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-3">Month</th>
                  <th className="p-3">Reports</th>
                  <th className="p-3">Recoveries</th>
                </tr>
              </thead>
              <tbody>
                {(data.monthly_trend || []).map((row) => (
                  <tr key={row.month} className="border-t">
                    <td className="p-3">{row.month}</td>
                    <td className="p-3">{row.reports}</td>
                    <td className="p-3">{row.recoveries}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </main>
  );
}
