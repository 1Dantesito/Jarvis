from typing import Dict, Any, Optional
from tools.router import BaseTool
from core.memory_manager import memory_manager, MemoryType

# Claves de identidad que deben escribirse también en user_profile
# para que sean SIEMPRE visibles sin importar la conversación
_IDENTITY_KEYS = {
    "nombre", "name", "full_name", "nombre_completo", "alias", "apodo",
    "nickname", "me_llaman", "edad", "age", "birthdate", "fecha_nacimiento",
    "profesion", "trabajo", "carrera", "ubicacion", "ciudad", "pais",
    "universidad", "colegio", "idioma", "nationalidad", "sexo", "genero"
}

def _is_identity_key(key: str) -> bool:
    """Detecta si una clave corresponde a un dato de identidad personal."""
    k = key.lower().strip()
    if k in _IDENTITY_KEYS:
        return True
    for ident in _IDENTITY_KEYS:
        if ident in k or k in ident:
            return True
    return False


class RememberTool(BaseTool):
    name = "remember_info"
    description = (
        "Guarda o actualiza un hecho, preferencia, alias, dato personal o nota en la memoria a largo plazo. "
        "Úsala siempre que el usuario mencione algo sobre sí mismo, aunque no diga explícitamente 'recuerda'."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": (
                    "Concepto clave en snake_case (ej. 'alias', 'apodo', 'musica_favorita', "
                    "'fecha_nacimiento', 'profesion', 'ciudad_natal')"
                )
            },
            "value": {"type": "string", "description": "Información a recordar"},
            "type": {
                "type": "string",
                "default": "PERSONAL",
                "description": "Tipo de memoria: PERSONAL, PREFERENCE, PROJECT, HABIT, MEDIA_PREFERENCE"
            },
            "importance": {
                "type": "number",
                "default": 0.8,
                "description": "Nivel de importancia (0.1 a 1.0). Datos de identidad deben ser 1.0."
            }
        },
        "required": ["key", "value"]
    }

    async def execute(self, key: str, value: str, type: str = "PERSONAL", importance: float = 0.8, **kwargs) -> Dict[str, Any]:
        clean_key = key.lower().strip()

        # Elevar importancia de datos de identidad
        if _is_identity_key(clean_key):
            importance = max(importance, 1.0)

        # 1. Guardar siempre en memories (recuperación contextual)
        res = memory_manager.store_memory(
            key=clean_key,
            value=value,
            mem_type=type,
            importance=importance,
            category="identidad" if _is_identity_key(clean_key) else "general",
            source="user_explicit"
        )

        # 2. Si es dato de identidad, también persistirlo en user_profile
        #    para que esté SIEMPRE presente en el contexto del sistema
        if _is_identity_key(clean_key) and res.get("success"):
            memory_manager.set_profile(clean_key, value)

        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("error"),
            "persisted_to_profile": _is_identity_key(clean_key)
        }


class RecallTool(BaseTool):
    name = "recall_memories"
    description = "Recupera recuerdos relevantes basados en un tema o tipo de memoria."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Tema a consultar (ej. 'música', 'proyecto', 'Dante')"},
            "type": {"type": "string", "description": "Tipo opcional de memoria"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        mems = memory_manager.get_contextual_memories(query, limit=8)
        return {
            "success": True,
            "data": {
                "memories": mems,
                "count": len(mems),
                "summary": memory_manager.get_memory_summary(type)
            },
            "error": None
        }


class ForgetMemoryTool(BaseTool):
    name = "forget_memory"
    description = "Olvida o desactiva recuerdos sobre un tema específico o clave."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Tema o clave a olvidar (ej. 'alias', 'rock', 'proyecto')"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        res = memory_manager.forget_memory(query)
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("error")
        }


class GetMemorySummaryTool(BaseTool):
    name = "get_memory_summary"
    description = "Devuelve un resumen organizado de todo lo que JARVIS recuerda del usuario."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        summary = memory_manager.get_memory_summary()
        return {
            "success": True,
            "data": {"summary": summary},
            "error": None
        }


class ClearMemoryTool(BaseTool):
    name = "clear_memory"
    description = "Borra toda la memoria de recuerdos del usuario."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        res = memory_manager.clear_all_memory()
        return {
            "success": res.get("success", False),
            "data": res,
            "error": res.get("error")
        }


class ExportMemoryTool(BaseTool):
    name = "export_memory"
    description = "Exporta toda la memoria y perfil en formato estructurado JSON."
    parameters_schema = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        exp = memory_manager.export_memory()
        return {
            "success": True,
            "data": exp,
            "error": None
        }
