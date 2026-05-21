import { Sparkles, Terminal, ArrowRight } from "lucide-react";
import { useState } from "react";

const columns = [
  { label: "Swarm Run" },
  { label: "Target Item" },
  { label: "Customer Prompt" },
  { label: "Status" },
  { label: "Alpha Rating" },
  { label: "Recommendations" },
  { label: "Created" }
];

export default function EvaluationsTable({ runs = [], onSelectRun, onNew }) {
  const [search, setSearch] = useState("");

  const filteredRuns = runs.filter(
    (run) =>
      run.name.toLowerCase().includes(search.toLowerCase()) ||
      (run.target_item_id && run.target_item_id.toLowerCase().includes(search.toLowerCase())) ||
      (run.prompt && run.prompt.toLowerCase().includes(search.toLowerCase()))
  );

  const getStatusBadge = (status) => {
    switch (status) {
      case "Success":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Success
          </span>
        );
      case "Failed":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            Failed
          </span>
        );
      case "Running":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold bg-violet-500/10 text-violet-400 border border-violet-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
            Running
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold bg-neutral-500/10 text-neutral-400 border border-neutral-500/20">
            Unknown
          </span>
        );
    }
  };

  const renderStars = (rating) => {
    if (rating === undefined || rating === null) return <span className="text-neutral-600 font-sans">-</span>;
    const num = Math.min(5, Math.max(0, parseInt(rating || 0)));
    return (
      <div className="flex text-amber-400 text-xs">
        {Array.from({ length: 5 }).map((_, i) => (
          <span key={i}>{i < num ? "★" : "☆"}</span>
        ))}
      </div>
    );
  };

  const getFormattedTime = (timestamp) => {
    if (!timestamp) return "Just now";
    try {
      const diffMs = Date.now() - new Date(timestamp).getTime();
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return "Just now";
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      return new Date(timestamp).toLocaleDateString();
    } catch {
      return "Recently";
    }
  };

  return (
    <div className="bg-[#111111] border border-neutral-800 rounded-lg overflow-hidden">
      {/* Search */}
      <div className="border-b border-neutral-800 px-4 py-3 bg-[#0d0d0d]">
        <div className="flex items-center gap-2 text-neutral-500">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
            <path
              d="M10 6.5C10 8.43 8.43 10 6.5 10C4.57 10 3 8.43 3 6.5C3 4.57 4.57 3 6.5 3C8.43 3 10 4.57 10 6.5ZM9.47 10.18C8.73 10.69 7.85 11 6.9 11C4.52 11 2.4 9.24 2.4 6.5C2.4 3.76 4.52 2 6.5 2C8.48 2 10.6 3.76 10.6 6.5C10.6 7.45 10.29 8.33 9.78 9.07L12.85 12.15L12.15 12.85L9.47 10.18Z"
              fill="currentColor"
              fillRule="evenodd"
              clipRule="evenodd"
            />
          </svg>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by swarm run name, prompt, or target ID..."
            className="bg-transparent text-sm text-neutral-300 placeholder-neutral-600 outline-none w-full font-sans"
          />
        </div>
      </div>

      {/* Table header */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-800 bg-[#0e0e0e] select-none">
              {columns.map(({ label }) => (
                <th
                  key={label}
                  className="text-left px-4 py-3.5 text-xs text-neutral-400 font-semibold tracking-wider uppercase whitespace-nowrap"
                >
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-850">
            {filteredRuns.length === 0 ? (
              <tr>
                <td colSpan={columns.length}>
                  <EmptyState onNew={onNew} />
                </td>
              </tr>
            ) : (
              filteredRuns.map((run) => (
                <tr
                  key={run.id}
                  onClick={() => onSelectRun(run)}
                  className="hover:bg-neutral-800/20 active:bg-neutral-800/40 cursor-pointer transition-colors group"
                >
                  {/* Name */}
                  <td className="px-4 py-4 font-semibold text-white truncate max-w-[150px]">
                    {run.name}
                  </td>
                  {/* Target Item ID */}
                  <td className="px-4 py-4 font-mono text-xs text-neutral-400">
                    {run.target_item_id}
                  </td>
                  {/* Prompt */}
                  <td className="px-4 py-4 text-xs text-neutral-500 font-sans truncate max-w-[220px]">
                    {run.prompt}
                  </td>
                  {/* Status */}
                  <td className="px-4 py-4 whitespace-nowrap">
                    {getStatusBadge(run.status)}
                  </td>
                  {/* Alpha Rating */}
                  <td className="px-4 py-4 whitespace-nowrap">
                    {run.status === "Success"
                      ? renderStars(run.alpha_extraction?.predicted_rating)
                      : <span className="text-neutral-600">-</span>}
                  </td>
                  {/* Recs Count */}
                  <td className="px-4 py-4 font-mono text-xs text-neutral-400 whitespace-nowrap">
                    {run.status === "Success" && run.beta_reasoning?.payload?.ranked_items
                      ? `${run.beta_reasoning.payload.ranked_items.length} items`
                      : run.status === "Running"
                      ? "evaluating..."
                      : "-"}
                  </td>
                  {/* Created */}
                  <td className="px-4 py-4 text-xs text-neutral-400 font-mono whitespace-nowrap">
                    <div className="flex items-center justify-between gap-2">
                      <span>{getFormattedTime(run.timestamp)}</span>
                      <ArrowRight size={14} className="text-neutral-600 opacity-0 group-hover:opacity-100 group-hover:text-violet-400 translate-x-[-4px] group-hover:translate-x-0 transition-all shrink-0" />
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function EmptyState({ onNew }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center bg-[#111111]">
      <div className="w-12 h-12 rounded-xl bg-neutral-800/40 border border-neutral-700/60 flex items-center justify-center mb-5 shadow-inner">
        <Terminal size={20} className="text-violet-400 animate-pulse" />
      </div>
      <h3 className="text-white font-semibold text-base mb-2">Launch your first Swarm Orchestrator</h3>
      <p className="text-neutral-500 text-sm max-w-sm leading-relaxed mb-6 font-sans">
        Trigger our multi-agent langgraph swarm on Yelp data to synthesize rating insights and filter high-fidelity product recommendations.
      </p>
      <button
        onClick={onNew}
        className="bg-violet-600 hover:bg-violet-700 active:bg-violet-850 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition-colors border border-violet-500/20 flex items-center gap-2 shadow-lg shadow-violet-600/10"
      >
        <Sparkles size={14} />
        New Swarm Run
      </button>
    </div>
  );
}
