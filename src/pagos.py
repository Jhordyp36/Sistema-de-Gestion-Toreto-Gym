from datetime import datetime
import os
import sqlite3
import tkinter as tk
from tkinter import Button, Entry, Frame, Label, Listbox, Scrollbar, StringVar, Tk, Toplevel, messagebox, ttk
from tkcalendar import DateEntry
from reportlab.pdfgen import canvas  # Para generar facturas en PDF

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

def ventana_pagos(usuario, callback):
    """ Crea la ventana de Gestión de Pagos y Facturación. """
    ventana = Tk()
    ventana.title("Gestión de Pagos y Facturación")
    ventana.state("zoomed")
    ventana.resizable(False, False)
    ventana.configure(bg="#272643")
    cargar_icono(ventana, os.path.join(ICONS_DIR, "Icono.ico"))

    # HEADER
    frame_header = Frame(ventana, bg="#2C3E50", pady=10)
    frame_header.pack(fill="x")
    Label(frame_header, text="Gestión de Pagos y Facturación", font=("Segoe UI", 18, "bold"), fg="white", bg="#2C3E50").pack()

    # BOTONES PRINCIPALES
    frame_botones_principales = Frame(ventana, bg="#2c698d", pady=10)
    frame_botones_principales.pack(fill="x", padx=20)

    btn_registrar_pago = Button(frame_botones_principales, text="Registrar Pago", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: registrar_pago())
    btn_registrar_pago.pack(side="left", padx=10)

    btn_historial_pagos = Button(frame_botones_principales, text="Historial de Pagos", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: ver_historial_pagos())
    btn_historial_pagos.pack(side="left", padx=10)

    btn_editar_pago = Button(frame_botones_principales, text="Editar Pago", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: editar_pago())
    btn_editar_pago.pack(side="left", padx=10)  # Este es el nuevo botón para editar el pago

    btn_eliminar_pago = Button(frame_botones_principales, text="Eliminar Pago", font=("Segoe UI", 14), bg="#f19c42", fg="white", command=lambda: eliminar_pago())
    btn_eliminar_pago.pack(side="left", padx=10)  # Este es el botón para eliminar el pago
    
    btn_factura = Button(frame_botones_principales, text="Emitir Factura", font=("Segoe UI", 14), bg="#bae8e8", command=lambda: emitir_factura(), state="disabled")
    btn_factura.pack(side="left", padx=10)

    btn_regresar = Button(frame_botones_principales, text="Regresar", font=("Segoe UI", 14), bg="red", fg="white", command=lambda: regresar(callback, ventana))
    btn_regresar.pack(side="left", padx=10)

    # CONTENEDOR PRINCIPAL
    frame_contenido = Frame(ventana, bg="#272643")
    frame_contenido.pack(fill="both", expand=True, padx=20, pady=20)

    # TÍTULO DE LA TABLA
    Label(frame_contenido, text="Lista de Usuarios", font=("Segoe UI", 16, "bold"), fg="white", bg="#272643").pack(pady=10)

    # FRAME DE LA TABLA
    frame_tabla = Frame(frame_contenido, bg="#272643")
    frame_tabla.pack(expand=True, fill="both", padx=20, pady=10)

    columnas = ("Cédula", "Nombre", "Membresía", "Monto", "Pago")
    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col.capitalize())
        tabla.column(col, width=120, anchor="center")

    tabla.pack(expand=True, fill="both")

    def cargar_datos_usuarios():
        """Carga en la tabla los usuarios registrados con pagos pendientes."""
        conn = conexion_db()
        if not conn:
            return
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                u.cedula,
                u.nombres,
                m.nombre AS membresia,
                m.precio AS monto,  -- Aquí se toma el precio de la membresía
                u.cedula  -- Aquí se mantiene la cédula para referencia
            FROM 
                usuarios u
            LEFT JOIN 
                membresias m ON u.membresia_id = m.id
            WHERE 
                u.rol IN ('Cliente', 'Entrenador');
        """)

        datos = cursor.fetchall()
        conn.close()

        # Limpiar tabla antes de cargar nuevos datos
        for item in tabla.get_children():
            tabla.delete(item)

        # Cargar las filas de la tabla
        for fila in datos:
            # Obtener la cédula para luego determinar el estado de pago
            cedula = fila[0]
            
            # Usamos la función obtener_estado_pago para obtener el estado de pago del usuario
            estado_pago = obtener_estado_pago(cedula)

            # Reemplazar la cédula con "Paga" o "No paga" dependiendo del estado de pago
            if estado_pago == "Pagado":
                estado_pago = "Paga"
            else:
                estado_pago = "No paga"

            # Inserta la fila modificada en la tabla, donde el último campo ahora es el estado de pago
            tabla.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], estado_pago))

        # Revisar el estado de pago de cada usuario y habilitar/deshabilitar el botón de "Emitir Factura"
        habilitar_factura = False  # Variable para determinar si habilitar el botón

        for item in tabla.get_children():
            # Obtener la cédula del usuario (que está en la primera columna)
            cedula = tabla.item(item)["values"][0]
            
            # Usamos la función obtener_estado_pago para obtener el estado de pago del usuario
            estado_pago = obtener_estado_pago(cedula)

            # Si el estado es "Paga" o "Pagado", habilitamos el botón de "Emitir Factura"
            if estado_pago == "Pagado" or estado_pago == "Paga":
                habilitar_factura = True
                break  # Ya encontramos un usuario que pagó, no es necesario seguir buscando

        # Habilitar o deshabilitar el botón de "Emitir Factura"
        if habilitar_factura:
            btn_factura.config(state="normal")
        else:
            btn_factura.config(state="disabled")

    def cargar_datos_pagos():
        """Carga los datos de los pagos en la tabla."""
        # Limpiar los datos existentes en la tabla antes de cargar nuevos
        for item in tabla.get_children():
            tabla.delete(item)
        
        # Conectar a la base de datos y recuperar los datos de los pagos
        conn = conexion_db()
        cursor = conn.cursor()
        try:
            # Obtener los datos de los pagos desde la base de datos
            cursor.execute("""
                SELECT p.id, p.cedula, p.monto, p.fecha_pago, m.nombre
                FROM pagos p
                JOIN membresias m ON p.membresia_id = m.id
            """)
            pagos = cursor.fetchall()
            
            # Insertar los datos en la tabla
            for pago in pagos:
                # Asegúrate de que el monto es un número y no None
                monto = pago[2] if pago[2] is not None else 0
                # Para la columna "Pago", muestra el estado de pago (si está pagado o no)
                estado_pago = 'Pagado' if pago[3] else 'No Pagado'
                tabla.insert("", "end", values=(pago[0], pago[1], pago[4], monto, estado_pago))
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudieron cargar los pagos: {e}")
        finally:
            conn.close()

    def editar_pago():
        """Abre una ventana para editar la información de un pago."""
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un pago para editar")
            return

        item = tabla.item(seleccionado[0])
        datos = item['values']

        # Obtener estado de pago utilizando la función obtener_estado_pago
        estado_pago = obtener_estado_pago(datos[0])  # La cédula está en la primera columna

        ventana_editar = Toplevel(ventana)
        ventana_editar.title("Editar Pago")
        ventana_editar.geometry("600x400")
        ventana_editar.configure(bg="#272643")

        # Frame principal
        frame_principal = Frame(ventana_editar, bg="#272643", padx=20, pady=20)
        frame_principal.pack(fill="both", expand=True)

        Label(frame_principal, text="Editar Pago", font=("Segoe UI", 14, "bold"), fg="white", bg="#272643").pack(pady=5)

        Label(frame_principal, text="Cédula:", bg="#272643", fg="white").pack(anchor="w")
        entry_cedula = Entry(frame_principal)
        entry_cedula.insert(0, datos[0])
        entry_cedula.config(state="disabled")  # No se puede modificar la cédula
        entry_cedula.pack(fill="x")

        Label(frame_principal, text="Monto:", bg="#272643", fg="white").pack(anchor="w")
        entry_monto = Entry(frame_principal)
        entry_monto.insert(0, datos[3])
        entry_monto.pack(fill="x")

        Label(frame_principal, text="Fecha de Pago:", bg="#272643", fg="white").pack(anchor="w")
        
        # Cuadro de selección de fecha con DateEntry
        entry_fecha_pago = DateEntry(frame_principal, width=28, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        
        # Asignamos la fecha actual si la fecha de pago no es válida (No paga, None, etc.)
        if datos[4] in [None, 'No paga'] or not datos[4]:
            fecha_pago = datetime.now().date()  # Asignar la fecha actual si no hay una fecha de pago válida
        else:
            try:
                fecha_pago = datetime.strptime(datos[4], '%Y-%m-%d').date()  # Si es una fecha válida, la usamos
            except ValueError:
                fecha_pago = datetime.now().date()  # Si ocurre un error, asignamos la fecha actual

        entry_fecha_pago.set_date(fecha_pago)
        entry_fecha_pago.pack(fill="x")

        def validar_monto(monto):
            """Valida que el monto sea un número positivo."""
            try:
                monto = float(monto)
                if monto <= 0:
                    return False
                return True
            except ValueError:
                return False

        def actualizar_pago():
            """Actualiza la información del pago en la base de datos."""
            cedula = datos[0]
            monto = entry_monto.get().strip()
            
            if not validar_monto(monto):
                messagebox.showerror("Error", "El monto ingresado no es válido.")
                return
            
            monto = float(monto)
            fecha_pago = entry_fecha_pago.get_date()

            conn = conexion_db()
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    UPDATE pagos 
                    SET monto = ?, fecha_pago = ? 
                    WHERE cedula = ? AND membresia_id = (SELECT membresia_id FROM usuarios WHERE cedula = ?)
                """, (monto, fecha_pago, cedula, cedula))
                conn.commit()

                # Actualizar el estado de pago después de la edición
                nuevo_estado_pago = obtener_estado_pago(cedula)
                messagebox.showinfo("Éxito", f"Pago actualizado correctamente. Estado de pago: {nuevo_estado_pago}")
                ventana_editar.destroy()
                cargar_datos_usuarios()  # Recargar los pagos después de la actualización
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo actualizar el pago: {e}")
            finally:
                conn.close()

        # Botones dentro de la ventana de edición
        frame_botones = Frame(ventana_editar, bg="#272643", pady=10)
        frame_botones.pack(fill="x", side="bottom")

        btn_guardar = Button(frame_botones, text="Guardar", font=("Segoe UI", 12), bg="#bae8e8", command=actualizar_pago)
        btn_guardar.pack(side="left", padx=10)

        btn_regresar = Button(frame_botones, text="Cerrar", font=("Segoe UI", 12), bg="#bae8e8", command=ventana_editar.destroy)
        btn_regresar.pack(side="right", padx=10)

    def eliminar_pago():
        """Elimina un pago seleccionado de la base de datos y actualiza el estado de pago a 'No paga' si es necesario."""
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un pago para eliminar")
            return

        item = tabla.item(seleccionado[0])
        pago_id = item['values'][0]
        cedula = item['values'][1]  # La cédula está en la segunda columna

        respuesta = messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de eliminar el pago de la cédula {cedula}?")
        if not respuesta:
            return

        conn = conexion_db()
        cursor = conn.cursor()
        try:
            # Eliminar el pago seleccionado
            cursor.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))
            conn.commit()

            # Verificar si el usuario tiene otros pagos registrados
            cursor.execute("SELECT COUNT(*) FROM pagos WHERE cedula = ?", (cedula,))
            count_pagos = cursor.fetchone()[0]

            # Si no hay más pagos, el estado de pago se considera "No paga"
            if count_pagos == 0:
                messagebox.showinfo("Éxito", f"Pago eliminado correctamente. Estado de pago: No paga")
            else:
                messagebox.showinfo("Éxito", f"Pago eliminado correctamente. El usuario aún tiene otros pagos registrados.")

            cargar_datos_usuarios()  # Recargar la lista de pagos
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el pago: {e}")
        finally:
            conn.close()

    def registrar_pago():
        """Registra el pago de un usuario."""
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un usuario para registrar pago")
            return

        item = tabla.item(seleccionado[0])
        cedula, nombre, membresia, monto, pago = item["values"]

        # Obtener el estado del pago usando el método obtener_estado_pago(cedula)
        estado_pago = obtener_estado_pago(cedula)

        if estado_pago == "Pagado":  # Si el estado es 'Realizado', ya ha pagado
            messagebox.showinfo("Información", "Este usuario ya realizó un pago.")
            return

        # Confirmar si se desea registrar el pago
        respuesta = messagebox.askyesno("Registrar Pago", f"{nombre} debe pagar ${monto}. ¿Desea confirmar el pago?")
        if respuesta:
            conn = conexion_db()
            if not conn:
                messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
                return

            cursor = conn.cursor()
            try:
                # Obtener el ID de membresía a partir del nombre de la membresía
                cursor.execute("SELECT id FROM membresias WHERE nombre = ?", (membresia,))
                resultado = cursor.fetchone()
                if not resultado:
                    messagebox.showerror("Error", "Membresía no encontrada.")
                    return

                membresia_id = resultado[0]

                # Crear ventana emergente para confirmar y registrar el pago
                ventana_pago = tk.Toplevel(ventana)
                ventana_pago.title("Confirmación de Pago")
                ventana_pago.geometry("400x300")
                ventana_pago.configure(bg="#272643")

                # Frame para los controles de la ventana
                frame_pago = Frame(ventana_pago, bg="#272643", padx=20, pady=20)
                frame_pago.pack(fill="both", expand=True)

                # Etiquetas para mostrar los detalles del pago
                Label(frame_pago, text=f"Usuario: {nombre}", font=("Segoe UI", 14), fg="white", bg="#272643").pack(pady=10)
                Label(frame_pago, text=f"Membresía: {membresia}", font=("Segoe UI", 14), fg="white", bg="#272643").pack(pady=10)
                Label(frame_pago, text=f"Monto a Pagar: ${monto}", font=("Segoe UI", 14), fg="white", bg="#272643").pack(pady=10)

                # Función para guardar el pago
                def guardar_pago():
                    """Guarda el pago en la base de datos."""
                    fecha_pago = datetime.now().strftime('%Y-%m-%d')

                    try:
                        # Registrar el pago en la base de datos
                        cursor.execute("INSERT INTO pagos (cedula, membresia_id, monto, fecha_pago) VALUES (?, ?, ?, ?)",
                                    (cedula, membresia_id, monto, fecha_pago))
                        conn.commit()

                        messagebox.showinfo("Éxito", "Pago registrado correctamente")
                        ventana_pago.destroy()
                        cargar_datos_usuarios()  # Actualiza la tabla de pagos
                    except sqlite3.Error as e:
                        messagebox.showerror("Error", f"No se pudo registrar el pago: {e}")
                    finally:
                        # Asegúrate de cerrar el cursor y la conexión solo después de que todo se haya realizado
                        cursor.close()
                        conn.close()

                # Botón para guardar el pago
                btn_guardar = Button(frame_pago, text="Guardar", font=("Segoe UI", 12), bg="#bae8e8", command=guardar_pago)
                btn_guardar.pack(pady=10)

                # Botón para regresar
                btn_regresar = Button(frame_pago, text="Regresar", font=("Segoe UI", 12), bg="#f19c42", fg="white", command=ventana_pago.destroy)
                btn_regresar.pack(pady=10)

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo procesar el pago: {e}")
            finally:
                # Cerramos el cursor y la conexión solo después de que el pago ha sido procesado
                if not cursor.closed:
                    cursor.close()
                if conn:
                    conn.close()  # Asegúrate de cerrar la conexión

    def obtener_estado_pago(cedula):
        """Obtiene el estado de pago de un usuario."""
        conn = conexion_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                CASE
                    WHEN p.fecha_pago IS NOT NULL THEN 'Pagado'
                    ELSE 'No Paga'
                END AS estado_pago
            FROM 
                usuarios u
            LEFT JOIN 
                pagos p ON u.cedula = p.cedula
            WHERE u.cedula = ?
        """, (cedula,))
        estado_pago = cursor.fetchone()
        conn.close()
        if estado_pago:
            return estado_pago[0]
        return 'No Paga'

    def emitir_factura():
        """Genera un archivo PDF con la factura del pago."""
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un usuario con pago realizado para emitir factura")
            return

        item = tabla.item(seleccionado[0])
        cedula, nombre, membresia, monto, pago = item["values"]

        if pago == "No paga":
            messagebox.showerror("Error", "Este usuario no ha realizado un pago")
            return

        # Asegúrate de convertir 'monto' a float para evitar el error de tipo
        try:
            monto = float(monto)
        except ValueError:
            messagebox.showerror("Error", "El monto es inválido.")
            return

        # Generar la factura en PDF
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        nombre_archivo = f"factura_{cedula}_{fecha_actual}.pdf"

        # Calcular IVA y total
        iva = round(monto * 0.12, 2)
        total = round(monto + iva, 2)

        # Crear el PDF
        c = canvas.Canvas(nombre_archivo)
        c.drawString(100, 750, f"Factura para: {nombre}")
        c.drawString(100, 730, f"Cédula: {cedula}")
        c.drawString(100, 710, f"Membresía: {membresia}")
        c.drawString(100, 690, f"Monto: ${monto:.2f}")
        c.drawString(100, 670, f"IVA (12%): ${iva:.2f}")
        c.drawString(100, 650, f"Total a pagar: ${total:.2f}")
        c.drawString(100, 600, f"Fecha de emisión: {fecha_actual}")
        c.save()

        # Actualizar el estado de la factura en la base de datos
        conn = conexion_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.id
                FROM pagos p
                WHERE p.cedula = ? AND p.fecha_pago IS NOT NULL
            """, (cedula,))
            pago_id = cursor.fetchone()
            if pago_id:
                pago_id = pago_id[0]
                cursor.execute("INSERT INTO facturas (pago_id, fecha_emision) VALUES (?, ?)", (pago_id, fecha_actual))
                conn.commit()

            messagebox.showinfo("Factura Generada", f"Factura guardada como {nombre_archivo}")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"No se pudo generar la factura: {str(e)}")
        finally:
            conn.close()

    def ver_historial_pagos():
        """Muestra el historial de pagos de un usuario seleccionado."""
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccione un usuario para ver el historial de pagos")
            return

        item = tabla.item(seleccionado[0])
        cedula_usuario = item['values'][0]

        ventana_historial = tk.Toplevel()
        ventana_historial.title("Historial de Pagos")
        ventana_historial.geometry("600x400")
        ventana_historial.configure(bg="#272643")

        frame_tabla = Frame(ventana_historial, bg="#272643")
        frame_tabla.pack(expand=True, fill="both", padx=20, pady=10)

        columnas = ("ID", "Membresía", "Monto", "Fecha de Pago")
        tabla_historial = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

        for col in columnas:
            tabla_historial.heading(col, text=col.capitalize())
            tabla_historial.column(col, width=150, anchor="center")

        tabla_historial.pack(expand=True, fill="both", padx=10, pady=10)

        # Consulta los pagos del usuario seleccionado
        conn = conexion_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, membresia_id, monto, fecha_pago
                FROM pagos 
                WHERE cedula = ?
            """, (cedula_usuario,))
            pagos = cursor.fetchall()

            if not pagos:  # Si no hay pagos, mostramos un mensaje
                messagebox.showinfo("Información", "Este usuario no tiene pagos registrados.")
            else:
                for pago in pagos:
                    tabla_historial.insert("", "end", values=pago)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener los pagos: {e}")
        finally:
            conn.close()

        # Botón para cerrar
        btn_cerrar = Button(ventana_historial, text="Cerrar", font=("Segoe UI", 12), bg="#bae8e8", command=ventana_historial.destroy)
        btn_cerrar.pack(pady=10)

    cargar_datos_usuarios()
    ventana.mainloop()


def regresar(callback, ventana):
    ventana.destroy()
    callback()
