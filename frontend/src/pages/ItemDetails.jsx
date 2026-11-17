
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import itemService from "../services/itemService";
import { MapPin, Calendar, Tag, ArrowLeft } from "lucide-react";

export default function ItemDetails() {
  const { id } = useParams();

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchItem = async () => {
      try {
        setLoading(true);

        const data = await itemService.getItemDetails(id);
        setItem(data.item);
      } catch (err) {
        setError(
          err.response?.data?.message ||
          "Unable to load item details."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchItem();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        Loading item details...
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="min-h-screen flex flex-col gap-4 justify-center items-center">
        <h2 className="text-2xl font-bold">
          {error || "Item not found"}
        </h2>
        <Link to="/found-items" className="text-primary">
          Back to Items
        </Link>
      </div>
    );
  }

  const isLost = item.item_type === "lost";

  return (
    <div className="min-h-screen bg-background py-12 px-5">

      <div className="max-w-5xl mx-auto">

        <Link to="/" className="flex gap-2 items-center text-primary mb-7">
          <ArrowLeft size={18} />
          Back to Home
        </Link>

        <div className="bg-white rounded-2xl shadow-sm overflow-hidden grid md:grid-cols-2">

          <div className="bg-gray-100 min-h-72">

            {item.image_url ? (
              <img
                src={item.image_url}
                alt={item.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="h-full min-h-72 flex justify-center items-center text-gray-400">
                No Image Available
              </div>
            )}

          </div>

          <div className="p-8">

            <span className={`inline-block px-4 py-2 rounded-full text-sm font-semibold ${
              isLost
                ? "bg-red-100 text-red-600"
                : "bg-green-100 text-green-600"
            }`}>
              {isLost ? "LOST ITEM" : "FOUND ITEM"}
            </span>

            <h1 className="text-3xl font-bold mt-5">
              {item.title}
            </h1>

            <p className="text-gray-500 mt-4 leading-relaxed">
              {item.description}
            </p>

            <div className="space-y-4 mt-8">

              <p className="flex gap-3 items-center">
                <Tag className="text-primary" />
                {item.category}
              </p>

              <p className="flex gap-3 items-center">
                <MapPin className="text-primary" />
                {item.location}, {item.campus}
              </p>

              <p className="flex gap-3 items-center">
                <Calendar className="text-primary" />
                {item.item_date}
              </p>

            </div>

            <div className="mt-8 pt-5 border-t">
              <p className="text-sm text-gray-500">
                Report ID: #{item.id}
              </p>

              <p className="text-sm text-gray-500 mt-2">
                Status: {item.status}
              </p>
            </div>

            <Link
              to="/found-items"
              className="block text-center bg-primary text-white rounded-xl py-3 mt-7"
            >
              Explore Other Items
            </Link>

          </div>

        </div>

      </div>
    </div>
  );
}

