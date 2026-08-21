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
        id_sucursal
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

def subir_borrador(id_oferta, puesto, descripcion, jornada, vacantes):

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
    SELECT *
    FROM OfertaLaboral
    WHERE estado = %s
    ORDER BY id_oferta;
    """

    cursor.execute(sql, (True,))

    ofertas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return ofertas

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