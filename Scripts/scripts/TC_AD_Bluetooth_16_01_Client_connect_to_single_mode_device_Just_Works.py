#
#=BEGIN
#
# This file is part of the Bluetooth use-case verification
#
# Copyright (C) ST-Ericsson SA 2011. All rights reserved.
#
# This code is ST-Ericsson proprietary and confidential.
# Any use of the code for whatever purpose is subject to
# specific written permission of ST-Ericsson SA.
#
#=END
#
import setup_paths
import sys, os
curdir = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(curdir + "/.."))

from includes.BluetoothTestCase import BluetoothTestCase

from core.session.Session import Session
from core.general.Exceptions import Error, Failure
from includes.BluetoothOpCodes import OpCodes
from includes.BluetoothTestComponent import BluetoothTestComponent
from string import find
import time, re


class TC_AD_Bluetooth_16_01_Client_connect_to_single_mode_device_Just_Works(BluetoothTestCase):

   def execute(self):
        ComponentOne = '1'
        BLEdeviceAddress = "E2:0E:DC:25:7A:F4"
        BT_PID= ''

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        #Find PID of the Bluetooth Daemon
        BT_PID = self.RunShellCommand(ComponentOne, command='dbus-send --print-reply --system --dest=org.bluez / org.bluez.Manager.DefaultAdapter')
        BT_PID = BT_PID[BT_PID.find('org/bluez/')+10:]
        BT_PID = BT_PID[:BT_PID.find('/')]
        print ' BT_PID ', BT_PID

        if int(BT_PID) < 0:
            self.log.info("Bluetooth daemon PID not found")
            raise TestException('Bluetooth daemon PID not found')
        else:
            self.log.info('Bluetooth daemon PID found %s' %BT_PID)

        #Discover the BLE peripheral device from HREF
        self.SendAndWaitForEvent(ComponentOne, OpCodes.START_DEVICE_DISCOVERY, OpCodes.START_DEVICE_DISCOVERY, message='Discover devices app 1', timeout=10)
        foundDevices = []
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.ACTION_DISCOVERY_FINISHED, OpCodes.ACTION_FOUND, timeout=120)

        #Verify that the device was discovered
        targetString = "%s"%(BLEdeviceAddress)
        targetFound = self.MatchStringInList(foundDevices,targetString)

        if not targetFound:
            self.log.info("BLE peripheral device not found")
            raise TestException('BLE peripheral device not found')
        else:
            self.log.info("BLE peripheral device found")

        #Create Device
        BLE_Device = self.RunShellCommand(ComponentOne, command='dbus-send --print-reply --system --dest=org.bluez /org/bluez/'+BT_PID+'/hci0 org.bluez.Adapter.CreateDevice string:'+BLEdeviceAddress+'')

        #Extract the object path of the new device
        m = re.search('object path "(/org/bluez/'+BT_PID+'/hci0/dev(_\w+){6})', BLE_Device)

        if not m.group(1):
            self.log.info("Could not esblish dbus connection to BLE peripheral device")
            raise TestException('Could not esblish dbus connection to BLE peripheral device')
        else:
            self.log.info("Dbus connection to BLE peripheral device successfully created")

        dbus_object_path = m.group(1)

        #Remove the created dbus device
        BLE_Device = self.RunShellCommand(ComponentOne, command='dbus-send --system --type=method_call --print-reply --dest=org.bluez "/org/bluez/'+BT_PID+'/hci0" org.bluez.Adapter.RemoveDevice objpath:"'+dbus_object_path+'"')

        m = re.search('method return sender=:\w+\.\w+ -> dest=:\w+\.\w+', BLE_Device)

        if not m.group(0):
            self.log.info("Could not remove dbus device")
            raise TestException('Could not remove dbus device')
        else:
            self.log.info("sucessfully removed dbus device")

        #Clean up
        self.RestoreApplication(ComponentOne)
        self.CloseDownExecution()


if __name__ == '__main__':
    from core.script.Script                   import Script
    from core.setup.Environment               import Environment
    from plugins.android.device.AndroidDevice import AndroidDevice

    Session.init(Script(__file__))

    duts = []
    dut1 = AndroidDevice('DUT1', connection=1)
    duts.append(dut1)

    env = Environment()
    env.addEquipment(dut1)

    if(env.setup()):
        tc = TC_AD_Bluetooth_16_01_Client_connect_to_single_mode_device_Just_Works("TC_AD_Bluetooth_16_01_Client_connect_to_single_mode_device_Just_Works", duts)
        tc.run()

    env.tearDown()

    Session.summary()
