from kafka import KafkaConsumer

consumer = KafkaConsumer('common', bootstrap_servers='kafka:9092')

for msg in consumer:
    print(f'Got message {msg.value.decode("utf-8")}')
