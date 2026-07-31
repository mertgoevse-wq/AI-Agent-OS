# SYSTEM ARCHITECTURE: AI-Agent-OS

## Systemübersicht
Das AI-Agent-OS ist eine ebenen-basierte Architektur (Layered Architecture). Sie entkoppelt die kognitive Logik der Agenten von der physischen LLM-Infrastruktur, der Zustandsspeicherung und der Tool-Ausführung.

Das System folgt dem Prinzip der ereignisgesteuerten Architektur (Event-Driven Architecture), bei der Agenten über einen zentralen Event-Bus kommunizieren und auf Umgebungsänderungen reagieren.

## Komponenten

### 1. Agent Kernel
Der Kern des OS, der den fundamentalen Lebenszyklus jedes Agenten orchestriert.
- **Agent Lifecycle:** Initialisierung -> Idle -> Running -> Paused -> Terminated.
- **Agent States:** Beinhaltet den aktuellen Kontext, offene Tasks, und geladene Skills.
- **Task Management:** Warteschlange von asynchronen Tasks (Tree-of-Thoughts / Plan-and-Solve Routinen).
- **Event System:** Pub/Sub Bus, über den Agenten System-Events empfangen (z.B. "Message_Received", "Tool_Execution_Failed").
- **Execution Tracing:** Detaillierte Speicherung jedes Zwischenschritts.
- **Fehlerbehandlung:** Automatische Recovery-Strategien, Retry-Mechanismen bei LLM-Hallen oder Tool-Fehlern.

### 2. Model Router
Eine universelle Modellschicht, die Agenten von spezifischen LLM-Providern entkoppelt.
- **Provider-Unterstützung:** Cloud APIs (OpenAI, Anthropic, Google Gemini) und lokale Modelle (Ollama, vLLM, HuggingFace).
- **Routing-Logik:** Dynamische Modellauswahl basierend auf der Aufgabe (z.B. Gemini 1.5 Pro für riesige Kontexte, lokales Llama-3 für einfache Formatierungen).
- **Fallback-Mechanismen:** Automatischer Wechsel bei Rate Limits oder API-Timeouts.
- **Kostenkontrolle (Cost Control):** Tracking von Token-Verbrauch und Budget-Limits per Agent/Task.
- **Capability Matching:** Anforderungen eines Agenten (z.B. "braucht Vision", "braucht Function Calling") werden mit Modellfähigkeiten gematcht.

### 3. Skill System
Ein Modulsystem, das Agenten kognitive und methodische Fähigkeiten verleiht.
- **Skill Definition:** `ID`, `Name`, `Version`, `Description`.
- **Interface:** Stark typisierte `Input Schemas` und `Output Schemas` (JSON Schema / Pydantic).
- **Permissions:** Welche Ressourcen der Skill anfragen darf.
- **Dependencies:** Ein Skill kann andere Skills oder bestimmte Tools voraussetzen.
- **Beispiele:** Web Research, Data Analysis, Code Review.

### 4. Tool System
Die Registry für alle physischen Interaktionen mit der Außenwelt.
- **Tool Definition:** `ID`, `Description`, `Input Schema` (für das LLM), `Output Schema`.
- **Berechtigungen & Sicherheit:** Deklarative Permissions (z.B. read-only, write, network-access).
- **Logging & Audit Trail:** Jeder Tool-Aufruf wird mit Input, Output, Dauer und Agent-ID geloggt.
- **Execution Sandbox:** Containerisierte (Docker) oder isolierte (WebAssembly/MicroVM) Ausführungsumgebungen für unsichere Tools (z.B. Python Interpreter).

### 5. Memory System
Die Speicherverwaltung des OS, aufgeteilt in kognitive Zeithorizonte.
- **Short Term Memory (STM):**
  - Aktueller Konversationskontext.
  - Scratchpads für laufende Aufgaben.
  - Oft direkt in das LLM-Context-Window injiziert (via Sliding Window oder Token Summarization).
- **Long Term Memory (LTM):**
  - Benutzerpräferenzen und Persona-Eigenschaften.
  - Vergangene Interaktionen und Reflexionen ("Lessons Learned").
  - Meist realisiert über Entity-Extraction und Memory-Graphen.
- **Knowledge Memory:**
  - Externe Wissensbasis (Dokumente, APIs).
  - Umgesetzt mittels Vector Databases (Embeddings) und Knowledge Graphs.

### 6. Multi Agent Orchestration
Verantwortlich für die Koordination mehrerer unabhängiger Agenten.
- **Supervisor Agent:** Das "Mainboard". Übernimmt Aufgabenanalyse, bricht diese in Sub-Tasks herunter, delegiert an Spezialisten, priorisiert und aggregiert die Ergebnisse.
- **Specialized Agents:**
  - *Research Agent:* Sucht Fakten und Quellen.
  - *Coding Agent:* Schreibt und modifiziert Code.
  - *Verification Agent:* Testet Outputs auf Korrektheit.
  - *Planning Agent:* Erstellt langfristige Ausführungspläne.
  - *Report Agent:* Formatiert und kommuniziert mit dem Endnutzer.
- **Kommunikation:** Über Channels/Topics (Blackboard-Pattern) oder direkte Message-Queues.

### 7. Security Architecture
Sicherheit als fundamentaler Designaspekt.
- **Permission System (RBAC/ABAC):** Granulare Rechte für Agenten (Darf Agent A in Datenbank B schreiben?).
- **Sandbox:** Isolation von Tool-Execution und Code-Generierung.
- **Secret Management:** Verschlüsselter Tresor (Vault) für API-Keys (z.B. GitHub Tokens), auf den Agenten niemals direkten Plaintext-Zugriff haben, sondern der in den Tool-Wrappern injiziert wird.
- **Nutzerisolation:** Strikte Mandantenfähigkeit (Tenancy-Isolation).
- **Audit Logs:** Immutable Logs für Compliance-Audits.

### 8. Observability
Die Instrumentierung des OS, um Black-Box-Effekte zu vermeiden.
- **Logs:** Strukturierte JSON-Logs für jeden State-Transition-Schritt.
- **Metrics:** Zähler für Token-Verbrauch, Task-Latenzen, Tool-Fehlerraten.
- **Tracing (OpenTelemetry):** Verteilte Tracing-Spans vom User-Request über den Agenten, LLM-Calls bis zur Tool-Execution.
- **Agent Entscheidungsverlauf:** Ein UI-Dashboard (ähnlich LangSmith), das den "Gedankengang" (Chain of Thought) visualisiert.

## Datenflüsse
1. **User Request** -> API Gateway (REST/WebSocket).
2. **Orchestrator** empfängt Request, analysiert Context (Memory) und formuliert einen Plan.
3. Orchestrator delegiert Teilaufgaben an **Worker Agents** über den Event Bus.
4. Worker Agent lädt benötigte **Skills** und fragt den **Model Router** nach Next-Steps (LLM Call).
5. Router führt LLM-Call aus. LLM entscheidet, ein **Tool** zu nutzen.
6. OS fängt Tool-Request ab, verifiziert **Permissions**, führt Tool in der **Sandbox** aus.
7. Tool-Resultat geht zurück ans LLM.
8. Agent fasst Ergebnis zusammen -> Orchestrator aggregiert -> Antwort an User.
