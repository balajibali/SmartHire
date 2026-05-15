from database.db import get_connection


def chatbot_response(query):
    query = query.lower()

    conn = get_connection()
    cursor = conn.cursor()

    # 🔥 TOP CANDIDATES
    if "top" in query or "best candidate" in query:
        cursor.execute("""
            SELECT name, score FROM candidates
            ORDER BY score DESC LIMIT 5
        """)
        data = cursor.fetchall()

        conn.close()

        if not data:
            return "No candidates found."

        response = "🏆 Top Candidates:\n"
        for name, score in data:
            response += f"{name} → {score}%\n"

        return response

    # 📊 MOST APPLICATIONS JOB
    elif "most applications" in query or "top job" in query:
        cursor.execute("""
            SELECT job_id, COUNT(*) as total 
            FROM candidates
            GROUP BY job_id
            ORDER BY total DESC LIMIT 1
        """)
        job = cursor.fetchone()

        if not job:
            conn.close()
            return "No job data available."

        cursor.execute("SELECT title FROM jobs WHERE id=?", (job[0],))
        job_name = cursor.fetchone()

        conn.close()

        return f"📊 Job with most applications: {job_name[0]} ({job[1]} candidates)"

    # 📌 SHORTLISTED
    elif "shortlisted" in query:
        cursor.execute("""
            SELECT name FROM candidates WHERE status='Shortlisted'
        """)
        data = cursor.fetchall()

        conn.close()

        if not data:
            return "No shortlisted candidates."

        response = "⭐ Shortlisted Candidates:\n"
        for (name,) in data:
            response += f"{name}\n"

        return response

    # ❌ DEFAULT
    else:
        conn.close()
        return "Try asking: top candidates, shortlisted, top job"