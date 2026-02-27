from datetime import datetime
from .db import db


class TimeSlot(db.Model):
    """
    Representa un slot de tiempo disponible para reservar.
    
    Cada slot tiene un horario fijo y puede estar disponible o reservado.
    """
    __tablename__ = 'timeslots'
    
    id = db.Column(db.Integer, primary_key=True)
    datetime_str = db.Column(db.String(64), nullable=False, index=True)  # "YYYY-MM-DD HH:MM"
    service = db.Column(db.String(128), nullable=False, default="General")
    customer = db.Column(db.String(128), nullable=True)  # None = disponible
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convierte el slot a diccionario compatible con la interfaz anterior."""
        return {
            'id': self.id,
            'datetime': self.datetime_str,
            'service': self.service,
            'customer': self.customer
        }
    
    def is_available(self):
        """Retorna True si el slot está disponible."""
        return self.customer is None
    
    def __repr__(self):
        status = "Disponible" if self.is_available() else f"Reservado ({self.customer})"
        return f"<TimeSlot {self.id}: {self.datetime_str} - {status}>"


class Appointment(db.Model):
    """
    DEPRECATED: Mantenido por compatibilidad.
    Usar TimeSlot en su lugar.
    """
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, nullable=False, index=True, unique=True)
    customer = db.Column(db.String(128), nullable=False)
    service = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'slot_id': self.slot_id,
            'customer': self.customer,
            'service': self.service,
            'created_at': self.created_at.isoformat()
        }