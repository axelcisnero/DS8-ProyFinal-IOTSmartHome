import sqlite3

conn = sqlite3.connect("smart_home.db")
cur = conn.cursor()

print("Últimos 10 registros:\n")
for row in cur.execute("SELECT sensor_type, value, unit, timestamp FROM sensor_readings ORDER BY timestamp DESC LIMIT 10"):
    print(row)

conn.close()