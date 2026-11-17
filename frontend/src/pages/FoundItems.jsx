
import { useCallback, useEffect, useState } from "react";
import itemService from "../services/itemService";
import ItemCard from "../components/ItemCard";
import SearchBar from "../components/SearchBar";
import FilterBar from "../components/FilterBar";

export default function FoundItems() {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [campus, setCampus] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchItems = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const data = await itemService.getItems({
        q: search,
        type: "found",
        category,
        campus
      });

      setItems(data.items || []);
    } catch (err) {
      setError(
        err.response?.data?.message || "Unable to load found items."
      );
    } finally {
      setLoading(false);
    }
  }, [search, category, campus]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  function clearFilters() {
    setSearch("");
    setCategory("");
    setCampus("");
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Found Items
        </h1>
        <p className="mt-2 text-gray-600">
          Browse items found by other students.
        </p>
      </div>

      <div className="mb-4">
        <SearchBar
          value={search}
          onChange={setSearch}
          onSearch={fetchItems}
        />
      </div>

      <div className="mb-8">
        <FilterBar
          category={category}
          campus={campus}
          onCategoryChange={setCategory}
          onCampusChange={setCampus}
          onClear={clearFilters}
        />
      </div>

      {loading ? (
        <p className="py-12 text-center text-gray-500">
          Loading found items...
        </p>
      ) : error ? (
        <p className="py-12 text-center text-red-600">{error}</p>
      ) : items.length === 0 ? (
        <p className="py-12 text-center text-gray-500">
          No found items available.
        </p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
