import json
import paho.mqtt.client as mqtt
import time
import datetime

allowedKeys = {b'', b'', b''}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    setState("waiting")


def setState(state, key):
    if state == "waiting":
        setLockState("locked")
        setColor(0, 0, 0)
        logActivity("waiting", key)
    if state == "allowing":
        setLockState("unlocked")
        setColor(0, 1, 0)
        logActivity("unlocked", key)
    if state == "disallowing":
        setLockState("locked")
        setColor(1, 0, 0)
        logActivity("locked", key)


def setLockState(state):
    # No lock available
    print("Lock state is: " + state)


def setColor(red, green, blue):
    client.publish("paho/gpio", "set 6 " + red)
    client.publish("paho/gpio", "set 7 " + green)
    client.publish("paho/gpio", "set 24 " + blue)


def logActivity(action, key):
    print(str(datetime.now()) + ": lock change state to " + action + "; key used: " + key)


# The callback for when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    if msg.topic == "key":
        checkKey(msg.payload)


def checkKey(key):
    if key in allowedKeys:
        setState("allowing", key)
        time.sleep(3)
        setState("waiting")
    else:
        setState("disallowing", key)
        time.sleep(3)
        setState("waiting")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("iot.eclipse.org", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
