import sqlite3
import os

if not os.path.exists('data'):
    os.makedirs('data')

conn = sqlite3.connect('data/toretogym.db')
cursor = conn.cursor()

# Tabla usuarios
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        cedula TEXT PRIMARY KEY CHECK(length(cedula) = 10),
        apellidos TEXT NOT NULL,
        nombres TEXT NOT NULL,
        usuario TEXT UNIQUE,
        contrasena TEXT,
        telefono TEXT NOT NULL CHECK(length(telefono) = 10),
        correo TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('Cliente', 'Administrador', 'Entrenador')),
        estado TEXT NOT NULL DEFAULT 'A' CHECK(estado IN ('A', 'X')),
        fecha_nacimiento TEXT NOT NULL,
        membresia_id INTEGER,
        fecha_registro TEXT,
        FOREIGN KEY (membresia_id) REFERENCES membresias(id)
    )
''')

# Tabla Membresías
cursor.execute('''
    CREATE TABLE IF NOT EXISTS membresias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        duracion_dias INTEGER NOT NULL,
        estado TEXT NOT NULL DEFAULT 'Activo' CHECK(estado IN ('Activo', 'Inactivo'))
    )
''')

# Tabla Categorías de Equipos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias_equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    )
''')

# Tabla Equipos del Gimnasio
cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        categoria_id INTEGER NOT NULL,
        estado TEXT NOT NULL CHECK(estado IN ('Disponible', 'Mantenimiento')),
        FOREIGN KEY (categoria_id) REFERENCES categorias_equipos(id)
    )
''')

# Tabla Clases
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT,
        duracion_minutos INTEGER NOT NULL
    )
''')

# Tabla Servicios
cursor.execute('''
    CREATE TABLE IF NOT EXISTS servicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        disponible TEXT NOT NULL CHECK(disponible IN ('Si', 'No')),
        clase_id INTEGER,
        dia TEXT,
        hora TEXT,
        lugar TEXT,
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    )
''')

# Tabla Membresía - Servicios
cursor.execute('''
    CREATE TABLE IF NOT EXISTS membresias_servicios (
        membresia_id INTEGER,
        servicio_id INTEGER,
        PRIMARY KEY (membresia_id, servicio_id),
        FOREIGN KEY (membresia_id) REFERENCES membresias(id),
        FOREIGN KEY (servicio_id) REFERENCES servicios(id)
    )
''')

# Tabla Historial de Asistencias
cursor.execute('''
    CREATE TABLE IF NOT EXISTS historial_asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT NOT NULL,
        fecha TEXT NOT NULL,
        asistencia TEXT NOT NULL CHECK(asistencia IN ('Si', 'No')),
        descripcion TEXT NOT NULL,
        FOREIGN KEY (cedula) REFERENCES usuarios(cedula)
    )
''')

# Tabla Historial de uso de equipos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS historial_uso_equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT NOT NULL,
        equipo_id INTEGER NOT NULL,
        fecha_uso TEXT NOT NULL,
        FOREIGN KEY (cedula) REFERENCES usuarios(cedula),
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
    )
''')

# Tabla de Pagos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pagos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cedula TEXT NOT NULL,
        membresia_id INTEGER NOT NULL,
        monto REAL NOT NULL,
        fecha_pago TEXT NOT NULL,
        FOREIGN KEY (cedula) REFERENCES usuarios(cedula),
        FOREIGN KEY (membresia_id) REFERENCES membresias(id)
    )
''')

# Tabla de Facturación
cursor.execute('''
    CREATE TABLE IF NOT EXISTS facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pago_id INTEGER NOT NULL,
        fecha_emision TEXT NOT NULL,
        FOREIGN KEY (pago_id) REFERENCES pagos(id)
    )
''')

# Tabla de logs
cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        fecha_hora TEXT NOT NULL,
        accion TEXT NOT NULL
    )
''')

# Categorías de equipos de ejemplo
cursor.execute('''
    INSERT OR IGNORE INTO categorias_equipos (nombre)
    VALUES ('Cardio'), ('Pesas libres'), ('Máquinas de fuerza')
''')

# Clases de ejemplo
cursor.execute('''
    INSERT OR IGNORE INTO clases (nombre, descripcion, duracion_minutos)
    VALUES ('Yoga', 'Clase de relajación y estiramientos', 60),
           ('Spinning', 'Ejercicio cardiovascular en bicicleta estática', 45)
''')


cursor.execute('''
    INSERT OR IGNORE INTO usuarios (cedula, apellidos, nombres, usuario, contrasena, telefono, correo, rol, estado, fecha_nacimiento)
    VALUES ('1234567890', 'Pagual Pisco', 'Christian Jonathan', 'admin', '1234', '0912345678', 'admin@gmail.com', 'Administrador', 'A', '2000-01-01')
''')


conn.commit()
conn.close()
