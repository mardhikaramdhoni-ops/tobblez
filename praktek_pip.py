# Import (panggil) library colorama yang udah diinstall tadi
from colorama import Fore, Back, Style, init

# Inisialisasi colorama (biar jalan di Windows)
init(autoreset=True)

# ==========================================
# TEST TULISAN BERWARNA-WARNI
# ==========================================

print(Fore.RED + "Ini tulisan warna MERAH!")
print(Fore.GREEN + "Ini tulisan warna HIJAU!")
print(Fore.YELLOW + "Ini tulisan warna KUNING!")
print(Fore.CYAN + "Ini tulisan warna BIRU MUDA!")

# Kombinasi Warna Teks + Background + Bold
print(Fore.BLACK + Back.WHITE + " Teks Hitam Background Putih ")
print(Fore.YELLOW + Back.BLUE + Style.BRIGHT + " TEKS KUNING BACKGROUND BIRU " )

print("\nKeren kan bro, terminal kamu sekarang berwarna!")