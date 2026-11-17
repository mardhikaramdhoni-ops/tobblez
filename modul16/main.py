from dotenv import load_dotenv
load_dotenv()  # Wajib di paling atas sebelum import routes!

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Tobblez Agent API Service",
    description="Modul 16 - Production-Ready Agentic RAG REST API",
    version="1.0.0",
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)