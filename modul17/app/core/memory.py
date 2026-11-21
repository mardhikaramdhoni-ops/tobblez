import sqlite3
import os
import asyncio


class AgentMemory:
    def __init__(self, db_path: str = "db_data/tobblez_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    async def save_message(self, user_id: str, role: str, content: str):
        def _save():
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )
            conn.commit()
            conn.close()

        await asyncio.to_thread(_save)

    async def get_history(self, user_id: str, limit: int = 10) -> list[dict]:
        def _get():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT role, content FROM chat_history "
                "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
            conn.close()
            return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

        return await asyncio.to_thread(_get)

    async def clear_history(self, user_id: str):
        def _clear():
            conn = sqlite3.connect(self.db_path)
            conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()

        await asyncio.to_thread(_clear)