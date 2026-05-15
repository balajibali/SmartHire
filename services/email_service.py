import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
import os
from datetime import datetime
from dotenv import load_dotenv


# =========================
# 🔐 CONFIG
# =========================
APP_NAME = "AI Resume Screening"

load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")

SMTP_SERVER = "smtp.gmail.com"

SMTP_PORT = 587


# =========================
# 📧 CORE SEND FUNCTION
# =========================
def send_email(
    to_email,
    subject,
    body,
    is_html=False,
    attachment_path=None
):

    try:

        # =========================
        # 📩 MESSAGE
        # =========================
        msg = MIMEMultipart()

        msg["From"] = formataddr((
            APP_NAME,
            SENDER_EMAIL
        ))

        msg["To"] = to_email

        msg["Subject"] = subject

        # =========================
        # 📝 BODY
        # =========================
        if is_html:

            msg.attach(
                MIMEText(body, "html")
            )

        else:

            msg.attach(
                MIMEText(body, "plain")
            )

        # =========================
        # 📎 ATTACHMENT
        # =========================
        if (
            attachment_path
            and
            os.path.exists(attachment_path)
        ):

            with open(
                attachment_path,
                "rb"
            ) as file:

                part = MIMEApplication(
                    file.read(),
                    Name=os.path.basename(
                        attachment_path
                    )
                )

            part[
                'Content-Disposition'
            ] = f'''
            attachment;
            filename="{os.path.basename(attachment_path)}"
            '''

            msg.attach(part)

        # =========================
        # 🔒 SMTP
        # =========================
        context = ssl.create_default_context()

        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT
        ) as server:

            server.ehlo()

            server.starttls(
                context=context
            )

            server.ehlo()

            server.login(
                SENDER_EMAIL,
                SENDER_PASSWORD
            )

            server.send_message(msg)

        print(
            f"Email Sent -> {to_email}"
        )

        return True

    except Exception as e:

        print(
            "Email Error:",
            e
        )

        return False


# =========================
# ⭐ INTERVIEW EMAIL
# =========================
def send_interview_email(
    to_email,
    candidate_name,
    job_title
):

    subject = (
        f" Shortlisted for "
        f"{job_title}"
    )

    body = f"""
Dear {candidate_name},

Congratulations!

We are pleased to inform you that you have been shortlisted for the position of "{job_title}".

Our HR team will contact you shortly with the next steps.

Best regards,
HR Team
"""

    return send_email(
        to_email,
        subject,
        body
    )


# =========================
# 💎 HTML INTERVIEW EMAIL
# =========================
def send_interview_email_html(
    to_email,
    candidate_name,
    job_title
):

    subject = (
        f"🎉 Shortlisted for "
        f"{job_title}"
    )

    current_year = datetime.now().year

    body = f"""
    <html>

    <body style="
        font-family: Arial;
        background:#f8fafc;
        padding:20px;
    ">

        <div style="
            max-width:650px;
            margin:auto;
            background:white;
            border-radius:16px;
            overflow:hidden;
            box-shadow:
                0 10px 30px
                rgba(0,0,0,0.08);
        ">

            <!-- HEADER -->
            <div style="
                background:
                    linear-gradient(
                        135deg,
                        #2563eb,
                        #4f46e5
                    );

                padding:30px;
                color:white;
                text-align:center;
            ">

                <h1 style="
                    margin:0;
                    font-size:28px;
                ">
                    🎉 Congratulations
                </h1>

                <p style="
                    margin-top:10px;
                    opacity:0.9;
                ">
                    AI Resume Screening
                </p>

            </div>

            <!-- BODY -->
            <div style="
                padding:35px;
                color:#111827;
            ">

                <h2>
                    Hello {candidate_name},
                </h2>

                <p style="
                    font-size:16px;
                    line-height:1.7;
                ">

                    We are excited to inform you
                    that you have been shortlisted
                    for the role of:

                </p>

                <div style="
                    background:#eff6ff;
                    border-left:
                        5px solid #2563eb;

                    padding:18px;
                    border-radius:10px;
                    margin:20px 0;
                ">

                    <h2 style="
                        margin:0;
                        color:#2563eb;
                    ">
                        {job_title}
                    </h2>

                </div>

                <p style="
                    font-size:16px;
                    line-height:1.7;
                ">

                    Our recruitment team
                    will contact you shortly
                    with the next steps.

                </p>

                <br>

                <div style="
                    background:#f9fafb;
                    padding:16px;
                    border-radius:10px;
                    font-size:14px;
                    color:#6b7280;
                ">

                    🚀 Please keep checking
                    your email for updates.

                </div>

                <br><br>

                <p>
                    Best Regards,
                </p>

                <b>
                    HR TEAM
                </b>

            </div>

            <!-- FOOTER -->
            <div style="
                background:#111827;
                color:#d1d5db;
                text-align:center;
                padding:18px;
                font-size:13px;
            ">

                © {current_year}
                HR TEAM

            </div>

        </div>

    </body>

    </html>
    """

    return send_email(
        to_email,
        subject,
        body,
        is_html=True
    )


# =========================
# 📤 BULK EMAIL
# =========================
def send_bulk_emails(
    candidates,
    job_title
):

    success_count = 0

    failed = []

    for cand in candidates:

        try:

            email = cand.get("email")

            name = cand.get("name")

            if not email:
                continue

            sent = send_interview_email(
                email,
                name,
                job_title
            )

            if sent:

                success_count += 1

            else:

                failed.append(email)

        except Exception as e:

            print(
                "Bulk Email Error:",
                e
            )

    print(
        f"Bulk Email Success: "
        f"{success_count}"
    )

    return success_count


# =========================
# 📤 BULK HTML EMAIL
# =========================
def send_bulk_emails_html(
    candidates,
    job_title
):

    success_count = 0

    failed = []

    for cand in candidates:

        try:

            email = cand.get("email")

            name = cand.get("name")

            if not email:
                continue

            sent = send_interview_email_html(
                email,
                name,
                job_title
            )

            if sent:

                success_count += 1

            else:

                failed.append(email)

        except Exception as e:

            print(
                "Bulk HTML Error:",
                e
            )

    print(
        f"Bulk HTML Success: "
        f"{success_count}"
    )

    return success_count


# =========================
# ❌ REJECTION EMAIL
# =========================
def send_rejection_email(
    to_email,
    candidate_name,
    job_title
):

    subject = (
        f"Application Update - "
        f"{job_title}"
    )

    body = f"""
Dear {candidate_name},

Thank you for applying for the role of "{job_title}".

After careful consideration, we regret to inform you that you were not selected for this position at this time.

We truly appreciate your interest in AI Resume Screening and encourage you to apply for future opportunities.

Best regards,
HR Team
"""

    return send_email(
        to_email,
        subject,
        body
    )


# =========================
# 📅 INTERVIEW INVITATION
# =========================
def send_interview_schedule_email(
    to_email,
    candidate_name,
    job_title,
    interview_date,
    interview_time,
    meeting_link=None
):

    subject = (
        f"Interview Invitation - "
        f"{job_title}"
    )

    meeting_section = ""

    if meeting_link:

        meeting_section = f"""
Meeting Link:
{meeting_link}
"""

    body = f"""
Dear {candidate_name},

Congratulations!

You have been invited for an interview for the position of "{job_title}".

Interview Details:

Date:
{interview_date}

Time:
{interview_time}

{meeting_section}

Please join the interview on time.

Best regards,
HR Team
"""

    return send_email(
        to_email,
        subject,
        body
    )