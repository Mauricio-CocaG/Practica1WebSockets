from app import db
from datetime import datetime
from config import get_bolivia_time  # 👈 IMPORTAR

class Mensaje(db.Model):
    """Modelo para mensajes bidireccionales servidor-cliente"""
    __tablename__ = 'mensajes'
    
    id = db.Column(db.Integer, primary_key=True)
    nodo_id = db.Column(db.Integer, db.ForeignKey('nodos.id'), nullable=False)
    
    # Contenido del mensaje
    contenido = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(20))  # 'comando', 'notificacion', 'alerta'
    direccion = db.Column(db.String(10))  # 'enviado' (servidor->cliente), 'recibido'
    
    # Estado del mensaje
    requiere_ack = db.Column(db.Boolean, default=True)
    ack_recibido = db.Column(db.Boolean, default=False)
    fecha_ack = db.Column(db.DateTime, nullable=True)
    
    # Timestamps - HORA BOLIVIA
    fecha_creacion = db.Column(db.DateTime, default=get_bolivia_time)  # 👈 HORA BOLIVIA
    
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
    
    def __repr__(self):
        return f'<Mensaje {self.tipo} para Nodo:{self.nodo_id}>'