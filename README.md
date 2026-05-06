#  Sistema RPC Distribuido con Flask y RabbitMQ

Este proyecto implementa un sistema RPC (Remote Procedure Call) utilizando Flask, RabbitMQ y AMQPStorm.  
La aplicación permite enviar mensajes desde una interfaz web hacia un servidor RPC mediante colas de mensajes y recibir respuestas mediante callback.

---

# Tecnologías utilizadas

- Python
- Flask
- RabbitMQ
- AMQPStorm
- Bootstrap 5

---

# 🧠 Arquitectura del sistema

```text
Cliente Web
     ↓
Flask Client
     ↓
RabbitMQ
     ↓
RPC Server
     ↓
Callback Response
```

---

# 📂 Estructura del proyecto

```text
RPC/
│
├── app.py
├── rpc_server.py
├── simular_clientes.bat
├── requirements.txt
│
├── templates/
│   └── index.html
│
└── README.md
```

---

# ⚙️ Instalación

## 1. Instalar Python

Instalar Python 3.10 o superior.

Durante la instalación marcar:

```text
Add Python to PATH
```

---

## 2. Instalar Erlang

RabbitMQ necesita Erlang para funcionar.

---

## 3. Instalar RabbitMQ

Instalar RabbitMQ Server y verificar que el servicio esté ejecutándose.

---

# Ejecutar el proyecto

## Crear entorno virtual

```bash
python -m venv venv
```

---

## Activar entorno virtual

### PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Luego:

```powershell
.\venv\Scripts\activate
```

---

## Instalar dependencias

```bash
pip install flask amqpstorm 

---

# Ejecutar servidor RPC

## Terminal 1

```bash
python rpc_server.py
```

Debe mostrarse:

```text
[Servidor RPC] Esperando solicitudes...
```

---

# Ejecutar Flask

## Terminal 2

```bash
python app.py
```

---

# Abrir aplicación web

Ingresar a:

```text
http://127.0.0.1:5000
```

---

# Simulación de clientes

El archivo:

```text
simular_clientes.bat
```

permite enviar múltiples solicitudes RPC automáticamente usando CURL.

---

# Despliegue en la nube

La aplicación puede desplegarse en plataformas cloud como:

- Render
- Railway

Y RabbitMQ puede utilizarse mediante:

- CloudAMQP

---

#  Conclusiones

- Se implementó un sistema RPC distribuido utilizando RabbitMQ.
- Se utilizó callback para recibir respuestas asíncronas.
- RabbitMQ permitió la comunicación entre cliente y servidor mediante colas de mensajes.
- La aplicación puede ejecutarse localmente o desplegarse en la nube.