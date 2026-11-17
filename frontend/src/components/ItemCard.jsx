
import { Link } from "react-router-dom";
import { MapPin, CalendarDays, Tag } from "lucide-react";

export default function ItemCard({ item }) {
  if (!item) return null;

  const isLost = item.item_type === "lost";

  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md">
      <div className="relative h-48 bg-gray-100">
        {item.image_url ? (
          <img
            src={item.image_url}
            alt={item.title}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-400">
            No image available
          </div>
        )}

        <span
          className={`absolute left-3 top-3 rounded-full px-3 py-1 text-xs font-semibold ${
            isLost
              ? "bg-red-100 text-red-700"
              : "bg-green-100 text-green-700"
          }`}
        >
          {isLost ? "Lost" : "Found"}
        </span>
      </div>

      <div className="p-4">
        <h3 className="mb-2 truncate text-lg font-semibold text-gray-900">
          {item.title}
        </h3>

        <p className="mb-3 line-clamp-2 min-h-10 text-sm text-gray-600">
          {item.description}
        </p>

        <div className="space-y-2 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <Tag size={16} />
            <span>{item.category}</span>
          </div>

          <div className="flex items-center gap-2">
            <MapPin size={16} />
            <span>{item.location}, {item.campus}</span>
          </div>

          <div className="flex items-center gap-2">
            <CalendarDays size={16} />
            <span>{item.item_date}</span>
          </div>
        </div>

        <Link
          to={`/items/${item.id}`}
          className="mt-4 block rounded-lg bg-indigo-600 px-4 py-2 text-center text-sm font-medium text-white transition hover:bg-indigo-700"
        >
          View Details
        </Link>
      </div>
    </div>
  );
}
