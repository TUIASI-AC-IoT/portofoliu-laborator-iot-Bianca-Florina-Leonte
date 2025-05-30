from threading import Thread, Lock
from serial import Serial
from flask import Flask
from flask import request
from os.path import exists
from time import sleep
import random


PORT = 'COM3'
BAUDRATE = 115200
SENSOR_ID = "137"
CONFIG_FILE_PATH = "sensor_{0}.cfg".format(SENSOR_ID)
KNOWN_SCALE_LIST = ['C', 'K', 'F']

#serial_port = Serial(PORT, BAUDRATE, timeout=0)
mutex = Lock()
last_temp = 0

app = Flask(__name__)

#se comenteaza pt a se putea testa virtual cu o simulare de senzor
#def read_sensor_data():
#   global last_temp
#    while True:
#        data = serial_port.readline().decode().strip()
#        if data:
#            try:
#                temp = float(data)
#                with mutex:
#                    last_temp = temp
#            except ValueError:
#                continue

#pentru versiune simulata
def read_sensor_data():
    global last_temp
    while True:
        with mutex:
            last_temp = round(random.uniform(20.0, 30.0), 2)  # Temperaturi simulate între 20 și 30
        sleep(2)


sensor_thread = Thread(target=read_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()


def convertCelsiusTo(temp, new_scale):
    if new_scale == 'K':
        return temp + 273.15
    if new_scale == 'F':
        return (temp * 9/5) + 32
    return temp


@app.route('/sensor/<sensor_id>', methods=['GET'])
def getTemp(sensor_id):
    if sensor_id != SENSOR_ID:
        return {"message": "Sensor not found!"}, 404
    scale = 'C'
    if exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as f:
            scale = f.readline().strip()
    with mutex:
        ret_value = convertCelsiusTo(last_temp, scale)

    link = f"/sensor/{sensor_id}"
    return {
        "ID": sensor_id,
        "temp": ret_value,
        "scale": scale,
        "_links": {
            "parent": "/sensor/",
            "self": link
        },
        "_rel": [
            {"link": link, "type": "PUT"},
            {"link": link, "type": "POST"},
            {"link": link, "type": "GET"},
        ]
    }, 200


@app.route('/sensor/<sensor_id>', methods=['POST'])
def setScale(sensor_id):
    if sensor_id != SENSOR_ID:
        return {"message": "Sensor not found!"}, 404
    if exists(CONFIG_FILE_PATH):
        return {
            "message": f"Config file already exists for sensor with ID={sensor_id}"
        }, 409
    req = request.get_json()
    if not req or req.get('scale') not in KNOWN_SCALE_LIST:
        return {
            "message": "Invalid or missing scale! Accepted scales: C, K, F"
        }, 400
    with open(CONFIG_FILE_PATH, 'w') as f:
        f.write(req['scale'])
    return {"message": "Config file created."}, 200


@app.route('/sensor/<sensor_id>/<config_file>', methods=['PUT'])
def updateScale(sensor_id, config_file):
    if sensor_id != SENSOR_ID:
        return {"message": f"Sensor with ID={sensor_id} not found!"}, 404
    config_path = f"{config_file}.cfg"
    if not exists(config_path):
        return {
            "message": f"Config file '{config_file}.cfg' does not exist for sensor ID={sensor_id}."
        }, 406
    req = request.get_json()
    if not req or req.get('scale') not in KNOWN_SCALE_LIST:
        return {
            "message": "Invalid or missing scale! Accepted scales: C, K, F"
        }, 400
    with open(config_path, 'w') as f:
        f.write(req['scale'])
    return {"message": f"Config file '{config_file}.cfg' updated successfully."}, 200



if __name__ == "__main__":
    app.run()


