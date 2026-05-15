import streamlit as st
from database.db import get_connection
from datetime import date
from nav import navigate, go_back   # ✅ ONLY ADD (NAVIGATION UPGRADE)

st.set_page_config(layout="wide")


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
        st.markdown("<h2 class='title'>View Jobs</h2>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Manage your job postings</p>", unsafe_allow_html=True)

    with col2:
        if st.button("Back"):
            go_back()   # ✅ UPGRADED BACK NAVIGATION

    st.markdown("<div class='space'></div>", unsafe_allow_html=True)

    # =========================
    # FILTER
    # =========================
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)

    f1, f2 = st.columns([3, 1])
    search = f1.text_input("Search jobs", key="search_jobs")
    status_filter = f2.selectbox("Status", ["All", "Active", "Closed"], key="status_filter")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='space'></div>", unsafe_allow_html=True)

    # =========================
    # FETCH DATA
    # =========================
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, deadline
        FROM jobs
        WHERE user_id=?
        ORDER BY created_at DESC
    """, (st.session_state.user_id,))
    jobs = cursor.fetchall()

    if not jobs:
        conn.close()
        st.info("No jobs found")
        return

    # =========================
    # TABLE HEADER
    # =========================
    st.markdown("<div class='table-box'>", unsafe_allow_html=True)

    h1, h2, h3, h4, h5, h6 = st.columns([3, 1, 1, 2, 1, 2])

    h1.markdown("<div class='th'>Title</div>", unsafe_allow_html=True)
    h2.markdown("<div class='th'>Applications</div>", unsafe_allow_html=True)
    h3.markdown("<div class='th'>Shortlisted</div>", unsafe_allow_html=True)
    h4.markdown("<div class='th'>Deadline</div>", unsafe_allow_html=True)
    h5.markdown("<div class='th'>Status</div>", unsafe_allow_html=True)
    h6.markdown("<div class='th'>Actions</div>", unsafe_allow_html=True)

    # =========================
    # ROWS
    # =========================
    for job in jobs:
        job_id, title, deadline = job

        if not title or str(title).strip() == "":
            continue

        # STATUS
        status = "Active"
        if deadline:
            try:
                if date.fromisoformat(str(deadline)) < date.today():
                    status = "Closed"
            except:
                pass

        # COUNTS
        cursor.execute("SELECT COUNT(*) FROM candidates WHERE job_id=?", (job_id,))
        total = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM candidates WHERE job_id=? AND status='Shortlisted'",
            (job_id,)
        )
        shortlisted = cursor.fetchone()[0]

        # FILTER
        if search and search.lower() not in title.lower():
            continue

        if status_filter != "All" and status != status_filter:
            continue

        # ROW UI
        c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 1, 2, 1, 2])

        c1.markdown(f"<div class='td title'>{title.strip()}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='td'>{total}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='td'>{shortlisted}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='td'>{deadline if deadline else '-'}</div>", unsafe_allow_html=True)
        c5.markdown(badge(status), unsafe_allow_html=True)

        # ACTIONS
        a1, a2 = c6.columns(2)

        with a1:
            if st.button("Open", key=f"open_{job_id}"):
                st.session_state.selected_job_id = job_id
                navigate("job_details")   # ✅ UPGRADED NAVIGATION

        with a2:
            if st.button("Delete", key=f"delete_{job_id}"):
                delete_job(job_id)
                st.success("Job deleted")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    conn.close()


# =========================
# DELETE
# =========================
def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()


# =========================
# BADGE
# =========================
def badge(status):
    color = "green" if status == "Active" else "red"
    return f'<span class="badge {color}">{status}</span>'


# =========================
# CSS (UNCHANGED)
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
        background: linear-gradient(135deg, #f8fafc, #eef2ff);
    }

    .title { font-weight: 600; }
    .subtitle { color: #6b7280; }

    .space { height: 15px; }

    .section-box {
        background: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }

    .table-box {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
    }

    .th {
        background: #f3f4f6;
        padding: 10px;
        font-weight: 600;
        border-bottom: 1px solid #e5e7eb;
    }

    .td {
        background: #ffffff;
        padding: 10px;
        border-bottom: 1px solid #e5e7eb;
    }

    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        color: white;
        font-size: 12px;
    }

    .badge.green { background: #10b981; }
    .badge.red { background: #ef4444; }

    button {
        width: 100%;
        border-radius: 6px !important;
    }

    </style>
    """, unsafe_allow_html=True)