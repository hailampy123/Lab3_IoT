print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json
import random
import serial.tools.list_ports

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "b2kmvKec5H0nyckRjAtD"
mess = ""
def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")
    
def getPort():
    ports = serial.tools.list_ports.comports()
    for i in range(len(ports)):
        print(str(ports[i]))
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        print(strPort)
        if "USB Serial Device" in strPort:
            splitPort = strPort.split(" ")
            commPort = splitPort[0]
    return commPort

bbc_port = getPort()
if bbc_port != "None":
    ser = serial.Serial(port=bbc_port, baudrate=115200)

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    
    led_data = {}
    pump_data = {}
    cmd = -1
    #0 : led off, 1 : led on, 2 : pump off, 3 : pump on
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setLED":
            led_data['valueLED'] = jsonobj['params']
            if(jsonobj['params']):
                cmd = 1
            else:
                cmd = 0
            client.publish('v1/devices/me/attributes', json.dumps(led_data), 1)
        if jsonobj['method'] == "setPUMP":
            pump_data['valuePUMP'] = jsonobj['params']
            if(jsonobj['params']):
                cmd = 3
            else:
                cmd = 2
            client.publish('v1/devices/me/attributes', json.dumps(pump_data), 1)
    except:
        pass

    if bbc_port != "None":
        ser.write((str(cmd) + "#").encode())


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 30
humi = 50
light_intesity = 50

longitude = 106.7
latitude = 10.6
counter = 0


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print("Receive from sensor: ", splitData)
    #TODO: Add your source code to publish data to the server
    if len(splitData) != 3:
        print('line 128', data)
        return

    if splitData[1] == "TEMP":
        client.publish("v1/devices/me/telemetry",  json.dumps({'temperature': splitData[2]}), 1)
    elif splitData[1] == "LIGHT":
        client.publish("v1/devices/me/telemetry",  json.dumps({'light': splitData[2]}), 1)

def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]
   
while True:
    if bbc_port != "None":
        readSerial()
    
    collect_data = {'temperature': temp, 'light': light_intesity}    
    light_intesity = random.randrange(0,200)
    temp = random.randrange(-30, 50)
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    
    time.sleep(1)
    

