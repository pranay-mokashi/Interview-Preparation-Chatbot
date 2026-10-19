import streamlit as st

CSS = """
<style>

/* Main application background */
.stApp {
    background: #FFFFFF !important;
    color: #1E293B !important;
}

/* Main content */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* Streamlit header and top toolbar */
[data-testid="stHeader"] {
    background: #FFFFFF !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

[data-testid="stDecoration"] {
    background: #FFFFFF !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #F8FAFC !important;
    border-right: 1px solid #E2E8F0;
}

[data-testid="stSidebar"] * {
    color: #1E293B;
}

/* Sidebar expand and collapse controls */
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebarCollapseButton"] button {
    color: #1E293B !important;
    opacity: 1 !important;
}

/* Typography */
h1, h2, h3, h4 {
    color: #0F172A !important;
    letter-spacing: -0.025em;
}

p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
    color: #475569;
}

/* Metric cards */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 22px;
    min-height: 120px;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.06);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    border-color: #6366F1;
}

.metric-label {
    color: #64748B;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 12px;
}

.metric-value {
    color: #0F172A;
    font-size: 2rem;
    line-height: 1.2;
    font-weight: 800;
}

.metric-help {
    color: #4F46E5;
    font-size: 0.78rem;
    margin-top: 8px;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;
    font-weight: 650;
    border: 1px solid #4F46E5;
    background: linear-gradient(135deg, #4F46E5, #2563EB);
    color: #FFFFFF !important;
    padding: 0.55rem 1rem;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #818CF8;
    color: #FFFFFF !important;
    box-shadow: 0 5px 18px rgba(79, 70, 229, 0.20);
    transform: translateY(-1px);
}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1;
    border-radius: 10px;
}

[data-baseweb="select"] > div {
    background-color: #FFFFFF;
    border-color: #CBD5E1;
    color: #1E293B;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #E2E8F0;
}

.stTabs [data-baseweb="tab"] {
    background: #F8FAFC;
    border-radius: 10px 10px 0 0;
    color: #475569;
    padding: 12px 18px;
}

.stTabs [aria-selected="true"] {
    background: #EEF2FF !important;
    color: #4338CA !important;
}

/* Dataframes and tables */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    overflow: hidden;
}

/* Expanders */
[data-testid="stExpander"] {
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    background: #FFFFFF;
}

/* Dividers */
hr {
    border-color: #E2E8F0;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 12px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 12px 16px;
    background: #F8FAFC;
}

/* Form container */
[data-testid="stForm"] {
    background: #FFFFFF;
    padding: 20px;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
}

</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def metric_card(label: str, value: str, help_text: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_user_panel():
    with st.sidebar:
        st.markdown("## 🎯 Interview Bot")
        st.divider()
        st.markdown(f"### 👋 {st.session_state.username}")
        st.caption(f"Role: {st.session_state.role}")

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.divider()