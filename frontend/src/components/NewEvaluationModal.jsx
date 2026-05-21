import { X } from "lucide-react";
import { useState } from "react";

export default function NewEvaluationModal({ onClose }) {
  const [name, setName] = useState("");
  const [model, setModel] = useState("");
  const [environment, setEnvironment] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#111111] border border-neutral-800 rounded-xl w-full max-w-md mx-4 shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-800">
          <h2 className="text-white font-semibold text-base">New Evaluation</h2>
          <button onClick={onClose} className="text-neutral-500 hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="px-6 py-5 space-y-4">
          <div>
            <label className="block text-xs text-neutral-400 mb-1.5 font-medium">Evaluation Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. my-eval-run-1"
              className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-neutral-600 outline-none focus:border-violet-600 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs text-neutral-400 mb-1.5 font-medium">Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white outline-none focus:border-violet-600 transition-colors appearance-none"
            >
              <option value="">Select a model...</option>
              <option>meta-llama/Llama-3.1-8B</option>
              <option>meta-llama/Llama-3.1-70B</option>
              <option>mistralai/Mistral-7B-v0.1</option>
              <option>Qwen/Qwen2.5-7B</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-neutral-400 mb-1.5 font-medium">Environment</label>
            <select
              value={environment}
              onChange={(e) => setEnvironment(e.target.value)}
              className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white outline-none focus:border-violet-600 transition-colors appearance-none"
            >
              <option value="">Select an environment...</option>
              <option>AIME 2024</option>
              <option>GSM8K</option>
              <option>HumanEval</option>
              <option>MMLU</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end gap-3 px-6 py-4 border-t border-neutral-800">
          <button
            onClick={onClose}
            className="text-sm text-neutral-400 hover:text-white px-4 py-2 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onClose}
            className="bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium px-5 py-2 rounded-lg transition-colors"
          >
            Create Evaluation
          </button>
        </div>
      </div>
    </div>
  );
}
