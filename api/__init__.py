"""
Módulo API REST para el ChatBot de turnos.

Este módulo expone:
- db: Instancia de SQLAlchemy para gestión de base de datos
- TimeSlot: Modelo de datos para slots de tiempo
- Appointment: Modelo de datos para reservas (deprecated)
- chat_blueprint: Blueprint de Flask con todos los endpoints REST
- require_token: Decorador para proteger endpoints
- optional_token: Decorador para autenticación opcional

Uso:
    from api import db, TimeSlot, chat_blueprint, require_token
    
    app.register_blueprint(chat_blueprint, url_prefix='/chat')
"""

from .db import db
from .models import TimeSlot, Appointment
from .routes import chat_blueprint
from .auth import require_token, optional_token

__all__ = ['db', 'TimeSlot', 'Appointment', 'chat_blueprint', 'require_token', 'optional_token']
