"""Authentication: password hashing, signup/login, and page access guards."""
import bcrypt
import streamlit as st
from utils.db import run_query


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError, AttributeError):
        return False


def username_exists(username: str) -> bool:
    row = run_query("SELECT id FROM users WHERE username=%s", (username,), fetchone=True)
    return row is not None


def signup_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    if not username or not password:
        return False, "Please fill in all fields."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if len(password.encode("utf-8")) > 72:
        return False, "Password is too long; use at most 72 UTF-8 bytes."
    if username_exists(username):
        return False, "That username is already taken."

    result = run_query(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
        (username, hash_password(password), "user"),
    )
    if result is not True:
        return False, "Account could not be created. Check the database connection."
    return True, "Account created successfully. You can log in now."


def login_user(username: str, password: str) -> tuple[bool, str, str | None]:
    if not username or not password:
        return False, "Enter your username and password.", None
    row = run_query(
        "SELECT password_hash, role FROM users WHERE username=%s",
        (username.strip(),),
        fetchone=True,
    )
    if not row or not verify_password(password, row[0]):
        return False, "Invalid username or password.", None
    return True, "Login successful.", row[1]


def require_login():
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to continue.")
        st.page_link("Home.py", label="Go to Login", icon="🔑")
        st.stop()


def require_admin():
    require_login()
    if st.session_state.get("role") != "admin":
        st.error("You don't have permission to view this page.")
        st.stop()
