"""
Analizador de logs para JARVIS
Herramienta para revisar y analizar sesiones anteriores
"""
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt


class LogAnalyzer:
    """Analiza los logs y sesiones de JARVIS"""
    
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.sessions = []
        self._load_sessions()
    
    def _load_sessions(self):
        """Carga todas las sesiones disponibles"""
        if not os.path.exists(self.log_dir):
            print(f"⚠️ Directorio de logs no encontrado: {self.log_dir}")
            return
        
        for filename in os.listdir(self.log_dir):
            if filename.startswith("session_") and filename.endswith(".json"):
                filepath = os.path.join(self.log_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    session['filename'] = filename
                    self.sessions.append(session)
        
        # Ordenar por fecha
        self.sessions.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        print(f"📊 {len(self.sessions)} sesiones cargadas.\n")
    
    def list_sessions(self):
        """Lista todas las sesiones disponibles"""
        if not self.sessions:
            print("No hay sesiones registradas.")
            return
        
        print("=" * 80)
        print("📋 SESIONES REGISTRADAS")
        print("=" * 80)
        
        for i, session in enumerate(self.sessions, 1):
            start = datetime.fromisoformat(session['start_time'])
            end_time = session.get('end_time')
            end = datetime.fromisoformat(end_time) if end_time else None
            duration = (end - start).total_seconds() if end else 0
            
            print(f"\n{i}. Sesión: {session['filename']}")
            print(f"   Inicio: {start.strftime('%Y-%m-%d %H:%M:%S')}")
            if end:
                print(f"   Fin: {end.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Duración: {duration:.1f} segundos")
            print(f"   Interacciones: {len(session.get('interactions', []))}")
        
        print("\n" + "=" * 80)
    
    def analyze_session(self, session_index=0):
        """
        Analiza una sesión específica
        
        Args:
            session_index (int): Índice de la sesión (0 = más reciente)
        """
        if not self.sessions:
            print("No hay sesiones para analizar.")
            return
        
        if session_index >= len(self.sessions):
            print(f"⚠️ Sesión {session_index} no existe.")
            return
        
        session = self.sessions[session_index]
        interactions = session.get('interactions', [])
        
        print("\n" + "=" * 80)
        print(f"📊 ANÁLISIS DE SESIÓN: {session['filename']}")
        print("=" * 80)
        
        # Estadísticas generales
        total = len(interactions)
        commands = sum(1 for i in interactions if i['type'] == 'command')
        ai_responses = sum(1 for i in interactions if i['type'] == 'ai')
        
        durations = [i['duration'] for i in interactions if i.get('duration')]
        avg_duration = sum(durations) / len(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        
        print(f"\n📈 Estadísticas:")
        print(f"   Total interacciones: {total}")
        print(f"   Comandos ejecutados: {commands} ({commands/total*100:.1f}%)" if total > 0 else "   Comandos ejecutados: 0")
        print(f"   Respuestas de IA: {ai_responses} ({ai_responses/total*100:.1f}%)" if total > 0 else "   Respuestas de IA: 0")
        print(f"\n⏱️  Tiempos de respuesta:")
        print(f"   Promedio: {avg_duration:.2f}s")
        print(f"   Máximo: {max_duration:.2f}s")
        print(f"   Mínimo: {min_duration:.2f}s")
        
        # Comandos más usados
        if commands > 0:
            command_texts = [i['user_input'] for i in interactions if i['type'] == 'command']
            print(f"\n⚙️  Comandos más frecuentes:")
            for cmd in set(command_texts):
                count = command_texts.count(cmd)
                print(f"   - '{cmd}': {count} veces")
        
        # Últimas 5 interacciones
        print(f"\n💬 Últimas 5 interacciones:")
        for i, interaction in enumerate(interactions[-5:], 1):
            timestamp = datetime.fromisoformat(interaction['timestamp']).strftime('%H:%M:%S')
            user_input = interaction['user_input'][:50]
            response = interaction['response'][:50]
            print(f"\n   {i}. [{timestamp}] ({interaction['type'].upper()})")
            print(f"      Usuario: {user_input}...")
            print(f"      JARVIS: {response}...")
        
        print("\n" + "=" * 80)
    
    def compare_sessions(self):
        """Compara métricas entre todas las sesiones"""
        if len(self.sessions) < 2:
            print("Se necesitan al menos 2 sesiones para comparar.")
            return
        
        print("\n" + "=" * 80)
        print("📊 COMPARACIÓN DE SESIONES")
        print("=" * 80)
        
        for i, session in enumerate(self.sessions[:5], 1):  # Últimas 5 sesiones
            interactions = session.get('interactions', [])
            total = len(interactions)
            commands = sum(1 for i in interactions if i['type'] == 'command')
            ai = total - commands
            
            start = datetime.fromisoformat(session['start_time'])
            print(f"\n{i}. {start.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Total: {total} | Comandos: {commands} | IA: {ai}")
            print(f"   {'█' * (total // 2)} ({total})")
        
        print("\n" + "=" * 80)
    
    def export_summary(self, output_file="session_summary.txt"):
        """Exporta un resumen de todas las sesiones"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("RESUMEN DE SESIONES DE JARVIS\n")
            f.write("=" * 80 + "\n\n")
            
            for session in self.sessions:
                interactions = session.get('interactions', [])
                start = datetime.fromisoformat(session['start_time'])
                
                f.write(f"\nSesión: {start.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Interacciones: {len(interactions)}\n")
                f.write("-" * 40 + "\n")
                
                for interaction in interactions:
                    f.write(f"Usuario: {interaction['user_input']}\n")
                    f.write(f"JARVIS: {interaction['response']}\n")
                    f.write(f"Tipo: {interaction['type']} | Tiempo: {interaction.get('duration', 0):.2f}s\n\n")
        
        print(f"✅ Resumen exportado a: {output_file}")


def main():
    """Menú interactivo para analizar logs"""
    analyzer = LogAnalyzer()
    
    while True:
        print("\n" + "=" * 60)
        print("🔍 ANALIZADOR DE LOGS DE JARVIS")
        print("=" * 60)
        print("1. Listar sesiones")
        print("2. Analizar sesión específica")
        print("3. Comparar sesiones")
        print("4. Exportar resumen")
        print("5. Salir")
        print("=" * 60)
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            analyzer.list_sessions()
        elif opcion == "2":
            analyzer.list_sessions()
            try:
                idx = int(input("\n¿Qué sesión analizar? (1 = más reciente): ")) - 1
                analyzer.analyze_session(idx)
            except ValueError:
                print("⚠️ Entrada inválida.")
        elif opcion == "3":
            analyzer.compare_sessions()
        elif opcion == "4":
            analyzer.export_summary()
        elif opcion == "5":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("⚠️ Opción no válida.")


if __name__ == "__main__":
    main()