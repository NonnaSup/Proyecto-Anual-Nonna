from src.conexion import obtener_conexion


def crear_negocio(
    id_usuario,
    nombre_comercial,
    descripcion,
    logo,
    portada,
    telefono,
    correo,
    sitio_web,
    redes_sociales
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
        False,
        descripcion,
        logo,
        portada,
        telefono,
        correo,
        sitio_web,
        redes_sociales,
        True
    )

    cursor.execute(consulta, valores)

    conexion.commit()

    filas_afectadas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas_afectadas > 0

def crear_sucursal(id_negocio, nombre, direccion, horarios, casa_central):

    conexion = obtener_conexion()

    cursor = conexion.cursor(dictionary=True)

    consulta = """
    INSERT INTO Sucursal
    (
        id_negocio,
        nombre,
        direccion,
        horarios,
        casa_central 
    )
    VALUES
    (%s, %s, %s, %s, %s)
    """

    valores = (
        id_negocio,
        nombre,
        direccion,
        horarios,
        casa_central
    )

    cursor.execute(consulta, valores)

    conexion.commit()

    filas_afectadas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas_afectadas > 0

def buscar_casa_central(id_negocio):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Sucursal
        WHERE id_negocio = %s
        AND casa_central = %s
    """

    cursor.execute(sql, (id_negocio, True,))

    oferta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return oferta is not None
