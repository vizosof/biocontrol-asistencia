"""
Ventana Principal (Panel de Administración).
Contiene el menú superior y el área de contenido donde se cargarán las vistas.
"""

import customtkinter as ctk
from tkinter import messagebox

class MainView(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()
        self.usuario_actual = usuario # Guardamos los datos del usuario logueado

        # --- Configuración de la ventana ---
        self.title("BioControl - Panel Principal")
        
        # Ajustar al tamaño de la pantalla
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        self.geometry(f"{ancho_pantalla}x{alto_pantalla}+0+0")
        
        self.configure(fg_color="#eef2f5")
        ctk.set_appearance_mode("light")

        # --- Barra de Navegación Superior (Header) ---
        self.header = ctk.CTkFrame(self, height=60, fg_color="#2c3e50", corner_radius=0)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)

        # Logo en el header
        ctk.CTkLabel(
            self.header, 
            text="🏢 BioControl", 
            font=("Arial", 20, "bold"), 
            text_color="white"
        ).pack(side="left", padx=20)

        # Menú de navegación (Botones en el header)
        self.btn_empleados = ctk.CTkButton(self.header, text="Empleados", fg_color="transparent", hover_color="#1a252f", command=self.mostrar_empleados)
        self.btn_empleados.pack(side="left", padx=10, pady=10)

        self.btn_marcaje = ctk.CTkButton(self.header, text="Marcaje", fg_color="transparent", hover_color="#1a252f", command=self.mostrar_marcaje)
        self.btn_marcaje.pack(side="left", padx=10)

        self.btn_auditoria = ctk.CTkButton(self.header, text="Auditoría", fg_color="transparent", hover_color="#1a252f", command=self.mostrar_auditoria)
        self.btn_auditoria.pack(side="left", padx=10)

        self.btn_nomina = ctk.CTkButton(self.header, text="Nómina", fg_color="transparent", hover_color="#1a252f", command=self.mostrar_nomina)
        self.btn_nomina.pack(side="left", padx=10)

        self.btn_gestion_marcajes = ctk.CTkButton(self.header, text="Corregir Marcajes", fg_color="transparent", hover_color="#1a252f", command=self.mostrar_gestion_marcajes)
        self.btn_gestion_marcajes.pack(side="left", padx=10)

        # Botón de Salir (a la derecha)
        self.btn_salir = ctk.CTkButton(
            self.header, 
            text="Cerrar Sesión", 
            fg_color="#e74c3c", 
            hover_color="#c0392b",
            width=100,
            command=self.cerrar_sesion
        )
        self.btn_salir.pack(side="right", padx=20)

        # --- Área de Contenido Central ---
        # Acá iremos "inyectando" las pantallas (Empleados, etc.)
        self.contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido.pack(fill="both", expand=True, padx=20, pady=20)

        # Mensaje de bienvenida inicial
        self.mostrar_bienvenida()

    def mostrar_bienvenida(self):
        # Limpiamos el contenido actual
        for widget in self.contenido.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.contenido, 
            text=f"Bienvenido, {self.usuario_actual['username']}", 
            font=("Arial", 28, "bold"), 
            text_color="#2c3e50"
        ).pack(pady=(100, 10))

        ctk.CTkLabel(
            self.contenido, 
            text=f"Has ingresado como: {self.usuario_actual['rol']}", 
            font=("Arial", 16), 
            text_color="#6b7280"
        ).pack()

        ctk.CTkLabel(
            self.contenido, 
            text="Seleccione una opción en el menú superior para comenzar.", 
            font=("Arial", 14), 
            text_color="#9ca3af"
        ).pack(pady=30)

    def mostrar_empleados(self):
        """Carga la vista CRUD de empleados en el área de contenido."""
        for widget in self.contenido.winfo_children():
            widget.destroy()
            
        from views.empleados_view import EmpleadosView
        vista = EmpleadosView(self.contenido, usuario_actual=self.usuario_actual['username'])
        vista.pack(fill="both", expand=True)
        self.update()

    def mostrar_marcaje(self):
        """Carga la vista del reloj de marcaje."""
        for widget in self.contenido.winfo_children():
            widget.destroy()
            
        from views.marcaje_view import MarcajeView
        vista = MarcajeView(self.contenido)
        vista.pack(fill="both", expand=True)
        self.update()

    def mostrar_auditoria(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()
            
        from views.auditoria_view import AuditoriaView
        vista = AuditoriaView(self.contenido)
        vista.pack(fill="both", expand=True)
        self.update()   

    def cerrar_sesion(self):
        respuesta = messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea salir?")
        if respuesta:
            self.destroy()
            self.update()

    def mostrar_nomina(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()
            
        from views.nomina_view import NominaView
        vista = NominaView(self.contenido)
        vista.pack(fill="both", expand=True)
        self.update()

    def mostrar_gestion_marcajes(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()
            self.update()
            
        from views.gestion_marcajes_view import GestionMarcajesView
        vista = GestionMarcajesView(self.contenido, usuario_actual=self.usuario_actual['username'])
        vista.pack(fill="both", expand=True)
        self.update()   