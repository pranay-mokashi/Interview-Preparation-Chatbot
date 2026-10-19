import pandas as pd
import streamlit as st

from utils.styles import apply_theme, sidebar_user_panel, metric_card
from utils.auth import require_login
from utils.db import run_query

st.set_page_config(page_title="Dashboard | Interview Bot", page_icon="📊", layout="wide")
apply_theme()
require_login()
sidebar_user_panel()

st.title("📊 My Dashboard")

username = st.session_state.username

results = run_query(
    "SELECT score, total, category, created_at FROM mock_results WHERE username=%s ORDER BY created_at",
    (username,),
    fetch=True,
) or []

chats = run_query(
    "SELECT id, question, answer, created_at FROM chat_history WHERE username=%s ORDER BY id DESC LIMIT 20",
    (username,),
    fetch=True,
) or []

# ---------------- METRICS ----------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Mock Tests Taken", str(len(results)))
with col2:
    avg_pct = (
        f"{sum((r[0] / r[1]) for r in results if r[1]) / max(1, sum(1 for r in results if r[1])) * 100:.0f}%" if results else "—"
    )
    metric_card("Average Score", avg_pct)
with col3:
    best_pct = (
        f"{max((r[0] / r[1]) for r in results if r[1]) * 100 if any(r[1] for r in results) else 0:.0f}%" if results else "—"
    )
    metric_card("Best Score", best_pct)
with col4:
    metric_card("Chat Messages", str(len(chats)))

st.write("")

# ---------------- SCORE HISTORY CHART ----------------
st.subheader("Score History")
if results:
    df = pd.DataFrame(results, columns=["score", "total", "category", "created_at"])
    df["percent"] = (df["score"] / df["total"].replace(0, pd.NA) * 100).round(1)
    df = df.set_index("created_at")
    st.line_chart(df["percent"])
else:
    st.caption("Take a mock test to start tracking your progress.")

st.divider()

# ---------------- CHAT HISTORY ----------------
st.subheader("Recent Chat History")
if chats:
    for cid, q, a, ts in chats:
        with st.expander(f"🕘 {q[:60]}{'...' if len(q) > 60 else ''}"):
            st.markdown(f"**You:** {q}")
            st.markdown(f"**Bot:** {a}")
            st.caption(str(ts))
else:
    st.caption("No chat history yet — head to the Chat page to get started.")
