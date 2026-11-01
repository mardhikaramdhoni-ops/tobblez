import os
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


def tanya_llm(prompt: str) -> str:
    """
    Fungsi untuk mengirim prompt pertanyaan user ke LLM via Groq API
    dan mengembalikan jawaban teksnya.
    """
    try:
    
        api_key = os.getenv("GROQ_API_KEY")


        if not api_key:
            return "❌ Error: GROQ_API_KEY tidak ditemukan di file .env!"
        
        client = Groq(api_key=api_key)


        response = client.chat.completions.create(
            model='openai/gpt-oss-20b',
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        answer = response.choices[0].message.content
        return answer

    except Exception as e:

        return f"❌ Error terjadi: {e}"


# --- MAIN BLOCK ---
if __name__ == "__main__":
    print("Halo! Gw LLM Assistant lu. Ketik 'keluar' buat stop.\n")

    while True:
        \
        user_input = input("Lu: ").strip()


        if user_input.lower() == "keluar":
            print("Dadah! Semoga harimu menyenangkan.")
            break


        if not user_input:
            continue


        jawaban = tanya_llm(user_input)
        print(f"LLM: {jawaban}\n")