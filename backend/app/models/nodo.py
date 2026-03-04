from app import db
from app.utils.timezone import now, to_iso

class Nodo(db.Model):
    __tablename__ = 'nodos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)
    puerto = db.Column(db.Integer, default=9999)
    estado = db.Column(db.String(20), default='Activo')
    ultima_conexion = db.Column(db.DateTime, default=now)
    fecha_registro = db.Column(db.DateTime, default=now)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'ip_address': self.ip_address,
            'puerto': self.puerto,
            'estado': self.estado,
            'ultima_conexion': to_iso(self.ultima_conexion),
            'fecha_registro': to_iso(self.fecha_registro),
        }