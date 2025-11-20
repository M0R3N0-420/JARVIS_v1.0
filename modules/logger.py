"""
Módulo de logging para rastrear eventos del asistente JARVIS
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json


class JarvisLogger:
    """Clase para gestionar el sistema de logging del asistente"""
    
    def __init__(self, log_dir="logs", log_level=logging.INFO):
        """
        Inicializa el sistema de logging
        
        Args:
            log_dir (str): Directorio donde se guardarán los logs
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = log_dir
        self.log_level = log_level
        
        # Crear directorio de logs si no existe
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Crear subdirectorio para sesiones
        self.sessions_dir = os.path.join(self.log_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Configurar loggers
        self.main_logger = self._setup_logger(
            "jarvis_main",
            os.path.join(self.log_dir, "jarvis_main.log")
        )
        
        self.conversation_logger = self._setup_logger(
            "jarvis_conversation",
            os.path.join(self.log_dir, "conversations.log")
        )
        
        self.error_logger = self._setup_logger(
            "jarvis_errors",
            os.path.join(self.log_dir, "errors.log"),
            level=logging.ERROR
        )
        
        self.command_logger = self._setup_logger(
            "jarvis_commands",
            os.path.join(self.log_dir, "commands.log")
        )
        
        # Archivo de sesión actual (ahora en subcarpeta)
        self.session_file = os.path.join(
            self.sessions_dir,
            f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        self.session_data = {
            "start_time": datetime.now().isoformat(),
            "interactions": []
        }
        
        self.main_logger.info("=" * 60)
        self.main_logger.info("Sistema de logging inicializado")
        self.main_logger.info(f"Sesión guardada en: {self.session_file}")
        self.main_logger.info("=" * 60)
    
    def _setup_logger(self, name, log_file, level=None):
        """
        Configura un logger específico
        
        Args:
            name (str): Nombre del logger
            log_file (str): Ruta del archivo de log
            level: Nivel de logging
            
        Returns:
            logging.Logger: Logger configurado
        """
        logger = logging.getLogger(name)
        logger.setLevel(level or self.log_level)
        
        # Evitar duplicación de handlers
        if logger.handlers:
            return logger
        
        # Formato detallado
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para archivo (rotativo: máx 5MB, 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler para consola (solo para logger principal)
        if name == "jarvis_main":
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.WARNING)  # Solo warnings+ en consola
            logger.addHandler(console_handler)
        
        return logger
    
    # === MÉTODOS DE LOGGING POR CATEGORÍA ===
    
    def log_audio_recording(self, status, duration=None, file_path=None):
        """Registra eventos de grabación de audio"""
        if status == "started":
            self.main_logger.info("🎙️ Grabación de audio iniciada")
        elif status == "stopped":
            self.main_logger.info(f"🛑 Grabación detenida. Duración: {duration:.2f}s")
        elif status == "saved":
            self.main_logger.info(f"💾 Audio guardado: {file_path}")
    
    def log_transcription(self, audio_file, transcribed_text, duration=None):
        """Registra transcripciones de audio"""
        self.main_logger.info(f"📝 Transcripción completada en {duration:.2f}s" if duration else "📝 Transcripción completada")
        # Registrar en archivo de conversaciones
        self.conversation_logger.info(f"")
        self.conversation_logger.info(f"--- TRANSCRIPCIÓN ---")
        self.conversation_logger.info(f"Archivo: {audio_file}")
        self.conversation_logger.info(f"👤 Usuario dijo: {transcribed_text}")
        if duration:
            self.conversation_logger.info(f"Duración transcripción: {duration:.2f}s")
    
    def log_command_execution(self, command_keyword, action, result):
        """Registra ejecución de comandos del sistema"""
        # Log en archivo principal
        self.main_logger.info(f"⚙️ Comando ejecutado: {command_keyword}")
        
        # Log detallado en archivo de comandos
        self.command_logger.info(f"")
        self.command_logger.info(f"========================================")
        self.command_logger.info(f"⚙️  COMANDO: '{command_keyword}'")
        self.command_logger.info(f"🔧 ACCIÓN: {action}")
        self.command_logger.info(f"✅ RESULTADO: {result}")
        self.command_logger.info(f"========================================")
        
        # También registrar en conversaciones
        self.conversation_logger.info(f"")
        self.conversation_logger.info(f"⚙️  Comando ejecutado: {command_keyword}")
        self.conversation_logger.info(f"✅ {result}")
    
    def log_ai_response(self, user_input, ai_response, model_name, response_time=None):
        """Registra interacciones con el modelo de IA"""
        # Log en archivo de conversaciones (detallado)
        self.conversation_logger.info(f"")
        self.conversation_logger.info(f"========================================")
        self.conversation_logger.info(f"👤 Usuario preguntó: {user_input}")
        self.conversation_logger.info(f"")
        self.conversation_logger.info(f"🤖 Asistente ({model_name}) respondió:")
        self.conversation_logger.info(f"{ai_response}")
        if response_time:
            self.conversation_logger.info(f"")
            self.conversation_logger.info(f"⏱️  Tiempo de respuesta: {response_time:.2f}s")
        self.conversation_logger.info(f"========================================")
        
        # Log resumido en archivo principal
        if response_time:
            self.main_logger.info(f"🤖 Respuesta IA generada en {response_time:.2f}s")
    
    def log_tts(self, text, duration=None):
        """Registra síntesis de voz"""
        self.main_logger.info(f"🗣️ TTS reproducido: '{text[:50]}...' ({len(text)} caracteres)")
    
    def log_error(self, error_type, error_message, module=None):
        """Registra errores del sistema"""
        error_info = f"❌ ERROR en {module}: {error_type} - {error_message}" if module else f"❌ ERROR: {error_type} - {error_message}"
        self.error_logger.error(error_info)
        self.main_logger.error(error_info)
    
    def log_model_load(self, model_type, model_name, load_time=None):
        """Registra carga de modelos"""
        msg = f"📦 Modelo {model_type} cargado: {model_name}"
        if load_time:
            msg += f" (tiempo: {load_time:.2f}s)"
        self.main_logger.info(msg)
    
    def log_session_start(self):
        """Registra inicio de sesión"""
        self.main_logger.info("🚀 Sesión de JARVIS iniciada")
    
    def log_session_end(self, total_interactions):
        """Registra fin de sesión"""
        self.session_data["end_time"] = datetime.now().isoformat()
        self.session_data["total_interactions"] = total_interactions
        
        # Guardar datos de sesión en JSON
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        self.main_logger.info(f"🏁 Sesión finalizada. Total de interacciones: {total_interactions}")
        self.main_logger.info(f"📊 Datos de sesión guardados en: {self.session_file}")
    
    def log_interaction(self, user_input, response, response_type, duration=None):
        """
        Registra una interacción completa usuario-asistente
        
        Args:
            user_input (str): Entrada del usuario
            response (str): Respuesta del sistema
            response_type (str): 'command' o 'ai'
            duration (float): Duración total de la interacción
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "response": response,
            "type": response_type,
            "duration": duration
        }
        
        self.session_data["interactions"].append(interaction)
        
        # Log en archivo de conversaciones (formato legible)
        self.conversation_logger.info(f"\n{'='*60}")
        self.conversation_logger.info(f"NUEVA INTERACCIÓN [{response_type.upper()}]")
        self.conversation_logger.info(f"Timestamp: {interaction['timestamp']}")
        if duration:
            self.conversation_logger.info(f"Duración total: {duration:.2f}s")
        self.conversation_logger.info(f"{'='*60}\n")
        
        # Log en archivo principal
        log_msg = f"💬 INTERACCIÓN [{response_type.upper()}]: Usuario: '{user_input[:30]}...' | Respuesta: '{response[:30]}...'"
        if duration:
            log_msg += f" | Duración: {duration:.2f}s"
        
        self.main_logger.info(log_msg)
    
    # === MÉTODOS DE ANÁLISIS ===
    
    def get_session_stats(self):
        """
        Obtiene estadísticas de la sesión actual
        
        Returns:
            dict: Estadísticas de la sesión
        """
        total = len(self.session_data["interactions"])
        commands = sum(1 for i in self.session_data["interactions"] if i["type"] == "command")
        ai_responses = sum(1 for i in self.session_data["interactions"] if i["type"] == "ai")
        
        durations = [i["duration"] for i in self.session_data["interactions"] if i.get("duration")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_interactions": total,
            "commands_executed": commands,
            "ai_responses": ai_responses,
            "average_duration": avg_duration,
            "session_duration": (datetime.now() - datetime.fromisoformat(self.session_data["start_time"])).total_seconds()
        }
    
    def print_session_summary(self):
        """Imprime un resumen de la sesión en consola"""
        stats = self.get_session_stats()
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE LA SESIÓN")
        print("=" * 60)
        print(f"⏱️  Duración total: {stats['session_duration']:.1f} segundos")
        print(f"💬 Total de interacciones: {stats['total_interactions']}")
        print(f"⚙️  Comandos ejecutados: {stats['commands_executed']}")
        print(f"🤖 Respuestas de IA: {stats['ai_responses']}")
        print(f"⏳ Tiempo promedio por interacción: {stats['average_duration']:.2f}s")
        print("=" * 60 + "\n")
    
    # === MÉTODOS DE UTILIDAD ===
    
    def set_log_level(self, level):
        """
        Cambia el nivel de logging
        
        Args:
            level: logging.DEBUG, logging.INFO, etc.
        """
        self.main_logger.setLevel(level)
        self.log_level = level
        self.main_logger.info(f"Nivel de logging cambiado a: {logging.getLevelName(level)}")
    
    def cleanup_old_logs(self, days=30):
        """
        Elimina logs antiguos
        
        Args:
            days (int): Eliminar logs más antiguos que X días
        """
        import time
        current_time = time.time()
        
        for filename in os.listdir(self.log_dir):
            filepath = os.path.join(self.log_dir, filename)
            if os.path.isfile(filepath):
                file_age_days = (current_time - os.path.getmtime(filepath)) / 86400
                if file_age_days > days:
                    os.remove(filepath)
                    self.main_logger.info(f"🗑️ Log antiguo eliminado: {filename}")