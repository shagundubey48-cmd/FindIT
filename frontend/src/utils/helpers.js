// The API returns naive UTC timestamps (no "Z"). Without a timezone the
// browser would treat them as local time and show the wrong date/time.
const parseApiDate = (value) => {
  if (!value) return null;
  const text = String(value);
  const hasTimezone = /([zZ]|[+-]\d{2}:?\d{2})$/.test(text);
  const isDateTime = text.includes("T");
  return new Date(isDateTime && !hasTimezone ? `${text}Z` : text);
};

export const formatDate = (value) => {
  const date = parseApiDate(value);
  if (!date || Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
};

export const formatDateTime = (value) => {
  const date = parseApiDate(value);
  if (!date || Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const getErrorMessage = (error) =>
  error?.response?.data?.message || error?.message || "Something went wrong.";

export const titleCase = (value) =>
  String(value || "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

export const statusClasses = (status) =>
  ({
    pending: "bg-amber-100 text-amber-700",
    approved: "bg-green-100 text-green-700",
    rejected: "bg-red-100 text-red-700",
    active: "bg-green-100 text-green-700",
    claimed: "bg-indigo-100 text-indigo-700",
    resolved: "bg-blue-100 text-blue-700",
    withdrawn: "bg-gray-100 text-gray-600",
    removed: "bg-red-100 text-red-700",
  }[status] || "bg-slate-100 text-slate-600");

// Download a protected image (QR code) through the authenticated API client.
export const openBlobInNewTab = (blob) => {
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank", "noopener");
  setTimeout(() => URL.revokeObjectURL(url), 60000);
};
