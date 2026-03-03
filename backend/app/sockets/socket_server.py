"""
Servidor TCP para manejo de conexiones de clientes
"""

import socket
import threading
from config import Config

class SocketServer:
    def __init__(self, app_context):
        self.app_context = app_context
        self.host = Config.SOCKET_HOST
        self.port = Config.SOCKET_PORT
        self.max_clients = Config.MAX_CLIENTS
        self.server_socket = None
        self.running = False
        self.client_handlers = []
        self.client_ids = {}
    
    def start(self):
        """Inicia el servidor de sockets"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_clients)
            self.running = True
            
            print(f"✅ Servidor de sockets iniciado correctamente en puerto {self.port}")
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, address = self.server_socket.accept()
                    
                    if len(self.client_handlers) >= self.max_clients:
                        print(f"[!] Límite de clientes alcanzado. Rechazando {address}")
                        client_socket.close()
                        continue
                    
                    # Importar aquí para evitar problemas circulares
                    try:
                        from app.sockets.cliente_handler import ClienteHandler
                        handler = ClienteHandler(client_socket, address, self.app_context, self)
                        handler.start()
                        self.client_handlers.append(handler)
                        print(f"[+] Handler creado para {address}")
                    except ImportError as e:
                        print(f"[!] Error importando ClienteHandler: {e}")
                        client_socket.close()
                    
                    self.limpiar_handlers()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[!] Error aceptando conexión: {e}")
                        
        except Exception as e:
            print(f"[!] Error iniciando servidor: {e}")
        finally:
            self.stop()
    
    def limpiar_handlers(self):
        self.client_handlers = [h for h in self.client_handlers if h.is_alive()]
    
    def registrar_id_cliente(self, nodo_id, handler):
        if nodo_id in self.client_ids:
            handler_anterior = self.client_ids[nodo_id]
            print(f"[!] Cliente duplicado detectado (ID: {nodo_id})")
            handler_anterior.running = False
            try:
                handler_anterior.client_socket.close()
            except:
                pass
        self.client_ids[nodo_id] = handler
    
    def eliminar_id_cliente(self, nodo_id):
        if nodo_id in self.client_ids:
            del self.client_ids[nodo_id]
    
    def enviar_comando_a_nodo(self, nodo_id, comando, parametros=None):
        """Envía un comando a un nodo específico"""
        if nodo_id in self.client_ids:
            handler = self.client_ids[nodo_id]
            if handler and handler.is_alive():
                print(f"📤 Enviando comando '{comando}' a nodo {nodo_id}")
                return handler.enviar_comando(comando, parametros)
            else:
                self.eliminar_id_cliente(nodo_id)
        
        print(f"[!] No se encontró conexión activa para nodo {nodo_id}")
        return False
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for handler in self.client_handlers:
            handler.running = False
            try:
                handler.client_socket.close()
            except:
                pass
        print("[*] Servidor de sockets detenido")

# Variable global
socket_server_instance = None

def iniciar_servidor_sockets(app_context):
    global socket_server_instance
    server = SocketServer(app_context)
    socket_server_instance = server
    server.start()