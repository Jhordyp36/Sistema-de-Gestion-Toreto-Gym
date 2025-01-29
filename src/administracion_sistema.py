import os
import sqlite3
import tkinter as tk
from tkinter import Button, Frame, Label, Entry, Tk, ttk, messagebox
from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono

def conexion_bd():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None    

def cargar_administracion_usuarios():
    print("Hola")

def cargar_administracion_parametros():
    print("Hola")

def cargar_auditoria():
    print("Hola")

def regresar():
    print("Hola")
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
    
    # Botones de navegación
    btn_administracion_usuarios = tk.Button(frame_botones_principales, text="Administración de Usuarios", font=("Segoe UI", 14), bg="#bae8e8", command=cargar_administracion_usuarios)
    btn_administracion_usuarios.pack(side="left", padx=10)

    btn_administracion_parametros = tk.Button(frame_botones_principales, text="Administración de Parámetros", font=("Segoe UI", 14), bg="#bae8e8", command=cargar_administracion_parametros)
    btn_administracion_parametros.pack(side="left", padx=10)
    
    btn_auditoria = tk.Button(frame_botones_principales, text="Auditoría", font=("Segoe UI", 14), bg="#bae8e8", command=cargar_auditoria)
    btn_auditoria.pack(side="left", padx=10)
    
    btn_regresar = tk.Button(frame_botones_principales, text="Regresar", font=("Segoe UI", 14), bg="#bae8e8", command=regresar)
    btn_regresar.pack(side="right", padx=10)

    
    ventana.mainloop()