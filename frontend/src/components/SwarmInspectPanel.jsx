import { X, Copy, Check, Terminal, Cpu, Sparkles, CornerDownRight, Star } from "lucide-react";
import { useState } from "react";
import { getSwarmRecommendations, getRecommendationDetails } from "../utils/swarmUtils";

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
          <span key={i} className="text-xs font-semibold">
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
              <div className="space-y-3">
                {getSwarmRecommendations(run).length > 0 ? (
                  <div className="grid grid-cols-1 gap-3">
                    {getSwarmRecommendations(run).map((salvagedItem, idx) => {
                      const displayId = salvagedItem.id;
                      const details = getRecommendationDetails(displayId, run.prompt || "");
                      
                      return (
                        <div
                          key={idx}
                          className={`bg-[#111111] border ${salvagedItem.isSalvaged ? 'border-violet-500/40 bg-gradient-to-r from-violet-950/10 to-neutral-900/40 shadow-md shadow-violet-950/5' : 'border-neutral-850'} rounded-lg p-3.5 hover:border-violet-500/30 transition-colors flex flex-col gap-2 relative group`}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="flex flex-wrap items-center gap-1.5 mb-1 select-none">
                                <span className="text-[9px] uppercase tracking-wider font-mono text-violet-400 bg-violet-950/45 px-1.5 py-0.5 rounded border border-violet-800/30 inline-block">
                                  {details.tag}
                                </span>
                                {salvagedItem.isSalvaged && (
                                  <span className="text-[8px] uppercase tracking-wider font-mono text-emerald-400 bg-emerald-950/45 px-1.5 py-0.5 rounded border border-emerald-800/30 inline-block animate-pulse">
                                    ✨ Swarm Cognitive Salvage: {salvagedItem.method}
                                  </span>
                                )}
                              </div>
                              <h4 className="text-white font-semibold text-xs font-sans">
                                {details.title}
                              </h4>
                            </div>
                            <div className="flex flex-col items-end gap-1 select-none">
                              <span className="text-[10px] text-neutral-500 font-mono">#{idx + 1}</span>
                              <div className="flex text-amber-400">
                                {Array.from({ length: details.rating }).map((_, i) => (
                                  <span key={i} className="text-[10px]">★</span>
                                ))}
                              </div>
                            </div>
                          </div>
                          
                          <p className="text-[11px] text-neutral-400 leading-relaxed font-sans mt-0.5">
                            {details.reason}
                          </p>
                          
                          <div className="flex justify-between items-center border-t border-neutral-900/60 pt-2 mt-1 select-none">
                            <span className="text-[9px] font-mono text-neutral-600 bg-neutral-950 px-1.5 py-0.5 rounded border border-neutral-850 truncate max-w-[150px]">
                              {displayId}
                            </span>
                            <button
                              onClick={() => copyToClipboard(displayId)}
                              className="text-[9px] font-mono text-neutral-500 hover:text-white transition-colors flex items-center gap-1 cursor-pointer bg-neutral-900 border border-neutral-800 px-2 py-0.5 rounded"
                            >
                              {copiedId === displayId ? (
                                <>
                                  <Check size={8} className="text-emerald-400" />
                                  <span>Copied</span>
                                </>
                              ) : (
                                <>
                                  <Copy size={8} />
                                  <span>Copy ID</span>
                                </>
                              )}
                            </button>
                          </div>
                          {salvagedItem.isSalvaged && (
                            <div className="text-[9px] text-neutral-500/80 font-mono border-t border-neutral-900/30 pt-1.5 select-none">
                              🛡️ Recalibrated client-side from Agent Beta's internal thinking. Zero-shot alignment preserved.
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="bg-[#111111] border border-neutral-800 rounded-lg p-4 text-center text-xs text-neutral-500 italic">
                    No items recommended.
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
