import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
import uuid
from appJar import gui

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

# TO DO: fill in topics for publishing and subscribing
PUBLISH_RAT_TOPIC = ''
SAVE_RAT_TOPIC = ''
MQTT_TOPIC_SUBSCRIBE = ''

class Student:
    name : str
    team : int
    

    login = {}
    cancel = {}
    start_irat = {}
    t1 = {}
    irat_done = {}
    leader = {}
    not_leader = {}
    trat_done = {}
    leader_done = {}

    def __init__(self, name, team):
        self.name = name
        self.team = team

