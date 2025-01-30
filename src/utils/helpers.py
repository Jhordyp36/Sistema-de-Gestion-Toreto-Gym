import re
import os

# Verificar nombres y apellidos
def verifica_nombres_apellidos(cadena):
    if not cadena or len(cadena.strip()) > 60:
        return False
    return bool(re.fullmatch(r"[A-Za-záéíóúÁÉÍÓÚñÑ]+( [A-Za-záéíóúÁÉÍÓÚñÑ]+)?", cadena.strip()))

# Verificar nombre de usuario
def verifica_usuario(usuario):
    if not usuario or not (5 <= len(usuario) <= 15):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9]+", usuario.strip()))

# Verificar contraseña
def verifica_contrasena(contrasena):
    if not contrasena or not (8 <= len(contrasena) <= 20):
        return False
    return bool(re.search(r"[A-Z]", contrasena) and 
                re.search(r"[a-z]", contrasena) and 
                re.search(r"\d", contrasena) and 
                re.search(r"[!@#$%^&*]", contrasena))

# Verificar correo electrónico
def verifica_correo(correo):
    return bool(re.fullmatch(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", correo.strip()))

# Verificar número telefónico 
def verifica_telefono(telefono):
    return bool(re.fullmatch(r"\d{10}", telefono.strip()))

# Verificar fecha de nacimiento (formato DD/MM/AAAA y mayor de 16 años)
def verifica_fecha_nacimiento(fecha_nacimiento):
    try:
        from datetime import datetime, timedelta
        
        fecha = datetime.strptime(fecha_nacimiento.strip(), "%d-%m-%Y")
        edad_minima = datetime.now() - timedelta(days=16 * 365 + 4)
        return fecha <= edad_minima
    except ValueError:
        return False

# Función para centrar ventanas
def centrar_ventana(ventana, ancho, alto):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho - ancho) // 2
    y = (pantalla_alto - alto) // 2
    ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

# Función para cargar ícono
def cargar_icono(ventana, icono_path):
    if os.path.exists(icono_path):
        ventana.iconbitmap(icono_path)
    else:
        print(f"El icono {icono_path} no existe.")

def verifica_identificacion(identificacion):
    estado = False
    if len(identificacion) >= 10:
        valced = list(identificacion.strip())
        provincia = int(valced[0] + valced[1])

        if 0 < provincia < 31:  # Permitir cédulas emitidas en Consulados
            if int(valced[2]) < 6:
                estado = verifica_cedula(valced)
            elif int(valced[2]) == 6:
                if len(valced) == 13:
                    # Se agrega la validación de excluir de la validación de RUC, las identificaciones cuyo tercer dígito sea 6 o 9.
                    estado = True
                else:
                    # Permitir cédulas emitidas en Consulados
                    estado = verifica_cedula(valced)
            elif int(valced[2]) == 8:
                if len(valced) == 13:
                    estado = verifica_sector_publico(valced)
                else:
                    estado = False
            elif int(valced[2]) == 9:
                # Se agrega la validación de excluir de la validación de RUC, las identificaciones cuyo tercer dígito sea 6 o 9.
                estado = True

    return estado


def verifica_ruc_persona_natural(validar_cedula):
    try:
        establecimiento = "001"
        establecimiento_ruc = "".join(validar_cedula[10:13])
        return establecimiento_ruc == establecimiento and verifica_cedula(validar_cedula)
    except:
        return False


def verifica_cedula(validar_cedula):
    aux = 0
    par = 0
    impar = 0
    verifi = 0
    for i in range(0, 9, 2):
        aux = 2 * int(validar_cedula[i])
        if aux > 9:
            aux -= 9
        par += aux
    for i in range(1, 9, 2):
        impar += int(validar_cedula[i])

    aux = par + impar
    if aux % 10 != 0:
        verifi = 10 - (aux % 10)
    else:
        verifi = 0

    return verifi == int(validar_cedula[9])


def verifica_sector_publico(validar_cedula):
    aux = 0
    veri = sum(int(validar_cedula[i]) for i in range(9, 13))
    if veri > 0:
        coeficiente = [3, 2, 7, 6, 5, 4, 3, 2]

        for i in range(8):
            prod = int(validar_cedula[i]) * coeficiente[i]
            aux += prod

        if aux % 11 == 0:
            veri = 0
        elif aux % 11 == 1:
            return False
        else:
            aux = aux % 11
            veri = 11 - aux

        return veri == int(validar_cedula[8])

    return False

