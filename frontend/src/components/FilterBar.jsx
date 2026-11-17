
const categories = [
  "Electronics",
  "Accessories",
  "Bags",
  "Stationery",
  "Clothing",
  "Documents",
  "Other",
];

const campuses = [
  "JIIT Sector 62",
  "JIIT Sector 128",
];

export default function FilterBar({ filters, setFilters }) {

  const handleChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="grid sm:grid-cols-2 gap-4">

      <select
        name="category"
        value={filters.category}
        onChange={handleChange}
        className="border rounded-xl p-3 bg-white outline-none focus:ring-2 focus:ring-primary"
      >
        <option value="">All Categories</option>

        {categories.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>

      <select
        name="campus"
        value={filters.campus}
        onChange={handleChange}
        className="border rounded-xl p-3 bg-white outline-none focus:ring-2 focus:ring-primary"
      >
        <option value="">All Campuses</option>

        {campuses.map((campus) => (
          <option key={campus} value={campus}>
            {campus}
          </option>
        ))}
      </select>

    </div>
  );
}

