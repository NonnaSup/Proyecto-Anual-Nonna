from src.conexion import obtener_conexion
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash

def crear_usuario(nombre, nombre_usuario, correo, clave, fecha_nacimiento):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    clave_hasheada = generate_password_hash(clave)

    consulta = """
    INSERT INTO Usuario
    (
        nombre,
        nombre_usuario,
        correo,
        clave,
        fecha_nacimiento,
        foto_perfil,
        biografia,
        cuenta_verificada,
        estado,
        fecha_registro
    )
    VALUES
    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    valores = (
        nombre,
        nombre_usuario,
        correo,
        clave_hasheada,
        fecha_nacimiento,
        None,
        None,
        False,
        "Activo",
        date.today()
    )

    cursor.execute(consulta, valores)
    conexion.commit()

    filas = cursor.rowcount

    cursor.close()
    conexion.close()

    return filas > 0


def listar_usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    consulta = """
    SELECT
        id_usuario,
        nombre,
        nombre_usuario,
        correo
    FROM Usuario
    WHERE estado != 'Eliminado'
    ORDER BY id_usuario;
    """

    cursor.execute(consulta)
    usuarios = cursor.fetchall()

    cursor.close()
    conexion.close()

    return usuarios


def buscar_usuario_por_id(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Usuario
        WHERE id_usuario = %s AND estado != 'Eliminado'
    """

    cursor.execute(sql, (id_usuario,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario


def buscar_usuario_por_nombre(nombre_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Usuario
        WHERE nombre_usuario = %s AND estado != 'Eliminado'
    """

    cursor.execute(sql, (nombre_usuario,))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario


def buscar_usuario_por_credencial(identificador):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT *
        FROM Usuario
        WHERE (correo = %s OR nombre_usuario = %s)
          AND estado != 'Eliminado'
    """

    cursor.execute(sql, (identificador, identificador))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario


def actualizar_usuario(id_usuario, nombre, biografia):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        UPDATE Usuario
        SET nombre = %s,
            biografia = %s
        WHERE id_usuario = %s
    """

    cursor.execute(sql, (nombre, biografia, id_usuario))
    conexion.commit()

    actualizado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return actualizado


def eliminar_usuario(id_usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    sql = """
        UPDATE Usuario
        SET estado = 'Eliminado'
        WHERE id_usuario = %s
    """

    cursor.execute(sql, (id_usuario,))
    conexion.commit()

    eliminado = cursor.rowcount > 0

    cursor.close()
    conexion.close()

    return eliminado


def iniciar_sesion(credencial, clave):
    print(f"\n[DEBUG] Intentando login con credencial: '{credencial}' y clave: '{clave}'")
    
    usuario = buscar_usuario_por_credencial(credencial)

    if usuario is None:
        print("[DEBUG] ERROR: El usuario o correo NO existe en la base de datos.")
        return False

    print(f"[DEBUG] Usuario encontrado: {usuario['nombre_usuario']}")
    print(f"[DEBUG] Hash en DB: {usuario['clave']}")

    coincide = check_password_hash(usuario["clave"], clave)
    print(f"[DEBUG] ¿La contraseña coincide?: {coincide}")

    if not coincide:
        print("[DEBUG] ERROR: La contraseña no coincide con el hash.")
        return False

    usuario.pop("clave", None)
    return usuario