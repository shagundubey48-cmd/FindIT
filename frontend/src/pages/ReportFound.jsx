
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import itemService from "../services/itemService";

const initialForm = {
  title: "",
  description: "",
  category: "",
  campus: "",
  location: "",
  item_date: "",
};

export default function ReportFound() {
  const navigate = useNavigate();

  const [form, setForm] = useState(initialForm);
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleImage = (e) => {
    const file = e.target.files?.[0];

    if (!file) return;

    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Only JPG, PNG and WEBP images are allowed.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("Image must be below 5 MB.");
      return;
    }

    setError("");
    setImage(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await itemService.reportFound(form);
      const item = response.item;

      if (image && item?.id) {
        await itemService.uploadImage(item.id, image);
      }

      navigate(`/items/${item.id}`);
    } catch (err) {
      setError(
        err.response?.data?.message ||
        "Unable to submit found item report."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background py-12 px-4">

      <div className="max-w-2xl mx-auto bg-white rounded-2xl shadow-sm p-8">

        <h1 className="text-3xl font-bold">
          Report Found Item
        </h1>

        <p className="text-gray-500 mt-2 mb-8">
          Help someone recover their lost belongings.
        </p>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-5">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">

          <div>
            <label className="block font-medium mb-2">
              Item Name *
            </label>

            <input
              name="title"
              value={form.title}
              onChange={handleChange}
              maxLength={150}
              placeholder="Example: Blue Water Bottle"
              className="w-full border rounded-xl p-3"
              required
            />
          </div>

          <div>
            <label className="block font-medium mb-2">
              Description *
            </label>

            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              rows="4"
              placeholder="Describe the found item..."
              className="w-full border rounded-xl p-3"
              required
            />
          </div>

          <div>
            <label className="block font-medium mb-2">
              Category *
            </label>

            <select
              name="category"
              value={form.category}
              onChange={handleChange}
              className="w-full border rounded-xl p-3"
              required
            >
              <option value="">Select category</option>
              <option>Electronics</option>
              <option>Accessories</option>
              <option>Bags</option>
              <option>Stationery</option>
              <option>Clothing</option>
              <option>Documents</option>
              <option>Other</option>
            </select>
          </div>

          <div>
            <label className="block font-medium mb-2">
              Campus *
            </label>

            <select
              name="campus"
              value={form.campus}
              onChange={handleChange}
              className="w-full border rounded-xl p-3"
              required
            >
              <option value="">Select campus</option>
              <option>JIIT Sector 62</option>
              <option>JIIT Sector 128</option>
            </select>
          </div>

          <div>
            <label className="block font-medium mb-2">
              Found Location *
            </label>

            <input
              name="location"
              value={form.location}
              onChange={handleChange}
              placeholder="Example: Academic Block"
              className="w-full border rounded-xl p-3"
              required
            />
          </div>

          <div>
            <label className="block font-medium mb-2">
              Date Found *
            </label>

            <input
              type="date"
              name="item_date"
              value={form.item_date}
              onChange={handleChange}
              max={new Date().toLocaleDateString("en-CA")}
              className="w-full border rounded-xl p-3"
              required
            />
          </div>

          <div>
            <label className="block font-medium mb-2">
              Item Image (Optional)
            </label>

            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handleImage}
              className="w-full border rounded-xl p-3"
            />

            {preview && (
              <img
                src={preview}
                alt="Found item preview"
                className="mt-4 w-40 h-40 object-cover rounded-xl"
              />
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-white py-3 rounded-xl font-semibold disabled:opacity-60"
          >
            {loading ? "Submitting..." : "Submit Found Report"}
          </button>

        </form>

      </div>
    </div>
  );
}

