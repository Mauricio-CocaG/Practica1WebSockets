from app.models.nodo import Nodo
from app.models.metrica import Metrica
from app import db
from sqlalchemy import func
from app.utils.timezone import to_iso

class ClusterService:
    """Servicio para cálculos globales del cluster"""
    
    @staticmethod
    def get_cluster_metrics():
        """Calcula todas las métricas globales del cluster"""
        
        # Estadísticas básicas
        total_nodos = Nodo.query.count()
        nodos_activos = Nodo.query.filter_by(estado='Activo').count()
        
        # Obtener última métrica de cada nodo
        subquery = db.session.query(
            Metrica.nodo_id, 
            func.max(Metrica.timestamp).label('max_timestamp')
        ).group_by(Metrica.nodo_id).subquery()
        
        ultimas_metricas = db.session.query(Metrica).join(
            subquery, 
            (Metrica.nodo_id == subquery.c.nodo_id) & 
            (Metrica.timestamp == subquery.c.max_timestamp)
        ).all()
        
        # Cálculos globales
        capacidad_total = sum(m.capacidad_total for m in ultimas_metricas)
        espacio_usado = sum(m.espacio_usado for m in ultimas_metricas)
        espacio_libre = sum(m.espacio_libre for m in ultimas_metricas)
        
        # Porcentaje de utilización global
        if capacidad_total > 0:
            porcentaje_global = (espacio_usado / capacidad_total) * 100
        else:
            porcentaje_global = 0
        
        # Disponibilidad
        disponibilidad = (nodos_activos / total_nodos * 100) if total_nodos > 0 else 0
        
        return {
            'total_nodos': total_nodos,
            'nodos_activos': nodos_activos,
            'capacidad_total_gb': round(capacidad_total, 2),
            'espacio_usado_gb': round(espacio_usado, 2),
            'espacio_libre_gb': round(espacio_libre, 2),
            'porcentaje_utilizacion_global': round(porcentaje_global, 2),
            'disponibilidad_porcentaje': round(disponibilidad, 2)
        }
    
    @staticmethod
    def get_nodos_estado():
        """Obtiene el estado actual de todos los nodos con sus últimas métricas"""
        
        nodos = Nodo.query.all()
        resultado = []
        
        for nodo in nodos:
            # Última métrica de este nodo
            ultima_metrica = Metrica.query.filter_by(nodo_id=nodo.id)\
                                .order_by(Metrica.timestamp.desc())\
                                .first()
            
            nodo_data = nodo.to_dict()
            if ultima_metrica:
                nodo_data.update({
                    'capacidad_total': ultima_metrica.capacidad_total,
                    'espacio_usado': ultima_metrica.espacio_usado,
                    'espacio_libre': ultima_metrica.espacio_libre,
                    'tipo_disco': ultima_metrica.tipo_disco,
                    'porcentaje_uso': ultima_metrica.porcentaje_uso,
                    'ultima_actualizacion': to_iso(ultima_metrica.timestamp)
                })
            else:
                nodo_data.update({
                    'capacidad_total': 0,
                    'espacio_usado': 0,
                    'espacio_libre': 0,
                    'tipo_disco': 'Desconocido',
                    'porcentaje_uso': 0,
                    'ultima_actualizacion': None
                })
            
            resultado.append(nodo_data)
        
        return resultado