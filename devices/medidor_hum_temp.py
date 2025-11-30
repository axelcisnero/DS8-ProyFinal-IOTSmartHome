import network
import ujson
import dht 
import urandom
from machine import Pin, PWM, I2C 
from lcd_api import LcdApi 
from i2c_lcd import I2cLcd 
from time import sleep, time
from mqtt import MQTTClient

# --- 1. CONFIGURACIÓN DE HIVE MQ CLOUD (¡CAMBIA ESTO!) ---
SSID = "Wokwi-GUEST"
PASSWORD = ""

# Copia esto EXACTO de tu captura de pantalla:
MQTT_BROKER = "2378ba4b3fc64b5695542985699ce9c9.s1.eu.hivemq.cloud" 
MQTT_PORT = 8883 # El puerto SSL seguro

# TUS CREDENCIALES (Las que creaste en Access Management):
MQTT_USER = "Jorge"
MQTT_PASSWORD = "Jorge2612"

# ID Aleatorio (Igual que antes)
random_id = urandom.randint(1000, 9999)
MQTT_CLIENT_ID = f"PicoW_Sala_{random_id}"
MQTT_TOPIC_PUB = "jorge_iot_final_2025/sala/datos"

# --- CONFIGURACIÓN DE PINES (Igual que antes) ---
DHT_PIN = 15       
BUZZER_PIN = 10    
LED_R_PIN = 18     
LED_G_PIN = 17     
LED_B_PIN = 16     
BOTON_PIN = 22     
LCD_SDA = 0        
LCD_SCL = 1        

# --- INICIALIZACIÓN ---
print(f"Iniciando... ID: {MQTT_CLIENT_ID}")
sensor_dht = dht.DHT22(Pin(DHT_PIN)) 
buzzer = PWM(Pin(BUZZER_PIN)) 
led_r = Pin(LED_R_PIN, Pin.OUT) 
led_g = Pin(LED_G_PIN, Pin.OUT) 
led_b = Pin(LED_B_PIN, Pin.OUT) 
boton = Pin(BOTON_PIN, Pin.IN) 
i2c = I2C(0, sda=Pin(LCD_SDA), scl=Pin(LCD_SCL), freq=400000) 
lcd = I2cLcd(i2c, 0x27, 2, 16) 

# --- VARIABLES ---
modo_visualizacion = 1 
boton_anterior = 0 
ultimo_envio = 0
INTERVALO_ENVIO = 5 

# --- CONEXIÓN WIFI ---
def conectar_wifi():
    lcd.clear()
    lcd.putstr("WiFi...")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        sleep(0.1)
    print("WiFi Listo:", wlan.ifconfig()[0])
    lcd.move_to(0,1)
    lcd.putstr("OK!")
    sleep(1)

# --- CONEXIÓN MQTT SEGURA (¡NUEVO!) ---
def conectar_mqtt():
    try:
        print("Conectando a HiveMQ Cloud SSL...")
        client = MQTTClient(
            client_id=MQTT_CLIENT_ID, 
            server=MQTT_BROKER, 
            port=MQTT_PORT, 
            user=MQTT_USER, 
            password=MQTT_PASSWORD, 
            keepalive=60,
            ssl=True, 
            ssl_params={'server_hostname': MQTT_BROKER}
        )
        client.connect()
        print("¡MQTT Seguro Conectado!")
        return client
    except Exception as e:
        print(f"Error MQTT: {e}")
        return None

# --- ACTUADORES ---
def beep_boton(): 
    buzzer.freq(2000); buzzer.duty_u16(10000); sleep(0.05); buzzer.duty_u16(0) 

def set_color_rgb(r, g, b): 
    led_r.value(r); led_g.value(g); led_b.value(b) 

def leer_sensores(): 
    try: 
        sensor_dht.measure() 
        return sensor_dht.temperature(), sensor_dht.humidity(), True 
    except OSError: 
        return 0, 0, False

# --- MAIN LOOP ---
conectar_wifi()
client = conectar_mqtt()

lcd.clear(); lcd.putstr("Sistema Seguro"); sleep(1)

try: 
    while True: 
        # 1. BOTÓN
        boton_actual = boton.value() 
        if boton_actual == 1 and boton_anterior == 0: 
            modo_visualizacion += 1 
            if modo_visualizacion > 3: 
                modo_visualizacion = 1 
            beep_boton()
            lcd.clear(); lcd.putstr(f"Vista: Modo {modo_visualizacion}"); sleep(0.5)
        boton_anterior = boton_actual 
         
        # 2. SENSORES
        temp, hum, exito = leer_sensores() 
        if exito:
            if temp > 30: 
                set_color_rgb(1, 0, 0) 
            elif hum > 70: 
                set_color_rgb(0, 0, 1) 
            else: 
                set_color_rgb(0, 1, 0) 

            if modo_visualizacion == 1: 
                lcd.move_to(0,0); lcd.putstr(f"T:{temp:.1f}C H:{hum:.0f}% ")
            elif modo_visualizacion == 2: 
                lcd.move_to(0,0); lcd.putstr(f"Temp: {temp:.1f}C    ")
            elif modo_visualizacion == 3: 
                lcd.move_to(0,0); lcd.putstr(f"Hum: {hum:.1f}%      ")

            # 3. ENVIAR (igual que antes)
            ahora = time()
            if (ahora - ultimo_envio > INTERVALO_ENVIO):
                if client:
                    mensaje = ujson.dumps({"dispositivo": "clima_sala", "temp": temp, "hum": hum})
                    print(f"Enviando SSL: {mensaje}")
                    try:
                        client.publish(MQTT_TOPIC_PUB, mensaje)
                        ultimo_envio = ahora
                    except:
                        print("Reconectando...")
                        client = conectar_mqtt()

        # 4. CONSULTAR COMANDOS DESDE LA NUBE (NUEVO)
        try:
            import urequests
            r = urequests.get("http://149.130.166.159:5005/comando")
            data = r.json()
            r.close()

            if data.get("cmd") == "BUZZER_ON":
                print("Comando HTTP: BUZZER_ON")
                buzzer.freq(1500)
                buzzer.duty_u16(30000)
                sleep(1)
                buzzer.duty_u16(0)
        except Exception as e:
            # Si algo falla (no hay urequests, no hay red, etc.), no rompe el programa
            pass

        sleep(0.1) 

except KeyboardInterrupt: 
    lcd.clear()
    set_color_rgb(0,0,0)
    buzzer.duty_u16(0)