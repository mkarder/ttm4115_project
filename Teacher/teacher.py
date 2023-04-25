import paho.mqtt.client as mqtt
import datetime
import logging
from threading import Thread
import json
import uuid
from appJar import gui
from teacherUserInterface import TeacherUserInterface

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

# TO DO: fill in topics for publishing and subscribing
PUBLISH_RAT_TOPIC = 'ttm4115/team_5/publish'
SAVE_RAT_TOPIC = 'ttm4115/team_5/save'
MQTT_TOPIC_SUBSCRIBE = 'ttm4115/team_5/#'


class Teacher:
    def __init__(self):
        self.rats = {}

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug(
            'Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()

        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # load the user interface
        TeacherUserInterface(self)

    def on_connect(self, client, userdata, flags, rc):
        """Request available RATs from database"""
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        self._logger.debug('ON_MESSAGE | client: {} | userdata: {} | msg: {}'.format(
            client, userdata, msg))
        print('{}: {} | {}'.format(client, userdata, msg))

    def create_rat(self, name, size, subject='TTM4115'):
        rat = Rat(name, size, subject)
        self.rats[rat.id] = rat
        return rat

    def create_question(self, rat_id, question, correct, false):
        rat = self.rats[rat_id]
        rat.create_question(question, correct, false)


    def save_rat(self, rat_id):
        """send MQTT message to server (database) containing the RAT-object"""
        payload = json.dumps(self.rats[rat_id].reprJSON(), cls=ComplexEncoder)
        self._logger.info("Saving RAT {}".format(rat_id))
        self.mqtt_client.publish(SAVE_RAT_TOPIC, payload)

    def publish_rat(self, rat_id):
        """send MQTT message to server (manager) indicating which RAT (rat_id) should be made available."""
        payload = json.dumps({
            "command": "start_iRAT",
            "RAT_ID": rat_id
        })
        self._logger.info("Publishing {} at {}".format(
            rat_id, datetime.datetime.now()))
        self.mqtt_client.publish(PUBLISH_RAT_TOPIC, payload)

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()

# Transitions 
t0 = {
    'source': 'initial',
    'target': 'idle'
    }

t1 = {
    'source': 'idle',
    'target': 'creating_rat',
    'trigger': 'create_rat'
    }

t2 = {
    'source': 'creating_rat',
    'target': 'idle',
    'trigger': 'cancel',
    }

t3 = {
    'source': 'creating_rat',
    'target': 'idle',
    'trigger': 'save_rat',
    'effect': 'save_rat(*)'
}

t4 = {
    'source': 'idle',
    'target': 'idle',
    'trigger': 'publish_rat',
    'effect': 'publish_rat'
}

# Add transition for incoming RATs and polling for RAT

# States 
# Add open/close window for UI in the 'entry' field for each state? 
idle = {
    'name': 'idle',
    }

creating_rat = {
    'name': 'creating_rat'
}


# Sub-classes for RAT and question objects
class Rat:
    id: uuid
    name: str
    size: int
    subject: str
    questions: dict

    def __init__(self, name, size, subject):
        self.name = name
        self.id = uuid.uuid4()
        self.size = size
        self.subject = subject
        self.question_counter = 0
        self.questions = {}
        self.rat_complete = False

    def reprJSON(self):
        return dict(id=str(self.id), name=self.name, size=self.size, subject=self.subject, questions=self.questions)
    
    # Add Exception handling
    def create_question(self, question, correct, false):
        self.question_counter += 1
        if self.question_counter == self.size:
            q = Question(question, correct, false)
            self.questions[self.question_counter] = q
            print(self.questions)
            self.rat_complete = True
        else:
            q = Question(question, correct, false)
            self.questions[self.question_counter] = q
    
    # def get_questions(self):

class Question:
    question: str
    correct: str
    a: str
    b: str
    c: str

    def __init__(self, question, correct, false):
        self.question = question
        self.correct = correct
        self.a = false[0]
        self.b = false[1]
        self.c = false[2]

    def reprJSON(self):
        return dict(question=self.question, correct=self.correct, a=self.a, b=self.b, c=self.c)

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)


# logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter(
    '%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

teacher = Teacher()
