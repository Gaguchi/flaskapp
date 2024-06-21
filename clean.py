import sqlite3

def delete_data():
    conn = sqlite3.connect('monitoring.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM stats')
    conn.commit()
    conn.close()

delete_data()