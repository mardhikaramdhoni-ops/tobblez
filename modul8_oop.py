import json
import requests

class LLMAgent:

    def __init__(self, nama, role):
        self.nama = nama
        self.role = role

    def ambil_advice(self):
        url = "https://api.adviceslip.com/advice"
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

    # 4. Method: Flow utama percakapan
    def tanya(self, user_prompt):
        print(
            f"\n🤖 [{self.nama} | Role: {self.role}] sedang memproses prompt..."
        )

        jawaban = self.ambil_advice()

        self.log_percakapan(user_prompt, jawaban)

        print(f'User Prompt : "{user_prompt}"')
        print(f'AI Response : "{jawaban}"')
        print(f"✅ Log otomatis tersimpan atas nama: {self.nama}")



if __name__ == "__main__":
    print("==========================================")
    print("🚀 MEMULAI SISTEM MULTI-AGENT")
    print("==========================================")

    agent_curhat = LLMAgent("Curhat-Bot", "Mental Health Advisor")
    agent_curhat.tanya("Aku lagi overthinking nih bro...")

    agent_karir = LLMAgent("Karir-Coach", "Professional Career Consultant")
    agent_karir.tanya("Gimana caranya biar sukses di dunia software engineer?")