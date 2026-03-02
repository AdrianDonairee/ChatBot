"""
Servidor TCP multihilo para gestión de turnos.

Proporciona una interfaz de socket TCP alternativa al API REST:
- Protocolo simple basado en texto
- Maneja múltiples clientes concurrentes mediante threading
- Encola operaciones de escritura en un worker process

Comandos soportados:
    LIST [fecha]           - Lista turnos disponibles
    BOOK id|name|service   - Reserva un turno
    CANCEL_ID id           - Cancela por ID
    CANCEL_NAME nombre     - Cancela por nombre
    QUIT                   - Cierra conexión

Uso:
    from socket_srv import start_server
    
    import multiprocessing
    task_queue = multiprocessing.Queue()
    start_server('0.0.0.0', 5001, task_queue)
"""

from common import Config

HOST = Config.SOCKET_HOST
PORT = Config.SOCKET_PORT


def start_server(*args, **kwargs):
    from .server import start_server as _start_server
    return _start_server(*args, **kwargs)


def handle_client(*args, **kwargs):
    from .server import handle_client as _handle_client
    return _handle_client(*args, **kwargs)

__all__ = ['start_server', 'handle_client', 'HOST', 'PORT']
