from app import db
from datetime import datetime

class Mensaje(db.Model):
    """Modelo para mensajes bidireccionales"""
    __tablename__ = 'mensajes'
    
    id = db.Column(db.Integer, primary_key=True)
    nodo_id = db.Column(db.Integer, db.ForeignKey('nodos.id'), nullable=False)
    
    contenido = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20))
    direccion = db.Column(db.String(10))
    requiere_ack = db.Column(db.Boolean, default=True)
    ack_recibido = db.Column(db.Boolean, default=False)
    fecha_ack = db.Column(db.DateTime, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nodo_id': self.nodo_id,
            'contenido': self.contenido,
            'tipo': self.tipo,
            'direccion': self.direccion,
            'requiere_ack': self.requiere_ack,
            'ack_recibido': self.ack_recibido,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }