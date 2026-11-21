import os
import json
from dotenv import load_dotenv
from groq import AsyncGroq
from app.core.tools import TOOLS_REGISTRY
from app.core.memory import AgentMemory

load_dotenv()


class AgentOrchestrator:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY tidak ditemukan di file .env!")

        self.client = AsyncGroq(api_key=api_key)
        self.memory = AgentMemory()
        self.model = "openai/gpt-oss-120b"

        self.tools_definition = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Cari informasi di dalam knowledge base internal tentang Tobblez AI, arsitektur, atau kebijakan sistem.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Kata kunci atau pertanyaan pencarian",
                            }
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Hitung operasi matematika secara akurat.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Ekspresi matematika standar, misal: '(125 * 4) + 50'",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            },
        ]

    def _build_system_prompt(self) -> str:
        return (
            "Kamu adalah Tobblez Research Agent yang pintar, ramah, dan akurat. "
            "Gunakan tool 'search_knowledge_base' jika ditanya soal dokumen/sistem internal Tobblez, "
            "dan gunakan tool 'calculate' untuk semua hitungan matematika. "
            "Jawab selalu dengan bahasa Indonesia yang jelas."
        )

    async def _build_messages(self, user_id: str) -> list[dict]:
        history = await self.memory.get_history(user_id, limit=10)
        return [{"role": "system", "content": self._build_system_prompt()}] + history

    # 1. Method untuk Endpoint POST /api/v1/chat (Standard JSON)
    async def run(self, user_id: str, message: str) -> dict:
        await self.memory.save_message(user_id, "user", message)
        messages = await self._build_messages(user_id)
        tools_used = []

        for _ in range(5):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools_definition,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                })

                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    if fn_name not in tools_used:
                        tools_used.append(fn_name)

                    if fn_name in TOOLS_REGISTRY:
                        result = await TOOLS_REGISTRY[fn_name](**fn_args)
                    else:
                        result = f"Error: Tool '{fn_name}' tidak ditemukan."

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    })
            else:
                # Jika tidak ada tool call, langsung return jawaban final
                final_answer = msg.content or ""
                await self.memory.save_message(user_id, "assistant", final_answer)
                return {
                    "user_id": user_id,
                    "response": final_answer,
                    "tools_used": tools_used,
                }

        # Fallback jika mencapai max iteration setelah tool calls
        final_res = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        final_answer = final_res.choices[0].message.content or ""
        await self.memory.save_message(user_id, "assistant", final_answer)
        return {
            "user_id": user_id,
            "response": final_answer,
            "tools_used": tools_used,
        }

    # 2. Method untuk Endpoint POST /api/v1/chat/stream (SSE Streaming)
    async def run_stream(self, user_id: str, message: str):
        await self.memory.save_message(user_id, "user", message)
        messages = await self._build_messages(user_id)
        tools_used = []

        for _ in range(5):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools_definition,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            if msg.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                })

                for tool_call in msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    if fn_name not in tools_used:
                        tools_used.append(fn_name)

                    yield f"data: {json.dumps({'status': f'Calling tool: {fn_name}'})}\n\n"

                    if fn_name in TOOLS_REGISTRY:
                        result = await TOOLS_REGISTRY[fn_name](**fn_args)
                    else:
                        result = f"Error: Tool '{fn_name}' tidak ditemukan."

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),
                    })
            else:
                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=True,
                )

                full_response = ""
                async for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        full_response += delta.content
                        yield f"data: {json.dumps({'token': delta.content})}\n\n"

                await self.memory.save_message(user_id, "assistant", full_response)
                yield f"data: {json.dumps({'status': 'done', 'tools_used': tools_used})}\n\n"
                return