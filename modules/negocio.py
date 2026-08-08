from src.conexion import obtener_conexion


def crear_negocio(
    id_usuario,
    nombre_comercial,
    verificado,
    descripcion,
    logo,
    portada,
    telefono,
    correo,
    sitio_web,
    redes_sociales,
    estado
):

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    consulta = """
    INSERT INTO Negocio
    (
        id_usuario,
        nombre_comercial,
        verificado,
        descripcion,
        logo,
        portada,
        telefono,
        correo,
        sitio_web,
        redes_sociales,
        estado
    )
    VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        id_usuario,
        nombre_comercial,
        verificado,
        descripcion,
        logo,
        portada,
        telefono,
        correo,
        sitio_web,
        redes_sociales,
        estado
    )

    cursor.execute(consulta, valores)

    conexion.commit()

    filas_afectadas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas_afectadas > 0