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
            SELECT u.cedula, u.nombres, u.apellidos, u.telefono, u.correo, 
                   u.fecha_nacimiento, u.estado, 
                   COALESCE(s.nombre, 'Sin Servicio'), u.fecha_registro
            FROM usuarios u
            LEFT JOIN membresias_servicios ms ON u.membresia_id = ms.membresia_id
            LEFT JOIN servicios s ON ms.servicio_id = s.id
            WHERE u.rol = 'Entrenador'
        """)
        datos = cursor.fetchall()
        conn.close()
        for item in tabla.get_children():
            tabla.delete(item)
        for fila in datos:
            tabla.insert("", "end", values=fila)

    def editar_entrenador():
        """Abre una ventana para editar la información de un entrenador, membresía y sus servicios."""
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
        entry_telefono = Entry(frame_izq)
        entry_telefono.insert(0, datos[3])
        entry_telefono.pack(fill="x")

        Label(frame_izq, text="Correo:", bg="#272643", fg="white").pack(anchor="w")
        entry_correo = Entry(frame_izq)
        entry_correo.insert(0, datos[4])
        entry_correo.pack(fill="x")

        # Membresía
        Label(frame_izq, text="Membresía:", bg="#272643", fg="white").pack(anchor="w")
        combo_membresia = ttk.Combobox(frame_izq, state="readonly")
        combo_membresia.pack(fill="x")

        # Obtener Membresías Disponibles
        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM membresias")
        membresias = [m[0] for m in cursor.fetchall()]
        conn.close()

        combo_membresia["values"] = membresias
        combo_membresia.set(datos[6])  # Establecer membresía actual

        # Marco Derecho - Lista de Servicios
        frame_der = Frame(ventana_editar, bg="#272643", padx=20, pady=20)
        frame_der.pack(side="right", fill="both", expand=True)

        Label(frame_der, text="Servicios Disponibles", font=("Segoe UI", 14, "bold"), fg="white", bg="#272643").pack(pady=5)

        scroll_y = Scrollbar(frame_der, orient="vertical")
        lista_servicios = Listbox(frame_der, selectmode="multiple", height=12, yscrollcommand=scroll_y.set)
        scroll_y.config(command=lista_servicios.yview)

        lista_servicios.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Cargar los servicios desde la base de datos
        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM servicios")
        servicios = cursor.fetchall()

        # Cargar servicios disponibles en la lista
        for servicio in servicios:
            lista_servicios.insert("end", servicio[0])

        # Seleccionar los servicios ya asignados
        cursor.execute("""
            SELECT s.nombre FROM servicios s
            JOIN membresias_servicios ms ON s.id = ms.servicio_id
            JOIN usuarios u ON ms.membresia_id = u.membresia_id
            WHERE u.cedula = ?
        """, (datos[0],))
        
        servicios_asignados = cursor.fetchall()
        conn.close()

        servicios_asignados = [s[0] for s in servicios_asignados]

        for idx in range(lista_servicios.size()):
            if lista_servicios.get(idx) in servicios_asignados:
                lista_servicios.selection_set(idx)

        def actualizar_entrenador():
            """Actualiza la información del entrenador en la base de datos."""
            nuevo_nombres = entry_nombres.get()
            nuevo_apellidos = entry_apellidos.get()
            nuevo_telefono = entry_telefono.get()
            nuevo_correo = entry_correo.get()
            nueva_membresia = combo_membresia.get()
            cedula = datos[0]

            if not (nuevo_nombres and nuevo_apellidos and nuevo_telefono and nuevo_correo and nueva_membresia):
                messagebox.showerror("Error", "Todos los campos deben estar llenos")
                return

            conn = conexion_db()
            cursor = conn.cursor()
            try:
                # Obtener ID de la membresía seleccionada
                cursor.execute("SELECT id FROM membresias WHERE nombre = ?", (nueva_membresia,))
                membresia_id = cursor.fetchone()[0]

                cursor.execute("""
                    UPDATE usuarios SET nombres = ?, apellidos = ?, telefono = ?, correo = ?, membresia_id = ? WHERE cedula = ?
                """, (nuevo_nombres, nuevo_apellidos, nuevo_telefono, nuevo_correo, membresia_id, cedula))

                # Actualizar servicios asignados
                cursor.execute("DELETE FROM membresias_servicios WHERE membresia_id = (SELECT membresia_id FROM usuarios WHERE cedula = ?)", (cedula,))
                
                for idx in lista_servicios.curselection():
                    servicio_nombre = lista_servicios.get(idx)
                    cursor.execute("""
                        INSERT INTO membresias_servicios (membresia_id, servicio_id)
                        VALUES ((SELECT membresia_id FROM usuarios WHERE cedula = ?), (SELECT id FROM servicios WHERE nombre = ?))
                    """, (cedula, servicio_nombre))

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

    def registrar_entrenador():
        """Abre una ventana para registrar un nuevo entrenador."""
        ventana_registro = tk.Toplevel()
        ventana_registro.title("Registrar Entrenador")
        ventana_registro.geometry("600x500")
        ventana_registro.configure(bg="#272643")

        # --- Contenedor Izquierdo (Formulario) ---
        frame_izq = Frame(ventana_registro, bg="#272643", padx=20, pady=20)
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
        entry_fecha_nacimiento = DateEntry(frame_izq, background="darkblue", foreground="white", date_pattern="dd-mm-yyyy")
        entry_fecha_nacimiento.pack(fill="x")

        # --- Selección de Membresía ---
        Label(frame_izq, text="Membresía:", bg="#272643", fg="white").pack(anchor="w")
        combo_membresia = ttk.Combobox(frame_izq, state="readonly")
        combo_membresia.pack(fill="x")

        # Obtener Membresías Disponibles
        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM membresias")
        membresias = [m[0] for m in cursor.fetchall()]
        conn.close()

        combo_membresia["values"] = membresias
        if membresias:
            combo_membresia.set(membresias[0])

        # --- Contenedor Derecho (Servicios) ---
        frame_der = Frame(ventana_registro, bg="#272643", padx=20, pady=20)
        frame_der.pack(side="right", fill="both", expand=True)

        Label(frame_der, text="Servicios Disponibles", font=("Segoe UI", 14, "bold"), fg="white", bg="#272643").pack(pady=5)

        scroll_y = Scrollbar(frame_der, orient="vertical")
        lista_servicios = Listbox(frame_der, selectmode="multiple", height=12, yscrollcommand=scroll_y.set)
        scroll_y.config(command=lista_servicios.yview)

        lista_servicios.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Cargar los servicios desde la base de datos
        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM servicios")
        servicios = cursor.fetchall()

        for servicio in servicios:
            lista_servicios.insert("end", servicio[0])

        conn.close()

        def guardar_entrenador():
            """Guarda el nuevo entrenador en la base de datos evitando duplicaciones."""
            cedula = entry_cedula.get()
            nombres = entry_nombres.get()
            apellidos = entry_apellidos.get()
            telefono = entry_telefono.get()
            correo = entry_correo.get()
            fecha_nacimiento = entry_fecha_nacimiento.get()
            membresia = combo_membresia.get()

            if not (cedula and nombres and apellidos and telefono and correo and fecha_nacimiento and membresia):
                messagebox.showerror("Error", "Todos los campos deben estar llenos")
                return

            conn = conexion_db()
            cursor = conn.cursor()

            try:
                # Verificar si ya existe la cédula
                cursor.execute("SELECT cedula FROM usuarios WHERE cedula = ?", (cedula,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "La cédula ya está registrada en el sistema.")
                    return

                # Obtener ID de la membresía seleccionada
                cursor.execute("SELECT id FROM membresias WHERE nombre = ?", (membresia,))
                membresia_id = cursor.fetchone()[0]

                # Insertar entrenador
                cursor.execute("""
                    INSERT INTO usuarios (cedula, nombres, apellidos, telefono, correo, fecha_nacimiento, rol, estado, membresia_id)
                    VALUES (?, ?, ?, ?, ?, ?, 'Entrenador', 'A', ?)
                """, (cedula, nombres, apellidos, telefono, correo, fecha_nacimiento, membresia_id))

                # Insertar servicios seleccionados
                for idx in lista_servicios.curselection():
                    servicio_nombre = lista_servicios.get(idx)
                    cursor.execute("""
                        INSERT INTO membresias_servicios (membresia_id, servicio_id)
                        VALUES (?, (SELECT id FROM servicios WHERE nombre = ?))
                    """, (membresia_id, servicio_nombre))

                conn.commit()
                messagebox.showinfo("Éxito", "Entrenador registrado correctamente")
                ventana_registro.destroy()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo registrar el entrenador: {e}")

            finally:
                conn.close()

        # Botón para guardar
        btn_guardar = Button(ventana_registro, text="Guardar", font=("Segoe UI", 14), bg="#bae8e8", command=guardar_entrenador)
        btn_guardar.pack(pady=20)

        # Botón para regresar sin guardar
        btn_cancelar = Button(ventana_registro, text="Cancelar", font=("Segoe UI", 14), bg="red", fg="white", command=ventana_registro.destroy)
        btn_cancelar.pack(pady=5)

    cargar_datos_entrenadores()

    # FOOTER
    frame_footer = Frame(ventana, bg="#2C3E50", pady=10)
    frame_footer.pack(fill="x", side="bottom")
    Label(frame_footer, text="Desarrollado por Toreto-Gym", font=("Segoe UI", 12), fg="white", bg="#2C3E50").pack()

    ventana.mainloop()

def regresar(callback, ventana):
    ventana.destroy()
    callback()