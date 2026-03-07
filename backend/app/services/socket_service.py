# Al final de socket_server.py
import json
import os

SOCKET_STATE_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'socket_state.json')

def save_socket_state():
    """Guarda el estado del servidor en un archivo"""
    global socket_server_instance
    if socket_server_instance:
        state = {
            'running': True,
            'port': socket_server_instance.port,
            'clients': list(socket_server_instance.client_ids.keys())
        }
        with open(SOCKET_STATE_FILE, 'w') as f:
            json.dump(state, f)
        print(f"📝 Estado del socket guardado: {state}")

def load_socket_state():
    """Carga el estado del servidor desde un archivo"""
    try:
        with open(SOCKET_STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return None