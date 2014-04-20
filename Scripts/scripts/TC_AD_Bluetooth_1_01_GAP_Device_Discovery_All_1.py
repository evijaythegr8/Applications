#
#=BEGIN
#
# This file is part of the Bluetooth use-case verification
#
# Copyright (C) ST-Ericsson SA 2010. All rights reserved.
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
from includes.BluetoothConstants import BluetoothConstants as BTC
from string import find
import time
import re


class TC_AD_Bluetooth_1_01_GAP_Device_Discovery_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Get device two out of sleep mode
        self.Wakeup(ComponentTwo, timeout=20)
        time.sleep(2)

        #Set discoverable
        self.SendAndWaitForEvent(ComponentTwo, OpCodes.SET_DISCOVERABLE, OpCodes.SET_DISCOVERABLE, message='Set Discoverable app 2', timeout=10)
        time.sleep(6)
        self.pressYes(ComponentTwo)
        time.sleep(3)

        #Perform discovery
        self.SendAndWaitForEvent(ComponentOne, OpCodes.START_DEVICE_DISCOVERY, OpCodes.START_DEVICE_DISCOVERY, message='Discover devices app 1', timeout=10)
        foundDevices = []
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.ACTION_DISCOVERY_FINISHED, OpCodes.ACTION_FOUND, timeout=120)

        #Verify that the device was discovered
        self.log.info(('%d \n %s')%(len(foundDevices),foundDevices))
        targetString = "%s"%(deviceTwoAddress)
        targetFound = self.MatchStringInList(foundDevices,targetString)
        if not targetFound:
            self.log.info("Target device not found")
            raise Failure('Target device not found')
        else:
            self.log.info("Device found")

        #Clean up
        self.RestoreApplication(ComponentOne)
        self.RestoreApplication(ComponentTwo)
        self.CloseDownExecution()


if __name__ == '__main__':
    from core.script.Script                   import Script
    from core.setup.Environment               import Environment
    from plugins.android.device.AndroidDevice import AndroidDevice

    Session.init(Script(__file__))

    duts = []
    dut1 = AndroidDevice('DUT1', connection=1)
    dut2 = AndroidDevice('DUT2', connection=1)
    duts.append(dut1)
    duts.append(dut2)

    env = Environment()
    env.addEquipment(dut1)
    env.addEquipment(dut2)

    if(env.setup()):
        tc = TC_AD_Bluetooth_1_01_GAP_Device_Discovery_All_1("TC_AD_Bluetooth_1_01_GAP_Device_Discovery_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
