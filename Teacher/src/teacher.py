import paho.mqtt.client as mqtt
import datetime
import logging
import json
import uuid
from teacherUI import TeacherUserInterface

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

# TO DO: fill in topics for publishing and subscribing
MQTT_TOPIC = 'ttm4115/team_5/teacher'


class Teacher:
    def __init__(self):
        # dict with all RAT objects: { rat_id: RAT-object }
        self.rats = {}

        # dict with available RATs from server: { rat_id: rat_name }             
        self.available_rats = {}

        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug(
            'Connecting to MQTT broker {} at port {}'
            .format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()

        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.mqtt_client.subscribe(MQTT_TOPIC)

        # load the user interface
        self.ui = TeacherUserInterface(self)

    def on_connect(self, client, userdata, flags, rc):
        """Request available RATs from database"""
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        self._logger.debug('Incoming message to topic {}'.format(msg.topic))
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error(
                'Message had no valid JSON. Message ignored. {}'
                .format(err))
            return
        command = payload.get('command')
        self._logger.debug('Command in message is {}'.format(command))
        if command == 'available_RATs':
            try:
                self.available_rats.update(payload.get('rat_info'))
                # for k, v in temp:
                #     self.rats[k] = Rat(v, 0)
                # self.rats.update(payload.get('rat_info'))

            except Exception as err:
                self._logger.error(
                    'Message had no valid RATs. Ignored: {}'
                    .format(err))
                return

    def create_rat(self, name, size, subject='TTM4115'):
        rat = Rat(name, size, subject)
        self.rats[str(rat.id)] = rat
        self.available_rats[str(rat.id)] = rat.name
        return rat

    def create_question(self, rat_id, question, correct, false):
        rat = self.rats[rat_id]
        rat.create_question(question, correct, false)

    def save_rat(self, rat_id):
        """send MQTT message to server (database) containing the RAT-object"""
        payload = json.dumps({
            "command": "create_RAT",
            str(rat_id): self.rats[rat_id].reprJSON()
            },
            cls=ComplexEncoder)
        self._logger.info("Saving RAT {}".format(rat_id))
        self.mqtt_client.publish(MQTT_TOPIC, payload)

    def find_rat(self, rat_name):
        for k, v in self.available_rats.items():
            if rat_name == v:
                return str(k)

    def publish_rat(self, rat_name):
        """send MQTT message to server (manager)
        indicating which RAT (rat_id) should be made available."""
        rat_id = self.find_rat(rat_name)
        if rat_id:
            payload = json.dumps({
                "command": "start_RAT",
                "RAT_ID": rat_id
            })
            self._logger.info("Publishing {} at {}".format(
                rat_id, datetime.datetime.now()))
            self.mqtt_client.publish(MQTT_TOPIC, payload)

    def fetch_rat(self):
        payload = json.dumps({
            "command": "fetch_RATs"
        })
        self.mqtt_client.publish(MQTT_TOPIC, payload)

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()


# Sub-classes for RAT and question objects
class Rat:
    id: str
    name: str
    size: int
    subject: str
    questions: dict

    def __init__(self, name, size=0, subject='TTM4115', rat_id=None):
        self.name = name
        if rat_id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = rat_id
        self.size = size
        self.subject = subject
        self.question_counter = 0
        self.questions = {}
        self.rat_complete = False

    def reprJSON(self):
        return dict(name=self.name,
                    id=str(self.id),
                    size=self.size,
                    subject=self.subject,
                    questions=self.questions)

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
        return dict(question=self.question,
                    correct=self.correct,
                    a=self.a,
                    b=self.b,
                    c=self.c)


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)


# Function for deserializing RAT
# Probably only needed for students
def load_RAT(d: dict):
    rat = Rat(d['name'], d['size'], d['subject'], d['id'])
    for k in d['questions']:
        rat.create_question(d['questions'][k]['question'],
                            d['questions'][k]['correct'],
                            [d['questions'][k]['a'],
                            d['questions'][k]['b'],
                            d['questions'][k]['c']])
    return rat


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
