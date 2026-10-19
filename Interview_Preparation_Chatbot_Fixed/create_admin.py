"""Run once from the terminal to create or promote an admin account.

Usage:
    python create_admin.py

This does NOT go through Streamlit — it connects directly so you can
bootstrap your first admin before the app is even running.
"""
import getpass
import bcrypt
import mysql.connector
try:
    import tomllib
except ImportError:
    import tomli as tomllib

with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomllib.load(f)["db"]

conn = mysql.connector.connect(**secrets)
cursor = conn.cursor()

username = input("Admin username: ").strip()
if not username:
    raise SystemExit("Username cannot be empty.")
cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
existing = cursor.fetchone()

if existing:
    cursor.execute("UPDATE users SET role='admin' WHERE username=%s", (username,))
    conn.commit()
    print(f"Promoted existing user '{username}' to admin.")
else:
    password = getpass.getpass("New admin password: ")
    if len(password) < 6:
        raise SystemExit("Password must be at least 6 characters.")
    if len(password.encode("utf-8")) > 72:
        raise SystemExit("Password must be at most 72 UTF-8 bytes.")
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'admin')",
        (username, hashed),
    )
    conn.commit()
    print(f"Created new admin user '{username}'.")

cursor.close()
conn.close()
