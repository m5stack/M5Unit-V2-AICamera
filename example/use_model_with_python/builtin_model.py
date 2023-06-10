from json.decoder import JSONDecodeError
import subprocess
import json
import base64
import serial
import time
from datetime import datetime
from PIL import Image
import os
import io

uart_grove = serial.Serial('/dev/ttyS0', 115200, timeout=0.1)
reconizer = subprocess.Popen(['/home/m5stack/payload/bin/object_recognition', '/home/m5stack/payload/uploads/models/nanodet_80class'],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

reconizer.stdin.write("_{\"stream\":1}\r\n".encode('utf-8'))
reconizer.stdin.flush()

img = b''

while True:
    today = datetime.now()
    path = str(today.strftime("%Y_%m_%d") + "/")
    newpath = "/media/sdcard/" + path

    line = reconizer.stdout.readline().decode('utf-8').strip()
    if not line:
        break  # Process finished or empty line

    try:
        doc = json.loads(line)
        if 'img' in doc:
            byte_data = base64.b64decode(doc["img"])
            img = bytes(byte_data)
        elif 'num' in doc:
            for obj in doc['obj']:
                uart_grove.write(str(obj['type'] + '\n').encode('utf-8'))
                if obj['type'] == "aeroplane":
                    print('aeroplane ' + today.strftime("%Y_%m_%d_%H_%M_%S"))
                    if os.path.exists(newpath):
                        image_path = newpath + today.strftime("%Y_%m_%d_%H_%M_%S") + ".jpg"
                        img = Image.open(io.BytesIO(byte_data))
                        img.save(image_path, 'jpeg')
                    else:
                        os.mkdir(newpath)
                        image_path = newpath + today.strftime("%Y_%m_%d_%H_%M_%S") + ".jpg"
                        img = Image.open(io.BytesIO(byte_data))
                        img.save(image_path, 'jpeg')
                    time.sleep(1)
                else:
                    print('Not detect '+ today.strftime("%Y_%m_%d_%H_%M_%S"))
    except JSONDecodeError as e:
        print("Error: Invalid JSON string")
        print("JSONDecodeError:", str(e))

