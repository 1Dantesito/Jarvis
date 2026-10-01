import os
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from core.ai_provider import AIProvider
from core.config import settings, mask_key
from core.logger import logger

class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model_name = settings.DEFAULT_CLAUDE_MODEL
        self.client = None

        if self.is_configured():
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
                logger.info(f"[AnthropicProvider] Inicializado con API Key: {mask_key(self.api_key)} | Modelo: {self.model_name}")
            except Exception as e:
                logger.warning(f"[AnthropicProvider] Error inicializando SDK: {e}")
                self.client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("your_"))

    async def _test_model(self, model_name: str) -> bool:
        if not self.client:
            return False
        try:
            resp = await self.client.messages.create(
                model=model_name,
                max_tokens=5,
                messages=[{"role": "user", "content": "ping"}]
            )
            return bool(resp)
        except Exception:
            return False

    async def health_check(self) -> Dict[str, Any]:
        if not self.is_configured() or not self.client:
            return {
                "status": "not_configured" if not self.is_configured() else "error",
                "model": self.model_name,
                "latency_ms": None,
                "error": "ANTHROPIC_API_KEY no configurada o SDK no inicializado."
            }

        start_t = time.time()
        try:
            resp = await self.client.messages.create(
                model=self.model_name,
                max_tokens=5,
                messages=[{"role": "user", "content": "ping"}]
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
                    "error": "Sin respuesta de Claude."
                }
        except Exception as e:
            latency = round((time.time() - start_t) * 1000, 2)
            return {
                "status": "error",
                "model": self.model_name,
                "latency_ms": latency,
                "error": str(e)
            }

    def _prepare_kwargs(self, messages: List[Dict[str, Any]], system_prompt: Optional[str], tools: Optional[List[Dict[str, Any]]], temperature: float) -> Dict[str, Any]:
        anthropic_msgs = []
        for m in messages:
            role = "user" if m.get("role") in ["user", "human"] else "assistant"
            content = m.get("content", "")
            if content:
                anthropic_msgs.append({"role": role, "content": content})

        if not anthropic_msgs:
            anthropic_msgs.append({"role": "user", "content": "Hola"})

        kwargs = {
            "model": self.model_name,
            "max_tokens": 1024,
            "messages": anthropic_msgs,
            "temperature": temperature
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            clean_tools = []
            for t in tools:
                schema = t.get("input_schema") or t.get("parameters") or {"type": "object", "properties": {}}
                clean_tools.append({
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "input_schema": schema
                })
            kwargs["tools"] = clean_tools
        return kwargs

    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.client:
            return {
                "success": False,
                "text": "",
                "tool_calls": [],
                "error": "ANTHROPIC_API_KEY no configurada o inválida.",
                "provider": self.name,
                "model": model or self.model_name
            }

        kwargs = self._prepare_kwargs(messages, system_prompt, tools, temperature)
        if model:
            kwargs["model"] = model

        try:
            start_t = time.time()
            response = await self.client.messages.create(**kwargs)
            latency = round((time.time() - start_t) * 1000, 2)
            text_content = ""
            tool_calls = []
            for block in response.content:
                if block.type == "text":
                    text_content += block.text
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })

            logger.info(f"[AnthropicProvider] OK {self.model_name} | Latencia: {latency}ms | Tools: {len(tool_calls)}")
            return {
                "success": True,
                "text": text_content.strip(),
                "tool_calls": tool_calls,
                "error": None,
                "provider": self.name,
                "model": self.model_name
            }
        except Exception as e:
            logger.error(f"[AnthropicProvider] Error en API: {e}")
            return {
                "success": False,
                "text": "",
                "tool_calls": [],
                "error": str(e),
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
        if not self.client:
            yield {"type": "error", "error": "ANTHROPIC_API_KEY no configurada"}
            return

        kwargs = self._prepare_kwargs(messages, system_prompt, tools, temperature)

        try:
            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    if text:
                        yield {"type": "token", "content": text}

                final_message = await stream.get_final_message()
                for block in final_message.content:
                    if block.type == "tool_use":
                        yield {
                            "type": "tool_call",
                            "tool_call": {
                                "id": block.id,
                                "name": block.name,
                                "input": block.input
                            }
                        }
        except Exception as e:
            logger.error(f"[AnthropicProvider] Error en stream: {e}")
            yield {"type": "error", "error": str(e)}
