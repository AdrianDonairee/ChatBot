"""
Aplicación principal Flask para ChatBot de turnos.

Este módulo crea y configura la aplicación Flask con:
- API REST para gestión de turnos
- Base de datos SQLAlchemy unificada
- CORS para frontend
- Configuración centralizada
"""
from flask import Flask
from api import chat_blueprint, db
from common import Config, setup_logging

try:
    from flask_cors import CORS
except ImportError:
    CORS = None

# Configurar logging
logger = setup_logging(__name__)


def create_app():
    """
    Factory function para crear la aplicación Flask.
    
    Returns:
        Flask: Aplicación configurada y lista para usar
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Usar configuración centralizada
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['DEBUG'] = Config.FLASK_DEBUG
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS

    # Habilitar CORS para el frontend si está disponible
    if CORS:
        CORS(app)
        logger.info("CORS habilitado")
    
    # Inicializar DB
    db.init_app(app)
    
    # Asegurar que exista la carpeta instance y crear tablas
    with app.app_context():
        Config.ensure_instance_dir()
        db.create_all()
        logger.info("Base de datos inicializada")

    # Registrar blueprints
    app.register_blueprint(chat_blueprint, url_prefix='/chat')
    logger.info("API REST registrada en /chat")
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    logger.info(f"Iniciando Flask API en {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    logger.info(f"Debug mode: {Config.FLASK_DEBUG}")
    logger.info(f"Database: {Config.DATABASE_URI}")
    
    # Bind to 0.0.0.0 so the app is reachable from Docker/container network
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )
