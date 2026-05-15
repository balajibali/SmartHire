import streamlit as st
from database.db import get_connection
import re
import zipfile
import io

# ✅ NAVIGATION UPGRADE (ONLY ADDITION)
from nav import go_back, navigate


# ---------- HELPERS ----------
def extract_name(text, fallback):
    if not text:
        return fallback.replace(".pdf", "")
    for line in text.strip().split("\n")[:5]:
        if 2 <= len(line.split()) <= 4 and not any(c.isdigit() for c in line):
            return line.strip()
    return fallback.replace(".pdf", "")


def calculate_match_score(job_desc, resume_text):
    job_desc = (job_desc or "").lower()
    resume_text = (resume_text or "").lower()
    words = set(re.findall(r'\b\w+\b', job_desc))
    if not words:
        return 0
    match = sum(1 for w in words if w in resume_text)
    return int((match / len(words)) * 100)


def update_status(cid, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE candidates SET status=? WHERE id=?", (status, cid))
    conn.commit()
    conn.close()


def create_zip(data):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as z:
        for d in data:
            z.writestr(f"{d['name']}.txt", d["resume"])
    buffer.seek(0)
    return buffer


# ---------- CSS (LIGHT MODE + MODERN UI) ----------
def load_css():
    st.markdown("""
    <style>

    #MainMenu, header, footer {visibility: hidden;}

    .block-container {
        padding: 1rem 2rem;
        max-width: 100%;
    }

    /* 🌈 LIGHT BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #f8fafc, #eef2ff, #ffffff);
    }

    /* TABLE FIX */
    div[data-testid="column"] {
        padding: 0px !important;
        margin: 0px !important;
    }

    /* HEADER */
    h2 {
        color: #111827;
        font-weight: 600;
    }

    /* TABLE HEADER */
    .table-header {
        border:1px solid #e5e7eb;
        padding:10px;
        font-size:13px;
        font-weight:600;
        background:#f3f4f6;
        color:#111827;
    }

    /* TABLE CELL */
    .table-cell {
        border:1px solid #e5e7eb;
        padding:10px;
        font-size:13px;
        background:white;
    }

    /* DIVIDER */
    .divider {
        border-top:1px solid #e5e7eb;
        margin:10px 0;
    }

    /* BUTTON */
    button {
        padding:5px 10px !important;
        font-size:12px !important;
        border-radius:6px !important;
    }

    /* LIST CARD */
    .card {
        background:white;
        padding:12px;
        border-radius:10px;
        border:1px solid #e5e7eb;
        box-shadow:0 2px 10px rgba(0,0,0,0.04);
    }

    </style>
    """, unsafe_allow_html=True)


# ---------- TABLE ----------
def render_table(data, title, show_actions=False, show_download=True, key="tbl"):

    if not data:
        st.info("No data available")
        return

    st.markdown(f"### {title}")

    page_key = f"{key}_page"
    st.session_state.setdefault(page_key, 1)

    PER_PAGE = 5
    total_pages = (len(data)-1)//PER_PAGE + 1
    page = st.session_state[page_key]

    start = (page-1)*PER_PAGE
    rows = data[start:start+PER_PAGE]

    col_sizes = [0.6, 2, 3, 1]

    if show_download:
        col_sizes.append(1.5)

    if show_actions:
        col_sizes.append(2)

    col_sizes.append(1.2)

    headers = ["#", "Name", "Email", "Score"]

    if show_download:
        headers.append("Download")

    if show_actions:
        headers.append("Action")

    headers.append("Status")

    cols = st.columns(col_sizes)
    for c, h in zip(cols, headers):
        c.markdown(f"<div class='table-header'>{h}</div>", unsafe_allow_html=True)

    for i, d in enumerate(rows, start=start+1):
        cols = st.columns(col_sizes)
        idx = 0

        cols[idx].markdown(f"<div class='table-cell'>{i}</div>", unsafe_allow_html=True); idx+=1
        cols[idx].markdown(f"<div class='table-cell'>{d['name']}</div>", unsafe_allow_html=True); idx+=1
        cols[idx].markdown(f"<div class='table-cell'>{d['email']}</div>", unsafe_allow_html=True); idx+=1
        cols[idx].markdown(f"<div class='table-cell'>{d['score']}</div>", unsafe_allow_html=True); idx+=1

        if show_download:
            with cols[idx]:
                st.download_button(
                    "DL",
                    d["resume"],
                    file_name=f"{d['name']}.txt",
                    key=f"{key}_d_{d['id']}"
                )
            idx+=1

        if show_actions:
            with cols[idx]:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("✔", key=f"{key}_s_{d['id']}"):
                        update_status(d["id"], "Shortlisted")
                        st.rerun()
                with b2:
                    if st.button("✖", key=f"{key}_r_{d['id']}"):
                        update_status(d["id"], "Rejected")
                        st.rerun()
            idx+=1

        cols[idx].markdown(f"<div class='table-cell'>{d['status']}</div>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    p1, p2, p3 = st.columns([1,2,1])

    with p1:
        if st.button("Prev", key=f"{key}_prev") and page > 1:
            st.session_state[page_key] -= 1
            st.rerun()

    with p2:
        st.markdown(f"<div style='text-align:center;'>Page {page}/{total_pages}</div>", unsafe_allow_html=True)

    with p3:
        if st.button("Next", key=f"{key}_next") and page < total_pages:
            st.session_state[page_key] += 1
            st.rerun()

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.download_button("Download ZIP", create_zip(data), f"{title}.zip")


# ---------- MAIN ----------
def show():

    load_css()

    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    c1, c2 = st.columns([10,1])

    c1.markdown("## Candidates")

    with c2:
        if st.button("Back"):
            go_back()

    st.divider()

    job_id = st.session_state.get("selected_job_id")

    if not job_id:
        st.warning("No job selected")
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT title,description FROM jobs WHERE id=?", (job_id,))
    job = cur.fetchone()

    if not job:
        st.error("Job not found")
        return

    title, desc = job

    st.markdown(f"### {title}")

    cur.execute("SELECT id,name,email,resume_text,status FROM candidates WHERE job_id=?", (job_id,))
    rows = cur.fetchall()
    conn.close()

    data = []
    for r in rows:
        cid, name, email, resume, status = r
        data.append({
            "id": cid,
            "name": extract_name(resume, name),
            "email": email or "-",
            "score": calculate_match_score(desc, resume),
            "resume": resume or "",
            "status": status or "Applied"
        })

    f1, f2, f3 = st.columns(3)
    search = f1.text_input("Search")
    status_filter = f2.selectbox("Status", ["All","Applied","Shortlisted","Rejected"])
    sort = f3.selectbox("Sort", ["High to Low","Low to High"])

    if search:
        data = [d for d in data if search.lower() in d["name"].lower() or search.lower() in d["email"].lower()]

    if status_filter != "All":
        data = [d for d in data if d["status"] == status_filter]

    data = sorted(data, key=lambda x: x["score"], reverse=(sort=="High to Low"))

    render_table(data, "All Candidates", True, True, "all")

    st.divider()

    st.session_state.setdefault("show_list", "none")

    t1, t2 = st.columns(2)

    with t1:
        if st.button("Shortlisted List"):
            st.session_state.show_list = "none" if st.session_state.show_list == "short" else "short"

    with t2:
        if st.button("Rejected List"):
            st.session_state.show_list = "none" if st.session_state.show_list == "reject" else "reject"

    if st.session_state.show_list == "short":
        st.divider()
        render_table([d for d in data if d["status"]=="Shortlisted"], "Shortlisted", False, False, "short")

    elif st.session_state.show_list == "reject":
        st.divider()
        render_table([d for d in data if d["status"]=="Rejected"], "Rejected", False, False, "rej")