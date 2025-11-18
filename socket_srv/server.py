"""Servidor TCP multihilo (módulo reorganizado en socket_srv.server).

Se mantiene la misma funcionalidad que el archivo anterior `socket_server.py`.
"""
import socket
import threading
import argparse
import multiprocessing
from typing import Tuple

from services.reservation_service import ReservationService


HOST = '127.0.0.1'
PORT = 5001


def handle_client(conn: socket.socket, addr: Tuple[str, int], task_queue: multiprocessing.Queue, max_days: int = 3):
    # Usar el servicio para lecturas
    svc = ReservationService()
    with conn:
        conn.sendall("Bienvenido al servidor de turnos\n".encode('utf-8'))
        buf = b""
        while True:
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
            parts = cmd.split()
            if parts[0].upper() == 'LIST':
                date = parts[1] if len(parts) > 1 else None
                slots = svc.list_available(date)
                if not slots:
                    conn.sendall("No hay turnos disponibles.\n".encode('utf-8'))
                else:
                    for s in slots:
                        conn.sendall((svc.pretty(s) + "\n").encode('utf-8'))

            elif parts[0].upper() == 'BOOK':
                # formato: BOOK id|name|service
                rest = cmd[len('BOOK'):].strip()
                try:
                    slot_id_s, name, service = rest.split('|', 2)
                    task = {'action': 'book', 'slot_id': int(slot_id_s), 'name': name, 'service': service}
                    task_queue.put(task)
                    conn.sendall("Reserva encolada. El worker la procesará pronto.\n".encode('utf-8'))
                except Exception as e:
                    conn.sendall(f"Formato inválido BOOK. Use: BOOK id|name|service. Error: {e}\n".encode('utf-8'))

            elif parts[0].upper() == 'CANCEL_ID':
                try:
                    slot_id = int(parts[1])
                    task_queue.put({'action': 'cancel_id', 'slot_id': slot_id})
                    conn.sendall("Cancelación encolada por id.\n".encode('utf-8'))
                except Exception:
                    conn.sendall(b"Uso: CANCEL_ID <id>\n")

            elif parts[0].upper() == 'CANCEL_NAME':
                name = ' '.join(parts[1:]).strip()
                if not name:
                    conn.sendall(b"Uso: CANCEL_NAME <nombre>\n")
                else:
                    task_queue.put({'action': 'cancel_name', 'name': name})
                    conn.sendall("Cancelación encolada por nombre.\n".encode('utf-8'))

            elif parts[0].upper() in ('QUIT', 'EXIT'):
                conn.sendall("Adiós\n".encode('utf-8'))
                break

            else:
                conn.sendall("Comando no reconocido.\n".encode('utf-8'))


def start_server(host: str, port: int, task_queue: multiprocessing.Queue, max_days: int = 3):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen()
    print(f"Servidor escuchando en {host}:{port}")
    try:
        while True:
            conn, addr = srv.accept()
            print(f"Conexión desde {addr}")
            # lanzar un hilo por cliente para manejar la conexión
            t = threading.Thread(target=handle_client, args=(conn, addr, task_queue, max_days), daemon=True)
            t.start()
    finally:
        srv.close()


def main():
    parser = argparse.ArgumentParser(description='Servidor de turnos (módulo socket_srv.server)')
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
