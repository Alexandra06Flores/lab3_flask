import re
from flask import (Blueprint, flash, redirect, render_template,
                   request, session, url_for)
from psycopg2 import errors
from werkzeug.security import generate_password_hash

from .auth import admin_required, login_required
from .db import get_connection

panel_bp = Blueprint("panel", __name__)
ROLES = ("admin", "usuario")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASS = 6


def validar(nombre, email, rol, password, es_nuevo):
    if not nombre or not email or not rol:
        return "Nombre, correo y rol son obligatorios."
    if not EMAIL_RE.match(email):
        return "El correo no tiene un formato válido."
    if rol not in ROLES:
        return "Rol inválido."
    if es_nuevo and not password:
        return "La contraseña es obligatoria."
    if password and len(password) < MIN_PASS:
        return f"La contraseña debe tener al menos {MIN_PASS} caracteres."
    return None


def obtener_usuario(id_):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nombre, email, rol FROM usuarios WHERE id = %s", (id_,))
            return cur.fetchone()
    finally:
        conn.close()


# LEER: lo pueden ver admin y usuario
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
    return render_template("panel.html", nombre=session.get("nombre"),
                           rol=session.get("rol"), usuarios=usuarios)


# CREAR: solo admin
@panel_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        rol = request.form.get("rol", "")
        password = request.form.get("password", "")
        datos = {"nombre": nombre, "email": email, "rol": rol}

        error = validar(nombre, email, rol, password, es_nuevo=True)
        if error:
            flash(error, "error")
            return render_template("usuario_form.html", titulo="Nuevo usuario",
                                   u=datos, roles=ROLES, es_nuevo=True)

        conn = get_connection()
        try:
            with conn, conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuarios (nombre, email, rol, password_hash) VALUES (%s, %s, %s, %s)",
                    (nombre, email, rol, generate_password_hash(password)),
                )
        except errors.UniqueViolation:
            flash("Ya existe un usuario con ese correo.", "error")
            return render_template("usuario_form.html", titulo="Nuevo usuario",
                                   u=datos, roles=ROLES, es_nuevo=True)
        finally:
            conn.close()

        flash("Usuario creado correctamente.", "ok")
        return redirect(url_for("panel.panel"))

    return render_template("usuario_form.html", titulo="Nuevo usuario",
                           u={"nombre": "", "email": "", "rol": "usuario"},
                           roles=ROLES, es_nuevo=True)


# ACTUALIZAR: solo admin
@panel_bp.route("/usuarios/<int:id_>/editar", methods=["GET", "POST"])
@admin_required
def editar(id_):
    existente = obtener_usuario(id_)
    if existente is None:
        flash("El usuario no existe.", "error")
        return redirect(url_for("panel.panel"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        rol = request.form.get("rol", "")
        password = request.form.get("password", "")
        datos = {"nombre": nombre, "email": email, "rol": rol}

        error = validar(nombre, email, rol, password, es_nuevo=False)
        if not error and id_ == session.get("user_id") and rol != "admin":
            error = "No puedes quitarte el rol admin a ti mismo."
        if error:
            flash(error, "error")
            return render_template("usuario_form.html", titulo="Editar usuario",
                                   u=datos, roles=ROLES, es_nuevo=False)

        conn = get_connection()
        try:
            with conn, conn.cursor() as cur:
                if password:
                    cur.execute(
                        "UPDATE usuarios SET nombre = %s, email = %s, rol = %s, password_hash = %s WHERE id = %s",
                        (nombre, email, rol, generate_password_hash(password), id_),
                    )
                else:
                    cur.execute(
                        "UPDATE usuarios SET nombre = %s, email = %s, rol = %s WHERE id = %s",
                        (nombre, email, rol, id_),
                    )
        except errors.UniqueViolation:
            flash("Ya existe un usuario con ese correo.", "error")
            return render_template("usuario_form.html", titulo="Editar usuario",
                                   u=datos, roles=ROLES, es_nuevo=False)
        finally:
            conn.close()

        flash("Usuario actualizado correctamente.", "ok")
        return redirect(url_for("panel.panel"))

    return render_template("usuario_form.html", titulo="Editar usuario",
                           u=existente, roles=ROLES, es_nuevo=False)


# ELIMINAR: solo admin, solo por POST
@panel_bp.route("/usuarios/<int:id_>/eliminar", methods=["POST"])
@admin_required
def eliminar(id_):
    if id_ == session.get("user_id"):
        flash("No puedes eliminar tu propia cuenta.", "error")
        return redirect(url_for("panel.panel"))

    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("DELETE FROM usuarios WHERE id = %s", (id_,))
    finally:
        conn.close()
    flash("Usuario eliminado.", "ok")
    return redirect(url_for("panel.panel"))