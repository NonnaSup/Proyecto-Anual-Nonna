from src.conexion import obtener_conexion
from mysql.connector import IntegrityError


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

def actualizar_perfil(id_negocio, nombre_comercial, descripcion, logo, portada, telefono, correo, sitio_web, redes_sociales):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        consulta = """
            UPDATE Negocio
            SET nombre_comercial = %s,
                descripcion = %s,
                logo = %s,
                portada = %s,
                telefono = %s,
                correo = %s,
                sitio_web = %s,
                redes_sociales = %s
            WHERE id_negocio = %s
        """

        cursor.execute(consulta, (
            nombre_comercial, 
            descripcion, 
            logo, 
            portada, 
            telefono, 
            correo, 
            sitio_web, 
            redes_sociales, 
            id_negocio
        ))

        conexion.commit()
        return True

    except IntegrityError:
        # algun dato UNIQUE ya lo usa otro negocio
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()

def obtener_perfil_negocio(id_negocio):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT
                id_negocio,
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
            FROM Negocio
            WHERE id_negocio = %s
              AND estado = 1
        """

        cursor.execute(consulta, (id_negocio,))
        return cursor.fetchone()

    finally:
        cursor.close()
        conexion.close()


def negocio_es_de_usuario(id_negocio, id_usuario):
    # Verifica que el negocio exista, este activo y pertenezca al usuario
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            """
            SELECT id_negocio
            FROM Negocio
            WHERE id_negocio = %s
              AND id_usuario = %s
              AND estado = 1
            """,
            (id_negocio, id_usuario)
        )
        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conexion.close()


def eliminar_negocio(id_negocio):
    # Baja logica: no se borra la fila, solo se pasa estado a 0.
    # Asi no rompe las foreign keys (sucursales, empleos, etc.)
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute(
            "UPDATE Negocio SET estado = 0 WHERE id_negocio = %s",
            (id_negocio,)
        )
        conexion.commit()
        return cursor.rowcount > 0

    finally:
        cursor.close()
        conexion.close()


def listar_negocios():
    # Todos los negocios activos (para la pagina publica de Negocios).
    # La direccion sale de la casa central; si no tiene, de su primera sucursal.
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    consulta = """
    SELECT
        n.id_negocio,
        n.nombre_comercial,
        n.descripcion,
        n.logo,
        n.portada,
        n.verificado,
        n.telefono,
        n.correo,
        n.sitio_web,
        n.redes_sociales,
        s.direccion
    FROM Negocio AS n
    LEFT JOIN Sucursal AS s
        ON s.id_sucursal = (
            SELECT s2.id_sucursal
            FROM Sucursal AS s2
            WHERE s2.id_negocio = n.id_negocio
            ORDER BY s2.casa_central DESC, s2.id_sucursal
            LIMIT 1
        )
    WHERE n.estado = 1
    ORDER BY n.nombre_comercial
    """

    try:
        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def listar_productos_activos():
    # Publicaciones (Producto) activas de negocios activos, con su imagen
    # principal (tabla Imagen, por id_producto). Los destacados van primero.
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    consulta = """
    SELECT
        p.id_producto,
        p.id_negocio,
        p.nombre,
        p.descripcion,
        p.precio,
        p.destacado,
        (
            SELECT i.ruta
            FROM Imagen AS i
            WHERE i.id_producto = p.id_producto
            ORDER BY i.principal DESC, (i.orden IS NULL), i.orden, i.id_imagen
            LIMIT 1
        ) AS imagen
    FROM Producto AS p
    INNER JOIN Negocio AS n
        ON n.id_negocio = p.id_negocio
    WHERE p.estado = 1
      AND n.estado = 1
    ORDER BY p.id_negocio, p.destacado DESC, p.id_producto DESC
    """

    try:
        cursor.execute(consulta)
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()


def listar_mis_negocios(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    consulta = """
    SELECT
        n.id_negocio,
        n.nombre_comercial,
        n.descripcion,
        n.logo
    FROM Negocio AS n
    WHERE n.id_usuario = %s
      AND n.estado = 1
    """

    try:
        cursor.execute(consulta, (id_usuario,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conexion.close()

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

    cursor.execute(sql, (id_negocio, 1,))

    oferta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return oferta is not None

def crear_producto(id_negocio, nombre, descripcion, precio, imagen=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        consulta = """
            INSERT INTO Producto (
                id_negocio,
                nombre,
                descripcion,
                precio,
                estado,
                destacado
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(consulta, (
            id_negocio,
            nombre,
            descripcion,
            precio,
            True,
            False
        ))

        id_producto = cursor.lastrowid

        if imagen:
            consulta_imagen = """
                INSERT INTO Imagen (
                    id_producto,
                    ruta,
                    principal,
                    orden
                )
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(consulta_imagen, (
                id_producto,
                imagen,
                True,
                1
            ))

        conexion.commit()
        return id_producto

    except Exception:
        conexion.rollback()
        raise

    finally:
        cursor.close()
        conexion.close()


def listar_productos_negocio(id_negocio):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT
                p.id_producto,
                p.id_negocio,
                p.nombre,
                p.descripcion,
                p.precio,
                p.estado,
                p.destacado,
                (
                    SELECT i.ruta
                    FROM Imagen AS i
                    WHERE i.id_producto = p.id_producto
                    ORDER BY
                        i.principal DESC,
                        (i.orden IS NULL),
                        i.orden,
                        i.id_imagen
                    LIMIT 1
                ) AS imagen
            FROM Producto AS p
            INNER JOIN Negocio AS n
                ON n.id_negocio = p.id_negocio
            WHERE p.id_negocio = %s
              AND p.estado = 1
              AND n.estado = 1
            ORDER BY p.destacado DESC, p.id_producto DESC
        """

        cursor.execute(consulta, (id_negocio,))
        productos = cursor.fetchall()

        for producto in productos:
            if producto["precio"] is not None:
                producto["precio"] = float(producto["precio"])

            producto["estado"] = bool(producto["estado"])
            producto["destacado"] = bool(producto["destacado"])

        return productos

    finally:
        cursor.close()
        conexion.close()