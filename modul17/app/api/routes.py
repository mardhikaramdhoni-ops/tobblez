from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse, HistoryResponse
from app.core.agent_orchestrator import AgentOrchestrator
from app.core.memory import AgentMemory

router = APIRouter()
orchestrator = AgentOrchestrator()
memory = AgentMemory()


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "Tobblez Agent API"}


@router.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    result = await orchestrator.run(req.user_id, req.message)
    return ChatResponse(**result)


@router.post("/api/v1/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    return StreamingResponse(
        orchestrator.run_stream(req.user_id, req.message),
        media_type="text/event-stream",
    )


@router.get("/api/v1/history/{user_id}", response_model=HistoryResponse)
async def get_user_history(user_id: str):
    history = await memory.get_history(user_id, limit=20)
    return HistoryResponse(history=history)


@router.delete("/api/v1/history/{user_id}")
async def clear_user_history(user_id: str):
    await memory.clear_history(user_id)
    return {"status": "cleared", "user_id": user_id}