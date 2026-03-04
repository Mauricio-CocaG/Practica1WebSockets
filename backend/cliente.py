#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================
 CLUSTERMONITOR - Cliente de Monitoreo de Nodos
==============================================================
 Arquitectura:
   - Protocolo   : empaqueta/desempaqueta mensajes TCP
   - RecolectorMetricas : obtiene metricas de disco con psutil
   - Cliente     : logica principal (conexion, hilos, comandos)

 Uso:
   python cliente.py [IP_SERVIDOR]
   python cliente.py          (auto-deteccion en LAN)
==============================================================
"""

import socket
import json
import struct
import time
import threading
import logging
import sys
import os
import random
from datetime import datetime

# ── dependencias externas ────────────────────────────────────
try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

try:
    import pytz
    _BOLIVIA_TZ = pytz.timezone('America/La_Paz')
    _PYTZ = True
except ImportError:
    _PYTZ = False


def _bolivia_now() -> datetime:
    """Retorna la hora actual de Bolivia (UTC-4) como naive datetime."""
    if _PYTZ:
        return datetime.now(_BOLIVIA_TZ).replace(tzinfo=None)
    # Fallback: UTC-4 manual
    from datetime import timezone, timedelta
    return datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)


# ==============================================================
# LOGGING
# Doble handler: archivo (DEBUG) + consola (INFO)
# Ambos usan hora de Bolivia (UTC-4).
# ==============================================================

class _BoliviaFormatter(logging.Formatter):
    """Formatter que muestra la hora de Bolivia en los logs."""
    def formatTime(self, record, datefmt=None):
        dt = _bolivia_now()
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def _configurar_logging() -> logging.Logger:
    logger = logging.getLogger('ClusterMonitor')
    logger.setLevel(logging.DEBUG)

    fmt = _BoliviaFormatter(
        '%(asctime)s [%(levelname)-8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler archivo
    fh = logging.FileHandler('cliente.log', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Handler consola
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


log = _configurar_logging()


# ==============================================================
# PROTOCOLO
# Formato de mensaje: [4 bytes longitud big-endian] + [JSON UTF-8]
# ==============================================================
class Protocolo:
    """
    Maneja la serializacion/deserializacion de mensajes sobre TCP.
    Cabecera de 4 bytes (big-endian) indica la longitud del payload JSON.
    """

    @staticmethod
    def empaquetar(datos: dict) -> bytes:
        """Convierte un dict en bytes listos para enviar."""
        payload = json.dumps(datos, ensure_ascii=False).encode('utf-8')
        cabecera = struct.pack('>I', len(payload))
        return cabecera + payload

    @staticmethod
    def desempaquetar(conn: socket.socket) -> dict | None:
        """
        Lee un mensaje completo desde el socket.
        Retorna el dict o None si la conexion se cerro.
        """
        try:
            raw = Protocolo._leer_exacto(conn, 4)
            if raw is None:
                return None
            longitud = struct.unpack('>I', raw)[0]

            # Validacion basica de longitud (max 10 MB)
            if longitud == 0 or longitud > 10 * 1024 * 1024:
                log.warning(f'Longitud de mensaje invalida: {longitud}')
                return None

            payload = Protocolo._leer_exacto(conn, longitud)
            if payload is None:
                return None

            return json.loads(payload.decode('utf-8'))

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            log.error(f'Error decodificando mensaje: {e}')
            return None
        except Exception as e:
            log.debug(f'Error en desempaquetar: {e}')
            return None

    @staticmethod
    def _leer_exacto(conn: socket.socket, n: int) -> bytes | None:
        """Lee exactamente n bytes del socket, bloqueante."""
        buf = b''
        while len(buf) < n:
            try:
                chunk = conn.recv(n - len(buf))
                if not chunk:
                    return None          # Conexion cerrada por el otro extremo
                buf += chunk
            except socket.timeout:
                continue                # Timeout normal, seguir esperando
            except OSError:
                return None
        return buf


# ==============================================================
# RECOLECTOR DE METRICAS
# Usa psutil para datos reales; datos simulados como fallback.
# ==============================================================
class RecolectorMetricas:
    """
    Obtiene informacion del disco local.
    Si psutil no esta disponible, genera datos simulados para pruebas.
    """

    @staticmethod
    def obtener() -> dict:
        """Punto de entrada principal. Retorna metricas del disco."""
        if _PSUTIL:
            return RecolectorMetricas._real()
        log.warning('psutil no disponible, usando datos simulados.')
        return RecolectorMetricas._simular()

    @staticmethod
    def _real() -> dict:
        """Lee el primer disco fisico accesible con psutil."""
        try:
            particiones = psutil.disk_partitions(all=False)
            disco = None
            for p in particiones:
                # Buscar la primera particion montada y accesible
                if p.mountpoint and os.path.exists(p.mountpoint):
                    disco = p
                    break

            if disco is None:
                log.warning('No se encontro particion accesible.')
                return RecolectorMetricas._simular()

            uso = psutil.disk_usage(disco.mountpoint)

            # Deteccion simplificada del tipo de disco
            tipo = 'SSD' if any(k in disco.opts.lower() for k in ('ssd', 'nvme')) else 'HDD'

            # IOPS simulado segun tipo (psutil no expone IOPS directamente)
            iops = random.randint(2000, 5000) if tipo == 'SSD' else random.randint(150, 500)

            return {
                'nombre_disco': disco.device or disco.mountpoint,
                'tipo_disco'  : tipo,
                'capacidad_total': round(uso.total / 1e9, 2),   # GB
                'espacio_usado'  : round(uso.used  / 1e9, 2),
                'espacio_libre'  : round(uso.free  / 1e9, 2),
                'porcentaje_uso' : round(uso.percent, 2),
                'iops'           : iops,
                'timestamp'      : _bolivia_now().isoformat(),
            }

        except Exception as e:
            log.warning(f'Error leyendo disco real: {e}. Usando simulacion.')
            return RecolectorMetricas._simular()

    @staticmethod
    def _simular() -> dict:
        """Genera datos ficticios para entornos sin acceso real al disco."""
        cap   = round(random.uniform(200, 2000), 2)
        usado = round(random.uniform(50, cap * 0.9), 2)
        tipo  = random.choice(['SSD', 'HDD'])
        return {
            'nombre_disco'   : 'C:\\',
            'tipo_disco'     : tipo,
            'capacidad_total': cap,
            'espacio_usado'  : usado,
            'espacio_libre'  : round(cap - usado, 2),
            'porcentaje_uso' : round((usado / cap) * 100, 2),
            'iops'           : random.randint(150, 5000),
            'timestamp'      : _bolivia_now().isoformat(),
        }


# ==============================================================
# CLIENTE
# Clase principal. Gestiona conexion, reconexion y dos hilos:
#   - Hilo "Emisor"  : envia metricas cada `intervalo` segundos
#   - Hilo "Receptor": escucha mensajes/comandos del servidor
# ==============================================================
class Cliente:
    """
    Cliente TCP para ClusterMonitor.

    Parametros:
        servidor_host  : IP del servidor central.
        servidor_puerto: Puerto TCP del servidor (default 9999).
        intervalo      : Segundos entre envios de metricas (default 30).
    """

    def __init__(self, servidor_host: str, servidor_puerto: int = 9999, intervalo: int = 30):
        self.servidor_host   = servidor_host
        self.servidor_puerto = servidor_puerto
        self.intervalo       = intervalo
        self.nombre          = f'Cliente-{socket.gethostname()}'

        # Socket activo
        self._sock: socket.socket | None = None

        # Eventos de control de hilos
        self._ejecutando = threading.Event()   # True mientras el cliente corre
        self._conectado  = threading.Event()   # True cuando el socket esta activo

        # Lock para envios concurrentes (emisor + receptor comparten socket)
        self._lock_envio = threading.Lock()

    # ----------------------------------------------------------
    # API publica
    # ----------------------------------------------------------

    def iniciar(self):
        """
        Arranca el cliente:
          1. Imprime cabecera de inicio.
          2. Intenta conectar al servidor.
          3. Lanza hilo Emisor y hilo Receptor.
          4. Bloquea hasta Ctrl+C.
        """
        self._imprimir_cabecera()
        self._ejecutando.set()
        log.info('Iniciando cliente...')

        if not self._conectar():
            log.error('No se pudo establecer conexion inicial. Abortando.')
            return

        # Hilo Receptor: escucha mensajes entrantes del servidor
        hilo_rx = threading.Thread(
            target=self._escuchar_servidor,
            name='Receptor',
            daemon=True
        )

        # Hilo Emisor: envia metricas periodicamente
        hilo_tx = threading.Thread(
            target=self._enviar_metricas_periodicamente,
            name='Emisor',
            daemon=True
        )

        hilo_rx.start()
        log.info('Hilo Receptor iniciado.')

        hilo_tx.start()
        log.info(f'Hilo Emisor iniciado (intervalo: {self.intervalo}s).')

        log.info('Cliente en marcha. Presiona Ctrl+C para detener.')

        # Mantener el hilo principal vivo
        try:
            while self._ejecutando.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.detener()

    def detener(self):
        """Cierre seguro: detiene hilos y cierra el socket."""
        log.info('Deteniendo cliente...')
        self._ejecutando.clear()
        self._conectado.clear()
        self._cerrar_socket()
        log.info('Cliente detenido.')

    # ----------------------------------------------------------
    # Conexion y reconexion
    # ----------------------------------------------------------

    def _conectar(self) -> bool:
        """
        Intenta abrir la conexion TCP al servidor.
        Si tiene exito, envia el mensaje de REGISTRO inicial.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(8)
            sock.connect((self.servidor_host, self.servidor_puerto))
            sock.settimeout(15)   # Timeout de lectura para el receptor

            self._sock = sock
            self._conectado.set()
            log.info(f'Conectado a {self.servidor_host}:{self.servidor_puerto}')

            # Mensaje de presentacion al servidor
            self._enviar({
                'tipo'     : 'REGISTRO',
                'nombre'   : self.nombre,
                'ip'       : self._ip_local(),
                'timestamp': _bolivia_now().isoformat(),
            })
            return True

        except ConnectionRefusedError:
            log.error(f'Conexion rechazada en {self.servidor_host}:{self.servidor_puerto}')
        except socket.timeout:
            log.error('Timeout al intentar conectar.')
        except OSError as e:
            log.error(f'Error de red al conectar: {e}')
        except Exception as e:
            log.error(f'Error inesperado al conectar: {e}')

        self._conectado.clear()
        return False

    def _reconectar(self):
        """
        Bucle de reconexion con backoff lineal.
        Espera: 10s, 20s, 30s ... hasta max 120s entre intentos.
        """
        self._cerrar_socket()
        self._conectado.clear()
        intento = 0

        while self._ejecutando.is_set():
            intento += 1
            espera = min(10 * intento, 120)
            log.info(f'Reconectando en {espera}s (intento #{intento})...')
            time.sleep(espera)

            if self._conectar():
                log.info('Reconexion exitosa.')
                return

        log.info('Reconexion cancelada (cliente detenido).')

    def _cerrar_socket(self):
        """Cierra el socket activo de forma segura."""
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    # ----------------------------------------------------------
    # Hilo Emisor: envia metricas periodicamente
    # ----------------------------------------------------------

    def _enviar_metricas_periodicamente(self):
        """
        Hilo que recolecta metricas del disco y las envia al servidor.
        Primer envio es inmediato; luego espera `self.intervalo` segundos.
        """
        # Primer envio inmediato al arrancar
        self._ciclo_envio()

        while self._ejecutando.is_set():
            # Esperar intervalo de forma interrumpible (tick de 1s)
            for _ in range(self.intervalo):
                if not self._ejecutando.is_set():
                    return
                time.sleep(1)

            self._ciclo_envio()

    def _ciclo_envio(self):
        """Recolecta y envia un paquete de metricas."""
        if not self._conectado.is_set():
            log.debug('Sin conexion, omitiendo envio de metricas.')
            return

        metricas = RecolectorMetricas.obtener()
        enviado  = self._enviar({
            'tipo'     : 'METRICA',
            'datos'    : metricas,
            'timestamp': _bolivia_now().isoformat(),
        })

        if enviado:
            log.info(
                f'Metrica enviada | Disco: {metricas["nombre_disco"]} | '
                f'Usado: {metricas["espacio_usado"]} GB / '
                f'{metricas["capacidad_total"]} GB | '
                f'{metricas["porcentaje_uso"]}%'
            )
        else:
            log.warning('Fallo al enviar metricas.')

    # ----------------------------------------------------------
    # Hilo Receptor: escucha mensajes del servidor
    # ----------------------------------------------------------

    def _escuchar_servidor(self):
        """
        Hilo bloqueante que lee mensajes entrantes del servidor.
        Si se pierde la conexion, inicia la reconexion.
        """
        while self._ejecutando.is_set():
            if not self._conectado.is_set():
                # Esperar a que se restaure la conexion
                time.sleep(1)
                continue

            mensaje = Protocolo.desempaquetar(self._sock)

            if mensaje is None:
                if self._ejecutando.is_set():
                    log.warning('Conexion perdida con el servidor.')
                    self._reconectar()
                continue

            self._procesar_mensaje(mensaje)

    # ----------------------------------------------------------
    # Procesamiento de mensajes entrantes
    # ----------------------------------------------------------

    def _procesar_mensaje(self, msg: dict):
        """Despacha el mensaje segun su tipo."""
        tipo = msg.get('tipo', '').upper()

        if tipo == 'BIENVENIDA':
            log.info(
                f'Registro confirmado | '
                f'ID de nodo: {msg.get("nodo_id")} | '
                f'{msg.get("mensaje", "")}'
            )

        elif tipo == 'REGISTRO_CONFIRMADO':
            log.info(f'Nodo registrado correctamente | ID: {msg.get("nodo_id")}')

        elif tipo == 'METRICA_RECIBIDA':
            log.debug('Servidor confirmo recepcion de metrica.')

        elif tipo == 'COMANDO':
            self._ejecutar_comando(msg)

        elif tipo == 'CONFIG':
            # El servidor puede reconfigurar el intervalo remotamente
            nuevo = msg.get('intervalo')
            if isinstance(nuevo, int) and nuevo > 0:
                self.intervalo = nuevo
                log.info(f'Intervalo actualizado a {nuevo}s por el servidor.')

        elif tipo == 'ALERTA':
            log.warning(f'ALERTA del servidor: {msg.get("mensaje")}')

        elif tipo == 'ERROR':
            log.error(f'Error del servidor: {msg.get("mensaje")}')

        else:
            log.debug(f'Tipo de mensaje no reconocido: {tipo}')

    def _ejecutar_comando(self, msg: dict):
        """
        Ejecuta un comando recibido desde el servidor.
        Comandos soportados:
          - VERIFICAR_DISCO       : reporta estado actual del disco
          - ACTUALIZAR_INTERVALO  : cambia el periodo de envio
          - REINICIAR             : simula reinicio del servicio
        Al finalizar, envia un ACK al servidor.
        """
        comando = msg.get('comando', '').upper()
        params  = msg.get('parametros', {})
        log.info(f'Comando recibido: {comando} | Parametros: {params}')

        try:
            if comando == 'VERIFICAR_DISCO':
                m = RecolectorMetricas.obtener()
                log.info(
                    f'Verificacion de disco: {m["espacio_libre"]} GB libres '
                    f'({m["porcentaje_uso"]}% usado)'
                )

            elif comando == 'ACTUALIZAR_INTERVALO':
                nuevo = params.get('intervalo')
                if isinstance(nuevo, int) and nuevo > 0:
                    self.intervalo = nuevo
                    log.info(f'Intervalo de envio actualizado a {nuevo}s.')
                else:
                    log.warning('ACTUALIZAR_INTERVALO: valor de intervalo invalido.')

            elif comando == 'REINICIAR':
                log.warning('Comando REINICIAR recibido. Simulando reinicio...')
                # Aqui iria logica real de reinicio del servicio

            else:
                log.warning(f'Comando desconocido: {comando}')

        except Exception as e:
            log.error(f'Error ejecutando comando {comando}: {e}')

        # Confirmar recepcion del comando al servidor
        self._enviar({
            'tipo'      : 'ACK',
            'message_id': msg.get('id', 0),
            'timestamp' : _bolivia_now().isoformat(),
        })
        log.debug(f'ACK enviado para comando {comando}.')

    # ----------------------------------------------------------
    # Envio de mensajes (thread-safe)
    # ----------------------------------------------------------

    def _enviar(self, datos: dict) -> bool:
        """
        Envia un mensaje al servidor de forma thread-safe.
        Retorna True si el envio fue exitoso.
        """
        try:
            with self._lock_envio:
                if self._sock and self._conectado.is_set():
                    self._sock.sendall(Protocolo.empaquetar(datos))
                    return True
        except BrokenPipeError:
            log.debug('BrokenPipe al enviar, conexion perdida.')
            self._conectado.clear()
        except OSError as e:
            log.debug(f'Error de red al enviar: {e}')
            self._conectado.clear()
        except Exception as e:
            log.error(f'Error inesperado al enviar: {e}')
        return False

    # ----------------------------------------------------------
    # Utilidades
    # ----------------------------------------------------------

    def _ip_local(self) -> str:
        """Obtiene la IP local de la maquina."""
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return '127.0.0.1'

    def _imprimir_cabecera(self):
        """Imprime informacion de inicio en consola y log."""
        sep = '=' * 58
        log.info(sep)
        log.info(' ClusterMonitor - Cliente de Monitoreo')
        log.info(sep)
        log.info(f'Nombre    : {self.nombre}')
        log.info(f'IP local  : {self._ip_local()}')
        log.info(f'Servidor  : {self.servidor_host}:{self.servidor_puerto}')
        log.info(f'Intervalo : {self.intervalo} segundos')
        log.info(f'psutil    : {"disponible" if _PSUTIL else "NO disponible (simulacion)"}')
        log.info(sep)

    # ----------------------------------------------------------
    # Auto-deteccion del servidor en la LAN
    # ----------------------------------------------------------

    @staticmethod
    def detectar_servidor(puerto: int = 9999, timeout: float = 0.15) -> str | None:
        """
        Escanea la red local buscando el servidor en el puerto indicado.
        Retorna la primera IP que responda, o None si no encuentra ninguna.

        Parametros:
            puerto : puerto TCP del servidor (default 9999).
            timeout: timeout por host en segundos (default 0.15).
        """
        log.info('Buscando servidor en la red local...')
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            base = '.'.join(local_ip.split('.')[:-1]) + '.'
            log.info(f'IP local: {local_ip} | Escaneando {base}1-254 en puerto {puerto}...')

            for i in range(1, 255):
                ip = f'{base}{i}'
                if ip == local_ip:
                    continue
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(timeout)
                    resultado = s.connect_ex((ip, puerto))
                    s.close()
                    if resultado == 0:
                        log.info(f'Servidor encontrado en {ip}:{puerto}')
                        return ip
                except Exception:
                    pass

        except Exception as e:
            log.error(f'Error durante auto-deteccion: {e}')

        log.warning('No se encontro ningun servidor en la red.')
        return None


# ==============================================================
# PUNTO DE ENTRADA
# ==============================================================
if __name__ == '__main__':
    print('=' * 58)
    print(' ClusterMonitor - Nodo Cliente')
    print('=' * 58)

    # Determinar IP del servidor
    ip_servidor = None

    if len(sys.argv) > 1:
        # IP pasada como argumento de linea de comandos
        ip_servidor = sys.argv[1]
        log.info(f'Servidor especificado por argumento: {ip_servidor}')
    else:
        # Intentar auto-deteccion en la LAN
        ip_servidor = Cliente.detectar_servidor(puerto=9999)
        if not ip_servidor:
            try:
                ip_servidor = input('Ingresa la IP del servidor: ').strip()
            except (EOFError, KeyboardInterrupt):
                ip_servidor = ''
            if not ip_servidor:
                ip_servidor = '127.0.0.1'
                log.info(f'Usando localhost: {ip_servidor}')

    # Crear e iniciar el cliente
    cliente = Cliente(
        servidor_host   = ip_servidor,
        servidor_puerto = 9999,
        intervalo       = 30,
    )

    try:
        cliente.iniciar()
    except KeyboardInterrupt:
        cliente.detener()
    except Exception as e:
        log.critical(f'Error fatal: {e}')
        cliente.detener()
        sys.exit(1)


# ==============================================================
# ESTRUCTURA DEL CODIGO
# ==============================================================
# Protocolo
#   empaquetar(dict) -> bytes      Serializa mensaje a [cabecera+JSON]
#   desempaquetar(socket) -> dict  Lee y deserializa mensaje del socket
#
# RecolectorMetricas
#   obtener() -> dict              Lee disco real (psutil) o simula
#
# Cliente
#   iniciar()                      Arranca hilos y bloquea hasta Ctrl+C
#   detener()                      Cierre seguro de hilos y socket
#   _conectar() -> bool            Abre TCP y envia REGISTRO
#   _reconectar()                  Reintenta con backoff lineal
#   _enviar(dict) -> bool          Envio thread-safe con Lock
#   _escuchar_servidor()           Hilo Receptor: lee mensajes entrantes
#   _enviar_metricas_periodicamente() Hilo Emisor: envia cada N segundos
#   _procesar_mensaje(dict)        Despacha por tipo de mensaje
#   _ejecutar_comando(dict)        Ejecuta comandos del servidor + ACK
#   detectar_servidor() -> str     Escanea LAN buscando el servidor
# ==============================================================
