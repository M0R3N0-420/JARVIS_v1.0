# 🤖 JARVIS - Asistente de Voz Inteligente

Asistente de voz modular con capacidades de IA, reconocimiento de voz, síntesis de texto a voz, y sistema de persistencia con base de datos.

## ✨ Características

### 🎙️ **Funcionalidades Principales**
- ✅ Reconocimiento de voz con Whisper (OpenAI)
- ✅ Respuestas inteligentes con Llama 3.1 (Ollama)
- ✅ Síntesis de voz con pyttsx3
- ✅ Ejecución de comandos del sistema
- ✅ Memoria conversacional persistente
- ✅ Sistema de logging profesional
- ✅ Base de datos SQLite integrada

### 💾 **Sistema de Base de Datos**
- 📊 Historial completo de conversaciones
- ⚙️ Estadísticas de uso y comandos
- 📅 Sistema de recordatorios/tareas
- 🔧 Preferencias personalizadas del usuario
- 🔍 Búsqueda semántica con RAG básico
- 📈 Análisis de patrones de uso

### 📦 **Arquitectura Modular**
```
jarvis_assistant/
│
├── main.py                      # Punto de entrada
├── config.py                    # Configuraciones
│
├── modules/
│   ├── audio_handler.py         # Grabación de audio
│   ├── speech_to_text.py        # Whisper STT
│   ├── text_to_speech.py        # pyttsx3 TTS
│   ├── ai_engine.py             # Motor de IA
│   ├── command_executor.py      # Comandos del sistema
│   ├── logger.py                # Sistema de logging
│   └── database_manager.py      # Gestor de BD
│
├── data/
│   ├── jarvis.db                # Base de datos SQLite
│   └── rec.wav                  # Audio temporal
│
├── logs/
│   ├── jarvis_main.log          # Log principal
│   ├── conversations.log        # Conversaciones completas
│   ├── commands.log             # Comandos ejecutados
│   ├── errors.log               # Solo errores
│   └── sessions/                # Sesiones en JSON
│       ├── session_20241120_080000.json
│       └── session_20241120_143000.json
│
└── backups/
    └── jarvis_backup_*.db
```

## 🚀 Instalación

### 1. Requisitos Previos
```bash
# Python 3.8 o superior
python --version

# Ollama instalado y corriendo
# Descargar de: https://ollama.ai
ollama pull llama3.1:8b
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar
Edita `config.py` según tus preferencias:
```python
WHISPER_MODEL = "small"  # tiny, base, small, medium, large
OLLAMA_MODEL = "llama3.1:8b"
RECORDING_KEY = "|"  # Tecla para grabar
```

## 🎮 Uso

### Ejecutar JARVIS
```bash
python main.py
```

**Controles:**
- Mantén presionada la tecla `|` para hablar
- Suelta para procesar
- `Ctrl+C` para salir

### Explorar Base de Datos
```bash
python database_explorer.py
```

Menú interactivo con:
- Resumen de estadísticas
- Historial de conversaciones
- Comandos más usados
- Recordatorios pendientes
- Búsqueda de conversaciones
- Exportación a JSON

## 📊 Ejemplos de Uso

### Comandos del Sistema
```
Usuario: "Abre YouTube"
JARVIS: "Abriendo YouTube."

Usuario: "Dame la hora"
JARVIS: "Son las 15:30."

Usuario: "Abre Ableton"
JARVIS: "Abriendo Ableton Live 12."
```

### Conversación con IA
```
Usuario: "¿Qué es la síntesis FM?"
JARVIS: "La síntesis FM (Frecuencia Modulada) es una técnica 
de síntesis de audio donde..."

Usuario: "Dame ejemplos de sintetizadores que la usen"
JARVIS: "Claro, algunos sintetizadores famosos que usan FM son 
el Yamaha DX7, el FM8 de Native Instruments..."
```

### Recordatorios
```
Usuario: "Recuérdame revisar el mix de mi canción mañana"
JARVIS: "Entendido, he guardado tu recordatorio."

# Al iniciar JARVIS más tarde:
📅 Tienes recordatorios pendientes:
  • Revisar el mix de mi canción
```

## 🗄️ Base de Datos

### Tablas Principales

**sessions**
- Registra cada vez que ejecutas JARVIS
- Estadísticas agregadas por sesión

**interactions**
- Cada interacción usuario-asistente
- Texto completo de entrada/salida
- Tiempos de procesamiento

**commands**
- Comandos ejecutados
- Frecuencia de uso

**user_preferences**
- Configuraciones personalizadas
- Preferencias del usuario

**reminders**
- Sistema de tareas/recordatorios
- Estados: pending, completed, cancelled

**conversation_context**
- Contexto para RAG
- Keywords y scores de importancia

### Consultas SQL Útiles

```sql
-- Comandos más usados
SELECT command_keyword, COUNT(*) as count 
FROM commands 
GROUP BY command_keyword 
ORDER BY count DESC;

-- Uso por hora del día
SELECT strftime('%H', timestamp) as hour, COUNT(*) 
FROM interactions 
GROUP BY hour;

-- Conversaciones sobre un tema
SELECT * FROM interactions 
WHERE user_input LIKE '%música%' 
ORDER BY timestamp DESC;
```

## 🔧 Personalización

### Agregar Comandos Personalizados

En `config.py`:
```python
SYSTEM_COMMANDS = {
    "tu comando": {
        "action": "open_app",
        "args": "C:\\ruta\\a\\aplicacion.exe"
    }
}
```

### Cambiar Modelo de Whisper
```python
# config.py
WHISPER_MODEL = "base"  # Más rápido, menos preciso
WHISPER_MODEL = "large"  # Más lento, muy preciso
```

### Ajustar Voz del Asistente
```python
# config.py
TTS_RATE = 200  # Más rápido
TTS_VOLUME = 0.8  # Más bajo
```

## 📈 Análisis de Datos

### Exportar Datos
```python
from modules import DatabaseManager

db = DatabaseManager()

# Estadísticas de los últimos 7 días
stats = db.get_usage_statistics(days=7)
print(stats)

# Comandos más usados
commands = db.get_most_used_commands(limit=10)

# Buscar conversaciones
results = db.search_interactions("programación", limit=20)
```

### Crear Backup Manual
```python
db = DatabaseManager()
backup_path = db.backup_database()
print(f"Backup creado en: {backup_path}")
```

## 🛠️ Desarrollo

### Estructura de un Módulo
```python
class NuevoModulo:
    def __init__(self, logger=None):
        self.logger = logger
        # Inicialización
    
    def metodo_principal(self):
        # Lógica
        if self.logger:
            self.logger.main_logger.info("Evento")
```

### Agregar Nueva Tabla a la BD
```python
# En database_manager.py -> _initialize_schema()
self.cursor.execute("""
CREATE TABLE IF NOT EXISTS mi_tabla (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campo TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
```

## 🐛 Troubleshooting

### Whisper no carga
```bash
# Instalar ffmpeg
# Windows: Descargar de ffmpeg.org
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

### Ollama no responde
```bash
# Verificar que Ollama está corriendo
ollama serve

# En otra terminal
ollama list
```

### Errores de micrófono
```bash
# Windows: Verificar permisos de micrófono
# Linux: Instalar portaudio
sudo apt-get install portaudio19-dev
```

## 📝 Logs y Debugging

Logs disponibles en `/logs/`:
- `jarvis_main.log` - Eventos principales
- `conversations.log` - Transcripciones completas
- `errors.log` - Solo errores
- `commands.log` - Comandos ejecutados

## 🔐 Privacidad

- ✅ Todos los datos se guardan **localmente**
- ✅ No se envía información a servidores externos (excepto Ollama local)
- ✅ Base de datos encriptable si es necesario
- ✅ Backups automáticos

## 📚 Próximas Funcionalidades

- [ ] Interfaz gráfica (GUI)
- [ ] Soporte multi-idioma
- [ ] Integración con servicios externos (Gmail, Calendar)
- [ ] Sistema de plugins
- [ ] Embeddings para búsqueda semántica avanzada
- [ ] Reconocimiento de voz continuo (sin push-to-talk)
- [ ] App móvil

## 🤝 Contribuir

¿Ideas para mejorar JARVIS? 
1. Fork el proyecto
2. Crea una branch (`git checkout -b feature/amazing`)
3. Commit tus cambios
4. Push y abre un Pull Request

## 📄 Licencia

MIT License - Libre para usar y modificar

## 👨‍💻 Autor

Desarrollado con ❤️ para automatizar tareas y facilitar la productividad

---

**¿Preguntas?** Abre un issue en GitHub o consulta la documentación completa.