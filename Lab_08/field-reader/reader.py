import json
import os
import psycopg2
from time import sleep
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=os.environ.get("KAFKA_HOST"))
filename = 'data/field_centroids.geojson'


def connect_to_db():
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST"),
        port=os.environ.get("POSTGRES_PORT"),
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD")
    )
    return conn


def insert_field_to_db(field):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO features (id, name, geometry) VALUES (%s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))",
            (field['id'], field['name'], json.dumps(field['geom'])))
        conn.commit()
        print(f"Field with ID {field['id']} inserted into the database.")
    except Exception as e:
        print(f"Error inserting field into the database: {str(e)}")
    finally:
        cur.close()
        conn.close()


def read_fields_from_file():
    try:
        with open(filename, 'r') as f:
            data = json.load(f)

        for feature in data['features']:
            field = {
                'id': feature['properties']['id'],
                'name': feature['properties']['Name'],
                'geom': feature['geometry']}
            insert_field_to_db(field)
        os.remove(filename)
        producer.send('field-reading', "Data received".encode("UTF-8"))
        print(f"Field data sent to Kafka.\n")
    except Exception as e:
        print(f"Error reading file: {str(e)}")


if __name__ == "__main__":
    print("Service started!\n")
    while True:
        if os.path.exists(filename):
            read_fields_from_file()
            print("Data saved into db.\n")
        sleep(5)
