from src.conexion import obtener_conexion
from datetime import date

def crear_oferta(
    id_negocio,
    id_sucursal,
    puesto,
    descripcion,
    jornada,
    vacantes
):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    INSERT INTO OfertaLaboral
    (
        id_negocio,
        id_sucursal,
        puesto,
        descripcion,
        jornada,
        vacantes,
        estado
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s)
    """

    valores = (
        id_negocio,
        id_sucursal,
        puesto,
        descripcion,
        jornada,
        vacantes,
        True,           # estado
    )

    cursor.execute(consulta, valores,)

    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas > 0

def crear_oferta_borrador(
    id_negocio,
    id_sucursal,
    puesto,
    descripcion,
    jornada,
    vacantes
):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    INSERT INTO OfertaLaboral
    (
        id_negocio,
        id_sucursal,
        puesto,
        descripcion,
        jornada,
        vacantes,
        estado
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s)
    """

    valores = (
        id_negocio,
        id_sucursal,
        puesto,
        descripcion,
        jornada,
        vacantes,
        False,           # estado
    )

    cursor.execute(consulta, valores,)

    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas > 0

def actualizar_borrador(id_oferta, puesto, descripcion, jornada, vacantes):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        UPDATE OfertaLaboral
        SET puesto = %s,
            descripcion = %s,
            jornada = %s,
            vacantes = %s,
            estado = %s
        WHERE id_oferta = %s
    """

    cursor.execute(sql, (puesto, descripcion, jornada, vacantes, True, id_oferta, ))

    conexion.commit()

    actualizado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return actualizado

def buscar_oferta_por_id(id_oferta):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM OfertaLaboral
        WHERE id_oferta = %s
    """

    cursor.execute(sql, (id_oferta,))

    oferta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return oferta

def buscar_borradores(id_negocio):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM OfertaLaboral
        WHERE id_negocio = %s
        AND estado = %s
    """

    cursor.execute(sql, (id_negocio, False,))

    oferta = cursor.fetchall()

    cursor.close()
    conexion.close()

    return oferta

def listar_ofertas():

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM OfertaLaboral
    ORDER BY id_oferta;
    """

    cursor.execute(sql)

    ofertas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return ofertas

def listar_ofertas_activas():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT
            o.id_oferta,
            o.id_negocio,
            o.id_sucursal,
            o.puesto,
            o.descripcion,
            o.jornada,
            o.vacantes,
            n.nombre_comercial,
            n.logo,
            s.nombre AS nombre_sucursal,
            s.direccion AS direccion_sucursal

        FROM OfertaLaboral AS o

        INNER JOIN Negocio AS n
            ON n.id_negocio = o.id_negocio

        LEFT JOIN Sucursal AS s
            ON s.id_sucursal = o.id_sucursal

        WHERE o.estado = 1
          AND n.estado = 1

        ORDER BY o.id_oferta DESC
    """

    try:
        cursor.execute(sql)
        ofertas = cursor.fetchall()
        return ofertas

    finally:
        cursor.close()
        conexion.close()


def buscar_oferta_publicada_por_id(id_oferta):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT
            o.id_oferta,
            o.id_negocio,
            o.id_sucursal,
            o.puesto,
            o.descripcion,
            o.jornada,
            o.vacantes,
            n.nombre_comercial,
            n.logo,
            s.nombre AS nombre_sucursal,
            s.direccion AS direccion_sucursal

        FROM OfertaLaboral AS o

        INNER JOIN Negocio AS n
            ON n.id_negocio = o.id_negocio

        LEFT JOIN Sucursal AS s
            ON s.id_sucursal = o.id_sucursal

        WHERE o.id_oferta = %s
          AND o.estado = 1
          AND n.estado = 1

        LIMIT 1
    """

    try:
        cursor.execute(sql, (id_oferta,))
        oferta = cursor.fetchone()
        return oferta

    finally:
        cursor.close()
        conexion.close()

def eliminar_oferta(id_oferta):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        UPDATE OfertaLaboral
        SET estado = %s
        WHERE id_oferta = %s
    """

    cursor.execute(sql, (3, id_oferta, ))

    conexion.commit()

    eliminado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return eliminado


def usuario_ya_postulado(id_usuario, id_oferta):
    """
    Comprueba si un usuario ya se postuló a una oferta laboral.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        sql = """
            SELECT id_postulacion
            FROM Postulacion
            WHERE id_usuario = %s
              AND id_oferta = %s
            LIMIT 1
        """

        cursor.execute(sql, (id_usuario, id_oferta))

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conexion.close()


def registrar_postulacion(id_usuario, id_oferta, archivo_cv):
    """
    Registra una postulación nueva junto con la ruta del CV.
    Devuelve True si se registró correctamente.
    Devuelve False si el usuario ya se había postulado.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        sql = """
            INSERT INTO Postulacion
            (
                id_usuario,
                id_oferta,
                fecha,
                estado,
                archivo_cv
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        valores = (
            id_usuario,
            id_oferta,
            date.today(),
            1,
            archivo_cv
        )

        cursor.execute(sql, valores)
        conexion.commit()

        return cursor.rowcount > 0

    except Exception as error:

        conexion.rollback()

        # El índice UNIQUE evita postulaciones duplicadas
        if getattr(error, "errno", None) == 1062:
            return False

        raise

    finally:
        cursor.close()
        conexion.close()
        



def listar_postulaciones_por_oferta(id_oferta):
    """
    Devuelve las postulaciones de una oferta laboral
    junto con los datos del usuario y la ruta del CV.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        sql = """
            SELECT
                p.id_postulacion,
                p.id_usuario,
                p.id_oferta,
                p.fecha,
                p.estado,
                p.archivo_cv,
                u.nombre,
                u.nombre_usuario,
                u.foto_perfil

            FROM Postulacion AS p

            INNER JOIN Usuario AS u
                ON u.id_usuario = p.id_usuario

            WHERE p.id_oferta = %s

            ORDER BY p.fecha DESC, p.id_postulacion DESC
        """

        cursor.execute(sql, (id_oferta,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def contar_postulaciones_por_oferta(id_oferta):
    """
    Devuelve la cantidad de usuarios postulados a una oferta.
    """

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        sql = """
            SELECT COUNT(*)
            FROM Postulacion
            WHERE id_oferta = %s
        """

        cursor.execute(sql, (id_oferta,))

        resultado = cursor.fetchone()

        return resultado[0] if resultado else 0

    finally:
        cursor.close()
        conexion.close()
