import streamlit as st

def show():

    # ⚠️ Only keep this here OR in app.py (not both)
    st.set_page_config(layout="wide")

    # =========================
    # 🎨 GLOBAL STYLE
    # =========================
    st.markdown("""
    <style>

    /* 🔥 Hide Streamlit UI */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Background */
    .stApp {
        background: linear-gradient(rgba(10,10,40,0.9), rgba(10,10,40,0.95)),
                    url("https://images.unsplash.com/photo-1521737604893-d14cc237f11d");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }

    /* Layout spacing */
    .block-container {
        padding-top: 3rem;
        padding-left: 6rem;
        padding-right: 6rem;
    }

    /* Title */
    .title {
        font-size: 68px;
        font-weight: 800;
        line-height: 1.1;
    }

    .highlight {
        color: #6c7bff;
    }

    .subtitle {
        font-size: 20px;
        margin-top: 15px;
    }

    .desc {
        font-size: 16px;
        margin-top: 12px;
        opacity: 0.85;
        max-width: 520px;
    }

    /* Button */
    div.stButton > button {
        background: linear-gradient(90deg, #6c7bff, #4a90e2);
        color: white;
        border-radius: 30px;
        padding: 12px 32px;
        font-size: 16px;
        border: none;
    }

    div.stButton > button:hover {
        background: linear-gradient(90deg, #4a90e2, #357ABD);
    }

    /* Cards */
    .card {
        background: white;
        color: #333;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
        height: 190px;
    }

    .icon {
        width: 42px;
        margin-bottom: 10px;
    }

    </style>
    """, unsafe_allow_html=True)

    # =========================
    # 🎯 HERO SECTION
    # =========================
    col1, col2 = st.columns([1.2, 1], gap="large")

    # LEFT CONTENT
    with col1:
        st.markdown(
            '<div class="title">AI RESUME <br><span class="highlight">SCREENING</span></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="subtitle">Smart Hiring. Better Candidates. Faster.</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="desc">Upload, analyze and shortlist the best candidates using AI-powered resume screening.</div>',
            unsafe_allow_html=True
        )

        st.write("")

        if st.button("Get Started ➜"):
            st.session_state.page = "login"
            st.rerun()

    # RIGHT IMAGE (YOUR HERO)
    with col2:
        st.image("assets/hero.png", width=500)

    st.write("\n\n")

    # =========================
    # 🧩 FEATURES SECTION
    # =========================
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div class="card">
            <img class="icon" src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png"/>
            <h4>AI Powered Screening</h4>
            <p>Automatically analyze resumes and extract key information.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <img class="icon" src="https://cdn-icons-png.flaticon.com/512/1828/1828919.png"/>
            <h4>Smart Matching</h4>
            <p>Match candidates with job requirements instantly.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <img class="icon" src="https://cdn-icons-png.flaticon.com/512/1828/1828859.png"/>
            <h4>Easy Sharing</h4>
            <p>Create job links and share with candidates anywhere.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.caption("AI Resume Screening • Final Year Project")