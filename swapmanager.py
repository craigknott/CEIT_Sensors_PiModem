#########################################################################
#
# SwapManager
#
# Copyright (c) 2012 Daniel Berenguer <dberenguer@usapiens.com>
#
# This file is part of the lagarto project.
#
# lagarto  is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# lagarto is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with panLoader; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA
#
#########################################################################
__author__="Daniel Berenguer"
__date__  ="$Jan 23, 2012$"

__edited__="Buddhika De Seram"
__date__="$02/01/2012$"

__edited__="Craig Knott"
__date__="$20/11/2013$"
#########################################################################

from swap.SwapInterface import SwapInterface
from swap.protocol.SwapDefs import SwapState
from swap.xmltools.XmlSettings import XmlSettings
from MQTT import MQTT

import sys
import os
import json
import random
import mosquitto

class SwapManager(SwapInterface):
    """
    SWAP Management Class
    """
    def newMoteDetected(self, mote):
        """
        New mote detected by SWAP server
        
        @param mote: Mote detected
        """
        if self._print_swap == True:
            print "New mote with address " + str(mote.address) + " : " + mote.definition.product + \
            " (by " + mote.definition.manufacturer + ")"


    def newEndpointDetected(self, endpoint):
        """
        New endpoint detected by SWAP server
        
        @param endpoint: Endpoint detected
        """
        if self._print_swap == True:
            print "New endpoint with Reg ID = " + str(endpoint.getRegId()) + " : " + endpoint.name


    def moteStateChanged(self, mote):
        """
        Mote state changed
        
        @param mote: Mote having changed
        """
        if self._print_swap == True:
            print "Mote with address " + str(mote.address) + " switched to \"" + \
            SwapState.toString(mote.state) + "\""     


    def moteAddressChanged(self, mote):
        """
        Mote address changed
        
        @param mote: Mote having changed
        """
        if self._print_swap == True:
            print "Mote changed address to " + str(mote.address)


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
                if self._print_swap:
                    if endp.unit is not None:
                        strval += " " + endp.unit.name
                    print endp.name + " in address " + str(endp.getRegAddress()) + " changed to " + strval
                               
                if endp.display:
                    endp_data = endp.dumps()
                    if endp_data is not None:
                        status.append(endp_data)
	return status

    def publishData(self, status):
	# publish data onto the server LIB/level4/climate_raw        
        data = json.dumps(status)
        L = len(data)
        data = data[1:L-1]

	try:
	    print MQTT.config[str(endp.id)]
            if (str(MQTT.config[str(endp.id)]) == str(MQTT.pi_id)):
    	        (result, mid) = self.mqttc.publish(MQTT.topic_temp, data, retain = True)

	    # Check if mosquito accepted the publish or not.
    	    if (result == 0):
    	        print "PUBLISH SUCCESS: " + data
    	    else:
		print "PUBLISH FAILED: " + data
    	        #self.restart();	
	except:
	    e = sys.exc_info()[0]
	    print ("<p>Error: %s</p>" % e )

    def registerValueChanged(self, register):
        """
        Register value changed
        
        @param register: register object having changed
        """
        # Skip config registers
        if register.isConfig():
            return
        
        if self._print_swap == True:
            print  "Register addr= " + str(register.getAddress()) + " id=" + str(register.id) + " changed to " + register.value.toAsciiHex()
        
	# Get the list of end pts
        status = self.getEndPts(register)
        
        if len(status) > 0:
	    self.publishData(status)
            

    def get_status(self, endpoints):
        """
        Return network status as a list of endpoints in JSON format
        
        @param endpoints: list of endpoints being queried
        
        @return list of endpoints in JSON format
        """
        status = []
        if endpoints is None:
            for mote in self.network.motes:
                for reg in mote.regular_registers:
                    for endp in reg.parameters:
                        status.append(endp.dumps())
        else:
            for item in endpoints:
                endp = self.get_endpoint(item["id"], item["location"], item["name"])
                if endp is not None:
                    status.append(endp.dumps()) 
        return status
            
    
    def stop(self):
        """
        Stop SWAP manager
        """
        logger.error('Server dead for some reason')
        self.server.stop()
        sys.exit(0)


    def restart(self):
	"""
	Restarts this SWAP manager script
	"""
 	command="/usr/bin/sudo svc -t /etc/service/lib"	
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
	Callback when client disconnects from matt server successfully.
	"""
	print "DISCONNECTED: RC:  " + str(rc)


    def __init__(self, swap_settings=None):
        """
        Class constructor
        
        @param swap_settings: path to the main SWAP configuration file
        @param verbose: Print out SWAP frames or not
        @param monitor: Print out network events or not
        """

        # MAin configuration file
        self.swap_settings = swap_settings

        # Print SWAP activity
        self._print_swap = False
        
	#Setup MQTT client
        self.mqttc = mosquitto.Mosquitto("LIB-PI_"+str(MQTT.pi_id)+str(random.randrange(10000)))
        self.mqttc.on_connect = self.on_connect
	self.mqttc.on_publish = self.on_publish
	self.mqttc.connect(MQTT.server, 1883)

        try:
            # Superclass call
            SwapInterface.__init__(self, swap_settings)

	    # Check if debug is on or not
	    if XmlSettings.debug == 2:
        	self._print_swap = True

	    # Start MQTT client loop
	    self.mqttc.loop_forever()
        except:
	    e = sys.exc_info()[0]
	    print ("<p>Error: %s</p>" % e )
            self.restart() 


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
	print ("<p>Error: %s</p>" % e )
	sys.exit(1)
