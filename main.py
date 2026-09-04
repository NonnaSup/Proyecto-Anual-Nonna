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

from modules.receta import (
    crear_receta,
    crear_pasos_ingredientes_imagen
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


if __name__ == "__main__":
    app.run(debug=True)