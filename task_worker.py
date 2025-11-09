"""Worker que procesa tareas desde una multiprocessing.Queue.

Ejecuta acciones mutantes sobre AppointmentManager (book/cancel).
Esta separación demuestra IPC entre el servidor y el worker.
"""
import time
from typing import Any, Dict
from chatbot_logic.appointments import AppointmentManager


class TaskWorker:
    def __init__(self, task_queue, max_days: int = 3):
        self.task_queue = task_queue
        self.max_days = max_days
        self.running = True

    def _process(self, task: Dict[str, Any]):
        am = AppointmentManager(max_days=self.max_days)
        action = task.get('action')
        if action == 'book':
            slot_id = task.get('slot_id')
            name = task.get('name')
            service = task.get('service', 'General')
            ok = am.book(slot_id, name, service)
            print(f"[Worker] Reserva {slot_id} para {name} ({service}) -> {'OK' if ok else 'FALLÓ'}")
        elif action == 'cancel_id':
            slot_id = task.get('slot_id')
            ok = am.cancel_by_slot(slot_id)
            print(f"[Worker] Cancelar id {slot_id} -> {'OK' if ok else 'FALLÓ'}")
        elif action == 'cancel_name':
            name = task.get('name')
            n = am.cancel_by_customer(name)
            print(f"[Worker] Cancelar por nombre {name} -> {n} cancelados")
        else:
            print(f"[Worker] Tarea desconocida: {task}")

    def run(self):
    print('[Worker] Iniciado')
        while True:
            try:
                task = self.task_queue.get(timeout=1)
            except Exception:
                continue
            try:
                self._process(task)
            except Exception as e:
                print(f"[Worker] Error procesando tarea {task}: {e}")
            time.sleep(0.1)


if __name__ == '__main__':
    import multiprocessing
    q = multiprocessing.Queue()
    w = TaskWorker(q)
    # demo: encolar una tarea
    q.put({'action': 'book', 'slot_id': 1, 'name': 'Demo', 'service': 'Corte'})
    w.run()
