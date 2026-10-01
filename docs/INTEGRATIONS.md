# INTEGRACIONES MULTIMEDIA DE JARVIS

## 1. SPOTIFY WEB API

### Requisitos y Scopes:
- **Client Credentials Flow:** Búsqueda de canciones, metadatos de artistas y álbumes sin sesión de usuario.
- **Authorization Code Flow (OAuth 2.0):** Requerido para control de reproducción activa (`user-read-playback-state`, `user-modify-playback-state`).
- **Restricción de Cuenta Premium:** El control de reproducción (`play`, `pause`, `skip`) a través de Spotify Connect requiere una cuenta **Spotify Premium** activa y un dispositivo/aplicación de Spotify en ejecución.
- **Manejo de Estados:**
  - `NOT_CONNECTED`: Credenciales ausentes en variables de entorno.
  - `AUTH_REQUIRED`: Token de usuario no autorizado.
  - `NO_ACTIVE_DEVICE`: Spotify no está abierto en ningún dispositivo.
  - `AVAILABLE`: Conexión establecida.

---

## 2. YOUTUBE / YOUTUBE MUSIC

### Arquitectura de Descubrimiento y Reproducción:
- **Descubrimiento (Backend):** Utiliza `ytmusicapi` para búsqueda de canciones, álbumes, pistas de artistas y vídeos.
- **Reproducción (Frontend):** Se ejecuta en el cliente mediante **YouTube IFrame Player API**, garantizando el cumplimiento estricto de las directivas de YouTube (sin extracción de audio local).
- **Control de Cola:** JARVIS mantiene una `SmartQueue` en memoria y sincroniza la playlist con el reproductor IFrame mediante callbacks de fin de reproducción (`YT.PlayerState.ENDED`).
