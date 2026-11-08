import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, logger
from memory import Memory
from tools import TOOL_DEFINITIONS, execute_tool
from datetime import datetime

CURRENT_DATE = datetime.now().strftime("%d %B %Y")

SYSTEM_PROMPT = f"""You are J.A.R.V.I.S., a highly capable personal terminal executive assistant.
Today's Date: {CURRENT_DATE}

Personality:
- Professional, efficient, slightly witty (like Tony Stark's AI assistant).
- Call the user "Sir" or "Boss".
- Always respond in the language used by the user (Indonesian / English).

Capabilities & Instructions:
- You have tools to check current time, calculate math, save notes, manage todos, inspect system info, AND SEARCH THE WEB.
- ALWAYS use tools when user asks for specific actions covered by tools.
- Use web search tool when asked about current events, news, weather, or real-time data.
- Be concise and clear.
"""

class Jarvis:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY tidak ditemukan! Cek file .env lu, bro.")

        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.memory = Memory()

        # Inject System Prompt di awal pesan
        if not self.memory.messages or self.memory.messages[0]["role"] != "system":
            self.memory.messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

        logger.info(f"Jarvis initialized with model: {self.model}")

    def chat(self, user_input: str) -> str:
        """Proses input user via Tool Calling Loop."""
        self.memory.add_message("user", user_input)

        max_loops = 5  # Safety guard biar ga infinite loop
        loop_count = 0

        while loop_count < max_loops:
            loop_count += 1

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.memory.get_messages(),
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto"
                )
            except Exception as e:
                logger.error(f"Groq API Error: {e}")
                return f"⚠️ Maaf Sir, terjadi error pada API: {str(e)}"

            message = response.choices[0].message

            # Kalau LLM NGGAK MINTA tool → return jawaban langsung
            if not message.tool_calls:
                final_response = message.content or "Ada yang bisa saya bantu lagi, Sir?"
                self.memory.add_message("assistant", final_response)
                return final_response

            # Kalo LLM MINTA Tool Call → Eksekusi Tool
            # Simpan pesan assistant beserta request tool_calls nya
            assistant_msg = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            }
            self.memory.messages.append(assistant_msg)

            # Iterasi setiap tool yang diminta
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except Exception:
                    args = {}

                logger.info(f"🔧 Executing Tool: {tool_name} with args: {args}")

                # Jalankan fungsi
                result = execute_tool(tool_name, args, self.memory)

                # Kirim hasil eksekusi tool balik ke memory (role: tool)
                self.memory.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

        return "⚠️ Maaf Sir, proses terlalu kompleks/looping."

    def shutdown(self):
        self.memory.close()
        logger.info("Jarvis system offline.")