import asyncio
from typing import Dict, Any, Optional
from tools.router import BaseTool
from core.windows_automation import WindowsAutomationProvider
from core.security import SecurityPolicy
from core.document_generator import DocumentGenerator
from core.image_generator import ImageGenerator
from core.platform_capabilities import PlatformCapabilities
from core.logger import logger

class OpenAppTool(BaseTool):
    name = "open_application"
    description = "Abre una aplicación autorizada de Windows (Chrome, Edge, Spotify, Calculadora, Bloc de notas, Explorador, CMD, VS Code, Configuración)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Nombre de la aplicación a abrir (ej. 'Chrome', 'Spotify', 'Calculadora', 'Bloc de notas')"
            }
        },
        "required": ["app_name"]
    }

    async def execute(self, app_name: str, **kwargs) -> Dict[str, Any]:
        res = await asyncio.to_thread(WindowsAutomationProvider.open_application, app_name)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class FocusAppTool(BaseTool):
    name = "focus_application"
    description = "Cambia o trae al frente una aplicación que ya está abierta en Windows (ej. 'Chrome', 'Spotify', 'Calculadora')."
    parameters_schema = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Nombre de la aplicación a enfocar/traer al frente"
            }
        },
        "required": ["app_name"]
    }

    async def execute(self, app_name: str, **kwargs) -> Dict[str, Any]:
        is_supported, err = PlatformCapabilities.is_tool_supported(self.name)
        if not is_supported:
            return {"success": False, "data": {"platform_restricted": True}, "error": err}
        res = await asyncio.to_thread(WindowsAutomationProvider.focus_application, app_name)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class CloseAppTool(BaseTool):
    name = "close_application"
    description = "Cierra de forma segura una aplicación autorizada en ejecución (Calculadora, Bloc de notas, Spotify, Chrome, Opera, etc.) o una ventana específica."
    parameters_schema = {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Nombre de la aplicación autorizada a cerrar (ej. 'Opera', 'Chrome', 'Spotify')"
            },
            "window_title": {
                "type": "string",
                "description": "Título o parte del título de la ventana específica a cerrar (opcional)"
            }
        },
        "required": ["app_name"]
    }

    async def execute(self, app_name: str, window_title: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        res = await asyncio.to_thread(WindowsAutomationProvider.close_application, app_name, window_title=window_title)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class CloseWindowTool(BaseTool):
    name = "close_window"
    description = (
        "Cierra una ventana específica abierta en el escritorio por su título o pestaña (ej. una ventana de Opera, YouTube, Chrome, o un documento específico). "
        "Usa esta herramienta cuando el usuario pida cerrar una ventana en particular o cerrar tal pestaña/ventana."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "window_title": {
                "type": "string",
                "description": "Título o parte del título de la ventana a cerrar (ej. 'YouTube', 'GitHub', 'Opera', 'WhatsApp')"
            },
            "app_name": {
                "type": "string",
                "description": "Nombre opcional del navegador o aplicación (ej. 'Opera', 'Chrome', 'Edge')"
            }
        },
        "required": []
    }

    async def execute(self, window_title: Optional[str] = None, app_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        res = await asyncio.to_thread(WindowsAutomationProvider.close_window, window_title=window_title, app_name=app_name)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class CreateTextFileTool(BaseTool):
    name = "create_text_file"
    description = "Crea un archivo de texto con contenido en el Escritorio o Documentos del usuario."
    parameters_schema = {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Nombre del archivo a crear (ej. 'nota.txt', 'ideas.txt', 'archivodeprueba.txt')"
            },
            "content": {
                "type": "string",
                "description": "Texto o contenido que se debe escribir dentro del archivo"
            },
            "location": {
                "type": "string",
                "default": "desktop",
                "description": "Ubicación (desktop, documents, downloads)"
            }
        },
        "required": ["filename", "content"]
    }

    async def execute(self, filename: str, content: str, location: str = "desktop", **kwargs) -> Dict[str, Any]:
        res = await asyncio.to_thread(WindowsAutomationProvider.create_text_file, filename, content, location)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class ReadTextFileTool(BaseTool):
    name = "read_text_file"
    description = "Lee el contenido de un archivo de texto existente en el Escritorio o Documentos."
    parameters_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Ruta o nombre del archivo de texto a leer"
            }
        },
        "required": ["file_path"]
    }

    async def execute(self, file_path: str, **kwargs) -> Dict[str, Any]:
        res = await asyncio.to_thread(WindowsAutomationProvider.read_text_file, file_path)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class SearchFilesTool(BaseTool):
    name = "search_files"
    description = "Busca archivos por nombre o término dentro de las carpetas autorizadas de usuario (Desktop, Documents, Downloads, etc.)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Nombre o palabra clave del archivo a buscar (ej. 'tesis', 'presupuesto', 'arquitectura.pdf')"
            },
            "location": {
                "type": "string",
                "description": "Ubicación opcional donde buscar (Documents, Downloads, Desktop, Pictures)"
            }
        },
        "required": ["query"]
    }

    async def execute(self, query: str, location: str = None, **kwargs) -> Dict[str, Any]:
        res = await asyncio.to_thread(WindowsAutomationProvider.search_files, query, location)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class GetRunningAppsTool(BaseTool):
    name = "get_running_applications"
    description = "Consulta cuáles aplicaciones autorizadas de usuario están abiertas actualmente."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        is_supported, err = PlatformCapabilities.is_tool_supported(self.name)
        if not is_supported:
            return {"success": False, "data": {"platform_restricted": True}, "error": err}
        res = await asyncio.to_thread(WindowsAutomationProvider.get_running_applications)
        return {
            "success": True,
            "data": res,
            "error": None
        }

class OpenUrlTool(BaseTool):
    name = "open_url"
    description = "Abre una dirección web segura (http / https) en el navegador predeterminado."
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL a abrir (ej. 'https://www.youtube.com', 'https://www.google.com')"}
        },
        "required": ["url"]
    }

    async def execute(self, url: str, **kwargs) -> Dict[str, Any]:
        is_supported, err = PlatformCapabilities.is_tool_supported(self.name)
        if not is_supported:
            return {"success": False, "data": {"platform_restricted": True}, "error": err}
        res = await asyncio.to_thread(WindowsAutomationProvider.open_url, url)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class OpenFileTool(BaseTool):
    name = "open_file"
    description = "Abre un archivo ubicado dentro de las carpetas autorizadas de usuario (Escritorio, Documentos, Descargas, etc.)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "file_path": {"type": "string", "description": "Ruta o nombre del archivo a abrir"}
        },
        "required": ["file_path"]
    }

    async def execute(self, file_path: str, **kwargs) -> Dict[str, Any]:
        is_supported, err = PlatformCapabilities.is_tool_supported(self.name)
        if not is_supported:
            return {"success": False, "data": {"platform_restricted": True}, "error": err}
        res = await asyncio.to_thread(WindowsAutomationProvider.open_file, file_path)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class OpenFolderTool(BaseTool):
    name = "open_folder"
    description = "Abre una carpeta autorizada en el Explorador de Windows (ej. 'Desktop', 'Downloads', 'Documents')."
    parameters_schema = {
        "type": "object",
        "properties": {
            "folder_path": {"type": "string", "description": "Nombre o ruta de la carpeta"}
        },
        "required": ["folder_path"]
    }

    async def execute(self, folder_path: str = "Desktop", **kwargs) -> Dict[str, Any]:
        is_supported, err = PlatformCapabilities.is_tool_supported(self.name)
        if not is_supported:
            return {"success": False, "data": {"platform_restricted": True}, "error": err}
        res = await asyncio.to_thread(WindowsAutomationProvider.open_folder, folder_path)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("message") if not res.get("success") else None
        }

class ListFilesTool(BaseTool):
    name = "list_files"
    description = "Lista los archivos en una carpeta autorizada de usuario (Desktop, Documents, Downloads, etc.)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "default": "desktop",
                "description": "Ubicación a consultar (Desktop, Documents, Downloads, Pictures)"
            }
        },
        "required": []
    }

    async def execute(self, location: str = "desktop", **kwargs) -> Dict[str, Any]:
        def _list():
            is_safe, path, err = SecurityPolicy.validate_path_access(location, must_exist=False)
            if not is_safe or not path or not path.exists():
                return {"success": True, "data": {"items": [], "summary": "Directorio no encontrado o vacío."}, "error": None}

            try:
                items = [f.name for f in path.iterdir() if not f.name.startswith(".")][:15]
                summary = f"Archivos en {path.name}: " + (", ".join(items) if items else "Carpeta vacía")
                return {
                    "success": True,
                    "data": {"items": items, "directory": path.name, "summary": summary},
                    "error": None
                }
            except Exception as e:
                return {"success": False, "data": {}, "error": str(e)}

        return await asyncio.to_thread(_list)

class GetActiveAppTool(BaseTool):
    name = "get_active_application"
    description = "Consulta cuál es la ventana y aplicación activa en primer plano en Windows."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        is_supported, err = PlatformCapabilities.is_tool_supported(self.name)
        if not is_supported:
            return {"success": False, "data": {"platform_restricted": True}, "error": err}
        info = await asyncio.to_thread(WindowsAutomationProvider.get_active_application)
        if info.get("available") and info.get("title"):
            summary = f"Estás usando {info.get('app_name', info.get('process'))} ({info.get('title')})."
        else:
            summary = "No se detectó ninguna aplicación en primer plano en este momento."
        return {
            "success": True,
            "data": {**info, "summary": summary},
            "error": None
        }

class CreatePdfTool(BaseTool):
    name = "create_pdf"
    description = "Genera un documento PDF formal con maquetación limpia y estándares APA (márgenes de 1 pulgada, tipografía sans-serif, encabezados jerárquicos y numeración de páginas). Guarda en Desktop o Documents."
    parameters_schema = {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "Nombre del archivo PDF a generar (ej. 'investigacion_ia.pdf')"},
            "title": {"type": "string", "description": "Título principal formal del documento"},
            "content": {
                "type": "string",
                "description": (
                    "Contenido estructurado del documento. Soporta Markdown extendido: "
                    "encabezados (# ##), viñetas (-), tablas (filas '| Col A | Col B |' con separador '|---|---|') "
                    "e imágenes ('![descripción](nombre_de_archivo.png)' o '<img src=\"...\" alt=\"...\">'), "
                    "maquetadas automáticamente centradas con rótulo formal APA ('Figura N. Descripción'). "
                    "Soporta archivos en disco, fotos adjuntas en el chat ('![Foto](adjunto)'), URLs o auto-síntesis de imágenes."
                )
            },
            "standard": {"type": "string", "enum": ["pdf/a", "pdf/ua", "standard"], "default": "pdf/a", "description": "Estándar o variante de PDF (por defecto PDF/A)"},
            "author": {"type": "string", "default": "Dante", "description": "Nombre del autor del documento"},
            "location": {"type": "string", "enum": ["desktop", "documents"], "default": "desktop", "description": "Ubicación donde se guardará el archivo"}
        },
        "required": ["filename", "title", "content"]
    }

    async def execute(
        self,
        filename: str,
        title: str,
        content: str,
        standard: str = "pdf/a",
        author: str = "Dante",
        location: str = "desktop",
        **kwargs
    ) -> Dict[str, Any]:
        res = await asyncio.to_thread(
            DocumentGenerator.create_pdf,
            filename=filename,
            title=title,
            content=content,
            standard=standard,
            author=author,
            location=location
        )
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("error") if not res.get("success") else None
        }

class CreateDocxTool(BaseTool):
    name = "create_docx"
    description = "Genera un documento de texto editable en Microsoft Word (.docx) con estilo APA, márgenes de 1 pulgada y tipografía Calibri. Guarda en Desktop o Documents."
    parameters_schema = {
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "Nombre del archivo DOCX a generar (ej. 'ensayo_arquitectura.docx')"},
            "title": {"type": "string", "description": "Título principal del documento"},
            "content": {
                "type": "string",
                "description": (
                    "Contenido estructurado del documento. Soporta Markdown extendido: "
                    "encabezados (# ##), viñetas (-), tablas (filas '| Col A | Col B |' con separador '|---|---|') "
                    "e imágenes ('![descripción](nombre_de_archivo.png)' o '<img src=\"...\" alt=\"...\">'), "
                    "centradas con rótulo formal APA ('Figura N. Descripción'). "
                    "Soporta archivos en disco, fotos adjuntas del chat ('![Foto](adjunto)'), URLs o auto-síntesis de imágenes."
                )
            },
            "author": {"type": "string", "default": "Dante", "description": "Nombre del autor"},
            "location": {"type": "string", "enum": ["desktop", "documents"], "default": "desktop", "description": "Ubicación de guardado"}
        },
        "required": ["filename", "title", "content"]
    }

    async def execute(
        self,
        filename: str,
        title: str,
        content: str,
        author: str = "Dante",
        location: str = "desktop",
        **kwargs
    ) -> Dict[str, Any]:
        res = await asyncio.to_thread(
            DocumentGenerator.create_docx,
            filename=filename,
            title=title,
            content=content,
            author=author,
            location=location
        )
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("error") if not res.get("success") else None
        }

class GenerateImageTool(BaseTool):
    name = "generate_image"
    description = (
        "Genera una imagen artística o fotográfica independiente en alta resolución y la almacena en Imágenes o Escritorio. "
        "IMPORTANTE: NO uses esta herramienta si el usuario solicitó un documento PDF o Word; para documentos con imágenes "
        "o referencias visuales, invoca directamente 'create_pdf' o 'create_docx' incluyendo las imágenes dentro del parámetro 'content'."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Descripción detallada de la imagen a generar (en español o inglés)"},
            "filename": {"type": "string", "description": "Nombre opcional de archivo para guardar (ej. 'robot_futurista.png')"},
            "location": {"type": "string", "enum": ["pictures", "desktop"], "default": "pictures", "description": "Carpeta de destino donde guardar la imagen"},
            "style": {"type": "string", "description": "Estilo visual opcional (ej. 'cyberpunk', 'fotografía realista', 'arte digital 3D', 'anime')"},
            "width": {"type": "integer", "default": 1024, "description": "Ancho en píxeles (512 a 2048)"},
            "height": {"type": "integer", "default": 1024, "description": "Alto en píxeles (512 a 2048)"},
            "model": {"type": "string", "default": "flux", "enum": ["flux", "flux-realism", "turbo"], "description": "Modelo de generación IA (flux para máxima calidad)"}
        },
        "required": ["prompt"]
    }

    async def execute(
        self,
        prompt: str,
        filename: Optional[str] = None,
        location: str = "pictures",
        style: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
        **kwargs
    ) -> Dict[str, Any]:
        res = await ImageGenerator.generate_image(
            prompt=prompt,
            filename=filename,
            location=location,
            style=style,
            width=width,
            height=height,
            model=model
        )
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("error") if not res.get("success") else None
        }

class AnalyzeScreenTool(BaseTool):
    name = "analyze_screen"
    description = (
        "Captura de forma segura la ventana o pantalla activa en Windows, aplicando filtros de privacidad "
        "contra contraseñas, bancos o datos sensibles, y devuelve un análisis visual multimodal de lo que se visualiza."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Pregunta o instrucción sobre el contenido visual en pantalla (ej. '¿qué error aparece en la ventana?', 'resume lo que se ve')"
            },
            "full_screen": {
                "type": "boolean",
                "default": False,
                "description": "Si es True captura toda la pantalla; si es False captura la ventana activa"
            }
        },
        "required": ["prompt"]
    }

    SENSITIVE_KEYWORDS = [
        "password", "contraseña", "bitwarden", "1password", "keepass", "lastpass",
        "banco", "online banking", "tarjeta", "credit card", "credenciales", "token", "cbu"
    ]

    async def execute(self, prompt: str, full_screen: bool = False, **kwargs) -> Dict[str, Any]:
        is_supported, err = PlatformCapabilities.is_tool_supported(self.name)
        if not is_supported:
            return {"success": False, "data": {"platform_restricted": True}, "error": err}

        # 1. Filtro de privacidad estricto por ventana activa
        active_info = await asyncio.to_thread(WindowsAutomationProvider.get_active_application)
        active_title = (active_info.get("title") or "").lower()
        active_app = (active_info.get("app_name") or active_info.get("process") or "").lower()

        for kw in self.SENSITIVE_KEYWORDS:
            if kw in active_title or kw in active_app:
                logger.warning(f"[AnalyzeScreenTool] Captura bloqueada por privacidad: '{active_title}'")
                return {
                    "success": False,
                    "data": {"privacy_blocked": True, "window": active_info.get("title")},
                    "error": "Captura bloqueada por política de privacidad: la ventana activa contiene credenciales o información sensible."
                }

        # 2. Captura segura con Pillow
        def _capture():
            try:
                import io
                import base64
                from PIL import ImageGrab
                img = ImageGrab.grab()
                max_dim = 1280
                if img.width > max_dim or img.height > max_dim:
                    img.thumbnail((max_dim, max_dim))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=80)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                return {
                    "success": True,
                    "data": {
                        "prompt": prompt,
                        "window_title": active_info.get("title"),
                        "active_app": active_info.get("app_name", active_info.get("process")),
                        "data_url": f"data:image/jpeg;base64,{b64}",
                        "width": img.width,
                        "height": img.height,
                        "summary": f"Pantalla capturada ({img.width}x{img.height}) sobre '{active_info.get('title', 'escritorio')}'. Consulta: {prompt}"
                    },
                    "error": None
                }
            except Exception as ex:
                logger.error(f"[AnalyzeScreenTool] Error capturando pantalla: {ex}")
                return {"success": False, "data": {}, "error": f"Error al capturar pantalla: {str(ex)}"}

        return await asyncio.to_thread(_capture)


