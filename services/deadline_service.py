from datetime import date, timedelta
from database.db import get_connection
from services.email_service import send_email


# 🔔 AUTO EMAIL REMINDER
def send_deadline_reminders(user_email, user_id):
    conn = get_connection()
    cursor = conn.cursor()

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

        # 🔧 fix string date
        if isinstance(deadline, str):
            deadline = date.fromisoformat(deadline)

        # 🎯 CONDITION
        if deadline == tomorrow:
            send_email(
                user_email,
                "⏰ Job Deadline Reminder",
                f"""
Reminder!

Your job "{title}" is expiring tomorrow.

Please take action.

- HR Hiring System
"""
            )
            sent_count += 1

    conn.close()
    return sent_count