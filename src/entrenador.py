import sys
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono

class GestionEntrenadores:
    def __init__(self, root):
        """Inicializa la ventana de gestión de entrenadores."""
        self.root = root
        self.root.title("Gestión de Entrenadores")
        self.root.state("zoomed")
        self.root.configure(bg="#272643")
        cargar_icono(self.root, os.path.join(ICONS_DIR, "Icono.ico"))

        # Estilo para botones ttk
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 12))  # Aplicar estilo a todos los botones ttk
        
        # Frame para botones principales
        self.frame_botones_principales = tk.Frame(self.root, bg="#2c698d", pady=5)
        self.frame_botones_principales.pack(side="top", fill="x")

        # Contenedor principal
        self.frame_contenido = tk.Frame(self.root, bg="#272643")
        self.frame_contenido.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Crear variables para las tablas
        self.tabla_entrenadores = None
        self.tabla_servicios = None
        
        # Botón para cambiar vistas (Corrección: eliminar bg y usar style)
        ttk.Button(self.frame_botones_principales, text="Vista General", style="TButton",
                   command=self.cargar_vista_general).pack(side="left", padx=10)

        # Cargar la vista general al iniciar
        self.cargar_vista_general()

    def conexion_db(self):
        """Establece la conexión con SQLite."""
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la base de datos:\n{e}")
            return None

    def limpiar_contenido(self):
        """Elimina todos los widgets de frame_contenido para cambiar la vista."""
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def obtener_id_seleccionado(self, tabla):
        """Devuelve el ID (cédula) del entrenador seleccionado en la tabla."""
        seleccionado = tabla.selection()
        if seleccionado:
            return tabla.item(seleccionado[0], "values")[0]  # Primera columna es la cédula
        return None

    def mostrar_servicios(self, tabla_servicios, entrenador_id):
        """Muestra los servicios asignados al entrenador seleccionado."""
        if entrenador_id is None:
            messagebox.showwarning("Selección", "Por favor, seleccione un entrenador.")
            return

        conn = self.conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.nombre
                FROM servicios s
                JOIN entrenadores_servicios es ON s.id = es.servicio_id
                WHERE es.entrenador_id = ?
            """, (entrenador_id,))
            servicios = cursor.fetchall()

            # Limpiar la tabla
            for item in tabla_servicios.get_children():
                tabla_servicios.delete(item)

            # Insertar datos en la tabla
            for servicio in servicios:
                tabla_servicios.insert("", "end", values=servicio)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener servicios: {e}")
        finally:
            conn.close()

    def cargar_entrenadores_tabla(self):
        """Carga la lista de entrenadores en la tabla."""
        conn = self.conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cedula, nombres, apellidos, correo, telefono, clase_asignada
                FROM usuarios
                WHERE rol = 'Entrenador' AND estado = 'A'
            """)
            entrenadores = cursor.fetchall()

            # Limpiar la tabla
            for item in self.tabla_entrenadores.get_children():
                self.tabla_entrenadores.delete(item)

            # Insertar entrenadores en la tabla
            for entrenador in entrenadores:
                self.tabla_entrenadores.insert("", "end", values=entrenador)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener entrenadores: {e}")
        finally:
            conn.close()

    def cargar_clases_combobox(self, combobox):
        """Carga las clases disponibles en el combobox."""
        conn = self.conexion_db()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM clases WHERE estado = 'Activo'")
            clases = [row[0] for row in cursor.fetchall()]
            combobox["values"] = clases
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener clases: {e}")
        finally:
            conn.close()

    def cargar_editar_entrenadores(self):
        """Carga la vista de edición de entrenadores en la misma pantalla."""
        self.limpiar_contenido()

        tk.Label(self.frame_contenido, text="Editar Entrenador", font=("Segoe UI", 16), bg="#272643", fg="white").pack(pady=10)

        frame_edicion = tk.Frame(self.frame_contenido, bg="#272643")
        frame_edicion.pack(pady=10, fill="both", expand=True)

        frame_izquierda = tk.Frame(frame_edicion, bg="#272643")
        frame_izquierda.pack(side="left", padx=20, fill="y", expand=True)

        var_cedula = tk.StringVar()
        var_nombre = tk.StringVar()
        var_apellido = tk.StringVar()
        var_correo = tk.StringVar()
        var_telefono = tk.StringVar()
        var_clase = tk.StringVar()

        campos = [
            ("Cédula:", var_cedula),
            ("Nombre:", var_nombre),
            ("Apellido:", var_apellido),
            ("Correo:", var_correo),
            ("Teléfono:", var_telefono),
            ("Clase Asignada:", var_clase)
        ]

        for i, (label, var) in enumerate(campos):
            tk.Label(frame_izquierda, text=label, bg="#272643", fg="white", font=("Segoe UI", 12)).grid(row=i, column=0, sticky="w", padx=5, pady=5)

            if label == "Clase Asignada:":
                combo_clases = ttk.Combobox(frame_izquierda, textvariable=var, state="readonly", width=30)
                combo_clases.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
                self.cargar_clases_combobox(combo_clases)
            else:
                tk.Entry(frame_izquierda, textvariable=var, width=30).grid(row=i, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(self.frame_contenido, text="Cancelar", font=("Segoe UI", 12), bg="#bae8e8", command=self.cargar_vista_general).pack(side="left", padx=10)

    def cargar_vista_general(self):
        """Carga la vista general de entrenadores."""
        self.limpiar_contenido()

        frame_botones = tk.Frame(self.frame_contenido, bg="#272643")
        frame_botones.pack(side="top", fill="x")

        tk.Button(frame_botones, text="Editar Entrenador - Clases", font=("Segoe UI", 12), bg="#bae8e8",
                  command=self.cargar_editar_entrenadores).pack(side="left", padx=10, pady=10)

        tk.Button(frame_botones, text="Mostrar Servicios", font=("Segoe UI", 12), bg="#bae8e8",
                  command=self.mostrar_servicios).pack(side="left", padx=10, pady=10)

        # Crear tablas en la vista general
        frame_tabla = tk.Frame(self.frame_contenido, bg="#272643")
        frame_tabla.pack(fill="both", expand=True)

        columnas = ("Cédula", "Nombre", "Apellido", "Correo", "Teléfono", "Clase")
        self.tabla_entrenadores = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        for col in columnas:
            self.tabla_entrenadores.heading(col, text=col)
            self.tabla_entrenadores.column(col, width=150, anchor="center")

        self.tabla_entrenadores.pack(side="left", fill="both", expand=True)
        self.cargar_entrenadores_tabla()

        # Tabla de servicios
        frame_tabla2 = tk.Frame(self.frame_contenido, bg="#272643")
        frame_tabla2.pack(fill="both", expand=True)

        label_tabla2 = tk.Label(frame_tabla2, text="Servicios", bg="#272643", font=("Segoe UI", 12))
        label_tabla2.pack(anchor="n", pady=5)

        columnas_servicios = ("ID", "Servicio")
        self.tabla_servicios = ttk.Treeview(frame_tabla2, columns=columnas_servicios, show="headings")

        for col in columnas_servicios:
            self.tabla_servicios.heading(col, text=col)
            self.tabla_servicios.column(col, width=150, anchor="center")

        self.tabla_servicios.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = GestionEntrenadores(root)
    root.mainloop()
