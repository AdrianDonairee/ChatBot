#!/usr/bin/env python3
"""Chatbot CLI y runner multi-modo para gestionar turnos de peluquería.

Permite ejecutar en modo CLI local, servidor de sockets (multihilo) o cliente asyncio demo.
"""
import argparse
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


def main():
    parser = argparse.ArgumentParser(description='Run ChatBot in different modes')
    parser.add_argument('--mode', choices=['cli', 'server', 'async-client'], default='cli',
                        help='Modo de ejecución: cli (por defecto), server (socket server), async-client (demo)')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5001)
    args = parser.parse_args()

    if args.mode == 'cli':
        cli_mode()
    elif args.mode == 'server':
        # lanzar servidor de sockets
        from socket_server import main as server_main
        server_main()
    elif args.mode == 'async-client':
        from async_client import main as client_main
        client_main()


if __name__ == '__main__':
    main()
