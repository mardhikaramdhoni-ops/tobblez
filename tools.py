import math
import platform
import os
from datetime import datetime
from config import logger
from tavily import TavilyClient
from config import TAVILY_API_KEY
# =====================================================
# 1. TOOL DEFINITIONS (Skema yang dikirim ke Groq)
# =====================================================
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Dapatkan tanggal dan waktu saat ini. Gunakan saat user bertanya tentang jam, hari, atau tanggal.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Hitung ekspresi matematika. Gunakan untuk semua perhitungan angka.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Ekspresi matematika, misal '25 * 4 + 10' atau 'math.sqrt(144)'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": "Simpan catatan penting ke memori database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Judul singkat catatan"},
                    "content": {"type": "string", "description": "Isi lengkap catatan"}
                },
                "required": ["title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_todo",
            "description": "Tambah tugas baru ke todo list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Deskripsi tugas yang harus dikerjakan"}
                },
                "required": ["task"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_todos",
            "description": "Lihat daftar semua tugas (todo list) yang pending.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Dapatkan informasi sistem komputer (OS, Python Version, CPU).",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },

    # =========================================================
    # 🌐 FITUR BARU v1.1 — Web Search Tool
    # =========================================================
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Cari informasi real-time dari internet menggunakan DuckDuckGo. "
                "Gunakan tool ini saat user bertanya tentang berita terkini, harga saat ini, "
                "cuaca, event terbaru, atau informasi yang membutuhkan akses internet. "
                "JANGAN gunakan untuk pengetahuan umum yang sudah kamu ketahui."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Kata kunci pencarian. Buat spesifik dan ringkas."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Jumlah maksimal hasil pencarian (default: 3, max: 5)."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# =====================================================
# 2. TOOL EXECUTOR (Eksekusi fungsi Python beneran)
# =====================================================
def execute_tool(tool_name: str, arguments: dict, memory) -> str:
    """Jalankan fungsi Python berdasarkan nama tool yang diminta LLM."""
    try:
        if tool_name == "get_current_time":
            now = datetime.now()
            return now.strftime("%A, %d %B %Y — %H:%M:%S")

        elif tool_name == "calculate":
            expression = arguments.get("expression", "")
            try:
                safe_dict = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
                safe_dict.update({"abs": abs, "round": round, "min": min, "max": max})
                result = eval(expression, {"__builtins__": {}}, safe_dict)
                return f"✅ Hasil dari {expression} = {result}"
            except ZeroDivisionError:
                return f"❌ Gagal: Pembagian dengan nol! ({expression})"
            except (SyntaxError, TypeError):
                return f"❌ Gagal: Syntax ekspresi salah — '{expression}'"
            except NameError as e:
                return f"❌ Gagal: Fungsi/variabel tidak dikenal — {e}"
            except ValueError as e:
                return f"❌ Gagal: Nilai tidak valid — {e}"
            except OverflowError:
                return f"❌ Gagal: Angka terlalu besar!"
            except Exception as e:
                return f"❌ Gagal menghitung: {e}"

        elif tool_name == "save_note":
            title = arguments.get("title", "Untitled")
            content = arguments.get("content", "")
            return memory.save_note(title, content)

        elif tool_name == "add_todo":
            task = arguments.get("task", "")
            return memory.add_todo(task)

        elif tool_name == "get_todos":
            return memory.get_todos()

        elif tool_name == "get_system_info":
            info = [
                f"OS: {platform.system()} {platform.release()}",
                f"Architecture: {platform.machine()}",
                f"Python Version: {platform.python_version()}",
                f"Hostname: {platform.node()}",
                f"Current Dir: {os.getcwd()}"
            ]
            return "\n".join(info)

        # 🌐 FITUR BARU v1.1
        elif tool_name == "web_search":
            query = arguments.get("query", "")
            max_results = arguments.get("max_results", 3)
            return web_search(query=query, max_results=max_results)

        else:
            return f"Error: Tool '{tool_name}' tidak ditemukan."

    except Exception as e:
        logger.error(f"Error eksekusi tool [{tool_name}]: {e}")
        return f"Gagal menjalankan {tool_name}: {str(e)}"


# =========================================================
# 🌐 FITUR v1.1 — Web Search Implementation (Tavily API)
# =========================================================
def web_search(query: str, max_results: int = 3) -> str:
    """
    Mencari informasi real-time dari internet via Tavily API.
    """
    try:
        if not TAVILY_API_KEY:
            return "⚠️ Error: TAVILY_API_KEY belum di-set di file .env!"

        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, max_results=max_results)

        results = response.get("results", [])

        if not results:
            return f"Tidak ditemukan hasil pencarian untuk '{query}'."

        output = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No Title")
            url = r.get("url", "No URL")
            content = r.get("content", "No content available.")
            output.append(
                f"[{i}] {title}\n"
                f"    🔗 {url}\n"
                f"    📝 {content}"
            )

        logger.info(f"Tavily Search berhasil: '{query}' → {len(results)} hasil")
        return "\n\n".join(output)

    except Exception as e:
        logger.error(f"Tavily Search error: {e}")
        return f"⚠️ Gagal melakukan pencarian web: {str(e)}"