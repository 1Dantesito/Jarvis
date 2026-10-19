import os
import re
import io
import sys
import time
import socket
import asyncio
import shutil
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any

from core.logger import logger
from core.config import settings

class NetworkTunnelManager:
    """
    Gestor de túnel seguro hacia Internet y conectividad móvil para JARVIS.
    Permite acceder a JARVIS desde cualquier celular vía HTTPS sin configurar puertos en el router.
    """

    CLOUDFLARED_DOWNLOAD_URL = (
        "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    )

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or settings.BASE_DIR
        self.bin_dir = self.base_dir / "tools" / "bin"
        self.binary_path = self.bin_dir / "cloudflared.exe"
        self._process: Optional[asyncio.subprocess.Process] = None
        self._public_url: Optional[str] = None
        self._is_starting = False
        self._last_error: Optional[str] = None

    def get_local_ip(self) -> str:
        """Obtiene la dirección IP local de la máquina en la red Wi-Fi o Ethernet."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def get_local_url(self, port: Optional[int] = None) -> str:
        p = port or settings.PORT
        return f"http://{self.get_local_ip()}:{p}"

    def ensure_cloudflared_binary(self) -> Optional[Path]:
        """Verifica si cloudflared existe o intenta descargarlo de forma segura."""
        # 1. Comprobar en PATH del sistema
        system_cloudflared = shutil.which("cloudflared")
        if system_cloudflared:
            return Path(system_cloudflared)

        # 2. Comprobar en tools/bin local
        if self.binary_path.exists() and self.binary_path.stat().st_size > 10_000_000:
            return self.binary_path

        # 3. Descarga automática del binario oficial de Cloudflare
        try:
            self.bin_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"[Tunnel] Descargando cloudflared oficial desde {self.CLOUDFLARED_DOWNLOAD_URL}...")
            req = urllib.request.Request(
                self.CLOUDFLARED_DOWNLOAD_URL,
                headers={"User-Agent": "JARVIS-Assistant/4.0"}
            )
            temp_path = self.bin_dir / "cloudflared.exe.tmp"
            with urllib.request.urlopen(req, timeout=45) as resp, open(temp_path, "wb") as f:
                shutil.copyfileobj(resp, f)
            
            if temp_path.exists() and temp_path.stat().st_size > 10_000_000:
                temp_path.replace(self.binary_path)
                logger.info(f"[Tunnel] cloudflared descargado exitosamente en {self.binary_path}")
                return self.binary_path
            else:
                if temp_path.exists():
                    temp_path.unlink()
                raise ValueError("Archivo descargado incompleto o corrupto")
        except Exception as e:
            self._last_error = f"Error descargando cloudflared: {e}"
            logger.warning(f"[Tunnel] No se pudo descargar cloudflared automáticamente: {e}")
            return None

    async def start_tunnel(self, port: Optional[int] = None, timeout: int = 30) -> Optional[str]:
        """Inicia el túnel seguro Cloudflare Quick Tunnel hacia el puerto especificado."""
        if self._public_url and self._process and self._process.returncode is None:
            return self._public_url

        target_port = port or settings.PORT
        bin_path = self.ensure_cloudflared_binary()
        if not bin_path or not bin_path.exists():
            self._last_error = "Binario cloudflared no disponible"
            return None

        self._is_starting = True
        self._last_error = None
        target_local_url = f"http://127.0.0.1:{target_port}"

        try:
            cmd = [
                str(bin_path),
                "tunnel",
                "--url",
                target_local_url,
                "--no-autoupdate",
            ]
            
            logger.info(f"[Tunnel] Lanzando túnel Cloudflare para {target_local_url}...")
            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Buscar la URL pública en los logs de cloudflared (impresos en stderr)
            url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
            start_time = time.time()

            async def _read_stderr():
                while self._process and self._process.stderr:
                    line = await self._process.stderr.readline()
                    if not line:
                        break
                    decoded = line.decode("utf-8", errors="ignore")
                    match = url_pattern.search(decoded)
                    if match:
                        found_url = match.group(0)
                        self._public_url = found_url
                        logger.info(f"[Tunnel] ¡Túnel Cloudflare activo y verificado!: {found_url}")
                        return found_url
                return None

            try:
                found_url = await asyncio.wait_for(_read_stderr(), timeout=timeout)
                self._is_starting = False
                return found_url
            except asyncio.TimeoutError:
                self._last_error = "Tiempo de espera agotado al conectar túnel Cloudflare"
                logger.warning(f"[Tunnel] {self._last_error}")
                self._is_starting = False
                return None

        except Exception as e:
            self._last_error = str(e)
            self._is_starting = False
            logger.error(f"[Tunnel] Error ejecutando cloudflared: {e}")
            return None

    def stop_tunnel(self):
        """Detiene el proceso del túnel si está activo."""
        if self._process:
            try:
                self._process.terminate()
            except Exception:
                pass
            self._process = None
        self._public_url = None
        self._is_starting = False
        logger.info("[Tunnel] Túnel detenido.")

    def get_tunnel_url(self) -> Optional[str]:
        if self._process and self._process.returncode is not None:
            self._public_url = None
        return self._public_url

    def is_active(self) -> bool:
        return bool(self._public_url and self._process and self._process.returncode is None)

    def generate_terminal_qr(self, url: str) -> str:
        """Genera un código QR en arte ASCII legible para terminales Windows."""
        try:
            import qrcode
            qr = qrcode.QRCode(border=1)
            qr.add_data(url)
            qr.make(fit=True)
            f = io.StringIO()
            qr.print_ascii(out=f, invert=True)
            return f.getvalue()
        except Exception as e:
            return f"[QR no disponible: {e}]"

    def generate_svg_qr(self, url: str) -> str:
        """Genera un código QR en formato SVG puro para insertar en la UI web."""
        try:
            import qrcode
            import qrcode.image.svg
            factory = qrcode.image.svg.SvgPathImage
            img = qrcode.make(url, image_factory=factory, box_size=8, border=1)
            buf = io.BytesIO()
            img.save(buf)
            return buf.getvalue().decode("utf-8")
        except Exception as e:
            logger.warning(f"[Tunnel] Error generando SVG QR: {e}")
            return ""

    def get_mobile_connection_info(self, port: Optional[int] = None) -> Dict[str, Any]:
        """Retorna toda la información necesaria para conectar un celular a JARVIS."""
        target_port = port or settings.PORT
        local_url = self.get_local_url(target_port)
        tunnel_url = self.get_tunnel_url()
        active_url = tunnel_url or local_url

        qr_svg = self.generate_svg_qr(active_url)

        return {
            "tunnel_active": self.is_active(),
            "internet_url": tunnel_url,
            "local_url": local_url,
            "recommended_url": active_url,
            "is_starting": self._is_starting,
            "last_error": self._last_error,
            "qr_svg": qr_svg,
            "pwa_ready": True,
            "instructions": {
                "step1": "Escanea el código QR con la cámara de tu celular o abre la URL recomendada.",
                "step2": "En iPhone (Safari): pulsa 'Compartir' y luego 'Agregar a la pantalla de inicio'.",
                "step3": "En Android (Chrome): pulsa el menú de 3 puntos y 'Instalar aplicación' o 'Agregar a la pantalla principal'.",
                "step4": "¡Listo! Tienes JARVIS en tu celular como app nativa con voz, música, recuerdos y control de PC."
            }
        }

# Instancia singleton para uso en el servidor y scripts
tunnel_manager = NetworkTunnelManager()
