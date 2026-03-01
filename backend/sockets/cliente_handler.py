import threading
import socket
from datetime import datetime

class ClienteHandler(threading.Thread):
    def __init__(self, client_socket, address, app_context):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        self.app_context = app_context
        self.running = True
        self.daemon = True
    
    def run(self):
        print(f"[+] Cliente conectado: {self.address}")
        while self.running:
            try:
                self.client_socket.settimeout(1.0)
                # Aquí irá la lógica de recepción
                pass
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[-] Error: {e}")
                break
        self.client_socket.close()
        print(f"[-] Cliente desconectado: {self.address}")