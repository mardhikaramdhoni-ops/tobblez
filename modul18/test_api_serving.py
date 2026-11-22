from fastapi.testclient import TestClient
from api_serving import app
from unittest.mock import MagicMock

# Inisialisasi client testing buat FastAPI
client = TestClient(app)

def test_health_endpoint():
    # Ngetes endpoint GET /health
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}

def test_chat_endpoint_full(mocker):
    # 1. Bajak (Mock) LLM lagi biar gak bayar token
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Respon API Mocking Berhasil!"))
    ]
    mocker.patch("groq.resources.chat.completions.Completions.create", return_value=mock_response)
    
    # 2. Kirim request POST palsu ke API kita
    payload = {"message": "Halo AI!"}
    response = client.post("/chat", json=payload)
    
    # 3. Validasi
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["agent_response"] == "Respon API Mocking Berhasil!"