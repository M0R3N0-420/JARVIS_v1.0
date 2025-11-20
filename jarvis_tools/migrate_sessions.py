"""
Script para migrar archivos session_*.json existentes a logs/sessions/
"""
import os
import shutil
from pathlib import Path


def migrate_sessions():
    """Mueve todos los archivos session_*.json a logs/sessions/"""
    
    log_dir = "logs"
    sessions_dir = os.path.join(log_dir, "sessions")
    
    print("=" * 60)
    print("📦 MIGRACIÓN DE ARCHIVOS DE SESIÓN")
    print("=" * 60)
    
    # Verificar que el directorio logs existe
    if not os.path.exists(log_dir):
        print(f"❌ Directorio {log_dir} no encontrado")
        return
    
    # Crear directorio sessions si no existe
    os.makedirs(sessions_dir, exist_ok=True)
    print(f"✅ Directorio creado/verificado: {sessions_dir}\n")
    
    # Buscar archivos session_*.json en logs/
    session_files = [f for f in os.listdir(log_dir) 
                     if f.startswith("session_") and f.endswith(".json")]
    
    if not session_files:
        print("📭 No se encontraron archivos de sesión para migrar")
        print(f"   (Buscando en: {log_dir}/)")
        return
    
    print(f"📋 Encontrados {len(session_files)} archivos de sesión:\n")
    
    moved_count = 0
    error_count = 0
    
    for filename in session_files:
        source = os.path.join(log_dir, filename)
        destination = os.path.join(sessions_dir, filename)
        
        try:
            # Verificar si ya existe en destino
            if os.path.exists(destination):
                print(f"⚠️  {filename} - Ya existe en destino, omitiendo")
                continue
            
            # Mover archivo
            shutil.move(source, destination)
            print(f"✅ {filename} - Movido correctamente")
            moved_count += 1
        
        except Exception as e:
            print(f"❌ {filename} - Error: {e}")
            error_count += 1
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    print(f"✅ Archivos movidos: {moved_count}")
    if error_count > 0:
        print(f"❌ Errores: {error_count}")
    print(f"📁 Nueva ubicación: {sessions_dir}")
    print("=" * 60)
    
    # Verificar estructura final
    print("\n📂 Estructura final de logs/:")
    print("=" * 60)
    
    for item in sorted(os.listdir(log_dir)):
        path = os.path.join(log_dir, item)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            print(f"  📄 {item:30} ({size:,} bytes)")
        elif os.path.isdir(path):
            files_inside = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            print(f"  📁 {item:30} ({files_inside} archivos)")
    
    print("=" * 60)


if __name__ == "__main__":
    migrate_sessions()