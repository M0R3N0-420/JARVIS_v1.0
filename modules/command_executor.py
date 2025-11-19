"""
Módulo para ejecutar comandos del sistema
"""
import os
import webbrowser
import time
from config import SYSTEM_COMMANDS


class CommandExecutor:
    """Clase para detectar y ejecutar comandos del sistema"""
    
    def __init__(self, custom_commands=None, logger=None):
        """
        Inicializa el ejecutor de comandos
        
        Args:
            custom_commands (dict): Comandos personalizados adicionales
            logger: Logger opcional
        """
        self.commands = SYSTEM_COMMANDS.copy()
        self.logger = logger
        
        if custom_commands:
            self.commands.update(custom_commands)
        
        print(f"⚙️ Ejecutor de comandos inicializado ({len(self.commands)} comandos disponibles)\n")
    
    def execute(self, user_text):
        """
        Busca y ejecuta comandos en el texto del usuario
        
        Args:
            user_text (str): Texto transcrito del usuario
            
        Returns:
            str or None: Mensaje de confirmación si se ejecutó un comando, None si no
        """
        text_lower = user_text.lower()
        
        # Buscar coincidencia con comandos registrados
        for keyword, command_data in self.commands.items():
            if keyword in text_lower:
                return self._execute_action(command_data)
        
        return None  # No se encontró comando
    
    def _execute_action(self, command_data):
        """
        Ejecuta la acción específica del comando
        
        Args:
            command_data (dict): Datos del comando con 'action' y opcionalmente 'args'
            
        Returns:
            str: Mensaje de confirmación
        """
        action = command_data.get("action")
        args = command_data.get("args")
        
        # Navegador
        if action == "open_browser":
            os.system(f"start {args}")
            return f"Abriendo {args}."
        
        # URLs
        elif action == "open_url":
            webbrowser.open(args)
            url_name = args.split("//")[1].split(".")[1] if "//" in args else args
            return f"Abriendo {url_name.capitalize()}."
        
        # Aplicaciones
        elif action == "open_app":
            os.startfile(args)
            app_name = os.path.basename(args).replace(".exe", "")
            return f"Abriendo {app_name}."
        
        # Sistema
        elif action == "lock_screen":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Bloqueando la pantalla."
        
        elif action == "shutdown":
            os.system("shutdown /s /t 1")
            return "Apagando el sistema."
        
        # Utilidades
        elif action == "get_time":
            hora = time.strftime("%H:%M")
            return f"Son las {hora}."
        
        else:
            return "Comando no reconocido."
    
    def add_command(self, keyword, action, args=None):
        """
        Agrega un nuevo comando dinámicamente
        
        Args:
            keyword (str): Palabra clave para activar el comando
            action (str): Tipo de acción
            args (str): Argumentos opcionales
        """
        self.commands[keyword.lower()] = {
            "action": action,
            "args": args
        }
        print(f"✅ Comando '{keyword}' agregado.")
    
    def remove_command(self, keyword):
        """
        Elimina un comando
        
        Args:
            keyword (str): Palabra clave del comando a eliminar
        """
        if keyword.lower() in self.commands:
            del self.commands[keyword.lower()]
            print(f"🗑️ Comando '{keyword}' eliminado.")
        else:
            print(f"⚠️ Comando '{keyword}' no encontrado.")
    
    def list_commands(self):
        """
        Lista todos los comandos disponibles
        
        Returns:
            list: Lista de palabras clave de comandos
        """
        return list(self.commands.keys())