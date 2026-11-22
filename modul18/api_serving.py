from fastapi import FastAPI
from pydantic import BaseModel
from agent_service import query_llm_agent # Fungsi yang tadi kita buat

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    # Di sini kita panggil fungsi agent yang tadi
    response_text = query_llm_agent(req.message)
    return {"status": "success", "agent_response": response_text}

@app.get("/health")
def health_check():
    return {"status": "online"}