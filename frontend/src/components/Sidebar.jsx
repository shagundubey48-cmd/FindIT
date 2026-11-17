
import { NavLink } from "react-router-dom";
const links=[["/dashboard","Overview"],["/report-lost","Report lost"],["/report-found","Report found"],["/my-reports","My reports"],["/my-claims","My claims"],["/my-handovers","Handovers"],["/messages","Messages"],["/profile","Profile"]];
export default function Sidebar(){return <aside className="rounded-2xl border bg-white p-3"><p className="px-3 py-2 text-xs font-bold uppercase tracking-wider text-slate-400">Workspace</p>{links.map(([to,label])=><NavLink key={to} to={to} className={({isActive})=>`mb-1 block rounded-xl px-3 py-2.5 text-sm ${isActive?"bg-indigo-50 font-semibold text-indigo-700":"text-slate-600 hover:bg-slate-50"}`}>{label}</NavLink>)}</aside>}
