from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Habilita CORS para responder al cliente Ionic en localhost o producción
CORS(app, resources={r"/*": {"origins": "*"}})
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "imagenes")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from modules.usuario import (
    crear_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario,
    iniciar_sesion
)

from modules.usuario_google import (
    buscar_usuario_google_por_uid,
    buscar_usuario_google_por_correo,
    buscar_usuario_normal_por_correo,
    crear_usuario_google,
    actualizar_ultimo_inicio_sesion_google,
    completar_usuario_google

)

from modules.receta import (
    crear_receta,
    listar_recetas_previa,
    reaccionar_receta,
    traer_receta
)

from modules.negocio import (
    crear_negocio,
    crear_sucursal,
    buscar_casa_central
)

from modules.empleo import (
    crear_oferta,
    crear_oferta_borrador,
    buscar_oferta_por_id,
    actualizar_borrador,
    buscar_borradores,
    listar_ofertas,
    listar_ofertas_activas,
    eliminar_oferta
)

# -----------------------------------------
# RUTA PRINCIPAL
# -----------------------------------------

@app.route("/")
def inicio():
    return "NONNA funcionando correctamente"

# -----------------------------------------
# USUARIO
# -----------------------------------------

@app.route("/nuevo_usuario", methods=["POST"])
def nuevo_usuario():
    datos = request.get_json() or {}
    nombre = datos.get("nombre")
    nombre_usuario = datos.get("nombre_usuario")
    correo = datos.get("correo")
    clave = datos.get("clave")
    fecha_nacimiento = datos.get("fecha_nacimiento")

    if not nombre or not nombre_usuario or not correo or not clave or not fecha_nacimiento:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        creado = crear_usuario(nombre, nombre_usuario, correo, clave, fecha_nacimiento)
        if creado:
            return jsonify({"resultado": "Agregado nuevo usuario"}), 201
        return jsonify({"resultado": "No se pudo crear el usuario"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/iniciar_sesion", methods=["POST", "OPTIONS"])
def iniciar_sesion_api():
    if request.method == "OPTIONS":
        return "", 200

    datos = request.get_json() or {}
    correo = datos.get("correo")  # Puede ser el correo o el nombre de usuario
    clave = datos.get("clave")

    if not correo or not clave:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        usuario = iniciar_sesion(correo, clave)
        if usuario:
            return jsonify({
                "resultado": "Sesion iniciada",
                "usuario": usuario
            }), 200

        return jsonify({"error": "Correo/Usuario o contraseña incorrectos"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------------------
# INICIO DE SESIÓN CON GOOGLE
# -----------------------------------------

@app.route("/iniciar_sesion_google", methods=["POST", "OPTIONS"])
def iniciar_sesion_google_api():

    if request.method == "OPTIONS":
        return "", 200

    datos = request.get_json() or {}

    firebase_uid = datos.get("firebase_uid")
    nombre = datos.get("nombre")
    correo = datos.get("correo")
    foto_perfil = datos.get("foto_perfil")
    confirmar_google = datos.get("confirmar_google", False)

    if not firebase_uid or not nombre or not correo:
        return jsonify({
            "error": "Faltan datos obligatorios"
        }), 400

    try:

        usuario_google = buscar_usuario_google_por_uid(firebase_uid)

        if usuario_google:

            actualizar_ultimo_inicio_sesion_google(firebase_uid)

            return jsonify({
                "resultado": "Sesion iniciada con Google",
                "usuario_google": usuario_google
            }), 200

        usuario_google_correo = buscar_usuario_google_por_correo(correo)

        if usuario_google_correo:

            actualizar_ultimo_inicio_sesion_google(
                usuario_google_correo["firebase_uid"]
            )

            return jsonify({
                "resultado": "Sesion iniciada con Google",
                "usuario_google": usuario_google_correo
            }), 200

        usuario_normal = buscar_usuario_normal_por_correo(correo)

        if usuario_normal and not confirmar_google:

            return jsonify({
                "resultado": "correo_existente",
                "mensaje": "Este correo ya existe en Nonna, ¿querés proceder con Google?"
            }), 200

        id_usuario_google = crear_usuario_google(
            firebase_uid,
            nombre,
            correo,
            foto_perfil
        )

        return jsonify({
            "resultado": "Usuario Google creado",
            "id_usuario_google": id_usuario_google
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
        
@app.route('/completar_usuario_google', methods=['POST'])
def completar_usuario_google_route():

    datos = request.get_json()

    if not datos:
        return jsonify({
            "error": "No se recibieron datos"
        }), 400

    firebase_uid = datos.get("firebase_uid")
    nombre_usuario = datos.get("nombre_usuario")
    fecha_nacimiento = datos.get("fecha_nacimiento")

    # ------------------------------------------
    # Validar datos
    # ------------------------------------------

    if not firebase_uid:
        return jsonify({
            "error": "Falta firebase_uid"
        }), 400

    if not nombre_usuario:
        return jsonify({
            "error": "Falta nombre_usuario"
        }), 400

    if not fecha_nacimiento:
        return jsonify({
            "error": "Falta fecha_nacimiento"
        }), 400

    try:

        # ------------------------------------------
        # Completar usuario
        # ------------------------------------------

        id_usuario = completar_usuario_google(
            firebase_uid,
            nombre_usuario,
            fecha_nacimiento
        )

        if id_usuario is None:
            return jsonify({
                "error": "No existe el usuario de Google"
            }), 404

        return jsonify({
            "mensaje": "Usuario completado correctamente",
            "id_usuario": id_usuario
        }), 200

    except Exception as e:

        print("ERROR AL COMPLETAR USUARIO GOOGLE:", e)

        return jsonify({
            "error": "Error al completar usuario"
        }), 500
    

@app.route("/traer_usuarios", methods=["GET"])
def traer_usuarios():
    try:
        usuarios = listar_usuarios()
        return jsonify(usuarios), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/buscar_usuario/<int:id_usuario>", methods=["GET"])
def buscar_usuario(id_usuario):
    try:
        usuario = buscar_usuario_por_id(id_usuario)
        if usuario is None:
            return jsonify({"resultado": "Usuario no encontrado"}), 404
        return jsonify(usuario), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/actualizar_usuario/<int:id_usuario>", methods=["PUT"])
def actualizar_usuario_api(id_usuario):
    datos = request.get_json() or {}
    nombre = datos.get("nombre")
    biografia = datos.get("biografia")

    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400

    try:
        usuario = buscar_usuario_por_id(id_usuario)
        if usuario is None:
            return jsonify({"resultado": "Usuario no encontrado"}), 404

        actualizado = actualizar_usuario(id_usuario, nombre, biografia)
        if actualizado:
            return jsonify({"resultado": "Usuario actualizado"}), 200
        return jsonify({"resultado": "No se pudo actualizar el usuario"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/eliminar_usuario/<int:id_usuario>", methods=["DELETE"])
def eliminar_usuario_api(id_usuario):
    try:
        usuario = buscar_usuario_por_id(id_usuario)
        if usuario is None:
            return jsonify({"resultado": "Usuario no encontrado"}), 404

        eliminado = eliminar_usuario(id_usuario)
        if eliminado:
            return jsonify({"resultado": "Usuario eliminado"}), 200
        return jsonify({"resultado": "No se pudo eliminar el usuario"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------
# NEGOCIO
# -----------------------------------------

@app.route("/nuevo_negocio", methods=["POST"])
def nuevo_negocio():
    datos = request.get_json() or {}
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
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        creado = crear_negocio(
            id_usuario, nombre_comercial, descripcion, logo,
            portada, telefono, correo, sitio_web, redes_sociales
        )
        if creado:
            return jsonify({"resultado": "Agregado nuevo negocio"}), 201
        return jsonify({"resultado": "No se pudo crear el negocio"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/nueva_sucursal", methods=["POST"])
def nueva_sucursal():
    datos = request.get_json() or {}
    id_negocio = datos.get("id_negocio")
    nombre = datos.get("nombre")
    direccion = datos.get("direccion")
    horarios = datos.get("horarios")
    casa_central = int(datos.get("casa_central", 0))

    try:
        buscar = buscar_casa_central(id_negocio)
        if buscar and casa_central == 1:
            return jsonify({"error": "Ya hay una casa central"}), 400

        creado = crear_sucursal(id_negocio, nombre, direccion, horarios, casa_central)
        if creado:
            return jsonify({"resultado": "Agregada nueva sucursal"}), 201
        return jsonify({"resultado": "No se pudo crear la sucursal"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------
# EMPLEO
# -----------------------------------------

@app.route("/nuevo_empleo", methods=["POST"])
def nuevo_empleo():
    datos = request.get_json() or {}
    id_negocio = datos.get("id_negocio")
    id_sucursal = datos.get("id_sucursal")
    puesto = datos.get("puesto")
    descripcion = datos.get("descripcion")
    jornada = datos.get("jornada")
    vacantes = datos.get("vacantes")

    try:
        creado = crear_oferta(id_negocio, id_sucursal, puesto, descripcion, jornada, vacantes)
        if creado:
            return jsonify({"resultado": "Oferta subida"}), 201
        return jsonify({"resultado": "No se pudo crear la oferta"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/nuevo_empleo_borrador", methods=["POST"])
def nuevo_empleo_borrador():
    datos = request.get_json() or {}
    id_negocio = datos.get("id_negocio")
    id_sucursal = datos.get("id_sucursal")
    puesto = datos.get("puesto")
    descripcion = datos.get("descripcion")
    jornada = datos.get("jornada")
    vacantes = datos.get("vacantes")

    try:
        creado = crear_oferta_borrador(id_negocio, id_sucursal, puesto, descripcion, jornada, vacantes)
        if creado:
            return jsonify({"resultado": "Guardada en borrador"}), 201
        return jsonify({"resultado": "No se pudo crear la oferta"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/subir_borrador/<int:id_oferta>", methods=["PUT"])
def subir_borrador(id_oferta):
    datos = request.get_json() or {}
    puesto = datos.get("puesto")
    descripcion = datos.get("descripcion")
    jornada = datos.get("jornada")
    vacantes = datos.get("vacantes")

    try:
        oferta = buscar_oferta_por_id(id_oferta)
        if oferta is None:
            return jsonify({"resultado": "Oferta no encontrada"}), 404

        actualizado = actualizar_borrador(id_oferta, puesto, descripcion, jornada, vacantes)
        if actualizado:
            return jsonify({"resultado": "Borrador subido"}), 200
        return jsonify({"resultado": "No se pudo subir el borrador"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/mostrar_borradores/<int:id_usuario>", methods=["GET"])
def mostrar_borradores(id_usuario):
    try:
        usuario = buscar_usuario_por_id(id_usuario)
        if usuario is None:
            return jsonify({"resultado": "Usuario no encontrado"}), 404

        borrador = buscar_borradores(id_usuario)
        if borrador is None:
            return jsonify({"resultado": "Sin borradores"}), 404

        return jsonify(borrador), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/traer_ofertas", methods=["GET"])
def traer_ofertas():
    try:
        ofertas = listar_ofertas()
        return jsonify(ofertas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/traer_ofertas_activas", methods=["GET"])
def traer_ofertas_activas():
    try:
        ofertas = listar_ofertas_activas()
        return jsonify(ofertas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/eliminar_oferta/<int:id_oferta>", methods=["DELETE"])
def eliminar_oferta_api(id_oferta):
    try:
        oferta = buscar_oferta_por_id(id_oferta)
        if oferta is None:
            return jsonify({"resultado": "Oferta no encontrada"}), 404

        eliminado = eliminar_oferta(id_oferta)
        if eliminado:
            return jsonify({"resultado": "Oferta eliminada"}), 200
        return jsonify({"resultado": "No se pudo eliminar la oferta"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------
# RECETA
# -----------------------------------------

@app.route("/nueva_receta", methods=["POST"])
def nueva_receta():
    id_usuario = request.form.get("id_usuario")
    titulo = request.form.get("titulo")
    descripcion = request.form.get("descripcion")
    tiempo_preparacion = request.form.get("tiempo_preparacion")
    porciones = request.form.get("porciones")

    try:
        pasos = json.loads(request.form.get("pasos", "[]"))
        ingredientes = json.loads(request.form.get("ingredientes", "[]"))
    except (TypeError, json.JSONDecodeError):
        return jsonify({"error": "Formato inválido en pasos o ingredientes"}), 400

    imagenes = []
    archivos = request.files.getlist("imagenes")

    for indice, archivo in enumerate(archivos):
        if archivo and archivo.filename:
            nombre_seguro = secure_filename(archivo.filename)
            nombre_unico = f"{uuid.uuid4().hex}_{nombre_seguro}"
            archivo.save(os.path.join(UPLOAD_FOLDER, nombre_unico))

            imagenes.append({
                "ruta": f"/static/imagenes/{nombre_unico}",
                "principal": 1 if indice == 0 else 0,
                "orden": indice + 1
            })

    try:
        receta = crear_receta(
            id_usuario, titulo, descripcion, tiempo_preparacion,
            porciones, pasos, ingredientes, imagenes
        )
        if receta:
            return jsonify({"resultado": "receta subida", "id_receta": receta}), 201
        return jsonify({"resultado": "No se pudo crear la receta"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/recetas_previa", methods=["GET"])
def recetas_previa():

    try:

        id_usuario = request.args.get("id_usuario", type=int)

        recetas = listar_recetas_previa(id_usuario)

        resultado = []

        for receta in recetas:

            resultado.append({
                "id_receta": receta[0],
                "id_usuario": receta[1],
                "titulo": receta[2],
                "descripcion": receta[3],
                "nombre_usuario": receta[4],
                "foto_perfil": receta[5],
                "id_imagen": receta[6],
                "imagen_principal": receta[7],
                "likes": receta[8],
                "dislikes": receta[9],
                "comentarios": receta[10],
                "mi_reaccion": receta[11]
            })

        return jsonify(resultado), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/receta_amplia", methods=["GET"])
def receta_amplia():

    try:

        id_receta = request.args.get("id_receta", type=int)

        if id_receta is None:
            return jsonify({
                "error": "Falta el id_receta"
            }), 400

        receta = traer_receta(id_receta)

        return jsonify(receta), 200

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

        

@app.route("/reaccionar_receta", methods=["POST"])
def reaccionar_receta_api():

    datos = request.get_json() or {}
    id_usuario = datos.get("id_usuario")
    id_receta = datos.get("id_receta")
    like = datos.get("like")

    if id_usuario is None or id_receta is None or like is None:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        resultado = reaccionar_receta(id_usuario, id_receta, like)
        return jsonify({"resultado": resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)