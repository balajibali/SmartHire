from datetime import date, timedelta
from database.db import get_connection


# =========================
# 🔔 GET ALERTS (UI USE)
# =========================
def get_deadline_alerts(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT title, deadline FROM jobs WHERE user_id=?",
            (user_id,)
        )
        jobs = cursor.fetchall()

        today = date.today()
        soon = today + timedelta(days=2)

        expiring = []
        expired = []

        for title, deadline in jobs:
            if not deadline:
                continue

            if isinstance(deadline, str):
                deadline = date.fromisoformat(deadline)

            if deadline < today:
                expired.append(title)

            elif today <= deadline <= soon:
                expiring.append(title)

        return expiring, expired

    finally:
        conn.close()


# =========================
# 📧 SEND REMINDER EMAILS
# =========================
def send_deadline_reminders(user_email, user_id):
    from services.email_service import send_email

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT title, deadline FROM jobs WHERE user_id=?",
            (user_id,)
        )
        jobs = cursor.fetchall()

        today = date.today()
        tomorrow = today + timedelta(days=1)

        sent_count = 0

        for title, deadline in jobs:
            if not deadline:
                continue

            if isinstance(deadline, str):
                deadline = date.fromisoformat(deadline)

            if deadline == tomorrow:
                success = send_email(
                    user_email,
                    "⏳ Job Deadline Reminder",
                    f"""
Hello,

This is a reminder that your job posting:

📌 {title}

is expiring tomorrow ({deadline}).

Please take necessary action.

Regards,  
Recruitment System
"""
                )

                if success:
                    sent_count += 1

        return sent_count

    finally:
        conn.close()