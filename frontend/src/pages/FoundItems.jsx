
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import itemService from "../services/itemService";
import ItemCard from "../components/ItemCard";
import SearchBar from "../components/SearchBar";
import FilterBar from "../components/FilterBar";

export default function FoundItems() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");

  const [filters, setFilters] = useState({
    category: "",
    campus: "",
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        setLoading(true);
        setError("");

        const data = await itemService.getFoundItems({
          q: search,
          ...filters,
        });

        setItems(data.items || []);
      } catch (err) {
        setError(
          err.response?.data?.message ||
          "Unable to load found items."
        );
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [search, filters]);

  return (
    <div className="min-h-screen bg-background">

      <div className="max-w-7xl mx-auto px-6 py-10">

        <div className="flex flex-wrap justify-between items-center gap-4 mb-8">

          <div>
            <h1 className="text-3xl font-bold">
              Found Items
            </h1>

            <p className="text-gray-500 mt-2">
              Explore belongings found by other students.
            </p>
          </div>

          <Link
            to="/report-found"
            className="bg-primary text-white px-5 py-3 rounded-xl"
          >
            + Report Found Item
          </Link>

        </div>

        <div className="space-y-4 mb-8">

          <SearchBar
            value={search}
            onChange={setSearch}
          />

          <FilterBar
            filters={filters}
            setFilters={setFilters}
          />

        </div>

        {error && (
          <p className="text-red-500 text-center py-6">
            {error}
          </p>
        )}

        {loading ? (
          <p className="text-center py-16 text-gray-500">
            Loading found items...
          </p>
        ) : items.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl">
            <h2 className="text-xl font-semibold">
              No Found Items Available
            </h2>

            <p className="text-gray-500 mt-2">
              Try another search or category.
            </p>
          </div>
        ) : (
          <>
            <p className="text-gray-500 mb-5">
              {items.length} items found
            </p>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          </>
        )}

      </div>
    </div>
  );
}

