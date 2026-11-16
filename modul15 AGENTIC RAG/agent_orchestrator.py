import os
import json
from dotenv import load_dotenv
from groq import Groq
from memory import ConversationMemory
import tools # Import file tools.py yang tadi lu bikin

class AgentOrchestrator:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY belum diset di .env bro!")
            
        self.client = Groq(api_key=api_key)
        self.memory = ConversationMemory()
        self.model = "openai/gpt-oss-120b"
        
        # System prompt: Kasih tau AI siapa dia dan aturan mainnya
        self.system_prompt = """
        Lu adalah Tobblez Research Agent, asisten AI yang cerdas, santai, dan suka manggil 'bro'.
        Lu punya akses ke 3 tools:
        1. search_knowledge_base — buat cari info dari dokumen internal.
        2. calculate — buat hitung matematika.
        3. get_current_time — buat cek waktu sekarang.

        ATURAN:
        - Kalau user nanya soal dokumen/topik spesifik (kayak MLOps, Docker, CI/CD), SELALU search knowledge base dulu.
        - Kalau user nanya hitungan, pake calculate.
        - Kalau user nanya jam/tanggal, pake get_current_time.
        - Kalau lu bisa jawab langsung (contoh: nyapa, nanya kabar), jawab langsung.
        - Lu boleh pake LEBIH DARI SATU tool kalau ditanya multiple pertanyaan.
        - Jawab dengan bahasa Indonesia gaul (lu-gw/bro). Jangan hallucinate.
        """

    def _get_tools_definition(self) -> list:
        """Definisi tools format JSON schema untuk Groq Function Calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Cari dokumen internal. Gunakan jika ditanya topik spesifik teknis.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Kata kunci pencarian dokumen"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Hitung ekspresi matematika.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "Ekspresi matematika, contoh: '100 / 4'"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "Dapatkan waktu sekarang.",
                    "parameters": {
                        "type": "object",
                        "properties": {}, # Gak butuh argumen
                        "required": []
                    }
                }
            }
        ]

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Router buat manggil fungsi asli di tools.py"""
        if tool_name == "search_knowledge_base":
            return tools.search_knowledge_base(arguments.get("query"))
        elif tool_name == "calculate":
            return tools.calculate(arguments.get("expression"))
        elif tool_name == "get_current_time":
            return tools.get_current_time()
        else:
            return f"Error: Tool '{tool_name}' tidak dikenal."

    def chat(self, user_message: str) -> str:
        """⭐ THE AGENTIC LOOP ⭐"""
        # Step 1: Simpan chat user ke memory SQLite
        self.memory.add("user", user_message)

        # Step 2: Siapkan array messages (System + History)
        messages = [{"role": "system", "content": self.system_prompt}]
        history = self.memory.get_history(limit=10)
        messages.extend(history)

        # Max loop safety net (biar gak muter terus kalo LLM bingung)
        max_iterations = 5
        
        print("🤖 Agent lagi mikir...") # Feedback visual di CLI
        
        for i in range(max_iterations):
            # Step 3: Panggil Groq API dengan membawa list tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tools_definition(),
                tool_choice="auto",
                max_tokens=1024
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Step 4: Cek apakah LLM minta tool call
            if tool_calls:
                # Append assistant message (yang isinya request tool) ke messages
                messages.append(response_message)
                
                # Execute semua tool yang diminta (bisa lebih dari 1)
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    # Parse argument dari string JSON ke dictionary
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"   [Tool Dipanggil] 🛠️ {tool_name}({arguments})")
                    
                    # Jalankan fungsinya!
                    tool_result = self._execute_tool(tool_name, arguments)
                    
                    # Kembalikan hasil tool ke Groq (role: "tool")
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_name,
                        "content": str(tool_result),
                    })
                
                # Setelah hasil tool masuk array, LOOP KEMBALI ke Step 3!
                continue 
                
            else:
                # Kalau gak ada tool_calls, berarti LLM udah nemu jawaban final!
                final_answer = response_message.content
                
                # Step 5: Simpan jawaban AI ke memory
                self.memory.add("assistant", final_answer)
                
                # Step 6: Selesai!
                return final_answer
                
        # Kalau sampe ngelewatin batas iterasi
        fallback_msg = "Sori bro, gw bingung nyari jawabannya (Loop timeout)."
        self.memory.add("assistant", fallback_msg)
        return fallback_msg