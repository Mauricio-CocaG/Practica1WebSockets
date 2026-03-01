from flask import Blueprint, jsonify
from app.models.nodo import Nodo

nodo_bp = Blueprint('nodo', __name__)

@nodo_bp.route('/', methods=['GET'])
def get_nodos():
    """Obtiene todos los nodos"""
    try:
        nodos = Nodo.query.all()
        return jsonify([nodo.to_dict() for nodo in nodos])
    except Exception as e:
        print(f"Error en get_nodos: {e}")
        return jsonify({'error': str(e)}), 500

@nodo_bp.route('/<int:nodo_id>', methods=['GET'])
def get_nodo(nodo_id):
    """Obtiene un nodo por ID"""
    try:
        nodo = Nodo.query.get(nodo_id)
        if not nodo:
            return jsonify({'error': 'Nodo no encontrado'}), 404
        return jsonify(nodo.to_dict())
    except Exception as e:
        print(f"Error en get_nodo: {e}")
        return jsonify({'error': str(e)}), 500