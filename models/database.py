"""
Módulo de acceso a la base de datos SQLite.

- Abre conexiones con foreign keys activas.
- Crea las tablas desde schema.sql si no existen.
- Inserta roles y parámetros iniciales.
"""

import sqlite3
import os

# Ruta absoluta a biocontrol.db (en la raíz del proyecto, al lado de main.py)
DB_NOMBRE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "biocontrol.db")

# Ruta absoluta a schema.sql (en la misma carpeta que este archivo)
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def conectar():
    """
    Abre una conexión a la base de datos.

    - row_factory permite acceder a columnas por nombre (fila["username"]).
    - PRAGMA foreign_keys se activa en CADA conexión porque SQLite las
    trae apagadas por defecto. Sin esto, las cláusulas ON DELETE
    RESTRICT / CASCADE del schema no tendrían efecto.
    """
    conn = sqlite3.connect(DB_NOMBRE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def crear_tablas():
    """
    Ejecuta schema.sql completo.

    Usa executescript para correr varias sentencias SQL separadas por ';'
    en una sola llamada. Es idempotente gracias a CREATE TABLE IF NOT EXISTS,
    por lo que se puede llamar en cada arranque sin duplicar tablas.
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = conectar()
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def insertar_datos_iniciales():
    """
    Inserta roles y parámetros por defecto si no existen.

    Usa INSERT OR IGNORE para no duplicar si ya están cargados
    (aprovecha las restricciones UNIQUE del schema).
    """
    conn = conectar()
    try:
        cursor = conn.cursor()

        # Roles básicos
        cursor.execute("INSERT OR IGNORE INTO roles (nombre_rol) VALUES (?)", ("Administrador",))
        cursor.execute("INSERT OR IGNORE INTO roles (nombre_rol) VALUES (?)", ("Supervisor",))

        # Parámetros de jornada
        cursor.execute(
            "INSERT OR IGNORE INTO parametros (clave, valor, descripcion) VALUES (?, ?, ?)",
            ("hora_entrada", "08:00", "Hora oficial de entrada")
        )
        cursor.execute(
            "INSERT OR IGNORE INTO parametros (clave, valor, descripcion) VALUES (?, ?, ?)",
            ("hora_salida", "17:00", "Hora oficial de salida")
        )
        cursor.execute(
            "INSERT OR IGNORE INTO parametros (clave, valor, descripcion) VALUES (?, ?, ?)",
            ("tolerancia_min", "10", "Minutos de tolerancia antes de marcar tardanza")
        )

        conn.commit()
    finally:
        conn.close()


def inicializar_bd():
    """
    Punto de entrada único: crea tablas + datos iniciales.
    Llamar desde main.py al arrancar la aplicación.
    """
    crear_tablas()
    insertar_datos_iniciales()


if __name__ == "__main__":
    # Bloque de prueba manual: solo corre si ejecutás este archivo directamente.
    inicializar_bd()
    print(f"✅ Base de datos lista en: {DB_NOMBRE}")

    # Verificación rápida: listar tablas creadas
    conn = conectar()
    tablas = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    conn.close()

    print("Tablas encontradas:")
    for t in tablas:
        print(f"  - {t['name']}")