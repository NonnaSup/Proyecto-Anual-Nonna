from src.conexion import obtener_conexion
from modules.usuario import eliminar_usuario

# Denuncia.estado se guarda como número (tinyint): la posición en esta lista.
ESTADOS = ["Pendiente", "Resuelto", "Desestimado"]

# Cómo se elimina cada tipo (Cuenta usa eliminar_usuario, que ya oculta también sus recetas)
ELIMINAR = {
    "Receta": "UPDATE Receta SET estado = 0 WHERE id_receta = %s",
    "Comentario": "UPDATE Comentario SET estado = 0 WHERE id_comentario = %s",
    "Reaccion": "DELETE FROM Reaccion WHERE id_reaccion = %s",
}


# Lo que un usuario puede denunciar desde la app
TIPOS_DENUNCIABLES = ("Receta", "Comentario", "Cuenta")


def _leer(sql, params=()):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


def _escribir(*sentencias):
    # todas las sentencias van en una sola transacción
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        for sql, params in sentencias:
            cursor.execute(sql, params)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def es_admin(id_usuario):
    # administrador = usuario activo que figura en la tabla Moderador
    filas = _leer(
        "SELECT 1 FROM Moderador m "
        "JOIN Usuario u ON u.id_usuario = m.id_usuario "
        "WHERE m.id_usuario = %s AND u.estado != 'Eliminado'",
        (id_usuario,)
    )
    return len(filas) > 0


def listar_denuncias():
    # los alias coinciden con la interfaz Reporte del frontend
    filas = _leer("""
        SELECT
            d.id_denuncia AS id,
            d.tipo_contenido AS tipoContenido,
            d.motivo AS tipo,
            d.descripcion AS motivo,
            d.estado,
            d.fecha,
            u.nombre_usuario AS reportante,
            COALESCE(r.id_receta, c.id_receta, re.id_receta) AS idReceta,
            COALESCE(r.titulo, c.contenido, cu.nombre_usuario,
            CONCAT(d.tipo_contenido, ' #', d.id_contenido)) AS contenido
        FROM Denuncia d
        JOIN Usuario u ON u.id_usuario = d.id_usuario
        LEFT JOIN Receta r ON d.tipo_contenido = 'Receta' AND r.id_receta = d.id_contenido
        LEFT JOIN Comentario c ON d.tipo_contenido = 'Comentario' AND c.id_comentario = d.id_contenido
        LEFT JOIN Reaccion re ON d.tipo_contenido = 'Reaccion' AND re.id_reaccion = d.id_contenido
        LEFT JOIN Usuario cu ON d.tipo_contenido = 'Cuenta' AND cu.id_usuario = d.id_contenido
        ORDER BY (COALESCE(d.estado, 0) = 0) DESC, d.fecha DESC, d.id_denuncia DESC
    """)

    for fila in filas:
        fila["estado"] = ESTADOS[fila["estado"] or 0]
        fila["fecha"] = fila["fecha"].strftime("%d/%m/%Y") if fila["fecha"] else ""

    return filas


def buscar_denuncia(id_denuncia):
    filas = _leer(
        "SELECT tipo_contenido, id_contenido FROM Denuncia WHERE id_denuncia = %s",
        (id_denuncia,)
    )
    return filas[0] if filas else None


def cambiar_estado(id_denuncia, estado):
    _escribir((
        "UPDATE Denuncia SET estado = %s WHERE id_denuncia = %s",
        (ESTADOS.index(estado), id_denuncia)
    ))


def eliminar_contenido(denuncia, id_denuncia):
    tipo, id_contenido = denuncia["tipo_contenido"], denuncia["id_contenido"]

    # el contenido ya no existe: se resuelven también las demás denuncias pendientes sobre él
    resolver = (
        "UPDATE Denuncia SET estado = 1 "
        "WHERE tipo_contenido = %s AND id_contenido = %s "
        "AND (estado = 0 OR estado IS NULL OR id_denuncia = %s)",
        (tipo, id_contenido, id_denuncia)
    )

    if tipo == "Cuenta":
        # shortcut: eliminar_usuario usa su propia transacción, no es atómico con resolver; unificar si molesta
        eliminar_usuario(id_contenido)
        _escribir(resolver)
    else:
        _escribir((ELIMINAR[tipo], (id_contenido,)), resolver)


def crear_denuncia(id_usuario, tipo, id_contenido, motivo, descripcion):
    # False si ese usuario ya tiene una denuncia pendiente igual (evita repetirlas)
    repetida = _leer(
        "SELECT 1 FROM Denuncia WHERE id_usuario = %s AND tipo_contenido = %s "
        "AND id_contenido = %s AND (estado = 0 OR estado IS NULL)",
        (id_usuario, tipo, id_contenido)
    )
    if repetida:
        return False

    _escribir((
        "INSERT INTO Denuncia (id_usuario, tipo_contenido, id_contenido, motivo, descripcion, estado, fecha) "
        "VALUES (%s, %s, %s, %s, %s, 0, CURDATE())",
        (id_usuario, tipo, id_contenido, motivo, descripcion or None)
    ))
    return True