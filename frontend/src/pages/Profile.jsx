import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { formatDate, getErrorMessage } from "../utils/helpers";

export default function Profile() {
  const { user, updateProfile } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setName(user?.name || "");
  }, [user?.name]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage("");
    setError("");

    if (!name.trim()) {
      setError("Name cannot be empty.");
      return;
    }

    try {
      setSaving(true);
      const data = await updateProfile({ name: name.trim() });
      setMessage(data.message || "Profile updated.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="mx-auto max-w-xl px-5 py-10">
      <h1 className="text-3xl font-bold">My profile</h1>

      <form onSubmit={handleSubmit} className="mt-6 space-y-5 rounded-2xl border bg-white p-6">
        {message && <p className="rounded-lg bg-green-50 p-3 text-green-700">{message}</p>}
        {error && <p className="rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

        <div>
          <label className="mb-2 block text-sm font-medium">Full name</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={100}
            className="w-full rounded-lg border px-4 py-3"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium">Email</label>
          <input
            value={user?.email || ""}
            disabled
            className="w-full rounded-lg border bg-slate-50 px-4 py-3 text-slate-500"
          />
        </div>

        <p className="text-sm text-slate-500">
          Member since {formatDate(user?.created_at)}
          {user?.is_verified ? " · Email verified" : ""}
          {user?.is_admin ? " · Administrator" : ""}
        </p>

        <button
          type="submit"
          disabled={saving}
          className="w-full rounded-lg bg-primary px-5 py-3 font-semibold text-white disabled:opacity-60"
        >
          {saving ? "Saving..." : "Save changes"}
        </button>
      </form>
    </main>
  );
}
