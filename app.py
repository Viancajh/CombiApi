from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
from datetime import datetime, timedelta
import jwt
from simulador_combis import SimuladorCombis

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos y JWT
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Cambiar en producción

db = SQLAlchemy(app)

# Inicializar el simulador de combis
simulador = SimuladorCombis()

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Usuario {self.usuario}>'

# Crear las tablas de la base de datos
with app.app_context():
    if not os.path.exists(os.path.join(basedir, 'data')):
        os.makedirs(os.path.join(basedir, 'data'))
    db.create_all()

# Función para generar token JWT
def generar_token(usuario_id):
    try:
        token = jwt.encode(
            {
                'user_id': usuario_id,
                'exp': datetime.utcnow() + timedelta(hours=24)
            },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    except Exception as e:
        return None

# Decorador para verificar token
def token_required(f):
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token faltante'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token inválido'}), 401

        return f(current_user, *args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated

# Rutas de autenticación
@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['usuario', 'email', 'password']):
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    # Verificar si el usuario o email ya existen
    if Usuario.query.filter_by(usuario=data['usuario']).first():
        return jsonify({'success': False, 'message': 'El usuario ya existe'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'El email ya está registrado'}), 400
    
    # Encriptar contraseña
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), salt)
    
    # Crear nuevo usuario
    nuevo_usuario = Usuario(
        usuario=data['usuario'],
        email=data['email'],
        password=hashed.decode('utf-8')
    )
    
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Usuario registrado exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al registrar usuario'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'usuario' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
    
    # Buscar usuario
    usuario = Usuario.query.filter_by(usuario=data['usuario']).first()
    
    if usuario and bcrypt.checkpw(data['password'].encode('utf-8'), usuario.password.encode('utf-8')):
        # Generar token
        token = generar_token(usuario.id)
        
        return jsonify({
            'success': True,
            'message': 'Inicio de sesión exitoso',
            'token': token,
            'usuario': {
                'id': usuario.id,
                'usuario': usuario.usuario,
                'email': usuario.email
            }
        })
    
    return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'}), 401

# Ruta de prueba para verificar si el servidor está funcionando
@app.route('/')
def index():
    return jsonify({'message': 'Servidor funcionando correctamente'})

# Ruta para obtener posiciones de las combis
@app.route('/api/combis/posiciones')
@token_required
def posiciones_combis(current_user):
    return jsonify({'combis': simulador.obtener_estado_combis()})

if __name__ == '__main__':
    app.run(debug=True)
