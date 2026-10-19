import random
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.styles import apply_theme, sidebar_user_panel
from utils.auth import require_login
from utils.db import run_query

st.set_page_config(page_title="Mock Test | Interview Bot", page_icon="📝", layout="centered")
apply_theme()
require_login()
sidebar_user_panel()

st.title("📝 Mock Interview")

defaults = {
    "mock_mode": False, "score": 0.0, "question_index": 0,
    "mock_questions": [], "mock_category": "All", "mock_saved": False,
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

def feedback(score: float) -> str:
    if score > 0.7:
        return "🔥 Excellent"
    if score > 0.4:
        return "👍 Good"
    if score > 0.2:
        return "⚠️ Average"
    return "❌ Weak"

if not st.session_state.mock_mode:
    st.write("Answer randomly selected questions and receive similarity-based scoring.")
    category = st.selectbox("Category", ["All", "HR", "Technical", "Aptitude", "General"])
    num_questions = st.slider("Number of questions", 3, 10, 5)

    if category == "All":
        data = run_query("SELECT question FROM questions", fetch=True) or []
    else:
        data = run_query("SELECT question FROM questions WHERE category=%s", (category,), fetch=True) or []
    available = [str(row[0]) for row in data]

    if not available:
        st.warning("No questions available for this category yet.")
    elif st.button("Start Mock Test", use_container_width=True):
        st.session_state.mock_mode = True
        st.session_state.score = 0.0
        st.session_state.question_index = 0
        st.session_state.mock_category = category
        st.session_state.mock_questions = random.sample(available, min(num_questions, len(available)))
        st.session_state.mock_saved = False
        st.rerun()
else:
    total = len(st.session_state.mock_questions)
    index = st.session_state.question_index

    if total == 0:
        st.warning("No questions were selected. Start a new test.")
        st.session_state.mock_mode = False
        st.rerun()
    elif index < total:
        st.progress(index / total, text=f"Question {index + 1} of {total}")
        question = st.session_state.mock_questions[index]
        st.markdown(f"### {question}")
        answer = st.text_area("Your answer", key=f"answer_{index}")

        if st.button("Submit Answer", use_container_width=True):
            answer = answer.strip()
            if not answer:
                st.warning("Please write an answer before submitting.")
            else:
                result = run_query(
                    "SELECT answer FROM questions WHERE question=%s LIMIT 1",
                    (question,), fetchone=True,
                )
                if result and result[0]:
                    correct_answer = str(result[0])
                    try:
                        vectorizer = CountVectorizer()
                        vectors = vectorizer.fit_transform([answer, correct_answer])
                        similarity = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
                    except ValueError:
                        similarity = 0.0
                    st.info(feedback(similarity))
                    if similarity >= 0.5:
                        st.session_state.score += 1
                    elif similarity >= 0.3:
                        st.session_state.score += 0.5
                else:
                    st.warning("The reference answer could not be found; this question was not scored.")
                st.session_state.question_index += 1
                st.rerun()
    else:
        st.success(f"Final Score: {st.session_state.score:g}/{total}")
        if not st.session_state.mock_saved:
            saved = run_query(
                "INSERT INTO mock_results (username, score, total, category) VALUES (%s, %s, %s, %s)",
                (st.session_state.username, st.session_state.score, total, st.session_state.mock_category),
            )
            st.session_state.mock_saved = saved is True
            if saved is not True:
                st.warning("Your result could not be saved to the database.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Retake", use_container_width=True):
                st.session_state.mock_mode = False
                st.session_state.mock_saved = False
                st.rerun()
        with col2:
            if st.button("View Dashboard", use_container_width=True):
                st.switch_page("pages/3_📊_Dashboard.py")
