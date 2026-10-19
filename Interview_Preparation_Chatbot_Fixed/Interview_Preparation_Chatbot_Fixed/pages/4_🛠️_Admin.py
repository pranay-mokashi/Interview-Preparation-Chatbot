import pandas as pd
import streamlit as st

from utils.styles import apply_theme, sidebar_user_panel, metric_card
from utils.auth import require_admin
from utils.db import run_query

st.set_page_config(
    page_title="Admin Dashboard | Interview Bot",
    page_icon="🛠️",
    layout="wide"
)

apply_theme()
require_admin()
sidebar_user_panel()

st.title("🛠️ Admin Dashboard")
st.caption("Manage users, questions, and mock-test performance.")

# --------------------------------------------------
# DATABASE HELPERS
# --------------------------------------------------

def get_rows(query, params=None):
    """Fetch database rows safely."""
    result = run_query(query, params=params, fetch=True)
    return result if result is not None else []


def get_count(query):
    """Return a count from the database."""
    result = run_query(query, fetchone=True)

    if result and result[0] is not None:
        return int(result[0])

    return 0


# --------------------------------------------------
# LOAD DATABASE INFORMATION
# --------------------------------------------------

users = get_rows(
    "SELECT username, role, created_at FROM users ORDER BY created_at DESC"
)

questions = get_rows(
    "SELECT id, question, answer, category "
    "FROM questions ORDER BY id DESC"
)

total_users = get_count("SELECT COUNT(*) FROM users")
total_questions = get_count("SELECT COUNT(*) FROM questions")

# Inspect existing mock_results columns before using them.
result_columns = get_rows("SHOW COLUMNS FROM mock_results")
available_columns = {
    str(row[0]).lower()
    for row in result_columns
}

# Determine likely score and user columns without changing the schema.
score_column = next(
    (
        col for col in ["score", "marks", "total_score", "percentage"]
        if col in available_columns
    ),
    None
)

user_column = next(
    (
        col for col in ["username", "user_id", "user"]
        if col in available_columns
    ),
    None
)

date_column = next(
    (
        col for col in ["created_at", "test_date", "date", "attempted_at"]
        if col in available_columns
    ),
    None
)

total_mock_tests = get_count(
    "SELECT COUNT(*) FROM mock_results"
)

# --------------------------------------------------
# LOAD MOCK RESULTS
# --------------------------------------------------

mock_results = []
average_score = 0.0
results_error = None

if score_column:
    try:
        # Column names are selected only from the known list above.
        selected_columns = ["*"]

        order_clause = (
            f" ORDER BY `{date_column}` DESC"
            if date_column else ""
        )

        mock_results = get_rows(
            f"SELECT {', '.join(selected_columns)} "
            f"FROM mock_results{order_clause}"
        )

        score_values = get_rows(
            f"SELECT AVG(`{score_column}`) FROM mock_results"
        )

        if score_values and score_values[0][0] is not None:
            average_score = float(score_values[0][0])

    except Exception:
        results_error = "Mock-test results could not be loaded."
else:
    results_error = (
        "The score column in mock_results was not recognized. "
        "Check the table's column names."
    )

# --------------------------------------------------
# OVERVIEW METRICS
# --------------------------------------------------

st.subheader("📊 Overview")

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    metric_card("Registered Users", str(total_users))

with metric2:
    metric_card("Question Bank", str(total_questions))

with metric3:
    metric_card("Mock Tests", str(total_mock_tests))

with metric4:
    metric_card("Average Score", f"{average_score:.2f}")

st.divider()

# --------------------------------------------------
# QUESTION CATEGORY CHART
# --------------------------------------------------

st.subheader("📚 Question Bank Analytics")

if questions:
    question_df = pd.DataFrame(
        questions,
        columns=["ID", "Question", "Answer", "Category"]
    )

    category_counts = (
        question_df["Category"]
        .fillna("Uncategorized")
        .value_counts()
        .rename_axis("Category")
        .reset_index(name="Number of Questions")
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Questions by Category**")
        st.bar_chart(
            category_counts.set_index("Category")
        )

    with chart_col2:
        st.markdown("**Category Distribution**")
        st.dataframe(
            category_counts,
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("Your question bank is empty. Add questions below.")

st.divider()

# --------------------------------------------------
# ADMIN TABS
# --------------------------------------------------

tab_add, tab_manage, tab_users, tab_results, tab_export = st.tabs(
    [
        "➕ Add Question",
        "🔍 Manage Questions",
        "👥 Users",
        "📝 Mock Results",
        "📥 Export Data"
    ]
)

# --------------------------------------------------
# TAB 1: ADD QUESTION
# --------------------------------------------------

with tab_add:
    st.subheader("Add a New Question")

    with st.form("add_question_form", clear_on_submit=True):
        new_question = st.text_area(
            "Question",
            placeholder="Enter the interview question..."
        )

        new_answer = st.text_area(
            "Answer",
            placeholder="Enter the suggested answer..."
        )

        new_category = st.selectbox(
            "Category",
            ["HR", "Technical", "Aptitude", "General"]
        )

        submitted = st.form_submit_button(
            "➕ Add Question",
            use_container_width=True
        )

    if submitted:
        if not new_question.strip() or not new_answer.strip():
            st.error("Please enter both the question and answer.")
        else:
            result = run_query(
                "INSERT INTO questions (question, answer, category) "
                "VALUES (%s, %s, %s)",
                (
                    new_question.strip(),
                    new_answer.strip(),
                    new_category
                )
            )

            if result is True:
                st.success("Question added successfully!")
                st.rerun()
            else:
                st.error(
                    "Question could not be added. "
                    "Check the database connection."
                )

# --------------------------------------------------
# TAB 2: MANAGE QUESTIONS
# --------------------------------------------------

with tab_manage:
    st.subheader("Manage Question Bank")

    if questions:
        question_df = pd.DataFrame(
            questions,
            columns=["ID", "Question", "Answer", "Category"]
        )

        search_text = st.text_input(
            "🔍 Search questions",
            placeholder="Search by question, answer, or keyword..."
        )

        category_options = ["All"] + sorted(
            question_df["Category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected_category = st.selectbox(
            "Filter by category",
            category_options
        )

        filtered_df = question_df.copy()

        if search_text.strip():
            search_mask = (
                filtered_df["Question"].astype(str).str.contains(
                    search_text, case=False, na=False, regex=False
                )
                |
                filtered_df["Answer"].astype(str).str.contains(
                    search_text, case=False, na=False, regex=False
                )
            )

            filtered_df = filtered_df[search_mask]

        if selected_category != "All":
            filtered_df = filtered_df[
                filtered_df["Category"].astype(str) == selected_category
            ]

        st.caption(f"Showing {len(filtered_df)} question(s).")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Delete a Question")

        question_ids = [
            int(question_id)
            for question_id in question_df["ID"].tolist()
        ]

        selected_id = st.selectbox(
            "Select question ID",
            question_ids
        )

        confirm_delete = st.checkbox(
            f"I confirm that I want to delete question #{selected_id}."
        )

        if st.button(
            "🗑️ Delete Selected Question",
            disabled=not confirm_delete,
            use_container_width=True
        ):
            result = run_query(
                "DELETE FROM questions WHERE id=%s",
                (int(selected_id),)
            )

            if result is True:
                st.success(f"Question #{selected_id} deleted.")
                st.rerun()
            else:
                st.error(
                    "Question could not be deleted. "
                    "Check the database connection."
                )
    else:
        st.info("No questions are available.")

# --------------------------------------------------
# TAB 3: USERS
# --------------------------------------------------

with tab_users:
    st.subheader("Registered Users")

    if users:
        users_df = pd.DataFrame(
            users,
            columns=["Username", "Role", "Joined"]
        )

        user_search = st.text_input(
            "Search users by username",
            key="user_search"
        )

        if user_search.strip():
            users_df = users_df[
                users_df["Username"].astype(str).str.contains(
                    user_search,
                    case=False,
                    na=False,
                    regex=False
                )
            ]

        st.dataframe(
            users_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(f"Users displayed: {len(users_df)}")
    else:
        st.info("No registered users found.")

# --------------------------------------------------
# TAB 4: MOCK TEST RESULTS
# --------------------------------------------------

with tab_results:
    st.subheader("Mock-Test Results")

    if results_error:
        st.warning(results_error)

    if mock_results:
        result_df = pd.DataFrame(
            mock_results,
            columns=[str(row[0]) for row in result_columns]
        )

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )

        if score_column:
            st.markdown("### Score Distribution")

            score_series = pd.to_numeric(
                result_df[score_column],
                errors="coerce"
            ).dropna()

            if not score_series.empty:
                st.bar_chart(score_series.reset_index(drop=True))
    else:
        st.info(
            "No mock-test results to display, or the score column "
            "needs to be configured."
        )

# --------------------------------------------------
# TAB 5: EXPORT DATA
# --------------------------------------------------

with tab_export:
    st.subheader("Download Reports")

    st.caption(
        "Export the available data for project reports and analysis."
    )

    if users:
        export_users_df = pd.DataFrame(
            users,
            columns=["Username", "Role", "Joined"]
        )

        st.download_button(
            "📥 Download Users CSV",
            data=export_users_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="registered_users.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No user data available to export.")

    if questions:
        export_questions_df = pd.DataFrame(
            questions,
            columns=["ID", "Question", "Answer", "Category"]
        )

        st.download_button(
            "📥 Download Questions CSV",
            data=export_questions_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="question_bank.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No questions available to export.")

    if mock_results:
        export_results_df = pd.DataFrame(
            mock_results,
            columns=[str(row[0]) for row in result_columns]
        )

        st.download_button(
            "📥 Download Mock Results CSV",
            data=export_results_df.to_csv(index=False).encode("utf-8-sig"),
            file_name="mock_test_results.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No mock-test results available to export.")

st.divider()
st.caption("Interview Preparation Chatbot | Admin Dashboard")

