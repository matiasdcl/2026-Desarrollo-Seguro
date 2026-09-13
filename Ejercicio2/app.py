from flask import Flask, render_template, request, g, redirect, url_for, session
import sqlite3
from config import Config
from functools import wraps
import os

app = Flask(__name__)
app.config.from_object(Config)

ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'changeme')
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('usuario') == ADMIN_USER and request.form.get('password') == ADMIN_PASS:
            session['logueado'] = True
            return redirect(url_for('index'))
        error = 'Usuario o contraseña incorrectos'
    return f'''
        <form method="post">
            <input name="usuario" placeholder="usuario"><br>
            <input name="password" type="password" placeholder="password"><br>
            <button type="submit">Entrar</button>
        </form>
        {"<p style='color:red'>" + error + "</p>" if error else ""}
    '''

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def buscar_funciones(query, sort_by='nombre', sort_dir='ASC'):
    db = get_db()

    columnas_validas = {'nombre': 'peliculas.nombre', 'fecha': 'funciones.fecha_hora'}
    sort_by = columnas_validas.get(sort_by, 'peliculas.nombre')
    sort_dir = 'ASC' if sort_dir.upper() != 'DESC' else 'DESC'

    sql = ("SELECT peliculas.nombre as pelicula, funciones.fecha_hora, "
           "(funciones.asientos_totales - funciones.asientos_ocupados) as disponibles, "
           "peliculas.descripcion as descripcion, peliculas.id as id "
           "FROM funciones "
           "JOIN peliculas ON funciones.pelicula_id = peliculas.id "
           "WHERE peliculas.nombre LIKE ? "
           f"ORDER BY {sort_by} {sort_dir}")

    return db.execute(sql, (f'%{query}%',)).fetchall()

@app.route('/')
def index():
    query = request.args.get('buscar', '')
    sort_by = request.args.get('ordenar_por', 'nombre')
    sort_dir = request.args.get('sentido', 'ASC')
    resultados = []
    if query:
        resultados = buscar_funciones(query, sort_by, sort_dir)
    return render_template(
        'index.html',
        resultados=resultados,
        query=query,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

@app.route('/edit/<int:pelicula_id>', methods=['GET'])
@login_required
def edit_get(pelicula_id):
    db = get_db()
    pelicula = db.execute(
        'SELECT * FROM peliculas WHERE id = ?', (pelicula_id,)
    ).fetchone()
    return render_template('edit.html', pelicula=pelicula)

@app.route('/edit/<int:pelicula_id>', methods=['POST'])
@login_required
def edit_post(pelicula_id):
    nombre = request.form.get('nombre', '')
    genero = request.form.get('genero', '')
    director = request.form.get('director', '')
    descripcion = request.form.get('descripcion', '')

    db = get_db()
    db.execute(
        '''UPDATE peliculas
           SET nombre=?, genero=?, director=?, descripcion=?
           WHERE id=?''',
        (nombre, genero, director, descripcion, pelicula_id),
    )
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG_MODE', 'true').lower() in ('true', '1', 'yes')
    app.run(debug=debug, host=host)