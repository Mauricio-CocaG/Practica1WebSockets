# ClusterMonitor

Sistema de monitoreo distribuido de almacenamiento en cluster, desarrollado con Flask + WebSockets + React.

---

## Arquitectura

```
┌─────────────────┐        TCP :9999        ┌──────────────────┐
│   cliente.py    │ ──────────────────────► │  Socket Server   │
│  (Nodo Cliente) │                         │  (Flask Backend) │
└─────────────────┘                         └────────┬─────────┘
                                                     │ REST :3000
                                            ┌────────▼─────────┐
                                            │  React Frontend  │
                                            │  (Vite :5173)    │
                                            └──────────────────┘
```

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Backend API | Flask 2.3 + Flask-SQLAlchemy |
| Base de datos | MySQL (Aiven Cloud) |
| Socket Server | Python TCP (puerto 9999) |
| Frontend | React + Material-UI v7 + Recharts |
| Cliente nodo | Python 3.11 + psutil |

---

## Rama `client-py` — Cambios Principales

### 1. `backend/cliente.py` — Reescritura profesional
Cliente TCP de monitoreo de nodos con arquitectura limpia:

- **`Protocolo`** — empaqueta/desempaqueta mensajes con cabecera 4 bytes big-endian + JSON UTF-8
- **`RecolectorMetricas`** — lee métricas reales de disco con `psutil` (fallback simulado)
- **`Cliente`** — gestiona conexión, reconexión con backoff lineal y dos hilos:
  - *Hilo Emisor*: envía métricas cada N segundos
  - *Hilo Receptor*: escucha comandos del servidor
- Auto-detección del servidor en la LAN
- Reconexión automática: 10s, 20s, 30s ... hasta 120s
- Logging doble (archivo DEBUG + consola INFO) en hora de **Bolivia (UTC-4)**
- Sin emojis (compatible con Windows cp1252)

### 2. `backend/app/utils/timezone.py` — Zona horaria Bolivia
Módulo centralizado para manejo de fechas en todo el sistema:

```python
from app.utils.timezone import now, to_iso, BoliviaFormatter

fecha = now()           # datetime Bolivia naive (para DB)
iso   = to_iso(fecha)   # '2026-03-04T11:00:00-04:00'
```

- `BOLIVIA_TZ` = `pytz.timezone('America/La_Paz')` (UTC-4)
- `now()` — hora actual de Bolivia para DB y lógica de negocio
- `to_iso(dt)` — ISO 8601 con offset explícito `-04:00`
- `BoliviaFormatter` — logging con hora de Bolivia
- Configurado en `.env` como `TIMEZONE=America/La_Paz`

### 3. Correcciones de backend
- Rutas de imports corregidas (`app.sockets` → `sockets`)
- Método `create_command_message()` añadido a `ProtocoloCluster`
- `import json` añadido en `cliente_handler.py`
- Todos los emojis eliminados (compatibilidad Windows cp1252)
- `datetime.utcnow()` reemplazado por `now()` en todos los archivos

### 4. `frontend/src/services/api.js`
- IP hardcodeada reemplazada por proxy Vite (`/api` → `http://localhost:3000`)

---

## Cómo ejecutar

### Requisitos
```bash
cd backend
python -m pip install -r requirements.txt
```

### Terminal 1 — Backend
```bash
cd backend
python run.py
```

### Terminal 2 — Frontend
```bash
cd frontend
npm run dev
```
Abrir: `http://localhost:5173`

### Terminal 3 — Cliente nodo
```bash
cd backend
python cliente.py 127.0.0.1
```

---

## Endpoints REST

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/nodos` | Lista todos los nodos |
| GET | `/api/metricas` | Métricas con filtros (nodo_id, dias) |
| GET | `/api/dashboard/resumen` | Resumen global del cluster |
| GET | `/api/ip` | IP y puerto del servidor |
