from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="ID unik user", example="toblez_01")
    message: str = Field(..., description="Pesan atau pertanyaan dari user", example="Berapa hasil 25 * 40?")


class ChatResponse(BaseModel):
    user_id: str
    response: str
    tools_used: list[str]


class HistoryResponse(BaseModel):
    history: list[dict]