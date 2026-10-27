"""
Script de inicialización de datos por defecto.
Crea el usuario admin si no existe.

Uso:
    python -m utils.seed
"""

from models.database import inicializar_bd
from models.user_model import registrar_usuario, verificar_credenciales


def crear_admin():
    """Crea el usuario admin con password '1234' si no existe."""
    print("Verificando si el usuario 'admin' existe...")

    # Si el login falla, significa que no existe (o la contraseña es otra)
    if verificar_credenciales("admin", "1234") is None:
        # rol_id=1 corresponde a 'Administrador' (insertado por insertar_datos_iniciales)
        ok = registrar_usuario("admin", "1234", 1)
        if ok:
            print("✅ Usuario 'admin' creado exitosamente (password: 1234)")
        else:
            print("❌ ERROR: No se pudo crear el usuario.")
            print("   Posible causa: el rol_id=1 no existe en la tabla 'roles'.")
    else:
        print("ℹ️ El usuario 'admin' ya existía.")


if __name__ == "__main__":
    # 1. Asegurar que las tablas y roles existan
    inicializar_bd()
    # 2. Crear el admin
    crear_admin()