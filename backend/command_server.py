from flask import Flask, request, jsonify, Response
import os
import logging
import sqlite3

app = Flask(__name__)

# ==== RUTAS DE ARCHIVOS ====
# command_server.py está en /home/ubuntu/iot_backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# smart_home.log en la raíz del proyecto
LOG_FILE = os.path.join(BASE_DIR, "smart_home.log")

# Base de datos en /home/ubuntu/iot_backend/database/smart_home.db
DB_PATH = os.path.join(BASE_DIR, "database", "smart_home.db")

# ==== LOGGING ====
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ==== VARIABLE GLOBAL PARA COMANDOS HTTP (PICOS) ====
ULTIMO_COMANDO = {"cmd": ""}


def get_last_lines(file_path, n=150):
    """Devuelve las últimas n líneas de un archivo de texto."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return "".join(lines[-n:])
    except FileNotFoundError:
        return "No hay logs todavía.\n"
    except Exception as e:
        return f"Error leyendo logs: {e}\n"


def obtener_ultimas_lecturas(limit=10):
    """
    Lee las últimas 'limit' lecturas de la tabla 'lecturas'
    y devuelve una lista de diccionarios.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT timestamp, sensor, valor, unidad
            FROM lecturas
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        filas = cur.fetchall()
        datos = []
        for ts, sensor, valor, unidad in filas:
            datos.append(
                {
                    "timestamp": ts,
                    "sensor": sensor,
                    "valor": valor,
                    "unidad": unidad,
                }
            )
        return datos
    finally:
        conn.close()


@app.route("/")
def panel():
    """Panel HTML con botones, logs y botón para ver las últimas lecturas."""
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Panel Smart Home IoT</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}
            h1 {{
                margin-top: 0;
            }}
            .box {{
                margin-bottom: 20px;
                padding: 10px 15px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 0 5px rgba(0,0,0,0.1);
            }}
            button {{
                margin: 5px;
                padding: 8px 14px;
                cursor: pointer;
            }}
            #logs {{
                white-space: pre-wrap;
                background: #111;
                color: #eee;
                padding: 10px;
                border-radius: 8px;
                height: 260px;
                overflow-y: scroll;
                font-size: 13px;
            }}
            #bd {{
                white-space: pre-wrap;
                background: #111;
                color: #eee;
                padding: 10px;
                border-radius: 8px;
                height: 200px;
                overflow-y: auto;
                font-size: 13px;
            }}
            #status {{
                margin-top: 10px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <h1>Panel Smart Home IoT</h1>

        <div class="box">
            <h3>Enviar comandos</h3>
            <button onclick="sendCommand('BUZZER_ON')">BUZZER ON</button>
            <button onclick="sendCommand('BUZZER_OFF')">BUZZER OFF</button>
            <div id="status"></div>
        </div>

        <div class="box">
            <h3>Logs del servidor</h3>
            <div id="logs">Cargando logs...</div>
        </div>

        <div class="box">
            <h3>Últimos registros de la base de datos</h3>
            <button onclick="cargarLecturas()">Ver últimos registros (BD)</button>
            <div id="bd">Pulsa el botón para consultar la base de datos.</div>
        </div>

        <script>
            function updateLogs() {{
                fetch('/logs')
                    .then(response => response.text())
                    .then(text => {{
                        const logsDiv = document.getElementById('logs');
                        logsDiv.textContent = text;
                        logsDiv.scrollTop = logsDiv.scrollHeight;
                    }})
                    .catch(err => console.error(err));
            }}

            function sendCommand(cmd) {{
                fetch('/enviar_comando?cmd=' + encodeURIComponent(cmd))
                    .then(response => response.json())
                    .then(data => {{
                        const statusDiv = document.getElementById('status');
                        statusDiv.textContent = 'Comando enviado: ' + data.cmd + ' -> ' + data.status;
                    }})
                    .catch(err => console.error(err));
            }}

            function cargarLecturas() {{
                fetch('/ultimas_lecturas')
                    .then(resp => resp.json())
                    .then(datos => {{
                        const bdDiv = document.getElementById('bd');

                        // Si el backend envía {{ "error": "..." }} lo mostramos tal cual
                        if (datos && datos.error) {{
                            bdDiv.textContent = 'Error BD: ' + datos.error;
                            return;
                        }}

                        // Si no es un arreglo, algo raro pasó
                        if (!Array.isArray(datos)) {{
                            bdDiv.textContent = 'Error BD: respuesta inesperada';
                            return;
                        }}

                        if (datos.length === 0) {{
                            bdDiv.textContent = 'No hay registros en la base de datos.';
                            return;
                        }}

                        let texto = '';
                        datos.forEach(reg => {{
                            texto += `[${{reg.timestamp}}] ${{reg.sensor}} = ${{reg.valor}} ${{reg.unidad}}\\n`;
                        }});

                        bdDiv.textContent = texto;
                    }})
                    .catch(err => {{
                        document.getElementById('bd').textContent =
                            'Error consultando la BD: ' + err;
                    }});
            }}


            // Actualiza logs cada 2 segundos
            setInterval(updateLogs, 2000);
            updateLogs();
        </script>
    </body>
    </html>
    """
    return Response(html, mimetype="text/html")


@app.route("/logs")
def logs():
    """Devuelve las últimas líneas del archivo de logs."""
    contenido = get_last_lines(LOG_FILE, n=150)
    return Response(contenido, mimetype="text/plain")


@app.route("/enviar_comando")
def enviar_comando():
    """
    Recibe un comando (cmd) desde el panel y lo guarda como último comando
    para que los Picos lo puedan leer en /comando.
    """
    global ULTIMO_COMANDO

    cmd = request.args.get("cmd", "").strip()

    if not cmd:
        return jsonify({"error": "Falta el parámetro cmd"}), 400

    logging.info(f"Comando recibido desde panel: {cmd}")
    print(f"Comando recibido desde panel: {cmd}")

    # Guardamos el último comando para los Picos
    ULTIMO_COMANDO = {"cmd": cmd}

    return jsonify({"cmd": cmd, "status": "OK"})


@app.route("/comando")
def comando():
    """
    Endpoint que consultan los dispositivos Pico (con urequests.get).
    Devuelve en JSON el último comando enviado desde el panel.
    """
    return jsonify(ULTIMO_COMANDO)


@app.route("/ultimas_lecturas")
def ultimas_lecturas():
    """Devuelve las últimas 10 lecturas de la BD en JSON."""
    try:
        # Usa el DB_PATH global que ya definiste arriba
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("""
            SELECT sensor_type, value, unit, timestamp
            FROM sensor_readings
            ORDER BY id DESC
            LIMIT 10
        """)

        filas = cur.fetchall()
        conn.close()

        datos = [
            {
                "sensor": f[0],      # sensor_type
                "valor": f[1],       # value
                "unidad": f[2],      # unit
                "timestamp": f[3],
            }
            for f in filas
        ]

        return jsonify(datos)

    except Exception as e:
        return jsonify({"error": f"Error consultando BD: {e}"}), 500

if __name__ == "__main__":
    # Escuchamos en 0.0.0.0 para que sea accesible desde fuera del VPS
    app.run(host="0.0.0.0", port=5005, debug=False)