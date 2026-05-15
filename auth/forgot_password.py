import streamlit as st
from auth.otp_service import store_otp, verify_otp
from services.email_service import send_email
from database.db import get_connection
import hashlib
import re


# 🔐 HASH
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 📧 EMAIL VALIDATION
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def show():
    load_css()

    # 🔙 BACK
    if st.button("⬅ Back to Login"):
        st.session_state.page = "login"
        st.rerun()

    st.title("🔄 Reset Password")

    # =========================
    # 📧 EMAIL INPUT
    # =========================
    email = st.text_input("Email")

    # =========================
    # 📩 SEND OTP
    # =========================
    if st.button("📩 Send OTP"):

        if not email:
            st.warning("Enter your email")
            return

        if not is_valid_email(email):
            st.warning("Invalid email format")
            return

        # 🔍 CHECK USER EXISTS
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        conn.close()

        if not user:
            st.error("Email not registered")
            return

        otp = store_otp(st.session_state, email)
        send_email(email, "Reset OTP", f"Your OTP is {otp}")

        st.success("OTP sent to your email")

    st.divider()

    # =========================
    # 🔐 RESET FORM
    # =========================
    otp_input = st.text_input("Enter OTP")
    new_pass = st.text_input("New Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("✅ Reset Password"):

        if not otp_input or not new_pass or not confirm:
            st.warning("All fields required")
            return

        if len(new_pass) < 6 or not any(c.isdigit() for c in new_pass):
            st.warning("Password must be 6+ chars and include a number")
            return

        if new_pass != confirm:
            st.warning("Passwords do not match")
            return

        success, msg = verify_otp(st.session_state, email, otp_input)

        if success:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET password=? WHERE email=?",
                (hash_password(new_pass), email)
            )

            conn.commit()
            conn.close()

            st.success("✅ Password updated successfully")
            st.session_state.page = "login"
            st.rerun()

        else:
            st.error(msg)

    st.divider()

    # 🔐 NAV
    if st.button("🔐 Go to Login"):
        st.session_state.page = "login"
        st.rerun()


# 🎨 CSS FIX
def load_css():
    try:
        with open("assets/styles.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        print("CSS Load Error:", e)