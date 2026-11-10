import os
import json
import requests
from dotenv import load_dotenv

# Tarik semua data dari file .env ke sistem environment
load_dotenv()


# ==========================================
# 🔐 CLASS LLMAGENT (SECURE VERSION)
# ==========================================
class LLMAgent:


    def __init__(self, role):
        self.nama = os.getenv("AGENT_NAME")
        self.role = role


    def ambil_advice(self):
        url = os.getenv("API_URL")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data["slip"]["advice"]
            else:
                return "Gagal mengambil advice dari server."
        except Exception as e:
            return f"Error koneksi ke API: {e}"


    def log_percakapan(self, prompt, response):
        log_baru = {"user": self.nama, "prompt": prompt, "response": response}

        try:
            with open("logs.json", "r") as file:
                daftar_log = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            daftar_log = []

        daftar_log.append(log_baru)
        with open("logs.json", "w") as file:
            json.dump(daftar_log, file, indent=4)


    def tanya(self, user_prompt):
        print(
            f"\n🤖 [{self.nama} | Role: {self.role}] sedang memproses..."
        )

        jawaban = self.ambil_advice()
        self.log_percakapan(user_prompt, jawaban)

        print(f'User Prompt : "{user_prompt}"')
        print(f'AI Response : "{jawaban}"')
        print(f"✅ Log tersimpan atas nama: {self.nama}")


# ==========================================
# 🧪 TESTING
# ==========================================
if __name__ == "__main__":
    print("==========================================")
    print("🔐 SECURE AGENT LOGGER (MODUL 9)")
    print("==========================================")

    # Nama agent GA diketik di sini, diambil dari .env!
    agent = LLMAgent("Secure Mental Health Advisor")
    agent.tanya("Aku butuh motivasi hari ini bro...")