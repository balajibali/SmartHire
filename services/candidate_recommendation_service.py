from database.db import get_connection
from services.matching_service import match_candidates
from services.ollama_service import generate_ai_response


def recommend_candidates(job_id, job_desc, min_match=10, status_filter="All", top_n=10, use_ai=True):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.id, c.name, c.email, c.resume_text, c.score, c.status, j.title
        FROM candidates c
        LEFT JOIN jobs j ON c.job_id = j.id
    """)

    data = cursor.fetchall()
    conn.close()

    results = []

    for c in data:
        cid, name, email, resume, score, status, applied_job = c

        if status_filter != "All" and (status or "").lower() != status_filter.lower():
            continue

        # =========================
        # 🔥 SKILL MATCHING
        # =========================
        match_percent, matched_skills = match_candidates(resume, job_id)

        if match_percent < min_match:
            continue

        # =========================
        # 🤖 AI SCORING
        # =========================
        if use_ai:
            prompt = f"""
            You are a recruiter.

            Job Description:
            {job_desc}

            Candidate Resume:
            {resume}

            Return:
            score|reason
            """

            try:
                ai = generate_ai_response(prompt)
                ai_score, ai_reason = ai.split("|", 1)
                ai_score = int(ai_score.strip())
                ai_reason = ai_reason.strip()
            except:
                ai_score = match_percent
                ai_reason = "Skill match based scoring"
        else:
            ai_score = match_percent
            ai_reason = "AI disabled"

        # =========================
        # 🎯 FINAL SCORE
        # =========================
        final_score = int((0.6 * ai_score) + (0.4 * match_percent))

        results.append({
            "Name": name,
            "Email": email,
            "Applied Job": applied_job,
            "Match %": match_percent,
            "AI Score": ai_score,
            "Final Score": final_score,
            "Skills": ", ".join(matched_skills[:5]),
            "Reason": ai_reason
        })

    results = sorted(results, key=lambda x: x["Final Score"], reverse=True)

    return results[:top_n]