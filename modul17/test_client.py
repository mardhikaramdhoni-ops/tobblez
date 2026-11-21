import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"
USER_ID = "toblez_tester"


def run_tests():
    print("1️⃣ [GET /health]")
    res = requests.get(f"{BASE_URL}/health")
    print("Response:", res.json(), "\n")

    print("2️⃣ [POST /api/v1/chat] - Standard JSON (Multi-Tool Test)")
    payload = {
        "user_id": USER_ID,
        "message": "Apa itu Tobblez AI Service dan berapa hasil dari 150 * 4?",
    }
    res = requests.post(f"{BASE_URL}/api/v1/chat", json=payload)
    print(json.dumps(res.json(), indent=2, ensure_ascii=False), "\n")

    print("3️⃣ [POST /api/v1/chat/stream] - Real-time SSE Streaming")
    stream_payload = {
        "user_id": USER_ID,
        "message": "Hitung (999 + 1) * 5 lalu jelaskan kenapa FastAPI dipilih di Modul 16!",
    }
    with requests.post(f"{BASE_URL}/api/v1/chat/stream", json=stream_payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                decoded = line.decode("utf-8")
                if decoded.startswith("data: "):
                    data = json.loads(decoded[6:])
                    if "status" in data:
                        print(f"\n⚡ [EVENT]: {data}")
                    elif "token" in data:
                        sys.stdout.write(data["token"])
                        sys.stdout.flush()
    print("\n")

    print("4️⃣ [GET /api/v1/history/{user_id}]")
    res = requests.get(f"{BASE_URL}/api/v1/history/{USER_ID}")
    print(f"Total history tersimpan: {len(res.json()['history'])} pesan\n")

    print("5️⃣ [DELETE /api/v1/history/{user_id}]")
    res = requests.delete(f"{BASE_URL}/api/v1/history/{USER_ID}")
    print("Response:", res.json())


if __name__ == "__main__":
    run_tests()