import datetime
import re
from knowledge_base import KnowledgeBase

# Inisialisasi KnowledgeBase instance
# Nanti pas file ini di-import, KB langsung siap dipanggil
kb = KnowledgeBase()

def search_knowledge_base(query: str) -> str:
    """
    Cari informasi spesifik dari dokumen internal / knowledge base. 
    Gunakan tool ini ketika user bertanya tentang topik teknis spesifik 
    seperti Docker, MLOps, CI/CD, atau konsep sistem lain yang ada di dokumen.
    """
    try:
        results = kb.search(query, n_results=3)
        if not results:
            return "Tidak ditemukan informasi relevan di knowledge base."
        return "\n\n".join(results)
    except Exception as e:
        return f"Error saat mencari di knowledge base: {str(e)}"

def calculate(expression: str) -> str:
    """
    Hitung operasi matematika (penjumlahan, pengurangan, perkalian, pembagian, pangkat).
    Gunakan tool ini ketika user meminta perhitungan matematika atau angka.
    Contoh input expression: '157 * 23', '(100 + 50) / 2', '2**8'.
    """
    # 🛡️ SECURITY FIRST: Mencegah RCE (Remote Code Execution)
    # Cuma izinkan angka, operator matematika (+ - * / % . ( )), dan spasi
    safe_pattern = r'^[0-9+\-*/%.()\s]+$'
    
    clean_expr = expression.strip()
    
    # Cek apakah ada karakter mencurigakan (kayak __import__, os, eval, dll)
    if not re.match(safe_pattern, clean_expr):
        return "Error: Ekspresi matematika mengandung karakter terlarang demi alasan keamanan."
    
    try:
        # Restricted eval: __builtins__ di-set ke None biar gak bisa panggil fungsi OS/System
        result = eval(clean_expr, {"__builtins__": None}, {})
        return str(result)
    except ZeroDivisionError:
        return "Error: Tidak bisa membagi angka dengan nol."
    except Exception as e:
        return f"Error perhitungan matematika: {str(e)}"

def get_current_time() -> str:
    """
    Ambil tanggal dan waktu saat ini secara real-time.
    Gunakan tool ini ketika user bertanya tentang jam berapa sekarang, 
    hari apa hari ini, atau tanggal berapa sekarang.
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S (%A)")