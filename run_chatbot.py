#!/usr/bin/env python3
"""Chatbot CLI y runner multi-modo para gestionar turnos de peluquería.

Permite ejecutar en modo CLI local, servidor de sockets (multihilo) o cliente asyncio demo.
"""
import argparse
import socket
from typing import Optional
from chatbot_logic.appointments import AppointmentManager, pretty_slot
from chatbot_logic.processor import process_message


def input_int(prompt: str) -> int:
    txt = safe_input(prompt)
    if txt is None:
        return -1
    try:
        return int(txt.strip())
    except Exception:
        return -1


def safe_input(prompt: str) -> str | None:
    """Wrapper around input() that returns None on EOF/interrupt instead of raising.

    This makes the CLI exit gracefully when stdin is closed (e.g. non-interactive runs).
    """
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        # Signal to caller that input is unavailable/closed
        return None


def recv_until_quiet(sock: socket.socket, timeout: float = 0.4) -> str:
    """Lee respuesta del socket hasta que no lleguen más bytes por un tiempo corto."""
    chunks: list[bytes] = []
    previous_timeout = sock.gettimeout()
    sock.settimeout(timeout)
    try:
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
            except TimeoutError:
                break
    finally:
        sock.settimeout(previous_timeout)
    return b"".join(chunks).decode("utf-8", errors="replace")


def send_command(sock: socket.socket, command: str) -> str:
    """Envía un comando al servidor TCP y devuelve la respuesta completa."""
    sock.sendall((command.strip() + "\n").encode("utf-8"))
    return recv_until_quiet(sock)


def cli_mode():
    am = AppointmentManager()
    print("Bienvenido al ChatBot de Turnos - Peluquería\n")

    while True:
        print("Elige una opción:")
        print("  1) Mostrar turnos disponibles")
        print("  2) Reservar un turno")
        print("  3) Cancelar un turno")
        print("  4) Listar reservas")
        print("  5) Chatear (entrada libre)")
        print("  6) Salir")
        raw = safe_input("> ")
        if raw is None:
            print("\nEntrada cerrada. Saliendo.")
            break
        choice = raw.strip()

        if choice == '1':
            date_raw = safe_input("Filtrar por fecha (YYYY-MM-DD) o Enter para todos: ")
            date = date_raw.strip() if date_raw else ""
            slots = am.list_available(date if date else None)
            if not slots:
                print("No hay turnos disponibles para esa fecha." if date else "No hay turnos disponibles.")
            else:
                for s in slots:
                    print(pretty_slot(s))

        elif choice == '2':
            try:
                slot_id = input_int("Ingrese el id del turno a reservar: ")
                if slot_id <= 0:
                    print("Id no válido.")
                    continue
                slot = am.find_slot(slot_id)
                if not slot:
                    print("Turno no encontrado.")
                    continue
                if slot['customer']:
                    print("Ese turno ya está reservado.")
                    continue
                name_raw = safe_input("Nombre del cliente: ")
                name = name_raw.strip() if name_raw else ""
                service_raw = safe_input("Servicio (ej. corte, tinte) [General]: ")
                service = (service_raw.strip() if service_raw else "") or "General"
                if am.book(slot_id, name, service):
                    print(f"Turno reservado: {pretty_slot(am.find_slot(slot_id))}")
                else:
                    print("No se pudo reservar el turno.")
            except Exception as e:
                print("Error al reservar:", e)

        elif choice == '3':
            sub_raw = safe_input("Cancelar por (1) id o (2) nombre del cliente? ")
            sub = sub_raw.strip() if sub_raw else ""
            if sub == '1':
                slot_id = input_int("Ingrese id del turno a cancelar: ")
                if am.cancel_by_slot(slot_id):
                    print("Turno cancelado correctamente.")
                else:
                    print("No se pudo cancelar el turno (id inválido o no reservado).")
            elif sub == '2':
                name_raw = safe_input("Nombre del cliente: ")
                name = name_raw.strip() if name_raw else ""
                n = am.cancel_by_customer(name)
                print(f"Turnos cancelados: {n}")
            else:
                print("Opción inválida.")

        elif choice == '4':
            bookings = am.list_bookings()
            if not bookings:
                print("No hay reservas activas.")
            else:
                for b in bookings:
                    print(pretty_slot(b))

        elif choice == '5':
            msg_raw = safe_input("Escribí tu mensaje: ")
            if msg_raw is None:
                print("Entrada cerrada. Volviendo al menú.")
                continue
            msg = msg_raw.strip()
            if not msg:
                print("Mensaje vacío.")
            else:
                resp = process_message(msg)
                print("Bot:", resp)

        elif choice == '6' or choice.lower() in ('q', 'quit', 'salir'):
            print("Hasta luego 👋")
            break
        else:
            print("Opción no reconocida. Elegí 1-6.")


def socket_cli_mode(host: str, port: int):
    """Interfaz de menú que opera contra el servidor socket TCP."""
    print(f"Conectando al servidor socket en {host}:{port}...")
    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            welcome = recv_until_quiet(sock)
            if welcome:
                print(welcome.strip())

            while True:
                print("\nElige una opción (SOCKET):")
                print("  1) Mostrar turnos disponibles")
                print("  2) Reservar un turno")
                print("  3) Cancelar un turno")
                print("  4) Ver ayuda del servidor")
                print("  5) Salir")
                raw = safe_input("> ")
                if raw is None:
                    print("\nEntrada cerrada. Saliendo.")
                    send_command(sock, "QUIT")
                    break

                choice = raw.strip()
                if choice == "1":
                    date_raw = safe_input("Filtrar por fecha (YYYY-MM-DD) o Enter para todos: ")
                    date = date_raw.strip() if date_raw else ""
                    cmd = f"LIST {date}" if date else "LIST"
                    response = send_command(sock, cmd)
                    print(response.strip() if response else "(sin respuesta)")

                elif choice == "2":
                    slot_id_raw = safe_input("ID del slot: ")
                    name_raw = safe_input("Nombre del cliente: ")
                    service_raw = safe_input("Servicio [General]: ")
                    slot_id = (slot_id_raw or "").strip()
                    name = (name_raw or "").strip()
                    service = (service_raw or "").strip() or "General"
                    if not slot_id.isdigit() or not name:
                        print("Datos inválidos. Requiere ID numérico y nombre.")
                        continue
                    response = send_command(sock, f"BOOK {slot_id}|{name}|{service}")
                    print(response.strip() if response else "(sin respuesta)")

                elif choice == "3":
                    sub_raw = safe_input("Cancelar por (1) id o (2) nombre del cliente? ")
                    sub = (sub_raw or "").strip()
                    if sub == "1":
                        slot_id_raw = safe_input("ID del slot a cancelar: ")
                        slot_id = (slot_id_raw or "").strip()
                        if not slot_id.isdigit():
                            print("ID inválido.")
                            continue
                        response = send_command(sock, f"CANCEL_ID {slot_id}")
                        print(response.strip() if response else "(sin respuesta)")
                    elif sub == "2":
                        name_raw = safe_input("Nombre del cliente: ")
                        name = (name_raw or "").strip()
                        if not name:
                            print("Nombre inválido.")
                            continue
                        response = send_command(sock, f"CANCEL_NAME {name}")
                        print(response.strip() if response else "(sin respuesta)")
                    else:
                        print("Opción inválida.")

                elif choice == "4":
                    response = send_command(sock, "HELP")
                    print(response.strip() if response else "(sin respuesta)")

                elif choice == "5" or choice.lower() in ("q", "quit", "salir"):
                    bye = send_command(sock, "QUIT")
                    print(bye.strip() if bye else "Adiós")
                    break

                else:
                    print("Opción no reconocida. Elegí 1-5.")
    except OSError as e:
        print(f"No se pudo conectar al servidor socket ({host}:{port}): {e}")
        print("Asegurate de ejecutar: python -m socket_srv.server")


def main():
    parser = argparse.ArgumentParser(description='Run ChatBot in different modes')
    parser.add_argument('--mode', choices=['cli', 'socket-cli', 'server', 'async-client'], default='socket-cli',
                        help='Modo: cli local, socket-cli (menú via socket - DEFAULT), server (socket server), async-client (demo)')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Host del servidor socket (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5001,
                        help='Puerto del servidor socket (default: 5001)')
    args = parser.parse_args()

    if args.mode == 'cli':
        cli_mode()
    elif args.mode == 'socket-cli':
        socket_cli_mode(args.host, args.port)
    elif args.mode == 'server':
        # lanzar servidor de sockets
        from socket_srv.server import main as server_main
        server_main()
    elif args.mode == 'async-client':
        import asyncio
        from async_client import main as client_main
        asyncio.run(client_main())


if __name__ == '__main__':
    main()
