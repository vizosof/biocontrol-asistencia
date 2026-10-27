"""
Script para cargar 5 empleados de prueba con sus respectivos marcajes.
Útil para probar la Nómina y la Bitácora.
"""

from models.database import conectar, inicializar_bd
from models.empleado_model import crear_empleado
from models.marcaje_model import registrar_marcaje
from models.auditoria_model import registrar_accion
from datetime import datetime, timedelta

def limpiar_base_de_datos():
    """Borra todos los datos de las tablas para empezar de cero (deja los roles)."""
    conn = conectar()
    try:
        cursor = conn.cursor()
        # Desactivamos las llaves foráneas temporalmente para poder borrar en orden
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DELETE FROM marcajes;")
        cursor.execute("DELETE FROM huellas;")
        cursor.execute("DELETE FROM empleados;")
        cursor.execute("DELETE FROM auditoria;")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('marcajes', 'empleados', 'auditoria');")
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        print("🧹 Base de datos limpiada (Marcajes, Empleados y Auditoría).")
    finally:
        conn.close()

def cargar_datos_prueba():
    print("Iniciando carga de datos de prueba...\n")
    
    # 1. Empleados a crear (Cédula, Nombre, Apellido, Cargo, Sueldo Base)
    empleados = [
        ("V-11111111", "Carlos", "Gómez", "Gerente General", 150000.0),
        ("V-22222222", "María", "Rodríguez", "Analista RRHH", 80000.0),
        ("V-33333333", "José", "Pérez", "Operador de Máquina", 45000.0),
        ("E-44444444", "Ana", "Martínez", "Contadora", 90000.0),
        ("V-55555555", "Luis", "Fernández", "Pasante", 20000.0),
    ]

    ids_empleados = []
    
    # Registrar empleados en la base de datos
    for cedula, nombre, apellido, cargo, sueldo in empleados:
        exito, msg = crear_empleado(cedula, nombre, apellido, cargo, sueldo)
        if exito:
            print(f"✅ Empleado creado: {nombre} {apellido} ({cedula})")
            # Obtenemos el ID del empleado recién creado
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM empleados WHERE cedula = ?", (cedula,))
            emp_id = cursor.fetchone()["id"]
            ids_empleados.append(emp_id)
            conn.close()
        else:
            print(f"❌ Error al crear {nombre}: {msg}")

    print("\nCargando marcajes de prueba...")

    # 2. Marcajes (Para simular, vamos a usar fechas de la semana pasada)
    # Formato: (días_atras, hora_entrada, hora_salida)
    marcajes = [
        # Carlos (ID 1)
        (1, 1, "08:00:00", "17:00:00"),
        (1, 2, "07:55:00", "17:05:00"),
        # María (ID 2) - Un día se le olvidó marcar la salida
        (2, 1, "08:15:00", None),
        (2, 3, "08:00:00", "16:30:00"),
        # José (ID 3) - Hizo horas extras
        (3, 1, "07:00:00", "19:00:00"),
        (3, 2, "07:05:00", "18:30:00"),
        # Ana (ID 4) - Llegó tarde
        (4, 1, "09:30:00", "17:30:00"),
        # Luis (ID 5) - Media jornada
        (5, 1, "08:00:00", "12:00:00"),
    ]

    for emp_id, dias_atras, entrada, salida in marcajes:
        # Calculamos la fecha
        fecha = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        
        conn = conectar()
        try:
            cursor = conn.cursor()
            
            # Calcular horas trabajadas si hay salida
            horas = 0.0
            if entrada and salida:
                t_ent = datetime.strptime(entrada, "%H:%M:%S")
                t_sal = datetime.strptime(salida, "%H:%M:%S")
                diff = t_sal - t_ent
                horas = diff.total_seconds() / 3600.0

            estado = "Normal" if (entrada and salida) else "Incompleto"

            cursor.execute("""
                INSERT INTO marcajes (empleado_id, fecha, entrada, salida, horas_trabajadas, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (emp_id, fecha, entrada, salida, horas, estado))
            conn.commit()
        finally:
            conn.close()

    print(f"✅ {len(marcajes)} marcajes de prueba cargados.")
    
    registrar_accion("Sistema", "DATOS_PRUEBA", "sistema", None, "Se cargaron 5 empleados y marcajes de prueba.")
    print("\n¡Todo listo! Abrí la aplicación y andá a la pestaña 'Nómina'.")

if __name__ == "__main__":
    inicializar_bd()          # Asegura que las tablas existan
    limpiar_base_de_datos()   # Borra la basura de pruebas anteriores
    cargar_datos_prueba()