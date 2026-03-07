from app import create_app
import os

app = create_app('development')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 INICIANDO CLUSTERMONITOR BACKEND")
    print("="*60)
    print(f"📊 Base de datos: {app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}")
    print(f"🔌 Socket server: {app.config['SOCKET_HOST']}:{app.config['SOCKET_PORT']}")
    print(f"📡 API REST: http://localhost:3000")
    print(f"👥 Máximo clientes: {app.config['MAX_CLIENTS']}")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0', 
        port=3000, 
        debug=True,
        use_reloader=False  # Importante: evitar duplicar sockets
    )