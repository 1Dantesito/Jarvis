import os
import json
import time
import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator
from core.ai_provider import AIProvider
from core.config import settings, mask_key
from core.logger import logger

class OpenRouterProvider(AIProvider):
    """
    Proveedor OpenRouter unificado para acceso a GPT-4o, Claude 3.5, Gemini 2.0 y modelos open-source.
    Soporta Function/Tool Calling, Streaming y Failover de modelos candidatos.
    """
    name = "openrouter"
    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model_name = settings.DEFAULT_OPENROUTER_MODEL
        self.candidate_models = settings.OPENROUTER_MODEL_CANDIDATES
        if not self.candidate_models:
            self.candidate_models = [self.model_name]
        elif self.model_name not in self.candidate_models:
            self.candidate_models.insert(0, self.model_name)

        if self.is_configured():
            logger.info(f"[OpenRouterProvider] Inicializado con API Key: {mask_key(self.api_key)} | Modelo: {self.model_name}")

    def is_configured(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("your_"))

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/jarvis-assistant",
            "X-Title": "JARVIS AI Assistant",
            "Content-Type": "application/json"
        }

    def _convert_tools(self, tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None
        converted = []
        for t in tools:
            schema = t.get("parameters") or t.get("input_schema") or {"type": "object", "properties": {}}
            converted.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": schema
                }
            })
        return converted

    def _convert_messages(self, messages: List[Dict[str, Any]], system_prompt: Optional[str] = None) -> List[Dict[str, Any]]:
        converted = []
        if system_prompt:
            converted.append({"role": "system", "content": system_prompt})

        for m in messages:
            role = m.get("role", "user")
            if role in ["human", "user"]:
                role = "user"
            elif role in ["assistant", "model"]:
                role = "assistant"

            if m.get("image"):
                img_info = m["image"]
                raw_b64 = img_info.get("data") or ""
                mime = img_info.get("mime_type", "image/png")
                if not raw_b64.startswith("data:"):
                    data_url = f"data:{mime};base64,{raw_b64}"
                else:
                    data_url = raw_b64
                converted.append({
                    "role": role,
                    "content": [
                        {"type": "text", "text": m.get("content", "")},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                })
            else:
                converted.append({"role": role, "content": m.get("content", "")})

        if not converted or (len(converted) == 1 and converted[0]["role"] == "system"):
            converted.append({"role": "user", "content": "Hola"})

        return converted

    async def _test_model(self, model_name: str) -> bool:
        if not self.is_configured():
            return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    self.API_URL,
                    headers=self._get_headers(),
                    json={
                        "model": model_name,
                        "messages": [{"role": "user", "content": "ping"}],
                        "max_tokens": 5
                    }
                )
                return res.status_code == 200
        except Exception:
            return False

    async def health_check(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "status": "not_configured",
                "model": self.model_name,
                "latency_ms": None,
                "error": "OPENROUTER_API_KEY no configurada."
            }

        start_t = time.time()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(
                    self.API_URL,
                    headers=self._get_headers(),
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": "hola"}],
                        "max_tokens": 5
                    }
                )
                latency = round((time.time() - start_t) * 1000, 2)
                if res.status_code == 200:
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
                        "error": f"HTTP {res.status_code}: {res.text[:120]}"
                    }
        except Exception as e:
            latency = round((time.time() - start_t) * 1000, 2)
            return {
                "status": "error",
                "model": self.model_name,
                "latency_ms": latency,
                "error": str(e)
            }

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "success": False,
                "text": "",
                "tool_calls": [],
                "error": "OPENROUTER_API_KEY no configurada o inválida.",
                "provider": self.name,
                "model": model or self.model_name
            }

        payload_msgs = self._convert_messages(messages, system_prompt)
        payload_tools = self._convert_tools(tools)

        last_error = None
        candidates = [model] if model else self.candidate_models
        for cand_model in candidates:
            start_t = time.time()
            req_body: Dict[str, Any] = {
                "model": cand_model,
                "messages": payload_msgs,
                "temperature": temperature,
                "max_tokens": 350
            }
            if payload_tools:
                req_body["tools"] = payload_tools
                req_body["tool_choice"] = "auto"

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.API_URL,
                        headers=self._get_headers(),
                        json=req_body
                    )
                    latency = round((time.time() - start_t) * 1000, 2)

                    if response.status_code == 200:
                        data = response.json()
                        choice = data.get("choices", [{}])[0]
                        msg = choice.get("message", {})
                        text_content = msg.get("content") or ""
                        tool_calls = []

                        if msg.get("tool_calls"):
                            for tc in msg["tool_calls"]:
                                fn = tc.get("function", {})
                                raw_args = fn.get("arguments", "{}")
                                try:
                                    parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                                except Exception:
                                    parsed_args = {}
                                tool_calls.append({
                                    "id": tc.get("id", f"call_{fn.get('name')}"),
                                    "name": fn.get("name"),
                                    "input": parsed_args
                                })

                        self.model_name = cand_model
                        logger.info(f"[OpenRouterProvider] OK {cand_model} | Latencia: {latency}ms | Tools: {len(tool_calls)}")
                        return {
                            "success": True,
                            "text": text_content.strip(),
                            "tool_calls": tool_calls,
                            "error": None,
                            "provider": self.name,
                            "model": cand_model
                        }
                    else:
                        last_error = f"HTTP {response.status_code}: {response.text[:150]}"
                        logger.warning(f"[OpenRouterProvider] Modelo {cand_model} falló ({last_error}). Probando siguiente...")
                        continue

            except Exception as e:
                last_error = str(e)
                logger.warning(f"[OpenRouterProvider] Excepción con {cand_model}: {last_error}")
                continue

        logger.error(f"[OpenRouterProvider] Todos los modelos candidatos fallaron: {last_error}")
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
        if not self.is_configured():
            yield {"type": "error", "error": "OPENROUTER_API_KEY no configurada"}
            return

        payload_msgs = self._convert_messages(messages, system_prompt)
        payload_tools = self._convert_tools(tools)

        for cand_model in self.candidate_models:
            req_body: Dict[str, Any] = {
                "model": cand_model,
                "messages": payload_msgs,
                "temperature": temperature,
                "max_tokens": 350,
                "stream": True
            }
            if payload_tools:
                req_body["tools"] = payload_tools
                req_body["tool_choice"] = "auto"

            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    async with client.stream(
                        "POST",
                        self.API_URL,
                        headers=self._get_headers(),
                        json=req_body
                    ) as response:
                        if response.status_code != 200:
                            err_body = await response.aread()
                            logger.warning(f"[OpenRouterProvider Stream] Fallo {cand_model} HTTP {response.status_code}: {err_body.decode(errors='ignore')[:100]}")
                            continue

                        tool_calls_acc: Dict[int, Dict[str, Any]] = {}
                        got_content = False

                        async for line in response.aiter_lines():
                            if not line or not line.startswith("data: "):
                                continue
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break

                            try:
                                chunk = json.loads(data_str)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})

                                # Token de texto
                                if "content" in delta and delta["content"]:
                                    got_content = True
                                    yield {"type": "token", "content": delta["content"]}

                                # Tool calls delta
                                if "tool_calls" in delta and delta["tool_calls"]:
                                    got_content = True
                                    for tc in delta["tool_calls"]:
                                        idx = tc.get("index", 0)
                                        if idx not in tool_calls_acc:
                                            tool_calls_acc[idx] = {
                                                "id": tc.get("id", ""),
                                                "name": tc.get("function", {}).get("name", ""),
                                                "arguments": ""
                                            }
                                        if "id" in tc and tc["id"]:
                                            tool_calls_acc[idx]["id"] = tc["id"]
                                        if "function" in tc:
                                            fn = tc["function"]
                                            if "name" in fn and fn["name"]:
                                                tool_calls_acc[idx]["name"] = fn["name"]
                                            if "arguments" in fn and fn["arguments"]:
                                                tool_calls_acc[idx]["arguments"] += fn["arguments"]

                            except Exception:
                                continue

                        # Emitir tool calls consolidadas
                        for _, tc_data in tool_calls_acc.items():
                            parsed_args = {}
                            try:
                                parsed_args = json.loads(tc_data["arguments"])
                            except Exception:
                                pass
                            yield {
                                "type": "tool_call",
                                "tool_call": {
                                    "id": tc_data["id"] or f"call_{tc_data['name']}",
                                    "name": tc_data["name"],
                                    "input": parsed_args
                                }
                            }

                        if got_content:
                            self.model_name = cand_model
                            return

            except Exception as e:
                logger.warning(f"[OpenRouterProvider Stream] Error en {cand_model}: {e}")
                continue

        # Si el stream falla, fallback a generate_response normal
        normal_res = await self.generate_response(messages, system_prompt, tools, temperature)
        if normal_res.get("success"):
            if normal_res.get("text"):
                yield {"type": "token", "content": normal_res["text"]}
            for tc in normal_res.get("tool_calls", []):
                yield {"type": "tool_call", "tool_call": tc}
        else:
            yield {"type": "error", "error": normal_res.get("error", "Error en OpenRouter")}
