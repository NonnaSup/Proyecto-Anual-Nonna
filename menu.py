def menu_principal(usuario):

    while True:

        print("\n==============================")
        print(f" Bienvenido {usuario['nombre']}")
        print("==============================")
        print("1 - Perfil")
        print("2 - Recetas")
        print("3 - Negocios")
        print("4 - Empleo")
        print("0 - Cerrar sesión")

        opcion = input("\nSeleccione una opción: ")

        if opcion == "1":
            print("\n[Módulo Perfil próximamente]")

        elif opcion == "2":
            print("\n[Módulo Recetas próximamente]")

        elif opcion == "3":
            print("\n[Módulo Negocios próximamente]")

        elif opcion == "4":
            print("\n[Módulo Empleo próximamente]")

        elif opcion == "0":
            print("\nSesión cerrada.")
            break

        else:
            print("\nOpción inválida.")