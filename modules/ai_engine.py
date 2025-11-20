"""
Módulo para interacción con modelos de lenguaje (Ollama)
"""
from ollama import chat, ChatResponse
from config import OLLAMA_MODEL, ASSISTANT_ROLE


class AIEngine:
    """Clase para gestionar conversaciones con IA"""
    
    def __init__(self, model_name=None, system_role=None, logger=None):
        """
        Inicializa el motor de IA con memoria conversacional
        
        Args:
            model_name (str): Nombre del modelo de Ollama
            system_role (str): Instrucciones del sistema para el asistente
            logger: Logger opcional
        """
        self.model_name = model_name or OLLAMA_MODEL
        self.system_role = system_role or ASSISTANT_ROLE
        self.logger = logger
        
        # Historial conversacional
        self.history = [
            {"role": "system", "content": self.system_role}
        ]
        
        print(f"🤖 Motor IA inicializado con modelo: {self.model_name}\n")
    
    def generate_response(self, user_message):
        """
        Genera respuesta del asistente manteniendo contexto
        
        Args:
            user_message (str): Mensaje del usuario
            
        Returns:
            str: Respuesta del asistente
        """
        import time
        
        # Agregar mensaje del usuario al historial
        self.history.append({"role": "user", "content": user_message})
        
        print("🤖 Generando respuesta con IA...\n")
        
        start_time = time.time()
        # Obtener respuesta del modelo
        response: ChatResponse = chat(
            model=self.model_name,
            messages=self.history
        )
        response_time = time.time() - start_time
        
        assistant_message = response.message.content.strip()
        
        # Agregar respuesta al historial
        self.history.append({"role": "assistant", "content": assistant_message})
        
        print(f"💬 Asistente: {assistant_message}\n")
        
        if self.logger:
            # Log detallado con entrada del usuario
            self.logger.log_ai_response(
                user_message, 
                assistant_message, 
                self.model_name, 
                response_time
            )
        
        return assistant_message
    
    def clear_history(self, keep_system=True):
        """
        Limpia el historial conversacional
        
        Args:
            keep_system (bool): Si mantener el mensaje del sistema
        """
        if keep_system:
            self.history = [
                {"role": "system", "content": self.system_role}
            ]
        else:
            self.history = []
        
        print("🗑️ Historial conversacional limpiado.")
    
    def get_history(self):
        """
        Obtiene el historial completo
        
        Returns:
            list: Lista de mensajes
        """
        return self.history
    
    def get_conversation_length(self):
        """
        Obtiene el número de intercambios (sin contar mensaje del sistema)
        
        Returns:
            int: Número de mensajes del usuario + asistente
        """
        return len(self.history) - 1
    
    def change_model(self, model_name):
        """
        Cambia el modelo de Ollama
        
        Args:
            model_name (str): Nuevo modelo
        """
        self.model_name = model_name
        print(f"Modelo cambiado a: {model_name}")
    
    def update_system_role(self, new_role):
        """
        Actualiza el rol/comportamiento del asistente
        
        Args:
            new_role (str): Nuevas instrucciones del sistema
        """
        self.system_role = new_role
        self.history[0] = {"role": "system", "content": new_role}
        print("✅ Rol del asistente actualizado.")