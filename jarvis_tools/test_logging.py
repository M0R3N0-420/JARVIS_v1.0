"""
Script de prueba para verificar que todos los archivos de log se crean correctamente
"""
import os
import time
from modules import JarvisLogger

def test_all_loggers():
    """Prueba todos los loggers para verificar que funcionen"""
    
    print("=" * 60)
    print("🧪 PRUEBA DEL SISTEMA DE LOGGING")
    print("=" * 60)
    
    # Crear logger
    logger = JarvisLogger()
    
    print("\n1️⃣ Probando logger principal (jarvis_main.log)...")
    logger.main_logger.info("✅ Test: Logger principal funciona")
    logger.main_logger.warning("⚠️ Test: Warning en logger principal")
    
    print("2️⃣ Probando logger de conversaciones (conversations.log)...")
    logger.log_transcription(
        audio_file="test_audio.wav",
        transcribed_text="Hola JARVIS, esta es una prueba",
        duration=2.5
    )
    logger.log_ai_response(
        user_input="Hola JARVIS, esta es una prueba",
        ai_response="¡Hola! Estoy funcionando correctamente. Este es un mensaje de prueba.",
        model_name="llama3.1:8b",
        response_time=1.8
    )
    
    print("3️⃣ Probando logger de comandos (commands.log)...")
    logger.log_command_execution(
        command_keyword="abrir youtube",
        action="open_url",
        result="Abriendo YouTube."
    )
    logger.log_command_execution(
        command_keyword="dame la hora",
        action="get_time",
        result="Son las 15:30"
    )
    
    print("4️⃣ Probando logger de errores (errors.log)...")
    logger.log_error(
        error_type="TestError",
        error_message="Este es un error de prueba, ignóralo",
        module="test_logging"
    )
    
    print("5️⃣ Probando interacciones completas...")
    logger.log_interaction(
        user_input="Abre Spotify",
        response="Abriendo Spotify.",
        response_type="command",
        duration=3.2
    )
    logger.log_interaction(
        user_input="¿Qué es la síntesis FM?",
        response="La síntesis FM es una técnica de síntesis de audio...",
        response_type="ai",
        duration=5.7
    )
    
    print("\n6️⃣ Verificando archivos creados...")
    time.sleep(0.5)  # Dar tiempo para que se escriban los logs
    
    log_files = {
        "jarvis_main.log": "logs/jarvis_main.log",
        "conversations.log": "logs/conversations.log",
        "commands.log": "logs/commands.log",
        "errors.log": "logs/errors.log"
    }
    
    print("\n" + "=" * 60)
    print("📋 RESULTADOS:")
    print("=" * 60)
    
    all_ok = True
    for name, path in log_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name:25} - {size} bytes")
        else:
            print(f"❌ {name:25} - NO ENCONTRADO")
            all_ok = False
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✅ TODOS LOS ARCHIVOS DE LOG SE CREARON CORRECTAMENTE")
        print("\nPuedes revisar cada archivo con:")
        print("  - Windows: type logs\\jarvis_main.log")
        print("  - Linux/Mac: cat logs/jarvis_main.log")
    else:
        print("⚠️ ALGUNOS ARCHIVOS NO SE CREARON")
        print("Verifica que la carpeta 'logs' exista y tengas permisos de escritura")
    
    print("\n" + "=" * 60)
    
    # Mostrar contenido de ejemplo
    print("\n📄 CONTENIDO DE EJEMPLO (conversations.log):")
    print("=" * 60)
    try:
        with open("logs/conversations.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-10:]:  # Últimas 10 líneas
                print(line.rstrip())
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
    
    print("\n" + "=" * 60)
    print("\n📄 CONTENIDO DE EJEMPLO (commands.log):")
    print("=" * 60)
    try:
        with open("logs/commands.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                print(line.rstrip())
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_all_loggers()