# test_socket_v2.py
import time
import json
import os
import socket

SOCKET_STATE_FILE = os.path.join(os.path.dirname(__file__), 'socket_state.json')

def check_socket():
    """Verifica si el puerto 9999 está escuchando"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('192.168.100.6', 9999))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("="*60)
    print("📡 VERIFICACIÓN DE COMUNICACIÓN BIDIRECCIONAL")
    print("="*60)
    
    # Método 1: Verificar puerto
    puerto_abierto = check_socket()
    print(f"\n1️⃣ Puerto 9999 accesible: {puerto_abierto}")
    
    # Método 2: Leer archivo de estado
    try:
        with open(SOCKET_STATE_FILE, 'r') as f:
            state = json.load(f)
            print(f"2️⃣ Estado desde archivo: {state}")
            print(f"   Clientes: {state.get('clients', [])}")
    except:
        print("2️⃣ No hay archivo de estado")
    
    # Método 3: Verificar proceso
    print("\n📋 INSTRUCCIONES:")
    print("1. El backend DEBE estar corriendo en OTRA terminal")
    print("2. El cliente DEBE estar conectado")
    print("3. Para enviar comandos, USA LA TERMINAL DEL BACKEND")
    print("\n👉 En la terminal del backend, ejecuta:")
    print("   python")
    print("   >>> from app.sockets.socket_server import socket_server_instance")
    print("   >>> print(socket_server_instance.client_ids)")
    print("   >>> socket_server_instance.enviar_comando_a_nodo(10, 'VERIFICAR_DISCO')")

if __name__ == "__main__":
    main()