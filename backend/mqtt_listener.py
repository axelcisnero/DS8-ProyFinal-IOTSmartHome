import json
import os
import sys
import logging
import paho.mqtt.client as mqtt

# --- RUTAS PARA TOOLS Y DATABASE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # .../iot_backend/backend
ROOT_DIR = os.path.dirname(BASE_DIR)                       # .../iot_backend
TOOLS_DIR = os.path.join(ROOT_DIR, "tools")
DB_DIR = os.path.join(ROOT_DIR, "database")

sys.path.extend([TOOLS_DIR, DB_DIR])

from thingspeak_client import enviar_datos
from db_manager import guardar_lectura

# --- LOGS COMPARTIDOS CON EL PANEL WEB ---
LOG_FILE = os.path.join(BASE_DIR, "smart_home.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- CONFIG MQTT: MOSQUITTO LOCAL, SIN SSL ---
MQTT_BROKER = "localhost"          # o "149.130.166.159", es lo mismo dentro del VPS
MQTT_PORT = 1883
MQTT_USER = None
MQTT_PASSWORD = None

MQTT_TOPIC_SUB = "jorge_iot_final_2025/#"


def on_connect(client, userdata, flags, rc):
    print("on_connect → código:", rc)
    logging.info(f"Conexión al broker rc={rc}")

    if rc == 0:
        print("Conectado correctamente a Mosquitto.")
        logging.info("Conectado correctamente a Mosquitto")

        client.subscribe(MQTT_TOPIC_SUB)
        print("Suscrito a:", MQTT_TOPIC_SUB)
        logging.info(f"Suscrito a: {MQTT_TOPIC_SUB}")
    else:
        print("Error de conexión:", rc)
        logging.error(f"Error al conectar: {rc}")


def procesar_sala(data):
    temp = data.get("temp")
    hum = data.get("hum")

    if temp is not None:
        guardar_lectura("temperatura", temp, "C")
        logging.info(f"Temperatura guardada: {temp} C")
        print(f"[BD] Temperatura guardada: {temp} C")

    if hum is not None:
        guardar_lectura("humedad", hum, "%")
        logging.info(f"Humedad guardada: {hum} %")
        print(f"[BD] Humedad guardada: {hum} %")

    # Enviar a ThingSpeak (si lo estás usando)
    enviar_datos(temp=temp, hum=hum)


def procesar_seguridad(data, topic):
    dist = data.get("distancia_cm")
    alerta = data.get("alerta")
    estado = data.get("estado", "")

    movimiento = 0 if estado == "SEGURO" else 1

    if dist is not None:
        guardar_lectura("distancia", dist, "cm")
        logging.info(f"Distancia guardada: {dist} cm")
        print(f"[BD] Distancia guardada: {dist} cm")

    guardar_lectura("movimiento", movimiento, "0/1")
    logging.info(f"Movimiento guardado: {movimiento}")
    print(f"[BD] Movimiento guardado: {movimiento}")

    if alerta is not None:
        guardar_lectura("alerta", alerta, "0/1")
        logging.info(f"Alerta guardada: {alerta}")
        print(f"[BD] Alerta guardada: {alerta}")

    enviar_datos(distancia=dist, movimiento=movimiento, alerta=alerta)


def on_message(client, userdata, msg):
    logging.info(f"Mensaje recibido en tópico: {msg.topic}")
    try:
        payload = msg.payload.decode()
        logging.info(f"Payload: {payload}")
        print(f"[MQTT] {msg.topic} -> {payload}")

        data = json.loads(payload)

        if "sala/datos" in msg.topic:
            procesar_sala(data)
        elif "seguridad/datos" in msg.topic:
            procesar_seguridad(data, msg.topic)

    except Exception as e:
        logging.error(f"Error procesando mensaje: {e}")
        print("Error procesando mensaje:", e)


def main():
    logging.info("Iniciando MQTT Listener (Mosquitto local)")
    print("Iniciando MQTT Listener (Mosquitto local)...")

    client = mqtt.Client()

    # Sin usuario / contraseña / SSL, porque Mosquitto está abierto en tu VPS
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    logging.info("Conectando al broker MQTT…")
    print(f"Conectando a {MQTT_BROKER}:{MQTT_PORT} ...")

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    logging.info("Esperando mensajes…")
    print("Esperando mensajes MQTT…")
    client.loop_forever()


if __name__ == "__main__":
    main()