
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import itemService from "../services/itemService";

export default function ReportFound() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    description: "",
    category: "",
    campus: "",
    location: "",
    item_date: ""
  });

  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");

      const result = await itemService.reportFoundItem(form);

      if (image && result.item?.id) {
        await itemService.uploadImage(result.item.id, image);
      }

      navigate(`/items/${result.item.id}`);
    } catch (err) {
      setError(
        err.response?.data?.message || "Unable to submit found item report."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="mb-2 text-3xl font-bold text-gray-900">
        Report a Found Item
      </h1>

      <p className="mb-8 text-gray-600">
        Help another student by reporting an item you found.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="mb-2 block font-medium">Item Name</label>
          <input
            name="title"
            value={form.title}
            onChange={handleChange}
            required
            maxLength={150}
            className="w-full rounded-lg border border-gray-300 px-4 py-3"
            placeholder="e.g. Blue Water Bottle"
          />
        </div>

        <div>
          <label className="mb-2 block font-medium">Description</label>
          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            required
            rows={4}
            className="w-full rounded-lg border border-gray-300 px-4 py-3"
            placeholder="Describe the item..."
          />
        </div>

        <div>
          <label className="mb-2 block font-medium">Category</label>
          <select
            name="category"
            value={form.category}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-gray-300 px-4 py-3"
          >
            <option value="">Select category</option>
            <option>Electronics</option>
            <option>Accessories</option>
            <option>Bags</option>
            <option>Clothing</option>
            <option>Stationery</option>
            <option>Documents</option>
            <option>Other</option>
          </select>
        </div>

        <div>
          <label className="mb-2 block font-medium">Campus</label>
          <select
            name="campus"
            value={form.campus}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-gray-300 px-4 py-3"
          >
            <option value="">Select campus</option>
            <option value="JIIT Sector 62">JIIT Sector 62</option>
            <option value="JIIT Sector 128">JIIT Sector 128</option>
          </select>
        </div>

        <div>
          <label className="mb-2 block font-medium">Location Found</label>
          <input
            name="location"
            value={form.location}
            onChange={handleChange}
            required
            className="w-full rounded-lg border border-gray-300 px-4 py-3"
            placeholder="e.g. Library, Academic Block"
          />
        </div>

        <div>
          <label className="mb-2 block font-medium">Date Found</label>
          <input
            type="date"
            name="item_date"
            value={form.item_date}
            onChange={handleChange}
            required
            max={new Date().toISOString().split("T")[0]}
            className="w-full rounded-lg border border-gray-300 px-4 py-3"
          />
        </div>

        <div>
          <label className="mb-2 block font-medium">
            Item Image (Optional)
          </label>
          <input
            type="file"
            accept=".jpg,.jpeg,.png,.webp"
            onChange={(event) => setImage(event.target.files?.[0] || null)}
            className="w-full rounded-lg border border-gray-300 p-3"
          />
          <p className="mt-1 text-xs text-gray-500">
            Allowed formats: JPG, JPEG, PNG, WEBP.
          </p>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-green-600 px-5 py-3 font-semibold text-white hover:bg-green-700 disabled:opacity-60"
        >
          {loading ? "Submitting..." : "Submit Found Item"}
        </button>
      </form>
    </div>
  );
}
