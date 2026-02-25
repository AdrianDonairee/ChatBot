"""
Servidor TCP multihilo para gestión de turnos.

Proporciona una interfaz TCP alternativa al API REST con:
- Protocolo simple basado en texto
- Múltiples clientes concurrentes via threading
- IPC con worker process para operaciones de escritura
"""
import socket
import threading
import argparse
import multiprocessing
import logging
import os
from typing import Tuple

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
HOST = os.getenv('SOCKET_HOST', '0.0.0.0')
PORT = int(os.getenv('SOCKET_PORT', '5001'))


def handle_client(conn: socket.socket, addr: Tuple[str, int], task_queue: multiprocessing.Queue, max_days: int = 3):
    """
    Maneja la conexión de un cliente TCP.
    
    Args:
        conn: Socket de conexión del cliente
        addr: Dirección del cliente (host, port)
        task_queue: Cola para encolar tareas de escritura
        max_days: Días a futuro para listar turnos
    """
    client_id = f"{addr[0]}:{addr[1]}"
    logger.info(f"Cliente conectado: {client_id}")
    
    svc = ReservationService()
    with conn:
        conn.sendall("Bienvenido al servidor de turnos\n".encode('utf-8'))
        buf = b""
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                buf += data
                if b"\n" not in buf:
                    continue
                line, _, buf = buf.partition(b"\n")
                cmd = line.decode('utf-8').strip()
                if not cmd:
                    continue
                
                logger.debug(f"Comando recibido de {client_id}: {cmd}")
                parts = cmd.split()
                
                if parts[0].upper() == 'LIST':
                    date = parts[1] if len(parts) > 1 else None
                    slots = svc.list_available(date)
                    if not slots:
                        conn.sendall("No hay turnos disponibles.\n".encode('utf-8'))
                    else:
                        for s in slots:
                            conn.sendall((svc.pretty(s) + "\n").encode('utf-8'))
                    logger.info(f"{client_id} listó {len(slots)} turnos")

                elif parts[0].upper() == 'BOOK':
                    rest = cmd[len('BOOK'):].strip()
                    try:
                        slot_id_s, name, service = rest.split('|', 2)
                        task = {
                            'action': 'book',
                            'slot_id': int(slot_id_s),
                            'name': name,
                            'service': service
                        }
                        task_queue.put(task)
                        conn.sendall("Reserva encolada. El worker la procesará pronto.\n".encode('utf-8'))
                        logger.info(f"{client_id} encoló reserva: slot={slot_id_s}, name={name}")
                    except Exception as e:
                        error_msg = f"Formato inválido BOOK. Use: BOOK id|name|service. Error: {e}\n"
                        conn.sendall(error_msg.encode('utf-8'))
                        logger.warning(f"{client_id} envió comando BOOK inválido: {e}")

                elif parts[0].upper() == 'CANCEL_ID':
                    try:
    """
    Inicia el servidor TCP y escucha conexiones entrantes.
    
    Args:
        host: Dirección IP para vincular el servidor
        port: Puerto para escuchar
        task_queue: Cola para encolar tareas al worker
        max_days: Días a futuro para operaciones
    """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen()
    logger.info(f"✓ Servidor TCP escuchando en {host}:{port}")
    
    try:
        while True:
            conn, addr = srv.accept()
            # Lanzar un hilo por cada cliente
            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, task_queue, max_days),
                daemon=True,
                name=f"Client-{addr[0]}:{addr[1]}"
            )
            t.start()
    except KeyboardInterrupt:
        logger.info("Interrupción recibida, cerrando servidor...")
    except Exception as e:
        logger.error(f"Error en servidor: {e}")
    finally:
        srv.close()
        logger.info("Servidor cerrado"      task_queue.put({'action': 'cancel_name', 'name': name})
                        conn.sendall("Cancelación encolada por nombre.\n".encode('utf-8'))
                        logger.info(f"{client_id} encoló cancelación por nombre: {name}")

                elif parts[0].upper() in ('QUIT', 'EXIT'):
                    conn.sendall("Adiós\n".encode('utf-8'))
                    logger.info(f"{client_id} finalizó conexión")
                    break

                else:
                    conn.sendall("Comando no reconocido.\n".encode('utf-8'))
                    logger.warning(f"{client_id} envió comando desconocido: {cmd}")
                    
            except Exception as e:
                logger.error(f"Error manejando cliente {client_id}: {e}")
                break
    
    logger.info(f"Cliente desconectado: {client_id}")

"""Punto de entrada principal del servidor."""
    parser = argparse.ArgumentParser(
        description='Servidor TCP multihilo para gestión de turnos',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--host',
        default=HOST,
        help='Dirección IP para vincular el servidor'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=PORT,
        help='Puerto para escuchar'
    )
    parser.add_argument(
        '--max-days',
        type=int,
        default=int(os.getenv('WORKER_MAX_DAYS', '7')),
        help='Días a futuro para generar slots'
    )
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("INICIANDO SERVIDOR DE TURNOS")
    logger.info("=" * 50)
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Max days: {args.max_days}")
    logger.info("=" * 50)

    # Crear cola de tareas para IPC
    task_queue = multiprocessing.Queue()
    
    # Lanzar worker en proceso separado
    logger.info("Iniciando worker process...")
    from worker import TaskWorker
    worker = TaskWorker(task_queue, max_days=args.max_days)
    worker_process = multiprocessing.Process(
        target=worker.run,
        daemon=True,
        name="TaskWorker"
    )
    worker_process.start()
    logger.info(f"✓ Worker iniciado (PID: {worker_process.pid})")

    try:
        start_server(args.host, args.port, task_queue, max_days=args.max_days)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupción recibida (Ctrl+C)")
    finally:
        logger.info("Deteniendo worker...")
        worker_process.terminate()
        worker_process.join(timeout=5)
        if worker_process.is_alive():
            logger.warning("Worker no respondió, forzando terminación...")
            worker_process.kill()
        logger.info("✓ Servidor detenido correctamente"ntParser(description='Servidor de turnos (módulo socket_srv.server)')
    parser.add_argument('--host', default=HOST)
    parser.add_argument('--port', type=int, default=PORT)
    parser.add_argument('--max-days', type=int, default=3, help='Cantidad de días desde hoy para generar slots (por defecto 3)')
    args = parser.parse_args()

    task_queue = multiprocessing.Queue()
    # Lanzar worker en proceso aparte
    from worker.worker import TaskWorker
    worker = TaskWorker(task_queue, max_days=args.max_days)
    worker_process = multiprocessing.Process(target=worker.run, daemon=True)
    worker_process.start()

    try:
        start_server(args.host, args.port, task_queue, max_days=args.max_days)
    except KeyboardInterrupt:
        print('Deteniendo servidor...')
    finally:
        worker_process.terminate()
        worker_process.join()


if __name__ == '__main__':
    main()
