**🏠 Proyecto Final – IoT Smart Home**

**Curso:** Desarrollo de Software 8
**Integrantes:** Axel Cisnero, Jorge Izarra, Isabella Linares

**Tecnologías utilizadas:** MicroPython, Wokwi, MQTT (Mosquitto local), Flask (API REST), SQLite, VPS Ubuntu, ThingSpeak.

**Repositorio:** DS8-ProyFinal-IOTSmartHome

**📌 Descripción General**

Este proyecto implementa un sistema IoT de Smart Home compuesto por dos dispositivos:

+ Monitor de Temperatura y Humedad (Clima)
+ Sensor de Movimiento con Alarma (Seguridad)

Ambos se comunican mediante MQTT local (Mosquitto en la VPS) y un backend Flask que:

+ Permite el control remoto de actuadores (buzzer).
+ Expone un endpoint para enviar comandos desde un panel web.
+ Recibe mensajes MQTT y almacena lecturas en SQLite
+ Permite la visualización de datos históricos.
+ Se integra opcionalmente con ThingSpeak para dashboards.

Toda la solución corre continuamente en una VPS Ubuntu usando servicios systemd.

**📡 Arquitectura General**
```

          ┌────────────┐        MQTT Local        ┌───────────────┐
          │ Dispositivo │ ───────────────────────►│  Mosquitto     │
          │   Wokwi #1  │                         │  (en VPS)      │
          └────────────┘                         └───────────────┘
                                                         │
                                                         │
          ┌────────────┐          MQTT Listener          │
          │ Dispositivo │ ◄──────────────────────────────┘
          │   Wokwi #2  │
          └────────────┘

```

```

┌──────────────────────────────────────────────────┐
│ VPS Ubuntu (IP Pública)                          │
│  - command_server.py (API Flask + Panel Web)     │
│  - mqtt_listener.py (guarda datos en SQLite)     │
│  - SQLite (smart_home.db)                        │
│  - Mosquitto (Broker MQTT local)                 │
│  - Servicios systemd para ejecución continua     │
└──────────────────────────────────────────────────┘

```

```

┌───────────────┐
│ ThingSpeak     │ ← Dashboards y gráficas
└───────────────┘

```
**📁 Estructura del Repositorio**

**backend/**

    + command_server.py     # API REST + Panel Web
    + mqtt_listener.py      # Escucha MQTT y guarda datos en BD
    + requirements.txt      # Librerías necesarias

**database/**

    + smart_home.db         # Base de datos SQLite
    + consultas_db.py       # Consultas de históricos
    + init_db.py            # Crea estructura inicial de la BD

**devices/**

    + medidor_hum_temp.py   # Dispositivo: DHT22 + LCD + RGB + Buzzer
    + sensor_movimiento.py  # Dispositivo: Ultrasonido + LEDs + Alarma

**tools/**

    + thingspeak_client.py  # Integración con ThingSpeak
    + db_manager.py         # Manejo de BD

**README.md (este archivo)**


**🖥️ Backend (VPS)**

**1️⃣ Servidor Flask: command_server.py**

Provee endpoints:

+ GET /enviar_comando?cmd=BUZZER_ON
+ GET /comando → dispositivo consulta aquí cuál es el último comando enviado.
+ GET /ultimas_lecturas → devuelve lecturas almacenadas.
+ Panel web accesible desde:
http://149.130.166.159:5005

Comandos actualmente soportados:

+ **BUZZER_ON**
+ **BUZZER_OFF**

**2️⃣ Listener MQTT: mqtt_listener.py**

Escucha:

+ jorge_iot_final_2025/sala/datos
+ jorge_iot_final_2025/seguridad/datos

Cada lectura recibida se almacena automáticamente en:

**Tabla principal: sensor_readings**
```
id INTEGER PRIMARY KEY AUTOINCREMENT
sensor_type TEXT
value REAL
unit TEXT
timestamp TEXT

```


**🗄️ Base de Datos (SQLite)**
Archivo: smart_home.db

+ init_db.py → crea estructura inicial.
+ mqtt_listener.py → inserta datos automáticamente.
+ db_manager.py → maneja operaciones de BD.

Incluye:

+ Lecturas de clima (temperatura, humedad)
+ Distancia ultrasonido
+ Alertas de seguridad
+ Historial completo con timestamp

**📟 Dispositivos IoT (Wokwi)**

**1️⃣ Medidor de Humedad y Temperatura**

Archivo: medidor_hum_temp.py

Componentes:

+ DHT22
+ LCD I2C
+ Buzzer
+ Botón para cambiar vistas
+ Publicación MQTT a Mosquitto
+ Recepción de comandos desde el VPS vía HTTP

**2️⃣ Sensor de Movimiento y Alarma**

Archivo: sensor_movimiento.py

Componentes:

+ Sensor HC-SR04 (ultrasonido)
+ Buzzer para alertas
+ Estados:
 + SEGURO
 + ADVERTENCIA
 + INTRUSO
+ Publicación MQTT
+ Almacenamiento en BD vía mqtt_listener

**📊 Dashboards (ThingSpeak)**

Incluye canal configurado con:

+ Temperatura
+ Humedad
+ Movimiento
+ Alertas

Script opcional: tools/thingspeak_client.py

**🧪 Cómo Ejecutar el Proyecto**

**▶️ En la VPS (servicios automáticos)**

Los servicios se ejecutan 24/7:
```
sudo systemctl status iot_listener.service
sudo systemctl status iot_panel.service
```
Para reiniciar manualmente:
```
sudo systemctl restart iot_listener.service
sudo systemctl restart iot_panel.service
```

**▶️ En Wokwi**

Subir y ejecutar cada dispositivo.
Ambos se conectan a:

+ WiFi Wokwi
+ Mosquitto en la VPS
+ API Flask

**✔️ Requisitos del proyecto (cumplidos)**

+ Sensores múltiples
+ Actuadores (buzzer)
+ Conexión nube (ThingSpeak + VPS)
+ MQTT (broker propio en VPS)
+ Base de datos integrada
+ Backend REST
+ Panel web operativo
+ Dashboards opcionales
+ Arquitectura IoT real

**🎯 Estado del Proyecto**

100% funcional:
Sensores → MQTT → Listener → BD → Panel Web → Comandos → Dispositivos.
