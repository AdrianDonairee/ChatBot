"""
Worker para procesamiento asíncrono de tareas.

Este módulo implementa un worker que procesa tareas encoladas mediante IPC:
- Ejecuta operaciones de escritura (book, cancel) de forma asíncrona
- Evita bloqueos en el servidor TCP
- Demuestra comunicación entre procesos con multiprocessing.Queue

Tipos de tareas soportadas:
    - book: Reserva un turno
    - cancel_id: Cancela por ID de turno
    - cancel_name: Cancela todos los turnos de un cliente

Uso:
    from worker import TaskWorker
    
    import multiprocessing
    task_queue = multiprocessing.Queue()
    worker = TaskWorker(task_queue)
    worker.run()
"""

from .worker import TaskWorker

__all__ = ['TaskWorker']
