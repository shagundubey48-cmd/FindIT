export default function Modal({ open, title, onClose, children }) {
  if (!open) return null;
  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4" onMouseDown={onClose}>
    <section className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl" onMouseDown={e => e.stopPropagation()}>
      <div className="mb-4 flex items-center justify-between"><h2 className="text-xl font-bold">{title}</h2><button onClick={onClose} className="text-2xl text-slate-500">×</button></div>{children}
    </section>
  </div>;
}

