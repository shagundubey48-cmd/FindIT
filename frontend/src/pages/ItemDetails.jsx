
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { MapPin, CalendarDays, Tag, ArrowLeft } from "lucide-react";
import itemService from "../services/itemService";

export default function ItemDetails() {
  const { id } = useParams();

  const [item, setItem] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadItem() {
      try {
        setLoading(true);
        setError("");

        const itemData = await itemService.getItemById(id);
        setItem(itemData);

        try {
          const matchData = await itemService.getMatches(id);
          setMatches(matchData.matches || []);
        } catch {
          setMatches([]);
        }
      } catch (err) {
        setError(
          err.response?.data?.message || "Unable to load item details."
        );
      } finally {
        setLoading(false);
      }
    }

    loadItem();
  }, [id]);

  if (loading) {
    return <p className="py-16 text-center">Loading item details...</p>;
  }

  if (error || !item) {
    return (
      <div className="px-4 py-16 text-center">
        <p className="mb-4 text-red-600">{error || "Item not found."}</p>
        <Link to="/lost-items" className="text-indigo-600 hover:underline">
          Back to items
        </Link>
      </div>
    );
  }

  const isLost = item.item_type === "lost";

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <Link
        to={isLost ? "/lost-items" : "/found-items"}
        className="mb-6 inline-flex items-center gap-2 text-indigo-600 hover:underline"
      >
        <ArrowLeft size={18} />
        Back to items
      </Link>

      <div className="grid gap-8 md:grid-cols-2">
        <div className="overflow-hidden rounded-xl bg-gray-100">
          {item.image_url ? (
            <img
              src={item.image_url}
              alt={item.title}
              className="h-80 w-full object-cover"
            />
          ) : (
            <div className="flex h-80 items-center justify-center text-gray-400">
              No image available
            </div>
          )}
        </div>

        <div>
          <span
            className={`inline-block rounded-full px-3 py-1 text-sm font-semibold ${
              isLost
                ? "bg-red-100 text-red-700"
                : "bg-green-100 text-green-700"
            }`}
          >
            {isLost ? "Lost Item" : "Found Item"}
          </span>

          <h1 className="mt-4 text-3xl font-bold text-gray-900">
            {item.title}
          </h1>

          <p className="mt-4 leading-7 text-gray-600">
            {item.description}
          </p>

          <div className="mt-6 space-y-4 text-gray-700">
            <div className="flex items-center gap-3">
              <Tag className="text-indigo-600" />
              <span>{item.category}</span>
            </div>

            <div className="flex items-center gap-3">
              <MapPin className="text-indigo-600" />
              <span>{item.location}, {item.campus}</span>
            </div>

            <div className="flex items-center gap-3">
              <CalendarDays className="text-indigo-600" />
              <span>{item.item_date}</span>
            </div>
          </div>

          <p className="mt-6 text-sm text-gray-500">
            Report ID: {item.id}
          </p>
        </div>
      </div>

      {matches.length > 0 && (
        <section className="mt-12">
          <h2 className="mb-5 text-2xl font-bold">
            Possible Matches
          </h2>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {matches.map((match) => (
              <div
                key={match.item.id}
                className="rounded-xl border border-gray-200 p-4"
              >
                <h3 className="font-semibold">{match.item.title}</h3>
                <p className="mt-2 text-sm text-gray-500">
                  {match.item.description}
                </p>
                <p className="mt-2 text-sm text-indigo-600">
                  Match score: {match.score}
                </p>
                <Link
                  to={`/items/${match.item.id}`}
                  className="mt-3 inline-block text-sm font-medium text-indigo-600 hover:underline"
                >
                  View match
                </Link>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
