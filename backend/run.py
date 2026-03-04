import os

# Forzar zona horaria Bolivia antes de cualquier import
# (efectivo en Linux/Mac; en Windows pytz maneja la conversion directamente)
os.environ.setdefault('TZ', 'America/La_Paz')

from app import create_app
from app.utils.timezone import now, BOLIVIA_TZ

app = create_app('development')

if __name__ == '__main__':
    print("\n" + "="*60)
    print("INICIANDO CLUSTERMONITOR BACKEND")
    print("="*60)
    print(f"Base de datos: {app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}")
    print(f"Socket server: {app.config['SOCKET_HOST']}:{app.config['SOCKET_PORT']}")
    print(f"API REST: http://localhost:3000")
    print(f"Maximo clientes: {app.config['MAX_CLIENTS']}")
    print(f"Zona horaria: {app.config['TIMEZONE']}  (hora actual: {now().strftime('%Y-%m-%d %H:%M:%S')})")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0', 
        port=3000, 
        debug=True,
        use_reloader=False  # Importante: evitar duplicar sockets
    )