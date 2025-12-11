import network
import ujson
import urandom
from machine import Pin, time_pulse_us, PWM
from time import sleep, sleep_us, time
from mqtt import MQTTClient

# --- 1. CONFIGURACIÓN HIVE MQ CLOUD ---
SSID = "Wokwi-GUEST"
PASSWORD = ""

# Tus credenciales (PON LAS MISMAS QUE EN EL OTRO DISPOSITIVO)
MQTT_BROKER = "149.130.166.159"
MQTT_PORT = 1883
MQTT_USER =""           
MQTT_PASSWORD =""   

# ID Aleatorio
random_id = urandom.randint(1000, 9999)
MQTT_CLIENT_ID = f"PicoW_Seguridad_{random_id}"
MQTT_TOPIC_PUB = "jorge_iot_final_2025/seguridad/datos"

# --- CONFIGURACIÓN DE PINES (Originales del diagrama de seguridad) ---
TRIG_PIN = 16
ECHO_PIN = 17
BUZZER_PIN = 13
LED_R_PIN = 5
LED_G_PIN = 4
LED_B_PIN = 3

# Inicializar componentes
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
buzzer = PWM(Pin(BUZZER_PIN))
led_r = Pin(LED_R_PIN, Pin.OUT)
led_g = Pin(LED_G_PIN, Pin.OUT)
led_b = Pin(LED_B_PIN, Pin.OUT)

# --- CONEXIÓN WIFI ---
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print(".", end="")
        sleep(0.1)
    print(" ¡Listo!")
    print("IP:", wlan.ifconfig()[0])

# --- CONEXIÓN MQTT SIN SSL (MOSQUITTO LOCAL EN EL VPS) ---
def conectar_mqtt():
    try:
        print(f"Conectando a Mosquitto como {MQTT_CLIENT_ID}...")
        client = MQTTClient(
            client_id=MQTT_CLIENT_ID,
            server=MQTT_BROKER,
            port=MQTT_PORT,
            keepalive=60
        )

        client.connect()
        print("¡MQTT Conectado sin SSL a Mosquitto!")
        return client
    except Exception as e:
        print(f"\nError conexión MQTT: {e}")
        return None

# --- FUNCIONES DE HARDWARE ---
def medir_distancia():
    trig.value(0); sleep_us(5)
    trig.value(1); sleep_us(10)
    trig.value(0)
    try:
        duracion = time_pulse_us(echo, 1, 30000)
        if duracion < 0:
            return -1
        return (duracion * 0.0343) / 2
    except OSError:
        return -1

def set_color(r, g, b):
    # Ajusta aquí si tus LEDs funcionan al revés (1/0)
    led_r.value(0 if r else 1)
    led_g.value(0 if g else 1)
    led_b.value(0 if b else 1)

def apagar_led():
    set_color(0, 0, 0)

def gestionar_alertas(distancia):
    estado = "NORMAL"
    if distancia == -1:
        apagar_led()
        return "ERROR"
    
    elif distancia < 20:  # ALERTA CRÍTICA
        set_color(1, 0, 0) 
        buzzer.freq(1500)
        buzzer.duty_u16(30000)
        estado = "INTRUSO_DETECTADO"
        
    elif distancia < 50:  # PRECAUCIÓN
        set_color(1, 1, 0)
        buzzer.freq(800)
        buzzer.duty_u16(10000)
        estado = "ADVERTENCIA"
        
    else:  # SEGURO
        set_color(0, 1, 0)
        buzzer.duty_u16(0)
        estado = "SEGURO"
    return estado

# --- BUCLE PRINCIPAL ---
conectar_wifi()
client = conectar_mqtt()
ultimo_envio = 0
INTERVALO_ENVIO = 2 

try:
    while True:
        # 1. Leer y Actuar (sensor + leds + buzzer local)
        dist = medir_distancia()
        estado_actual = gestionar_alertas(dist)
        
        # 2. Enviar a MQTT
        ahora = time()
        if (ahora - ultimo_envio > INTERVALO_ENVIO) or (estado_actual == "INTRUSO_DETECTADO"):
            if client:
                mensaje = ujson.dumps({
                    "dispositivo": "sensor_puerta",
                    "distancia_cm": round(dist, 1),
                    "estado": estado_actual,
                    "alerta": 1 if estado_actual == "INTRUSO_DETECTADO" else 0
                })
                print(f"Dist: {dist:.1f}cm | Estado: {estado_actual} -> Enviando SSL")
                try:
                    client.publish(MQTT_TOPIC_PUB, mensaje)
                    ultimo_envio = ahora
                except OSError:
                    print("Reconectando...")
                    client = conectar_mqtt()

        # 3. CONSULTAR COMANDOS DESDE LA NUBE (igual que el otro Pico)
        try:
            import urequests
            r = urequests.get("http://149.130.166.159:5005/comando")
            data = r.json()
            r.close()

            if data.get("cmd") == "BUZZER_ON":
                print("Comando HTTP (seguridad): BUZZER_ON")
                buzzer.freq(1500)
                buzzer.duty_u16(30000)
                sleep(1)
                buzzer.duty_u16(0)
        except Exception:
            # Si falla la petición HTTP o urequests, seguimos normal
            pass

        sleep(0.1)

except KeyboardInterrupt:
    print("\nApagando...")
    apagar_led()
    buzzer.duty_u16(0)