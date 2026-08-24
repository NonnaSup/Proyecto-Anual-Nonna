from src.conexion import obtener_conexion
from datetime import date

def crear_receta(
    id_usuario,
    titulo,
    descripcion,
    tiempo_preparacion,
    porciones,
    pasos,
    ingredientes,
    imagenes
):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:

        consulta = """
        INSERT INTO Receta
        (
            id_usuario,
            titulo,
            descripcion,
            tiempo_preparacion,
            porciones,
            estado,
            visibilidad,
            fecha_publicacion
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s)
        """

        valores = (
            id_usuario,
            titulo,
            descripcion,
            tiempo_preparacion,
            porciones,
            True,
            True,
            date.today()    
        )

        cursor.execute(consulta, valores)

        id_receta = cursor.lastrowid



        consulta_pasos = """
        INSERT INTO Paso
        (
            id_receta,
            numero,
            descripcion_paso
        )
        VALUES
        (%s,%s,%s)
        """

        for paso in pasos:
            
            valores_paso = (
                id_receta,
                paso["numero"],
                paso["descripcion_paso"]
            )

            cursor.execute(consulta_pasos, valores_paso)



        consulta_ingredientes = """
        INSERT INTO RecetaIngrediente
        (
            id_receta,
            cantidad,
            unidad,
            TEXTo_libre
        )
        VALUES
        (%s,%s,%s,%s)
        """

        for ingrediente in ingredientes:
            
            valores_ingredientes = (
                id_receta,
                ingrediente["cantidad"],
                ingrediente["unidad"],
                ingrediente["TEXTo_libre"]
            )

            cursor.execute(consulta_ingredientes, valores_ingredientes)



        consulta_imagenes = """
        INSERT INTO Imagen
        (
            id_receta,
            ruta,
            principal,
            orden
        )
        VALUES
        (%s,%s,%s,%s)
        """

        for imagen in imagenes:
            
            valores_imagenes = (
                id_receta,
                imagen["ruta"],
                imagen["principal"],
                imagen["orden"]
            )

            cursor.execute(consulta_imagenes, valores_imagenes)


        conexion.commit()

        return id_receta

    except Exception:
        
        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()


def crear_pasos_ingredientes_imagen(
    id_receta,
    numero,
    descripcion_paso,
    cantidad,
    unidad,
    TEXTo_libre,
    ruta,
    principal,
    orden
):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    INSERT INTO Paso
    (
        id_receta,
        numero,
        descripcion_paso
    )
    VALUES
    (%s,%s,%s)
    """

    valores = (
        id_receta,
        numero,
        descripcion_paso
    )

    consulta2 = """
    INSERT INTO RecetaIngrediente
    (
        id_receta,
        cantidad,
        unidad,
        TEXTo_libre
    )
    VALUES
    (%s,%s,%s,%s)
    """

    valores2 = (
        id_receta,
        cantidad,
        unidad,
        TEXTo_libre
    )

    consulta3 = """
    INSERT INTO Imagen
    (
        id_receta,
        ruta,
        principal,
        orden
    )
    VALUES
    (%s,%s,%s,%s)
    """

    valores3 = (
        id_receta,
        ruta,
        principal,
        orden
    )

    cursor.execute(consulta, valores)
    cursor.execute(consulta2, valores2)
    cursor.execute(consulta3, valores3)


    conexion.commit()

    cursor.close()
    conexion.close()

    return True

###///

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