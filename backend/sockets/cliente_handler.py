"""
Manejador de clientes en hilos separados
----------------------------------------
Cada conexión de cliente se maneja en un hilo independiente.
Procesa registro, métricas y comandos bidireccionales.
"""

import threading
import socket
import time
from datetime import datetime
from app.sockets.protocolo import ProtocoloCluster
from app.models.nodo import Nodo
from app.models.metrica import Metrica
from app.models.mensaje import Mensaje
from app import db

class ClienteHandler(threading.Thread):
    def __init__(self, client_socket, address, app_context, socket_server):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        self.app_context = app_context
        self.socket_server = socket_server  # Referencia al servidor
        self.nodo_id = None
        self.nodo_nombre = None
        self.running = True
        self.daemon = True
        
    def run(self):
        """Método principal del hilo"""
        print(f"[+] Nuevo cliente conectado: {self.address}")
        
        # Registrar o actualizar nodo en la BD
        self.registrar_nodo()
        
        # Enviar mensaje de bienvenida
        self.enviar_bienvenida()
        
        while self.running:
            try:
                # Configurar timeout para no bloquear forever
                self.client_socket.settimeout(5.0)
                
                # Recibir mensaje del cliente
                mensaje = ProtocoloCluster.decode_message(self.client_socket)
                
                if not mensaje:
                    # Timeout o conexión cerrada
                    continue
                
                # Procesar según el tipo
                self.procesar_mensaje(mensaje)
                
            except socket.timeout:
                # Timeout normal, continuar
                continue
            except (ConnectionResetError, BrokenPipeError):
                print(f"[-] Cliente {self.address} desconectado abruptamente")
                break
            except Exception as e:
                print(f"[!] Error con cliente {self.address}: {e}")
                break
        
        self.cerrar_conexion()
    
    def registrar_nodo(self):
        """Registra el nodo en la base de datos"""
        with self.app_context:
            try:
                # Buscar si el nodo ya existe por IP
                nodo = Nodo.query.filter_by(ip_address=self.address[0]).first()
                
                if not nodo:
                    # Crear nuevo nodo
                    count = Nodo.query.count() + 1
                    nombre = f"Regional {count}"
                    
                    nodo = Nodo(
                        nombre=nombre,
                        ip_address=self.address[0],
                        puerto=self.address[1],
                        estado='Activo',
                        ultima_conexion=datetime.utcnow()
                    )
                    db.session.add(nodo)
                    db.session.commit()
                    print(f"[+] Nuevo nodo registrado: {nodo.nombre} (ID: {nodo.id})")
                    
                    # Registrar en el servidor para control de duplicados
                    self.socket_server.registrar_id_cliente(nodo.id, self)
                    
                else:
                    # Verificar si ya hay una conexión activa para este nodo
                    if nodo.id in self.socket_server.client_ids:
                        print(f"[!] Nodo {nodo.nombre} ya tiene una conexión activa")
                        # Enviar mensaje de error y cerrar
                        self.enviar_mensaje({
                            'tipo': 'ERROR',
                            'mensaje': 'Ya existe una conexión activa para este nodo'
                        })
                        self.running = False
                        return
                    
                    # Actualizar nodo existente
                    nodo.estado = 'Activo'
                    nodo.ultima_conexion = datetime.utcnow()
                    nodo.puerto = self.address[1]
                    db.session.commit()
                    print(f"[+] Nodo reconectado: {nodo.nombre} (ID: {nodo.id})")
                    
                    # Registrar en el servidor
                    self.socket_server.registrar_id_cliente(nodo.id, self)
                
                self.nodo_id = nodo.id
                self.nodo_nombre = nodo.nombre
                
            except Exception as e:
                print(f"[!] Error registrando nodo: {e}")
                db.session.rollback()
    
    def enviar_bienvenida(self):
        """Envía mensaje de bienvenida al cliente"""
        mensaje = {
            'tipo': 'BIENVENIDA',
            'nodo_id': self.nodo_id,
            'mensaje': f'Conectado al ClusterMonitor. Nodo ID: {self.nodo_id}',
            'timestamp': datetime.utcnow().isoformat()
        }
        self.enviar_mensaje(mensaje)
        
        # Guardar en BD
        with self.app_context:
            try:
                msg_db = Mensaje(
                    nodo_id=self.nodo_id,
                    contenido=mensaje['mensaje'],
                    tipo='bienvenida',
                    direccion='enviado',
                    requiere_ack=False
                )
                db.session.add(msg_db)
                db.session.commit()
            except:
                db.session.rollback()
    
    def procesar_mensaje(self, mensaje):
        """Procesa diferentes tipos de mensajes"""
        tipo = mensaje.get('tipo')
        
        with self.app_context:
            try:
                if tipo == 'METRICA':
                    self.procesar_metrica(mensaje)
                elif tipo == 'ACK':
                    self.procesar_ack(mensaje)
                elif tipo == 'REGISTRO':
                    self.procesar_registro(mensaje)
                else:
                    print(f"[?] Tipo de mensaje desconocido: {tipo}")
                    # Responder con error
                    self.enviar_mensaje({
                        'tipo': 'ERROR',
                        'mensaje': f'Tipo de mensaje no soportado: {tipo}'
                    })
            except Exception as e:
                print(f"[!] Error procesando mensaje: {e}")
                db.session.rollback()
    
    def procesar_metrica(self, mensaje):
        """Guarda las métricas recibidas en la BD con manejo de errores"""
        try:
            datos = mensaje.get('datos', {})
            
            # Validar datos requeridos
            capacidad = datos.get('capacidad_total', 0)
            usado = datos.get('espacio_usado', 0)
            
            # Calcular porcentaje de uso
            if capacidad > 0:
                porcentaje = (usado / capacidad) * 100
            else:
                porcentaje = 0
            
            # Crear nueva métrica
            metrica = Metrica(
                nodo_id=self.nodo_id,
                nombre_disco=datos.get('nombre_disco', 'Desconocido'),
                tipo_disco=datos.get('tipo_disco', 'Desconocido'),
                capacidad_total=float(capacidad),
                espacio_usado=float(usado),
                espacio_libre=float(datos.get('espacio_libre', 0)),
                iops=int(datos.get('iops', 0)),
                porcentaje_uso=float(porcentaje),
                timestamp=datetime.utcnow()
            )
            
            db.session.add(metrica)
            
            # Actualizar última conexión del nodo
            nodo = Nodo.query.get(self.nodo_id)
            if nodo:
                nodo.ultima_conexion = datetime.utcnow()
                nodo.estado = 'Activo'
            
            db.session.commit()
            print(f"[✓] Métricas guardadas para nodo {self.nodo_nombre} (ID: {self.nodo_id})")
            
            # Enviar confirmación
            self.enviar_mensaje({
                'tipo': 'METRICA_RECIBIDA',
                'status': 'ok',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            print(f"[!] Error guardando métricas: {e}")
            db.session.rollback()
            self.enviar_mensaje({
                'tipo': 'ERROR',
                'mensaje': f'Error guardando métricas: {str(e)}'
            })
    
    def procesar_ack(self, mensaje):
        """Procesa confirmación de mensajes"""
        message_id = mensaje.get('message_id')
        print(f"[✓] ACK recibido de nodo {self.nodo_nombre} para mensaje {message_id}")
        
        with self.app_context:
            try:
                # Buscar mensaje por ID y marcar como confirmado
                mensaje_db = Mensaje.query.filter_by(id=message_id).first()
                if mensaje_db:
                    mensaje_db.ack_recibido = True
                    mensaje_db.fecha_ack = datetime.utcnow()
                    db.session.commit()
                    print(f"   ✓ Mensaje {message_id} marcado como confirmado")
            except:
                db.session.rollback()
    
    def procesar_registro(self, mensaje):
        """Procesa mensaje de registro inicial"""
        nombre_cliente = mensaje.get('nombre', f'Cliente-{self.address[0]}')
        print(f"[+] Registro de nodo {self.nodo_nombre}: {nombre_cliente}")
        
        # Actualizar nombre si se proporcionó
        with self.app_context:
            try:
                nodo = Nodo.query.get(self.nodo_id)
                if nodo and mensaje.get('nombre'):
                    nodo.nombre = mensaje['nombre']
                    db.session.commit()
                    self.nodo_nombre = nodo.nombre
            except:
                db.session.rollback()
        
        # Enviar confirmación
        self.enviar_mensaje({
            'tipo': 'REGISTRO_CONFIRMADO',
            'nodo_id': self.nodo_id,
            'mensaje': 'Registro exitoso',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def enviar_mensaje(self, mensaje):
        """Envía un mensaje al cliente"""
        try:
            datos = ProtocoloCluster.encode_message(mensaje)
            if datos:
                self.client_socket.send(datos)
                return True
        except (ConnectionResetError, BrokenPipeError):
            print(f"[!] Conexión perdida con cliente {self.nodo_nombre}")
            self.running = False
        except Exception as e:
            print(f"[!] Error enviando mensaje: {e}")
        return False
    
    def enviar_comando(self, comando, parametros=None):
        """Envía un comando específico al cliente"""
        mensaje = ProtocoloCluster.create_command_message(comando, parametros)
        
        # Guardar en BD
        with self.app_context:
            try:
                msg_db = Mensaje(
                    nodo_id=self.nodo_id,
                    contenido=json.dumps(mensaje),
                    tipo='comando',
                    direccion='enviado',
                    requiere_ack=True
                )
                db.session.add(msg_db)
                db.session.commit()
                mensaje['id'] = msg_db.id  # Asignar ID para tracking
            except:
                db.session.rollback()
        
        return self.enviar_mensaje(mensaje)
    
    def cerrar_conexion(self):
        """Cierra la conexión y actualiza estado"""
        print(f"[-] Cerrando conexión con {self.nodo_nombre} ({self.address})")
        
        # Eliminar del registro de IDs
        if self.nodo_id:
            self.socket_server.eliminar_id_cliente(self.nodo_id)
        
        with self.app_context:
            try:
                nodo = Nodo.query.get(self.nodo_id)
                if nodo:
                    nodo.estado = 'No Reporta'
                    db.session.commit()
                    print(f"[!] Nodo {nodo.nombre} marcado como 'No Reporta'")
            except Exception as e:
                print(f"[!] Error actualizando estado: {e}")
                db.session.rollback()
        
        try:
            self.client_socket.close()
        except:
            pass
        self.running = False