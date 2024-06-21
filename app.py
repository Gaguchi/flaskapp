from flask import Flask, jsonify, render_template, send_from_directory
from flask_apscheduler import APScheduler
import psutil
import sqlite3
from datetime import datetime
import plotly.graph_objs as go
import plotly.offline as pyo
import atexit

app = Flask(__name__)
scheduler = APScheduler()


def init_db():
    conn = sqlite3.connect('monitoring.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats
                     (timestamp TEXT, cpu REAL, ram REAL)''')
    conn.commit()
    conn.close()

init_db()


def log_stats():
    conn = sqlite3.connect('monitoring.db')
    cursor = conn.cursor()
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''INSERT INTO stats (timestamp, cpu, ram) VALUES (?, ?, ?)''', (timestamp, cpu, ram))
    conn.commit()
    conn.close()

@app.route('/log')
def log():
    log_stats()
    return jsonify({'status': 'logged'})

@app.route('/data')
def data():
    conn = sqlite3.connect('monitoring.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stats')
    data = cursor.fetchall()
    conn.close()

    timestamps = [row[0] for row in data]
    cpu_values = [row[1] for row in data]
    ram_values = [row[2] for row in data]

    return jsonify({'timestamps': timestamps, 'cpu_values': cpu_values, 'ram_values': ram_values})

@app.route('/')
def index():
    conn = sqlite3.connect('monitoring.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM stats')
    data = cursor.fetchall()
    conn.close()

    timestamps = [row[0] for row in data]
    cpu_values = [row[1] for row in data]
    ram_values = [row[2] for row in data]

    cpu_trace = go.Scatter(x=timestamps, y=cpu_values, mode='lines', name='CPU Usage')
    ram_trace = go.Scatter(x=timestamps, y=ram_values, mode='lines', name='RAM Usage')

    layout = go.Layout(title='CPU and RAM Usage Over Time', xaxis={'title': 'Time'}, yaxis={'title': 'Usage (%)'})
    fig = go.Figure(data=[cpu_trace, ram_trace], layout=layout)
    graph_html = pyo.plot(fig, output_type='div')

    return render_template('index.html', graph_html=graph_html)


scheduler.add_job(id='Scheduled task', func=log_stats, trigger='interval', seconds=10)
scheduler.start()


atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True)