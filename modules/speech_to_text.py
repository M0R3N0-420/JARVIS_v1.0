"""
Módulo para transcripción de audio a texto usando Whisper
"""
import whisper
from config import WHISPER_MODEL


class SpeechToText:
    """Clase para convertir audio a texto"""
    
    def __init__(self, model_name=None, logger=None):
        """
        Inicializa el modelo de Whisper
        
        Args:
            model_name (str): Nombre del modelo ('tiny', 'base', 'small', 'medium', 'large')
            logger: Logger opcional
        """
        import time
        
        self.model_name = model_name or WHISPER_MODEL
        self.logger = logger
        
        print(f"Cargando modelo Whisper '{self.model_name}'...")
        start_time = time.time()
        self.model = whisper.load_model(self.model_name)
        load_time = time.time() - start_time
        
        print(f"✅ Modelo '{self.model_name}' cargado correctamente.\n")
        
        if self.logger:
            self.logger.log_model_load("Whisper", self.model_name, load_time)
    
    def transcribe(self, audio_path):
        """
        Transcribe un archivo de audio a texto
        
        Args:
            audio_path (str): Ruta del archivo de audio
            
        Returns:
            str: Texto transcrito
        """
        print("🧠 Transcribiendo audio...")
        result = self.model.transcribe(audio_path)
        texto = result["text"].strip()
        print(f"\n🗒️ Transcripción:\n{texto}\n")
        return texto
    
    def transcribe_with_details(self, audio_path):
        """
        Transcribe con información detallada (segmentos, timestamps, idioma)
        
        Args:
            audio_path (str): Ruta del archivo de audio
            
        Returns:
            dict: Resultado completo de Whisper
        """
        print("🧠 Transcribiendo audio con detalles...")
        result = self.model.transcribe(audio_path)
        return result
    
    def change_model(self, model_name):
        """
        Cambia a un modelo diferente de Whisper
        
        Args:
            model_name (str): Nombre del nuevo modelo
        """
        self.model_name = model_name
        print(f"Cambiando a modelo '{model_name}'...")
        self.model = whisper.load_model(self.model_name)
        print(f"✅ Modelo '{model_name}' cargado.")