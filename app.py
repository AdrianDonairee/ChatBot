from flask import Flask
from api.routes import chat_blueprint
try:
    # optional: flask-cors may not be installed yet
    from flask_cors import CORS
except Exception:
    CORS = None

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # Carga configuración opcional
    try:
        app.config.from_pyfile('instance/config.py')
    except FileNotFoundError:
        pass
    # enable CORS for the frontend (Vite/dev server) if available
    if CORS is not None:
        CORS(app)

    app.register_blueprint(chat_blueprint, url_prefix='/chat')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
