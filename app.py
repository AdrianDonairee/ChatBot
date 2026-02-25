"""
Aplicación principal Flask para ChatBot de turnos.

Este módulo crea y configura la aplicación Flask con:
- API REST para gestión de turnos
- Base de datos SQLAlchemy
- CORS para frontend
- Configuración via variables de entorno
"""
from flask import Flask
from api import chat_blueprint, db
try:
    from flask_cors import CORS
except ImportError:
    CORS = None

import os

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv no instalado, usar solo variables de entorno del sistema
    pass

def create_app():
    """
    Factory function para crear la aplicación Flask.
    
    Returns:
        Flask: Aplicación configurada y lista para usar
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Carga configuración desde variables de entorno o archivo
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-cambiar-en-produccion')
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Intenta cargar configuración desde instance/config.py (opcional)
    try:
        app.config.from_pyfile('instance/config.py')
    except FileNotFoundError:
        pass

    # Configuración de base de datos
    instance_db_path = os.path.join(app.instance_path, 'appointments.db')
    default_db_uri = f"sqlite:///{instance_db_path}"
    app.config.setdefault(
        'SQLALCHEMY_DATABASE_URI',
        os.getenv('DATABASE_URL', default_db_uri)
    )
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # Habilitar CORS para el frontend si está disponible
    if CORS:
        CORS(app)
    
    # Inicializar DB
    db.init_app(app)
    # Asegurar que exista la carpeta instance y crear tablas
    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()

    app.register_blueprint(chat_blueprint, url_prefix='/chat')
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Configuración desde variables de entorno
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Bind to 0.0.0.0 so the app is reachable from Docker/container network
    app.run(host=host, port=port, debug=debug)
