# [LEGACY / ARCHIVADO]
# Este archivo corresponde a la implementación monolítica obsoleta (Flask v1.0).
# Ha sido archivado en /legacy/ con fines de referencia histórica.
# La arquitectura oficial y unificada de JARVIS v3.0+ corre exclusivamente sobre FastAPI en `api/server.py`.
raise RuntimeError(
    "Este archivo es código legacy archivado y no debe ejecutarse. "
    "Ejecuta JARVIS mediante 'Iniciar_Jarvis.bat' o 'uvicorn api.server:app --port 5001'."
)

import os
import time
import json
import re
import glob
import subprocess
import webbrowser
import urllib.parse
from pathlib import Path
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from gtts import gTTS
from dotenv import load_dotenv
from ytmusicapi import YTMusic
# Import roto intencionalmente de la arquitectura pre-v2:
from legacy_memory_manager_not_found import memory

app = Flask(__name__)
ytmusic = YTMusic()

AUDIO_DIR = os.path.join(app.static_folder, 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

def cleanup_old_audio(max_age_seconds=1800):
    try:
        now = time.time()
        for f in glob.glob(os.path.join(AUDIO_DIR, "response_*.mp3")):
            if os.path.isfile(f) and (now - os.path.getmtime(f)) > max_age_seconds:
                try:
                    os.remove(f)
                except Exception:
                    pass
    except Exception as e:
        print(f"Error limpiando audios: {e}")

cleanup_old_audio(max_age_seconds=0)

# Mapeo de aplicaciones de Windows
SAFE_APPS = {
    'cmd': lambda: subprocess.Popen(['start', 'cmd'], shell=True),
    'terminal': lambda: subprocess.Popen(['start', 'cmd'], shell=True),
    'consola': lambda: subprocess.Popen(['start', 'cmd'], shell=True),
    'notepad': lambda: subprocess.Popen(['notepad.exe']),
    'bloc de notas': lambda: subprocess.Popen(['notepad.exe']),
    'calc': lambda: subprocess.Popen(['calc.exe'], shell=True),
    'calculadora': lambda: subprocess.Popen(['calc.exe'], shell=True),
    'explorer': lambda: subprocess.Popen(['explorer.exe']),
    'explorador': lambda: subprocess.Popen(['explorer.exe']),
    'archivos': lambda: subprocess.Popen(['explorer.exe']),
    'spotify': lambda: subprocess.Popen(['start', 'spotify:'], shell=True),
    'taskmgr': lambda: subprocess.Popen(['taskmgr.exe']),
    'administrador de tareas': lambda: subprocess.Popen(['taskmgr.exe']),
    'browser': lambda: webbrowser.open('https://www.google.com'),
    'navegador': lambda: webbrowser.open('https://www.google.com')
}

def execute_open_app(app_target):
    target = app_target.lower().strip()
    for name, action in SAFE_APPS.items():
        if name in target:
            try:
                action()
                return True, f"Abriendo {name} en tu sistema."
            except Exception as e:
                return False, f"Error al abrir {name}: {e}"
    try:
        os.startfile(app_target)
        return True, f"Iniciando {app_target}..."
    except Exception as e:
        return False, f"No se pudo iniciar la aplicación ({e})."

def execute_web_search(query=None, url=None):
    try:
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return True, f"Abriendo {url} en tu navegador."
        elif query:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            return True, f"Buscando '{query}' en Google."
    except Exception as e:
        return False, f"Error en búsqueda web: {e}"
    return False, "Consulta no especificada."

def execute_list_files(location="desktop"):
    loc = location.lower().strip()
    home = Path.home()
    
    if "doc" in loc:
        target_path = home / "Documents"
    elif "descarga" in loc or "download" in loc:
        target_path = home / "Downloads"
    else:
        target_path = home / "Desktop"

    try:
        if not target_path.exists():
            return True, "El directorio solicitado no existe.", []
        
        items = [f.name for f in target_path.iterdir() if not f.name.startswith('.')]
        items = items[:15]
        
        if items:
            summary = f"Archivos en tu {target_path.name}: " + ", ".join(items)
        else:
            summary = f"Tu carpeta {target_path.name} está vacía."
        return True, summary, items
    except Exception as e:
        return False, f"Error accediendo a archivos: {e}", []

def detect_direct_intent(prompt):
    """Enrutador de alta precisión para acciones directas del sistema."""
    p = prompt.lower().strip()
    
    # Abrir CMD / Terminal
    if re.search(r'\b(abre|abrir|ejecuta|inicia|lanzar|abreme)\s+(el\s+|la\s+)?(cmd|consola|terminal|símbolo del sistema)\b', p):
        return {"intent": "open_app", "app": "cmd", "reply": "Abriendo la consola de comandos en tu pantalla, señor."}
    
    # Abrir Calculadora
    if re.search(r'\b(abre|abrir|ejecuta|inicia|abreme)\s+(la\s+)?(calc|calculadora)\b', p):
        return {"intent": "open_app", "app": "calc", "reply": "Abriendo la calculadora en tu pantalla."}
    
    # Abrir Bloc de Notas
    if re.search(r'\b(abre|abrir|ejecuta|inicia|abreme)\s+(el\s+)?(bloc de notas|notepad)\b', p):
        return {"intent": "open_app", "app": "notepad", "reply": "Abriendo el Bloc de notas."}

    # Abrir Explorador de Archivos
    if re.search(r'\b(abre|abrir|ejecuta|inicia|abreme)\s+(el\s+)?(explorador|explorador de archivos)\b', p):
        return {"intent": "open_app", "app": "explorer", "reply": "Abriendo el Explorador de archivos."}

    # Abrir Spotify
    if re.search(r'\b(abre|abrir|ejecuta|inicia|abreme)\s+spotify\b', p):
        return {"intent": "open_app", "app": "spotify", "reply": "Iniciando Spotify en tu equipo."}

    # Listar Archivos
    if re.search(r'\b(qu[eé]\s+(archivos|documentos|cosas)\s+(tengo|hay)\s+en\s+el\s+escritorio|ver\s+escritorio|listar\s+escritorio|archivos\s+del\s+escritorio)\b', p):
        return {"intent": "list_files", "location": "desktop", "reply": "Consultando los archivos en tu escritorio:"}

    # Búsqueda Web
    if re.search(r'\b(busca|buscar|googlea)\s+(en\s+google\s+|en\s+internet\s+)?(.+)', p):
        m = re.search(r'\b(busca|buscar|googlea)\s+(en\s+google\s+|en\s+internet\s+)?(.+)', p)
        if m and ("noticias" in p or "google" in p or "internet" in p or "web" in p):
            query = m.group(3).strip()
            return {"intent": "web_search", "query": query, "reply": f"Buscando '{query}' en Google."}

    return None

def build_system_instruction():
    memory_context = memory.get_memory_prompt_block()
    
    return f"""{memory_context}

Eres JARVIS, un asistente de inteligencia artificial leal, avanzado y humano para la computadora personal de tu usuario.
TIENES ACCESO DIRECTO A EJECUTAR HERRAMIENTAS EN EL SISTEMA DE TU USUARIO.
SIEMPRE que el usuario pida música o una acción, debes generar un bloque JSON:

1. MÚSICA / PLAYLISTS (1 a 15 canciones):
```json
{{"intent": "music", "songs": ["Cancion 1 - Artista", "Cancion 2 - Artista"], "reply": "Enseguida, aquí tienes tu música."}}
```

2. ABRIR APLICACIÓN LOCAL (cmd, notepad, calc, spotify, explorer, taskmgr):
```json
{{"intent": "open_app", "app": "cmd|notepad|calc|spotify|explorer", "reply": "Abriendo la aplicación en tu pantalla, señor."}}
```

3. BÚSQUEDAS WEB:
```json
{{"intent": "web_search", "query": "tema a buscar", "reply": "Buscando en Google enseguida."}}
```

4. CONSULTAR ARCHIVOS LOCALES:
```json
{{"intent": "list_files", "location": "desktop|documents|downloads", "reply": "Aquí están los archivos de tu carpeta."}}
```

5. APRENDER DATOS PERSONALES:
```json
{{"intent": "learn_fact", "key": "nombre|musica|hobby|profesion", "value": "valor aprendido", "reply": "Entendido, lo recordaré."}}
```

Si es solo conversación o preguntas generales, responde en texto plano de forma inteligente, cálida y natural sin JSON."""

conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided', 'text': ''}), 400
    
    audio_file = request.files['audio']
    audio_bytes = audio_file.read()
    
    if not audio_bytes:
        return jsonify({'error': 'Empty audio file', 'text': ''}), 400

    try:
        prompt = "Transcribe el texto hablado en este audio en español. Devuelve ÚNICAMENTE el texto reconocido."
        audio_part = {
            "mime_type": "audio/webm",
            "data": audio_bytes
        }
        
        transcribe_model = genai.GenerativeModel(MODEL_NAME)
        response = transcribe_model.generate_content([audio_part, prompt])
        transcription = response.text.strip() if response and response.text else ""
        return jsonify({'text': transcription})
    except Exception as e:
        print(f"Error en /api/transcribe: {e}")
        return jsonify({'error': str(e), 'text': ''}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    global conversation_history
    cleanup_old_audio()
    data = request.json or {}
    user_prompt = data.get('prompt', '').strip()
    
    if not user_prompt:
        return jsonify({'error': 'El mensaje no puede estar vacío'}), 400

    print(f"[Jarvis] Usuario: {user_prompt}")
    
    # Extraer hechos personales en segundo plano
    memory.extract_facts_background(user_prompt, genai.GenerativeModel(MODEL_NAME))

    action_type = None
    action_detail = None
    playlist_ids = None
    spoken_reply = ""

    # 1. Verificar si es una acción directa del sistema
    direct_action = detect_direct_intent(user_prompt)
    if direct_action:
        intent = direct_action.get('intent')
        custom_reply = direct_action.get('reply')

        if intent == 'open_app':
            app_name = direct_action.get('app')
            ok, msg = execute_open_app(app_name)
            action_type = 'system_app'
            action_detail = msg
            spoken_reply = custom_reply or msg

        elif intent == 'web_search':
            query = direct_action.get('query')
            ok, msg = execute_web_search(query=query)
            action_type = 'web_search'
            action_detail = msg
            spoken_reply = custom_reply or msg

        elif intent == 'list_files':
            location = direct_action.get('location', 'desktop')
            ok, msg, items = execute_list_files(location=location)
            action_type = 'file_system'
            action_detail = msg
            spoken_reply = f"{custom_reply} {msg}"

    # 2. Si no es una acción directa predefinida, consultar a Gemini
    if not spoken_reply:
        try:
            sys_inst = build_system_instruction()
            model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=sys_inst)

            contents = []
            for msg in conversation_history[-4:]:
                contents.append(msg)
            contents.append({"role": "user", "parts": [user_prompt]})

            response = model.generate_content(contents)
            reply_text = response.text.strip() if response and response.text else "A su disposición, señor."
            spoken_reply = reply_text

            json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', reply_text)
            if not json_match:
                json_match = re.search(r'(\{\s*"intent"\s*:\s*"[a-zA-Z_]+"[\s\S]*?\})', reply_text)

            if json_match:
                try:
                    action_data = json.loads(json_match.group(1))
                    intent = action_data.get('intent')
                    custom_reply = action_data.get('reply')

                    if intent == 'music' and action_data.get('songs'):
                        songs = action_data['songs']
                        video_ids = []
                        for song in songs:
                            try:
                                res = ytmusic.search(song, filter="songs", limit=1)
                                if res and 'videoId' in res[0]:
                                    video_ids.append(res[0]['videoId'])
                            except Exception as se:
                                print(f"Error buscando canción {song}: {se}")
                        
                        if video_ids:
                            playlist_ids = video_ids
                            action_type = 'music'
                            action_detail = f"{len(video_ids)} canciones preparadas"
                            spoken_reply = custom_reply or f"Enseguida. He preparado una lista con {len(video_ids)} canciones."
                        else:
                            spoken_reply = "No logré encontrar esas canciones en este momento."

                    elif intent == 'open_app' and action_data.get('app'):
                        app_name = action_data['app']
                        ok, msg = execute_open_app(app_name)
                        action_type = 'system_app'
                        action_detail = msg
                        spoken_reply = custom_reply or msg

                    elif intent == 'web_search':
                        query = action_data.get('query')
                        url = action_data.get('url')
                        ok, msg = execute_web_search(query=query, url=url)
                        action_type = 'web_search'
                        action_detail = msg
                        spoken_reply = custom_reply or msg

                    elif intent == 'list_files':
                        location = action_data.get('location', 'desktop')
                        ok, msg, items = execute_list_files(location=location)
                        action_type = 'file_system'
                        action_detail = msg
                        spoken_reply = f"{custom_reply} {msg}" if custom_reply else msg

                    elif intent == 'learn_fact':
                        key = action_data.get('key', 'fact')
                        val = action_data.get('value', '')
                        if val:
                            memory.update_profile(key, val)
                            memory.add_memory_entry(f"{key}: {val}", category="profile")
                        action_type = 'memory'
                        action_detail = f"Memoria actualizada: {key}"
                        spoken_reply = custom_reply or "Dato guardado en mi memoria."

                except Exception as pe:
                    print(f"[Jarvis] Error procesando JSON: {pe}")

        except Exception as e:
            print(f"Error procesando comando: {e}")
            return jsonify({
                'text': 'Ocurrió un inconveniente temporal. Intenta de nuevo en unos momentos.',
                'error': str(e)
            }), 500

    # Guardar en memoria de sesión
    conversation_history.append({"role": "user", "parts": [user_prompt]})
    conversation_history.append({"role": "model", "parts": [spoken_reply]})

    # Generar TTS
    timestamp = int(time.time() * 1000)
    filename = f"response_{timestamp}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    audio_url = None

    try:
        clean_speech = re.sub(r'[*#_`]', '', spoken_reply)
        tts = gTTS(text=clean_speech, lang='es', tld='com.mx')
        tts.save(filepath)
        audio_url = f"/static/audio/{filename}"
    except Exception as tts_err:
        print(f"TTS Error: {tts_err}")

    return jsonify({
        'text': spoken_reply,
        'audio_url': audio_url,
        'playlist': playlist_ids,
        'action_type': action_type,
        'action_detail': action_detail
    })

@app.route('/api/profile', methods=['GET'])
def get_profile():
    return jsonify(memory.local_memory)

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'ok', 'message': 'Conversación reiniciada.'})

if __name__ == '__main__':
    print("=====================================================")
    print("   JARVIS DESKTOP & SUPABASE AGENT INICIADO          ")
    print("   Disponible en: http://localhost:5001              ")
    print("=====================================================")
    app.run(host='0.0.0.0', port=5001, debug=False)
