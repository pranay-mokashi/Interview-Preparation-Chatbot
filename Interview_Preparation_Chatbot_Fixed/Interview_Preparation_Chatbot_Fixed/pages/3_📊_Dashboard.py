import pandas as pd
import streamlit as st

from utils.styles import apply_theme, sidebar_user_panel, metric_card
from utils.auth import require_login
from utils.db import run_query

st.set_page_config(
    page_title="My Dashboard | Interview Bot",
    page_icon="📊",
    layout="wide"
)

apply_theme()
require_login()
sidebar_user_panel()

username = st.session_state.username

# --------------------------------------------------
# CUSTOM DASHBOARD STYLING
# --------------------------------------------------

st.markdown("""
<style>
.dashboard-hero {
    padding: 26px 28px;
    border-radius: 20px;
    background: linear-gradient(120deg, #312E81, #1D4ED8, #0F766E);
    border: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 25px;
}

.dashboard-hero h1 {
    color: white !important;
    margin-bottom: 8px;
    font-size: 2rem;
}

.dashboard-hero p {
    color: #E0E7FF !important;
    margin-bottom: 0;
    font-size: 1rem;
}

.section-note {
    color: #94A3B8;
    font-size: 0.9rem;
    margin-top: -10px;
    margin-bottom: 18px;
}

.insight-card {
    background: linear-gradient(145deg, #1E293B, #172033);
    border: 1px solid #334155;
    border-radius: 15px;
    padding: 18px;
    min-height: 115px;
}

.insight-title {
    color: #94A3B8;
    font-size: 0.82rem;
    font-weight: 600;
}

.insight-value {
    color: #F8FAFC;
    font-size: 1.25rem;
    font-weight: 750;
    margin-top: 10px;
}

.insight-description {
    color: #A5B4FC;
    font-size: 0.8rem;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(f"""
<div class="dashboard-hero">
    <h1>📊 Your Learning Dashboard</h1>
    <p>
        Welcome back, {username}! Track your mock-test performance,
        review your practice history, and identify areas to improve.
    </p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD USER DATA
# --------------------------------------------------

results = run_query(
    """
    SELECT score, total, category, created_at
    FROM mock_results
    WHERE username = %s
    ORDER BY created_at ASC
    """,
    (username,),
    fetch=True
) or []

chats = run_query(
    """
    SELECT id, question, answer, created_at
    FROM chat_history
    WHERE username = %s
    ORDER BY id DESC
    LIMIT 20
    """,
    (username,),
    fetch=True
) or []

# --------------------------------------------------
# PREPARE MOCK-TEST DATA
# --------------------------------------------------

if results:
    df = pd.DataFrame(
        results,
        columns=["Score", "Total", "Category", "Date"]
    )

    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")

    df = df.dropna(subset=["Score", "Total"])
    df = df[df["Total"] > 0].copy()

    df["Percentage"] = (
        df["Score"] / df["Total"] * 100
    ).round(1)

    df["Test Number"] = range(1, len(df) + 1)

else:
    df = pd.DataFrame(
        columns=[
            "Score", "Total", "Category",
            "Date", "Percentage", "Test Number"
        ]
    )

# --------------------------------------------------
# METRICS
# --------------------------------------------------

st.subheader("📌 Performance Overview")

total_tests = len(df)
chat_count = len(chats)

if total_tests:
    avg_score = df["Percentage"].mean()
    best_score = df["Percentage"].max()
    latest_score = df.iloc[-1]["Percentage"]
else:
    avg_score = None
    best_score = None
    latest_score = None

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric_card(
        "📝 Mock Tests",
        str(total_tests),
        "Total recorded attempts"
    )

with c2:
    metric_card(
        "📈 Average Score",
        f"{avg_score:.1f}%" if avg_score is not None else "—",
        "Average across valid attempts"
    )

with c3:
    metric_card(
        "🏆 Best Score",
        f"{best_score:.1f}%" if best_score is not None else "—",
        "Your highest percentage"
    )

with c4:
    metric_card(
        "💬 Recent Chats",
        str(chat_count),
        "Messages in recent history"
    )

st.write("")
st.divider()

# --------------------------------------------------
# PERFORMANCE TREND
# --------------------------------------------------

st.subheader("📈 Performance Trend")
st.markdown(
    '<div class="section-note">'
    'Track your score percentage across recorded mock tests.'
    '</div>',
    unsafe_allow_html=True
)

if not df.empty:
    chart_col, insight_col = st.columns([2, 1])

    with chart_col:
        chart_df = df[["Test Number", "Percentage"]].set_index(
            "Test Number"
        )

        st.line_chart(
            chart_df,
            y="Percentage",
            x_label="Mock Test",
            y_label="Score (%)"
        )

    with insight_col:
        st.markdown("#### 🎯 Quick Insights")

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">LATEST TEST</div>
                <div class="insight-value">{latest_score:.1f}%</div>
                <div class="insight-description">
                    Most recent valid attempt
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        difference = latest_score - avg_score

        if difference > 0:
            comparison = f"{difference:.1f} percentage points above average"
        elif difference < 0:
            comparison = f"{abs(difference):.1f} percentage points below average"
        else:
            comparison = "Equal to your average score"

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">RECENT PERFORMANCE</div>
                <div class="insight-value">
                    {"↗️" if difference > 0 else "↘️" if difference < 0 else "➡️"}
                </div>
                <div class="insight-description">{comparison}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.caption(
        "Insights are calculated from your recorded mock-test scores. "
        "They do not predict future performance."
    )

else:
    st.info(
        "Your performance chart will appear here after you complete "
        "a mock test."
    )

st.divider()

# --------------------------------------------------
# CATEGORY ANALYSIS
# --------------------------------------------------

st.subheader("📚 Category Analysis")
st.markdown(
    '<div class="section-note">'
    'Compare average scores across categories where attempts are recorded.'
    '</div>',
    unsafe_allow_html=True
)

if not df.empty:
    category_df = df.copy()

    category_df["Category"] = (
        category_df["Category"]
        .fillna("Uncategorized")
        .astype(str)
    )

    category_summary = (
        category_df.groupby("Category", as_index=False)
        .agg(
            Attempts=("Percentage", "count"),
            Average=("Percentage", "mean"),
            Best=("Percentage", "max")
        )
    )

    category_summary["Average"] = category_summary["Average"].round(1)
    category_summary["Best"] = category_summary["Best"].round(1)

    category_col1, category_col2 = st.columns([3, 2])

    with category_col1:
        st.bar_chart(
            category_summary.set_index("Category")[["Average", "Best"]],
            y_label="Score (%)"
        )

    with category_col2:
        st.dataframe(
            category_summary.rename(
                columns={
                    "Category": "Category",
                    "Attempts": "Tests",
                    "Average": "Avg. %",
                    "Best": "Best %"
                }
            ),
            use_container_width=True,
            hide_index=True
        )

    lowest_category = category_summary.sort_values(
        "Average"
    ).iloc[0]

    st.info(
        f"💡 Your lowest average among recorded categories is "
        f"**{lowest_category['Category']}** "
        f"({lowest_category['Average']:.1f}%). "
        "Consider giving this category additional practice."
    )

else:
    st.caption(
        "Category analytics will be available after your first valid mock test."
    )

st.divider()

# --------------------------------------------------
# RECENT MOCK-TEST HISTORY
# --------------------------------------------------

st.subheader("🕘 Recent Mock-Test History")

if not df.empty:
    recent_df = df.sort_values(
        "Date", ascending=False, na_position="last"
    ).head(10).copy()

    recent_df["Result"] = recent_df.apply(
        lambda row: f"{row['Score']:g} / {row['Total']:g}",
        axis=1
    )

    display_df = recent_df[
        ["Date", "Category", "Result", "Percentage"]
    ].rename(
        columns={
            "Date": "Test Date",
            "Category": "Category",
            "Result": "Score",
            "Percentage": "Percentage (%)"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📥 Download My Mock-Test History",
        data=csv_data,
        file_name="my_mock_test_history.csv",
        mime="text/csv"
    )

else:
    st.caption("No mock-test attempts have been recorded yet.")

st.divider()

# --------------------------------------------------
# RECENT CHAT HISTORY
# --------------------------------------------------

st.subheader("💬 Recent Chat History")
st.markdown(
    '<div class="section-note">'
    'Review your recent questions and the chatbot responses.'
    '</div>',
    unsafe_allow_html=True
)

if chats:
    for chat_id, question, answer, timestamp in chats:
        question_text = str(question or "Untitled question")
        answer_text = str(answer or "No answer recorded")

        title = question_text[:65]
        if len(question_text) > 65:
            title += "..."

        with st.expander(f"🗨️ {title}"):
            st.markdown("**Your Question**")
            st.write(question_text)

            st.markdown("**Chatbot Answer**")
            st.write(answer_text)

            st.caption(f"Conversation ID: {chat_id} · {timestamp}")

else:
    st.info(
        "Your chat history will appear here after you start "
        "practising on the Chat page."
    )

st.divider()

st.caption(
    "Interview Preparation Chatbot • Personal learning analytics"
)
