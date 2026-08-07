from src.conexion import obtener_conexion
from datetime import date

def crear_usuario(
    nombre,
    nombre_usuario,
    correo,
    clave,
    fecha_nacimiento
):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    INSERT INTO Usuario
    (
        nombre,
        nombre_usuario,
        correo,
        clave,
        fecha_nacimiento,
        foto_perfil,
        biografia,
        cuenta_verificada,
        estado,
        fecha_registro
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    valores = (
        nombre,
        nombre_usuario,
        correo,
        clave,
        fecha_nacimiento,
        None,               # foto_perfil
        None,               # biografia
        False,              # cuenta_verificada
        "Activo",           # estado
        date.today()        # fecha_registro
    )

    cursor.execute(consulta, valores)

    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas > 0


def listar_usuarios():

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    consulta = """
    SELECT
        id_usuario,
        nombre,
        nombre_usuario,
        correo
    FROM Usuario
    ORDER BY id_usuario;
    """

    cursor.execute(consulta)

    usuarios = cursor.fetchall()

    cursor.close()
    conexion.close()

    return usuarios

def buscar_usuario_por_id(id_usuario):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Usuario
        WHERE id_usuario = %s
    """

    cursor.execute(sql, (id_usuario,))

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario

def buscar_usuario_por_nombre(nombre_usuario):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Usuario
        WHERE nombre_usuario = %s
    """

    cursor.execute(sql, (nombre_usuario,))

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario

def actualizar_usuario(id_usuario, nombre, biografia):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        UPDATE Usuario
        SET nombre = %s,
            biografia = %s
        WHERE id_usuario = %s
    """

    cursor.execute(sql, (nombre, biografia, id_usuario))

    conexion.commit()

    actualizado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return actualizado

def eliminar_usuario(id_usuario):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        UPDATE Usuario
        SET estado = 'Eliminado'
        WHERE id_usuario = %s
    """

    cursor.execute(sql, (id_usuario,))

    conexion.commit()

    eliminado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return eliminado

def buscar_usuario_por_correo(correo):

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Usuario
        WHERE correo = %s
    """

    cursor.execute(sql, (correo,))

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario

def iniciar_sesion(correo, clave):

    usuario = buscar_usuario_por_correo(correo)

    if usuario is None:

        return False

    if usuario["clave"] != clave:

        return False

    return usuario

