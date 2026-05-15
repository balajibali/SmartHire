import streamlit as st
import pandas as pd
from datetime import datetime
from database.db import get_connection
from services.ollama_service import generate_ai_response
from nav import go_back


# =========================
# 🎯 MAIN PAGE
# =========================
def show():
    load_css()

    # 🔐 AUTH
    if not st.session_state.get("logged_in"):
        st.warning("Please login first")
        st.session_state.page = "login"
        st.rerun()

    # =========================
    # HEADER
    # =========================
    col1, col2 = st.columns([6, 1])

    with col1:
        st.markdown("<h2 class='title'>Dashboard</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<p class='welcome'>Welcome back, {st.session_state.get('email')}</p>",
            unsafe_allow_html=True
        )

    with col2:
        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.rerun()

    # =========================
    # MENU
    # =========================
    if "nav_open" not in st.session_state:
        st.session_state.nav_open = False

    if st.button("Menu", key="menu_btn"):
        st.session_state.nav_open = not st.session_state.nav_open

    if st.session_state.nav_open:
        c1, c2, c3, c4, c5 = st.columns(5)

        if c1.button("Create Job"):
            st.session_state.page = "create_job"
            st.rerun()

        if c2.button("View Jobs"):
            st.session_state.page = "view_jobs"
            st.rerun()

        if c3.button("Upload Resume"):
            st.session_state.page = "upload_resume"
            st.rerun()

        if c4.button("Shortlisted"):
            st.session_state.page = "shortlisted"
            st.rerun()

        if c5.button("Recommendation"):
            st.session_state.page = "recommendation"
            st.rerun()

    st.divider()

    # =========================
    # KPI CARDS
    # =========================
    jobs, candidates = get_stats()

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(card("Total Jobs", jobs, "blue"), unsafe_allow_html=True)
    c2.markdown(card("Candidates", candidates, "purple"), unsafe_allow_html=True)
    c3.markdown(
        card("Shortlisted", get_total_shortlisted(), "green"),
        unsafe_allow_html=True
    )
    c4.markdown(
        card("Pending", get_pending(), "orange"),
        unsafe_allow_html=True
    )

    st.divider()

    # =========================
    # 📄 RECENT JOBS
    # =========================
    left, right = st.columns([6, 1])

    with left:
        st.markdown("<h4>Recent Jobs</h4>", unsafe_allow_html=True)

    with right:
        if st.button("View Jobs", key="view_jobs_top"):
            st.session_state.page = "view_jobs"
            st.rerun()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                j.id,
                j.title,
                j.deadline,
                (SELECT COUNT(*) FROM candidates c WHERE c.job_id = j.id),
                (
                    SELECT COUNT(*)
                    FROM candidates c
                    WHERE c.job_id = j.id
                    AND c.status='Shortlisted'
                )
            FROM jobs j
            WHERE j.user_id=?
            ORDER BY j.id DESC
            LIMIT 5
        """, (st.session_state.user_id,))

        jobs_data = cursor.fetchall()
        conn.close()

        if jobs_data:
            rows = []

            for row in jobs_data:
                job_id, title, deadline, applied, shortlisted = row

                if not title:
                    continue

                status = compute_status(deadline)

                rows.append([
                    title,
                    applied or 0,
                    shortlisted or 0,
                    deadline or "-",
                    badge(status)
                ])

            if rows:
                df = pd.DataFrame(
                    rows,
                    columns=[
                        "Job Title",
                        "Applied",
                        "Shortlisted",
                        "Deadline",
                        "Status"
                    ]
                )

                df = df.dropna(how="all")

                st.markdown(
                    df.to_html(index=False, escape=False),
                    unsafe_allow_html=True
                )

            else:
                st.info("No valid jobs found")

        else:
            st.info("No jobs found")

    except Exception as e:
        st.error(e)

    st.divider()

    # =========================
    # 🤖 AI ASSISTANT
    # =========================
    st.subheader("AI Assistant")

    # 🧠 INIT MEMORY
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    query = st.text_input("Ask anything", key="chat_input")

    # 🚀 SUBMIT
    submit = st.button("Submit")

    # 💬 DISPLAY CHAT
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**AI:** {msg['content']}")

    # 🗑 CLEAR CHAT
    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    # 🚀 PROCESS AI
    if submit:

        if not query:
            st.warning("Please enter a question")
            return

        try:
            with st.spinner("AI thinking..."):

                q = query.lower()

                is_general = any(word in q for word in [
                    "create",
                    "generate",
                    "write",
                    "how",
                    "what",
                    "jd",
                    "job description",
                    "resume",
                    "interview"
                ])

                candidate_context = ""
                job_context = ""

                if not is_general:

                    conn = get_connection()
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT name, skills, experience 
                        FROM candidates
                        WHERE job_id IN (
                            SELECT id FROM jobs WHERE user_id=?
                        )
                        LIMIT 5
                    """, (st.session_state.user_id,))

                    candidates_data = cursor.fetchall()

                    cursor.execute("""
                        SELECT title, skills, experience 
                        FROM jobs
                        WHERE user_id=?
                        ORDER BY id DESC
                        LIMIT 3
                    """, (st.session_state.user_id,))

                    jobs_data = cursor.fetchall()

                    conn.close()

                    for c in candidates_data:
                        candidate_context += (
                            f"Name: {c[0]}, "
                            f"Skills: {c[1]}, "
                            f"Exp: {c[2]}\n"
                        )

                    for j in jobs_data:
                        job_context += (
                            f"Job: {j[0]}, "
                            f"Skills: {j[1]}, "
                            f"Exp: {j[2]}\n"
                        )

                history_text = ""

                for m in st.session_state.chat_history[-5:]:
                    role = "User" if m["role"] == "user" else "AI"
                    history_text += f"{role}: {m['content']}\n"

                if is_general:

                    prompt = f"""
You are an expert AI assistant.

Conversation:
{history_text}

User: {query}

Give a helpful answer.
"""

                else:

                    prompt = f"""
You are an AI Recruitment Assistant.

Conversation:
{history_text}

=== JOBS ===
{job_context}

=== CANDIDATES ===
{candidate_context}

User: {query}

Answer using data. Keep it short.
"""

                response = generate_ai_response(prompt)

                if not response or response.strip() == "":
                    response = "No response. Try again."

                st.session_state.chat_history.append({
                    "role": "user",
                    "content": query
                })

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

            st.rerun()

        except Exception as e:
            st.error(f"AI Error: {str(e)}")


# =========================
# 📊 STATS
# =========================
def get_stats():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ✅ Total jobs created by current user
        cursor.execute(
            "SELECT COUNT(*) FROM jobs WHERE user_id=?",
            (st.session_state.user_id,)
        )
        jobs = cursor.fetchone()[0]

        # ✅ Total APPLIED candidates
        cursor.execute("""
            SELECT COUNT(*)
            FROM candidates c
            JOIN jobs j ON c.job_id = j.id
            WHERE j.user_id=?
            AND c.status='Applied'
        """, (st.session_state.user_id,))

        candidates = cursor.fetchone()[0]

        conn.close()

        return jobs, candidates

    except Exception as e:
        print(e)
        return 0, 0


def get_total_shortlisted():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM candidates
            WHERE status='Shortlisted'
        """)

        val = cursor.fetchone()[0]

        conn.close()

        return val

    except:
        return 0


def get_pending():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM candidates
            WHERE status='Applied'
        """)

        val = cursor.fetchone()[0]

        conn.close()

        return val

    except:
        return 0


# =========================
# 📌 STATUS
# =========================
def compute_status(deadline):
    try:
        if not deadline:
            return "Unknown"

        if isinstance(deadline, str):
            d = datetime.strptime(deadline, "%Y-%m-%d").date()
        else:
            d = deadline

        today = datetime.today().date()

        if d < today:
            return "Closed"

        elif (d - today).days <= 3:
            return "Urgent"

        else:
            return "Active"

    except:
        return "Unknown"


# =========================
# 🎨 UI HELPERS
# =========================
def card(title, value, color):
    return f"""
    <div class="card {color}">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
    </div>
    """


def badge(status):

    color = "green"

    if status == "Closed":
        color = "red"

    elif status == "Urgent":
        color = "orange"

    return f'<span class="badge {color}">{status}</span>'


# =========================
# 🎨 CSS
# =========================
def load_css():
    st.markdown("""
    <style>

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    .block-container {
        padding: 1.5rem 2rem;
        max-width: 100%;
    }

    .stApp {
        background:
            radial-gradient(circle at 20% 20%, rgba(99,102,241,0.15), transparent 40%),
            radial-gradient(circle at 80% 30%, rgba(59,130,246,0.15), transparent 40%),
            linear-gradient(135deg, #f8fafc, #eef2ff);
    }

    .title {
        color: #111827;
        font-weight: 600;
    }

    .welcome {
        color: #6b7280;
    }

    .card {
        padding: 20px;
        border-radius: 14px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }

    .blue {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
    }

    .purple {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
    }

    .green {
        background: linear-gradient(135deg, #10b981, #059669);
    }

    .orange {
        background: linear-gradient(135deg, #f59e0b, #d97706);
    }

    table {
        width: 100%;
        background: rgba(255,255,255,0.9);
        border-radius: 12px;
        overflow: hidden;
    }

    th, td {
        padding: 12px;
        text-align: left;
    }

    .badge {
        padding: 5px 10px;
        border-radius: 10px;
        color: white;
        font-size: 12px;
    }

    .badge.green {
        background: #10b981;
    }

    .badge.red {
        background: #ef4444;
    }

    .badge.orange {
        background: #f59e0b;
    }

    </style>
    """, unsafe_allow_html=True)