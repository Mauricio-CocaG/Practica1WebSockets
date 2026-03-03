from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
import threading
import sys
from pathlib import Path
import socket
import time

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from config import config

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()

# Variable para controlar que solo se inicie UNA VEZ
_socket_server_started = False

def get_local_ip():
    """Obtiene la IP local de la máquina"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "127.0.0.1"

def create_app(config_name='default'):
    global _socket_server_started
    
    app = Flask(__name__)
    
    # Configuración CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos
    from app.models.nodo import Nodo
    from app.models.metrica import Metrica
    from app.models.mensaje import Mensaje
    
    # Registrar blueprints
    from app.controllers.nodo_controller import nodo_bp
    from app.controllers.metrica_controller import metrica_bp
    from app.controllers.dashboard_controller import dashboard_bp
    
    app.register_blueprint(nodo_bp, url_prefix='/api/nodos')
    app.register_blueprint(metrica_bp, url_prefix='/api/metricas')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Ruta de prueba
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
    
    # IMPORTANTE: Función para iniciar sockets
    def start_socket_server():
        global _socket_server_started
        
        # Evitar iniciar múltiples veces
        if _socket_server_started:
            return
            
        try:
            print("\n🔧 Iniciando servidor de sockets...")
            
            # Importar usando la ruta correcta
            from app.sockets.socket_server import SocketServer
            
            with app.app_context():
                socket_server = SocketServer(app.app_context())
                
                # Mostrar información
                local_ip = get_local_ip()
                print(f"\n{'='*60}")
                print(f"📡 SERVIDOR DE SOCKETS LISTO")
                print(f"{'='*60}")
                print(f"   Escuchando en: {app.config['SOCKET_HOST']}:{app.config['SOCKET_PORT']}")
                print(f"   IP Local: {local_ip}")
                print(f"   Los clientes deben conectarse a: {local_ip}:{app.config['SOCKET_PORT']}")
                print(f"   Máximo clientes: {app.config['MAX_CLIENTS']}")
                print(f"{'='*60}\n")
                
                _socket_server_started = True
                socket_server.start()
                
        except Exception as e:
            print(f"\n❌ ERROR iniciando servidor de sockets: {e}")
            import traceback
            traceback.print_exc()
    
    # FUERZAMOS el inicio de sockets después de 2 segundos
    # Esto es independiente del debug mode de Flask
    def delayed_start():
        time.sleep(2)  # Esperar a que Flask esté listo
        print("🔄 Iniciando servidor de sockets (retrasado)...")
        start_socket_server()
    
    # Siempre iniciar sockets, sin importar el modo debug
    socket_thread = threading.Thread(target=delayed_start, daemon=True)
    socket_thread.start()
    print("✅ Hilo del servidor de sockets programado para iniciar en 2 segundos")
    
    return app