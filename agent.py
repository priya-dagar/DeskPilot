"""Gemini-grounded Veridian Corp Internal IT Service Agent."""

import json
import os
import time
from datetime import datetime, timezone

from google import genai
from data.kb import kb_as_prompt_block

PRIMARY_MODEL = os.environ.get("GEMINI_PRIMARY_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODEL = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-3.6-flash")
MAX_RETRIES = 2
RETRY_DELAYS = [2, 5]

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "decision_basis": {"type": "STRING"},
        "kb_sources": {"type": "ARRAY", "items": {"type": "STRING"}},
        "action": {
            "type": "STRING",
            "enum": ["resolve", "ask_followup", "escalate"],
        },
        "message_to_employee": {"type": "STRING"},
        "followup_question": {"type": "STRING"},
        "escalation_reason": {"type": "STRING"},
        "escalated_to": {"type": "STRING"},
        "ticket_needed": {"type": "BOOLEAN"},
        "ticket_category": {"type": "STRING"},
        "ticket_priority": {
            "type": "STRING",
            "enum": ["Low", "Medium", "High"],
        },
    },
    "required": [
        "decision_basis",
        "kb_sources",
        "action",
        "message_to_employee",
        "followup_question",
        "escalation_reason",
        "escalated_to",
        "ticket_needed",
        "ticket_category",
        "ticket_priority",
    ],
}


def _get_client():
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file or environment."
        )

    return genai.Client(api_key=api_key)


def _is_retryable_error(exc: Exception) -> bool:
    text = str(exc).lower()

    return any(
        x in text
        for x in (
            "429",
            "resource_exhausted",
            "rate_limit",
            "too many requests",
            "503",
            "service unavailable",
            "overloaded",
            "temporarily unavailable",
            "internal server error",
            "500",
        )
    )


def _call_model(client, model: str, contents: str):
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                    "response_schema": RESPONSE_SCHEMA,
                },
            )

        except Exception as exc:
            last_error = exc

            if attempt >= MAX_RETRIES or not _is_retryable_error(exc):
                raise

            time.sleep(
                RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
            )

    raise last_error


def _ticket_history_block(ticket_history: list[dict]) -> str:
    """Format existing tickets as contextual precedent for the agent."""

    if not ticket_history:
        return "No existing ticket history is available."

    lines = []

    for ticket in ticket_history:
        lines.append(
            f"[{ticket.get('id', '')}] "
            f"{ticket.get('employee', '')} | "
            f"{ticket.get('issue', '')} | "
            f"status: {ticket.get('status', '')} | "
            f"category: {ticket.get('category', '')}"
        )

    return "\n".join(lines)


def _build_prompt(
    conversation: list[dict],
    ticket_history: list[dict],
) -> str:
    conversation_text = "\n".join(
        f"{turn['role'].upper()}: {turn['content']}"
        for turn in conversation
    )

    return f"""You are the Internal IT Service Agent for Veridian Corp.

Your ONLY source of policy truth is the knowledge base below. Never invent a policy,
timeline, portal, procedure, approval rule, or fact that is not grounded in the KB.
Existing tickets are historical/contextual evidence only; they do not override current
KB policy.

=== KNOWLEDGE BASE ===
{kb_as_prompt_block()}
=== END KNOWLEDGE BASE ===

=== EXISTING TICKET HISTORY ===
{_ticket_history_block(ticket_history)}
=== END TICKET HISTORY ===

For every employee conversation, return ONLY the required JSON object.

Decision rules:
1. RESOLVE only when the employee has a clear, self-contained action or answer that
   is actually supported by the KB and does not require human approval.
2. ASK_FOLLOWUP when a missing fact changes which policy or owner applies. Ask ONE
   specific question. Do not guess the missing fact.
3. ESCALATE when human approval/review is required, the agent cannot grant the
   requested access/action, a security incident is involved, policies conflict, or
   there is no clear policy grounding.
4. Explaining a policy is NOT the same as resolving a request for approval/access.
5. Never invent a portal or troubleshooting process. Only state procedures explicitly
   present in the KB.
6. Apply only policies relevant to the employee's actual request. Do not introduce
   replacement/refresh rules when the employee is asking for repair/troubleshooting.
7. For KB-04, first establish whether software is in the approved catalog when that
   fact is missing. Catalog software can be self-installed; non-catalog software needs
   Security review.
8. For KB-08, do not assume the Finance-created account exists. If account existence
   matters and is unknown, ask about it.
9. For contractor VPN access under KB-02, manager approval is required. If approval
   status is unknown, ask whether manager approval has been submitted/obtained; do
   not grant access yourself.
10. For hardware issues, distinguish repair/troubleshooting from replacement. A repair
    request does not automatically become a replacement request.
11. If relevant, use ticket history as precedent. For example, TK-1050 is a prior admin
    access request rejected because no business justification was provided. Mention the
    precedent when useful, but do not claim the current request is rejected unless the
    current evidence supports that conclusion.
12. For security incidents (KB-09), always escalate and direct the employee to the
    specified Security reporting channel.
13. The decision_basis must be a short factual explanation suitable for an audit trail,
    NOT hidden chain-of-thought or private reasoning. Keep it to 1-3 concise sentences.

Conversation:
{conversation_text}
"""


def run_agent_turn(
    conversation: list[dict],
    ticket_history: list[dict] | None = None,
) -> dict:
    client = _get_client()
    ticket_history = ticket_history or []

    contents = _build_prompt(
        conversation,
        ticket_history,
    )

    errors = []

    for model in (PRIMARY_MODEL, FALLBACK_MODEL):
        try:
            response = _call_model(
                client,
                model,
                contents,
            )

            raw = getattr(response, "text", None)

            if not raw:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            decision = json.loads(raw)

            required = [
                "decision_basis",
                "kb_sources",
                "action",
                "message_to_employee",
                "followup_question",
                "escalation_reason",
                "escalated_to",
                "ticket_needed",
                "ticket_category",
                "ticket_priority",
            ]

            missing = [
                key for key in required
                if key not in decision
            ]

            if missing:
                raise RuntimeError(
                    f"Agent response missing required fields: {missing}"
                )

            if decision["action"] not in {
                "resolve",
                "ask_followup",
                "escalate",
            }:
                raise RuntimeError(
                    f"Invalid action: {decision['action']}"
                )

            return decision

        except Exception as exc:
            errors.append(f"{model}: {exc}")

            if not _is_retryable_error(exc):
                raise

    raise RuntimeError(
        "All Gemini models failed. " + " | ".join(errors)
    )


def make_ticket(
    next_number: int,
    employee: str,
    request_text: str,
    decision: dict,
) -> dict:
    now = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M UTC"
    )

    status = {
        "resolve": "Resolved (auto)",
        "ask_followup": "Pending employee response",
        "escalate": (
            f"Escalated to "
            f"{decision.get('escalated_to') or 'human review'}"
        ),
    }.get(
        decision["action"],
        "Open",
    )

    return {
        "id": f"TK-{next_number}",
        "employee": employee,
        "issue": request_text,
        "category": decision.get(
            "ticket_category",
            "General",
        ),
        "priority": decision.get(
            "ticket_priority",
            "Medium",
        ),
        "status": status,
        "kb_sources": decision.get(
            "kb_sources",
            [],
        ),
        "created": now,
    }


def make_audit_entry(
    employee: str,
    request_text: str,
    decision: dict,
) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        ),
        "employee": employee,
        "request": request_text,
        "action": decision["action"],
        "kb_sources": decision.get(
            "kb_sources",
            [],
        ),
        "decision_basis": decision.get(
            "decision_basis",
            "",
        ),
        "escalation_reason": decision.get(
            "escalation_reason",
            "",
        ),
    }