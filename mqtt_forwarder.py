#!/usr/bin/env python3
#
#  mqtt_forwarder.py
#
#  Copyright 2016 Sébastien Lucas <sebastien@slucas.fr>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


import os, re, time, json, argparse, signal
import paho.mqtt.client as mqtt # pip install paho-mqtt
import urllib.parse

verbose = False

def signal_handler(signal, frame):
  print('You pressed Ctrl+C!')
  client.disconnect()

def environ_or_required(key):
  if os.environ.get(key):
    return {'default': os.environ.get(key)}
  else:
    return {'required': True}

def debug(msg):
  if verbose:
    print (msg + "\n")

def on_connect(client, userdata, flags, rc):
    debug("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(args.topic)

def on_message(client, userdata, msg):
    mqttPath = args.destination
    debug("Received message from {0} with payload {1} to be published to {2}".format(msg.topic, str(msg.payload), mqttPath))
    if not args.dryRun:
        client.publish(mqttPath, msg.payload)
    else:
        debug("Dry run")



parser = argparse.ArgumentParser(description='Send MQTT payload received from a topic to firebase.', 
  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-m', '--mqtt-host', dest='host', action="store", default="127.0.0.1",
                   help='Specify the MQTT host to connect to.')
parser.add_argument('-n', '--dry-run', dest='dryRun', action="store_true", default=False,
                   help='No data will be sent to the MQTT broker.')
parser.add_argument('-d', '--destination', dest='destination', action="store", default="sensor/raw",
                   help='The destination MQTT topic base.')
parser.add_argument('-t', '--topic', dest='topic', action="store", default="sensor/esp/#",
                   help='The listening MQTT topic.')
parser.add_argument('-T', '--topic-error', dest='topicError', action="store", default="error/transformer", metavar="TOPIC",
                   help='The MQTT topic on which to publish the message (if it wasn\'t a success).')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                   help='Enable debug messages.')


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
args = parser.parse_args()
verbose = args.verbose

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(args.host, 1883, 60)

client.loop_forever()

