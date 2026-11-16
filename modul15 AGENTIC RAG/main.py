import os
from agent_orchestrator import AgentOrchestrator
from knowledge_base import KnowledgeBase

def main():
    print("==================================================")
    print("🤖 SELAMAT DATANG DI TOBBLEZ RESEARCH AGENT CLI 🤖")
    print("==================================================")
    print("Ketik 'exit' atau 'quit' untuk keluar.")
    print("Ketik 'clear' untuk reset memori percakapan.\n")

    # 1. Ingest Data Pertama Kali
    sample_file = os.path.join("data", "sample_docs.txt")
    if os.path.exists(sample_file):
        print("📥 Memeriksa & Meng-ingest dokumen internal...")
        kb = KnowledgeBase()
        kb.ingest(sample_file)
        print("--------------------------------------------------\n")
    else:
        print("⚠️ Warning: data/sample_docs.txt gak ketemu, pastikan filenya ada bro!\n")

    # 2. Inisialisasi Orchestrator (Otak AI)
    try:
        agent = AgentOrchestrator()
    except Exception as e:
        print(f"❌ Failed to init Agent: {e}")
        return

    # 3. Chat Loop Utama
    while True:
        try:
            user_input = input("\n👤 Lu: ").strip()
            
            # Cek jika input kosong
            if not user_input:
                continue

            # Command Keluar
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Siap bro, cabut dulu! Sampai jumpa lagi.")
                break

            # Command Clear Memory
            if user_input.lower() == "clear":
                agent.memory.clear()
                continue

            # Kirim pesan ke Agentic Orchestrator
            response = agent.chat(user_input)
            
            print(f"\n🤖 Agent: {response}")

        except KeyboardInterrupt:
            print("\n👋 Cabut dadakan! Bye bro.")
            break
        except Exception as e:
            print(f"\n❌ TERJADI ERROR: {str(e)}")

if __name__ == "__main__":
    main()