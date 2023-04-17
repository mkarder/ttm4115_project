import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
import uuid
from appJar import gui

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

# TO DO: choose topics for publishing and subscribing 

class Teacher: 
    def __init__(self):
        self.rats = {}
        pass

    def create_rat(self, name, size):
        rat = Rat(name, size)
        self.rats[rat.id] = rat
        pass
    
    def create_question(self, rat_id, question, correct, false):
        rat = self.rats[rat_id]
        rat.create_question(question, correct, false)

    def save_rat(self, rat_id):
        """send MQTT message to server (database) containing the RAT-object"""
        pass

    def publish_rat(self, rat_id):
        """send MQTT message to server (manager) indicating which RAT (rat_id) should be made available."""
        pass
    
    def create_gui(self):
        self.app = gui()

        def extract_timer_name(label):
            label = label.lower()
            return None

        def extract_duration_seconds(label):
            label = label.lower()
            return None

        def publish_command(command):
            payload = json.dumps(command)
            self._logger.info(command)
            self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)

        self.app.startLabelFrame('Starting timers:')
        def on_button_pressed_start(title):
            name = extract_timer_name(title)
            duration = extract_duration_seconds(title)
            command = {"command": "new_timer", "name": name, "duration": duration}
            publish_command(command)
        self.app.addButton('Start Spaghetti Timer', on_button_pressed_start)
        self.app.addButton('Start Green Tea Timer', on_button_pressed_start)
        self.app.addButton('Start Soft Eggs Timer', on_button_pressed_start)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Stopping timers:')
        def on_button_pressed_stop(title):
            name = extract_timer_name(title)
            command = {"command": "cancel_timer", "name": name}
            publish_command(command)
        self.app.addButton('Cancel Spaghetti Timer', on_button_pressed_stop)
        self.app.addButton('Cancel Green Tea Timer', on_button_pressed_stop)
        self.app.addButton('Cancel Soft Eggs Timer', on_button_pressed_stop)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Asking for status:')
        def on_button_pressed_status(title):
            name = extract_timer_name(title)
            if name is None:
                command = {"command": "status_all_timers"}
            else:
                command = {"command": "status_single_timer", "name": name}
            publish_command(command)
        self.app.addButton('Get All Timers Status', on_button_pressed_status)
        self.app.addButton('Get Spaghetti Timer Status', on_button_pressed_status)
        self.app.addButton('Get Green Tea Timer Status', on_button_pressed_status)
        self.app.addButton('Get Soft Eggs Timer Status', on_button_pressed_status)
        self.app.stopLabelFrame()

        self.app.go()

class Rat:

    def __init__(self, name, size, subject):
        self.name = name
        self.id = uuid.uuid1()
        self.size = size
        self.subject = subject
        self.question_counter = 1
        self.questions = {}
        

    def create_question(self, question, correct, false):
        if self.question_counter == self.size:
            print("DO SOMETHING!")
        else: 
            q = Question( self.question_counter, question, correct, false)
            self.question_counter += 1
            self.questions.append(q) 

class Question:

    def __init__(self, id, question, correct, false):
        self.id = id
        pass
