import { useState, useRef, useEffect } from "react";
import { Terminal as TerminalIcon, Sparkles, Play, Trash2, Cpu, Check, Copy } from "lucide-react";
import { getSwarmRecommendations, getRecommendationDetails } from "../utils/swarmUtils";

export default function DirectQuery() {
  const [prompt, setPrompt] = useState("");
  const [targetId, setTargetId] = useState("");
  const [loading, setLoading] = useState(false);
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [copiedId, setCopiedId] = useState(null);
  const [result, setResult] = useState(null);
  const [showReasoning, setShowReasoning] = useState(false);
  
  const terminalEndRef = useRef(null);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [terminalLogs]);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(text);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClearLogs = () => {
    setTerminalLogs([]);
    setResult(null);
    setShowReasoning(false);
  };

  const extractThinking = (monologue) => {
    if (!monologue) return "No reasoning recorded.";
    const thinkMatch = monologue.match(/<thinking>([\s\S]*?)<\/thinking>/);
    if (thinkMatch && thinkMatch[1]) {
      return thinkMatch[1].trim();
    }
    return monologue.trim();
  };



  const handleRunSandbox = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || !targetId.trim()) return;

    setLoading(true);
    setResult(null);
    setTerminalLogs([
      `user@swarm-act-sandbox:~$ python orchestrate.py --target ${targetId} --prompt "${prompt.substring(0, 40)}..."`,
      "🛰️ [SYSTEM] Initializing unified multi-agent orchestrator connection...",
      "🔗 [SYSTEM] Handshake established with Modal endpoint `/v1/swarm/process`."
    ]);

    const startTime = Date.now();
    
    // Simulate log ticks
    const ticks = [
      { delay: 3000, log: "⚡ [ALPHA] Invoking SFT rating and sentiment extractor node..." },
      { delay: 6000, log: "📝 [ALPHA] Analysis of historical review variance complete. Predicted rating generated." },
      { delay: 9000, log: "🧠 [SYSTEM] Passing Alpha extraction insights into Beta reasoning node..." },
      { delay: 12000, log: "🔮 [BETA] Invoking GRPO alignment reasoning node... Reading review databases." },
      { delay: 15000, log: "🧠 [BETA] Computing monologue reasoning paths... Formatting outputs." }
    ];

    const timeouts = ticks.map(({ delay, log }) => 
      setTimeout(() => {
        setTerminalLogs((prev) => [...prev, log]);
      }, delay)
    );

    try {
      const response = await fetch(
        "https://wakamateservices--bct-swarm-orchestrator-swarm-endpoint.modal.run/v1/swarm/process",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt, target_item_id: targetId })
        }
      );

      // Clear simulated timeouts
      timeouts.forEach(clearTimeout);

      const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

      if (response.ok) {
        const data = await response.json();
        setResult(data);
        
        // Extract monologue
        const monologue = data.beta_reasoning?.raw_monologue || "";
        const recommendationsList = getSwarmRecommendations(data, prompt, targetId);
        const recommendationCount = recommendationsList.length;
        const hasSalvagedItems = recommendationsList.some(x => x.isSalvaged);
        const rawPayloadCount = data.beta_reasoning?.payload?.ranked_items?.length || 0;
        const isCognitiveSalvageTriggered = hasSalvagedItems || rawPayloadCount === 0 || 
          recommendationsList.some(x => x.id === targetId && !data.beta_reasoning?.payload?.ranked_items?.includes(targetId));

        const finalLogs = [
          ...terminalLogs,
          `✅ [SUCCESS] Orchestration complete in ${elapsed}s.`,
          `✨ [ALPHA] Predicted Rating: ${data.alpha_extraction?.predicted_rating || "N/A"} Stars`,
          `💬 [ALPHA] Predicted Review Summary: "${data.alpha_extraction?.predicted_review?.substring(0, 80) || "N/A"}..."`,
          `🧠 [BETA] Monologue length: ${monologue.length} chars.`
        ];

        if (isCognitiveSalvageTriggered && recommendationCount > 0) {
          finalLogs.push(`✨ [SYSTEM-RECOVERY] Swarm Cognitive Salvage: Recovered ${recommendationCount} high-fidelity recommendation code(s) from monologue reasoning context!`);
          finalLogs.push(`✨ [SYSTEM-RECOVERY] Salvaged ID(s): ${recommendationsList.map(x => x.id).join(", ")}`);
          finalLogs.push(`📦 Saved ${recommendationCount} salvaged product recommendation codes.`);
        } else if (recommendationCount > 0) {
          finalLogs.push(`📦 Saved ${recommendationCount} product recommendation codes.`);
        } else {
          finalLogs.push("📦 Saved 0 product recommendation codes.");
        }

        setTerminalLogs(finalLogs);
      } else {
        const errText = await response.text();
        setTerminalLogs((prev) => [
          ...prev,
          `❌ [ERROR] Orchestrator responded with HTTP ${response.status}: ${errText}`
        ]);
      }
    } catch (err) {
      timeouts.forEach(clearTimeout);
      setTerminalLogs((prev) => [
        ...prev,
        `❌ [EXCEPTION] Network request failed: ${err.message || "Is endpoint alive?"}`
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Direct Query Sandbox</h1>
        <p className="text-sm text-neutral-500 mt-0.5 font-sans">
          Interactively test custom recommendation queries against the live Modal sequential swarm. View raw execution Trace logs.
        </p>
      </div>

      {/* Grid splits */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Form Inputs (Left) */}
        <div className="lg:col-span-5 bg-[#111111] border border-neutral-800 rounded-xl p-5 flex flex-col justify-between">
          <form onSubmit={handleRunSandbox} className="space-y-4">
            <div>
              <label className="block text-[10px] uppercase tracking-wider text-neutral-400 mb-1.5 font-semibold select-none">
                Target Yelp Item ID
              </label>
              <input
                type="text"
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                placeholder="e.g. ramen_shop_992, cafe_cafe_883"
                required
                disabled={loading}
                className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-neutral-600 outline-none focus:border-violet-600 transition-colors font-mono disabled:opacity-50"
              />
            </div>

            <div>
              <label className="block text-[10px] uppercase tracking-wider text-neutral-400 mb-1.5 font-semibold select-none">
                Custom User Preference Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Type a custom consumer profile preference (e.g. wants gluten-free, spicy, highly rated, quick service...)"
                required
                rows={7}
                disabled={loading}
                className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-neutral-600 outline-none focus:border-violet-600 transition-colors resize-none leading-relaxed font-sans disabled:opacity-50"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !prompt.trim() || !targetId.trim()}
              className="w-full bg-violet-600 hover:bg-violet-700 disabled:bg-neutral-800 disabled:text-neutral-500 text-white font-semibold text-sm py-2.5 rounded-lg flex items-center justify-center gap-2 cursor-pointer transition-all border border-violet-500/20 disabled:border-transparent select-none"
            >
              {loading ? (
                <>
                  <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                  Orchestrating...
                </>
              ) : (
                <>
                  <Play size={14} />
                  Run Sandbox Query
                </>
              )}
            </button>
          </form>

          {/* Model info tags */}
          <div className="border-t border-neutral-800/80 pt-4 mt-6 flex flex-wrap gap-2">
            <span className="text-[9px] font-mono px-2 py-0.5 rounded border border-neutral-800 bg-neutral-900 text-neutral-400 flex items-center gap-1 select-none">
              <Cpu size={8} /> Alpha: SFT
            </span>
            <span className="text-[9px] font-mono px-2 py-0.5 rounded border border-neutral-800 bg-neutral-900 text-neutral-400 flex items-center gap-1 select-none">
              <Cpu size={8} /> Beta: GRPO
            </span>
            <span className="text-[9px] font-mono px-2 py-0.5 rounded border border-neutral-800 bg-neutral-900 text-neutral-400 flex items-center gap-1 select-none">
              🌐 CORS: Enabled
            </span>
          </div>
        </div>

        {/* Monospace Output Terminal (Right) */}
        <div className="lg:col-span-7 bg-[#070707] border border-neutral-800 rounded-xl overflow-hidden flex flex-col h-[460px] shadow-inner">
          {/* Terminal Header */}
          <div className="bg-[#0f0f0f] border-b border-neutral-800 px-4 py-3 flex items-center justify-between select-none">
            <div className="flex items-center gap-2">
              <div className="flex gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
              </div>
              <span className="text-[10px] font-mono text-neutral-500 font-semibold ml-2 flex items-center gap-1">
                <TerminalIcon size={12} /> stdout -- Trace Sandbox
              </span>
            </div>
            {terminalLogs.length > 0 && (
              <button
                onClick={handleClearLogs}
                className="text-neutral-500 hover:text-rose-400 transition-colors"
                title="Clear Terminal stdout"
              >
                <Trash2 size={13} />
              </button>
            )}
          </div>

          {/* Terminal Logs Viewport */}
          <div className="flex-1 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed text-neutral-300 space-y-2.5 scrollbar-hide">
            {terminalLogs.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-neutral-600 px-4">
                <TerminalIcon size={24} className="opacity-40 mb-3" />
                <span>Sandbox idle. Command ready.</span>
                <span className="text-[10px] text-neutral-700 mt-1">
                  Fill target Yelp ID, write preference prompt, and trigger sandbox query.
                </span>
              </div>
            ) : (
              <>
                {terminalLogs.map((log, i) => (
                  <div key={i} className="whitespace-pre-wrap select-text selection:bg-violet-500/30">
                    {log.startsWith("user@") ? (
                      <span className="text-violet-400 font-bold">{log}</span>
                    ) : log.startsWith("❌") ? (
                      <span className="text-rose-400">{log}</span>
                    ) : log.startsWith("✅") ? (
                      <span className="text-emerald-400 font-semibold">{log}</span>
                    ) : log.startsWith("✨") || log.startsWith("💬") ? (
                      <span className="text-amber-400/90">{log}</span>
                    ) : (
                      <span className="text-neutral-300">{log}</span>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex items-center gap-2 text-violet-400 animate-pulse pt-1">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-violet-400" />
                    <span>sequential worker running endpoint thread...</span>
                  </div>
                )}
                <div ref={terminalEndRef} />
              </>
            )}
          </div>

          {/* Inline Sandbox Results Preview (Visible upon success) */}
          {result && (
            <div className="border-t border-neutral-800 bg-[#0e0e0e] p-4 flex flex-col gap-3 animate-in slide-in-from-bottom duration-250 overflow-y-auto max-h-[380px] scrollbar-hide">
              <div className="flex items-center justify-between select-none">
                <div className="flex items-center gap-2">
                  <Sparkles size={12} className="text-violet-400" />
                  <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500 font-mono">
                    ⚡ Swarm Yield Recommendations
                  </span>
                </div>
                <button
                  onClick={() => setShowReasoning(!showReasoning)}
                  className="text-[9px] font-mono text-violet-400 hover:text-violet-300 transition-colors flex items-center gap-1 cursor-pointer bg-violet-950/40 border border-violet-850 px-2 py-0.5 rounded select-none font-semibold"
                >
                  {showReasoning ? "Hide Agent Reasoning" : "Show Agent Reasoning"}
                </button>
              </div>

              {showReasoning && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 border-b border-neutral-800 pb-3 mb-1 animate-in fade-in duration-200">
                  {/* SFT Review Block */}
                  <div className="space-y-1.5">
                    <span className="text-[9px] uppercase tracking-wider font-semibold text-neutral-500 font-mono flex items-center gap-1.5 select-none">
                      👤 Synthesized Customer Persona Review (Alpha)
                    </span>
                    <div className="bg-[#111111] border border-neutral-850 p-2.5 rounded-lg text-xs leading-relaxed text-neutral-300 font-sans">
                      <div className="flex text-amber-400 mb-1.5 select-none">
                        {Array.from({ length: result.alpha_extraction?.predicted_rating || 5 }).map((_, i) => (
                          <span key={i} className="text-[10px]">★</span>
                        ))}
                      </div>
                      <blockquote className="italic border-l border-violet-500/60 pl-2 text-[10.5px] select-text">
                        "{result.alpha_extraction?.predicted_review || "No review generated."}"
                      </blockquote>
                    </div>
                  </div>

                  {/* GRPO Monologue Box */}
                  <div className="space-y-1.5">
                    <span className="text-[9px] uppercase tracking-wider font-semibold text-neutral-500 font-mono flex items-center gap-1.5 select-none">
                      🧠 Agent Beta Monologue
                    </span>
                    <div className="bg-[#070707] border border-neutral-850 p-2.5 rounded-lg text-[10px] font-mono leading-relaxed text-neutral-400 h-[100px] overflow-y-auto whitespace-pre-wrap scrollbar-hide select-text">
                      {extractThinking(result.beta_reasoning?.raw_monologue)}
                    </div>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 gap-2 select-none">
                {getSwarmRecommendations(result, prompt, targetId).length > 0 ? (
                  getSwarmRecommendations(result, prompt, targetId).map((salvagedItem, idx) => {
                    const displayId = salvagedItem.id;
                    const details = getRecommendationDetails(displayId, prompt);
                    return (
                      <div
                        key={idx}
                        className={`bg-[#111111] border ${salvagedItem.isSalvaged ? 'border-violet-500/40 bg-gradient-to-r from-violet-950/10 to-neutral-900/40 shadow-md shadow-violet-950/5' : 'border-neutral-850'} rounded-lg p-3 hover:border-violet-500/30 transition-colors flex flex-col gap-1.5 relative group`}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="flex flex-wrap items-center gap-1 mb-0.5 select-none">
                              <span className="text-[8px] uppercase tracking-wider font-mono text-violet-400 bg-violet-950/45 px-1.5 py-0.5 rounded border border-violet-800/30 inline-block">
                                {details.tag}
                              </span>
                              {salvagedItem.isSalvaged && (
                                <span className="text-[7px] uppercase tracking-wider font-mono text-emerald-400 bg-emerald-950/45 px-1.5 py-0.5 rounded border border-emerald-800/30 inline-block animate-pulse">
                                  ✨ Cognitive Salvage
                                </span>
                              )}
                            </div>
                            <h4 className="text-white font-semibold text-xs font-sans">
                              {details.title}
                            </h4>
                          </div>
                          <div className="flex flex-col items-end gap-0.5 select-none">
                            <span className="text-[9px] text-neutral-500 font-mono">#{idx + 1}</span>
                            <div className="flex text-amber-400">
                              {Array.from({ length: details.rating }).map((_, i) => (
                                <span key={i} className="text-[9px]">★</span>
                              ))}
                            </div>
                          </div>
                        </div>
                        
                        <p className="text-[10px] text-neutral-400 leading-relaxed font-sans">
                          {details.reason}
                        </p>
                        
                        <div className="flex justify-between items-center border-t border-neutral-900/60 pt-1.5 select-none">
                          <span className="text-[8px] font-mono text-neutral-600 bg-neutral-950 px-1.5 py-0.5 rounded border border-neutral-850 truncate max-w-[150px]">
                            {displayId}
                          </span>
                          <button
                            onClick={() => copyToClipboard(displayId)}
                            className="text-[8px] font-mono text-neutral-500 hover:text-white transition-colors flex items-center gap-1 cursor-pointer bg-neutral-900 border border-neutral-800 px-1.5 py-0.5 rounded"
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
                      </div>
                    );
                  })
                ) : (
                  <span className="text-[10px] text-neutral-600 italic">No recommendations yielded.</span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
