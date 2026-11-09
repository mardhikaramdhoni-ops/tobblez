#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  JARVIS-CLI v1.2 — UI/UX Overhaul (FIXED VERSION)      ║
║  openai/gpt-oss-20b + Tavily + SQLite + Rich UI            ║
║  Author: Toblez | Status: STABLE                        ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

from groq import Groq
from tavily import TavilyClient

# ── Rich Imports ──────────────────────────────────────────
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.rule import Rule
from rich import box

# ── Initialization ────────────────────────────────────────
console = Console()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MODEL = "openai/gpt-oss-20b"
DB_PATH = "jarvis_memory.db"


# ══════════════════════════════════════════════════════════
#  SECTION 1: DATABASE (SQLite — Memory + Notes)
# ══════════════════════════════════════════════════════════

def init_db():
    """Bikin tabel memory & notes kalau belum ada."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    return conn


def save_memory(conn, role, content):
    """Simpan percakapan teks ke tabel memory."""
    if not content or not content.strip():
        return
    c = conn.cursor()
    c.execute(
        "INSERT INTO memory (role, content, timestamp) VALUES (?, ?, ?)",
        (role, content, datetime.now().isoformat())
    )
    conn.commit()


def get_recent_memory(conn, limit=6):
    """Ambil percakapan bersih terakhir dari memory."""
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM memory WHERE content IS NOT NULL AND content != '' ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


# ══════════════════════════════════════════════════════════
#  SECTION 2: TOOLS (Functions)
# ══════════════════════════════════════════════════════════

def search_web(query: str) -> str:
    """Tool: Mencari informasi dari internet via Tavily."""
    with console.status(
        f"[bold cyan]🌐  Searching the web for: \"{query}\"...",
        spinner="dots"
    ):
        try:
            response = tavily.search(query=query, max_results=3)
            results = []
            for r in response.get("results", []):
                results.append(f"**{r['title']}**\n{r['content']}\nSource: {r['url']}")
            return "\n\n---\n\n".join(results) if results else "Tidak ada hasil pencarian."
        except Exception as e:
            return f"Search error: {str(e)}"


def save_note(title: str, content: str) -> str:
    """Tool: Menyimpan catatan ke SQLite."""
    with console.status(f"[bold yellow]📝  Saving note: \"{title}\"...", spinner="line"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO notes (title, content, timestamp) VALUES (?, ?, ?)",
            (title, content, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return f"✅ Note '{title}' berhasil disimpan!"


def get_notes(query: str = "") -> str:
    """Tool: Membaca catatan dari SQLite."""
    with console.status("[bold green]📖  Reading notes from database...", spinner="aesthetic"):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        if query.strip():
            c.execute(
                "SELECT title, content, timestamp FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY id DESC LIMIT 5",
                (f"%{query}%", f"%{query}%")
            )
        else:
            c.execute("SELECT title, content, timestamp FROM notes ORDER BY id DESC LIMIT 5")
        rows = c.fetchall()
        conn.close()

        if not rows:
            return "📭 Tidak ada catatan ditemukan."

        results = []
        for title, content, ts in rows:
            date_str = ts[:10] if ts else "unknown"
            results.append(f"### 📌 {title}\n{content}\n*({date_str})*")
        return "\n\n---\n\n".join(results)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for real-time information using Tavily API.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Save a note to the local SQLite database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the note"},
                    "content": {"type": "string", "description": "Content of the note"}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_notes",
            "description": "Retrieve notes from local SQLite database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Optional search keyword"}
                },
                "required": []
            }
        }
    }
]

TOOL_MAP = {
    "search_web": search_web,
    "save_note": save_note,
    "get_notes": get_notes,
}


# ══════════════════════════════════════════════════════════
#  SECTION 3: UI DISPLAY FUNCTIONS
# ══════════════════════════════════════════════════════════

def show_header():
    header_text = Text()
    header_text.append("⚡ JARVIS", style="bold cyan")
    header_text.append(" CLI ", style="bold white")
    header_text.append("v1.2", style="bold magenta")
    header_text.append("\n")
    header_text.append("openai/gpt-oss-20b • Tavily Search • SQLite Memory • Rich UI", style="dim")

    console.print()
    console.print(Panel(
        header_text,
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(1, 4),
        title="[bold]🤖 AI ASSISTANT[/bold]",
        title_align="center"
    ))
    console.print()


def show_user_message(text: str):
    console.print(Panel(
        Text(text, style="white"),
        title="[bold green]👤 You[/bold green]",
        title_align="left",
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 2),
        width=min(console.width, 90)
    ))


def show_tool_result(tool_name: str, result_preview: str):
    preview = result_preview[:200] + "..." if len(result_preview) > 200 else result_preview
    console.print(Panel(
        Text(preview, style="dim"),
        title=f"[bold yellow]🔧 Tool Result: {tool_name}[/bold yellow]",
        title_align="left",
        border_style="yellow",
        box=box.SIMPLE,
        padding=(0, 1),
        width=min(console.width, 90)
    ))


def show_separator():
    console.print(Rule(style="dim"))


def show_footer():
    console.print()
    console.print(Panel(
        Text("👋 Session ended. Data saved to SQLite.", style="dim italic"),
        border_style="dim",
        box=box.SIMPLE,
        width=min(console.width, 60)
    ))
    console.print()


# ══════════════════════════════════════════════════════════
#  SECTION 4: CORE STREAMING & TOOL EXECUTION
# ══════════════════════════════════════════════════════════

def stream_ai_response(messages: list, conn) -> str:
    """Stream response & handle tool calling without looping bugs."""
    max_tool_rounds = 3

    for round_num in range(max_tool_rounds):
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=True
            )
        except Exception as e:
            console.print(f"\n[bold red]❌ Groq API Error:[/bold red] {e}\n")
            return ""

        full_content = ""
        tool_calls_accum = {}
        finish_reason = None

        # Live Display
        with Live(
            Panel(
                Markdown("🤖 *Thinking...*"),
                title="[bold cyan]🤖 Jarvis[/bold cyan]",
                title_align="left",
                border_style="cyan",
                box=box.ROUNDED,
                width=min(console.width, 90)
            ),
            console=console,
            refresh_per_second=10,
            transient=False
        ) as live:
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason or finish_reason

                if delta.content:
                    full_content += delta.content
                    live.update(
                        Panel(
                            Markdown(full_content),
                            title="[bold cyan]🤖 Jarvis[/bold cyan]",
                            title_align="left",
                            border_style="cyan",
                            box=box.ROUNDED,
                            width=min(console.width, 90)
                        )
                    )

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_accum:
                            tool_calls_accum[idx] = {"id": "", "name": "", "arguments": ""}
                        if tc.id:
                            tool_calls_accum[idx]["id"] += tc.id
                        if tc.function:
                            if tc.function.name:
                                tool_calls_accum[idx]["name"] += tc.function.name
                            if tc.function.arguments:
                                tool_calls_accum[idx]["arguments"] += tc.function.arguments

        # If Tool Call Needed
        if tool_calls_accum and finish_reason == "tool_calls":
            formatted_tool_calls = []
            for tc in tool_calls_accum.values():
                formatted_tool_calls.append({
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"]
                    }
                })

            messages.append({
                "role": "assistant",
                "content": full_content if full_content.strip() else None,
                "tool_calls": formatted_tool_calls
            })

            # Execute Tools
            for tc in tool_calls_accum.values():
                func_name = tc["name"]
                try:
                    func_args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except Exception:
                    func_args = {}

                console.print()
                if func_name in TOOL_MAP:
                    result = TOOL_MAP[func_name](**func_args)
                else:
                    result = f"❌ Unknown tool: {func_name}"

                show_tool_result(func_name, str(result))
                console.print()

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result)
                })

            continue  # Loop lagi buat dapet jawaban akhir

        else:
            # ── FIXED: Simpan ke SQLite DAN Tambahkan ke 'messages' memory ──
            if full_content.strip():
                save_memory(conn, "assistant", full_content)
                messages.append({"role": "assistant", "content": full_content}) # <--- INI KUNCI FIX-NYA!
            return full_content

    return full_content

# ══════════════════════════════════════════════════════════
#  SECTION 5: MAIN LOOP
# ══════════════════════════════════════════════════════════

def main():
    conn = init_db()
    show_header()

    system_prompt = (
        "You are JARVIS, a highly capable AI assistant running in a CLI terminal. "
        "You have access to tools: web search (Tavily), note saving, and note retrieval. "
        "Respond in the same language the user uses. "
        "Use Markdown formatting for clarity. "
        "Be concise, direct, and helpful. "
        "When user asks to save something, use save_note. "
        "When user asks about saved notes, use get_notes."
    )

    messages = [{"role": "system", "content": system_prompt}]

    recent = get_recent_memory(conn, limit=6)
    if recent:
        console.print(f"[dim]📂 Loaded {len(recent)} recent messages from memory.[/dim]\n")
        messages.extend(recent)

    while True:
        try:
            user_input = console.input("[bold green]❯ [/bold green]").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "bye", "keluar"):
                show_footer()
                break

            if user_input.lower() == "/clear":
                messages = [{"role": "system", "content": system_prompt}]
                c = conn.cursor()
                c.execute("DELETE FROM memory")
                conn.commit()
                console.clear()
                show_header()
                console.print("[dim]🧹 Memory context & database cleared.[/dim]\n")
                continue

            show_user_message(user_input)
            console.print()
            save_memory(conn, "user", user_input)
            messages.append({"role": "user", "content": user_input})

            stream_ai_response(messages, conn)
            show_separator()

        except KeyboardInterrupt:
            show_footer()
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ Error:[/bold red] {str(e)}\n")


if __name__ == "__main__":
    main()