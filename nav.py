import streamlit as st

# =========================
# 🚀 NAVIGATE
# =========================
def navigate(page):
    if "history" not in st.session_state:
        st.session_state.history = []

    current = st.session_state.get("page")

    if current and (not st.session_state.history or st.session_state.history[-1] != current):
        st.session_state.history.append(current)

    st.session_state.page = page
    st.rerun()


# =========================
# 🔙 GO BACK
# =========================
def go_back(default="dashboard"):
    history = st.session_state.get("history", [])

    if history:
        st.session_state.page = history.pop()
        st.session_state.history = history
    else:
        st.session_state.page = default

    st.rerun()