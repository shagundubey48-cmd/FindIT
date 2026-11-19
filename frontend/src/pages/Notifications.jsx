import { Link } from "react-router-dom";
import { useNotifications } from "../hooks/useNotifications";
import { formatDateTime } from "../utils/helpers";

export default function Notifications() {
  const { notifications, unreadCount, markRead } = useNotifications();

  return (
    <main className="mx-auto max-w-3xl px-5 py-10">
      <h1 className="text-3xl font-bold">Notifications</h1>
      <p className="mt-2 text-slate-500">{unreadCount} unread</p>

      {notifications.length === 0 ? (
        <div className="mt-6 rounded-2xl border bg-white p-10 text-center text-slate-500">
          No notifications yet. You will be notified when a potential match is found.
        </div>
      ) : (
        <ul className="mt-6 space-y-3">
          {notifications.map((n) => (
            <li
              key={n.id}
              className={`rounded-2xl border p-4 ${n.is_read ? "bg-white" : "border-indigo-300 bg-indigo-50"}`}
            >
              <p className="text-slate-800">{n.message}</p>
              <p className="mt-1 text-xs text-slate-400">{formatDateTime(n.created_at)}</p>
              <div className="mt-3 flex flex-wrap gap-3 text-sm">
                <Link to={`/items/${n.item_id}`} className="text-primary">Item #{n.item_id}</Link>
                <Link to={`/items/${n.matched_item_id}`} className="text-primary">Item #{n.matched_item_id}</Link>
                {!n.is_read && (
                  <button onClick={() => markRead(n.id)} className="text-slate-600 underline">
                    Mark as read
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
