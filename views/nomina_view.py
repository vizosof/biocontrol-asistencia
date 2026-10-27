"""
Vista del Reporte de Nómina.
"""

import customtkinter as ctk
from tkinter import ttk
from models.nomina_model import calcular_nomina_mensual

class NominaView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # --- Título ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Reporte de Nómina", font=("Arial", 24, "bold"), text_color="#2c3e50").pack(side="left")
        
        self.btn_actualizar = ctk.CTkButton(header_frame, text="🔄 Actualizar Nómina", fg_color="#2c3e50", command=self.cargar_datos)
        self.btn_actualizar.pack(side="right")

        # --- Contenedor Principal ---
        self.contenedor_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_tabla.pack(fill="x", pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#ffffff", foreground="black", rowheight=30, fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        columnas = ("Cédula", "Empleado", "Sueldo Base", "H. Normales", "H. Extras", "Pago Total")
        
        frame_tabla_y_scroll = ctk.CTkFrame(self.contenedor_tabla, fg_color="transparent")
        frame_tabla_y_scroll.pack(fill="x")

        self.tabla = ttk.Treeview(frame_tabla_y_scroll, columns=columnas, show="headings", height=12)
        
        scrollbar = ttk.Scrollbar(frame_tabla_y_scroll, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar columnas
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=120, anchor="center")

        # Cargar datos
        self.cargar_datos()

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        reporte = calcular_nomina_mensual()
        for reg in reporte:
            self.tabla.insert("", "end", values=(
                reg["cedula"], 
                reg["nombre"], 
                f"${reg['sueldo_base']:.2f}", 
                f"{reg['horas_trabajadas'] - reg['horas_extras']:.2f} hs", # Horas normales
                f"{reg['horas_extras']:.2f} hs", # Horas extras
                f"${reg['pago_total']:.2f}"
            ))