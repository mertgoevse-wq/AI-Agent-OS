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
  Network
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

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("system");
  
  // Data States
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [skills, setSkills] = useState<SkillInfo[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [memory, setMemory] = useState<any>(null);
  
  // Workflow States
  const [workflowTopic, setWorkflowTopic] = useState("Analysiere KI-Agenten Trends 2026");
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

  const fetchMemory = async () => {
    try {
      const res = await fetch(`${API_URL}/memory`);
      if (res.ok) setMemory(await res.json());
    } catch (e) {
      console.error("Failed to fetch memory", e);
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
    fetchMemory();
    fetchEvents();

    const interval = setInterval(() => {
      fetchStatus();
      if (activeTab === "workflow" || workflowRunning) fetchEvents();
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
      fetchMemory(); // Refresh memory after workflow
    }
  };

  const navItems = [
    { id: "system", label: "System Status", icon: <Activity size={18} /> },
    { id: "registry", label: "Registry", icon: <Server size={18} /> },
    { id: "memory", label: "Memory Inspector", icon: <Database size={18} /> },
    { id: "workflow", label: "Workflow Studio", icon: <Network size={18} /> },
  ];

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto flex flex-col gap-6">
      
      {/* Header */}
      <header className="glass-panel p-6 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="bg-primary-600 p-2 rounded-lg">
            <BrainCircuit size={28} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white tracking-tight">AI-Agent-OS</h1>
            <p className="text-sm text-gray-400">Universal Multi-Agent Runtime</p>
          </div>
        </div>
        <div className="flex gap-4 items-center">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium border ${status?.status === 'online' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
            <div className={`w-2 h-2 rounded-full ${status?.status === 'online' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
            {status?.status === 'online' ? 'System Online' : 'Disconnected'}
          </div>
          <div className="flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium border bg-blue-500/10 text-blue-400 border-blue-500/20">
            <Cpu size={14} />
            {status?.active_model || "Loading..."} ({status?.active_provider})
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
                ? "bg-primary-600 text-white shadow-md" 
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
        
        {/* SYSTEM STATUS TAB */}
        {activeTab === "system" && status && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass-panel p-6">
              <h3 className="text-gray-400 text-sm font-medium flex items-center gap-2"><Cpu size={16}/> Kernel Status</h3>
              <p className="text-3xl font-bold mt-2 text-white">{status.kernel_running ? "Running" : "Idle"}</p>
            </div>
            <div className="glass-panel p-6">
              <h3 className="text-gray-400 text-sm font-medium flex items-center gap-2"><Server size={16}/> Loaded Agents</h3>
              <p className="text-3xl font-bold mt-2 text-white">{status.active_agents_count}</p>
            </div>
            <div className="glass-panel p-6">
              <h3 className="text-gray-400 text-sm font-medium flex items-center gap-2"><List size={16}/> Loaded Skills</h3>
              <p className="text-3xl font-bold mt-2 text-white">{status.loaded_skills_count}</p>
            </div>
            <div className="glass-panel p-6">
              <h3 className="text-gray-400 text-sm font-medium flex items-center gap-2"><Activity size={16}/> API Cost</h3>
              <p className="text-3xl font-bold mt-2 text-white">${status.total_cost_usd.toFixed(4)}</p>
              <p className="text-xs text-gray-500 mt-1">Limit: ${status.max_daily_budget_usd}</p>
            </div>
          </div>
        )}

        {/* REGISTRY TAB */}
        {activeTab === "registry" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-panel p-6 flex flex-col h-[600px]">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Server size={20} /> Agents Registry</h2>
              <div className="overflow-y-auto pr-2 space-y-4">
                {agents.map(a => (
                  <div key={a.id} className="p-4 rounded-lg bg-surface-hover/50 border border-border">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-white">{a.name} <span className="text-xs text-gray-400 bg-black/20 px-2 py-1 rounded ml-2">{a.id}</span></h4>
                      <span className="text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400">{a.role}</span>
                    </div>
                    <p className="text-sm text-gray-400">{a.description}</p>
                    {a.required_skills.length > 0 && (
                      <div className="mt-3 flex gap-2 flex-wrap">
                        {a.required_skills.map(s => <span key={s} className="text-xs text-gray-300 bg-white/5 px-2 py-1 rounded border border-white/10">{s}</span>)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="glass-panel p-6 flex flex-col h-[600px]">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><List size={20} /> Skills Registry</h2>
              <div className="overflow-y-auto pr-2 space-y-4">
                {skills.map(s => (
                  <div key={s.name} className="p-4 rounded-lg bg-surface-hover/50 border border-border">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-white">{s.name}</h4>
                      <span className="text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-400">v{s.version}</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{s.description}</p>
                    <p className="text-xs text-gray-500 truncate">{s.source_path}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* MEMORY TAB */}
        {activeTab === "memory" && memory && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
             <div className="glass-panel p-6 flex flex-col">
              <h2 className="text-lg font-semibold text-white mb-4">Short-Term (Context)</h2>
              <div className="overflow-y-auto flex-1 space-y-3">
                {memory.short_term.map((m: any, i: number) => (
                  <div key={i} className={`p-3 rounded-lg text-sm ${m.role === 'user' ? 'bg-blue-500/10 border border-blue-500/20 ml-4' : 'bg-surface-hover border border-border mr-4'}`}>
                    <span className="text-xs font-bold uppercase block mb-1 text-gray-500">{m.role}</span>
                    <p className="text-gray-300 whitespace-pre-wrap">{m.content}</p>
                  </div>
                ))}
              </div>
             </div>
             <div className="glass-panel p-6 flex flex-col">
              <h2 className="text-lg font-semibold text-white mb-4">Long-Term (K/V)</h2>
              <div className="overflow-y-auto flex-1 space-y-3">
                {memory.long_term.map((m: any, i: number) => (
                  <div key={i} className="p-3 rounded-lg bg-surface-hover border border-border text-sm">
                    <span className="text-xs text-green-400 font-mono block mb-1">{m.category} / {m.key}</span>
                    <p className="text-gray-300">{JSON.stringify(m.value)}</p>
                  </div>
                ))}
              </div>
             </div>
             <div className="glass-panel p-6 flex flex-col">
              <h2 className="text-lg font-semibold text-white mb-4">Knowledge (Vector)</h2>
              <div className="overflow-y-auto flex-1 space-y-3">
                {memory.vector_results?.map((m: any, i: number) => (
                  <div key={i} className="p-3 rounded-lg bg-surface-hover border border-border text-sm">
                    <span className="text-xs text-purple-400 block mb-1">Score: {m.score} | ID: {m.id}</span>
                    <p className="text-gray-300 line-clamp-3">{m.content}</p>
                  </div>
                ))}
              </div>
             </div>
          </div>
        )}

        {/* WORKFLOW STUDIO TAB */}
        {activeTab === "workflow" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
            <div className="lg:col-span-1 flex flex-col gap-6">
              <div className="glass-panel p-6">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Play size={20} /> Supervisor Dispatch</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Research Topic</label>
                    <textarea 
                      className="w-full bg-surface-hover border border-border rounded-lg p-3 text-white focus:outline-none focus:border-primary-500 transition-colors"
                      rows={4}
                      value={workflowTopic}
                      onChange={e => setWorkflowTopic(e.target.value)}
                    />
                  </div>
                  <button 
                    onClick={runWorkflow}
                    disabled={workflowRunning}
                    className="w-full bg-primary-600 hover:bg-primary-500 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {workflowRunning ? <Activity size={18} className="animate-spin" /> : <Play size={18} />}
                    {workflowRunning ? "Executing Workflow..." : "Start Orchestrator"}
                  </button>
                </div>
              </div>
              
              {workflowResult && (
                <div className="glass-panel p-6 flex-1 overflow-auto">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><CheckCircle2 size={20} className="text-green-400"/> Final Output</h2>
                  <div className="bg-surface-hover p-4 rounded-lg border border-border text-sm text-gray-300 whitespace-pre-wrap">
                    {workflowResult.output}
                  </div>
                </div>
              )}
            </div>

            <div className="lg:col-span-2 glass-panel p-6 flex flex-col">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><MessageSquare size={20} /> Live Event Bus Stream</h2>
              <div className="flex-1 bg-black/40 rounded-lg border border-border p-4 overflow-y-auto font-mono text-xs space-y-2">
                {events.map((e, i) => (
                  <div key={i} className="flex gap-4 p-2 hover:bg-white/5 rounded transition-colors">
                    <div className="text-gray-500 whitespace-nowrap">{new Date(e.timestamp).toLocaleTimeString()}</div>
                    <div className={`w-24 font-bold ${e.type.includes('ERROR') ? 'text-red-400' : e.type.includes('START') ? 'text-green-400' : e.type.includes('MESSAGE') ? 'text-blue-400' : 'text-gray-400'}`}>
                      {e.type}
                    </div>
                    <div className="text-gray-300 flex-1 truncate">{JSON.stringify(e.data)}</div>
                    <div className="text-gray-500">[{e.source}]</div>
                  </div>
                ))}
                {events.length === 0 && <div className="text-gray-500 text-center mt-10">No events found.</div>}
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
