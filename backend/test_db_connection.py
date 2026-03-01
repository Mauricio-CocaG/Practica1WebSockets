import pymysql
import socket
from dotenv import load_dotenv
import os

load_dotenv()

print("🔍 DIAGNÓSTICO DE CONEXIÓN A MYSQL")
print("="*50)

host = os.getenv('DB_HOST')
port = int(os.getenv('DB_PORT', 27961))
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')

print(f"📌 Datos de conexión:")
print(f"   Host: {host}")
print(f"   Puerto: {port}")
print(f"   Usuario: {user}")
print(f"   Base de datos: {database}")
print("="*50)

# 1. Probar resolución DNS
print("\n1️⃣ Probando resolución DNS...")
try:
    ip = socket.gethostbyname(host)
    print(f"   ✅ Host resuelto a: {ip}")
except socket.gaierror as e:
    print(f"   ❌ Error DNS: {e}")
    print("   ➡ El hostname no existe o no es accesible")

# 2. Probar conectividad de red
print("\n2️⃣ Probando conectividad...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    if result == 0:
        print(f"   ✅ Puerto {port} abierto y accesible")
    else:
        print(f"   ❌ No se puede conectar al puerto {port} (código: {result})")
        print(f"   ➡ Posible firewall o IP no permitida")
    sock.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Probar conexión MySQL
print("\n3️⃣ Probando conexión MySQL...")
try:
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port,
        connect_timeout=10
    )
    print("   ✅ Conexión exitosa a MySQL!")
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   📊 MySQL version: {version[0]}")
    conn.close()
    
except pymysql.err.OperationalError as e:
    print(f"   ❌ Error de conexión: {e}")
    if "Access denied" in str(e):
        print("   ➡ Usuario o contraseña incorrectos")
    elif "Unknown MySQL server host" in str(e):
        print("   ➡ El host no existe")
    elif "timed out" in str(e):
        print("   ➡ Timeout - firewall o IP no permitida")
    else:
        print(f"   ➡ {e}")