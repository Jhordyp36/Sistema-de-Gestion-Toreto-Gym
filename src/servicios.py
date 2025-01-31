import sys
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Agregar el directorio raíz al PATH para importar config.py correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono

def conexion_db():
    """
    Establece la conexión con la base de datos SQLite.
    Devuelve la conexión si es exitosa, o None si hay un error.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

class GestionServicios:
    """
    Clase que gestiona la interfaz y operaciones CRUD para la tabla 'servicios'.
    """

    def __init__(self, root, callback_regreso=None):
        """
        Inicializa la interfaz de usuario y carga los datos desde la base de datos.
        """
        self.root = root
        self.root.title("Gestión de Servicios")
        self.root.state("zoomed")  # Ventana en pantalla completa
        self.root.configure(bg="#272643")

        cargar_icono(self.root, ICONS_DIR)

        self.callback_regreso = callback_regreso  # ✅ Guardar la función de regreso

        # Variables para los campos del formulario
        self.var_id = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_disponibilidad = tk.StringVar()
        self.var_clase_id = tk.StringVar()
        self.var_equipo_id = tk.StringVar()

        # Configurar la interfaz gráfica
        self.configurar_interfaz()
        self.cargar_servicios()

    def configurar_interfaz(self):
        """Configura la interfaz gráfica de usuario con Tkinter."""
        
        default_font = ("Segoe UI", 12)
        header_font = ("Segoe UI", 14, "bold")

        # Título
        tk.Label(self.root, text="Gestión de Servicios", font=header_font, bg="#272643", fg="#bae8e8").pack(pady=20)

        # Frame para los campos de entrada
        frame_form = tk.Frame(self.root, bg="#272643")
        frame_form.pack(pady=10)

        # Campos del formulario
        campos = ["Nombre:", "Descripción:", "Disponibilidad (Sí, No):", "Clase ID:", "Equipo ID:"]
        variables = [self.var_nombre, self.var_descripcion, self.var_disponibilidad, self.var_clase_id, self.var_equipo_id]
        self.entries = []

        for i, (campo, variable) in enumerate(zip(campos, variables)):
            tk.Label(frame_form, text=campo, font=default_font, bg="#272643", fg="#bae8e8").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(frame_form, textvariable=variable, font=default_font, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(entry)

        # Botones de acción
        frame_botones = tk.Frame(self.root, bg="#272643")
        frame_botones.pack(pady=10)

        btn_registrar = tk.Button(frame_botones, text="Registrar Servicio", font=default_font, bg="#bae8e8", command=self.registrar_servicio)
        btn_registrar.grid(row=0, column=0, padx=10)

        btn_editar = tk.Button(frame_botones, text="Editar Servicio", font=default_font, bg="#bae8e8", command=self.editar_servicio)
        btn_editar.grid(row=0, column=1, padx=10)

        btn_consultar = tk.Button(frame_botones, text="Consultar Servicios", font=default_font, bg="#bae8e8", command=self.cargar_servicios)
        btn_consultar.grid(row=0, column=2, padx=10)

        # ✅ Botón de regresar correctamente configurado
        btn_regresar = tk.Button(frame_botones, text="Regresar", font=default_font, bg="#e3f6f5", command=self.regresar)
        btn_regresar.grid(row=0, column=3, padx=10)

        # Tabla para mostrar los servicios registrados
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nombre", "Descripción", "Disponible", "Clase ID", "Equipo ID"), show="headings", height=10)
        self.tree.pack(pady=20)

        for col in ("ID", "Nombre", "Descripción", "Disponible", "Clase ID", "Equipo ID"):
            self.tree.heading(col, text=col)

        # Evento para autocompletar campos al seleccionar un servicio en la tabla
        self.tree.bind("<<TreeviewSelect>>", self.autocompletar_campos)

    def regresar(self):
        """Cierra la ventana actual y regresa a la ventana principal."""
        if self.callback_regreso:
            self.root.destroy()
            self.callback_regreso()
    
    def registrar_servicio(self):
        """Registra un nuevo servicio en la base de datos."""
        conn = conexion_db()
        if conn is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return

        nombre = self.var_nombre.get()
        descripcion = self.var_descripcion.get()
        disponible = self.var_disponibilidad.get()
        clase_id = self.var_clase_id.get()
        equipo_id = self.var_equipo_id.get()

        if not nombre or not disponible:
            messagebox.showerror("Error", "El nombre y la disponibilidad son obligatorios.")
            return

        cursor = conn.cursor()
        cursor.execute("INSERT INTO servicios (nombre, descripcion, disponible, clase_id, equipo_id) VALUES (?, ?, ?, ?, ?)", 
                       (nombre, descripcion, disponible, clase_id, equipo_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Servicio registrado correctamente.")
        self.cargar_servicios()
        self.limpiar_campos()

    def cargar_servicios(self):
        """Carga los servicios desde la base de datos y los muestra en la tabla."""
        conn = conexion_db()
        if conn is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return

        self.tree.delete(*self.tree.get_children())
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicios")
        for fila in cursor.fetchall():
            self.tree.insert("", "end", values=fila)
        conn.close()

    def editar_servicio(self):
        """Edita un servicio seleccionado en la tabla."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un servicio para editar.")
            return

        id_seleccionado = self.tree.item(seleccion, "values")[0]

        nombre = self.var_nombre.get()
        descripcion = self.var_descripcion.get()
        disponible = self.var_disponibilidad.get()
        clase_id = self.var_clase_id.get()
        equipo_id = self.var_equipo_id.get()

        conn = conexion_db()
        if conn is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return

        cursor = conn.cursor()
        cursor.execute("UPDATE servicios SET nombre=?, descripcion=?, disponible=?, clase_id=?, equipo_id=? WHERE id=?", 
                       (nombre, descripcion, disponible, clase_id, equipo_id, id_seleccionado))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Servicio actualizado correctamente.")
        self.cargar_servicios()
        self.limpiar_campos()

    def autocompletar_campos(self, event):
        """Autocompleta los campos del formulario cuando se selecciona un servicio en la tabla."""
        seleccion = self.tree.selection()
        if seleccion:
            valores = self.tree.item(seleccion, "values")
            self.var_id.set(valores[0])
            self.var_nombre.set(valores[1])
            self.var_descripcion.set(valores[2])
            self.var_disponibilidad.set(valores[3])
            self.var_clase_id.set(valores[4])
            self.var_equipo_id.set(valores[5])

    def limpiar_campos(self):
        """Limpia los cuadros de texto y deselecciona la fila en la tabla."""
        self.var_id.set("")
        self.var_nombre.set("")
        self.var_descripcion.set("")
        self.var_disponibilidad.set("")
        self.var_clase_id.set("")
        self.var_equipo_id.set("")
        self.tree.selection_remove(self.tree.selection())

if __name__ == "__main__":
    def regresar_a_principal():
        print("Regresando a la ventana principal")

    root = tk.Tk()
    app = GestionServicios(root, callback_regreso=regresar_a_principal)
    root.mainloop()