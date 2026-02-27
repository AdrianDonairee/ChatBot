"""
Configuración centralizada del proyecto.

Todas las configuraciones se cargan desde variables de entorno
con valores por defecto sensatos para desarrollo.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """Configuración centralizada del sistema."""
    
    # Determinar directorio base del proyecto
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _INSTANCE_DIR = os.path.join(_BASE_DIR, 'instance')
    
    # Base de datos
    _DEFAULT_DB_PATH = os.path.join(_INSTANCE_DIR, 'appointments.db')
    DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{_DEFAULT_DB_PATH}'
    )
    
    # Flask API
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-cambiar-en-produccion')
    
    # Socket Server
    SOCKET_HOST = os.getenv('SOCKET_HOST', '0.0.0.0')
    SOCKET_PORT = int(os.getenv('SOCKET_PORT', 5001))
    
    # Worker
    WORKER_SLEEP_TIME = float(os.getenv('WORKER_SLEEP_TIME', '0.1'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Autenticación (API Token)
    API_TOKEN = os.getenv('API_TOKEN', 'dev-token-123')
    
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    @classmethod
    def get_db_uri(cls):
        """Retorna la URI de la base de datos."""
        return cls.DATABASE_URI
    
    @classmethod
    def ensure_instance_dir(cls):
        """Asegura que el directorio instance existe."""
        os.makedirs(cls._INSTANCE_DIR, exist_ok=True)
