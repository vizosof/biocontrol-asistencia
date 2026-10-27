"""
Vista CRUD de Empleados.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from models.empleado_model import obtener_empleados, crear_empleado, actualizar_empleado, eliminar_empleado


class EmpleadosView(ctk.CTkFrame):
    def __init__(self, master, usuario_actual="Sistema"):
        super().__init__(master, fg_color="transparent")
        self.usuario_actual = usuario_actual
        # --- Título y Botón Agregar ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text="Gestión de Empleados", font=("Arial", 24, "bold"), text_color="#2c3e50").pack(side="left")
        
        self.btn_agregar = ctk.CTkButton(header_frame, text="+ Nuevo Empleado", fg_color="#2c3e50", hover_color="#1a252f", command=self.abrir_formulario)
        self.btn_agregar.pack(side="right")

        # --- Contenedor Principal (Tabla + Botones) ---
        self.contenedor_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_tabla.pack(fill="x", pady=10)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#ffffff", foreground="black", rowheight=30, fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        columnas = ("ID", "Cédula", "Nombre", "Apellido", "Cargo", "Sueldo Base", "Estado")
        
        # --- NUEVO: Contenedor para la tabla y su scrollbar ---
        frame_tabla_y_scroll = ctk.CTkFrame(self.contenedor_tabla, fg_color="transparent")
        frame_tabla_y_scroll.pack(fill="x")

        self.tabla = ttk.Treeview(frame_tabla_y_scroll, columns=columnas, show="headings", height=12)
        
        # Agregamos el Scrollbar
        scrollbar = ttk.Scrollbar(frame_tabla_y_scroll, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        # Empaquetamos la tabla a la izquierda y el scrollbar a la derecha
        self.tabla.pack(side="left", fill="x", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor="center")
        
        self.tabla.column("ID", width=50)
        self.tabla.column("Nombre", width=150)
        self.tabla.column("Apellido", width=150)

        # --- Botones de Acción (Justo debajo de la tabla) ---
        acciones_frame = ctk.CTkFrame(self.contenedor_tabla, fg_color="transparent")
        acciones_frame.pack(fill="x", pady=(10, 0)) 
        
        ctk.CTkButton(acciones_frame, text="Editar Seleccionado", fg_color="#f39c12", hover_color="#e67e22", width=150, command=self.editar_seleccionado).pack(side="left", padx=(0, 10))
        ctk.CTkButton(acciones_frame, text="Eliminar Seleccionado", fg_color="#e74c3c", hover_color="#c0392b", width=150, command=self.eliminar_seleccionado).pack(side="left")

        # Cargar datos iniciales
        self.cargar_tabla()

    def cargar_tabla(self):
        """Limpia la tabla y vuelve a cargar los datos de la BD."""
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        empleados = obtener_empleados()
        for emp in empleados:
            self.tabla.insert("", "end", values=(
                emp["id"], emp["cedula"], emp["nombre"], emp["apellido"], 
                emp["cargo"], f"${emp['sueldo_base']:.2f}", emp["estado"]
            ))

    def abrir_formulario(self, empleado=None):
        """Abre una ventana modal para crear o editar."""
        FormularioEmpleado(self, al_guardar=self.cargar_tabla, empleado=empleado, usuario=self.usuario_actual)

    def editar_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un empleado de la tabla.")
            return
        
        item = self.tabla.item(seleccion[0])
        emp_id = item['values'][0]
        
        empleados = obtener_empleados()
        empleado_editar = next((e for e in empleados if e["id"] == emp_id), None)
        
        if empleado_editar:
            self.abrir_formulario(empleado_editar)

    def eliminar_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Seleccione un empleado de la tabla.")
            return
        
        item = self.tabla.item(seleccion[0])
        emp_id = item['values'][0]
        
        if messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este empleado?"):
            exito, msg = eliminar_empleado(emp_id, usuario=self.usuario_actual)
            if exito:
                messagebox.showinfo("Éxito", msg)
                self.cargar_tabla()
            else:
                messagebox.showerror("Error", msg)


# =================================================================
# VENTANA FLOTANTE (FORMULARIO)
# =================================================================
class FormularioEmpleado(ctk.CTkToplevel):
    """Ventana flotante para Crear/Editar Empleado."""
    def __init__(self, master, al_guardar, empleado=None, usuario="Sistema"):
        super().__init__(master)
        self.al_guardar = al_guardar
        self.empleado = empleado
        self.usuario = usuario

        self.title("Editar Empleado" if empleado else "Nuevo Empleado")
        self.geometry("400x600") # Altura suficiente para que se vea todo
        self.resizable(False, False)
        
        # Trucos para que la ventana aparezca al frente y dibuje bien los campos
        self.lift()
        self.focus_force()
        self.grab_set()
        self.update_idletasks() 

        ctk.CTkLabel(self, text="Datos del Empleado", font=("Arial", 18, "bold")).pack(pady=20)

        # --- Fila para la Cédula con el prefijo ---
        ctk.CTkLabel(self, text="Cédula", font=("Arial", 12)).pack(anchor="w", padx=40)
        
        frame_cedula = ctk.CTkFrame(self, fg_color="transparent")
        frame_cedula.pack(fill="x", padx=40, pady=(0, 10))

        self.combo_prefijo = ctk.CTkOptionMenu(
            frame_cedula, 
            values=["V-", "E-"], 
            width=70,
            fg_color="#e5e7eb",
            text_color="#000000",
            button_color="#d1d5db",
            button_hover_color="#9ca3af"
        )
        self.combo_prefijo.pack(side="left", padx=(0, 10))

        self.entry_cedula = ctk.CTkEntry(frame_cedula, width=240)
        self.entry_cedula.pack(side="left", fill="x", expand=True)

        # Los demás campos
        self.entry_nombre = self.crear_campo("Nombre")
        self.entry_apellido = self.crear_campo("Apellido")
        self.entry_cargo = self.crear_campo("Cargo")
        self.entry_sueldo = self.crear_campo("Sueldo Base (Mensual)")

        if empleado:
            # Si estamos editando, cargamos los datos
            cedula_completa = empleado["cedula"]
            if "-" in cedula_completa:
                prefijo, numero = cedula_completa.split("-", 1)
                self.combo_prefijo.set(prefijo + "-")
                self.entry_cedula.insert(0, numero)
            else:
                self.entry_cedula.insert(0, cedula_completa)

            self.entry_cedula.configure(state="disabled") # No se puede cambiar la cédula
            self.entry_nombre.insert(0, empleado["nombre"])
            self.entry_apellido.insert(0, empleado["apellido"])
            self.entry_cargo.insert(0, empleado["cargo"])
            self.entry_sueldo.insert(0, str(empleado["sueldo_base"]))

        ctk.CTkButton(self, text="Guardar Datos", fg_color="#2c3e50", hover_color="#1a252f", width=320, height=40, command=self.guardar).pack(pady=30)

    def crear_campo(self, label_text):
        ctk.CTkLabel(self, text=label_text, font=("Arial", 12)).pack(anchor="w", padx=40)
        entry = ctk.CTkEntry(self, width=320)
        entry.pack(pady=(0, 10))
        return entry

    def guardar(self):
        cedula = self.combo_prefijo.get() + self.entry_cedula.get().strip()
        nombre = self.entry_nombre.get().strip().title()
        apellido = self.entry_apellido.get().strip().title()
        cargo = self.entry_cargo.get().strip().title()

        try:
            sueldo = float(self.entry_sueldo.get())
        except ValueError:
            messagebox.showerror("Error", "El sueldo debe ser un número válido.")
            return

        if not all([cedula, nombre, apellido, cargo]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if self.empleado:
            exito = actualizar_empleado(self.empleado["id"], nombre, apellido, cargo, sueldo, self.empleado["estado"], usuario=self.usuario)
            if exito:
                self.al_guardar()
                self.destroy()
        else:
            exito, msg = crear_empleado(cedula, nombre, apellido, cargo, sueldo,usuario=self.usuario)
            if exito:
                self.al_guardar()
                self.destroy()
            else:
                messagebox.showerror("Error", msg)