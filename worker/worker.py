"""
Worker para procesamiento asíncrono de tareas.

Procesa tareas encoladas por el servidor de sockets mediante IPC:
- Ejecuta operaciones de escritura (book, cancel)
- Evita bloqueos en el servidor principal
- Maneja errores de forma robusta
"""
import time
import logging
import os
from typing import Any, Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from services import ReservationService

# Configurar logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
WORKER_SLEEP_TIME = float(os.getenv('WORKER_SLEEP_TIME', '0.1'))


class TaskWorker:
    """
    Worker que procesa tareas de una cola multiprocessing.Queue.
    
    Attributes:
        task_queue: Cola de tareas a procesar
        max_days: Días a futuro para operaciones
        running: Flag para controlar el loop principal
    """
    def __init__(self, task_queue, max_days: int = 7):
        self.task_queue = task_queue
        self.max_days = max_days
        self.running = True
        logger.info(f"TaskWorker inicializado (max_days={max_days})")

    def _process(self, task: Dict[str, Any]):
        """
        Procesa una tarea específica.
        
        Args:
            task: Diccionario con 'action' y parámetros específicos
        """
        svc = ReservationService()
        action = task.get('action')
        
        if action == 'book':
            slot_id = task.get('slot_id')
            name = task.get('name')
            service = task.get('service', 'General')
            ok = svc.book(slot_id, name, service)
            
            if ok:
                logger.info(f"✓ Reserva exitosa: slot={slot_id}, cliente={name}, servicio={service}")
            else:
                logger.warning(f"✗ Reserva fallida: slot={slot_id} (no disponible o no existe)")
                
        elif action == 'cancel_id':
            slot_id = task.get('slot_id')
            ok = svc.cancel_by_slot(slot_id)
            
            if ok:
                logger.info(f"✓ Cancelación exitosa: slot={slot_id}")
            else:
                logger.warning(f"✗ Cancelación fallida: slot={slot_id} (no encontrado)")
                
        elif action == 'cancel_name':
            name = task.get('name')
            n = svc.cancel_by_customer(name)
            logger.info(f"✓ Cancelados {n} turnos del cliente: {name}")
            
        else:
            logger.error(f"Tarea con action desconocida: {task}")

    def run(self):
        """Loop principal del worker."""
        logger.info("=" * 50)
        logger.info("WORKER INICIADO - Esperando tareas...")
        logger.info("=" * 50)
        
        while self.running:
            try:
                # Esperar tarea con timeout
                task = self.task_queue.get(timeout=1)
                logger.debug(f"Tarea recibida: {task}")
                
                try:
                    self._process(task)
                except Exception as e:
                    logger.error(f"Error procesando tarea {task}: {e}", exc_info=True)
                    
                # Pequeña pausa entre tareas
                time.sleep(WORKER_SLEEP_TIME)
                
            except Exception:
                # Timeout esperando tarea, continuar
                continue
        
        logger.info("Worker detenido")


if __name__ == '__main__':
    """Punto de entrada para testing del worker."""
    import multiprocessing
    
    logger.info("Modo de prueba del worker")
    q = multiprocessing.Queue()
    w = TaskWorker(q)
    
    # Demo: encolar una tarea de prueba
    logger.info("Encolando tarea de prueba...")
    q.put({'action': 'book', 'slot_id': 1, 'name': 'Demo', 'service': 'Corte'})
    
    # Ejecutar por 3 segundos y detener
    import threading
    def stop_after_timeout():
        time.sleep(3)
        w.running = False
        logger.info("Deteniendo worker de prueba...")
    
    threading.Thread(target=stop_after_timeout, daemon=True).start()
    w.run()
    logger.info("Prueba completada")
