# Architecture & Process Flow

## Process flow

```
Employee message
      │
      ▼
[1] Build prompt: system prompt (full KB text) + conversation so far
      │
      ▼
[2] LLM call (OpenAI, JSON-mode) reasons over the KB and decides:
      - which KB article(s) actually apply
      - action: resolve / ask_followup / escalate
      - the reply to send the employee
      - whether a ticket is needed, its category & priority
      │
      ▼
[3] Python parses & validates the structured JSON
      │
      ├── ask_followup ──► shown to employee, their reply is appended to the
      │                     conversation, loop back to [1]
      │
      ├── resolve ───────► reply shown, ticket created with status
      │                     "Resolved (auto)", closed
      │
      └── escalate ──────► reply shown, ticket created with status
                            "Escalated to <human/team>", left open
      │
      ▼
[4] Audit trail entry appended (timestamp, employee, action, KB sources,
    reasoning) — visible in the Audit Trail tab, independent of the ticket
    queue, so every decision is traceable even ones that didn't need a ticket
```

## Components

- `data/kb.py` — the 10 KB articles + Asset Management Policy extract. Sole
  source of policy truth given to the LLM.
- `data/seed_data.py` — the 15 employee requests and existing ticket queue
  (TK-1042–TK-1051) from the data pack, used to pre-populate the demo.
- `agent.py` — builds the grounding prompt, calls the OpenAI API in JSON
  mode, validates the response shape, and builds ticket/audit records from
  it. No keyword or if/else classification of the employee's issue happens
  here — that reasoning is entirely the LLM's.
- `app.py` — Streamlit UI: Agent Console (chat), Ticket Queue, Audit Trail.

## Inputs, sources & assumptions

- **Source of truth**: only the 10 KB articles + Asset Management Policy
  extract from the provided data pack. The agent is explicitly instructed
  never to invent a policy not grounded there.
- **Assumption**: "full-time vs. contractor" and "manager sign-off status"
  are often not stated in a request (e.g. REQ-11's new contractor, REQ-07's
  WFH monitor) — the agent is expected to ask a follow-up rather than guess,
  per the KB-02/KB-10 approval requirements.
- **Assumption**: where a KB article and the Asset Management Policy extract
  give different eligibility windows for hardware replacement (3 years vs.
  4-year refresh cycle), this is treated as a genuine policy conflict for the
  agent to surface, not something to silently resolve one way.
- **Assumption**: ticket numbering continues from the existing queue
  (next ticket is TK-1052).
- Model used: OpenAI `gpt-4o-mini` by default (configurable via
  `OPENAI_MODEL` env var) for a good cost/latency/quality balance for this
  scale of task; JSON response mode is used for structured, parseable output.

## AI tools used in building this

- Claude (Anthropic) was used to design the agent's decision schema, write
  the Streamlit UI/styling, and draft this documentation, working from the
  provided assignment brief and data pack as the only source material.
