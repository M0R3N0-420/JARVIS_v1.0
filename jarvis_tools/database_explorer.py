"""
Explorador y Analizador de Base de Datos de JARVIS
Herramienta interactiva para visualizar y analizar datos
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json


class DatabaseExplorer:
    """Herramienta para explorar la base de datos de JARVIS"""
    
    def __init__(self, db_path="data/jarvis.db"):
        """
        Inicializa el explorador
        
        Args:
            db_path: Ruta de la base de datos
        """
        if not Path(db_path).exists():
            print(f"❌ Base de datos no encontrada: {db_path}")
            print("Ejecuta JARVIS al menos una vez para crear la base de datos.")
            exit(1)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        print(f"✅ Conectado a: {db_path}\n")
    
    def show_overview(self):
        """Muestra un resumen general de la base de datos"""
        print("=" * 80)
        print("📊 RESUMEN GENERAL DE LA BASE DE DATOS")
        print("=" * 80)
        
        # Total de sesiones
        self.cursor.execute("SELECT COUNT(*) as total FROM sessions")
        total_sessions = self.cursor.fetchone()['total']
        print(f"\n📅 Total de sesiones: {total_sessions}")
        
        # Total de interacciones
        self.cursor.execute("SELECT COUNT(*) as total FROM interactions")
        total_interactions = self.cursor.fetchone()['total']
        print(f"💬 Total de interacciones: {total_interactions}")
        
        # Comandos vs IA
        self.cursor.execute("""
        SELECT 
            response_type,
            COUNT(*) as count
        FROM interactions
        GROUP BY response_type
        """)
        
        print("\n📊 Distribución de respuestas:")
        for row in self.cursor.fetchall():
            print(f"   • {row['response_type'].upper()}: {row['count']}")
        
        # Última actividad
        self.cursor.execute("SELECT MAX(timestamp) as last FROM interactions")
        last_activity = self.cursor.fetchone()['last']
        if last_activity:
            print(f"\n🕐 Última actividad: {last_activity}")
        
        # Total de recordatorios
        self.cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM reminders 
        GROUP BY status
        """)
        
        print("\n📝 Recordatorios:")
        for row in self.cursor.fetchall():
            print(f"   • {row['status'].capitalize()}: {row['count']}")
        
        # Errores registrados
        self.cursor.execute("SELECT COUNT(*) as total FROM error_logs WHERE resolved = 0")
        unresolved_errors = self.cursor.fetchone()['total']
        if unresolved_errors > 0:
            print(f"\n⚠️ Errores sin resolver: {unresolved_errors}")
        
        print("\n" + "=" * 80)
    
    def show_recent_interactions(self, limit=10):
        """Muestra las interacciones más recientes"""
        print("\n" + "=" * 80)
        print(f"💬 ÚLTIMAS {limit} INTERACCIONES")
        print("=" * 80)
        
        self.cursor.execute("""
        SELECT 
            timestamp,
            user_input,
            response,
            response_type,
            duration
        FROM interactions
        ORDER BY timestamp DESC
        LIMIT ?
        """, (limit,))
        
        for i, row in enumerate(self.cursor.fetchall(), 1):
            timestamp = datetime.fromisoformat(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            duration = row['duration'] or 0
            
            print(f"\n{i}. [{timestamp}] ({row['response_type'].upper()}) - {duration:.2f}s")
            print(f"   👤 Usuario: {row['user_input'][:80]}")
            print(f"   🤖 JARVIS: {row['response'][:80]}")
        
        print("\n" + "=" * 80)
    
    def show_command_statistics(self):
        """Muestra estadísticas de comandos"""
        print("\n" + "=" * 80)
        print("⚙️ ESTADÍSTICAS DE COMANDOS")
        print("=" * 80)
        
        self.cursor.execute("""
        SELECT 
            command_keyword,
            COUNT(*) as usage_count,
            MAX(timestamp) as last_used
        FROM commands
        GROUP BY command_keyword
        ORDER BY usage_count DESC
        LIMIT 15
        """)
        
        print("\n📊 Comandos más utilizados:")
        for i, row in enumerate(self.cursor.fetchall(), 1):
            last_used = datetime.fromisoformat(row['last_used']).strftime('%Y-%m-%d')
            print(f"   {i:2}. {row['command_keyword']:30} - {row['usage_count']:3} veces (último: {last_used})")
        
        print("\n" + "=" * 80)
    
    def show_session_details(self, session_id=None):
        """Muestra detalles de una sesión específica"""
        if session_id is None:
            # Mostrar última sesión
            self.cursor.execute("SELECT MAX(session_id) as sid FROM sessions")
            session_id = self.cursor.fetchone()['sid']
        
        self.cursor.execute("""
        SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))
        
        session = self.cursor.fetchone()
        if not session:
            print(f"❌ Sesión {session_id} no encontrada")
            return
        
        print("\n" + "=" * 80)
        print(f"📊 DETALLES DE SESIÓN #{session_id}")
        print("=" * 80)
        
        start = datetime.fromisoformat(session['start_time'])
        print(f"\n🕐 Inicio: {start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if session['end_time']:
            end = datetime.fromisoformat(session['end_time'])
            duration = (end - start).total_seconds()
            print(f"🕐 Fin: {end.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  Duración: {duration:.1f} segundos ({duration/60:.1f} minutos)")
        
        print(f"\n💬 Total interacciones: {session['total_interactions']}")
        print(f"⚙️  Comandos: {session['total_commands']}")
        print(f"🤖 Respuestas IA: {session['total_ai_responses']}")
        
        if session['average_duration']:
            print(f"⏳ Tiempo promedio: {session['average_duration']:.2f}s")
        
        # Mostrar interacciones de esta sesión
        self.cursor.execute("""
        SELECT COUNT(*) as count FROM interactions WHERE session_id = ?
        """, (session_id,))
        
        interaction_count = self.cursor.fetchone()['count']
        
        if interaction_count > 0:
            print(f"\n📝 Esta sesión tiene {interaction_count} interacciones registradas")
        
        print("\n" + "=" * 80)
    
    def show_preferences(self):
        """Muestra preferencias del usuario"""
        print("\n" + "=" * 80)
        print("⚙️ PREFERENCIAS DEL USUARIO")
        print("=" * 80)
        
        self.cursor.execute("SELECT * FROM user_preferences ORDER BY key")
        
        preferences = self.cursor.fetchall()
        
        if not preferences:
            print("\n❌ No hay preferencias guardadas")
        else:
            print()
            for pref in preferences:
                value = pref['value']
                
                # Formatear JSON
                if pref['data_type'] == 'json':
                    try:
                        value = json.dumps(json.loads(value), indent=2)
                    except:
                        pass
                
                updated = datetime.fromisoformat(pref['updated_at']).strftime('%Y-%m-%d')
                print(f"   • {pref['key']}: {value}")
                print(f"     Tipo: {pref['data_type']} | Actualizado: {updated}")
                print()
        
        print("=" * 80)
    
    def show_reminders(self):
        """Muestra recordatorios"""
        print("\n" + "=" * 80)
        print("📅 RECORDATORIOS")
        print("=" * 80)
        
        self.cursor.execute("""
        SELECT * FROM reminders 
        ORDER BY 
            CASE status 
                WHEN 'pending' THEN 1 
                WHEN 'completed' THEN 2 
                ELSE 3 
            END,
            scheduled_time ASC
        """)
        
        reminders = self.cursor.fetchall()
        
        if not reminders:
            print("\n❌ No hay recordatorios")
        else:
            pending = [r for r in reminders if r['status'] == 'pending']
            completed = [r for r in reminders if r['status'] == 'completed']
            
            if pending:
                print(f"\n⏳ PENDIENTES ({len(pending)}):")
                for r in pending:
                    scheduled = r['scheduled_time'] or 'Sin fecha'
                    print(f"   • {r['task']}")
                    print(f"     📅 {scheduled} | Prioridad: {r['priority']}")
            
            if completed:
                print(f"\n✅ COMPLETADOS ({len(completed)}):")
                for r in completed[:5]:  # Mostrar últimos 5
                    completed_at = datetime.fromisoformat(r['completed_at']).strftime('%Y-%m-%d')
                    print(f"   • {r['task']} (completado: {completed_at})")
        
        print("\n" + "=" * 80)
    
    def search_conversations(self, keyword):
        """Busca en conversaciones por palabra clave"""
        print("\n" + "=" * 80)
        print(f"🔍 BÚSQUEDA: '{keyword}'")
        print("=" * 80)
        
        self.cursor.execute("""
        SELECT 
            timestamp,
            user_input,
            response,
            response_type
        FROM interactions
        WHERE user_input LIKE ? OR response LIKE ?
        ORDER BY timestamp DESC
        LIMIT 20
        """, (f'%{keyword}%', f'%{keyword}%'))
        
        results = self.cursor.fetchall()
        
        if not results:
            print(f"\n❌ No se encontraron resultados para '{keyword}'")
        else:
            print(f"\n✅ {len(results)} resultados encontrados:\n")
            
            for i, row in enumerate(results, 1):
                timestamp = datetime.fromisoformat(row['timestamp']).strftime('%Y-%m-%d %H:%M')
                print(f"{i}. [{timestamp}] ({row['response_type'].upper()})")
                print(f"   👤: {row['user_input'][:70]}")
                print(f"   🤖: {row['response'][:70]}")
                print()
        
        print("=" * 80)
    
    def show_usage_by_hour(self):
        """Muestra uso por hora del día"""
        print("\n" + "=" * 80)
        print("📊 USO POR HORA DEL DÍA")
        print("=" * 80)
        
        self.cursor.execute("""
        SELECT 
            strftime('%H', timestamp) as hour,
            COUNT(*) as count
        FROM interactions
        GROUP BY hour
        ORDER BY hour
        """)
        
        print()
        for row in self.cursor.fetchall():
            hour = int(row['hour'])
            count = row['count']
            bar = '█' * (count // 2) if count > 0 else ''
            print(f"   {hour:02d}:00 | {bar} ({count})")
        
        print("\n" + "=" * 80)
    
    def export_to_json(self, output_file="jarvis_export.json"):
        """Exporta toda la base de datos a JSON"""
        print(f"\n📤 Exportando base de datos a {output_file}...")
        
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'sessions': [],
            'preferences': {},
            'reminders': []
        }
        
        # Exportar sesiones con sus interacciones
        self.cursor.execute("SELECT * FROM sessions")
        for session in self.cursor.fetchall():
            session_data = dict(session)
            
            # Obtener interacciones de esta sesión
            self.cursor.execute("""
            SELECT * FROM interactions WHERE session_id = ?
            """, (session['session_id'],))
            
            session_data['interactions'] = [dict(i) for i in self.cursor.fetchall()]
            export_data['sessions'].append(session_data)
        
        # Exportar preferencias
        self.cursor.execute("SELECT key, value, data_type FROM user_preferences")
        for pref in self.cursor.fetchall():
            key = pref['key']
            value = pref['value']
            
            if pref['data_type'] == 'json':
                try:
                    value = json.loads(value)
                except:
                    pass
            
            export_data['preferences'][key] = value
        
        # Exportar recordatorios
        self.cursor.execute("SELECT * FROM reminders")
        export_data['reminders'] = [dict(r) for r in self.cursor.fetchall()]
        
        # Guardar archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exportación completada: {output_file}")
    
    def close(self):
        """Cierra la conexión"""
        self.conn.close()


def main():
    """Menú interactivo"""
    explorer = DatabaseExplorer()
    
    while True:
        print("\n" + "=" * 80)
        print("🔍 EXPLORADOR DE BASE DE DATOS DE JARVIS")
        print("=" * 80)
        print("1.  📊 Resumen general")
        print("2.  💬 Interacciones recientes")
        print("3.  ⚙️  Estadísticas de comandos")
        print("4.  📅 Detalles de sesión")
        print("5.  🔧 Preferencias del usuario")
        print("6.  📝 Recordatorios")
        print("7.  🔍 Buscar en conversaciones")
        print("8.  📊 Uso por hora")
        print("9.  📤 Exportar a JSON")
        print("10. 🚪 Salir")
        print("=" * 80)
        
        opcion = input("\n👉 Selecciona una opción: ").strip()
        
        try:
            if opcion == "1":
                explorer.show_overview()
            elif opcion == "2":
                limit = input("¿Cuántas interacciones mostrar? [10]: ").strip()
                limit = int(limit) if limit else 10
                explorer.show_recent_interactions(limit)
            elif opcion == "3":
                explorer.show_command_statistics()
            elif opcion == "4":
                session_id = input("ID de sesión (Enter para última): ").strip()
                session_id = int(session_id) if session_id else None
                explorer.show_session_details(session_id)
            elif opcion == "5":
                explorer.show_preferences()
            elif opcion == "6":
                explorer.show_reminders()
            elif opcion == "7":
                keyword = input("Palabra clave a buscar: ").strip()
                if keyword:
                    explorer.search_conversations(keyword)
            elif opcion == "8":
                explorer.show_usage_by_hour()
            elif opcion == "9":
                filename = input("Nombre del archivo [jarvis_export.json]: ").strip()
                filename = filename if filename else "jarvis_export.json"
                explorer.export_to_json(filename)
            elif opcion == "10":
                print("\n👋 ¡Hasta luego!")
                break
            else:
                print("\n⚠️ Opción no válida")
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    explorer.close()


if __name__ == "__main__":
    main()