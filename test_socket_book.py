#!/usr/bin/env python3
"""Test script que prueba la funcionalidad de BOOK con feedback."""

import socket
import time

def recv_until_quiet(sock, timeout=0.5):
    """Lee respuesta del socket hasta que no lleguen más bytes."""
    chunks = []
    previous_timeout = sock.gettimeout()
    sock.settimeout(timeout)
    try:
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
            except socket.timeout:
                break
    finally:
        sock.settimeout(previous_timeout)
    return b"".join(chunks).decode("utf-8", errors="replace")

def send_cmd(sock, cmd, desc=""):
    """Envía comando y recibe respuesta."""
    print(f"\n>>> {cmd} {' (' + desc + ')' if desc else ''}")
    sock.sendall((cmd.strip() + "\n").encode("utf-8"))
    resp = recv_until_quiet(sock)
    print(f"<<< {resp.strip()}")
    return resp

try:
    print("=" * 60)
    print("TEST: Reservas con feedback")
    print("=" * 60)
    
    sock = socket.create_connection(("127.0.0.1", 5001), timeout=5)
    print("✓ Conectado al servidor\n")
    
    # Cargar bienvenida
    welcome = recv_until_quiet(sock)
    print(f"Servidor: {welcome.strip()}\n")
    
    # Listar turnos disponibles
    send_cmd(sock, "LIST", "Listar todos los turnos disponibles")
    time.sleep(1)
    
    print("\n" + "="*60)
    print("PRUEBA 1: Reservar un turno disponible")
    print("="*60)
    # Reservar un turno específico que DEBERÍA estar disponible (slot 3)
    send_cmd(sock, "BOOK 3|Juan Pérez|Corte", "✓ Reservar slot 3 (debe funcionar)")
    time.sleep(0.5)
    
    print("\n" + "="*60)
    print("PRUEBA 2: Intentar reservar el MISMO turno")
    print("="*60)
    # Intentar reservar el MISMO turno (debe fallar)
    send_cmd(sock, "BOOK 3|Carlos López|Tinte", "✗ Intentar reservar slot 3 nuevamente (debe FALLAR)")
    time.sleep(0.5)
    
    print("\n" + "="*60)
    print("PRUEBA 3: Reservar un turno diferente")
    print("="*60)
    # Reservar un turno diferente (debe funcionar)
    send_cmd(sock, "BOOK 4|Maria García|Pedicure", "✓ Reservar slot 4 (debe funcionar)")
    time.sleep(0.5)
    
    print("\n" + "="*60)
    print("PRUEBA 4: Listar turnos actualizado")
    print("="*60)
    # Listar de nuevo para ver cambios
    send_cmd(sock, "LIST", "Verificar que slots 3 y 4 no están en la lista")
    time.sleep(0.5)
    
    # QUIT
    send_cmd(sock, "QUIT", "Cerrar conexión")
    
    sock.close()
    print("\n✓ Test completado")
    print("=" * 60)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
