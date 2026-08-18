from src.conexion import obtener_conexion
from datetime import date

def crear_oferta(
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
        puesto,
        descripcion,
        jornada,
        vacantes,
        estado
    )
    VALUES
    (%s,%s,%s,%s,%s)
    """

    valores = (
        puesto,
        descripcion,
        jornada,
        vacantes,
        "Activo",           # estado
    )

    cursor.execute(consulta, valores)

    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas > 0

def crear_oferta_borrador(
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
        puesto,
        descripcion,
        jornada,
        vacantes,
        estado
    )
    VALUES
    (%s,%s,%s,%s,%s)
    """

    valores = (
        puesto,
        descripcion,
        jornada,
        vacantes,
        "Inactivo",           # estado
    )

    cursor.execute(consulta, valores)

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
            estado = "Activo"
        WHERE id_oferta = %s
    """

    cursor.execute(sql, (id_oferta, puesto, descripcion, jornada, vacantes))

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

    cursor.execute(sql, (id_negocio, "Inactivo",))

    oferta = cursor.fetchall()

    cursor.close()
    conexion.close()

    return oferta

def listar_ofertas():

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    sql = """
    SELECT
        id_oferta,
        id_negocio,
        puesto,
        descripcion,
        jornada,
        vacantes
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
        id_oferta,
        id_negocio,
        puesto,
        descripcion,
        jornada,
        vacantes
    FROM OfertaLaboral
    WHERE estado = %s
    ORDER BY id_oferta;
    """

    cursor.execute(sql, ("Activo"))

    ofertas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return ofertas

def eliminar_oferta(id_oferta):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        UPDATE OfertaLaboral
        SET estado = 'Eliminado'
        WHERE id_oferta = %s
    """

    cursor.execute(sql, (id_oferta,))

    conexion.commit()

    eliminado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return eliminado