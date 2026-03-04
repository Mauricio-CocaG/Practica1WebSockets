"""
Controlador de métricas
----------------------
Maneja las peticiones relacionadas con las métricas de disco.
"""

from flask import Blueprint, jsonify, request
from app.models.metrica import Metrica
from app.models.nodo import Nodo
from app import db
from datetime import timedelta
from app.utils.timezone import now

metrica_bp = Blueprint('metrica', __name__)

@metrica_bp.route('/', methods=['GET'])
def get_metricas():
    """Obtiene todas las métricas con filtros opcionales"""
    try:
        nodo_id = request.args.get('nodo_id', type=int)
        dias = request.args.get('dias', 7, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        query = Metrica.query
        
        if nodo_id:
            query = query.filter_by(nodo_id=nodo_id)
        
        if dias:
            fecha_limite = now() - timedelta(days=dias)
            query = query.filter(Metrica.timestamp >= fecha_limite)
        
        metricas = query.order_by(Metrica.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(metricas),
            'data': [m.to_dict() for m in metricas]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@metrica_bp.route('/', methods=['POST'])
def crear_metrica():
    """Crea una nueva métrica (usado por clientes)"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['nodo_id', 'capacidad_total', 'espacio_usado', 'espacio_libre']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Verificar que el nodo existe
        nodo = Nodo.query.get(data['nodo_id'])
        if not nodo:
            return jsonify({
                'success': False,
                'error': 'Nodo no encontrado'
            }), 404
        
        # Calcular porcentaje de uso
        capacidad = float(data['capacidad_total'])
        usado = float(data['espacio_usado'])
        porcentaje = (usado / capacidad * 100) if capacidad > 0 else 0
        
        # Crear métrica
        metrica = Metrica(
            nodo_id=data['nodo_id'],
            nombre_disco=str(data.get('nombre_disco', 'Desconocido')),
            tipo_disco=str(data.get('tipo_disco', 'Desconocido')),
            capacidad_total=capacidad,
            espacio_usado=usado,
            espacio_libre=float(data['espacio_libre']),
            iops=int(data.get('iops', 0)),
            porcentaje_uso=porcentaje
        )
        
        db.session.add(metrica)
        
        # Actualizar última conexión del nodo
        nodo.ultima_conexion = now()
        nodo.estado = 'Activo'
        
        db.session.commit()
        
        print(f"[OK] Metrica guardada para nodo {nodo.nombre} (ID: {nodo.id})")
        
        return jsonify({
            'success': True,
            'message': 'Métrica guardada exitosamente',
            'data': metrica.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[!] Error guardando métrica: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@metrica_bp.route('/ultimas/<int:nodo_id>', methods=['GET'])
def get_ultimas_metricas(nodo_id):
    """Obtiene las últimas métricas de un nodo específico"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        metricas = Metrica.query.filter_by(nodo_id=nodo_id)\
                        .order_by(Metrica.timestamp.desc())\
                        .limit(limit)\
                        .all()
        
        return jsonify({
            'success': True,
            'nodo_id': nodo_id,
            'count': len(metricas),
            'data': [m.to_dict() for m in metricas]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500