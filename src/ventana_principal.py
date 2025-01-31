import os
from tkinter import CENTER, Button, Frame, Label, PhotoImage, Tk
from config.config import ICONS_DIR, IMAGES_DIR
from src.utils.helpers import cargar_icono
from src.administracion_sistema import ventana_administracion
from src.servicios import GestionServicios
from src.membresias import ventana_membresias

def crear_ventana_principal(usuario, callback):
    # Configuración de la ventana principal
    ventana_principal = Tk()
    ventana_principal.title("Sistemas de Gestión de Reservas Toreto Gym")
    ventana_principal.state('zoomed')
    ventana_principal.configure(bg="#272643")
    cargar_icono(ventana_principal, os.path.join(ICONS_DIR, "Icono.ico"))

    # Imagen de logotipo
    imagen_logotipo = PhotoImage(file=os.path.join(IMAGES_DIR, "Logotipo.png"))
    label_imagen = Label(ventana_principal, image=imagen_logotipo, bg="#272643")
    label_imagen.place(x=0, y=0, relwidth=1)

    # Etiqueta de bienvenida
    label = Label(ventana_principal, text=f"Bienvenido, {usuario}", font=("Segoe UI", 18, "bold"), bg="#272643", fg="white")
    label.place(relx=0.5, rely=0.2, anchor=CENTER)

    # Frame para organizar los botones
    frame_botones = Frame(ventana_principal, bg="#2c698d", padx=10, pady=10)
    frame_botones.place(relx=0.5, rely=0.5, anchor=CENTER)

    # Funciones de los botones
    def abrir_membresias():
        """Abre la ventana de gestión de membresías."""
        ventana_principal.destroy()
        ventana_membresias(usuario, lambda: crear_ventana_principal(usuario, callback))

    def abrir_servicios():
        """Abre la ventana de gestión de servicios y permite regresar."""
        ventana_principal.destroy()
        root = Tk()
        app = GestionServicios(root, callback_regreso=lambda: crear_ventana_principal(usuario, callback))
        root.mainloop()

    def abrir_pagos_facturacion():
        print("En proceso")

    def abrir_administracion():
        ventana_principal.destroy()
        ventana_administracion(lambda: crear_ventana_principal(usuario, callback))

    def abrir_gestion_equipos():
        print("En proceso")

    # Creación de botones
    boton_membresias = Button(
        frame_botones,
        text="Membresías",
        font=("Segoe UI", 12),
        width=20,
        height=2,
        bg="#bae8e8",
        fg="black",
        command=abrir_membresias,
        relief="groove",
        bd=2
    )
    boton_membresias.grid(row=0, column=0, padx=10, pady=10)

    boton_servicios = Button(
        frame_botones,
        text="Servicios",
        font=("Segoe UI", 12),
        width=20,
        height=2,
        bg="#bae8e8",
        fg="black",
        command=abrir_servicios,
        relief="groove",
        bd=2
    )
    boton_servicios.grid(row=0, column=1, padx=10, pady=10)

    boton_pagos_facturacion = Button(
        frame_botones,
        text="Pagos y Facturación",
        font=("Segoe UI", 12),
        width=20,
        height=2,
        bg="#bae8e8",
        fg="black",
        command=abrir_pagos_facturacion,
        relief="groove",
        bd=2
    )
    boton_pagos_facturacion.grid(row=1, column=0, padx=10, pady=10)

    boton_administracion = Button(
        frame_botones,
        text="Administración del Sistema",
        font=("Segoe UI", 12),
        width=20,
        height=2,
        bg="#bae8e8",
        fg="black",
        command=abrir_administracion,
        relief="groove",
        bd=2
    )
    boton_administracion.grid(row=1, column=1, padx=10, pady=10)

    boton_gestion_equipos = Button(
        frame_botones,
        text="Gestión de Equipos",
        font=("Segoe UI", 12),
        width=20,
        height=2,
        bg="#bae8e8",
        fg="black",
        command=abrir_gestion_equipos,
        relief="groove",
        bd=2
    )
    boton_gestion_equipos.grid(row=2, column=0, padx=10, pady=10)

    boton_cerrar = Button(
        frame_botones,
        text="Cerrar sesión",
        font=("Segoe UI", 12, "bold"),
        width=20,
        height=2,
        bg="#e3f6f5",
        fg="black",
        command=lambda: regresar(callback, ventana_principal),
        relief="groove",
        bd=2
    )
    boton_cerrar.grid(row=3, column=0, columnspan=2, pady=20)

    ventana_principal.mainloop()

def regresar(callback, ventana):
    ventana.destroy()
    callback()

