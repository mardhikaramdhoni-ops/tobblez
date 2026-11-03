import os
import json
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_current_time():
    """Mengembalikan tanggal dan waktu saat ini."""
    sekarang = datetime.now()
    return sekarang.strftime("%Y-%m-%d %H:%M:%S")

def hitung_matematika(ekspresi: str):
    """Menghitung ekspresi matematika dari string."""
    try:
        # Keamanan sederhana: cuma boleh angka dan simbol matematika
        karakter_valid = "0123456789+-*/(). "
        if not all(c in karakter_valid for c in ekspresi):
            return "Error: Ekspresi mengandung karakter yang tidak diizinkan!"
            
        hasil = eval(ekspresi)
        return str(hasil)
    except Exception as e:
        return f"Error: Tidak bisa menghitung '{ekspresi}'. Detail: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Gunakan fungsi ini untuk mendapatkan tanggal dan waktu saat ini.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hitung_matematika",
            "description": "Gunakan fungsi ini untuk menghitung ekspresi matematika.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ekspresi": {
                        "type": "string",
                        "description": "Ekspresi matematika, contoh: '25 * 4 + 10'",
                    }
                },
                "required": ["ekspresi"],
            },
        },
    },
]

def jalankan_agent(prompt: str):
    print(f"\n[USER]: {prompt}")
    
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model='openai/gpt-oss-20b',
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    if response_message.tool_calls:
        print("🤖 Agent: 'Gue butuh panggil tool nih!'")

        messages.append(response_message)
        
        tool_call = response_message.tool_calls[0]
        nama_fungsi = tool_call.function.name
        argumen = json.loads(tool_call.function.arguments)
        
        print(f"🛠️ Tool dipanggil: {nama_fungsi}({argumen})")
        
        hasil_tool = ""
        if nama_fungsi == "get_current_time":
            hasil_tool = get_current_time()
        elif nama_fungsi == "hitung_matematika":
            hasil_tool = hitung_matematika(argumen.get("ekspresi", ""))
            
        print(f"📊 Hasil Tool: {hasil_tool}")
        
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(hasil_tool)
        })
        
        final_response = client.chat.completions.create(
            model='openai/gpt-oss-20b',
            messages=messages
        )
        
        return final_response.choices[0].message.content
    else:
        return response_message.content
    
if __name__ == "__main__":
    print("=== TEST AGENT TOOL CALLING ===")
    
    jawaban1 = jalankan_agent("Siapa presiden pertama Indonesia?")
    print(f"[AGENT]: {jawaban1}\n")
    
    jawaban2 = jalankan_agent("Jam berapa sekarang?")
    print(f"[AGENT]: {jawaban2}\n")
    
    jawaban3 = jalankan_agent("Berapa hasil dari 5432 dikali 128?")
    print(f"[AGENT]: {jawaban3}\n")