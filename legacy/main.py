# [LEGACY / ARCHIVADO]
# Este archivo corresponde al prototipo CLI inicial (JARVIS v1.0).
# Ha sido archivado en /legacy/ con fines de referencia histórica.
# La arquitectura oficial y unificada de JARVIS v3.0+ corre exclusivamente sobre FastAPI en `api/server.py`.
raise RuntimeError(
    "Este archivo es código legacy archivado y no debe ejecutarse. "
    "Ejecuta JARVIS mediante 'Iniciar_Jarvis.bat' o 'uvicorn api.server:app --port 5001'."
)

import os
import speech_recognition as sr
from gtts import gTTS
import pygame
import google.generativeai as genai
from dotenv import load_dotenv
# Cargar variables de entorno
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: No se encontró la API Key de Gemini en el archivo .env")
    exit(1)

# Configurar Gemini
genai.configure(api_key=GEMINI_API_KEY)
# Usar el modelo gemini-1.5-flash por ser rápido e ideal para asistentes de voz
model = genai.GenerativeModel('gemini-1.5-flash')

# Inicializar motor de audio
pygame.mixer.init()

def generate_and_play_audio(text):
    """Genera audio con gTTS y lo reproduce con pygame."""
    print(f"Jarvis: {text}")
    audio_file = "response.mp3"
    
    # Generar el audio en español
    tts = gTTS(text=text, lang='es', tld='com.mx') # tld='com.mx' para acento latino, 'es' para España
    tts.save(audio_file)
    
    # Reproducir audio
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    
    # Esperar a que termine de hablar
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
    pygame.mixer.music.unload()
    # Limpiar el archivo de audio temporal
    try:
        os.remove(audio_file)
    except Exception:
        pass

def speak(text):
    generate_and_play_audio(text)

def listen():
    """Escucha el micrófono y devuelve el texto reconocido."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nAjustando ruido ambiental...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Escuchando...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            print("Procesando...")
            # Usar Google Web Speech API
            text = recognizer.recognize_google(audio, language="es-ES")
            print(f"Tú: {text}")
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("No pude entender lo que dijiste.")
            return ""
        except sr.RequestError as e:
            print(f"No se pudo conectar al servicio de reconocimiento de voz: {e}")
            return ""
        except Exception as e:
            print(f"Error al escuchar: {e}")
            return ""

def think(prompt):
    """Envía el texto a Gemini y devuelve la respuesta."""
    try:
        # Añadimos un pequeño contexto para que actúe como Jarvis
        full_prompt = (
            "Eres Jarvis, un asistente virtual de inteligencia artificial muy útil, conciso y amigable. "
            "Responde a la siguiente entrada del usuario de manera breve para que la respuesta pueda ser hablada y no te extiendas demasiado:\n"
            f"{prompt}"
        )
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Error al pensar: {e}")
        return "Lo siento, tuve un problema al procesar tu solicitud."

def main():
    speak("Iniciando sistemas en línea. Hola, soy Jarvis. ¿En qué te puedo ayudar hoy?")
    
    while True:
        user_input = listen()
        
        if user_input:
            user_input_lower = user_input.lower()
            if "adiós" in user_input_lower or "apágate" in user_input_lower or "salir" in user_input_lower or "hasta luego" in user_input_lower:
                speak("Apagando sistemas. Hasta luego.")
                break
            
            # Jarvis piensa una respuesta
            response = think(user_input)
            
            # Jarvis dice la respuesta
            speak(response)

if __name__ == "__main__":
    main()
