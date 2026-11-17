import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import Loader from "../components/Loader";
import { getErrorMessage, formatDate, titleCase } from "../utils/helpers";

export default function Dashboard() {
  const [rows,setRows]=useState([]);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");
  const [notice,setNotice]=useState("");
  const [busy,setBusy]=useState(false);
  const [remarks,setRemarks]=useState("");
  const [query,setQuery]=useState("");
  const [selected,setSelected]=useState(null);
  const load=async()=>{setLoading(true);setError("");try{const {data}=await api.get("/statistics/summary");setRows(data.items||data.items||data.claims||data.handovers||data.notifications||data.conversations||[]);}catch(e){setError(getErrorMessage(e));}finally{setLoading(false);}};
  useEffect(()=>{load();},[]);
  const act=async(id,method,url,payload)=>{setBusy(true);setError("");setNotice("");try{await api[method](url,payload);setNotice("Updated successfully.");await load();}catch(e){setError(getErrorMessage(e));}finally{setBusy(false);}};
  const filtered=rows.filter(r=>JSON.stringify(r).toLowerCase().includes(query.toLowerCase()));
  return <main className="mx-auto max-w-6xl px-5 py-10"><div className="mb-7 flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm font-semibold uppercase tracking-wider text-indigo-600">FindIT workspace</p><h1 className="mt-1 text-3xl font-bold">Dashboard</h1><p className="mt-2 text-slate-500">Review and manage your FindIT activity.</p></div><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search..." className="rounded-xl border px-4 py-3 outline-none focus:border-indigo-500"/></div>
  {notice&&<p className="mb-4 rounded-xl bg-green-50 p-3 text-green-700">{notice}</p>}{error&&<p className="mb-4 rounded-xl bg-red-50 p-3 text-red-700">{error}</p>}
  {loading?<Loader/>:filtered.length===0?<div className="rounded-2xl border bg-white p-10 text-center text-slate-500">Nothing to show yet.</div>:<div className="grid gap-4 md:grid-cols-2">{filtered.map((r,i)=><article key={r.id??i} className="rounded-2xl border bg-white p-5 shadow-sm"><div className="flex items-start justify-between gap-3"><div><h2 className="font-bold text-slate-900">{r.title||r.item_title||r.message||r.name||`Record #${r.id}`}</h2><p className="mt-1 text-sm text-slate-500">{r.description||r.item_type||r.other_party||r.email||""}</p></div><span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">{titleCase(r.status||"available")}</span></div><p className="mt-3 text-sm text-slate-600">{r.location||r.admin_remarks||r.handover_notes||r.ownership_details||""}</p><p className="mt-3 text-xs text-slate-400">{formatDate(r.created_at||r.item_date||r.handed_over_at)}</p>{r.image_url&&<img src={r.image_url} alt={r.title||"Item"} className="mt-3 h-40 w-full rounded-xl object-cover"/>}<div className="mt-4 flex flex-wrap gap-2">{r.item_id&&<Link to={`/items/${r.item_id}`} className="rounded-lg border px-3 py-2 text-sm">View item</Link>}{r.id&&<button onClick={()=>setSelected(r)} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white">Details</button>}</div></article>)}</div>}
  {selected&&<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={()=>setSelected(null)}><div className="max-h-[85vh] w-full max-w-xl overflow-auto rounded-2xl bg-white p-6" onClick={e=>e.stopPropagation()}><div className="mb-4 flex justify-between"><h2 className="text-xl font-bold">Record details</h2><button onClick={()=>setSelected(null)}>✕</button></div><pre className="whitespace-pre-wrap break-words text-xs">{JSON.stringify(selected,null,2)}</pre></div></div>}
  </main>;
}

