# Architecture & Process Flow

## Process Flow

```text
Employee Request
       │
       ▼
Build Context
(Request + conversation history + IT Knowledge Base)
       │
       ▼
Gemini AI Agent
       │
       ├── Resolve ──────► Response + Ticket
       │
       ├── Follow-up ────► Ask employee → Continue conversation
       │
       └── Escalate ─────► Response + Escalated Ticket
       │
       ▼
Audit Trail
(Action + KB sources + decision basis + timestamp)
```

### Core Workflow

**Understand → Ground in Policy → Decide → Act → Record**

The agent can resolve requests, ask for missing information, or escalate requests that require human intervention.

---

## Components

* **`app.py`** — Streamlit UI with Agent Console, Ticket Queue and Audit Trail.
* **`agent.py`** — Builds the prompt, calls Gemini, validates structured output and handles agent decisions.
* **`data/kb.py`** — Internal IT knowledge base and Asset Management Policy; primary policy source.
* **`data/seed_data.py`** — Demo employee requests and existing ticket data.
* **`database/`** — SQLite database for tickets and audit records.

---

## Inputs, Sources & Assumptions

### Inputs

* Employee IT request
* Conversation history
* Relevant ticket/history context
* Internal IT policies

### Source of Truth

The agent is grounded only in the provided IT Knowledge Base and Asset Management Policy stored in `data/kb.py`. It is instructed not to invent unsupported policies or requirements.

### Key Assumptions

* If required information is missing, the agent asks a follow-up instead of guessing.
* Policy conflicts are surfaced rather than silently resolved.
* Demo data represents simulated enterprise data.
* Requests requiring human intervention are escalated rather than falsely marked as completed.

---

## AI Tools Used

### Google Gemini

Used as the runtime AI agent for:

* Understanding employee requests
* Identifying applicable policies
* Selecting resolve / follow-up / escalate
* Generating employee responses
* Producing structured decision data

### Claude

Used during development for:

* Agent workflow and schema design
* Streamlit UI implementation
* Documentation assistance

Claude is **not** the runtime AI model in the deployed application.

---

## Technology Stack

* **Python** — Agent and application logic
* **Google Gemini** — Runtime AI
* **Streamlit** — Web interface
* **SQLite** — Ticket and audit persistence
* **GitHub** — Version control and source code
* **Streamlit Cloud** — Deployment
