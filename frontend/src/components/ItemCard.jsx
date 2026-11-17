
import { Link } from "react-router-dom";
import { MapPin, Calendar, Tag } from "lucide-react";

export default function ItemCard({ item }) {
  const isLost = item.item_type === "lost";

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition">

      <div className="h-48 bg-gray-100 overflow-hidden">

        {item.image_url ? (
          <img
            src={item.image_url}
            alt={item.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No Image Available
          </div>
        )}

      </div>

      <div className="p-5">

        <div className="flex justify-between items-center mb-3">

          <span className={`text-xs font-semibold px-3 py-1 rounded-full ${
            isLost
              ? "bg-red-100 text-red-600"
              : "bg-green-100 text-green-600"
          }`}>
            {isLost ? "LOST ITEM" : "FOUND ITEM"}
          </span>

          <span className="text-xs text-gray-400">
            #{item.id}
          </span>

        </div>

        <h3 className="text-lg font-bold text-gray-900">
          {item.title}
        </h3>

        <p className="text-sm text-gray-500 mt-2 line-clamp-2">
          {item.description}
        </p>

        <div className="mt-4 space-y-2 text-sm text-gray-500">

          <p className="flex items-center gap-2">
            <Tag size={15} />
            {item.category}
          </p>

          <p className="flex items-center gap-2">
            <MapPin size={15} />
            {item.location}, {item.campus}
          </p>

          <p className="flex items-center gap-2">
            <Calendar size={15} />
            {item.item_date}
          </p>

        </div>

        <Link
          to={`/items/${item.id}`}
          className="block text-center bg-primary text-white py-2.5 rounded-lg mt-5 hover:bg-indigo-700"
        >
          View Details
        </Link>

      </div>
    </div>
  );
}

