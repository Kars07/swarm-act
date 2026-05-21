import { Sparkles, ArrowUpRight, Flame, ShieldAlert, Cpu } from "lucide-react";

const DATASET_PRESETS = [
  {
    id: "lib_1",
    name: "Gourmet Ramen Shop",
    icon: "🍜",
    target_item_id: "ramen_shop_992",
    difficulty: "Easy",
    sentiment: "Positive",
    prompt: "The customer wants an authentic Japanese ramen bar experience, specifically looking for rich tonkotsu broth, house-made noodles, and spicy miso options. They appreciate attentive but quick service and don't mind a wait.",
    notes: "Ideal for testing sentiment extraction speed & core Yelp classifications."
  },
  {
    id: "lib_2",
    name: "Cozy Seattle Cafe",
    icon: "☕",
    target_item_id: "cafe_cafe_883",
    difficulty: "Medium",
    sentiment: "Positive",
    prompt: "The customer is looking for a quiet, homey local café to study or work. They prefer house-roasted pour-over coffee, fresh-baked pastries like almond croissants, and strong, reliable Wi-Fi with a cozy 90s Seattle vibe.",
    notes: "Requires extracting quiet atmosphere cues and physical workspace parameters."
  },
  {
    id: "lib_3",
    name: "Luxury Fine Dining Steakhouse",
    icon: "🥩",
    target_item_id: "steakhouse_998",
    difficulty: "Hard",
    sentiment: "Positive",
    prompt: "The customer is celebrating an anniversary and looking for an upscale fine dining experience. They want perfectly cooked steaks (filet mignon), excellent craft cocktails (like a Manhattan), and high-end professional table service.",
    notes: "High complexity review structures. Triggers extensive Agent Beta reasoning."
  },
  {
    id: "lib_4",
    name: "Comfort Food Southern Diner",
    icon: "🍗",
    target_item_id: "diner_south_112",
    difficulty: "Medium",
    sentiment: "Positive",
    prompt: "The customer wants a comforting, late-night meal at a classic Southern diner. They are looking for large portions, highly rated chicken fried steak or chicken salad, and friendly, casual service.",
    notes: "Aligns with historical diner variance. Checks specific Yelp comfort recipes."
  },
  {
    id: "lib_5",
    name: "Relaxing Pedicure Spa",
    icon: "💅",
    target_item_id: "spa_nails_421",
    difficulty: "Hard",
    sentiment: "Positive",
    prompt: "The customer is looking for a hygienic nail salon for a relaxing pedicure. They are highly critical of cleanliness, quick/rushed service, and want precise, detailed care with complimentary drinks.",
    notes: "Strict sanitation criteria. Tests Beta's dictionary-unpacking filters."
  },
  {
    id: "lib_6",
    name: "Vintage Italian Osteria",
    icon: "🍷",
    target_item_id: "osteria_italy_404",
    difficulty: "Medium",
    sentiment: "Positive",
    prompt: "Desires house-rolled truffle pappardelle, a strong selection of Chianti Classico, dimmed candlelight, and slow, European-paced service where the waiter doesn't rush.",
    notes: "Tests slow-paced service preference matching."
  },
  {
    id: "lib_7",
    name: "Organic Craft Smashburger",
    icon: "🍔",
    target_item_id: "smash_burger_112",
    difficulty: "Easy",
    sentiment: "Positive",
    prompt: "Wants a double smashburger with crispy lace edges, house-made quick pickles, brioche bun, and locally sourced truffle fries in a lively, modern industrial gastropub.",
    notes: "Evaluates gastropub atmosphere tags and custom pickle descriptions."
  }
];

export default function PresetLibrary({ onLaunch }) {
  const getDifficultyColor = (diff) => {
    switch (diff) {
      case "Easy":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "Medium":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      case "Hard":
        return "text-rose-400 bg-rose-500/10 border-rose-500/20";
      default:
        return "text-neutral-400 bg-neutral-500/10 border-neutral-500/20";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Dataset Preset Library</h1>
        <p className="text-sm text-neutral-500 mt-0.5 font-sans">
          Select and launch pre-compiled consumer preference profiles from academic Yelp datasets to benchmark our orchestrator.
        </p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {DATASET_PRESETS.map((preset) => (
          <div
            key={preset.id}
            className="bg-[#111111] border border-neutral-800 rounded-xl p-5 hover:border-violet-500/50 hover:shadow-lg hover:shadow-violet-600/5 transition-all duration-300 flex flex-col justify-between group"
          >
            {/* Top info */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-2xl select-none">{preset.icon}</span>
                  <h3 className="font-semibold text-white text-sm group-hover:text-violet-400 transition-colors">
                    {preset.name}
                  </h3>
                </div>
                <span className="text-[10px] text-neutral-600 font-mono select-none">
                  {preset.id}
                </span>
              </div>

              <div className="flex gap-1.5 flex-wrap">
                <span className={`text-[9px] font-mono px-2 py-0.5 rounded border ${getDifficultyColor(preset.difficulty)}`}>
                  Diff: {preset.difficulty}
                </span>
                <span className="text-[9px] font-mono px-2 py-0.5 rounded border border-neutral-800 bg-neutral-900/60 text-neutral-400">
                  Target: {preset.sentiment}
                </span>
                <span className="text-[9px] font-mono px-2 py-0.5 rounded border border-neutral-850 bg-[#151515] text-violet-400 flex items-center gap-1 select-none">
                  <Cpu size={8} />
                  Modal-LangGraph
                </span>
              </div>

              <p className="text-xs text-neutral-400 leading-relaxed font-sans min-h-[58px]">
                {preset.prompt}
              </p>
            </div>

            {/* Bottom action */}
            <div className="border-t border-neutral-800/80 pt-4 mt-4 space-y-3">
              <div className="flex items-center gap-1.5 text-neutral-500 text-[10px] font-sans">
                <span className="font-mono text-neutral-400 bg-neutral-900 border border-neutral-800 px-1 py-0.5 rounded">
                  {preset.target_item_id}
                </span>
                <span className="truncate">{preset.notes}</span>
              </div>

              <button
                onClick={() =>
                  onLaunch({
                    name: preset.name + " (Lib)",
                    target_item_id: preset.target_item_id,
                    prompt: preset.prompt
                  })
                }
                className="w-full bg-neutral-900 border border-neutral-800 hover:border-violet-600 hover:bg-violet-650 hover:text-white transition-all text-neutral-300 font-semibold text-xs py-2 rounded-lg flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Sparkles size={12} />
                Import & Launch Swarm
                <ArrowUpRight size={12} className="opacity-60" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
