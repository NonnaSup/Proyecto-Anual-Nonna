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