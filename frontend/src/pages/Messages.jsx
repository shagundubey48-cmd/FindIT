import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getConversations,
  getMessages,
  sendMessage,
} from "../services/messageService";
import Loader from "../components/Loader";
import { formatDateTime, getErrorMessage } from "../utils/helpers";

export default function Messages() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [thread, setThread] = useState([]);
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const loadConversations = useCallback(async () => {
    try {
      const { data } = await getConversations();
      setConversations(data.conversations || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const openConversation = useCallback(async (id) => {
    try {
      setError("");
      setActiveId(id);
      const { data } = await getMessages(id);
      setThread(data.messages || []);
      // Opening a conversation marks its messages as read.
      await loadConversations();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }, [loadConversations]);

  const handleSend = async (event) => {
    event.preventDefault();
    if (!body.trim() || !activeId) return;

    try {
      setSending(true);
      setError("");
      await sendMessage(activeId, body.trim());
      setBody("");
      await openConversation(activeId);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSending(false);
    }
  };

  const active = conversations.find((c) => c.id === activeId);

  if (loading) return <Loader />;

  return (
    <main className="mx-auto max-w-5xl px-5 py-10">
      <h1 className="text-3xl font-bold">Messages</h1>
      <p className="mt-2 text-slate-500">
        Chats are anonymous — real identities are never shown.
      </p>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-red-700">{error}</p>}

      {conversations.length === 0 ? (
        <div className="mt-6 rounded-2xl border bg-white p-10 text-center text-slate-500">
          No conversations yet. Open an item and use "Message reporter" to start one.
        </div>
      ) : (
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <ul className="space-y-2">
            {conversations.map((c) => (
              <li key={c.id}>
                <button
                  onClick={() => openConversation(c.id)}
                  className={`w-full rounded-xl border p-3 text-left ${
                    c.id === activeId ? "border-indigo-500 bg-indigo-50" : "bg-white"
                  }`}
                >
                  <p className="truncate font-semibold">{c.item_title}</p>
                  <p className="text-xs text-slate-500">{c.other_party}</p>
                  {c.last_message && (
                    <p className="mt-1 truncate text-sm text-slate-600">{c.last_message.body}</p>
                  )}
                  {c.unread_count > 0 && (
                    <span className="mt-1 inline-block rounded-full bg-red-500 px-2 text-xs text-white">
                      {c.unread_count} new
                    </span>
                  )}
                </button>
              </li>
            ))}
          </ul>

          <section className="rounded-2xl border bg-white p-4 md:col-span-2">
            {!active ? (
              <p className="py-10 text-center text-slate-500">Select a conversation.</p>
            ) : (
              <>
                <div className="mb-3 flex items-center justify-between border-b pb-3">
                  <div>
                    <h2 className="font-bold">{active.item_title}</h2>
                    <p className="text-xs text-slate-500">with {active.other_party}</p>
                  </div>
                  <Link to={`/items/${active.item_id}`} className="text-sm text-primary">View item</Link>
                </div>

                <div className="max-h-96 space-y-2 overflow-y-auto">
                  {thread.map((m) => (
                    <div key={m.id} className={`flex ${m.is_mine ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${m.is_mine ? "bg-primary text-white" : "bg-slate-100"}`}>
                        <p className="whitespace-pre-wrap break-words">{m.body}</p>
                        <p className={`mt-1 text-[10px] ${m.is_mine ? "text-indigo-200" : "text-slate-400"}`}>
                          {formatDateTime(m.created_at)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                <form onSubmit={handleSend} className="mt-4 flex gap-2">
                  <input
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    maxLength={1000}
                    placeholder="Type a message..."
                    className="flex-1 rounded-lg border px-4 py-2"
                  />
                  <button
                    type="submit"
                    disabled={sending || !body.trim()}
                    className="rounded-lg bg-primary px-5 py-2 text-white disabled:opacity-60"
                  >
                    Send
                  </button>
                </form>
              </>
            )}
          </section>
        </div>
      )}
    </main>
  );
}
