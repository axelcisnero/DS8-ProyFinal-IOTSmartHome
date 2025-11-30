**🏠 Proyecto Final – IoT Smart Home**

Curso: Desarrollo de Software 8
Integrantes: Axel Cisnero, Jorge Izarra, Isabella Linares

Tecnologías: MicroPython, Wokwi, MQTT SSL (HiveMQ Cloud), Flask, SQLite, VPS Ubuntu, ThingSpeak

Repositorio: DS8-ProyFinal-IOTSmartHome

**📌 Descripción General**

Este proyecto implementa un sistema IoT de Smart Home compuesto por dos dispositivos:

+ Monitor de Temperatura y Humedad (Clima)
+ Sensor de Movimiento con Alarma (Seguridad)

Ambos dispositivos se comunican mediante MQTT Seguro (SSL) utilizando HiveMQ Cloud, y el backend está desplegado en una VPS con IP pública, permitiendo:

+ Control remoto de actuadores (ej. alarmas, buzzer)
+ Recepción de comandos desde navegador web
+ Almacenamiento de lecturas en SQLite
+ Visualización y análisis de datos históricos
+ Integración opcional con ThingSpeak para dashboard en nube

**📡 Arquitectura General**
```
┌────────────┐       MQTT SSL       ┌──────────────┐
│ Dispositivo│  ───────────────────►│ HiveMQ Cloud │
│ (Wokwi #1) │                      └──────────────┘
└────────────┘                              │
                                             │
┌────────────┐       MQTT Listener           │
│ Dispositivo│  ─────────────────────────────┘
│ (Wokwi #2) │
└────────────┘

┌────────────────────────────────────────────────┐
│ VPS Ubuntu (IP Pública)                        │
│  - command_server.py (Flask REST API)          │
│  - mqtt_listener.py (almacenamiento en BD)     │
│  - SQLite (smarthome.db)                       │
└────────────────────────────────────────────────┘

┌───────────────┐
│ ThingSpeak     │ ← Dashboards, alertas
└───────────────┘
```
**📁 Estructura del Repositorio**

**backend/**

    + command_server.py     # API REST para enviar comandos a dispositivos
    + mqtt_listener.py      # Suscrito a HiveMQ, guarda datos en SQLite
    + requirements.txt      # Librerías necesarias

**database/**

    + smarthome.db          # Base de datos con lecturas
    + db_manager.py         # Crea tablas y estructura
    + consultas_db.py       # Consultas de históricos

**devices/**

    + medidor_hum_temp.py   # Dispositivo: DHT22 + LCD + RGB + Buzzer
    + sensor_movimiento.py  # Dispositivo: Ultrasonido + LEDs + Alarma

**tools/**

    + thingspeak_client.py  # Script de prueba para ThingSpeak (opcional)
    + db_manager.py         # Script utilizado para la creación de la base de datos (opcional)

**README.md (este archivo)**


**🖥️ Backend (VPS)**

1️⃣ Servidor Flask: command_server.py

Permite enviar comandos desde el navegador: **http://IP_PUBLICA:5005/enviar_comando?cmd=BUZZER_ON**
Y entrega el comando al dispositivo: **http://IP_PUBLICA:5005/comando**
El dispositivo consulta este endpoint cada ciclo.

2️⃣ Listener MQTT: mqtt_listener.py

Escucha los tópicos:
jorge_iot_final_2025/sala/datos
jorge_iot_final_2025/seguridad/datos


Y guarda en la tabla: sensor_readings(id, sensor_type, value, unit, timestamp)


**🗄️ Base de Datos (SQLite)**
Archivo: smarthome.db

Generado por:
db_manager.py → crea estructura

mqtt_listener.py → inserta datos automáticos
```
Tabla Principal
sensor_readings
-------------------------------------------
id INTEGER PRIMARY KEY AUTOINCREMENT
sensor_type TEXT
value REAL
unit TEXT
timestamp TEXT
```
Consultas

Con consultas_db.py puedes obtener:

+ Últimas lecturas

+ Histórico por sensor

+ Eventos y alertas

**📟 Dispositivos IoT (Wokwi)**

1️⃣ Medidor de Humedad y Temperatura

Archivo: medidor_hum_temp.py

Incluye:

+ DHT22

+ LCD I2C

+ RGB status LED

+ Buzzer

+ Botón para cambiar vistas

+ Envío a MQTT SSL

+ Recepción de comandos desde el VPS vía HTTP

2️⃣ Sensor de Movimiento y Alarma

Archivo: sensor_movimiento.py

Incluye:

+ Sensor ultrasónico

+ LED RGB

+ Buzzer

+ Estados: SEGURO / ADVERTENCIA / INTRUSO

+ Envío a MQTT SSL

+ Lecturas en tiempo real

**📊 Dashboards (ThingSpeak)**

Proyecto configurado con:

Canal con 4–5 fields (temp, hum, movimiento, alerta)

Visualización en tiempo real

Reacciones vía ThingHTTP o MATLAB Analysis (opcional)

Script de prueba disponible en:

tools/thingspeak_client.py

**🧪 Cómo Ejecutar el Proyecto**

▶️ En el VPS
cd backend
python3 command_server.py
python3 mqtt_listener.py

▶️ En Wokwi

Subir cada dispositivo y ejecutar.

Ambos dispositivos se conectan automáticamente a:

+ WiFi Wokwi guest

+ HiveMQ SSL

+ API del VPS

✔️ Requisitos del proyecto (todos cumplidos)

 + Sensores múltiples

 + Actuadores controlables

 + Conexión a la nube (HiveMQ + VPS)

 + Dashboard en ThingSpeak

 + Base de datos con almacenamiento histórico

 + Backend accesible por IP pública

 + Envío de comandos desde web

 + Recepción de comandos en dispositivos

 + Arquitectura IoT real y profesional

🎯 Estado del Proyecto

100% funcional: sensores, backend, comandos, base de datos, MQTT y dashboard operativos.
