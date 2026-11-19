import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  getMyFeedback,
  getMyHandovers,
  submitFeedback,
} from "../services/handoverService";
import Loader from "../components/Loader";
import { formatDate, getErrorMessage } from "../utils/helpers";

function FeedbackForm({ handover, onDone }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    try {
      setSaving(true);
      await submitFeedback(handover.id, { rating, comment });
      onDone();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-2xl border bg-white p-5">
      <h3 className="font-bold">{handover.item_title}</h3>
      {error && <p className="mt-2 rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}

      <label className="mt-3 block text-sm font-medium">Rating</label>
      <select
        value={rating}
        onChange={(e) => setRating(Number(e.target.value))}
        className="mt-1 rounded-lg border px-3 py-2"
      >
        {[5, 4, 3, 2, 1].map((n) => (
          <option key={n} value={n}>{n} / 5</option>
        ))}
      </select>

      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        maxLength={1000}
        rows={3}
        placeholder="Comments (optional)"
        className="mt-3 w-full rounded-lg border px-3 py-2"
      />

      <button
        type="submit"
        disabled={saving}
        className="mt-3 rounded-lg bg-primary px-4 py-2 text-white disabled:opacity-60"
      >
        {saving ? "Submitting..." : "Submit feedback"}
      </button>
    </form>
  );
}

export default function Feedback() {
  const { user } = useAuth();
  const [handovers, setHandovers] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setError("");
      const [handoverRes, feedbackRes] = await Promise.all([
        getMyHandovers(),
        getMyFeedback(),
      ]);
      setHandovers(handoverRes.data.handovers || []);
      setFeedback(feedbackRes.data.feedback || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const rated = new Set(feedback.map((f) => f.handover_id));
  const pending = handovers.filter(
    (h) => h.received_by === user?.id && !rated.has(h.id)
  );

  if (loading) return <Loader />;

  return (
    <main className="mx-auto max-w-3xl px-5 py-10">
      <h1 className="text-3xl font-bold">Feedback</h1>
      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

      <h2 className="mb-3 mt-8 text-xl font-bold">Waiting for your feedback</h2>
      {pending.length === 0 ? (
        <p className="text-slate-500">Nothing to rate right now.</p>
      ) : (
        <div className="space-y-4">
          {pending.map((h) => (
            <FeedbackForm key={h.id} handover={h} onDone={load} />
          ))}
        </div>
      )}

      <h2 className="mb-3 mt-10 text-xl font-bold">Feedback you submitted</h2>
      {feedback.length === 0 ? (
        <p className="text-slate-500">No feedback submitted yet.</p>
      ) : (
        <div className="space-y-3">
          {feedback.map((f) => (
            <article key={f.id} className="rounded-2xl border bg-white p-4">
              <div className="flex justify-between">
                <h3 className="font-semibold">{f.item_title}</h3>
                <span className="text-amber-600">{"★".repeat(f.rating)}{"☆".repeat(5 - f.rating)}</span>
              </div>
              {f.comment && <p className="mt-2 text-sm text-slate-600">{f.comment}</p>}
              <p className="mt-2 text-xs text-slate-400">{formatDate(f.created_at)}</p>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
