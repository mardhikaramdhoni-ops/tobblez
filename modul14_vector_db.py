# modul14_vector_db.py
# Modul 14 - RAG dengan ChromaDB Vector Database
# Toblez - LLM Engineering Journey

import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"  # Biar warning symlink Windows gak muncul

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from groq import Groq
from colorama import init, Fore, Style

# ========================
# A. SETUP & IMPORT
# ========================
init(autoreset=True)
load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ========================
# B. INISIALISASI CHROMADB (PERSISTENT) + EMBEDDING
# ========================
# Data disimpan di folder ./chroma_db (gak ilang pas script mati)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Embedding function pake sentence-transformers (model yang sama kayak Modul 13)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Nama collection baru (_v2) biar gak konflik sama collection lama yang pake embedding "default"
collection = chroma_client.get_or_create_collection(
    name="tobblez_knowledge_v2",
    embedding_function=embedding_func,
)


# ========================
# C. FUNGSI: ADD DOCUMENTS
# ========================
def add_documents_to_vector_db():
    """
    Cek isi collection. Kalau kosong, populate data.
    Kalau udah ada isinya, skip (biar gak duplikat).
    """
    if collection.count() > 0:
        print(
            f"{Fore.YELLOW}[INFO] Collection 'tobblez_knowledge_v2' udah ada "
            f"{collection.count()} dokumen. Skip adding.{Style.RESET_ALL}"
        )
        return

    documents = [
        "Toblez adalah mahasiswa yang sedang belajar Software Engineering dan LLM Engineering secara intensif.",
        "Modul 10 membahas pembuatan LLM Chat CLI menggunakan Groq API dengan model llama3.",
        "Modul 11 membahas LLM Chat dengan SQLite Persistent Memory menggunakan file chat_history.db.",
        "Modul 12 membahas LLM Agent menggunakan teknik Tool Calling atau Function Calling.",
        "Modul 13 membahas RAG from scratch menggunakan sentence-transformers dan numpy cosine similarity.",
        "Modul 14 membahas penggunaan ChromaDB sebagai vector database untuk sistem RAG yang lebih scalable.",
        "ChromaDB adalah vector database open-source yang bisa menyimpan, meng-embed, dan mencari teks secara efisien.",
        "Groq API adalah layanan inference LLM yang sangat cepat, mendukung model seperti llama3-8b-8192 dan llama3-70b-8192.",
        "Tech stack yang digunakan Toblez meliputi Python 3.x, VS Code, Git, GitHub, Groq API, SQLite, dan ChromaDB.",
        "File .env digunakan untuk menyimpan API key secara aman dan tidak boleh di-push ke GitHub.",
    ]

    ids = [f"doc{i+1}" for i in range(len(documents))]

    # ChromaDB otomatis nge-embed dokumen pake embedding_func yang udah di-set di collection
    collection.add(
        documents=documents,
        ids=ids,
    )

    print(
        f"{Fore.GREEN}[SUCCESS] {len(documents)} dokumen berhasil "
        f"ditambahkan & di-embed ke ChromaDB!{Style.RESET_ALL}"
    )


# ========================
# D. FUNGSI: QUERY VECTOR DB
# ========================
def query_vector_db(query_text: str, n_results: int = 4) -> str:
    """
    Cari dokumen paling relevan dari ChromaDB berdasarkan query.
    Return gabungan teks chunk yang paling mirip.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
    )

    # Format: list of list -> [[doc1, doc2, ...]]
    if results["documents"] and results["documents"][0]:
        chunks = results["documents"][0]
        return "\n".join(chunks)

    return "Tidak ada dokumen yang relevan ditemukan."


# ========================
# E. FUNGSI: TANYA AGENT (RAG + GROQ)
# ========================
def tanya_agent_vector_rag(query: str) -> str:
    """
    1. Ambil konteks relevan dari ChromaDB.
    2. Rakit system prompt dengan konteks tersebut.
    3. Kirim ke Groq LLM.
    4. Return jawaban.
    """
    konteks = query_vector_db(query, n_results=4)

    system_prompt = f"""Kamu adalah asisten AI bernama Toblez Assistant.
Tugas kamu adalah menjawab pertanyaan user berdasarkan KONTEKS yang diberikan.

ATURAN:
- Jawab HANYA berdasarkan konteks yang tersedia.
- Jika konteks tidak mengandung informasi yang relevan, katakan:
  "Maaf, saya tidak memiliki informasi tersebut di knowledge base saya."
- Jawab dalam Bahasa Indonesia yang santai dan jelas.

KONTEKS:
{konteks}"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",  # model aktif di Groq (openai/gpt-oss-120b udah deprecated)
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0,  # Deterministic buat RAG
    )

    return response.choices[0].message.content


# ========================
# F. MAIN BLOCK
# ========================
if __name__ == "__main__":
    print(f"\n{Fore.CYAN}{'=' * 55}")
    print("  TOBLEZ RAG + ChromaDB Vector Database (Modul 14)")
    print(f"{'=' * 55}{Style.RESET_ALL}\n")

    add_documents_to_vector_db()

    print(f"\n{Fore.WHITE}Ketik pertanyaan lu, atau 'exit' buat keluar.{Style.RESET_ALL}")

    while True:
        user_input = input(f"\n{Fore.GREEN}🧑 Lu: {Style.RESET_ALL}").strip()

        if user_input.lower() in ["exit", "quit", "keluar"]:
            print(f"\n{Fore.YELLOW}Bye bro! Data lu aman tersimpan di ./chroma_db/ 👋{Style.RESET_ALL}")
            break

        if not user_input:
            continue

        # Tampilkan konteks yang diambil (buat debug)
        konteks_debug = query_vector_db(user_input, n_results=2)
        print(f"\n{Fore.MAGENTA}[📚 Konteks dari ChromaDB]:{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{konteks_debug}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}[🤖 Agent sedang mikir...]{Style.RESET_ALL}")
        jawaban = tanya_agent_vector_rag(user_input)
        print(f"\n{Fore.WHITE}🤖 Agent: {jawaban}{Style.RESET_ALL}")