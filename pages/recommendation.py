import streamlit as st
from database.db import get_connection, update_candidate_status
from nav import go_back


def load_css():
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa, #e4ecf7);
        color: #000;
    }

    .card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .top {
        color: #1e7e34;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)



def compute_fast(job_id, job_desc, min_match, top_n):
    from services.matching_service import match_candidates
    from services.faiss_service import search_similar

    conn = get_connection()
    cursor = conn.cursor()

    top_k = min(25, top_n * 3)

    raw_ids = search_similar(job_desc, top_k=top_k)

    ids = []
    for i in raw_ids:
        if isinstance(i, dict):
            if "id" in i:
                ids.append(i["id"])
            elif "candidate_id" in i:
                ids.append(i["candidate_id"])
        elif isinstance(i, (list, tuple)):
            ids.append(i[0])
        else:
            ids.append(i)

    if not ids:
        return []

    placeholders = ",".join(["?"] * len(ids))

    cursor.execute(f"""
        SELECT c.id, c.name, c.email, c.resume_text, c.status, c.job_id, j.title
        FROM candidates c
        LEFT JOIN jobs j ON c.job_id = j.id
        WHERE c.id IN ({placeholders})
    """, ids)

    data = cursor.fetchall()
    conn.close()

    results = []

    for c in data:
        cid, name, email, resume, status, candidate_job_id, applied_job = c

        if not resume:
            continue

        match_percent, _ = match_candidates(resume, job_id)

        if match_percent < min_match:
            continue

        results.append({
            "id": cid,
            "Name": name,
            "Email": email,
            "Applied Job": applied_job,
            "Match": match_percent,
            "Final": match_percent,
            "Reason": "Match based",
            "Status": status or "Applied",
            "Source": "Applied" if candidate_job_id == job_id else "Recommended"
        })

    return sorted(results, key=lambda x: x["Final"], reverse=True)[:top_n]


def show():
    load_css()

    if not st.session_state.get("logged_in"):
        st.session_state.page = "login"
        st.rerun()

    if "recommendations" not in st.session_state:
        st.session_state.recommendations = []

    if "last_job_id" not in st.session_state:
        st.session_state.last_job_id = None

    col1, col2 = st.columns([8, 1])

    with col1:
        st.markdown("## Candidate Recommendations")

    with col2:
        if st.button("Back"):
            go_back()

    st.divider()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, description FROM jobs WHERE user_id=?",
        (st.session_state.user_id,)
    )
    jobs = cursor.fetchall()

    if not jobs:
        st.info("No jobs available")
        conn.close()
        return

    job_map = {j[1]: j for j in jobs}
    selected = st.selectbox("Select Job Role", list(job_map.keys()))

    job_id, job_title, job_desc = job_map[selected]

    # Reset when job changes
    if st.session_state.last_job_id != job_id:
        st.session_state.recommendations = []
        st.session_state.last_job_id = job_id

    st.divider()

    col1, col2 = st.columns(2)
    min_match = col1.slider("Min Match %", 0, 100, 10)
    top_n = col2.number_input("Top Results", 1, 50, 10)

    filter_type = st.selectbox(
        "Filter",
        ["All", "Applied", "Shortlisted", "Rejected"]
    )

    if st.button("Generate Recommendations"):

        st.session_state.recommendations = []

        with st.spinner("Generating recommendations..."):

            results = compute_fast(job_id, job_desc, min_match, top_n)

            st.session_state.recommendations = sorted(
                results, key=lambda x: x["Final"], reverse=True
            )

    conn.close()

    if st.session_state.recommendations:

        filtered = []

        for r in st.session_state.recommendations:
            if filter_type == "All" or r["Status"].lower() == filter_type.lower():
                filtered.append(r)

        for i, r in enumerate(filtered):

            tag = ""
            if i == 0:
                tag = '<span class="top">Best Match</span>'

            st.markdown(f"""
            <div class="card">
                <h4>{r['Name']} {tag}</h4>
                <p><b>Score:</b> {r['Final']}</p>
                <p>{r['Applied Job']}</p>
                <p>Match: {r['Match']}%</p>
                <p>Status: {r['Status']}</p>
                <p><b>Type:</b> {r['Source']}</p>
                <p>{r['Reason']}</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            if col1.button("Shortlist", key=f"s_{r['id']}"):
                update_candidate_status(r["id"], "shortlisted")
                st.success(f"{r['Name']} shortlisted")