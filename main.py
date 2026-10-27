"""
Archivo principal de arranque del sistema BioControl.
Se encarga de inicializar la base de datos y abrir la ventana de Login.
"""

from models.database import inicializar_bd
from views.login_view import LoginView

def iniciar_aplicacion():
    """Inicializa la base de datos y arranca la interfaz gráfica."""
    print("Iniciando BioControl...")
    
    # 1. Nos aseguramos de que la base de datos y las tablas existan
    inicializar_bd()
    
    # 2. Abrimos la ventana de Login
    app = LoginView()
    app.mainloop()

if __name__ == "__main__":
    iniciar_aplicacion()