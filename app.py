from flask import Flask
from api.routes import chat_blueprint
try:
    # optional: flask-cors may not be installed yet
    from flask_cors import CORS
except Exception:
    CORS = None

import os
from api.db import db  # nuevo

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # Carga configuración opcional
    try:
        app.config.from_pyfile('instance/config.py')
    except FileNotFoundError:
        pass

    # configuración por defecto de la base de datos (puedes sobrescribir en instance/config.py)
    instance_db_path = os.path.join(app.instance_path, 'appointments.db')
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', f"sqlite:///{instance_db_path}")
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    # enable CORS for the frontend (Vite/dev server) if available
    if CORS is not None:
        CORS(app)

    # inicializar DB
    db.init_app(app)
    # asegurar que exista la carpeta instance y crear tablas
    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()

    app.register_blueprint(chat_blueprint, url_prefix='/chat')
    return app

if __name__ == '__main__':
    app = create_app()
    # Bind to 0.0.0.0 so the app is reachable from Docker/container network
    app.run(host='0.0.0.0', port=5000, debug=True)
