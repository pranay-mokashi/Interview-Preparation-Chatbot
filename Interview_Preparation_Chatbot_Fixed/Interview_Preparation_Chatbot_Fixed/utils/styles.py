"""Shared CSS. Uses data-testid selectors (stable across Streamlit versions)
instead of auto-generated class names like `.css-1d391kg` (those change on
every Streamlit release and silently break).
"""
import streamlit as st

CSS = """
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #EFF6FF, #FFFFFF);
    border-right: 1px solid #E2E8F0;
}

[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 10px 14px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
}

.stButton button {
    border-radius: 10px;
    font-weight: 600;
    background: linear-gradient(135deg, #2563EB, #0EA5E9);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    transition: transform 0.15s ease;
}
.stButton button:hover {
    transform: translateY(-1px);
    filter: brightness(1.05);
}

.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.06);
}

.auth-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 2.2rem 2rem;
    box-shadow: 0 4px 24px rgba(15, 23, 42, 0.08);
}

h1, h2, h3 { letter-spacing: -0.01em; }
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def metric_card(label: str, value: str, help_text: str = ""):
    st.markdown(
        f"""<div class="metric-card">
                <div style="color:#64748B;font-size:0.85rem;font-weight:600;">{label}</div>
                <div style="font-size:1.8rem;font-weight:700;color:#0F172A;">{value}</div>
                <div style="color:#94A3B8;font-size:0.78rem;">{help_text}</div>
            </div>""",
        unsafe_allow_html=True,
    )


def sidebar_user_panel():
    with st.sidebar:
        st.markdown(f"### 👋 {st.session_state.username}")
        st.caption(f"Role: {st.session_state.role}")
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.divider()
