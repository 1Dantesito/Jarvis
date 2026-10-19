# ☁️ GUÍA DE DESPLIEGUE EN LA NUBE 24/7 (JARVIS SIN PC)

> **Documento:** `/docs/CLOUD_DEPLOYMENT.md`  
> **Objetivo:** Tener JARVIS funcionando 24/7 en Internet gratis sin necesidad de encender la computadora.

---

## 🌟 ¿Cómo funciona?

Al desplegar JARVIS en la nube:
1. **El servidor de JARVIS corre en Internet 24/7:** Aloja la memoria, los motores de IA (Gemini / Claude / OpenRouter), la música y las conversaciones.
2. **Tu computadora puede estar 100% apagada:** No necesitas dejar tu PC prendida en casa ni ejecutar ningún archivo `.bat`.
3. **Tu celular se conecta desde cualquier lugar:** Abres tu aplicación [`JARVIS.apk`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/JARVIS.apk) con datos móviles o Wi-Fi y te responderá al instante.

---

## 🚀 Paso a Paso: Despliegue Gratis en Render.com (3 Minutos)

Render ofrece alojamiento web gratuito con soporte para FastAPI, WebSockets y HTTPS automático.

### 1. Subir tu proyecto a GitHub (o GitLab)
1. Si no lo has hecho, crea un repositorio en [GitHub.com](https://github.com) (puede ser **Privado** para mayor seguridad).
2. Sube los archivos de este proyecto al repositorio.
   *(Nota: `.env` ya está excluido por seguridad en `.gitignore`)*.

### 2. Crear el servicio en Render
1. Entra a [dashboard.render.com](https://dashboard.render.com) e inicia sesión con tu cuenta de GitHub.
2. Pulsa el botón **"New +"** y selecciona **"Web Service"**.
3. Selecciona tu repositorio de JARVIS y pulsa **"Connect"**.
4. Llena los siguientes campos sencillos:
   - **Name:** `jarvis-ai` (o el nombre que prefieras).
   - **Language / Runtime:** `Python 3`
   - **Branch:** `main` (o tu rama principal).
   - **Build Command:**
     ```bash
     pip install -r requirements-cloud.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn api.server:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** `Free` (Gratis).

### 3. Configurar tus Variables de Entorno (API Keys)
En la misma pantalla, baja a la sección **"Environment Variables"** y añade tus claves:
- `GEMINI_API_KEY`: tu clave de Google AI Studio.
- `OPENROUTER_API_KEY`: tu clave de OpenRouter (opcional si usas Gemini).
- `SUPABASE_URL` y `SUPABASE_KEY`: tus claves de base de datos Supabase (opcional para sincronización en la nube).

### 4. Crear el Servicio
Pulsa **"Create Web Service"**.
Render construirá la aplicación e iniciará tu servidor en menos de 2 minutos. Al terminar, te dará una URL pública con HTTPS como:
```text
https://jarvis-ai-xxxx.onrender.com
```

---

## 📱 Conectar tu APK a la Nube

1. Instala [`JARVIS.apk`](file:///c:/Users/6dant/OneDrive/Desktop/Jarvis/JARVIS.apk) en tu celular.
2. Abre la app **JARVIS**.
3. Toca el botón de ajustes (**⚙️**) en la esquina superior derecha.
4. Escribe o pega la URL que te dio Render:
   ```text
   https://jarvis-ai-xxxx.onrender.com
   ```
5. Pulsa **"Conectar"**.

**¡Listo!** A partir de este momento, JARVIS vivirá en la nube 24/7 y podrás hablar con él por voz, escuchar música y consultar tus recuerdos desde cualquier lugar del mundo sin tocar tu computadora.
