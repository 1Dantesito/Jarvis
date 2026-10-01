from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator

class AIProvider(ABC):
    """
    Interfaz abstracta universal para proveedores de Modelos de Lenguaje en JARVIS v3.0.
    """
    name: str = "base"
    model_name: str = "default"

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera una respuesta con soporte de llamadas a herramientas (Tool Calls).
        Retorna:
        {
            "success": bool,
            "text": str,
            "tool_calls": List[{"id": str, "name": str, "input": dict}],
            "error": Optional[str],
            "provider": str,
            "model": str
        }
        """
        pass

    async def generate_response_stream(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generador asíncrono para streaming de tokens y tool calls.
        Yields:
        {"type": "token", "content": str} o {"type": "tool_call", "tool_call": dict} o {"type": "error", "error": str}
        """
        res = await self.generate_response(messages, system_prompt, tools, temperature)
        if not res.get("success"):
            yield {"type": "error", "error": res.get("error", "Error desconocido")}
            return
        if res.get("text"):
            yield {"type": "token", "content": res["text"]}
        for tc in res.get("tool_calls", []):
            yield {"type": "tool_call", "tool_call": tc}

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado y latencia de conexión con el proveedor.
        Retorna:
        {
            "status": "ok" | "error" | "not_configured",
            "model": str,
            "latency_ms": Optional[float],
            "error": Optional[str]
        }
        """
        pass
