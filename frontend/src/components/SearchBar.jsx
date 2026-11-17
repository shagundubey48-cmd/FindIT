
import { Search } from "lucide-react";

export default function SearchBar({ value, onChange }) {
  return (
    <div className="relative w-full">

      <Search
        size={20}
        className="absolute left-4 top-3.5 text-gray-400"
      />

      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search items by name or description..."
        className="w-full border border-gray-200 bg-white rounded-xl py-3 pl-12 pr-4 outline-none focus:ring-2 focus:ring-primary"
      />

    </div>
  );
}

