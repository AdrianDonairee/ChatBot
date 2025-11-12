import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any


class AppointmentManager:
    """Gestor simple de turnos persistido en JSON.

    Cada turno es un diccionario:
    {
        "id": int,
        "datetime": "YYYY-MM-DD HH:MM",
        "service": "corte",
        "customer": None or "Nombre Cliente"
    }
    """

    def __init__(self, storage_path: Optional[str] = None):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_dir = os.path.join(repo_root, 'instance')
        os.makedirs(default_dir, exist_ok=True)
        self.storage_path = storage_path or os.path.join(default_dir, 'appointments.json')
        self.slots: List[Dict[str, Any]] = []
        self._load_or_init()

    def _load_or_init(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.slots = json.load(f)
            except Exception:
                # si hay error al leer, regeneramos
                self.slots = self._generate_slots()
                self._save()
        else:
            self.slots = self._generate_slots()
            self._save()

    def _save(self):
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.slots, f, ensure_ascii=False, indent=2)

    def _generate_slots(self, days: int = 7) -> List[Dict[str, Any]]:
        """Genera turnos para los próximos `days` días en horarios fijos."""
        times = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00"]
        slots: List[Dict[str, Any]] = []
        next_id = 1
        today = datetime.now().date()
        for d in range(days):
            day = today + timedelta(days=d)
            # opcional: omitir domingos
            # if day.weekday() == 6:
            #     continue
            for t in times:
                dt_str = f"{day.isoformat()} {t}"
                slots.append({
                    "id": next_id,
                    "datetime": dt_str,
                    "service": "General",
                    "customer": None,
                })
                next_id += 1
        return slots

    def list_available(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        if date:
            # date en formato YYYY-MM-DD
            return [s for s in self.slots if s['customer'] is None and s['datetime'].startswith(date)]
        return [s for s in self.slots if s['customer'] is None]

    def list_bookings(self) -> List[Dict[str, Any]]:
        return [s for s in self.slots if s['customer']]

    def find_slot(self, slot_id: int) -> Optional[Dict[str, Any]]:
        for s in self.slots:
            if s['id'] == slot_id:
                return s
        return None

    def book(self, slot_id: int, customer_name: str, service: str = "General") -> bool:
        slot = self.find_slot(slot_id)
        if not slot:
            return False
        if slot['customer'] is not None:
            return False
        slot['customer'] = customer_name
        slot['service'] = service
        self._save()
        return True

    def cancel_by_slot(self, slot_id: int) -> bool:
        slot = self.find_slot(slot_id)
        if not slot:
            return False
        if slot['customer'] is None:
            return False
        slot['customer'] = None
        slot['service'] = "General"
        self._save()
        return True

    def cancel_by_customer(self, customer_name: str) -> int:
        """Cancela todas las reservas a nombre de customer_name. Devuelve cantidad canceladas."""
        count = 0
        for s in self.slots:
            if s['customer'] and s['customer'].lower() == customer_name.lower():
                s['customer'] = None
                s['service'] = "General"
                count += 1
        if count:
            self._save()
        return count


def pretty_slot(slot: Dict[str, Any]) -> str:
    status = "Libre" if not slot['customer'] else f"Reservado por {slot['customer']} ({slot['service']})"
    return f"[{slot['id']}] {slot['datetime']} - {status}"


if __name__ == '__main__':
    am = AppointmentManager()
    print("Listado de próximos turnos:\n")
    for s in am.list_available()[:20]:
        print(pretty_slot(s))
