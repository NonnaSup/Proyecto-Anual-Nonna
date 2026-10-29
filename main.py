from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import uuid
from werkzeug.utils import secure_filename
from modules import interaccion
from modules import interaccion as inter
from modules import moderacion as mod
from mysql.connector import IntegrityError

app = Flask(__name__)

# Habilita CORS para responder al cliente Ionic en localhost o producción
CORS(app, resources={r"/*": {"origins": "*"}})
# En Railway, apuntar a una carpeta dentro de un volumen persistente.
UPLOAD_FOLDER = os.path.abspath(os.environ.get(
    "UPLOAD_FOLDER", os.path.join(app.root_path, "static", "imagenes")
))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/static/imagenes/<path:nombre>")
def servir_imagen(nombre):
    # send_from_directory impide salir de la carpeta mediante ../.
    return send_from_directory(UPLOAD_FOLDER, nombre)


from modules.usuario import (
    crear_usuario,
    listar_usuarios,
    buscar_usuario_por_id,
    actualizar_usuario,
    eliminar_usuario,
    iniciar_sesion,
    obtener_perfil,
    actualizar_perfil
)


from modules.usuario_google import (
    buscar_usuario_google_por_uid,
    buscar_usuario_google_por_correo,
    buscar_usuario_normal_por_correo,
    crear_usuario_google,
    actualizar_ultimo_inicio_sesion_google,
    completar_usuario_google,
    vincular_usuario_google

)

from modules.receta import (
    crear_receta,
    listar_recetas_previa,
    reaccionar_receta,
    traer_receta,
    listar_mis_recetas,
    editar_receta,
    eliminar_receta
)

from modules.negocio import (
    crear_negocio,
    crear_sucursal,
    buscar_casa_central,
    listar_mis_negocios,
    listar_negocios,
    listar_productos_activos,
    crear_producto,
    listar_productos_negocio,
    actualizar_perfil as actualizar_perfil_negocio,
    obtener_perfil_negocio,
    negocio_es_de_usuario,
    eliminar_negocio
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

        # -----------------------------------------
        # 1. Buscar por UID de Firebase
        # -----------------------------------------

        usuario_google = buscar_usuario_google_por_uid(firebase_uid)

        if usuario_google:

            actualizar_ultimo_inicio_sesion_google(firebase_uid)

            # -----------------------------------------
            # ¿Ya tiene usuario normal asociado?
            # -----------------------------------------

            if usuario_google["id_usuario"] is None:

                return jsonify({
                    "resultado": "completar_perfil",
                    "usuario_google": usuario_google
                }), 200

            # -----------------------------------------
            # Ya completó el perfil
            # -----------------------------------------

            return jsonify({
                "resultado": "Sesion iniciada con Google",
                "usuario_google": usuario_google,
                "id_usuario": usuario_google["id_usuario"]
            }), 200


        # -----------------------------------------
        # 2. Buscar Google por correo
        # -----------------------------------------

        usuario_google_correo = buscar_usuario_google_por_correo(correo)

        if usuario_google_correo:

            actualizar_ultimo_inicio_sesion_google(
                usuario_google_correo["firebase_uid"]
            )

            if usuario_google_correo["id_usuario"] is None:

                return jsonify({
                    "resultado": "completar_perfil",
                    "usuario_google": usuario_google_correo
                }), 200

            return jsonify({
                "resultado": "Sesion iniciada con Google",
                "usuario_google": usuario_google_correo,
                "id_usuario": usuario_google_correo["id_usuario"]
            }), 200


        # -----------------------------------------
        # 3. Buscar usuario normal por correo
        # -----------------------------------------

        usuario_normal = buscar_usuario_normal_por_correo(correo)


        # ==========================================
        # CORREO YA EXISTE EN UNA CUENTA NORMAL
        # ==========================================

        if usuario_normal and not confirmar_google:

            return jsonify({
                "resultado": "correo_existente",
                "mensaje": "Este correo ya existe en Nonna, ¿querés vincular tu cuenta con Google?"
            }), 200


        # ==========================================
        # CONFIRMÓ VINCULAR GOOGLE
        # ==========================================

        if usuario_normal and confirmar_google:

            id_usuario = usuario_normal["id_usuario"]

            # Crear registro de Google
            id_usuario_google = crear_usuario_google(
                firebase_uid,
                nombre,
                correo,
                foto_perfil
            )

            # Vincular Google con el usuario normal existente
            vinculado = vincular_usuario_google(
                firebase_uid,
                id_usuario
            )

            if not vinculado:

                return jsonify({
                    "error": "No se pudo vincular la cuenta de Google"
                }), 500

            return jsonify({
                "resultado": "Sesion iniciada con Google",
                "id_usuario": id_usuario,
                "id_usuario_google": id_usuario_google
            }), 200


        # ==========================================
        # NUEVO USUARIO GOOGLE
        # ==========================================

        id_usuario_google = crear_usuario_google(
            firebase_uid,
            nombre,
            correo,
            foto_perfil
        )

        return jsonify({
            "resultado": "completar_perfil",
            "id_usuario_google": id_usuario_google
        }), 201


    except Exception as e:

        print("ERROR LOGIN GOOGLE:", e)

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
        codigo_error = e.args[0] if e.args else None
        detalle_error = str(e)

        print(f"Error al registrar negocio: {detalle_error}")

        # Error SIGNAL de MySQL generado por un trigger.
        if codigo_error == 1644:
            return jsonify({
                "resultado": "limite_alcanzado",
                "mensaje": (
                    "¡Tu emprendimiento ya tiene su lugar en La Nonna! "
                    "Cada usuario puede registrar hasta 2 negocios."
                )
            }), 409

        return jsonify({
            "resultado": "error",
            "mensaje": (
                "No pudimos registrar tu negocio. "
                "Por favor, intentá nuevamente."
            )
        }), 500


@app.route("/traer_negocios", methods=["GET"])
def traer_negocios():
    try:
        negocios = listar_negocios()

        # Publicaciones de cada negocio = sus productos activos (maximo 3)
        publicaciones = {}

        try:
            for producto in listar_productos_activos():
                lista = publicaciones.setdefault(producto["id_negocio"], [])

                if len(lista) < 3:
                    precio = producto["precio"]

                    lista.append({
                        "id_producto": producto["id_producto"],
                        "nombre": producto["nombre"],
                        "descripcion": producto["descripcion"],
                        "precio": float(precio) if precio is not None else None,
                        "destacado": bool(producto["destacado"]),
                        "imagen": producto["imagen"]
                    })
        except Exception:
            # si fallan las publicaciones, igual se muestran los negocios
            app.logger.exception("Error al traer las publicaciones de los negocios")

        for negocio_fila in negocios:
            negocio_fila["publicaciones"] = publicaciones.get(
                negocio_fila["id_negocio"], []
            )

        return jsonify(negocios), 200

    except Exception:
        app.logger.exception("Error al listar los negocios")
        return jsonify({"error": "No se pudieron obtener los negocios"}), 500


@app.route("/traer_negocios_perfil/<int:id_usuario>", methods=["GET"])
def traer_negocios_perfil(id_usuario):
    try:
        negocios = listar_mis_negocios(id_usuario)
        return jsonify(negocios), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/perfil_negocio/<int:id_negocio>", methods=["GET"])
def perfil_negocio_obtener_api(id_negocio):
    id_usuario = request.args.get("id_usuario", type=int)

    if id_usuario is None:
        return jsonify({
            "error": "Falta el identificador del usuario"
        }), 400

    try:
        negocio = obtener_perfil_negocio(id_negocio)

        if negocio is None:
            return jsonify({
                "error": "Negocio no encontrado"
            }), 404

        if int(negocio["id_usuario"]) != id_usuario:
            return jsonify({
                "error": "No tenés permiso para acceder a este negocio"
            }), 403

        return jsonify(negocio), 200

    except Exception as e:
        app.logger.exception("Error al obtener el perfil del negocio")
        return jsonify({
            "error": "No se pudo obtener el perfil del negocio"
        }), 500


# -----------------------------------------
# EDITAR Y ELIMINAR NEGOCIO
# -----------------------------------------

EXTENSIONES_IMAGEN = {"jpg", "jpeg", "png", "webp"}


def guardar_imagen_negocio(archivo):
    # Si no se envio archivo devuelve None (se conserva la imagen anterior).
    # Si el archivo no es una imagen permitida lanza ValueError.
    if archivo is None or not archivo.filename:
        return None

    nombre_seguro = secure_filename(archivo.filename)
    extension = nombre_seguro.rsplit(".", 1)[-1].lower() if "." in nombre_seguro else ""

    if extension not in EXTENSIONES_IMAGEN:
        raise ValueError("La imagen debe ser JPG, PNG o WEBP")

    nombre_unico = f"{uuid.uuid4().hex}_{nombre_seguro}"
    archivo.save(os.path.join(UPLOAD_FOLDER, nombre_unico))

    # mismo formato de ruta que usan las imagenes de las recetas
    return f"/static/imagenes/{nombre_unico}"


@app.route("/negocio/<int:id_negocio>", methods=["PUT"])
def negocio_editar_api(id_negocio):
    id_usuario = request.form.get("id_usuario", type=int)

    if id_usuario is None:
        return jsonify({"error": "Falta el identificador del usuario"}), 400

    nombre_comercial = request.form.get("nombre_comercial", "").strip()
    telefono = request.form.get("telefono", "").strip()
    correo = request.form.get("correo", "").strip()

    if not nombre_comercial or not telefono or not correo:
        return jsonify({
            "error": "Nombre comercial, teléfono y correo son obligatorios"
        }), 400

    try:
        # Solo el dueño puede modificar su negocio
        if not negocio_es_de_usuario(id_negocio, id_usuario):
            return jsonify({
                "error": "No tenés permiso para modificar este negocio"
            }), 403

        actual = obtener_perfil_negocio(id_negocio)

        # Si no se subio una imagen nueva, se conserva la anterior
        logo = guardar_imagen_negocio(request.files.get("logo")) or actual["logo"]
        portada = guardar_imagen_negocio(request.files.get("portada")) or actual["portada"]

        actualizar_perfil_negocio(
            id_negocio,
            nombre_comercial,
            request.form.get("descripcion", "").strip() or None,
            logo,
            portada,
            telefono,
            correo,
            request.form.get("sitio_web", "").strip() or None,
            request.form.get("redes_sociales", "").strip() or None
        )

        return jsonify({"resultado": "Negocio actualizado"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        return jsonify({"error": "Ya existe un negocio con esos datos"}), 409
    except Exception:
        app.logger.exception("Error al actualizar el negocio")
        return jsonify({"error": "No se pudo actualizar el negocio"}), 500


@app.route("/negocio/<int:id_negocio>", methods=["DELETE"])
def negocio_eliminar_api(id_negocio):
    id_usuario = request.args.get("id_usuario", type=int)

    if id_usuario is None:
        return jsonify({"error": "Falta el identificador del usuario"}), 400

    try:
        # Solo el dueño puede eliminar su negocio
        if not negocio_es_de_usuario(id_negocio, id_usuario):
            return jsonify({
                "error": "No tenés permiso para eliminar este negocio"
            }), 403

        if eliminar_negocio(id_negocio):
            return jsonify({"resultado": "Negocio eliminado"}), 200

        return jsonify({"error": "No se pudo eliminar el negocio"}), 400

    except Exception:
        app.logger.exception("Error al eliminar el negocio")
        return jsonify({"error": "No se pudo eliminar el negocio"}), 500


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








@app.route("/nuevo_producto", methods=["POST"])
def nuevo_producto():
    try:
        id_usuario = request.form.get("id_usuario")
        id_negocio = request.form.get("id_negocio")
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        precio_texto = request.form.get("precio")

        # Validar campos obligatorios
        if not id_usuario or not id_negocio or not nombre or not precio_texto:
            return jsonify({
                "resultado": "error",
                "mensaje": "Completá los campos obligatorios."
            }), 400

        try:
            id_usuario = int(id_usuario)
            id_negocio = int(id_negocio)
            precio = float(precio_texto)
        except (ValueError, TypeError):
            return jsonify({
                "resultado": "error",
                "mensaje": "Los datos ingresados no son válidos."
            }), 400

        if precio < 0:
            return jsonify({
                "resultado": "error",
                "mensaje": "El precio no puede ser negativo."
            }), 400

        # Verificar que el negocio pertenezca al usuario
        if not negocio_es_de_usuario(id_negocio, id_usuario):
            return jsonify({
                "resultado": "error",
                "mensaje": "No tenés permiso para agregar productos a este negocio."
            }), 403

        # Guardar imagen opcional
        archivo = request.files.get("imagen")
        ruta_imagen = guardar_imagen_negocio(archivo) if archivo else None

        # Crear producto
        resultado = crear_producto(
            id_negocio=id_negocio,
            nombre=nombre,
            descripcion=descripcion or None,
            precio=precio,
            imagen=ruta_imagen
        )

        if not resultado:
            return jsonify({
                "resultado": "error",
                "mensaje": "No se pudo crear el producto."
            }), 500

        return jsonify({
            "resultado": "ok",
            "mensaje": "Producto creado correctamente.",
            "id_producto": resultado
        }), 201

    except ValueError as e:
        return jsonify({
            "resultado": "error",
            "mensaje": str(e)
        }), 400

    except Exception as e:
        print("Error al crear producto:", e)
        return jsonify({
            "resultado": "error",
            "mensaje": "Ocurrió un error al crear el producto."
        }), 500



@app.route("/productos_negocio/<int:id_negocio>", methods=["GET"])
def productos_negocio(id_negocio):
    try:
        productos = listar_productos_negocio(id_negocio)

        return jsonify({
            "resultado": "ok",
            "productos": productos
        }), 200

    except Exception as e:
        print("Error al listar productos del negocio:", e)
        return jsonify({
            "resultado": "error",
            "mensaje": "No se pudieron cargar los productos."
        }), 500


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

@app.route("/subir_receta", methods=["POST"])
def subir_receta():
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

        app.logger.info(
            "Solicitando recetas previas. id_usuario=%s",
            id_usuario
        )

        recetas = listar_recetas_previa(id_usuario)

        resultado = []

        for receta in recetas:
            ingredientes = receta[12]
            if isinstance(ingredientes, (bytes, bytearray)):
                ingredientes =ingredientes.decode("utf-8")
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
                "mi_reaccion": receta[11],
                "ingredientes": ingredientes.split("||") if ingredientes else [],
                "tiempo_preparacion": receta[13]
            })

        return jsonify(resultado), 200

    except Exception as e:
        app.logger.exception(
            "Error al obtener las recetas previas"
        )

        return jsonify({
            "error": "No se pudieron obtener las recetas previas",
            "detalle": str(e)
        }), 500


@app.route("/receta_amplia", methods=["GET"])
def receta_amplia():

    id_receta = request.args.get("id_receta", type=int)

    if id_receta is None:
        return jsonify({
            "error": "Falta el id_receta"
        }), 400

    try:
        receta = traer_receta(id_receta)

        if receta is None:
            return jsonify({
                "error": "Receta no encontrada"
            }), 404

        return jsonify(receta), 200

    except Exception as e:
        app.logger.exception("Error al obtener la receta")

        return jsonify({
            "error": "No se pudo obtener la receta",
            "detalle": str(e)
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


# -----------------------------------------
# PERFIL
# -----------------------------------------

@app.route("/perfil/<int:id_usuario>", methods=["GET"])
def perfil_obtener_api(id_usuario):
    try:
        perfil = obtener_perfil(id_usuario)
        if perfil is None:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(perfil), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/perfil/<int:id_usuario>", methods=["PUT"])
def perfil_actualizar_api(id_usuario):
    datos = request.get_json() or {}
    nombre = datos.get("nombre")
    nombre_usuario = datos.get("nombre_usuario")
    correo = datos.get("correo")
    fecha_nacimiento = datos.get("fecha_nacimiento")
    biografia = datos.get("biografia")

    if not nombre or not nombre_usuario or not correo or not fecha_nacimiento:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        actualizar_perfil(id_usuario, nombre, nombre_usuario, correo, fecha_nacimiento, biografia)
        return jsonify({"resultado": "Perfil actualizado"}), 200
    except IntegrityError:
        return jsonify({"error": "El nombre de usuario o el correo ya están en uso"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/mis_recetas/<int:id_usuario>", methods=["GET"])
def mis_recetas_api(id_usuario):
    try:
        return jsonify(listar_mis_recetas(id_usuario)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/receta/<int:id_receta>", methods=["PUT"])
def receta_editar_api(id_receta):
    datos = request.get_json() or {}
    id_usuario = datos.get("id_usuario")
    titulo = datos.get("titulo")
    descripcion = datos.get("descripcion")
    tiempo_preparacion = datos.get("tiempo_preparacion")
    porciones = datos.get("porciones")

    if not id_usuario or not titulo:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        editar_receta(id_receta, id_usuario, titulo, descripcion, tiempo_preparacion, porciones)
        return jsonify({"resultado": "Receta actualizada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/receta/<int:id_receta>", methods=["DELETE"])
def receta_eliminar_api(id_receta):
    id_usuario = request.args.get("id_usuario", type=int)

    if id_usuario is None:
        return jsonify({"error": "Falta el id_usuario"}), 400

    try:
        eliminado = eliminar_receta(id_receta, id_usuario)
        if eliminado:
            return jsonify({"resultado": "Receta eliminada"}), 200
        return jsonify({"resultado": "No se pudo eliminar la receta"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500







@app.route('/estado_interaccion/<int:id_receta>/<int:id_usuario>', methods=['GET'])
def api_inter_estado(id_receta, id_usuario):
    try:
        return jsonify(inter.estado_interaccion(id_receta, id_usuario))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reaccionar', methods=['POST'])
def api_inter_reaccionar():
    try:
        datos = request.get_json()
        return jsonify(inter.reaccionar(datos["id_usuario"], datos["id_receta"], datos["like"]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/comentarios/<int:id_receta>', methods=['GET'])
def api_inter_comentarios(id_receta):
    try:
        return jsonify(inter.listar_comentarios(id_receta))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/comentar', methods=['POST'])
def api_inter_comentar():
    try:
        datos = request.get_json()
        return jsonify(inter.comentar(datos["id_usuario"], datos["id_receta"], datos["texto"]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/guardar', methods=['POST'])
def api_inter_guardar():
    try:
        datos = request.get_json()
        return jsonify(inter.guardar(datos["id_usuario"], datos["id_receta"]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/recetas_con_dislike/<int:id_usuario>', methods=['GET'])
def api_inter_recetas_con_dislike(id_usuario):
    try:
        return jsonify(inter.recetas_con_dislike(id_usuario))
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# -----------------------------------------
# MODERACIÓN (solo administradores)
# -----------------------------------------

def _rechazar_si_no_admin(id_usuario):
    # Devuelve la respuesta 403 si quien llama no es administrador; None si puede seguir.
    # shortcut: el id_usuario lo manda el cliente (igual que el resto de la API), no hay token; agregar JWT/sesión antes de producción.
    if id_usuario is None or not mod.es_admin(id_usuario):
        return jsonify({"error": "No tenés permiso de administrador"}), 403


@app.get("/moderacion/denuncias")
def moderacion_listar_api():
    id_usuario = request.args.get("id_usuario", type=int)
    rechazo = _rechazar_si_no_admin(id_usuario)
    if rechazo:
        return rechazo

    try:
        return jsonify(mod.listar_denuncias()), 200
    except Exception:
        app.logger.exception("Error al listar las denuncias")
        return jsonify({"error": "No se pudieron obtener las denuncias"}), 500


@app.put("/moderacion/denuncias/<int:id_denuncia>")
def moderacion_estado_api(id_denuncia):
    datos = request.get_json() or {}
    estado = datos.get("estado")

    rechazo = _rechazar_si_no_admin(datos.get("id_usuario"))
    if rechazo:
        return rechazo

    if estado not in mod.ESTADOS:
        return jsonify({"error": "Estado inválido"}), 400

    try:
        if mod.buscar_denuncia(id_denuncia) is None:
            return jsonify({"error": "Denuncia no encontrada"}), 404

        mod.cambiar_estado(id_denuncia, estado)
        return jsonify({"resultado": "Denuncia actualizada"}), 200
    except Exception:
        app.logger.exception("Error al actualizar la denuncia")
        return jsonify({"error": "No se pudo actualizar la denuncia"}), 500


@app.delete("/moderacion/denuncias/<int:id_denuncia>/contenido")
def moderacion_eliminar_api(id_denuncia):
    rechazo = _rechazar_si_no_admin(request.args.get("id_usuario", type=int))
    if rechazo:
        return rechazo

    try:
        denuncia = mod.buscar_denuncia(id_denuncia)
        if denuncia is None:
            return jsonify({"error": "Denuncia no encontrada"}), 404

        mod.eliminar_contenido(denuncia, id_denuncia)
        return jsonify({"resultado": "Contenido eliminado"}), 200
    except Exception:
        app.logger.exception("Error al eliminar el contenido denunciado")
        return jsonify({"error": "No se pudo eliminar el contenido"}), 500


# -----------------------------------------
# DENUNCIAR (cualquier usuario)
# -----------------------------------------

@app.post("/denunciar")
def denunciar_api():
    datos = request.get_json() or {}
    id_usuario = datos.get("id_usuario")
    tipo = datos.get("tipo_contenido")
    id_contenido = datos.get("id_contenido")
    motivo = (datos.get("motivo") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()[:500]

    if not isinstance(id_usuario, int) or not isinstance(id_contenido, int) or not motivo:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    if tipo not in mod.TIPOS_DENUNCIABLES:
        return jsonify({"error": "Tipo de contenido inválido"}), 400

    if tipo == "Cuenta" and id_contenido == id_usuario:
        return jsonify({"error": "No podés reportar tu propia cuenta"}), 400

    try:
        if not mod.crear_denuncia(id_usuario, tipo, id_contenido, motivo[:100], descripcion):
            return jsonify({"error": "Ya reportaste este contenido"}), 409

        return jsonify({"resultado": "Denuncia enviada"}), 201
    except Exception:
        app.logger.exception("Error al crear la denuncia")
        return jsonify({"error": "No se pudo enviar el reporte"}), 500


if __name__ == "__main__":
    app.run(debug=True)