# modules/interaccion.py
# Usa la MISMA conexión que receta.py (sin librerías nuevas).
from src.conexion import obtener_conexion
from datetime import date


def _formatear_fecha(fecha):
    # Devuelve la fecha como dd/mm/aaaa (o vacío si el comentario no tiene fecha)
    if fecha is None:
        return ""
    return fecha.strftime("%d/%m/%Y")


def _estado(cursor, id_receta, id_usuario):
    # Likes y dislikes de la receta (solo reacciones a la receta, no a comentarios/productos)
    cursor.execute("""
        SELECT
            COALESCE(SUM(`like` = 1), 0) AS likes,
            COALESCE(SUM(`like` = 0), 0) AS dislikes
        FROM Reaccion
        WHERE id_receta = %s
          AND id_comentario IS NULL
          AND id_producto IS NULL
    """, (id_receta,))
    conteo = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Comentario
        WHERE id_receta = %s
          AND (estado = 1 OR estado IS NULL)
    """, (id_receta,))
    total_comentarios = cursor.fetchone()["total"]

    # Reacción del usuario actual
    cursor.execute("""
        SELECT `like`
        FROM Reaccion
        WHERE id_usuario = %s
          AND id_receta = %s
          AND id_comentario IS NULL
          AND id_producto IS NULL
    """, (id_usuario, id_receta))
    fila = cursor.fetchone()

    mi_reaccion = None
    if fila is not None:
        if fila["like"] == 1:
            mi_reaccion = "like"
        else:
            mi_reaccion = "dislike"

    cursor.execute(
        "SELECT 1 FROM Guardado WHERE id_usuario = %s AND id_receta = %s",
        (id_usuario, id_receta)
    )
    guardada = cursor.fetchone() is not None

    return {
        "likes": int(conteo["likes"]),
        "dislikes": int(conteo["dislikes"]),
        "comentarios": int(total_comentarios),
        "mi_reaccion": mi_reaccion,
        "guardada": guardada
    }


def estado_interaccion(id_receta, id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        return _estado(cursor, id_receta, id_usuario)
    finally:
        cursor.close()
        conexion.close()


def reaccionar(id_usuario, id_receta, like):
    valor = 1 if like else 0
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_reaccion, `like`
            FROM Reaccion
            WHERE id_usuario = %s
              AND id_receta = %s
              AND id_comentario IS NULL
              AND id_producto IS NULL
        """, (id_usuario, id_receta))
        existente = cursor.fetchone()

        if existente is None:
            cursor.execute("""
                INSERT INTO Reaccion (id_usuario, id_receta, `like`, fecha)
                VALUES (%s, %s, %s, %s)
            """, (id_usuario, id_receta, valor, date.today()))

        elif existente["like"] == valor:
            # Tocó el mismo botón: se quita la reacción
            cursor.execute("DELETE FROM Reaccion WHERE id_reaccion = %s",
                           (existente["id_reaccion"],))
        else:
            # Cambió de like a dislike (o al revés)
            cursor.execute("""
                UPDATE Reaccion SET `like` = %s, fecha = %s
                WHERE id_reaccion = %s
            """, (valor, date.today(), existente["id_reaccion"]))

        conexion.commit()
        return _estado(cursor, id_receta, id_usuario)

    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def listar_comentarios(id_receta):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT
                c.id_comentario,
                c.id_usuario,
                u.nombre_usuario AS nombre_usuario,
                c.contenido AS texto,
                c.fecha AS fecha
            FROM Comentario AS c
            INNER JOIN Usuario AS u
                ON u.id_usuario = c.id_usuario
            WHERE c.id_receta = %s
              AND (c.estado = 1 OR c.estado IS NULL)
            ORDER BY c.id_comentario ASC
        """, (id_receta,))
        filas = cursor.fetchall()
        for fila in filas:
            fila["fecha"] = _formatear_fecha(fila["fecha"])
        return filas
    finally:
        cursor.close()
        conexion.close()


def comentar(id_usuario, id_receta, texto):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            INSERT INTO Comentario (id_usuario, id_receta, contenido, fecha, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_usuario, id_receta, texto, date.today(), 1))
        nuevo_id = cursor.lastrowid
        conexion.commit()

        cursor.execute("""
            SELECT
                c.id_comentario,
                c.id_usuario,
                u.nombre_usuario AS nombre_usuario,
                c.contenido AS texto,
                c.fecha AS fecha
            FROM Comentario AS c
            INNER JOIN Usuario AS u
                ON u.id_usuario = c.id_usuario
            WHERE c.id_comentario = %s
        """, (nuevo_id,))
        fila = cursor.fetchone()
        fila["fecha"] = _formatear_fecha(fila["fecha"])
        return fila

    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def guardar(id_usuario, id_receta):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id_guardado FROM Guardado WHERE id_usuario = %s AND id_receta = %s",
            (id_usuario, id_receta)
        )
        existente = cursor.fetchone()

        if existente is None:
            cursor.execute("""
                INSERT INTO Guardado (id_usuario, id_receta, fecha)
                VALUES (%s, %s, %s)
            """, (id_usuario, id_receta, date.today()))
            guardada = True
        else:
            cursor.execute("DELETE FROM Guardado WHERE id_guardado = %s",
                           (existente["id_guardado"],))
            guardada = False

        conexion.commit()
        return {"guardada": guardada}

    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def recetas_con_dislike(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id_receta
            FROM Reaccion
            WHERE id_usuario = %s
              AND `like` = 0
              AND id_receta IS NOT NULL
              AND id_comentario IS NULL
              AND id_producto IS NULL
        """, (id_usuario,))
        return [fila["id_receta"] for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


# ---------------------------------------------------------------
# ACTIVIDAD DEL USUARIO (likes dados y recetas guardadas)
# Solo cuentan recetas activas (Receta.estado = 1).
# ---------------------------------------------------------------

_IMAGEN_PRINCIPAL_RECETA = """
    (
        SELECT i.ruta
        FROM Imagen AS i
        WHERE i.id_receta = r.id_receta
        ORDER BY i.principal DESC, (i.orden IS NULL), i.orden, i.id_imagen
        LIMIT 1
    ) AS imagen_principal
"""


def resumen_interacciones(id_usuario):
    # Cantidad de recetas con like y de recetas guardadas del usuario
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM Reaccion AS rx
            INNER JOIN Receta AS r
                ON r.id_receta = rx.id_receta
            WHERE rx.id_usuario = %s
              AND rx.`like` = 1
              AND rx.id_comentario IS NULL
              AND rx.id_producto IS NULL
              AND r.estado = 1
        """, (id_usuario,))
        likes = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM Guardado AS g
            INNER JOIN Receta AS r
                ON r.id_receta = g.id_receta
            WHERE g.id_usuario = %s
              AND r.estado = 1
        """, (id_usuario,))
        guardados = cursor.fetchone()["total"]

        return {"likes": int(likes), "guardados": int(guardados)}
    finally:
        cursor.close()
        conexion.close()


def listar_likes_usuario(id_usuario):
    # Recetas a las que el usuario les dio like (las mas recientes primero)
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(f"""
            SELECT
                r.id_receta,
                r.titulo,
                {_IMAGEN_PRINCIPAL_RECETA}
            FROM Reaccion AS rx
            INNER JOIN Receta AS r
                ON r.id_receta = rx.id_receta
            WHERE rx.id_usuario = %s
              AND rx.`like` = 1
              AND rx.id_comentario IS NULL
              AND rx.id_producto IS NULL
              AND r.estado = 1
            ORDER BY rx.fecha DESC, rx.id_reaccion DESC
        """, (id_usuario,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


def listar_guardados_usuario(id_usuario):
    # Recetas que el usuario guardo (las mas recientes primero)
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(f"""
            SELECT
                r.id_receta,
                r.titulo,
                {_IMAGEN_PRINCIPAL_RECETA}
            FROM Guardado AS g
            INNER JOIN Receta AS r
                ON r.id_receta = g.id_receta
            WHERE g.id_usuario = %s
              AND r.estado = 1
            ORDER BY g.fecha DESC, g.id_guardado DESC
        """, (id_usuario,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()