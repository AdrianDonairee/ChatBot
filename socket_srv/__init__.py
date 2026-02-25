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

from .server import start_server, handle_client, HOST, PORT

__all__ = ['start_server', 'handle_client', 'HOST', 'PORT']
