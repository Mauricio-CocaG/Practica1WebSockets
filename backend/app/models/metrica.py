from app import db
from datetime import datetime
from config import get_bolivia_time  # 👈 IMPORTAR

class Metrica(db.Model):
    """Modelo para las métricas de disco de cada nodo"""
    __tablename__ = 'metricas'
    
    id = db.Column(db.Integer, primary_key=True)
    nodo_id = db.Column(db.Integer, db.ForeignKey('nodos.id'), nullable=False)
    
    # Información del disco
    nombre_disco = db.Column(db.String(100))
    tipo_disco = db.Column(db.String(10))  # SSD/HDD
    capacidad_total = db.Column(db.Float)  # en GB
    espacio_usado = db.Column(db.Float)    # en GB
    espacio_libre = db.Column(db.Float)    # en GB
    iops = db.Column(db.Integer)           # Simulado
    porcentaje_uso = db.Column(db.Float)   # Calculado
    
    # Timestamp - HORA BOLIVIA
    timestamp = db.Column(db.DateTime, default=get_bolivia_time)  # 👈 HORA BOLIVIA
    
    def to_dict(self):
        return {
            'id': self.id,
            'nodo_id': self.nodo_id,
            'nombre_disco': self.nombre_disco,
            'tipo_disco': self.tipo_disco,
            'capacidad_total': self.capacidad_total,
            'espacio_usado': self.espacio_usado,
            'espacio_libre': self.espacio_libre,
            'iops': self.iops,
            'porcentaje_uso': self.porcentaje_uso,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<Metrica Nodo:{self.nodo_id} - {self.timestamp}>'