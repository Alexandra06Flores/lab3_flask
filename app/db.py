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
    """Agrega la columna de contraseña si falta y deja al admin inicial como usuario admin."""
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        return
    email = email.strip().lower()
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_hash TEXT")
            cur.execute("SELECT id, password_hash FROM usuarios WHERE email = %s", (email,))
            fila = cur.fetchone()
            if fila is None:
                cur.execute(
                    "INSERT INTO usuarios (nombre, email, rol, password_hash) VALUES (%s, %s, 'admin', %s)",
                    ("Administrador", email, generate_password_hash(password)),
                )
            elif not fila["password_hash"]:
                cur.execute(
                    "UPDATE usuarios SET rol = 'admin', password_hash = %s WHERE id = %s",
                    (generate_password_hash(password), fila["id"]),
                )
    finally:
        conn.close()