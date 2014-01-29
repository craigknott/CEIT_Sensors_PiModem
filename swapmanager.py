from swap.SwapInterface import SwapInterface
from MQTT import MQTT

DEBUG = True
import sys
import os
import json
import random
import mosquitto

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
            data = status[0] 
            
			try:
				if (str(MQTT.config[str(data["id"])]) == str(MQTT.pi_id)):
					(result, mid) = self.mqttc.publish(MQTT.topic_temp, str(pub_data), retain = True)
					# Check if mosquito accepted the publish or not. 
					if (result == 0):
						print "PUBLISH SUCCESS: " + str(pub_data)
					else:
						print "PUBLISH FAILED: " + str(pub_data)
						#sys.exit(2) 
			except:
				e = sys.exc_info()[0]
				print ("<publishData> Error: %s" % e )

	          

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


    def on_connect(self, mosq, userdata, rc):
        """
        Callback when client connects to mqtt server.
        """
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
        self.mqttc.connect(MQTT.server, 1883)

        try:
            # Superclass call
            SwapInterface.__init__(self, swap_settings)

            # Start MQTT client loop
            self.mqttc.loop_forever()
        except:
            e = sys.exc_info()[0]
            print ("<__init__> Error: %s" % e )
	    sys.exit(0)

if __name__ == '__main__':
    """
    Function run if this script is the main script being run.
    """
    if (len(sys.argv) < 2):
        print "Usage: python pyswapmanager.py PI_ID"
        exit(0)

    MQTT.pi_id = sys.argv[1]
    settings = os.path.join(os.path.dirname(sys.argv[0]), "config", "settings.xml")
    try:
    	sm = SwapManager(settings)
    except:
        e = sys.exc_info()[0]
        print ("<__main__> Error: %s" % e )
	sys.exit(0)
