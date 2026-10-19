"""Centralized MySQL connection and query helpers."""
import mysql.connector
import streamlit as st


@st.cache_resource(show_spinner=False)
def get_connection():
    """Return the shared MySQL connection."""
    try:
        return mysql.connector.connect(
            host=st.secrets["db"]["host"],
            user=st.secrets["db"]["user"],
            password=st.secrets["db"]["password"],
            database=st.secrets["db"].get("database", "chatbot_db"),
            autocommit=False,
            connection_timeout=10,
        )
    except (KeyError, FileNotFoundError):
        st.error(
            "Database credentials are missing. Copy "
            "`.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` "
            "and enter your MySQL details."
        )
        st.stop()
    except mysql.connector.Error as exc:
        st.error(f"Could not connect to MySQL: {exc}")
        st.stop()


def run_query(query, params=None, fetch=False, fetchone=False):
    """Execute a parameterized query and return fetched rows when requested."""
    conn = get_connection()
    cursor = None
    try:
        if not conn.is_connected():
            conn.reconnect(attempts=3, delay=1)
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if fetchone:
            return cursor.fetchone()
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return True
    except mysql.connector.Error as exc:
        try:
            conn.rollback()
        except mysql.connector.Error:
            pass
        st.error(f"Database error: {exc}")
        return None
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except mysql.connector.Error:
                pass
