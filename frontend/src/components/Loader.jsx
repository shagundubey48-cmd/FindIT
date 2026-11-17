export default function Loader({ text = "Loading..." }) {
  return <div className="flex min-h-40 items-center justify-center gap-3 text-slate-600"><span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />{text}</div>;
}

