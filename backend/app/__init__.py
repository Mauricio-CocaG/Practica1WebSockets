from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
import threading
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Configuración CORS - Permitir cualquier origen en LAN
    CORS(app, origins="*", supports_credentials=True)
    
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.models.nodo import Nodo
    from app.models.metrica import Metrica
    from app.models.mensaje import Mensaje
    
    from app.controllers.nodo_controller import nodo_bp
    from app.controllers.metrica_controller import metrica_bp
    from app.controllers.dashboard_controller import dashboard_bp
    
    app.register_blueprint(nodo_bp, url_prefix='/api/nodos')
    app.register_blueprint(metrica_bp, url_prefix='/api/metricas')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    @app.route('/')
    def home():
        return jsonify({
            'message': 'ClusterMonitor API funcionando',
            'status': 'online',
            'version': '1.0.0',
            'endpoints': {
                'nodos': '/api/nodos',
                'metricas': '/api/metricas',
                'dashboard': '/api/dashboard/resumen'
            }
        })
    
    @app.route('/api/ip')
    def get_ip():
        """Endpoint para que los clientes obtengan la IP del servidor"""
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return jsonify({
            'hostname': hostname,
            'ip': local_ip,
            'socket_port': app.config['SOCKET_PORT']
        })
    
    def start_socket_server():
        from app.sockets.socket_server import SocketServer
        with app.app_context():
            socket_server = SocketServer(app.app_context())
            socket_server.start()
    
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        socket_thread = threading.Thread(target=start_socket_server, daemon=True)
        socket_thread.start()
        print(f"✅ Servidor de sockets iniciado en {app.config['SOCKET_HOST']}:{app.config['SOCKET_PORT']}")
    
    return app