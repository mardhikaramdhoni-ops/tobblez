import os
from groq import Groq

def query_llm_agent(user_prompt: str) -> str:
    """
    Fungsi ini memanggil Groq API untuk memproses prompt user.
    """
    api_key = os.environ.get("GROQ_API_KEY", "dummy_key")
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Lu adalah AI Assistant."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )
    
    # Ambil teks jawaban dari struktur object Groq
    return response.choices[0].message.content