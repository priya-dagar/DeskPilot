# Veridian Corp — Internal IT Service Agent

An LLM-grounded agent that handles internal IT employee-support requests:
understands the issue, finds the relevant policy, asks follow-up questions
when needed, resolves simple requests, escalates risky/unclear ones, creates
a structured ticket, cites its source, and keeps a full audit trail.

## Why this isn't rule-based

All classification, policy-matching, and resolve/escalate reasoning is done
by the LLM at request time, grounded in the knowledge base text passed into
its prompt (`data/kb.py`). Python code only builds the prompt, parses the
structured JSON response, and manages ticket numbering / the audit log — it
never hardcodes "if request contains X then Y".

## Run it (one command after setup)

```bash
pip install -r requirements.txt
cp .env.example .env   # then paste your OPENAI_API_KEY into .env
streamlit run app.py
```

Opens at `http://localhost:8501`.

## How to demo it

1. **Agent Console tab** — pick any of the 15 preloaded employee requests
   (from the data pack) or type a new one, then click "Run agent".
2. Watch the agent's action badge (RESOLVE / ASK_FOLLOWUP / ESCALATE) and the
   KB article(s) it cites. Expand "Agent reasoning" to see why.
3. If it asks a follow-up question, type the employee's reply and continue
   the conversation.
4. **Ticket Queue tab** — see the original 10 tickets plus any new ones the
   agent created this session.
5. **Audit Trail tab** — every decision the agent made, with timestamp,
   action, and KB sources, for full traceability.

## Good test cases to run live

- `REQ-01` (Aditi's dead laptop, 3.5 yrs old) — tests policy conflict
  detection: KB-03 (3-year eligibility) vs. the Asset Management Policy
  (4-year cycle, needs Finance sign-off too).
- `REQ-08` (Ananya forwarding a phishing email to teammates) — tests that the
  agent flags a policy violation even though the ticket is already "handled".
- `REQ-10` (Kavya wants admin access to a finance server) — tests escalation
  with no clear policy grounding, referencing precedent (TK-1050 was rejected
  for the same reason).
- `REQ-15` (Rahul: "hey can you help, its not working") — tests that the
  agent asks a sensible follow-up instead of guessing.

## Architecture

See `ARCHITECTURE.md` for the process flow diagram, inputs/assumptions, and
the list of AI tools used.
