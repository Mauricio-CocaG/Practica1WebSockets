from app import db
from datetime import datetime
from config import get_bolivia_time  # 👈 IMPORTAR

class Nodo(db.Model):
    """Modelo para los nodos clientes (servidores regionales)"""
    __tablename__ = 'nodos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    puerto = db.Column(db.Integer, default=9999)
    estado = db.Column(db.String(20), default='Activo')
    ultima_conexion = db.Column(db.DateTime, default=get_bolivia_time)  # 👈 HORA BOLIVIA
    fecha_registro = db.Column(db.DateTime, default=get_bolivia_time)   # 👈 HORA BOLIVIA
    
    # Relaciones
    metricas = db.relationship('Metrica', backref='nodo', lazy=True, cascade='all, delete-orphan')
    mensajes = db.relationship('Mensaje', backref='nodo', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'ip_address': self.ip_address,
            'puerto': self.puerto,
            'estado': self.estado,
            'ultima_conexion': self.ultima_conexion.isoformat() if self.ultima_conexion else None,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
    
    def __repr__(self):
        return f'<Nodo {self.nombre} - {self.estado}>'