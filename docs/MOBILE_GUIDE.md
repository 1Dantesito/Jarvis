# 📱 GUÍA DE USO DE JARVIS EN CELULARES Y POR INTERNET

> **Documento:** `/docs/MOBILE_GUIDE.md`  
> **Versión:** 4.0.0 — Mobile-Ready & Remote Internet Access  
> **Dispositivos compatibles:** iPhone (iOS 14.5+), Android (Chrome 90+), Tablets y iPads

---

## 🌟 ¿Qué es JARVIS Mobile?

JARVIS Mobile te permite llevar a tu asistente contigo a cualquier lugar del mundo desde tu teléfono inteligente, manteniendo **exactamente las mismas funciones que en tu computadora**:
- 🗣️ **Voz y Diálogo en Tiempo Real:** Habla por el micrófono de tu teléfono y escucha las respuestas habladas en streaming continuo (Edge-TTS JorgeNeural).
- 🎵 **Estudio Musical & YouTube:** Reproduce cualquier canción, gestiona la cola y sigue las letras sincronizadas en vivo (LRCLIB) en tu celular.
- 🧠 **Memoria Permanente & Recuerdos:** Consulta y almacena preferencias, gustos y datos importantes sincronizados al instante.
- ⏰ **Recordatorios y Tareas:** Crea alarmas que suenan en tu teléfono con avisos visuales y por voz.
- 🖥️ **Control Remoto de tu PC:** Puedes pedirle a JARVIS desde tu celular *"Abre Chrome en mi computadora"*, *"Sube el volumen de mi PC"* o *"Captura la pantalla"* y se ejecutará en tu PC.
- 📷 **Análisis de Fotos y Documentos:** Adjunta fotos tomadas con la cámara de tu celular o archivos PDF/DOCX para que JARVIS los analice con visión multimodal.

---

## 🚀 Método 1: Inicio Rápido con 1 Clic (Recomendado)

1. En tu computadora, haz doble clic en el archivo:
   ```cmd
   Iniciar_Jarvis_Celular.bat
   ```
2. La terminal de Windows se abrirá, comprobará el servidor e iniciará el **Túnel Seguro de Cloudflare (HTTPS)**.
3. Aparecerá en pantalla:
   - Un **Código QR grande** en arte ASCII.
   - Un enlace público seguro de internet: `https://xxxx.trycloudflare.com`.
   - El enlace de tu red local Wi-Fi: `http://192.168.x.x:5001`.
4. **Apunta la cámara de tu celular** a la pantalla de la computadora y pulsa la notificación emergente para abrir JARVIS.

---

## 📲 Método 2: Desde la Interfaz de la Computadora

Si ya tienes JARVIS abierto en tu computadora (`Iniciar_Jarvis.bat`):
1. En la barra superior, haz clic en el botón con icono de teléfono **"Celular"**.
2. Se abrirá una ventana emergente (*Liquid Glass*) con el **Código QR vectorial** generado en vivo.
3. Puedes hacer clic en **"Activar Túnel Internet (HTTPS)"** para generar una URL mundial si estás fuera de casa, o usar la dirección de tu red Wi-Fi local.
4. Escanéalo con tu celular o copia el enlace.

---

## 🤖 Método 3: Instalación de la Aplicación APK Nativa en Android (`JARVIS.apk`)

Si prefieres tener un archivo `.apk` instalable directamente en Android:

1. El archivo instalador compilado está listo en la raíz del proyecto:
   ```text
   C:\Users\6dant\OneDrive\Desktop\Jarvis\JARVIS.apk (12.3 MB)
   ```
2. **Cómo pasarlo a tu celular:**
   - **Opción A (Desde el navegador del celular):** Cuando tengas JARVIS abierto en el navegador de tu celular o PC, ve al modal "Celular" y pulsa el botón **"Descargar JARVIS.apk"**, o entra directamente a:
     ```text
     http://<TU_IP_LOCAL>:5001/download/jarvis.apk
     ```
   - **Opción B (Por cable, WhatsApp, Drive o Telegram):** Envía el archivo `JARVIS.apk` desde tu PC a tu celular.
3. **Instalación en Android:**
   - Abre el archivo `JARVIS.apk` en tu celular y selecciona **"Instalar"** (si te lo solicita, activa "Permitir instalar aplicaciones desconocidas").
   - Abre la app **JARVIS** con su icono nativo del reactor Arc.
4. **Configuración de Conexión en la App:**
   - En la esquina superior derecha verás un botón de ajustes (**⚙️**).
   - Ingresa el enlace de tu servidor (el enlace HTTPS de Cloudflare como `https://xxxx.trycloudflare.com` o tu IP local `http://192.168.x.x:5001`) y pulsa **"Conectar"**.
   - ¡La app guardará la dirección y se conectará automáticamente a partir de ese momento!

---

## 📦 Método 4: Como Progressive Web App (PWA sin instalar APK)

Al abrir el enlace en tu navegador móvil, puedes instalarlo como una aplicación nativa sin barras del navegador:

### En iPhone / iPad (Safari):
1. Abre el enlace en **Safari**.
2. Toca el botón **Compartir** (el icono de cuadro con flecha hacia arriba en la parte inferior).
3. Desplázate hacia abajo y selecciona **"Agregar a la pantalla de inicio"** (o *"Add to Home Screen"*).
4. Confirma el nombre **JARVIS** y pulsa **"Agregar"**.
5. ¡Listo! Verás el icono futurista de JARVIS en tu pantalla principal.

### En Android (Google Chrome):
1. Abre el enlace en **Chrome**.
2. Toca el menú de los **3 puntos** (arriba a la derecha).
3. Selecciona **"Instalar aplicación"** o **"Agregar a la pantalla principal"**.
4. Confirma la instalación.
5. ¡Listo! JARVIS se abrirá a pantalla completa.

---

## 🔒 ¿Por qué requiere HTTPS (Túnel Cloudflare)?

Los navegadores móviles modernos (Chrome en Android y Safari en iOS) tienen políticas estrictas de seguridad (W3C Secure Contexts):
- El **micrófono** (`getUserMedia` y `SpeechRecognition`) solo funciona bajo conexiones seguras `https://` o `localhost`.
- La instalación como aplicación (**PWA**) solo está permitida bajo `https://`.
- El túnel gratuito de Cloudflare cifra todo el tráfico con certificados SSL oficiales, sin necesidad de abrir puertos en tu router ni exponer tu dirección IP pública de casa.

---

## 🛠️ Preguntas Frecuentes

### ¿Puedo usarlo con datos móviles (4G/5G) fuera de mi casa?
Sí. Mientras la computadora donde corre JARVIS esté encendida con el túnel activo, puedes hablar con JARVIS desde la calle, tu trabajo, transporte o cualquier red Wi-Fi exterior.

### ¿Se modificó algo en la versión de computadora?
No. La versión de escritorio, los atajos de teclado (`Alt + Espacio`), la aplicación nativa PyQt6 (`desktop_app.py`) y el lanzador local (`Iniciar_Jarvis.bat`) permanecen 100% idénticos e intactos.
