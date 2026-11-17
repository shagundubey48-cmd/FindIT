import { Link } from "react-router-dom";
export default function Footer() {
  return <footer className="mt-12 border-t bg-white px-6 py-7 text-center text-sm text-slate-500">© {new Date().getFullYear()} FindIT · Campus Lost & Found <span className="mx-2">·</span><Link to="/" className="text-indigo-600">Home</Link></footer>;
}

