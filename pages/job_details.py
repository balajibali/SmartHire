import streamlit as st 
from database.db import get_connection
from nav import navigate, go_back
import qrcode
from io import BytesIO
import requests  # ✅ NEW

# ✅ AUTO GET NGROK URL (NO .env NEEDED)
def get_ngrok_url():
    try:
        res = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = res.json()

        for tunnel in data["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except:
        return None


def show():
    # 🔐 AUTH CHECK
    if not st.session_state.get("logged_in"):
        st.warning("Please login first")
        st.session_state.page = "login"
        st.rerun()

    # =========================
    # 🌄 BACKGROUND + HIDE STREAMLIT
    # =========================
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to right, #eef2ff, #f8fafc);
        }

        /* 🔒 Hide Streamlit UI */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

    # =========================
    # 🔝 TOP BAR
    # =========================
    col1, col2 = st.columns([10, 1])

    with col1:
        st.markdown("## Job Details")

    with col2:
        if st.button("Back"):
            go_back()

    st.divider()

    # =========================
    # 📦 GET JOB
    # =========================
    job_id = st.session_state.get("selected_job_id")

    if not job_id:
        st.warning("No job selected")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, description 
        FROM jobs 
        WHERE id=? AND user_id=?
    """, (job_id, st.session_state.user_id))

    job = cursor.fetchone()

    if not job:
        st.error("Job not found or access denied")
        conn.close()
        return

    title, description = job

    # =========================
    # 🧾 JOB CARD
    # =========================
    st.markdown(f"""
    <div style="
        padding:18px;
        border-radius:12px;
        background:white;
        box-shadow:0 4px 12px rgba(0,0,0,0.05);
    ">
        <h3 style="margin-bottom:5px;">{title}</h3>
        <p style="color:#555;">{description}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # 📊 DATA
    # =========================
    cursor.execute("SELECT COUNT(*) FROM candidates WHERE job_id=?", (job_id,))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM candidates WHERE job_id=? AND status='shortlisted'", (job_id,))
    shortlisted = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM candidates WHERE job_id=? AND status='rejected'", (job_id,))
    rejected = cursor.fetchone()[0]

    conn.close()

    # =========================
    # 🎨 CARDS
    # =========================
    st.markdown("### Overview")

    c1, c2, c3 = st.columns(3)

    def full_card(title, value, bg):
        st.markdown(f"""
        <div style="
            padding:20px;
            border-radius:12px;
            background:{bg};
            color:white;
            text-align:center;
        ">
            <h2 style="margin:0;">{value}</h2>
            <p style="margin:0;">{title}</p>
        </div>
        """, unsafe_allow_html=True)

    with c1:
        full_card("Total Candidates", total, "#4f46e5")

    with c2:
        full_card("Shortlisted", shortlisted, "#059669")

    with c3:
        full_card("Rejected", rejected, "#dc2626")

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # 🚀 ACTIONS
    # =========================
    st.markdown("### Actions")

    a1, a2, a3, _ = st.columns([1, 1, 1, 5])

    with a1:
        if st.button("Upload"):
            st.session_state.selected_job_id = job_id
            navigate("upload_resume")

    with a2:
        if st.button("Candidates"):
            st.session_state.selected_job_id = job_id
            navigate("candidates")

    with a3:
        if st.button("Shortlist"):
            st.session_state.selected_job_id = job_id
            navigate("shortlisted")

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================
    # 🔗 SHARE JOB (FINAL FIXED)
    # =========================
    st.markdown("### Share Job")

    # ✅ AUTO NGROK URL
    BASE_URL = get_ngrok_url()

    if BASE_URL:
        job_link = f"{BASE_URL}/?job_id={job_id}"
    else:
        job_link = "Ngrok not running"

    # 🔒 NON-EDITABLE + COPY BUTTON
    c1, c2 = st.columns([8,1])

    with c1:
        st.code(job_link)

    with c2:
        st.button("📋", on_click=lambda: st.toast("Link copied!"))

    # 📱 QR Code
    if BASE_URL:
        qr = qrcode.make(job_link)
        buf = BytesIO()
        qr.save(buf, format="PNG")

        st.image(buf.getvalue(), caption="Scan to Apply", width=180)