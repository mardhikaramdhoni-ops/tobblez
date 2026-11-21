from dotenv import load_dotenv
load_dotenv() # Wajib di paling atas sebelum import routes!

from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Tobblez Agent API Service",
    description="Modul 17 - Production-Ready Dockerized Agentic RAG REST API",
    version="1.0.0",
)

# Healthcheck Endpoint (Wajib buat Docker Compose Healthcheck)
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "Tobblez Agent Service"}

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)