"""
Módulo común con configuración y utilidades compartidas.
"""
from .config import Config
from .logconfig import setup_logging

__all__ = ['Config', 'setup_logging']
