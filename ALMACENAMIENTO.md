# Im?genes persistentes

Las im?genes se guardan en la carpeta indicada por `UPLOAD_FOLDER`.
Sin esa variable, se usa `static/imagenes` junto a `main.py`, para desarrollo local.
Las direcciones p?blicas siguen siendo `/static/imagenes/<nombre>`.

## Railway

1. En el servicio del backend, crear un volumen y montarlo en `/data`.
2. Agregar la variable `UPLOAD_FOLDER=/data/imagenes` en ese servicio.
3. Redesplegar el backend para aplicar la configuraci?n.
4. Restaurar las im?genes originales en `/data/imagenes`, conservando sus nombres completos (incluido el prefijo UUID).
5. Abrir una direcci?n de imagen devuelta por `/recetas_previa` y comprobar que responde correctamente.

La base de datos guarda rutas, no el contenido de los archivos. Un volumen nuevo no recupera im?genes perdidas: hay que restaurarlas desde una copia o volver a subirlas. Descargar el repositorio tampoco descarga los archivos que se subieron al servidor.

Antes de cambiar de carpeta, respaldar y copiar las im?genes existentes al volumen. No borrar el volumen al redesplegar. Las im?genes nuevas se guardar?n y servir?n desde la carpeta configurada.
