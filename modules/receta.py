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


        consulta_co_ingr = """
        SELECT nombre, id_ingrediente
        FROM Ingrediente
        """

        cursor.execute(consulta_co_ingr)
        ingredientes_bd = cursor.fetchall()

        consulta_ingredientes = """
        INSERT INTO RecetaIngrediente
        (
            id_receta,
            id_ingrediente,
            cantidad,
            unidad,
            TEXTo_libre
        )
        VALUES
        (%s,%s,%s,%s,%s)
        """

        for ingrediente in ingredientes:

            nombre_ing = ingrediente["TEXTo_libre"]

            id_ingrediente = None

            for nombre, id_bd in ingredientes_bd:

                if nombre_ing.strip().lower() == nombre.strip().lower():
                        id_ingrediente = id_bd
                        break

            if id_ingrediente is None:

                nuevo_ingrediente = """
                INSERT INTO Ingrediente
                (
                    nombre,
                    oficial
                )
                VALUES
                (%s, %s)
                """

                cursor.execute(
                     nuevo_ingrediente,
                     (nombre_ing, False)
                )
                id_ingrediente = cursor.lastrowid


            valores_ingredientes = (
                id_receta,
                id_ingrediente,
                ingrediente["cantidad"],
                ingrediente["unidad"],
                ingrediente["TEXTo_libre"]
            )
                        
            cursor.execute(
                consulta_ingredientes,
                valores_ingredientes
            )

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

"""
def listar_receta_previa():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta =
    SELECT 
        id_receta,
        id_usuario, 
        titulo,
        descripcion
    FROM Receta

    cursor.execute(consulta)

    recetas = cursor.fetchall()

    consultaImg =
    SELECT 
        id_imagen,
        ruta
    FROM Imagen WHERE id_receta =%s AND principal = 1

    cursor.execute(consultaImg)

    imagenes = cursor.fetchall()

    consultaUsu =
    SELECT 
        nombre_usuario,
        foto_perfil
    FROM Usuario AND id_usuario

    cursor.execute(consultaUsu)

    usuario = cursor.fetchall()  

    cursor.close()
    conexion.close()

    return id_receta, imagenes, usuario
"""

def listar_recetas_previa():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    SELECT
        r.id_receta,
        r.id_usuario,
        r.titulo,
        r.descripcion,
        u.nombre_usuario,
        u.foto_perfil,
        i.id_imagen,
        i.ruta AS imagen_principal

    FROM Receta AS r

    INNER JOIN Usuario AS u
        ON r.id_usuario = u.id_usuario

    LEFT JOIN Imagen AS i
        ON r.id_receta = i.id_receta
        AND i.principal = 1
    """

    try:

        cursor.execute(consulta)

        recetas = cursor.fetchall()

        return recetas

    finally:

        cursor.close()
        conexion.close()

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

def listar_recetas_previa(id_usuario=None):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    SELECT
        r.id_receta,
        r.id_usuario,
        r.titulo,
        r.descripcion,
        u.nombre_usuario,
        u.foto_perfil,
        i.id_imagen,
        i.ruta AS imagen_principal,
        (
            SELECT COUNT(*)
            FROM Reaccion re
            WHERE re.id_receta = r.id_receta
              AND re.`like` = 1
        ) AS likes,
        (
            SELECT COUNT(*)
            FROM Reaccion re
            WHERE re.id_receta = r.id_receta
              AND re.`like` = 0
        ) AS dislikes,
        (
            SELECT COUNT(*)
            FROM Comentario c
            WHERE c.id_receta = r.id_receta
        ) AS comentarios,
        mi.`like` AS mi_reaccion

    FROM Receta AS r

    INNER JOIN Usuario AS u
        ON r.id_usuario = u.id_usuario

    LEFT JOIN Imagen AS i
        ON r.id_receta = i.id_receta
        AND i.principal = 1

    LEFT JOIN Reaccion AS mi
        ON mi.id_receta = r.id_receta
        AND mi.id_usuario = %s
    """

    try:

        cursor.execute(consulta, (id_usuario,))

        recetas = cursor.fetchall()

        return recetas

    finally:

        cursor.close()
        conexion.close()
        
def reaccionar_receta(id_usuario, id_receta, like):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:

        consulta_buscar = """
            SELECT id_reaccion, `like`
            FROM Reaccion
            WHERE id_usuario = %s AND id_receta = %s
        """

        cursor.execute(consulta_buscar, (id_usuario, id_receta))
        existente = cursor.fetchone()

        if existente is None:

            consulta_insert = """
                INSERT INTO Reaccion (id_usuario, id_receta, `like`, fecha)
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(consulta_insert, (id_usuario, id_receta, like, date.today()))
            resultado = "creada"

        else:

            id_reaccion, like_actual = existente

            if like_actual == like:

                # Tocó el mismo botón de nuevo -> saca la reacción
                consulta_delete = "DELETE FROM Reaccion WHERE id_reaccion = %s"
                cursor.execute(consulta_delete, (id_reaccion,))
                resultado = "eliminada"

            else:

                # Cambió de like a dislike o viceversa
                consulta_update = """
                    UPDATE Reaccion
                    SET `like` = %s, fecha = %s
                    WHERE id_reaccion = %s
                """
                cursor.execute(consulta_update, (like, date.today(), id_reaccion))
                resultado = "actualizada"

        conexion.commit()

        return resultado

    except Exception:

        conexion.rollback()
        raise

    finally:

        cursor.close()
        conexion.close()