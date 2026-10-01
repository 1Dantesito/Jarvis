import os
import re
import time
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from core.ai_provider import AIProvider
from core.config import settings, mask_key
from core.logger import logger

try:
    from google import genai
    from google.genai import types
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    _GENAI_AVAILABLE = False


class GeminiProvider(AIProvider):
    """
    Proveedor Gemini con soporte para Streaming en tiempo real, Tool Calling dinámico,
    failover automático entre modelos candidatos y auto-diagnóstico.
    Migrado al SDK moderno google.genai (Roadmap Fase 17).
    """
    name = "gemini"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model_name = settings.DEFAULT_GEMINI_MODEL
        self.candidate_models = settings.GEMINI_MODEL_CANDIDATES
        if not self.candidate_models:
            self.candidate_models = [self.model_name]
        elif self.model_name not in self.candidate_models:
            self.candidate_models.insert(0, self.model_name)

        self.client_ready = False
        self.client = None
        self.types = types

        if self.is_configured():
            if not _GENAI_AVAILABLE:
                logger.warning("[GeminiProvider] Paquete google-genai no está instalado.")
                self.client_ready = False
            else:
                try:
                    self.client = genai.Client(api_key=self.api_key)
                    self.client_ready = True
                    logger.info(f"[GeminiProvider] Inicializado con API Key: {mask_key(self.api_key)} | Modelo: {self.model_name}")
                except Exception as e:
                    logger.warning(f"[GeminiProvider] Error inicializando SDK: {e}")
                    self.client_ready = False

    def is_configured(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("your_"))

    @staticmethod
    def _sanitize_schema(schema_dict: Any) -> Any:
        if not isinstance(schema_dict, dict):
            return schema_dict
        allowed_keys = {'type', 'description', 'properties', 'required', 'enum', 'items', 'nullable'}
        sanitized = {}
        for k, v in schema_dict.items():
            if k in allowed_keys:
                if k == 'properties' and isinstance(v, dict):
                    sanitized['properties'] = {pk: GeminiProvider._sanitize_schema(pv) for pk, pv in v.items()}
                elif k == 'items' and isinstance(v, dict):
                    sanitized['items'] = GeminiProvider._sanitize_schema(v)
                else:
                    sanitized[k] = v
        return sanitized

    def _build_config(
        self,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> Any:
        if not self.types:
            return None
        config_kwargs: Dict[str, Any] = {
            "temperature": temperature,
            "automatic_function_calling": self.types.AutomaticFunctionCallingConfig(disable=True)
        }
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt

        if tools:
            function_declarations = []
            for t in tools:
                raw_params = t.get("parameters") or t.get("input_schema") or {"type": "object", "properties": {}}
                clean_params = self._sanitize_schema(raw_params)
                function_declarations.append({
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": clean_params
                })
            config_kwargs["tools"] = [{"function_declarations": function_declarations}]

        return self.types.GenerateContentConfig(**config_kwargs)

    async def health_check(self) -> Dict[str, Any]:
        if not self.is_configured() or not self.client_ready or not self.client or not self.types:
            return {
                "status": "not_configured" if not self.is_configured() else "error",
                "model": self.model_name,
                "latency_ms": None,
                "error": "GEMINI_API_KEY no configurada o SDK no inicializado."
            }

        start_t = time.time()
        try:
            resp = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents="ping",
                config=self.types.GenerateContentConfig(max_output_tokens=5)
            )
            latency = round((time.time() - start_t) * 1000, 2)
            if resp:
                return {
                    "status": "ok",
                    "model": self.model_name,
                    "latency_ms": latency,
                    "error": None
                }
            else:
                return {
                    "status": "error",
                    "model": self.model_name,
                    "latency_ms": latency,
                    "error": "Sin respuesta del modelo."
                }
        except Exception as e:
            latency = round((time.time() - start_t) * 1000, 2)
            return {
                "status": "error",
                "model": self.model_name,
                "latency_ms": latency,
                "error": str(e)
            }

    def _build_contents(self, messages: List[Dict[str, Any]]) -> List[Any]:
        import base64
        contents = []
        for m in messages:
            role = "user" if m.get("role") in ["user", "human"] else "model"
            parts = []
            if m.get("image"):
                img_info = m["image"]
                raw_b64 = img_info.get("data") or ""
                if "base64," in raw_b64:
                    raw_b64 = raw_b64.split("base64,")[1]
                mime = img_info.get("mime_type", "image/png")
                try:
                    if self.types:
                        parts.append(self.types.Part.from_bytes(data=base64.b64decode(raw_b64), mime_type=mime))
                except Exception as e:
                    logger.warning(f"[GeminiProvider] Error decodificando imagen: {e}")
            if m.get("content"):
                if self.types:
                    parts.append(self.types.Part.from_text(text=str(m["content"])))
                else:
                    parts.append(str(m["content"]))
            if not parts:
                if self.types:
                    parts.append(self.types.Part.from_text(text=""))
                else:
                    parts.append("")
            if self.types:
                contents.append(self.types.Content(role=role, parts=parts))
            else:
                contents.append({"role": role, "parts": parts})
        return contents

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.client_ready or not self.client:
            return {
                "success": False,
                "text": "",
                "tool_calls": [],
                "error": "GEMINI_API_KEY no configurada o inválida.",
                "provider": self.name,
                "model": model or self.model_name
            }

        contents = self._build_contents(messages)
        config = self._build_config(system_prompt, tools, temperature)
        last_error = None

        candidates = [model] if model else self.candidate_models
        for model_cand in candidates:
            start_t = time.time()
            try:
                response = await self.client.aio.models.generate_content(
                    model=model_cand,
                    contents=contents,
                    config=config
                )
                
                tool_calls = []
                text_out = ""

                if getattr(response, "candidates", None):
                    for candidate in response.candidates:
                        if getattr(candidate, "content", None) and getattr(candidate.content, "parts", None):
                            for part in candidate.content.parts:
                                if getattr(part, "function_call", None):
                                    fc = part.function_call
                                    tool_calls.append({
                                        "id": f"call_{fc.name}",
                                        "name": fc.name,
                                        "input": dict(fc.args) if getattr(fc, "args", None) else {}
                                    })
                                elif getattr(part, "text", None):
                                    text_out += part.text

                latency = round((time.time() - start_t) * 1000, 2)
                text_res = text_out.strip()
                if text_res or tool_calls:
                    self.model_name = model_cand
                    logger.info(f"[GeminiProvider] OK {model_cand} | Latencia: {latency}ms | Tools: {len(tool_calls)}")
                    return {
                        "success": True,
                        "text": text_res,
                        "tool_calls": tool_calls,
                        "error": None,
                        "provider": self.name,
                        "model": model_cand
                    }
            except Exception as e:
                err_str = str(e)
                last_error = err_str
                logger.warning(f"[GeminiProvider] Modelo {model_cand} falló ({err_str[:80]}). Probando alternativa...")
                continue

        logger.error(f"[GeminiProvider] Todos los modelos candidatos fallaron: {last_error}")
        return {
            "success": False,
            "text": "",
            "tool_calls": [],
            "error": last_error,
            "provider": self.name,
            "model": self.model_name
        }

    async def generate_response_stream(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not self.client_ready or not self.client:
            yield {"type": "error", "error": "GEMINI_API_KEY no configurada"}
            return

        contents = self._build_contents(messages)
        config = self._build_config(system_prompt, tools, temperature)

        for model_cand in self.candidate_models:
            try:
                response_stream = await self.client.aio.models.generate_content_stream(
                    model=model_cand,
                    contents=contents,
                    config=config
                )
                got_content = False

                async for chunk in response_stream:
                    tool_calls = []
                    text_part = ""

                    try:
                        if getattr(chunk, "candidates", None):
                            for cand in chunk.candidates:
                                if getattr(cand, "content", None) and getattr(cand.content, "parts", None):
                                    for part in cand.content.parts:
                                        if getattr(part, "function_call", None):
                                            fc = part.function_call
                                            tool_calls.append({
                                                "id": f"call_{fc.name}",
                                                "name": fc.name,
                                                "input": dict(fc.args) if getattr(fc, "args", None) else {}
                                            })
                                        elif getattr(part, "text", None):
                                            text_part += part.text
                    except Exception as chunk_err:
                        err_s = str(chunk_err).lower()
                        if "model output" in err_s or "must contain" in err_s or "both be empty" in err_s:
                            break
                        raise

                    if text_part:
                        got_content = True
                        yield {"type": "token", "content": text_part}
                    for tc in tool_calls:
                        got_content = True
                        yield {"type": "tool_call", "tool_call": tc}

                if got_content:
                    self.model_name = model_cand
                    return

            except Exception as e:
                logger.warning(f"[GeminiProvider] Stream de {model_cand} falló ({e}). Probando alternativa...")
                continue

        yield {"type": "error", "error": "Gemini no generó respuesta tras probar todos los modelos."}
