import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5433"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor,
    )


def crear_admin_inicial():
    """Crea el admin de login la primera vez, con la contraseña hasheada."""
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        return
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT id FROM admins WHERE usuario = %s", ("admin",))
            if cur.fetchone() is None:
                cur.execute(
                    "INSERT INTO admins (usuario, email, password_hash) VALUES (%s, %s, %s)",
                    ("admin", email, generate_password_hash(password)),
                )
    finally:
        conn.close()