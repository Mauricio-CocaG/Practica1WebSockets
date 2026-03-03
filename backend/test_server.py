# test_server.py
import socket

def test_server():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 9999))
        sock.listen(1)
        print("✅ Puerto 9999 disponible y escuchando")
        sock.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_server()