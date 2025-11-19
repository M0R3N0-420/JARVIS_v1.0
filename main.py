"""
Asistente de Voz JARVIS - Versión Modular con Logging y Base de Datos
Punto de entrada principal del programa
"""
import time
from modules import (
    AudioRecorder,
    SpeechToText,
    TextToSpeech,
    AIEngine,
    CommandExecutor,
    JarvisLogger,
    DatabaseManager
)


class JarvisAssistant:
    """Clase principal que orquesta todos los módulos"""
    
    def __init__(self):
        """Inicializa todos los módulos del asistente"""
        print("=" * 60)
        print("🤖 JARVIS - Asistente de Voz Inteligente")
        print("=" * 60 + "\n")
        
        # Inicializar sistema de logging PRIMERO
        self.logger = JarvisLogger()
        self.logger.log_session_start()
        
        # Inicializar base de datos
        self.db = DatabaseManager(logger=self.logger)
        self.session_id = self.db.create_session()
        
        # Inicializar módulos con logger
        try:
            self.audio_recorder = AudioRecorder(logger=self.logger)
            self.speech_to_text = SpeechToText(logger=self.logger)
            self.text_to_speech = TextToSpeech(logger=self.logger)
            self.ai_engine = AIEngine(logger=self.logger)
            self.command_executor = CommandExecutor(logger=self.logger)
            
            # Cargar preferencias del usuario desde BD
            self._load_user_preferences()
            
            print("=" * 60)
            print("✅ Todos los módulos cargados correctamente")
            print("=" * 60 + "\n")
        
        except Exception as e:
            self.logger.log_error("InitializationError", str(e), module="JarvisAssistant")
            self.db.log_error("InitializationError", str(e), module="JarvisAssistant")
            raise
        
        # Contador de interacciones
        self.interaction_count = 0
        self.command_count = 0
        self.ai_response_count = 0
    
    def _load_user_preferences(self):
        """Carga preferencias del usuario desde la base de datos"""
        preferences = self.db.get_all_preferences()
        
        if preferences:
            print(f"📋 Preferencias cargadas: {len(preferences)} configuraciones\n")
            
            # Aplicar preferencias si existen
            if 'tts_rate' in preferences:
                self.text_to_speech.rate = preferences['tts_rate']
            
            if 'user_name' in preferences:
                print(f"👋 ¡Hola de nuevo, {preferences['user_name']}!\n")
        else:
            # Primera vez - configurar preferencias por defecto
            self.db.set_preference('user_name', 'Usuario', 'string')
            self.db.set_preference('tts_rate', 180, 'int')
            self.db.set_preference('favorite_topics', ['general'], 'json')
            print("📋 Preferencias iniciales configuradas\n")
    
    def process_user_input(self, user_text: str) -> tuple:
        """
        Procesa el texto del usuario: primero busca comandos, 
        si no encuentra, responde con IA
        
        Args:
            user_text (str): Texto transcrito del usuario
            
        Returns:
            tuple: (respuesta, tipo) donde tipo es 'command' o 'ai'
        """
        # Intentar ejecutar comando del sistema
        command_response = self.command_executor.execute(user_text)
        
        if command_response:
            print(f"⚙️ Comando ejecutado: {command_response}")
            self.command_count += 1
            return command_response, "command"
        
        # Si no es comando, buscar contexto relevante en BD (RAG simple)
        relevant_context = self.db.search_context(user_text, limit=3)
        
        # Agregar contexto a la consulta si es relevante
        if relevant_context:
            context_info = "\n".join([ctx['content'] for ctx in relevant_context])
            enhanced_input = f"Contexto relevante de conversaciones previas:\n{context_info}\n\nPregunta actual: {user_text}"
            print(f"🔍 Usando contexto de conversaciones previas...")
        else:
            enhanced_input = user_text
        
        # Responder con IA
        ai_response = self.ai_engine.generate_response(enhanced_input)
        self.ai_response_count += 1
        
        return ai_response, "ai"
    
    def run(self):
        """Bucle principal del asistente"""
        print("\n🎤 Presiona y mantén '|' para hablar con JARVIS")
        print("⌨️  Presiona Ctrl+C para salir\n")
        
        # Mostrar recordatorios pendientes
        self._check_reminders()
        
        try:
            while True:
                interaction_start = time.time()
                
                try:
                    # 1. Grabar audio
                    audio_file = self.audio_recorder.record_while_pressed()
                    
                    # 2. Transcribir a texto
                    user_text = self.speech_to_text.transcribe(audio_file)
                    
                    # 3. Procesar y generar respuesta
                    response, response_type = self.process_user_input(user_text)
                    
                    # 4. Reproducir respuesta por voz
                    self.text_to_speech.speak(response)
                    
                    # 5. Guardar interacción en BD
                    interaction_duration = time.time() - interaction_start
                    self.interaction_count += 1
                    
                    model_used = self.ai_engine.model_name if response_type == 'ai' else None
                    
                    interaction_id = self.db.save_interaction(
                        session_id=self.session_id,
                        user_input=user_text,
                        response=response,
                        response_type=response_type,
                        duration=interaction_duration,
                        model_used=model_used
                    )
                    
                    # Guardar contexto para RAG (solo respuestas de IA importantes)
                    if response_type == 'ai' and len(user_text) > 20:
                        keywords = self._extract_keywords(user_text)
                        self.db.save_context(
                            interaction_id=interaction_id,
                            content=f"Usuario: {user_text}\nAsistente: {response}",
                            keywords=keywords,
                            importance=0.7 if len(response) > 100 else 0.5
                        )
                    
                    # Registrar en logger
                    self.logger.log_interaction(
                        user_text, 
                        response, 
                        response_type, 
                        interaction_duration
                    )
                    
                    # Detectar si el usuario está creando un recordatorio
                    self._detect_reminder(user_text)
                    
                except Exception as e:
                    error_msg = f"Error en interacción: {str(e)}"
                    print(f"❌ {error_msg}")
                    self.logger.log_error("InteractionError", str(e), module="run_loop")
                    self.db.log_error("InteractionError", str(e), module="run_loop")
                    continue
                
                # Pequeña pausa antes de la siguiente interacción
                print("\n" + "-" * 60)
                print("Listo para la siguiente interacción...")
                print("-" * 60 + "\n")
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            self._shutdown()
    
    def _check_reminders(self):
        """Verifica y muestra recordatorios pendientes"""
        reminders = self.db.get_pending_reminders()
        
        if reminders:
            print("\n📅 Tienes recordatorios pendientes:")
            for reminder in reminders[:5]:  # Mostrar máximo 5
                task = reminder['task']
                scheduled = reminder['scheduled_time']
                print(f"  • {task}" + (f" - Programado: {scheduled}" if scheduled else ""))
            print()
    
    def _detect_reminder(self, user_text: str):
        """
        Detecta si el usuario quiere crear un recordatorio
        
        Args:
            user_text: Texto del usuario
        """
        text_lower = user_text.lower()
        
        reminder_keywords = ['recuérdame', 'recordatorio', 'no olvides', 'tengo que']
        
        if any(keyword in text_lower for keyword in reminder_keywords):
            # Extraer la tarea (simplificado)
            task = user_text
            self.db.create_reminder(task, priority=1)
            print("📝 Recordatorio guardado en la base de datos")
    
    def _extract_keywords(self, text: str) -> list:
        """
        Extrae palabras clave del texto (versión simple)
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de palabras clave
        """
        # Palabras comunes a ignorar
        stopwords = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 
                     'no', 'haber', 'por', 'con', 'su', 'para', 'como', 'estar', 
                     'tener', 'le', 'lo', 'todo', 'pero', 'más', 'hacer', 'o', 'poder'}
        
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 4 and w not in stopwords]
        
        return keywords[:5]  # Máximo 5 keywords
    
    def _shutdown(self):
        """Procedimiento de cierre limpio"""
        print("\n\n" + "=" * 60)
        print("👋 Cerrando JARVIS...")
        print("=" * 60)
        
        # Finalizar sesión en BD
        stats = {
            'total_interactions': self.interaction_count,
            'total_commands': self.command_count,
            'total_ai_responses': self.ai_response_count,
            'average_duration': 0  # Calcular si es necesario
        }
        self.db.end_session(self.session_id, stats)
        
        # Crear backup si es necesario
        backup_path = self.db.backup_database()
        print(f"💾 Backup creado: {backup_path}")
        
        # Cerrar conexión a BD
        self.db.close()
        
        # Finalizar logging
        self.logger.log_session_end(self.interaction_count)
        self.logger.print_session_summary()
        
        print("\n✅ Sesión finalizada correctamente. ¡Hasta pronto!")


def main():
    """Función principal de entrada"""
    try:
        assistant = JarvisAssistant()
        assistant.run()
    except Exception as e:
        print(f"\n❌ Error crítico al iniciar JARVIS: {str(e)}")
        print("Por favor, verifica que todas las dependencias estén instaladas.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()