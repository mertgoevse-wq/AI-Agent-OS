"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  Cpu,
  Database,
  BrainCircuit,
  Settings,
  Server,
  Play,
  CheckCircle2,
  List,
  MessageSquare,
  Network,
  TrendingUp,
  Briefcase,
  AlertTriangle,
  Bot
} from "lucide-react";

// Types based on the Python DemoServer API responses
type SystemStatus = {
  status: string;
  kernel_running: boolean;
  active_agents_count: number;
  loaded_skills_count: number;
  total_cost_usd: number;
  max_daily_budget_usd: number;
  active_provider: string;
  active_model: string;
  total_events_logged: number;
};

type AgentInfo = {
  id: string;
  name: string;
  role: string;
  description: string;
  state: string;
  required_skills: string[];
};

type SkillInfo = {
  name: string;
  version: string;
  description: string;
  source_path: string;
};

export default function CryptoPilotDashboard() {
  const [activeTab, setActiveTab] = useState("trading");
  
  // Data States
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [memory, setMemory] = useState<any>(null);
  
  // CryptoPilot Specific
  const [portfolio, setPortfolio] = useState<any>({ USD: 100000.0, BTC: 0.5, ETH: 10.0 });
  const [activeOrders, setActiveOrders] = useState<any[]>([]);
  const [marketData, setMarketData] = useState<any>({ BTC: 65000, ETH: 3500 });
  
  // Workflow States
  const [workflowTopic, setWorkflowTopic] = useState("Analyze BTC trends and propose a trade.");
  const [workflowRunning, setWorkflowRunning] = useState(false);
  const [workflowResult, setWorkflowResult] = useState<any>(null);

  const API_URL = "http://localhost:8000/api";

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/status`);
      if (res.ok) setStatus(await res.json());
    } catch (e) {
      console.error("Failed to fetch status", e);
    }
  };

  const fetchRegistry = async () => {
    try {
      const [resAgents, resSkills] = await Promise.all([
        fetch(`${API_URL}/agents`),
        fetch(`${API_URL}/skills`)
      ]);
      if (resAgents.ok) {
        const data = await resAgents.json();
        setAgents(data.agents || []);
      }
      if (resSkills.ok) {
        const data = await resSkills.json();
        setSkills(data.skills || []);
      }
    } catch (e) {
      console.error("Failed to fetch registry", e);
    }
  };

  const fetchEvents = async () => {
    try {
      const res = await fetch(`${API_URL}/events/history`);
      if (res.ok) {
        const data = await res.json();
        setEvents(data.events || []);
      }
    } catch (e) {
      console.error("Failed to fetch events", e);
    }
  };

  // Initial Load & Polling
  useEffect(() => {
    fetchStatus();
    fetchRegistry();
    fetchEvents();

    const interval = setInterval(() => {
      fetchStatus();
      if (activeTab === "assistant" || workflowRunning) fetchEvents();
    }, 2000);
    return () => clearInterval(interval);
  }, [activeTab, workflowRunning]);

  const runWorkflow = async () => {
    setWorkflowRunning(true);
    setWorkflowResult(null);
    try {
      const res = await fetch(`${API_URL}/workflow/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: workflowTopic })
      });
      if (res.ok) {
        setWorkflowResult(await res.json());
      }
    } catch (e) {
      console.error("Workflow failed", e);
    } finally {
      setWorkflowRunning(false);
    }
  };

  const navItems = [
    { id: "trading", label: "Trading Engine", icon: <TrendingUp size={18} /> },
    { id: "portfolio", label: "Portfolio", icon: <Briefcase size={18} /> },
    { id: "analytics", label: "Analytics", icon: <Activity size={18} /> },
    { id: "assistant", label: "AI Assistant", icon: <Bot size={18} /> },
    { id: "registry", label: "OMNI Runtime", icon: <Server size={18} /> }
  ];

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto flex flex-col gap-6">
      
      {/* Header */}
      <header className="glass-panel p-6 flex justify-between items-center bg-gray-900 border-emerald-500/30">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-600 p-2 rounded-lg">
            <TrendingUp size={28} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">CryptoPilot-AI</h1>
            <p className="text-sm text-emerald-400">Powered by OMNI-Agent-OS</p>
          </div>
        </div>
        <div className="flex gap-4 items-center">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium border ${status?.status === 'online' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
            <div className={`w-2 h-2 rounded-full ${status?.status === 'online' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
            {status?.status === 'online' ? 'Engine Online' : 'Disconnected'}
          </div>
        </div>
      </header>

      {/* Navigation */}
      <div className="flex gap-2 p-1 glass-panel w-fit rounded-full">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`flex items-center gap-2 px-5 py-2 rounded-full text-sm font-medium transition-all ${
              activeTab === item.id 
                ? "bg-emerald-600 text-white shadow-md" 
                : "text-gray-400 hover:text-white hover:bg-white/5"
            }`}
          >
            {item.icon}
            {item.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <main className="flex-1">
        
        {/* TRADING TAB */}
        {activeTab === "trading" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-panel p-6">
              <h3 className="text-gray-400 text-sm font-medium flex items-center gap-2"><Activity size={16}/> BTC/USD</h3>
              <p className="text-3xl font-bold mt-2 text-white">${marketData.BTC.toLocaleString()}</p>
              <p className="text-xs text-emerald-400 mt-1">+2.4% (24h)</p>
            </div>
            <div className="glass-panel p-6">
              <h3 className="text-gray-400 text-sm font-medium flex items-center gap-2"><Activity size={16}/> ETH/USD</h3>
              <p className="text-3xl font-bold mt-2 text-white">${marketData.ETH.toLocaleString()}</p>
              <p className="text-xs text-red-400 mt-1">-0.8% (24h)</p>
            </div>
            <div className="glass-panel p-6 col-span-2">
              <h3 className="text-gray-400 text-sm font-medium flex items-center gap-2"><CheckCircle2 size={16}/> Active Orders</h3>
              {activeOrders.length === 0 ? (
                <p className="text-gray-500 mt-4 text-center">No active orders</p>
              ) : (
                <div className="mt-4">
                  {/* Map orders here */}
                </div>
              )}
            </div>
          </div>
        )}

        {/* PORTFOLIO TAB */}
        {activeTab === "portfolio" && (
          <div className="grid grid-cols-1 gap-6">
             <div className="glass-panel p-6">
              <h2 className="text-xl font-bold text-white mb-4">Total Portfolio Value</h2>
              <p className="text-4xl font-bold text-emerald-400">${(portfolio.USD + (portfolio.BTC * marketData.BTC) + (portfolio.ETH * marketData.ETH)).toLocaleString()}</p>
              <div className="mt-8 grid grid-cols-3 gap-4">
                 <div className="bg-surface-hover p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">USD Fiat</p>
                    <p className="text-2xl font-bold text-white">${portfolio.USD.toLocaleString()}</p>
                 </div>
                 <div className="bg-surface-hover p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">Bitcoin (BTC)</p>
                    <p className="text-2xl font-bold text-white">{portfolio.BTC} BTC</p>
                 </div>
                 <div className="bg-surface-hover p-4 rounded-lg">
                    <p className="text-gray-400 text-sm">Ethereum (ETH)</p>
                    <p className="text-2xl font-bold text-white">{portfolio.ETH} ETH</p>
                 </div>
              </div>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
               <div className="glass-panel p-6 border-emerald-500/20">
                 <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2"><AlertTriangle size={18} className="text-yellow-400" /> AI Risk Engine Metrics</h3>
                 <div className="space-y-3">
                   <div className="flex justify-between items-center bg-surface-hover p-3 rounded">
                     <span className="text-sm text-gray-400">Value at Risk (VaR 95%)</span>
                     <span className="text-sm font-bold text-emerald-400">3.85% ($5,489)</span>
                   </div>
                   <div className="flex justify-between items-center bg-surface-hover p-3 rounded">
                     <span className="text-sm text-gray-400">Max Historical Drawdown</span>
                     <span className="text-sm font-bold text-white">8.20%</span>
                   </div>
                   <div className="flex justify-between items-center bg-surface-hover p-3 rounded">
                     <span className="text-sm text-gray-400">Overall Risk Level</span>
                     <span className="text-xs px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-400 font-bold">MODERATE</span>
                   </div>
                 </div>
               </div>

               <div className="glass-panel p-6 border-emerald-500/20">
                 <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2"><TrendingUp size={18} className="text-emerald-400" /> Market Sentiment & Intelligence</h3>
                 <div className="space-y-3">
                   <div className="flex justify-between items-center bg-surface-hover p-3 rounded">
                     <span className="text-sm text-gray-400">Volatility Index</span>
                     <span className="text-sm font-bold text-white">42.5 (Normal)</span>
                   </div>
                   <div className="flex justify-between items-center bg-surface-hover p-3 rounded">
                     <span className="text-sm text-gray-400">Sentiment Score</span>
                     <span className="text-sm font-bold text-emerald-400">68 / 100 (Bullish)</span>
                   </div>
                   <div className="flex justify-between items-center bg-surface-hover p-3 rounded">
                     <span className="text-sm text-gray-400">Market Phase</span>
                     <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 font-bold">BULLISH ACCUMULATION</span>
                   </div>
                 </div>
               </div>
             </div>
          </div>
        )}

        {/* AI ASSISTANT TAB */}
        {activeTab === "assistant" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
            <div className="lg:col-span-1 flex flex-col gap-6">
              <div className="glass-panel p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Bot size={20} /> Trading Co-pilot</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Ask the Co-pilot</label>
                    <textarea 
                      className="w-full bg-surface-hover border border-border rounded-lg p-3 text-white focus:outline-none focus:border-emerald-500 transition-colors"
                      rows={4}
                      value={workflowTopic}
                      onChange={e => setWorkflowTopic(e.target.value)}
                    />
                  </div>
                  <button 
                    onClick={runWorkflow}
                    disabled={workflowRunning}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {workflowRunning ? <Activity size={18} className="animate-spin" /> : <Play size={18} />}
                    {workflowRunning ? "Analyzing..." : "Analyze"}
                  </button>
                </div>
              </div>
              
              {workflowResult && (
                <div className="glass-panel p-6 flex-1 overflow-auto border-emerald-500/30 border">
                  <h2 className="text-lg font-semibold text-emerald-400 mb-4 flex items-center gap-2"><CheckCircle2 size={20} /> Co-pilot Response</h2>
                  <div className="bg-surface-hover p-4 rounded-lg text-sm text-gray-300 whitespace-pre-wrap">
                    {workflowResult.output}
                  </div>
                </div>
              )}
            </div>

            <div className="lg:col-span-2 glass-panel p-6 flex flex-col">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><MessageSquare size={20} /> Agent Reasoning Stream</h2>
              <div className="flex-1 bg-black/40 rounded-lg border border-border p-4 overflow-y-auto font-mono text-xs space-y-2">
                {events.map((e, i) => (
                  <div key={i} className="flex gap-4 p-2 hover:bg-white/5 rounded transition-colors">
                    <div className="text-gray-500 whitespace-nowrap">{new Date(e.timestamp).toLocaleTimeString()}</div>
                    <div className={`w-24 font-bold ${e.type.includes('ERROR') ? 'text-red-400' : e.type.includes('START') ? 'text-emerald-400' : 'text-gray-400'}`}>
                      {e.type}
                    </div>
                    <div className="text-gray-300 flex-1 truncate">{JSON.stringify(e.data)}</div>
                    <div className="text-gray-500">[{e.source}]</div>
                  </div>
                ))}
                {events.length === 0 && <div className="text-gray-500 text-center mt-10">Waiting for agent activity...</div>}
              </div>
            </div>
          </div>
        )}

        {/* REGISTRY TAB */}
        {activeTab === "registry" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-panel p-6 flex flex-col h-[600px]">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Server size={20} /> OMNI Agents Registry</h2>
              <div className="overflow-y-auto pr-2 space-y-4">
                {agents.map(a => (
                  <div key={a.id} className="p-4 rounded-lg bg-surface-hover/50 border border-border">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-white">{a.name}</h4>
                      <span className="text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400">{a.role}</span>
                    </div>
                    <p className="text-sm text-gray-400">{a.description}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="glass-panel p-6 flex flex-col h-[600px]">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><List size={20} /> OMNI Skills Registry</h2>
              <div className="overflow-y-auto pr-2 space-y-4">
                {skills.map(s => (
                  <div key={s.name} className="p-4 rounded-lg bg-surface-hover/50 border border-border">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-white">{s.name}</h4>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{s.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
