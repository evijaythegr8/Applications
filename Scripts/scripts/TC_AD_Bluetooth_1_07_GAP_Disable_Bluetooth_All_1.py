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
import time


class TC_AD_Bluetooth_1_07_GAP_Disable_Bluetooth_All_1(BluetoothTestCase):

    def execute(self):
        ComponentOne = '1'

        self.Components[ComponentOne] = BluetoothTestComponent(self.devices[0])

        self.StartupExecution()

        #Enable BT
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_ISENABLED, OpCodes.GET_ISENABLED, message='Check state app 1', timeout=10)
        if returnData == "false":
            self.SendAndWaitForEvent(ComponentOne, OpCodes.ENABLE_BT_API, OpCodes.ENABLE_BT_API, message='Enable BT app 1', timeout=30)
            self.WaitForEvent(ComponentOne, OpCodes.CURR_STATE_ON, timeout=60)
            time.sleep(5)

        #Disable BT
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.DISABLE_BT, OpCodes.DISABLE_BT, message='Disable BT app 1', timeout=30)
        self.WaitForEvent(ComponentOne, OpCodes.CURR_STATE_OFF, timeout=30)
        time.sleep(2)

        #Check that BT is off
        returnData = self.SendAndWaitForEvent(ComponentOne, OpCodes.GET_ISENABLED, OpCodes.GET_ISENABLED, message='Check state app 1', timeout=10)
        if returnData == "true":
            self.log.info("Bluetooth still Enabled after Disable")
            raise Failure('Bluetooth still Enabled after Disable')
        time.sleep(2)

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
        tc = TC_AD_Bluetooth_1_07_GAP_Disable_Bluetooth_All_1("TC_AD_Bluetooth_1_07_GAP_Disable_Bluetooth_All_1", duts)
        tc.run()

    env.tearDown()

    Session.summary()
