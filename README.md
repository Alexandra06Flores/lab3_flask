# Lab 3 - Aplicación Flask (Login + CRUD de usuarios)

Aplicación web con Flask y PostgreSQL:

- Login con usuario y contraseña validados contra la base de datos.
- Código de verificación de 6 dígitos enviado al correo (expira en 5 minutos).
- Panel de administración con CRUD completo de usuarios (crear, listar, editar y eliminar con confirmación).
- Despliegue con Docker.

## Requisitos

- Docker Desktop instalado y abierto.
- Una cuenta de correo con contraseña de aplicación (Gmail: verificación en dos pasos y luego https://myaccount.google.com/apppasswords).

## Estructura

```
lab3_flask/
├── app/
│   ├── __init__.py
│   ├── auth.py        # login y verificación por correo
│   ├── db.py          # conexión a PostgreSQL
│   ├── panel.py       # CRUD de usuarios
│   ├── static/style.css
│   └── templates/
├── db/init.sql        # tablas y datos de ejemplo
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run.py
└── .env.example
```

## Instalación y ejecución

1. Clona el repositorio y entra a la carpeta:

```powershell
git clone URL_DEL_REPOSITORIO
cd lab3_flask
```

2. Crea tu archivo `.env` a partir de la plantilla y complétalo con tus datos:

```powershell
copy .env.example .env
```

- `MAIL_USERNAME`: correo que envía el código.
- `MAIL_PASSWORD`: contraseña de aplicación de 16 letras, sin espacios.
- `ADMIN_EMAIL`: correo donde llegará el código de verificación.
- `ADMIN_PASSWORD`: contraseña del usuario `admin`.

3. Levanta la aplicación:

```powershell
docker compose up --build
```

4. Abre http://localhost:5000

## Uso

- Usuario: `admin`
- Contraseña: la definida en `ADMIN_PASSWORD`
- Después del login, ingresa el código de 6 dígitos recibido por correo.

## Base de datos

El script `db/init.sql` crea las tablas `admins` (login) y `usuarios` (CRUD) y se ejecuta automáticamente la primera vez que se crea el contenedor de PostgreSQL. Para reiniciar la base desde cero:

```powershell
docker compose down -v
docker compose up --build
```

## Detener la aplicación

```powershell
docker compose down
```