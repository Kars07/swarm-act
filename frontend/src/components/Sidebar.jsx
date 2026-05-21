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
  CreditCard,
  Key,
  MessageSquare,
  BookOpen,
  ExternalLink,
} from "lucide-react";

const NavSection = ({ label, items, collapsed }) => (
  <div className="mb-4">
    {!collapsed && (
      <p className="text-[10px] uppercase tracking-widest text-neutral-500 px-3 mb-1 font-semibold">
        {label}
      </p>
    )}
    {items.map(({ icon: Icon, label: itemLabel, active, href }) => (
      <a
        key={itemLabel}
        href={href || "#"}
        className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors duration-150 group
          ${active
            ? "bg-neutral-800 text-white"
            : "text-neutral-400 hover:text-white hover:bg-neutral-800/60"
          }`}
      >
        <Icon size={16} className="shrink-0" />
        {!collapsed && <span className="truncate">{itemLabel}</span>}
      </a>
    ))}
  </div>
);

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  const labItems = [
    { icon: Box, label: "Environments Hub", href: "#" },
    { icon: BarChart2, label: "Evaluations", active: true, href: "#" },
    { icon: Zap, label: "Training", href: "#" },
    { icon: Activity, label: "Inference", href: "#" },
  ];

  const computeItems = [
    { icon: Cpu, label: "On-Demand GPUs", href: "#" },
    { icon: Server, label: "Reserved Clusters", href: "#" },
    { icon: Box, label: "Instances", href: "#" },
  ];

  const accountItems = [
    { icon: Settings, label: "Settings", href: "#" },
    { icon: Inbox, label: "Inbox", href: "#" },
    { icon: CreditCard, label: "Billing", href: "#" },
    { icon: Key, label: "Keys & Secrets", href: "#" },
  ];

  const supportItems = [
    { icon: MessageSquare, label: "Chat", href: "#" },
    { icon: BookOpen, label: "Documentation", href: "#" },
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
          <span className="text-white text-2xl font-bold text-sm tracking-tight">
            SWa<span className="text-neutral-400 font-light italic">rm</span>
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
        <a
          href="#"
          className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-neutral-400 hover:text-white hover:bg-neutral-800/60 transition-colors mb-4"
        >
          <Home size={16} className="shrink-0" />
          {!collapsed && <span>Home</span>}
        </a>

        <NavSection label="Lab" items={labItems} collapsed={collapsed} />
        <NavSection label="Compute" items={computeItems} collapsed={collapsed} />
        <NavSection label="Account" items={accountItems} collapsed={collapsed} />
        <NavSection label="Support" items={supportItems} collapsed={collapsed} />
      </nav>

      {/* Footer */}
      <div className="border-t border-neutral-800 px-3 py-3">
        {!collapsed && (
          <div className="flex gap-3 text-[10px] text-neutral-600 mb-2">
            <a href="#" className="hover:text-neutral-400 transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-neutral-400 transition-colors">Privacy Policy</a>
          </div>
        )}
        <a
          href="#"
          className="flex items-center gap-3 px-0 py-1 text-sm text-neutral-400 hover:text-white transition-colors"
        >
          <LogIn size={16} className="shrink-0" />
          {!collapsed && <span>Sign In</span>}
        </a>
      </div>
    </aside>
  );
}
