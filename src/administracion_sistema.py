import calendar
from datetime import datetime
import os
import sqlite3
import tkinter as tk
from tkinter import Listbox, filedialog
from tkinter.ttk import Combobox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import Button, Frame, Label, Entry, Scrollbar, StringVar, Tk, ttk, messagebox
from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono, verifica_correo, verifica_fecha_nacimiento, verifica_identificacion, verifica_nombres_apellidos, verifica_telefono

SECUENCIA_CORRECTA = ["Up", "Up", "Down", "Down", "Left", "Right", "Left", "Right", "b", "a", "Return"]
secuencia_actual = []

def conexion_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None    

def ventana_administracion(callback):
    """
    Crea la ventana de Administración del Sistema.
    """
    ventana = Tk()
    ventana.title("Administración del Sistema")
    ventana.state("zoomed")
    ventana.resizable(False,False)
    ventana.configure(bg="#272643")
    cargar_icono(ventana, os.path.join(ICONS_DIR, "Icono.ico"))
    
    # Botones principales
    frame_botones_principales = Frame(ventana, bg="#2c698d", pady = 5)
    frame_botones_principales.pack(side="top", fill="x")
    
    # Contenedor principal dinámico
    frame_contenido = Frame(ventana, bg="#272643")
    frame_contenido.pack(fill="both", expand=True, padx=20, pady=20)
    
    def cargar_administracion_usuarios():
        limpiar_contenido()
        
        # Botones del módulo "Administración de Usuarios"
        frame_botones = Frame(frame_contenido, bg="#272643")
        frame_botones.pack(side="top", fill="x")

        Button(frame_botones, text="Registar Cliente/Entrenador", font=("Segoe UI", 12), bg="#bae8e8", command=crear_cliente_entrenador).pack(side="left", padx=10, pady=10)
        Button(frame_botones, text="Editar Información", font=("Segoe UI", 12), bg="#bae8e8", command=lambda: editar_informacion()).pack(side="left", padx=10, pady=10)
        Button(frame_botones, text="Eliminar", font=("Segoe UI", 12), bg="#bae8e8", command=lambda: eliminar_usuario(tabla)).pack(side="left", padx=10, pady=10)
        
        # Etiqueta de título
        Label(frame_contenido, text="Consultar Usuarios", font=("Segoe UI", 16), bg="#272643", fg="white").pack(pady=10)

        # Frame contenedor de la tabla
        frame_tabla = Frame(frame_contenido, bg="#272643")
        frame_tabla.pack(fill="both", expand=True)

        # Barra de búsqueda
        Label(frame_tabla, text="Buscar:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        busqueda_var = StringVar()
        Entry(frame_tabla, textvariable=busqueda_var, width=30).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        # Button(frame_tabla, text="Buscar", command=lambda: cargar_datos(tabla, busqueda_var.get())).grid(row=0, column=2, padx=10, pady=5)
        Button(frame_tabla, text="Buscar", command=lambda: consultar_busqueda(busqueda_var.get(), tabla)).grid(row=0, column=2, padx=10, pady=5)

        # Scrollbars
        scroll_x = Scrollbar(frame_tabla, orient="horizontal")
        scroll_y = Scrollbar(frame_tabla, orient="vertical")

        # Tabla
        columnas = ("cedula", "apellidos", "nombres", "telefono", "correo", "rol", "estado", "fecha_nacimiento", "membresia", "fecha_registro")
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        tabla.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Configurar las barras de desplazamiento
        scroll_x.config(command=tabla.xview)
        scroll_y.config(command=tabla.yview)
        scroll_x.grid(row=2, column=0, columnspan=3, sticky="ew")
        scroll_y.grid(row=1, column=3, sticky="ns")

        # Encabezados y ajuste de anchos
        for col in columnas:
            tabla.heading(col, text=col.capitalize())
            tabla.column(col, width=100, anchor="center")  # Ajusta el ancho según tus necesidades

        # Ajustar tamaño del frame_tabla
        frame_tabla.grid_rowconfigure(1, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        
        cargar_datos(tabla)

    def crear_cliente_entrenador():
        limpiar_contenido()
        
        # Crear el marco para el formulario
        frame_formulario = tk.Frame(frame_contenido, bg="#272643")
        frame_formulario.pack(side="top", expand=True)

        # Centrar el formulario
        frame_formulario.grid(row=0, column=0, padx=10, pady=10)

        # Campos de entrada
        tk.Label(frame_formulario, text="Cédula:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_cedula = tk.Entry(frame_formulario, font=("Segoe UI", 12))
        entry_cedula.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame_formulario, text="Nombres:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_nombres = tk.Entry(frame_formulario, font=("Segoe UI", 12))
        entry_nombres.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame_formulario, text="Apellidos:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_apellidos = tk.Entry(frame_formulario, font=("Segoe UI", 12))
        entry_apellidos.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame_formulario, text="Correo:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_correo = tk.Entry(frame_formulario, font=("Segoe UI", 12))
        entry_correo.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        tk.Label(frame_formulario, text="Teléfono:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        entry_telefono = tk.Entry(frame_formulario, font=("Segoe UI", 12))
        entry_telefono.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        # Etiquetas y combobox para fecha de nacimiento
        tk.Label(frame_formulario, text="Fecha de nacimiento:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=5, column=0, padx=10, pady=5, sticky="w")

        # Día
        tk.Label(frame_formulario, text="Día:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        entry_dia = Combobox(frame_formulario, font=("Segoe UI", 12), values=[str(i).zfill(2) for i in range(1, 32)])
        entry_dia.grid(row=7, column=1, padx=10, pady=5, sticky="w")
        
        # Mes
        tk.Label(frame_formulario, text="Mes:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=8, column=0, padx=10, pady=5, sticky="w")
        entry_mes = Combobox(frame_formulario, font=("Segoe UI", 12), values=[str(i).zfill(2) for i in range(1, 13)])
        entry_mes.grid(row=8, column=1, padx=10, pady=5, sticky="w")
        
        # Año
        tk.Label(frame_formulario, text="Año:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=9, column=0, padx=10, pady=5, sticky="w")
        entry_ano = Combobox(frame_formulario, font=("Segoe UI", 12), values=[str(i) for i in range(1900, 2026)])
        entry_ano.grid(row=9, column=1, padx=10, pady=5, sticky="w")
        
        # Día
        tk.Label(frame_formulario, text="Rol:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        entry_rol = Combobox(frame_formulario, font=("Segoe UI", 12), values=('Cliente', 'Entrenador'))
        entry_rol.grid(row=6, column=1, padx=10, pady=5, sticky="w")

        def actualizar_dias():
            # Obtener mes y año seleccionados
            mes = int(entry_mes.get() if entry_mes.get() else 1)
            ano = int(entry_ano.get() if entry_ano.get() else 2025)
            
            # Ajustar los días según el mes y año
            dias_en_mes = calendar.monthrange(ano, mes)[1]
            entry_dia['values'] = [str(i).zfill(2) for i in range(1, dias_en_mes + 1)]
            if int(entry_dia.get()) > dias_en_mes:
                entry_dia.set(str(dias_en_mes).zfill(2))

        entry_mes.bind("<<ComboboxSelected>>", lambda event: actualizar_dias())
        entry_ano.bind("<<ComboboxSelected>>", lambda event: actualizar_dias())

        def guardar_cliente():
            # Obtener los valores del formulario
            cedula = entry_cedula.get().strip()
            cedula = str(cedula).zfill(10)
            nombres = entry_nombres.get().strip()
            apellidos = entry_apellidos.get().strip()
            correo = entry_correo.get().strip()
            telefono = entry_telefono.get().strip()
            fecha_nacimiento = f"{entry_dia.get()}-{entry_mes.get()}-{entry_ano.get()}"
            rol = f"{entry_rol.get()}"
            fecha_hora_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Validaciones
            if not verifica_identificacion(cedula):
                messagebox.showerror("Error", "La cédula ingresada no es válida.")
                return

            if not verifica_nombres_apellidos(nombres) or not verifica_nombres_apellidos(apellidos):
                messagebox.showerror("Error", "Los nombres y apellidos deben ser válidos.")
                return
            
            if not verifica_correo(correo):
                messagebox.showerror("Error", "El correo electrónico no es válido.")
                return

            if not verifica_telefono(telefono):
                messagebox.showerror("Error", "El número de teléfono no es válido.")
                return

            if not verifica_fecha_nacimiento(fecha_nacimiento):
                messagebox.showerror("Error", "La fecha de nacimiento no es válida o la persona es menor de edad.")
                return

            # Guardar en la base de datos
            try:
                conn = conexion_db()
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO usuarios (cedula, apellidos, nombres, telefono, correo, rol, fecha_nacimiento, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (cedula, apellidos, nombres, telefono, correo, rol, fecha_nacimiento, fecha_hora_actual),
                )
                cursor.execute(
                        "INSERT INTO logs (usuario, fecha_hora, accion) VALUES (?, ?, ?)",
                        ("admin", fecha_hora_actual, f"Creación usuario: {cedula}"),
                    )
                conn.commit()
                messagebox.showinfo("Éxito", "Cliente registrado correctamente.")
                cargar_administracion_usuarios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el cliente: {e}")
            finally:
                conn.close()

        tk.Button(frame_formulario, text="Guardar", font=("Segoe UI", 12), command=guardar_cliente).grid(row=10, column=0, padx=10, pady=10, sticky="e")
        tk.Button(frame_formulario, text="Cancelar", font=("Segoe UI", 12), command=cargar_administracion_usuarios).grid(row=10, column=1, padx=10, pady=10, sticky="e")

    def editar_informacion():
        limpiar_contenido()

        # Crear frame para la barra de búsqueda
        frame_busqueda_editar = tk.Frame(frame_contenido, bg="#272643")
        frame_busqueda_editar.pack(pady=5, padx=10)

        label_buscar_editar = tk.Label(frame_busqueda_editar, text="Buscar:", font=("Segoe UI", 12), bg="#272643", fg="#ffffff")
        label_buscar_editar.pack(side="left", padx=5)

        entry_buscar_editar = tk.Entry(frame_busqueda_editar, font=("Segoe UI", 12), width=30)
        entry_buscar_editar.pack(side="left", padx=5)
        
        btn_buscar_editar = tk.Button(frame_busqueda_editar, text="Buscar", font=("Segoe UI", 12), bg="#bae8e8", command=lambda: consultar_busqueda_editar(entry_buscar_editar.get(), tree_editar))
        btn_buscar_editar.pack(side="left", padx=5)

        # Tabla de resultados
        columns_editar = ("Cédula", "Apellidos", "Nombres", "Correo", "Teléfono", "Rol", "Fecha Nacimiento")
        tree_editar = ttk.Treeview(frame_contenido, columns=columns_editar, show="headings", height=10)
        for col in columns_editar:
            tree_editar.heading(col, text=col)
            tree_editar.column(col, anchor="center", width=150)

        tree_editar.pack(padx=10, pady=10)

        # Frame para los campos de edición
        frame_editar_campos = tk.Frame(frame_contenido, bg="#272643")
        frame_editar_campos.pack(pady=10, padx=10)

        # Labels y Entries para editar los campos
        label_apellidos = tk.Label(frame_editar_campos, text="Apellidos:", font=("Segoe UI", 12), bg="#272643", fg="#ffffff")
        label_apellidos.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_apellidos = tk.Entry(frame_editar_campos, font=("Segoe UI", 12), width=30)
        entry_apellidos.grid(row=0, column=1, padx=5, pady=5)

        label_nombres = tk.Label(frame_editar_campos, text="Nombres:", font=("Segoe UI", 12), bg="#272643", fg="#ffffff")
        label_nombres.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_nombres = tk.Entry(frame_editar_campos, font=("Segoe UI", 12), width=30)
        entry_nombres.grid(row=1, column=1, padx=5, pady=5)

        label_telefono = tk.Label(frame_editar_campos, text="Teléfono:", font=("Segoe UI", 12), bg="#272643", fg="#ffffff")
        label_telefono.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entry_telefono = tk.Entry(frame_editar_campos, font=("Segoe UI", 12), width=30)
        entry_telefono.grid(row=2, column=1, padx=5, pady=5)

        label_correo = tk.Label(frame_editar_campos, text="Correo:", font=("Segoe UI", 12), bg="#272643", fg="#ffffff")
        label_correo.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        entry_correo = tk.Entry(frame_editar_campos, font=("Segoe UI", 12), width=30)
        entry_correo.grid(row=3, column=1, padx=5, pady=5)
        
        def seleccionar_usuario(event):
            item = tree_editar.selection()
            if item:
                # Cargar datos en las entries
                datos_usuario = tree_editar.item(item)["values"]
                entry_apellidos.delete(0, "end")
                entry_apellidos.insert(0, datos_usuario[1])
                entry_nombres.delete(0, "end")
                entry_nombres.insert(0, datos_usuario[2])
                entry_correo.delete(0, "end")
                entry_correo.insert(0, datos_usuario[4])
                entry_telefono.delete(0, "end")
                entry_telefono.insert(0, "0" + str(datos_usuario[3]))
        
        tree_editar.bind("<ButtonRelease-1>", seleccionar_usuario)

        # Botones de guardar y cancelar
        frame_botones = tk.Frame(frame_contenido, bg="#272643")
        frame_botones.pack(pady=10)
        btn_guardar = tk.Button(frame_botones, text="Guardar", font=("Segoe UI", 12), bg="#bae8e8", command=lambda: guardar_cambios_usuarios(entry_apellidos, entry_nombres, entry_correo, entry_telefono, obtener_id_seleccionado(tree_editar)))

        btn_guardar.pack(side="left", padx=10)

        btn_cancelar = tk.Button(frame_botones, text="Cancelar", font=("Segoe UI", 12), bg="#bae8e8", command=cargar_administracion_usuarios)
        btn_cancelar.pack(side="left", padx=10)
        
        cargar_datos_edicion(tree_editar)

    def eliminar_usuario(tabla):
        seleccion = tabla.selection()
        fecha_hora_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        if not seleccion:
            messagebox.showwarning("Selección", "Por favor, seleccione un usuario para eliminar.")
            return

        usuario_id = tabla.item(seleccion[0])["values"][0]  # Cedula correctamente obtenida

        # Eliminar posibles espacios al inicio y final
        if str(usuario_id).strip() == "1234567890":
            messagebox.showwarning("Selección", "No es posible eliminar al Administrador")
            return

        conn = conexion_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET estado = 'X' WHERE cedula = ?", (usuario_id,))
            cursor.execute(
                        "INSERT INTO logs (usuario, fecha_hora, accion) VALUES (?, ?, ?)",
                        ("admin", fecha_hora_actual, f"Eliminación usuario: {usuario_id}"),
                    )
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
            cargar_administracion_usuarios()  # Recargar la tabla después de la eliminación
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al eliminar el usuario: {e}")
        finally:
            conn.close()

    def dejar_de_seleccionar(tabla_membresias, tabla_servicios):
        # Deseleccionar cualquier membresía seleccionada en la tabla
        tabla_membresias.selection_remove(tabla_membresias.selection())

        # Limpiar la tabla de servicios
        for row in tabla_servicios.get_children():
            tabla_servicios.delete(row)

    def cargar_membresias(tabla_membresias):
        # Conectar a la base de datos
        conn = conexion_db()
        cursor = conn.cursor()
        
        # Obtener las membresías sin la columna de servicios
        cursor.execute('''
            SELECT 
                m.id, 
                m.nombre, 
                m.precio, 
                m.duracion_dias,
                m.estado
            FROM 
                membresias m
        ''')
        membresias = cursor.fetchall()

        # Limpiar la tabla (si es necesario)
        for row in tabla_membresias.get_children():
            tabla_membresias.delete(row)

        # Insertar las membresías en el Treeview
        for membresia in membresias:
            tabla_membresias.insert("", "end", values=(membresia[0], membresia[1], membresia[2], membresia[3], membresia[4]))

        # Cerrar la conexión a la base de datos
        conn.close()

    def mostrar_servicios(tabla_servicios, membresia_id):
        
        if membresia_id is None:
            messagebox.showwarning("Selección inválida", "Por favor, selecciona una membresía.")
            return
        # Limpiar la tabla de servicios antes de cargar nuevos datos
        for row in tabla_servicios.get_children():
            tabla_servicios.delete(row)

        # Conectar a la base de datos
        conn = conexion_db()
        cursor = conn.cursor()

        try:
            # Obtener los servicios relacionados con la membresía seleccionada
            cursor.execute('''
                SELECT s.id, s.nombre
                FROM servicios s
                JOIN membresias_servicios ms ON s.id = ms.servicio_id
                WHERE ms.membresia_id = ?
            ''', (membresia_id,))
            servicios = cursor.fetchall()

            # Insertar los servicios en el Treeview
            for servicio in servicios:
                tabla_servicios.insert("", "end", values=(servicio[0], servicio[1]))
        except Exception as e:
            print(f"Error al obtener servicios: {e}")
        finally:
            # Cerrar la conexión a la base de datos
            conn.close()

    def obtener_id_seleccionado(tabla):
        seleccionado = tabla.selection()
        if seleccionado:
            valores = tabla.item(seleccionado[0], "values")
            return valores[0] 
        else:
            return None 

    def cargar_administracion_parametros():
        limpiar_contenido()
        # Obtener dimensiones de la pantalla
        screen_width = frame_contenido.winfo_screenwidth()

        # Calcular posiciones dinámicas
        btn_width = 150
        btn_height = 50

        # Botón Mostrar Servicios
        btn_mostrar_servicios = tk.Button(
            frame_contenido, text="Mostrar Servicios", command=lambda: mostrar_servicios(tabla2, obtener_id_seleccionado(tabla1)),
            font=("Segoe UI", 12), bg="#bae8e8", relief="flat"
        )
        btn_mostrar_servicios.place(
            x=1025, y=100, width=btn_width, height=btn_height
        )

        # Botón Editar Membresía
        btn_editar_membresia = tk.Button(
            frame_contenido, text="Editar Membresías", command= mostrar_edicion_membresia,
            font=("Segoe UI", 12), bg="#bae8e8", relief="flat"
        )
        btn_editar_membresia.place(
            x=250, y=100, width=btn_width, height=btn_height
        )
        
        # Botón Dejar de Seleccionar
        btn_dejar_de_seleccionar = tk.Button(
            frame_contenido, text="Dejar de Seleccionar", command=lambda: dejar_de_seleccionar(tabla1, tabla2),
            font=("Segoe UI", 12), bg="#bae8e8", relief="flat"
        )
        btn_dejar_de_seleccionar.place(
            x=500, y=100, width=btn_width, height=btn_height
        )

        # Tabla 1
        frame_tabla1 = tk.Frame(frame_contenido, bg="lightblue")
        frame_tabla1.place(
            x=150,  # Posición horizontal (izquierda)
            y=200,  # Centrado vertical
            width=600,
            height=500
        )


        label_tabla1 = tk.Label(frame_tabla1, text="Membresías", bg="lightblue", font=("Segoe UI", 12))
        label_tabla1.pack(anchor="n", pady=5)

        columns_tabla1 = ("ID", "Nombre", "Precio", "Duración(días)", "Estado")
        tabla1 = ttk.Treeview(frame_tabla1, columns=columns_tabla1, show="headings")
        # Configurar el ancho de cada columna y permitir que se ajusten
        tabla1.column("ID", anchor="center", width=50, stretch=True)  # Ancho fijo inicial
        tabla1.column("Nombre", anchor="w", width=100, stretch=True)  # Más ancho para texto largo
        tabla1.column("Precio", anchor="center", width=80, stretch=True)
        tabla1.column("Duración(días)", anchor="center", width=120, stretch=True)
        tabla1.column("Estado", anchor="center", width=120, stretch=True)

        # Agregar encabezados
        tabla1.heading("ID", text="ID")
        tabla1.heading("Nombre", text="Nombre")
        tabla1.heading("Precio", text="Precio")
        tabla1.heading("Duración(días)", text="Duración(días)")
        tabla1.heading("Estado", text="Estado")

        # Mostrar la tabla
        tabla1.pack(expand=True, fill="both")

        # Tabla 2
        frame_tabla2 = tk.Frame(frame_contenido, bg="lightblue")
        frame_tabla2.place(
            x=(screen_width / 2) + 50,  # Posición horizontal (derecha)
            y=200,  # Centrado vertical
            width=600,
            height=500
        )

        label_tabla2 = tk.Label(frame_tabla2, text="Servicios", bg="lightblue", font=("Segoe UI", 12))
        label_tabla2.pack(anchor="n", pady=5)

        # Definir columnas como una tupla
        columns_tabla2 = ("ID", "Servicios")
        tabla2 = ttk.Treeview(frame_tabla2, columns=columns_tabla2, show="headings")

        # Configurar el ancho de cada columna y permitir que se ajusten
        tabla2.column("ID", anchor="center", stretch=True)  # Ancho inicial
        tabla2.column("Servicios", anchor="center", stretch=True)  # Ancho inicial
        # Agregar encabezados
        tabla2.heading("ID", text="ID")
        tabla2.heading("Servicios", text="Servicios")

        # Mostrar la tabla en el frame
        tabla2.pack(expand=True, fill="both")

        # Cargar datos en tabla1
        cargar_membresias(tabla1)

    def mostrar_edicion_membresia():
        limpiar_contenido()
        
        Label(frame_contenido, text="Editar Membresía", font=("Segoe UI", 16), bg="#272643", fg="white").pack(pady=10)
        
        # Frame principal de la ventana de edición
        frame_edicion = Frame(frame_contenido, bg="#272643")
        frame_edicion.pack(pady=10, fill="both", expand=True)
        
        # Frame de la parte izquierda (para la edición de duración, estado y servicios)
        frame_izquierda = Frame(frame_edicion, bg="#272643")
        frame_izquierda.pack(side="left", padx=20, fill="y", expand=True)
        
        # Edición de duración
        Label(frame_izquierda, text="Duración (días):", bg="#272643", fg="white").pack()
        entry_duracion = Entry(frame_izquierda)
        entry_duracion.pack(pady=5)
        
        # Estado de la membresía
        Label(frame_izquierda, text="Estado:", bg="#272643", fg="white").pack()
        estado_var = StringVar()
        estado_dropdown = ttk.Combobox(frame_izquierda, textvariable=estado_var, values=["Activo", "Inactivo"])
        estado_dropdown.pack(pady=5)
        
        # Precio de la membresía
        Label(frame_izquierda, text="Precio:", bg="#272643", fg="white").pack()
        entry_precio = Entry(frame_izquierda)
        entry_precio.pack(pady=5)
        
        # Sección para seleccionar servicios
        Label(frame_izquierda, text="Seleccionar Servicios:", bg="#272643", fg="white").pack()
        frame_servicios = Frame(frame_izquierda, bg="#272643")
        frame_servicios.pack(pady=5)

        lista_servicios = Listbox(frame_servicios, selectmode="multiple", height=8, width=25)
        lista_servicios.pack(side="left", padx=5)

        scrollbar_servicios = Scrollbar(frame_servicios, orient="vertical", command=lista_servicios.yview)
        scrollbar_servicios.pack(side="right", fill="y")
        lista_servicios.configure(yscrollcommand=scrollbar_servicios.set)

        Button(frame_izquierda, text="Agregar Servicio", command=lambda: agregar_servicio(lista_servicios, tabla_servicios)).pack(pady=5)

        # Botón para deseleccionar todos los servicios
        Button(frame_izquierda, text="Deseleccionar Todos", command=lambda: deseleccionar_todos(lista_servicios)).pack(pady=5)

        # Función para deseleccionar todos los elementos en la lista de servicios
        def deseleccionar_todos(lista_servicios):
            lista_servicios.selection_clear(0, "end")
        
        # Frame de la parte derecha (tabla para mostrar servicios seleccionados)
        frame_derecha = Frame(frame_edicion, bg="#272643")
        frame_derecha.pack(side="right", padx=20, fill="y", expand=True)
        
        Label(frame_derecha, text="Servicios Seleccionados", bg="#272643", fg="white").pack()
        
        # Crear la tabla (Treeview) para mostrar servicios
        tabla_servicios = ttk.Treeview(frame_derecha, columns=("ID", "Servicio"), show="headings", height=4)
        tabla_servicios.heading("ID", text="ID")
        tabla_servicios.heading("Servicio", text="Servicio")
        tabla_servicios.column("ID", width=50, anchor="center")
        tabla_servicios.column("Servicio", width=200, anchor="center")
        tabla_servicios.pack(fill="y", expand=True)

        Button(frame_derecha, text="Eliminar Servicio", command=lambda: eliminar_servicio(tabla_servicios)).pack(pady=5)
        
        # Tabla de las membresías
        Label(frame_edicion, text="Membresías Disponibles", bg="#272643", fg="white").pack()
        tabla_membresias = ttk.Treeview(frame_edicion, columns=("ID", "Nombre", "Precio", "Duración(días)", "Estado"), show="headings", height=4)
        tabla_membresias.column("ID", width=50, anchor="center")
        tabla_membresias.column("Nombre", width=150, anchor="w")
        tabla_membresias.column("Precio", width=100, anchor="center")
        tabla_membresias.column("Duración(días)", width=120, anchor="center")
        tabla_membresias.column("Estado", width=100, anchor="center")
        
        for col in tabla_membresias["columns"]:
            tabla_membresias.heading(col, text=col)
        
        tabla_membresias.pack(fill="both", expand=True)
        
        def seleccionar_membresia(event):
            item = tabla_membresias.selection()
            if item:
                # Cargar datos en las entries
                datos_membresia = tabla_membresias.item(item)["values"]
                entry_duracion.delete(0, "end")
                entry_duracion.insert(0, datos_membresia[3])
                entry_precio.delete(0, "end")
                entry_precio.insert(0, datos_membresia[2])
                estado_var.set(datos_membresia[4])
                
                mostrar_servicios(tabla_servicios, datos_membresia[0])
        
        tabla_membresias.bind("<ButtonRelease-1>", seleccionar_membresia)
        
        Button(frame_contenido, text="Guardar Cambios", bg="#bae8e8", font=("Segoe UI", 12),
            command=lambda: guardar_cambios_membresia(entry_duracion, estado_var, entry_precio, tabla_servicios, obtener_id_seleccionado(tabla_membresias))).pack(pady=10, side="left", padx=10)
        
        Button(frame_contenido, text="Cancelar", bg="#bae8e8", font=("Segoe UI", 12), command=cargar_administracion_parametros).pack(pady=10, side="left", padx=10)
        
        cargar_servicios_disponibles(lista_servicios)
        cargar_membresias(tabla_membresias)

    def agregar_servicio(lista_servicios, tabla_servicios):
        try:
            # Obtener los servicios seleccionados
            seleccionados = lista_servicios.curselection()
            if not seleccionados:
                messagebox.showwarning("Selección Vacía", "Por favor, seleccione un servicio.")
                return

            # Obtener los servicios ya agregados a la tabla
            servicios_existentes = [tabla_servicios.item(item)["values"][1] for item in tabla_servicios.get_children()]

            # Conectar a la base de datos
            conn = conexion_db()
            cursor = conn.cursor()

            for index in seleccionados:
                servicio_nombre = lista_servicios.get(index)

                # Verificar si el servicio ya está en la tabla
                if servicio_nombre in servicios_existentes:
                    messagebox.showwarning("Servicio Duplicado", f"El servicio '{servicio_nombre}' ya está incluido.")
                    continue  # Saltar al siguiente servicio

                # Consultar el ID del servicio por su nombre
                cursor.execute('''SELECT id FROM servicios WHERE nombre = ?''', (servicio_nombre,))
                servicio_id = cursor.fetchone()

                if servicio_id:
                    # Agregar el servicio a la tabla de servicios seleccionados
                    tabla_servicios.insert('', 'end', values=(servicio_id[0], servicio_nombre))

            # Cerrar la conexión
            conn.close()

        except Exception as e:
            print(f"Error al agregar servicio: {e}")

    def cargar_servicios_disponibles(lista_servicios):
        try:
            # Conectar a la base de datos
            conn = conexion_db()
            cursor = conn.cursor()

            # Consultar los servicios disponibles
            cursor.execute('''SELECT nombre FROM servicios WHERE disponible = 'Si' ''')
            servicios = cursor.fetchall()

            # Limpiar la lista de servicios (si ya tiene elementos previos)
            lista_servicios.delete(0, 'end')

            # Llenar la lista con los servicios disponibles
            for servicio in servicios:
                lista_servicios.insert('end', servicio[0])

            # Cerrar la conexión
            conn.close()

        except Exception as e:
            print(f"Error al cargar los servicios disponibles: {e}")

    def eliminar_servicio(tabla_servicios):
        selected_item = tabla_servicios.selection()
        if selected_item:
            tabla_servicios.delete(selected_item)

    def guardar_cambios_usuarios(entry_apellidos, entry_nombres, entry_correo, entry_telefono, cedula):
        # Obtener los valores actualizados de los entrys
        apellidos = entry_apellidos.get()
        nombres = entry_nombres.get()
        correo = entry_correo.get()
        telefono = entry_telefono.get()
        fecha_hora_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")


        # Validaciones
        if not verifica_nombres_apellidos(nombres) or not verifica_nombres_apellidos(apellidos):
            messagebox.showerror("Error", "Los nombres y apellidos deben ser válidos.")
            return
        
        if not verifica_correo(correo):
            messagebox.showerror("Error", "El correo electrónico no es válido.")
            return

        if not verifica_telefono(telefono):
            messagebox.showerror("Error", "El número de teléfono no es válido.")
            return

        try:
            conn = conexion_db()
            cursor = conn.cursor()

            # 1. Recuperar los datos actuales del usuario
            cursor.execute('''SELECT apellidos, nombres, correo, telefono FROM usuarios WHERE cedula = ?''', (cedula,))
            datos_usuario = cursor.fetchone()

            # Si no existe el usuario, mostrar mensaje de error
            if not datos_usuario:
                messagebox.showerror("Error", "Usuario no encontrado.")
                return

            # 2. Verificar si los datos nuevos son diferentes a los actuales
            if (apellidos == datos_usuario[0] and 
                nombres == datos_usuario[1] and 
                correo == datos_usuario[2] and 
                telefono == datos_usuario[3]):
                messagebox.showinfo("Sin cambios", "No hay cambios en los datos.")
                return

            # 3. Si hay cambios, actualizar la información en la base de datos
            cursor.execute('''
                UPDATE usuarios
                SET apellidos = ?, nombres = ?, correo = ?, telefono = ?
                WHERE cedula = ?
            ''', (apellidos, nombres, correo, telefono, cedula))

            cursor.execute(
                        "INSERT INTO logs (usuario, fecha_hora, accion) VALUES (?, ?, ?)",
                        ("admin", fecha_hora_actual, f"Edición usuario: {cedula}"),
                    )

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Los datos se han actualizado correctamente")
            editar_informacion()

        except Exception as e:
            print(f"Error al guardar cambios: {e}")
            messagebox.showerror("Error", "Hubo un problema al guardar los cambios.")

    def guardar_cambios_membresia(entry_duracion, estado_var, entry_precio, tabla_servicios, membresia_id):
        try:
            # Obtener los valores actualizados de los entrys y la tabla de servicios
            duracion = entry_duracion.get()  # Duración en días
            estado = estado_var.get()        # Estado de la membresía
            precio = entry_precio.get()      # Precio de la membresía
            fecha_hora_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # Conectar a la base de datos
            conn = conexion_db()
            cursor = conn.cursor()

            # 1. Recuperar los datos actuales de la membresía
            cursor.execute('''SELECT duracion_dias, estado, precio FROM membresias WHERE id = ?''', (membresia_id,))
            datos_membresia = cursor.fetchone()

            if not datos_membresia:
                messagebox.showerror("Error", "Membresía no encontrada.")
                conn.close()
                return

            # 2. Recuperar los servicios actualmente asignados a la membresía
            cursor.execute('''SELECT servicio_id FROM membresias_servicios WHERE membresia_id = ?''', (membresia_id,))
            servicios_actuales = {row[0] for row in cursor.fetchall()}  # Conjunto de servicios actuales

            # 3. Obtener los servicios nuevos de la tabla
            servicios_nuevos = {int(tabla_servicios.item(fila, 'values')[0]) for fila in tabla_servicios.get_children()}  

            # 4. Verificar si hubo algún cambio
            datos_iguales = (duracion == str(datos_membresia[0]) and 
                            estado == datos_membresia[1] and 
                            precio == str(datos_membresia[2]))

            servicios_iguales = (servicios_actuales == servicios_nuevos)

            if datos_iguales and servicios_iguales:
                messagebox.showinfo("Sin cambios", "No hay cambios en los datos.")
                conn.close()
                return

            # 5. Si hay cambios en los datos, actualizar la membresía
            cursor.execute('''UPDATE membresias SET duracion_dias = ?, estado = ?, precio = ? WHERE id = ?''', 
                        (duracion, estado, precio, membresia_id))

            # 6. Si hay cambios en los servicios, actualizar la relación
            if not servicios_iguales:
                cursor.execute('''DELETE FROM membresias_servicios WHERE membresia_id = ?''', (membresia_id,))
                for servicio_id in servicios_nuevos:
                    cursor.execute('''INSERT INTO membresias_servicios (membresia_id, servicio_id) VALUES (?, ?)''', 
                                (membresia_id, servicio_id))

            # 7. Registrar la acción en los logs
            cursor.execute("INSERT INTO logs (usuario, fecha_hora, accion) VALUES (?, ?, ?)",
                        ("admin", fecha_hora_actual, f"Edición membresía: {membresia_id}"))

            # Confirmar cambios
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", "Los datos se han actualizado correctamente.")
            mostrar_edicion_membresia()

        except Exception as e:
            print(f"Error al guardar cambios: {e}")
            messagebox.showerror("Error", "Hubo un problema al guardar los cambios.")

    def verificar_secuencia(event):
        global secuencia_actual
        secuencia_actual.append(event.keysym)
        
        if secuencia_actual == SECUENCIA_CORRECTA:
            cargar_auditoria()
            secuencia_actual.clear()
        elif len(secuencia_actual) > len(SECUENCIA_CORRECTA) or secuencia_actual != SECUENCIA_CORRECTA[:len(secuencia_actual)]:
            secuencia_actual.clear()

    def cargar_auditoria():
        limpiar_contenido()

        Label(frame_contenido, text="Auditoría", font=("Segoe UI", 16), bg="#272643", fg="white").pack(pady=10)
        # Crear tabla para mostrar los logs
        frame_tabla = Frame(frame_contenido, bg="#272643")
        frame_tabla.pack(pady=10, fill="both", expand=True)

        tabla_logs = ttk.Treeview(frame_tabla, columns=("ID", "Usuario", "Fecha y Hora", "Acción"), show="headings", height=15)
        tabla_logs.heading("ID", text="ID")
        tabla_logs.heading("Usuario", text="Usuario")
        tabla_logs.heading("Fecha y Hora", text="Fecha y Hora")
        tabla_logs.heading("Acción", text="Acción")

        tabla_logs.column("ID", width=50, anchor="center")
        tabla_logs.column("Usuario", width=150, anchor="center")
        tabla_logs.column("Fecha y Hora", width=150, anchor="center")
        tabla_logs.column("Acción", width=300, anchor="w")
        tabla_logs.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(frame_tabla, orient="vertical", command=tabla_logs.yview)
        scrollbar.pack(side="right", fill="y")
        tabla_logs.configure(yscrollcommand=scrollbar.set)

        # Barra de búsqueda
        frame_busqueda = Frame(frame_contenido, bg="#272643")
        frame_busqueda.pack(pady=10)

        Label(frame_busqueda, text="Buscar:", font=("Segoe UI", 12), bg="#272643", fg="white").grid(row=0, column=0, padx=5)
        entrada_busqueda = Entry(frame_busqueda, width=30)
        entrada_busqueda.grid(row=0, column=1, padx=5)
        Button(frame_busqueda, text="Buscar", bg="#bae8e8", font=("Segoe UI", 12),
            command=lambda: filtrar_logs(entrada_busqueda.get(), tabla_logs)).grid(row=0, column=2, padx=5)

        # Botones de exportación
        frame_botones = Frame(frame_contenido, bg="#272643")
        frame_botones.pack(pady=10)

        Button(frame_botones, text="Exportar Logs", bg="#bae8e8", font=("Segoe UI", 12),
            command=lambda: exportar_logs(tabla_logs)).grid(row=0, column=0, padx=10)

        cargar_logs(tabla_logs)

    def cargar_logs(tabla):
        conn = conexion_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM logs")
            registros = cursor.fetchall()
            for registro in tabla.get_children():
                tabla.delete(registro)
            for registro in registros:
                tabla.insert("", "end", values=registro)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar logs: {e}")
        finally:
            conn.close()

    def filtrar_logs(termino, tabla):
        conn = conexion_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            consulta = "SELECT * FROM logs WHERE usuario LIKE ? OR fecha_hora LIKE ? OR accion LIKE ?"
            cursor.execute(consulta, (f"%{termino}%", f"%{termino}%", f"%{termino}%"))
            registros = cursor.fetchall()
            for registro in tabla.get_children():
                tabla.delete(registro)
            for registro in registros:
                tabla.insert("", "end", values=registro)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al filtrar logs: {e}")
        finally:
            conn.close()
        
    def consultar_busqueda_editar(termino, tabla):
        conn = conexion_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            consulta = """
            SELECT cedula, apellidos, nombres, telefono, correo, rol, fecha_nacimiento
            FROM usuarios
            WHERE cedula LIKE ? OR apellidos LIKE ? OR nombres LIKE ? OR telefono LIKE ? OR correo LIKE ? OR rol LIKE ?
            """
            cursor.execute(consulta, (f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%"))
            registros = cursor.fetchall()
            
            # Limpiar la tabla antes de insertar los nuevos resultados
            for registro in tabla.get_children():
                tabla.delete(registro)

            # Asegúrate de insertar los registros en el orden correcto
            for registro in registros:
                tabla.insert("", "end", values=registro)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al encontrar al usuario: {e}")
        finally:
            conn.close()

    def consultar_busqueda(termino, tabla):
        conn = conexion_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            consulta = """
            SELECT cedula, apellidos, nombres, telefono, correo, rol, estado, fecha_nacimiento, membresia_id, fecha_registro
            FROM usuarios
            WHERE cedula LIKE ? OR apellidos LIKE ? OR nombres LIKE ? OR telefono LIKE ? OR correo LIKE ? OR rol LIKE ?
            """
            cursor.execute(consulta, (f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%"))
            registros = cursor.fetchall()
            
            # Limpiar la tabla antes de insertar los nuevos resultados
            for registro in tabla.get_children():
                tabla.delete(registro)

            # Asegúrate de insertar los registros en el orden correcto
            for registro in registros:
                tabla.insert("", "end", values=registro)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al encontrar al usuario: {e}")
        finally:
            conn.close()

    def exportar_logs(tabla):
        # Obtener los registros de la tabla
        registros = [tabla.item(fila)["values"] for fila in tabla.get_children()]

        if not registros:
            messagebox.showwarning("Sin datos", "No hay datos para exportar.")
            return

        # Seleccionar la carpeta donde guardar el archivo y permitir elegir nombre
        ruta = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])

        if not ruta:
            messagebox.showwarning("No se seleccionó archivo", "No se ha seleccionado un archivo para guardar.")
            return

        try:
            # Crear el PDF
            c = canvas.Canvas(ruta, pagesize=letter)
            width, height = letter

            c.setFont("Helvetica-Bold", 14)
            c.drawString(200, height - 50, "Reporte de Logs")

            y_position = height - 80  # Posición inicial en Y

            # Escribir encabezado de la tabla
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y_position, "ID")
            c.drawString(100, y_position, "Usuario")
            c.drawString(250, y_position, "Fecha y Hora")
            c.drawString(400, y_position, "Acción")

            y_position -= 20
            c.setFont("Helvetica", 10)

            # Escribir los registros
            for registro in registros:
                if y_position < 50:  # Salto de página si se acaba el espacio
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y_position = height - 50

                c.drawString(50, y_position, str(registro[0]))  # ID
                c.drawString(100, y_position, str(registro[1]))  # Usuario
                c.drawString(250, y_position, str(registro[2]))  # Fecha y Hora
                c.drawString(400, y_position, str(registro[3]))  # Acción
                
                y_position -= 20

            c.save()

            conn = conexion_db()
            cursor = conn.cursor()
            fecha_hora_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            cursor.execute("INSERT INTO logs (usuario, fecha_hora, accion) VALUES (?, ?, 'Exportación PDF Logs')", ("admin", fecha_hora_actual))
            conn.commit()
            conn.close()

            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", f"Logs exportados correctamente a: {ruta}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar los logs: {e}")

    def cargar_datos_edicion(tabla, filtro=""):
        conn = conexion_db()  # Cambio aquí
        if not conn:
            return

        cursor = conn.cursor()
        query = "SELECT cedula, apellidos, nombres, telefono, correo, rol, fecha_nacimiento FROM usuarios WHERE estado = 'A' AND rol != 'Administrador'"

        if filtro:
            query += " AND (cedula LIKE ? OR apellidos LIKE ? OR nombres LIKE ? OR telefono LIKE ? OR correo LIKE ? OR rol LIKE?)"
            cursor.execute(query, (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute(query)

        datos = cursor.fetchall()
        conn.close()

        # Limpiar tabla
        for item in tabla.get_children():
            tabla.delete(item)

        # Insertar datos
        for fila in datos:
            # Reemplazar NULL o vacío por 'None' en cada columna
            fila_con_none = tuple(
                "None" if campo is None or campo == "" else campo for campo in fila
            )
            # Insertar fila en la tabla, asegurando que todos los datos (incluyendo fecha_registro) se muestren
            tabla.insert("", "end", values=fila_con_none)

    def cargar_datos(tabla, filtro=""):
        conn = conexion_db()  # Cambio aquí
        if not conn:
            return

        cursor = conn.cursor()
        query = "SELECT cedula, apellidos, nombres, telefono, correo, rol, estado, fecha_nacimiento, membresia_id, fecha_registro FROM usuarios WHERE estado = 'A'"

        if filtro:
            query += " AND (cedula LIKE ? OR apellidos LIKE ? OR nombres LIKE ? OR telefono LIKE ? OR correo LIKE ? OR rol LIKE ? OR membresia_id LIKE ?)"
            cursor.execute(query, (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute(query)

        datos = cursor.fetchall()
        conn.close()

        # Limpiar tabla
        for item in tabla.get_children():
            tabla.delete(item)

        # Insertar datos
        for fila in datos:
            # Reemplazar NULL o vacío por 'None' en cada columna
            fila_con_none = tuple(
                "None" if campo is None or campo == "" else campo for campo in fila
            )
            # Insertar fila en la tabla, asegurando que todos los datos (incluyendo fecha_registro) se muestren
            tabla.insert("", "end", values=fila_con_none)

    def limpiar_contenido():
        for widget in frame_contenido.winfo_children():
            widget.destroy()
    
    # Botones de navegación
    Button(frame_botones_principales, text="Administración de Usuarios", font=("Segoe UI", 14), bg="#bae8e8", command=cargar_administracion_usuarios).pack(side="left", padx=10)
    Button(frame_botones_principales, text="Administración de Parámetros", font=("Segoe UI", 14), bg="#bae8e8", command=cargar_administracion_parametros).pack(side="left", padx=10)
    Button(frame_botones_principales, text="Regresar", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: regresar(callback, ventana)).pack(side="right", padx=10)   

    ventana.bind_all("<KeyPress>", verificar_secuencia)
    ventana.mainloop()

def regresar(callback, ventana):
    ventana.destroy()
    callback()