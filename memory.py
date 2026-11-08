import sqlite3
from config import DB_PATH, logger

class Memory:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row  # Biar data bisa diakses pake nama kolom
        self._create_tables()
        self.messages = []  # Memori sementara buat session ini
        logger.info("Memory system initialized")

    def _create_tables(self):
        cursor = self.conn.cursor()
        # Bikin tabel chat, notes, dan todos kalo belum ada
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                status TEXT DEFAULT 'pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        if role in ["user", "assistant"]:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
            self.conn.commit()

    def get_messages(self):
        return self.messages

    # Fitur Notes
    def save_note(self, title, content):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        self.conn.commit()
        return f"Note '{title}' berhasil disimpan, Sir!"

    # Fitur Todos
    def add_todo(self, task):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO todos (task) VALUES (?)", (task,))
        self.conn.commit()
        return f"Tugas '{task}' dicatat, Sir!"

    def get_todos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, task, status FROM todos WHERE status = 'pending'")
        rows = cursor.fetchall()
        if not rows: return "Tidak ada tugas pending, Sir."
        return "\n".join([f"[{r['id']}] {r['task']}" for r in rows])

    def close(self):
        self.conn.close()