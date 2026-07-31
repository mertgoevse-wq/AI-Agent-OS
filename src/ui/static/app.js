/* AI-Agent-OS — UI Dashboard Reactive JavaScript Application */

document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  const navItems = document.querySelectorAll('.nav-item');
  const viewPanels = document.querySelectorAll('.view-panel');
  const pageTitle = document.getElementById('page-title');

  const titleMap = {
    'view-overview': 'Overview Dashboard',
    'view-studio': 'Multi-Agent Workflow Studio',
    'view-directory': 'Agents & Skills Directory',
    'view-memory': 'Memory System Inspector',
    'view-models': 'Model Router Manager'
  };

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      navItems.forEach(n => n.classList.remove('active'));
      viewPanels.forEach(p => p.classList.remove('active'));

      item.classList.add('active');
      const targetId = item.getAttribute('data-target');
      const panel = document.getElementById(targetId);
      if (panel) {
        panel.classList.add('active');
        pageTitle.textContent = titleMap[targetId] || 'Dashboard';
      }
    });
  });

  // Data Fetching & UI Updates
  async function fetchStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();

      document.getElementById('metric-agents').textContent = data.active_agents_count || 0;
      document.getElementById('metric-skills').textContent = data.loaded_skills_count || 0;
      document.getElementById('metric-provider').textContent = (data.active_provider || 'Mock').toUpperCase();
      document.getElementById('metric-events').textContent = data.total_events_logged || 0;

      document.getElementById('budget-counter').textContent = 
        `Spent: $${(data.total_cost_usd || 0).toFixed(4)} / $${(data.max_daily_budget_usd || 50).toFixed(2)}`;

      const statusText = document.getElementById('system-status-text');
      statusText.textContent = `Kernel Online (${data.active_provider})`;

      const headerSelect = document.getElementById('header-model-select');
      if (headerSelect && data.active_provider) {
        headerSelect.value = data.active_provider;
      }
    } catch (err) {
      console.error('Failed to fetch status:', err);
    }
  }

  async function fetchDirectory() {
    try {
      const [resAgents, resSkills] = await Promise.all([
        fetch('/api/agents'),
        fetch('/api/skills')
      ]);

      const agentsData = await resAgents.json();
      const skillsData = await resSkills.json();

      // Render Agents Table
      const agentTbody = document.getElementById('agents-table-body');
      agentTbody.innerHTML = '';
      (agentsData.agents || []).forEach(agent => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="font-weight:600;">${agent.id}</td>
          <td>${agent.name}</td>
          <td>${agent.role}</td>
          <td><span class="badge" style="color:var(--accent-indigo); border-color:var(--accent-indigo);">${(agent.permissions.access_levels || []).join(', ')}</span></td>
          <td><span class="badge">${agent.state}</span></td>
        `;
        agentTbody.appendChild(tr);
      });
      document.getElementById('agents-count-badge').textContent = `${(agentsData.agents || []).length} Total`;

      // Render Skills Table
      const skillTbody = document.getElementById('skills-table-body');
      skillTbody.innerHTML = '';
      (skillsData.skills || []).forEach(skill => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="font-weight:600;">${skill.name}</td>
          <td>${skill.version}</td>
          <td style="color:var(--text-muted);">${skill.description || 'Genesis_Harness Skill'}</td>
          <td>${(skill.dependencies || []).join(', ') || 'None'}</td>
        `;
        skillTbody.appendChild(tr);
      });
      document.getElementById('skills-count-badge').textContent = `${(skillsData.skills || []).length} Total`;

    } catch (err) {
      console.error('Failed to fetch directory:', err);
    }
  }

  async function fetchMemory(query = 'AI') {
    try {
      const res = await fetch(`/api/memory?q=${encodeURIComponent(query)}`);
      const data = await res.json();

      document.getElementById('stm-turns-count').textContent = (data.short_term || []).length;
      document.getElementById('ltm-items-count').textContent = (data.long_term || []).length;
      document.getElementById('knowledge-chunks-count').textContent = (data.knowledge || []).length;

      const vectorTbody = document.getElementById('vector-results-body');
      vectorTbody.innerHTML = '';
      (data.vector_results || []).forEach(res => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="font-family:var(--font-mono); font-size:12px;">${res.id}</td>
          <td>${res.content}</td>
          <td><span class="badge" style="background:rgba(99,102,241,0.1); color:var(--accent-indigo);">${(res.score * 100).toFixed(1)}%</span></td>
          <td style="color:var(--text-dim); font-size:11px;">${JSON.stringify(res.metadata)}</td>
        `;
        vectorTbody.appendChild(tr);
      });
    } catch (err) {
      console.error('Failed to fetch memory:', err);
    }
  }

  // Workflow Studio Execution
  const runWorkflowBtn = document.getElementById('run-workflow-btn');
  const quickDemoBtn = document.getElementById('quick-demo-btn');
  const studioTerminal = document.getElementById('studio-terminal');
  const reportOutput = document.getElementById('report-output');

  function appendLog(msg, type = 'info') {
    const line = document.createElement('div');
    line.className = `log-line log-${type}`;
    line.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    studioTerminal.appendChild(line);
    studioTerminal.scrollTop = studioTerminal.scrollHeight;
  }

  function setStepState(stepNum, state) {
    const card = document.getElementById(`step-${stepNum}`);
    if (card) {
      card.classList.remove('active', 'completed');
      if (state === 'active') card.classList.add('active');
      if (state === 'completed') card.classList.add('completed');
    }
  }

  async function executeWorkflow() {
    const topic = document.getElementById('topic-input').value.trim();
    if (!topic) return;

    // Switch to studio tab
    document.querySelector('[data-target="view-studio"]').click();

    runWorkflowBtn.disabled = true;
    runWorkflowBtn.textContent = 'Executing Workflow...';
    studioTerminal.innerHTML = '';
    reportOutput.innerHTML = '<p style="color:var(--text-dim); font-style:italic;">Processing workflow...</p>';

    // Reset steps
    for (let i = 1; i <= 4; i++) setStepState(i, '');

    appendLog(`Starting Multi-Agent Workflow for: "${topic}"`);
    
    // Simulate visual steps
    setStepState(1, 'active');
    appendLog('Step 1: Supervisor Agent analyzing scope...', 'info');

    try {
      const res = await fetch('/api/workflow/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topic })
      });

      const data = await res.json();

      setStepState(1, 'completed');
      setStepState(2, 'completed');
      setStepState(3, 'completed');
      setStepState(4, 'completed');

      appendLog(`Workflow complete! Total time: ${data.total_duration_sec}s`, 'success');
      document.getElementById('workflow-time-badge').textContent = `Duration: ${data.total_duration_sec}s`;

      // Render Report Markdown
      reportOutput.innerHTML = renderSimpleMarkdown(data.final_report);

      fetchStatus();
      fetchMemory();

    } catch (err) {
      appendLog(`Workflow Error: ${err.message}`, 'warn');
    } finally {
      runWorkflowBtn.disabled = false;
      runWorkflowBtn.textContent = 'Execute Workflow';
    }
  }

  function renderSimpleMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');
    return `<p>${html}</p>`;
  }

  if (runWorkflowBtn) runWorkflowBtn.addEventListener('click', executeWorkflow);
  if (quickDemoBtn) quickDemoBtn.addEventListener('click', executeWorkflow);

  // Vector Search sandbox trigger
  document.getElementById('vector-search-btn').addEventListener('click', () => {
    const q = document.getElementById('vector-search-input').value;
    fetchMemory(q);
  });

  // Refresh Button
  document.getElementById('refresh-btn').addEventListener('click', () => {
    fetchStatus();
    fetchDirectory();
    fetchMemory();
  });

  // Header Provider Select change
  document.getElementById('header-model-select').addEventListener('change', async (e) => {
    await fetch('/api/router/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider: e.target.value })
    });
    fetchStatus();
  });

  // Initial Load
  fetchStatus();
  fetchDirectory();
  fetchMemory();
});
