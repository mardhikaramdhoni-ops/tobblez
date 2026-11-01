import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load variabel dari file .env di awal script
load_dotenv()


def tanya_llm(prompt: str) -> str:
    """
    Fungsi untuk mengirim prompt pertanyaan user ke LLM via Groq API
    dan mengembalikan jawaban teksnya.
    """
    try:
        # Ambil API key dari environment variable
        api_key = os.getenv("GROQ_API_KEY")

        # Validation: Pastikan API Key ada
        if not api_key:
            return "❌ Error: GROQ_API_KEY tidak ditemukan di file .env!"

        # Inisialisasi client Groq dengan API key
        client = Groq(api_key=api_key)

        # Kirim request ke Groq Chat Completion API
        response = client.chat.completions.create(
            model='openai/gpt-oss-20b',
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # GALI RESPONSE (Ini yang diminta dosen):
        # Struktur Object Groq: response -> choices (list) -> message -> content
        answer = response.choices[0].message.content
        return answer

    except Exception as e:
        # Error handling jika koneksi putus, API key salah, dll
        return f"❌ Error terjadi: {e}"


# --- MAIN BLOCK ---
if __name__ == "__main__":
    print("Halo! Gw LLM Assistant lu. Ketik 'keluar' buat stop.\n")

    while True:
        # Minta input pertanyaan dari user
        user_input = input("Lu: ").strip()

        # Fitur untuk keluar dari program
        if user_input.lower() == "keluar":
            print("Dadah! Semoga harimu menyenangkan.")
            break

        # Jika user cuma pencet enter tanpa ngetik apa-apa, skip
        if not user_input:
            continue

        # Panggil fungsi tanya_llm dan cetak jalannya
        jawaban = tanya_llm(user_input)
        print(f"LLM: {jawaban}\n")