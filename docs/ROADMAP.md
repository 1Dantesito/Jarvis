# JARVIS — ROADMAP DE IMPLEMENTACIÓN Y EVOLUCIÓN

> **Documento:** /docs/ROADMAP.md  
> **Versión Actual:** 3.4.0  
> **Estado:** 247 Pruebas Automatizadas Pasando (100% Cobertura Funcional)  
> **Regla de Ejecución:** Cada fase requiere verificación, testing funcional y aprobación antes de proceder a la siguiente.

---

## 📌 HISTORIAL DE FASES COMPLETADAS (v1.0 — v3.4)

### [FASE 0 & 1] Auditoría, Higiene de Secretos y Modelo ALLOWLIST (COMPLETADA ✅)
- [x] Aislamiento de código legacy (legacy/app.py, legacy/main.py, legacy/memory_store.json) con bloqueos de ejecución.
- [x] .gitignore blindado para excluir .env, bases de datos locales y archivos en texto plano.
- [x] Implementación del modelo estricto **ALLOWLIST (Fail-Closed)** en core/security.py.
- [x] Prohibición absoluta y permanente de eliminación de archivos (BLOCKED_FILE_ACTIONS) y ejecución de comandos arbitrarios de consola.

### [FASE 2 & 3] Unificación de Arquitectura, Multi-Provider y Contexto Espacio-Temporal (COMPLETADA ✅)
- [x] Backend unificado en FastAPI / ASGI asíncrono con WebSockets y SSE.
- [x] Orquestador multi-proveedor con failover en cascada (Gemini → OpenRouter → Anthropic → Mock).
- [x] Inyección en tiempo real de fecha, hora, día de la semana, zona horaria y ubicación en core/context_engine.py.

### [FASE 4 & 5] Latencia de Voz, Streaming y Pipeline por Oraciones (COMPLETADA ✅)
- [x] Streaming token por token mediante WebSockets y Server-Sent Events (/api/chat/stream).
- [x] Implementación de SentenceBuffer y SentenceTTSPipeline para reproducir audio por oraciones antes de que el LLM termine toda la respuesta.
- [x] Detección de silencio y corte reactivo (*Barge-in*) para interrumpir a JARVIS al hablar o escribir.

### [FASE 6 & 7] Memoria Persistente Híbrida y Recordatorios con APScheduler (COMPLETADA ✅)
- [x] Base de datos relacional SQLite (jarvis.db) como fuente única de verdad con replicación asíncrona hacia Supabase Cloud.
- [x] Motor autónomo de recordatorios core/reminders.py y core/notification_engine.py con APScheduler (jobstore persistente en SQLite).
- [x] Procesamiento de lenguaje natural temporal con dateparser ('en 20 minutos', 'cada lunes a las 9am').
- [x] Notificaciones nativas del sistema operativo mediante plyer, winsound y winotify.

### [FASE 8 & 9] Automatización de Windows y Motor Musical Inteligente (COMPLETADA ✅)
- [x] Control del sistema operativo: gestión de procesos con psutil, protección de procesos críticos, apertura/cierre seguro y búsqueda de archivos en carpetas de usuario.
- [x] Control nativo de volumen con user32.keybd_event (absoluto, mute/unmute y deltas relativos).
- [x] Motor musical en core/music_engine.py con cola continua (ytmusicapi), mini-player y RecommendationEngine con scoring multivariable.

### [FASE 10 & 11] Presencia Visual, App de Escritorio Nativa y Capa Social (COMPLETADA ✅)
- [x] Interfaz Glassmorphic con orbe animado reactivo a estados de voz (IDLE, LISTENING, PROCESSING, SPEAKING) y fondo dinámico Boba.
- [x] Aplicación nativa de escritorio en **PyQt6** (desktop_app.py, Iniciar_Desktop.bat) minimizable a la bandeja del sistema (System Tray).
- [x] Atajo global Alt + Espacio (pynput) para barra de comandos flotante estilo Spotlight / Raycast.
- [x] Capa social SocialResponseLayer con política estricta de brevedad y eliminación de muletillas robóticas.

### [FASE 12 & 13] Enrutador de Herramientas Estructurado y Blindaje de Seguridad (COMPLETADA ✅)
- [x] Generador de esquemas Function Calling para **OpenAI**, **Anthropic** y **Gemini** en ToolRouter.
- [x] Intercepción obligatoria en ToolRouter.execute_tool: validación previa con SecurityPolicy antes de despachar cualquier herramienta.
- [x] Desacoplamiento asíncrono no bloqueante en todas las herramientas del sistema con wait asyncio.to_thread(...).

### [FASE 14] Wake-Word Nativo Offline en Segundo Plano (Voz Manos Libres Desktop) (COMPLETADA ✅)
- [x] Implementar motor de detección de palabra clave local en segundo plano en Python (`BackgroundWakeWordListener` en `core/wakeword/listener.py`).
- [x] Permitir despertar a JARVIS diciendo 'Jarvis' u 'Oye Jarvis' sin necesidad de tener el navegador abierto ni presionar teclas.
- [x] Bucle de audio en hilo separado con buffer circular de bajo consumo de CPU (<2%), condicionado a permisos y plataforma desktop.

### [FASE 15] Visión por Computadora y Comprensión de Pantalla (Screen Context) (COMPLETADA ✅)
- [x] Crear herramienta `analyze_screen` que tome capturas seguras de la pantalla activa con Pillow / ImageGrab.
- [x] Retorno optimizado en base64 para consumo multimodal por modelos de visión (Gemini Flash).
- [x] Filtro de privacidad estricto para bloquear captura ante ventanas de gestores de contraseñas, banca o datos confidenciales.

### [FASE 16] Navegación e Ingesta Web Profunda (Deep Web Reader) (COMPLETADA ✅)
- [x] Implementar herramienta `read_webpage` para extracción limpia de contenido y artículos web (vía `httpx` asíncrono y parser HTML sanitizado).
- [x] Permitir a JARVIS sintetizar documentación técnica, noticias o enlaces compartidos en el chat.
- [x] Caché semántico local (`CACHE_TTL = 1800s`) para no volver a descargar páginas recientemente consultadas.
- [x] Reclasificación de `web_search` a `ToolType.ACTION` para apertura expresa de búsquedas en el navegador de escritorio.

### [FASE 17] Modernización de Proveedores y SDK Oficial (google.genai) (COMPLETADA ✅)
- [x] Migrar `providers/gemini_provider.py` desde el paquete deprecado `google.generativeai` al nuevo SDK oficial `google.genai`.
- [x] Aprovechar capacidades nativas asíncronas (`client.aio.models`), streaming de llamadas a funciones y menor latencia de conexión.
- [x] Eliminar advertencias de deprecación en la suite de pruebas.

### [FASE 18] Automatización y Workflows Complejos de Escritorio (Multi-Step Agent) (COMPLETADA ✅)
- [x] Soporte para secuencias de tareas encadenadas y descomposición de peticiones complejas en `core/multi_step_planner.py`.
- [x] Modo de planificación interactiva con confirmación previa obligatoria para pasos clasificados en `CONFIRMATION_REQUIRED` o de alto riesgo.
- [x] Reportes ejecutivos diarios matutinos / vespertinos con resumen de tareas y recordatorios (`get_daily_briefing`).
- [x] Registro y orquestación de `execute_workflow` y `get_daily_briefing`.

### [FASE D] Cerebro Relacional, Memoria Semántica y Seguridad Afectiva (COMPLETADA ✅)
- [x] **D.1:** Diagnóstico de fragilidad léxica, amnesia monoturno y techo de reglas regex en `docs/RELATIONAL_ENGINE.md`.
- [x] **D.2:** Esquemas JSON formales (`relationship_state`, `personality_traits`, `semantic_memory_entry`) y arquitectura de seguridad en dos capas `CrisisSafetyGuard` (Fast-path 0ms + Capa 2 LLM aislada con Circuit Breaker y fallback por país sin latencia).
- [x] **D.3:** Motor vectorial denso local de 128 dimensiones (`LocalSemanticVectorizer`) con hashing trick determinista L2 offline, migraciones aditivas en SQLite y ranking híbrido con decaimiento temporal exponencial $e^{-\Delta t / 30}$ en `MemoryRetriever`.
- [x] **D.4:** Capa relacional continua (`RelationshipManager`), inercia afectiva 60/40 (anti-amnesia), sincronización de rasgos de personalidad, dual-write hacia `semantic_memories`, pool de 500 recuerdos y límites éticos inviolables (no fingir biología humana ni reemplazar apoyo clínico).
- [x] **D.5:** Suite completa de 53 pruebas dedicadas a la Fase D (`test_crisis_safety_guard.py`, `test_semantic_memory.py`, `test_relational_components.py`, `test_relational_orchestrator.py`).
- [x] **Total del proyecto:** 247 pruebas automatizadas pasando al 100% sin regresiones.
