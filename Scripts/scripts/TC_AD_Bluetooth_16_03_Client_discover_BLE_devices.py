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


class TC_AD_Bluetooth_16_03_Client_discover_BLE_devices(BluetoothTestCase):

   def execute(self):
        ComponentOne = '1'
        BLEdeviceAddress = "E2:0E:DC:25:7A:F4"
        BT_PID= ''

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)

        self.SendAndWaitForEvent(ComponentOne, OpCodes.START_DEVICE_DISCOVERY, OpCodes.START_DEVICE_DISCOVERY, message='Discover devices app 1', timeout=10)
        foundDevices = []
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.ACTION_DISCOVERY_FINISHED, OpCodes.ACTION_FOUND, timeout=120)

        #Verify that the device was discovered
        self.log.info(len(foundDevices),'\n',foundDevices) #######33 some problems with logging
        targetString = "%s"%(BLEdeviceAddress)
        targetFound = self.MatchStringInList(foundDevices,targetString)

        if not targetFound:
            self.log.info("BLE peripheral device not found")
            raise TestException('BLE peripheral device not found')
        else:
            self.log.info("BLE peripheral device found")

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
        tc = TC_AD_Bluetooth_16_03_Client_discover_BLE_devices("TC_AD_Bluetooth_16_03_Client_discover_BLE_devices", duts)
        tc.run()

    env.tearDown()

    Session.summary()
