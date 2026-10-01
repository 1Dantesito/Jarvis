# JARVIS — GUÍA MAESTRA DE DESARROLLO PARA AGENTES (AGENTS.md)

> **Documento:** `/AGENTS.md`  
> **Propósito:** Reglas obligatorias para cualquier modelo o ingeniero trabajando en JARVIS.

---

## 1. REGLAS FUNDAMENTALES DE INGENIERÍA

1. **PROHIBIDO REESCRIBIR A CIEGAS:** Antes de modificar un componente, analiza el código existente, sus dependencias y las pruebas asociadas.
2. **POLÍTICA DE BREVEDAD:** JARVIS debe responder con una sola frase concisa para acciones y confirmaciones. No agregues preámbulos innecesarios ni frases de relleno.
3. **NO SIMULAR CAPACIDADES:** Nunca agregues un elemento en la UI o un mensaje de éxito si la acción en el sistema operativo o en la API no fue completada con éxito.
4. **STREAMING Y ASINCRONÍA:** Todo I/O de red (LLM, TTS, YouTube Music, Supabase) debe ser asíncrono y preferir streaming para minimizar la latencia.
5. **SEGURIDAD DE SECRETOS:** Nunca agregues API keys o tokens a archivos de código, logs o commits. Utiliza siempre `.env` y variables de entorno.

---

## 2. ESTRUCTURA DE DIRECTORIOS ESTÁNDAR

```
Jarvis/
├── core/                       # Núcleo del asistente
│   ├── orchestrator.py         # Orquestador central
│   ├── ai_provider.py          # Interfaz abstracta para LLMs
│   ├── context_engine.py       # Contexto espacio-temporal y ubicación
│   ├── memory_manager.py       # Memoria SQLite + Supabase Sync
│   ├── database.py             # Modelos SQLAlchemy y conexión local
│   └── notification_engine.py  # Planificador y alertas Windows Toast
├── providers/                  # Implementaciones de LLMs y servicios
│   ├── gemini_provider.py      # Google Gemini 1.5/2.0 Flash
│   ├── anthropic_provider.py   # Anthropic Claude 3.5/3.7
│   └── mock_provider.py        # Fallback local offline
├── tools/                      # Herramientas del sistema
│   ├── router.py               # ToolRouter y BaseTool
│   └── implementations/
│       ├── system_tools.py     # Hora, fecha, ping
│       ├── desktop_tools.py    # Control de aplicaciones y archivos
│       ├── reminder_tools.py   # Gestión de recordatorios
│       ├── task_tools.py       # Gestión de tareas
│       ├── memory_tools.py     # Búsqueda y guardado de memoria
│       ├── web_tools.py        # Búsquedas en Google e investigación
│       └── music_tools.py      # YouTube Music y cola continua
├── api/                        # Servidor unificado FastAPI / ASGI
│   └── server.py               # Rutas REST, WebSockets, SSE y static
├── static/                     # Frontend estático
│   ├── script.js               # Lógica cliente, VAD, Barge-in, YouTube
│   ├── style.css               # Estilos Neumorphic / Glassmorphic
│   └── effects.js              # Efecto boba/bubbles animado ligero
├── templates/                  # Vistas HTML
│   └── index.html              # Plantilla principal
├── tests/                      # Suite de pruebas automatizadas
│   ├── test_ai.py
│   ├── test_tools.py
│   ├── test_memory.py
│   ├── test_latency.py
│   └── test_full_capabilities.py
├── docs/                       # Documentación técnica
│   ├── AUDIT.md
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   └── DECISIONS.md
├── Iniciar_Jarvis.bat           # Launcher 1-clic para Windows
├── .env.example                # Plantilla de variables de entorno
└── requirements.txt            # Dependencias del proyecto
```

---

## 3. PROTOCOLO DE TRABAJO POR FASES

- No avances automáticamente entre fases.
- Al culminar una fase:
  1. Ejecuta las pruebas automatizadas correspondientes.
  2. Verifica que no haya regresiones en funciones previas.
  3. Documenta los cambios realizados.
  4. Detente y espera confirmación del usuario para avanzar.
