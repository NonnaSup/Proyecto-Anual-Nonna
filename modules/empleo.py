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