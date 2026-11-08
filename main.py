import sys
from colorama import Fore, Style
from jarvis import Jarvis
from config import logger

BANNER = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════╗
║                                                    ║
║   {Fore.WHITE}██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗{Fore.CYAN}        ║
║   {Fore.WHITE}██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝{Fore.CYAN}        ║
║   {Fore.WHITE}██║███████║██████╔╝██║   ██║██║███████╗{Fore.CYAN}        ║
║   {Fore.WHITE}██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║{Fore.CYAN}        ║
║   {Fore.WHITE}██║██║  ██║██║  ██║ ╚████╔╝ ██║███████║{Fore.CYAN}        ║
║   {Fore.WHITE}╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝{Fore.CYAN}        ║
║                                                    ║
║   {Fore.YELLOW}Personal Terminal Executive Assistant v1.0{Fore.CYAN}       ║
║   {Fore.GREEN}⚡ Powered by Groq + LLaMA 3.3{Fore.CYAN}                   ║
║                                                    ║
╚════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

HELP_TEXT = f"""
{Fore.YELLOW}╭─── JARVIS COMMANDS ──────────────────────────╮
│                                              │
│  {Fore.CYAN}/help{Fore.YELLOW}     — Tampilkan menu bantuan              │
│  {Fore.CYAN}/todos{Fore.YELLOW}    — Lihat semua todo list pending        │
│  {Fore.CYAN}/quit{Fore.YELLOW}     — Matikan Jarvis                      │
│                                              │
│  {Fore.GREEN}💡 Ngobrol santai langsung ketik aja, Sir!{Fore.YELLOW}    │
╰──────────────────────────────────────────────╯{Style.RESET_ALL}
"""


def main():
    print(BANNER)

    try:
        jarvis = Jarvis()
    except Exception as e:
        print(f"{Fore.RED}❌ Gagal inisialisasi Jarvis: {e}{Style.RESET_ALL}")
        sys.exit(1)

    print(f"{Fore.GREEN}✅ Jarvis Online. At your service, Sir.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Ketik {Fore.CYAN}/help{Fore.YELLOW} untuk bantuan.\n{Style.RESET_ALL}")

    while True:
        try:
            user_input = input(f"{Fore.CYAN}You ➤ {Style.RESET_ALL}").strip()

            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd in ["/quit", "/exit"]:
                print(f"\n{Fore.YELLOW}JARVIS: Shutting down... Goodbye, Sir! 🫡{Style.RESET_ALL}")
                jarvis.shutdown()
                break

            elif cmd == "/help":
                print(HELP_TEXT)
                continue

            elif cmd == "/todos":
                print(f"\n{Fore.MAGENTA}📋 Pending Todos:{Style.RESET_ALL}")
                print(f"{Fore.WHITE}{jarvis.memory.get_todos()}{Style.RESET_ALL}\n")
                continue

            # Chat biasa / Agent query
            print(f"\n{Fore.YELLOW}JARVIS ➤ {Style.RESET_ALL}", end="", flush=True)
            response = jarvis.chat(user_input)
            print(f"{Fore.WHITE}{response}{Style.RESET_ALL}\n")

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}JARVIS: Interrupted. Shutdown... 🫡{Style.RESET_ALL}")
            jarvis.shutdown()
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n{Fore.RED}⚠️ Error: {e}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()