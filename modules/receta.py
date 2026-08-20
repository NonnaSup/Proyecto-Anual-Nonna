from src.conexion import obtener_conexion

def crear_receta(
    nombre,
    descripcion,
    id_usuario,
    fecha_publicacion,
    tiempo,
    visibilidad,
    estado,
    porciones,
    tiempo_preparacion     
):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    INSERT INTO Receta
    (
        nombre,
        descripcion,
        id_usuario,
        fecha_publicacion,
        tiempo,
        visibilidad,
        estado,
        porciones,
        tiempo_preparacion
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    valores = (
        nombre,
        descripcion,
        id_usuario,
        fecha_publicacion,
        tiempo,
        visibilidad,
        estado,
        porciones,
        tiempo_preparacion
    )

    cursor.execute(consulta, valores)

    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas > 0


def eliminar_receta(id_receta):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
        UPDATE Receta
        SET estado = 'Eliminado'
        WHERE id_receta = %s
    """

    cursor.execute(consulta, (id_receta,))

    conexion.commit()

    eliminado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return eliminado


def listar_receta():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    SELECT 
        id_receta, 
        nombre,
        tiempo,
        visibilidad,
        estado,
        porciones,
        fecha_publicacion,
        descripcion
    FROM Receta
    ORDER BY id_receta;
    """

    cursor.execute(consulta)

    recetas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return recetas


def buscar_receta(id_receta):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    consulta = """
        SELECT *
        FROM Usuario
        WHERE id_usuario = %s
    """

    cursor.execute(consulta, (id_receta,))

    receta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return receta


def buscar_usuario_por_nombre(nombre):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Receta
        WHERE nombre = %s
    """

    cursor.execute(sql, (nombre,))

    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario