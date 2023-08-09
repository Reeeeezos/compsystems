from time import sleep
from datetime import datetime

while True:
    current = datetime.now().strftime('%Y-%m-%d %H:%M:%S').replace(':', '_')
    with open(f'./timestamps/{current}.txt', 'w+') as f:
        f.write(current)
    print(f"Created {current}.txt")
    sleep(10)
