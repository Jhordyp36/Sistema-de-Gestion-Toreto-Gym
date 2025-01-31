# 📌 **Explicación General del Código**
Este archivo implementa una **interfaz gráfica (GUI)** en Python usando **Tkinter** para gestionar los servicios de un sistema de gimnasio. Permite realizar operaciones **CRUD (Crear, Leer, Actualizar y Eliminar)** sobre la tabla `servicios` en una base de datos SQLite.

La funcionalidad principal del código es:
- **Conectarse a la base de datos SQLite**.
- **Mostrar los servicios** en una tabla.
- **Registrar nuevos servicios**.
- **Editar servicios existentes**.
- **Autocompletar los campos** al seleccionar un servicio.
- **Limpiar los campos** después de una acción.
- **Regresar a la ventana principal** cuando el usuario lo desee.

---

# 📌 **Explicación Detallada del Código**

## 📌 **Importación de Módulos**
```python
import sys
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
```
- `sys`, `os`: Se utilizan para **modificar la ruta del sistema** y poder importar módulos personalizados (como `config` y `helpers`).
- `sqlite3`: Biblioteca para interactuar con la base de datos SQLite.
- `tkinter`: Se usa para crear la **interfaz gráfica (GUI)**.
- `ttk`, `messagebox`: Componentes gráficos avanzados de **Tkinter** para mostrar mensajes y tablas.

---

## 📌 **Configuración de Importación de Módulos Personalizados**
```python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.config import DB_PATH, ICONS_DIR
from src.utils.helpers import cargar_icono
```
Este fragmento **modifica la ruta del sistema** para poder importar archivos de configuración que no están en la misma carpeta.  
- **`DB_PATH`**: Ruta de la base de datos SQLite.
- **`ICONS_DIR`**: Ruta de los iconos del sistema.
- **`cargar_icono(root, ICONS_DIR)`**: Función que asigna un ícono a la ventana principal.

---

## 📌 **Función de Conexión a la Base de Datos**
```python
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
```
- Intenta **establecer una conexión** con SQLite.
- **Retorna la conexión** si tiene éxito.
- Si falla, **imprime el error** y retorna `None`.

---

## 📌 **Clase `GestionServicios`**
Esta clase representa la interfaz y la lógica para gestionar los **servicios** en la base de datos.

### 📌 **Inicialización de la Clase**
```python
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
```
- **Crea la ventana** `root` y la configura con título y tamaño.
- **Carga el icono** usando `cargar_icono`.
- **Guarda la función `callback_regreso`**, que se ejecutará cuando el usuario presione "Regresar".

---

### 📌 **Definición de Variables**
```python
        self.var_id = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_descripcion = tk.StringVar()
        self.var_disponibilidad = tk.StringVar()
        self.var_clase_id = tk.StringVar()
        self.var_equipo_id = tk.StringVar()
```
- **Crea variables** que almacenarán los datos ingresados por el usuario.

---

### 📌 **Configuración de la Interfaz**
```python
        self.configurar_interfaz()
        self.cargar_servicios()
```
- **`configurar_interfaz()`**: Construye los elementos gráficos (botones, tablas, etc.).
- **`cargar_servicios()`**: Carga los servicios existentes desde la base de datos.

---

## 📌 **Creación de la Interfaz**
```python
def configurar_interfaz(self):
    """Configura la interfaz gráfica de usuario con Tkinter."""
```
- **Crea los elementos gráficos** como etiquetas, botones y la tabla de datos.

```python
    btn_registrar = tk.Button(frame_botones, text="Registrar Servicio", font=default_font, bg="#bae8e8", command=self.registrar_servicio)
```
- **Botón para registrar un servicio** ejecutando `registrar_servicio()`.

```python
    btn_regresar = tk.Button(frame_botones, text="Regresar", font=default_font, bg="#e3f6f5", command=self.regresar)
```
- **Botón para regresar** ejecutando `self.regresar()`.

---

## 📌 **Función `registrar_servicio`**
```python
def registrar_servicio(self):
    """Registra un nuevo servicio en la base de datos."""
```
- **Guarda un nuevo servicio en la base de datos**.

**Lógica:**
1. **Conectar a la base de datos**.
2. **Verificar que los campos obligatorios están llenos**.
3. **Insertar el nuevo servicio** en la tabla `servicios`.
4. **Actualizar la tabla** en la interfaz.
5. **Limpiar los campos**.

---

## 📌 **Función `cargar_servicios`**
```python
def cargar_servicios(self):
    """Carga los servicios desde la base de datos y los muestra en la tabla."""
```
- **Consulta todos los servicios** en la base de datos y los muestra en la tabla de la GUI.

---

## 📌 **Función `editar_servicio`**
```python
def editar_servicio(self):
    """Edita un servicio seleccionado en la tabla."""
```
- **Permite editar un servicio** ya existente.

**Lógica:**
1. **Verificar que se ha seleccionado un servicio** en la tabla.
2. **Obtener el ID del servicio seleccionado**.
3. **Actualizar los datos en la base de datos**.
4. **Refrescar la tabla** con los nuevos datos.

---

## 📌 **Función `autocompletar_campos`**
```python
def autocompletar_campos(self, event):
    """Autocompleta los campos del formulario cuando se selecciona un servicio en la tabla."""
```
- **Cuando el usuario selecciona un servicio en la tabla**, los datos se cargan en los cuadros de texto.

---

## 📌 **Función `limpiar_campos`**
```python
def limpiar_campos(self):
    """Limpia los cuadros de texto y deselecciona la fila en la tabla."""
```
- **Elimina el texto en los cuadros de entrada** y **deselecciona cualquier fila** en la tabla.

---

## 📌 **Función `regresar`**
```python
def regresar(self):
    """Cierra la ventana actual y regresa a la ventana principal."""
    if self.callback_regreso:
        self.root.destroy()
        self.callback_regreso()
```
- **Si existe una función de regreso (`callback_regreso`)**, la ejecuta.
- **Cierra la ventana** de servicios y regresa a la **ventana principal**.

---

## 📌 **Código de Ejecución Principal**
```python
if __name__ == "__main__":
    def regresar_a_principal():
        print("Regresando a la ventana principal")

    root = tk.Tk()
    app = GestionServicios(root, callback_regreso=regresar_a_principal)
    root.mainloop()
```
- **Ejecuta la aplicación** si el script se ejecuta directamente.
- **Crea la ventana `root`** y la pasa a `GestionServicios`.
- **Define la función `regresar_a_principal()`**, que se ejecuta al presionar "Regresar".

---

# 📌 **Conclusión**
Este código implementa un sistema completo para **gestionar servicios** en una base de datos SQLite con **interfaz gráfica (Tkinter)**.  
Si necesitas más explicaciones o ajustes, dime qué mejorar. 🚀