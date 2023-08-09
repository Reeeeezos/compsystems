from time import sleep
import os

content_dir = 'timestamps'

while True:
    for file in os.listdir(content_dir):
        if file.endswith('.txt'):
            with open(os.path.join(content_dir, file), 'r') as f:
                print(f'timestamp {f.read()} from {file}\n')
    sleep(10)
