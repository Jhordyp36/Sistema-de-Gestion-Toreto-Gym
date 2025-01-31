# Sistema de Gestión de Servicios - Toreto Gym

## 📌 Descripción
El módulo `servicios.py` forma parte del **Sistema de Gestión de Reservas Toreto Gym**. Proporciona una interfaz gráfica para administrar los servicios disponibles en el gimnasio, permitiendo realizar operaciones **CRUD** (Crear, Leer, Actualizar, Eliminar) sobre la tabla `servicios` de la base de datos SQLite.

La interfaz ha sido desarrollada con **Tkinter**, y permite:
- Registrar nuevos servicios
- Consultar la lista de servicios
- Editar servicios existentes
- Regresar a la ventana principal del sistema

## 📂 Estructura del Código
El archivo `servicios.py` está organizado en las siguientes secciones:

1. **Importación de Módulos:**
   - Se importa **Tkinter** para la interfaz gráfica.
   - Se usa **sqlite3** para gestionar la base de datos.
   - Se cargan configuraciones desde `config.py`.
   - Se usa `helpers.py` para cargar íconos en la interfaz.

2. **Función `conexion_db()`**:
   - Establece una conexión con la base de datos SQLite.
   - Retorna la conexión activa para ser utilizada en consultas SQL.

3. **Clase `GestionServicios`**:
   - Crea la interfaz gráfica de gestión de servicios.
   - Maneja las operaciones CRUD.
   - Permite regresar a la ventana principal.

---

## 🔍 Funcionamiento de `servicios.py`

### 🖥️ **Inicialización de la Interfaz**
La clase `GestionServicios` gestiona toda la ventana gráfica.

```python
class GestionServicios:
    def __init__(self, root, callback_regreso=None):
        self.root = root
        self.root.title("Gestión de Servicios")
        self.root.state("zoomed")  # Modo pantalla completa
        self.root.configure(bg="#272643")
        cargar_icono(self.root, ICONS_DIR)
        self.callback_regreso = callback_regreso  # Función para regresar
```

- `root`: Ventana principal de Tkinter.
- `callback_regreso`: Función que permite regresar a la ventana principal.


### 📋 **Configurar Interfaz (`configurar_interfaz`)**
```python
def configurar_interfaz(self):
    tk.Label(self.root, text="Gestión de Servicios", font=("Segoe UI", 14, "bold"), bg="#272643", fg="#bae8e8").pack(pady=20)
```
- Se crean los **campos de entrada** para Nombre, Descripción, Disponibilidad, Clase ID y Equipo ID.
- Se agrega un **Treeview (tabla)** para mostrar los servicios disponibles.
- Se incluyen botones para Registrar, Editar, Consultar y Regresar.


### 📝 **Registrar Servicio (`registrar_servicio`)**
```python
def registrar_servicio(self):
    conn = conexion_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO servicios (nombre, descripcion, disponible, clase_id, equipo_id) VALUES (?, ?, ?, ?, ?)", 
                   (self.var_nombre.get(), self.var_descripcion.get(), self.var_disponibilidad.get(), self.var_clase_id.get(), self.var_equipo_id.get()))
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Servicio registrado correctamente.")
    self.cargar_servicios()
    self.limpiar_campos()
```
- Obtiene los datos de los **campos de entrada**.
- Inserta el nuevo servicio en la base de datos.
- Actualiza la tabla para reflejar los cambios.


### 🔄 **Cargar Servicios (`cargar_servicios`)**
```python
def cargar_servicios(self):
    conn = conexion_db()
    self.tree.delete(*self.tree.get_children())
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM servicios")
    for fila in cursor.fetchall():
        self.tree.insert("", "end", values=fila)
    conn.close()
```
- Consulta los servicios en la base de datos.
- Borra los datos previos en la tabla.
- Inserta los registros actualizados en la interfaz.


### ✏ **Editar Servicio (`editar_servicio`)**
```python
def editar_servicio(self):
    seleccion = self.tree.selection()
    if not seleccion:
        messagebox.showerror("Error", "Seleccione un servicio para editar.")
        return
    id_seleccionado = self.tree.item(seleccion, "values")[0]
    conn = conexion_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE servicios SET nombre=?, descripcion=?, disponible=?, clase_id=?, equipo_id=? WHERE id=?", 
                   (self.var_nombre.get(), self.var_descripcion.get(), self.var_disponibilidad.get(), self.var_clase_id.get(), self.var_equipo_id.get(), id_seleccionado))
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Servicio actualizado correctamente.")
    self.cargar_servicios()
    self.limpiar_campos()
```
- Permite seleccionar un servicio y actualizarlo.
- Llama a `cargar_servicios` para refrescar la tabla.


### ⬅ **Regresar a la Ventana Principal (`regresar`)**
```python
def regresar(self):
    if self.callback_regreso:
        self.root.destroy()
        self.callback_regreso()
```
- Cierra la ventana actual y llama a `callback_regreso` para volver a la principal.

---

## 🛠 **Cómo Ejecutar `servicios.py`**
1. Asegúrate de tener **Python 3.10+** instalado.
2. Instala las dependencias:
```bash
pip install -r requirements.txt
```
3. Ejecuta el sistema desde `main.py`:
```bash
python main.py
```

---

## 🎯 **Conclusión**
El archivo `servicios.py` proporciona una interfaz eficiente para gestionar los servicios del gimnasio. Con **una UI intuitiva y funciones CRUD**, permite registrar, editar y consultar servicios en la base de datos. 🚀