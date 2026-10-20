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
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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

        # Guardar pasos
        consulta_pasos = """
        INSERT INTO Paso
        (
            id_receta,
            numero,
            descripcion_paso
        )
        VALUES (%s, %s, %s)
        """

        for paso in pasos:
            valores_paso = (
                id_receta,
                paso["numero"],
                paso["descripcion_paso"]
            )

            cursor.execute(consulta_pasos, valores_paso)

        # Obtener ingredientes existentes
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
        VALUES (%s, %s, %s, %s, %s)
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
                VALUES (%s, %s)
                """

                cursor.execute(
                    nuevo_ingrediente,
                    (nombre_ing, False)
                )

                id_ingrediente = cursor.lastrowid

                # Agregarlo a la lista para evitar duplicados
                ingredientes_bd.append((nombre_ing, id_ingrediente))

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

        # Guardar TODAS las imágenes
        consulta_imagenes = """
        INSERT INTO Imagen
        (
            id_receta,
            ruta,
            principal,
            orden
        )
        VALUES (%s, %s, %s, %s)
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


def eliminar_receta(id_receta, id_usuario=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        if id_usuario is None:
            consulta = """
            UPDATE Receta
            SET estado = 0
            WHERE id_receta = %s
            """
            valores = (id_receta,)
        else:
            consulta = """
            UPDATE Receta
            SET estado = 0
            WHERE id_receta = %s
              AND id_usuario = %s
            """
            valores = (id_receta, id_usuario)

        cursor.execute(consulta, valores)
        conexion.commit()

        return cursor.rowcount > 0

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def buscar_receta(id_receta):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
        SELECT *
        FROM Receta
        WHERE id_receta = %s
          AND estado = 1
        """

        cursor.execute(consulta, (id_receta,))
        return cursor.fetchone()

    finally:
        cursor.close()
        conexion.close()


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
    WHERE r.estado = 1
    """

    try:
        cursor.execute(consulta, (id_usuario,))
        return cursor.fetchall()

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
        WHERE id_usuario = %s
          AND id_receta = %s
        """

        cursor.execute(consulta_buscar, (id_usuario, id_receta))
        existente = cursor.fetchone()

        if existente is None:
            consulta_insert = """
            INSERT INTO Reaccion
                (id_usuario, id_receta, `like`, fecha)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                consulta_insert,
                (id_usuario, id_receta, like, date.today())
            )

            resultado = "creada"

        else:
            id_reaccion, like_actual = existente

            if like_actual == like:
                consulta_delete = """
                DELETE FROM Reaccion
                WHERE id_reaccion = %s
                """

                cursor.execute(consulta_delete, (id_reaccion,))
                resultado = "eliminada"

            else:
                consulta_update = """
                UPDATE Reaccion
                SET `like` = %s, fecha = %s
                WHERE id_reaccion = %s
                """

                cursor.execute(
                    consulta_update,
                    (like, date.today(), id_reaccion)
                )

                resultado = "actualizada"

        conexion.commit()
        return resultado

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def traer_receta(id_receta):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:

        # Datos principales de la receta y su autor
        consulta1 = """
            SELECT
                r.id_receta,
                r.id_usuario,
                r.titulo,
                r.descripcion,
                r.tiempo_preparacion,
                r.porciones,
                u.nombre_usuario,
                u.foto_perfil
            FROM Receta AS r
            INNER JOIN Usuario AS u
                ON r.id_usuario = u.id_usuario
            WHERE r.id_receta = %s
        """

        cursor.execute(consulta1, (id_receta,))
        datos_receta = cursor.fetchone()

        if datos_receta is None:
            return None

        # Ingredientes
        consulta2 = """
            SELECT
                ri.id_ingrediente,
                ri.cantidad,
                ri.unidad,
                ri.TEXTo_libre
            FROM RecetaIngrediente AS ri
            WHERE ri.id_receta = %s
        """

        cursor.execute(consulta2, (id_receta,))
        ingredientes = cursor.fetchall()

        # Pasos de preparación
        consulta3 = """
            SELECT
                p.numero,
                p.descripcion_paso
            FROM Paso AS p
            WHERE p.id_receta = %s
            ORDER BY p.numero
        """

        cursor.execute(consulta3, (id_receta,))
        pasos = cursor.fetchall()

        # Todas las imágenes, ordenadas
        consulta4 = """
            SELECT
                i.id_imagen,
                i.ruta,
                i.principal,
                i.orden
            FROM Imagen AS i
            WHERE i.id_receta = %s
            ORDER BY i.orden
        """

        cursor.execute(consulta4, (id_receta,))
        imagenes = cursor.fetchall()

        return {
            "receta": datos_receta,
            "ingredientes": ingredientes,
            "pasos": pasos,
            "imagenes": imagenes
        }

# ---------------------------------------------------------------
# PERFIL: recetas del usuario
# ---------------------------------------------------------------

def listar_mis_recetas(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    consulta = """
    SELECT
        r.id_receta,
        r.titulo,
        r.descripcion,
        r.tiempo_preparacion,
        r.porciones,
        i.ruta AS imagen_principal
    FROM Receta AS r
    LEFT JOIN Imagen AS i
        ON r.id_receta = i.id_receta
       AND i.principal = 1
    WHERE r.id_usuario = %s
      AND r.estado = 1
    ORDER BY r.id_receta DESC
    """

    try:
        cursor.execute(consulta, (id_usuario,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def editar_receta(
    id_receta,
    id_usuario,
    titulo,
    descripcion,
    tiempo_preparacion,
    porciones
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    consulta = """
    UPDATE Receta
    SET titulo = %s,
        descripcion = %s,
        tiempo_preparacion = %s,
        porciones = %s
    WHERE id_receta = %s
      AND id_usuario = %s
      AND estado = 1
    """

    try:
        cursor.execute(
            consulta,
            (
                titulo,
                descripcion,
                tiempo_preparacion,
                porciones,
                id_receta,
                id_usuario
            )
        )

        conexion.commit()
        return cursor.rowcount > 0

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()

