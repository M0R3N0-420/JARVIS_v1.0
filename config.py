"""
Configuración centralizada del asistente de voz JARVIS
"""
import os

# === CONFIGURACIÓN DE AUDIO ===
SAMPLERATE = 16000
AUDIO_CHANNELS = 1
AUDIO_DTYPE = 'int16'
CHUNK_SIZE = 1024
RECORDING_KEY = "|"

# === RUTAS DE ARCHIVOS ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_AUDIO_FILE = os.path.join(DATA_DIR, "rec.wav")

# Crear carpeta data si no existe
os.makedirs(DATA_DIR, exist_ok=True)

# === MODELOS IA ===
WHISPER_MODEL = "small"  # tiny, base, small, medium, large
OLLAMA_MODEL = "llama3.1:8b"

# === CONFIGURACIÓN TTS ===
TTS_RATE = 200  # Palabras por minuto
TTS_VOLUME = 1.0  # 0.0 a 1.0

# === ROL DEL ASISTENTE ===
ASSISTANT_ROLE = """
Eres un asistente de voz tipo JARVIS. Hablas en español con tono natural, claro y confiado.
Eres útil, proactivo y recuerdas lo que el usuario dice durante la conversación.
Además evita usar emojis en tus respuestas y también evita usar caracteres especiales como * que no se pronuncian al hablar.
"""

# === CONFIGURACIÓN DE BASE DE DATOS ===
DATABASE_PATH = os.path.join(DATA_DIR, "jarvis.db")
ENABLE_AUTO_BACKUP = True
BACKUP_INTERVAL_HOURS = 24  # Backup automático cada 24 horas
MAX_BACKUPS = 7  # Mantener últimos 7 backups

# === CONFIGURACIÓN DE LOGGING ===
import logging

LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_LEVEL = logging.INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_TO_CONSOLE = True
LOG_ROTATION_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_ROTATION_BACKUP_COUNT = 5

# === COMANDOS DEL SISTEMA ===
SYSTEM_COMMANDS = {
    # Navegador
    "abrir navegador": {"action": "open_browser", "args": "chrome"},
    "abrir chrome": {"action": "open_browser", "args": "chrome"},
    
    # Webs
    "abrir youtube": {"action": "open_url", "args": "https://www.youtube.com"},
    "abrir spotify": {"action": "open_url", "args": "https://open.spotify.com"},
    
    # Sistema
    "bloquear pantalla": {"action": "lock_screen"},
    "apagar computadora": {"action": "shutdown"},
    "apagar el equipo": {"action": "shutdown"},
    
    # Utilidades
    "dame la hora": {"action": "get_time"},
    "reproduce música 1": {"action": "open_url", "args": "https://www.youtube.com/watch?v=rBaPwJe3W7c"},
    
    # Aplicaciones específicas
    "abre ableton": {
        "action": "open_app",
        "args": "C:\\Program Files\\Ableton\\Ableton Live 12 Suite\\Ableton Live 12 Suite.exe"
    },
    "abre mezclador": {
        "action": "open_app",
        "args": "D:\\Archivos de Programa\\rekordbox\\rekordbox 7.2.7\\rekordbox.exe"
    }
}