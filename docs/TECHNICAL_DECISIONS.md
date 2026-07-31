# TECHNICAL DECISIONS: AI-Agent-OS

Dieses Dokument protokolliert die zentralen Architekturentscheidungen (Architecture Decision Records - ADRs) für das AI-Agent-OS, die während der Initialphase getroffen wurden.

## 1. Programmiersprache & Kern-Framework
**Entscheidung:** Python als primäre Backend-Sprache (mit `asyncio` / FastAPI).
- **Begründung:** Python ist unbestritten der Branchenstandard für KI und LLMs. Fast alle Major-Provider (OpenAI, Anthropic, Google) bieten First-Class Python SDKs an. Wichtige Ökosystem-Bibliotheken (LangChain, LlamaIndex, PyTorch) existieren primär in Python.
- **Alternative:** TypeScript / Node.js.
- **Nachteil der Alternative:** Node.js ist hervorragend für I/O und Event-Loops, hinkt jedoch im Bereich der tiefergehenden KI-Bibliotheken und Data-Science-Tools stark hinterher.
- **Kompromiss:** Für spätere UIs und Client-SDKs wird TypeScript genutzt. Das Backend bleibt Python.

## 2. Kommunikation & Nebenläufigkeit (Concurrency)
**Entscheidung:** Asynchrone, ereignisgesteuerte Architektur mittels `asyncio` und einem internen Message-Bus (wie Redis Pub/Sub oder RabbitMQ für verteilte Setups).
- **Begründung:** LLM-Calls, Tool-Ausführungen und Web-Requests sind extrem I/O-lastig. Eine synchrone (blockierende) Architektur würde das System lähmen. Multi-Agenten-Systeme erfordern zudem asynchrone Nachrichtenübermittlung.

## 3. Datenbank und Memory Storage
**Entscheidung:** PostgreSQL (relational) + pgvector (Vektor-Suche) als primärer Datenspeicher.
- **Begründung:** Um die Systemarchitektur einfach zu halten und den "Operational Overhead" zu minimieren, vereinen wir strukturierte relationale Daten (Agent States, Task Logs, User Profiles) und Vektordaten (Embeddings für Memory) in einem System. PostgreSQL mit der `pgvector` Extension ist robust, skalierbar und Enterprise-ready.
- **Alternative:** MongoDB (Dokumente) + Chroma/Pinecone (Vektor) + Redis (State).
- **Nachteil der Alternative:** Drei separate Datenbanksysteme zu betreiben und konsistent zu halten, ist anfangs eine zu hohe Komplexität.

## 4. Tool Execution & Sandboxing
**Entscheidung:** Zwei-Klassen-Modell für Tools. Isolierte (Docker/MicroVM) Sandbox für "Code Execution", direkte In-Process-Ausführung für harmlose API-Calls (wie Wetter-Abfrage).
- **Begründung:** KI-generierter Code, der serverseitig ausgeführt wird, birgt massive Sicherheitsrisiken (RCE, Data Exfiltration). Alles, was dynamischen Code oder Shell-Befehle betrifft, MUSS in kurzlebigen, netzwerk-isolierten Sandboxes laufen.
- **Alternative:** Alles nativ ausführen.
- **Nachteil:** Inakzeptables Sicherheitsrisiko für ein OS-ähnliches System.

## 5. Model Routing & Interoperabilität
**Entscheidung:** Standardisierung aller LLM-Calls intern auf das OpenAI-Message-Format und Nutzung von Adaptern/Proxies (z.B. LiteLLM) für andere Provider.
- **Begründung:** Das OpenAI Format (`role: system/user/assistant`, `tool_calls`) hat sich als De-facto-Standard etabliert. Eine Normalisierung vereinfacht den Agent Kernel drastisch, da er sich nicht um provider-spezifische Eigenheiten kümmern muss.

## 6. Observability
**Entscheidung:** OpenTelemetry (OTel) als Standard für Traces, Metrics und Logs.
- **Begründung:** OTel ermöglicht es, Backends wie Jaeger, Prometheus, Datadog oder LangSmith modular anzubinden. Agent-Interaktionen lassen sich hervorragend als verschachtelte Spans darstellen (Task -> Agent Run -> LLM Call -> Tool Execution).
