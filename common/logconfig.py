"""
Configuración centralizada de logging.

Proporciona una función para crear loggers consistentes
en todos los módulos del proyecto.
"""
import logging
import sys
from .config import Config


def setup_logging(name: str, level: str = None) -> logging.Logger:
    """
    Crea y configura un logger con formato estándar.
    
    Args:
        name: Nombre del logger (usualmente __name__)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               Si es None, usa el valor de Config.LOG_LEVEL
    
    Returns:
        Logger configurado
    
    Example:
        >>> logger = setup_logging(__name__)
        >>> logger.info("Mensaje de información")
    """
    logger = logging.getLogger(name)
    
    # Determinar nivel
    if level is None:
        level = Config.LOG_LEVEL
    
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    
    # Formato: timestamp - nombre - nivel - mensaje
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger
