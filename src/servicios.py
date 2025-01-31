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
    """Establece la conexión con SQLite y evita bloqueos."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)  # Esperar hasta 10 segundos si está bloqueada
        conn.execute("PRAGMA journal_mode=WAL;")  # Permite acceso concurrente
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
        self.var_dia = tk.StringVar()
        self.var_hora = tk.StringVar()
        self.var_lugar = tk.StringVar()
        self.var_id_filtro = tk.StringVar()  # Para filtrar por ID

        # Configurar la interfaz gráfica
        self.configurar_interfaz()
        self.cargar_servicios()

    def configurar_interfaz(self):
        """Configura la interfaz gráfica de usuario con Tkinter."""
        default_font = ("Segoe UI", 12)
        header_font = ("Segoe UI", 14, "bold")

        # Título
        tk.Label(self.root, text="Gestión de Servicios", font=header_font, bg="#272643", fg="#bae8e8").pack(pady=20)

        # Frame principal
        frame_principal = tk.Frame(self.root, bg="#272643")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=10)

        # Frame para los campos de entrada
        frame_form = tk.Frame(frame_principal, bg="#272643", width=500, height=300)
        frame_form.pack(side="left", padx=20, pady=10, fill="both", expand=True)
        frame_form.grid_propagate(False)  # Evita que se agrande automáticamente

        # Campos del formulario con límite de ancho
        campos = ["Nombre:", "Descripción:", "Disponibilidad (Sí, No):", "Clase ID:", "Equipo ID:", "Día:", "Hora:", "Lugar:"]
        variables = [self.var_nombre, self.var_descripcion, self.var_disponibilidad, self.var_clase_id, self.var_equipo_id, self.var_dia, self.var_hora, self.var_lugar]
        self.entries = []

        for i, (campo, variable) in enumerate(zip(campos, variables)):
            tk.Label(frame_form, text=campo, font=default_font, bg="#272643", fg="#bae8e8").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            entry = tk.Entry(frame_form, textvariable=variable, font=default_font, width=30)  # Reducimos ancho si es necesario
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")  # Ajuste sin desbordarse
            self.entries.append(entry)

        frame_form.grid_columnconfigure(1, weight=1)  # Permite ajuste sin expansión descontrolada

        # Frame para botones
        frame_botones = tk.Frame(self.root, bg="#272643")
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Registrar Servicio", font=default_font, bg="#bae8e8", command=self.registrar_servicio).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Editar Servicio", font=default_font, bg="#bae8e8", command=self.editar_servicio).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Borrar Servicio", font=default_font, bg="#ff6961", command=self.borrar_servicio).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Limpiar", font=default_font, bg="#e3f6f5", command=self.limpiar_campos).pack(side="left", padx=10)
        tk.Button(frame_botones, text="Regresar", font=default_font, bg="#e3f6f5", command=self.regresar).pack(side="left", padx=10)

        # Frame para la tabla
        frame_tabla = tk.Frame(self.root, width=800, height=300)
        frame_tabla.pack(pady=10, fill="both", expand=True)
        frame_tabla.grid_propagate(False)  # Mantiene el tamaño definido

        self.tree = ttk.Treeview(frame_tabla, columns=("ID", "Nombre", "Descripción", "Disponible", "Clase ID", "Equipo ID", "Día", "Hora", "Lugar"),
                                show="headings", height=10)
        self.tree.pack(side="left", fill="both", expand=True)

        for col in ("ID", "Nombre", "Descripción", "Disponible", "Clase ID", "Equipo ID", "Día", "Hora", "Lugar"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

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
        dia = self.var_dia.get()
        hora = self.var_hora.get()
        lugar = self.var_lugar.get()

        if not nombre or not disponible or not dia or not hora or not lugar:
            messagebox.showerror("Error", "El nombre, disponibilidad, día, hora y lugar son obligatorios.")
            return

        cursor = conn.cursor()

        # 🔍 Validar si el servicio ya existe
        cursor.execute("SELECT id FROM servicios WHERE nombre = ?", (nombre,))
        servicio_existente = cursor.fetchone()

        if servicio_existente:
            messagebox.showerror("Error", "Ya existe un servicio con este nombre.")
            conn.close()
            return

        # ✅ Insertar nuevo servicio
        try:
            cursor.execute(
                "INSERT INTO servicios (nombre, descripcion, disponible, clase_id, equipo_id, dia, hora, lugar) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (nombre, descripcion, disponible, clase_id, equipo_id, dia, hora, lugar)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Servicio registrado correctamente.")
            self.cargar_servicios()
            self.limpiar_campos()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo registrar el servicio: {e}")
        finally:
            conn.close()

    def cargar_servicios(self):
        """Carga los servicios desde la base de datos y los muestra en la tabla."""
        conn = conexion_db()
        if conn is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return

        self.tree.delete(*self.tree.get_children())  

        cursor = conn.cursor()
        query = "SELECT id, nombre, descripcion, disponible, clase_id, equipo_id, dia, hora, lugar FROM servicios"

        if self.var_id_filtro.get():  
            query += " WHERE id = ?"
            cursor.execute(query, (self.var_id_filtro.get(),))
        else:
            cursor.execute(query)

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
        dia = self.var_dia.get()
        hora = self.var_hora.get()
        lugar = self.var_lugar.get()

        conn = conexion_db()
        if conn is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return

        cursor = conn.cursor()
        cursor.execute("UPDATE servicios SET nombre=?, descripcion=?, disponible=?, clase_id=?, equipo_id=?, dia=?, hora=?, lugar=? WHERE id=?", 
                    (nombre, descripcion, disponible, clase_id, equipo_id, dia, hora, lugar, id_seleccionado))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Servicio actualizado correctamente.")
        self.cargar_servicios()
        self.limpiar_campos()

    def borrar_servicio(self):
        """Elimina un servicio seleccionado o por ID ingresado en el filtro."""
        conn = conexion_db()
        if conn is None:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
            return

        id_seleccionado = self.var_id_filtro.get()

        if not id_seleccionado:
            seleccion = self.tree.selection()
            if not seleccion:
                messagebox.showerror("Error", "Seleccione un servicio de la tabla o ingrese un ID.")
                return
            id_seleccionado = self.tree.item(seleccion, "values")[0]

        confirmacion = messagebox.askyesno("Confirmar", f"¿Está seguro de que desea eliminar el servicio con ID {id_seleccionado}?")
        if not confirmacion:
            return

        cursor = conn.cursor()
        cursor.execute("DELETE FROM servicios WHERE id = ?", (id_seleccionado,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Servicio eliminado correctamente.")
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
            self.var_dia.set(valores[6])  # Nuevo campo
            self.var_hora.set(valores[7])  # Nuevo campo
            self.var_lugar.set(valores[8])  # Nuevo campo

    def limpiar_campos(self):
        """Limpia los cuadros de texto y resetea la tabla."""
        self.var_id_filtro.set("")
        for var in [self.var_nombre, self.var_descripcion, self.var_disponibilidad, self.var_clase_id, self.var_equipo_id, self.var_dia, self.var_hora, self.var_lugar]:
            var.set("")
        self.tree.selection_remove(self.tree.selection())
        self.cargar_servicios()

if __name__ == "__main__":
    def regresar_a_principal():
        print("Regresando a la ventana principal")

    root = tk.Tk()
    app = GestionServicios(root, callback_regreso=regresar_a_principal)
    root.mainloop()