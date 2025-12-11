import sqlite3
import os

# Ruta del archivo smart_home.db en esta carpeta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "smart_home.db")

print("Usando base de datos:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Creamos la tabla lecturas si no existe
cur.execute("""
CREATE TABLE IF NOT EXISTS lecturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor TEXT NOT NULL,
    valor REAL NOT NULL,
    unidad TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()
print("Tabla 'lecturas' lista.")