from datetime import datetime
from .db import db

class Appointment(db.Model):
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