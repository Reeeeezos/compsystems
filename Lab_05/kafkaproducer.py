from time import sleep
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='kafka:9092')

while True:
    message = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    producer.send('common', value=message.encode('utf-8'))
    sleep(5)
