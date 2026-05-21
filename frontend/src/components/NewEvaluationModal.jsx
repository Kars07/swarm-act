import { X, Sparkles } from "lucide-react";
import { useState, useEffect } from "react";

const PRESETS = {
  "1": {
    name: "Gourmet Ramen Swarm",
    label: "🍜 Gourmet Ramen (Japanese Food)",
    target_item_id: "ramen_shop_992",
    prompt: "The customer wants an authentic Japanese ramen bar experience, specifically looking for rich tonkotsu broth, house-made noodles, and spicy miso options. They appreciate attentive but quick service and don't mind a wait."
  },
  "2": {
    name: "Cozy Cafe Swarm",
    label: "☕ Cozy Coffeehouse & Bakery (Café)",
    target_item_id: "cafe_cafe_883",
    prompt: "The customer is looking for a quiet, homey local café to study or work. They prefer house-roasted pour-over coffee, fresh-baked pastries like almond croissants, and strong, reliable Wi-Fi with a cozy 90s Seattle vibe."
  },
  "3": {
    name: "Steakhouse Swarm",
    label: "🥩 Fine Dining Steakhouse (Luxury Food)",
    target_item_id: "steakhouse_998",
    prompt: "The customer is celebrating an anniversary and looking for an upscale fine dining experience. They want perfectly cooked steaks (filet mignon), excellent craft cocktails (like a Manhattan), and high-end professional table service."
  },
  "4": {
    name: "Southern Diner Swarm",
    label: "🍗 Late-Night Southern Diner (Comfort Food)",
    target_item_id: "diner_south_112",
    prompt: "The customer wants a comforting, late-night meal at a classic Southern diner. They are looking for large portions, highly rated chicken fried steak or chicken salad, and friendly, casual service."
  },
  "5": {
    name: "Nail Salon Swarm",
    label: "💅 Relaxing Nail Salon & Spa (Service)",
    target_item_id: "spa_nails_421",
    prompt: "The customer is looking for a hygienic nail salon for a relaxing pedicure. They are highly critical of cleanliness, quick/rushed service, and want precise, detailed care with complimentary drinks."
  }
};

export default function NewEvaluationModal({ onClose, onSubmit }) {
  const [presetKey, setPresetKey] = useState("1");
  const [name, setName] = useState("");
  const [targetItemId, setTargetItemId] = useState("");
  const [prompt, setPrompt] = useState("");

  // Sync preset data to input fields
  useEffect(() => {
    if (presetKey && PRESETS[presetKey]) {
      const preset = PRESETS[presetKey];
      setName(preset.name);
      setTargetItemId(preset.target_item_id);
      setPrompt(preset.prompt);
    } else if (presetKey === "custom") {
      setName("Custom Swarm Run");
      setTargetItemId("");
      setPrompt("");
    }
  }, [presetKey]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    if (!targetItemId.trim()) return;
    if (!prompt.trim()) return;

    onSubmit({
      name: name.trim(),
      target_item_id: targetItemId.trim(),
      prompt: prompt.trim()
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="bg-[#111111] border border-neutral-800 rounded-xl w-full max-w-lg mx-4 shadow-2xl overflow-hidden animate-in fade-in duration-200">
        <form onSubmit={handleSubmit}>
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-800 bg-[#0e0e0e]">
            <div className="flex items-center gap-2">
              <Sparkles size={16} className="text-violet-400" />
              <h2 className="text-white font-semibold text-base">Launch Swarm Orchestrator</h2>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="text-neutral-500 hover:text-white transition-colors"
            >
              <X size={18} />
            </button>
          </div>

          {/* Form Fields */}
          <div className="px-6 py-5 space-y-4 max-h-[480px] overflow-y-auto scrollbar-hide">
            {/* Preset Selector */}
            <div>
              <label className="block text-[10px] uppercase tracking-wider text-neutral-400 mb-1.5 font-semibold">
                Preset Domain
              </label>
              <select
                value={presetKey}
                onChange={(e) => setPresetKey(e.target.value)}
                className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white outline-none focus:border-violet-600 transition-colors appearance-none cursor-pointer"
              >
                {Object.entries(PRESETS).map(([key, item]) => (
                  <option key={key} value={key}>
                    {item.label}
                  </option>
                ))}
                <option value="custom">✍️ Custom Prompt & Target ID</option>
              </select>
            </div>

            {/* Swarm Run Name */}
            <div>
              <label className="block text-[10px] uppercase tracking-wider text-neutral-400 mb-1.5 font-semibold">
                Swarm Run Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Ramen Evaluator Swarm"
                required
                className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-neutral-600 outline-none focus:border-violet-600 transition-colors"
              />
            </div>

            {/* Target Item ID */}
            <div>
              <label className="block text-[10px] uppercase tracking-wider text-neutral-400 mb-1.5 font-semibold">
                Target Yelp Item ID
              </label>
              <input
                type="text"
                value={targetItemId}
                onChange={(e) => setTargetItemId(e.target.value)}
                placeholder="e.g. ramen_shop_992"
                required
                className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-neutral-600 outline-none focus:border-violet-600 transition-colors font-mono"
              />
            </div>

            {/* Customer Prompt */}
            <div>
              <label className="block text-[10px] uppercase tracking-wider text-neutral-400 mb-1.5 font-semibold">
                Swarm Evaluation Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe what preference profile the customer has..."
                required
                rows={4}
                className="w-full bg-neutral-900 border border-neutral-700 rounded-lg px-3 py-2.5 text-sm text-white placeholder-neutral-600 outline-none focus:border-violet-600 transition-colors resize-none leading-relaxed font-sans"
              />
            </div>
          </div>

          {/* Footer Action Buttons */}
          <div className="flex justify-end gap-3 px-6 py-4 border-t border-neutral-800 bg-[#0e0e0e]">
            <button
              type="button"
              onClick={onClose}
              className="text-sm text-neutral-400 hover:text-white px-4 py-2 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-violet-600 hover:bg-violet-700 active:bg-violet-850 text-white text-sm font-semibold px-5 py-2 rounded-lg transition-colors flex items-center gap-1.5 shadow-lg shadow-violet-600/10"
            >
              <Sparkles size={14} />
              Launch Swarm
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

