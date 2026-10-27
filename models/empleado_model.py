# =====================================================================
# MÓDULO: GESTIÓN DE EMPLEADOS (CRUD)
# =====================================================================
# Este archivo contiene las funciones para Crear, Leer, Actualizar y 
# Eliminar (CRUD) a los empleados de la base de datos.
# Cada acción importante se registra en la bitácora del sistema.
# =====================================================================

import sqlite3
from models.database import conectar
from models.auditoria_model import registrar_accion

def crear_empleado(cedula, nombre, apellido, cargo, sueldo_base, foto_path="", usuario="Sistema"):
    """
    Inserta un nuevo empleado en la base de datos.
    Devuelve una tupla (Booleano, Mensaje) indicando si tuvo éxito.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        # Usamos parámetros (?) para prevenir inyecciones SQL
        cursor.execute(
            """
            INSERT INTO empleados (cedula, nombre, apellido, cargo, sueldo_base, foto_path) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (cedula, nombre, apellido, cargo, sueldo_base, foto_path)
        )
        conn.commit()

        # Registramos la acción en la bitácora
        registrar_accion(usuario, "CREAR", "empleados", None, f"Se creó al empleado {nombre} {apellido}")

        return True, "Empleado creado exitosamente."
    except sqlite3.IntegrityError:
        # Salta si la cédula ya existe (restricción UNIQUE en el schema.sql)
        return False, "Error: La cédula ya está registrada."
    finally:
        conn.close()


def obtener_empleados():
    """
    Devuelve una lista con todos los empleados registrados.
    Se ordenan alfabéticamente por apellido y luego por nombre.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, cedula, nombre, apellido, cargo, sueldo_base, estado FROM empleados ORDER BY apellido, nombre")
        # Convertimos las filas a diccionarios para que la Vista las maneje fácilmente
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        conn.close()


def actualizar_empleado(empleado_id, nombre, apellido, cargo, sueldo_base, estado, usuario="Sistema"):
    """
    Actualiza los datos de un empleado existente.
    Nota: La cédula no se actualiza porque es un identificador único.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE empleados 
            SET nombre=?, apellido=?, cargo=?, sueldo_base=?, estado=? 
            WHERE id=?
            """,
            (nombre, apellido, cargo, sueldo_base, estado, empleado_id)
        )
        conn.commit()

        # Registramos la acción en la bitácora
        registrar_accion(usuario, "ACTUALIZAR", "empleados", empleado_id, f"Se actualizó al empleado {nombre} {apellido}")

        return True
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return False
    finally:
        conn.close()


def eliminar_empleado(empleado_id, usuario="Sistema"):
    """
    Elimina un empleado.
    La llave foránea (ON DELETE RESTRICT) impide borrar empleados que ya tengan marcajes.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empleados WHERE id=?", (empleado_id,))
        conn.commit()
        
        # Registramos la acción en la bitácora
        registrar_accion(usuario, "ELIMINAR", "empleados", empleado_id, f"Se eliminó al empleado ID {empleado_id}")

        return True, "Empleado eliminado."
    except sqlite3.IntegrityError:
        return False, "No se puede eliminar: el empleado tiene marcajes registrados."
    finally:
        conn.close()