import psutil
import requests
import time

SERVER_URL = 'http://localhost:5000/data'

while True:
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    data = {'cpu_usage': cpu_usage, 'ram_usage': ram_usage}
    try:
        requests.post(SERVER_URL, json=data)
    except Exception as e:
        print(f"Error sending data: {e}")
    time.sleep(10)  # Send data every 10 seconds
