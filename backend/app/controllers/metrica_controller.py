from flask import Blueprint, jsonify
from app.models.metrica import Metrica

metrica_bp = Blueprint('metrica', __name__)

@metrica_bp.route('/', methods=['GET'])
def get_metricas():
    metricas = Metrica.query.order_by(Metrica.timestamp.desc()).limit(100).all()
    return jsonify([m.to_dict() for m in metricas])