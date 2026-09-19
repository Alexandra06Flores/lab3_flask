# Laboratorio 3 - Flask

Aplicación web con Flask, PostgreSQL y Docker. Incluye inicio de sesión con código de verificación por correo y CRUD de usuarios con roles.

## Requisito

Tener Docker Desktop instalado y abierto.

## Antes de iniciar: configurar el correo

El inicio de sesión envía un código de 6 dígitos por correo, así que hay que configurar el correo **antes del primer inicio**.

1. En la carpeta del proyecto crea el archivo `.env` a partir de la plantilla:

```
Copy-Item .env.example .env
```

2. Abre `.env` y completa estos datos:

```
DB_USER=postgres
DB_PASSWORD=cambia_esto
DB_NAME=lab3
SECRET_KEY=una_clave_larga_y_aleatoria
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contrasena_de_aplicacion
ADMIN_EMAIL=tu_correo@gmail.com
ADMIN_PASSWORD=Admin123!
```

- `MAIL_USERNAME`: correo Gmail que **envía** el código.
- `MAIL_PASSWORD`: contraseña de aplicación de Gmail (16 letras, sin espacios), no tu contraseña normal. Se genera en https://myaccount.google.com/apppasswords (requiere verificación en dos pasos).
- `ADMIN_EMAIL`: correo del usuario administrador. Es el correo con el que iniciarás sesión y donde **llegará el código**, por lo que debe ser uno al que tengas acceso.
- `ADMIN_PASSWORD`: contraseña del administrador.

3. Guarda el archivo. `.env` contiene datos privados y no se sube a GitHub.

Si olvidaste hacerlo, no hay problema: edita `.env` y reinicia con `docker compose up --build`. Si cambiaste `ADMIN_EMAIL` o `ADMIN_PASSWORD` después del primer inicio, reinicia la base de datos con `docker compose down -v` y vuelve a levantar.

## Ejecutar la aplicación

1. Abre una terminal dentro de la carpeta del proyecto.
2. Ejecuta:

```
docker compose up --build
```

3. Espera a que Docker termine de iniciar los servicios (debe aparecer `Running on http://0.0.0.0:5000`).
4. Abre en el navegador:

```
http://localhost:5000
```

## Cuenta para probar el CRUD

```
Correo: el valor de ADMIN_EMAIL
Contraseña: el valor de ADMIN_PASSWORD
```

1. Ingresa el correo y la contraseña.
2. Revisa la bandeja de `ADMIN_EMAIL` (y Spam) e ingresa el código de 6 dígitos. Expira en 5 minutos.
3. Entrarás al panel con rol `admin`, que permite crear, editar y eliminar usuarios.

## Roles

- `admin`: ve el listado y puede crear, editar y eliminar usuarios.
- `usuario`: solo ve el listado, sin botones de crear, editar ni eliminar.

Los usuarios que el admin registre en el CRUD pueden iniciar sesión con su correo y la contraseña que se les asignó. El código de verificación llega al correo de cada uno.

## Base de datos

El script `db/init.sql` crea la tabla `usuarios` con datos de ejemplo y se ejecuta automáticamente la primera vez que se crea el contenedor de PostgreSQL. Al iniciar, la aplicación crea el usuario administrador definido en `ADMIN_EMAIL` y `ADMIN_PASSWORD`.

Para reiniciar la base de datos desde cero:

```
docker compose down -v
docker compose up --build
```

## Detener la aplicación

En la terminal presiona `Ctrl + C` y luego ejecuta:

```
docker compose down
```