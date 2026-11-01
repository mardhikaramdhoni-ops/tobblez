import json

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

    print(f" Log dari '{nama_user}' berhasil disimpan!")
 

def tampilkan_semua_log():
    try:
        with open("logs.json", "r) as file:
            daftar_log = json.load(file)

        print("\n" + "=" * 60)
        print("📜 DAFTAR SEMUA LOG PERCAKAPAN")
        print("=" * 60)

        for log in daftar_log:
            print(
                f'[User: {log["user"]}] Prompt: "{log["prompt"]}" | Response: "{log["response"]}"'
            )

        print("=" * 60 + "\n")

    except FileNotFoundError:
        print("❌ Belum ada file logs.json. Silakan simpan log terlebih dahulu.")


if __name__ == "__main__":
    print("--- MENYIMPAN DATA DUMMY ---")
    simpan_log(
        "toblez",
        "Apa itu RAG?",
        "RAG adalah Retrieval-Augmented Generation untuk menggabungkan search dengan LLM.",
    )
    simpan_log(
        "toblez",
        "Gimana cara fine-tuning?",
        "Fine-tuning dilakukan dengan melatih ulang model menggunakan dataset spesifik.",
    )
    simpan_log(
        "admin",
        "Bagaimana cara deployment?",
        "Deployment bisa menggunakan Docker dan dieksekusi di cloud server.",
    )

    tampilkan_semua_log()