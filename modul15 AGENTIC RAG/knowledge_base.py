import os
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

class KnowledgeBase:
    def __init__(self, db_path="./chroma_db", collection_name="tobblez_knowledge_v2"):
        # 1. Inisialisasi Persistent Client (biar data nggak ilang pas restart)
        self.client = PersistentClient(path=db_path)
        
        # 2. Setup Embedding Function (pake model yang sama kayak modul 14)
        self.embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        # 3. Get atau Create Collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def ingest(self, file_path: str):
        """Baca file, chunking sederhana, dan simpan ke ChromaDB"""
        if not os.path.exists(file_path):
            print(f"❌ File {file_path} gak ketemu, bro!")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Chunking sederhana per paragraf (dipisah pake double newline)
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        
        ids = [f"id_{i}" for i in range(len(paragraphs))]
        
        # Simpan ke ChromaDB
        self.collection.upsert(
            documents=paragraphs,
            ids=ids
        )
        print(f"✅ Berhasil ingest {len(paragraphs)} paragraf ke Knowledge Base.")

    def search(self, query: str, n_results: int = 3):
        """Cari potongan teks yang relevan berdasarkan query"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Balikin dalam bentuk list of string biar gampang dibaca Agent
        return results['documents'][0] if results['documents'] else []