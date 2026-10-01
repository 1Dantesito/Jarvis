# PROBLEMAS CONOCIDOS Y MITIGACIONES (KNOWN ISSUES) — JARVIS v2.0

## 1. INTEGRACIÓN CON SPOTIFY CONNECT
- **ID:** `ISS-01`
- **Severidad:** `LOW`
- **Descripción:** La reproducción remota directa mediante Spotify Connect requiere obligatoriamente una cuenta **Spotify Premium** activa y un dispositivo con la app de Spotify en ejecución.
- **Mitigación Implementada:** `SpotifyProvider` detecta el estado `PREMIUM_REQUIRED` o `NO_ACTIVE_DEVICE` y redirige el flujo de reproducción de manera segura a **YouTube Music (IFrame Player)** sin interrumpir la experiencia.

---

## 2. COMPATIBILIDAD DEL MICRÓFONO EN NAVEGADORES
- **ID:** `ISS-02`
- **Severidad:** `LOW`
- **Descripción:** La Web Speech API (`SpeechRecognition`) requiere que la página se sirva bajo `https://` o `http://localhost / 127.0.0.1` y que el usuario conceda permisos en el navegador.
- **Mitigación Implementada:** Detección de soporte al cargar; fallback a entrada de texto instantánea y aviso visual en el icono de micrófono.

---

## 3. LÍMITES DE TASA DE APIS EXTERNAS (RATE LIMITING)
- **ID:** `ISS-03`
- **Severidad:** `MEDIUM`
- **Descripción:** Si la cuota de la API de Anthropic o Gemini se agota temporalmente (código 429), la generación directa se interrumpe.
- **Mitigación Implementada:** Cascada de fallback resiliente en `JarvisOrchestrator` (`Anthropic` $\rightarrow$ `Gemini` $\rightarrow$ `Mock Provider`) evitando caídas del sistema.

---

## 4. VENTANA ACTIVA EN MODO HEADLESS
- **ID:** `ISS-04`
- **Severidad:** `LOW`
- **Descripción:** Al ejecutar pruebas automatizadas en entornos headless o servicios en segundo plano donde no existe ventana en primer plano, `get_active_application()` retorna `title: None`.
- **Mitigación Implementada:** Fallback seguro en `_resolve_contextual_anaphora` y protección contra excepciones `NoneType`.
