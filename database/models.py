"""Data models for the SQLite persistence layer.

The project intentionally uses Python's built-in sqlite3 module rather than an ORM.
"""

from dataclasses import dataclass


@dataclass
class Ticket:
    id: str
    employee: str
    issue: str
    category: str = "General"
    priority: str = "Medium"
    status: str = "Open"
    kb_sources: list[str] | None = None
    created: str = ""


@dataclass
class AuditLog:
    employee: str
    request: str
    action: str
    kb_sources: list[str] | None = None
    decision_basis: str = ""
    escalation_reason: str = ""
    timestamp: str = ""
