import urllib.parse
import urllib.request

WRITE_API_KEY = "SRSQPNGCB3ZVJ7OD"

BASE_URL = "https://api.thingspeak.com/update"


def enviar_datos(temp=None, hum=None, movimiento=None, alerta=None, distancia=None):
    """
    Envía a ThingSpeak usando:
    field1 = temperatura
    field2 = humedad
    field3 = movimiento (0 o 1)
    field4 = alerta (0 o 1)
    field5 = distancia
    """

    params = {"api_key": WRITE_API_KEY}

    if temp is not None:
        params["field1"] = temp
    if hum is not None:
        params["field2"] = hum
    if movimiento is not None:
        params["field3"] = movimiento
    if alerta is not None:
        params["field4"] = alerta
    if distancia is not None:
        params["field5"] = distancia

    url = BASE_URL + "?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url) as resp:
            resultado = resp.read().decode()
            print("ThingSpeak respondió:", resultado)
    except Exception as e:
        print("Error enviando a ThingSpeak:", e)
