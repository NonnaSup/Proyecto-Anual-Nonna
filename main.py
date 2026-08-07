from menu import menu_principal
from modules.usuario import crear_usuario
from modules.usuario import iniciar_sesion

while True:

    print("\n========================")
    print("        NONNA")
    print("========================")
    print("1 - Registrarse")
    print("2 - Iniciar sesión")
    print("0 - Salir")

    opcion = input("\nSeleccione una opción: ")

    if opcion == "1":

        nombre = input("Nombre: ")
        usuario = input("Usuario: ")
        correo = input("Correo: ")
        clave = input("Contraseña: ")
        nacimiento = input("Fecha nacimiento (AAAA-MM-DD): ")

        crear_usuario(
            nombre,
            usuario,
            correo,
            clave,
            nacimiento
        )

        print("\nUsuario registrado correctamente.")

    elif opcion == "2":

        correo = input("Correo: ")
        clave = input("Contraseña: ")

        usuario = iniciar_sesion(correo, clave)

        if usuario:

            print("\nInicio de sesión exitoso.")
            menu_principal(usuario)

        else:

            print("\nCorreo o contraseña incorrectos.")

    elif opcion == "0":

        print("\nHasta luego.")
        break

    else:

        print("\nOpción inválida.")