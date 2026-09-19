import secrets
import time
from functools import wraps

from flask import (Blueprint, flash, redirect, render_template,
                   request, session, url_for)
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash

from . import mail
from .db import get_connection

auth_bp = Blueprint("auth", __name__)
CODIGO_TTL = 300  # segundos (5 minutos)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logueado"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logueado"):
            return redirect(url_for("auth.login"))
        if session.get("rol") != "admin":
            flash("No tienes permiso para hacer esto.", "error")
            return redirect(url_for("panel.panel"))
        return f(*args, **kwargs)
    return wrapper


def enmascarar(email):
    nombre, dominio = email.split("@", 1)
    return f"{nombre[0]}***@{dominio}"


@auth_bp.route("/")
def inicio():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Completa correo y contraseña.", "error")
            return render_template("login.html")

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nombre, email, rol, password_hash FROM usuarios WHERE email = %s",
                    (email,),
                )
                usuario = cur.fetchone()
        finally:
            conn.close()

        if (usuario is None or not usuario["password_hash"]
                or not check_password_hash(usuario["password_hash"], password)):
            flash("Correo o contraseña incorrectos.", "error")
            return render_template("login.html")

        # Credenciales OK: generar y enviar el código al correo del usuario
        codigo = f"{secrets.randbelow(10**6):06d}"
        msg = Message("Tu código de verificación", recipients=[usuario["email"]])
        msg.body = f"Tu código de verificación es: {codigo}\nExpira en 5 minutos."
        try:
            mail.send(msg)
        except Exception as e:
            print("ERROR MAIL:", repr(e), flush=True)
            flash("No se pudo enviar el correo. Revisa MAIL_USERNAME y MAIL_PASSWORD en el .env.", "error")
            return render_template("login.html")

        session.clear()
        session["pendiente"] = {
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "rol": usuario["rol"],
        }
        session["codigo_hash"] = generate_password_hash(codigo)
        session["expira"] = time.time() + CODIGO_TTL
        session["email_oculto"] = enmascarar(usuario["email"])
        return redirect(url_for("auth.verificar"))

    return render_template("login.html")


@auth_bp.route("/verificar", methods=["GET", "POST"])
def verificar():
    if "codigo_hash" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        ingresado = request.form.get("codigo", "").strip()

        if time.time() > session["expira"]:
            session.clear()
            flash("El código expiró. Inicia sesión de nuevo.", "error")
            return redirect(url_for("auth.login"))

        if not check_password_hash(session["codigo_hash"], ingresado):
            flash("Código incorrecto.", "error")
            return render_template("verificar.html", email=session["email_oculto"])

        datos = session["pendiente"]
        session.clear()
        session["logueado"] = True
        session["user_id"] = datos["id"]
        session["nombre"] = datos["nombre"]
        session["rol"] = datos["rol"]
        return redirect(url_for("panel.panel"))

    return render_template("verificar.html", email=session["email_oculto"])


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))