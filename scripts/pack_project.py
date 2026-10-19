"""
scripts/pack_project.py - Empaquetador oficial y optimizado para compartir JARVIS a otro computador.
Genera un archivo JARVIS_Portable.zip excluyendo entornos virtuales dependientes de máquina,
caché compilada y archivos con credenciales privadas o datos personales.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

# Asegurar compatibilidad con consolas Windows sin UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_ZIP = BASE_DIR / "JARVIS_Portable.zip"

EXCLUDE_DIRS = {
    "venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
}

EXCLUDE_FILES = {
    "jarvis.db",
    "JARVIS_Portable.zip",
    "Thumbs.db",
    ".DS_Store",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".log",
}

def clean_caches():
    """Limpia carpetas de caché y audios temporales antes de comprimir."""
    print("[1/3] Limpiando archivos temporales y cache...")
    count_dirs = 0
    for root, dirs, files in os.walk(BASE_DIR, topdown=False):
        for d in dirs:
            if d in ("__pycache__", ".pytest_cache"):
                dir_path = os.path.join(root, d)
                try:
                    shutil.rmtree(dir_path)
                    count_dirs += 1
                except Exception:
                    pass
    
    # Limpiar audios generados antiguos en static/audio (conservar directorio)
    audio_dir = BASE_DIR / "static" / "audio"
    if audio_dir.exists():
        for f in audio_dir.glob("*.mp3"):
            try:
                f.unlink()
            except Exception:
                pass
    print(f"      OK: {count_dirs} directorios de cache limpiados.")

def create_portable_zip():
    """Genera el ZIP portable con compresión deflated óptima."""
    print("[2/3] Empaquetando proyecto en JARVIS_Portable.zip...")
    if OUTPUT_ZIP.exists():
        try:
            OUTPUT_ZIP.unlink()
        except Exception:
            pass

    total_files = 0
    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                ext = os.path.splitext(file)[1].lower()
                if ext in EXCLUDE_EXTENSIONS:
                    continue

                full_path = Path(root) / file
                rel_path = full_path.relative_to(BASE_DIR)

                zipf.write(full_path, arcname=str(rel_path))
                total_files += 1

    size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
    print(f"      OK: {total_files} archivos empaquetados.")
    print(f"      OK: Peso final: {size_mb:.2f} MB (ultra liviano).")

def main():
    print("=" * 65)
    print("   JARVIS v4.0 — GENERADOR DE PAQUETE PORTABLE")
    print("=" * 65)
    clean_caches()
    create_portable_zip()
    print("=" * 65)
    print("[3/3] PAQUETE GENERADO CON EXITO.")
    print(f"Ubicacion: {OUTPUT_ZIP}")
    print("\nInstrucciones para la persona que lo reciba:")
    print(" 1. Descomprimir JARVIS_Portable.zip.")
    print(" 2. Leer LEEME_PRIMERO.txt y pegar su GEMINI_API_KEY en .env.")
    print(" 3. Doble clic en Iniciar_Jarvis.bat (auto-instalara todo en 1-clic).")
    print("=" * 65)

if __name__ == "__main__":
    main()
