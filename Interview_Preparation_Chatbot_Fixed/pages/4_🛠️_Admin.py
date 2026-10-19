import pandas as pd
import streamlit as st

from utils.styles import apply_theme, sidebar_user_panel, metric_card
from utils.auth import require_admin
from utils.db import run_query

st.set_page_config(page_title="Admin | Interview Bot", page_icon="🛠️", layout="wide")
apply_theme()
require_admin()
sidebar_user_panel()

st.title("🛠️ Admin Panel")

questions = run_query("SELECT id, question, answer, category FROM questions ORDER BY id DESC", fetch=True) or []
users = run_query("SELECT username, role, created_at FROM users", fetch=True) or []

col1, col2 = st.columns(2)
with col1:
    metric_card("Total Questions", str(len(questions)))
with col2:
    metric_card("Total Users", str(len(users)))

tab1, tab2, tab3 = st.tabs(["➕ Add Question", "📋 Manage Questions", "👥 Users"])

with tab1:
    q = st.text_input("Question")
    a = st.text_area("Answer")
    c = st.selectbox("Category", ["HR", "Technical", "Aptitude", "General"])
    if st.button("Add Question", use_container_width=True):
        if q and a:
            result = run_query(
                "INSERT INTO questions (question, answer, category) VALUES (%s, %s, %s)",
                (q.strip(), a.strip(), c),
            )
            if result is True:
                st.success("Added successfully.")
                st.rerun()
            else:
                st.error("Question could not be added. Check the database connection.")
        else:
            st.error("Please fill in both the question and answer.")

with tab2:
    if questions:
        df = pd.DataFrame(questions, columns=["ID", "Question", "Answer", "Category"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        del_id = st.number_input("Question ID to delete", step=1, min_value=0)
        if st.button("Delete Question", use_container_width=True):
            existing_ids = {row[0] for row in questions}
            if del_id in existing_ids:
                result = run_query("DELETE FROM questions WHERE id=%s", (int(del_id),))
                if result is True:
                    st.success(f"Deleted question #{int(del_id)}.")
                    st.rerun()
                else:
                    st.error("Question could not be deleted. Check the database connection.")
            else:
                st.error("No question with that ID.")
    else:
        st.caption("No questions in the bank yet.")

with tab3:
    if users:
        st.dataframe(
            pd.DataFrame(users, columns=["Username", "Role", "Joined"]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No users yet.")
