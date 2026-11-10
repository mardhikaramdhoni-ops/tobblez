import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
import numpy as np

# ---------- A. Setup ----------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "openai/gpt-oss-120b"  

# ---------- B. Load model embedding & knowledge base ----------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def load_chunks(file_name: str = "knowledge_base.txt") -> list:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return [c.strip() for c in text.split("\n\n") if c.strip()]

chunks = load_chunks() 

# ---------- C. Retrieve ----------
def get_most_relevant_chunk(query: str, chunks: list) -> str:
    query_vec = embedder.encode(query)    # shape: (384,)
    chunk_vecs = embedder.encode(chunks)  # shape: (jumlah_chunk, 384)

    # Cosine similarity: (A . B) / (||A|| * ||B||)
    similarities = np.dot(chunk_vecs, query_vec) / (
        np.linalg.norm(chunk_vecs, axis=1) * np.linalg.norm(query_vec)
    )

    best_idx = int(np.argmax(similarities))
    judul = chunks[best_idx].splitlines()[0]
    print(f"[DEBUG] Chunk terpilih: {judul} | skor: {similarities[best_idx]:.3f}")
    return chunks[best_idx]

# ---------- D. Augment + Generate ----------
def tanya_agent_rag(query: str) -> str:
    konteks_relevan = get_most_relevant_chunk(query, chunks)

    system_prompt = f"""Lu adalah Customer Service Tobblez Tech.
Jawab pertanyaan user HANYA berdasarkan konteks pengetahuan berikut.
Jika tidak ada di konteks, katakan dengan sopan bahwa lu tidak tahu.

KONTEKS:
{konteks_relevan}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0,  # biar jawabannya konsisten & faktual
    )
    return response.choices[0].message.content

# ---------- Main loop ----------
if __name__ == "__main__":
    print("RAG Agent Tobblez Tech siap. Ketik 'exit' buat keluar.\n")
    while True:
        query = input("Lu: ").strip()
        if query.lower() in ("exit", "quit"):
            break
        if not query:
            continue
        print(f"Agent: {tanya_agent_rag(query)}\n")