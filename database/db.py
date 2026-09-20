import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from data.seed_data import TICKET_QUEUE

DB_PATH = Path(__file__).resolve().parent.parent / "veridian_agent.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the SQLite schema and seed the assignment ticket queue idempotently."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                employee TEXT NOT NULL,
                issue TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'General',
                priority TEXT NOT NULL DEFAULT 'Medium',
                status TEXT NOT NULL,
                kb_sources TEXT NOT NULL DEFAULT '[]',
                created TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                employee TEXT NOT NULL,
                request TEXT NOT NULL,
                action TEXT NOT NULL,
                kb_sources TEXT NOT NULL DEFAULT '[]',
                decision_basis TEXT NOT NULL DEFAULT '',
                escalation_reason TEXT NOT NULL DEFAULT ''
            )
        """)

        seed_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        for item in TICKET_QUEUE:
            conn.execute("""
                INSERT OR IGNORE INTO tickets
                    (id, employee, issue, category, priority, status, kb_sources, created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item["id"], item["employee"], item["issue"], "Historical", "Medium",
                item["status"], "[]", seed_time,
            ))
        conn.commit()


def _ticket_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "employee": row["employee"],
        "issue": row["issue"],
        "category": row["category"],
        "priority": row["priority"],
        "status": row["status"],
        "kb_sources": json.loads(row["kb_sources"] or "[]"),
        "created": row["created"],
    }


def get_tickets() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM tickets ORDER BY rowid DESC").fetchall()
    return [_ticket_dict(row) for row in rows]


def get_next_ticket_number() -> int:
    with _connect() as conn:
        rows = conn.execute("SELECT id FROM tickets").fetchall()

    numbers = []
    for row in rows:
        try:
            numbers.append(int(row["id"].split("-")[-1]))
        except (ValueError, IndexError):
            pass
    return max(numbers, default=1051) + 1


def insert_ticket(ticket: dict) -> None:
    with _connect() as conn:
        conn.execute("""
            INSERT INTO tickets
                (id, employee, issue, category, priority, status, kb_sources, created)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket["id"],
            ticket["employee"],
            ticket["issue"],
            ticket.get("category", "General"),
            ticket.get("priority", "Medium"),
            ticket["status"],
            json.dumps(ticket.get("kb_sources", [])),
            ticket.get("created", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")),
        ))
        conn.commit()


def insert_audit(entry: dict) -> None:
    with _connect() as conn:
        conn.execute("""
            INSERT INTO audit_logs
                (timestamp, employee, request, action, kb_sources,
                 decision_basis, escalation_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")),
            entry["employee"],
            entry["request"],
            entry["action"],
            json.dumps(entry.get("kb_sources", [])),
            entry.get("decision_basis", ""),
            entry.get("escalation_reason", ""),
        ))
        conn.commit()


def get_audits() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC").fetchall()

    return [{
        "timestamp": row["timestamp"],
        "employee": row["employee"],
        "request": row["request"],
        "action": row["action"],
        "kb_sources": json.loads(row["kb_sources"] or "[]"),
        "decision_basis": row["decision_basis"],
        "escalation_reason": row["escalation_reason"],
    } for row in rows]
