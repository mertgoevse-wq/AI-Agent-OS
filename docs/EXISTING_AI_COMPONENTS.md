# EXISTING AI COMPONENTS

Diese Übersicht dokumentiert die existierenden Agenten und Skills, die im parallel existierenden `Genesis_Harness` Ökosystem (welches als Referenz und Baustein-Lieferant für das AI-Agent-OS dient) analysiert wurden. Diese Bausteine können in die neue Architektur des AI-Agent-OS migriert oder adaptiert werden.

## 1. Analysierte Agenten (Agents)
Das bestehende System nutzt ein Zwei-Dateien-Konzept (`AGENT.md` als Charter und `.claude/agents/<id>.md` als Runtime Adapter) für über 50 spezialisierte Agenten. Hier ist eine Auswahl der wichtigsten Kern-Agenten:

### 1.1 Architect Agent
- **Zweck:** Software Architect – Verantworlich für Struktur, System-Verträge und technische Technologie-Entscheidungen.
- **Input:** Feature-Requirements, System Constraints, Research Reports.
- **Output:** Architektur-Dokumente, Systemverträge, Tech-Stack Entscheidungen.
- **Abhängigkeiten:** `software-engineering`, `ai-agents` Skills. Erhält Input oft vom `research` Agent.
- **Verbesserungsmöglichkeiten:** Bessere Integration in automatisierte Architektur-Diagramm-Generierung (Mermaid) und Validierung gegen existierende Codebasen.

### 1.2 Coding Agent
- **Zweck:** Implementation – Übernimmt das Schreiben und Verändern des Quellcodes.
- **Input:** Architektur-Vorgaben, Bug-Reports, Tasks vom Architect.
- **Output:** Source File Änderungen (Commits).
- **Abhängigkeiten:** `software-engineering` Skill. Übergibt Resultate an `qa`.
- **Verbesserungsmöglichkeiten:** Sandboxed Execution für direkte Test-Ausführung (Test-Driven-Development Lifecycle) fehlt teilweise noch in der Isolation.

### 1.3 QA Agent
- **Zweck:** Verification – Bestimmt die Definition of "Done". Kann jeden Commit blockieren.
- **Input:** Veränderten Code vom `coding` Agent, Test-Pläne.
- **Output:** QA-Reports, Pass/Fail Entscheidungen, CRITICAL findings.
- **Abhängigkeiten:** `software-engineering` und `testing` Skills.
- **Verbesserungsmöglichkeiten:** Bessere automatisierte Tool-Integration (z.B. Linter, Coverage-Tools) als direkte Agent-Erweiterungen.

### 1.4 Research Agent
- **Zweck:** Research Lead – Übernimmt die Verifikation von Fakten über die "Außenwelt".
- **Input:** Recherchier-Aufträge (z.B. "Evaluiere Tech Stack X").
- **Output:** Verifizierte Fakten, Research-Berichte.
- **Abhängigkeiten:** Kann Domänen-Skills wie `physics`, `chemistry` oder `prompt-engineering` laden.
- **Verbesserungsmöglichkeiten:** Bessere Memory-Integration (Langzeitgedächtnis), um redundante Recherchen zu vermeiden.

## 2. Analysierte Skills
Das bestehende System verfügt über ~56 isolierte Skills. Skills sind reine Wissensdomänen und Methoden, ohne Orchestrierungslogik.

### 2.1 Software Engineering
- **Zweck:** Standard-Skill für Code-Struktur, Testing, Security und Debugging.
- **Wann zu nutzen:** Default-Skill, wenn kein anderer passt.
- **Verbesserungsmöglichkeiten:** Aufteilung in granulare Sub-Skills (z.B. `frontend-engineering`, `backend-engineering` - teilweise schon vorhanden, aber Überschneidungen müssen geklärt werden).

### 2.2 AI Agents
- **Zweck:** Wissen über Agenten-Design, Orchestrierung und Evaluierung.
- **Wann zu nutzen:** Wenn Architektur für Multi-Agenten-Systeme gebaut wird.
- **Verbesserungsmöglichkeiten:** Aktualisierung mit den neuesten Erkenntnissen über Tree-of-Thoughts und Graph-basierte Workflows.

### 2.3 Simulation & Science (Physics, Chemistry, Biology)
- **Zweck:** Domänenspezifisches Wissen (z.B. Stabilität von Simulationen, deterministische Systeme).
- **Wann zu nutzen:** Wenn naturwissenschaftliche Systeme entworfen oder simuliert werden.
- **Verbesserungsmöglichkeiten:** Direkte API-Anbindungen (z.B. Wolfram Alpha oder Jupyter Notebook Sandbox) für numerische Berechnungen hinzufügen.

## Fazit & Wiederverwendbarkeit
Das bestehende Konstrukt aus `AGENT.md` (Charter) und `SKILL.md` ist extrem robust. 
Für das **AI-Agent-OS** sollten wir dieses Konzept 1:1 übernehmen:
- **Agenten sind das "Wer"** (Rolle, Workflow, Handoff-Regeln).
- **Skills sind das "Was"** (Methodik, Wissensdomäne, Guardrails).

**Nächster logischer Schritt:** Das AI-Agent-OS muss eine Runtime bereitstellen, die genau diese `.md` und `.json` Definitionen dynamisch laden, den passenden Kontext an das LLM übergeben und die beschriebenen Tool-Aufrufe überwachen kann.
