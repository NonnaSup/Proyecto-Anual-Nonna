from flask import Flask, request, jsonify

from modules.usuario import (
    crear_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario
)


"""
from modules.receta import (
    
)
"""

""""
from modules.negocio import (
    
)
"""

"""
from modules.moderacion import (
    
)
"""

from modules.empleo import (
    crear_oferta
)

app = Flask(__name__)

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ---------------------------------USUARIO.PY---------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------

# -----------------------------------------
# RUTA PRINCIPAL
# -----------------------------------------

@app.route("/")
def inicio():
    return "NONNA funcionando correctamente"


# -----------------------------------------
# CREAR USUARIO
# -----------------------------------------

@app.route("/nuevo_usuario", methods=["POST"])
def nuevo_usuario():

    datos = request.get_json()

    nombre = datos.get("nombre")
    nombre_usuario = datos.get("nombre_usuario")
    correo = datos.get("correo")
    clave = datos.get("clave")
    fecha_nacimiento = datos.get("fecha_nacimiento")

    if not nombre or not nombre_usuario or not correo or not clave or not fecha_nacimiento:

        return jsonify({
            "error": "Faltan datos obligatorios"
        }), 400

    try:

        creado = crear_usuario(
            nombre,
            nombre_usuario,
            correo,
            clave,
            fecha_nacimiento
        )

        if creado:

            return jsonify({
                "resultado": "Agregado nuevo usuario"
            }), 201

        return jsonify({
            "resultado": "No se pudo crear el usuario"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------------------
# LISTAR USUARIOS
# -----------------------------------------

@app.route("/traer_usuarios", methods=["GET"])
def traer_usuarios():

    try:

        usuarios = listar_usuarios()

        return jsonify(usuarios), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------------------
# BUSCAR USUARIO POR ID
# -----------------------------------------

@app.route("/buscar_usuario/<int:id_usuario>", methods=["GET"])
def buscar_usuario(id_usuario):

    try:

        usuario = buscar_usuario_por_id(id_usuario)

        if usuario is None:

            return jsonify({
                "resultado": "Usuario no encontrado"
            }), 404

        return jsonify(usuario), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------------------
# ACTUALIZAR USUARIO
# -----------------------------------------

@app.route("/actualizar_usuario/<int:id_usuario>", methods=["PUT"])
def actualizar_usuario_api(id_usuario):

    datos = request.get_json()

    nombre = datos.get("nombre")
    biografia = datos.get("biografia")

    if not nombre:

        return jsonify({
            "error": "El nombre es obligatorio"
        }), 400

    try:

        usuario = buscar_usuario_por_id(id_usuario)

        if usuario is None:

            return jsonify({
                "resultado": "Usuario no encontrado"
            }), 404

        actualizado = actualizar_usuario(
            id_usuario,
            nombre,
            biografia
        )

        if actualizado:

            return jsonify({
                "resultado": "Usuario actualizado"
            }), 200

        return jsonify({
            "resultado": "No se pudo actualizar el usuario"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------------------
# ELIMINAR USUARIO
# -----------------------------------------

@app.route("/eliminar_usuario/<int:id_usuario>", methods=["DELETE"])
def eliminar_usuario_api(id_usuario):

    try:

        usuario = buscar_usuario_por_id(id_usuario)

        if usuario is None:

            return jsonify({
                "resultado": "Usuario no encontrado"
            }), 404

        eliminado = eliminar_usuario(id_usuario)

        if eliminado:

            return jsonify({
                "resultado": "Usuario eliminado"
            }), 200

        return jsonify({
            "resultado": "No se pudo eliminar el usuario"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500





# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ---------------------------------NEGOCIO.PY---------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------


































# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ---------------------------------EMPLEO.PY---------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
@app.route("/nuevo_empleo", methods=["POST"])
def nuevo_empleo():

    datos = request.get_json()

    puesto = datos.get("puesto")
    descripcion = datos.get("descripcion")
    jornada = datos.get("jornada")
    vacantes = datos.get("vacantes")
    
    try:

        creado = crear_oferta(
            puesto,
            descripcion,
            jornada,
            vacantes,
        )

        if creado:

            return jsonify({
                "resultado": "Guardada en borrador"
            }), 201

        return jsonify({
            "resultado": "No se pudo crear la oferta"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
































# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# --------------------------------MODERACION.PY---------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------





































# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ---------------------------------RECETA.PY---------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------


















# -----------------------------------------
# EJECUCIÓN LOCAL
# -----------------------------------------

if __name__ == "__main__":
    app.run(debug=True)