import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { MapPin, Calendar, Tag, ArrowLeft } from "lucide-react";
import itemService from "../services/itemService";
import {
  createClaim,
  getItemQr,
  getSecretQuestion,
  setSecretQuestion,
  verifySecretAnswer,
} from "../services/claimService";
import { startConversation } from "../services/messageService";
import { useAuth } from "../context/AuthContext";
import Loader from "../components/Loader";
import {
  formatDate,
  getErrorMessage,
  openBlobInNewTab,
  statusClasses,
  titleCase,
} from "../utils/helpers";

export default function ItemDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  // Secret question state
  const [secret, setSecret] = useState(null);
  const [answer, setAnswer] = useState("");
  const [newQuestion, setNewQuestion] = useState("");
  const [newAnswer, setNewAnswer] = useState("");

  // Claim / message state
  const [ownership, setOwnership] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const isOwner = Boolean(item && user && item.user_id === user.id);
  const isFound = item?.item_type === "found";
  const canInteract = item?.status === "active" && !isOwner;

  const loadItem = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      setItem(await itemService.getItemById(id));
    } catch (err) {
      setItem(null);
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadItem();
  }, [loadItem]);

  // Load the secret question once we know this is someone else's found item.
  useEffect(() => {
    if (!item || item.item_type !== "found" || item.status !== "active") return;

    getSecretQuestion(item.id)
      .then(({ data }) => setSecret(data))
      .catch(() => setSecret(null));
  }, [item]);

  const run = async (action) => {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await action();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const handleVerify = (event) => {
    event.preventDefault();
    run(async () => {
      try {
        await verifySecretAnswer(item.id, answer);
        setSecret({ ...secret, verified: true });
        setNotice("Answer verified. You can now submit your claim.");
      } catch (err) {
        const data = err.response?.data;
        if (data?.attempts_remaining !== undefined) {
          throw new Error(
            `Incorrect answer. ${data.attempts_remaining} attempt(s) remaining.`
          );
        }
        throw err;
      }
    });
  };

  const handleClaim = (event) => {
    event.preventDefault();
    run(async () => {
      const { data } = await createClaim(item.id, { ownership_details: ownership });
      navigate(`/claims/${data.claim.id}`);
    });
  };

  const handleMessage = (event) => {
    event.preventDefault();
    run(async () => {
      await startConversation(item.id, message);
      navigate("/messages");
    });
  };

  const handleSaveSecret = (event) => {
    event.preventDefault();
    run(async () => {
      await setSecretQuestion(item.id, { question: newQuestion, answer: newAnswer });
      setSecret({ has_secret_question: true, question: newQuestion });
      setNewQuestion("");
      setNewAnswer("");
      setNotice("Secret question saved.");
    });
  };

  const handleQr = () =>
    run(async () => {
      const { data } = await getItemQr(item.id);
      openBlobInNewTab(data);
    });

  if (loading) return <Loader text="Loading item details..." />;

  if (!item) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
        <h2 className="text-2xl font-bold">{error || "Item not found"}</h2>
        <Link to="/found-items" className="text-primary">Back to Items</Link>
      </div>
    );
  }

  const isLost = item.item_type === "lost";
  const needsSecret = isFound && secret?.has_secret_question && !secret.verified;

  return (
    <div className="bg-background px-5 py-12">
      <div className="mx-auto max-w-5xl">
        <Link
          to={isLost ? "/lost-items" : "/found-items"}
          className="mb-7 flex items-center gap-2 text-primary"
        >
          <ArrowLeft size={18} />
          Back to {isLost ? "lost" : "found"} items
        </Link>

        <div className="grid overflow-hidden rounded-2xl bg-white shadow-sm md:grid-cols-2">
          <div className="min-h-72 bg-gray-100">
            {item.image_url ? (
              <img src={item.image_url} alt={item.title} className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full min-h-72 items-center justify-center text-gray-400">
                No Image Available
              </div>
            )}
          </div>

          <div className="p-8">
            <span
              className={`inline-block rounded-full px-4 py-2 text-sm font-semibold ${
                isLost ? "bg-red-100 text-red-600" : "bg-green-100 text-green-600"
              }`}
            >
              {isLost ? "LOST ITEM" : "FOUND ITEM"}
            </span>

            <h1 className="mt-5 text-3xl font-bold">{item.title}</h1>
            <p className="mt-4 leading-relaxed text-gray-500">{item.description}</p>

            <div className="mt-8 space-y-4">
              <p className="flex items-center gap-3"><Tag className="text-primary" /> {item.category}</p>
              <p className="flex items-center gap-3"><MapPin className="text-primary" /> {item.location}, {item.campus}</p>
              <p className="flex items-center gap-3"><Calendar className="text-primary" /> {formatDate(item.item_date)}</p>
            </div>

            <div className="mt-8 border-t pt-5 text-sm text-gray-500">
              <p>Report ID: #{item.id}</p>
              <p className="mt-2">
                Status:{" "}
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClasses(item.status)}`}>
                  {titleCase(item.status)}
                </span>
              </p>
            </div>
          </div>
        </div>

        {error && <p className="mt-6 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}
        {notice && <p className="mt-6 rounded-lg bg-green-50 p-3 text-green-700">{notice}</p>}

        {/* Owner tools */}
        {isOwner && (
          <section className="mt-6 space-y-4 rounded-2xl bg-white p-6">
            <h2 className="text-lg font-bold">Your report</h2>
            <div className="flex flex-wrap gap-3 text-sm">
              <Link to={`/matched-items?item=${item.id}`} className="rounded-lg border px-4 py-2 text-primary">
                View matches
              </Link>
              <button onClick={handleQr} disabled={busy} className="rounded-lg border px-4 py-2 text-primary">
                Show QR code
              </button>
              <Link to="/my-reports" className="rounded-lg border px-4 py-2 text-slate-600">
                Manage in My Reports
              </Link>
            </div>

            {isFound && item.status === "active" && (
              <form onSubmit={handleSaveSecret} className="space-y-3 border-t pt-4">
                <h3 className="font-semibold">
                  Secret question {secret?.has_secret_question ? "(set — enter new values to replace)" : ""}
                </h3>
                {secret?.has_secret_question && (
                  <p className="text-sm text-slate-500">Current question: {secret.question}</p>
                )}
                <input
                  value={newQuestion}
                  onChange={(e) => setNewQuestion(e.target.value)}
                  maxLength={255}
                  required
                  placeholder="Question only the owner can answer"
                  className="w-full rounded-lg border px-4 py-2"
                />
                <input
                  value={newAnswer}
                  onChange={(e) => setNewAnswer(e.target.value)}
                  maxLength={255}
                  required
                  placeholder="Answer"
                  className="w-full rounded-lg border px-4 py-2"
                />
                <button disabled={busy} className="rounded-lg bg-primary px-4 py-2 text-white disabled:opacity-60">
                  Save secret question
                </button>
              </form>
            )}
          </section>
        )}

        {/* Claim flow for found items */}
        {canInteract && isFound && (
          <section className="mt-6 rounded-2xl bg-white p-6">
            <h2 className="text-lg font-bold">Is this yours?</h2>

            {needsSecret ? (
              <form onSubmit={handleVerify} className="mt-4 space-y-3">
                <p className="text-sm text-slate-600">
                  Answer the finder's question first: <strong>{secret.question}</strong>
                </p>
                <input
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  required
                  placeholder="Your answer"
                  className="w-full rounded-lg border px-4 py-2"
                />
                <button disabled={busy} className="rounded-lg bg-primary px-4 py-2 text-white disabled:opacity-60">
                  Verify answer
                </button>
              </form>
            ) : (
              <form onSubmit={handleClaim} className="mt-4 space-y-3">
                <textarea
                  value={ownership}
                  onChange={(e) => setOwnership(e.target.value)}
                  rows={4}
                  maxLength={2000}
                  required
                  placeholder="Describe how you can prove this item is yours"
                  className="w-full rounded-lg border px-4 py-3"
                />
                <button disabled={busy} className="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white disabled:opacity-60">
                  Submit claim
                </button>
              </form>
            )}
          </section>
        )}

        {/* Anonymous message to the reporter */}
        {canInteract && (
          <section className="mt-6 rounded-2xl bg-white p-6">
            <h2 className="text-lg font-bold">Message the reporter</h2>
            <p className="text-sm text-slate-500">Your identity stays anonymous.</p>
            <form onSubmit={handleMessage} className="mt-4 space-y-3">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={3}
                maxLength={1000}
                required
                placeholder="Write your message..."
                className="w-full rounded-lg border px-4 py-3"
              />
              <button disabled={busy} className="rounded-lg bg-primary px-5 py-3 font-semibold text-white disabled:opacity-60">
                Send message
              </button>
            </form>
          </section>
        )}
      </div>
    </div>
  );
}
