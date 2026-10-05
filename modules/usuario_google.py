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
# COMPLETAR USUARIO GOOGLE
# ==================================================

def completar_usuario_google(firebase_uid, nombre_usuario, fecha_nacimiento):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:

        # ------------------------------------------
        # 1. Buscar los datos del usuario Google
        # ------------------------------------------

        sql_google = """
            SELECT nombre, correo, foto_perfil
            FROM usuario_google
            WHERE firebase_uid = %s
        """

        cursor.execute(sql_google, (firebase_uid,))
        usuario_google = cursor.fetchone()

        if not usuario_google:
            return None

        # ------------------------------------------
        # 2. Crear usuario normal
        # ------------------------------------------

        sql_usuario = """
            INSERT INTO Usuario
            (
                nombre,
                nombre_usuario,
                correo,
                fecha_nacimiento,
                foto_perfil,
                cuenta_verificada,
                estado,
                fecha_registro
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        fecha_actual = datetime.now().date()

        valores = (
            usuario_google["nombre"],
            nombre_usuario,
            usuario_google["correo"],
            fecha_nacimiento,
            usuario_google["foto_perfil"],
            True,
            "Activo",
            fecha_actual
        )

        cursor.execute(sql_usuario, valores)

        id_usuario = cursor.lastrowid

        # ------------------------------------------
        # 3. Vincular usuario_google con Usuario
        # ------------------------------------------

        sql_update = """
            UPDATE usuario_google
            SET id_usuario = %s
            WHERE firebase_uid = %s
        """

        cursor.execute(
            sql_update,
            (
                id_usuario,
                firebase_uid
            )
        )

        conexion.commit()

        return id_usuario

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


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