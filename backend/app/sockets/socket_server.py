"""
Servidor TCP para manejo de conexiones de clientes
"""

import socket
import threading
from config import Config

# Variable global - se inicializará cuando el servidor arranque
socket_server_instance = None

class SocketServer:
    def __init__(self, app_context):
        self.app_context = app_context
        self.host = Config.SOCKET_HOST
        self.port = Config.SOCKET_PORT
        self.max_clients = Config.MAX_CLIENTS
        self.server_socket = None
        self.running = False
        self.client_handlers = []
        self.client_ids = {}  # Diccionario: ID del nodo → handler
        
    def start(self):
        """Inicia el servidor de sockets"""
        global socket_server_instance
        socket_server_instance = self  # 👈 ASIGNAR LA VARIABLE GLOBAL AQUÍ
        
        print("🔧 Inicializando servidor de sockets...")
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_clients)
            self.running = True
            
            print(f"✅ Servidor de sockets iniciado en puerto {self.port}")
            print(f"📡 Variable global 'socket_server_instance' asignada: {socket_server_instance}")
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, address = self.server_socket.accept()
                    
                    if len(self.client_handlers) >= self.max_clients:
                        print(f"[!] Límite alcanzado. Rechazando {address}")
                        client_socket.close()
                        continue
                    
                    from app.sockets.cliente_handler import ClienteHandler
                    handler = ClienteHandler(client_socket, address, self.app_context, self)
                    handler.start()
                    self.client_handlers.append(handler)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[!] Error: {e}")
                        
        except Exception as e:
            print(f"[!] Error iniciando: {e}")
        finally:
            self.stop()
    
    def registrar_id_cliente(self, nodo_id, handler):
        """Registra un cliente por su ID"""
        if nodo_id in self.client_ids:
            print(f"[!] Cliente duplicado ID {nodo_id}")
        self.client_ids[nodo_id] = handler
        print(f"📝 Cliente {nodo_id} registrado para comandos")
    
    def eliminar_id_cliente(self, nodo_id):
        """Elimina un cliente cuando se desconecta"""
        if nodo_id in self.client_ids:
            del self.client_ids[nodo_id]
            print(f"📝 Cliente {nodo_id} eliminado")
    
    def enviar_comando_a_nodo(self, nodo_id, comando, parametros=None):
        """📤 ENVÍA UN COMANDO A UN NODO ESPECÍFICO"""
        print(f"🔍 Buscando nodo {nodo_id}...")
        print(f"📊 Clientes conectados: {list(self.client_ids.keys())}")
        
        if nodo_id in self.client_ids:
            handler = self.client_ids[nodo_id]
            if handler and handler.is_alive():
                print(f"📤 Enviando comando '{comando}' a nodo {nodo_id}")
                return handler.enviar_comando(comando, parametros)
            else:
                print(f"[!] Handler de nodo {nodo_id} no está vivo")
                self.eliminar_id_cliente(nodo_id)
        else:
            print(f"[!] Nodo {nodo_id} no está en la lista de clientes")
        
        return False
    
    def get_clientes_conectados(self):
        """Retorna lista de IDs de clientes conectados"""
        return list(self.client_ids.keys())
    
    def stop(self):
        """Detiene el servidor"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("🛑 Servidor de sockets detenido")

def iniciar_servidor_sockets(app_context):
    """Función para iniciar el servidor"""
    global socket_server_instance
    server = SocketServer(app_context)
    server.start()
    socket_server_instance = server  # 👈 DOBLE ASIGNACIÓN POR SEGURIDAD
    return server

# Para acceso directo desde otros módulos
def get_socket_server():
    """Retorna la instancia del servidor de sockets"""
    global socket_server_instance
    return socket_server_instance