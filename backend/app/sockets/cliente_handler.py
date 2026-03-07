"""
Manejador de clientes en hilos separados
"""

import threading
import socket
import json
import time
from datetime import datetime
from app.sockets.protocolo import ProtocoloCluster
from app.models.nodo import Nodo
from app.models.metrica import Metrica
from app.models.mensaje import Mensaje
from app import db
from config import get_bolivia_time  # 👈 IMPORTAR

class ClienteHandler(threading.Thread):
    def __init__(self, client_socket, address, app_context, socket_server):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        self.app_context = app_context
        self.socket_server = socket_server
        self.nodo_id = None
        self.nodo_nombre = None
        self.running = True
        self.daemon = True
        self.last_activity = time.time()
        
    def run(self):
        print(f"[+] Nuevo cliente conectado: {self.address}")
        
        if not self.registrar_nodo():
            print(f"   ↳ Cliente rechazado")
            self._cerrar_socket()
            return
            
        self.enviar_bienvenida()
        
        while self.running:
            try:
                self.client_socket.settimeout(10.0)
                mensaje = ProtocoloCluster.decode_message(self.client_socket)
                
                if mensaje:
                    self.last_activity = time.time()
                    self.procesar_mensaje(mensaje)
                
            except socket.timeout:
                # Timeout normal - verificar actividad
                if time.time() - self.last_activity > 60:
                    print(f"   ⏱️ Cliente {self.nodo_nombre} inactivo por 60s")
                    self.last_activity = time.time()
                continue
            except (ConnectionResetError, BrokenPipeError):
                print(f"   🔌 Cliente {self.address} desconectado abruptamente")
                break
            except Exception as e:
                print(f"[!] Error con cliente {self.address}: {e}")
                break
        
        self.cerrar_conexion()
    
    def _cerrar_socket(self):
        """Cierra el socket de forma segura"""
        try:
            if self.client_socket:
                self.client_socket.close()
        except:
            pass
    
    def registrar_nodo(self):
        """Registra el nodo en la base de datos"""
        with self.app_context:
            try:
                nodo = Nodo.query.filter_by(ip_address=self.address[0]).first()
                
                if not nodo:
                    count = Nodo.query.count() + 1
                    nombre = f"Regional {count}"
                    
                    nodo = Nodo(
                        nombre=nombre,
                        ip_address=self.address[0],
                        puerto=self.address[1],
                        estado='Activo',
                        ultima_conexion=get_bolivia_time()  # 👈 HORA BOLIVIA
                    )
                    db.session.add(nodo)
                    db.session.commit()
                    print(f"[+] Nuevo nodo registrado: {nodo.nombre} (ID: {nodo.id})")
                    
                else:
                    if nodo.id in self.socket_server.client_ids:
                        print(f"[!] Nodo {nodo.nombre} (ID: {nodo.id}) ya tiene una conexión activa")
                        self.enviar_mensaje({
                            'tipo': 'ERROR',
                            'mensaje': 'Ya existe una conexión activa'
                        })
                        return False
                    
                    nodo.estado = 'Activo'
                    nodo.ultima_conexion = get_bolivia_time()  # 👈 HORA BOLIVIA
                    nodo.puerto = self.address[1]
                    db.session.commit()
                    print(f"[+] Nodo reconectado: {nodo.nombre} (ID: {nodo.id})")
                
                self.nodo_id = nodo.id
                self.nodo_nombre = nodo.nombre
                self.socket_server.registrar_id_cliente(self.nodo_id, self)
                return True
                
            except Exception as e:
                print(f"[!] Error registrando nodo: {e}")
                db.session.rollback()
                return False
    
    def enviar_bienvenida(self):
        """Envía mensaje de bienvenida y lo guarda en BD con hora Bolivia"""
        if not self.nodo_id:
            return
            
        mensaje = {
            'tipo': 'BIENVENIDA',
            'nodo_id': self.nodo_id,
            'mensaje': f'Conectado al ClusterMonitor. Nodo ID: {self.nodo_id}',
            'timestamp': get_bolivia_time().isoformat()  # 👈 HORA BOLIVIA
        }
        
        self.enviar_mensaje(mensaje)
        
        with self.app_context:
            try:
                msg_db = Mensaje(
                    nodo_id=self.nodo_id,
                    contenido=mensaje['mensaje'],
                    tipo='bienvenida',
                    direccion='enviado',
                    requiere_ack=False,
                    fecha_creacion=get_bolivia_time()  # 👈 HORA BOLIVIA
                )
                db.session.add(msg_db)
                db.session.commit()
                print(f"   📝 Mensaje de bienvenida guardado en BD (ID: {msg_db.id})")
            except Exception as e:
                print(f"   ❌ Error guardando mensaje: {e}")
                db.session.rollback()
    
    def procesar_mensaje(self, mensaje):
        tipo = mensaje.get('tipo')
        
        with self.app_context:
            try:
                if tipo == 'METRICA':
                    self.procesar_metrica(mensaje)
                elif tipo == 'ACK':
                    self.procesar_ack(mensaje)
                elif tipo == 'REGISTRO':
                    self.procesar_registro(mensaje)
            except Exception as e:
                print(f"[!] Error procesando mensaje: {e}")
                db.session.rollback()
    
    def procesar_metrica(self, mensaje):
        if not self.nodo_id:
            return
            
        try:
            datos = mensaje.get('datos', {})
            
            metrica = Metrica(
                nodo_id=self.nodo_id,
                nombre_disco=datos.get('nombre_disco', 'Desconocido'),
                tipo_disco=datos.get('tipo_disco', 'Desconocido'),
                capacidad_total=float(datos.get('capacidad_total', 0)),
                espacio_usado=float(datos.get('espacio_usado', 0)),
                espacio_libre=float(datos.get('espacio_libre', 0)),
                iops=int(datos.get('iops', 0)),
                porcentaje_uso=float(datos.get('porcentaje_uso', 0)),
                timestamp=get_bolivia_time()  # 👈 HORA BOLIVIA
            )
            
            db.session.add(metrica)
            
            nodo = Nodo.query.get(self.nodo_id)
            if nodo:
                nodo.ultima_conexion = get_bolivia_time()  # 👈 HORA BOLIVIA
                nodo.estado = 'Activo'
            
            db.session.commit()
            print(f"[✓] Métricas guardadas para nodo {self.nodo_nombre}")
            
            # Enviar confirmación con hora Bolivia
            self.enviar_mensaje({
                'tipo': 'METRICA_RECIBIDA', 
                'status': 'ok',
                'timestamp': get_bolivia_time().isoformat()
            })
            
        except Exception as e:
            print(f"[!] Error guardando métricas: {e}")
            db.session.rollback()
    
    def procesar_ack(self, mensaje):
        if not self.nodo_id:
            return
        message_id = mensaje.get('mensaje_id')
        print(f"[✓] ACK recibido de nodo {self.nodo_nombre} para mensaje {message_id}")
        
        # Actualizar el mensaje original como confirmado
        with self.app_context:
            try:
                msg_original = Mensaje.query.filter_by(id=message_id).first()
                if msg_original:
                    msg_original.ack_recibido = True
                    msg_original.fecha_ack = get_bolivia_time()  # 👈 HORA BOLIVIA
                    db.session.commit()
            except:
                db.session.rollback()
    
    def procesar_registro(self, mensaje):
        if not self.nodo_id:
            return
        print(f"[+] Registro de nodo {self.nodo_nombre}: {mensaje.get('nombre', 'Desconocido')}")
    
    def enviar_mensaje(self, mensaje):
        try:
            datos = ProtocoloCluster.encode_message(mensaje)
            if datos:
                self.client_socket.send(datos)
                return True
        except Exception as e:
            print(f"[!] Error enviando mensaje: {e}")
        return False
    
    def enviar_comando(self, comando, parametros=None):
        """Envía un comando al cliente con hora Bolivia"""
        if not self.nodo_id:
            return False
            
        mensaje = {
            'tipo': 'COMANDO',
            'comando': comando,
            'parametros': parametros or {},
            'timestamp': get_bolivia_time().isoformat()  # 👈 HORA BOLIVIA
        }
        
        with self.app_context:
            try:
                msg_db = Mensaje(
                    nodo_id=self.nodo_id,
                    contenido=json.dumps(mensaje),
                    tipo='comando',
                    direccion='enviado',
                    requiere_ack=True,
                    fecha_creacion=get_bolivia_time()  # 👈 HORA BOLIVIA
                )
                db.session.add(msg_db)
                db.session.commit()
                mensaje['id'] = msg_db.id
                print(f"   📝 Comando guardado en BD (ID: {msg_db.id})")
            except Exception as e:
                print(f"   ❌ Error guardando comando: {e}")
                db.session.rollback()
                mensaje['id'] = 0
        
        return self.enviar_mensaje(mensaje)
    
    def cerrar_conexion(self):
        print(f"[-] Cerrando conexión con {self.nodo_nombre or 'cliente desconocido'}")
        
        if self.nodo_id:
            self.socket_server.eliminar_id_cliente(self.nodo_id)
        
        with self.app_context:
            try:
                if self.nodo_id:
                    nodo = Nodo.query.get(self.nodo_id)
                    if nodo:
                        nodo.estado = 'No Reporta'
                        db.session.commit()
                        print(f"   📝 Nodo {nodo.nombre} marcado como 'No Reporta'")
                        
                        # Guardar evento de desconexión
                        msg = Mensaje(
                            nodo_id=self.nodo_id,
                            contenido="Cliente desconectado - marcado como No Reporta",
                            tipo='notificacion',
                            direccion='enviado',
                            requiere_ack=False,
                            fecha_creacion=get_bolivia_time()  # 👈 HORA BOLIVIA
                        )
                        db.session.add(msg)
                        db.session.commit()
            except Exception as e:
                print(f"   ❌ Error actualizando estado: {e}")
                db.session.rollback()
        
        self._cerrar_socket()
        self.running = False