"""
Vista de Auditoría (Bitácora).
"""

import customtkinter as ctk
from tkinter import ttk
from models.auditoria_model import obtener_auditoria

class AuditoriaView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # --- Título y Botón Actualizar ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Bitácora del Sistema", font=("Arial", 24, "bold"), text_color="#2c3e50").pack(side="left")
        
        self.btn_actualizar = ctk.CTkButton(header_frame, text="🔄 Actualizar", fg_color="#2c3e50", hover_color="#1a252f", command=self.cargar_datos)
        self.btn_actualizar.pack(side="right")

        # --- Contenedor Principal ---
        self.contenedor_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_tabla.pack(fill="x", pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#ffffff", foreground="black", rowheight=30, fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        columnas = ("ID", "Fecha y Hora", "Usuario", "Acción", "Detalles")
        
        frame_tabla_y_scroll = ctk.CTkFrame(self.contenedor_tabla, fg_color="transparent")
        frame_tabla_y_scroll.pack(fill="x")

        self.tabla = ttk.Treeview(frame_tabla_y_scroll, columns=columnas, show="headings", height=15)
        
        scrollbar = ttk.Scrollbar(frame_tabla_y_scroll, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar columnas
        self.tabla.heading("ID", text="ID")
        self.tabla.column("ID", width=50, anchor="center")
        
        self.tabla.heading("Fecha y Hora", text="Fecha y Hora")
        self.tabla.column("Fecha y Hora", width=150, anchor="center")
        
        self.tabla.heading("Usuario", text="Usuario")
        self.tabla.column("Usuario", width=100, anchor="center")
        
        self.tabla.heading("Acción", text="Acción")
        self.tabla.column("Acción", width=120, anchor="center")
        
        self.tabla.heading("Detalles", text="Detalles")
        self.tabla.column("Detalles", width=400, anchor="w")

        # Cargar datos
        self.cargar_datos()

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        registros = obtener_auditoria()
        for reg in registros:
            self.tabla.insert("", "end", values=(
                reg["id"], 
                reg["fecha_hora"], 
                reg["usuario_responsable"], 
                reg["accion"], 
                reg["detalles"]
            ))