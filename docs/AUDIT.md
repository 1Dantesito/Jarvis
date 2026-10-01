# JARVIS — AUDITORÍA TÉCNICA Y DIAGNÓSTICO PROFUNDO (FASE 1)

> **Fecha:** 2026-08-17  
> **Estado:** Fase 1 — Auditoría Completa Finalizada  
> **Equipo:** Senior Software Engineering & AI Agents Architecture  

---

## 1. RESUMEN EJECUTIVO

Se ha realizado una inspección exhaustiva de todo el repositorio y las implementaciones existentes de **JARVIS**.

### Hallazgos Principales:
1. **Arquitectura Fragmentada (Dual Core Disconnect):** Existen dos sistemas completamente desconectados en el proyecto:
   - **Sistema A (`api/server.py` + `core/`):** FastAPI + Anthropic/MockProvider + SQLite (`jarvis.db`) + `ToolRouter` (Time, Memory, Reminder, Task).
   - **Sistema B (`app.py`):** Flask + Gemini (`google.generativeai`) + `memory_manager.py` (JSON + Supabase) + `ytmusicapi` + `gTTS`.
   El launcher actual ejecuta el **Sistema B**, dejando inactivas todas las herramientas de tareas, recordatorios y base de datos SQL del **Sistema A**.
2. **Latencia Crítica de Voz (4 a 9 segundos):** Pipeline 100% secuencial y bloqueante sin streaming, sin detección de actividad de voz (VAD) y sin capacidad de interrupción (*barge-in*).
3. **Verbosidad Descontrolada:** El prompt del sistema no impone reglas de brevedad ni distinción entre tipos de respuesta (Acción, Confirmación, Conversación, Investigación).
4. **Falsas Capacidades y Herramientas Desconectadas:** Los recordatorios carecen de motor de ejecución (*NotificationEngine* / *Scheduler*). Las búsquedas de música hacen peticiones HTTP síncronas en bucle. El control de apps es un mapeo frágil sin gestión de procesos.
5. **Carencia de Contexto Espacio-Temporal:** Ni la fecha/hora actual, ni la zona horaria del sistema, ni la ubicación se inyectan en el prompt del modelo en el servidor activo.

---

## 2. MATRIZ DE PROBLEMAS IDENTIFICADOS

| ID | Categoría | Problema | Severidad | Prioridad |
|---|---|---|---|---|
| **AUD-01** | Arquitectura | Doble backend desconectado (`app.py` vs `core/orchestrator.py`) | **CRITICAL** | P0 |
| **AUD-02** | Voz / Latencia | Pipeline de audio bloqueante (sin streaming, gTTS a disco, STT síncrono) | **CRITICAL** | P0 |
| **AUD-03** | Voz / UX | Imposibilidad de interrumpir a JARVIS mientras habla (sin barge-in) | **HIGH** | P1 |
| **AUD-04** | LLM / Prompts | Verbosidad excesiva y falta de políticas de respuesta concisa | **HIGH** | P1 |
| **AUD-05** | Contexto | Carencia de inyección de fecha, hora, zona horaria y ubicación | **HIGH** | P1 |
| **AUD-06** | Productividad | Recordatorios y tareas no poseen motor proactivo de notificación | **CRITICAL** | P0 |
| **AUD-07** | Memoria | Doble almacén divergente (SQLite vs JSON+Supabase) y extracción redundante | **MEDIUM** | P2 |
| **AUD-08** | OS / Desktop | Automatización de escritorio limitada a 5 alias fijos sin control de ciclo de vida | **MEDIUM** | P2 |
| **AUD-09** | Música | Búsqueda secuencial bloqueante de canciones y falta de auto-encolado continuo | **MEDIUM** | P2 |
| **AUD-10** | Seguridad | Claves y rutas en texto plano sin validación estricta de permisos de SO | **HIGH** | P1 |
| **AUD-11** | UI / UX | Espacio vacío excesivo, ausencia de estados claros (Listening, Thinking, Speaking) | **MEDIUM** | P2 |

---

## 3. DETALLE DE PROBLEMAS Y DIAGNÓSTICO

---

### [AUD-01] CRITICAL: Fragmentación del Backend
- **Archivos:** `app.py`, `api/server.py`, `core/orchestrator.py`
- **Causa:** En iteraciones previas se construyó un orquestador modular basado en FastAPI y SQLite en `core/`, pero luego se desarrolló un servidor Flask monolítico en `app.py` para la interfaz gráfica y YouTube Music.
- **Impacto:** Las herramientas creadas en `core/tools/implementations/` (recordatorios, tareas, base de datos SQLite) no son accesibles desde la interfaz web actual.
- **Solución Propuesta:** Unificar el backend en una arquitectura única basada en FastAPI/ASGI con soporte nativo de WebSockets y SSE para streaming, integrando todos los proveedores y herramientas en un solo pipeline.
- **Riesgo:** Bajo si se preservan los endpoints REST y la interfaz web existente.

---

### [AUD-02] CRITICAL: Latencia Extrema en el Pipeline de Voz
- **Archivos:** `static/script.js`, `app.py`
- **Causa:** 
  1. El cliente graba el audio completo antes de enviarlo por POST HTTP.
  2. El servidor procesa todo el archivo `.webm` con Gemini STT.
  3. El servidor ejecuta Gemini LLM de forma síncrona.
  4. El servidor llama síncronamente a Google Translate TTS (`gTTS`) y lo guarda en disco (`response_*.mp3`).
  5. El cliente descarga el archivo y lo reproduce.
- **Impacto:** Tiempo total de respuesta de 4 a 9 segundos. Sensación de lentitud y poca naturalidad.
- **Solución Propuesta:**
  - Implementar streaming de tokens desde el LLM.
  - Implementar TTS en streaming (Web Speech API optimizada / Edge-TTS de baja latencia con <300ms).
  - VAD (Voice Activity Detection) para corte automático al terminar de hablar.
- **Riesgo:** Medio (requiere coordinación cliente-servidor).

---

### [AUD-03] HIGH: Ausencia de Interrupción de Voz (Barge-in)
- **Archivos:** `static/script.js`
- **Causa:** El reproductor de audio HTML5 no detiene la reproducción si el usuario activa el micrófono o comienza a hablar.
- **Impacto:** Voces superpuestas y frustración del usuario.
- **Solución Propuesta:** Event listener que aborte inmediatamente la reproducción de audio (`audio.pause()`, `speechSynthesis.cancel()`) en cuanto se detecte activación del micrófono o entrada de texto.
- **Riesgo:** Bajo.

---

### [AUD-04] HIGH: Verbosidad Descontrolada del Asistente
- **Archivos:** `app.py`, `core/orchestrator.py`
- **Causa:** Los system prompts no establecen límites de longitud ni especifican modos de respuesta según el tipo de intención.
- **Impacto:** Respuestas de varios párrafos para acciones simples como "abre la calculadora" o "¿qué hora es?".
- **Solución Propuesta:** Inyectar una estricta política de respuesta:
  - *Acción simple:* Máximo 1 frase ("Abriendo la calculadora.").
  - *Confirmación:* 1 frase ("Listo, recordatorio guardado para las 5.").
  - *Pregunta puntual:* Respuesta directa y breve.
  - *Investigación:* Estructurada y concisa.
- **Riesgo:** Muy bajo.

---

### [AUD-05] HIGH: Carencia de Contexto Espacio-Temporal
- **Archivos:** `app.py`, `core/orchestrator.py`
- **Causa:** El system prompt no incluye la hora actual, día de la semana, zona horaria ni ubicación del usuario.
- **Impacto:** El LLM inventa la hora o falla al calcular fechas relativas como "mañana a las 6" o "el próximo viernes".
- **Solución Propuesta:** Crear un generador de contexto dinámico `ContextEngine` que inyecte en cada turno: `current_datetime`, `timezone`, `day_of_week`, y `location` (vía `LocationProvider`).
- **Riesgo:** Muy bajo.

---

### [AUD-06] CRITICAL: Recordatorios y Tareas Sin Motor Proactivo
- **Archivos:** `tools/implementations/reminder_tools.py`, `core/database.py`
- **Causa:** Los recordatorios se insertan como texto plano en una tabla SQLite, pero no existe ningún proceso en segundo plano (daemon/scheduler) que evalúe si la hora ya se cumplió.
- **Impacto:** Los recordatorios jamás se notifican proactivamente.
- **Solución Propuesta:** Implementar `NotificationEngine` respaldado por `APScheduler` o `asyncio.create_task` con notificaciones nativas de Windows (Toast notifications) y audio de alerta.
- **Riesgo:** Bajo.

---

### [AUD-07] MEDIUM: Almacén de Memoria Divergente
- **Archivos:** `memory_manager.py`, `core/memory.py`, `core/supabase_client.py`
- **Causa:** Coexisten tres implementaciones distintas: `memory_store.json`, SQLite `jarvis.db` y llamadas a Supabase.
- **Impacto:** Inconsistencias de datos, riesgo de escrituras concurrentes en JSON sin locks.
- **Solución Propuesta:** Unificar la memoria en un `MemoryManager` único: SQLite local como caché inmediata y replicación asíncrona hacia Supabase Cloud.
- **Riesgo:** Bajo.

---

### [AUD-08] MEDIUM: Automatización de Escritorio Limitada y No Segura
- **Archivos:** `app.py` (función `SAFE_APPS`, `execute_open_app`)
- **Causa:** Mapeo manual de strings con `subprocess.Popen` sin validación de salida, sin capacidad de cerrar procesos y sin verificación de estado de éxito.
- **Impacto:** No se pueden cerrar apps, no se sabe si fallaron al abrirse, y no hay control granular de permisos.
- **Solución Propuesta:** Crear `DesktopAutomationProvider` con lista blanca estricta (Safe vs Dangerous), seguimiento de PIDs mediante `psutil` y confirmación para acciones destructivas.
- **Riesgo:** Bajo.

---

### [AUD-09] MEDIUM: Búsqueda y Reproducción Musical Ineficiente
- **Archivos:** `app.py` (búsqueda de canciones en bucle síncrono `ytmusic.search`)
- **Causa:** Si el modelo genera 10 canciones, el backend realiza 10 llamadas HTTP secuenciales antes de responder.
- **Impacto:** Latencia de hasta 10 segundos adicionales por petición musical. Cuando la canción termina, la música se detiene.
- **Solución Propuesta:**
  - Búsqueda paralela con `asyncio.gather`.
  - Crear `MusicQueue` y `RecommendationEngine` que precargue pistas relacionadas y mantenga la reproducción continua.
- **Riesgo:** Bajo.

---

### [AUD-10] HIGH: Seguridad de Credenciales y Permisos
- **Archivos:** `.env`, `core/supabase_client.py`
- **Causa:** Variables de entorno expuestas previamente en texto plano.
- **Impacto:** Riesgo de filtración de claves administrativas de Supabase o Gemini.
- **Solución Propuesta:** Mantener `.env` fuera del control de versiones, proporcionar `.env.example` sanitizado y validar variables al inicio.
- **Riesgo:** Cero.

---

### [AUD-11] MEDIUM: Interfaz Visual con Espacio Desaprovechado
- **Archivos:** `templates/index.html`, `static/style.css`
- **Causa:** Contenedor central con proporciones estáticas, carencia de fondo dinámico interactivo y falta de paneles laterales para tareas, recordatorios y ajustes.
- **Impacto:** Sensación de aplicación estática o vacía.
- **Solución Propuesta:**
  - Recuperar la estética de burbujas suaves animadas (*boba background*) con CSS/Canvas ligero.
  - Añadir indicadores de estado reactivos (IDLE, LISTENING, THINKING, SPEAKING, ERROR).
  - Incluir panel de control de tareas y configuración de permisos.
- **Riesgo:** Bajo.

---

## 4. CONCLUSIÓN DE LA AUDITORÍA

El proyecto cuenta con bases funcionales sólidas (integración con Gemini, Supabase, YouTube Music, gTTS y frontend interactivo), pero sufre de fragmentación entre dos backends y cuellos de botella severos de latencia y sincronización.

Procederemos a documentar la nueva arquitectura objetivo, roadmap, decisiones técnicas y pautas para agentes antes de iniciar cualquier modificación de código.
