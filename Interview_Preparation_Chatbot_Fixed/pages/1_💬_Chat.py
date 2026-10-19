import streamlit as st
import PyPDF2
import speech_recognition as sr
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.styles import apply_theme, sidebar_user_panel
from utils.auth import require_login
from utils.db import run_query

st.set_page_config(page_title="Chat | Interview Bot", page_icon="💬", layout="wide")
apply_theme()
require_login()
sidebar_user_panel()
st.session_state.setdefault("messages", [])

st.title("💬 Practice Chat")

with st.sidebar:
    st.subheader("Filter")
    category = st.selectbox("Category", ["All", "HR", "Technical", "Aptitude", "General"], key="chat_category")

if category == "All":
    data = run_query("SELECT question, answer FROM questions", fetch=True) or []
else:
    data = run_query(
        "SELECT question, answer FROM questions WHERE category=%s", (category,), fetch=True
    ) or []

questions = [str(row[0]) for row in data]
answers = [str(row[1]) for row in data]

@st.cache_resource(show_spinner=False)
def build_vectorizer(qs: tuple):
    if not qs:
        return None, None
    try:
        vec = CountVectorizer().fit(qs)
        return vec, vec.transform(qs)
    except ValueError:
        return None, None

vectorizer, vectors = build_vectorizer(tuple(questions))

def get_response(user_text: str) -> str:
    if not questions:
        return "No questions available for this category yet."
    if vectorizer is None:
        return "I couldn't match that — try rephrasing as an interview question."
    try:
        query_vector = vectorizer.transform([user_text])
        if query_vector.nnz == 0:
            return "I couldn't match that — try rephrasing as an interview question."
        similarities = cosine_similarity(query_vector, vectors)[0]
        index = int(similarities.argmax())
        return answers[index] if similarities[index] > 0.3 else "I couldn't match that — try rephrasing as an interview question."
    except ValueError:
        return "Please enter a question containing searchable words."

def log_and_respond(user_text: str):
    bot = get_response(user_text)
    st.session_state.messages.extend([("user", user_text), ("assistant", bot)])
    run_query(
        "INSERT INTO chat_history (username, question, answer) VALUES (%s, %s, %s)",
        (st.session_state.username, user_text, bot),
    )

with st.sidebar:
    st.subheader("📄 Resume-based prompts")
    uploaded_file = st.file_uploader("Upload resume", type=["txt", "pdf"])
    if uploaded_file:
        resume_text = ""
        try:
            if uploaded_file.name.lower().endswith(".txt"):
                raw = uploaded_file.getvalue()
                try:
                    resume_text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    resume_text = raw.decode("latin-1", errors="replace")
            else:
                pdf = PyPDF2.PdfReader(uploaded_file)
                resume_text = " ".join(page.extract_text() or "" for page in pdf.pages)
        except Exception as exc:
            st.error(f"Couldn't read that resume: {exc}")

        keys = ["python", "java", "sql", "ai", "ml", "flutter", "react", "cloud", "aws"]
        skills = [skill for skill in keys if skill in resume_text.lower()]
        if skills:
            st.caption("Detected skills — click to ask:")
            for skill in skills:
                if st.button(f"Explain {skill}", key=f"skill_{skill}"):
                    log_and_respond(f"Explain {skill}")
                    st.rerun()
        elif resume_text:
            st.caption("No supported skills detected in this resume.")

user_input = st.chat_input("Ask an interview question...")
if st.button("🎤 Speak instead"):
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            with st.spinner("Listening..."):
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
        spoken = recognizer.recognize_google(audio)
        log_and_respond(spoken)
        st.rerun()
    except Exception as exc:
        st.error(f"Microphone unavailable or speech could not be recognized: {exc}")

if user_input:
    log_and_respond(user_input)
    st.rerun()

for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.write(message)

if st.session_state.messages and st.button("🆕 Clear chat"):
    st.session_state.messages = []
    st.rerun()
