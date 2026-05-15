import streamlit as st
from database.db import get_connection
from auth.otp_service import store_otp, verify_otp
from services.email_service import send_email
import hashlib
import re


# 🔐 HASH PASSWORD
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

    st.title("📝 Sign Up")

    # ✅ FORM (better UX)
    with st.form("register_form"):

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        send_otp = st.form_submit_button("📩 Send OTP")

    # =========================
    # 📩 SEND OTP
    # =========================
    if send_otp:

        if not email or not password or not confirm:
            st.warning("All fields are required")
            return

        if not is_valid_email(email):
            st.warning("Enter a valid email")
            return

        if len(password) < 6 or not any(c.isdigit() for c in password):
            st.warning("Password must be 6+ chars and include a number")
            return

        if password != confirm:
            st.warning("Passwords do not match")
            return

        # 🔍 CHECK EXISTING USER
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            st.error("Email already registered")
            conn.close()
            return

        conn.close()

        # 🔐 STORE OTP
        otp = store_otp(st.session_state, email)

        send_email(email, "OTP Verification", f"Your OTP is {otp}")

        st.success("OTP sent to your email")

    st.divider()

    # =========================
    # ✅ VERIFY & REGISTER
    # =========================
    otp_input = st.text_input("Enter OTP")

    if st.button("✅ Register"):

        if not email or not otp_input:
            st.warning("Enter email and OTP")
            return

        success, msg = verify_otp(st.session_state, email, otp_input)

        if success:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (email, password, is_verified) VALUES (?, ?, 1)",
                (email, hash_password(password))
            )

            conn.commit()
            conn.close()

            st.success("✅ Registered successfully")
            st.session_state.page = "login"
            st.rerun()

        else:
            st.error(msg)

    st.divider()

    # 🔐 LOGIN NAV
    if st.button("🔐 Already have account? Login"):
        st.session_state.page = "login"
        st.rerun()


# 🎨 CSS FIX
def load_css():
    try:
        with open("assets/styles.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        print("CSS Load Error:", e)