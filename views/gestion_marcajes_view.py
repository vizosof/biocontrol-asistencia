"""
Vista exclusiva para que el Administrador corrija los marcajes.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from models.marcaje_model import obtener_todos_los_marcajes, actualizar_marcaje_admin

class GestionMarcajesView(ctk.CTkFrame):
    def __init__(self, master, usuario_actual):
        super().__init__(master, fg_color="transparent")
        self.usuario_actual = usuario_actual

        # --- Título ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Corrección de Marcajes", font=("Arial", 24, "bold"), text_color="#2c3e50").pack(side="left")
        
        ctk.CTkButton(header_frame, text="🔄 Actualizar", fg_color="#2c3e50", command=self.cargar_tabla).pack(side="right")

        # --- Tabla ---
        frame_tabla = ctk.CTkFrame(self, fg_color="transparent")
        frame_tabla.pack(fill="x", pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#ffffff", foreground="black", rowheight=30, fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        columnas = ("ID", "Cédula", "Empleado", "Fecha", "Entrada", "Salida", "Horas", "Estado")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        self.tabla.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self.al_seleccionar_marcaje)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor="center")

        # --- Formulario de Edición ---
        editar_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        editar_frame.pack(fill="x", pady=20, padx=20)

        ctk.CTkLabel(editar_frame, text="Seleccione un marcaje de la tabla para corregirlo:", font=("Arial", 14, "bold")).pack(pady=10)

        campos_frame = ctk.CTkFrame(editar_frame, fg_color="transparent")
        campos_frame.pack(pady=10)

        ctk.CTkLabel(campos_frame, text="Hora Entrada (HH:MM:SS):").pack(side="left", padx=5)
        self.entry_entrada = ctk.CTkEntry(campos_frame, width=120)
        self.entry_entrada.pack(side="left", padx=5)

        ctk.CTkLabel(campos_frame, text="Hora Salida (HH:MM:SS):").pack(side="left", padx=5)
        self.entry_salida = ctk.CTkEntry(campos_frame, width=120)
        self.entry_salida.pack(side="left", padx=5)

        ctk.CTkButton(campos_frame, text="Guardar Corrección", fg_color="#f39c12", hover_color="#e67e22", command=self.guardar_correccion).pack(side="left", padx=20)

        self.cargar_tabla()

    def cargar_tabla(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        marcajes = obtener_todos_los_marcajes()
        for m in marcajes:
            self.tabla.insert("", "end", values=(
                m["id"], m["cedula"], f"{m['nombre']} {m['apellido']}", 
                m["fecha"], m["entrada"] or "---", m["salida"] or "---", 
                f"{m['horas_trabajadas']:.2f} hs", m["estado"]
            ))

    def al_seleccionar_marcaje(self, event):
        """Rellena los campos de texto cuando el admin hace clic en una fila."""
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        
        item = self.tabla.item(seleccion[0])
        valores = item['values']
        
        # Los valores de la tabla son: (ID, Cédula, Empleado, Fecha, Entrada, Salida, Horas, Estado)
        # El índice 4 es Entrada y el 5 es Salida.
        hora_entrada = valores[4]
        hora_salida = valores[5]

        self.entry_entrada.delete(0, 'end')
        self.entry_salida.delete(0, 'end')

        # Si dice "---" es porque no había hora, así que dejamos el campo vacío
        if hora_entrada != "---":
            self.entry_entrada.insert(0, hora_entrada)
        if hora_salida != "---":
            self.entry_salida.insert(0, hora_salida)

    def guardar_correccion(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un marcaje de la tabla.")
            return

        item = self.tabla.item(seleccion[0])
        marcaje_id = item['values'][0]
        
        nueva_entrada = self.entry_entrada.get().strip()
        nueva_salida = self.entry_salida.get().strip()

        if not nueva_entrada and not nueva_salida:
            messagebox.showwarning("Atención", "Debe ingresar al menos una hora.")
            return

        exito, msg = actualizar_marcaje_admin(marcaje_id, nueva_entrada, nueva_salida, self.usuario_actual)
        
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_tabla()
            self.entry_entrada.delete(0, 'end')
            self.entry_salida.delete(0, 'end')
        else:
            messagebox.showerror("Error", msg)