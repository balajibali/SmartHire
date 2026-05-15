import streamlit as st
import os
import re
import urllib.parse
import qrcode

from io import BytesIO
from datetime import date

from database.db import get_connection
from utils.skill_extractor import extract_skills
from services.ollama_service import generate_ai_response
from nav import navigate, go_back


# =========================
# ⚙️ PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Create Job",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# 🔹 EXPERIENCE LEVEL MAP
# =========================
EXPERIENCE_LEVELS = {
    "fresher": 0,
    "basic": 1,
    "beginner": 1,
    "junior": 1,
    "intermediate": 2,
    "experienced": 3,
    "senior": 3,
    "expert": 4
}

# =========================
# 🔹 EXTRACT EXPERIENCE
# =========================
def extract_experience(text):

    text = (text or "").lower()

    match = re.findall(r"(\d+)\+?\s*years?", text)

    if match:

        years = int(match[0])

        if years <= 1:
            return 1

        elif years <= 3:
            return 2

        elif years <= 5:
            return 3

        else:
            return 4

    for key, val in EXPERIENCE_LEVELS.items():

        if key in text:
            return val

    return None


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
    # 🧠 SESSION INIT
    # =========================
    if "extracted_skills" not in st.session_state:
        st.session_state.extracted_skills = []

    if "extracted_exp" not in st.session_state:
        st.session_state.extracted_exp = None

    if "job_desc" not in st.session_state:
        st.session_state.job_desc = ""

    # =========================
    # 🔝 HEADER
    # =========================
    col1, col2 = st.columns([6, 1])

    with col1:

        st.markdown(
            "<h2 class='title'>Create Job</h2>",
            unsafe_allow_html=True
        )

        st.markdown(
            "<p class='subtitle'>Post a job with AI assistance</p>",
            unsafe_allow_html=True
        )

    with col2:

        if st.button("⬅ Back", key="back_dashboard"):

            st.session_state.page = "dashboard"

            st.rerun()

    st.divider()

    # =========================
    # 🧾 FORM CARD
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        title = st.text_input(
            "Job Title",
            key="job_title"
        )

    with col2:

        deadline = st.date_input(
            "📅 Application Deadline",
            min_value=date.today(),
            key="deadline"
        )

    # =========================
    # 📄 DESCRIPTION + AI
    # =========================
    col_desc, col_ai = st.columns([5, 1])

    with col_desc:

        description = st.text_area(
            "Job Description",
            height=260,  # ✅ increased height
            placeholder="Paste full job description...",
            key="job_desc"
        )

    with col_ai:

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("✨ AI Generate", key="ai_generate"):

            if not title.strip():

                st.warning("Enter job title first")

            else:

                prompt = f"""
                Generate a professional job description for:

                Role: {title}

                Include:
                - Responsibilities
                - Required skills
                - Experience
                - Nice to have

                Keep it structured and clear.
                """

                try:

                    # ✅ Better UX
                    with st.spinner("🤖 AI is generating job description..."):

                        ai_text = generate_ai_response(prompt)

                    # ✅ Safety
                    if ai_text:

                        st.session_state["job_desc"] = ai_text  # ✅ fixed

                        st.success("AI description generated")

                    else:
                        st.error("Empty AI response")

                except Exception as e:

                    st.error(f"AI generation failed: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # =========================
    # 🧠 SMART EXTRACTION
    # =========================
    st.markdown(
        "<h4>Smart Extraction</h4>",
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([2, 2, 1])

    with c1:

        manual_skills = st.text_input(
            "Skills",
            key="manual_skills"
        )

    with c2:

        manual_experience = st.text_input(
            "Experience",
            key="manual_exp"
        )

    with c3:

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Auto Extract", key="auto_extract"):

            if not description.strip():

                st.warning("Enter job description first")

            else:

                st.session_state.extracted_skills = extract_skills(description)

                st.session_state.extracted_exp = extract_experience(description)

                st.success("Extracted")

    if st.session_state.extracted_skills:

        st.info(
            "🛠 Skills: " +
            ", ".join(st.session_state.extracted_skills)
        )

    if st.session_state.extracted_exp is not None:

        st.info(
            f"📊 Experience Level: {st.session_state.extracted_exp}"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # =========================
    # 🚀 CREATE JOB
    # =========================
    if st.button("Create Job", key="create_job_btn"):

        if not title.strip() or not description.strip():

            st.warning("Title and Description required")

            return

        final_skills = (
            manual_skills
            if manual_skills
            else ", ".join(st.session_state.extracted_skills)
        )

        final_experience = (
            manual_experience
            if manual_experience
            else st.session_state.extracted_exp
        )

        conn = get_connection()

        cursor = conn.cursor()

        # =========================
        # 💾 INSERT JOB
        # =========================
        cursor.execute(
            """
            INSERT INTO jobs
            (
                title,
                description,
                skills,
                experience,
                user_id,
                deadline
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                description.strip(),
                final_skills,
                str(final_experience)
                if final_experience is not None
                else None,
                st.session_state.user_id,
                deadline.isoformat()
                if deadline
                else None
            )
        )

        job_id = cursor.lastrowid

        conn.commit()

        conn.close()

        # =========================
        # 🌐 PUBLIC LINK
        # =========================
        base_url = os.getenv(
            "BASE_URL",
            " https://staining-twisty-disrupt.ngrok-free.dev"
        ).strip()

        apply_link = f"{base_url}/?job_id={job_id}"

        # =========================
        # ✅ SUCCESS
        # =========================
        st.success("✅ Job created successfully")

        st.markdown("### 🌐 Apply Link")

        st.code(apply_link)

        # =========================
        # 📋 COPY LINK
        # =========================
        st.markdown(
            f"""
            <button
                onclick="navigator.clipboard.writeText('{apply_link}')"
                style="
                    background:#2563eb;
                    color:white;
                    border:none;
                    padding:10px 18px;
                    border-radius:8px;
                    cursor:pointer;
                    margin-top:10px;
                "
            >
                📋 Copy Link
            </button>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # =========================
        # 📱 WHATSAPP SHARE
        # =========================
        whatsapp_message = f"""
🚀 Job Opening: {title}

Apply here:
{apply_link}
"""

        whatsapp_url = (
            "https://wa.me/?text=" +
            urllib.parse.quote(whatsapp_message)
        )

        st.link_button(
            "📱 Share on WhatsApp",
            whatsapp_url
        )

        # =========================
        # 📷 QR CODE
        # =========================
        try:

            qr = qrcode.make(apply_link)

            buffer = BytesIO()

            qr.save(buffer, format="PNG")

            st.markdown("### 📷 Scan QR Code")

            st.image(
                buffer.getvalue(),
                width=220
            )

        except Exception as e:

            st.warning(f"QR generation failed: {e}")


# =========================
# 🎨 CSS
# =========================
def load_css():

    st.markdown("""
    <style>

    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 100%;
        padding: 2rem 3rem;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(99,102,241,0.15),
                transparent 40%
            ),
            radial-gradient(
                circle at 80% 30%,
                rgba(59,130,246,0.15),
                transparent 40%
            ),
            linear-gradient(
                135deg,
                #f8fafc,
                #eef2ff
            );
    }

    .title {
        color: #111827;
        font-weight: 600;
    }

    .subtitle {
        color: #6b7280;
    }

    .card {
        background: rgba(255,255,255,0.9);
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }

    .stButton>button {
        border-radius: 8px;
        background:
            linear-gradient(
                135deg,
                #3b82f6,
                #2563eb
            );
        color: white;
        border: none;
        padding: 8px 16px;
    }

    .stButton>button:hover {
        transform: scale(1.02);
    }

    </style>
    """, unsafe_allow_html=True)