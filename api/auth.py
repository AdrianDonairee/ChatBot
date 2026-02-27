"""
Módulo de autenticación para API REST.

Proporciona decoradores para proteger endpoints con tokens de API.
"""
from functools import wraps
from flask import request, jsonify
from common import Config


def require_token(f):
    """
    Decorador que requiere un token de API válido en el header.
    
    El cliente debe enviar el token en el header X-API-Token.
    
    Uso:
        @app.route('/protected')
        @require_token
        def protected_endpoint():
            return {'message': 'Acceso autorizado'}
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada que verifica el token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener token del header
        token = request.headers.get('X-API-Token')
        
        if not token:
            return jsonify({
                'error': 'Token de autenticación requerido',
                'message': 'Incluya el header X-API-Token con su token de acceso'
            }), 401
        
        # Validar token
        if token != Config.API_TOKEN:
            return jsonify({
                'error': 'Token inválido',
                'message': 'El token proporcionado no es válido'
            }), 403
        
        # Token válido, ejecutar función
        return f(*args, **kwargs)
    
    return decorated_function


def optional_token(f):
    """
    Decorador que permite pero no requiere autenticación.
    
    Útil para endpoints que ofrecen funcionalidad adicional a usuarios autenticados.
    
    Agrega request.authenticated (bool) para que la función pueda verificar si hay auth.
    
    Args:
        f: Función a decorar
        
    Returns:
        Función decorada
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        request.authenticated = (token == Config.API_TOKEN) if token else False
        return f(*args, **kwargs)
    
    return decorated_function
