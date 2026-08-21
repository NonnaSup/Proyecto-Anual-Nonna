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


from modules.negocio import (
    crear_negocio,
    crear_sucursal,
    buscar_casa_central
)

"""
from modules.moderacion import (
    
)
"""

from modules.empleo import (
    crear_oferta,
    crear_oferta_borrador,
    buscar_oferta_por_id,
    subir_borrador,
    buscar_borradores,
    listar_ofertas,
    listar_ofertas_activas,
    eliminar_oferta
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
@app.route("/nuevo_negocio", methods=["POST"])
def nuevo_negocio():

    datos = request.get_json()


    id_usuario = datos.get("id_usuario")
    nombre_comercial = datos.get("nombre_comercial")
    descripcion = datos.get("descripcion")
    logo = datos.get("logo")
    portada = datos.get("portada")
    telefono = datos.get("telefono")
    correo = datos.get("correo")
    sitio_web = datos.get("sitio_web")
    redes_sociales = datos.get("redes_sociales")

    if not id_usuario or not nombre_comercial or not telefono or not correo:

        return jsonify({
            "error": "Faltan datos obligatorios"
        }), 400

    try:

        creado = crear_negocio(
            id_usuario,
            nombre_comercial,
            descripcion,
            logo,
            portada,
            telefono,
            correo,
            sitio_web,
            redes_sociales
        )

        if creado:

            return jsonify({
                "resultado": "Agregado nuevo negocio"
            }), 201

        return jsonify({
            "resultado": "No se pudo crear el negocio"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/nueva_sucursal", methods=["POST"])
def nueva_sucursal():

    datos = request.get_json()
    
    id_negocio = datos.get("id_negocio")
    nombre = datos.get("nombre")
    direccion = datos.get("direccion")
    horarios = datos.get("horarios")
    casa_central = datos.get("casa_central")

    try:
        buscar = buscar_casa_central(id_negocio)

        if buscar is True and casa_central is True:
            return jsonify({
                "error": "Ya hay una casa central"
            }), 400
        
        creado = crear_sucursal(
            id_negocio,
            nombre,
            direccion,
            horarios,
            casa_central 
        )

        if creado:

            return jsonify({
                "resultado": "Agregada nueva sucursal"
            }), 201

        return jsonify({
            "resultado": "No se pudo crear la sucursal"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

































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
                "resultado": "Oferta subida"
            }), 201

        return jsonify({
            "resultado": "No se pudo crear la oferta"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/nuevo_empleo_borrador", methods=["POST"])
def nuevo_empleo_borrador():

    datos = request.get_json()

    puesto = datos.get("puesto")
    descripcion = datos.get("descripcion")
    jornada = datos.get("jornada")
    vacantes = datos.get("vacantes")
    
    try:

        creado = crear_oferta_borrador(
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


@app.route("/subir_borrador/<int:id_oferta>", methods=["PUT"])
def subir_borrador(id_oferta):

    datos = request.get_json()

    puesto = datos.get("puesto")
    descripcion = datos.get("descripcion")
    jornada = datos.get("jornada")
    vacantes = datos.get("vacantes")

    try:

        oferta = buscar_oferta_por_id(id_oferta)

        if oferta is None:

            return jsonify({
                "resultado": "Oferta no encontrada"
            }), 404

        actualizado = subir_borrador(id_oferta, puesto, descripcion, jornada, vacantes)

        if actualizado:

            return jsonify({
                "resultado": "Borrador subido"
            }), 200

        return jsonify({
            "resultado": "No se pudo subir el borrador"
        }), 400

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/mostrar_borradores/<int:id_usuario>", methods=["GET"])
def mostrar_borradores(id_usuario):

    try:

        usuario = buscar_usuario_por_id(id_usuario)

        if usuario is None:

            return jsonify({
                "resultado": "Usuario no encontrado"
            }), 404
        
        borrador = buscar_borradores(id_usuario)
        
        if borrador is None:
        
            return jsonify({
                "resultado": "Sin borradores"
            }), 404

        return jsonify(borrador), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/traer_ofertas", methods=["GET"])
def traer_ofertas():

    try:

        ofertas = listar_ofertas()

        return jsonify(ofertas), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/traer_ofertas_activas", methods=["GET"])
def traer_ofertas_activas():

    try:

        ofertas = listar_ofertas_activas()

        return jsonify(ofertas), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/eliminar_oferta/<int:id_usuario>", methods=["DELETE"])
def eliminar_oferta(id_oferta):

    try:

        oferta = buscar_oferta_por_id(id_oferta)

        if oferta is None:

            return jsonify({
                "resultado": "Oferta no encontrada"
            }), 404

        eliminado = eliminar_oferta(id_oferta)

        if eliminado:

            return jsonify({
                "resultado": "Oferta eliminada"
            }), 200

        return jsonify({
            "resultado": "No se pudo eliminar la oferta"
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