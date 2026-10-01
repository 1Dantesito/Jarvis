# AUDITORÍA EXHAUSTIVA DE HERRAMIENTAS — JARVIS v4.0 (FASE B.1)

> **Documento:** `/docs/TOOLS_AUDIT.md`  
> **Fecha de Elaboración:** Septiembre 2026  
> **Estado:** Fase B.1 — Auditoría Previa a Modificaciones de Código  
> **Objetivo:** Inspeccionar el 100% de las herramientas existentes en `tools/router.py` y `tools/implementations/`, documentando su tipo, permisos requeridos, plataforma soportada, cobertura de pruebas, estado de registro en el orquestador y deficiencias encontradas.

---

## 1. RESUMEN EJECUTIVO Y HALLAZGOS CRÍTICOS

Se auditaron **7 módulos de implementación** y el núcleo de enrutamiento (`tools/router.py`), abarcando un total de **49 herramientas y variantes**.

### 🚨 Hallazgos Críticos Principales:
1. **14 Herramientas Huérfanas (Unregistered Orphans):** Existen 14 herramientas formalmente implementadas en `tools/implementations/` que **nunca se registran en `JarvisOrchestrator._register_tools()`**. Como resultado, los modelos LLM (Gemini, Claude, OpenRouter) jamás reciben su esquema ni pueden invocarlas en tiempo de ejecución.
2. **Brecha de Permisos Lógicos (`PermissionManager`):** `ToolRouter.execute_tool` verifica patrones de inyección y allowlist con `SecurityPolicy`, pero **no comprueba si el permiso lógico correspondiente (`PermissionCategory`) está otorgado en `PermissionManager`** antes de disparar la acción (ej. `set_volume` y `open_application` no validan `PermissionCategory.AUTOMATION`; `get_location` no valida `PermissionCategory.LOCATION`).
3. **Falta de Capa de Aislamiento de Plataforma (Desktop vs. Mobile/Web):** Herramientas estrictamente ligadas a la API Win32 de Windows (`focus_application`, `set_volume`, `get_active_application`, `open_folder`, `open_file`) asumen ejecución local en la misma pantalla física. En un contexto cliente-servidor o móvil (PWA/Capacitor), estas herramientas se ejecutan en el servidor en lugar de interactuar con el cliente o retornar un error estructurado de plataforma no soportada.
4. **Falsa Consulta Web (`web_search`):** La herramienta `web_search` solo ejecuta `webbrowser.open(...)` en el navegador del host de Windows. No realiza scraping, no devuelve contenido y no permite al LLM responder preguntas basadas en la web. Carece de capacidades de lectura profunda (Fase 16 del Roadmap).
5. **Riesgo Destructivo no Confirmado (`clear_memory`):** La herramienta `clear_memory` borra irreversiblemente toda la memoria del usuario, pero se encuentra listada dentro de `SecurityPolicy.SAFE_ACTIONS` sin requerir confirmación previa (`CONFIRMATION_REQUIRED`).

---

## 2. MATRIZ MAESTRA DE AUDITORÍA DE HERRAMIENTAS

| Herramienta | Archivo Fuente | Tipo | Propósito | Permiso Requerido | Plataforma | Cobertura de Tests | Registrada en Orquestador | Problemas / Deficiencias Detectadas |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| `get_current_datetime` | `system_tools.py` | `QUERY` | Obtiene fecha, hora, día, zona horaria y UTC offset en vivo. | Ninguno | Universal | `test_tool_router.py`, `test_context_engine.py` | ✅ Sí | Ninguno. Totalmente operativa y no bloqueante. |
| `get_location` | `system_tools.py` | `QUERY` | Consulta ubicación geográfica por IP/GPS. | `LOCATION` | Universal | `test_location_provider.py` | ✅ Sí | No valida `PermissionManager.is_granted(PermissionCategory.LOCATION)` en la herramienta. |
| `parse_relative_time` | `system_tools.py` | `QUERY` | Interpreta lenguaje natural temporal a ISO 8601. | Ninguno | Universal | `test_time_parser.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** El LLM no puede invocarla directamente como tool. |
| `ping` | `system_tools.py` | `QUERY` | Comprueba estado operativo del asistente. | Ninguno | Universal | `test_tool_router.py` | ✅ Sí | Ninguno. Salud operativa básica. |
| `set_volume` | `system_tools.py` | `ACTION` | Ajusta volumen Windows (0-100, mute, deltas). | `AUTOMATION` | Desktop (Win32) | `test_tool_router.py`, `test_windows_automation.py` | ✅ Sí | Usa `user32.keybd_event`. No verifica plataforma ni `PermissionCategory.AUTOMATION`. |
| `open_application` | `desktop_tools.py` | `ACTION` | Abre apps autorizadas (Chrome, Spotify, Calc, etc.). | `AUTOMATION` | Desktop (Windows) | `test_windows_automation.py`, `test_orchestrator.py` | ✅ Sí | Dependencia directa de `psutil` y registro de Windows; no aplicable en móvil. |
| `focus_application` | `desktop_tools.py` | `ACTION` | Trae al frente una ventana de app abierta. | `AUTOMATION` | Desktop (Win32) | `test_windows_automation.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** Requiere Win32 `SetForegroundWindow`. |
| `close_application` | `desktop_tools.py` | `ACTION` | Cierra de forma segura una app autorizada. | `AUTOMATION` | Desktop (Windows) | `test_windows_automation.py` | ✅ Sí | Solo en Windows. Mata procesos por nombre ejecutable. |
| `create_text_file` | `desktop_tools.py` | `ACTION` | Crea archivo .txt con contenido en Desktop/Doc. | `FILES` | Servidor / Desktop | `test_windows_automation.py`, `test_security.py` | ✅ Sí | Escribe en el sistema de archivos del servidor/host local. |
| `read_text_file` | `desktop_tools.py` | `QUERY` | Lee archivo de texto en carpetas de usuario. | `FILES` | Servidor / Desktop | `test_windows_automation.py` | ✅ Sí | No limita tamaño máximo de lectura (riesgo OOM si el archivo es masivo). |
| `search_files` | `desktop_tools.py` | `QUERY` | Busca archivos por coincidencia de nombre. | `FILES` | Servidor / Desktop | `test_windows_automation.py`, `test_tool_router.py` | ✅ Sí | Búsqueda síncrona delegada en thread; puede ser lenta sin límite de profundidad. |
| `get_running_applications`| `desktop_tools.py` | `QUERY` | Lista apps autorizadas en ejecución. | `AUTOMATION` | Desktop (Windows) | `test_windows_automation.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** `psutil` dependiente. |
| `open_url` | `desktop_tools.py` | `ACTION` | Abre URL en el navegador por defecto. | Ninguno | Desktop (Host) | `test_windows_automation.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** Abre navegador en el host, no en el cliente móvil. |
| `open_file` | `desktop_tools.py` | `ACTION` | Abre un archivo con su visor predeterminado. | `FILES`, `AUTOMATION` | Desktop (Win32) | `test_windows_automation.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** Usa `os.startfile` (falla fuera de Windows). |
| `open_folder` | `desktop_tools.py` | `ACTION` | Abre carpeta en el Explorador de Windows. | `FILES`, `AUTOMATION` | Desktop (Win32) | `test_windows_automation.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** Lanza `explorer.exe`. |
| `list_files` | `desktop_tools.py` | `QUERY` | Lista los primeros 15 archivos en directorio. | `FILES` | Servidor / Desktop | `test_windows_automation.py` | ✅ Sí | Límite fijo de 15 archivos no parametrizable ni paginado. |
| `get_active_application` | `desktop_tools.py` | `QUERY` | Obtiene título y proceso en primer plano. | `AUTOMATION` | Desktop (Win32) | `test_windows_automation.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** Usa Win32 `GetForegroundWindow`. |
| `create_pdf` | `desktop_tools.py` | `ACTION` | Compila PDF formal bajo normas APA con ReportLab. | `FILES` | Universal (Headless) | `test_document_generator.py` | ✅ Sí | Retorna solo ruta en disco; para clientes web/móviles requiere URL de descarga. |
| `create_docx` | `desktop_tools.py` | `ACTION` | Genera documento Word .docx editable APA. | `FILES` | Universal (Headless) | `test_document_generator.py` | ✅ Sí | Misma observación que `create_pdf`: requiere link de descarga para web/móvil. |
| `generate_image` | `desktop_tools.py` | `ACTION` | Genera imagen sintética con IA (Pollinations/Flux).| `FILES` | Universal | `test_document_generator.py` | ✅ Sí | Alta latencia de red sujeta a disponibilidad de servicio externo. |
| `remember_info` | `memory_tools.py` | `ACTION` | Persiste recuerdos, hechos y datos de identidad. | Ninguno | Universal | `test_memory.py`, `test_advanced_memory.py` | ✅ Sí | Búsqueda por palabras clave; no cuenta aún con búsqueda vectorial/semántica. |
| `recall_memories` | `memory_tools.py` | `QUERY` | Recupera recuerdos contextuales por query. | Ninguno | Universal | `test_memory.py`, `test_advanced_memory.py` | ✅ Sí | Recuperación basada en coincidencia léxica SQL `LIKE`. |
| `forget_memory` | `memory_tools.py` | `ACTION` | Desactiva/olvida recuerdos específicos. | Ninguno | Universal | `test_memory.py` | ✅ Sí | Si la coincidencia es amplia, puede desactivar más de un recuerdo sin avisar. |
| `get_memory_summary` | `memory_tools.py` | `QUERY` | Resumen consolidado del perfil y recuerdos. | Ninguno | Universal | `test_memory.py` | ✅ Sí | Funciona correctamente. |
| `clear_memory` | `memory_tools.py` | `ACTION` | Borra todos los recuerdos almacenados en la BD. | Ninguno (Alto impacto) | Universal | `test_memory.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** Además, en `SecurityPolicy` no pide confirmación. |
| `export_memory` | `memory_tools.py` | `QUERY` | Exporta memorias y perfil en formato JSON. | Ninguno | Universal | `test_memory.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** |
| `play_music` | `music_tools.py` | `ACTION` | Inicia streaming continuo de YouTube Music. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Dependencia de `ytmusicapi`; si hay bloqueo de red o IP, la degradación es lenta. |
| `search_music` | `music_tools.py` | `QUERY` | Busca canciones y devuelve lista de pistas. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Funciona correctamente. |
| `pause_music` | `music_tools.py` | `ACTION` | Pausa reproducción de audio. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Estado exclusivamente en memoria. |
| `resume_music` | `music_tools.py` | `ACTION` | Reanuda reproducción pausada. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Estado exclusivamente en memoria. |
| `skip_music` | `music_tools.py` | `ACTION` | Salta a la siguiente pista en cola. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Funciona correctamente. |
| `get_now_playing` | `music_tools.py` | `QUERY` | Consulta pista y artista en reproducción. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Funciona correctamente. |
| `get_music_queue` | `music_tools.py` | `QUERY` | Consulta lista de temas en cola. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Funciona correctamente. |
| `clear_music_queue` | `music_tools.py` | `ACTION` | Vacía la cola de reproducción musical. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Funciona correctamente. |
| `recommend_music` | `music_tools.py` | `QUERY` *(Error de Tipo)* | Prepara cola de canciones por similitud/ánimo. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | **Inconsistencia:** Clasificada como `QUERY` pero muta estado iniciando música. |
| `search_videos` | `music_tools.py` | `QUERY` | Busca videos educativos/entretenimiento. | Ninguno | Universal | `test_music_engine.py` | ✅ Sí | Funciona correctamente. |
| `create_reminder` | `reminder_tools.py`| `ACTION` | Agenda recordatorio proactivo en APScheduler. | `NOTIFICATIONS` | Universal | `test_reminders.py` | ✅ Sí | No verifica `PermissionCategory.NOTIFICATIONS`. |
| `list_reminders` | `reminder_tools.py`| `QUERY` | Lista recordatorios activos o pendientes. | Ninguno | Universal | `test_reminders.py`, `test_tool_type_query_action.py`| ❌ **No (Huérfana)** | **No registrada en Orquestador.** Orquestador solo usa `get_pending_summary`. |
| `snooze_reminder` | `reminder_tools.py`| `ACTION` | Pospone recordatorio N minutos. | `NOTIFICATIONS` | Universal | `test_reminders.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** |
| `complete_reminder` | `reminder_tools.py`| `ACTION` | Marca recordatorio como completado. | Ninguno | Universal | `test_reminders.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** |
| `delete_reminder` | `reminder_tools.py`| `ACTION` | Borra recordatorio por ID o título. | Ninguno | Universal | `test_reminders.py` | ✅ Sí | Funciona correctamente. |
| `clear_all_reminders`| `reminder_tools.py`| `ACTION`| Vacía todos los recordatorios. | Ninguno | Universal | `test_reminders.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** |
| `clear_all_pending` | `reminder_tools.py`| `ACTION` | Borra recordatorios y tareas a la vez. | Ninguno | Universal | `test_reminders.py` | ✅ Sí | Funciona correctamente. |
| `get_pending_summary`| `reminder_tools.py`| `QUERY` | Resumen combinado de tareas y recordatorios. | Ninguno | Universal | `test_reminders.py` | ✅ Sí | Funciona correctamente. |
| `create_task` | `task_tools.py` | `ACTION` | Crea tarea en la lista de pendientes. | Ninguno | Universal | `test_reminders.py` | ✅ Sí | Funciona correctamente. |
| `list_tasks` | `task_tools.py` | `QUERY` | Lista tareas pendientes del usuario. | Ninguno | Universal | `test_reminders.py`, `test_tool_type_query_action.py`| ✅ Sí | Funciona correctamente. |
| `complete_task` | `task_tools.py` | `ACTION` | Marca tarea como completada. | Ninguno | Universal | `test_reminders.py` | ✅ Sí | Funciona correctamente. |
| `delete_task` | `task_tools.py` | `ACTION` | Elimina tarea por ID o título. | Ninguno | Universal | `test_reminders.py` | ✅ Sí | Funciona correctamente. |
| `clear_all_tasks` | `task_tools.py` | `ACTION` | Vacía todas las tareas acumuladas. | Ninguno | Universal | `test_reminders.py` | ❌ **No (Huérfana)** | **No registrada en Orquestador.** |
| `web_search` | `web_tools.py` | `QUERY` *(Simulación)* | Abre búsqueda en navegador por defecto. | Ninguno | Desktop (Host) | Indirecta | ✅ Sí | **Simulación:** No lee la web ni devuelve texto al LLM. Abre browser en el host. |

---

## 3. AUDITORÍA DETALLADA POR MÓDULO

### 3.1. `tools/router.py` (Enrutador Central y Clasificación)
- **Implementación:** `ToolRouter`, `BaseTool`, enum `ToolType (ACTION / QUERY)`, catálogo `TOOL_REGISTRY`.
- **Fortalezas:**
  - Exportación estructurada de esquemas para **Anthropic** (`input_schema`), **Gemini** (`parameters`) y **OpenAI / OpenRouter** (`{"type": "function", "function": ...}`).
  - Intercepción previa obligatoria en `execute_tool` mediante `SecurityPolicy.classify_action`.
  - Fail-Fast al registrar herramientas no catalogadas (`BUG-24`).
- **Deficiencias Detectadas:**
  1. `execute_tool` no verifica permisos con `PermissionManager`. Aunque la acción sea `SAFE` según `SecurityPolicy`, si el usuario tiene `PermissionCategory.AUTOMATION` o `FILES` en estado `DENIED`, la herramienta se ejecuta igual.
  2. No evalúa `SystemCapabilities` ni contexto de ejecución (`desktop` vs `mobile-dev`) antes de intentar ejecutar automatización de Windows.

### 3.2. `tools/implementations/system_tools.py`
- **Herramientas:** `CurrentDatetimeTool`, `LocationTool`, `ParseTimeTool`, `PingTool`, `SetVolumeTool`.
- **Deficiencias:**
  - `parse_relative_time` quedó huérfana al omitirse en `JarvisOrchestrator._register_tools()`.
  - `set_volume` carece de verificación de plataforma (invoca directamente Win32 en cualquier entorno).

### 3.3. `tools/implementations/desktop_tools.py`
- **Herramientas:** 15 herramientas de automatización y documentos.
- **Deficiencias:**
  - 6 herramientas huérfanas: `focus_application`, `get_running_applications`, `open_url`, `open_file`, `open_folder`, `get_active_application`.
  - Dependencia acoplada a Win32 / host local: Al usarse desde un cliente web o móvil, abrir carpetas o enfocar ventanas carece de sentido sin una capa de despacho que notifique al cliente correspondiente.
  - `create_pdf` y `create_docx` guardan en rutas absolutas locales (`Desktop`, `Documents`) pero no devuelven un endpoint HTTP o token para que un cliente web/móvil descargue el archivo generado.

### 3.4. `tools/implementations/memory_tools.py`
- **Herramientas:** `RememberTool`, `RecallTool`, `ForgetMemoryTool`, `GetMemorySummaryTool`, `ClearMemoryTool`, `ExportMemoryTool`.
- **Deficiencias:**
  - `clear_memory` y `export_memory` son huérfanas.
  - `clear_memory` es una acción de alto impacto destructivo que en `SecurityPolicy` figura como `SAFE_ACTIONS` sin requerir confirmación explícita del usuario (`CONFIRMATION_REQUIRED`).
  - La recuperación léxica en `recall_memories` falla ante sinónimos o consultas descriptivas sin coincidencias exactas.

### 3.5. `tools/implementations/music_tools.py`
- **Herramientas:** 10 herramientas de reproducción y cola musical.
- **Deficiencias:**
  - Inconsistencia de clasificación: `recommend_music` está catalogada como `ToolType.QUERY`, pero internamente ejecuta `music_engine.play_recommendations(...)` que altera el estado de la cola y comienza a reproducir música (debe ser `ToolType.ACTION` o no reproducir automáticamente).
  - Manejo de excepciones en `play_query`: si `ytmusicapi` lanza `KeyError` o timeout por bloqueo de red, el mensaje de error retornado es genérico.

### 3.6. `tools/implementations/reminder_tools.py` y `task_tools.py`
- **Herramientas:** 8 herramientas de recordatorios + 5 de tareas.
- **Deficiencias:**
  - 5 herramientas huérfanas: `list_reminders`, `snooze_reminder`, `complete_reminder`, `clear_all_reminders`, `clear_all_tasks`.
  - `create_reminder` y `snooze_reminder` programan trabajos en APScheduler sin comprobar si el canal de notificación (`NOTIFICATIONS`) está permitido.

### 3.7. `tools/implementations/web_tools.py`
- **Herramientas Implementadas:** `ReadWebpageTool` (`read_webpage`) y `WebSearchTool` (`web_search`).
- **Resolución Arquitectónica y Decisión Documentada (Fase 16):**
  1. **Implementación de `read_webpage` (Lectura e Ingesta Web Real):** Se implementó formalmente bajo `ToolType.QUERY`, utilizando `httpx` asíncrono para descarga segura, extracción y saneamiento de texto HTML (removiendo scripts, styles, navs, headers, footers), soporte de longitud configurable y caché semántico local (`CACHE_TTL = 1800s`) para evitar re-descargas innecesarias. Esta es la herramienta principal que el asistente usa para leer, sintetizar y responder sobre el contenido de páginas web.
  2. **Decisión sobre `web_search` (Conservada como Acción de Escritorio Separada):** Se decidió **conservar `web_search` reclasificándola estrictamente a `ToolType.ACTION`** con una descripción no ambigua. Su propósito exclusivo es la automatización visual de escritorio: abrir en el navegador web del equipo del usuario una pestaña con la búsqueda en Google cuando el usuario lo solicite expresamente (ej. "Abre en Google una búsqueda de vuelos a París"). Se eliminó de ella la apertura de URLs arbitrarias (tarea cubierta por `open_url`) y se reservó la ingesta de contenido a `read_webpage`.

---

## 4. RESOLUCIÓN Y MITIGACIÓN IMPLEMENTADA (FASE B COMPLETADA ✅)

Todas las deficiencias identificadas en la auditoría fueron resueltas y verificadas mediante pruebas automatizadas:

1. **B.2.1 Mitigación de Acciones Destructivas:**
   - `clear_memory`, `clear_all_reminders` y `clear_all_tasks` fueron trasladadas a `CONFIRMATION_ACTIONS` en `SecurityPolicy`. Se prohíbe su ejecución no supervisada y se excluyeron del registro directo no interactivo.
2. **B.2.2 Verificación Real de Permisos (`PermissionManager`):**
   - Se añadió verificación de `PermissionManager.is_granted(...)` en `get_location` (`LOCATION`), `set_volume` (`AUTOMATION`) y `create_reminder` (`NOTIFICATIONS`).
3. **B.2.3 Corrección de Clasificación de Herramientas:**
   - `recommend_music` reclasificada de `QUERY` a `ToolType.ACTION` en `music_tools.py`, `TOOL_REGISTRY` y tests.
4. **B.2.4 Capa de Capacidades de Plataforma (`core/platform_capabilities.py`):**
   - Creado módulo `PlatformCapabilities` con catálogo `DESKTOP_ONLY_TOOLS` (`open_url`, `open_file`, `open_folder`, `focus_application`, `get_active_application`, `get_running_applications`, `analyze_screen`).
   - Intercepción en `ToolRouter.execute_tool` y guardado condicional en `JarvisOrchestrator._register_tools()`.
5. **B.2.5 Registro de Huérfanas Universales y Seguras:**
   - Registradas en el orquestador: `parse_relative_time`, `list_reminders`, `snooze_reminder`, `complete_reminder`, `export_memory`.
6. **B.2.6 Roadmap Fase 16 (Lectura Web e Ingesta):**
   - Implementada herramienta `read_webpage` (`ToolType.QUERY`, `httpx`, extracción de texto limpio y caché semántico de 30 min). `web_search` preservada como acción visual de escritorio.
7. **B.2.7 Roadmap Fase 14 (Wake-word en segundo plano):**
   - Implementado `BackgroundWakeWordListener` en `core/wakeword/listener.py` con buffer circular (`collections.deque`), bajo consumo de CPU y respeto a permisos/plataforma.
8. **B.2.8 Roadmap Fase 15 (Visión y análisis de pantalla):**
   - Implementada herramienta `analyze_screen` (`Pillow` / `ImageGrab`, base64, filtro de privacidad estricto que enmascara ventanas con datos sensibles como contraseñas, banca y gestores de credenciales).
9. **B.2.9 Roadmap Fase 17 (Migración a `google.genai`):**
   - Migrado `providers/gemini_provider.py` al SDK oficial moderno `google.genai` con cliente asíncrono nativo (`client.aio.models`), eliminando por completo las advertencias de obsolescencia.
10. **B.2.10 Roadmap Fase 18 (Multi-Step Agent & Briefings):**
    - Implementado `MultiStepPlanner` en `core/multi_step_planner.py` con descomposición de peticiones complejas, verificación interactiva de seguridad y generador de reportes ejecutivos diarios matutinos/vespertinos.
    - Herramientas añadidas: `execute_workflow` (`ToolType.ACTION`) y `get_daily_briefing` (`ToolType.QUERY`).

