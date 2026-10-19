import os
import sys
import time
import socket
import asyncio
from pathlib import Path

# Agregar raíz al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.network_tunnel import tunnel_manager
from core.config import settings

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

async def main():
    print("=" * 68)
    print("   ⚡ JARVIS v4.0 — INICIANDO MODO CELULAR POR INTERNET")
    print("=" * 68)
    print("\n[1/3] Verificando servidor local de JARVIS...")

    port = settings.PORT
    server_process = None

    if not is_port_in_use(port):
        print(f"      Iniciando servidor JARVIS en http://127.0.0.1:{port}...")
        python_exe = sys.executable
        server_cmd = [
            python_exe, "-m", "uvicorn", "api.server:app",
            "--host", "0.0.0.0", "--port", str(port)
        ]
        server_process = await asyncio.create_subprocess_exec(
            *server_cmd,
            cwd=str(BASE_DIR)
        )
        # Esperar a que el puerto responda
        for _ in range(40):
            await asyncio.sleep(0.5)
            if is_port_in_use(port):
                break
        print("      [OK] Servidor local iniciado correctamente.")
    else:
        print("      [OK] Servidor JARVIS ya está activo.")

    print("\n[2/3] Conectando túnel seguro Cloudflare hacia Internet (HTTPS)...")
    print("      (Esto puede tomar unos segundos en su primera ejecución)...")
    
    tunnel_url = await tunnel_manager.start_tunnel(port=port, timeout=45)

    local_url = tunnel_manager.get_local_url(port)
    active_url = tunnel_url or local_url

    print("\n" + "=" * 68)
    print("   🎉 ¡JARVIS ESTÁ LISTO PARA TU CELULAR!")
    print("=" * 68)

    print("\n[PASO 1] ESCANEA ESTE CÓDIGO QR CON LA CÁMARA DE TU CELULAR:\n")
    try:
        qr_ascii = tunnel_manager.generate_terminal_qr(active_url)
        print(qr_ascii)
    except Exception as e:
        print(f"   (No se pudo renderizar QR ASCII: {e})")

    print("[PASO 2] O ESCRIBE ESTE ENLACE DIRECTO EN EL NAVEGADOR DE TU CELULAR:")
    if tunnel_url:
        print(f"   🌍 INTERNET (Cualquier lugar, Wi-Fi o Datos 4G/5G):")
        print(f"      👉 {tunnel_url}\n")
    print(f"   🏠 RED LOCAL WI-FI (Mismo router en casa):")
    print(f"      👉 {local_url}\n")

    print("-" * 68)
    print("📱 CÓMO GUARDARLO COMO APP EN TU CELULAR (PWA):")
    print("   • En iPhone (Safari): Presiona 'Compartir' y luego 'Agregar a inicio'.")
    print("   • En Android (Chrome): Presiona los 3 puntos y 'Instalar aplicación'.")
    print("   • Tendrás icono de JARVIS y pantalla completa con todas las funciones.")
    print("-" * 68)
    print("💡 Presiona Ctrl + C para detener el modo celular cuando termines.\n")

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n[!] Deteniendo modo celular...")
    finally:
        tunnel_manager.stop_tunnel()
        if server_process:
            try:
                server_process.terminate()
            except Exception:
                pass
        print("[OK] Modo celular detenido correctamente.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
