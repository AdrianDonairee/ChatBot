"""
Gestor de turnos usando SQLAlchemy.

Refactorizado para usar base de datos en lugar de JSON,
permitiendo que todas las interfaces compartan los mismos datos.
"""
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class AppointmentManager:
    """
    Gestor de turnos persistido en base de datos SQLAlchemy.
    
    Cada turno es un diccionario/objeto TimeSlot:
    {
        "id": int,
        "datetime": "YYYY-MM-DD HH:MM",
        "service": "corte",
        "customer": None or "Nombre Cliente"
    }
    """

    def __init__(self, db_uri: Optional[str] = None):
        """
        Inicializa el gestor de turnos.
        
        Args:
            db_uri: URI de la base de datos. Si es None, usa sqlite por defecto.
        """
        # Importar aquí para evitar dependencias circulares
        from api.models import TimeSlot
        from api.db import db
        
        self.TimeSlot = TimeSlot
        self.db = db
        
        # Si no hay URI, usar SQLite por defecto
        if db_uri is None:
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            instance_dir = os.path.join(repo_root, 'instance')
            os.makedirs(instance_dir, exist_ok=True)
            db_path = os.path.join(instance_dir, 'appointments.db')
            db_uri = f'sqlite:///{db_path}'
        
        # Crear engine y sesión
        self.engine = create_engine(db_uri)
        self.SessionLocal = scoped_session(sessionmaker(bind=self.engine))
        
        # Inicializar DB si es necesario
        self._init_db()
        
        # Generar slots si la DB está vacía
        self._ensure_slots()

    def _init_db(self):
        """Crea las tablas si no existen."""
        from api.db import db
        
        # Crear una app Flask temporal para el contexto
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = str(self.engine.url)
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            db.create_all()

    def _ensure_slots(self):
        """Genera slots iniciales si la base está vacía."""
        session = self.SessionLocal()
        try:
            count = session.query(self.TimeSlot).count()
            if count == 0:
                self._generate_slots_to_db(session)
                session.commit()
        finally:
            session.close()

    def _generate_slots_to_db(self, session, days: int = 7):
        """Genera slots en la base de datos."""
        times = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00"]
        today = datetime.now().date()
        
        for d in range(days):
            day = today + timedelta(days=d)
            for t in times:
                dt_str = f"{day.isoformat()} {t}"
                slot = self.TimeSlot(
                    datetime_str=dt_str,
                    service="General",
                    customer=None
                )
                session.add(slot)

    def list_available(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista turnos disponibles.
        
        Args:
            date: Fecha en formato YYYY-MM-DD para filtrar, o None para todos
            
        Returns:
            Lista de diccionarios con información de slots disponibles
        """
        session = self.SessionLocal()
        try:
            query = session.query(self.TimeSlot).filter(self.TimeSlot.customer.is_(None))
            
            if date:
                query = query.filter(self.TimeSlot.datetime_str.like(f'{date}%'))
            
            slots = query.order_by(self.TimeSlot.datetime_str).all()
            return [slot.to_dict() for slot in slots]
        finally:
            session.close()

    def list_bookings(self) -> List[Dict[str, Any]]:
        """Lista todos los turnos reservados."""
        session = self.SessionLocal()
        try:
            slots = session.query(self.TimeSlot)\
                .filter(self.TimeSlot.customer.isnot(None))\
                .order_by(self.TimeSlot.datetime_str)\
                .all()
            return [slot.to_dict() for slot in slots]
        finally:
            session.close()

    def find_slot(self, slot_id: int) -> Optional[Dict[str, Any]]:
        """
        Busca un slot por ID.
        
        Args:
            slot_id: ID del slot a buscar
            
        Returns:
            Diccionario con datos del slot o None si no existe
        """
        session = self.SessionLocal()
        try:
            slot = session.query(self.TimeSlot).filter_by(id=slot_id).first()
            return slot.to_dict() if slot else None
        finally:
            session.close()

    def book(self, slot_id: int, customer_name: str, service: str = "General") -> bool:
        """
        Reserva un turno.
        
        Args:
            slot_id: ID del slot a reservar
            customer_name: Nombre del cliente
            service: Servicio solicitado
            
        Returns:
            True si se reservó exitosamente, False en caso contrario
        """
        session = self.SessionLocal()
        try:
            slot = session.query(self.TimeSlot).filter_by(id=slot_id).first()
            
            if not slot:
                return False
            
            if slot.customer is not None:
                return False
            
            slot.customer = customer_name
            slot.service = service
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def cancel_by_slot(self, slot_id: int) -> bool:
        """
        Cancela una reserva por ID de slot.
        
        Args:
            slot_id: ID del slot a cancelar
            
        Returns:
            True si se canceló exitosamente, False en caso contrario
        """
        session = self.SessionLocal()
        try:
            slot = session.query(self.TimeSlot).filter_by(id=slot_id).first()
            
            if not slot or slot.customer is None:
                return False
            
            slot.customer = None
            slot.service = "General"
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def cancel_by_customer(self, customer_name: str) -> int:
        """
        Cancela todas las reservas a nombre de un cliente.
        
        Args:
            customer_name: Nombre del cliente
            
        Returns:
            Cantidad de turnos cancelados
        """
        session = self.SessionLocal()
        try:
            slots = session.query(self.TimeSlot)\
                .filter(self.TimeSlot.customer.ilike(f'%{customer_name}%'))\
                .all()
            
            count = 0
            for slot in slots:
                slot.customer = None
                slot.service = "General"
                count += 1
            
            if count > 0:
                session.commit()
            
            return count
        except Exception:
            session.rollback()
            return 0
        finally:
            session.close()


def pretty_slot(slot: Dict[str, Any]) -> str:
    """
    Formatea un slot para mostrar en texto.
    
    Args:
        slot: Diccionario con datos del slot
        
    Returns:
        String formateado
    """
    status = "Libre" if not slot['customer'] else f"Reservado por {slot['customer']} ({slot['service']})"
    return f"[{slot['id']}] {slot['datetime']} - {status}"


if __name__ == '__main__':
    am = AppointmentManager()
    print("Listado de próximos turnos:\n")
    for s in am.list_available()[:20]:
        print(pretty_slot(s))
