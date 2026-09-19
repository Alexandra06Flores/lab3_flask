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


def enmascarar(email):
    nombre, dominio = email.split("@", 1)
    return f"{nombre[0]}***@{dominio}"


@auth_bp.route("/")
def inicio():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        if not usuario or not password:
            flash("Completa usuario y contraseña.", "error")
            return render_template("login.html")

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM admins WHERE usuario = %s", (usuario,))
                admin = cur.fetchone()
        finally:
            conn.close()

        if admin is None or not check_password_hash(admin["password_hash"], password):
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template("login.html")

        # Credenciales OK: generar y enviar el código al correo
        codigo = f"{secrets.randbelow(10**6):06d}"
        msg = Message("Tu código de verificación", recipients=[admin["email"]])
        msg.body = f"Tu código de verificación es: {codigo}\nExpira en 5 minutos."
        try:
            mail.send(msg)
        except Exception as e:
            print("ERROR MAIL:", repr(e), flush=True)
            flash("No se pudo enviar el correo. Revisa MAIL_USERNAME y MAIL_PASSWORD en el .env.", "error")
            return render_template("login.html")

        session.clear()
        session["pendiente"] = admin["usuario"]
        session["codigo_hash"] = generate_password_hash(codigo)
        session["expira"] = time.time() + CODIGO_TTL
        session["email_oculto"] = enmascarar(admin["email"])
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

        usuario = session["pendiente"]
        session.clear()
        session["logueado"] = True
        session["usuario"] = usuario
        return redirect(url_for("panel.panel"))

    return render_template("verificar.html", email=session["email_oculto"])


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))