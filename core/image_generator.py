import os
import re
import time
import base64
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from core.security import SecurityPolicy
from core.logger import logger

class ImageGenerator:
    """
    Generador de imágenes artísticas y fotográficas mediante IA.
    Descarga imágenes en alta resolución y las almacena en carpetas de usuario autorizadas.
    """

    @classmethod
    async def generate_image(
        cls,
        prompt: str,
        filename: Optional[str] = None,
        location: str = "pictures",
        style: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        model: str = "flux"
    ) -> Dict[str, Any]:
        clean_prompt = prompt.strip()
        if not clean_prompt:
            return {"success": False, "error": "El prompt de imagen no puede estar vacío."}

        # Filtrado preventivo con SecurityPolicy
        if SecurityPolicy.is_dangerous(clean_prompt):
            return {"success": False, "error": "Prompt bloqueado por contener patrones no autorizados."}

        enhanced_prompt = clean_prompt
        if style:
            enhanced_prompt = f"{clean_prompt}, {style} style, masterpiece, high quality, professional"

        # Limitar dimensiones a rangos válidos
        width = max(512, min(width, 2048))
        height = max(512, min(height, 2048))

        loc_str = location.lower().strip()
        target_dir = SecurityPolicy.get_actual_user_dir("Pictures")
        if loc_str in ["desktop", "escritorio"]:
            target_dir = SecurityPolicy.get_actual_user_dir("Desktop")
        elif loc_str in ["documents", "documentos"]:
            target_dir = SecurityPolicy.get_actual_user_dir("Documents")

        if not filename:
            slug = re.sub(r'[^a-zA-Z0-9]', '_', clean_prompt[:25]).strip('_').lower() or "imagen"
            filename = f"jarvis_{slug}_{int(time.time())}.png"
        elif not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            filename += ".png"

        target_file_path = target_dir / filename
        is_safe, safe_path, err = SecurityPolicy.validate_path_access(str(target_file_path), must_exist=False)
        if not is_safe or not safe_path:
            return {
                "success": False,
                "error": err or "BLOCKED_ACTION",
                "message": "Acceso denegado: la ubicación de guardado no está autorizada."
            }

        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        seed = int(time.time() * 1000) % 1000000
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model={model}&nologo=true&seed={seed}"

        logger.info(f"[ImageGenerator] Descargando imagen ({width}x{height}, modelo: {model}) desde: {image_url}")

        try:
            async with httpx.AsyncClient(timeout=45.0, follow_redirects=True) as client:
                resp = await client.get(image_url)
                if resp.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Error del servicio de imagen (HTTP {resp.status_code})",
                        "message": "No se pudo generar la imagen en este momento."
                    }

                # Validar tipo de contenido y tamaño mínimo real
                content_type = resp.headers.get("content-type", "").lower()
                image_bytes = resp.content
                if len(image_bytes) < 2048:
                    return {
                        "success": False,
                        "error": "Respuesta corrupta o vacía del generador",
                        "message": "El servicio devolvió un archivo de imagen incompleto o corrupto."
                    }

                if "text/html" in content_type or "application/json" in content_type:
                    return {
                        "success": False,
                        "error": f"Respuesta no válida del proveedor ({content_type})",
                        "message": "El servicio de imágenes devolvió un error en lugar de la imagen solicitada."
                    }

                safe_path.parent.mkdir(parents=True, exist_ok=True)
                with open(safe_path, "wb") as f:
                    f.write(image_bytes)

            file_size = safe_path.stat().st_size if safe_path.exists() else 0
            b64_data = base64.b64encode(image_bytes).decode('utf-8')
            data_url = f"data:image/png;base64,{b64_data}"

            logger.info(f"[ImageGenerator] Imagen guardada en: {safe_path} ({file_size} bytes)")
            return {
                "success": True,
                "file_name": safe_path.name,
                "path": str(safe_path),
                "bytes_written": file_size,
                "data_url": data_url,
                "prompt": clean_prompt,
                "width": width,
                "height": height,
                "model": model,
                "message": f"Imagen '{safe_path.name}' generada con éxito ({width}x{height}, {model}) y guardada en tus Imágenes."
            }

        except Exception as e:
            logger.error(f"[ImageGenerator] Error en generate_image: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error al generar la imagen: {e}"
            }
