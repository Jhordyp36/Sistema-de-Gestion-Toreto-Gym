import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from tkinter import PhotoImage
from tkinter import Label, Button, Frame, Entry, Scrollbar, StringVar, Tk, ttk
from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono, verifica_identificacion, verifica_nombres_apellidos

def conexion_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def ventana_gestion_equipos(callback):
    ventana = Tk()
    ventana.title("Gestión de Equipos")
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
    
    def cargar_equipos_registrados():
        limpiar_contenido()
        
        Label(frame_contenido, text="Equipos Registrados", font=("Segoe UI", 16), bg="#272643", fg="white").pack(pady=10)
        
        # Crear frame para la barra de búsqueda
        frame_busqueda = tk.Frame(frame_contenido, bg="#272643")
        frame_busqueda.pack(pady=5, padx=10)

        label_buscar = tk.Label(frame_busqueda, text="Buscar:", font=("Segoe UI", 12), bg="#272643", fg="#ffffff")
        label_buscar.pack(side="left", padx=5)

        entry_buscar = tk.Entry(frame_busqueda, font=("Segoe UI", 12), width=30)
        entry_buscar.pack(side="left", padx=5)
        
        btn_buscar = tk.Button(frame_busqueda, text="Buscar", font=("Segoe UI", 12), bg="#bae8e8", command=lambda: consultar_busqueda(entry_buscar.get(), tabla_equipos))
        btn_buscar.pack(side="left", padx=5)

        # Tabla de resultados
        columns_equipos = ("Nombre", "Categoría", "Estado")
        tabla_equipos = ttk.Treeview(frame_contenido, columns=columns_equipos, show="headings", height=15)
        for col in columns_equipos:
            tabla_equipos.heading(col, text=col)
            tabla_equipos.column(col, anchor="center", width=150)

        tabla_equipos.pack(padx=10, pady=10)

        # Botones de acción
        frame_botones = tk.Frame(frame_contenido, bg="#272643")
        frame_botones.pack(pady=10)

        btn_registrar_equipo = tk.Button(frame_botones, text="Registrar Equipo", font=("Segoe UI", 12), bg="#bae8e8", command=registrar_equipo)
        btn_registrar_equipo.pack(side="left", padx=10)

        btn_actualizar_estado = tk.Button(frame_botones, text="Actualizar Estado", font=("Segoe UI", 12), bg="#bae8e8", command=lambda: actualizar_estado(tabla_equipos))
        btn_actualizar_estado.pack(side="left", padx=10)

        cargar_datos_equipos(tabla_equipos)

    def registrar_equipo():
        limpiar_contenido()
        
        # Crear el marco para el formulario
        frame_formulario = tk.Frame(frame_contenido, bg="#bae8e8", width=400, height=400)
        frame_formulario.pack(pady=50, padx=50)
        frame_formulario.pack_propagate(False)

        # Título del formulario
        tk.Label(frame_formulario, text="Registrar Equipo", font=("Segoe UI", 18), bg="#bae8e8", fg="#000000").pack(pady=20)
        
        # Campos de entrada
        tk.Label(frame_formulario, text="Nombre del Equipo:", font=("Segoe UI", 12), bg="#bae8e8", fg="#000000").pack(pady=10)
        entry_nombre_equipo = tk.Entry(frame_formulario, font=("Segoe UI", 12))
        entry_nombre_equipo.pack(pady=10)

        tk.Label(frame_formulario, text="Categoría del Equipo:", font=("Segoe UI", 12), bg="#bae8e8", fg="#000000").pack(pady=10)
        
        # Obtener categorías de la base de datos
        conn = conexion_db()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM categorias_equipos")
        categorias = [fila[0] for fila in cursor.fetchall()]
        conn.close()

        categoria_var = StringVar()
        categoria_dropdown = ttk.Combobox(frame_formulario, textvariable=categoria_var, values=categorias, font=("Segoe UI", 12), width=18)
        categoria_dropdown.pack(pady=10)
        

        def guardar_equipo():
            # Obtener los valores del formulario
            nombre_equipo = entry_nombre_equipo.get().strip()
            categoria_equipo = categoria_var.get()

            # Verificar que los campos estén llenos
            if not nombre_equipo or not categoria_equipo:
                messagebox.showerror("Error", "Por favor, complete todos los campos.")
                return

            # Validaciones
            #Validación de longitud
            if not nombre_equipo or len(nombre_equipo) > 100:
                messagebox.showerror("Error", "El nombre del equipo debe ser una cadena de hasta 100 caracteres.")
                return
            
            # Validar que el nombre del equipo solo contenga letras
            if not nombre_equipo.replace(" ", "").isalpha():
                messagebox.showerror("Error", "El nombre del equipo solo puede contener letras y espacios.")
                return

            # Validación de campo vació de categoría
            if not categoria_equipo:
                messagebox.showerror("Error", "La categoría del equipo es obligatoria.")
                return
            
            # Verificar si el equipo ya está registrado
            conn = conexion_db()
            if not conn:
                return

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) > 0 AS existe FROM equipos WHERE nombre = ?", (nombre_equipo,))
            existe = cursor.fetchone()[0]
            conn.close()

            if existe:
                messagebox.showerror("Error", "El equipo ya está registrado.")
                return
            
            try:
                conn = conexion_db()
                cursor = conn.cursor()

                # Guardar en la base de datos
                cursor.execute('''
                    INSERT INTO equipos (nombre, categoria_id, estado)
                    VALUES (?, (SELECT id FROM categorias_equipos WHERE nombre = ?), 'Libre para uso')
                ''', (nombre_equipo, categoria_equipo))

                conn.commit()
                messagebox.showinfo("Éxito", "Equipo registrado correctamente.")
                cargar_equipos_registrados()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo registrar el equipo: {e}")
            finally:
                conn.close()

        # Crear un frame para los botones
        frame_botones = tk.Frame(frame_formulario, bg="#bae8e8")
        frame_botones.pack(pady=20)

        # Botones de guardar y cancelar
        tk.Button(frame_botones, text="Guardar", font=("Segoe UI", 12), command=guardar_equipo).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Cancelar", font=("Segoe UI", 12), command=cargar_equipos_registrados).pack(side="left", padx=10)

    def actualizar_estado(tabla_equipos):
        seleccion = tabla_equipos.selection()
        if not seleccion:
            messagebox.showerror("Error", "Por favor, seleccione un equipo para actualizar su estado.")
            return

        # Obtener el nombre del equipo seleccionado
        equipo_nombre = tabla_equipos.item(seleccion, "values")[0]

        # Obtener el ID del equipo seleccionado
        conn = conexion_db()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute("SELECT id FROM equipos WHERE nombre = ?", (equipo_nombre,))
        equipo_id = cursor.fetchone()[0]
        conn.close()

        def confirmar_actualizacion(estado_nuevo):
            conn = conexion_db()
            if not conn:
                return

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT estado FROM equipos WHERE id = ?", (equipo_id,))
                estado_actual = cursor.fetchone()[0]

                # Validaciones
                # Verificar que el estado a cambiar sea diferente
                if estado_nuevo == estado_actual:
                    messagebox.showerror("Error", "El equipo ya se encuentra en ese estado.")
                    return
                
                # Verificar si el equipo está en uso
                if estado_actual == 'En uso':             
                    cursor.execute("SELECT COUNT(*) > 0 AS en_uso FROM historial_uso_equipos WHERE equipo_id = ? AND fecha_fin_uso IS NULL", (equipo_id,))
                    en_uso = cursor.fetchone()[0]

                    if en_uso:
                        messagebox.showerror("Error", "Equipo en uso, no es posible cambiar su estado.")
                        return

                cursor.execute("UPDATE equipos SET estado = ? WHERE id = ?", (estado_nuevo, equipo_id))
                conn.commit()
                messagebox.showinfo("Éxito", "Estado del equipo actualizado correctamente.")
                cargar_equipos_registrados()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el estado del equipo: {e}")
            finally:
                conn.close()

        ventana_actualizar = Tk()
        ventana_actualizar.title("Actualizar Estado")
        ventana_actualizar.configure(bg="#272643")

        tk.Label(ventana_actualizar, text="¿Está seguro de actualizar el estado del equipo?", font=("Segoe UI", 12), bg="#272643", fg="#ffffff").pack(pady=10)

        estado_var = StringVar()
        estado_dropdown = ttk.Combobox(ventana_actualizar, textvariable=estado_var, values=('Libre para uso', 'En uso', 'Inactivo'), font=("Segoe UI", 12), width=14)
        estado_dropdown.pack(pady=10)

        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("SELECT estado FROM equipos WHERE id = ?", (equipo_id,))
        estado_actual = cursor.fetchone()[0]
        conn.close()

        estado_dropdown.set(estado_actual)

        def mostrar_confirmacion():
            ventana_confirmacion = Tk()
            ventana_confirmacion.title("Confirmar Actualización")
            ventana_confirmacion.configure(bg="#272643")

            tk.Label(ventana_confirmacion, text="¿Está seguro de realizar los cambios?", font=("Segoe UI", 12), bg="#272643", fg="#ffffff").pack(pady=10)

            def confirmar():
                confirmar_actualizacion(estado_dropdown.get())
                ventana_confirmacion.destroy()
                ventana_actualizar.destroy()

        # Frame para agrupar los botones
            frame_botones = tk.Frame(ventana_confirmacion, bg="#272643")
            frame_botones.pack(pady=10)

        # Botones dentro del frame
            tk.Button(frame_botones, text="Sí", font=("Segoe UI", 12), bg="#bae8e8", width=10, command=confirmar).pack(side=tk.LEFT, padx=10)
            tk.Button(frame_botones, text="No", font=("Segoe UI", 12), bg="#bae8e8", width=10, command=ventana_confirmacion.destroy).pack(side=tk.LEFT, padx=10)

        # Frame para agrupar los botones en la ventana principal
        frame_botones_principal = tk.Frame(ventana_actualizar, bg="#272643")
        frame_botones_principal.pack(pady=10)

        # Botones dentro del frame
        tk.Button(frame_botones_principal, text="Actualizar", font=("Segoe UI", 12), bg="#bae8e8", command=mostrar_confirmacion).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_botones_principal, text="Cancelar", font=("Segoe UI", 12), bg="#bae8e8", command=ventana_actualizar.destroy).pack(side=tk.LEFT, padx=10)
    
    def cargar_datos_equipos(tabla):
        conn = conexion_db()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute("SELECT e.nombre, ce.nombre, e.estado FROM equipos e JOIN categorias_equipos ce ON e.categoria_id = ce.id")
        datos = cursor.fetchall()
        conn.close()

        for item in tabla.get_children():
            tabla.delete(item)

        for fila in datos:
            tabla.insert("", "end", values=fila)

    def consultar_busqueda(termino, tabla):
        
        if not termino.strip():
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda.")
            return
        
        conn = conexion_db()
        if not conn:
            return

        cursor = conn.cursor()
        consulta = "SELECT e.nombre, ce.nombre, e.estado FROM equipos e JOIN categorias_equipos ce ON e.categoria_id = ce.id WHERE e.nombre LIKE ? OR ce.nombre LIKE ? OR e.estado LIKE ?"
        cursor.execute(consulta, (f"%{termino}%", f"%{termino}%", f"%{termino}%"))
        registros = cursor.fetchall()
        conn.close()

        for item in tabla.get_children():
            tabla.delete(item)
            
        if not registros:
            messagebox.showerror("Error", "No se encontraron resultados")

        for registro in registros:
            tabla.insert("", "end", values=registro)
            

    def cargar_historial_uso_equipos():
        limpiar_contenido()

        Label(frame_contenido, text="Historial de Uso de Equipos", font=("Segoe UI", 16), bg="#272643", fg="white").pack(pady=10)

        # Crear frame para la barra de búsqueda
        frame_busqueda = tk.Frame(frame_contenido, bg="#272643")
        frame_busqueda.pack(pady=5, padx=10)

        label_buscar = tk.Label(frame_busqueda, text="Buscar:", font=("Segoe UI", 12), bg="#272643", fg="#ffffff")
        label_buscar.pack(side="left", padx=5)

        entry_buscar = tk.Entry(frame_busqueda, font=("Segoe UI", 12), width=30)
        entry_buscar.pack(side="left", padx=5)

        btn_buscar = tk.Button(frame_busqueda, text="Buscar", font=("Segoe UI", 12), bg="#bae8e8", command=lambda: consultar_busqueda_historial(entry_buscar.get(), tabla_historial))
        btn_buscar.pack(side="left", padx=5)

        # Tabla de resultados
        columns_historial = ("ID", "C.I. Cliente", "Nombre Equipo", "Fecha Inicio Uso", "Fecha Fin Uso")
        tabla_historial = ttk.Treeview(frame_contenido, columns=columns_historial, show="headings", height=15)
        for col in columns_historial:
            tabla_historial.heading(col, text=col)
            tabla_historial.column(col, anchor="center", width=150)

        tabla_historial.pack(padx=10, pady=10)

        # Botones de acción
        frame_botones = tk.Frame(frame_contenido, bg="#272643")
        frame_botones.pack(pady=10)


        def registrar_uso():
            limpiar_contenido()
            
            # Crear el marco para el formulario
            frame_formulario = tk.Frame(frame_contenido, bg="#bae8e8", width=400, height=400)
            frame_formulario.pack(pady=50, padx=50)
            frame_formulario.pack_propagate(False)

            # Título del formulario
            tk.Label(frame_formulario, text="Registrar Uso", font=("Segoe UI", 18), bg="#bae8e8", fg="#000000").pack(pady=20)

            # Campos de entrada
            tk.Label(frame_formulario, text="C.I. Cliente:", font=("Segoe UI", 12), bg="#bae8e8", fg="#000000").pack(pady=10)
            entry_ci_cliente = tk.Entry(frame_formulario, font=("Segoe UI", 12))
            entry_ci_cliente.pack(pady=10)

            # Obtener nombres de equipos de la base de datos
            tk.Label(frame_formulario, text="Nombre Equipo:", font=("Segoe UI", 12), bg="#bae8e8", fg="#000000").pack(pady=10)
            conn = conexion_db()
            if not conn:
                return

            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM equipos")
            nombres_equipos = [fila[0] for fila in cursor.fetchall()]
            conn.close()

            equipo_var = StringVar()
            equipo_dropdown = ttk.Combobox(frame_formulario, textvariable=equipo_var, values=nombres_equipos, font=("Segoe UI", 12), width=18)
            equipo_dropdown.pack(pady=10)


            def guardar_uso():
                ci_cliente = entry_ci_cliente.get().strip()
                nombre_equipo = equipo_var.get()

                if not ci_cliente or not nombre_equipo:
                    messagebox.showerror("Error", "Por favor, complete todos los campos.")
                    return
                
                # Validar que la cédula solo contenga números
                if not ci_cliente.isdigit():
                    messagebox.showerror("Error", "La cédula solo puede contener números.")
                    return

                conn = conexion_db()
                if not conn:
                    return

                # Validar que el nombre del equipo solo contenga letras
                if not nombre_equipo.replace(" ", "").isalpha():
                    messagebox.showerror("Error", "El nombre del equipo solo puede contener letras y espacios.")
                    return

                try:
                    cursor = conn.cursor()
                    
                    # Verificar si el cliente existe
                    cursor.execute("SELECT * FROM usuarios WHERE cedula = ?", (ci_cliente,))
                    cliente = cursor.fetchone()

                    if not cliente:
                        messagebox.showerror("Error", "El cliente no existe en el sistema.")
                        return

                    # Verificar si el cliente tiene membresía activa
                    cursor.execute("SELECT membresia_id FROM usuarios WHERE cedula = ?", (ci_cliente,))
                    membresia_id = cursor.fetchone()

                    if membresia_id is None or membresia_id[0] is None:
                        messagebox.showerror("Error", "El cliente no tiene membresía.")
                        return

                    cursor.execute("SELECT estado FROM membresias WHERE id = ?", (membresia_id[0],))
                    membresia_estado = cursor.fetchone()[0]

                    if membresia_estado != 'Activo':
                        messagebox.showerror("Error", "Membresía no activa.")
                        return
                    
                    # Verificar si el equipo existe en el sistema
                    cursor.execute("SELECT id FROM equipos WHERE nombre = ?", (nombre_equipo,))
                    equipo_id = cursor.fetchone()

                    if not equipo_id:
                        messagebox.showerror("Error", "El equipo no existe en el sistema.")
                        return

                    # Verificar si el cliente tiene acceso al equipo
                    cursor.execute('''
                        SELECT COUNT(*) > 0 AS tiene_acceso
                        FROM usuarios u
                        JOIN membresias m ON u.membresia_id = m.id
                        JOIN membresias_servicios ms ON m.id = ms.membresia_id
                        JOIN servicios s ON ms.servicio_id = s.id
                        JOIN equipos e ON s.equipo_id = e.id
                        WHERE u.cedula = ? AND e.nombre = ?
                    ''', (ci_cliente, nombre_equipo))

                    tiene_acceso = cursor.fetchone()[0]

                    if not tiene_acceso:
                        messagebox.showerror("Error", "El cliente no tiene acceso a este equipo.")
                        return
                    
                    # Verificar si el cliente ya tiene un uso de máquina en curso
                    cursor.execute("SELECT COUNT(*) > 0 AS tiene_uso_en_curso FROM historial_uso_equipos WHERE cedula = ? AND fecha_fin_uso IS NULL", (ci_cliente,))
                    tiene_uso_en_curso = cursor.fetchone()[0]

                    if tiene_uso_en_curso:
                        messagebox.showerror("Error", "El cliente ya tiene un uso de máquina en curso. Debe finalizar el uso actual antes de iniciar otro.")
                        return

                    # Verificar el estado del equipo
                    cursor.execute("SELECT estado FROM equipos WHERE id = ?", (equipo_id[0],))
                    estado_equipo = cursor.fetchone()[0]

                    if estado_equipo == 'Inactivo':
                        messagebox.showerror("Error", "El equipo está inactivo.")
                        return

                    if estado_equipo == 'En uso':
                        messagebox.showerror("Error", "El equipo no está libre para uso.")
                        return

                    # Registrar el uso del equipo
                    cursor.execute("INSERT INTO historial_uso_equipos (cedula, equipo_id, fecha_inicio_uso) VALUES (?, ?, strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))", (ci_cliente, equipo_id[0]))
                    conn.commit()

                    # Actualizar el estado del equipo a 'En Uso'
                    cursor.execute("UPDATE equipos SET estado = 'En uso' WHERE id = ?", (equipo_id[0],))
                    conn.commit()

                    messagebox.showinfo("Éxito", "Uso del equipo registrado correctamente.")
                    cargar_historial_uso_equipos()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo registrar el uso del equipo: {e}")
                finally:
                    conn.close()

            # Crear un frame para los botones
            frame_botones = tk.Frame(frame_formulario, bg="#bae8e8")
            frame_botones.pack(pady=20)

            # Botones de guardar y cancelar
            tk.Button(frame_botones, text="Guardar", font=("Segoe UI", 12), command=guardar_uso).pack(side="left", padx=10)
            tk.Button(frame_botones, text="Cancelar", font=("Segoe UI", 12), command=cargar_historial_uso_equipos).pack(side="left", padx=10)
            

        btn_registrar_uso = tk.Button(frame_botones, text="Registrar Uso", font=("Segoe UI", 12), bg="#bae8e8", command=registrar_uso)
        btn_registrar_uso.pack(side="left", padx=10)

        def registrar_fin_uso():
            seleccion = tabla_historial.selection()
            if not seleccion:
                messagebox.showerror("Error", "Por favor, seleccione un registro para registrar el fin del uso.")
                return

            conn = conexion_db()
            if not conn:
                return

            cursor = conn.cursor()
            cursor.execute("SELECT fecha_fin_uso FROM historial_uso_equipos WHERE id = ?", (tabla_historial.item(seleccion, "values")[0],))
            fecha_fin_uso = cursor.fetchone()[0]

            if fecha_fin_uso is not None:
                messagebox.showerror("Error", "La fecha fin de uso ya ha sido registrada para este equipo.")
                return

            def confirmar_fin_uso():
                conn = conexion_db()
                if not conn:
                    return

                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE historial_uso_equipos SET fecha_fin_uso = strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime') WHERE id = ?", (tabla_historial.item(seleccion, "values")[0],))
                    conn.commit()

                    # Obtener el ID del equipo
                    cursor.execute("SELECT equipo_id FROM historial_uso_equipos WHERE id = ?", (tabla_historial.item(seleccion, "values")[0],))
                    equipo_id = cursor.fetchone()[0]

                    # Actualizar el estado del equipo a 'Libre para uso'
                    cursor.execute("UPDATE equipos SET estado = 'Libre para uso' WHERE id = ?", (equipo_id,))
                    conn.commit()

                    messagebox.showinfo("Éxito", "Fin del uso registrado correctamente.")
                    cargar_historial_uso_equipos()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo registrar el fin del uso: {e}")
                finally:
                    conn.close()

            ventana_confirmacion = Tk()
            ventana_confirmacion.title("Confirmar Fin del Uso")
            ventana_confirmacion.configure(bg="#272643")

            frame_contenido = Frame(ventana_confirmacion, bg="#272643")
            frame_contenido.pack(pady=20, padx=20)

            tk.Label(frame_contenido, text="¿Está seguro de registrar el fin del uso?", font=("Segoe UI", 12), bg="#272643", fg="#ffffff").pack(pady=10)

            frame_botones = Frame(frame_contenido, bg="#272643")
            frame_botones.pack(pady=10)

            tk.Button(frame_botones, text="Confirmar", font=("Segoe UI", 12), bg="#bae8e8", command=lambda: [confirmar_fin_uso(), ventana_confirmacion.destroy()]).pack(side=tk.LEFT, padx=10)
            tk.Button(frame_botones, text="Cancelar", font=("Segoe UI", 12), bg="#bae8e8", command=ventana_confirmacion.destroy).pack(side=tk.LEFT, padx=10)

        btn_registrar_fin_uso = tk.Button(frame_botones, text="Registrar Fin de Uso", font=("Segoe UI", 12), bg="#bae8e8", command=registrar_fin_uso)
        btn_registrar_fin_uso.pack(side="left", padx=10)

        cargar_datos_historial(tabla_historial)

        
    def cargar_datos_historial(tabla):
        conn = conexion_db()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute('''
            SELECT hue.id, u.cedula, e.nombre, hue.fecha_inicio_uso, hue.fecha_fin_uso
            FROM historial_uso_equipos hue
            JOIN usuarios u ON hue.cedula = u.cedula
            JOIN equipos e ON hue.equipo_id = e.id
        ''')
        datos = cursor.fetchall()
        conn.close()

        for item in tabla.get_children():
            tabla.delete(item)

        for fila in datos:
            tabla.insert("", "end", values=fila)

    def consultar_busqueda_historial(termino, tabla):
        
        if not termino.strip():
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda.")
            return
        
        conn = conexion_db()
        if not conn:
            return

        cursor = conn.cursor()
        consulta = '''
            SELECT hue.id, u.cedula, e.nombre, hue.fecha_inicio_uso, hue.fecha_fin_uso
            FROM historial_uso_equipos hue
            JOIN usuarios u ON hue.cedula = u.cedula
            JOIN equipos e ON hue.equipo_id = e.id
            WHERE u.cedula LIKE ? OR e.nombre LIKE ? OR hue.fecha_inicio_uso LIKE ? OR hue.fecha_fin_uso LIKE ?
        '''
        cursor.execute(consulta, (f"%{termino}%", f"%{termino}%", f"%{termino}%", f"%{termino}%"))
        registros = cursor.fetchall()
        conn.close()

        for item in tabla.get_children():
            tabla.delete(item)

        if not registros:
            messagebox.showerror("Error", "No se encontraron resultados")
            
        for registro in registros:
            tabla.insert("", "end", values=registro)

    def limpiar_contenido():
        for widget in frame_contenido.winfo_children():
            widget.destroy()
    
    # Botones de navegación
    Button(frame_botones_principales, text="Equipos Registrados", font=("Segoe UI", 14), bg="#bae8e8", command=cargar_equipos_registrados).pack(side="left", padx=10)
    Button(frame_botones_principales, text="Historial de Uso de Equipos", font=("Segoe UI", 14), bg="#bae8e8", command=cargar_historial_uso_equipos).pack(side="left", padx=10)
    Button(frame_botones_principales, text="Regresar", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: regresar(callback, ventana)).pack(side="right", padx=10)   

    ventana.mainloop()

def regresar(callback, ventana):
    ventana.destroy()
    callback()