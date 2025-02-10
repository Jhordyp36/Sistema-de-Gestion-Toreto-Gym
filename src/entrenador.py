from datetime import datetime
import os
import sqlite3
import tkinter as tk
from tkinter import Button, Entry, Frame, Label, Listbox, Scrollbar, StringVar, Tk, messagebox, ttk
from tkcalendar import DateEntry

from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono

def conexion_db():
    """Conecta a la base de datos SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def ventana_entrenadores(usuario, callback):
    """ Crea la ventana de Entrenadores. """
    ventana = Tk()
    ventana.title("Administración de Entrenadores")
    ventana.state("zoomed")
    ventana.resizable(False, False)
    ventana.configure(bg="#272643")
    cargar_icono(ventana, os.path.join(ICONS_DIR, "Icono.ico"))

    # HEADER
    frame_header = Frame(ventana, bg="#2C3E50", pady=10)
    frame_header.pack(fill="x")
    Label(frame_header, text="Gestión de Entrenadores y Servicios", font=("Segoe UI", 18, "bold"), fg="white", bg="#2C3E50").pack()

    # BOTONES PRINCIPALES
    frame_botones_principales = Frame(ventana, bg="#2c698d", pady=10)
    frame_botones_principales.pack(fill="x", padx=20)

    btn_registrar = Button(frame_botones_principales, text="Registrar Entrenador", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: registrar_entrenador())
    btn_registrar.pack(side="left", padx=10)    
    
    btn_editar = Button(frame_botones_principales, text="Editar Información", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: editar_entrenador())
    btn_editar.pack(side="left", padx=10)

    btn_eliminar = Button(frame_botones_principales, text="Eliminar Entrenador", font=("Segoe UI", 14), bg="red", fg="white", command=lambda: eliminar_entrenador())
    btn_eliminar.pack(side="left", padx=10)  
    
    btn_regresar = Button(frame_botones_principales, text="Regresar", font=("Segoe UI", 14), bg="red", fg="white", command=lambda: regresar(callback, ventana))
    btn_regresar.pack(side="left", padx=10)
    
    # CONTENEDOR PRINCIPAL
    frame_contenido = Frame(ventana, bg="#272643")
    frame_contenido.pack(fill="both", expand=True, padx=20, pady=20)

    # TÍTULO DE LA TABLA
    Label(frame_contenido, text="Lista de Entrenadores", font=("Segoe UI", 16, "bold"), fg="white", bg="#272643").pack(pady=10)

    # FRAME DE LA TABLA
    frame_tabla = Frame(frame_contenido, bg="#272643")
    frame_tabla.pack(expand=True, fill="both", padx=20, pady=10)

    scroll_x = Scrollbar(frame_tabla, orient="horizontal")
    scroll_y = Scrollbar(frame_tabla, orient="vertical")

    columnas = ("Cédula", "Nombres", "Apellidos", "Teléfono", "Correo", "Fecha Nacimiento", "Estado", "Servicio", "Fecha Registro")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
    tabla.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    scroll_x.config(command=tabla.xview)
    scroll_y.config(command=tabla.yview)
    scroll_x.grid(row=2, column=0, columnspan=3, sticky="ew")
    scroll_y.grid(row=1, column=3, sticky="ns")

    for col in columnas:
        tabla.heading(col, text=col.capitalize())
        tabla.column(col, width=150, anchor="center")

    def cargar_datos_entrenadores():
        """Carga en la tabla los entrenadores registrados."""
        conn = conexion_db()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                u.cedula, 
                u.nombres, 
                u.apellidos, 
                u.telefono, 
                u.correo, 
                u.fecha_nacimiento, 
                u.estado, 
                COALESCE(GROUP_CONCAT(s.nombre, ', '), 'Sin Servicio'),
                u.fecha_registro
            FROM usuarios u
            LEFT JOIN membresias_servicios ms ON u.membresia_id = ms.membresia_id
            LEFT JOIN servicios s ON ms.servicio_id = s.id
            WHERE u.rol = 'Entrenador'
            GROUP BY u.cedula
        """)  # Agrupado por cédula y servicios concatenados
        datos = cursor.fetchall()
        conn.close()
        for item in tabla.get_children():
            tabla.delete(item)
        for fila in datos:
            tabla.insert("", "end", values=fila)

    def eliminar_entrenador():
        """Elimina un entrenador seleccionado de la base de datos."""
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un entrenador para eliminar")
            return

        item = tabla.item(seleccionado[0])
        cedula = item['values'][0]

        respuesta = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar al entrenador con cédula {cedula}?")
        if not respuesta:
            return

        conn = conexion_db()
        cursor = conn.cursor()
        try:
            # Eliminar servicios relacionados con la membresía del entrenador
            cursor.execute("""
                DELETE FROM membresias_servicios 
                WHERE membresia_id = (SELECT membresia_id FROM usuarios WHERE cedula = ?)
            """, (cedula,))

            # Eliminar al entrenador
            cursor.execute("DELETE FROM usuarios WHERE cedula = ?", (cedula,))
            conn.commit()

            messagebox.showinfo("Éxito", "Entrenador eliminado correctamente")
            cargar_datos_entrenadores()  # Refrescar la tabla

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el entrenador: {e}")

        finally:
            conn.close()

    def registrar_entrenador():
        """Abre la interfaz de registro de entrenadores."""
        ventana_registrar = tk.Toplevel()
        ventana_registrar.title("Registrar Entrenador")
        ventana_registrar.geometry("900x500")
        ventana_registrar.configure(bg="#272643")

        # Frame izquierdo - Datos del entrenador
        frame_izq = Frame(ventana_registrar, bg="#272643", padx=20, pady=20)
        frame_izq.pack(side="left", fill="y")

        Label(frame_izq, text="Registrar Nuevo Entrenador", font=("Segoe UI", 14, "bold"), fg="white", bg="#272643").pack(pady=5)

        Label(frame_izq, text="Cédula:", bg="#272643", fg="white").pack(anchor="w")
        entry_cedula = Entry(frame_izq)
        entry_cedula.pack(fill="x")

        Label(frame_izq, text="Nombres:", bg="#272643", fg="white").pack(anchor="w")
        entry_nombres = Entry(frame_izq)
        entry_nombres.pack(fill="x")

        Label(frame_izq, text="Apellidos:", bg="#272643", fg="white").pack(anchor="w")
        entry_apellidos = Entry(frame_izq)
        entry_apellidos.pack(fill="x")

        Label(frame_izq, text="Teléfono:", bg="#272643", fg="white").pack(anchor="w")
        entry_telefono = Entry(frame_izq)
        entry_telefono.pack(fill="x")

        Label(frame_izq, text="Correo:", bg="#272643", fg="white").pack(anchor="w")
        entry_correo = Entry(frame_izq)
        entry_correo.pack(fill="x")

        Label(frame_izq, text="Fecha de Nacimiento:", bg="#272643", fg="white").pack(anchor="w")
        entry_fecha_nacimiento = DateEntry(frame_izq, width=28, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        entry_fecha_nacimiento.pack(fill="x")

        # Frame derecho - Selección de servicios
        frame_der = Frame(ventana_registrar, bg="#272643", padx=20, pady=20)
        frame_der.pack(side="right", fill="both", expand=True)

        Label(frame_der, text="Seleccionar Servicios", font=("Segoe UI", 14, "bold"), fg="white", bg="#272643").pack(pady=5)

        scroll_y = Scrollbar(frame_der, orient="vertical")
        lista_servicios = Listbox(frame_der, selectmode="single", height=12, yscrollcommand=scroll_y.set)
        scroll_y.config(command=lista_servicios.yview)

        lista_servicios.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Cargar servicios desde la base de datos
        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM servicios WHERE disponible = 'Si'")
        servicios = cursor.fetchall()
        conn.close()

        for servicio in servicios:
            lista_servicios.insert("end", f"{servicio[0]} - {servicio[1]}")

        def guardar_entrenador():
            """Guarda el nuevo entrenador en la base de datos."""
            cedula = entry_cedula.get().strip()
            nombres = entry_nombres.get().strip()
            apellidos = entry_apellidos.get().strip()
            correo = entry_correo.get().strip()
            telefono = entry_telefono.get().strip()
            fecha_nacimiento = entry_fecha_nacimiento.get_date()
            fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Obtener la fecha actual

            # Corregir el formato del teléfono
            if not telefono.startswith("0"):
                telefono = "0" + telefono  # Asegurar que tenga el 0 inicial

            conn = conexion_db()
            cursor = conn.cursor()

            try:
                # Obtener el ID de la membresía "VIP"
                cursor.execute("SELECT id FROM membresias WHERE nombre = 'VIP'")
                membresia_vip = cursor.fetchone()
                if not membresia_vip:
                    messagebox.showerror("Error", "No se encontró la membresía 'VIP' en la base de datos.")
                    return
                membresia_id = membresia_vip[0]

                # Insertar en la tabla usuarios
                cursor.execute("""
                    INSERT INTO usuarios (cedula, nombres, apellidos, usuario, contrasena, telefono, correo, rol, estado, fecha_nacimiento, membresia_id, fecha_registro)
                    VALUES (?, ?, ?, NULL, NULL, ?, ?, 'Entrenador', 'A', ?, ?, ?)
                """, (cedula, nombres, apellidos, telefono, correo, fecha_nacimiento, membresia_id, fecha_registro))

                # Obtener ID de los servicios seleccionados
                servicios_seleccionados = lista_servicios.curselection()

                # Limpiar servicios anteriores en caso de que ya existan
                cursor.execute("DELETE FROM membresias_servicios WHERE membresia_id = ?", (membresia_id,))

                for index in servicios_seleccionados:
                    servicio_id = int(lista_servicios.get(index).split(" - ")[0])
                    cursor.execute("INSERT INTO membresias_servicios (membresia_id, servicio_id) VALUES (?, ?)", (membresia_id, servicio_id))

                conn.commit()
                messagebox.showinfo("Éxito", "Entrenador registrado correctamente.")
                ventana_registrar.destroy()
                cargar_datos_entrenadores()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo registrar el entrenador: {e}")
            finally:
                conn.close()

        # Botón para guardar
        Button(ventana_registrar, text="Guardar", font=("Segoe UI", 12), bg="#bae8e8", command=guardar_entrenador).pack(pady=10)

        # Botón para cancelar
        Button(ventana_registrar, text="Cancelar", font=("Segoe UI", 12), bg="#bae8e8", command=ventana_registrar.destroy).pack(pady=5)


    def editar_entrenador():
        """Abre una ventana para editar la información de un entrenador, sin modificar la membresía (se mantiene en VIP)."""
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un entrenador para editar")
            return

        item = tabla.item(seleccionado[0])
        datos = item['values']

        ventana_editar = tk.Toplevel(ventana)
        ventana_editar.title("Editar Entrenador")
        ventana_editar.geometry("900x500")
        ventana_editar.configure(bg="#272643")

        # Marco Izquierdo - Información del Entrenador
        frame_izq = Frame(ventana_editar, bg="#272643", padx=20, pady=20)
        frame_izq.pack(side="left", fill="y")

        Label(frame_izq, text="Editar Información del Entrenador", font=("Segoe UI", 14, "bold"), fg="white", bg="#272643").pack(pady=5)

        Label(frame_izq, text="Cédula:", bg="#272643", fg="white").pack(anchor="w")
        entry_cedula = Entry(frame_izq)
        entry_cedula.insert(0, datos[0])
        entry_cedula.config(state="disabled")  # No se puede modificar la cédula
        entry_cedula.pack(fill="x")

        Label(frame_izq, text="Nombres:", bg="#272643", fg="white").pack(anchor="w")
        entry_nombres = Entry(frame_izq)
        entry_nombres.insert(0, datos[1])
        entry_nombres.pack(fill="x")

        Label(frame_izq, text="Apellidos:", bg="#272643", fg="white").pack(anchor="w")
        entry_apellidos = Entry(frame_izq)
        entry_apellidos.insert(0, datos[2])
        entry_apellidos.pack(fill="x")

        Label(frame_izq, text="Teléfono:", bg="#272643", fg="white").pack(anchor="w")
        telefono = str(datos[3])  # Convertir a string
        if len(telefono) == 9:  # Si falta el "0" inicial
            telefono = "0" + telefono  # Agregar "0" al inicio
        
        entry_telefono = Entry(frame_izq)
        entry_telefono.insert(0, telefono)
        entry_telefono.pack(fill="x")

        Label(frame_izq, text="Correo:", bg="#272643", fg="white").pack(anchor="w")
        entry_correo = Entry(frame_izq)
        entry_correo.insert(0, datos[4])
        entry_correo.pack(fill="x")

        # Marco Derecho - Lista de Servicios
        frame_der = Frame(ventana_editar, bg="#272643", padx=20, pady=20)
        frame_der.pack(side="right", fill="both", expand=True)

        Label(frame_der, text="Servicios Disponibles", font=("Segoe UI", 14, "bold"), fg="white", bg="#272643").pack(pady=5)

        scroll_y = Scrollbar(frame_der, orient="vertical")
        lista_servicios = Listbox(frame_der, selectmode="single", height=12, yscrollcommand=scroll_y.set)
        scroll_y.config(command=lista_servicios.yview)

        lista_servicios.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Cargar los servicios desde la base de datos
        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM servicios")
        servicios = cursor.fetchall()

        # Insertar servicios en la lista
        for servicio in servicios:
            lista_servicios.insert("end", f"{servicio[0]} - {servicio[1]}")

        # Obtener servicios actuales del entrenador
        cursor.execute("""
            SELECT s.id, s.nombre FROM servicios s
            JOIN membresias_servicios ms ON s.id = ms.servicio_id
            JOIN usuarios u ON ms.membresia_id = u.membresia_id
            WHERE u.cedula = ?
        """, (datos[0],))

        servicios_asignados = cursor.fetchall()
        conn.close()

        # Seleccionar servicios actuales
        servicios_asignados_ids = [str(s[0]) for s in servicios_asignados]
        for idx in range(lista_servicios.size()):
            if lista_servicios.get(idx).split(" - ")[0] in servicios_asignados_ids:
                lista_servicios.selection_set(idx)

        def actualizar_entrenador():
            """Actualiza la información del entrenador en la base de datos."""
            nuevo_nombres = entry_nombres.get()
            nuevo_apellidos = entry_apellidos.get()
            nuevo_telefono = entry_telefono.get()
            nuevo_correo = entry_correo.get()
            cedula = datos[0]

            # Corregir formato del teléfono
            if not nuevo_telefono.startswith("0"):
                nuevo_telefono = "0" + nuevo_telefono  # Asegurar que tenga el 0 inicial

            conn = conexion_db()
            cursor = conn.cursor()

            try:
                # Obtener ID de la membresía "VIP"
                cursor.execute("SELECT id FROM membresias WHERE nombre = 'VIP'")
                membresia_vip = cursor.fetchone()
                if not membresia_vip:
                    messagebox.showerror("Error", "No se encontró la membresía 'VIP' en la base de datos.")
                    return
                membresia_id = membresia_vip[0]

                # Actualizar información del entrenador
                cursor.execute("""
                    UPDATE usuarios 
                    SET nombres = ?, apellidos = ?, telefono = ?, correo = ?, membresia_id = ? 
                    WHERE cedula = ?
                """, (nuevo_nombres, nuevo_apellidos, nuevo_telefono, nuevo_correo, membresia_id, cedula))

                # Eliminar servicios previos y actualizar con los nuevos
                cursor.execute("DELETE FROM membresias_servicios WHERE membresia_id = ?", (membresia_id,))

                seleccion = lista_servicios.curselection()
                for idx in seleccion:
                    servicio_id = int(lista_servicios.get(idx).split(" - ")[0])
                    cursor.execute("INSERT INTO membresias_servicios (membresia_id, servicio_id) VALUES (?, ?)", (membresia_id, servicio_id))

                conn.commit()
                messagebox.showinfo("Éxito", "Entrenador actualizado correctamente")
                ventana_editar.destroy()
                cargar_datos_entrenadores()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo actualizar el entrenador: {e}")
            finally:
                conn.close()

        # Botón de actualización
        btn_actualizar = Button(ventana_editar, text="Actualizar", font=("Segoe UI", 12), bg="#bae8e8", command=actualizar_entrenador)
        btn_actualizar.pack(pady=10)

        # Botón para regresar a la ventana general sin cerrar el programa
        btn_regresar = Button(ventana_editar, text="Regresar", font=("Segoe UI", 12), bg="#bae8e8", command=ventana_editar.destroy)
        btn_regresar.pack(pady=5)

    cargar_datos_entrenadores()

    # FOOTER
    frame_footer = Frame(ventana, bg="#2C3E50", pady=10)
    frame_footer.pack(fill="x", side="bottom")
    Label(frame_footer, text="Desarrollado por Toreto-Gym", font=("Segoe UI", 12), fg="white", bg="#2C3E50").pack()

    ventana.mainloop()

def regresar(callback, ventana):
    ventana.destroy()
    callback()