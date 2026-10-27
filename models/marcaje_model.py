"""
Modelo para el control de marcajes (entrada/salida) y cálculo de horas.
"""

import sqlite3
from datetime import datetime
from models.database import conectar
from models.auditoria_model import registrar_accion


def obtener_empleado_por_cedula(cedula):
    """
    Busca un empleado por su cédula para verificar si existe y si está activo.
    Devuelve un diccionario con los datos o None si no lo encuentra.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, apellido, estado FROM empleados WHERE cedula = ?", (cedula,))
        fila = cursor.fetchone()
        return dict(fila) if fila else None
    finally:
        conn.close()


def registrar_marcaje(cedula: str, tipo: str) -> tuple[bool, str]:
    """
    Registra la entrada o salida de un empleado.
    Calcula las horas trabajadas automáticamente al registrar la salida.
    
    Retorna una tupla (éxito, mensaje) para que la vista muestre el resultado.
    """
    empleado = obtener_empleado_por_cedula(cedula)
    if not empleado:
        return False, "Empleado no encontrado."
    
    if empleado["estado"] == "Inactivo":
        return False, "El empleado está inactivo. No puede marcar."

    conn = conectar()
    try:
        cursor = conn.cursor()
        hoy = datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        # Buscamos si el empleado ya tiene un registro de marcaje para el día de hoy
        cursor.execute("SELECT id, entrada, salida FROM marcajes WHERE empleado_id = ? AND fecha = ?", (empleado["id"], hoy))
        marcaje_hoy = cursor.fetchone()

        if tipo == "entrada":
            # Si ya hay un marcaje hoy, no permitimos una segunda entrada
            if marcaje_hoy:
                return False, "Ya registró una entrada hoy."
            
            # Insertamos el registro de entrada. El estado queda 'Incompleto' hasta que marque salida.
            cursor.execute(
                "INSERT INTO marcajes (empleado_id, fecha, entrada, estado) VALUES (?, ?, ?, 'Incompleto')",
                (empleado["id"], hoy, hora_actual)
            )
            conn.commit()
            
            # Registramos en la bitácora
            registrar_accion("Sistema", "MARCAR_ENTRADA", "marcajes", None, f"Entrada de {empleado['nombre']} {empleado['apellido']}")
            return True, f"Entrada registrada a las {hora_actual}."

        elif tipo == "salida":
            # Validaciones para la salida
            if not marcaje_hoy:
                return False, "No registró entrada hoy. No puede marcar salida."
            if marcaje_hoy["salida"]:
                return False, "Ya registró una salida hoy."

            # Cálculo de horas trabajadas:
            # Convertimos las horas en texto a objetos datetime para poder restarlas
            entrada_str = marcaje_hoy["entrada"]
            formato = "%H:%M:%S"
            t_entrada = datetime.strptime(entrada_str, formato)
            t_salida = datetime.strptime(hora_actual, formato)
            
            # La diferencia se obtiene en segundos, la pasamos a horas
            diferencia = t_salida - t_entrada
            horas_trabajadas = diferencia.total_seconds() / 3600.0

            cursor.execute(
                """
                UPDATE marcajes 
                SET salida = ?, horas_trabajadas = ?, estado = 'Normal' 
                WHERE id = ?
                """,
                (hora_actual, horas_trabajadas, marcaje_hoy["id"])
            )
            conn.commit()

            # Registramos en la bitácora
            registrar_accion("Sistema", "MARCAR_SALIDA", "marcajes", None, f"Salida de {empleado['nombre']} {empleado['apellido']}")
            return True, f"Salida registrada a las {hora_actual}.\nHoras trabajadas hoy: {horas_trabajadas:.2f} hs."
            
        # Retorno por defecto en caso de que el 'tipo' no sea ni entrada ni salida
        return False, "Tipo de marcaje no válido."
            
    finally:
        conn.close()


def obtener_todos_los_marcajes():
    """
    Trae todos los marcajes junto con el nombre del empleado.
    Se usa un JOIN para unir la tabla de marcajes con la de empleados.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, e.cedula, e.nombre, e.apellido, m.fecha, m.entrada, m.salida, m.horas_trabajadas, m.estado
            FROM marcajes m
            JOIN empleados e ON m.empleado_id = e.id
            ORDER BY m.fecha DESC, m.entrada DESC
        """)
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        conn.close()


def actualizar_marcaje_admin(marcaje_id, nueva_entrada, nueva_salida, usuario_admin):
    """
    Permite al administrador corregir las horas de un marcaje.
    Si un campo se deja vacío, el sistema mantiene el valor anterior de la base de datos.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        
        # 1. Buscamos los datos actuales del marcaje
        cursor.execute("SELECT entrada, salida FROM marcajes WHERE id = ?", (marcaje_id,))
        marcaje_actual = cursor.fetchone()
        
        if not marcaje_actual:
            return False, "El marcaje no existe."

        # 2. Lógica para mantener los valores anteriores si el admin no escribe nada
        entrada_final = nueva_entrada if nueva_entrada else marcaje_actual["entrada"]
        salida_final = nueva_salida if nueva_salida else marcaje_actual["salida"]

        # 3. Recalculamos las horas si tenemos entrada y salida
        horas_trabajadas = 0.0
        if entrada_final and salida_final:
            formato = "%H:%M:%S"
            try:
                t_entrada = datetime.strptime(entrada_final, formato)
                t_salida = datetime.strptime(salida_final, formato)
                diferencia = t_salida - t_entrada
                horas_trabajadas = diferencia.total_seconds() / 3600.0
                
                # Validación de coherencia
                if horas_trabajadas < 0:
                    return False, "La hora de salida no puede ser menor a la de entrada."
            except ValueError:
                return False, "Formato de hora inválido. Use HH:MM:SS (ej: 08:00:00)."

        # 4. Actualizamos la base de datos con el estado 'Corregido'
        cursor.execute("""
            UPDATE marcajes 
            SET entrada = ?, salida = ?, horas_trabajadas = ?, estado = 'Corregido'
            WHERE id = ?
        """, (entrada_final, salida_final, horas_trabajadas, marcaje_id))
        conn.commit()

        # 5. Guardamos en la bitácora
        registrar_accion(usuario_admin, "CORRECCIÓN", "marcajes", marcaje_id, f"Se corrigió el marcaje ID {marcaje_id}")
        
        return True, "Marcaje corregido exitosamente."
    finally:
        conn.close()