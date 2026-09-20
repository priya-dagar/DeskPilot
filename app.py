import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from html import escape

load_dotenv()

from data.seed_data import EMPLOYEE_REQUESTS, TICKET_QUEUE, NEXT_TICKET_NUMBER
from agent import run_agent_turn, make_ticket, make_audit_entry

st.set_page_config(
    page_title="Veridian IT Service Agent",
    page_icon="🛠️",
    layout="wide"
)

# ---------------------------------------------------------------- styling ---

st.markdown("""
<style>
/* ============================================================
   THEME-AWARE COLORS
   ============================================================ */

:root {
    --accent: var(--primary-color);
    --bg: var(--background-color);
    --surface: var(--secondary-background-color);
    --text: var(--text-color);

    --border: rgba(128, 128, 128, 0.25);
    --muted: rgba(128, 128, 128, 0.85);

    --ok-bg: rgba(34, 197, 94, 0.15);
    --ok-text: #22c55e;

    --warn-bg: rgba(245, 158, 11, 0.15);
    --warn-text: #f59e0b;

    --danger-bg: rgba(239, 68, 68, 0.15);
    --danger-text: #ef4444;

    --accent-bg: rgba(99, 102, 241, 0.15);
    --accent-text: #818cf8;
}

/* Main application background */

.stApp {
    background: var(--bg);
    color: var(--text);
}

.block-container {
    padding-top: 1.6rem;
    max-width: 1200px;
}

/* ============================================================
   HEADER
   ============================================================ */

.va-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 22px;
    border-radius: 16px;

    background: linear-gradient(
        135deg,
        #4f46e5 0%,
        #4f7cff 60%,
        #38bdf8 100%
    );

    color: white;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.25);
}

.va-header h1 {
    font-size: 1.35rem;
    margin: 0;
    font-weight: 700;
    color: white;
}

.va-header p {
    margin: 2px 0 0 0;
    opacity: 0.9;
    font-size: 0.88rem;
    color: white;
}

/* ============================================================
   METRICS
   ============================================================ */

.va-metric {
    background: var(--surface);
    color: var(--text);

    border-radius: 14px;
    padding: 14px 18px;

    border: 1px solid var(--border);
    text-align: center;
}

.va-metric .num {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
}

.va-metric .lbl {
    font-size: 0.78rem;
    color: var(--muted);

    text-transform: uppercase;
    letter-spacing: .04em;
}

/* ============================================================
   BADGES
   ============================================================ */

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;

    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: .02em;

    margin-right: 4px;
}

.badge-resolve {
    background: var(--ok-bg);
    color: var(--ok-text);
}

.badge-followup {
    background: var(--warn-bg);
    color: var(--warn-text);
}

.badge-escalate {
    background: var(--danger-bg);
    color: var(--danger-text);
}

.badge-kb {
    background: var(--accent-bg);
    color: var(--accent-text);
}

/* ============================================================
   TICKET CARDS
   ============================================================ */

.ticket-card {
    background: var(--surface);
    color: var(--text);

    border-radius: 12px;
    padding: 12px 16px;

    border: 1px solid var(--border);
    margin-bottom: 8px;
}

.ticket-card .tid {
    font-weight: 700;
    color: var(--text);
}

.ticket-card .issue {
    color: var(--text);
}

.ticket-card .status {
    font-size: 0.8rem;
    color: var(--muted);
}

/* ============================================================
   AUDIT ENTRIES
   ============================================================ */

.audit-entry {
    background: var(--surface);
    color: var(--text);

    border-left: 3px solid var(--accent);
    border-radius: 8px;

    padding: 10px 14px;
    margin-bottom: 8px;

    font-size: 0.86rem;
}

.audit-entry .muted {
    color: var(--muted);
}

/* ============================================================
   STREAMLIT INPUTS
   ============================================================ */

.stTextInput input,
.stTextArea textarea {
    color: var(--text) !important;
    background-color: var(--surface) !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--surface);
    color: var(--text);
}

/* ============================================================
   STREAMLIT TABS
   ============================================================ */

button[data-baseweb="tab"] {
    color: var(--text);
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent);
}

/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border-color: var(--border);
}

/* ============================================================
   EXPANDERS
   ============================================================ */

div[data-testid="stExpander"] {
    border-color: var(--border);
    background: var(--surface);
}

/* ============================================================
   CHAT MESSAGES
   ============================================================ */

div[data-testid="stChatMessage"] {
    border-radius: 12px;
}

/* ============================================================
   INFO / WARNING / ERROR BOXES
   ============================================================ */

div[data-testid="stAlert"] {
    border-radius: 10px;
}

/* ============================================================
   DARK MODE EXTRA OVERRIDES
   ============================================================ */

@media (prefers-color-scheme: dark) {
    .ticket-card,
    .va-metric,
    .audit-entry {
        box-shadow: none;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- header ---

st.markdown("""
<div class="va-header">
  <div style="font-size:2rem;">🛠️</div>
  <div>
    <h1>Veridian Corp &middot; Internal IT Service Agent</h1>
    <p>
        LLM-grounded on the IT knowledge base
        &middot; understands, resolves, escalates
        &middot; full audit trail
    </p>
  </div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------ source helper ---

def format_sources(sources) -> str:
    """Return source IDs as readable, separate labels."""
    if not sources:
        return "None"

    return " · ".join(
        str(source).strip()
        for source in sources
        if str(source).strip()
    )


# ------------------------------------------------------------------ state ---

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "active_request" not in st.session_state:
    st.session_state.active_request = None

if "tickets" not in st.session_state:
    st.session_state.tickets = list(TICKET_QUEUE)

if "next_ticket_num" not in st.session_state:
    st.session_state.next_ticket_num = NEXT_TICKET_NUMBER

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

if "last_decision" not in st.session_state:
    st.session_state.last_decision = None


# --------------------------------------------------------------- metrics ---

resolved_ct = sum(
    1
    for t in st.session_state.tickets
    if "Resolved" in t["status"] or "auto" in t["status"]
)

escalated_ct = sum(
    1
    for t in st.session_state.tickets
    if "Escalated" in t["status"]
)

open_ct = len(st.session_state.tickets) - resolved_ct


m1, m2, m3, m4 = st.columns(4)

for col, num, lbl in [
    (m1, len(st.session_state.tickets), "Total tickets"),
    (m2, resolved_ct, "Resolved"),
    (m3, escalated_ct, "Escalated"),
    (m4, open_ct, "Open / pending"),
]:
    with col:
        st.markdown(
            f"""
            <div class="va-metric">
                <div class="num">{num}</div>
                <div class="lbl">{lbl}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


st.write("")

tab_chat, tab_tickets, tab_audit = st.tabs(
    ["💬 Agent Console", "🎫 Ticket Queue", "🧾 Audit Trail"]
)


# ============================================================= CHAT TAB ===

with tab_chat:

    left, right = st.columns([1, 2])

    # ---------------------------------------------------------- left panel

    with left:

        st.subheader("Pick a request")

        options = {
            f"{r['id']} — {r['employee']}": r
            for r in EMPLOYEE_REQUESTS
        }

        choice = st.selectbox(
            "Preloaded employee requests",
            list(options.keys()),
            index=None,
            placeholder="Choose a request from the data pack..."
        )

        if st.button(
            "Load request",
            use_container_width=True,
            disabled=choice is None
        ):
            r = options[choice]

            st.session_state.active_request = {
                "employee": r["employee"],
                "text": r["text"]
            }

            st.session_state.conversation = [
                {
                    "role": "user",
                    "content": r["text"]
                }
            ]

            st.session_state.last_decision = None

            st.rerun()

        st.divider()

        st.subheader("Or type a new one")

        with st.form("new_request_form", clear_on_submit=True):

            emp_name = st.text_input(
                "Employee name",
                value=""
            )

            new_text = st.text_area(
                "Issue",
                height=90
            )

            submitted = st.form_submit_button(
                "Start conversation",
                use_container_width=True
            )

            if submitted and new_text.strip():

                st.session_state.active_request = {
                    "employee": emp_name or "Employee",
                    "text": new_text
                }

                st.session_state.conversation = [
                    {
                        "role": "user",
                        "content": new_text
                    }
                ]

                st.session_state.last_decision = None

                st.rerun()

    # --------------------------------------------------------- right panel

    with right:

        if not st.session_state.active_request:

            st.info(
                "Pick a preloaded request or type a new one "
                "to start the agent."
            )

        else:

            emp = st.session_state.active_request["employee"]

            st.markdown(f"**Employee:** {emp}")

            # Conversation
            for turn in st.session_state.conversation:

                role = (
                    "user"
                    if turn["role"] == "user"
                    else "assistant"
                )

                avatar = (
                    "🧑"
                    if role == "user"
                    else "🛠️"
                )

                with st.chat_message(role, avatar=avatar):
                    st.write(turn["content"])

            # Run agent
            run_col, _ = st.columns([1, 3])

            if (
                st.session_state.last_decision is None
                or st.session_state.conversation[-1]["role"] == "user"
            ):

                if run_col.button(
                    "▶ Run agent",
                    type="primary"
                ):

                    with st.spinner(
                        "Analyzing the request against the knowledge base..."
                    ):

                        try:
                            decision = run_agent_turn(
                                st.session_state.conversation
                            )

                        except Exception as e:
                            st.error(
                                f"Agent error: {e}"
                            )
                            decision = None

                    if decision:

                        st.session_state.last_decision = decision

                        st.session_state.conversation.append(
                            {
                                "role": "assistant",
                                "content": decision[
                                    "message_to_employee"
                                ]
                            }
                        )

                        st.session_state.audit_log.append(
                            make_audit_entry(
                                emp,
                                st.session_state.active_request[
                                    "text"
                                ],
                                decision
                            )
                        )

                        if decision.get("ticket_needed"):

                            ticket = make_ticket(
                                st.session_state.next_ticket_num,
                                emp,
                                st.session_state.active_request[
                                    "text"
                                ],
                                decision
                            )

                            st.session_state.tickets.insert(
                                0,
                                ticket
                            )

                            st.session_state.next_ticket_num += 1

                        st.rerun()

            # ------------------------------------------------ decision

            d = st.session_state.last_decision

            if d:

                badge_class = {
                    "resolve": "badge-resolve",
                    "ask_followup": "badge-followup",
                    "escalate": "badge-escalate"
                }[d["action"]]

                st.markdown(
                    f'<span class="badge {badge_class}">'
                    f'{escape(d["action"].upper())}'
                    f'</span> '
                    +
                    "".join(
                        f'<span class="badge badge-kb">'
                        f'{escape(str(s))}'
                        f'</span>'
                        for s in d.get("kb_sources", [])
                        if s
                    ),
                    unsafe_allow_html=True
                )

                with st.expander(
                    "Decision Basis"
                ):

                    st.write(
                        d.get(
                            "decision_basis",
                            d.get("reasoning", "")
                        )
                    )

                    if d["action"] == "escalate":

                        st.write(
                            f"**Escalated to:** "
                            f"{d.get('escalated_to', '')}"
                        )

                        st.write(
                            f"**Reason:** "
                            f"{d.get('escalation_reason', '')}"
                        )

                # ------------------------------------------------ follow-up

                if d["action"] == "ask_followup":

                    reply = st.text_input(
                        "Employee's reply to the follow-up question:",
                        key="followup_reply"
                    )

                    if st.button("Send reply") and reply.strip():

                        st.session_state.conversation.append(
                            {
                                "role": "user",
                                "content": reply
                            }
                        )

                        st.session_state.last_decision = None

                        st.rerun()


# ========================================================== TICKETS TAB ===

with tab_tickets:

    st.subheader("Ticket queue")

    for t in st.session_state.tickets:

        status = str(t["status"])

        if (
            "Resolved" in status
            or "auto" in status
        ):
            dot = "🟢"

        elif "Escalated" in status:
            dot = "🔴"

        elif "Rejected" in status:
            dot = "⚫"

        else:
            dot = "🟡"

        ticket_id = escape(str(t.get("id", "")))
        employee = escape(str(t.get("employee", "")))
        issue = escape(str(t.get("issue", "")))
        status_safe = escape(status)

        # Use a single-line HTML block so Streamlit renders it as HTML
        # rather than interpreting the indentation as a code block.
        ticket_html = (
            '<div class="ticket-card">'
            f'<span class="tid">{dot} {ticket_id}</span>'
            f' &middot; {employee}'
            '<br/>'
            f'<span class="issue">{issue}</span>'
            '<br/>'
            f'<span class="status">{status_safe}</span>'
            '</div>'
        )

        st.markdown(
            ticket_html,
            unsafe_allow_html=True
        )


# ============================================================ AUDIT TAB ===

with tab_audit:

    st.subheader("Audit trail")

    if not st.session_state.audit_log:

        st.caption(
            "No agent decisions logged yet this session."
        )

    for entry in reversed(
        st.session_state.audit_log
    ):

        sources = format_sources(
            entry.get("kb_sources", [])
        )

        timestamp = escape(
            str(entry.get("timestamp", ""))
        )

        employee = escape(
            str(entry.get("employee", ""))
        )

        action = escape(
            str(entry.get("action", ""))
        )

        sources_safe = escape(
            sources
        )

        decision_basis = escape(
            str(
                entry.get(
                    "decision_basis",
                    entry.get("reasoning", "")
                )
            )
        )

        escalation_reason = escape(
            str(
                entry.get(
                    "escalation_reason",
                    ""
                )
            )
        )

        escalation_html = ""

        if escalation_reason:
            escalation_html = (
                '<br/>'
                '<span class="muted">'
                '<b>Escalation reason:</b> '
                f'{escalation_reason}'
                '</span>'
            )

        audit_html = (
            '<div class="audit-entry">'
            f'<b>{timestamp}</b>'
            f' &middot; {employee}'
            f' &middot; action: <b>{action}</b>'
            f' &middot; sources: {sources_safe}'
            '<br/>'
            f'{decision_basis}'
            f'{escalation_html}'
            '</div>'
        )

        st.markdown(
            audit_html,
            unsafe_allow_html=True
        )