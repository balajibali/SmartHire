import streamlit as st
from database.db import get_connection
from services.email_service import send_interview_email, send_bulk_emails
import zipfile
import io
import pandas as pd
import re
import base64
import nav
from datetime import datetime


# =========================
# 🔧 PAGE CONFIG + UI HIDE
# =========================
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>

/* Hide Streamlit UI */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f7f9fc, #e6ecf5);
    color: #000;
}

/* Typography */
h2 {
    font-weight: 600;
    color: #222;
}

/* Card */
.card {
    background: #ffffff;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}

/* AI Badge */
.ai-badge {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 3px 8px;
    border-radius: 8px;
    font-size: 12px;
    margin-left: 6px;
    font-weight: 500;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    padding: 6px 14px;
    border: none;
    background: #2f80ed;
    color: white;
    font-weight: 500;
}

.stButton > button:hover {
    background: #1c60c4;
}

/* Divider spacing */
hr {
    margin-top: 10px;
    margin-bottom: 10px;
}

.metric-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0 3px 12px rgba(0,0,0,0.05);
}

.metric-title {
    font-size: 13px;
    color: #666;
}

.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #111;
}

.resume-box {
    background: #fff;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #eee;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)


# =========================
# SCORE
# =========================
def calculate_match_score(job_desc, resume_text):
    job_desc = (job_desc or "").lower()
    resume_text = (resume_text or "").lower()

    words = set(re.findall(r'\b\w+\b', job_desc))

    if not words or not resume_text:
        return 0

    match_count = sum(1 for word in words if word in resume_text)

    return int((match_count / max(len(words), 1)) * 100)


# =========================
# 🧠 AI SUMMARY
# =========================
def generate_resume_summary(resume_text):
    try:
        if not resume_text:
            return "No resume text found"

        lines = resume_text.split("\n")
        cleaned = [line.strip() for line in lines if len(line.strip()) > 20]

        summary = " ".join(cleaned[:5])

        if len(summary) > 250:
            summary = summary[:250] + "..."

        return summary

    except:
        return "Unable to summarize"


# =========================
# PDF PREVIEW
# =========================
def show_pdf(file_bytes):
    if not file_bytes:
        st.warning("Resume file not available")
        return

    try:
        if isinstance(file_bytes, memoryview):
            file_bytes = file_bytes.tobytes()

        base64_pdf = base64.b64encode(file_bytes).decode("utf-8")

        pdf_display = f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
        width="100%" height="500px"></iframe>
        """

        st.markdown(pdf_display, unsafe_allow_html=True)

    except:
        st.error("Unable to preview file")


# =========================
# MAIN PAGE
# =========================
def show():

    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    if "selected_candidates" not in st.session_state:
        st.session_state.selected_candidates = set()

    if "email_sent" not in st.session_state:
        st.session_state.email_sent = {}

    if "show_ai_only" not in st.session_state:
        st.session_state.show_ai_only = False

    c1, c2 = st.columns([10, 1])

    c1.markdown("## Shortlisted Candidates")

    with c2:
        if st.button("Back"):
            nav.go_back()

    st.divider()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM jobs
        WHERE user_id=?
    """, (st.session_state.user_id,))

    jobs = cursor.fetchall()

    if not jobs:
        conn.close()
        st.info("No jobs found")
        return

    job_map = {j[1]: j[0] for j in jobs}

    selected_title = st.selectbox("Select Job", list(job_map.keys()))
    job_id = job_map[selected_title]

    cursor.execute("SELECT description FROM jobs WHERE id=?", (job_id,))
    job_desc = cursor.fetchone()[0]

    cursor.execute("""
        SELECT id,name,email,resume_text,resume_file,score,created_at
        FROM candidates
        WHERE job_id=? AND status='Shortlisted'
        ORDER BY score DESC
    """, (job_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.info("No shortlisted candidates")
        return

    ai_ids = set()
    if "recommendations" in st.session_state:
        ai_ids = {r["id"] for r in st.session_state.recommendations}

    colA, colB = st.columns(2)

    with colA:
        if st.button("AI Recommended"):
            st.session_state.show_ai_only = True

    with colB:
        if st.button("Show All"):
            st.session_state.show_ai_only = False

    data = []

    for r in rows:
        cid, name, email, resume, file, score, created_at = r

        if not score:
            score = calculate_match_score(job_desc, resume)

        if st.session_state.show_ai_only and cid not in ai_ids:
            continue

        data.append({
            "id": cid,
            "name": (name or "").replace(".pdf", ""),
            "email": email or "",
            "score": score,
            "resume": resume or "",
            "file": file,
            "summary": generate_resume_summary(resume),
            "created_at": created_at
        })

    if not data:
        st.warning("No AI recommended candidates found")
        return

    df = pd.DataFrame(data)

    m1, m2, m3 = st.columns(3)

    m1.markdown(f'<div class="metric-card"><div class="metric-title">Total Candidates</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-title">Average Match</div><div class="metric-value">{int(df["score"].mean())}%</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-title">AI Recommended</div><div class="metric-value">{len([x for x in data if x["id"] in ai_ids])}</div></div>', unsafe_allow_html=True)

    st.divider()

    st.success(f"{len(df)} candidates")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Send Email to Selected"):
            selected = [r for _, r in df.iterrows() if r["id"] in st.session_state.selected_candidates]
            emails = [{"email": r["email"], "name": r["name"]} for r in selected if r["email"]]

            if emails:
                try:
                    count = send_bulk_emails(emails, selected_title)
                    st.success(f"{count} emails sent")
                except Exception as e:
                    st.error(f"Email failed: {e}")
            else:
                st.warning("No emails selected")

    with col2:
        if st.button("Download ZIP"):
            selected = [r for _, r in df.iterrows() if r["id"] in st.session_state.selected_candidates]

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as z:
                for r in selected:
                    if r["file"]:
                        z.writestr(f"{r['name']}.pdf", r["file"])

            zip_buffer.seek(0)
            st.download_button("Download", zip_buffer, "resumes.zip")

    st.divider()

    headers = ["Select","Name","Email","Score","Preview","Send"]
    cols = st.columns([1,2,3,1,1,1])

    for c, h in zip(cols, headers):
        c.markdown(f"**{h}**")

    for _, row in df.iterrows():
        with st.container():
            cols = st.columns([1,2,3,1,1,1])

            checked = row["id"] in st.session_state.selected_candidates

            # ✅ FIXED CHECKBOX
            new_val = cols[0].checkbox(
                "select",
                value=checked,
                key=f"chk_{row['id']}",
                label_visibility="collapsed"
            )

            if new_val:
                st.session_state.selected_candidates.add(row["id"])
            else:
                st.session_state.selected_candidates.discard(row["id"])

            tag = ""
            if row["id"] in ai_ids:
                tag = '<span class="ai-badge">AI Recommended</span>'

            cols[1].markdown(f"{row['name']}{tag}", unsafe_allow_html=True)
            cols[2].write(row["email"])
            cols[3].write(f"{row['score']}%")

            if cols[4].button("View", key=f"view_{row['id']}"):
                show_pdf(row["file"])

            if cols[5].button("Send", key=f"send_{row['id']}"):
                if row["email"]:
                    try:
                        send_interview_email(row["email"], row["name"], selected_title)
                        st.success(f"Sent to {row['name']}")
                        st.session_state.email_sent[row["id"]] = True
                    except Exception as e:
                        st.error(f"Failed: {e}")
                else:
                    st.warning("No email")

            with st.expander(f"AI Resume Insights - {row['name']}"):
                st.markdown(f"""
                <div class="resume-box">
                <b>AI Summary:</b><br><br>
                {row['summary']}
                <br><br>
                <b>Match Score:</b> {row['score']}%
                <br><br>
                <b>Applied:</b> {row['created_at']}
                </div>
                """, unsafe_allow_html=True)

        st.divider()