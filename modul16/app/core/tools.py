import re
from app.core.knowledge_base import KnowledgeBase

kb = KnowledgeBase()


async def search_knowledge_base(query: str) -> str:
    """Cari informasi internal di knowledge base."""
    return await kb.search(query)


async def calculate(expression: str) -> str:
    """Kalkulator aman dengan filter regex."""
    if not re.match(r"^[\d\s\+\-\*\/\.\(\)]+$", expression):
        return "Error: Ekspresi ditolak karena mengandung karakter berbahaya/tidak valid."
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error perhitungan: {str(e)}"


TOOLS_REGISTRY = {
    "search_knowledge_base": search_knowledge_base,
    "calculate": calculate,
}