import sqlite3
import os

if not os.path.exists('data'):
    os.makedirs('data')

conn = sqlite3.connect('data/toretogym.db')
cursor = conn.cursor()

# # Borrar tabla membresias_servicios
# cursor.execute('DROP TABLE IF EXISTS membresias_servicios')

# # Borrar tabla servicios
# cursor.execute('DROP TABLE IF EXISTS servicios')

# # Borrar tabla clases
# cursor.execute('DROP TABLE IF EXISTS clases')

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
        nombre TEXT NOT NULL UNIQUE,
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


# Crear la nueva tabla con la restricción corregida
cursor.execute('''
    CREATE TABLE equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        categoria_id INTEGER NOT NULL,
        estado TEXT NOT NULL CHECK(estado IN ('Disponible', 'No Disponible', 'X')),
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
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT,
        disponible TEXT NOT NULL CHECK(disponible IN ('Si', 'No')),
        clase_id INTEGER,
        equipo_id INTEGER,
        dia TEXT,
        hora TEXT,
        lugar TEXT,
        FOREIGN KEY (clase_id) REFERENCES clases(id)
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
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
           ('Spinning', 'Ejercicio cardiovascular en bicicleta estática', 45),
            ('Entrenamiento Funcional', 'Entrenamiento físico que combina ejercicios de fuerza, resistencia y agilidad', 45),
            ('Aeróbicos', 'Clase grupal de ejercicios aeróbicos para mejorar la resistencia cardiovascular', 40),
            ('Estiramientos', 'Clase de estiramientos para mejorar la flexibilidad', 30),
            ('Zumba', 'Clase de baile aeróbico con música latina para mejorar la resistencia', 45),
            ('Calistenia', 'Ejercicio físico que utiliza el peso corporal como resistencia', 40),
            ('Circuito', 'Entrenamiento en circuito, alternando entre diferentes estaciones de ejercicio', 50)
''')


cursor.execute('''
    INSERT OR IGNORE INTO usuarios (cedula, apellidos, nombres, usuario, contrasena, telefono, correo, rol, estado, fecha_nacimiento)
    VALUES ('1234567890', 'Pagual Pisco', 'Christian Jonathan', 'admin', '1234', '0912345678', 'admin@gmail.com', 'Administrador', 'A', '01-01-2001')
''')

cursor.execute('''
    INSERT OR IGNORE INTO membresias (nombre, precio, duracion_dias)
    VALUES ('Pase Diario', 1.50, 1),
           ('Estándar', 2.00, 7),
           ('Premium', 4.00, 20),
           ('VIP', 7.00, 30)
''')


# Relacionar las membresías con los servicios correspondientes
cursor.execute('''
    INSERT OR IGNORE INTO membresias_servicios (membresia_id, servicio_id)
    VALUES
        -- Pase Diario solo tiene acceso a algunas máquinas
        (1, 9),  -- Uso de Bicicleta Estática (id = 9)
        (1, 10), -- Uso de Cinta de Correr (id = 10)
        
        -- Pase Estándar tiene acceso a todas las máquinas pero no a clases
        (2, 9),  -- Uso de Bicicleta Estática (id = 9)
        (2, 10), -- Uso de Cinta de Correr (id = 10)
        (2, 11), -- Uso de Banco de Pesas (id = 11)
        (2, 12), -- Uso de Pesas de mano (id = 12)
        (2, 13), -- Uso de Máquina de Pecho (id = 13)
        (2, 14), -- Uso de Máquina de Piernas (id = 14)
        
        -- Membresía Premium tiene acceso a máquinas y algunas clases básicas
        (3, 3),  -- Entrenamiento Funcional (id = 3)
        (3, 4),  -- Aeróbicos (id = 4)
        (3, 5),  -- Estiramientos (id = 5)
        (3, 9),  -- Uso de Bicicleta Estática (id = 9)
        (3, 10), -- Uso de Cinta de Correr (id = 10)
        (3, 11), -- Uso de Banco de Pesas (id = 11)
        (3, 12), -- Uso de Pesas de mano (id = 12)
        (3, 13), -- Uso de Máquina de Pecho (id = 13)
        (3, 14), -- Uso de Máquina de Piernas (id = 14)
        
        -- Membresía VIP tiene acceso a todas las máquinas y todas las clases, más acceso exclusivo
        (4, 1),  -- Entrenamiento Funcional (id = 3)
        (4, 2),  -- Entrenamiento Funcional (id = 3)
        (4, 3),  -- Entrenamiento Funcional (id = 3)
        (4, 4),  -- Aeróbicos (id = 4)
        (4, 5),  -- Estiramientos (id = 5)
        (4, 6),  -- Zumba (id = 6)
        (4, 7),  -- Calistenia (id = 7)
        (4, 8),   -- Circuito (id = 8)
        (4, 9),  -- Uso de Bicicleta Estática (id = 9)
        (4, 10), -- Uso de Cinta de Correr (id = 10)
        (4, 11), -- Uso de Banco de Pesas (id = 11)
        (4, 12), -- Uso de Pesas de mano (id = 12)
        (4, 13), -- Uso de Máquina de Pecho (id = 13)
        (4, 14) -- Uso de Máquina de Piernas (id = 14)
''')

# Insertar equipos básicos en las categorías existentes
cursor.execute('''
    INSERT OR IGNORE INTO equipos (nombre, categoria_id, estado)
    VALUES 
        ('Bicicleta Estática', (SELECT id FROM categorias_equipos WHERE nombre = 'Cardio'), 'Disponible'),
        ('Cinta de Correr', (SELECT id FROM categorias_equipos WHERE nombre = 'Cardio'), 'Disponible'),
        ('Banco de Pesas', (SELECT id FROM categorias_equipos WHERE nombre = 'Pesas libres'), 'Disponible'),
        ('Pesas de mano', (SELECT id FROM categorias_equipos WHERE nombre = 'Pesas libres'), 'Disponible'),
        ('Máquina de Pecho', (SELECT id FROM categorias_equipos WHERE nombre = 'Máquinas de fuerza'), 'Disponible'),
        ('Máquina de Piernas', (SELECT id FROM categorias_equipos WHERE nombre = 'Máquinas de fuerza'), 'Disponible')
''')

# Insertar servicios (Clases y Equipos)
cursor.execute('''
    INSERT OR IGNORE INTO servicios (nombre, descripcion, disponible, clase_id, equipo_id, dia, hora, lugar)
    VALUES
        -- Servicios relacionados con clases
        ('Clase de Yoga', 'Clase grupal de relajación y estiramiento', 'Si', (SELECT id FROM clases WHERE nombre = 'Yoga'), NULL, 'Lunes', '08:00', 'Sala A'),
        ('Clase de Spinning', 'Ejercicio cardiovascular en bicicleta estática', 'Si', (SELECT id FROM clases WHERE nombre = 'Spinning'), NULL, 'Miércoles', '09:00', 'Sala B'),
        ('Entrenamiento Funcional', 'Entrenamiento físico que combina ejercicios de fuerza, resistencia y agilidad', 'Si', (SELECT id FROM clases WHERE nombre = 'Entrenamiento Funcional'), NULL, 'Martes', '10:00', 'Sala A'),
        ('Aeróbicos', 'Clase grupal de ejercicios aeróbicos para mejorar la resistencia cardiovascular', 'Si', (SELECT id FROM clases WHERE nombre = 'Aeróbicos'), NULL, 'Jueves', '10:00', 'Sala A'),
        ('Estiramientos', 'Clase de estiramientos para mejorar la flexibilidad', 'Si', (SELECT id FROM clases WHERE nombre = 'Estiramientos'), NULL, 'Lunes', '07:00', 'Sala A'),
        ('Zumba', 'Clase de baile aeróbico con música latina para mejorar la resistencia', 'Si', (SELECT id FROM clases WHERE nombre = 'Zumba'), NULL, 'Viernes', '08:00', 'Sala A'),
        ('Calistenia', 'Ejercicio físico que utiliza el peso corporal como resistencia', 'Si', (SELECT id FROM clases WHERE nombre = 'Calistenia'), NULL, 'Miércoles', '07:00', 'Sala B'),
        ('Circuito', 'Entrenamiento en circuito, alternando entre diferentes estaciones de ejercicio', 'Si', (SELECT id FROM clases WHERE nombre = 'Circuito'), NULL, 'Sábado', '09:00', 'Sala B'),
        
        -- Servicios relacionados con equipos
        ('Uso de Bicicleta Estática', 'Servicio para uso de bicicleta estática', 'Si', NULL, (SELECT id FROM equipos WHERE nombre = 'Bicicleta Estática'), NULL, NULL, 'Gimnasio'),
        ('Uso de Cinta de Correr', 'Servicio para uso de cinta de correr', 'Si', NULL, (SELECT id FROM equipos WHERE nombre = 'Cinta de Correr'), NULL, NULL, 'Gimnasio'),
        ('Uso de Banco de Pesas', 'Servicio para uso de banco de pesas', 'Si', NULL, (SELECT id FROM equipos WHERE nombre = 'Banco de Pesas'), NULL, NULL, 'Área de Pesas'),
        ('Uso de Pesas de mano', 'Servicio para uso de pesas de mano', 'Si', NULL, (SELECT id FROM equipos WHERE nombre = 'Pesas de mano'), NULL, NULL, 'Área de Pesas'),
        ('Uso de Máquina de Pecho', 'Servicio para uso de máquina de pecho', 'Si', NULL, (SELECT id FROM equipos WHERE nombre = 'Máquina de Pecho'), NULL, NULL, 'Área de Fuerza'),
        ('Uso de Máquina de Piernas', 'Servicio para uso de máquina de piernas', 'Si', NULL, (SELECT id FROM equipos WHERE nombre = 'Máquina de Piernas'), NULL, NULL, 'Área de Fuerza')
''')

cursor.execute(''' 
    INSERT or IGNORE INTO usuarios (cedula, apellidos, nombres, telefono, correo, rol, estado, fecha_nacimiento, fecha_registro) 
    VALUES
        ('0954632781', 'López Andrade', 'Carlos Andrés', '0987654321', 'carlos.lopez@mail.com', 'Cliente', 'A', '15-08-2004', '29-01-2025 16:10:45'),
        ('1765432987', 'Castillo Romero', 'Andrea Fernanda', '0987123456', 'andrea.castillo@mail.com', 'Cliente', 'A', '20-02-2003', '29-01-2025 16:12:30'),
        ('1785643201', 'Benítez Montalvo', 'David Sebastián', '0987543210', 'david.benitez@mail.com', 'Cliente', 'A', '05-06-2001', '29-01-2025 16:15:12'),
        ('1723456789', 'Mendoza Salazar', 'Sofía Gabriela', '0978123456', 'sofia.mendoza@mail.com', 'Cliente', 'A', '12-12-2000', '29-01-2025 16:18:54'),
        ('1809876543', 'Narváez Suárez', 'Fernando Ricardo', '0967452310', 'fernando.narvaez@mail.com', 'Cliente', 'A', '03-05-2005', '29-01-2025 16:22:01'),

        ('1798765432', 'Chávez Ortega', 'Jorge Luis', '0956348721', 'jorge.chavez@mail.com', 'Entrenador', 'A', '22-03-1995', '29-01-2025 16:30:15'),
        ('1897654321', 'Reyes Cevallos', 'Marcelo Esteban', '0945632187', 'marcelo.reyes@mail.com', 'Entrenador', 'A', '17-07-1992', '29-01-2025 16:35:27'),
        ('1923456789', 'Zambrano Torres', 'Patricia Elena', '0978432165', 'patricia.zambrano@mail.com', 'Entrenador', 'A', '09-09-1998', '29-01-2025 16:40:33'),
        ('1854321765', 'Figueroa Ayala', 'Luis Daniel', '0954321678', 'luis.figueroa@mail.com', 'Entrenador', 'A', '14-01-1990', '29-01-2025 16:45:49'),
        ('1745612398', 'Galarza Espinoza', 'Carolina Beatriz', '0986712345', 'carolina.galarza@mail.com', 'Entrenador', 'A', '08-11-1996', '29-01-2025 16:50:20');
''')

# cursor.execute(''' 
#     INSERT INTO logs (usuario, fecha_hora, accion) 
#     VALUES
#         ('admin', '29-01-2025 16:10:45', 'Creación usuario: 0954632781'),
#         ('admin', '29-01-2025 16:12:30', 'Creación usuario: 1765432987'),
#         ('admin', '29-01-2025 16:15:12', 'Creación usuario: 1785643201'),
#         ('admin', '29-01-2025 16:18:54', 'Creación usuario: 1723456789'),
#         ('admin', '29-01-2025 16:22:01', 'Creación usuario: 1809876543'),
#         ('admin', '29-01-2025 16:30:15', 'Creación usuario: 1798765432'),
#         ('admin', '29-01-2025 16:35:27', 'Creación usuario: 1897654321'),
#         ('admin', '29-01-2025 16:40:33', 'Creación usuario: 1923456789'),
#         ('admin', '29-01-2025 16:45:49', 'Creación usuario: 1854321765'),
#         ('admin', '29-01-2025 16:50:20', 'Creación usuario: 1745612398');
# ''')
conn.commit()

conn.close()
