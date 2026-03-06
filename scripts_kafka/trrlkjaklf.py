import time
import json
import requests
from kafka import KafkaProducer

# CONFIGURACIÓN
API_KEY = "721d5451b85103aad14d2289eda0e714"
LAT = "-41.8101" # Patagonia
LON = "-68.9063"
URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&appid={API_KEY}"

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'weather_stream'

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(f"Iniciando ingesta desde OpenWeather hacia Kafka topic: {TOPIC}")

while True:
    try:
        response = requests.get(URL)
        if response.status_size == 200:
            data = response.json()
            producer.send(TOPIC, value=data)
            producer.flush()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Dato enviado a Kafka exitosamente.")
        else:
            print(f"Error API: {response.status_code}")
    except Exception as e:
        print(f"Error de conexión: {e}")
    
    time.sleep(60) # Consulta cada 60 segundos
