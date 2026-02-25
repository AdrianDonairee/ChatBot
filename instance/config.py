"""
Configuración de instancia para el ChatBot.

Este archivo es para configuraciones específicas de tu entorno local.
NO debe subirse al repositorio (está en .gitignore).

Para configuraciones sensibles, usa variables de entorno en .env
"""
import os
import secrets

# Generar SECRET_KEY segura si no está en variables de entorno
# En producción, SIEMPRE usar variable de entorno
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    # Generar una clave aleatoria para desarrollo
    SECRET_KEY = secrets.token_hex(32)
    print("⚠️  ADVERTENCIA: Usando SECRET_KEY generada. En producción, define SECRET_KEY en .env")

# Debug mode (False en producción)
DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Base de datos
# Puedes sobrescribir DATABASE_URL aquí si lo prefieres
# DATABASE_URL = 'sqlite:///instance/appointments.db'
# DATABASE_URL = 'postgresql://user:pass@localhost:5432/chatbot'
