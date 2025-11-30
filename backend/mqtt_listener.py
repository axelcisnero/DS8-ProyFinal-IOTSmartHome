import json
import ssl
import paho.mqtt.client as mqtt
from thingspeak_client import enviar_datos
from db_manager import guardar_lectura


# Datos del broker HiveMQ Cloud (los mismos que usan tus Picos)
MQTT_BROKER = "2378ba4b3fc64b5695542985699ce9c9.s1.eu.hivemq.cloud"
MQTT_PORT = 8883  # SSL
MQTT_USER = "Jorge"
MQTT_PASSWORD = "Jorge2612"

# Nos suscribimos a TODOS los tópicos de tu proyecto
MQTT_TOPIC_SUB = "jorge_iot_final_2025/#"


def on_connect(client, userdata, flags, rc):
    print("on_connect -> código de resultado:", rc)
    if rc == 0:
        print("Conectado correctamente al broker.")
        client.subscribe(MQTT_TOPIC_SUB)
        print("Suscrito a:", MQTT_TOPIC_SUB)
    else:
        print("Error al conectar. Código:", rc)


def on_message(client, userdata, msg):
    print("\n--- Mensaje recibido ---")
    print("Tópico:", msg.topic)
    try:
        payload = msg.payload.decode()
        print("Payload bruto:", payload)
        data = json.loads(payload)
        print("JSON decodificado:", data)

        # === Mensajes del dispositivo de clima ===
        if "sala/datos" in msg.topic:
            temp = data.get("temp")
            hum = data.get("hum")

            # Guardar en BD
            if temp is not None:
                guardar_lectura("temperatura", temp, "C")
            if hum is not None:
                guardar_lectura("humedad", hum, "%")

            # Enviar a ThingSpeak
            print("Enviando a ThingSpeak (clima)...")
            enviar_datos(temp=temp, hum=hum)

        # === Mensajes del dispositivo de seguridad ===
        elif "seguridad/datos" in msg.topic:
            dist = data.get("distancia_cm")
            alerta = data.get("alerta")
            estado = data.get("estado", "")

            # Consideramos movimiento = 1 si NO está SEGURO
            movimiento = 0 if estado == "SEGURO" else 1

            # Guardar en BD
            if dist is not None:
                guardar_lectura("distancia", dist, "cm")
            if movimiento is not None:
                guardar_lectura("movimiento", movimiento, "0/1")
            if alerta is not None:
                guardar_lectura("alerta", alerta, "0/1")

            # Enviar a ThingSpeak
            print("Enviando a ThingSpeak (seguridad)...")
            enviar_datos(movimiento=movimiento, alerta=alerta, distancia=dist)

    except Exception as e:
        print("Error al decodificar mensaje:", e)

def main():
    print("Creando cliente MQTT...")
    client = mqtt.Client()  # Usamos la API simple
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    # SSL/TLS usando certificados del sistema
    client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)
    client.tls_insecure_set(False)

    client.on_connect = on_connect
    client.on_message = on_message

    print("Conectando a HiveMQ...")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    print("Esperando mensajes. Ctrl+C para salir.\n")
    client.loop_forever()


if __name__ == "__main__":
    main()