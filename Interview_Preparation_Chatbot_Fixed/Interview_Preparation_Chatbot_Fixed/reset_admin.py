
import getpass
import bcrypt
import mysql.connector

password = getpass.getpass("Enter new admin password: ")

if len(password) < 6:
    print("Password must be at least 6 characters.")
    raise SystemExit

if len(password.encode("utf-8")) > 72:
    print("Password is too long. Use at most 72 UTF-8 bytes.")
    raise SystemExit

confirm = getpass.getpass("Confirm new admin password: ")

if password != confirm:
    print("Passwords do not match.")
    raise SystemExit

password_hash = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

connection = None
cursor = None

try:
    mysql_password = getpass.getpass("Enter MySQL root password: ")

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=mysql_password,
        database="chatbot_db",
        connection_timeout=10
    )

    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE username = %s AND role = %s",
        (password_hash, "admin", "admin")
    )

    if cursor.rowcount == 1:
        connection.commit()
        print("Admin password reset successfully!")
    else:
        connection.rollback()
        print("Admin account not found or not updated.")

except mysql.connector.Error as error:
    if connection is not None:
        connection.rollback()

    print(f"Database error: {error}")

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()

