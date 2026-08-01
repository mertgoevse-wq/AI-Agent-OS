// In a real environment, this would use WebSockets or SSE to connect to OMNI-Agent-OS
console.log("OMNI-Agent-OS Monitoring Initialized");

function updateDashboard(data) {
    // Update Task
    document.getElementById('task-desc').innerText = data.task || "No active task";
    document.getElementById('task-model').innerText = `Model: ${data.model || "None"}`;
    
    // Update Agents
    const agentsList = document.getElementById('agents-list');
    agentsList.innerHTML = '';
    (data.agents || []).forEach(agent => {
        const li = document.createElement('li');
        li.innerText = agent;
        agentsList.appendChild(li);
    });

    // Update Skills
    const skillsList = document.getElementById('skills-list');
    skillsList.innerHTML = '';
    (data.skills || []).forEach(skill => {
        const li = document.createElement('li');
        li.innerText = skill;
        skillsList.appendChild(li);
    });

    // Add Log
    if (data.log) {
        const logBox = document.getElementById('routing-log');
        const logEntry = document.createElement('div');
        logEntry.innerText = `[${new Date().toLocaleTimeString()}] ${data.log}`;
        logBox.appendChild(logEntry);
        logBox.scrollTop = logBox.scrollHeight;
    }
}

// Mock initial data for demonstration purposes
setTimeout(() => {
    updateDashboard({
        task: "Analyze the newly added CryptoPilot backend endpoints.",
        model: "claude-3-opus",
        agents: ["system_architect", "backend_engineer"],
        skills: ["code_analysis", "architecture_design"],
        log: "MetaRouter assigned backend_engineer based on 'backend' keyword."
    });
}, 2000);
