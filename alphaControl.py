import json
import paho.mqtt.client as mqtt
import time
import datetime

allowedKeys = {b'530000018E526401'}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("devices/lora/#")
    setState("waiting", 0)


def setState(state, key):
    if state == "waiting":
        setLockState("locked")
        setColor(1, 0, 0)
        logActivity("waiting", key)
    if state == "allowing":
        setLockState("unlocked")
        setColor(0, 0, 1)
        logActivity("unlocked", key)
    if state == "disallowing":
        setLockState("locked")
        setColor(0, 1, 0)
        logActivity("locked", key)


def setLockState(state):
    # No lock available
    print("Lock state is: " + state)


def setColor(blue,red,green):
    client.publish("devices/lora/807B859020000231/gpio", "set 7 " + str(red))
    client.publish("devices/lora/807B859020000231/gpio", "set 24 " + str(green))
    client.publish("devices/lora/807B859020000231/gpio", "set 6 " + str(blue))


def logActivity(action, key):
    print(str(datetime.datetime.now()) + ": lock change state to " + action + "; key used: " + str(key))


# The callback for when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    if msg.topic == "devices/lora/807B859020000231/ibutton":
        # data = input()
        # data_d = json.dumps(msg.payload)
        # data_l = json.loads(msg.payload)
        # temp = msg.payload['data']['id']
        # print (temp)
        # checkKey(temp)

        json_data = msg.payload.decode('utf-8')

        print("Message received: " + json_data)
        data = json.dumps(json_data)
        print (data)
        parsed_json = json.loads(data)
        print (parsed_json)
        # print(parsed_json["data"]["id"])
        print(parsed_json['data']['id'])
        checkKey(parsed_json["data"]["id"])


def checkKey(key):
    if key in allowedKeys:
        setState("allowing", key)
        time.sleep(30)
        setState("waiting", key)
    else:
        setState("disallowing", key)
        time.sleep(30)
        setState("waiting", key)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("10.11.162.100", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()