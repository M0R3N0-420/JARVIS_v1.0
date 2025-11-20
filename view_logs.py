"""
Visor de logs de JARVIS - Lee y muestra archivos de log de forma amigable
"""
import os
import time
from pathlib import Path


class LogViewer:
    """Visor interactivo de logs"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.log_files = {
            "1": ("Principal", "jarvis_main.log"),
            "2": ("Conversaciones", "conversations.log"),
            "3": ("Comandos", "commands.log"),
            "4": ("Errores", "errors.log")
        }
    
    def list_log_files(self):
        """Lista todos los archivos de log disponibles"""
        print("\n" + "=" * 60)
        print("📂 ARCHIVOS DE LOG DISPONIBLES")
        print("=" * 60)
        
        for key, (name, filename) in self.log_files.items():
            filepath = os.path.join(self.log_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                modified = time.ctime(os.path.getmtime(filepath))
                print(f"{key}. {name:20} ({filename})")
                print(f"   Tamaño: {size:,} bytes | Modificado: {modified}")
            else:
                print(f"{key}. {name:20} - ❌ NO EXISTE")
        
        print("=" * 60)
    
    def view_log(self, log_key, lines=50):
        """
        Muestra las últimas líneas de un archivo de log
        
        Args:
            log_key: Clave del archivo (1-4)
            lines: Número de líneas a mostrar
        """
        if log_key not in self.log_files:
            print("⚠️ Opción inválida")
            return
        
        name, filename = self.log_files[log_key]
        filepath = os.path.join(self.log_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return
        
        print("\n" + "=" * 80)
        print(f"📄 {name.upper()} - Últimas {lines} líneas")
        print("=" * 80)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                
                if len(all_lines) == 0:
                    print("📭 El archivo está vacío")
                else:
                    # Mostrar últimas N líneas
                    display_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    
                    for line in display_lines:
                        print(line.rstrip())
                    
                    print("\n" + "=" * 80)
                    print(f"Total de líneas en archivo: {len(all_lines)}")
                    print(f"Mostrando: {len(display_lines)} líneas")
        
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
        
        print("=" * 80)
    
    def tail_log(self, log_key):
        """
        Muestra el log en tiempo real (como tail -f)
        
        Args:
            log_key: Clave del archivo (1-4)
        """
        if log_key not in self.log_files:
            print("⚠️ Opción inválida")
            return
        
        name, filename = self.log_files[log_key]
        filepath = os.path.join(self.log_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return
        
        print("\n" + "=" * 80)
        print(f"📡 {name.upper()} - Modo Tiempo Real")
        print("Presiona Ctrl+C para salir")
        print("=" * 80 + "\n")
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                # Ir al final del archivo
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        print(line.rstrip())
                    else:
                        time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n\n👋 Saliendo del modo tiempo real...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def search_in_log(self, log_key, keyword):
        """
        Busca una palabra clave en el log
        
        Args:
            log_key: Clave del archivo
            keyword: Palabra a buscar
        """
        if log_key not in self.log_files:
            print("⚠️ Opción inválida")
            return
        
        name, filename = self.log_files[log_key]
        filepath = os.path.join(self.log_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return
        
        print("\n" + "=" * 80)
        print(f"🔍 Buscando '{keyword}' en {name}")
        print("=" * 80 + "\n")
        
        try:
            matches = []
            with open(filepath, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if keyword.lower() in line.lower():
                        matches.append((i, line.rstrip()))
            
            if not matches:
                print(f"❌ No se encontraron coincidencias para '{keyword}'")
            else:
                print(f"✅ {len(matches)} coincidencias encontradas:\n")
                
                for line_num, line in matches:
                    print(f"Línea {line_num}: {line}")
                    print()
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 80)
    
    def clear_log(self, log_key):
        """
        Limpia un archivo de log (con confirmación)
        
        Args:
            log_key: Clave del archivo
        """
        if log_key not in self.log_files:
            print("⚠️ Opción inválida")
            return
        
        name, filename = self.log_files[log_key]
        filepath = os.path.join(self.log_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            return
        
        confirm = input(f"⚠️ ¿Estás seguro de limpiar {name}? (s/n): ").lower()
        
        if confirm == 's':
            try:
                open(filepath, 'w').close()
                print(f"✅ {name} limpiado correctamente")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Operación cancelada")


def main():
    """Menú interactivo"""
    viewer = LogViewer()
    
    while True:
        print("\n" + "=" * 60)
        print("📊 VISOR DE LOGS DE JARVIS")
        print("=" * 60)
        print("1. Ver archivos disponibles")
        print("2. Ver log completo")
        print("3. Ver últimas líneas")
        print("4. Modo tiempo real (tail -f)")
        print("5. Buscar en log")
        print("6. Limpiar log")
        print("7. Salir")
        print("=" * 60)
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        try:
            if opcion == "1":
                viewer.list_log_files()
            
            elif opcion == "2":
                viewer.list_log_files()
                log_key = input("\n¿Qué log ver? (1-4): ").strip()
                viewer.view_log(log_key, lines=1000)
            
            elif opcion == "3":
                viewer.list_log_files()
                log_key = input("\n¿Qué log ver? (1-4): ").strip()
                lines = input("¿Cuántas líneas? [50]: ").strip()
                lines = int(lines) if lines else 50
                viewer.view_log(log_key, lines)
            
            elif opcion == "4":
                viewer.list_log_files()
                log_key = input("\n¿Qué log monitorear? (1-4): ").strip()
                viewer.tail_log(log_key)
            
            elif opcion == "5":
                viewer.list_log_files()
                log_key = input("\n¿En qué log buscar? (1-4): ").strip()
                keyword = input("Palabra clave: ").strip()
                if keyword:
                    viewer.search_in_log(log_key, keyword)
            
            elif opcion == "6":
                viewer.list_log_files()
                log_key = input("\n¿Qué log limpiar? (1-4): ").strip()
                viewer.clear_log(log_key)
            
            elif opcion == "7":
                print("\n👋 ¡Hasta luego!")
                break
            
            else:
                print("\n⚠️ Opción no válida")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()