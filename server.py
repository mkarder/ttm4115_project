import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883
MQTT_TOPIC_INPUT = 'ttm4115/team_5/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_5/answer'

TOTAL_TEAMS = 3
irat_finished_counter = 0

class TimerLogic:   
    """
    State Machine for a named timer.

    This is the support object for a state machine that models a single
    timer.
    """
    def __init__(self, name, duration, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.duration = duration
        self.component = component
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

    def started(self):
        self.stm.start_timer('t', self.duration)
        self._logger.debug('New timer {} with duration {} started.'
                           .format(self.name, self.duration))

    def timer_completed(self):
        self._logger.debug('Timer {} expired.'.format(self.name))
        self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, '"command":"t1_expired"')
        self.stm.terminate()


    def create_machine(timer_name, duration, component):
        """
        Create a complete state machine instance for the timer object.
        Note that this method is static (no self argument), since it is a helper
        method to create this object.
        """
        timer_logic = TimerLogic(name=timer_name, duration=duration, component=component)
        t0 = {'source': 'initial',
              'target': 'active',
              'effect': 'started'}
        t1 = {
            'source': 'active',
            'target': 'completed',
            'trigger': 't',
            'effect': 'timer_completed'}
        t2 = {
            'source': 'active',
            'target': 'completed',
            'trigger': 'rat_completed',
            'effect': 'timer_completed'}
        timer_stm = stmpy.Machine(name=timer_name, transitions=[t0, t1, t2],
                                  obj=timer_logic)
        timer_logic.stm = timer_stm
        return timer_stm




class ManagerComponent:
    """
    The component to manage named timers in a voice assistant.

    This component connects to an MQTT broker and listens to commands.
    To interact with the component, do the following:

    * Connect to the same broker as the component. You find the broker address
    in the value of the variable `MQTT_BROKER`.
    *Subscribe to the topic in variable `MQTT_TOPIC_OUTPUT`. On this topic, the
    component sends its answers.
    * Send the messages listed below to the topic in variable `MQTT_TOPIC_INPUT`.

        {"command": "new_timer", "name": "spaghetti", "duration":50}

        {"command": "status_all_timers"}

        {"command": "status_single_timer", "name": "spaghetti"}

        {"command": "start_iRAT", "RAT_ID": "X"}

    """

    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        global irat_finished_counter
        """
        Processes incoming MQTT messages.

        We assume the payload of all received MQTT messages is an UTF-8 encoded
        string, which is formatted as a JSON object. The JSON object contains
        a field called `command` which identifies what the message should achieve.

        As a reaction to a received message, we can for example do the following:

        * create a new state machine instance to handle the incoming messages,
        * route the message to an existing state machine session,
        * handle the message right here,
        * throw the message away.

        """
        self._logger.debug('Incoming message to topic {}'.format(msg.topic))
        # encdoding from bytes to string. This


        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        command = payload.get('command')
        self._logger.debug('Command in message is {}'.format(command))



        """Får mqtt message fra teacher, sier at teacher vil starte t1 timeren. Dette fører til at iRAT starter"""
        if command == 'start_iRAT':
            irat_finished_counter = 0
            try:
                print(type(self))
                rat_id = payload.get('RAT_ID')
                # create a new instance of the timer logic state machine
                #timer_stm = TimerLogic.create_machine(timer_name, 10000, self)

                #TODO: Start timer 10 min.
                timer_stm1 = TimerLogic.create_machine("t1", 20000, self)

                #TODO: Send RAT with id X to all of the team managers
                try:
                    with open('ratDB.json', 'r') as f:
                        data = json.load(f)
                    question = data[str(rat_id)]['Questions']
                    print(question)
                    self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps(question))
                except:
                    print("An error occured")

                # add the machine to the driver to start it
                self.stm_driver.add_machine(timer_stm1)
            except Exception as err:
                self._logger.error('Invalid arguments to command. {}'.format(err))

        #TODO: elif command == 'stop_timer'

        elif command == 'iRAT_done':
            irat_finished_counter += 1
            self._logger.debug('{} teams are done with iRAT'.format(irat_finished_counter))
            if irat_finished_counter == TOTAL_TEAMS:
                self.stm_driver.send('rat_completed','t1')

        elif command == 'status_all_timers':
            s = "List of all timers"
            # We loop over all state machines in the driver. All of them are a
            # timer that we should include in our list that we present to the
            # user.
            for name, stm in self.stm_driver._stms_by_id.items():
                time = int(stm.get_timer('t')/1000)
                s = s + 'Timer {} has about {} seconds left. '.format(stm.id, time)
            self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, s)
        elif command == 'status_single_timer':
            # report the status of a single timer
            try:
                # print(type(self))
                timer_name = payload.get('name')
                # send a signal to the corresponding timer state machine to
                # trigger reporting the status.
                self.stm_driver.send_signal('report', timer_name)
            except Exception as err:
                self._logger.error('Invalid arguments to command. {}'.format(err))
        else:
            self._logger.error('Unknown command {}. Message ignored.'.format(command))

    def __init__(self):
        """
        Start the component.

        ## Start of MQTT
        We subscribe to the topic(s) the component listens to.
        The client is available as variable `self.client` so that subscriptions
        may also be changed over time if necessary.

        The MQTT client reconnects in case of failures.

        ## State Machine driver
        We create a single state machine driver for STMPY. This should fit
        for most components. The driver is available from the variable
        `self.driver`. You can use it to send signals into specific state
        machines, for instance.

        """
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self._logger.debug('Component initialization finished')

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()

        # logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = ManagerComponent()
