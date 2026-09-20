# Veridian Corp — Internal IT Service Agent

**DeskPilot** is an AI-powered internal IT support agent that helps employees with common IT requests. It understands the request, grounds its response in the provided IT knowledge base, and decides whether to **resolve, ask for clarification, or escalate**.

The application also creates structured tickets and maintains an audit trail for traceability.

## Live Demo

**Live App:** https://deskpilot.streamlit.app/

**GitHub:** https://github.com/priya-dagar/DeskPilot

---

## Key Features

* Natural-language IT support requests
* Policy-grounded AI responses
* Resolve / Follow-up / Escalate workflow
* Structured ticket creation
* Ticket Queue
* Audit Trail
* Conversation and ticket history context
* Preloaded demo requests and ticket data
* Persistent SQLite storage

## How It Works

```text
Employee Request
       ↓
Gemini AI Agent
       ↓
Policy / Knowledge Base
       ↓
Decision
 ┌─────┼─────────┐
 ↓     ↓         ↓
Resolve Follow-up Escalate
 ↓     ↓         ↓
Ticket Conversation Ticket
       ↓
   Audit Trail
```

The core workflow is:

**Understand → Ground → Decide → Act → Record**

For ambiguous requests, the agent asks for the required information instead of guessing. Requests requiring human intervention are escalated.

## Knowledge Base

The primary policy source is:

```text
data/kb.py
```

It contains the provided internal IT knowledge-base content and Asset Management Policy information.

The agent is instructed to use this information as its policy source and avoid inventing unsupported policies or requirements.

Demo data is stored in:

```text
data/seed_data.py
```

## Technology Stack

* **Python** — Application and agent logic
* **Google Gemini** — Runtime AI agent
* **Streamlit** — Web interface
* **SQLite** — Ticket and audit persistence
* **GitHub** — Source control
* **Streamlit Community Cloud** — Deployment

## Project Structure

```text
DeskPilot/
├── app.py
├── agent.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── data/
│   ├── __init__.py
│   ├── kb.py
│   └── seed_data.py
└── database/
    ├── __init__.py
    ├── db.py
    └── models.py
```

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

The application will open at:

```text
http://localhost:8501
```

## Demo Flow

For a live demonstration:

1. Open the **Agent Console**.
2. Select a preloaded request or enter a new IT request.
3. Run the agent.
4. Observe the selected action:

   * **RESOLVE**
   * **ASK_FOLLOWUP**
   * **ESCALATE**
5. Continue the conversation if a follow-up is requested.
6. Open **Ticket Queue** to view generated tickets.
7. Open **Audit Trail** to view recorded decisions and policy sources.

## Example Scenarios

### Guest Wi-Fi Request

Demonstrates a straightforward request that can be resolved using the available policy information.

### Laptop Replacement

Demonstrates policy-aware handling where eligibility and approval requirements need to be considered.

### Ambiguous Request

A vague request such as:

```text
"Hey, can you help? It's not working."
```

demonstrates that the agent asks for clarification instead of guessing.

### Security / Phishing Request

Demonstrates escalation of a security-related request for appropriate human/team intervention.

## AI Tools Used

### Google Gemini

Used at runtime for natural-language understanding, policy matching, action selection, response generation, and structured decision output.

### Claude

Used during development for agent workflow design, UI implementation assistance, and documentation.

Claude is **not** the runtime AI model of the deployed application.

## Security

* API keys are stored through environment variables locally.
* The deployed application uses Streamlit secrets.
* API keys and local database files are excluded from Git using `.gitignore`.
* The repository contains no API credentials.

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the system architecture, process flow, inputs, assumptions, and AI tools used.
