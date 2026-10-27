"""
Controlador de autenticación.

Hace de puente entre la vista de login y el modelo de usuarios.
La vista NO conoce SQLite: solo llama a estas funciones.
"""

from models.user_model import verificar_credenciales, obtener_rol
from models.auditoria_model import registrar_accion



def login(username: str, password: str):

    """
    Intenta iniciar sesión en el sistema.
    
    Retorna un diccionario con los datos del usuario (incluyendo su rol)
    si el login es exitoso. Retorna None si las credenciales son incorrectas.
    """
    # 1. Preguntamos al modelo si las credenciales son válidas
    usuario = verificar_credenciales(username, password)
    
    # 2. Si devolvió None, el login falló
    if usuario is None:
        return None
        
    # 3. Si es correcto, buscamos el nombre del rol (Administrador, Supervisor, etc.)
    nombre_rol = obtener_rol(usuario["id"])
    
    # 4. Agregamos el rol al diccionario para que la vista sepa qué mostrar
    usuario["rol"] = nombre_rol
    registrar_accion(
        usuario=usuario["username"], 
        accion="LOGIN", 
        entidad="usuarios", 
        registro_id=usuario["id"], 
        detalles=f"Inicio de sesión exitoso como {nombre_rol}"
    )
    
    # 5. Devolvemos los datos completos
    return usuario


