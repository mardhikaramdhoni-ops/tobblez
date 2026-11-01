# modul11_sqlite_memory.py
# Modul 11 — LLM Chat CLI dengan SQLite Memory
# By: Tobblez 🚀

import sqlite3
import os
from dotenv import load_dotenv
from groq import Groq
from colorama import init, Fore, Style

init(autoreset=True)
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = 'openai/gpt-oss-20b'
DB_NAME = "chat_history.db"


def init_db():
    """Bikin database dan tabel messages kalau belum ada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_message(role: str, content: str):
    """Simpan satu pesan ke tabel messages."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (role, content) VALUES (?, ?)",
        (role, content)
    )
    conn.commit()
    conn.close()


def get_all_messages() -> list:
    """Ambil semua pesan dari DB sebagai list of dict."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages")
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in rows]


def tanya_llm_with_memory(prompt: str) -> str:
    """Kirim prompt ke LLM dengan full history dari DB."""
    save_message("user", prompt)
    messages = get_all_messages()

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"⚠️ Error dari LLM: {e}"

    save_message("assistant", answer)
    return answer


if __name__ == "__main__":
    init_db()

    print(Fore.GREEN + "=" * 50)
    print("  🤖 TOBBLEZ CHAT BOT — SQLite Memory Edition")
    print("=" * 50 + Style.RESET_ALL)
    print(Fore.YELLOW + "  Ketik 'keluar' → stop program")
    print("  Ketik 'hapus'  → reset semua memory chat")
    print("=" * 50 + Style.RESET_ALL)

    while True:
        user_input = input(Fore.CYAN + "\nLu: " + Style.RESET_ALL).strip()

        if user_input == "":
            continue
        elif user_input.lower() == "keluar":
            print(Fore.YELLOW + "\nBye bro! Memory lu aman di DB. 👋" + Style.RESET_ALL)
            break
        elif user_input.lower() == "hapus":
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages")
            conn.commit()
            conn.close()
            print(Fore.RED + "\n🗑️  Semua memory chat berhasil dihapus! Fresh start!" + Style.RESET_ALL)
        else:
            answer = tanya_llm_with_memory(user_input)
            print(Fore.GREEN + f"\nLLM: {answer}" + Style.RESET_ALL)