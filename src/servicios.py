import sys
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono

def conexion_db():
    """Establece la conexión con SQLite y configura WAL para acceso concurrente."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

class GestionServicios:
    """Clase para la gestión de servicios en la interfaz gráfica."""

    def __init__(self, root, callback_regreso=None):
        self.root = root
        self.root.title("Gestión de Servicios")
        self.root.state("zoomed")
        self.root.configure(bg="#272643")

        cargar_icono(self.root, ICONS_DIR)
        self.callback_regreso = callback_regreso

        # Variables para los campos del formulario
        self.var_id = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_disponibilidad = tk.StringVar()
        self.var_dia = tk.StringVar()
        self.var_hora = tk.StringVar()
        self.var_lugar = tk.StringVar()
        
        # Variables para Clases
        self.var_clase_id = tk.StringVar()
        self.var_clase_nombre = tk.StringVar()
        self.var_clase_descripcion = tk.StringVar()
        self.var_clase_duracion = tk.StringVar()

        # Variable para seleccionar el equipo
        self.var_equipo_id = tk.StringVar()

        self.configurar_interfaz()
        self.cargar_servicios()
        self.cargar_clases()
        self.cargar_datos_generales()
        
    def configurar_interfaz(self):
        """Configura la interfaz gráfica con header, footer, formularios y una tabla unificada con botones globales."""

        default_font = ("Segoe UI", 12)
        header_font = ("Segoe UI", 14, "bold")

        # --- HEADER ---
        header_frame = tk.Frame(self.root, bg="#2C3E50", pady=10)
        header_frame.pack(fill="x")

        tk.Label(
            header_frame, text="Bienvenido a la interfaz de servicios y clases",
            font=("Segoe UI", 18, "bold"), fg="white", bg="#2C3E50"
        ).pack()

        # Contenedor principal con dos columnas
        main_frame = tk.Frame(self.root, bg="#272643")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columnas_frame = tk.Frame(main_frame, bg="#272643")
        columnas_frame.pack(fill="x", expand=True)

        ## --- SECCIÓN SERVICIOS (Izquierda) --- ##
        servicios_frame = tk.LabelFrame(columnas_frame, text="Servicios", font=header_font, bg="#272643", fg="#bae8e8")
        servicios_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        form_servicios = tk.Frame(servicios_frame, bg="#272643")
        form_servicios.pack(fill="x", padx=10, pady=10)

        self.var_equipo = tk.StringVar()

        campos_servicios = [
            ("Nombre:", self.var_nombre),
            ("Descripción:", self.var_descripcion),
            ("Disponibilidad:", self.var_disponibilidad),
            ("Día:", self.var_dia),
            ("Hora:", self.var_hora),
            ("Lugar:", self.var_lugar),
            ("Equipo:", self.var_equipo)
        ]

        for i, (campo, var) in enumerate(campos_servicios):
            tk.Label(form_servicios, text=campo, bg="#272643", fg="#bae8e8", font=default_font).grid(row=i, column=0, sticky="w", padx=5, pady=5)

            if campo == "Disponibilidad:":
                combo = ttk.Combobox(form_servicios, textvariable=var, values=["Sí", "No"], state="readonly", width=27)
                combo.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            elif campo == "Equipo:":
                self.combo_equipos = ttk.Combobox(form_servicios, textvariable=self.var_equipo, state="readonly", width=27)
                self.combo_equipos.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.cargar_equipos()
            else:
                entry = tk.Entry(form_servicios, textvariable=var, width=30)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")

        ## --- SECCIÓN CLASES (Derecha) --- ##
        clases_frame = tk.LabelFrame(columnas_frame, text="Clases", font=header_font, bg="#272643", fg="#bae8e8")
        clases_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        form_clases = tk.Frame(clases_frame, bg="#272643")
        form_clases.pack(fill="x", padx=10, pady=10)

        tk.Label(form_clases, text="Nombre:", bg="#272643", fg="#bae8e8", font=default_font).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_clases = ttk.Combobox(form_clases, textvariable=self.var_clase_nombre, state="readonly", width=27)
        self.combo_clases.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_clases.bind("<<ComboboxSelected>>", self.autocompletar_clase_seleccionada)

        tk.Label(form_clases, text="Descripción:", bg="#272643", fg="#bae8e8", font=default_font).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_clase_descripcion = tk.Entry(form_clases, textvariable=self.var_clase_descripcion, width=30, state="readonly")
        self.entry_clase_descripcion.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(form_clases, text="Duración (min):", bg="#272643", fg="#bae8e8", font=default_font).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_clase_duracion = tk.Entry(form_clases, textvariable=self.var_clase_duracion, width=30)
        self.entry_clase_duracion.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Cargar las clases en el combobox
        self.cargar_clases_disponibles()

        # --- BOTONES UNIFICADOS --- #
        btn_frame = tk.Frame(main_frame, bg="#272643")
        btn_frame.pack(pady=10)

        botones = [
            ("Registrar", self.registrar),
            ("Editar", self.editar),
            ("Eliminar", self.borrar),
            ("Limpiar", self.limpiar_campos),
            ("Regresar", self.regresar)
        ]

        for texto, comando in botones:
            tk.Button(btn_frame, text=texto, font=default_font, command=comando, bg="#bae8e8").pack(side="left", padx=5)

        # --- TABLA GENERAL UNIFICADA --- #
        tabla_general_frame = tk.Frame(main_frame, bg="#272643")
        tabla_general_frame.pack(fill="both", expand=True, pady=10)

        scrollbar_y_general = ttk.Scrollbar(tabla_general_frame, orient="vertical")
        scrollbar_x_general = ttk.Scrollbar(tabla_general_frame, orient="horizontal")

        self.tree_general = ttk.Treeview(
            tabla_general_frame,
            columns=("ID", "Nombre Servicio", "Descripción Servicio", "Disponible", "Día", "Hora", "Lugar", "Equipo", "Nombre Clase", "Descripción Clase", "Duración"),
            show="headings",
            yscrollcommand=scrollbar_y_general.set,
            xscrollcommand=scrollbar_x_general.set
        )

        scrollbar_y_general.config(command=self.tree_general.yview)
        scrollbar_x_general.config(command=self.tree_general.xview)

        columnas = [
            "ID", "Nombre Servicio", "Descripción Servicio", "Disponible", "Día", "Hora", "Lugar", 
            "Equipo", "Nombre Clase", "Descripción Clase", "Duración"
        ]
        
        for col in columnas:
            self.tree_general.heading(col, text=col)
            self.tree_general.column(col, width=150, anchor="center")

        scrollbar_y_general.pack(side="right", fill="y")
        scrollbar_x_general.pack(side="bottom", fill="x")
        self.tree_general.pack(fill="both", expand=True)
        self.tree_general.bind("<<TreeviewSelect>>", self.autocompletar_campos)

        # --- FOOTER --- #
        footer_frame = tk.Frame(self.root, bg="#2C3E50", pady=10)
        footer_frame.pack(fill="x", side="bottom")

        tk.Label(
            footer_frame, text="Desarrollado por Toreto-Gym",
            font=("Segoe UI", 12), fg="white", bg="#2C3E50"
        ).pack()


    def cargar_servicios(self):
        """Carga los servicios desde la base de datos y los muestra en la tabla general unificada."""
        conn = conexion_db()
        if conn is None:
            return

        self.tree_general.delete(*self.tree_general.get_children())  # Limpiar tabla unificada

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.nombre, s.descripcion, s.disponible, s.dia, s.hora, s.lugar,
                    IFNULL(e.nombre, 'Sin equipo') AS equipo, 
                    IFNULL(c.nombre, 'Sin clase') AS clase, 
                    IFNULL(c.duracion_minutos, 'N/A') AS duracion
                FROM servicios s
                LEFT JOIN equipos e ON s.equipo_id = e.id
                LEFT JOIN clases c ON s.clase_id = c.id
            """)
            filas = cursor.fetchall()

            for fila in filas:
                self.tree_general.insert("", "end", values=fila)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar servicios: {e}")

        finally:
            conn.close()

    def registrar_servicio(self):
        """Registra un nuevo servicio en la base de datos, verificando si el nombre ya existe."""
        conn = conexion_db()
        if conn is None:
            return

        # Verificar si el nombre del servicio ya existe
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM servicios WHERE nombre = ?", (self.var_nombre.get(),))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Ya existe un servicio con este nombre. Use otro nombre.")
                return  # Evitar que se registre un duplicado

            # Obtener ID del equipo seleccionado
            equipo_nombre = self.combo_equipos.get()
            equipo_id = self.obtener_id_equipo_por_nombre(equipo_nombre) if equipo_nombre else None

            # Obtener ID de la clase seleccionada
            clase_nombre = self.var_clase_nombre.get()
            clase_id = self.obtener_id_clase_por_nombre(clase_nombre) if clase_nombre else None

            # Insertar en la base de datos
            cursor.execute("""
                INSERT INTO servicios (nombre, descripcion, disponible, dia, hora, lugar, equipo_id, clase_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.var_nombre.get(),
                self.var_descripcion.get(),
                self.var_disponibilidad.get(),
                self.var_dia.get(),
                self.var_hora.get(),
                self.var_lugar.get(),
                equipo_id,
                clase_id
            ))

            conn.commit()
            self.cargar_datos_generales()
            self.limpiar_campos()
            messagebox.showinfo("Éxito", "Servicio registrado correctamente")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar servicio: {e}")

        finally:
            conn.close()

    def editar_servicio(self):
        """Edita un servicio seleccionado en la tabla, incluyendo la actualización del equipo y la clase asociada."""
        seleccion = self.tree_general.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un servicio para editar")
            return

        servicio_id = self.tree_general.item(seleccion)['values'][0]

        equipo_nombre = self.combo_equipos.get()
        equipo_id = self.obtener_id_equipo_por_nombre(equipo_nombre) if equipo_nombre else None

        clase_nombre = self.var_clase_nombre.get()
        clase_id = self.obtener_id_clase_por_nombre(clase_nombre) if clase_nombre else None

        datos = (
            self.var_nombre.get(),
            self.var_descripcion.get(),
            self.var_disponibilidad.get(),
            self.var_dia.get(),
            self.var_hora.get(),
            self.var_lugar.get(),
            equipo_id,
            clase_id,
            servicio_id
        )

        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE servicios SET 
                nombre = ?, 
                descripcion = ?, 
                disponible = ?, 
                dia = ?, 
                hora = ?, 
                lugar = ?,
                equipo_id = ?,
                clase_id = ?
                WHERE id = ?
            """, datos)
            conn.commit()
            self.cargar_datos_generales()  # Actualizar tabla general
            messagebox.showinfo("Éxito", "Servicio actualizado correctamente")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar servicio: {e}")
        finally:
            conn.close()

    def cargar_datos_generales(self):
        """Carga los servicios y clases en la tabla general con nombres de columnas correctos."""
        conn = conexion_db()
        if conn is None:
            return

        self.tree_general.delete(*self.tree_general.get_children())  # Limpiar tabla

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, 
                    s.nombre AS nombre_servicio, 
                    s.descripcion AS descripcion_servicio, 
                    s.disponible, 
                    s.dia, 
                    s.hora, 
                    s.lugar,
                    IFNULL(e.nombre, 'Sin equipo') AS equipo, 
                    IFNULL(c.nombre, 'Sin clase') AS nombre_clase, 
                    IFNULL(c.descripcion, 'Sin descripción') AS descripcion_clase, 
                    IFNULL(c.duracion_minutos, 'N/A') AS duracion_clase
                FROM servicios s
                LEFT JOIN equipos e ON s.equipo_id = e.id
                LEFT JOIN clases c ON s.clase_id = c.id
            """)
            filas = cursor.fetchall()

            for fila in filas:
                self.tree_general.insert("", "end", values=fila)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar los datos generales: {e}")

        finally:
            conn.close()

    def obtener_id_equipo_por_nombre(self, nombre_equipo):
        """Obtiene el ID de un equipo según su nombre."""
        conn = conexion_db()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM equipos WHERE nombre = ?", (nombre_equipo,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener ID del equipo: {e}")
            return None
        finally:
            conn.close()

    def obtener_id_clase_por_nombre(self, nombre_clase):
        """Obtiene el ID de una clase según su nombre."""
        conn = conexion_db()
        if conn is None:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM clases WHERE nombre = ?", (nombre_clase,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener ID de la clase: {e}")
            return None
        finally:
            conn.close()

    def cargar_equipos(self):
        """Carga la lista de equipos en el ComboBox."""
        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM equipos")
            equipos = [eq[0] for eq in cursor.fetchall()]
            self.combo_equipos["values"] = equipos

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar equipos: {e}")

        finally:
            conn.close()

    def borrar_servicio(self):
        """Elimina un servicio seleccionado en la tabla general."""
        seleccion = self.tree_general.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un servicio para borrar")
            return

        servicio_id = self.tree_general.item(seleccion)["values"][0]

        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM servicios WHERE id = ?", (servicio_id,))
            conn.commit()
            self.cargar_servicios()
            messagebox.showinfo("Éxito", "Servicio eliminado correctamente")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al eliminar servicio: {e}")
        finally:
            conn.close()

    def limpiar_campos(self):
        """Limpia todos los campos del formulario."""
        for var in [self.var_nombre, self.var_descripcion, self.var_disponibilidad, self.var_dia, self.var_hora, self.var_lugar]:
            var.set("")
        self.tree_servicios.selection_remove(self.tree_servicios.selection())

    def regresar(self):
        """Cierra la ventana y regresa a la pantalla principal."""
        if self.callback_regreso:
            self.root.destroy()
            self.callback_regreso()
            
    def autocompletar_campos(self, event):
        """Autocompleta los formularios de Servicios y Clases al seleccionar una fila de la tabla."""
        seleccion = self.tree_general.selection()
        if seleccion:
            valores = self.tree_general.item(seleccion, "values")

            # Autocompletar Servicios
            self.var_id.set(valores[0])
            self.var_nombre.set(valores[1])
            self.var_descripcion.set(valores[2])  # Ahora es Descripción Servicio
            self.var_disponibilidad.set(valores[3])
            self.var_dia.set(valores[4])
            self.var_hora.set(valores[5])
            self.var_lugar.set(valores[6])
            self.var_equipo.set(valores[7])

            # Autocompletar Clases
            self.var_clase_nombre.set(valores[8])  # Nombre de la clase
            self.var_clase_descripcion.set(valores[9])  # Descripción de la clase
            self.var_clase_duracion.set(valores[10])  # Duración de la clase

    def cargar_clases(self):
        """Carga las clases desde la base de datos y las muestra en la tabla general unificada."""
        conn = conexion_db()
        if conn is None:
            return

        self.tree_general.delete(*self.tree_general.get_children())  # Limpiar la tabla unificada

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, 'Clase' AS tipo, c.nombre, c.descripcion, 'N/A' AS disponible, 
                    'N/A' AS dia, 'N/A' AS hora, 'N/A' AS lugar, 'Sin equipo' AS equipo, 
                    c.nombre AS clase, c.duracion_minutos AS duracion
                FROM clases c
            """)
            filas = cursor.fetchall()

            for fila in filas:
                self.tree_general.insert("", "end", values=fila)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar clases: {e}")

        finally:
            conn.close()

    def registrar_clase(self):
        """Registra una nueva clase en la base de datos."""
        conn = conexion_db()
        if conn is None:
            return
        
        datos = (self.var_clase_nombre.get(), self.var_clase_descripcion.get(), self.var_clase_duracion.get())

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clases (nombre, descripcion, duracion_minutos) VALUES (?, ?, ?)", datos)
            conn.commit()
            self.cargar_clases()
            self.limpiar_campos_clases()
            messagebox.showinfo("Éxito", "Clase registrada correctamente")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de la clase ya existe. Ingrese un nombre único.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar clase: {e}")
        finally:
            conn.close()

    def editar_clase(self):
        """Edita una clase seleccionada en la tabla."""
        seleccion = self.tree_clases.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una clase para editar")
            return
        
        datos = (
            self.var_clase_nombre.get(),
            self.var_clase_descripcion.get(),
            self.var_clase_duracion.get(),
            self.var_clase_id.get()
        )
        
        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE clases SET nombre=?, descripcion=?, duracion_minutos=? WHERE id=?", datos)
            conn.commit()
            self.cargar_clases()
            messagebox.showinfo("Éxito", "Clase actualizada")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al actualizar clase: {e}")
        finally:
            conn.close()

    def borrar_clase(self):
        """Elimina una clase seleccionada en la tabla general."""
        seleccion = self.tree_general.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una clase para borrar")
            return

        clase_id = self.tree_general.item(seleccion)["values"][0]

        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clases WHERE id = ?", (clase_id,))
            conn.commit()
            self.cargar_clases()
            messagebox.showinfo("Éxito", "Clase eliminada correctamente")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al eliminar clase: {e}")
        finally:
            conn.close()

    def limpiar_campos_clases(self):
        """Limpia todos los campos del formulario de clases."""
        for var in [self.var_clase_id, self.var_clase_nombre, self.var_clase_descripcion, self.var_clase_duracion]:
            var.set("")
        self.tree_clases.selection_remove(self.tree_clases.selection())

    def autocompletar_campos_clases(self, event):
        """Autocompleta los campos del formulario cuando se selecciona una clase en la tabla general."""
        seleccion = self.tree_general.selection()
        if seleccion:
            valores = self.tree_general.item(seleccion, "values")
            self.var_clase_id.set(valores[0])
            self.var_clase_nombre.set(valores[2])
            self.var_clase_descripcion.set(valores[3])
            self.var_clase_duracion.set(valores[9])

    def registrar(self):
        """Registra un nuevo servicio y/o clase en la base de datos."""

        conn = conexion_db()
        if conn is None:
            return

        equipo_nombre = self.combo_equipos.get()
        equipo_id = self.obtener_id_equipo_por_nombre(equipo_nombre) if equipo_nombre else None

        clase_nombre = self.var_clase_nombre.get()
        clase_id = self.obtener_id_clase_por_nombre(clase_nombre) if clase_nombre else None

        try:
            cursor = conn.cursor()

            # Registrar Servicio
            cursor.execute("""
                INSERT INTO servicios (nombre, descripcion, disponible, dia, hora, lugar, equipo_id, clase_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.var_nombre.get(),
                self.var_descripcion.get(),
                self.var_disponibilidad.get(),
                self.var_dia.get(),
                self.var_hora.get(),
                self.var_lugar.get(),
                equipo_id,
                clase_id
            ))

            # Registrar Clase si se llenó el nombre de clase
            if clase_nombre:
                cursor.execute("""
                    INSERT OR IGNORE INTO clases (nombre, descripcion, duracion_minutos)
                    VALUES (?, ?, ?)
                """, (
                    self.var_clase_nombre.get(),
                    self.var_clase_descripcion.get(),
                    self.var_clase_duracion.get()
                ))

            conn.commit()
            self.cargar_datos_generales()
            self.limpiar_campos()
            messagebox.showinfo("Éxito", "Registro exitoso")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar: {e}")

        finally:
            conn.close()

    def editar(self):
        """Edita un servicio y/o clase seleccionado en la tabla."""
        seleccion = self.tree_general.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un registro para editar")
            return

        servicio_id = self.tree_general.item(seleccion)['values'][0]

        equipo_nombre = self.combo_equipos.get()
        equipo_id = self.obtener_id_equipo_por_nombre(equipo_nombre) if equipo_nombre else None

        clase_nombre = self.var_clase_nombre.get()
        clase_id = self.obtener_id_clase_por_nombre(clase_nombre) if clase_nombre else None

        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()

            # Actualizar Servicio
            cursor.execute("""
                UPDATE servicios SET 
                    nombre = ?, descripcion = ?, disponible = ?, 
                    dia = ?, hora = ?, lugar = ?, equipo_id = ?, clase_id = ?
                WHERE id = ?
            """, (
                self.var_nombre.get(),
                self.var_descripcion.get(),
                self.var_disponibilidad.get(),
                self.var_dia.get(),
                self.var_hora.get(),
                self.var_lugar.get(),
                equipo_id,
                clase_id,
                servicio_id
            ))

            # Actualizar Clase si existe
            if clase_id:
                cursor.execute("""
                    UPDATE clases SET nombre=?, descripcion=?, duracion_minutos=? WHERE id=?
                """, (
                    self.var_clase_nombre.get(),
                    self.var_clase_descripcion.get(),
                    self.var_clase_duracion.get(),
                    clase_id
                ))

            conn.commit()
            self.cargar_datos_generales()
            messagebox.showinfo("Éxito", "Edición exitosa")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al editar: {e}")

        finally:
            conn.close()

    def borrar(self):
        """Elimina un servicio y su clase asociada."""
        seleccion = self.tree_general.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un registro para eliminar")
            return

        servicio_id = self.tree_general.item(seleccion)["values"][0]

        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM servicios WHERE id = ?", (servicio_id,))
            conn.commit()

            self.cargar_datos_generales()
            messagebox.showinfo("Éxito", "Registro eliminado correctamente")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")

        finally:
            conn.close()

    def cargar_clases_disponibles(self):
        """Carga la lista de clases en el ComboBox."""
        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM clases")
            clases = [clase[0] for clase in cursor.fetchall()]
            self.combo_clases["values"] = clases

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar clases: {e}")

        finally:
            conn.close()

    def autocompletar_clase_seleccionada(self, event):
        """Autocompleta la descripción y la duración cuando se selecciona una clase del combobox."""
        clase_nombre = self.var_clase_nombre.get()
        conn = conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT descripcion, duracion_minutos FROM clases WHERE nombre = ?", (clase_nombre,))
            resultado = cursor.fetchone()
            if resultado:
                self.var_clase_descripcion.set(resultado[0])  # Descripción
                self.var_clase_duracion.set(resultado[1])  # Duración

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al autocompletar clase: {e}")

        finally:
            conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = GestionServicios(root)
    root.mainloop()
