import { useState, useEffect } from "react";
import { Terminal, ShieldCheck, HelpCircle, CornerDownRight, Check, Copy, Activity, Sparkles } from "lucide-react";

export default function ExecutionRuns({ runs = [], onGoToConsole }) {
  const [selectedRunId, setSelectedRunId] = useState(() => {
    return runs.length > 0 ? runs[0].id : null;
  });
  const [copiedId, setCopiedId] = useState(null);

  // Sync selection if list updates and nothing is selected
  useEffect(() => {
    if (runs.length > 0 && !selectedRunId) {
      setSelectedRunId(runs[0].id);
    }
  }, [runs, selectedRunId]);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const selectedRun = runs.find((r) => r.id === selectedRunId);

  const getStatusColor = (status) => {
    switch (status) {
      case "Success":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "Failed":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      case "Running":
        return "bg-violet-500/10 text-violet-400 border-violet-500/20";
      default:
        return "bg-neutral-500/10 text-neutral-400 border-neutral-500/20";
    }
  };

  const renderStars = (rating) => {
    const num = Math.min(5, Math.max(0, parseInt(rating || 0)));
    return (
      <div className="flex gap-0.5 text-amber-400">
        {Array.from({ length: 5 }).map((_, i) => (
          <span key={i} className="text-xs">
            {i < num ? "★" : "☆"}
          </span>
        ))}
      </div>
    );
  };

  const extractThinking = (monologue) => {
    if (!monologue) return "No reasoning monologue recorded.";
    const thinkMatch = monologue.match(/<thinking>([\s\S]*?)<\/thinking>/);
    if (thinkMatch && thinkMatch[1]) {
      return thinkMatch[1].trim();
    }
    return monologue.trim();
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
    <div className="h-full flex flex-col space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Execution Runs</h1>
        <p className="text-sm text-neutral-500 mt-0.5 font-sans">
          Audit previous multi-agent execution steps, raw outputs, and reasoning monologue logs.
        </p>
      </div>

      {runs.length === 0 ? (
        <div className="flex-1 border border-neutral-800 bg-[#111111] rounded-xl flex flex-col items-center justify-center text-center p-12 h-[420px]">
          <div className="w-12 h-12 rounded-xl bg-neutral-800/40 border border-neutral-700/60 flex items-center justify-center mb-5 shadow-inner select-none">
            <Activity size={20} className="text-neutral-500" />
          </div>
          <h3 className="text-white font-semibold text-base mb-2">No execution runs recorded</h3>
          <p className="text-neutral-500 text-sm max-w-sm leading-relaxed mb-6 font-sans">
            You haven't run any Swarms yet. Head over to the Swarm Console or Dataset Library to launch your first execution run.
          </p>
          <button
            onClick={onGoToConsole}
            className="bg-neutral-800 hover:bg-neutral-700 text-white text-xs font-semibold px-4 py-2 rounded-lg border border-neutral-700 transition-colors cursor-pointer select-none"
          >
            Go to Console
          </button>
        </div>
      ) : (
        <div className="flex-1 grid grid-cols-12 border border-neutral-800 rounded-xl overflow-hidden h-[540px] items-stretch">
          {/* Runs Sidebar Timeline (Left 4 cols) */}
          <div className="col-span-4 border-r border-neutral-800 bg-[#0d0d0d] flex flex-col overflow-hidden h-full">
            <div className="px-4 py-3 border-b border-neutral-800 bg-[#0e0e0e] text-[10px] uppercase font-bold tracking-wider text-neutral-500 select-none">
              Runs Pipeline History ({runs.length})
            </div>
            <div className="flex-1 overflow-y-auto divide-y divide-neutral-900 scrollbar-hide">
              {runs.map((run) => {
                const isSelected = run.id === selectedRunId;
                return (
                  <div
                    key={run.id}
                    onClick={() => setSelectedRunId(run.id)}
                    className={`px-4 py-3.5 cursor-pointer text-left transition-colors flex flex-col gap-2
                      ${isSelected ? "bg-neutral-800/35 border-l-2 border-violet-500" : "hover:bg-neutral-800/10"}`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-semibold text-sm text-white truncate max-w-[140px] group-hover:text-violet-400">
                        {run.name}
                      </span>
                      <span className="text-[9px] font-mono text-neutral-500 shrink-0">
                        {getFormattedTime(run.timestamp)}
                      </span>
                    </div>

                    <div className="flex items-center justify-between gap-1.5 select-none">
                      <span className="text-[10px] font-mono text-neutral-400 bg-neutral-900 border border-neutral-850 px-1 py-0.5 rounded truncate max-w-[130px]">
                        {run.target_item_id}
                      </span>
                      <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono border ${getStatusColor(run.status)}`}>
                        {run.status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Runs Details stdout Viewer (Right 8 cols) */}
          <div className="col-span-8 bg-[#070707] flex flex-col overflow-hidden h-full">
            {selectedRun ? (
              <>
                {/* Console header */}
                <div className="px-5 py-3.5 border-b border-neutral-850 bg-[#0f0f0f] flex items-center justify-between select-none">
                  <div className="flex items-center gap-2">
                    <Terminal size={14} className="text-violet-400 animate-pulse" />
                    <span className="text-[10px] font-mono text-neutral-400 uppercase tracking-widest font-bold">
                      Swarm Execution stdout Trace
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-[10px] font-mono text-neutral-500">
                    <span>TIMING: {selectedRun.elapsedTime ? `${selectedRun.elapsedTime}s` : "N/A"}</span>
                    <span>ID: {selectedRun.id}</span>
                  </div>
                </div>

                {/* Console Log Viewport */}
                <div className="flex-1 overflow-y-auto p-6 font-mono text-[11px] leading-relaxed text-neutral-300 space-y-5 scrollbar-hide select-text selection:bg-violet-500/30">
                  {/* Prompt Block */}
                  <div className="space-y-1 bg-neutral-900/20 border border-neutral-850 rounded-lg p-3">
                    <span className="text-[10px] uppercase font-bold text-neutral-500 tracking-wide block">
                      📥 Swarm Input Prompt
                    </span>
                    <p className="text-neutral-300 font-sans text-xs leading-relaxed">
                      {selectedRun.prompt}
                    </p>
                  </div>

                  {/* Beta Monologue Reasoning (Monospace) */}
                  {selectedRun.status === "Success" && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between border-b border-neutral-850 pb-1.5 text-neutral-500 select-none">
                        <span className="text-[10px] uppercase font-bold tracking-wide flex items-center gap-1">
                          🧠 Agent Beta Reasoning Monologue
                        </span>
                        <span className="text-[9px]">SIZE: {selectedRun.beta_reasoning?.raw_monologue?.length || 0} characters</span>
                      </div>
                      <div className="bg-[#0b0b0b] border border-neutral-850 rounded-lg p-4 max-h-[220px] overflow-y-auto whitespace-pre-wrap leading-relaxed text-neutral-200 scrollbar-hide">
                        {extractThinking(selectedRun.beta_reasoning?.raw_monologue)}
                      </div>
                    </div>
                  )}

                  {/* SFT Agent Alpha Review Insight */}
                  {selectedRun.status === "Success" && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between border-b border-neutral-850 pb-1.5 text-neutral-500 select-none">
                        <span className="text-[10px] uppercase font-bold tracking-wide flex items-center gap-1">
                          💬 Agent Alpha Review Synthesis
                        </span>
                        <span>{renderStars(selectedRun.alpha_extraction?.predicted_rating)}</span>
                      </div>
                      <blockquote className="bg-neutral-950 border-l-2 border-violet-500 rounded-r p-3 italic text-neutral-300 font-sans text-xs leading-relaxed">
                        "{selectedRun.alpha_extraction?.predicted_review || "No review content synthesized."}"
                      </blockquote>
                    </div>
                  )}

                  {/* Recommendations badge display */}
                  {selectedRun.status === "Success" && (
                    <div className="space-y-2">
                      <div className="border-b border-neutral-850 pb-1.5 text-neutral-500 select-none text-[10px] uppercase font-bold tracking-wide flex items-center gap-1">
                        <Sparkles size={11} className="text-violet-400" /> Final Yelp Recommendations
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {selectedRun.beta_reasoning?.payload?.ranked_items && selectedRun.beta_reasoning.payload.ranked_items.length > 0 ? (
                          selectedRun.beta_reasoning.payload.ranked_items.map((item, idx) => {
                            const itemId = typeof item === 'object' && item !== null ? (item.item_id || item.ground_truth_item_id) : item;
                            const displayId = typeof itemId === 'string' ? itemId : JSON.stringify(item);
                            return (
                              <div
                                key={idx}
                                onClick={() => copyToClipboard(displayId)}
                                className="group flex items-center gap-1.5 bg-[#141414] border border-neutral-850 hover:border-violet-500/50 hover:bg-neutral-900 px-2.5 py-1.5 rounded-lg text-xs cursor-pointer transition-all text-neutral-300"
                              >
                                <CornerDownRight size={10} className="text-neutral-500 group-hover:text-violet-400" />
                                <span>{displayId}</span>
                                {copiedId === displayId ? (
                                  <Check size={10} className="text-emerald-400" />
                                ) : (
                                  <Copy size={10} className="text-neutral-600 group-hover:text-neutral-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                                )}
                              </div>
                            );
                          })
                        ) : (
                          <div className="text-xs text-neutral-500 italic">No recommendations.</div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Trace execution logs */}
                  <div className="space-y-2">
                    <div className="border-b border-neutral-850 pb-1.5 text-neutral-500 select-none text-[10px] uppercase font-bold tracking-wide">
                      📜 Execution Trace Log Pipeline
                    </div>
                    <div className="space-y-1.5 text-[10px] text-neutral-400">
                      {(selectedRun.logs || []).map((log, idx) => (
                        <div key={idx} className="flex gap-2 items-start">
                          <span className="text-neutral-600 select-none">[{idx + 1}]</span>
                          <span className={idx === (selectedRun.logs.length - 1) ? "text-violet-400" : "text-neutral-300"}>
                            {log}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center text-neutral-600 px-4">
                <Terminal size={24} className="opacity-40 mb-3" />
                <span>Select a Swarm Run to trace pipeline stdout logs.</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
