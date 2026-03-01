#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLIENTE DE MONITOREO - ClusterMonitor
Ejecutar en cada nodo regional (laptop/PC cliente)
"""

import socket
import psutil
import json
import time
import threading
from datetime import datetime
import random
import os
import sys

class ClusterCliente:
    def __init__(self, servidor_host=None, servidor_port=9999):
        """
        Inicializa el cliente
        servidor_host: IP del servidor central
        servidor_port: Puerto del servidor (9999 por defecto)
        """
        self.servidor_host = servidor_host
        self.servidor_port = servidor_port
        self.socket_cliente = None
        self.id_nodo = None
        self.intervalo = 30  # segundos (parametrizable)
        self.running = True
        self.nombre_cliente = f"Cliente-{socket.gethostname()}"
        
        print(f"\n{'='*60}")
        print(f"🚀 CLIENTE DE MONITOREO - {self.nombre_cliente}")
        print(f"{'='*60}")
    
    def obtener_info_disco(self):
        """
        Obtiene información REAL del primer disco
        Usa psutil para obtener datos del sistema
        """
        try:
            discos = psutil.disk_partitions()
            if not discos:
                print("⚠ No se detectaron discos, usando datos simulados")
                return self._datos_simulados()
                
            primer_disco = discos[0]
            uso = psutil.disk_usage(primer_disco.mountpoint)
            
            # Intentar detectar tipo de disco (simplificado)
            tipo = 'SSD' if 'ssd' in primer_disco.device.lower() else 'HDD'
            
            # Calcular IOPS simulado basado en tipo de disco
            iops = random.randint(2000, 5000) if tipo == 'SSD' else random.randint(150, 500)
            
            return {
                'nombre_disco': primer_disco.device,
                'tipo_disco': tipo,
                'capacidad_total': round(uso.total / (1024**3), 2),
                'espacio_usado': round(uso.used / (1024**3), 2),
                'espacio_libre': round(uso.free / (1024**3), 2),
                'iops': iops,
                'porcentaje_uso': round((uso.used / uso.total) * 100, 2),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠ Error obteniendo disco real: {e}")
            return self._datos_simulados()
    
    def _datos_simulados(self):
        """
        Genera datos simulados si no se puede obtener información real
        Útil para pruebas sin psutil o en sistemas sin discos
        """
        capacidad = random.uniform(200, 2000)
        usado = random.uniform(50, capacidad * 0.9)
        tipo = random.choice(['SSD', 'HDD'])
        
        return {
            'nombre_disco': 'C:',
            'tipo_disco': tipo,
            'capacidad_total': round(capacidad, 2),
            'espacio_usado': round(usado, 2),
            'espacio_libre': round(capacidad - usado, 2),
            'iops': random.randint(150, 5000),
            'porcentaje_uso': round((usado / capacidad) * 100, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def auto_detectar_servidor(self):
        """
        Intenta detectar automáticamente el servidor en la red local
        """
        print("\n🔍 Buscando servidor central automáticamente...")
        
        # Obtener IP de la red local
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
            red_base = '.'.join(local_ip.split('.')[:-1]) + '.'
            
            print(f"   IP local: {local_ip}")
            print(f"   Escaneando red: {red_base}1-254")
            
            # Escanear puerto 9999 en la red local
            for i in range(1, 255):
                ip = f"{red_base}{i}"
                if ip == local_ip:
                    continue  # Saltar propia IP
                    
                try:
                    # Probar conexión al puerto de sockets (9999)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex((ip, self.servidor_port))
                    sock.close()
                    
                    if result == 0:
                        print(f"✅ ¡Servidor encontrado en {ip}:{self.servidor_port}!")
                        return ip
                        
                except:
                    pass
        except:
            pass
        
        print("❌ No se pudo detectar servidor automáticamente")
        return None
    
    def conectar(self):
        """
        Conecta al servidor central
        """
        try:
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_cliente.settimeout(5)
            self.socket_cliente.connect((self.servidor_host, self.servidor_port))
            
            print(f"\n✅ Conectado al servidor {self.servidor_host}:{self.servidor_port}")
            
            # Enviar registro inicial
            self.enviar_mensaje({
                'tipo': 'REGISTRO',
                'nombre': self.nombre_cliente,
                'ip': socket.gethostbyname(socket.gethostname()),
                'timestamp': datetime.now().isoformat()
            })
            
            # Hilo para recibir mensajes del servidor
            threading.Thread(target=self.recibir_mensajes, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False
    
    def enviar_metricas(self):
        """
        Envía métricas periódicamente al servidor
        """
        while self.running:
            try:
                metricas = self.obtener_info_disco()
                if metricas:
                    mensaje = {
                        'tipo': 'METRICA',
                        'datos': metricas,
                        'timestamp': datetime.now().isoformat()
                    }
                    if self.enviar_mensaje(mensaje):
                        print(f"📤 [{datetime.now().strftime('%H:%M:%S')}] Métricas enviadas: {metricas['capacidad_total']}GB total, {metricas['espacio_usado']:.1f}GB usado ({metricas['tipo_disco']})")
                    else:
                        print("❌ Error enviando métricas")
                
                # Esperar el intervalo configurado
                for _ in range(self.intervalo):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error en envío de métricas: {e}")
                time.sleep(5)
    
    def recibir_mensajes(self):
        """
        Recibe y procesa mensajes del servidor (comunicación bidireccional)
        """
        while self.running:
            try:
                # Recibir longitud del mensaje (4 bytes)
                header = self.socket_cliente.recv(4)
                if not header:
                    print("⚠ Conexión cerrada por el servidor")
                    break
                    
                longitud = int.from_bytes(header, 'big')
                
                # Recibir el mensaje completo
                datos = b''
                while len(datos) < longitud:
                    chunk = self.socket_cliente.recv(min(longitud - len(datos), 4096))
                    if not chunk:
                        break
                    datos += chunk
                
                if len(datos) == longitud:
                    mensaje = json.loads(datos.decode('utf-8'))
                    self.procesar_mensaje(mensaje)
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ Error recibiendo mensaje: {e}")
                break
    
    def procesar_mensaje(self, mensaje):
        """
        Procesa diferentes tipos de mensajes del servidor
        """
        tipo = mensaje.get('tipo')
        
        if tipo == 'BIENVENIDA':
            print(f"\n📩 SERVIDOR: {mensaje.get('mensaje')}")
            self.id_nodo = mensaje.get('nodo_id')
            print(f"   ID asignado: {self.id_nodo}")
            
        elif tipo == 'COMANDO':
            comando = mensaje.get('comando')
            parametros = mensaje.get('parametros', {})
            print(f"\n📩 COMANDO RECIBIDO: {comando}")
            if parametros:
                print(f"   Parámetros: {parametros}")
            
            # Guardar en archivo log
            self._guardar_log(f"COMANDO: {mensaje}")
            
            # Ejecutar comandos especiales
            if comando == 'REINICIAR':
                print("   ⚠ Ejecutando: Reiniciar servicio...")
                # Aquí iría la lógica de reinicio
            
            elif comando == 'VERIFICAR_DISCO':
                print("   🔍 Ejecutando: Verificando disco...")
                metricas = self.obtener_info_disco()
                print(f"   📊 Resultado: {metricas['espacio_libre']}GB libres")
            
            elif comando == 'ACTUALIZAR_INTERVALO':
                if 'intervalo' in parametros:
                    self.intervalo = parametros['intervalo']
                    print(f"   ⚙ Intervalo actualizado a {self.intervalo} segundos")
            
            # Enviar ACK (confirmación)
            self.enviar_mensaje({
                'tipo': 'ACK',
                'mensaje_id': mensaje.get('id', 0),
                'timestamp': datetime.now().isoformat()
            })
            print("   ✅ ACK enviado")
            
        elif tipo == 'CONFIG':
            if 'intervalo' in mensaje:
                self.intervalo = mensaje['intervalo']
                print(f"\n⚙ Intervalo actualizado a {self.intervalo} segundos")
        
        elif tipo == 'METRICA_RECIBIDA':
            print(f"   ✅ Servidor confirmó recepción")
        
        elif tipo == 'ALERTA':
            print(f"\n⚠ ALERTA: {mensaje.get('mensaje')}")
            self._guardar_log(f"ALERTA: {mensaje}")
    
    def _guardar_log(self, mensaje):
        """
        Guarda mensajes en archivo de log
        """
        try:
            with open('cliente.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()}: {mensaje}\n")
        except:
            pass
    
    def enviar_mensaje(self, mensaje):
        """
        Envía un mensaje al servidor
        Protocolo: [longitud(4 bytes)][json]
        """
        try:
            datos = json.dumps(mensaje).encode('utf-8')
            header = len(datos).to_bytes(4, 'big')
            self.socket_cliente.send(header + datos)
            return True
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False
    
    def iniciar(self):
        """
        Inicia el cliente
        """
        print(f"\n📡 Servidor: {self.servidor_host}:{self.servidor_port}")
        print(f"⏱ Intervalo de envío: {self.intervalo} segundos")
        
        if self.conectar():
            print("\n📤 Enviando métricas periódicamente...")
            print("   Presiona Ctrl+C para detener\n")
            self.enviar_metricas()
        else:
            print("\n❌ No se pudo conectar al servidor")
            print("   Verifica que:")
            print("   1. El servidor esté ejecutándose")
            print(f"   2. La IP {self.servidor_host} sea correcta")
            print("   3. No haya firewall bloqueando el puerto 9999")
    
    def detener(self):
        """
        Detiene el cliente
        """
        self.running = False
        if self.socket_cliente:
            try:
                self.socket_cliente.close()
            except:
                pass
        print("\n🛑 Cliente detenido")

def main():
    """
    Función principal
    """
    print("="*60)
    print("CLUSTERMONITOR - CLIENTE DE MONITOREO")
    print="="*60
    
    # Determinar IP del servidor
    servidor_ip = None
    
    # Si se pasa como argumento
    if len(sys.argv) > 1:
        servidor_ip = sys.argv[1]
        print(f"\n📌 Usando servidor especificado: {servidor_ip}")
    else:
        # Intentar auto-detección
        cliente_temp = ClusterCliente()
        servidor_ip = cliente_temp.auto_detectar_servidor()
        
        if not servidor_ip:
            print("\n❌ No se pudo detectar servidor automáticamente")
            ip_manual = input("📝 Ingresa la IP del servidor manualmente: ").strip()
            if ip_manual:
                servidor_ip = ip_manual
            else:
                servidor_ip = 'localhost'
                print(f"⚠ Usando localhost: {servidor_ip}")
    
    # Crear y ejecutar cliente
    cliente = ClusterCliente(servidor_ip, 9999)
    
    try:
        cliente.iniciar()
    except KeyboardInterrupt:
        print("\n")
        cliente.detener()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        cliente.detener()

if __name__ == '__main__':
    main()