
export default function FilterBar({
  category,
  campus,
  onCategoryChange,
  onCampusChange,
  onClear
}) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row">
      <select
        value={category}
        onChange={(event) => onCategoryChange(event.target.value)}
        className="rounded-lg border border-gray-300 bg-white px-4 py-3 outline-none focus:border-indigo-500"
      >
        <option value="">All Categories</option>
        <option value="Electronics">Electronics</option>
        <option value="Accessories">Accessories</option>
        <option value="Bags">Bags</option>
        <option value="Clothing">Clothing</option>
        <option value="Stationery">Stationery</option>
        <option value="Documents">Documents</option>
        <option value="Other">Other</option>
      </select>

      <select
        value={campus}
        onChange={(event) => onCampusChange(event.target.value)}
        className="rounded-lg border border-gray-300 bg-white px-4 py-3 outline-none focus:border-indigo-500"
      >
        <option value="">All Campuses</option>
        <option value="JIIT Sector 62">JIIT Sector 62</option>
        <option value="JIIT Sector 128">JIIT Sector 128</option>
      </select>

      <button
        type="button"
        onClick={onClear}
        className="rounded-lg border border-gray-300 px-4 py-3 text-gray-700 hover:bg-gray-50"
      >
        Clear Filters
      </button>
    </div>
  );
}
