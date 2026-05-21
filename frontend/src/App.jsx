import { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import StatCard from "./components/StatCard";
import EvaluationsTable from "./components/EvaluationsTable";
import NewEvaluationModal from "./components/NewEvaluationModal";
import SwarmInspectPanel from "./components/SwarmInspectPanel";
import PresetLibrary from "./components/PresetLibrary";
import DirectQuery from "./components/DirectQuery";
import ExecutionRuns from "./components/ExecutionRuns";

export default function App() {
  const [activeTab, setActiveTab] = useState("console");
  const [showModal, setShowModal] = useState(false);
  const [runs, setRuns] = useState(() => {
    try {
      const saved = localStorage.getItem("swarm_runs");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [activeRunId, setActiveRunId] = useState(null);

  // Persist runs in localStorage
  useEffect(() => {
    localStorage.setItem("swarm_runs", JSON.stringify(runs));
  }, [runs]);

  // Compute stat metrics
  const activeSwarms = runs.filter((r) => r.status === "Running").length;
  const failedSwarms = runs.filter((r) => r.status === "Failed").length;
  const totalSwarms = runs.length;

  const handleLaunchSwarm = (payload) => {
    const runId = "run_" + Math.random().toString(36).slice(2, 9);
    const newRun = {
      id: runId,
      name: payload.name,
      target_item_id: payload.target_item_id,
      prompt: payload.prompt,
      status: "Running",
      timestamp: new Date().toISOString(),
      elapsedTime: 0,
      logs: [
        "🛰️ Initializing Swarm Orchestration...",
        "🔗 Tunneling sequential agent flow parameters..."
      ]
    };

    // Prepend new run and open panel
    setRuns((prev) => [newRun, ...prev]);
    setActiveRunId(runId);
    setShowModal(false);

    // Setup simulated log timer
    const startTime = Date.now();
    const timerId = setInterval(() => {
      setRuns((prev) =>
        prev.map((run) => {
          if (run.id !== runId || run.status !== "Running") return run;

          const seconds = Math.floor((Date.now() - startTime) / 1000);
          const newLogs = [...run.logs];

          if (seconds >= 3 && !newLogs.includes("⚡ Activating Agent Alpha (SFT Sentiment Extractor)...")) {
            newLogs.push("⚡ Activating Agent Alpha (SFT Sentiment Extractor)...");
          }
          if (seconds >= 6 && !newLogs.includes("📝 Agent Alpha: Synthesizing Yelp review and predicting sentiment rating...")) {
            newLogs.push("📝 Agent Alpha: Synthesizing Yelp review and predicting sentiment rating...");
          }
          if (seconds >= 9 && !newLogs.includes("🧠 Alpha node complete. Flowing contextual insights into Agent Beta...")) {
            newLogs.push("🧠 Alpha node complete. Flowing contextual insights into Agent Beta...");
          }
          if (seconds >= 12 && !newLogs.includes("🔮 Activating Agent Beta (GRPO Alignment Orchestrator)...")) {
            newLogs.push("🔮 Activating Agent Beta (GRPO Alignment Orchestrator)...");
          }
          if (seconds >= 15 && !newLogs.includes("🧠 Agent Beta: Starting deep monologue reasoning process...")) {
            newLogs.push("🧠 Agent Beta: Starting deep monologue reasoning process...");
          }
          if (seconds >= 19 && !newLogs.includes("🎯 Agent Beta: Finalizing review correlations & recommended item filtering...")) {
            newLogs.push("🎯 Agent Beta: Finalizing review correlations & recommended item filtering...");
          }

          return {
            ...run,
            elapsedTime: seconds,
            logs: newLogs
          };
        })
      );
    }, 1000);

    // Fire actual Modal API Request
    executeSwarmRequest(runId, payload, timerId);
  };

  const handleLaunchSwarmFromLib = (payload) => {
    handleLaunchSwarm(payload);
    setActiveTab("console");
  };

  const executeSwarmRequest = async (runId, payload, timerId) => {
    const startTime = Date.now();
    try {
      const response = await fetch(
        "https://wakamateservices--bct-swarm-orchestrator-swarm-endpoint.modal.run/v1/swarm/process",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            prompt: payload.prompt,
            target_item_id: payload.target_item_id
          })
        }
      );

      clearInterval(timerId);
      const finalElapsed = Math.floor((Date.now() - startTime) / 1000);

      if (response.ok) {
        const data = await response.json();
        setRuns((prev) =>
          prev.map((run) => {
            if (run.id !== runId) return run;
            return {
              ...run,
              status: "Success",
              elapsedTime: finalElapsed,
              alpha_extraction: data.alpha_extraction,
              beta_reasoning: data.beta_reasoning,
              logs: [
                ...run.logs,
                "✅ Sequential swarm execution completed successfully!",
                `📦 Saved ${data.beta_reasoning?.payload?.ranked_items?.length || 0} product recommendation codes.`
              ]
            };
          })
        );
      } else {
        const errText = await response.text();
        setRuns((prev) =>
          prev.map((run) => {
            if (run.id !== runId) return run;
            return {
              ...run,
              status: "Failed",
              elapsedTime: finalElapsed,
              error: `HTTP Error ${response.status}: ${errText}`,
              logs: [...run.logs, `❌ Swarm endpoint failed with HTTP ${response.status}.`]
            };
          })
        );
      }
    } catch (err) {
      clearInterval(timerId);
      const finalElapsed = Math.floor((Date.now() - startTime) / 1000);
      setRuns((prev) =>
        prev.map((run) => {
          if (run.id !== runId) return run;
          return {
            ...run,
            status: "Failed",
            elapsedTime: finalElapsed,
            error: err.message || "Network request failed.",
            logs: [...run.logs, `❌ Network exception: ${err.message || "Server unreachable."}`]
          };
        })
      );
    }
  };

  const activeRun = runs.find((r) => r.id === activeRunId);

  return (
    <div className="flex h-screen bg-[#0d0d0d] text-white overflow-hidden font-mono">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {/* Dynamic Inner SPA Routing */}
        <div className="px-8 py-6">
          {activeTab === "console" && (
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-neutral-800 pb-5">
                <div>
                  <h1 className="text-xl font-bold text-white tracking-tight">Swarm Console</h1>
                  <p className="text-sm text-neutral-500 mt-0.5 font-sans">
                    Monitor, launch, and inspect unified multi-agent recommendation swarms
                  </p>
                </div>
                <button
                  onClick={() => setShowModal(true)}
                  className="bg-violet-600 hover:bg-violet-750 active:bg-violet-800 text-white text-sm font-semibold px-4 py-2.5 rounded-lg transition-all shadow-lg shadow-violet-600/10 cursor-pointer"
                >
                  Launch Swarm
                </button>
              </div>

              {/* Stats row */}
              <div className="flex gap-4">
                <StatCard
                  label="Active Swarms"
                  value={activeSwarms.toString()}
                  description="Pending or currently executing sequential pipelines"
                />
                <StatCard
                  label="Failed Swarms"
                  value={failedSwarms.toString()}
                  description="Swarms that timed out or threw endpoint errors"
                />
                <StatCard
                  label="Total Swarms"
                  value={totalSwarms.toString()}
                  description="All running, succeeded, or failed orchestration metrics"
                />
              </div>

              {/* Table */}
              <EvaluationsTable
                runs={runs}
                onSelectRun={(run) => setActiveRunId(run.id)}
                onNew={() => setShowModal(true)}
              />
            </div>
          )}

          {activeTab === "presets" && (
            <PresetLibrary onLaunch={handleLaunchSwarmFromLib} />
          )}

          {activeTab === "direct" && (
            <DirectQuery />
          )}

          {activeTab === "runs" && (
            <ExecutionRuns runs={runs} onGoToConsole={() => setActiveTab("console")} />
          )}
        </div>
      </main>

      {/* Slide Inspect Panel */}
      {activeRun && <SwarmInspectPanel run={activeRun} onClose={() => setActiveRunId(null)} />}

      {/* New Swarm Run Modal */}
      {showModal && (
        <NewEvaluationModal onClose={() => setShowModal(false)} onSubmit={handleLaunchSwarm} />
      )}
    </div>
  );
}


