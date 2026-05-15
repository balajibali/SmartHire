import streamlit as st
from database.db import get_connection, add_global_candidate
from datetime import date
import re

from utils.file_handler import extract_text_from_pdf
from utils.validation import (
    is_valid_email,
    is_valid_phone,
    is_not_empty
)


# =========================
# 🚀 MAIN PAGE
# =========================
def show():

    load_css()

    st.title("📄 Apply for Job")

    # =========================
    # 🔗 GET JOB ID (FIXED)
    # =========================
    job_id = st.session_state.get("selected_job_id")

    # ✅ fallback if session lost (IMPORTANT)
    if not job_id:
        query_params = st.query_params
        job_id = query_params.get("job_id")

        if isinstance(job_id, list):
            job_id = job_id[0]

        try:
            job_id = int(job_id)
            st.session_state.selected_job_id = job_id
        except:
            st.error("Invalid job link")
            return

    # =========================
    # 🗄️ DB
    # =========================
    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # 🔍 FETCH JOB
    # =========================
    try:

        cursor.execute(
            """
            SELECT title, description, deadline
            FROM jobs
            WHERE id = ?
            """,
            (int(job_id),)
        )

        job = cursor.fetchone()

    except Exception as e:
        st.error(f"Database error: {e}")
        conn.close()
        return

    # =========================
    # ❌ JOB NOT FOUND
    # =========================
    if not job:
        st.error("Job not found")
        conn.close()
        return

    title, description, deadline = job

    # =========================
    # ⏳ DEADLINE CHECK
    # =========================
    try:

        if deadline:

            if isinstance(deadline, str):
                deadline = date.fromisoformat(deadline)

            if date.today() > deadline:
                st.error("❌ This job is expired. Applications are closed.")
                conn.close()
                return

    except:
        pass

    # =========================
    # 🧾 JOB INFO
    # =========================
    st.subheader(title)

    st.caption(f"Job ID: {job_id}")

    st.write(description)

    if deadline:
        st.info(f"⏳ Apply before: {deadline}")

    st.divider()

    # =========================
    # 📝 APPLICATION FORM
    # =========================
    with st.form("apply_form", clear_on_submit=True):

        name = st.text_input("Full Name", key="apply_name")
        phone = st.text_input("Phone Number", key="apply_phone")
        email = st.text_input("Email", key="apply_email")

        resume = st.file_uploader(
            "Upload Resume (PDF)",
            type=["pdf"],
            key="apply_resume"
        )

        submit = st.form_submit_button("🚀 Apply")

    # =========================
    # 🚀 SUBMIT LOGIC
    # =========================
    if submit:

        name = (name or "").strip()
        email = (email or "").strip().lower()
        phone = (phone or "").strip()

        # =========================
        # 🔍 VALIDATION
        # =========================
        if not is_not_empty(name):
            st.warning("Name is required")
            conn.close()
            return

        if not is_valid_email(email):
            st.warning("Invalid email")
            conn.close()
            return

        if phone and not is_valid_phone(phone):
            st.warning("Invalid phone number")
            conn.close()
            return

        if not resume:
            st.warning("Please upload resume")
            conn.close()
            return

        # =========================
        # 🚫 DUPLICATE CHECK
        # =========================
        cursor.execute(
            """
            SELECT id
            FROM candidates
            WHERE job_id = ?
            AND LOWER(email) = ?
            """,
            (int(job_id), email)
        )

        if cursor.fetchone():
            st.warning("⚠️ You already applied for this job")
            conn.close()
            return

        # =========================
        # 📄 EXTRACT RESUME TEXT
        # =========================
        try:
            resume_text = extract_text_from_pdf(resume)
        except:
            resume_text = ""

        # =========================
        # 💾 RESUME BYTES
        # =========================
        try:
            resume_bytes = resume.getvalue()
        except:
            resume_bytes = None

        # =========================
        # 💾 INSERT CANDIDATE (FIXED STATUS)
        # =========================
        try:

            cursor.execute(
                """
                INSERT INTO candidates
                (
                    job_id,
                    name,
                    email,
                    resume_text,
                    resume_file,
                    status
                )
                VALUES (?, ?, ?, ?, ?, 'applied')
                """,
                (
                    int(job_id),
                    name,
                    email,
                    resume_text,
                    resume_bytes
                )
            )

            conn.commit()

        except Exception as e:
            st.error(f"Failed to submit application: {e}")
            conn.close()
            return

        finally:
            conn.close()

        # =========================
        # 🌍 GLOBAL TALENT POOL
        # =========================
        try:
            add_global_candidate(
                name=name,
                email=email,
                resume_text=resume_text
            )
        except:
            pass

        # =========================
        # ✅ SUCCESS
        # =========================
        st.success("✅ Application submitted successfully")
        st.info("You can close this page now.")
        st.balloons()


# =========================
# 🎨 LOAD CSS
# =========================
def load_css():

    try:
        with open("assets/styles.css", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )
    except:
        pass