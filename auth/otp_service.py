import random
import time

OTP_EXPIRY = 300  # 5 minutes

def generate_otp():
    return str(random.randint(100000, 999999))

def store_otp(session, email):
    otp = generate_otp()
    session["otp"] = otp
    session["otp_email"] = email
    session["otp_time"] = time.time()
    session["otp_attempts"] = 0
    return otp

def verify_otp(session, email, entered_otp):
    if "otp" not in session:
        return False, "No OTP found"

    if email != session.get("otp_email"):
        return False, "Email mismatch"

    if time.time() - session["otp_time"] > OTP_EXPIRY:
        return False, "OTP expired"

    if session["otp_attempts"] >= 3:
        return False, "Too many attempts"

    if entered_otp == session["otp"]:
        return True, "Success"
    else:
        session["otp_attempts"] += 1
        return False, "Invalid OTP"