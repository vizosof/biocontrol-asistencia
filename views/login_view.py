"""
Vista de Login - Diseño basado en el prototipo de BioControl.
El rol se detecta automáticamente desde la base de datos.
"""

import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import login

class LoginView(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuración de la ventana ---
        self.title("BioControl - Acceso")
        ancho, alto = 900, 650
        
        # Centrar en la pantalla
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.resizable(False, False)
        
        # Color de fondo general (gris azulado claro del prototipo)
        self.configure(fg_color="#eef2f5")
        ctk.set_appearance_mode("light") 

        # --- Tarjeta Central Blanca ---
        self.tarjeta = ctk.CTkFrame(
            self, 
            width=380, 
            height=420, # Achicamos un poco el alto porque sacamos el rol
            fg_color="#ffffff", 
            corner_radius=10,
            border_width=1,
            border_color="#d1d5db"
        )
        self.tarjeta.pack_propagate(False)
        self.tarjeta.place(relx=0.5, rely=0.5, anchor="center")

        # --- Icono / Logo ---
        self.logo = ctk.CTkLabel(
            self.tarjeta, 
            text="🏢", 
            font=("Arial", 32), 
            fg_color="#2c3e50", 
            text_color="white",
            width=60, 
            height=60,
            corner_radius=10
        )
        self.logo.pack(pady=(30, 10))

        # --- Títulos ---
        ctk.CTkLabel(
            self.tarjeta, 
            text="Panel de administración", 
            font=("Arial", 20, "bold"), 
            text_color="#2c3e50"
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            self.tarjeta, 
            text="Ingrese sus credenciales de acceso", 
            font=("Arial", 12), 
            text_color="#6b7280"
        ).pack(pady=(0, 25))

        # --- Campo Usuario ---
        ctk.CTkLabel(self.tarjeta, text="Usuario", font=("Arial", 12), text_color="#4b5563").pack(anchor="w", padx=40, pady=(0, 5))
        self.entry_usuario = ctk.CTkEntry(
            self.tarjeta, 
            width=300, 
            height=35,
            fg_color="#ffffff",
            border_color="#d1d5db",
            text_color="#000000"
        )
        self.entry_usuario.pack(padx=40)

        # --- Campo Contraseña ---
        ctk.CTkLabel(self.tarjeta, text="Contraseña", font=("Arial", 12), text_color="#4b5563").pack(anchor="w", padx=40, pady=(15, 5))
        self.entry_password = ctk.CTkEntry(
            self.tarjeta, 
            width=300, 
            height=35, 
            show="*",
            fg_color="#ffffff",
            border_color="#d1d5db",
            text_color="#000000"
        )
        self.entry_password.pack(padx=40)

        # --- Botón Ingresar ---
        self.btn_login = ctk.CTkButton(
            self.tarjeta, 
            text="Ingresar", 
            command=self.intentar_login,
            width=300,
            height=40,
            fg_color="#2c3e50",
            hover_color="#1a252f",
            font=("Arial", 14, "bold")
        )
        self.btn_login.pack(pady=(30, 15))

        # --- Texto de pie de página ---
        ctk.CTkLabel(
            self.tarjeta,
            text="El acceso queda registrado. Las contraseñas se\nalmacenan cifradas.",
            font=("Arial", 10),
            text_color="#9ca3af",
            justify="center"
        ).pack(pady=(0, 20))

    def intentar_login(self):
        """Se ejecuta al presionar el botón Ingresar."""
        usuario_input = self.entry_usuario.get()
        pass_input = self.entry_password.get()

        # Si los campos están vacíos, avisamos
        if not usuario_input or not pass_input:
            messagebox.showwarning("Atención", "Por favor, complete todos los campos.")
            return

        # Llamamos al controlador (él ya sabe qué rol tiene el usuario)
        usuario = login(usuario_input, pass_input)

        if usuario:
            # 1. Cerramos la ventana de Login
            self.destroy() 
            
            # 2. Importamos la vista principal acá adentro (para evitar errores de importación circular)
            from views.main_view import MainView 
            
            # 3. Abrimos la ventana principal pasándole los datos del usuario
            app_principal = MainView(usuario)
            app_principal.mainloop()
            
        else:
            # Login fallido
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            self.entry_password.delete(0, 'end')

if __name__ == "__main__":
    app = LoginView()
    app.mainloop()