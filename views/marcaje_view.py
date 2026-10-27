"""
Vista para registrar Entradas y Salidas.
"""

import customtkinter as ctk
from tkinter import messagebox
from models.marcaje_model import registrar_marcaje

class MarcajeView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # --- Tarjeta Central ---
        self.tarjeta = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#d1d5db")
        self.tarjeta.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.tarjeta, 
            text="⏱️ Reloj Control", 
            font=("Arial", 24, "bold"), 
            text_color="#2c3e50"
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            self.tarjeta, 
            text="Ingrese su número de cédula para marcar", 
            font=("Arial", 14), 
            text_color="#6b7280"
        ).pack(pady=(0, 30))

        frame_cedula = ctk.CTkFrame(self.tarjeta, fg_color="transparent")
        frame_cedula.pack(pady=10)

        self.combo_prefijo = ctk.CTkOptionMenu(
            frame_cedula, 
            values=["V-", "E-"], 
            width=80,
            height=40,
            fg_color="#e5e7eb",
            text_color="#000000",
            button_color="#d1d5db",
            button_hover_color="#9ca3af"
        )
        self.combo_prefijo.pack(side="left", padx=(0, 10))

        self.entry_cedula = ctk.CTkEntry(
            frame_cedula, 
            width=220, 
            height=40, 
            placeholder_text="Número de cédula",
            font=("Arial", 16)
        )
        self.entry_cedula.pack(side="left")

        # Botones
        botones_frame = ctk.CTkFrame(self.tarjeta, fg_color="transparent")
        botones_frame.pack(pady=30)

        ctk.CTkButton(
            botones_frame, 
            text="Registrar ENTRADA", 
            fg_color="#2ecc71", 
            hover_color="#27ae60",
            width=140,
            height=45,
            font=("Arial", 14, "bold"),
            command=lambda: self.accion_marcar("entrada")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            botones_frame, 
            text="Registrar SALIDA", 
            fg_color="#e74c3c", 
            hover_color="#c0392b",
            width=140,
            height=45,
            font=("Arial", 14, "bold"),
            command=lambda: self.accion_marcar("salida")
        ).pack(side="left", padx=10)

    def accion_marcar(self, tipo):
        # Concatenamos el prefijo (ej: "V-") con el número de cédula
        cedula = self.combo_prefijo.get() + self.entry_cedula.get().strip()
        
        if len(cedula) <= 2: # Si solo puso "V-" y nada más
            messagebox.showwarning("Atención", "Por favor, ingrese un número de cédula.")
            return

        exito, mensaje = registrar_marcaje(cedula, tipo)

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.entry_cedula.delete(0, 'end') # Limpiamos el campo
        else:
            messagebox.showerror("Error", mensaje)