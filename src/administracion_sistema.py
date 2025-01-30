import calendar
from datetime import datetime
import os
import sqlite3
import tkinter as tk
from tkinter import CENTER, LEFT, RIGHT, Canvas, Listbox, filedialog
from tkinter.ttk import Combobox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import Button, Frame, Label, Entry, Scrollbar, StringVar, Tk, ttk, messagebox
from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono, verifica_correo, verifica_fecha_nacimiento, verifica_identificacion, verifica_nombres_apellidos, verifica_telefono

def conexion_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None    

def ventana_administracion():
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
        Button(frame_tabla, text="Buscar", command=lambda: print("hola")).grid(row=0, column=2, padx=10, pady=5)

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

        # Actualizar los días al seleccionar mes y año
        entry_mes.bind("<<ComboboxSelected>>", lambda event: actualizar_dias())
        entry_ano.bind("<<ComboboxSelected>>", lambda event: actualizar_dias())

        # Función para guardar cliente
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
        # Botón de guardar
        tk.Button(frame_formulario, text="Guardar", font=("Segoe UI", 12), command=guardar_cliente).grid(row=10, column=0, padx=10, pady=10, sticky="e")
        tk.Button(frame_formulario, text="Cancelar", font=("Segoe UI", 12), command=cargar_administracion_usuarios).grid(row=10, column=1, padx=10, pady=10, sticky="e")

    def editar_informacion():
        limpiar_contenido()
        print("HOla")

    def eliminar_usuario(tabla):
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selección", "Por favor, seleccione un usuario para eliminar.")
            return

        usuario_id = tabla.item(seleccion[0])["values"][0]  # Cedula correctamente obtenida
        print(f"usuario_id: '{usuario_id}'")  # Imprime el valor con comillas para ver si hay espacios

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
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
            cargar_administracion_usuarios()  # Recargar la tabla después de la eliminación
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al eliminar el usuario: {e}")
        finally:
            conn.close()

    # Función para cargar las membresías
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

    # Función para cargar los servicios de la membresía seleccionada
    def mostrar_servicios(tabla_servicios, membresia_id):
        # Limpiar la tabla de servicios antes de cargar nuevos datos
        for row in tabla_servicios.get_children():
            tabla_servicios.delete(row)

        # Conectar a la base de datos
        conn = conexion_db()
        cursor = conn.cursor()

        # Obtener los servicios relacionados con la membresía seleccionada
        cursor.execute('''
            SELECT s.nombre
            FROM servicios s
            JOIN membresias_servicios ms ON s.id = ms.servicio_id
            WHERE ms.membresia_id = ?
        ''', (membresia_id,))
        servicios = cursor.fetchall()

        # Insertar los servicios en el Treeview
        for servicio in servicios:
            tabla_servicios.insert("", "end", values=(servicio[0],))

        # Cerrar la conexión a la base de datos
        conn.close()

    def cargar_administracion_parametros():
        limpiar_contenido()



    def mostrar_edicion_membresia(tabla_membresias):
        limpiar_contenido()
        
        Label(frame_contenido, text="Editar Membresía", font=("Segoe UI", 16), bg="#272643", fg="white").pack(pady=10)
        
        frame_edicion = Frame(frame_contenido, bg="#272643")
        frame_edicion.pack(pady=10, fill="x")
        
        # Sección izquierda para edición de datos
        frame_izquierda = Frame(frame_edicion, bg="#272643")
        frame_izquierda.pack(side="left", padx=20)
        
        Label(frame_izquierda, text="Duración (días):", bg="#272643", fg="white").pack()
        entry_duracion = Entry(frame_izquierda)
        entry_duracion.pack(pady=5)
        
        Label(frame_izquierda, text="Estado:", bg="#272643", fg="white").pack()
        estado_var = StringVar()
        estado_dropdown = ttk.Combobox(frame_izquierda, textvariable=estado_var, values=["Activo", "Inactivo"])
        estado_dropdown.pack(pady=5)
        
        # Sección de selección de servicios
        Label(frame_izquierda, text="Seleccionar Servicios:", bg="#272643", fg="white").pack()
        frame_servicios = Frame(frame_izquierda, bg="#272643")
        frame_servicios.pack()
        
        lista_servicios = Listbox(frame_servicios, selectmode="multiple", height=5)
        lista_servicios.pack(side="left", padx=5)
        
        scrollbar_servicios = Scrollbar(frame_servicios, orient="vertical", command=lista_servicios.yview)
        scrollbar_servicios.pack(side="right", fill="y")
        lista_servicios.configure(yscrollcommand=scrollbar_servicios.set)
        
        Button(frame_izquierda, text="Agregar Servicio", command=lambda: agregar_servicio(lista_servicios, tabla_servicios)).pack(pady=5)
        
        # Tabla pequeña a la derecha para mostrar servicios seleccionados
        frame_derecha = Frame(frame_edicion, bg="#272643")
        frame_derecha.pack(side="right", padx=20)
        
        Label(frame_derecha, text="Servicios Seleccionados", bg="#272643", fg="white").pack()
        
        tabla_servicios = ttk.Treeview(frame_derecha, columns=("Servicio"), show="headings", height=5)
        tabla_servicios.heading("Servicio", text="Servicio")
        tabla_servicios.column("Servicio", width=200, anchor="center")
        tabla_servicios.pack()
        
        Button(frame_derecha, text="Eliminar Servicio", command=lambda: eliminar_servicio(tabla_servicios)).pack(pady=5)
        
        Button(frame_contenido, text="Guardar Cambios", bg="#bae8e8", font=("Segoe UI", 12),
            command=lambda: guardar_cambios_membresia(entry_duracion, estado_var, tabla_servicios)).pack(pady=10)
        
        cargar_servicios_disponibles(lista_servicios)

    def agregar_servicio(lista_servicios, tabla_servicios):
        for index in lista_servicios.curselection():
            servicio = lista_servicios.get(index)
            tabla_servicios.insert("", "end", values=(servicio,))

    def eliminar_servicio(tabla_servicios):
        selected_item = tabla_servicios.selection()
        if selected_item:
            tabla_servicios.delete(selected_item)

    def cargar_servicios_disponibles(lista_servicios):
        # Aquí se deben cargar los servicios disponibles desde la base de datos
        pass

    def guardar_cambios_membresia(entry_duracion, estado_var, tabla_servicios):
        # Aquí se guardarán los cambios en la base de datos
        pass

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

    def regresar():
        print("Hola")

    # Función: Cargar datos en la tabla
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
    Button(frame_botones_principales, text="Auditoría", font=("Segoe UI", 14), bg="#bae8e8", command=cargar_auditoria).pack(side="left", padx=10)
    Button(frame_botones_principales, text="Regresar", font=("Segoe UI", 14), bg="#bae8e8", command=regresar).pack(side="right", padx=10)   

    ventana.mainloop()