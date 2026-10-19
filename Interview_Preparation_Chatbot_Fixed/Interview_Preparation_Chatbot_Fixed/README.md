# Interview Preparation Chatbot

Streamlit multipage app with login/signup, interview Q&A chat, resume skill prompts,
mock tests, score dashboard, and an admin question bank.

## Project structure

```text
Interview_Preparation_Chatbot_Fixed/
├── Home.py
├── create_admin.py
├── schema.sql
├── requirements.txt
├── pages/
│   ├── 1_💬_Chat.py
│   ├── 2_📝_Mock_Test.py
│   ├── 3_📊_Dashboard.py
│   └── 4_🛠️_Admin.py
├── utils/
│   ├── __init__.py
│   ├── auth.py
│   ├── db.py
│   └── styles.py
└── .streamlit/
    ├── config.toml
    ├── secrets.toml.example
    └── secrets.toml  # create this yourself; do not share/commit it
```

## Run on Windows

1. Extract the ZIP and open the extracted project folder in VS Code.
2. Open Terminal in that folder and create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   If PowerShell blocks activation, use Command Prompt and run:
   `.venv\Scripts\activate.bat`

3. Make sure MySQL Server is running. In MySQL Workbench, open `schema.sql`
   and execute it, or run `mysql -u root -p < schema.sql` from a terminal
   where the MySQL client is on PATH.

4. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
   Edit `secrets.toml` and set the correct MySQL host, username, password,
   and database. Example:

   ```toml
   [db]
   host = "localhost"
   user = "root"
   password = "YOUR_REAL_MYSQL_PASSWORD"
   database = "chatbot_db"
   ```

5. Start the app:

   ```powershell
   streamlit run Home.py
   ```

6. Create a regular account in the app, then promote it to admin if needed:

   ```powershell
   python create_admin.py
   ```

   Enter the same username you registered. The script promotes that account
   to admin. To create a new admin, enter a username that does not exist.

## Notes

- The voice-input feature needs a working microphone and PyAudio/PortAudio.
  If microphone dependencies cannot be installed, remove `SpeechRecognition`
  and the voice feature or install PyAudio separately for your platform.
- Similarity scoring is a simple word-overlap baseline, not an evaluation of
  meaning. It may score valid answers imperfectly.
- Do not commit `.streamlit/secrets.toml` or share real database credentials.
