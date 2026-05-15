import streamlit as st
from database.db import get_connection

from utils.file_handler import process_uploaded_files
from utils.validation import is_valid_email
from services.matching_service import match_candidates

import re

# ✅ ONLY NAVIGATION ADD
from nav import navigate, go_back


# =========================
# ⚙️ PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Upload Resumes",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def show():
    load_css()

    # =========================
    # 🔐 AUTH CHECK
    # =========================
    if not st.session_state.get("logged_in"):
        st.warning("Please login first")
        st.session_state.page = "login"
        st.rerun()

    # =========================
    # 🔙 BACK (NAV FIXED)
    # =========================
    col1, col2 = st.columns([10, 1])

    with col1:
        st.markdown("<h2 class='title'>Upload Resumes</h2>", unsafe_allow_html=True)

    with col2:
        if st.button("Back"):
            go_back()   # ✅ FIXED NAVIGATION

    st.markdown("<p class='subtitle'>Upload candidate resumes for processing</p>", unsafe_allow_html=True)

    st.divider()

    # =========================
    # 📦 DB
    # =========================
    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # 🔹 SELECT JOB
    # =========================
    cursor.execute(
        "SELECT id, title FROM jobs WHERE user_id=?",
        (st.session_state.user_id,)
    )
    jobs = cursor.fetchall()

    if not jobs:
        st.info("No jobs found. Create a job first.")
        conn.close()
        return

    job_map = {title: job_id for job_id, title in jobs}

    selected_title = st.selectbox(
        "Select Job Role",
        list(job_map.keys()),
        key="upload_job"
    )

    job_id = job_map[selected_title]

    # =========================
    # 📂 UPLOAD CARD
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    files = st.file_uploader(
        "Upload Resumes (PDF only)",
        type=["pdf"],
        accept_multiple_files=True,
        key="resume_upload"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # 🚀 PROCESS
    # =========================
    if st.button("Process Resumes"):

        if not files:
            st.warning("Please upload at least one resume")
            return

        progress = st.progress(0)
        results = process_uploaded_files(files)

        success_count = 0

        for i, file_data in enumerate(results):

            text = file_data.get("text", "")
            file_bytes = file_data.get("file_bytes", None)
            filename = file_data.get("filename", "Unknown")

            if not text:
                continue

            # EMAIL
            email = None
            match = re.search(
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                text
            )

            if match:
                email = match.group(0).lower()

            if not is_valid_email(email):
                email = None

            # DUPLICATE CHECK
            if email:
                cursor.execute("""
                    SELECT id FROM candidates
                    WHERE job_id=? AND email=?
                """, (job_id, email))

                if cursor.fetchone():
                    continue

            # SCORE
            score = match_candidates(text, job_id)

            # SAVE
            cursor.execute("""
                INSERT INTO candidates 
                (job_id, name, email, resume_text, resume_file, score, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Applied')
            """, (
                job_id,
                filename,
                email,
                text,
                file_bytes,
                score
            ))

            # GLOBAL POOL
            if email:
                cursor.execute(
                    "SELECT id FROM global_candidates WHERE email=?",
                    (email,)
                )
                exists = cursor.fetchone()

                if not exists:
                    cursor.execute("""
                        INSERT INTO global_candidates
                        (name, email, resume_text)
                        VALUES (?, ?, ?)
                    """, (
                        filename,
                        email,
                        text
                    ))

            success_count += 1
            progress.progress((i + 1) / len(results))

        conn.commit()
        conn.close()

        st.success(f"✅ {success_count} resumes processed successfully")

    st.divider()

    # =========================
    # 🚀 QUICK NAV
    # =========================
    c1, c2 = st.columns(2)

    with c1:
        if st.button("View Candidates"):
            navigate("candidates")   # ✅ FIXED NAV

    with c2:
        if st.button("Dashboard"):
            navigate("dashboard")    # ✅ FIXED NAV


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
        max-width: 100%;
        padding: 2rem 3rem;
    }

    .stApp {
        background:
            radial-gradient(circle at 20% 20%, rgba(99,102,241,0.15), transparent 40%),
            radial-gradient(circle at 80% 30%, rgba(59,130,246,0.15), transparent 40%),
            linear-gradient(135deg, #f8fafc, #eef2ff);
    }

    .title {
        font-weight: 600;
        color: #111827;
        margin-bottom: 0;
    }

    .subtitle {
        color: #6b7280;
        margin-top: 0;
    }

    .card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }

    button {
        border-radius: 8px !important;
    }

    </style>
    """, unsafe_allow_html=True)