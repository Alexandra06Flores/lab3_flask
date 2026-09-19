import re
from flask import (Blueprint, flash, redirect, render_template,
                   request, session, url_for)
from psycopg2 import errors

from .auth import login_required
from .db import get_connection

panel_bp = Blueprint("panel", __name__)
ROLES = ("admin", "usuario")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar(nombre, email, rol):
    if not nombre or not email or not rol:
        return "Todos los campos son obligatorios."
    if not EMAIL_RE.match(email):
        return "El correo no tiene un formato válido."
    if rol not in ROLES:
        return "Rol inválido."
    return None


def obtener_usuario(id_):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre, email, rol FROM usuarios WHERE id = %s", (id_,))
            return cur.fetchone()
    finally:
        conn.close()


# LEER: listado de todos los usuarios
@panel_bp.route("/panel")
@login_required
def panel():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre, email, rol FROM usuarios ORDER BY id")
            usuarios = cur.fetchall()
    finally:
        conn.close()
    return render_template("panel.html", usuario=session.get("usuario"), usuarios=usuarios)


# CREAR
@panel_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        rol = request.form.get("rol", "")
        datos = {"nombre": nombre, "email": email, "rol": rol}

        error = validar(nombre, email, rol)
        if error:
            flash(error, "error")
            return render_template("usuario_form.html", titulo="Nuevo usuario", u=datos, roles=ROLES)

        conn = get_connection()
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuarios (nombre, email, rol) VALUES (%s, %s, %s)",
                    (nombre, email, rol),
                )
        except errors.UniqueViolation:
            flash("Ya existe un usuario con ese correo.", "error")
            return render_template("usuario_form.html", titulo="Nuevo usuario", u=datos, roles=ROLES)
        finally:
            conn.close()

        flash("Usuario creado correctamente.", "ok")
        return redirect(url_for("panel.panel"))

    return render_template("usuario_form.html", titulo="Nuevo usuario",
                           u={"nombre": "", "email": "", "rol": "usuario"}, roles=ROLES)


# ACTUALIZAR
@panel_bp.route("/usuarios/<int:id_>/editar", methods=["GET", "POST"])
@login_required
def editar(id_):
    existente = obtener_usuario(id_)
    if existente is None:
        flash("El usuario no existe.", "error")
        return redirect(url_for("panel.panel"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        rol = request.form.get("rol", "")
        datos = {"nombre": nombre, "email": email, "rol": rol}

        error = validar(nombre, email, rol)
        if error:
            flash(error, "error")
            return render_template("usuario_form.html", titulo="Editar usuario", u=datos, roles=ROLES)

        conn = get_connection()
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    "UPDATE usuarios SET nombre = %s, email = %s, rol = %s WHERE id = %s",
                    (nombre, email, rol, id_),
                )
        except errors.UniqueViolation:
            flash("Ya existe un usuario con ese correo.", "error")
            return render_template("usuario_form.html", titulo="Editar usuario", u=datos, roles=ROLES)
        finally:
            conn.close()

        flash("Usuario actualizado correctamente.", "ok")
        return redirect(url_for("panel.panel"))

    return render_template("usuario_form.html", titulo="Editar usuario", u=existente, roles=ROLES)


# ELIMINAR (solo por POST, con confirmación en el botón)
@panel_bp.route("/usuarios/<int:id_>/eliminar", methods=["POST"])
@login_required
def eliminar(id_):
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM usuarios WHERE id = %s", (id_,))
    finally:
        conn.close()
    flash("Usuario eliminado.", "ok")
    return redirect(url_for("panel.panel"))