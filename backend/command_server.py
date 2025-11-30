from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)

# Variable global para guardar el último comando
comando_actual = "NINGUNO"

# --- MQTT (si lo estás usando para HiveMQ, lo dejamos igual que lo tenías) ---
MQTT_BROKER = "2378ba4b3fc64b5695542985699ce9c9.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "Jorge"
MQTT_PASSWORD = "Jorge2612"

def publicar_mqtt(cmd):
    try:
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        client.tls_set()  # usa SSL por defecto
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.publish("jorge_iot_final_2025/comandos", cmd)
        client.disconnect()
        print("Publicando comando MQTT:", cmd)
    except Exception as e:
        print("Error publicando MQTT:", e)

# --- ENDPOINT PARA ENVIAR COMANDO DESDE EL NAVEGADOR ---
@app.route("/enviar_comando")
def enviar_comando():
    global comando_actual
    cmd = request.args.get("cmd", "NINGUNO")
    comando_actual = cmd

    # (Opcional) publicarlo también por MQTT
    publicar_mqtt(cmd)

    return f"Comando enviado: {cmd}"

# --- ENDPOINT QUE CONSULTA EL PICO (WOKWI) ---
@app.route("/comando")
def comando():
    global comando_actual
    cmd = comando_actual
    # Después de leerlo, lo reseteamos para que no se repita
    comando_actual = "NINGUNO"
    # devolvemos JSON
    return jsonify({"cmd": cmd})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)