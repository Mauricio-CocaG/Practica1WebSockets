from flask import Blueprint, jsonify
from app.services.cluster_service import ClusterService
from app.services.nodo_service import NodoService
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/resumen', methods=['GET'])
def get_resumen():
    NodoService.verificar_nodos_timeout()
    
    return jsonify({
        'cluster': ClusterService.get_cluster_metrics(),
        'nodos': ClusterService.get_nodos_estado(),
        'timestamp': datetime.utcnow().isoformat()
    })