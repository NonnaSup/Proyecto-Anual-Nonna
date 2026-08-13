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
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
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

    