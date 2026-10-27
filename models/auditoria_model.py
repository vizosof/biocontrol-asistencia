# =====================================================================
# MÓDULO: GESTIÓN DE LA BITÁCORA (AUDITORÍA)
# =====================================================================
# Este archivo se encarga de guardar un registro de todas las acciones
# importantes que se hacen en el sistema (quién entró, quién creó un
# empleado, quién corrigió un marcaje, etc.).
# =====================================================================
from typing import Optional
from models.database import conectar

def registrar_accion(usuario: str, accion: str, entidad: Optional[str] = None, registro_id: Optional[int] = None, detalles: str = ""):
    """
    Guarda una acción en la tabla de auditoría.
    
    Parámetros:
    - usuario: El nombre de quien realizó la acción (ej: 'admin').
    - accion: El tipo de acción (ej: 'LOGIN', 'CREAR', 'MARCAR_ENTRADA').
    - entidad: La tabla afectada (ej: 'empleados', 'marcajes').
    - registro_id: El ID del registro que se modificó (opcional).
    - detalles: Un texto descriptivo de lo que pasó (ej: 'Se creó a Juan Pérez').
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        # Insertamos el registro usando parámetros (?) para evitar inyecciones SQL
        cursor.execute(
            """
            INSERT INTO auditoria (usuario_responsable, accion, entidad, registro_id, detalles)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usuario, accion, entidad, registro_id, detalles)
        )
        conn.commit()
    except Exception as e:
        # Si falla la auditoría, mostramos el error en consola pero no detenemos el programa
        print(f"Error al guardar auditoría: {e}")
    finally:
        conn.close()


def obtener_auditoria():
    """
    Devuelve una lista con todos los registros de la bitácora.
    Los ordena por ID descendente para mostrar primero las acciones más recientes.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auditoria ORDER BY id DESC")
        # Convertimos las filas de SQLite a diccionarios de Python para que la vista las use fácilmente
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        conn.close()