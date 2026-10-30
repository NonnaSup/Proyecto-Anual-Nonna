import os
import time

import mysql.connector
from flask import Blueprint, request, jsonify

reinicio_bp = Blueprint('reinicio_clave', __name__)

# Límite de intentos por correo (se reinicia al redeployar el servidor)
MAX_INTENTOS = 5
VENTANA_SEGUNDOS = 15 * 60
intentos = {}


def conectar():
    # Si ya tenés tu propia función de conexión, usala en su lugar.
    # Estas variables las provee Railway automáticamente.
    return mysql.connector.connect(
        host=os.environ['MYSQLHOST'],
        user=os.environ['MYSQLUSER'],
        password=os.environ['MYSQLPASSWORD'],
        database=os.environ['MYSQLDATABASE'],
        port=int(os.environ.get('MYSQLPORT', 3306)),
    )


def demasiados_intentos(correo):
    ahora = time.time()
    recientes = [t for t in intentos.get(correo, []) if ahora - t < VENTANA_SEGUNDOS]
    intentos[correo] = recientes
    return len(recientes) >= MAX_INTENTOS


@reinicio_bp.route('/restablecer_clave', methods=['POST'])
def restablecer_clave():
    datos = request.get_json(silent=True) or {}
    correo = (datos.get('correo') or '').strip().lower()
    fecha_nacimiento = datos.get('fecha_nacimiento') or ''  # YYYY-MM-DD
    clave = datos.get('clave') or ''  # ya llega hasheada desde el front

    if not correo or not fecha_nacimiento or not clave:
        return jsonify({'error': 'Datos incompletos'}), 400

    if demasiados_intentos(correo):
        return jsonify({'error': 'Demasiados intentos. Probá de nuevo en 15 minutos.'}), 429

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    try:
        # Se cuenta el intento antes de verificar
        intentos.setdefault(correo, []).append(time.time())

        cursor.execute(
            'SELECT id_usuario FROM Usuario WHERE LOWER(correo) = %s AND fecha_nacimiento = %s',
            (correo, fecha_nacimiento),
        )
        usuario = cursor.fetchone()

        # Mensaje genérico: no revela si falló el correo o la fecha
        if not usuario:
            return jsonify({'error': 'Los datos no coinciden con ninguna cuenta.'}), 400

        cursor.execute('UPDATE Usuario SET clave = %s WHERE id_usuario = %s',
                       (clave, usuario['id_usuario']))
        conexion.commit()

        intentos.pop(correo, None)
        return jsonify({'mensaje': 'Contraseña actualizada. Ya podés iniciar sesión.'}), 200

    except Exception as e:
        conexion.rollback()
        print('Error en /restablecer_clave:', e)
        return jsonify({'error': 'No se pudo restablecer la contraseña'}), 500

    finally:
        cursor.close()
        conexion.close()