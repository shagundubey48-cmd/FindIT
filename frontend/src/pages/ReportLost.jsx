import { useState } from "react";
import { useNavigate } from "react-router-dom";
import itemService from "../services/itemService";
import { CATEGORIES, CAMPUSES } from "../utils/constants";

export default function ReportLost() {
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

      const result = await itemService.reportLostItem(form);

      // The report already exists at this point. If only the image fails,
      // keep the report (retrying would create a duplicate) and go on.
      if (image && result.item?.id) {
        try {
          await itemService.uploadImage(result.item.id, image);
        } catch {
          window.alert(
            "Your report was saved, but the image could not be uploaded."
          );
        }
      }

      navigate(`/items/${result.item.id}`);
    } catch (err) {
      setError(
        err.response?.data?.message || "Unable to submit lost item report."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="mb-2 text-3xl font-bold text-gray-900">
        Report a Lost Item
      </h1>

      <p className="mb-8 text-gray-600">
        Provide details about the item you lost.
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
            placeholder="e.g. Black Wallet"
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
            {CATEGORIES.map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
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
            {CAMPUSES.map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-2 block font-medium">Location</label>
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
          <label className="mb-2 block font-medium">Date Lost</label>
          <input
            type="date"
            name="item_date"
            value={form.item_date}
            onChange={handleChange}
            required
            max={new Date().toLocaleDateString("en-CA")}
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
          className="w-full rounded-lg bg-indigo-600 px-5 py-3 font-semibold text-white hover:bg-indigo-700 disabled:opacity-60"
        >
          {loading ? "Submitting..." : "Submit Lost Item"}
        </button>
      </form>
    </div>
  );
}
