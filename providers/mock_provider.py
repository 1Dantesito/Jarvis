import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from core.ai_provider import AIProvider

class MockAIProvider(AIProvider):
    name = "mock"
    model_name = "mock-rules-engine"

    def __init__(self):
        self.forced_response: Optional[str] = None
        self.forced_delay: float = 0.0
        self.forced_error: Optional[str] = None
        self.calls_count: int = 0
        self.last_messages: Optional[List[Dict[str, Any]]] = None
        self.last_system_prompt: Optional[str] = None
        self.last_model: Optional[str] = None

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "model": self.model_name,
            "latency_ms": 0.5,
            "error": None
        }

    def _resolve_mock(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        # Si es una evaluación de seguridad clínica aislada
        if system_prompt and ("seguridad clinica" in system_prompt.lower() or "evaluador de seguridad" in system_prompt.lower() or "autolisis" in system_prompt.lower() or "autolesion" in system_prompt.lower()):
            if self.forced_response is not None:
                return {"text": self.forced_response, "tool_calls": []}
            last_msg = messages[-1]["content"].lower() if messages else ""
            if any(k in last_msg for k in ["suicid", "matarme", "morir", "acabar con mi vida", "no quiero vivir", "ganó la oscuridad", "gano la oscuridad", "gracias por todo adios", "me rindo"]):
                return {"text": "SI", "tool_calls": []}
            elif any(k in last_msg for k in ["triste", "desesperado", "vacio", "no puedo mas", "pesadilla", "cansado de vivir", "cansada de vivir", "cansado de todo", "cansada de todo"]):
                return {"text": "AMBIGUO", "tool_calls": []}
            else:
                return {"text": "NO", "tool_calls": []}

        last_message = messages[-1]["content"] if messages else ""
        text_lower = last_message.lower().strip()
        tool_calls = []
        text = "Todo listo."

        # Respuestas casuales y de empatía
        if "hola jarvis" in text_lower or text_lower == "hola":
            text = "¡Hola! ¿Qué hay en mente para hoy?"
        elif "¿qué haces?" in text_lower or "que haces" in text_lower:
            text = "Esperándote. ¿Qué vamos a hacer?"
        elif "estoy cansado" in text_lower or "estoy agotado" in text_lower:
            text = "Entonces bajemos el ritmo. ¿Quieres que te ayude a organizar lo que queda del día?"
        elif "organízame el día" in text_lower or "organizame el dia" in text_lower:
            tool_calls.append({"id": "call_pending", "name": "get_pending_summary", "input": {}})
            text = "Vamos a ello. Primero reviso lo que tienes pendiente."
        elif any(w in text_lower for w in ["hora", "fecha", "día", "tiempo"]):
            tool_calls.append({"id": "call_time", "name": "get_current_datetime", "input": {}})
            text = "Consultando hora."
        elif "borra toda mi memoria" in text_lower or "borrar memoria" in text_lower:
            tool_calls.append({"id": "call_clear_mem", "name": "clear_memory", "input": {}})
            text = "Borrando memoria."
        elif "olvida" in text_lower:
            target = text_lower.replace("olvida", "").replace("que", "").replace("sobre", "").strip()
            tool_calls.append({"id": "call_forget", "name": "forget_memory", "input": {"query": target or "musica"}})
            text = f"Olvidando recuerdos sobre {target}."
        elif "ya no me gusta" in text_lower:
            target = text_lower.replace("ya no me gusta", "").strip()
            tool_calls.append({"id": "call_update_mem", "name": "remember_info", "input": {"key": "musica_disgusto", "value": f"No le gusta {target}"}})
            text = f"Preferencia actualizada."
        elif "qué recuerdas" in text_lower or "que recuerdas" in text_lower or "qué sabes de" in text_lower or "que sabes de" in text_lower:
            tool_calls.append({"id": "call_summary", "name": "recall_memories", "input": {"query": last_message}})
            text = "Consultando memoria."
        elif "recuerda" in text_lower:
            content = last_message.replace("recuerda que", "").replace("recuerda", "").strip()
            tool_calls.append({"id": "call_remember", "name": "remember_info", "input": {"key": "nota", "value": content}})
            text = "Guardado en memoria."
        elif "tarea" in text_lower or "pendiente" in text_lower:
            if any(w in text_lower for w in ["crear", "agregar", "anota", "nueva", "revisar"]):
                tool_calls.append({"id": "call_task_create", "name": "create_task", "input": {"title": last_message}})
                text = "Creando tarea."
            else:
                tool_calls.append({"id": "call_task_list", "name": "list_tasks", "input": {}})
                text = "Consultando pendientes."
        elif "recordatorio" in text_lower or "recuérdame" in text_lower:
            tool_calls.append({"id": "call_rem_create", "name": "create_reminder", "input": {"title": last_message, "remind_at": "Hoy"}})
            text = "Creando recordatorio."
        elif "pausa" in text_lower:
            tool_calls.append({"id": "call_pause", "name": "pause_music", "input": {}})
            text = "Música pausada."
        elif "reanuda" in text_lower or "play" == text_lower:
            tool_calls.append({"id": "call_resume", "name": "resume_music", "input": {}})
            text = "Reanudando música."
        elif "siguiente" in text_lower:
            tool_calls.append({"id": "call_skip", "name": "skip_music", "input": {}})
            text = "Siguiente canción."
        elif "pon" in text_lower or "reproduce" in text_lower:
            target = last_message.replace("pon", "").replace("reproduce", "").strip() or "Linkin Park"
            tool_calls.append({"id": "call_play_music", "name": "play_music", "input": {"query": target}})
            text = f"Reproduciendo {target}."
        elif "cierra" in text_lower:
            found_app = False
            for app_key in ["calc", "notepad", "spotify", "chrome", "vscode", "explorer", "cmd"]:
                if app_key in text_lower or app_key.replace("calc", "calculadora") in text_lower:
                    tool_calls.append({"id": f"call_close_{app_key}", "name": "close_application", "input": {"app_name": app_key}})
                    text = f"Cerrando {app_key}."
                    found_app = True
                    break
            if not found_app:
                tool_calls.append({"id": "call_close_fallback", "name": "close_application", "input": {"app_name": "calc"}})
                text = "Cerrando aplicación activa."
        elif "abre" in text_lower or "abrir" in text_lower:
            for app_key in ["calc", "notepad", "spotify", "chrome", "vscode", "explorer", "cmd"]:
                if app_key in text_lower or app_key.replace("calc", "calculadora") in text_lower:
                    tool_calls.append({"id": f"call_open_{app_key}", "name": "open_application", "input": {"app_name": app_key}})
                    text = f"Abriendo {app_key}."
                    break
        else:
            text = "Entendido. ¿En qué te ayudo?"

        return {"text": text, "tool_calls": tool_calls}

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        self.calls_count += 1
        self.last_messages = messages
        self.last_system_prompt = system_prompt
        self.last_model = model

        if self.forced_delay > 0:
            await asyncio.sleep(self.forced_delay)

        if self.forced_error:
            return {
                "success": False,
                "text": "",
                "tool_calls": [],
                "error": self.forced_error,
                "provider": self.name,
                "model": model or self.model_name
            }

        data = self._resolve_mock(messages, system_prompt)
        return {
            "success": True,
            "text": data["text"],
            "tool_calls": data["tool_calls"],
            "error": None,
            "provider": self.name,
            "model": model or self.model_name
        }

    async def generate_response_stream(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        self.calls_count += 1
        data = self._resolve_mock(messages, system_prompt)
        words = data["text"].split(" ")
        for w in words:
            yield {"type": "token", "content": w + " "}
            await asyncio.sleep(0.01)

        for tc in data["tool_calls"]:
            yield {"type": "tool_call", "tool_call": tc}
