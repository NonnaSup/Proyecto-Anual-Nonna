# modules/interaccion.py
# Lógica de like/dislike, comentarios y guardados de recetas.
# ⚠️ Cambiá obtener_conexion() por la forma en que ya te conectás a MySQL en receta.py
import pymysql
from datetime import date


def obtener_conexion():
    # Adaptá estos datos (o importá tu conexión existente)
    return pymysql.connect(
        host="localhost", user="root", password="", database="la_nonna",
        cursorclass=pymysql.cursors.DictCursor
    )


def _estado(cur, id_receta, id_usuario):
    # Contadores de likes y dislikes ("like" va entre comillas invertidas porque es palabra reservada)
    cur.execute("""SELECT
                     COALESCE(SUM(`like` = 1), 0) AS likes,
                     COALESCE(SUM(`like` = 0), 0) AS dislikes
                   FROM Reaccion
                   WHERE id_receta = %s AND id_comentario IS NULL AND id_producto IS NULL""", (id_receta,))
    conteo = cur.fetchone()

    cur.execute("SELECT COUNT(*) AS total FROM Comentario WHERE id_receta = %s", (id_receta,))
    comentarios = cur.fetchone()["total"]

    # Reacción del usuario actual
    cur.execute("""SELECT `like` FROM Reaccion
                   WHERE id_usuario = %s AND id_receta = %s
                   AND id_comentario IS NULL AND id_producto IS NULL""", (id_usuario, id_receta))
    fila = cur.fetchone()
    mi_reaccion = None
    if fila is not None:
        mi_reaccion = "like" if fila["like"] == 1 else "dislike"

    cur.execute("SELECT 1 FROM Guardado WHERE id_usuario = %s AND id_receta = %s", (id_usuario, id_receta))
    guardada = cur.fetchone() is not None

    return {
        "likes": int(conteo["likes"]),
        "dislikes": int(conteo["dislikes"]),
        "comentarios": comentarios,
        "mi_reaccion": mi_reaccion,
        "guardada": guardada
    }


def estado_interaccion(id_receta, id_usuario):
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            return _estado(cur, id_receta, id_usuario)
    finally:
        con.close()


def reaccionar(datos):
    id_usuario = datos["id_usuario"]
    id_receta = datos["id_receta"]
    valor = 1 if datos["like"] else 0

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("""SELECT id_reaccion, `like` FROM Reaccion
                           WHERE id_usuario = %s AND id_receta = %s
                           AND id_comentario IS NULL AND id_producto IS NULL""", (id_usuario, id_receta))
            existente = cur.fetchone()

            if existente is None:
                # No había reacción: se crea
                cur.execute("""INSERT INTO Reaccion (id_usuario, id_receta, `like`, fecha)
                               VALUES (%s, %s, %s, %s)""", (id_usuario, id_receta, valor, date.today()))
            elif existente["like"] == valor:
                # Tocó el mismo botón otra vez: se quita la reacción
                cur.execute("DELETE FROM Reaccion WHERE id_reaccion = %s", (existente["id_reaccion"],))
            else:
                # Cambió de like a dislike (o al revés)
                cur.execute("UPDATE Reaccion SET `like` = %s, fecha = %s WHERE id_reaccion = %s",
                            (valor, date.today(), existente["id_reaccion"]))
            con.commit()
            return _estado(cur, id_receta, id_usuario)
    finally:
        con.close()


def listar_comentarios(id_receta):
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            # ⚠️ Asumo que la columna del texto se llama "texto" y la de fecha "fecha"
            cur.execute("""SELECT c.id_comentario, c.id_usuario, u.nombre AS nombre_usuario,
                                  c.texto, DATE_FORMAT(c.fecha, '%%d/%%m/%%Y') AS fecha
                           FROM Comentario c
                           JOIN Usuario u ON u.id_usuario = c.id_usuario
                           WHERE c.id_receta = %s
                           ORDER BY c.id_comentario ASC""", (id_receta,))
            return cur.fetchall()
    finally:
        con.close()


def comentar(datos):
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("""INSERT INTO Comentario (id_usuario, id_receta, texto, fecha)
                           VALUES (%s, %s, %s, %s)""",
                        (datos["id_usuario"], datos["id_receta"], datos["texto"], date.today()))
            con.commit()
            nuevo_id = cur.lastrowid

            cur.execute("""SELECT c.id_comentario, c.id_usuario, u.nombre AS nombre_usuario,
                                  c.texto, DATE_FORMAT(c.fecha, '%%d/%%m/%%Y') AS fecha
                           FROM Comentario c
                           JOIN Usuario u ON u.id_usuario = c.id_usuario
                           WHERE c.id_comentario = %s""", (nuevo_id,))
            return cur.fetchone()
    finally:
        con.close()


def guardar(datos):
    id_usuario = datos["id_usuario"]
    id_receta = datos["id_receta"]
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT id_guardado FROM Guardado WHERE id_usuario = %s AND id_receta = %s",
                        (id_usuario, id_receta))
            existente = cur.fetchone()
            if existente is None:
                cur.execute("INSERT INTO Guardado (id_usuario, id_receta) VALUES (%s, %s)",
                            (id_usuario, id_receta))
                guardada = True
            else:
                cur.execute("DELETE FROM Guardado WHERE id_guardado = %s", (existente["id_guardado"],))
                guardada = False
            con.commit()
            return {"guardada": guardada}
    finally:
        con.close()
