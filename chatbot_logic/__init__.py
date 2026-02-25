"""
Lógica del chatbot y gestión de turnos.

Módulos:
- processor: Procesamiento de mensajes del usuario mediante palabras clave
- appointments: Gestión de turnos (AppointmentManager)
- responses: Base de conocimiento de respuestas predefinidas

Uso:
    from chatbot_logic import process_message, AppointmentManager, pretty_slot
    
    response = process_message("hola")
    am = AppointmentManager()
    slots = am.list_available()
"""

from .processor import process_message
from .appointments import AppointmentManager, pretty_slot
from .responses import RESPONSES

__all__ = [
    'process_message',
    'AppointmentManager',
    'pretty_slot',
    'RESPONSES'
]
