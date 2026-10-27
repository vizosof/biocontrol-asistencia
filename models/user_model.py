"""
Módulo de gestión de usuarios del sistema (login del panel).

- Hashea contraseñas antes de guardarlas (nunca texto plano).
- Registra usuarios nuevos con su rol.
- Verifica credenciales en el login.
- Obtiene el rol de un usuario.

Nota: Se usa SHA-256 sin salt por simplicidad del TP.
En un entorno de producción real, se recomendaría usar bcrypt o argon2 
con un 'salt' aleatorio para mayor seguridad.
"""

import hashlib
import sqlite3
from models.database import conectar


def hash_password(password: str) -> str:
    """Devuelve el hash SHA-256 de la contraseña en hexadecimal."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Compara una contraseña en texto plano con su hash guardado."""
    return hash_password(password) == hash_guardado


def registrar_usuario(username: str, password: str, rol_id: int) -> bool:
    """
    Registra un usuario nuevo.

    - Devuelve True si se insertó correctamente.
    - Devuelve False si el username ya existe (UNIQUE en el schema).
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, rol_id) VALUES (?, ?, ?)",
            (username, hash_password(password), rol_id)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Se dispara si el username ya existe o si rol_id no existe (FK).
        return False
    finally:
        conn.close()


def verificar_credenciales(username: str, password: str):
    """
    Verifica el login.

    Devuelve un dict con id, username y rol_id si las credenciales son
    correctas. Devuelve None si el usuario no existe o la contraseña no
    coincide.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, rol_id FROM usuarios WHERE username = ?",
            (username,)
        )
        fila = cursor.fetchone()

        if fila is None:
            return None

        if not verificar_password(password, fila["password_hash"]):
            return None

        return {
            "id": fila["id"],
            "username": fila["username"],
            "rol_id": fila["rol_id"],
        }
    finally:
        conn.close()


def obtener_rol(usuario_id: int):
    """
    Devuelve el nombre del rol del usuario (ej: 'Administrador').
    Devuelve None si el usuario no existe.
    """
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.nombre_rol
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            WHERE u.id = ?
            """,
            (usuario_id,)
        )
        fila = cursor.fetchone()
        return fila["nombre_rol"] if fila else None
    finally:
        conn.close()


def listar_usuarios():
    """Devuelve todos los usuarios (sin hash) como lista de dicts."""
    conn = conectar()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.username, r.nombre_rol
            FROM usuarios u
            JOIN roles r ON u.rol_id = r.id
            ORDER BY u.username
            """
        )
        return [dict(fila) for fila in cursor.fetchall()]
    finally:
        conn.close()





