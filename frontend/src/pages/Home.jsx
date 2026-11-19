import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Search, PackageSearch, ShieldCheck, Bell } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import itemService from "../services/itemService";
import ItemCard from "../components/ItemCard";
import Loader from "../components/Loader";
import { getErrorMessage } from "../utils/helpers";

const steps = [
  {
    icon: PackageSearch,
    title: "Report",
    text: "Post what you lost or found, with a photo and where it happened.",
  },
  {
    icon: Bell,
    title: "Get matched",
    text: "FindIT compares reports by text and image and notifies both sides.",
  },
  {
    icon: ShieldCheck,
    title: "Claim safely",
    text: "Owners prove ownership and admins hand the item over with a QR code.",
  },
];

export default function Home() {
  const { isAuthenticated } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // The items API needs a login, so recent items are shown to signed-in users only.
  useEffect(() => {
    if (!isAuthenticated) return;

    const load = async () => {
      try {
        setLoading(true);
        setError("");
        const data = await itemService.getItems();
        setItems((data.items || []).slice(0, 6));
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [isAuthenticated]);

  return (
    <main>
      <section className="bg-gradient-to-br from-indigo-600 to-violet-600 px-5 py-20 text-center text-white">
        <h1 className="mx-auto max-w-3xl text-4xl font-bold md:text-5xl">
          Lost something on campus? Found something?
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-indigo-100">
          FindIT connects students to reunite lost belongings with their owners.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          {isAuthenticated ? (
            <>
              <Link
                to="/report-lost"
                className="rounded-xl bg-white px-6 py-3 font-semibold text-indigo-700"
              >
                Report lost item
              </Link>
              <Link
                to="/report-found"
                className="rounded-xl border border-white px-6 py-3 font-semibold"
              >
                Report found item
              </Link>
            </>
          ) : (
            <>
              <Link
                to="/register"
                className="rounded-xl bg-white px-6 py-3 font-semibold text-indigo-700"
              >
                Get started
              </Link>
              <Link
                to="/login"
                className="rounded-xl border border-white px-6 py-3 font-semibold"
              >
                Login
              </Link>
            </>
          )}
        </div>
      </section>

      <section className="mx-auto grid max-w-5xl gap-6 px-5 py-14 md:grid-cols-3">
        {steps.map(({ icon: Icon, title, text }) => (
          <div key={title} className="rounded-2xl border bg-white p-6 text-center">
            <Icon className="mx-auto text-primary" size={32} />
            <h2 className="mt-4 text-lg font-bold">{title}</h2>
            <p className="mt-2 text-sm text-slate-500">{text}</p>
          </div>
        ))}
      </section>

      {isAuthenticated && (
        <section className="mx-auto max-w-7xl px-5 pb-14">
          <div className="mb-6 flex items-center justify-between">
            <h2 className="text-2xl font-bold">Recent reports</h2>
            <Link to="/found-items" className="flex items-center gap-1 text-primary">
              <Search size={16} /> Browse all
            </Link>
          </div>

          {loading ? (
            <Loader />
          ) : error ? (
            <p className="rounded-lg bg-red-50 p-3 text-red-600">{error}</p>
          ) : items.length === 0 ? (
            <p className="text-slate-500">No reports yet.</p>
          ) : (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </section>
      )}
    </main>
  );
}
