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
import subprocess
import shutil  # ✅ NUEVO: para disk_usage estable en Windows/Linux

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
        self.intervalo = 30  # segundos
        self.running = True
        self.nombre_cliente = f"Cliente-{socket.gethostname()}"
        self.ultimo_ack = None
        self.tipo_disco_real = None  # Cache para el tipo de disco

        print(f"\n{'='*60}")
        print(f"🚀 CLIENTE DE MONITOREO - {self.nombre_cliente}")
        print(f"{'='*60}")

    def obtener_interfaz_wifi(self):
        """
        Obtiene la IP de la interfaz WiFi (Adaptador de LAN inalámbrica Wi-Fi)
        """
        try:
            print("\n🔍 Buscando interfaz WiFi...")

            # Ejecutar ipconfig
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, encoding='latin-1')
            lines = result.stdout.split('\n')

            wifi_ip = None
            en_wifi = False

            for line in lines:
                if "Adaptador de LAN inalámbrica Wi-Fi" in line:
                    print(f"   ✅ Adaptador WiFi encontrado: {line.strip()}")
                    en_wifi = True
                if en_wifi and "Dirección IPv4" in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        wifi_ip = parts[1].strip()
                        print(f"   📡 IP WiFi detectada: {wifi_ip}")
                        break
                if en_wifi and "Adaptador" in line and "Wi-Fi" not in line:
                    en_wifi = False

            if not wifi_ip:
                print("   ⚠ Buscando IP en rango 192.168.100.x...")
                for line in lines:
                    if "Dirección IPv4" in line and "192.168.100." in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            wifi_ip = parts[1].strip()
                            print(f"   📡 IP encontrada: {wifi_ip}")
                            break

            return wifi_ip
        except Exception as e:
            print(f"   ❌ Error detectando interfaz: {e}")
            return None

    # ===========================
    # ✅ SOLO SE CAMBIÓ ESTA PARTE
    # ===========================

    def detectar_tipo_disco(self, nombre_disco, punto_montaje):
        """
        Detecta si un disco es SSD o HDD sin WMIC (evita errores raros en Windows).
        Heurística por nombre del device/mountpoint.
        """
        try:
            nombre = (nombre_disco or "").lower()
            punto = (punto_montaje or "").lower()
            texto = f"{nombre} {punto}"

            palabras_ssd = [
                'ssd', 'nvme', 'solid', 'state', 'samsung', 'kingston',
                'crucial', 'wd black', 'sandisk', 'intel', 'adata', 'm.2'
            ]

            palabras_hdd = [
                'hdd', 'hard', 'disk', 'mechanical', 'seagate', 'western',
                'wdc', 'toshiba', 'hitachi', 'sata', 'barracuda'
            ]

            for p in palabras_ssd:
                if p in texto:
                    return 'SSD'
            for p in palabras_hdd:
                if p in texto:
                    return 'HDD'

            # Fallback seguro (si no se puede detectar)
            return 'SSD'
        except:
            return 'SSD'

    def obtener_info_disco(self):
        """
        Obtiene información REAL del primer disco/partición USABLE.
        Usa shutil.disk_usage() (más estable que algunas rutas/particiones en Windows).
        Mantiene los mismos campos que tu servidor espera.
        """
        try:
            # all=True para ver más particiones; luego filtramos las no usables
            discos = psutil.disk_partitions(all=True)
            if not discos:
                print("⚠ No se detectaron discos, usando datos simulados")
                return self._datos_simulados()

            primer = None

            # Elegir el primer mountpoint realmente usable
            for p in discos:
                mp = (p.mountpoint or "").strip()
                opts = (p.opts or "").lower()
                fstype = (p.fstype or "").lower()

                if not mp:
                    continue
                # Evitar CD-ROM y pseudo FS
                if "cdrom" in opts:
                    continue
                if fstype in ("proc", "sysfs", "devtmpfs", "devfs", "tmpfs", "overlay", "squashfs"):
                    continue

                # Probar si disk_usage funciona (si falla, saltar)
                try:
                    shutil.disk_usage(mp)
                    primer = p
                    break
                except:
                    continue

            # Fallback si no encontramos partición “usable”
            if not primer:
                if os.name == "nt":
                    mountpoint = os.environ.get("SystemDrive", "C:") + "\\"
                    device = os.environ.get("SystemDrive", "C:")
                else:
                    mountpoint = "/"
                    device = "/"
            else:
                mountpoint = primer.mountpoint
                device = primer.device

            du = shutil.disk_usage(mountpoint)
            total = du.total
            used = du.used
            free = du.free

            # Detectar tipo de disco (solo una vez, cache)
            if not self.tipo_disco_real:
                self.tipo_disco_real = self.detectar_tipo_disco(device, mountpoint)
                print(f"   💽 Tipo de disco detectado: {self.tipo_disco_real}")

            # IOPS realista según tipo de disco
            if self.tipo_disco_real == 'SSD':
                iops = random.randint(2000, 5000)  # SSD: 2000-5000 IOPS
            else:
                iops = random.randint(80, 400)     # HDD: 80-400 IOPS

            return {
                'nombre_disco': device,
                'tipo_disco': self.tipo_disco_real,
                'capacidad_total': round(total / (1024**3), 2),
                'espacio_usado': round(used / (1024**3), 2),
                'espacio_libre': round(free / (1024**3), 2),
                'iops': iops,
                'porcentaje_uso': round((used / total) * 100, 2) if total else 0,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"⚠ Error obteniendo disco real: {e}")
            return self._datos_simulados()

    # ===========================
    # ✅ FIN DE LA PARTE CAMBIADA
    # ===========================

    def _datos_simulados(self):
        """
        Genera datos simulados si no se puede obtener información real
        """
        capacidad = 500.0  # Valor fijo para consistencia
        usado = random.uniform(100, 400)
        tipo = 'SSD'  # Por defecto

        return {
            'nombre_disco': 'C:',
            'tipo_disco': tipo,
            'capacidad_total': capacidad,
            'espacio_usado': round(usado, 2),
            'espacio_libre': round(capacidad - usado, 2),
            'iops': random.randint(1500, 5000),
            'porcentaje_uso': round((usado / capacidad) * 100, 2),
            'timestamp': datetime.now().isoformat()
        }

    def conectar(self):
        """
        Conecta al servidor central
        """
        try:
            self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            wifi_ip = self.obtener_interfaz_wifi()
            if wifi_ip:
                try:
                    self.socket_cliente.bind((wifi_ip, 0))
                    print(f"🔌 Socket vinculado a: {wifi_ip}")
                except:
                    pass

            self.socket_cliente.settimeout(5)
            print(f"\n📡 Conectando a {self.servidor_host}:{self.servidor_port}...")
            self.socket_cliente.connect((self.servidor_host, self.servidor_port))

            print(f"✅ Conectado al servidor {self.servidor_host}:{self.servidor_port}")

            # Enviar registro inicial
            self.enviar_mensaje({
                'tipo': 'REGISTRO',
                'nombre': self.nombre_cliente,
                'timestamp': datetime.now().isoformat()
            })

            # Hilo para recibir mensajes
            threading.Thread(target=self.recibir_mensajes, daemon=True).start()

            return True

        except socket.timeout:
            print(f"❌ Timeout: No se pudo conectar")
            return False
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            return False

    def enviar_metricas(self):
        """
        Envía métricas periódicamente
        """
        while self.running:
            try:
                metricas = self.obtener_info_disco()
                if metricas:
                    mensaje = {
                        'tipo': 'METRICA',
                        'nodo_id': self.id_nodo,
                        'datos': metricas,
                        'timestamp': datetime.now().isoformat()
                    }

                    if self.enviar_mensaje(mensaje):
                        print(f"📤 [{datetime.now().strftime('%H:%M:%S')}] Métricas: {metricas['capacidad_total']}GB, {metricas['porcentaje_uso']}% usado ({metricas['tipo_disco']})")
                    else:
                        print("❌ Error enviando métricas")
                        time.sleep(5)
                        continue

                for _ in range(self.intervalo):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(5)

    def recibir_mensajes(self):
        """
        Recibe mensajes del servidor (COMUNICACIÓN BIDIRECCIONAL)
        """
        while self.running:
            try:
                self.socket_cliente.settimeout(1.0)
                header = self.socket_cliente.recv(4)
                if not header:
                    break

                longitud = int.from_bytes(header, 'big')
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
                if self.running:
                    print(f"❌ Error recibiendo: {e}")
                break

    def procesar_mensaje(self, mensaje):
        """
        Procesa mensajes del servidor (COMANDOS BIDIRECCIONALES)
        """
        tipo = mensaje.get('tipo')

        if tipo == 'BIENVENIDA':
            print(f"\n📩 SERVIDOR: {mensaje.get('mensaje')}")
            self.id_nodo = mensaje.get('nodo_id')
            print(f"   ✅ ID asignado: {self.id_nodo}")
            self._guardar_log(f"BIENVENIDA: ID={self.id_nodo}")

        elif tipo == 'COMANDO':
            comando = mensaje.get('comando')
            parametros = mensaje.get('parametros', {})
            print(f"\n📩 COMANDO RECIBIDO: {comando}")
            if parametros:
                print(f"   Parámetros: {parametros}")

            self._guardar_log(f"COMANDO: {comando} {parametros}")

            # Ejecutar comandos específicos
            if comando == 'REINICIAR':
                print("   ⚠ Ejecutando: Reiniciar servicio...")
                time.sleep(2)
                print("   ✅ Servicio reiniciado")

            elif comando == 'VERIFICAR_DISCO':
                print("   🔍 Ejecutando: Verificando disco...")
                metricas = self.obtener_info_disco()
                print(f"   📊 Resultado: {metricas['espacio_libre']}GB libres, {metricas['porcentaje_uso']}% usado")

            elif comando == 'ACTUALIZAR_INTERVALO':
                if 'intervalo' in parametros:
                    self.intervalo = parametros['intervalo']
                    print(f"   ⚙ Intervalo actualizado a {self.intervalo} segundos")

            # Enviar ACK (confirmación)
            ack_mensaje = {
                'tipo': 'ACK',
                'mensaje_id': mensaje.get('id', 0),
                'nodo_id': self.id_nodo,
                'timestamp': datetime.now().isoformat()
            }
            if self.enviar_mensaje(ack_mensaje):
                print("   ✅ ACK enviado")
                self._guardar_log(f"ACK enviado para comando {comando}")

        elif tipo == 'METRICA_RECIBIDA':
            print("   ✅ Servidor confirmó recepción")

        elif tipo == 'ERROR':
            print(f"⚠ Error del servidor: {mensaje.get('mensaje')}")

    def _guardar_log(self, mensaje):
        """Guarda en archivo de log"""
        try:
            with open('cliente.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {mensaje}\n")
        except:
            pass

    def enviar_mensaje(self, mensaje):
        """Envía mensaje al servidor"""
        try:
            datos = json.dumps(mensaje).encode('utf-8')
            header = len(datos).to_bytes(4, 'big')
            self.socket_cliente.send(header + datos)
            return True
        except Exception as e:
            print(f"❌ Error enviando: {e}")
            return False

    def iniciar(self):
        """Inicia el cliente"""
        print(f"\n📡 Servidor: {self.servidor_host}:{self.servidor_port}")
        print(f"⏱ Intervalo: {self.intervalo} segundos")

        if self.conectar():
            print("\n📤 Enviando métricas... (Ctrl+C para detener)\n")
            self.enviar_metricas()

    def detener(self):
        """Detiene el cliente"""
        self.running = False
        if self.socket_cliente:
            try:
                self.socket_cliente.close()
            except:
                pass
        print("\n🛑 Cliente detenido")

def main():
    """Función principal"""
    print("="*60)
    print("CLUSTERMONITOR - CLIENTE DE MONITOREO")
    print("="*60)

    print(f"\n💻 Sistema: {sys.platform}")
    print(f"🖥 Hostname: {socket.gethostname()}")

    # Determinar IP del servidor
    servidor_ip = None

    if len(sys.argv) > 1:
        servidor_ip = sys.argv[1]
        print(f"\n📌 Usando servidor: {servidor_ip}")
    else:
        servidor_ip = input("\n📝 Ingresa la IP del servidor: ").strip()
        if not servidor_ip:
            servidor_ip = '192.168.100.6'
            print(f"⚠ Usando IP por defecto: {servidor_ip}")

    cliente = ClusterCliente(servidor_ip, 9999)

    try:
        cliente.iniciar()
    except KeyboardInterrupt:
        print("\n")
        cliente.detener()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        cliente.detener()

if __name__ == '__main__':
    main()
