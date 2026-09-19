CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    rol VARCHAR(10) NOT NULL CHECK (rol IN ('admin', 'usuario')),
    password_hash TEXT
);

INSERT INTO usuarios (nombre, email, rol) VALUES
    ('Ana Torres', 'ana@example.com', 'admin'),
    ('Luis Perez', 'luis@example.com', 'usuario');