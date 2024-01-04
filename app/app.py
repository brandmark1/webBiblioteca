from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, Email
from flask_paginate import Pagination
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@127.0.0.1/biblioteca'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Funciones de conexión y consulta
def conectar_base_datos():
    try:
        db_config = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': '',
            'database': 'biblioteca',
        }
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print(f"Conexión establecida a la base de datos: {db_config['database']}")
            return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def cerrar_conexion(connection):
    if connection.is_connected():
        connection.close()
        print("Conexión cerrada")

def obtener_libros(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Libro")
        libros = cursor.fetchall()
        return libros
    except Error as e:
        print(f"Error al obtener libros: {e}")
        return None
    finally:
        cursor.close()

def obtener_categorias(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Categoria")
        categorias = cursor.fetchall()
        return categorias
    except Error as e:
        print(f"Error al obtener categorías: {e}")
        return None
    finally:
        cursor.close()

def obtener_usuarios(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Usuario")
        usuarios = cursor.fetchall()
        return usuarios
    except Error as e:
        print(f"Error al obtener usuarios: {e}")
        return None
    finally:
        cursor.close()
        

# Definir modelos
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    correo_electronico = db.Column(db.String(255), unique=True, nullable=False)

class Libro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    fecha_publicacion = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    categoria = db.relationship('Categoria', backref=db.backref('libros', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('libros_prestados', lazy=True))

# Formulario para Libro
class LibroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    autor = StringField('Autor', validators=[DataRequired()])
    categoria_id = StringField('Categoría ID', validators=[DataRequired()])
    fecha_publicacion = DateField('Fecha de Publicación (YYYY-MM-DD)', validators=[DataRequired()])

# Formulario para Categoría
class CategoriaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    descripcion = StringField('Descripción', validators=[DataRequired()])

# Formulario para Usuario
class UsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    correo_electronico = StringField('Correo Electrónico', validators=[DataRequired(), Email()])

# Resto del código Flask
# ... (operaciones CRUD y rutas)
# Rutas CRUD
@app.route('/')
def index():
    connection = conectar_base_datos()
    if connection:
        try:
            libros = obtener_libros(connection)
            print("Libros:")
            for libro in libros:
                print(libro)

            categorias = obtener_categorias(connection)
            print("\nCategorías:")
            for categoria in categorias:
                print(categoria)

            usuarios = obtener_usuarios(connection)
            print("\nUsuarios:")
            for usuario in usuarios:
                print(usuario)

        finally:
            cerrar_conexion(connection)

    # Resto del código de la ruta index
    page = request.args.get('page', 1, type=int)
    per_page = 5
    libros = Libro.query.paginate(page=page, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=libros.total, record_name='libros')
    return render_template('index.html', libros=libros, pagination=pagination)

#codigo para crear la lista libro, categorias y usuarios
@app.route('/libro/create', methods=['GET', 'POST'])
def create_libro():
    form = LibroForm()
    if form.validate_on_submit():
        libro = Libro(
            nombre=form.nombre.data,
            autor=form.autor.data,
            categoria_id=form.categoria_id.data,
            fecha_publicacion=form.fecha_publicacion.data
        )
        db.session.add(libro)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_libro.html', form=form)

@app.route('/categoria/create', methods=['GET', 'POST'])
def create_categoria():
    form = CategoriaForm()
    if form.validate_on_submit():
        categoria = Categoria(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data
        )
        db.session.add(categoria)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_categoria.html', form=form)

@app.route('/usuario/create', methods=['GET', 'POST'])
def create_usuario():
    form = UsuarioForm()
    if form.validate_on_submit():
        usuario = Usuario(
            nombre=form.nombre.data,
            correo_electronico=form.correo_electronico.data
        )
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_usuario.html', form=form)

#Este apartado es para edictar la lista de libro, categoria y usuarios

@app.route('/libro/edit/<int:id>', methods=['GET', 'POST'])
def edit_libro(id):
    libro = Libro.query.get(id)
    form = LibroForm(obj=libro)
    if form.validate_on_submit():
        libro.nombre = form.nombre.data
        libro.autor = form.autor.data
        libro.categoria_id = form.categoria_id.data
        libro.fecha_publicacion = form.fecha_publicacion.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_libro.html', form=form, libro=libro)

@app.route('/categoria/edit/<int:id>', methods=['GET', 'POST'])
def edit_categoria(id):
    categoria = Categoria.query.get(id)
    form = CategoriaForm(obj=categoria)
    if form.validate_on_submit():
        categoria.nombre = form.nombre.data
        categoria.descripcion = form.descripcion.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_categoria.html', form=form, categoria=categoria)

@app.route('/usuario/edit/<int:id>', methods=['GET', 'POST'])
def edit_usuario(id):
    usuario = Usuario.query.get(id)
    form = UsuarioForm(obj=usuario)
    if form.validate_on_submit():
        usuario.nombre = form.nombre.data
        usuario.correo_electronico = form.correo_electronico.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_usuario.html', form=form, usuario=usuario)

#Este apartado es para eliminar lista la lista de libro, categoria y usuarios

@app.route('/libro/delete/<int:id>')
def delete_libro(id):
    libro = Libro.query.get(id)
    db.session.delete(libro)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/categoria/delete/<int:id>')
def delete_categoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/usuario/delete/<int:id>')
def delete_usuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

