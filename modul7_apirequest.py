import json
import requests


def simpan_log(nama_user, prompt, response):
    log_baru = {"user": nama_user, "prompt": prompt, "response": response}

    try:
        with open("logs.json", "r") as file:
            daftar_log = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        daftar_log = []

    daftar_log.append(log_baru)

    with open("logs.json", "w") as file:
        json.dump(daftar_log, file, indent=4)

    print(f"✅ Log dari '{nama_user}' berhasil disimpan ke logs.json!")


def fetch_ai_advice():
    url = "https://api.adviceslip.com/advice"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()


            advice = data["slip"]["advice"]
            return advice
        else:
            return "Gagal mengambil advice dari server."

    except Exception as e:
        return f"Error saat koneksi ke API: {e}"



if __name__ == "__main__":
    print("🤖 Toblez-Agent sedang mengambil advice dari internet...")

    hasil_advice = fetch_ai_advice()

    simpan_log(
        nama_user="Toblez-Agent",
        prompt="Berikan aku saran hari ini!",
        response=hasil_advice,
    )

    print("\n" + "=" * 60)
    print("🎉 HASIL ADVICE HARI INI:")
    print(f'"{hasil_advice}"')
    print("=" * 60)