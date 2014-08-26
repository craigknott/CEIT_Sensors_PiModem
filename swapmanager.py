from swap.SwapInterface import SwapInterface
from MQTT import MQTT

DEBUG = True
import sys
import os
import json
import random
import mosquitto
import time

class SwapManager(SwapInterface):
    """
    SWAP Management Class
    """

    def getEndPts(self, register):
	"""
	Returns the list of end points from the register.
	Helper function for registerValueChanged
	"""
        status = []
        # For every endpoint contained in this register
        for endp in register.parameters:
            strval = endp.getValueInAscii()
            if endp.valueChanged:
                if DEBUG:
                    if endp.unit is not None:
                        strval += " " + endp.unit.name
                    print endp.name + " in address " + str(endp.getRegAddress()) + " changed to " + strval
                           
                if endp.display:
                    endp_data = endp.dumps()
                    if endp_data is not None:
                        status.append(endp_data)
        return status


    def registerValueChanged(self, register):
        """
        Register value changed
        
        @param register: register object having changed
        """
        # Skip config registers
        if register.isConfig():
            return
        
        # Check if debugging is on
        if DEBUG:
            print  "Register addr= " + str(register.getAddress()) + " id=" + str(register.id) + " changed to " + register.value.toAsciiHex()
        
        # Get the list of end pts
        status = self.getEndPts(register)
        
        if len(status) > 0:
            # Publish data onto the server LIB/level4/climate_raw
            pub_data = json.dumps(status)[1:-1]
            pub_data = pub_data[:-1] + ", 'pi_id' : " + str(MQTT.pi_id) + pub_data[-1]
            data = status[0] 
            
            try:
                if (str(MQTT.config[str(data["id"])]) == str(MQTT.pi_id)):
                    (result, mid) = self.mqttc.publish(MQTT.topic_temp, str(pub_data), retain = True)
                    # Check if mosquito accepted the publish or not. 
                    if (result == 0):
                        print "PUBLISH SUCCESS: " + str(pub_data)
                    else:
                        print "PUBLISH FAILED: " + str(pub_data)
                        self.reconnect_loop(MQTT.topic_temp, str(pub_data))
            except:
                e = sys.exc_info()[0]
                print ("<publishData> Error: %s" % e )


    def reconnect_loop(self, topic, data):
    	result = -1
    	while result!=0:
    	    self.shell_command("sudo ifup wlan0")
    	    time.sleep(2)
            self.mqttc.connect(MQTT.server, 1883)
            (result, mid) = self.mqttc.publish(topic, data, retain = True)

    def shell_command(self, command):
        """
 		Sends command to bash shell	
        """
        import subprocess
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = process.communicate()[0]
        print output


    def on_publish(self, mosq, userdata, mid):
        """
        Callback when a message was sent to the broker using publish.
        """
        print("PUBLISHED: MID: "+str(mid))


    def on_message(self, mosq, obj, msg):
        """
        Callback when a message has been recieved from the broker on a topic.
        """
        print("Message received on topic "+msg.topic+" with QoS "+str(msg.qos)+" and payload "+msg.payload)
        if (msg.topic == "github/craigknott/CEIT_Sensors_PiModem"):
            cmd = os.path.join(MQTT.directory, "gitpull.sh")
            print "On message command fired: " + cmd
            self.shell_command(cmd)
            

    def on_connect(self, mosq, userdata, rc):
        """
        Callback when client connects to mqtt server.
        """
        self.mqttc.subscribe("github/craigknott/CEIT_Sensors_PiModem")
        print("CONNECTED: RC: "+str(rc))


    def on_disconnect(self, obj, rc):
        """
        Callback when client disconnects from mqtt server successfully.
        """
        print "DISCONNECTED: RC:  " + str(rc)


    def __init__(self, swap_settings=None):
        """
        Class constructor
        
        @param swap_settings: path to the main SWAP configuration file
        """
        
        # MAin configuration file
        self.swap_settings = swap_settings
        
        # Print SWAP activity
        DEBUG = False
        
        #Setup MQTT client
        self.mqttc = mosquitto.Mosquitto("LIB-PI_"+str(MQTT.pi_id)+str(random.randrange(10000)))
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_message = self.on_message
        self.mqttc.connect(MQTT.server, 1883)
        
        try:
            # Superclass call
            SwapInterface.__init__(self, swap_settings)
            
            # Start MQTT client loop
            self.mqttc.loop_forever()
        except:
            e = sys.exc_info()[0]
            print ("<__init__> Error: %s" % e )
            self.shell_command("sudo svc -t /etc/service/lib/")

if __name__ == '__main__':
    """
    Function run if this script is the main script being run.
    """
    if (len(sys.argv) < 2):
        print "Usage: python pyswapmanager.py PI_ID"
        exit(0)
    
    MQTT.pi_id = sys.argv[1]
    MQTT.directory = os.path.dirname(os.path.realpath(__file__))
    print "INIT DIRECTORY SET : " + MQTT.directory
    settings = os.path.join(MQTT.directory, "config", "settings.xml")
    try:
        sm = SwapManager(settings)
    except:
        e = sys.exc_info()[0]
        print ("<__main__> Error: %s" % e )
        self.shell_command("sudo svc -t /etc/service/lib/")
