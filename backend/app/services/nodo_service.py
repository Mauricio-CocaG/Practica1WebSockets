from app.models.nodo import Nodo
from app import db
from datetime import timedelta
from app.utils.timezone import now

class NodoService:
    """Servicio para operaciones relacionadas con nodos"""
    
    @staticmethod
    def verificar_nodos_timeout(timeout_minutos=5):
        """
        Verifica nodos que no han reportado en X minutos
        y los marca como 'No Reporta'
        """
        tiempo_limite = now() - timedelta(minutes=timeout_minutos)
        
        # Buscar nodos activos que no han reportado
        nodos_inactivos = Nodo.query.filter(
            Nodo.ultima_conexion < tiempo_limite,
            Nodo.estado == 'Activo'
        ).all()
        
        # Marcar como inactivos
        for nodo in nodos_inactivos:
            nodo.estado = 'No Reporta'
            print(f"[!] Nodo {nodo.nombre} marcado como 'No Reporta'")
        
        if nodos_inactivos:
            db.session.commit()
        
        return nodos_inactivos
    
    @staticmethod
    def registrar_nodo(ip_address, puerto, nombre=None):
        """Registra un nuevo nodo o actualiza uno existente"""
        nodo = Nodo.query.filter_by(ip_address=ip_address).first()
        
        if not nodo:
            # Crear nuevo nodo
            if not nombre:
                count = Nodo.query.count() + 1
                nombre = f"Regional {count}"
            
            nodo = Nodo(
                nombre=nombre,
                ip_address=ip_address,
                puerto=puerto,
                estado='Activo',
                ultima_conexion=now()
            )
            db.session.add(nodo)
            db.session.commit()
            print(f"[+] Nuevo nodo registrado: {nombre}")
            return nodo, True
        else:
            # Actualizar nodo existente
            nodo.estado = 'Activo'
            nodo.ultima_conexion = now()
            nodo.puerto = puerto
            db.session.commit()
            print(f"[+] Nodo actualizado: {nodo.nombre}")
            return nodo, False
    
    @staticmethod
    def marcar_nodo_inactivo(nodo_id):
        """Marca un nodo específico como inactivo"""
        nodo = Nodo.query.get(nodo_id)
        if nodo:
            nodo.estado = 'No Reporta'
            db.session.commit()
            print(f"[!] Nodo {nodo.nombre} marcado como inactivo manualmente")
            return True
        return False
    
    @staticmethod
    def get_nodo_by_ip(ip_address):
        """Busca un nodo por su dirección IP"""
        return Nodo.query.filter_by(ip_address=ip_address).first()