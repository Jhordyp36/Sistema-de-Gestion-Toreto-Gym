import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
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

# Ventana de membresias
def ventana_membresias(usuario, callback):
    """Crea la ventana del módulo de Membresías."""
    ventana = tk.Tk()
    ventana.title("Módulo de Membresías")
    ventana.state("zoomed")
    ventana.configure(bg="#272643")
    cargar_icono(ventana, os.path.join(ICONS_DIR, "Icono.ico"))

    # Frame principal
    frame_contenido = tk.Frame(ventana, bg="#272643")
    frame_contenido.pack(fill="both", expand=True, padx=20, pady=20)

    # Tabla de clientes
    columnas_clientes = ("Cédula", "Apellidos", "Nombres", "Estado", "Membresía")
    tabla_clientes = ttk.Treeview(frame_contenido, columns=columnas_clientes, show="headings")
    for col in columnas_clientes:
        tabla_clientes.heading(col, text=col)
        tabla_clientes.column(col, anchor="center")

    tabla_clientes.pack(fill="both", expand=True)

    # Función para cargar clientes
    def cargar_clientes():
        """Carga los clientes desde la base de datos a la tabla."""
        conn = conexion_db()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute("SELECT cedula, apellidos, nombres, estado, membresia_id FROM usuarios")
        clientes = cursor.fetchall()

        # Limpiar tabla antes de cargar datos
        for item in tabla_clientes.get_children():
            tabla_clientes.delete(item)

        for cliente in clientes:
            tabla_clientes.insert("", "end", values=cliente)

        conn.close()

    cargar_clientes()  # Cargar datos iniciales

    # Función para consultar clientes
    def consultar_clientes():
        """Consulta los clientes según el texto ingresado."""
        filtro = entry_buscar_cliente.get()
        conn = conexion_db()
        if not conn:
            return

        cursor = conn.cursor()
        cursor.execute("""
            SELECT cedula, apellidos, nombres, estado, membresia_id 
            FROM usuarios 
            WHERE (cedula LIKE ? OR apellidos LIKE ? OR nombres LIKE ? OR membresia_id IS NULL)
        """, (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"))
        
        clientes = cursor.fetchall()

        # Limpiar tabla antes de cargar datos
        for item in tabla_clientes.get_children():
            tabla_clientes.delete(item)

        if not clientes:
            messagebox.showinfo("Resultado", "No se encontraron clientes con ese criterio de búsqueda.")
            return

        for cliente in clientes:
            tabla_clientes.insert("", "end", values=cliente)

        conn.close()

    # Función para mostrar la lista completa
    def mostrar_lista_completa():
        """Muestra la lista completa de clientes."""
        cargar_clientes()

    # Campo de entrada para buscar clientes
    entry_buscar_cliente = tk.Entry(frame_contenido, width=30)
    entry_buscar_cliente.pack(pady=5)

    # Botón para consultar clientes
    btn_consultar_cliente = tk.Button(frame_contenido, text="Consultar", command=consultar_clientes)
    btn_consultar_cliente.pack(pady=5)

    # Botón para mostrar lista completa
    btn_mostrar_lista_completa = tk.Button(frame_contenido, text="Mostrar Lista Completa", command=mostrar_lista_completa)
    btn_mostrar_lista_completa.pack(pady=5)

    # Función para abrir ventana de asignar o cambiar membresía
    def abrir_ventana_membresia(cliente_cedula, es_cambio=False):
        """Abre la ventana para asignar o cambiar una membresía al cliente seleccionado."""
        ventana_membresia = tk.Toplevel(ventana)
        ventana_membresia.title("Asignar/Cambiar Membresía")
        ventana_membresia.geometry("400x300")
        
        tk.Label(ventana_membresia, text="Seleccionar Membresía:", font=("Segoe UI", 12)).pack(pady=10)

        # ComboBox para seleccionar membresía
        membresias = ["Pase Diario", "Estándar", "Premium", "VIP"]
        seleccion_membresia = tk.StringVar()
        combo_membresias = ttk.Combobox(ventana_membresia, textvariable=seleccion_membresia, values=membresias)
        combo_membresias.pack(pady=10)

        # Botón de confirmación
        def confirmar_cambio():
            membresia_seleccionada = seleccion_membresia.get()
            if not membresia_seleccionada:
                messagebox.showwarning("Advertencia", "Debe seleccionar un tipo de membresía antes de continuar.")
                return

            # Asignar o cambiar membresía
            conn = conexion_db()
            if not conn:
                return

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT membresia_id FROM usuarios WHERE cedula = ?", (cliente_cedula,))
                membresia_actual = cursor.fetchone()

                if es_cambio:
                    if not membresia_actual or not membresia_actual[0]:  # Si no tiene membresía
                        messagebox.showerror("Error", "Este cliente no tiene una membresía asignada.")
                        return
                    
                    if membresia_actual[0] == membresias.index(membresia_seleccionada) + 1:  # Si ya tiene la misma membresía
                        messagebox.showerror("Error", "El cliente ya cuenta con esta membresía.")
                        return
                    
                    # Cambiar membresía
                    membresia_id = membresias.index(membresia_seleccionada) + 1
                    cursor.execute("UPDATE usuarios SET membresia_id = ? WHERE cedula = ?", (membresia_id, cliente_cedula))
                    messagebox.showinfo("Éxito", f"La membresía del cliente ha sido cambiada a '{membresia_seleccionada}' exitosamente.")

                else:
                    if membresia_actual and membresia_actual[0]:  # Si ya tiene membresía
                        messagebox.showerror("Error", "Este cliente ya tiene una membresía asignada.")
                        return
                    
                    # Asignar nueva membresía
                    membresia_id = membresias.index(membresia_seleccionada) + 1
                    cursor.execute("UPDATE usuarios SET membresia_id = ? WHERE cedula = ?", (membresia_id, cliente_cedula))
                    messagebox.showinfo("Éxito", f"La membresía '{membresia_seleccionada}' ha sido asignada al cliente.")

                conn.commit()
                ventana_membresia.destroy()  # Cerrar ventana

                # Volver a cargar clientes
                cargar_clientes()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo cambiar/asignar la membresía: {e}")
            finally:
                conn.close()

        btn_confirmar = tk.Button(ventana_membresia, text="Confirmar", command=confirmar_cambio)
        btn_confirmar.pack(pady=20)

    # Función para asignar membresía
    def asignar_membresia():
        """Abre la ventana de asignación de membresía."""
        selected_item = tabla_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, selecciona un cliente.")
            return
        
        cliente_cedula = tabla_clientes.item(selected_item)["values"][0]
        abrir_ventana_membresia(cliente_cedula, es_cambio=False)

    # Función para cambiar membresía
    def cambiar_membresia():
        """Abre la ventana de cambio de membresía."""
        selected_item = tabla_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, selecciona un cliente.")
            return
        
        cliente_cedula = tabla_clientes.item(selected_item)["values"][0]
        abrir_ventana_membresia(cliente_cedula, es_cambio=True)

    # Función para deshabilitar cliente
    def deshabilitar_cliente():
        """Abre la ventana para cambiar el estado del cliente seleccionado."""
        selected_item = tabla_clientes.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, selecciona un cliente.")
            return
        
        cliente_cedula = tabla_clientes.item(selected_item)["values"][0]
        estado_actual = tabla_clientes.item(selected_item)["values"][3]  # Obtener el estado actual

        ventana_estado = tk.Toplevel(ventana)
        ventana_estado.title("Cambiar Estado")
        ventana_estado.geometry("300x200")

        tk.Label(ventana_estado, text="Espacio para verificar si se realizó pago", font=("Segoe UI", 12)).pack(pady=10)
        
        # ComboBox para seleccionar nuevo estado (solo activo)
        nuevo_estado = tk.StringVar(value="A")  # Solo 'A' para activo
        combo_estado = ttk.Combobox(ventana_estado, textvariable=nuevo_estado, values=["A"])
        combo_estado.pack(pady=10)

        # Botón de confirmación
        def confirmar_estado():
            conn = conexion_db()
            if not conn:
                return
            
            try:
                cursor = conn.cursor()
                # Establecer siempre como activo
                cursor.execute("UPDATE usuarios SET estado = 'A' WHERE cedula = ?", (cliente_cedula,))
                conn.commit()
                messagebox.showinfo("Éxito", "El estado del cliente ha sido actualizado a Activo.")
                ventana_estado.destroy()  # Cerrar ventana

                # Volver a cargar clientes
                cargar_clientes()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo cambiar el estado del cliente: {e}")
            finally:
                conn.close()

        btn_confirmar_estado = tk.Button(ventana_estado, text="Confirmar", command=confirmar_estado)
        btn_confirmar_estado.pack(pady=20)

    # Botones de acción
    btn_asignar_membresia = tk.Button(frame_contenido, text="Asignar Membresía", command=asignar_membresia)
    btn_asignar_membresia.pack(side="left", padx=10, pady=10)

    btn_cambiar_membresia = tk.Button(frame_contenido, text="Cambiar Membresía", command=cambiar_membresia)
    btn_cambiar_membresia.pack(side="left", padx=10, pady=10)

    btn_deshabilitar_membresia = tk.Button(frame_contenido, text="Habilitar Cliente", command=deshabilitar_cliente)
    btn_deshabilitar_membresia.pack(side="left", padx=10, pady=10)

    # Botón para regresar a la ventana principal
    btn_regresar = tk.Button(frame_contenido, text="Regresar", command=lambda: [ventana.destroy(), callback()])
    btn_regresar.pack(side="left", padx=10, pady=10)

    ventana.mainloop()