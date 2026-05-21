import { BarChart2, ChevronsUpDown, ListFilter } from "lucide-react";

const columns = [
  { label: "Name", sortable: true },
  { label: "Environment", filterable: true },
  { label: "Model", filterable: true },
  { label: "Status", sortable: true, filterable: true },
  { label: "Avg Reward", sortable: true },
  { label: "Samples" },
  { label: "Created", sortable: true },
];

export default function EvaluationsTable({ onNew }) {
  return (
    <div className="bg-[#111111] border border-neutral-800 rounded-lg overflow-hidden">
      {/* Search */}
      <div className="border-b border-neutral-800 px-4 py-3">
        <div className="flex items-center gap-2 text-neutral-500">
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
            <path d="M10 6.5C10 8.43 8.43 10 6.5 10C4.57 10 3 8.43 3 6.5C3 4.57 4.57 3 6.5 3C8.43 3 10 4.57 10 6.5ZM9.47 10.18C8.73 10.69 7.85 11 6.9 11C4.52 11 2.4 9.24 2.4 6.5C2.4 3.76 4.52 2 6.5 2C8.48 2 10.6 3.76 10.6 6.5C10.6 7.45 10.29 8.33 9.78 9.07L12.85 12.15L12.15 12.85L9.47 10.18Z" fill="currentColor" fillRule="evenodd" clipRule="evenodd" />
          </svg>
          <input
            type="text"
            placeholder="Search by name or model..."
            className="bg-transparent text-sm text-neutral-300 placeholder-neutral-600 outline-none w-full"
          />
        </div>
      </div>

      {/* Table header */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-800">
              <th className="w-10 px-4 py-3">
                <input type="checkbox" className="accent-violet-600 w-3.5 h-3.5" />
              </th>
              {columns.map(({ label, sortable, filterable }) => (
                <th
                  key={label}
                  className="text-left px-3 py-3 text-xs text-neutral-400 font-medium whitespace-nowrap"
                >
                  <span className="flex items-center gap-1">
                    {label}
                    {sortable && <ChevronsUpDown size={12} className="text-neutral-600" />}
                    {filterable && <ListFilter size={11} className="text-neutral-600" />}
                  </span>
                </th>
              ))}
              <th className="w-10" />
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={columns.length + 2}>
                <EmptyState onNew={onNew} />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function EmptyState({ onNew }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
      <div className="w-12 h-12 rounded-xl bg-neutral-800 flex items-center justify-center mb-5">
        <BarChart2 size={22} className="text-neutral-300" />
      </div>
      <h3 className="text-white font-semibold text-base mb-2">Run your first evaluation</h3>
      <p className="text-neutral-500 text-sm max-w-xs leading-relaxed mb-6">
        Measure how models perform across environments, using our hosted infrastructure for inference, sandboxes, and more.
      </p>
      <button
        onClick={onNew}
        className="bg-neutral-800 hover:bg-neutral-700 text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors border border-neutral-700"
      >
        New Evaluation
      </button>
    </div>
  );
}
