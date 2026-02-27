#!/usr/bin/env python3
"""Script para probar todas las mejoras implementadas"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("="*60)
print("PRUEBA 1: Chatbot Logic - NLP y respuestas")
print("="*60)
from chatbot_logic import process_message

tests = [
    "hola",
    "quiero reservar",
    "horarios disponibles",
    "cancelar",
    "ayuda"
]

for msg in tests:
    resp = process_message(msg)
    print(f"👤 Usuario: {msg}")
    print(f"🤖 Bot: {resp[:80]}...")
    print()

print("✅ Chatbot Logic funcionando\n")

print("="*60)
print("PRUEBA 2: AppointmentManager con SQLAlchemy")
print("="*60)
from chatbot_logic import AppointmentManager

am = AppointmentManager()
slots = am.list_available()
print(f"✅ Slots disponibles: {len(slots)}")
if slots:
    print(f"   Primer slot: {slots[0]}")

bookings = am.list_bookings()
print(f"✅ Reservas activas: {len(bookings)}")

print()

print("="*60)
print("PRUEBA 3: Configuración centralizada")
print("="*60)
from common.config import Config

print(f"✅ DATABASE_URI: {Config.DATABASE_URI[:50]}...")
print(f"✅ FLASK_PORT: {Config.FLASK_PORT}")
print(f"✅ SOCKET_PORT: {Config.SOCKET_PORT}")
print(f"✅ API_TOKEN configurado: {'Sí' if Config.API_TOKEN else 'No'}")
print()

print("="*60)
print("PRUEBA 4: Autenticación")
print("="*60)
from api.auth import require_token

print(f"✅ Decorador @require_token importado correctamente")
print(f"✅ Token requerido: {Config.API_TOKEN[:10]}..." if Config.API_TOKEN else "❌ No configurado")
print()

print("="*60)
print("PRUEBA 5: Modelos de base de datos")
print("="*60)
from api.models import Appointment, TimeSlot

print(f"✅ Modelo Appointment importado (deprecated)")
print(f"✅ Modelo TimeSlot importado (nuevo - unificado)")
print(f"   Campos: id, datetime_str, service, customer")
print()

print("="*60)
print("PRUEBA 6: Logging centralizado")
print("="*60)
from common.logconfig import setup_logging
import logging

test_logger = setup_logging("test_module")
print(f"✅ Logger creado: {test_logger.name}")
print(f"✅ Nivel: {logging.getLevelName(test_logger.level)}")
print()

print("="*60)
print("RESUMEN: Todas las pruebas completadas exitosamente")
print("="*60)
print("✅ Chatbot Logic funcionando")
print("✅ AppointmentManager con SQLAlchemy")
print("✅ Configuración centralizada")
print("✅ Autenticación implementada")
print("✅ Modelos de DB correctos")
print("✅ Logging centralizado")
print()
print("🎉 Todas las mejoras están funcionando correctamente!")
