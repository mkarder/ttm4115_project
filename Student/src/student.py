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
MQTT_TOPIC = 'ttm4115/team_5/student'


class Student:

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

        self.mqtt_client.subscribe(MQTT_TOPIC)

    def start(self, broker, port):

        # create a new MQTT client
        self._logger.debug(
            'Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

        self.client.subscribe(MQTT_TOPIC)

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
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        # msg = json.loads(str(msg.payload.decode("utf-8", "ignore")))
        command = payload.get('command')
        self._logger.debug('Command in message is {}'.format(command))
        
        if "command" in msg.keys():
            if msg["command"] == "start_iRAT":
                if "RAT" in msg.keys():
                    self.rat = msg["RAT"]
                    self.stm.send("start_irat", "student")
            elif msg["command"] == "iRAT_done":
                self.stm.send("irat_done", "student")
            elif msg["command"] == "start_tRAT" and "leader" in msg.keys():
                if msg["leader"] == self.student["student_id"]:
                    self.leader = True
                    self.stm.send("leader", "student")
                elif msg["leader"] != self.student["student_id"]:
                    self.leader = False
                    self.stm.send("not_leader", "student")
            elif msg["command"] == "tRAT_done":
                self.stm.send("trat_done", "student")
            elif msg["command"] == "t1_expired":
                self.stm.send("t1", "student")
            elif msg["command"] == "timer_team{}_expired".format(self.team):
                self.stm.send("t2_expired", "student")

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()

    def start_irat(self):
        self.rat = self.rat
        self.studentUI.rat = self.rat
        self.studentUI.start_irat()
        print("conducting irate state")

    def sign_in(self):
        self.student = self.studentUI.student
        print("pre irat state")

    def irat_done(self):
        self.studentUI.irat_done()
        message = {"command": "student_iRAT_done",
                   "student_id": str(self.student["student_id"]),
                   "RAT_id": str(self.rat["id"]),
                   "team_id": str(self.student["team"]),
                   "answers": json.dumps(self.studentUI.answers)}
        self.mqtt_client.publish(MQTT_TOPIC, json.dumps(message))
        self.studentUI.answers = []
        print("pre trat state")

    def start_trat(self):
        self.studentUI.start_trat()
        print("conducting trat state")

    def trat_done(self):
        self.studentUI.trat_done()
        print("trat done, idle state")
        if self.leader:
            message = {"command": "tRAT_answers",
                       "RAT_id": self.rat["id"],
                       "team_id": self.student["team"],
                       "answers": json.dumps(self.studentUI.answers)}
            self.mqtt_client.publish(MQTT_TOPIC, json.dumps(message))
        self.studentUI.answers = []
        self.student = None

    def waiting_for_leader(self):
        print("waiting for leader state")
        self.studentUI.trat_not_leader()


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
      'target': 'idle',
      'effect': 'trat_done'}

t6 = {'trigger': 'trat_done',
      'source': 'waiting_for_leader',
      'target': 'idle',
      'effect': 'trat_done'}

t7 = {'trigger': 't2',
      'source': 'conducting_trat',
      'target': 'idle',
      'effect': 'trat_done'}

t8 = {'trigger': 't2',
      'source': 'waiting_for_leader',
      'target': 'idle',
      'effect': 'trat_done'}

t9 = {'trigger': 'not_leader',
      'source': 'pre_trat',
      'target': 'waiting_for_leader',
      'effect': 'waiting_for_leader'}

t10 = {'trigger': 't1',
       'source': 'conducting_irat',
       'target': 'pre_trat',
       'effect': 'irat_done'}

t11 = {'trigger': 'cancel',
       'source': 'pre_irat',
       'target': 'idle',
       'effect': ''}


transitions = [t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11]

debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter(
    '%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


student = Student()
student_machine = Machine(
    transitions=transitions, obj=student, name="student")
student.stm = student_machine

studentUI = StudentUI()
studentUI.stm = student_machine
student.studentUI = studentUI


driver = Driver()
driver.add_machine(student_machine)


driver.start()
studentUI.create_ui()
