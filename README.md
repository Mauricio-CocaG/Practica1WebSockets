text

### **Componentes:**
- **PC Servidor (Central)**: Ejecuta backend Flask, base de datos MySQL y sirve el frontend
- **PC Cliente (Regional)**: Ejecuta cliente Python que envía métricas de disco
- **Comunicación**: Sockets TCP bidireccionales (puerto 9999) + API REST (puerto 3000)

---

## 🚀 **GUÍA DE INICIALIZACIÓN PASO A PASO**

### **🖥️ EN LA PC SERVIDOR (CENTRAL)**

#### **1. Iniciar Backend (Flask + Sockets)**
```bash
# Abrir terminal
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# o source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt



# Iniciar servidor
python run.py
Verás:

text
============================================================
🚀 INICIANDO CLUSTERMONITOR BACKEND
============================================================
📡 SERVIDOR DE SOCKETS LISTO
   IP Local: 192.168.100.6
   Los clientes deben conectarse a: 192.168.100.6:9999
📡 API REST: http://localhost:3000
============================================================
2. Iniciar Frontend (React + Vite)
bash
# Abrir terminal
cd frontend
npm install
npm run dev
Verás:

text
VITE v5.x.x ready in xxx ms
➜ Local: http://localhost:5173
➜ Network: http://192.168.100.6:5173
💻 EN LA PC CLIENTE (REGIONAL)
1. Configurar cliente
bash
# Crear carpeta para el cliente
mkdir C:\ClusterCliente
cd C:\ClusterCliente

# Copiar archivo cliente.py desde el repositorio
# (o crear nuevo archivo con el código)

# Instalar dependencias
pip install psutil
2. Ejecutar cliente
bash
# Opción 1: Con IP del servidor
python cliente.py 192.168.100.6

# Opción 2: Sin argumentos (preguntará la IP)
python cliente.py
# Cuando pregunte, escribir: 192.168.100.6
Verás:

text
============================================================
🚀 CLIENTE DE MONITOREO - Cliente-LAPTOP
============================================================
📡 Servidor: 192.168.100.6:9999
⏱ Intervalo: 30 segundos

🔍 Buscando interfaz WiFi...
   ✅ Adaptador WiFi encontrado
   📡 IP WiFi detectada: 192.168.100.201
✅ Conectado al servidor 192.168.100.6:9999

📤 Enviando métricas...
📤 [14:35:22] Métricas enviadas: 500GB, 45% usado
📩 Servidor: Conectado al ClusterMonitor. Nodo ID: 1
