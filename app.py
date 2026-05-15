import streamlit as st
from database.db import init_db

# 🔐 AUTH (keep these — lightweight)
from auth import login, register, forgot_password

from nav import navigate, go_back

# =========================
# 🔧 INIT DB
# =========================
init_db()

# =========================
# 🧠 SESSION STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "start"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = None

if "job_loaded" not in st.session_state:
    st.session_state.job_loaded = False

if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# 🌐 JOB LINK HANDLER (FIXED)
# =========================
query_params = st.query_params

if "job_id" in query_params and not st.session_state.job_loaded:
    job_id = query_params.get("job_id")

    # ✅ handle list safely
    if isinstance(job_id, list):
        job_id = job_id[0]

    try:
        job_id = str(job_id).strip()

        st.session_state.selected_job_id = int(job_id)
        st.session_state.page = "public_apply"
        st.session_state.job_loaded = True

        # ✅ prevent infinite reload loop
        st.query_params.clear()

        st.rerun()  # ✅ IMPORTANT (forces navigation instantly)

    except:
        st.error("Invalid job link")

# =========================
# 🚀 START PAGE (LAZY LOAD)
# =========================
if st.session_state.page == "start":
    from pages import start_page
    start_page.show()
    st.stop()

# =========================
# 🔐 AUTH ROUTES
# =========================
if not st.session_state.logged_in:

    if st.session_state.page == "login":
        login.show()

    elif st.session_state.page == "register":
        register.show()

    elif st.session_state.page == "forgot":
        forgot_password.show()

    elif st.session_state.page == "public_apply":
        from pages import public_apply
        public_apply.show()

    else:
        st.session_state.page = "login"
        st.rerun()

# =========================
# 🚀 MAIN APP ROUTES
# =========================
else:

    if st.session_state.page == "dashboard":
        from pages import dashboard
        dashboard.show()

    elif st.session_state.page == "create_job":
        from pages import create_job
        create_job.show()

    elif st.session_state.page == "view_jobs":
        from pages import view_jobs
        view_jobs.show()

    elif st.session_state.page == "job_details":
        from pages import job_details
        job_details.show()

    elif st.session_state.page == "upload_resume":
        from pages import upload_resume
        upload_resume.show()

    elif st.session_state.page == "candidates":
        from pages import candidates
        candidates.show()

    elif st.session_state.page == "shortlisted":
        from pages import shortlisted
        shortlisted.show()

    elif st.session_state.page == "public_apply":
        from pages import public_apply
        public_apply.show()

    elif st.session_state.page == "recommendation":
        from pages import recommendation
        recommendation.show()

    else:
        st.session_state.page = "dashboard"
        st.rerun()