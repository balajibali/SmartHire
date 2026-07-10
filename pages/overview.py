import streamlit as st
import plotly.express as px
import pandas as pd

from services.analytics_service import (
    get_kpi_data,
    applications_per_job,
    candidate_status_distribution,
    recent_activity,
    top_skills,
    funnel_data,
    get_ai_insight_context,
    get_chat_context,
    
)

from services.ollama_service import (
    generate_ai_response,
    generate_chat_response,
    check_ollama
)


# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="Recruitment Overview",
    layout="wide"
)


# =====================================
# CSS
# =====================================
def load_css():

    st.markdown("""
    <style>

    #MainMenu {visibility:hidden;}
    footer {visibility:hidden;}
    header {visibility:hidden;}

    .stApp{
        background:
        linear-gradient(
            135deg,
            #f8fafc 0%,
            #eef2ff 50%,
            #ffffff 100%
        );
    }

    .main-title{
        text-align:center;
        font-size:34px;
        font-weight:700;
        color:#111827;
        margin-bottom:25px;
    }

    .card{
        background:white;
        padding:20px;
        border-radius:16px;
        border:1px solid #e5e7eb;
        box-shadow:0 4px 20px rgba(0,0,0,0.05);
    }
.kpi-card{
    padding:20px;
    border-radius:18px;
    text-align:center;
    color:white;
    box-shadow:0 8px 20px rgba(0,0,0,0.08);
    transition:0.3s;
}

.kpi-card:hover{
    transform:translateY(-5px);
}

/* Different colors */
.kpi-1{
    background:linear-gradient(135deg,#3b82f6,#2563eb);
}

.kpi-2{
    background:linear-gradient(135deg,#10b981,#059669);
}

.kpi-3{
    background:linear-gradient(135deg,#8b5cf6,#7c3aed);
}

.kpi-4{
    background:linear-gradient(135deg,#f59e0b,#d97706);
}

.kpi-5{
    background:linear-gradient(135deg,#ef4444,#dc2626);
}

.kpi-6{
    background:linear-gradient(135deg,#06b6d4,#0891b2);
}

.kpi-value{
    font-size:32px;
    font-weight:700;
}

.kpi-title{
    font-size:14px;
    margin-top:8px;
    opacity:0.9;
}


    .insight-box{

        background:white;

        border-left:5px solid #2563eb;

        padding:20px;

        border-radius:12px;

        border:1px solid #e5e7eb;

        box-shadow:
            0 4px 15px rgba(0,0,0,0.05);

        color:#111827;
    }

    .stDataFrame{

        border:1px solid #e5e7eb;
        border-radius:12px;
    }

    div[data-testid="stMetric"]{

        background:white;
        border-radius:12px;
        padding:10px;
    }

    .stButton > button{

        background:#2563eb;
        color:white;
        border:none;
        border-radius:10px;
        font-weight:600;
        padding:0.6rem 1rem;
    }

    .stButton > button:hover{

        background:#1d4ed8;
        color:white;
    }

    .stTextInput input{

        border-radius:10px;
        border:1px solid #d1d5db;
    }

    .chat-user{

        background:#dbeafe;
        padding:12px;
        border-radius:10px;
        margin-bottom:10px;
        color:#111827;
        border-left:4px solid #2563eb;
    }

    .chat-ai{

        background:#f3f4f6;
        padding:12px;
        border-radius:10px;
        margin-bottom:10px;
        color:#111827;
        border-left:4px solid #10b981;
    }

    </style>
    """, unsafe_allow_html=True)


# =====================================
# SHOW
# =====================================
def show():

    load_css()

    st.markdown(
        "<div class='main-title'>Recruitment Analytics Dashboard</div>",
        unsafe_allow_html=True
    )

    if st.button("⬅ Back To Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================
    # KPI SECTION
    # =====================================

    kpi = get_kpi_data()

    metrics = [
             ("Total Jobs", kpi["total_jobs"], "kpi-1"),
             ("Active Jobs", kpi["active_jobs"], "kpi-2"),
             ("Candidates", kpi["total_candidates"], "kpi-3"),
             ("Shortlisted", kpi["shortlisted"], "kpi-4"),
             ("Interviews", kpi["interviews"], "kpi-5"),
             ("Hired", kpi["hired"], "kpi-6"),
    ]

    cols = st.columns(6)

    for col, (title, value, css_class) in zip(cols, metrics):

          with col:

                 st.markdown(
                        f"""
                        <div class="kpi-card {css_class}">
                           <div class="kpi-value">{value}</div>
                           <div class="kpi-title">{title}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
        )



    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================
    # APPLICATIONS + STATUS
    # =====================================

    left, right = st.columns(2)

    with left:

        st.markdown("### Applications Per Job")

        jobs_df = applications_per_job()

        if not jobs_df.empty:

            fig = px.bar(
                jobs_df,
                x="title",
                y="total",
                text_auto=True
            )

            fig.update_layout(
                template="plotly_white",
                height=400
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with right:

        st.markdown("### Candidate Status")

        status_df = candidate_status_distribution()

        if not status_df.empty:

            fig2 = px.pie(
                status_df,
                names="status",
                values="total",
                hole=0.55
            )

            fig2.update_layout(
                template="plotly_white",
                height=400
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================
    # SKILLS + FUNNEL
    # =====================================

    left, right = st.columns(2)

    with left:

        st.markdown("###  Top Skills")

        skills_df = top_skills()

        if not skills_df.empty:

            fig3 = px.bar(
                skills_df,
                x="skill",
                y="count",
                text_auto=True
            )

            fig3.update_layout(
                template="plotly_white",
                height=400
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

        else:
            st.info("No skills data available")

    with right:

        st.markdown("###  Recruitment Funnel")

        funnel = funnel_data()

        funnel_df = pd.DataFrame({
            "Stage": list(funnel.keys()),
            "Count": list(funnel.values())
        })

        fig4 = px.funnel(
            funnel_df,
            x="Count",
            y="Stage"
        )

        fig4.update_layout(
            template="plotly_white",
            height=400
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================
    # RECENT ACTIVITY
    # =====================================

    st.markdown("###  Recent Candidate Activity")

    activity = recent_activity()

    if not activity.empty:

        st.dataframe(
            activity,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No candidate activity found")

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================
    # AI INSIGHTS
    # =====================================

    st.markdown("### AI Recruitment Insights")

    if st.button("Generate AI Insights"):

        if not check_ollama():

            st.error(
                "Ollama is not running. Start with: ollama serve"
            )

        else:

            context = get_ai_insight_context()

            prompt = f"""
Analyze recruitment performance.

Total Candidates:
{context['total_candidates']}

Shortlisted:
{context['shortlisted']}

Interviews:
{context['interviews']}

Hired:
{context['hired']}

Recent Jobs:
{', '.join(context['jobs'])}

Provide:

1. Hiring Trends
2. Recruitment Bottlenecks
3. Recommendations
4. Risk Areas
5. Hiring Health Score
"""

            with st.spinner("Generating Insights..."):

                insights = generate_ai_response(prompt)

            st.markdown("<div class='insight-box'>", unsafe_allow_html=True)
            st.markdown(insights)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

        # =====================================
    # AI CHAT ASSISTANT
    # =====================================

    st.markdown("### Recruitment Assistant")

    if "overview_chat" not in st.session_state:
        st.session_state.overview_chat = []

    question = st.text_input(
        "Ask about candidates, jobs, hiring trends..."
    )

    col1, col2 = st.columns(2)

    with col1:
        ask_ai = st.button("Ask AI")

    with col2:
        quick = st.button("Quick Analytics")

    # =====================================
    # QUICK ANALYTICS
    # =====================================

    if quick:

        context = get_chat_context()

        prompt = """
Give:

1. Top Candidates
2. Hiring Status Summary
3. Open Jobs Summary
4. Recruitment Health
5. Recommendations
"""

        answer = generate_chat_response(
            prompt,
            context
        )

        st.session_state.overview_chat.append(
            ("Assistant", answer)
        )

    # =====================================
    # ASK AI
    # =====================================

    if ask_ai and question:

        context = get_chat_context()

        if check_ollama():

            answer = generate_chat_response(
                question,
                context
            )

        else:

            answer = "❌ Ollama service is not running."

        st.session_state.overview_chat.append(
            ("You", question)
        )

        st.session_state.overview_chat.append(
            ("Assistant", answer)
        )

    # =====================================
    # CHAT HISTORY
    # =====================================

    if st.session_state.overview_chat:

        st.markdown("### Conversation")

        for role, msg in st.session_state.overview_chat:

            if role == "You":

                st.markdown(
                    f"<div class='chat-user'>{msg}</div>",
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    f"<div class='chat-ai'>{msg}</div>",
                    unsafe_allow_html=True
                )
    