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
from string import find
import time,re


class TC_AD_Bluetooth_1_17_GAP_Dedicated_Outgoing_Bonding_Display_Yes_No_Rejected_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'
        ComponentTwo = '2'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])
        self.Components[ComponentTwo] = BluetoothTestComponent(self.devices[1])

        self.StartupExecution()

        #Initialization
        deviceOneAddress,deviceOneName = self.InititalizeApplication(ComponentOne)
        deviceTwoAddress,deviceTwoName = self.InititalizeApplication(ComponentTwo)

        #Check the bond state
        self.SendCommand(ComponentOne, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 1')
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        if len(foundDevices) != 0:
            TestException("Paired device list not empty for ComponentOne")

        self.SendCommand(ComponentTwo, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 2')
        foundDevices = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        if len(foundDevices) != 0:
            TestException("Paired device list not empty for ComponentTwo")

        #Bond devices
        self.SendCommand(ComponentOne, OpCodes.CREATE_BOND, message=deviceTwoAddress)
        passkey = self.WaitForEvent(ComponentOne, OpCodes.PAIRING_VARIANT_PASSKEY_CONFIRMATION, timeout=30)
        self.SendCommand(ComponentTwo, OpCodes.SET_PASSKEY, message='%s;%s'%(deviceOneAddress,passkey))
        self.SendAndWaitForEvent(ComponentOne, OpCodes.SET_PAIRING_CONFIRMATION, OpCodes.UNBOND_REASON_AUTH_FAILED, message='%s;false'%deviceTwoAddress, timeout=10)

        time.sleep(2)

        #Check the bond state
        self.SendCommand(ComponentOne, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 1')
        foundDevices = self.WaitForEventAndStore(ComponentOne, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceTwoName,deviceTwoAddress)

        targetFound = self.MatchStringInList(foundDevices, targetString)
        if targetFound:
            self.log.info("Target device found")
            raise Failure('Target device found')
        else:
            self.log.info("Device not found")

        #Check the bond state
        self.SendCommand(ComponentTwo, OpCodes.GET_BONDED_DEVICES, message='Get Bonded App 2')
        foundDevices = self.WaitForEventAndStore(ComponentTwo, OpCodes.NO_MORE_DEVICES, OpCodes.DEVICE_FOUND, timeout=60)
        targetString = "%s;%s"%(deviceOneName,deviceOneAddress)

        targetFound = self.MatchStringInList(foundDevices, targetString)
        if targetFound:
            self.log.info("Target device found")
            raise Failure('Target device found')
        else:
            self.log.info("Device not found")

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
        tc = TC_AD_Bluetooth_1_17_GAP_Dedicated_Outgoing_Bonding_Display_Yes_No_Rejected_All_1("TC_AD_Bluetooth_1_17_GAP_Dedicated_Outgoing_Bonding_Display_Yes_No_Rejected_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
