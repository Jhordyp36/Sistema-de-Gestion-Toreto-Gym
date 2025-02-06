from datetime import datetime
import os
import re
import sqlite3
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import Button, Frame, Label, Entry, Scrollbar, Tk, ttk, messagebox
from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono

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

    def exportar_logs(tabla):
        # Obtener los registros de la tabla
        registros = [tabla.item(fila)["values"] for fila in tabla.get_children()]

        if not registros:
            messagebox.showwarning("Sin datos", "No hay datos para exportar.")
            return

        while True:
            # Seleccionar la carpeta donde guardar el archivo y permitir elegir nombre
            ruta = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Archivos PDF", "*.pdf")])

            if not ruta:
                messagebox.showwarning("No se seleccionó archivo", "No se ha seleccionado un archivo para guardar.")
                return

            # Extraer el nombre del archivo sin la ruta completa
            nombre_archivo = ruta.split("/")[-1].split("\\")[-1]  # Compatibilidad con Windows y Linux

            # Validar que el nombre no esté vacío, no tenga solo puntos o comas, y contenga al menos una letra
            if not nombre_archivo.strip() or not re.search(r'[A-Za-z]', nombre_archivo) or re.match(r'^[.,]+$', nombre_archivo):
                messagebox.showerror("Nombre de archivo no válido", "El nombre del archivo no puede estar vacío, contener solo puntos o comas, y debe incluir al menos una letra.")
            elif re.match(r'^[\.,]+$', nombre_archivo):  # Verifica si el nombre está compuesto solo por puntos o comas
                messagebox.showerror("Nombre de archivo no válido", "El nombre del archivo no puede contener solo puntos o comas.")
            else:
                break  # Salir del bucle si el nombre es válido

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


    def limpiar_contenido():
        for widget in frame_contenido.winfo_children():
            widget.destroy()
    
    # Botones de navegación
    Button(frame_botones_principales, text="Regresar", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: regresar(callback, ventana)).pack(side="right", padx=10)   

    ventana.bind_all("<KeyPress>", verificar_secuencia)
    ventana.mainloop()

def regresar(callback, ventana):
    ventana.destroy()
    callback()