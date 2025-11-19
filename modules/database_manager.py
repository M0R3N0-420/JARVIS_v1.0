"""
Módulo de gestión de base de datos para JARVIS
Maneja persistencia de conversaciones, preferencias, comandos y más
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import shutil
from typing import List, Dict, Optional, Any


class DatabaseManager:
    """Gestor centralizado de base de datos SQLite"""
    
    def __init__(self, db_path="data/jarvis.db", logger=None):
        """
        Inicializa la conexión a la base de datos
        
        Args:
            db_path (str): Ruta del archivo de base de datos
            logger: Logger opcional para registrar operaciones
        """
        self.db_path = db_path
        self.logger = logger
        
        # Crear directorio si no existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Conectar a la base de datos
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
        self.cursor = self.conn.cursor()
        
        # Inicializar esquema
        self._initialize_schema()
        
        if self.logger:
            self.logger.main_logger.info(f"💾 Base de datos inicializada: {db_path}")
    
    def _initialize_schema(self):
        """Crea las tablas si no existen"""
        
        # Tabla de sesiones
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            total_interactions INTEGER DEFAULT 0,
            total_commands INTEGER DEFAULT 0,
            total_ai_responses INTEGER DEFAULT 0,
            average_duration REAL,
            notes TEXT
        )
        """)
        
        # Tabla de interacciones
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_input TEXT NOT NULL,
            response TEXT NOT NULL,
            response_type TEXT CHECK(response_type IN ('command', 'ai')),
            duration REAL,
            model_used TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        """)
        
        # Tabla de comandos ejecutados
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            command_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            command_keyword TEXT NOT NULL,
            action_type TEXT NOT NULL,
            result TEXT,
            success BOOLEAN DEFAULT 1,
            FOREIGN KEY (interaction_id) REFERENCES interactions(interaction_id)
        )
        """)
        
        # Tabla de preferencias del usuario
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            data_type TEXT DEFAULT 'string',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabla de recordatorios/tareas
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            scheduled_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'cancelled')),
            priority INTEGER DEFAULT 0,
            notes TEXT
        )
        """)
        
        # Tabla de contexto conversacional (para RAG)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_context (
            context_id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            content TEXT NOT NULL,
            keywords TEXT,  -- JSON array de palabras clave
            importance_score REAL DEFAULT 0.5,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interaction_id) REFERENCES interactions(interaction_id)
        )
        """)
        
        # Tabla de estadísticas de uso
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_stats (
            stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE DEFAULT (DATE('now')),
            hour INTEGER,
            interaction_count INTEGER DEFAULT 0,
            command_count INTEGER DEFAULT 0,
            ai_response_count INTEGER DEFAULT 0,
            avg_duration REAL,
            UNIQUE(date, hour)
        )
        """)
        
        # Tabla de errores
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS error_logs (
            error_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_type TEXT NOT NULL,
            error_message TEXT NOT NULL,
            module TEXT,
            stack_trace TEXT,
            resolved BOOLEAN DEFAULT 0
        )
        """)
        
        # Tabla de historial de modelos (para tracking de versiones)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_type TEXT NOT NULL,  -- 'whisper', 'ollama'
            model_name TEXT NOT NULL,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            load_time REAL,
            configuration TEXT  -- JSON con config del modelo
        )
        """)
        
        # Crear índices para optimizar consultas
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_interactions_session 
        ON interactions(session_id)
        """)
        
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_interactions_timestamp 
        ON interactions(timestamp)
        """)
        
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_commands_timestamp 
        ON commands(timestamp)
        """)
        
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reminders_status 
        ON reminders(status)
        """)
        
        self.conn.commit()
    
    # === MÉTODOS PARA SESIONES ===
    
    def create_session(self) -> int:
        """
        Crea una nueva sesión
        
        Returns:
            int: ID de la sesión creada
        """
        self.cursor.execute("""
        INSERT INTO sessions (start_time) VALUES (CURRENT_TIMESTAMP)
        """)
        self.conn.commit()
        session_id = self.cursor.lastrowid
        
        if self.logger:
            self.logger.main_logger.info(f"📊 Nueva sesión creada: ID {session_id}")
        
        return session_id
    
    def end_session(self, session_id: int, stats: Dict[str, Any]):
        """
        Finaliza una sesión con estadísticas
        
        Args:
            session_id: ID de la sesión
            stats: Diccionario con estadísticas (total_interactions, etc.)
        """
        self.cursor.execute("""
        UPDATE sessions 
        SET end_time = CURRENT_TIMESTAMP,
            total_interactions = ?,
            total_commands = ?,
            total_ai_responses = ?,
            average_duration = ?
        WHERE session_id = ?
        """, (
            stats.get('total_interactions', 0),
            stats.get('total_commands', 0),
            stats.get('total_ai_responses', 0),
            stats.get('average_duration', 0),
            session_id
        ))
        self.conn.commit()
        
        if self.logger:
            self.logger.main_logger.info(f"📊 Sesión {session_id} finalizada")
    
    # === MÉTODOS PARA INTERACCIONES ===
    
    def save_interaction(self, session_id: int, user_input: str, response: str, 
                        response_type: str, duration: float = None, 
                        model_used: str = None) -> int:
        """
        Guarda una interacción usuario-asistente
        
        Args:
            session_id: ID de la sesión actual
            user_input: Texto del usuario
            response: Respuesta del asistente
            response_type: 'command' o 'ai'
            duration: Tiempo de procesamiento
            model_used: Modelo de IA usado (si aplica)
            
        Returns:
            int: ID de la interacción guardada
        """
        self.cursor.execute("""
        INSERT INTO interactions 
        (session_id, user_input, response, response_type, duration, model_used)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, user_input, response, response_type, duration, model_used))
        self.conn.commit()
        
        interaction_id = self.cursor.lastrowid
        
        # Actualizar estadísticas de uso
        self._update_usage_stats(response_type, duration)
        
        return interaction_id
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene las interacciones más recientes
        
        Args:
            limit: Número máximo de resultados
            
        Returns:
            Lista de diccionarios con datos de interacciones
        """
        self.cursor.execute("""
        SELECT * FROM interactions 
        ORDER BY timestamp DESC 
        LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def search_interactions(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        Busca interacciones que contengan una palabra clave
        
        Args:
            keyword: Palabra o frase a buscar
            limit: Número máximo de resultados
            
        Returns:
            Lista de interacciones relevantes
        """
        self.cursor.execute("""
        SELECT * FROM interactions 
        WHERE user_input LIKE ? OR response LIKE ?
        ORDER BY timestamp DESC
        LIMIT ?
        """, (f'%{keyword}%', f'%{keyword}%', limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    # === MÉTODOS PARA COMANDOS ===
    
    def save_command(self, interaction_id: int, command_keyword: str, 
                     action_type: str, result: str, success: bool = True):
        """
        Guarda un comando ejecutado
        
        Args:
            interaction_id: ID de la interacción asociada
            command_keyword: Palabra clave del comando
            action_type: Tipo de acción ejecutada
            result: Resultado de la ejecución
            success: Si el comando se ejecutó correctamente
        """
        self.cursor.execute("""
        INSERT INTO commands 
        (interaction_id, command_keyword, action_type, result, success)
        VALUES (?, ?, ?, ?, ?)
        """, (interaction_id, command_keyword, action_type, result, success))
        self.conn.commit()
    
    def get_most_used_commands(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene los comandos más utilizados
        
        Args:
            limit: Número de comandos a retornar
            
        Returns:
            Lista de comandos ordenados por frecuencia
        """
        self.cursor.execute("""
        SELECT command_keyword, COUNT(*) as usage_count,
               MAX(timestamp) as last_used
        FROM commands
        GROUP BY command_keyword
        ORDER BY usage_count DESC
        LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    # === MÉTODOS PARA PREFERENCIAS ===
    
    def set_preference(self, key: str, value: Any, data_type: str = 'string'):
        """
        Guarda o actualiza una preferencia del usuario
        
        Args:
            key: Nombre de la preferencia
            value: Valor (será convertido a JSON si no es string)
            data_type: Tipo de dato ('string', 'int', 'float', 'json')
        """
        if data_type == 'json' or isinstance(value, (dict, list)):
            value = json.dumps(value)
            data_type = 'json'
        elif not isinstance(value, str):
            value = str(value)
        
        self.cursor.execute("""
        INSERT OR REPLACE INTO user_preferences (key, value, data_type, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (key, value, data_type))
        self.conn.commit()
        
        if self.logger:
            self.logger.main_logger.info(f"⚙️ Preferencia guardada: {key} = {value}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Obtiene una preferencia del usuario
        
        Args:
            key: Nombre de la preferencia
            default: Valor por defecto si no existe
            
        Returns:
            Valor de la preferencia o default
        """
        self.cursor.execute("""
        SELECT value, data_type FROM user_preferences WHERE key = ?
        """, (key,))
        
        result = self.cursor.fetchone()
        if not result:
            return default
        
        value, data_type = result
        
        # Convertir según el tipo
        if data_type == 'json':
            return json.loads(value)
        elif data_type == 'int':
            return int(value)
        elif data_type == 'float':
            return float(value)
        else:
            return value
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """
        Obtiene todas las preferencias
        
        Returns:
            Diccionario con todas las preferencias
        """
        self.cursor.execute("SELECT key, value, data_type FROM user_preferences")
        
        preferences = {}
        for row in self.cursor.fetchall():
            key, value, data_type = row
            if data_type == 'json':
                preferences[key] = json.loads(value)
            elif data_type == 'int':
                preferences[key] = int(value)
            elif data_type == 'float':
                preferences[key] = float(value)
            else:
                preferences[key] = value
        
        return preferences
    
    # === MÉTODOS PARA RECORDATORIOS ===
    
    def create_reminder(self, task: str, scheduled_time: str = None, 
                       priority: int = 0, notes: str = None) -> int:
        """
        Crea un recordatorio
        
        Args:
            task: Descripción de la tarea
            scheduled_time: Fecha/hora programada (formato ISO)
            priority: Nivel de prioridad (0-5)
            notes: Notas adicionales
            
        Returns:
            ID del recordatorio creado
        """
        self.cursor.execute("""
        INSERT INTO reminders (task, scheduled_time, priority, notes)
        VALUES (?, ?, ?, ?)
        """, (task, scheduled_time, priority, notes))
        self.conn.commit()
        
        reminder_id = self.cursor.lastrowid
        
        if self.logger:
            self.logger.main_logger.info(f"📅 Recordatorio creado: {task}")
        
        return reminder_id
    
    def get_pending_reminders(self) -> List[Dict]:
        """
        Obtiene todos los recordatorios pendientes
        
        Returns:
            Lista de recordatorios pendientes
        """
        self.cursor.execute("""
        SELECT * FROM reminders 
        WHERE status = 'pending'
        ORDER BY scheduled_time ASC, priority DESC
        """)
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def complete_reminder(self, reminder_id: int):
        """Marca un recordatorio como completado"""
        self.cursor.execute("""
        UPDATE reminders 
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE reminder_id = ?
        """, (reminder_id,))
        self.conn.commit()
    
    # === MÉTODOS PARA CONTEXTO CONVERSACIONAL (RAG) ===
    
    def save_context(self, interaction_id: int, content: str, 
                     keywords: List[str] = None, importance: float = 0.5):
        """
        Guarda contexto conversacional para RAG
        
        Args:
            interaction_id: ID de la interacción
            content: Contenido a guardar
            keywords: Lista de palabras clave
            importance: Score de importancia (0-1)
        """
        keywords_json = json.dumps(keywords) if keywords else None
        
        self.cursor.execute("""
        INSERT INTO conversation_context 
        (interaction_id, content, keywords, importance_score)
        VALUES (?, ?, ?, ?)
        """, (interaction_id, content, keywords_json, importance))
        self.conn.commit()
    
    def search_context(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Busca contexto relevante para RAG
        
        Args:
            query: Consulta a buscar
            limit: Número máximo de resultados
            
        Returns:
            Lista de contextos relevantes ordenados por importancia
        """
        self.cursor.execute("""
        SELECT * FROM conversation_context
        WHERE content LIKE ?
        ORDER BY importance_score DESC, timestamp DESC
        LIMIT ?
        """, (f'%{query}%', limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    # === MÉTODOS PARA ERRORES ===
    
    def log_error(self, error_type: str, error_message: str, 
                  module: str = None, stack_trace: str = None):
        """
        Registra un error en la base de datos
        
        Args:
            error_type: Tipo de error
            error_message: Mensaje del error
            module: Módulo donde ocurrió
            stack_trace: Stack trace completo
        """
        self.cursor.execute("""
        INSERT INTO error_logs 
        (error_type, error_message, module, stack_trace)
        VALUES (?, ?, ?, ?)
        """, (error_type, error_message, module, stack_trace))
        self.conn.commit()
    
    # === MÉTODOS DE ANÁLISIS ===
    
    def get_usage_statistics(self, days: int = 7) -> Dict:
        """
        Obtiene estadísticas de uso de los últimos N días
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Diccionario con estadísticas
        """
        self.cursor.execute("""
        SELECT 
            COUNT(*) as total_interactions,
            SUM(CASE WHEN response_type = 'command' THEN 1 ELSE 0 END) as commands,
            SUM(CASE WHEN response_type = 'ai' THEN 1 ELSE 0 END) as ai_responses,
            AVG(duration) as avg_duration,
            MIN(timestamp) as first_interaction,
            MAX(timestamp) as last_interaction
        FROM interactions
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        row = self.cursor.fetchone()
        return dict(row) if row else {}
    
    def _update_usage_stats(self, response_type: str, duration: float):
        """Actualiza estadísticas de uso por hora"""
        current_hour = datetime.now().hour
        
        self.cursor.execute("""
        INSERT INTO usage_stats (date, hour, interaction_count, command_count, ai_response_count, avg_duration)
        VALUES (DATE('now'), ?, 1, ?, ?, ?)
        ON CONFLICT(date, hour) DO UPDATE SET
            interaction_count = interaction_count + 1,
            command_count = command_count + ?,
            ai_response_count = ai_response_count + ?,
            avg_duration = (avg_duration * interaction_count + ?) / (interaction_count + 1)
        """, (
            current_hour,
            1 if response_type == 'command' else 0,
            1 if response_type == 'ai' else 0,
            duration or 0,
            1 if response_type == 'command' else 0,
            1 if response_type == 'ai' else 0,
            duration or 0
        ))
        self.conn.commit()
    
    # === MÉTODOS DE UTILIDAD ===
    
    def backup_database(self, backup_dir: str = "backups") -> str:
        """
        Crea un backup de la base de datos
        
        Args:
            backup_dir: Directorio donde guardar el backup
            
        Returns:
            Ruta del archivo de backup
        """
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{backup_dir}/jarvis_backup_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        
        if self.logger:
            self.logger.main_logger.info(f"💾 Backup creado: {backup_path}")
        
        return backup_path
    
    def optimize_database(self):
        """Optimiza la base de datos (VACUUM)"""
        self.cursor.execute("VACUUM")
        self.conn.commit()
        
        if self.logger:
            self.logger.main_logger.info("🔧 Base de datos optimizada")
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        self.conn.close()
        
        if self.logger:
            self.logger.main_logger.info("💾 Conexión a base de datos cerrada")