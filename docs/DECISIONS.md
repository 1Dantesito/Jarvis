# JARVIS — REGISTRO DE DECISIONES DE ARQUITECTURA (ADR)

> **Documento:** `/docs/DECISIONS.md`  
> **Versión:** 2.0.0  

---

## ADR-001: Unificación del Servidor en Arquitectura Asíncrona (ASGI / FastAPI)
- **Contexto:** Existían dos servidores: un servidor FastAPI en `api/server.py` y un servidor Flask en `app.py`. Flask ejecuta llamadas bloqueantes de I/O (gTTS, ytmusicapi, Gemini), disparando la latencia a más de 5 segundos.
- **Decisión:** Unificar en una arquitectura asíncrona única utilizando FastAPI / ASGI con endpoints HTTP para el frontend y WebSockets / SSE para el flujo continuo de audio y texto.
- **Consecuencias:** Permite streaming token a token, consultas en paralelo de música, y background tasks no bloqueantes.

---

## ADR-002: Reducción de Latencia mediante Streaming y VAD
- **Contexto:** El usuario debía presionar el botón de micrófono para iniciar y detener, enviar el archivo completo a Gemini STT, esperar el texto completo de Gemini y esperar a que gTTS generase un archivo MP3 en disco.
- **Decisión:** 
  1. Integrar VAD (*Voice Activity Detection*) en el cliente para corte automático.
  2. Implementar streaming de respuestas desde el LLM.
  3. Implementar TTS en streaming oracional (<300ms de primer audio).
  4. Habilitar *barge-in* (interrupción instantánea) para cancelar el audio en cuanto el usuario vuelva a hablar.
- **Consecuencias:** Reducción del tiempo hasta el primer audio de ~6s a <1s.

---

## ADR-003: Abstracción Multimodelo con Tool Calling Estructurado
- **Contexto:** En `app.py` se utilizaba regex scraping para extraer bloques JSON de la salida de texto libre de Gemini, provocando fallos de parseo e inconsistencias.
- **Decisión:** Implementar la interfaz abstracta `AIProvider` con soporte nativo de Function Calling / Tool Use tanto para Google Gemini como para Anthropic Claude, con fallback automático si una clave no está disponible.
- **Consecuencias:** Respuestas estructuradas confiables sin depender de trucos de expresiones regulares.

---

## ADR-004: Persistencia Híbrida (SQLite Local + Supabase Cloud)
- **Contexto:** Se usaba `memory_store.json` y llamadas inseguras a Supabase en hilos secundarios sin sincronización de esquema.
- **Decisión:** Utilizar SQLite local (`jarvis.db`) como almacén primario y caché de alta velocidad (disponible 100% offline), con un worker asíncrono que replica cambios a Supabase Cloud en segundo plano.
- **Consecuencias:** Inmunidad a fallos de red o errores de conexión a la nube, con respaldo continuo en Supabase.

---

## ADR-005: NotificationEngine Desacoplado para Alertas del Sistema
- **Contexto:** Los recordatorios solo se guardaban en base de datos sin un proceso activo que los disparara.
- **Decisión:** Implementar un servicio de fondo en segundo plano que monitorea recordatorios pendientes y dispara notificaciones nativas de Windows (*Windows Toast Notifications*) con sonido de alerta sin requerir que la ventana del navegador esté activa.
- **Consecuencias:** JARVIS se convierte en un verdadero asistente de escritorio proactivo.

---

## ADR-006: Política Estricta de Concisión y Brevedad
- **Contexto:** JARVIS emitía explicaciones largas y saludos robóticos innecesarios para tareas rutinarias.
- **Decisión:** Inyectar una regla obligatoria en los prompts del sistema: las acciones y confirmaciones deben limitarse a 1 frase concisa, reservando respuestas detalladas únicamente para consultas informativas explícitas.
- **Consecuencias:** Diálogo fluido, rápido y natural similar a un asistente real de alta gama.
