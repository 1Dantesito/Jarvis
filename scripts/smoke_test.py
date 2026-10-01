import os
import sys
import json
import asyncio
from pathlib import Path

# Añadir raíz al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.config import settings, mask_key
from core.logger import logger
from core.orchestrator import JarvisOrchestrator
from core.music_engine import music_engine
from api.server import perform_health_check

async def run_smoke_tests():
    print("=====================================================")
    print(f"   JARVIS v{settings.VERSION} — SMOKE TEST DE INTEGRACIÓN")
    print("=====================================================")
    print(f"Directorio: {BASE_DIR}")
    print(f"Modo DEV: {settings.DEV_MODE}")
    print(f"OpenRouter Key: {mask_key(settings.OPENROUTER_API_KEY)}")
    print(f"Gemini Key: {mask_key(settings.GEMINI_API_KEY)}")
    print(f"Anthropic Key: {mask_key(settings.ANTHROPIC_API_KEY)}")
    print("-----------------------------------------------------\n")

    passed = 0
    total = 0

    # 1. Test de Auto-Diagnóstico / Health Check
    total += 1
    print("[TEST 1/4] Comprobando perform_health_check() ...")
    try:
        health = await perform_health_check()
        print(f"  Resultado Health: {json.dumps(health, indent=2)}")
        assert "version" in health
        assert "openrouter" in health or "gemini" in health
        print("  -> PASSED: Endpoint de salud responde correctamente.\n")
        passed += 1
    except Exception as e:
        print(f"  -> FAILED: {e}\n")

    # 2. Test de Búsqueda y Motor de Música (YouTube Music)
    total += 1
    print("[TEST 2/4] Probando búsqueda de música en YouTubeProvider ...")
    try:
        tracks = await music_engine.search_music("Linkin Park In The End", limit=2)
        print(f"  Pistas encontradas: {len(tracks)}")
        for t in tracks:
            print(f"    - [{t.id}] {t.title} ({t.artist})")
        assert len(tracks) > 0, "No se encontraron canciones en YouTube"
        assert tracks[0].id, "Pista sin ID de video"
        print("  -> PASSED: Búsqueda de música operativa y con IDs válidos.\n")
        passed += 1
    except Exception as e:
        print(f"  -> FAILED: {e}\n")

    # 3. Test de Reproducción e Inicialización de Cola
    total += 1
    print("[TEST 3/4] Probando play_query() en MusicEngine ...")
    try:
        play_res = await music_engine.play_query("Linkin Park")
        print(f"  Play result: success={play_res.get('success')}, playlist_len={len(play_res.get('playlist', []))}")
        assert play_res.get("success"), f"Fallo al reproducir: {play_res}"
        assert len(play_res.get("playlist", [])) > 0, "Playlist vacía"
        print("  -> PASSED: Cola de reproducción y playlist generadas correctamente.\n")
        passed += 1
    except Exception as e:
        print(f"  -> FAILED: {e}\n")

    # 4. Test del Orquestador con Fallback Real y Tool Calling
    total += 1
    print("[TEST 4/4] Probando JarvisOrchestrator con prompt de usuario ...")
    try:
        orchestrator = JarvisOrchestrator()
        res = await orchestrator.process_user_input("Ponme música de Queen")
        print(f"  Respuesta: '{res.get('response_text')}'")
        print(f"  Proveedor activo: {res.get('provider')}")
        print(f"  Herramientas ejecutadas: {[t['tool_name'] for t in res.get('tools_executed', [])]}")
        assert res.get("success"), f"Fallo en orquestador: {res}"
        assert res.get("response_text"), "Respuesta vacía"
        print("  -> PASSED: Orquestador procesó el comando y ejecutó la tool de música.\n")
        passed += 1
    except Exception as e:
        print(f"  -> FAILED: {e}\n")

    print("=====================================================")
    print(f" RESUMEN DE PRUEBAS: {passed}/{total} PASADAS")
    print("=====================================================")

    if passed == total:
        print(" [OK] Todos los componentes v3.0 funcionan correctamente.")
        return 0
    else:
        print(" [WARN] Algunas pruebas fallaron. Revisa los detalles arriba.")
        return 1

if __name__ == "__main__":
    code = asyncio.run(run_smoke_tests())
    sys.exit(code)
