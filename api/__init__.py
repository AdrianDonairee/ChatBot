"""
Módulo API REST para el ChatBot de turnos.

Este módulo expone:
- db: Instancia de SQLAlchemy para gestión de base de datos
- Appointment: Modelo de datos para reservas
- chat_blueprint: Blueprint de Flask con todos los endpoints REST

Uso:
    from api import db, Appointment, chat_blueprint
    
    app.register_blueprint(chat_blueprint, url_prefix='/chat')
"""

from .db import db
from .models import Appointment
from .routes import chat_blueprint

__all__ = ['db', 'Appointment', 'chat_blueprint']
