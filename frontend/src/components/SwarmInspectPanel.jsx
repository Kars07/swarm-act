import { X, Copy, Check, Terminal, Cpu, Sparkles, CornerDownRight } from "lucide-react";
import { useState } from "react";

export default function SwarmInspectPanel({ run, onClose }) {
  const [copiedId, setCopiedId] = useState(null);

  if (!run) return null;

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

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
          <span key={i} className="text-sm font-semibold">
            {i < num ? "★" : "☆"}
          </span>
        ))}
      </div>
    );
  };

  // Helper to extract clean thinking part or display the raw monologue
  const extractThinking = (monologue) => {
    if (!monologue) return "No reasoning recorded.";
    
    // Check if monologue has <thinking> tags
    const thinkMatch = monologue.match(/<thinking>([\s\S]*?)<\/thinking>/);
    if (thinkMatch && thinkMatch[1]) {
      return thinkMatch[1].trim();
    }
    
    return monologue.trim();
  };

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-[550px] bg-[#0c0c0c] border-l border-neutral-800 shadow-2xl flex flex-col h-full overflow-hidden animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-neutral-800 bg-[#0e0e0e]">
        <div>
          <span className="text-[10px] tracking-widest uppercase font-semibold text-neutral-500">
            Swarm Orchestrator Run
          </span>
          <h2 className="text-white font-semibold text-base mt-0.5 truncate max-w-[380px]">
            {run.name}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="text-neutral-500 hover:text-white hover:bg-neutral-800/60 p-2 rounded-lg transition-all"
        >
          <X size={16} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 scrollbar-hide">
        {/* Status & Metadata */}
        <div className="bg-[#111111] border border-neutral-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-400 font-medium">Status</span>
            <span
              className={`text-xs px-2.5 py-0.5 rounded-full border font-medium ${getStatusColor(
                run.status
              )}`}
            >
              {run.status === "Running" && (
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse mr-1.5" />
              )}
              {run.status}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-400 font-medium">Target ID</span>
            <span className="text-xs font-mono text-neutral-300 bg-neutral-900 border border-neutral-800 px-1.5 py-0.5 rounded">
              {run.target_item_id || "N/A"}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-neutral-400 font-medium">Execution Time</span>
            <span className="text-xs font-mono text-neutral-300">
              {run.elapsedTime ? `${run.elapsedTime}s` : "N/A"}
            </span>
          </div>

          <div className="border-t border-neutral-800/80 pt-3">
            <span className="text-[10px] uppercase font-semibold tracking-wider text-neutral-500 block mb-1">
              Customer Prompt
            </span>
            <p className="text-xs text-neutral-300 font-sans leading-relaxed whitespace-pre-wrap">
              {run.prompt}
            </p>
          </div>
        </div>

        {/* Loading/Execution logs */}
        {run.status === "Running" && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Terminal size={14} className="text-violet-400" />
              <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                Live Execution Logs
              </h3>
            </div>
            <div className="bg-[#080808] border border-neutral-800 rounded-lg p-4 font-mono text-[11px] text-neutral-400 space-y-2 h-[280px] overflow-y-auto">
              {(run.logs || []).map((log, i) => (
                <div key={i} className="flex gap-2 items-start animate-fade-in">
                  <span className="text-neutral-600 select-none">[{i + 1}]</span>
                  <span className={i === (run.logs.length - 1) ? "text-violet-400" : "text-neutral-300"}>
                    {log}
                  </span>
                </div>
              ))}
              <div className="flex gap-2 items-center text-violet-400 animate-pulse pt-1">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-violet-400 mr-1" />
                <span>Waiting for next agent node response...</span>
              </div>
            </div>
          </div>
        )}

        {/* Failed details */}
        {run.status === "Failed" && (
          <div className="bg-[#181111] border border-rose-950/45 rounded-lg p-4 space-y-2">
            <h3 className="text-xs font-semibold text-rose-400 uppercase tracking-wider">
              Execution Failure
            </h3>
            <p className="text-xs text-rose-300/85 leading-relaxed font-mono whitespace-pre-wrap">
              {run.error || "Connection to the Modal Orchestrator endpoint timed out or failed to parse. Please check your internet connection or backend server status."}
            </p>
          </div>
        )}

        {/* Success Details */}
        {run.status === "Success" && (
          <>
            {/* Agent Alpha Extraction */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Cpu size={14} className="text-emerald-400" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                  Agent Alpha Review Synthesis
                </h3>
              </div>
              <div className="bg-[#111111] border border-neutral-800 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between border-b border-neutral-800/80 pb-2">
                  <span className="text-xs text-neutral-400 font-medium">Predicted Rating</span>
                  <div>{renderStars(run.alpha_extraction?.predicted_rating)}</div>
                </div>
                <div className="space-y-1.5">
                  <span className="text-[10px] uppercase font-semibold tracking-wider text-neutral-500 block">
                    Synthesized Review Prompt Insight
                  </span>
                  <blockquote className="text-xs text-neutral-300 font-sans italic leading-relaxed border-l-2 border-violet-500 pl-3 py-0.5 bg-neutral-900/40 rounded-r pr-2 whitespace-pre-wrap">
                    "{run.alpha_extraction?.predicted_review || "No review content generated."}"
                  </blockquote>
                </div>
              </div>
            </div>

            {/* Agent Beta Reasoning */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Terminal size={14} className="text-violet-400" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                  Agent Beta Reasoning Monologue
                </h3>
              </div>
              <div className="bg-[#080808] border border-neutral-800 rounded-lg p-4 font-mono text-[11px] leading-relaxed text-neutral-300 h-[220px] overflow-y-auto whitespace-pre-wrap scrollbar-hide">
                <div className="text-neutral-500 select-none pb-2 border-b border-neutral-900/80 mb-2 flex items-center justify-between">
                  <span>🧠 MONOLOGUE READOUT</span>
                  <span>SIZE: {run.beta_reasoning?.raw_monologue?.length || 0} Chars</span>
                </div>
                {extractThinking(run.beta_reasoning?.raw_monologue)}
              </div>
            </div>

            {/* Recommendations */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Sparkles size={14} className="text-violet-400" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                  Swarm Recommendations
                </h3>
              </div>
              <div className="bg-[#111111] border border-neutral-800 rounded-lg p-4 space-y-3">
                <p className="text-xs text-neutral-400 font-sans">
                  The orchestrator returned the following highly relevant items matching the user request:
                </p>
                <div className="flex flex-wrap gap-2">
                  {run.beta_reasoning?.payload?.ranked_items && run.beta_reasoning.payload.ranked_items.length > 0 ? (
                    run.beta_reasoning.payload.ranked_items.map((item, idx) => {
                      const itemId = typeof item === 'object' && item !== null ? (item.item_id || item.ground_truth_item_id) : item;
                      const displayId = typeof itemId === 'string' ? itemId : JSON.stringify(item);
                      
                      return (
                        <div
                          key={idx}
                          onClick={() => copyToClipboard(displayId)}
                          className="group flex items-center gap-2 bg-neutral-900 border border-neutral-800 hover:border-violet-500/50 hover:bg-neutral-800/40 px-3 py-1.5 rounded-lg text-xs font-mono text-neutral-300 cursor-pointer transition-all"
                        >
                          <CornerDownRight size={10} className="text-neutral-500 group-hover:text-violet-400" />
                          <span className="truncate max-w-[200px]">{displayId}</span>
                          {copiedId === displayId ? (
                            <Check size={11} className="text-emerald-400 shrink-0" />
                          ) : (
                            <Copy size={11} className="text-neutral-500 group-hover:text-neutral-300 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
                          )}
                        </div>
                      );
                    })
                  ) : (
                    <div className="text-xs text-neutral-500 italic py-1 pl-1">
                      No items recommended.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
