import chromadb
from chromadb.utils import embedding_functions
import asyncio
import os


class KnowledgeBase:
    def __init__(self, persist_dir: str = "chroma_data"):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)

        # 💡 PERBAIKAN: Gunakan SentenceTransformerEmbeddingFunction
        # Ini bakal otomatis make model 'all-MiniLM-L6-v2' yang udah ter-cache di laptop lu dari Modul 14/15
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name="tobblez_knowledge",
            embedding_function=self.ef
        )
        self._seed_default_data()

    def _seed_default_data(self):
        """Isi data awal otomatis kalau database masih kosong."""
        if self.collection.count() == 0:
            docs = [
                "Tobblez AI Service adalah platform AI Agent buatan Toblez yang menggunakan arsitektur ReAct, FastAPI, ChromaDB, dan Groq Llama-3.3-70B.",
                "Kebijakan keamanan Tobblez: Kalkulator menggunakan filter Regex ketat untuk mencegah Arbitrary Code Execution pada fungsi eval().",
                "FastAPI dipilih untuk Modul 16 karena mendukung Asynchronous I/O (ASGI), validasi otomatis dengan Pydantic, dan mendukung Server-Sent Events (SSE) streaming."
            ]
            ids = ["doc_1", "doc_2", "doc_3"]
            self.collection.add(documents=docs, ids=ids)

    async def search(self, query: str, n_results: int = 2) -> str:
        def _search():
            results = self.collection.query(query_texts=[query], n_results=n_results)
            if results["documents"] and results["documents"][0]:
                return "\n---\n".join(results["documents"][0])
            return "Tidak ada informasi relevan ditemukan di knowledge base."

        return await asyncio.to_thread(_search)