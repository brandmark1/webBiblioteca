-- Crear la tabla de Categoría
CREATE TABLE Categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT NOT NULL
);

-- Crear la tabla de Usuario
CREATE TABLE Usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE
);

-- Crear la tabla de Libro
CREATE TABLE Libro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    categoria_id INTEGER NOT NULL,
    fecha_publicacion DATE NOT NULL,
    usuario_id INTEGER,
    FOREIGN KEY (categoria_id) REFERENCES Categoria(id),
    FOREIGN KEY (usuario_id) REFERENCES Usuario(id)
);
