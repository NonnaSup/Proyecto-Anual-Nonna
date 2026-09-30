from src.conexion import obtener_conexion
from datetime import datetime


# ==================================================
# BUSCAR USUARIO GOOGLE POR UID FIREBASE
# ==================================================

def buscar_usuario_google_por_uid(firebase_uid):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM usuario_google
        WHERE firebase_uid = %s
    """

    cursor.execute(sql, (firebase_uid,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario


# ==================================================
# BUSCAR USUARIO GOOGLE POR CORREO
# ==================================================

def buscar_usuario_google_por_correo(correo):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM usuario_google
        WHERE correo = %s
    """

    cursor.execute(sql, (correo,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario


# ==================================================
# BUSCAR USUARIO NORMAL POR CORREO
# ==================================================

def buscar_usuario_normal_por_correo(correo):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Usuario
        WHERE correo = %s
          AND estado != 'Eliminado'
    """

    cursor.execute(sql, (correo,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario


# ==================================================
# CREAR USUARIO GOOGLE
# ==================================================

def crear_usuario_google(firebase_uid, nombre, correo, foto_perfil):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        INSERT INTO usuario_google
        (
            firebase_uid,
            nombre,
            correo,
            foto_perfil,
            fecha_registro,
            ultimo_inicio_sesion
        )
        VALUES
        (%s, %s, %s, %s, %s, %s)
    """

    fecha_actual = datetime.now()

    valores = (
        firebase_uid,
        nombre,
        correo,
        foto_perfil,
        fecha_actual,
        fecha_actual
    )

    cursor.execute(sql, valores)

    conexion.commit()

    id_usuario_google = cursor.lastrowid

    cursor.close()
    conexion.close()

    return id_usuario_google


# ==================================================
# ACTUALIZAR ÚLTIMO INICIO DE SESIÓN
# ==================================================

def actualizar_ultimo_inicio_sesion_google(firebase_uid):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        UPDATE usuario_google
        SET ultimo_inicio_sesion = %s
        WHERE firebase_uid = %s
    """

    fecha_actual = datetime.now()

    cursor.execute(
        sql,
        (fecha_actual, firebase_uid)
    )

    conexion.commit()

    actualizado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return actualizado