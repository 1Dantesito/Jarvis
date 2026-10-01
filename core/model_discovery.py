import time
from typing import Dict, Any, Optional
from core.logger import logger

# Cache en memoria por sesión del proceso { "provider:model_name": (is_valid: bool, timestamp: float) }
_MODEL_VALIDATION_CACHE: Dict[str, bool] = {}

async def validate_model(provider_client: Any, model_name: str, provider_name: str = "generic") -> bool:
    """
    Realiza una validación mínima en tiempo de ejecución para confirmar que un modelo
    está disponible y responde adecuadamente. Cachea el resultado durante la sesión.
    """
    cache_key = f"{provider_name}:{model_name}"
    if cache_key in _MODEL_VALIDATION_CACHE:
        return _MODEL_VALIDATION_CACHE[cache_key]

    try:
        if provider_name == "gemini":
            # Prueba con Google Generative AI
            loop_result = await _validate_gemini(provider_client, model_name)
            _MODEL_VALIDATION_CACHE[cache_key] = loop_result
            return loop_result

        elif provider_name == "openrouter":
            # Prueba con OpenRouter / OpenAI format
            res = await provider_client._test_model(model_name)
            _MODEL_VALIDATION_CACHE[cache_key] = res
            return res

        elif provider_name == "anthropic":
            # Prueba con Anthropic
            res = await provider_client._test_model(model_name)
            _MODEL_VALIDATION_CACHE[cache_key] = res
            return res

        # Por defecto asumir válido si no hay handler específico
        return True

    except Exception as e:
        logger.warning(f"[ModelDiscovery] Validación falló para {provider_name}/{model_name}: {e}")
        _MODEL_VALIDATION_CACHE[cache_key] = False
        return False

async def _validate_gemini(genai_module: Any, model_name: str) -> bool:
    import asyncio
    def _sync_ping():
        model = genai_module.GenerativeModel(model_name)
        resp = model.generate_content("ping", generation_config={"max_output_tokens": 1})
        return bool(resp)
    
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _sync_ping)
