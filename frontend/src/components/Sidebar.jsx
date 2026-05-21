import { useState } from "react";
import {
  Home,
  ChevronLeft,
  ChevronRight,
  Settings,
  LogIn,
  Cpu,
  Server,
  Box,
  BarChart2,
  Zap,
  Activity,
  Inbox,
  Key,
  MessageSquare,
  BookOpen,
} from "lucide-react";

const NavSection = ({ label, items, collapsed, activeTab, onTabChange }) => (
  <div className="mb-4">
    {!collapsed && (
      <p className="text-[10px] uppercase tracking-widest text-neutral-500 px-3 mb-1 font-semibold select-none">
        {label}
      </p>
    )}
    {items.map(({ id, icon: Icon, label: itemLabel, disabled }) => {
      const isActive = activeTab === id;
      return (
        <button
          key={itemLabel}
          onClick={() => !disabled && onTabChange && onTabChange(id)}
          disabled={disabled}
          className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-all duration-150 group cursor-pointer text-left outline-none
            ${isActive
              ? "bg-neutral-800 text-white font-medium border-l-2 border-violet-500 pl-2.5"
              : disabled
              ? "text-neutral-600 cursor-not-allowed opacity-50"
              : "text-neutral-400 hover:text-white hover:bg-neutral-800/60"
            }`}
        >
          <Icon size={16} className={`shrink-0 ${isActive ? "text-violet-400" : "text-neutral-500 group-hover:text-white"}`} />
          {!collapsed && <span className="truncate">{itemLabel}</span>}
        </button>
      );
    })}
  </div>
);

export default function Sidebar({ activeTab, onTabChange }) {
  const [collapsed, setCollapsed] = useState(false);

  const labItems = [
    { id: "console", icon: BarChart2, label: "Swarm Console" },
    { id: "presets", icon: Box, label: "Preset Library" },
    { id: "direct", icon: Zap, label: "Direct Query" },
    { id: "runs", icon: Activity, label: "Execution Runs" },
  ];

  const computeItems = [
    { id: "modal-services", icon: Cpu, label: "Modal Services", disabled: true },
    { id: "worker-instances", icon: Server, label: "Worker Instances", disabled: true },
  ];

  const accountItems = [
    { id: "settings", icon: Settings, label: "Settings", disabled: true },
    { id: "inbox", icon: Inbox, label: "Inbox", disabled: true },
    { id: "keys", icon: Key, label: "Keys & Secrets", disabled: true },
  ];

  const supportItems = [
    { id: "chat", icon: MessageSquare, label: "Chat", disabled: true },
    { id: "docs", icon: BookOpen, label: "Documentation", disabled: true },
  ];

  return (
    <aside
      className={`flex flex-col h-screen bg-[#0a0a0a] border-r border-neutral-800 transition-all duration-300 ${
        collapsed ? "w-14" : "w-56"
      } shrink-0`}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-3 py-4 border-b border-neutral-800">
        {!collapsed && (
          <span className="text-white text-lg font-bold tracking-tight">
            SWARM<span className="text-violet-500 font-light italic">ACT</span>
          </span>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-neutral-500 hover:text-white transition-colors p-1 rounded"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 py-4 space-y-1 scrollbar-hide">
        <button
          onClick={() => onTabChange("console")}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm text-neutral-400 hover:text-white hover:bg-neutral-800/60 transition-colors mb-4 text-left outline-none cursor-pointer"
        >
          <Home size={16} className="shrink-0" />
          {!collapsed && <span>Home</span>}
        </button>

        <NavSection label="Console" items={labItems} collapsed={collapsed} activeTab={activeTab} onTabChange={onTabChange} />
        <NavSection label="Infrastructure" items={computeItems} collapsed={collapsed} activeTab={activeTab} onTabChange={onTabChange} />
        <NavSection label="Account" items={accountItems} collapsed={collapsed} activeTab={activeTab} onTabChange={onTabChange} />
        <NavSection label="Support" items={supportItems} collapsed={collapsed} activeTab={activeTab} onTabChange={onTabChange} />
      </nav>

      {/* Footer */}
      <div className="border-t border-neutral-800 px-3 py-3 select-none">
        {!collapsed && (
          <div className="flex gap-3 text-[10px] text-neutral-600 mb-2">
            <span className="hover:text-neutral-400 transition-colors">Terms of Service</span>
            <span className="hover:text-neutral-400 transition-colors">Privacy Policy</span>
          </div>
        )}
        <div className="flex items-center gap-3 px-0 py-1 text-sm text-neutral-500">
          <LogIn size={16} className="shrink-0" />
          {!collapsed && <span>Verified User</span>}
        </div>
      </div>
    </aside>
  );
}

