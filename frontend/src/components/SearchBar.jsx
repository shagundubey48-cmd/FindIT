
import { Search } from "lucide-react";

export default function SearchBar({ value, onChange, onSearch }) {
  function handleSubmit(event) {
    event.preventDefault();
    onSearch?.();
  }

  return (
    <form onSubmit={handleSubmit} className="flex w-full gap-2">
      <div className="relative flex-1">
        <Search
          size={19}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
        />

        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Search by item name or description..."
          className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
        />
      </div>

      <button
        type="submit"
        className="rounded-lg bg-indigo-600 px-5 py-3 font-medium text-white hover:bg-indigo-700"
      >
        Search
      </button>
    </form>
  );
}
