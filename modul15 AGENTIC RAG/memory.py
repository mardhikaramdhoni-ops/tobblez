import sqlite3
from typing import List, Dict

class ConversationMemory:
    def __init__(self, db_path="chat_history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Bikin tabel conversations kalau belum ada"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add(self, role: str, content: str):
        """Simpan chat ke database (role: 'user' / 'assistant')"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (role, content) VALUES (?, ?)",
                (role, content)
            )
            conn.commit()

    def get_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """
        Ambil histori percakapan terakhir.
        Output-nya berbentuk list of dict yang siap dikirim ke LLM:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Ambil n data terbaru (dibalik urutannya dari terlama ke terbaru)
            cursor.execute(
                "SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            
            # Revers biar urutannya kronologis (dari chat lama -> baru)
            rows.reverse()
            
            return [{"role": r[0], "content": r[1]} for r in rows]

    def clear(self):
        """Hapus semua memori percakapan"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations")
            conn.commit()
            print("🧹 Memory percakapan berhasil di-reset!")