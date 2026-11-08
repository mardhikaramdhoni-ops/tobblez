import os
import logging
from dotenv import load_dotenv
from colorama import init

# Inisialisasi colorama biar warna jalan di terminal Windows
init(autoreset=True)

# Load data dari file .env
load_dotenv()

# Konfigurasi API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # ← TAMBAHIN DI SINI BRO!

# Setup Folder buat simpan data (Database & Log)
DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "jarvis.db")
LOG_FILE = os.path.join(DATA_DIR, "jarvis.log")

def setup_logger():
    """Setup logger buat nyatet semua aktivitas Jarvis."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    logger = logging.getLogger("jarvis")
    logger.setLevel(logging.DEBUG)

    # Simpan log ke file jarvis.log
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Tampilkan error aja di console biar gak spam
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

# Singleton logger biar bisa dipake di semua file
logger = setup_logger()