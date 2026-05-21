export default function StatCard({ label, value, description }) {
  return (
    <div className="bg-[#111111] border border-neutral-800 rounded-lg px-6 py-5 flex-1 min-w-0">
      <p className="text-[10px] uppercase tracking-widest text-neutral-500 font-semibold mb-2">{label}</p>
      <p className="text-3xl font-semibold text-white mb-1">{value}</p>
      <p className="text-xs text-neutral-500">{description}</p>
    </div>
  );
}
