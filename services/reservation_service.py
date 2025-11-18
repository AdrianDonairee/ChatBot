from typing import List, Dict, Any, Optional

from chatbot_logic.appointments import AppointmentManager, pretty_slot


class ReservationService:
    """Capa de servicio que envuelve AppointmentManager.

    Provee una API estable para listar, reservar y cancelar turnos. Mantiene
    la persistencia existente (JSON) a través de AppointmentManager.
    """

    def __init__(self, storage_path: Optional[str] = None):
        # No guardamos estado en memoria para evitar stales en este simple diseño;
        # cada operación crea un AppointmentManager (lectura/escritura desde disco).
        self.storage_path = storage_path

    def list_available(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        am = AppointmentManager(storage_path=self.storage_path)
        return am.list_available(date)

    def list_bookings(self) -> List[Dict[str, Any]]:
        am = AppointmentManager(storage_path=self.storage_path)
        return am.list_bookings()

    def pretty(self, slot: Dict[str, Any]) -> str:
        return pretty_slot(slot)

    def book(self, slot_id: int, name: str, service: str = 'General') -> bool:
        am = AppointmentManager(storage_path=self.storage_path)
        return am.book(slot_id, name, service)

    def cancel_by_slot(self, slot_id: int) -> bool:
        am = AppointmentManager(storage_path=self.storage_path)
        return am.cancel_by_slot(slot_id)

    def cancel_by_customer(self, name: str) -> int:
        am = AppointmentManager(storage_path=self.storage_path)
        return am.cancel_by_customer(name)


__all__ = ['ReservationService']
