"""
Módulo para síntesis de voz (Text-to-Speech)
"""
import subprocess
import sys
from config import TTS_RATE, TTS_VOLUME


class TextToSpeech:
    """Clase para convertir texto a voz"""
    
    def __init__(self, rate=None, volume=None, logger=None):
        """
        Inicializa el motor TTS
        
        Args:
            rate (int): Velocidad de habla (palabras por minuto)
            volume (float): Volumen (0.0 a 1.0)
            logger: Logger opcional
        """
        self.rate = rate or TTS_RATE
        self.volume = volume or TTS_VOLUME
        self.logger = logger
    
    def speak(self, texto):
        """
        Reproduce texto por voz usando pyttsx3 en proceso separado
        
        Args:
            texto (str): Texto a reproducir
        """
        print("🗣️ Reproduciendo respuesta...")
        
        # Ejecutar en proceso separado para evitar conflictos
        subprocess.run([sys.executable, "-c", f"""
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', {self.rate})
engine.setProperty('volume', {self.volume})
engine.say({repr(texto)})
engine.runAndWait()
"""])
    
    def speak_async(self, texto):
        """
        Reproduce texto en background (no bloquea ejecución)
        
        Args:
            texto (str): Texto a reproducir
        """
        print("🗣️ Reproduciendo respuesta en background...")
        
        subprocess.Popen([sys.executable, "-c", f"""
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', {self.rate})
engine.setProperty('volume', {self.volume})
engine.say({repr(texto)})
engine.runAndWait()
"""])
    
    def set_voice_properties(self, rate=None, volume=None):
        """
        Cambia propiedades de la voz
        
        Args:
            rate (int): Nueva velocidad
            volume (float): Nuevo volumen
        """
        if rate is not None:
            self.rate = rate
            print(f"Velocidad actualizada a: {rate} wpm")
        
        if volume is not None:
            self.volume = volume
            print(f"Volumen actualizado a: {volume}")