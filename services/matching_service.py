from utils.skill_extractor import extract_skills
from database.db import get_connection
import re
from difflib import SequenceMatcher


# =========================
# 🔹 NORMALIZE
# =========================
def normalize(skills):
    return set(
        s.strip().lower()
        for s in skills
        if s and len(s.strip()) > 1
    )


# =========================
# 🔹 EXPERIENCE SCORE
# =========================
def extract_years(text):
    try:
        text = (text or "").lower()

        matches = re.findall(r"(\d+)\+?\s*years?", text)

        if matches:
            return max([int(x) for x in matches])

        return 0

    except:
        return 0


# =========================
# 🔹 FUZZY MATCH
# =========================
def fuzzy_match(a, b):
    try:
        return SequenceMatcher(None, a, b).ratio()
    except:
        return 0


# =========================
# 🔹 MATCH CANDIDATES
# =========================
def match_candidates(resume_text, job_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skills, description, experience
        FROM jobs
        WHERE id=?
    """, (job_id,))

    result = cursor.fetchone()

    conn.close()

    if not result:
        return 0, []

    skills_text, job_desc, job_exp = result

    if not skills_text:
        return 0, []

    # =========================
    # 🔹 JOB SKILLS
    # =========================
    job_skills = normalize(skills_text.split(","))

    # =========================
    # 🔹 RESUME SKILLS
    # =========================
    resume_skills = normalize(
        extract_skills(resume_text)
    )

    if not resume_skills:
        return 0, []

    # =========================
    # 🔥 EXACT MATCH
    # =========================
    matched_skills = set()

    for js in job_skills:
        for rs in resume_skills:

            # exact
            if js == rs:
                matched_skills.add(js)
                continue

            # partial
            if js in rs or rs in js:
                matched_skills.add(js)
                continue

            # fuzzy
            ratio = fuzzy_match(js, rs)

            if ratio >= 0.82:
                matched_skills.add(js)

    # =========================
    # 📊 SKILL SCORE
    # =========================
    skill_score = (
        len(matched_skills) / max(len(job_skills), 1)
    ) * 100

    # =========================
    # 📈 EXPERIENCE BONUS
    # =========================
    exp_bonus = 0

    try:
        required_exp = int(job_exp) if job_exp else 0
    except:
        required_exp = 0

    candidate_exp = extract_years(resume_text)

    if required_exp > 0:

        if candidate_exp >= required_exp:
            exp_bonus = 10

        elif candidate_exp >= max(required_exp - 1, 0):
            exp_bonus = 5

    # =========================
    # 🧠 JD KEYWORD BONUS
    # =========================
    keyword_bonus = 0

    try:
        jd_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                (job_desc or "").lower()
            )
        )

        resume_words = set(
            re.findall(
                r"\b[a-zA-Z]{4,}\b",
                (resume_text or "").lower()
            )
        )

        common = jd_words & resume_words

        keyword_bonus = min(len(common) * 0.3, 10)

    except:
        keyword_bonus = 0

    # =========================
    # 🚀 FINAL SCORE
    # =========================
    final_score = skill_score + exp_bonus + keyword_bonus

    final_score = min(round(final_score, 2), 100)

    # =========================
    # 📌 MISSING SKILLS
    # =========================
    missing_skills = list(job_skills - matched_skills)

    # =========================
    # 📊 RETURN
    # =========================
    return final_score, list(matched_skills)