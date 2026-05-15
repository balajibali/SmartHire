import streamlit as st
from database.db import get_connection
import hashlib
import base64


# =========================
# 🔐 PASSWORD HASH
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# 🖼️ LOAD BACKGROUND
# =========================
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# =========================
# 🎨 CSS (MAKE RIGHT COLUMN = CARD)
# =========================
def load_css():
    bg = get_base64_image("assets/login.jpeg")

    st.markdown(f"""
    <style>

    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* BACKGROUND */
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0), rgba(0,0,0,0)),
                    url("data:image/jpeg;base64,{bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .block-container {{
        padding-top: 2rem;
    }}

    /* 🔥 RIGHT COLUMN BECOMES FULL CARD */
    div[data-testid="column"]:nth-of-type(2) {{
        display: flex;
        justify-content: center;
        align-items: flex-start;
    }}

    div[data-testid="column"]:nth-of-type(2) > div {{
        background: rgba(255,255,255,0.97);
        padding: 40px;
        border-radius: 18px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.25);
        width: 100%;
        max-width: 420px;
    }}

    /* TEXT */
    .title {{
        font-size: 30px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }}

    .subtitle {{
        text-align: center;
        color: #666;
        margin-bottom: 25px;
    }}

    .divider {{
        text-align: center;
        margin: 25px 0;
        color: #999;
    }}

    /* BUTTONS */
    div.stButton > button {{
        background: linear-gradient(90deg, #4a6cf7, #3557d6);
        color: white;
        border-radius: 8px;
        height: 45px;
        border: none;
        font-weight: 600;
    }}

    </style>
    """, unsafe_allow_html=True)


# =========================
# 🚀 PAGE
# =========================
def show():
    load_css()

    # 🏠 Home
    col1, col2 = st.columns([8,1])
    with col2:
        if st.button("🏠 Home"):
            st.session_state.page = "start"
            st.rerun()

    # =========================
    # SPLIT LAYOUT
    # =========================
    left, right = st.columns([1, 1], gap="large")

    # LEFT EMPTY (just for spacing)
    with left:
        st.empty()

    # RIGHT = FULL LOGIN CARD
    with right:

        st.markdown('<div class="title">Welcome Back!</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Login to your account</div>', unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        # ROW: REMEMBER + FORGOT
        colA, colB = st.columns([1,1])
        with colA:
            remember = st.checkbox("Remember me")

        with colB:
            if st.button("Forgot Password?", use_container_width=True):
                st.session_state.page = "forgot"
                st.rerun()

        # LOGIN
        if st.button(" Login", use_container_width=True):
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email=? AND password=? AND is_verified=1",
                (email, hash_password(password))
            )

            user = cursor.fetchone()
            conn.close()

            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.email = email
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")

        # DIVIDER
        st.markdown('<div class="divider">──────── OR ────────</div>', unsafe_allow_html=True)

        # CREATE ACCOUNT
        if st.button(" Create Account", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()