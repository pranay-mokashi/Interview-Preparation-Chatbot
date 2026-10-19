import streamlit as st
from utils.styles import apply_theme, sidebar_user_panel
from utils.auth import signup_user, login_user

st.set_page_config(page_title="Interview Prep Chatbot", page_icon="🤖", layout="wide")
apply_theme()

defaults = {
    "logged_in": False,
    "role": None,
    "username": None,
    "messages": [],
    "mock_mode": False,
    "score": 0,
    "question_index": 0,
    "mock_questions": [],
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# ---------------- LOGGED-IN LANDING ----------------
if st.session_state.logged_in:
    sidebar_user_panel()

    st.title("🤖 Interview Preparation Dashboard")
    st.write(f"Welcome back, **{st.session_state.username}**. Pick where you'd like to go.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 💬 Practice Chat")
        st.caption("Ask interview questions and get instant matched answers, or upload your resume for skill-based prompts.")
        st.page_link("pages/1_💬_Chat.py", label="Open Chat", icon="💬")
    with col2:
        st.markdown("#### 📝 Mock Test")
        st.caption("Take a timed 5-question mock interview and get scored feedback.")
        st.page_link("pages/2_📝_Mock_Test.py", label="Start Mock Test", icon="📝")
    with col3:
        st.markdown("#### 📊 My Dashboard")
        st.caption("Track your score history and review past chat sessions.")
        st.page_link("pages/3_📊_Dashboard.py", label="View Dashboard", icon="📊")

    if st.session_state.role == "admin":
        st.divider()
        st.markdown("#### 🛠️ Admin")
        st.caption("Manage the question bank and view all users.")
        st.page_link("pages/4_🛠️_Admin.py", label="Open Admin Panel", icon="🛠️")

# ---------------- LOGIN / SIGNUP ----------------
else:
    st.markdown(
        "<h1 style='text-align:center;'>🤖 Interview Preparation Chatbot</h1>"
        "<p style='text-align:center;color:#64748B;'>Practice smarter with instant feedback and mock interviews.</p>",
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        login_tab, signup_tab = st.tabs(["🔑 Login", "🚀 Sign Up"])

        with login_tab:
            u = st.text_input("Username", key="login_user")
            p = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True, key="login_btn"):
                ok, msg, role = login_user(u.strip(), p)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username = u.strip()
                    st.session_state.role = role
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with signup_tab:
            nu = st.text_input("Choose a username", key="signup_user")
            np_ = st.text_input("Choose a password", type="password", key="signup_pass")
            np2 = st.text_input("Confirm password", type="password", key="signup_pass2")
            if st.button("Create Account", use_container_width=True, key="signup_btn"):
                if np_ != np2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = signup_user(nu, np_)
                    st.success(msg) if ok else st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)
