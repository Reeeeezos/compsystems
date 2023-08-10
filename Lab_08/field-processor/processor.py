import os
import psycopg2
from kafka import KafkaConsumer, KafkaProducer

KAFKA_HOST = os.environ.get("KAFKA_HOST")

consumer = KafkaConsumer(
    'field-reading',
    bootstrap_servers=KAFKA_HOST,
    group_id='field-reading-group',
    auto_offset_reset='earliest'
)
producer = KafkaProducer(bootstrap_servers=KAFKA_HOST)


def connect_to_db():
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT"),
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD")
    )
    return conn


def process_message(message):
    if message == "Data received":
        print("Message received")
        with open('data/POI.txt', 'r') as f:
            for i in f:
                points = i.strip().split(",")
                nearest_point = get_nearest_point(points)
                print("Nearest point found: ", i.strip().split(","))
                send_to_field_processing(nearest_point[3], nearest_point[2], nearest_point[1], points)


def get_nearest_point(points):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
    Select id, name, ST_X(geometry), ST_Y(geometry), ST_Distance(geometry, 'SRID=4326;Point(%s %s)'::geometry)   
    from features
    order by ST_Distance(geometry, 'SRID=4326;Point(%s %s)'::geometry)
    limit 1;""", (float(points[0]), float(points[1]), float(points[0]), float(points[1])))

    nearest_point = cursor.fetchone()
    cursor.close()
    conn.close()
    return nearest_point


def send_to_field_processing(nearest_point_x, nearest_point_y, name, poi):
    data = {
        'point_of_interest': {
            'lat': float(poi[0]),
            'lon': float(poi[1])
        },
        'field_data': {
            "name": name,
            'lat': nearest_point_y,
            'lon': nearest_point_x
        }
    }
    producer.send('field-processing', str(data).encode("UTF-8"))
    print(f"Message sent: {str(data)}\n")


def main():
    print("Service started!...\n")
    for message in consumer:
        payload = message.value.decode('utf-8')
        print(f"New message received: \n{payload}\n")
        process_message(payload)
        consumer.commit()


if __name__ == '__main__':
    main()
