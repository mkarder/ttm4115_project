import paho.mqtt.client as mqtt
import datetime
import logging
from threading import Thread
import json
import uuid
from appJar import gui
from studentUI import StudentUI
from json import dumps

from stmpy import Machine, Driver

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

# TO DO: fill in topics for publishing and subscribing
PUBLISH_RAT_TOPIC = ''
SAVE_ANSWERS_TOPIC = 'ttm4115/team5/Answers'
MQTT_TOPIC_SUBSCRIBE = 'ttm4115/team_5/#'


class Student_client:
    def __init__(self):
        self.rats = {}
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')
        self.mqtt_client = mqtt.Client()

        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.mqtt_client.subscribe(MQTT_TOPIC_SUBSCRIBE)

    def start(self, broker, port):

        # create a new MQTT client
        self._logger.debug(
            'Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

        self.client.subscribe(MQTT_TOPIC_SUBSCRIBE)

        try:
            # line below should not have the () after the function!
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.mqtt_client.disconnect()
            self.stop()

    def on_connect(self, client, userdata, flags, rc):
        """Request available RATs from database"""
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        self._logger.debug('ON_MESSAGE | client: {} | userdata: {} | msg: {}'.format(
            client, userdata, msg))
        print('{}: {} | {}'.format(client, userdata, msg))
        print(msg.payload)
        msg = json.loads(str(msg.payload.decode("utf-8", "ignore")))
        print(msg.keys())
        print("command" in msg.keys())
        if "command" in msg.keys():
            print(msg["command"])
            if msg["command"] == "start_iRAT":
                print("starte_iRAT")
                self.rat = msg["RAT"]
                self.stm_driver.send("start_irat", "student")

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()


class Student:

    def __init__(self):
        self.answers = []

    def start_irat(self):
        self.rat = self.student_client.rat
        self.studentUI.rat = self.rat
        self.studentUI.start_irat()
        print("start irate state")

    def sign_in(self):
        self.student = self.studentUI.student
        print("sign in state")

    def irat_done(self):
        message = {"command": "student_iRAT_done",
                   "student_id": self.student.student_id,
                   "RAT_id": self.rat.id,
                   "team_id": self.student.team,
                   "answers": self.studetnUI.answers}
        self.mqtt_client.publish("topic", message)
        self.studentUI.answers = []
        print("irat done state")

    def trat_done(self):
        message = {"command": "tRAT_answers",
                   "RAT_id": self.rat.id,
                   "team_id": self.student.team,
                   "answers": self.studetnUI.answers}
        self.mqtt_client.publish("topic", message)
        self.studentUI.answers = []

    # do something
    def transistion_1():
        if ...:
            return 's1'
        else:
            return 's2'


t0 = {'source': 'initial',
      'target': 'idle'}

t1 = {'trigger': 'sign_in',
      'source': 'idle',
      'target': 'pre_irat',
      'effect': 'sign_in'}

t2 = {'trigger': 'start_irat',
      'source': 'pre_irat',
      'target': 'conducting_irat',
      'effect': 'start_irat'}

t3 = {'trigger': 'irat_done',
      'source': 'conducting_irat',
      'target': 'pre_trat',
      'effect': 'irat_done'}

t4 = {'trigger': 'leader',
      'source': 'pre_trat',
      'target': 'conducting_trat',
      'effect': 'start_trat'}

t5 = {'trigger': 'trat_done',
      'source': 'conducting_trat',
      'target': 'waiting_for_leader',
      'effect': 'trat_done'}

t6 = {'trigger': 'leader_done',
      'source': 'waiting_for_leader',
      'target': 'idle waiting_for_leader',
      'function': 'transistion_1'}

t7 = {'trigger': 't2',
      'source': 'conducting_trat',
      'target': 'waiting_for_leader',
      'effect': ''}

t8 = {'trigger': 'not_leader',
      'source': 'pre_trat',
      'target': 'waiting_for_leader',
      'effect': 'waiting_for_leader'}

t9 = {'trigger': 't1',
      'source': 'conducting_irat',
      'target': 'pre_trat',
      'effect': 'irat_done'}

t10 = {'trigger': 'cancel',
       'source': 'pre_irat',
       'target': 'idle',
       'effect': ''}

t11 = {'trigger': 'trat_answer',
       'source': 'conduction_trat',
       'target': 'conduction_trat',
       'effect': 'send_trat_answer'}

t12 = {'trigger': 'trat_result',
       'source': 'conducting_trat',
       'target': 'conducting_trat',
       'effect': 'show_result'}

t13 = {'trigger': 'rat',
       'source': 'conducting_irat',
       'target': 'conduction_irat',
       'effect': 'show_irat'}


transitions = [t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13]


student = Student()
student_machine = Machine(
    transitions=transitions, obj=student, name="student")
student.stm = student_machine


driver = Driver()
driver.add_machine(student_machine)

student_client = Student_client()
student.mqtt_client = student_client.mqtt_client
student_client.stm_driver = driver

studentUI = StudentUI()
studentUI.stm_driver = driver
student.studentUI = studentUI
student.student_client = student_client
driver.start()
studentUI.create_ui()
