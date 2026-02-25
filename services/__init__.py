"""
Capa de servicios para operaciones de negocio.

Este módulo implementa el patrón Service Layer para:
- Desacoplar la lógica de negocio de la API
- Centralizar operaciones de reserva y cancelación
- Facilitar el testing y mantenimiento

Uso:
    from services import ReservationService
    
    svc = ReservationService()
    slots = svc.list_available()
    ok = svc.book(slot_id=5, name="Juan", service="Corte")
"""

from .reservation_service import ReservationService

__all__ = ['ReservationService']
