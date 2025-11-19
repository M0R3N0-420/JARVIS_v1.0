"""
Módulo para captura y manejo de audio
"""
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import keyboard
from config import (
    SAMPLERATE, AUDIO_CHANNELS, AUDIO_DTYPE, 
    CHUNK_SIZE, RECORDING_KEY, TEMP_AUDIO_FILE
)


class AudioRecorder:
    """Clase para manejar la grabación de audio"""
    
    def __init__(self, logger=None):
        self.samplerate = SAMPLERATE
        self.channels = AUDIO_CHANNELS
        self.dtype = AUDIO_DTYPE
        self.chunk_size = CHUNK_SIZE
        self.recording_key = RECORDING_KEY
        self.output_file = TEMP_AUDIO_FILE
        self.logger = logger  # Logger opcional
    
    def record_while_pressed(self):
        """
        Graba audio mientras se mantiene presionada la tecla configurada.
        
        Returns:
            str: Ruta del archivo de audio guardado
        """
        print(f"Mantén presionada la tecla [{self.recording_key}] para grabar...")
        keyboard.wait(self.recording_key)
        
        print("🎙️ Grabando... (suelta para detener)")
        audio_frames = []
        
        with sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype=self.dtype
        ) as stream:
            while keyboard.is_pressed(self.recording_key):
                data, _ = stream.read(self.chunk_size)
                audio_frames.append(data)
        
        print("🛑 Grabación detenida.")
        
        # Concatenar y guardar
        audio_np = np.concatenate(audio_frames, axis=0)
        write(self.output_file, self.samplerate, audio_np)
        
        print(f"✅ Audio guardado como: {self.output_file}")
        return self.output_file
    
    def set_recording_key(self, key):
        """Permite cambiar la tecla de grabación dinámicamente"""
        self.recording_key = key
        print(f"Tecla de grabación actualizada a: [{key}]")