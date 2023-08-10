import os
import json
import rasterio
import ast
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'field-processing',
    bootstrap_servers=os.environ.get("KAFKA_HOST"),
    group_id='field-processing-group',
    auto_offset_reset='earliest'
)


def get_soil_moisture(lat, lon):
    file_path = 'soil_moisture.tif'

    with rasterio.open(file_path) as dataset:
        col, row = dataset.index(lat, lon)
        moisture = dataset.read(1, window=((row, row + 1), (col, col + 1)))
    return moisture[0][0]


def process_field_data(field_data):
    moisture = get_soil_moisture(field_data['field_data']['lat'], field_data['field_data']['lon'])

    feature = {
        'type': 'Feature',
        'properties': {
            'moisture': int(moisture)
        },
        'geometry': {
            'type': 'Point',
            'coordinates': [field_data['point_of_interest']['lat'], field_data['point_of_interest']['lon']]
        }
    }
    result = {
        'type': 'FeatureCollection',
        'name': 'field_data',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'
            }
        },
        'features': [feature]
    }

    return result


def process_message(message):
    data = ast.literal_eval(message)
    result = process_field_data(data)

    filename = f"output/result_{data['point_of_interest']['lat']}_{data['point_of_interest']['lon']}.geojson"
    with open(filename, 'w') as file:
        json.dump(result, file, indent=4)

    print(f"Message processed into {filename}!\n")


def main():
    print("Service started!...\n")
    for message in consumer:
        payload = message.value.decode('utf-8')
        print(f"New message received: \n{payload}\n")
        process_message(payload)
        consumer.commit()


if __name__ == '__main__':
    main()
