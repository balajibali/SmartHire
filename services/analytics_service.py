
import pandas as pd
from database.db import get_connection


# =========================
# KPI DATA
# =========================
def get_kpi_data():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM jobs")
    active_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='shortlisted'
    """)
    shortlisted = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='interview'
    """)
    interviews = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='hired'
    """)
    hired = cursor.fetchone()[0]

    conn.close()

    return {
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "total_candidates": total_candidates,
        "shortlisted": shortlisted,
        "interviews": interviews,
        "hired": hired
    }


# =========================
# APPLICATIONS PER JOB
# =========================
def applications_per_job():

    conn = get_connection()

    try:

        query = """
            SELECT
                j.title,
                COUNT(c.id) AS total
            FROM jobs j
            LEFT JOIN candidates c
            ON j.id = c.job_id
            GROUP BY j.id
            ORDER BY total DESC
        """

        df = pd.read_sql(query, conn)

    except:

        df = pd.DataFrame(
            columns=["title", "total"]
        )

    conn.close()

    return df


# =========================
# STATUS DISTRIBUTION
# =========================
def candidate_status_distribution():

    conn = get_connection()

    try:

        query = """
            SELECT
                status,
                COUNT(*) AS total
            FROM candidates
            GROUP BY status
        """

        df = pd.read_sql(query, conn)

        if df.empty:

            df = pd.DataFrame({
                "status": ["Applied"],
                "total": [0]
            })

    except:

        df = pd.DataFrame({
            "status": ["Applied"],
            "total": [0]
        })

    conn.close()

    return df


# =========================
# RECENT ACTIVITY
# =========================
def recent_activity():

    conn = get_connection()

    try:

        query = """
            SELECT
                name,
                email,
                score,
                status,
                created_at
            FROM candidates
            ORDER BY id DESC
            LIMIT 10
        """

        df = pd.read_sql(query, conn)

    except:

        df = pd.DataFrame()

    conn.close()

    return df


# =========================
# TOP SKILLS
# =========================
def top_skills():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT skills
            FROM jobs
            WHERE skills IS NOT NULL
        """)

        rows = cursor.fetchall()

    except:

        rows = []

    conn.close()

    skills = {}

    for row in rows:

        if not row[0]:
            continue

        for skill in str(row[0]).split(","):

            skill = skill.strip()

            if not skill:
                continue

            skills[skill] = skills.get(skill, 0) + 1

    if not skills:

        return pd.DataFrame({
            "skill": [],
            "count": []
        })

    df = pd.DataFrame(
        list(skills.items()),
        columns=["skill", "count"]
    )

    return df.sort_values(
        "count",
        ascending=False
    ).head(10)


# =========================
# RECRUITMENT FUNNEL
# =========================
def funnel_data():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM candidates"
    )
    applied = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='shortlisted'
    """)
    shortlisted = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='interview'
    """)
    interview = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='hired'
    """)
    hired = cursor.fetchone()[0]

    conn.close()

    return {
        "Applied": applied,
        "Shortlisted": shortlisted,
        "Interview": interview,
        "Hired": hired
    }


# =========================
# AI INSIGHT CONTEXT
# =========================
def get_ai_insight_context():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM candidates"
    )
    total_candidates = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='shortlisted'
    """)
    shortlisted = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='interview'
    """)
    interviews = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM candidates
        WHERE LOWER(status)='hired'
    """)
    hired = cursor.fetchone()[0]

    cursor.execute("""
        SELECT title
        FROM jobs
        ORDER BY id DESC
        LIMIT 5
    """)

    jobs = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "total_candidates": total_candidates,
        "shortlisted": shortlisted,
        "interviews": interviews,
        "hired": hired,
        "jobs": jobs
    }


# =========================
# CHAT CONTEXT
# =========================
def get_chat_context():

    conn = get_connection()
    cursor = conn.cursor()

    context = ""

    try:

        candidate_columns = [
            row[1]
            for row in cursor.execute(
                "PRAGMA table_info(candidates)"
            ).fetchall()
        ]

        cursor.execute(
            "SELECT * FROM candidates LIMIT 50"
        )

        candidates = cursor.fetchall()

        context += "\n========== CANDIDATES ==========\n"

        for row in candidates:

            context += "\nCandidate:\n"

            for i, col in enumerate(candidate_columns):

                try:

                    value = row[i]

                    if (
                        value is not None and
                        str(value).strip()
                    ):
                        context += (
                            f"{col}: {value}\n"
                        )

                except:
                    pass

    except Exception as e:

        context += (
            f"\nCandidate Error: {e}\n"
        )

    try:

        job_columns = [
            row[1]
            for row in cursor.execute(
                "PRAGMA table_info(jobs)"
            ).fetchall()
        ]

        cursor.execute(
            "SELECT * FROM jobs LIMIT 30"
        )

        jobs = cursor.fetchall()

        context += "\n========== JOBS ==========\n"

        for row in jobs:

            context += "\nJob:\n"

            for i, col in enumerate(job_columns):

                try:

                    value = row[i]

                    if (
                        value is not None and
                        str(value).strip()
                    ):
                        context += (
                            f"{col}: {value}\n"
                        )

                except:
                    pass

    except Exception as e:

        context += (
            f"\nJob Error: {e}\n"
        )

    conn.close()

    return context

