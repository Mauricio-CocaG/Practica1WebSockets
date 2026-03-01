import socket
import threading
from config import Config

class SocketServer:
    def __init__(self, app_context):
        self.app_context = app_context
        self.host = Config.SOCKET_HOST  # 0.0.0.0
        self.port = Config.SOCKET_PORT  # 9999
        self.max_clients = Config.MAX_CLIENTS
        self.server_socket = None
        self.running = False
        self.client_handlers = []
    
    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_clients)
            self.running = True
            
            # Obtener IP local para mostrar
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            print(f"\n{'='*60}")
            print(f"📡 SERVIDOR DE SOCKETS LISTO")
            print(f"{'='*60}")
            print(f"   Escuchando en: {self.host}:{self.port}")
            print(f"   IP Local: {local_ip}")
            print(f"   Los clientes deben conectarse a: {local_ip}:{self.port}")
            print(f"{'='*60}\n")
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    client_socket, address = self.server_socket.accept()
                    
                    if len(self.client_handlers) >= self.max_clients:
                        print(f"[!] Límite de clientes alcanzado. Rechazando {address}")
                        client_socket.close()
                        continue
                    
                    from app.sockets.cliente_handler import ClienteHandler
                    handler = ClienteHandler(client_socket, address, self.app_context)
                    handler.start()
                    self.client_handlers.append(handler)
                    
                    self.limpiar_handlers()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[!] Error: {e}")
                        
        except Exception as e:
            print(f"[!] Error iniciando servidor: {e}")
        finally:
            self.stop()
    
    def limpiar_handlers(self):
        self.client_handlers = [h for h in self.client_handlers if h.is_alive()]
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for handler in self.client_handlers:
            handler.running = False
        print("[*] Servidor de sockets detenido")