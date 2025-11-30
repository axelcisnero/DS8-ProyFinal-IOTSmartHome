import sqlite3
from datetime import datetime

DB_NAME = "smart_home.db"


def crear_tablas():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Tabla de lecturas de sensores
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_type TEXT,
            value REAL,
            unit TEXT,
            timestamp TEXT
        )
    """)

    # Tabla de eventos (ej: movimiento detectado, alerta, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            description TEXT,
            timestamp TEXT
        )
    """)

    # Tabla de comandos (cuando implementemos comandos desde la nube)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            target TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Tablas creadas/verificadas en", DB_NAME)


def guardar_lectura(sensor_type, value, unit):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    ts = datetime.now().isoformat(timespec="seconds")

    cur.execute("""
        INSERT INTO sensor_readings (sensor_type, value, unit, timestamp)
        VALUES (?, ?, ?, ?)
    """, (sensor_type, value, unit, ts))

    conn.commit()
    conn.close()
    print(f"Lectura guardada: {sensor_type} = {value} {unit} @ {ts}")


if __name__ == "__main__":
    # Prueba rápida
    crear_tablas()
    guardar_lectura("temperatura", 25.5, "C")
