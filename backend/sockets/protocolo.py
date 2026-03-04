import json
import struct

class ProtocoloCluster:
    @staticmethod
    def encode_message(data):
        try:
            json_str = json.dumps(data)
            json_bytes = json_str.encode('utf-8')
            length = len(json_bytes)
            header = struct.pack('!I', length)
            return header + json_bytes
        except Exception as e:
            print(f"Error codificando: {e}")
            return None
    
    @staticmethod
    def decode_message(socket_connection):
        try:
            header = socket_connection.recv(4)
            if not header or len(header) < 4:
                return None

            length = struct.unpack('!I', header)[0]
            data = b''
            while len(data) < length:
                chunk = socket_connection.recv(min(length - len(data), 4096))
                if not chunk:
                    return None
                data += chunk

            return json.loads(data.decode('utf-8'))
        except Exception as e:
            print(f"Error decodificando: {e}")
            return None

    @staticmethod
    def create_command_message(comando, parametros=None):
        return {
            'tipo': 'COMANDO',
            'comando': comando,
            'parametros': parametros or {}
        }