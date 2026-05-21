import { useState } from "react";
import Sidebar from "./components/Sidebar";
import StatCard from "./components/StatCard";
import EvaluationsTable from "./components/EvaluationsTable";
import NewEvaluationModal from "./components/NewEvaluationModal";

export default function App() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="flex h-screen bg-[#0d0d0d] text-white overflow-hidden">
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-8 py-6 border-b border-neutral-800 sticky top-0 bg-[#0d0d0d] z-10">
          <div>
            <h1 className="text-xl font-semibold text-white">Evaluations</h1>
            <p className="text-sm text-neutral-500 mt-0.5">View and manage your evaluations</p>
          </div>
          <button
            onClick={() => setShowModal(true)}
            className="bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors"
          >
            New Evaluation
          </button>
        </div>

        {/* Body */}
        <div className="px-8 py-6 space-y-6">
          {/* Stats row */}
          <div className="flex gap-4">
            <StatCard
              label="Active Evals"
              value="0"
              description="Pending, running, or processing"
            />
            <StatCard
              label="Failed Evals"
              value="0"
              description="Failed or timed out evaluations"
            />
            <StatCard
              label="Total Evals"
              value="0"
              description="All evaluations in this account"
            />
          </div>

          {/* Table */}
          <EvaluationsTable onNew={() => setShowModal(true)} />
        </div>
      </main>

      {/* Modal */}
      {showModal && <NewEvaluationModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
